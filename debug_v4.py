#!/usr/bin/env python3
"""Debug v4: check actual scoring"""
import sys, os, re
sys.path.insert(0, "/tmp/wpf-gui-testkit")

for mod in list(sys.modules.keys()):
    if 'scene_matcher' in mod:
        del sys.modules[mod]

from wpf_testkit.scene_matcher import SceneMatcher

sep = re.compile(r'[，。；：！？、/\s]+')
intent = "弹窗是否关闭"

m = SceneMatcher()
scores = m._compute_scores(intent)

print(f"intent: {intent!r}")
intent_words = set()
for part in sep.split(intent.lower()):
    part = part.strip()
    if len(part) > 1:
        intent_words.add(part)
for word in intent.lower().split():
    word = word.strip(",.;:!?")
    if len(word) > 1:
        intent_words.add(word)
print(f"intent_words: {intent_words}")

print(f"\nscores:")
for s, pb in sorted(scores, key=lambda x: -x[0]):
    matched = [w for w in intent_words if w in pb.description.lower()]
    print(f"  {s:4d} {pb.name:25s} matched={matched}")
