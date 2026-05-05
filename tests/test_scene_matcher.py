"""SceneMatcher 单元测试"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from wpf_testkit.scene_matcher import SceneMatcher, PlaybookDef, _is_conclusive


def make_matcher():
    m = SceneMatcher()
    m.register(PlaybookDef(name="test-custom", description="custom test playbook", prompt="test", fallback=False))
    return m


class TestSceneMatcher:

    def test_positive_match(self):
        """正向匹配：弹窗相关 intent 应匹配 dialog-verify"""
        m = make_matcher()
        r = m.match("弹窗是否关闭")
        assert len(r) >= 1
        assert r[0].name == "dialog-verify"

    def test_negation_penalty(self):
        """C-1: 否定意图不应匹配正向 playbook"""
        m = make_matcher()
        r = m.match("弹窗未关闭")
        assert r[0].name != "dialog-verify", f"否定意图误配到 dialog-verify, got {r[0].name}"

    def test_fallback_fill(self):
        """S-1: 无匹配时 fallback 填充"""
        m = SceneMatcher()
        r = m.match("xyzunknown_intent")
        assert len(r) >= 1
        assert any(p.fallback for p in r), f"无 fallback 填充: {[p.name for p in r]}"

    def test_custom_playbook_registration(self):
        """自定义 playbook 注册后应能被匹配"""
        m = make_matcher()
        m.register(PlaybookDef(name="jianting-player", description="检测简听收音机播放器播放状态", prompt="test"))
        r = m.match("简听播放器状态")
        assert any(p.name == "jianting-player" for p in r)

    def test_chinese_layout_match(self):
        """中文布局匹配"""
        m = make_matcher()
        r = m.match("检查布局是否错位")
        assert r[0].name == "layout-integrity"

    def test_chinese_error_match(self):
        """中文错误状态匹配（注意"错误"bigram也可能匹配control-existence的"否"）"""
        m = make_matcher()
        r = m.match("检测错误提示")
        assert r[0].name == "error-state"

    def test_chinese_mini_mode_match(self):
        """中文迷你模式匹配"""
        m = make_matcher()
        r = m.match("迷你模式状态")
        assert r[0].name == "mini-mode"

    def test_chinese_playback_match(self):
        """中文播放状态匹配"""
        m = make_matcher()
        r = m.match("播放器播放状态")
        assert r[0].name == "playback-status"

    def test_multiple_matches(self):
        """匹配应返回 top_k=2 个结果"""
        m = make_matcher()
        r = m.match("弹窗布局")
        assert len(r) >= 2
        assert r[0].name == "dialog-verify"


class TestIsConclusive:

    def test_conclusive_short(self):
        assert _is_conclusive("已关闭") is True

    def test_uncertainty_chinese(self):
        assert _is_conclusive("可能已关闭") is False

    def test_uncertainty_at_end(self):
        assert _is_conclusive("看起来弹窗关闭了，但我不太确定") is False

    def test_uncertainty_english(self):
        assert _is_conclusive("unclear, maybe closed") is False

    def test_empty_string(self):
        assert _is_conclusive("") is False

    def test_single_char(self):
        assert _is_conclusive("a") is False

    def test_long_conclusive(self):
        assert _is_conclusive("按钮是灰色禁用状态") is True
