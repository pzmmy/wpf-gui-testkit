"""wpf-gui-testkit — 极简 WPF GUI 自动化测试框架

基于 Python + pywinauto (UIA backend) + pytest，零外部服务依赖。
"""

__version__ = "0.6.1"

# ── 核心 vision 模块导出 ──
try:
    from wpf_testkit.vision import (
        VisionAnalyzer,
        VisionProvider,
        OpenAIVisionProvider,
        get_analyzer,
        reset_analyzer,
    )
except ImportError:
    pass

# ── SceneMatcher 模块导出（独立于 vision） ──
try:
    from wpf_testkit.scene_matcher import (
        SceneMatcher,
        PlaybookDef,
    )
except ImportError:
    pass
