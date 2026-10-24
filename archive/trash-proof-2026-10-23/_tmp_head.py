# -*- coding: utf-8 -*-
# 验标题段切分是否可靠：标题段 = 第一个全角冒号之前；无冒号则整条（保守）
import sys, io, re, os, collections
sys.path.insert(0, '05-exec')
import importlib
m = importlib.import_module('r38_debt_aging')
COLON = chr(65306)
RE_P = re.compile(r"(?:^|[^0-9A-Za-z])(P[0-2])(?:[^0-9]|$)")
no_colon = 0
total = 0
multi = collections.Counter()
examples = []
for f in m.volume_files():
    try:
        body = io.open(f, encoding='utf-8', errors='replace').read()
    except OSError:
        continue
    for line in body.splitlines():
        mm = m.RE_ITEM.match(line)
        if not mm:
            continue
        text = mm.group(2)
        total += 1
        if COLON not in text:
            no_colon += 1
            continue
        head = text.split(COLON)[0]
        n = text.count(COLON)
        multi[n] += 1
        if len(examples) < 3 and n > 3:
            examples.append((n, head[:90]))
print('条目总数 =', total, '| 无全角冒号 =', no_colon)
print('冒号个数分布（前 6 档）:', dict(sorted(multi.items())[:6]))
print()
# 关键：标题段内匹配 P 级，会不会匹到正文里更靠前的 P 级？
amb = 0
for f in m.volume_files():
    try:
        body = io.open(f, encoding='utf-8', errors='replace').read()
    except OSError:
        continue
    for line in body.splitlines():
        mm = m.RE_ITEM.match(line)
        if not mm:
            continue
        text = mm.group(2)
        if COLON not in text:
            continue
        head = text.split(COLON)[0]
        a = RE_P.search(head)
        b = RE_P.search(text)
        if a and b and a.group(1) != b.group(1):
            amb += 1
            if amb <= 3:
                print('  不一致: head=%s full=%s | %s' % (a.group(1), b.group(1), text[:80]))
print('标题段与全文结论不一致 =', amb, '条')