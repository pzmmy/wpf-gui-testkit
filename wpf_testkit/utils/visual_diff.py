"""wpf_testkit/utils/visual_diff.py — 视觉回归测试工具

基于 PIL 的截图比对引擎，零额外依赖。

功能：
- compare_to_baseline(candidate, baseline) → diff 分析结果
- generate_diff_image(candidate, baseline) → 差异高亮图（红色标记差异区域）
- is_within_threshold(result, threshold) → 阈值判定

用法：
    from wpf_testkit.utils.visual_diff import VisualDiff, DiffResult

    vd = VisualDiff()
    result = vd.compare("current.png", "baseline/win10_1909_main.png")
    assert result.within_threshold(0.05), f"差异 {result.diff_pct:.2%} 超过阈值"
"""
from __future__ import annotations

import os

from PIL import Image, ImageChops


class DiffResult:
    """截图比对结果。"""

    def __init__(self, candidate: str, baseline: str):
        self.candidate_path = candidate
        self.baseline_path = baseline
        self.diff_count: int = 0          # 差异像素数
        self.total_pixels: int = 0        # 总像素数
        self.diff_pct: float = 0.0        # 差异百分比 (0.0 ~ 1.0)
        self.max_diff: int = 0            # 单像素最大差异值 (0~255)
        self.diff_image_path: str = ""    # 生成的差异高亮图路径
        self.size_mismatch: bool = False   # 尺寸不匹配
        self.baseline_missing: bool = False  # baseline 不存在

    @property
    def passed(self) -> bool:
        """无尺寸不匹配且 baseline 存在即为通过（像素级差异需配合阈值）。"""
        return not self.size_mismatch and not self.baseline_missing

    def within_threshold(self, threshold: float = 0.05) -> bool:
        """差异百分比是否在阈值内（默认 5%）。"""
        if self.baseline_missing or self.size_mismatch:
            return False
        return self.diff_pct <= threshold

    def summary(self) -> str:
        """人类可读的摘要。"""
        if self.baseline_missing:
            return f"❌ Baseline 不存在: {self.baseline_path}"
        if self.size_mismatch:
            return "⚠️ 尺寸不匹配"
        passing = "✅" if self.diff_pct < 0.05 else "❌"
        return (
            f"{passing} 差异: {self.diff_pct:.2%} "
            f"(差异像素 {self.diff_count}/{self.total_pixels}, "
            f"最大偏差 {self.max_diff})"
        )


class VisualDiff:
    """视觉差异比较引擎。

    零额外依赖（仅使用 PIL）。
    所有 PIL 操作均可 mock，方便单元测试。
    """

    def __init__(self, diff_output_dir: str = "screenshots/diffs"):
        self.diff_output_dir = diff_output_dir

    # ── 核心 API ────────────────────────────────────────────

    def compare(self, candidate_path: str, baseline_path: str
                ) -> DiffResult:
        """
        比较候选截图与基准截图。

        参数:
            candidate_path: 当前截图路径
            baseline_path: 基准截图路径

        返回:
            DiffResult 包含像素差异统计
        """
        result = DiffResult(candidate_path, baseline_path)

        # 检查 baseline 存在
        if not os.path.exists(baseline_path):
            result.baseline_missing = True
            return result

        # 打开图片
        try:
            candidate_img = Image.open(candidate_path).convert("RGB")
            baseline_img = Image.open(baseline_path).convert("RGB")
        except Exception:
            result.baseline_missing = True
            return result

        # 检查尺寸
        if candidate_img.size != baseline_img.size:
            result.size_mismatch = True
            return result

        # 像素级差异计算
        diff_img = ImageChops.difference(candidate_img, baseline_img)
        # diff_img 是 RGB 三个通道的差值，合并为单通道灰度
        grayscale = diff_img.convert("L")

        # 转为像素数组做统计
        # 兼容 PIL 12+ (get_flattened_data) 和旧版本 (getdata)
        if hasattr(grayscale, "get_flattened_data"):
            pixels = list(grayscale.get_flattened_data())
        else:
            pixels = list(grayscale.getdata())
        result.total_pixels = len(pixels)
        # 差异像素：灰度值 > 0 的像素
        result.diff_count = sum(1 for p in pixels if p > 0)
        result.max_diff = max(pixels) if pixels else 0
        result.diff_pct = result.diff_count / max(result.total_pixels, 1)

        # 生成差异高亮图
        result.diff_image_path = self._generate_diff_image(
            candidate_img, baseline_img, candidate_path
        )

        return result

    def update_baseline(self, candidate_path: str, baseline_path: str
                        ) -> str:
        """
        将当前截图更新为新的基准，并返回 baseline 路径。
        """
        os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
        candidate_img = Image.open(candidate_path)
        candidate_img.save(baseline_path)
        return baseline_path

    # ── 差异高亮图 ──────────────────────────────────────────

    def _generate_diff_image(
        self,
        candidate: Image.Image,
        baseline: Image.Image,
        candidate_path: str
    ) -> str:
        """
        生成差异高亮图：将差异区域用红色叠加在候选图上。

        返回保存路径。
        """
        diff = ImageChops.difference(candidate, baseline)
        # 灰度掩码：差异像素为白色，相同为黑色
        gray = diff.convert("L")
        # 阈值：灰度值 > 15 视为差异（抗锯齿/压缩噪声）
        mask = gray.point(lambda p: 255 if p > 15 else 0)

        # 在候选图上叠加红色半透明覆盖
        overlay = Image.new("RGBA", candidate.size, (255, 0, 0, 0))
        overlay.putalpha(mask.point(lambda p: 128 if p > 15 else 0))

        result_img = candidate.convert("RGBA")
        result_img = Image.alpha_composite(result_img, overlay)

        # 保存
        os.makedirs(self.diff_output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(candidate_path))[0]
        out_path = os.path.join(self.diff_output_dir, f"{base_name}_diff.png")
        result_img.save(out_path, "PNG")
        return out_path


# ── pytest fixture ─────────────────────────────────────────

# 由 conftest.pytest_configure 设置，--update-baseline 时强制更新
UPDATE_BASELINE = False


def visual_regression_fixture(screenshot_manager, window,
                              baseline_name: str,
                              threshold: float = 0.05,
                              baseline_dir: str = "screenshots/baseline"):
    """
    视觉回归 fixture：截图 → 对比 baseline → 断言。

    使用方式（在 conftest.py 或测试文件中注册 fixture）：

        from wpf_testkit.utils.visual_diff import visual_regression_fixture

        def test_main_window(app_launch, main_window, screenshot_manager):
            vd = visual_regression_fixture(
                screenshot_manager, main_window,
                baseline_name="main_window",
            )
            assert vd.within_threshold(0.05), vd.summary()

    首次运行时 baseline 不存在不会失败，会自动创建 baseline。
    传入 --update-baseline 时强制更新 baseline（抛弃旧 baseline）。
    """
    os.makedirs(baseline_dir, exist_ok=True)
    baseline_path = os.path.join(baseline_dir, f"{baseline_name}.png")

    # 截图
    shot_path = screenshot_manager.capture(window, f"visreg_{baseline_name}")

    vd = VisualDiff()

    # --update-baseline 模式：强制更新，不比较
    if UPDATE_BASELINE:
        vd.update_baseline(shot_path, baseline_path)
        return DiffResult(shot_path, baseline_path)  # 视为通过

    result = vd.compare(shot_path, baseline_path)

    # 首次运行：没有 baseline，自动创建
    if result.baseline_missing:
        vd.update_baseline(shot_path, baseline_path)
        return DiffResult(shot_path, baseline_path)  # 视为通过

    return result
