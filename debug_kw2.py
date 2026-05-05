#!/usr/bin/env python3
"""Check keyword extraction in real playbooks"""
import sys
sys.path.insert(0, "/tmp/wpf-gui-testkit")

from wpf_testkit.scene_matcher import _DEFAULT_PLAYBOOKS

for pb in _DEFAULT_PLAYBOOKS:
    print(f"\n{pb.name}:")
    print(f"  keywords={pb.keywords}")
    print(f"  description={pb.description}")
    
# Test: does keyword matching work for "弹窗"?
print("\n\n=== Test matching ===")
test_intent = "弹窗是否关闭"
for pb in _DEFAULT_PLAYBOOKS:
    matched = [k for k in (pb.keywords or set()) if k in test_intent.lower()]
    print(f"  {pb.name}: matched={matched}")
