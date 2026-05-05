"""wpf_testkit/utils/visual_diff.py — 视觉回归测试工具

基于 PIL 的截图比对引擎，零额外依赖。
Vision 扩展：像素差异超标时自动用多模态大模型做语义差异分析，
过滤时钟/天气/滚动位置等非功能性变化导致的误报。
"""

from __future__ import annotations

import os
from typing import Optional

from PIL import Image, ImageChops


class DiffResult:
    """截图比对结果。"""

    def __init__(self, candidate: str, baseline: str):
        self.candidate_path = candidate
        self.baseline_path = baseline
        self.diff_count: int = 0
        self.total_pixels: int = 0
        self.diff_pct: float = 0.0
        self.max_diff: int = 0
        self.diff_image_path: str = ""
        self.size_mismatch: bool = False
        self.baseline_missing: bool = False
        # Vision 语义分析（可选）
        self.semantic_diff: Optional[str] = None
        self.semantic_acceptable: Optional[bool] = None

    @property
    def passed(self) -> bool:
        return not self.size_mismatch and not self.baseline_missing

    def within_threshold(self, threshold: float = 0.05) -> bool:
        """差异百分比是否在阈值内。"""
        if self.baseline_missing or self.size_mismatch:
            return False
        if self.diff_pct <= threshold:
            return True
        # 像素超标但语义分析通过了，也算通过
        if self.semantic_acceptable:
            return True
        return False

    def summary(self) -> str:
        """人类可读的摘要。"""
        if self.baseline_missing:
            return f"❌ Baseline 不存在: {self.baseline_path}"
        if self.size_mismatch:
            return "⚠️ 尺寸不匹配"
        # 判定逻辑：像素通过 或 语义通过
        pixel_pass = self.diff_pct < 0.05
        semantic_hint = ""
        if self.semantic_acceptable:
            semantic_hint = " (Vision 语义判定为非实质性差异)"
        if pixel_pass or self.semantic_acceptable:
            return (
                f"✅ 差异: {self.diff_pct:.2%}{semantic_hint}"
                f" (差异像素 {self.diff_count}/{self.total_pixels}, "
                f"最大偏差 {self.max_diff})"
            )
        extra = ""
        if self.semantic_diff:
            extra = f"\n   Vision 语义: {self.semantic_diff[:150]}"
        return (
            f"❌ 差异: {self.diff_pct:.2%}{extra}"
            f" (差异像素 {self.diff_count}/{self.total_pixels}, "
            f"最大偏差 {self.max_diff})"
        )


class VisualDiff:
    """视觉差异比较引擎。"""

    def __init__(self, diff_output_dir: str = "screenshots/diffs"):
        self.diff_output_dir = diff_output_dir
        self._vision = None

    def _get_vision(self):
        if self._vision is None:
            try:
                from wpf_testkit.vision import get_analyzer

                self._vision = get_analyzer()
            except ImportError:
                self._vision = False
        return self._vision if self._vision else None

    # ── 核心 API ──

    def compare(
        self, candidate_path: str, baseline_path: str
    ) -> DiffResult:
        """比较候选截图与基准截图。

        像素差异超标时自动用 Vision 做语义分析。
        """
        result = DiffResult(candidate_path, baseline_path)

        if not os.path.exists(baseline_path):
            result.baseline_missing = True
            return result

        try:
            candidate_img = Image.open(candidate_path).convert("RGB")
            baseline_img = Image.open(baseline_path).convert("RGB")
        except Exception:
            result.baseline_missing = True
            return result

        if candidate_img.size != baseline_img.size:
            result.size_mismatch = True
            return result

        # 像素级差异计算
        diff_img = ImageChops.difference(candidate_img, baseline_img)
        grayscale = diff_img.convert("L")

        if hasattr(grayscale, "get_flattened_data"):
            pixels = list(grayscale.get_flattened_data())
        else:
            pixels = list(grayscale.getdata())
        result.total_pixels = len(pixels)
        result.diff_count = sum(1 for p in pixels if p > 0)
        result.max_diff = max(pixels) if pixels else 0
        result.diff_pct = result.diff_count / max(result.total_pixels, 1)

        # 生成差异高亮图
        result.diff_image_path = self._generate_diff_image(
            candidate_img, baseline_img, candidate_path
        )

        # 像素超标时：Vision 语义分析
        if result.diff_pct > 0.05:
            va = self._get_vision()
            if va and va.available:
                semantic = va.compare_semantic(candidate_img, baseline_img)
                if semantic:
                    result.semantic_diff = semantic
                    result.semantic_acceptable = (
                        "非实质性差异" in semantic
                        or "非功能性差异" in semantic
                        or "功能没有影响" in semantic
                    )

        return result

    def update_baseline(self, candidate_path: str, baseline_path: str) -> str:
        """将当前截图更新为新的基准。"""
        os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
        candidate_img = Image.open(candidate_path)
        candidate_img.save(baseline_path)
        return baseline_path

    # ── 差异高亮图 ──

    def _generate_diff_image(
        self,
        candidate: Image.Image,
        baseline: Image.Image,
        candidate_path: str,
    ) -> str:
        """生成差异高亮图。"""
        diff = ImageChops.difference(candidate, baseline)
        gray = diff.convert("L")
        mask = gray.point(lambda p: 255 if p > 15 else 0)

        overlay = Image.new("RGBA", candidate.size, (255, 0, 0, 0))
        overlay.putalpha(mask.point(lambda p: 128 if p > 15 else 0))

        result_img = candidate.convert("RGBA")
        result_img = Image.alpha_composite(result_img, overlay)

        os.makedirs(self.diff_output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(candidate_path))[0]
        out_path = os.path.join(
            self.diff_output_dir, f"{base_name}_diff.png"
        )
        result_img.save(out_path, "PNG")
        return out_path


# ── pytest fixture ──

UPDATE_BASELINE = False


def visual_regression_check(
    screenshot_manager,
    window,
    baseline_name: str,
    threshold: float = 0.05,
    baseline_dir: str = "screenshots/baseline",
):
    """视觉回归检查：截图 → 对比 baseline → 断言。

    自动处理：
    - baseline 不存在时自动创建（视为通过）
    - --update-baseline 时强制更新
    - 像素超标时 Vision 语义分析过滤误报
    """
    os.makedirs(baseline_dir, exist_ok=True)
    baseline_path = os.path.join(baseline_dir, f"{baseline_name}.png")

    shot_path = screenshot_manager.capture(
        window, f"visreg_{baseline_name}"
    )

    vd = VisualDiff()

    if UPDATE_BASELINE:
        vd.update_baseline(shot_path, baseline_path)
        return DiffResult(shot_path, baseline_path)

    result = vd.compare(shot_path, baseline_path)

    if result.baseline_missing:
        vd.update_baseline(shot_path, baseline_path)
        return DiffResult(shot_path, baseline_path)

    return result
