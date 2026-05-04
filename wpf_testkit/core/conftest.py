"""wpf_testkit/core/conftest.py — pytest fixtures

提供：
- app_launch / app_connect — 启动/连接被测应用
- session_cleanup — 进程 + AppData 自动清理
- crash_daemon — 崩溃监控
- screenshot_manager — 失败自动截图
"""
from __future__ import annotations

import os
import time
import subprocess
import shutil
from typing import Generator, Optional

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


# ── 辅助函数 ──


def kill_all_app() -> None:
    """强制结束所有被测应用进程。"""
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() == APP_PROCESS_NAME.lower():
                p = psutil.Process(proc.info["pid"])
                p.kill()
                p.wait(timeout=5)
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
    clean_appdata()
    kill_all_app()
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

    # 等待主窗口出现
    main = app.window(auto_id=MAIN_WINDOW_ID)
    main.wait("visible", timeout=15)
    time.sleep(1)

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
