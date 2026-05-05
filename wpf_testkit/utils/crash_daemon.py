"""wpf_testkit/utils/crash_daemon.py — 崩溃守护进程

在测试执行期间监控被测应用进程状态，检测意外退出并记录现场。
Vision 扩展：崩溃时截图自动发送给多模态大模型分析错误内容。
"""

from __future__ import annotations

import os
import time
import threading
from typing import Optional

import psutil


class CrashDaemon:
    """崩溃守护线程：检测被测应用进程意外退出。"""

    def __init__(
        self,
        process_name: str = "app.exe",
        main_window_id: str = "MainWindow",
        screenshot_dir: str = "screenshots",
    ):
        self.process_name = process_name
        self.main_window_id = main_window_id
        self.screenshot_dir = screenshot_dir
        self.crashed = False
        self.crash_log: Optional[str] = None
        self.crash_time: Optional[str] = None
        self.last_pid: Optional[int] = None
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._stop_time: float = 0.0
        # Vision 分析器
        self._vision = None

    def _get_vision(self):
        if self._vision is None:
            try:
                from wpf_testkit.vision import get_analyzer

                self._vision = get_analyzer()
            except ImportError:
                self._vision = False
        return self._vision if self._vision else None

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
                    if (
                        pinfo["name"]
                        and pinfo["name"].lower() == self.process_name.lower()
                    ):
                        found_pid = pinfo["pid"]
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if found_pid:
                self.last_pid = found_pid
            elif self.last_pid is not None:
                if self._stop_time > 0 and time.time() - self._stop_time < 3:
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
        """崩溃时截取当前桌面，并用 Vision 分析错误内容。"""
        try:
            from pywinauto import Desktop

            desktop = Desktop(backend="uia")
            shot_path = os.path.join(
                self.screenshot_dir,
                f"crash_screen_{self.crash_time}.png",
            )
            desktop.capture_as_image().save(shot_path)

            # Vision 分析崩溃截图
            va = self._get_vision()
            if va and va.available:
                try:
                    from PIL import Image

                    with Image.open(shot_path) as img:
                        prompt = (
                            "分析这张WPF桌面应用崩溃截图。请回答：\n"
                            "1. 是否有错误对话框或崩溃对话框？它的标题是什么？\n"
                            "2. 错误消息内容是什么？\n"
                            "3. 错误类型属于：.NET运行时崩溃 / 应用级异常弹窗 / 系统级错误 / 正常状态\n"
                            "4. 是否是'已停止工作'对话框？\n"
                        )
                        desc = va.analyze(img, prompt, max_tokens=512)
                        if desc:
                            txt_path = shot_path.replace(".png", "_vision.txt")
                            with open(
                                txt_path, "w", encoding="utf-8"
                            ) as f:
                                f.write(
                                    f"崩溃场景分析 ({self.crash_time})\n"
                                    f"{'='*50}\n"
                                    f"Vision 分析:\n{desc}\n"
                                )
                except Exception:
                    pass  # Vision 分析失败不阻塞
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
