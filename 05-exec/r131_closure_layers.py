# -*- coding: utf-8 -*-
# r131_closure_layers.py -- 三层闭包统一面（direct / tag / domain）一张表。
#
# 存在理由：r120 立域过滤（第 8 类）、r126 立 tag 闭包（第 9 类）、r131 立 direct 正则抢答（第 10 类），
# 三张面各自跑、各自成件，但**读的人无法一眼看出「哪些 miss 是闭包、哪些是可救的排序错」**，
# 于是每轮都要重新逐条复盘（r131 实测就是如此）。本件把三层合成一张表 + 一个优先级序。
#
# 三层在生产链路的**先后顺序**（这决定了修哪层收益最大）：
#   1. direct_route  —— 链路第一环，命中即返回，BGE 不参与（第 10 类）
#   2. tag_filter     —— 命中则 bge_recall 只在 tag 内搜（第 9 类）
#   3. classify_domain + L1.5 兜底 —— 域失配，第 8 类（且有 L1.5 union 救回机制）
#
# 用法: python 05-exec/r131_closure_layers.py [--json 06-benchmark/closure_layers_r131_2026-10-20.json]
# 退出码: 0 完成 / 2 任一上游面不可用（R247 禁按 0 记绿）
import argparse
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, '06-benchmark')

UPSTREAM = [
    ('direct', 'direct_closure_r131_2026-10-20.json'),
    ('tag', 'tag_closure_r127_2026-10-20.json'),
]

LAYER_ORDER = ['DIRECT', 'TAG', 'DOMAIN', 'OPEN']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    args = ap.parse_args()
    faces = {}
    for name, fn in UPSTREAM:
        p = os.path.join(BENCH, fn)
        if not os.path.isfile(p):
            print('[LAYERS] UNVERIFIED 上游面缺失: %s（%s）' % (name, fn))
            print('          禁按 0 记绿 —— 三层表必须建立在真实上游读数上')
            return 2
        try:
            faces[name] = json.loads(io.open(p, encoding='utf-8-sig').read())
        except Exception as e:  # noqa: BLE001
            print('[LAYERS] UNVERIFIED 上游面不可解析: %r' % (e,))
            return 2
    dr = faces['direct']
    tr = faces['tag']
    dq = dict((r['query'], r) for r in (dr.get('direct_closed') or []))
    tmiss = dict((r['query'], r) for r in (tr.get('rows') or []) if not r.get('actually_hit'))
    rows = []
    for q in set(list(dq.keys()) + list(tmiss.keys())):
        d = dq.get(q)
        t = tmiss.get(q)
        if d is not None and d.get('cls') == 'DIRECT_CLOSED':
            first = 'DIRECT'
        elif d is not None and d.get('cls') == 'STALE':
            first = 'STALE'
        elif t is not None and t.get('gate') == 'TAG':
            first = 'TAG'
        elif t is not None and t.get('gate') == 'DOMAIN':
            first = 'DOMAIN'
        else:
            first = 'OPEN'
        rows.append({'query': q, 'first_blocking_layer': first, 'expected': (d or t or {}).get('expected')})
    from collections import Counter
    cnt = Counter(r['first_blocking_layer'] for r in rows)
    doc = {'schema': 'closure-layers-r131-v1',
           'cmd': 'python 05-exec/r131_closure_layers.py --json <out>',
           'upstream': {k: os.path.basename(v.get('cmd', '')) for k, v in [(n, {}) for n, _ in UPSTREAM]},
           'face': {'miss_n': len(rows),
                     'by_first_layer': dict(cnt),
                     'layer_order': LAYER_ORDER,
                     'reading': {
                         'by_first_layer': '按「**最先**挡住期望件的那一层」归类；同一题可能同时被多层挡，只记最早的一层',
                         'layer_order': '修哪层收益最大：DIRECT > TAG > DOMAIN（越靠前越早出局，且 L1.5 已给域路径留了兜底）',
                         'STALE': '期望件已退役 ⇒ 属题面维护问题，不是路由缺陷（禁算进路由质量）',
                     }},
           'rows': sorted(rows, key=lambda r: (LAYER_ORDER.index(r['first_blocking_layer']), r['query']))}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    fa = doc['face']
    print('[LAYERS] 未命中 %d 题，按最先闭包层：' % fa['miss_n'])
    for k in LAYER_ORDER:
        if k in cnt:
            print('  %-8s %d' % (k, cnt[k]))
    if 'STALE' in cnt:
        print('  %-8s %d（题面过期，非路由缺陷）' % ('STALE', cnt['STALE']))
    for r in doc['rows'][:10]:
        print('  %-8s %-36s exp=%s' % (r['first_blocking_layer'], str(r['query'])[:34], r['expected']))
    if args.out:
        print('[LAYERS] JSON -> %s' % args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())