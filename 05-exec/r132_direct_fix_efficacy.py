# -*- coding: utf-8 -*-
# r132_direct_fix_efficacy.py -- 转办处方的**实测效力**面（r132 新增）。
#
# 存在理由（r132 一手）：r131 我把处方①「direct_route 命中后放行到 tag/bge 层」写进了转办提案第 10 条，
# 但**没实测过它能救几条**。r132 实测：6 条 DIRECT_CLOSED 里，处方①只救回 2/6 ——
# 其余 4 条即使关掉 direct 层也仍拿不到 top1。
#
# 根因（本件测出来的）：direct_route 与 tag_filter **串谋** ——
# 6 条里 5 条的期望件根本不在 tag_hits 里（只有「HTML 演示文稿」那条在），
# 所以「放行到 tag 层」这条路对 5 条是死路：期望件连候选集都进不去。
#
# 本件对每条 DIRECT_CLOSED 逐条给出该条实际能被哪类处方救：
#   A_DIRECT_ONLY   —— 关掉 direct 就能救（期望件上 top1）
#   B_NEIGHBOR_RANK —— 关掉 direct 仍不够，期望件浮上来了但被语义邻居压（需排序面/语料面）
#   C_STALE         —— 期望件已退役（题面问题，不是路由问题）
#   D_UNREACHABLE   —— 关掉 direct 仍完全浮不上来（需 tag/domain 层先放行）
#
# 用法: python 05-exec/r132_direct_fix_efficacy.py --json 06-benchmark/direct_fix_efficacy_r132_2026-10-20.json
# 退出码: 0 完成 / 2 输入面不可用（R247 禁按 0 记绿）
import argparse
import io
import json
import os
import sys
from collections import Counter

FW = r'C:\Users\37533\Desktop\workspace\焚诀'
EVAL = os.path.join(FW, 'eval')
GS = r'D:\global_skills'
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UP = os.path.join(ROOT, '06-benchmark', 'direct_closure_r131_2026-10-20.json')

READING = {
    'fix1_effective_n': '处方①(direct 放行到 tag/bge 层)实测能救的条数 = A_DIRECT_ONLY + B_NEIGHBOR_RANK。B 类还需额外的排序/语料面处方，D 类则完全无效（期望件连候选集都进不去）。',
    'exp_in_tags_n': 'direct 与 tag 串谋的量化：期望件不在 tag_hits 里的条数。占比高 => 处方①对大多数条目是死路，须先修 tag/domain 层。',
    'A_DIRECT_ONLY': '关掉 direct 即救回（期望件上 top1）',
    'B_NEIGHBOR_RANK': '关掉 direct 后期望件浮上来但被语义邻居压（需排序面处方）',
    'C_STALE': '期望件已退役 => 题面问题，不是路由问题',
    'D_UNREACHABLE': '关掉 direct 仍完全浮不上来 => 须先修 tag/domain 层',
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    ap.add_argument('--limit', type=int, default=20)
    args = ap.parse_args()
    if not os.path.isfile(UP):
        print('[EFFICACY] UNVERIFIED 上游面缺失: %s' % os.path.basename(UP))
        print('           禁按 0 记绿 —— 效力面必须建立在真实 direct_closure 读数上')
        return 2
    up = json.loads(io.open(UP, encoding='utf-8-sig').read())
    rows = up.get('direct_closed') or []
    if not rows:
        print('[EFFICACY] UNVERIFIED 上游面 direct_closed 为空')
        return 2
    sys.path.insert(0, EVAL)
    os.environ['FENJUE_ROUTE_TRACE'] = '0'
    try:
        import unified_router as R
        import bge_layer
    except Exception as e:  # noqa: BLE001
        print('[EFFICACY] FATAL 判据面不可用: %r' % (e,))
        return 2
    out_rows = []
    for r in rows:
        q = r['query']
        exp = r['expected']
        on_disk = os.path.isfile(os.path.join(GS, exp, 'SKILL.md'))
        nq = R.normalize_query(q)
        dom = R.classify_domain(nq)
        tags = R.tag_filter(nq, dom)
        exp_in_tags = exp in (tags or [])
        try:
            cands = bge_layer.bge_recall(nq, tags, dom, 10, raw_query=q) or []
            names = [c['name'] for c in cands]
            top = names[0] if names else None
            rank = (names.index(exp) + 1) if exp in names else None
        except Exception:  # noqa: BLE001
            names, top, rank = [], None, None
        if not on_disk:
            cls = 'C_STALE'
        elif top == exp:
            cls = 'A_DIRECT_ONLY'
        elif rank is not None:
            cls = 'B_NEIGHBOR_RANK'
        else:
            cls = 'D_UNREACHABLE'
        out_rows.append({'query': q, 'expected': exp, 'on_disk': on_disk,
                         'domain': dom, 'tag_hits': tags, 'exp_in_tags': exp_in_tags,
                         'would_top1': top, 'would_rank': rank, 'class': cls})
    cnt = Counter(x['class'] for x in out_rows)
    fix1 = cnt.get('A_DIRECT_ONLY', 0) + cnt.get('B_NEIGHBOR_RANK', 0)
    doc = {'schema': 'direct-fix-efficacy-r132-v1',
           'cmd': 'python 05-exec/r132_direct_fix_efficacy.py --json <out>',
           'upstream': os.path.basename(UP),
           'face': {'closed_n': len(out_rows),
                     'by_class': dict(cnt),
                     'exp_in_tags_n': sum(1 for x in out_rows if x['exp_in_tags']),
                     'fix1_effective_n': fix1,
                     'reading': READING},
           'rows': out_rows[:args.limit]}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    fa = doc['face']
    print('[EFFICACY] 闭包 %d 条 | 处方①有效 %d | 期望件不在 tag 内 %d'
          % (fa['closed_n'], fa['fix1_effective_n'], fa['exp_in_tags_n']))
    for k in ('A_DIRECT_ONLY', 'B_NEIGHBOR_RANK', 'C_STALE', 'D_UNREACHABLE'):
        if k in cnt:
            print('  %-16s %d' % (k, cnt[k]))
    for x in doc['rows']:
        print('  %-16s %-26s exp_rank=%s exp_in_tags=%s' % (x['class'], str(x['query'])[:24], x['would_rank'], x['exp_in_tags']))
    if args.out:
        print('[EFFICACY] JSON -> %s' % args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())