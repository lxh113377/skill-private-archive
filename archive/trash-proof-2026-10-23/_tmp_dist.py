# -*- coding: utf-8 -*-
# 改判据前置量化：用 monkeypatch 换掉 grace 取值，看分类分布怎么动（不落盘）
import sys, io, re, os, collections
sys.path.insert(0, '05-exec')
import importlib
m = importlib.import_module('r38_debt_aging')
COLON = chr(65306)
RE_P = re.compile(r"(?:^|[^0-9A-Za-z])(P[0-2])(?:[^0-9]|$)")

items = []
for f in m.volume_files():
    try:
        body = io.open(f, encoding='utf-8', errors='replace').read()
    except OSError:
        continue
    for line in body.splitlines():
        mm = m.RE_ITEM.match(line)
        if mm:
            items.append(mm.group(2))
now = m.current_round()[0] if isinstance(m.current_round(), tuple) else 194
print('now_round =', now, '| 条目 =', len(items))

def dist(grace_fn):
    c = collections.Counter()
    for t in items:
        orig = m.GRACE_BY_PRIORITY.get
        # 复制 classify 的核心：临时替换 grace 计算
        kind, arg = m.parse_last_verdict(t)
        if kind == 'DEFER':
            tgt = arg
            if tgt > now:
                n = m.count_deferrals(t)
                c['REPEAT' if n >= m.REPEAT_AFTER else 'DEFERRED'] += 1
            else:
                c['OVERDUE'] += 1
            continue
        if kind == 'FINAL':
            c['DECIDED'] += 1
            continue
        g = grace_fn(t)
        origin, held = None, None
        own = m.RE_TITLE_OWN.match(t)
        if own:
            origin = int(own.group(1))
        else:
            for x in m.RE_ROUND_DECL.finditer(t):
                if x.group(1): origin = int(x.group(1))
                elif x.group(2): origin = int(x.group(2))
                elif x.group(3): held = int(x.group(3))
        age = (now - origin) if origin is not None else (held if held is not None else None)
        if age is None:
            c['UNDATED'] += 1
        else:
            c['OVERDUE' if age > g else 'ACTIVE'] += 1
    return c

def cur(t):
    k = (m.RE_PRIORITY.search(t) or ['', 'UNMARKED'])[1]
    return m.GRACE_BY_PRIORITY.get(k, m.GRACE_DEFAULT)
def new(t):
    head = t.split(COLON)[0] if COLON in t else t
    mm = RE_P.search(head)
    return m.GRACE_BY_PRIORITY.get(mm.group(1) if mm else 'UNMARKED', m.GRACE_DEFAULT)

dc, dn = dist(cur), dist(new)
print()
print('%-10s %6s %6s %6s' % ('类', '现状', '改后', '差'))
for k in ('OVERDUE','ACTIVE','DECIDED','DEFERRED','REPEAT','UNDATED'):
    print('%-10s %6d %6d %+6d' % (k, dc.get(k,0), dn.get(k,0), dn.get(k,0)-dc.get(k,0)))