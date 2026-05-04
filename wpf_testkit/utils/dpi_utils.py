"""wpf_testkit/utils/dpi_utils.py — DPI 缩放适配工具"""
from __future__ import annotations

from pywinauto import Desktop


def get_dpi_scale() -> float:
    """获取当前 DPI 缩放比例。"""
    try:
        desktop = Desktop(backend="uia")
        # 取任务栏高度来估算 DPI（任务栏通常 ~40px at 100%）
        taskbar = desktop.window(class_name="Shell_TrayWnd")
        if taskbar.exists():
            rect = taskbar.rectangle()
            taskbar_height = rect.height()
            # 100% DPI 时任务栏高度约为 40
            return taskbar_height / 40.0
    except Exception:
        pass
    return 1.0


def scale_coordinate(value: int, dpi_scale: float = None) -> int:
    """根据 DPI 缩放坐标。"""
    if dpi_scale is None:
        dpi_scale = get_dpi_scale()
    return int(value * dpi_scale)
