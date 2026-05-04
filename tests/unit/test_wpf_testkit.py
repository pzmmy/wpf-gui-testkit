"""wpf_testkit 框架自测 — 纯逻辑测试，不依赖真实 WPF 窗口。

pywinauto 调用被 mock，可在无 Windows UIA 环境（如 WSL、CI）运行。
"""
from __future__ import annotations

import sys
import os
import time
from unittest.mock import MagicMock, patch

import pytest

# ─── 在导入被测试模块前 mock pywinauto ──────────────────
# 注意：不 mock PIL，避免影响同进程中的 test_visual_diff.py

sys.modules["pywinauto"] = MagicMock()
sys.modules["pywinauto.Desktop"] = MagicMock()
sys.modules["pywinauto.Application"] = MagicMock()
sys.modules["pywinauto.timings"] = MagicMock()
sys.modules["pywinauto.timings.Timings"] = MagicMock()
import pywinauto


class FakeAppClass:
    """伪造的 pywinauto.Application 类。"""
    pass


pywinauto.Application = FakeAppClass

from wpf_testkit.exceptions import (
    ElementNotFoundError,
    CommandInvokeError,
    CrashDetectedError,
)
from wpf_testkit.utils.screenshot import ScreenshotManager
from wpf_testkit.utils.crash_daemon import CrashDaemon
from wpf_testkit.utils.uia_helpers import dump_controls, find_window_by_title


# ═══════════════════════════════════════════════════════
# exceptions.py
# ═══════════════════════════════════════════════════════

class TestExceptions:
    def test_element_not_found_error(self):
        err = ElementNotFoundError("BtnTest 不存在")
        assert "BtnTest" in str(err)
        assert isinstance(err, Exception)

    def test_command_invoke_error(self):
        err = CommandInvokeError("点击失败")
        assert "点击失败" in str(err)

    def test_crash_detected_error(self):
        err = CrashDetectedError("进程已退出")
        assert "进程" in str(err)

    def test_raise_and_catch(self):
        with pytest.raises(ElementNotFoundError):
            raise ElementNotFoundError("not found")
        with pytest.raises(CommandInvokeError):
            raise CommandInvokeError("invoke fail")
        with pytest.raises(CrashDetectedError):
            raise CrashDetectedError("crash")


# ═══════════════════════════════════════════════════════
# screenshot.py
# ═══════════════════════════════════════════════════════

class TestScreenshotManager:
    def test_init_creates_dirs(self, tmp_path):
        save_dir = str(tmp_path / "shots")
        _ = ScreenshotManager(save_dir)
        assert os.path.exists(save_dir)
        assert os.path.exists(os.path.join(save_dir, "baseline"))
        assert os.path.exists(os.path.join(save_dir, "failures"))
    def test_capture_fallback_on_failure(self, tmp_path):
        save_dir = str(tmp_path / "shots")
        sm = ScreenshotManager(save_dir)
        bad_window = MagicMock()
        bad_window.capture_as_image.side_effect = RuntimeError("no screen")
        path = sm.capture(bad_window, "test_fail")
        assert path.endswith(".txt"), f"应回退为 .txt，实际: {path}"
        assert os.path.exists(path)

    def test_capture_roi_handles_non_png_fallback(self, tmp_path):
        save_dir = str(tmp_path / "shots")
        sm = ScreenshotManager(save_dir)
        bad_window = MagicMock()
        bad_window.capture_as_image.side_effect = RuntimeError("no screen")
        path = sm.capture_roi(bad_window, "roi_test", (0, 0, 100, 50))
        assert path.endswith(".txt")

    def test_cleanup_old_removes_expired(self, tmp_path):
        save_dir = str(tmp_path / "shots")
        sm = ScreenshotManager(save_dir)
        old_file = os.path.join(save_dir, "old_shot.png")
        with open(old_file, "w") as f:
            f.write("old")
        old_mtime = time.time() - (10 * 86400)
        os.utime(old_file, (old_mtime, old_mtime))
        new_file = os.path.join(save_dir, "new_shot.png")
        with open(new_file, "w") as f:
            f.write("new")
        sm.cleanup_old(keep_days=7)
        assert not os.path.exists(old_file), "旧文件应被清理"
        assert os.path.exists(new_file), "新文件应保留"

    def test_capture_failure_writes_file(self, tmp_path):
        save_dir = str(tmp_path / "shots")
        sm = ScreenshotManager(save_dir)
        mock_window = MagicMock()
        path = sm.capture_failure(mock_window, "test_fail")
        assert "failures" in path
        assert path.endswith(".png")

    def test_capture_failure_fallback(self, tmp_path):
        save_dir = str(tmp_path / "shots")
        sm = ScreenshotManager(save_dir)
        bad_window = MagicMock()
        bad_window.capture_as_image.side_effect = RuntimeError("no img")
        result = sm.capture_failure(bad_window, "fail")
        assert "写入错误" in result


# ═══════════════════════════════════════════════════════
# crash_daemon.py
# ═══════════════════════════════════════════════════════

class TestCrashDaemon:
    def test_start_stop_no_crash(self):
        """正常启动和停止，不应报告崩溃。"""
        with patch("wpf_testkit.utils.crash_daemon.psutil") as mock_psutil:
            mock_proc = MagicMock()
            mock_proc.info = {"name": "app.exe", "pid": 1234}

            # process_iter 始终保持有进程 → 永不崩溃
            def always_has_process(*args, **kwargs):
                return [mock_proc]
            mock_psutil.process_iter.side_effect = always_has_process

            daemon = CrashDaemon(process_name="app.exe")
            daemon.start()
            time.sleep(0.4)
            daemon.stop()
            assert not daemon.has_crashed

    def test_detect_crash(self):
        """进程消失时，守护线程应检测到崩溃。"""
        with patch("wpf_testkit.utils.crash_daemon.psutil") as mock_psutil:
            mock_proc = MagicMock()
            mock_proc.info = {"name": "app.exe", "pid": 1234}

            call_count = [0]

            def process_iter_side_effect(*args, **kwargs):
                call_count[0] += 1
                # 第一次返回进程，之后返回空
                if call_count[0] == 1:
                    return [mock_proc]
                return []
            mock_psutil.process_iter.side_effect = process_iter_side_effect

            daemon = CrashDaemon(process_name="app.exe")
            daemon.start()
            # 守护线程 sleep(2) 一次循环，所以需等 > 2 秒触发第二次
            time.sleep(3)
            daemon.stop()

            assert daemon.has_crashed, "应检测到崩溃"
            assert daemon.crash_log is not None
            assert daemon.crash_time is not None
            if daemon.crash_log and os.path.exists(daemon.crash_log):
                os.remove(daemon.crash_log)

    def test_get_summary_no_crash(self):
        daemon = CrashDaemon()
        assert "未检测到崩溃" in daemon.get_summary()
        assert not daemon.has_crashed

    def test_get_summary_after_crash(self):
        with patch("wpf_testkit.utils.crash_daemon.psutil") as mock_psutil:
            mock_proc = MagicMock()
            mock_proc.info = {"name": "test.exe", "pid": 999}

            call_count = [0]

            def side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return [mock_proc]
                return []
            mock_psutil.process_iter.side_effect = side_effect

            daemon = CrashDaemon(process_name="test.exe")
            daemon.start()
            time.sleep(3)
            daemon.stop()

            summary = daemon.get_summary()
            assert "崩溃时间" in summary
            assert "999" in summary

    def test_stop_before_start(self):
        daemon = CrashDaemon()
        daemon.stop()

    def test_initial_state(self):
        daemon = CrashDaemon(
            process_name="myapp.exe", main_window_id="MainWin"
        )
        assert daemon.process_name == "myapp.exe"
        assert daemon.main_window_id == "MainWin"
        assert not daemon.has_crashed
        assert daemon.crash_log is None


# ═══════════════════════════════════════════════════════
# base_page.py
#
# pywinauto.Application 被替换为 FakeAppClass，这样：
#   - isinstance(app, Application) 可通过 (FakeAppClass 的子类)
#   - MagicMock(spec=Application) 可用 (FakeAppClass 不是 MagicMock)
# ═══════════════════════════════════════════════════════

class FakeApp:
    """伪造的 Application 实例，供 BasePage 构造使用。"""
    pass


# 让 FakeApp 继承 FakeAppClass，isinstance 检查通过
class FakeAppWithInheritance(FakeApp, FakeAppClass):
    pass


class TestBasePage:
    def _make_app(self):
        """创建一个可通过 BasePage.__init__ isinstance 检查的伪造 app。"""
        return FakeAppWithInheritance()

    def test_init_with_application(self):
        from wpf_testkit.core.base_page import BasePage
        app = self._make_app()
        page = BasePage(app)
        assert page.app is app

    def test_init_with_invalid_type_raises(self):
        from wpf_testkit.core.base_page import BasePage
        with pytest.raises(TypeError) as exc:
            BasePage("not an app")
        assert "Expected pywinauto.Application" in str(exc.value)

    def test_init_with_none_raises(self):
        from wpf_testkit.core.base_page import BasePage
        with pytest.raises(TypeError):
            BasePage(None)

    def test_window_property_not_implemented(self):
        from wpf_testkit.core.base_page import BasePage
        page = BasePage(self._make_app())
        with pytest.raises(NotImplementedError):
            _ = page.window

    def _make_test_page(self, mock_window=None):
        """创建继承 BasePage 的测试用子类。"""
        from wpf_testkit.core.base_page import BasePage

        if mock_window is None:
            mock_window = MagicMock()

        class TestPage(BasePage):
            @property
            def window(self):
                return mock_window

        return TestPage(self._make_app()), mock_window

    def test_wait_visible_delegates(self):
        page, mock_win = self._make_test_page()
        _result = page.wait_visible(timeout=5)
        mock_win.wait.assert_called_once_with("visible", timeout=5)

    def test_is_element_visible(self):
        mock_ctrl = MagicMock()
        mock_ctrl.exists.return_value = True
        mock_ctrl.is_visible.return_value = True
        mock_win = MagicMock()
        mock_win.child_window.return_value = mock_ctrl
        page, _ = self._make_test_page(mock_win)
        assert page.is_element_visible("BtnOK") is True
        mock_win.child_window.assert_called_with(auto_id="BtnOK")

    def test_is_element_not_visible(self):
        mock_ctrl = MagicMock()
        mock_ctrl.exists.return_value = False
        mock_win = MagicMock()
        mock_win.child_window.return_value = mock_ctrl
        page, _ = self._make_test_page(mock_win)
        assert page.is_element_visible("BtnMissing") is False

    def test_get_text_returns_text(self):
        mock_ctrl = MagicMock()
        mock_ctrl.exists.return_value = True
        mock_ctrl.window_text.return_value = "Hello"
        mock_win = MagicMock()
        mock_win.child_window.return_value = mock_ctrl
        page, _ = self._make_test_page(mock_win)
        assert page.get_text("Label1") == "Hello"

    def test_get_text_not_exists(self):
        mock_ctrl = MagicMock()
        mock_ctrl.exists.return_value = False
        mock_win = MagicMock()
        mock_win.child_window.return_value = mock_ctrl
        page, _ = self._make_test_page(mock_win)
        assert page.get_text("Missing") == ""

    def test_assert_element_exists_passes(self):
        mock_ctrl = MagicMock()
        mock_ctrl.exists.return_value = True
        mock_ctrl.is_visible.return_value = True
        mock_win = MagicMock()
        mock_win.child_window.return_value = mock_ctrl
        page, _ = self._make_test_page(mock_win)
        page.assert_element_exists("BtnOK")

    def test_assert_element_exists_fails(self):
        mock_ctrl = MagicMock()
        mock_ctrl.exists.return_value = False
        mock_win = MagicMock()
        mock_win.child_window.return_value = mock_ctrl
        page, _ = self._make_test_page(mock_win)
        with pytest.raises(AssertionError):
            page.assert_element_exists("BtnMissing")

    def test_click_element_calls_click(self):
        mock_ctrl = MagicMock()
        mock_win = MagicMock()
        mock_win.child_window.return_value = mock_ctrl
        page, _ = self._make_test_page(mock_win)
        page.click_element("BtnOK")
        mock_ctrl.click.assert_called_once()

    def test_click_element_fallback_to_click_input(self):
        mock_ctrl = MagicMock()
        mock_ctrl.click.side_effect = AttributeError("not clickable")
        mock_win = MagicMock()
        mock_win.child_window.return_value = mock_ctrl
        page, _ = self._make_test_page(mock_win)
        page.click_element("BtnOK")
        mock_ctrl.click_input.assert_called_once()

    def test_click_element_all_fail_does_not_raise(self):
        mock_ctrl = MagicMock()
        mock_ctrl.click.side_effect = AttributeError
        mock_ctrl.click_input.side_effect = RuntimeError
        mock_ctrl.invoke.side_effect = RuntimeError
        mock_win = MagicMock()
        mock_win.child_window.return_value = mock_ctrl
        page, _ = self._make_test_page(mock_win)
        page.click_element("BtnOK")
        mock_ctrl.set_focus.assert_called_once()
        mock_ctrl.type_keys.assert_called_once_with("{ENTER}")


# ═══════════════════════════════════════════════════════
# uia_helpers.py
# ═══════════════════════════════════════════════════════

class TestUiaHelpers:
    def test_find_window_by_title_returns_desktop_window(self):
        win = find_window_by_title("SomeWindow")
        assert win is not None

    def test_dump_controls_returns_string(self):
        mock_window = MagicMock()
        mock_window.descendants.return_value = []
        result = dump_controls(mock_window, max_depth=3)
        assert isinstance(result, str)
        assert "descendants" in result
