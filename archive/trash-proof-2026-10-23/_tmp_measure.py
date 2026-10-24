# -*- coding: utf-8 -*-
# R194-2 前置取证：量化「宽限表对主流写法失效」的真实影响面（先测量，后动手）
import sys, os, io, re, collections
sys.path.insert(0, '05-exec')
import importlib
m = importlib.import_module('r38_debt_aging')
files = m.volume_files()
print('受检卷数 =', len(files))
RE_HDR_ONLY = re.compile(r"(?:^|[^0-9A-Za-z])(P[0-2])(?:[^0-9]|$)")
rows = []
for f in files:
    try:
        body = io.open(f, encoding='utf-8', errors='replace').read()
    except OSError:
        continue
    for ln, line in enumerate(body.splitlines(), 1):
        mm = m.RE_ITEM.match(line)
        if not mm:
            continue
        text = mm.group(2)
        now = m.RE_PRIORITY.search(text)
        cur = now.group(1) if now else None
        # 只看条目标题段（第一个全角冒号之前），避免正文引用劫持（X-23）
        head = text.split(chr(65306))[0]
        w2 = RE_HDR_ONLY.search(head)
        wid = w2.group(1) if w2 else None
        if cur != wid:
            rows.append((os.path.basename(f), ln, cur, wid, text[:66]))
print('宽限判定会改变的条目数 =', len(rows))
c = collections.Counter((a, b) for _, _, a, b, _ in rows)
for k, v in sorted(c.items(), key=lambda x: -x[1]):
    print('   %s -> %s : %d 条' % (k[0], k[1], v))
print()
print('样例（前 8）:')
for f, ln, a, b, t in rows[:8]:
    print('   %-28s L%-4d %s->%s  %s' % (f[:28], ln, a, b, t.replace(chr(10), ' ')))