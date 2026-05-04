"""wpf_testkit/utils/dpi_utils.py — DPI 缩放适配工具"""
from __future__ import annotations

from pywinauto import Desktop


def get_dpi_scale() -> float:
    """获取当前 DPI 缩放比例。

    通过任务栏矩形取最短边长估算。
    支持任务栏在任意方向（底部/顶部/左侧/右侧）。
    """
    try:
        desktop = Desktop(backend="uia")
        # 取任务栏来估算 DPI
        taskbar = desktop.window(class_name="Shell_TrayWnd")
        if taskbar.exists():
            rect = taskbar.rectangle()
            # 取最短边（无论任务栏水平还是垂直放置，任务栏的短边 ≈ 40px at 100%）
            short_side = min(rect.width(), rect.height())
            # 100% DPI 时任务栏短边约为 40
            return short_side / 40.0
    except Exception:
        pass
    return 1.0


def scale_coordinate(value: int, dpi_scale: float = None) -> int:
    """根据 DPI 缩放坐标。"""
    if dpi_scale is None:
        dpi_scale = get_dpi_scale()
    return int(value * dpi_scale)
