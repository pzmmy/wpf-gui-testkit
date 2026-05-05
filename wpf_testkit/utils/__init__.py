"""wpf_testkit/utils/__init__.py — 工具模块导出

注意：所有 pywinauto 依赖使用延迟导入（Lazy Import），
确保在无 Windows UIA 环境（如 CI、WSL）中导入此模块不报错。
"""

from wpf_testkit.utils.uia_helpers import (  # noqa: E402
    dump_controls,
    get_desktop,
    find_window_by_title,
)


def select_files_via_open_dialog(*args, **kwargs):
    """延迟导入 win32_dialogs。"""
    from wpf_testkit.utils.win32_dialogs import select_files_via_open_dialog as _fn

    return _fn(*args, **kwargs)


def select_files_via_open_dialog_uia(*args, **kwargs):
    """延迟导入 win32_dialogs。"""
    from wpf_testkit.utils.win32_dialogs import select_files_via_open_dialog_uia as _fn

    return _fn(*args, **kwargs)


def wait_dialog_closed(*args, **kwargs):
    """延迟导入 win32_dialogs。"""
    from wpf_testkit.utils.win32_dialogs import wait_dialog_closed as _fn

    return _fn(*args, **kwargs)
