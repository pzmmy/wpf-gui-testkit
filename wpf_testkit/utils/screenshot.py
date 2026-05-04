"""wpf_testkit/utils/screenshot.py — 截图管理器

提供截图拍摄、ROI 裁剪、失败自动截图、老旧清理等功能。
"""
from __future__ import annotations

import os
import time
from typing import Tuple

from PIL import Image


class ScreenshotManager:
    """截图管理器。"""

    def __init__(self, save_dir: str = "screenshots"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(os.path.join(save_dir, "baseline"), exist_ok=True)
        os.makedirs(os.path.join(save_dir, "failures"), exist_ok=True)

    def capture(self, window, name: str) -> str:
        """截取窗口/桌面截图。"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        path = os.path.join(self.save_dir, filename)
        try:
            window.capture_as_image().save(path)
            return path
        except Exception as e:
            fallback = os.path.join(
                self.save_dir, f"ERROR_{name}_{timestamp}.txt"
            )
            with open(fallback, "w") as f:
                f.write(f"截图失败: {e}")
            return fallback

    def capture_roi(self, window, name: str,
                    region: Tuple[int, int, int, int]) -> str:
        """截取 ROI 区域 (x, y, w, h)。"""
        path = self.capture(window, name)
        if path.endswith(".png"):
            try:
                with Image.open(path) as img:
                    cropped = img.crop((
                        region[0], region[1],
                        region[0] + region[2], region[1] + region[3]
                    ))
                    roi_path = path.replace(".png", "_roi.png")
                    cropped.save(roi_path)
                return roi_path
            except Exception:
                pass
        return path

    def capture_failure(self, window, test_name: str) -> str:
        """失败时截图，存入 failures/ 子目录。"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        path = os.path.join(
            self.save_dir, "failures", f"{test_name}_{timestamp}.png"
        )
        try:
            window.capture_as_image().save(path)
            return path
        except Exception as e:
            return f"失败截图写入错误: {e}"

    def cleanup_old(self, keep_days: int = 7):
        """清理超过 N 天的截图。"""
        now = time.time()
        cutoff = now - (keep_days * 86400)
        for root, _dirs, files in os.walk(self.save_dir):
            for f in files:
                fpath = os.path.join(root, f)
                try:
                    if os.path.getmtime(fpath) < cutoff:
                        os.remove(fpath)
                except OSError:
                    pass
