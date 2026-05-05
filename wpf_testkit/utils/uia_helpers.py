"""wpf_testkit/utils/uia_helpers.py — UIA 辅助工具

提供 UIA 控件树枚举、窗口查找。
Vision 增强：UIA 枚举返回 0 控件时自动用 Vision 描述补充。

注意：pywinauto 在函数内部延迟导入，避免无 Windows UIA 环境报错。
"""

from __future__ import annotations

from typing import Optional


def _get_desktop():
    """延迟获取 Desktop 对象。"""
    from pywinauto import Desktop

    return Desktop(backend="uia")


def dump_controls(
    window,
    max_depth: int = 5,
    use_vision: bool = True,
    window_title: str = "",
) -> str:
    """列举窗口下所有控件的 UIA 属性。

    默认启用 Vision 增强：UIA 找到 0 个控件时（分层窗口场景），
    自动用 Vision 视觉分析描述控件布局。

    参数:
        window: pywinauto WindowSpecification
        max_depth: UIA 递归深度限制（每个深度约 20 个控件）
        use_vision: 是否启用 Vision 增强
        window_title: 窗口标题（Vision 分析用的上下文）

    返回:
        格式化控件树文本
    """
    lines = []
    ctrls = window.descendants()
    lines.append(f"UIA descendants: {len(ctrls)}")
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

    # Vision 增强：UIA 为空时补充视觉描述
    if use_vision and len(ctrls) == 0:
        try:
            from wpf_testkit.vision import get_analyzer
            from PIL import ImageGrab

            va = get_analyzer()
            if va and va.available:
                snap = ImageGrab.grab()
                # 尝试从窗口取位置缩小截图范围
                try:
                    rect = window.rectangle()
                    snap = ImageGrab.grab(bbox=(
                        rect.left, rect.top, rect.right, rect.bottom
                    ))
                except Exception:
                    pass
                name = window_title or "窗口"
                prompt = (
                    f"详细描述此'{name}'弹窗中的所有可见UI元素。\n"
                    "按以下格式输出，每行一个控件：\n"
                    "[控件类型] - [文本/值] - [位置描述: 上/下/左/右/中/顶部/底部]\n"
                    "只列出你确定能看到的内容。\n"
                )
                result = va.analyze(snap, prompt)
                if result:
                    lines.append("")
                    lines.append(
                        f"=== Vision 控件描述（UIA 返回 0 个控件）==="
                    )
                    for line in result.split("\n"):
                        lines.append(f"  {line}")
        except ImportError:
            pass
        except Exception as e:
            lines.append(f"")
            lines.append(f"=== Vision 增强失败: {e} ===")

    return "\n".join(lines)


def get_desktop():
    """获取桌面对象。"""
    return _get_desktop()


def find_window_by_title(title: str, timeout: float = 5):
    """按标题查找顶层窗口。"""
    desktop = _get_desktop()
    return desktop.window(title=title, control_type="Window")
