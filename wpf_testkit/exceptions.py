"""wpf_testkit/exceptions.py — 自定义异常"""
from __future__ import annotations


class ElementNotFoundError(Exception):
    """控件未找到。"""
    pass


class CommandInvokeError(Exception):
    """命令调用失败。"""
    pass


class CrashDetectedError(Exception):
    """被测应用崩溃。"""
    pass
