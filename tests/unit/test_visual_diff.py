"""test_visual_diff.py — 视觉回归引擎自测

使用真实 PIL 生成纯色测试图像验证 diff 逻辑。
可在任何有 PIL 的环境运行（不需要 Windows UIA）。
"""
from __future__ import annotations

import os
import tempfile
import shutil

import pytest
from PIL import Image

from wpf_testkit.utils.visual_diff import VisualDiff, DiffResult


@pytest.fixture
def tmp_dir():
    """临时目录作为图片存放路径。"""
    d = tempfile.mkdtemp(prefix="vdiff_")
    yield d
    shutil.rmtree(d)


@pytest.fixture
def vd(tmp_dir):
    """VisualDiff 实例，diff 输出使用临时目录。"""
    diff_dir = os.path.join(tmp_dir, "diffs")
    return VisualDiff(diff_output_dir=diff_dir)


def _create_image(width, height, color, path):
    """创建纯色 PNG 图像。"""
    img = Image.new("RGB", (width, height), color)
    img.save(path, format="PNG")
    return path


# ═══════════════════════════════════════════════════════
# DiffResult
# ═══════════════════════════════════════════════════════

class TestDiffResult:
    def test_default_passed(self):
        dr = DiffResult("a.png", "b.png")
        assert dr.passed is True  # 默认无异常

    def test_baseline_missing_not_passed(self):
        dr = DiffResult("a.png", "b.png")
        dr.baseline_missing = True
        assert dr.passed is False

    def test_size_mismatch_not_passed(self):
        dr = DiffResult("a.png", "b.png")
        dr.size_mismatch = True
        assert dr.passed is False

    def test_within_threshold(self):
        dr = DiffResult("a.png", "b.png")
        dr.diff_pct = 0.03
        assert dr.within_threshold(0.05) is True
        assert dr.within_threshold(0.01) is False

    def test_within_threshold_fails_when_missing(self):
        dr = DiffResult("a.png", "b.png")
        dr.baseline_missing = True
        assert dr.within_threshold(0.99) is False

    def test_within_threshold_fails_when_size_mismatch(self):
        dr = DiffResult("a.png", "b.png")
        dr.size_mismatch = True
        assert dr.within_threshold(0.99) is False

    def test_summary_baseline_missing(self):
        dr = DiffResult("a.png", "b.png")
        dr.baseline_missing = True
        assert "Baseline 不存在" in dr.summary()

    def test_summary_size_mismatch(self):
        dr = DiffResult("a.png", "b.png")
        dr.size_mismatch = True
        assert "尺寸不匹配" in dr.summary()

    def test_summary_diff(self):
        dr = DiffResult("a.png", "b.png")
        dr.diff_pct = 0.12
        dr.diff_count = 120
        dr.total_pixels = 1000
        dr.max_diff = 200
        s = dr.summary()
        assert "12" in s or "12.00" in s
        assert "120/1000" in s


# ═══════════════════════════════════════════════════════
# VisualDiff.compare
# ═══════════════════════════════════════════════════════

class TestVisualDiffCompare:
    def test_baseline_missing(self, tmp_dir, vd):
        candidate = os.path.join(tmp_dir, "candidate.png")
        baseline = os.path.join(tmp_dir, "nonexistent.png")
        _create_image(100, 100, (255, 0, 0), candidate)

        result = vd.compare(candidate, baseline)
        assert result.baseline_missing is True
        assert result.passed is False

    def test_identical_images(self, tmp_dir, vd):
        candidate = os.path.join(tmp_dir, "candidate.png")
        baseline = os.path.join(tmp_dir, "baseline.png")
        _create_image(100, 100, (0, 128, 255), candidate)
        _create_image(100, 100, (0, 128, 255), baseline)

        result = vd.compare(candidate, baseline)
        assert result.passed is True
        assert result.diff_pct == 0.0
        assert result.diff_count == 0
        assert result.max_diff == 0

    def test_completely_different_images(self, tmp_dir, vd):
        candidate = os.path.join(tmp_dir, "candidate.png")
        baseline = os.path.join(tmp_dir, "baseline.png")
        _create_image(100, 100, (255, 255, 255), candidate)
        _create_image(100, 100, (0, 0, 0), baseline)

        result = vd.compare(candidate, baseline)
        assert result.passed is True
        assert result.diff_pct == 1.0  # 每个像素都不同
        assert result.diff_count == 100 * 100
        assert result.max_diff > 0

    def test_partial_difference(self, tmp_dir, vd):
        """一张 10x10 图——一半相同一半不同。"""
        candidate = os.path.join(tmp_dir, "candidate.png")
        baseline = os.path.join(tmp_dir, "baseline.png")

        img_a = Image.new("RGB", (10, 10), (100, 100, 100))
        for x in range(5, 10):
            for y in range(10):
                img_a.putpixel((x, y), (200, 200, 200))

        img_b = Image.new("RGB", (10, 10), (100, 100, 100))

        img_a.save(candidate)
        img_b.save(baseline)

        result = vd.compare(candidate, baseline)
        assert result.passed is True
        # 5*10 = 50 个像素不同，总 100 像素
        assert result.diff_count == 50
        assert result.diff_pct == 0.5
        assert result.diff_image_path != ""

    def test_size_mismatch(self, tmp_dir, vd):
        candidate = os.path.join(tmp_dir, "candidate.png")
        baseline = os.path.join(tmp_dir, "baseline.png")
        _create_image(100, 100, (0, 0, 0), candidate)
        _create_image(200, 100, (0, 0, 0), baseline)

        result = vd.compare(candidate, baseline)
        assert result.size_mismatch is True
        assert result.passed is False

    def test_diff_image_generated(self, tmp_dir, vd):
        """差异高亮图应被生成且存在。"""
        candidate = os.path.join(tmp_dir, "candidate.png")
        baseline = os.path.join(tmp_dir, "baseline.png")
        _create_image(50, 50, (255, 255, 255), candidate)
        _create_image(50, 50, (0, 0, 0), baseline)

        result = vd.compare(candidate, baseline)
        assert os.path.exists(result.diff_image_path)
        # 验证是有效 PNG
        with Image.open(result.diff_image_path) as img:
            assert img.size == (50, 50)

    def test_visual_regression_happy_path(self, tmp_dir, vd):
        """完整的视觉回归流程。"""
        shot = os.path.join(tmp_dir, "visreg_main.png")
        baseline = os.path.join(tmp_dir, "baseline_main.png")
        _create_image(200, 150, (50, 100, 150), shot)
        _create_image(200, 150, (50, 100, 150), baseline)

        result = vd.compare(shot, baseline)
        assert result.within_threshold(0.01) is True

    def test_visual_regression_fails_on_change(self, tmp_dir, vd):
        """UI 变化后视觉回归应失败。"""
        shot = os.path.join(tmp_dir, "visreg_changed.png")
        baseline = os.path.join(tmp_dir, "baseline_original.png")
        _create_image(200, 150, (255, 0, 0), shot)   # 红色
        _create_image(200, 150, (0, 0, 255), baseline)  # 蓝色

        result = vd.compare(shot, baseline)
        assert result.within_threshold(0.05) is False  # 全部不同


# ═══════════════════════════════════════════════════════
# VisualDiff.update_baseline
# ═══════════════════════════════════════════════════════

class TestUpdateBaseline:
    def test_update_baseline_creates_file(self, tmp_dir, vd):
        candidate = os.path.join(tmp_dir, "shot.png")
        baseline = os.path.join(tmp_dir, "baseline", "main.png")
        _create_image(100, 80, (0, 255, 0), candidate)

        result_path = vd.update_baseline(candidate, baseline)
        assert result_path == baseline
        assert os.path.exists(baseline)

        # 验证内容一致
        with Image.open(baseline) as img:
            assert img.size == (100, 80)
