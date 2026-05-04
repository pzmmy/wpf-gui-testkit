"""wpf_testkit/core/conftest.py — pytest fixtures

提供：
- app_launch / app_connect — 启动/连接被测应用
- session_cleanup — 进程 + AppData 自动清理
- crash_daemon — 崩溃监控
- screenshot_manager — 失败自动截图
- --update-baseline 命令行选项
"""
from __future__ import annotations

import os
import time
import shutil
from typing import Generator

import pytest
import psutil
from pywinauto import Application


# 可环境变量覆盖：WPF_TEST_APP_PATH
APP_PATH = os.environ.get("WPF_TEST_APP_PATH")
if not APP_PATH:
    APP_PATH = ""  # 启动时会报 FileNotFoundError，见 app_launch fixture

# 可环境变量覆盖：WPF_TEST_APP_PROCESS_NAME
APP_PROCESS_NAME = os.environ.get("WPF_TEST_APP_PROCESS_NAME", "app.exe")

# 可环境变量覆盖：WPF_TEST_APP_DATA_DIR（AppData 清理目录名）
APP_DATA_DIR = os.environ.get("WPF_TEST_APP_DATA_DIR", "App")

# 可环境变量覆盖：WPF_TEST_MAIN_WINDOW_ID
MAIN_WINDOW_ID = os.environ.get("WPF_TEST_MAIN_WINDOW_ID", "MainWindow")

# 可环境变量覆盖：WPF_TEST_GUIDE_WINDOW_TITLE（首次引导页标题，为空则跳过关闭引导页）
GUIDE_WINDOW_TITLE = os.environ.get("WPF_TEST_GUIDE_WINDOW_TITLE", "")


# ── 辅助函数 ──


def kill_all_app() -> None:
    """强制结束所有被测应用进程（含子进程），带超时保护。"""
    timeout = 5  # 单进程最多等 5 秒
    targeted_pids = []

    for proc in psutil.process_iter(["name", "pid"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() == APP_PROCESS_NAME.lower():
                targeted_pids.append(proc.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    for pid in targeted_pids:
        try:
            parent = psutil.Process(pid)
            # 递归杀子进程（WPF 常驻子进程如 background thread 等）
            children = parent.children(recursive=True)
            for child in children:
                try:
                    child.kill()
                    child.wait(timeout=timeout)
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    pass
            parent.kill()
            parent.wait(timeout=timeout)
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            pass
    time.sleep(1)


def clean_appdata() -> None:
    """清理 AppData 下的应用配置残留。"""
    appdata_path = os.path.join(os.environ.get("APPDATA", ""), APP_DATA_DIR)
    if os.path.exists(appdata_path):
        for retry in range(3):
            try:
                if os.path.isfile(appdata_path):
                    os.remove(appdata_path)
                else:
                    shutil.rmtree(appdata_path)
                break
            except (PermissionError, OSError):
                time.sleep(0.5)


# ── Session 级 fixtures ──


@pytest.fixture(scope="session", autouse=True)
def session_cleanup() -> Generator:
    """Session 级清理（全局一次）。"""
    kill_all_app()
    clean_appdata()
    # 在 session 开始时初始化 COM
    import ctypes
    try:
        ctypes.windll.ole32.CoInitializeEx(None, 2)
    except Exception:
        pass
    yield
    kill_all_app()


# ── Function 级 fixtures ──


@pytest.fixture
def app_launch() -> Application:
    """启动新实例（每条用例隔离）。"""
    kill_all_app()
    clean_appdata()

    app = Application(backend="uia")
    app.start(APP_PATH, timeout=20)

    # 轮询等待主窗口出现（替代 time.sleep 硬等）
    from pywinauto import Desktop
    desktop = Desktop(backend="uia")
    for _ in range(15):
        try:
            win = desktop.window(auto_id=MAIN_WINDOW_ID)
            if win.exists():
                break
        except Exception:
            pass
        time.sleep(1)

    # 关闭引导页窗口（如配置了标题）
    if GUIDE_WINDOW_TITLE:
        import ctypes
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.FindWindowW(None, GUIDE_WINDOW_TITLE)
            if hwnd:
                user32.PostMessageW(hwnd, 0x0010, 0, 0)
                time.sleep(0.5)
        except Exception:
            pass

    yield app

    try:
        app.kill()
    except Exception:
        pass
    kill_all_app()


@pytest.fixture
def app_connect() -> Application:
    """连接到已运行的实例。"""
    app = Application(backend="uia").connect(path=APP_PATH, timeout=15)
    yield app


@pytest.fixture
def main_window(app_launch: Application):
    """启动应用并返回主窗口。"""
    from pywinauto import Desktop
    desktop = Desktop(backend="uia")
    for _ in range(15):
        win = desktop.window(auto_id=MAIN_WINDOW_ID)
        try:
            if win.exists():
                return win
        except Exception:
            pass
        time.sleep(1)
    return app_launch.window(auto_id=MAIN_WINDOW_ID)


# ── 截图与崩溃守护 ──


@pytest.fixture
def screenshot_manager():
    """截图管理器。"""
    from wpf_testkit.utils.screenshot import ScreenshotManager
    sm = ScreenshotManager()
    yield sm
    sm.cleanup_old(keep_days=7)


@pytest.fixture(autouse=True)
def auto_screenshot_on_failure(request, screenshot_manager):
    """失败时自动截图。"""
    yield
    # 兼容不同 pytest 版本：尝试多种属性名
    rep = getattr(request.node, 'rep_call', None) or getattr(request.node, 'rep_setup', None)
    if rep and rep.failed:
        try:
            from pywinauto import Desktop
            desktop = Desktop(backend="uia")
            screenshot_manager.capture(desktop, f"FAILED_{request.node.name}")
        except Exception:
            pass


@pytest.fixture(autouse=True)
def crash_daemon(app_launch):
    """崩溃守护（自动监控进程状态）。"""
    from wpf_testkit.utils.crash_daemon import CrashDaemon
    daemon = CrashDaemon(
        process_name=APP_PROCESS_NAME,
        main_window_id=MAIN_WINDOW_ID,
    )
    daemon.start()
    yield daemon
    daemon.stop()
    summary = daemon.get_summary()
    if daemon.crash_log:
        pytest.fail(f"崩溃守护检测到异常:\n{summary}")


# ── pytest 钩子 ──


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """记录测试报告（用于 auto_screenshot_on_failure）。"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


# ── 命令行选项 ──


def pytest_addoption(parser):
    """添加命令行选项。"""
    parser.addoption(
        "--update-baseline",
        action="store_true",
        default=False,
        help="强制更新视觉回归测试的 baseline 截图（覆盖旧 baseline）",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """将 --update-baseline 标志存入全局。"""
    from wpf_testkit.utils import visual_diff
    if config.getoption("--update-baseline", default=False):
        visual_diff.UPDATE_BASELINE = True
