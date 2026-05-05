#!/usr/bin/env python3
"""Debug single test failure"""
intent = "界面是否有错误"
chars = [c for c in intent if '\u4e00' <= c <= '\u9fff']
bigrams = set()
for i in range(len(chars)-1):
    bigrams.add(chars[i] + chars[i+1])
print("bigrams:", bigrams)

desc1 = "检查界面中特定控件是否存在、可用、可见"
desc2 = "检测错误提示、异常状态、空状态、加载失败"

m1 = [bg for bg in bigrams if bg in desc1]
m2 = [bg for bg in bigrams if bg in desc2]
print(f"control-existence matched: {m1} (score={len(m1)*5})")
print(f"error-state matched: {m2} (score={len(m2)*5})")
