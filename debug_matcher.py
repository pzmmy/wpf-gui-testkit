#!/usr/bin/env python3
"""Debug scene_matcher.py issues"""
import sys
sys.path.insert(0, "/tmp/wpf-gui-testkit")
from wpf_testkit.scene_matcher import _is_conclusive, SceneMatcher, UNCERTAINTY_MARKERS

# Issue 1: _is_conclusive 
print("=== _is_conclusive ===")
test_cases = [
    ("Short conclusive", "closed", True),
    ("Chinese conclusive", "已关闭", True),
    ("Uncertain at end", "看起来弹窗关闭了，但我不太确定", False),
    ("Uncertain only", "可能已关闭", False),
    ("English uncertain", "unclear maybe", False),
]
for label, text, expected in test_cases:
    got = _is_conclusive(text)
    status = "PASS" if got == expected else "FAIL"
    print(f"  [{status}] {label}: expected={expected} got={got}")
    if status == "FAIL":
        print(f"    '不确定' in text: {'不确定' in text}")
        print(f"    UNCERTAINTY_MARKERS: {UNCERTAINTY_MARKERS}")
        for m in UNCERTAINTY_MARKERS:
            if m in text:
                print(f"    matched marker: '{m}'")

# Issue 2: scoring
print("\n=== _compute_scores ===")
m = SceneMatcher()
scores = m._compute_scores("layout integrity")
print("match('layout integrity'):")
for score, pb in sorted(scores, key=lambda x: -x[0]):
    print(f"  {score:4d} {pb.name:25s} desc={pb.description[:40]}")

print("\nmatch('检查布局是否错位'):")
scores2 = m._compute_scores("检查布局是否错位")
for score, pb in sorted(scores2, key=lambda x: -x[0]):
    print(f"  {score:4d} {pb.name:25s} desc={pb.description[:40]}")

print("\nmatch('error state'):")
scores3 = m._compute_scores("error state")
for score, pb in sorted(scores3, key=lambda x: -x[0]):
    print(f"  {score:4d} {pb.name:25s}")
