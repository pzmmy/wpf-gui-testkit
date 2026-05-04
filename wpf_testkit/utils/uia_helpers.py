"""wpf_testkit/utils/uia_helpers.py — UIA 辅助工具"""
from __future__ import annotations

from pywinauto import Desktop


def dump_controls(window, max_depth: int = 5) -> str:
    """列举窗口下所有控件的 UIA 属性。"""
    lines = []
    ctrls = window.descendants()
    lines.append(f"Total descendants: {len(ctrls)}")
    lines.append(f"{'#':>4}  {'class':<30} {'aid':<30} {'text'}")
    lines.append("-" * 100)
    for i, c in enumerate(ctrls):
        try:
            aid = c.element_info.automation_id or ""
            cls = c.element_info.class_name or ""
            txt = c.window_text()[:50] if c.window_text() else ""
            lines.append(f"{i:>4}  {cls:<30} {aid:<30} {txt}")
        except Exception as e:
            lines.append(f"{i:>4}  ERROR: {e}")
        if i > max_depth * 20:
            lines.append("  ... (truncated)")
            break
    return "\n".join(lines)


def get_desktop() -> Desktop:
    """获取桌面对象。"""
    return Desktop(backend="uia")


def find_window_by_title(title: str, timeout: float = 5):
    """按标题查找顶层窗口。"""
    desktop = get_desktop()
    return desktop.window(title=title, control_type="Window")
