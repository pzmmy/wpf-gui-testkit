"""wpf_testkit/utils/crash_daemon.py — 崩溃守护进程

在测试执行期间监控被测应用进程状态，检测意外退出并记录现场。
"""
from __future__ import annotations

import os
import time
import threading
from typing import Optional

import psutil


class CrashDaemon:
    """崩溃守护线程：检测被测应用进程意外退出。

    用于长时间运行测试中，一旦应用崩溃自动记录现场（截图 + 日志）。
    """

    def __init__(self, process_name: str = "app.exe",
                 main_window_id: str = "MainWindow",
                 screenshot_dir: str = "screenshots"):
        self.process_name = process_name
        self.main_window_id = main_window_id
        self.screenshot_dir = screenshot_dir
        self.crashed = False
        self.crash_log: Optional[str] = None
        self.crash_time: Optional[str] = None
        self.last_pid: Optional[int] = None
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._stop_time: float = 0.0  # stop() 时记录时间戳，减少假阳性

    def start(self) -> "CrashDaemon":
        """启动守护线程。"""
        self._thread = threading.Thread(target=self._monitor, daemon=True)
        self._thread.start()
        return self

    def stop(self) -> "CrashDaemon":
        """停止守护线程。"""
        self._stop_time = time.time()
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        return self

    def _monitor(self) -> None:
        """监控循环：每 2 秒检测一次进程。"""
        while not self._stop_event.is_set():
            found_pid = None
            for proc in psutil.process_iter(["pid", "name", "create_time"]):
                try:
                    pinfo = proc.info
                    if (pinfo["name"] and
                            pinfo["name"].lower() == self.process_name.lower()):
                        found_pid = pinfo["pid"]
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if found_pid:
                self.last_pid = found_pid
            elif self.last_pid is not None:
                # 检查是否在 stop 时间附近（区分正常退出 vs 崩溃）
                if self._stop_time > 0 and time.time() - self._stop_time < 3:
                    # 3秒内的进程消失视为正常停止，不报告崩溃
                    break
                self.crashed = True
                self.crash_time = time.strftime("%Y%m%d_%H%M%S")
                self._write_crash_log()
                self._capture_crash_screen()
                break

            time.sleep(2)

    def _write_crash_log(self) -> None:
        """记录崩溃日志。"""
        os.makedirs(self.screenshot_dir, exist_ok=True)
        crash_log = os.path.join(
            self.screenshot_dir, f"crash_{self.crash_time}.txt"
        )
        with open(crash_log, "w", encoding="utf-8") as f:
            f.write("=== 崩溃检测报告 ===\n")
            f.write(f"时间: {self.crash_time}\n")
            f.write(f"进程: {self.process_name}\n")
            f.write(f"最后 PID: {self.last_pid}\n")
            f.write("状态: 进程意外退出\n")
        self.crash_log = crash_log

    def _capture_crash_screen(self) -> None:
        """崩溃时截取当前桌面。"""
        try:
            from pywinauto import Desktop
            desktop = Desktop(backend="uia")
            shot_path = os.path.join(
                self.screenshot_dir, f"crash_screen_{self.crash_time}.png"
            )
            desktop.capture_as_image().save(shot_path)
        except Exception:
            pass

    def get_summary(self) -> str:
        """获取崩溃摘要。"""
        if not self.crashed:
            return "未检测到崩溃"
        return (
            f"崩溃时间: {self.crash_time}\n"
            f"最后 PID: {self.last_pid}\n"
            f"日志: {self.crash_log}\n"
            f"截图: screenshots/crash_screen_{self.crash_time}.png"
        )

    @property
    def has_crashed(self) -> bool:
        return self.crashed
