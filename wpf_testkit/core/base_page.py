"""wpf_testkit/core/base_page.py — Page Object 基类

提供：
- 四级点击兜底（click → click_input → invoke → set_focus+ENTER）
- 控件等待 / 文本获取 / 可见性判断
- 断言辅助
- 截图
"""
from __future__ import annotations

import os
import time
from typing import Optional, Dict, Callable

from pywinauto import Application


class BasePage:
    """WPF Page Object 基类。"""

    def __init__(self, app):
        """
        参数:
            app: pywinauto.Application 实例（或包含 .app 属性的 WindowSpecification）
        """
        self._window = None
        if isinstance(app, Application):
            self.app = app
        elif hasattr(app, '_WindowSpecification__app'):
            self.app = app._WindowSpecification__app
        else:
            raise TypeError(
                f"Expected pywinauto.Application, got {type(app).__name__}. "
                "Pass the Application object, not a WindowSpecification."
            )

    @property
    def window(self):
        """子类必须实现，返回目标窗口的 WindowSpecification。"""
        raise NotImplementedError

    # ── 等待 ──

    def wait_visible(self, timeout: float = 15):
        """等待窗口可见。"""
        return self.window.wait("visible", timeout=timeout)

    def wait_enabled(self, timeout: float = 10):
        """等待窗口可用。"""
        return self.window.wait("enabled", timeout=timeout)

    def wait_element_visible(self, auto_id: str, timeout: float = 10):
        """等待指定控件可见。"""
        ctrl = self.window.child_window(auto_id=auto_id)
        ctrl.wait("visible", timeout=timeout)
        return ctrl

    # ── 操作 ──

    def click_element(self, auto_id: str, timeout: float = 10,
                       debug: bool = False):
        """点击指定控件，自动降级兜底。

        降级链: click() → click_input() → invoke() → set_focus + ENTER

        参数:
            auto_id: 控件 AutomationId
            timeout: 等待控件可用的超时秒数
            debug: 为 True 时打印每次降级的详细日志
        """
        ctrl = self.window.child_window(auto_id=auto_id)
        ctrl.wait("enabled", timeout=timeout)

        strategies = [
            ("click", lambda: ctrl.click()),
            ("click_input", lambda: ctrl.click_input()),
            ("invoke", lambda: ctrl.invoke()),
            ("set_focus+ENTER", lambda: (
                ctrl.set_focus(), ctrl.type_keys("{ENTER}")
            )),
        ]
        last_error = None
        for name, action in strategies:
            try:
                action()
                if debug:
                    print(f"[BasePage] click_element({auto_id}) 使用: {name}")
                return
            except Exception as e:
                if debug:
                    print(f"[BasePage] click_element({auto_id}) {name} 失败: {e}")
                last_error = e
                continue
        raise RuntimeError(
            f"click_element 全部降级失败 ({auto_id}): {last_error}"
        )

    def click_input_element(self, auto_id: str, timeout: float = 10):
        """用 click_input 替代 click，适合 WPF 自定义控件。"""
        ctrl = self.window.child_window(auto_id=auto_id)
        ctrl.wait("enabled", timeout=timeout)
        try:
            ctrl.click_input()
        except Exception:
            ctrl.invoke()

    def set_text(self, auto_id: str, text: str, timeout: float = 10):
        """在文本框中输入内容。

        使用 Ctrl+A → Delete 清空已有内容（兼容 PasswordBox 等不支持 clear() 的控件）。
        """
        ctrl = self.window.child_window(auto_id=auto_id)
        ctrl.wait("enabled", timeout=timeout)
        ctrl.set_focus()
        ctrl.type_keys("^a{DELETE}")  # Ctrl+A 全选，Delete 删除
        ctrl.type_keys(text, with_spaces=True)

    def get_text(self, auto_id: str) -> str:
        """获取控件文本内容。"""
        ctrl = self.window.child_window(auto_id=auto_id)
        return ctrl.window_text() if ctrl.exists() else ""

    def is_element_visible(self, auto_id: str) -> bool:
        """判断控件是否可见。"""
        ctrl = self.window.child_window(auto_id=auto_id)
        return ctrl.exists() and ctrl.is_visible()

    def get_element_rectangle(self, auto_id: str):
        """获取控件矩形区域。"""
        ctrl = self.window.child_window(auto_id=auto_id)
        return ctrl.rectangle() if ctrl.exists() else None

    def invoke_command(self, command_name: str,
                       command_mapping: Optional[Dict[str, str]] = None):
        """通过 UIA InvokePattern 触发 WPF Command。

        参数:
            command_name: 命令名称（如 'PlayPauseCommand'）
            command_mapping: 命令名到 auto_id 的映射字典。
                             为 None 时尝试 'Cmd_{command_name}' 模式。
        """
        if command_mapping:
            ctrl_id = command_mapping.get(command_name)
            if ctrl_id:
                ctrl = self.window.child_window(auto_id=ctrl_id)
                ctrl.wait("enabled", timeout=5)
                ctrl.invoke()
                return True

        try:
            cmd_btn = self.window.child_window(auto_id=f"Cmd_{command_name}")
            if cmd_btn.exists():
                cmd_btn.invoke()
                return True
        except Exception:
            pass

        raise ValueError(f"无法通过 UIA 调用命令: {command_name}")

    # ── 截图 ──

    def screenshot(self, name: str, save_dir: str = "screenshots") -> str:
        """保存窗口截图。"""
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, f"{name}_{int(time.time())}.png")
        self.window.capture_as_image().save(path)
        return path

    # ── 断言 ──

    def assert_element_exists(self, auto_id: str, msg: str = ""):
        """断言控件存在。"""
        assert self.is_element_visible(auto_id), msg or f"控件 {auto_id} 不存在"

    def assert_element_text_contains(self, auto_id: str, expected: str):
        """断言控件文本包含预期内容。"""
        actual = self.get_text(auto_id)
        assert expected in actual, (
            f"期望包含 '{expected}'，实际: '{actual}'"
        )
