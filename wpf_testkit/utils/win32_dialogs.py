"""wpf_testkit/utils/win32_dialogs.py — Win32 系统对话框自动化

提供 SendKeys + UIA 双通道操作 Win32 对话框（OpenFileDialog、SaveFileDialog、FolderBrowserDialog）。

设计原则：
- 优先使用 SendKeys 键盘模拟（最通用，不受 UIA 树结构影响）
- 降级到 UIA 控件查找（适配不同 Windows 版本）
- 零额外依赖（仅用 pywinauto 已有的 send_keys 和 Desktop）

使用示例：
    from wpf_testkit.utils.win32_dialogs import select_files_via_open_dialog

    def test_select_mp3(page):
        page.click_select_files()  # 触发 OpenFileDialog
        result = select_files_via_open_dialog(
            page.app,
            [r"C:\\test\\01.mp3"],
            dialog_title="选择媒体文件"
        )
        assert result
        assert page.get_file_count() > 0
"""

from __future__ import annotations

import time
from typing import List, Optional

from pywinauto import Desktop, Application
from pywinauto.keyboard import send_keys


def select_files_via_open_dialog(
    app: Application,
    file_paths: List[str],
    dialog_title: str = "打开",
    wait_after_click: float = 1.0,
    timeout: float = 8.0,
) -> bool:
    """通过 Win32 OpenFileDialog 选择一个或多个文件。

    工作流程：
    1. 调用方先点击触发对话框的按钮（此函数不负责触发）
    2. 此函数等待对话框弹出
    3. SendKeys 直接输入路径（多个路径用双引号包裹）
    4. 按 Enter 确认

    参数:
        app: pywinauto Application 实例
        file_paths: 要选择的文件完整路径列表
        dialog_title: OpenFileDialog 的 Title 属性值
        wait_after_click: 对话框弹出等待时间（秒）
        timeout: 对话框等待超时（秒）

    返回:
        True 表示对话框已操作（是否成功由测试用例验证）
    """
    time.sleep(wait_after_click)

    desktop = Desktop(backend="uia")
    dialog = desktop.window(title=dialog_title, control_type="Window")

    try:
        dialog.wait("visible", timeout=timeout)
    except Exception:
        return False

    # ── 方案 A（首选）：SendKeys 键盘输入路径 ──
    # OpenFileDialog 弹出后默认焦点在"文件名(N):"输入框
    # 多个文件路径用空格分隔，每个路径用双引号包裹（处理路径中的空格）
    time.sleep(0.3)  # 等焦点稳定

    if len(file_paths) == 1:
        keys = file_paths[0]
    else:
        keys = " ".join(f'"{p}"' for p in file_paths)

    send_keys(keys, pause=0.03)
    time.sleep(0.2)
    send_keys("{ENTER}", pause=0.05)
    return True


def select_files_via_open_dialog_uia(
    file_paths: List[str],
    dialog_title: str = "打开",
    timeout: float = 8.0,
) -> bool:
    """通过 UIA 查找 OpenFileDialog 内部控件选择文件。

    方案 A（SendKeys）的备选方案，适配 UIA 树结构不同的系统。
    部分系统上 OpenFileDialog 的 Edit 控件可能有 auto_id="FileNameControlHost"。

    返回:
        True 表示对话框已操作
    """
    time.sleep(1.0)

    desktop = Desktop(backend="uia")
    dialog = desktop.window(title=dialog_title, control_type="Window")

    try:
        dialog.wait("visible", timeout=timeout)
    except Exception:
        return False

    # 尝试通过 auto_id 找文件名输入框（Win10 较新版本）
    file_edit = dialog.child_window(auto_id="FileNameControlHost")
    if not file_edit.exists():
        # 备选：找所有 Edit 控件（通常第一个是文件名输入框）
        edits = dialog.descendants(control_type="Edit")
        if edits:
            file_edit = edits[0]

    if file_edit.exists():
        file_edit.set_focus()
        file_edit.type_keys("^a{DELETE}", pause=0.02)
        file_edit.type_keys(file_paths[0], pause=0.02)

    # 找"打开(O)"按钮
    open_btn = dialog.child_window(title="打开(&O)")
    if not open_btn.exists():
        open_btn = dialog.child_window(title="打开")
    if not open_btn.exists():
        # 按 class_name 找
        btns = dialog.descendants(control_type="Button")
        for btn in btns:
            text = btn.window_text()
            if "打开" in text or "Open" in text:
                open_btn = btn
                break

    if open_btn.exists():
        open_btn.click_input()
    else:
        # 兜底：Enter
        send_keys("{ENTER}")

    return True


def wait_dialog_closed(
    dialog_title: str,
    timeout: float = 5.0,
) -> bool:
    """等待指定标题的对话框关闭。

    用于验证文件选择/保存操作确实完成了。
    """
    desktop = Desktop(backend="uia")
    dialog = desktop.window(title=dialog_title, control_type="Window")
    try:
        dialog.wait_not("visible", timeout=timeout)
        return True
    except Exception:
        return False
