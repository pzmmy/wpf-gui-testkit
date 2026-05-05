#!/usr/bin/env python3
"""Debug: check keyword extraction"""
import sys, re
sys.path.insert(0, "/tmp/wpf-gui-testkit")
from wpf_testkit.scene_matcher import PlaybookDef

# Test Chinese keyword extraction
pb = PlaybookDef(name="dlg", description="验证弹窗是否存在、弹窗内容、弹窗关闭状态", prompt="test")
print("Chinese description:", pb.description)
print("Keywords:", pb.keywords)
print()

# Test English keyword extraction
pb2 = PlaybookDef(name="test", description="layout integrity check test", prompt="test")
print("EN description:", pb2.description)
print("EN Keywords:", pb2.keywords)
print()

# Test intent matching
for kw in pb.keywords:
    print(f"  '{kw}' in 'layout integrity': {kw in 'layout integrity'}")

print()
print("--- split behavior ---")
desc = "验证弹窗是否存在、弹窗内容、弹窗关闭状态"
for word in desc.split():
    print(f"  split: '{word}'")
print()
for part in re.split(r'[，。；：！？、/\s]+', desc):
    part = part.strip()
    print(f"  re.split: '{part}' (len={len(part)})")
