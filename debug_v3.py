#!/usr/bin/env python3
"""Debug v3: force reload module"""
import sys, os, re
sys.path.insert(0, "/tmp/wpf-gui-testkit")

# Force clear any cached import
for mod in list(sys.modules.keys()):
    if 'scene_matcher' in mod:
        del sys.modules[mod]

from wpf_testkit.scene_matcher import SceneMatcher, _DEFAULT_PLAYBOOKS

# First check PlaybookDef keywords
for pb in _DEFAULT_PLAYBOOKS:
    print(f"  {pb.name:25s} kw_count={len(pb.keywords)} desc={pb.description[:35]}")

print("\n=== _compute_scores ===")
m = SceneMatcher()
intent = "弹窗是否关闭"
print(f"intent: '{intent}'")
print(f"分词: {[p for p in re.split(r'[，。；：！？、/\\s]+', intent.lower()) if len(p.strip())>1]}")

scores = m._compute_scores(intent)
for s, pb in sorted(scores, key=lambda x: -x[0]):
    # Recompute what matched
    iw = set()
    for part in re.split(r'[，。；：！？、/\\s]+', intent.lower()):
        part = part.strip()
        if len(part) > 1:
            iw.add(part)
    for word in intent.lower().split():
        word = word.strip(",.;:!?")
        if len(word) > 1:
            iw.add(word)
    matched = [w for w in iw if w in pb.description.lower()]
    print(f"  {s:4d} {pb.name:25s} matched={matched}")

r = m.match(intent)
print(f"  => {[p.name for p in r]}")
