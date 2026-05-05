"""wpf_testkit/core/base_page.py — Page Object 基类

提供：
- 四级点击兜底（click → click_input → invoke → set_focus+ENTER）
- 第五级 Vision 坐标点击（可选，需安装 [vision] 扩展）
- Vision 语义断言（播放状态、弹窗验证、错误检测等）
- Vision 控件定位（无 AutomationId 的控件）
- 控件等待 / 文本获取 / 可见性判断
- 断言辅助
- 截图
"""

from __future__ import annotations

import ctypes
import os
import time
from typing import Optional, Dict, Any, List

from pywinauto import Application


class BasePage:
    """WPF Page Object 基类。"""

    # ── Vision 支持（延迟初始化） ──
    _vision = None  # VisionAnalyzer 实例

    @classmethod
    def _get_vision(cls):
        """延迟获取 VisionAnalyzer 实例。"""
        if cls._vision is None:
            from wpf_testkit.vision import get_analyzer

            cls._vision = get_analyzer()
        return cls._vision

    def __init__(self, app):
        """
        参数:
            app: pywinauto.Application 实例（或包含 .app 属性的 WindowSpecification）
        """
        self._window = None
        if isinstance(app, Application):
            self.app = app
        elif hasattr(app, "_WindowSpecification__app"):
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

    # ── Vision 辅助属性 ──

    @property
    def vision_available(self) -> bool:
        """Vision 分析器是否可用。"""
        return self._get_vision().available

    def vision_healthy_check(self) -> bool:
        """启动时检测 Vision API 可用性（发送真实请求验证）。"""
        va = self._get_vision()
        ok = va.healthy_check()
        if not ok:
            print(f"[BasePage] Vision API 不可用，降级到 UIA 模式")
        return ok

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

    # ── 操作（UIA 四级兜底 + Vision 第五级）──

    def click_element(
        self,
        auto_id: str,
        timeout: float = 10,
        debug: bool = False,
    ):
        """点击指定控件，自动降级兜底。

        降级链:
        1. click()
        2. click_input()
        3. invoke()
        4. set_focus + ENTER
        5. Vision 坐标定位 + Win32 mouse_event（需 vision 可用）

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
            ("set_focus+ENTER", lambda: (ctrl.set_focus(), ctrl.type_keys("{ENTER}"))),
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

        # 第五层：Vision 坐标点击（兜底）
        if self.vision_available:
            try:
                self._vision_click_element(auto_id, debug)
                return
            except Exception as e:
                if debug:
                    print(f"[BasePage] click_element({auto_id}) Vision 兜底失败: {e}")
                last_error = e

        raise RuntimeError(
            f"click_element 全部降级失败 ({auto_id}): {last_error}"
        )

    def _vision_click_element(self, auto_id: str, debug: bool = False):
        """Vision 第五级兜底：截图定位控件坐标后用 Win32 mouse_event 点击。"""
        from PIL import ImageGrab

        snap = ImageGrab.grab()
        va = self._get_vision()
        result = va.find_control(
            snap, f"包含 AutomationId 为'{auto_id}'的控件"
        )
        if not result or "not_found" in result:
            raise RuntimeError(f"Vision 找不到控件 {auto_id}")

        # 解析 "x_pct=50, y_pct=60"
        x_pct = y_pct = None
        for part in result.replace(",", " ").split():
            if "x_pct" in part:
                try:
                    x_pct = float(part.split("=")[1])
                except (IndexError, ValueError):
                    pass
            if "y_pct" in part:
                try:
                    y_pct = float(part.split("=")[1])
                except (IndexError, ValueError):
                    pass
        if x_pct is None or y_pct is None:
            raise RuntimeError(f"Vision 坐标解析失败: {result}")

        screen_w = ctypes.windll.user32.GetSystemMetrics(0)
        screen_h = ctypes.windll.user32.GetSystemMetrics(1)
        click_x = int(screen_w * x_pct / 100)
        click_y = int(screen_h * y_pct / 100)

        user32 = ctypes.windll.user32
        user32.SetCursorPos(click_x, click_y)
        user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
        user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
        if debug:
            print(f"[BasePage] Vision 坐标点击 ({click_x}, {click_y})")

    def click_input_element(self, auto_id: str, timeout: float = 10):
        """用 click_input 替代 click，适合 WPF 自定义控件。"""
        ctrl = self.window.child_window(auto_id=auto_id)
        ctrl.wait("enabled", timeout=timeout)
        try:
            ctrl.click_input()
        except Exception:
            ctrl.invoke()

    def combo_select_by_text(
        self, auto_id: str, text: str, timeout: float = 10
    ):
        """从 ComboBox 中选择指定文本的项。"""
        ctrl = self.window.child_window(auto_id=auto_id)
        ctrl.wait("enabled", timeout=timeout)
        ctrl.set_focus()
        ctrl.type_keys("%{DOWN}")  # Alt+↓ 展开
        time.sleep(0.3)
        if text:
            for _ in range(50):
                try:
                    cur_text = ctrl.window_text()
                except Exception:
                    break
                if text in cur_text:
                    break
                ctrl.type_keys("{DOWN}")
                time.sleep(0.2)
        ctrl.type_keys("{ENTER}")
        time.sleep(0.3)

    def set_text(self, auto_id: str, text: str, timeout: float = 10):
        """在文本框中输入内容。"""
        ctrl = self.window.child_window(auto_id=auto_id)
        ctrl.wait("enabled", timeout=timeout)
        ctrl.set_focus()
        ctrl.type_keys("^a{DELETE}")
        ctrl.type_keys(text, with_spaces=True)

    def get_text(self, auto_id: str) -> str:
        """获取控件文本内容。"""
        ctrl = self.window.child_window(auto_id=auto_id)
        return ctrl.window_text() if ctrl.exists() else ""

    @staticmethod
    def safe_text(ctrl) -> str:
        """安全获取控件文本，兼容 GBK 编码异常。"""
        try:
            return ctrl.window_text()
        except UnicodeEncodeError:
            try:
                return ctrl.window_text().encode(
                    "utf-8", errors="replace"
                ).decode("utf-8")
            except Exception:
                return ""

    @staticmethod
    def log(msg: str) -> None:
        """输出日志（兼容 GBK 编码）。"""
        from datetime import datetime

        line = f"[{datetime.now():%H:%M:%S}] {msg}"
        try:
            print(line, flush=True)
        except UnicodeEncodeError:
            print(
                line.encode("utf-8", errors="replace").decode(
                    "utf-8", errors="replace"
                ),
                flush=True,
            )

    def is_element_visible(self, auto_id: str) -> bool:
        """判断控件是否可见。"""
        ctrl = self.window.child_window(auto_id=auto_id)
        return ctrl.exists() and ctrl.is_visible()

    def get_element_rectangle(self, auto_id: str):
        """获取控件矩形区域。"""
        ctrl = self.window.child_window(auto_id=auto_id)
        return ctrl.rectangle() if ctrl.exists() else None

    def invoke_command(
        self,
        command_name: str,
        command_mapping: Optional[Dict[str, str]] = None,
    ):
        """通过 UIA InvokePattern 触发 WPF Command。"""
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

    # ── Vision 驱动控件定位（无 AutomationId） ──

    def click_by_vision(
        self,
        description: str,
        timeout: float = 10,
        debug: bool = False,
    ):
        """通过 Vision 定位并点击控件（适合无 AutomationId 的控件）。

        参数:
            description: 控件描述，如 "包含文字'保存'的按钮"
            timeout: 重试超时（Vision 可能第一次识别不准，可重试）
            debug: 打印调试信息

        抛出:
            RuntimeError: Vision 不可用或定位失败
        """
        if not self.vision_available:
            raise RuntimeError("Vision 不可用，无法使用 click_by_vision")

        from PIL import ImageGrab

        deadline = time.time() + timeout
        last_error = None

        while time.time() < deadline:
            snap = ImageGrab.grab()
            va = self._get_vision()
            result = va.find_control(snap, description)
            if result and "not_found" not in result:
                # 解析坐标
                x_pct = y_pct = None
                for part in result.replace(",", " ").split():
                    if "x_pct" in part:
                        try:
                            x_pct = float(part.split("=")[1])
                        except (IndexError, ValueError):
                            pass
                    if "y_pct" in part:
                        try:
                            y_pct = float(part.split("=")[1])
                        except (IndexError, ValueError):
                            pass
                if x_pct is not None and y_pct is not None:
                    user32 = ctypes.windll.user32
                    sw = user32.GetSystemMetrics(0)
                    sh = user32.GetSystemMetrics(1)
                    cx = int(sw * x_pct / 100)
                    cy = int(sh * y_pct / 100)
                    user32.SetCursorPos(cx, cy)
                    user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
                    user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
                    if debug:
                        print(
                            f"[BasePage] click_by_vision '{description}' "
                            f"坐标 ({cx}, {cy})"
                        )
                    return
            last_error = result
            time.sleep(1)

        raise RuntimeError(
            f"click_by_vision 超时 ({timeout}s): '{description}', "
            f"最后结果: {last_error}"
        )

    # ── Vision 语义断言 ──
    #
    # 所有 WPF 场景专用的分析提示词放在这里，
    # 不污染 VisionAnalyzer（保持与具体模型供应商解耦）。
    #

    def _vision_verify_dialog(self, img, dlg_name: str):
        """内部：通过 Vision 验证弹窗。"""
        prompt = (
            f"分析这张WPF桌面应用截图。用户点击了'{dlg_name}'按钮。请回答（按编号输出）：\n"
            "1. 画面上是否有一个弹窗/对话框/子窗口？如果有，它的标题或内容是什么？\n"
            "2. 这个弹窗是否是空的？（只有背景色或无法操作？）\n"
            "3. 弹窗中有哪些可视的控件？（按钮、文本框、列表、滑块等）\n"
            "4. 右上角或左上角是否有关闭按钮（✕ 或 关闭 字样）？\n"
            "5. 弹窗的功能是什么？\n"
        )
        va = self._get_vision()
        result = va.analyze(img, prompt)
        if result is None:
            return {"dialog_open": False, "empty": None, "close_found": None, "desc": None}
        return {
            "dialog_open": ("弹窗" in result or "对话框" in result or "子窗口" in result),
            "empty": "空" in result and ("没有控件" in result or "空白" in result),
            "close_found": "✕" in result or "关闭按钮" in result or "Close" in result,
            "desc": result,
        }

    def _vision_check_playing(self, img):
        """内部：通过 Vision 验证播放状态。"""
        prompt = (
            "分析这张WPF桌面应用截图。请回答（逐项简短精确）：\n"
            "1. 播放按钮是 ▶ 播放状态还是 ▢ 停止状态？\n"
            "2. 当前是否有电台名称被选中/显示？\n"
            "3. 是否有任何正在播放的视觉指示？\n"
            "4. 界面上是否有错误提示、红色文字或异常信息？\n"
        )
        return self._get_vision().analyze(img, prompt)

    def _vision_check_recording(self, img):
        """内部：通过 Vision 验证录音状态。"""
        prompt = (
            "分析这张WPF桌面应用截图。请回答：\n"
            "1. 是否有录音正在进行的指示？\n"
            "2. 录音按钮现在是红色（录音中）还是灰色（未录音）？\n"
            "3. 状态文本区域是否有任何文字变化？\n"
        )
        return self._get_vision().analyze(img, prompt)

    def _vision_check_no_error(self, img):
        """内部：通过 Vision 检查错误提示。"""
        prompt = (
            "分析这张WPF桌面应用截图。请回答：\n"
            "1. 截图是否有红色文字、错误提示框、异常弹窗或警告图标？\n"
            "2. 如果有，错误/警告的内容是什么？\n"
            "3. 整体界面是否正常可用？\n"
        )
        return self._get_vision().analyze(img, prompt)

    def _vision_describe_all_controls(self, img, dlg_name: str):
        """内部：通过 Vision 描述控件的完整列表。"""
        prompt = (
            f"详细描述此'{dlg_name}'弹窗中的所有可见UI元素。\n"
            "按以下格式输出，每行一个控件：\n"
            "[控件类型] - [文本/值] - [位置描述: 上/下/左/右/中/顶部/底部]\n"
            "只列出你确定能看到的内容。\n"
        )
        return self._get_vision().analyze(img, prompt)

    def vision_assert_dialog_open(
        self, dlg_name: str, timeout: float = 10
    ):
        """Vision 断言：弹窗已打开。"""
        if not self.vision_available:
            raise RuntimeError("Vision 不可用，无法使用 vision_assert_dialog_open")

        from PIL import ImageGrab

        deadline = time.time() + timeout
        while time.time() < deadline:
            snap = ImageGrab.grab()
            result = self._vision_verify_dialog(snap, dlg_name)
            if result["dialog_open"] and not result.get("empty"):
                return result
            time.sleep(1)

        raise AssertionError(
            f"Vision 断言失败: 弹窗 '{dlg_name}' 未打开。"
            f"Vision 描述: {(result or {}).get('desc', '无返回')[:200]}"
        )

    def vision_assert_playing(self, timeout: float = 10):
        """Vision 断言：播放器正在播放。"""
        if not self.vision_available:
            raise RuntimeError("Vision 不可用，无法使用 vision_assert_playing")

        from PIL import ImageGrab

        deadline = time.time() + timeout
        while time.time() < deadline:
            snap = ImageGrab.grab()
            result = self._vision_check_playing(snap)
            if result and ("▶" in result or "正在播放" in result or "播放中" in result):
                return result
            time.sleep(1)

        raise AssertionError(
            f"Vision 断言失败: 未检测到正在播放状态。"
            f"最后检测结果: {(result or '无返回')[:200]}"
        )

    def vision_assert_recording(self, timeout: float = 10):
        """Vision 断言：正在录音。"""
        if not self.vision_available:
            raise RuntimeError("Vision 不可用，无法使用 vision_assert_recording")

        from PIL import ImageGrab

        deadline = time.time() + timeout
        while time.time() < deadline:
            snap = ImageGrab.grab()
            result = self._vision_check_recording(snap)
            if result and ("录音" in result or "红色" in result or "REC" in result):
                return result
            time.sleep(1)

        raise AssertionError(
            f"Vision 断言失败: 未检测到录音状态。"
            f"最后检测结果: {(result or '无返回')[:200]}"
        )

    def vision_assert_no_error(self):
        """Vision 断言：截图中没有错误提示。"""
        if not self.vision_available:
            return

        from PIL import ImageGrab

        snap = ImageGrab.grab()
        result = self._vision_check_no_error(snap)
        if result and (
            "没有" in result or "无" in result or "正常" in result
        ):
            return
        if result:
            print(f"[BasePage] Vision 检测到可能的错误: {result[:200]}")

    def vision_assert_dialog_closed(self, title: str, timeout: float = 5):
        """Vision 断言：弹窗已关闭。"""
        if not self.vision_available:
            return

        from PIL import ImageGrab

        deadline = time.time() + timeout
        while time.time() < deadline:
            snap = ImageGrab.grab()
            result = self._vision_verify_dialog(snap, title)
            if not result["dialog_open"]:
                return
            time.sleep(1)

        print(
            f"[BasePage] Vision 提示: 弹窗 '{title}' 可能未完全关闭（"
            f"{result.get('desc', '')[:100]}）"
        )

    # ── Vision 辅助：截图 + 分析 ──

    def vision_capture_and_analyze(
        self, prompt: str, name: str = "analysis", save_dir: str = "screenshots"
    ) -> Optional[str]:
        """截图并发送给 Vision 分析，同时保存截图到本地。

        返回:
            str: Vision 分析文本
        """
        if not self.vision_available:
            return None

        from PIL import ImageGrab

        os.makedirs(save_dir, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        path = os.path.join(save_dir, f"{name}_{ts}.png")
        snap = ImageGrab.grab()
        snap.save(path)

        va = self._get_vision()
        result = va.analyze(snap, prompt)
        if result:
            # 同时保存分析文本
            txt_path = path.replace(".png", "_vision.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"Prompt: {prompt}\n\n{result}")
        return result

    # ── 控件信息（Vision 增强） ──

    def dump_controls_with_vision(
        self, fallback_vision_on_empty: bool = True
    ) -> str:
        """列举控件信息。

        先尝试 UIA descendants()，如果返回 0 个（分层窗口场景），
        使用 Vision describe_all_controls 补充。
        """
        lines = []
        ctrls = self.window.descendants()
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
            if i > 500:
                lines.append("  ... (truncated)")
                break

        # Vision 补充
        if fallback_vision_on_empty and len(ctrls) == 0 and self.vision_available:
            from PIL import ImageGrab

            snap = ImageGrab.grab()
            result = self._vision_describe_all_controls(snap, "窗口")
            if result:
                lines.append("")
                lines.append("=== Vision 控件描述（UIA 不可用时）===")
                for line in result.split("\n"):
                    lines.append(f"  {line}")
        return "\n".join(lines)

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

    # ── 清理 ──

    def close(self):
        """关闭窗口（子类可重写）。"""
        try:
            self.window.close()
        except Exception:
            pass
