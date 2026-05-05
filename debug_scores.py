#!/usr/bin/env python3
"""Debug match scores"""
import sys, re
sys.path.insert(0, "/tmp/wpf-gui-testkit")
from wpf_testkit.scene_matcher import SceneMatcher

m = SceneMatcher()

test_cases = [
    "弹窗是否关闭",
    "检查布局是否错位",
    "界面是否有错误",
    "迷你模式状态",
    "弹窗布局",
    "简听播放器状态",
]

for intent in test_cases:
    print(f"\n=== match('{intent}') ===")
    scores = m._compute_scores(intent)
    for score, pb in sorted(scores, key=lambda x: -x[0])[:4]:
        # Show matched keywords
        matched_kws = [k for k in pb.keywords if k in intent.lower()]
        print(f"  {score:4d} {pb.name:25s} matched_kws={matched_kws}")
    
    r = m.match(intent)
    print(f"  => {[p.name for p in r]}")
