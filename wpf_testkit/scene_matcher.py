"""
Skills Playbook 自动选择 + 多模型角色分离
为 VisionAnalyzer 提供 SceneMatcher、多模型 Brain 切换能力。

使用方式：
    from wpf_testkit.vision import get_analyzer
    va = get_analyzer()
    result = va.analyze_with_intent(screenshot, "弹窗是否关闭", brain="auto")
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import threading


# ── Playbook 定义 ──────────────────────────────────────

@dataclass
class PlaybookDef:
    """一个分析场景的 playbook。"""
    name: str
    description: str             # 仅用于匹配
    prompt: str                  # 完整分析提示词
    fallback: bool = False       # 是否作为通用兜底 playbook


# ── 预置 Playbook ──────────────────────────────────────

_DEFAULT_PLAYBOOKS = [
    PlaybookDef(
        name="dialog-verify",
        description="验证弹窗是否存在、弹窗内容、弹窗关闭状态",
        prompt="分析这张截图。1)是否有弹窗打开？2)弹窗标题是什么？"
               "3)弹窗内容是否完整？4)弹窗是否有关闭按钮？"
               "5)如果之前有弹窗现在没有了，说明弹窗已关闭。",
    ),
    PlaybookDef(
        name="playback-status",
        description="检测播放器状态：正在播放、已暂停、停止、录音中",
        prompt="分析截图中的播放控制区域。"
               "1)播放按钮图标是 ▶(播放) 还是 ▢(暂停)？"
               "2)是否有进度条在移动？"
               "3)是否有录音指示(红色圆点)？"
               "4)当前总体的播放状态是什么？",
    ),
    PlaybookDef(
        name="control-existence",
        description="检查界面中特定控件是否存在、可用、可见",
        prompt="分析截图。1)找到所有可见的按钮/滑块/下拉框/输入框。"
               "2)对每个控件描述它的位置和功能。"
               "3)特别检查：是否有控件处于禁用状态(灰色不可点击)？",
        fallback=True,
    ),
    PlaybookDef(
        name="layout-integrity",
        description="检查界面布局是否完整、元素是否错位、重叠、缺失",
        prompt="分析截图中的界面布局。"
               "1)所有元素是否在预期位置？"
               "2)是否有元素重叠或超出边界？"
               "3)文本是否完整显示(没有截断/省略号异常)？",
    ),
    PlaybookDef(
        name="error-state",
        description="检测错误提示、异常状态、空状态、加载失败",
        prompt="分析截图。1)是否有错误提示或警告图标？"
               "2)是否有'加载失败'、'网络错误'等异常文字？"
               "3)列表/表格是否为空？",
    ),
    PlaybookDef(
        name="mini-mode",
        description="检测迷你模式/紧凑模式下的界面状态",
        prompt="分析截图。1)这是迷你模式还是完整模式？"
               "2)迷你模式下哪些控件可见？"
               "3)窗口尺寸比例是否正常？",
    ),
]


# ── 否定词匹配常量 ─────────────────────────────────────

_NEGATIONS = {"不", "没", "未", "无", "no", "not", "without", "none"}
_POSITIVE_DESCRIPTORS = {"存在", "是", "有", "完整", "正常", "显示"}


# ── SceneMatcher ────────────────────────────────────────

class SceneMatcher:
    """根据场景意图描述匹配合适的 playbook。

    仅匹配 name 和 description，不提前加载 prompt 全文。
    匹配策略：关键词+描述包含关系评分 + 否定词负分，返回 top_k。
    线程安全。
    """

    def __init__(self):
        self._registry: list[PlaybookDef] = list(_DEFAULT_PLAYBOOKS)
        self._lock = threading.Lock()

    def register(self, pb: PlaybookDef) -> None:
        """注册自定义 playbook。线程安全。"""
        with self._lock:
            self._registry.append(pb)

    def match(self, intent: str, top_k: int = 2) -> list[PlaybookDef]:
        """返回匹配度最高的 top_k 个 playbook。线程安全。"""
        with self._lock:
            scores = self._compute_scores(intent)
            scores.sort(key=lambda x: -x[0])
            matched = [pb for _, pb in scores[:top_k]]

        # 如果匹配结果不足 top_k，用 fallback playbook 填充
        if len(matched) < top_k:
            for pb in self._registry:
                if pb.fallback and pb not in matched:
                    matched.append(pb)
                    if len(matched) >= top_k:
                        break
        return matched

    def _compute_scores(self, intent: str) -> list[tuple[int, PlaybookDef]]:
        """计算所有 playbook 与 intent 的匹配评分。

        评分规则（C-1 否定词处理）：
        - 关键词交集正分 = 匹配词数 × 10
        - 关键词包含正分 = 每个匹配词 +5
        - 否定词惩罚 = 如果 intent 含否定词而 playbook 描述含正向词，-20
        """
        scores: list[tuple[int, PlaybookDef]] = []
        intent_lower = intent.lower()
        intent_words = set(intent_lower.split())

        # 检测 intent 是否含否定意图
        has_negation = any(n in intent_lower for n in _NEGATIONS)

        for pb in self._registry:
            desc_lower = pb.description.lower()
            desc_words = set(desc_lower.split())

            score = len(intent_words & desc_words) * 10
            for kw in intent_words:
                if kw in desc_lower:
                    score += 5

            # C-1: 否定词惩罚
            # 用户说否定但 playbook 描述是正向 → 大惩罚
            if has_negation and any(p in desc_lower for p in _POSITIVE_DESCRIPTORS):
                score -= 20

            scores.append((score, pb))

        return scores


# ── 多模型 Brain Config ────────────────────────────────

@dataclass
class BrainConfig:
    """一个"大脑"的配置。"""
    provider: str = "openai"
    model: str = "qwen2.5-vl-7b-instruct"
    detail: str = "low"
    max_tokens: int = 256


# ── 置信度判断 ─────────────────────────────────────────

UNCERTAINTY_MARKERS = {
    "不确定", "可能", "无法判断", "模糊", "不太清楚",
    "unclear", "uncertain", "maybe", "not sure",
}


def _is_conclusive(result: str) -> bool:
    """判断粗筛结果是否足够确定。

    W-1 修复：移除 >= 10 的硬阈值，改为 >= 2（至少两个字符）。
    主判断依据是 UNCERTAINTY_MARKERS 检测，而非长度。
    """
    if not result or len(result.strip()) < 2:
        return False
    result_lower = result.lower()
    return not any(m in result_lower for m in UNCERTAINTY_MARKERS)


# ── 集成到 VisionAnalyzer ───────────────────────────────

# 注意：以下方法设计为注入到 wpf_testkit/vision.py 的 VisionAnalyzer 类中。
# 导入方式：
#   from wpf_testkit.vision import VisionAnalyzer
#   VisionAnalyzer.analyze_with_intent = analyze_with_intent
#   VisionAnalyzer.register_custom_playbook = register_custom_playbook

def analyze_with_intent(
    self,
    img,
    intent: str,
    max_tokens: int = 1024,
    detail: str = "high",
    brain: str = "auto",
    max_premium_retries: int = 1,
) -> Optional[str]:
    """根据意图自动选择 playbook 并分析。

    Args:
        img: PIL Image 或 ndarray
        intent: 场景意图描述（如 "弹窗是否关闭"）
        brain: "auto" | "cheap" | "premium"
            auto = 先 cheap 看置信度，不够再 premium
        max_premium_retries: auto 模式 premium 重试次数（默认 1）

    W-2 修复：premium 重试 max_premium_retries 次，
    最后一次无论是否确定都返回结果而非 None。
    """
    if not getattr(self, "_enabled", None):
        return None
    if not hasattr(self, "_matcher"):
        self._matcher = SceneMatcher()

    matched = self._matcher.match(intent)
    prompt = matched[0].prompt if matched else intent

    if brain == "premium":
        return self._call_api(img, prompt, max_tokens, detail)
    if brain == "cheap":
        return self._call_api(img, prompt, min(max_tokens, 256), "low")

    # auto 模式：先 cheap
    cheap_result = self._call_api(img, prompt, min(max_tokens, 256), "low")
    if cheap_result is None:
        return None
    if _is_conclusive(cheap_result):
        return cheap_result

    # W-2: 不够确定，重试 premium 最多 max_premium_retries 次
    premium_result: Optional[str] = None
    for _ in range(max_premium_retries):
        premium_result = self._call_api(img, prompt, max_tokens, detail)
        if premium_result is not None and _is_conclusive(premium_result):
            return premium_result

    # W-2: 最后一次的结果也返回（即使用户宁可见不确定的回答也好过 None）
    return premium_result


def register_custom_playbook(
    self, name: str, description: str, prompt: str,
    fallback: bool = False,
) -> None:
    """注册自定义 playbook（如 BasePage 初始化时注册 WPF 专用场景）。"""
    if not hasattr(self, "_matcher"):
        self._matcher = SceneMatcher()
    self._matcher.register(
        PlaybookDef(name=name, description=description, prompt=prompt, fallback=fallback)
    )
