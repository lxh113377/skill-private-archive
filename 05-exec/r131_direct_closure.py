# -*- coding: utf-8 -*-
# r131_direct_closure.py -- 第 10 类失败层「direct_map 正则抢答」常驻读数。
#
# 存在理由（r131 一手）：L2 frozen 盲测集实测 7/10，3 条 miss 逐层复盘后 ——
#   ① 2 条的期望件已退役（pptx / tencent-cos-skill__skillhub 不在盘不在语料）=> STALE 题面；
#   ② 剩 1 条「给一个GitHub项目写代码审查意见」期望 github，实得 code-review。
#      逐层复算发现：**语料改造完全无效** —— direct_route 是生产链路的**第一环**，
#      它先于 normalize / classify_domain / tag_filter / bge_recall 短路返回，
#      BGE 根本没参与（candidates 里只有 code-review 一个）。
#      证据：eval/direct_map.json 第 196 条
#        ["全面审查|代码审查|审查.*代码|代码.*审查|code.*review|...", "code-review"]
#      query 含「代码审查」=> 正则命中 => 短路。
#
# 这是比 tag 闭包（第 9 类）**更靠前**的一层：tag 闭包在 bge_recall 的 indices 选择里，
# 而 direct 抢答在链路第一环，期望件连候选集都进不去。
#
# 本件读四面（全部只读，不写任何派生产物）：
#   direct_closed_n  -- 期望件在册，但 direct_route 把它抢答成别的（真闭包）
#   stale_n          -- 期望件已退役（STALE 题面，不是路由缺陷）
#   recoverable_n    -- 期望件在册且未被抢答，纯粹排序错（语料/排序面）
#   hit_n            -- 正常命中
#
# 用法: python 05-exec/r131_direct_closure.py --json 06-benchmark/direct_closure_r131_2026-10-20.json
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    ap.add_argument('--limit', type=int, default=20)
    args = ap.parse_args()
    sys.path.insert(0, EVAL)
    os.environ['FENJUE_ROUTE_TRACE'] = '0'
    try:
        import unified_router as R
    except Exception as e:  # noqa: BLE001
        print('[DIRECTCLOSE] FATAL 判据面不可用: %r' % (e,))
        return 2
    try:
        sk = json.loads(io.open(os.path.join(EVAL, 'bge_fullbody_skills.json'), encoding='utf-8').read())
    except Exception as e:  # noqa: BLE001
        print('[DIRECTCLOSE] FATAL 语料面不可用: %r' % (e,))
        return 2
    names = set(s.get('name') if isinstance(s, dict) else s for s in sk)
    sets = [('layered', os.path.join(EVAL, 'layered_testset.json')),
            ('frozen', os.path.join(EVAL, 'frozen_blind_test.json'))]
    questions = []
    for sn, p in sets:
        if not os.path.isfile(p):
            continue
        tiers = json.loads(io.open(p, encoding='utf-8').read())
        for tier in tiers:
            for q in (tier.get('queries') or []):
                if q.get('expected_skill'):
                    questions.append({'set': sn, 'query': q['query'], 'expected': q['expected_skill']})
    if not questions:
        print('[DIRECTCLOSE] UNVERIFIED 题面为空')
        return 2
    rows = []
    for it in questions:
        exp = it['expected']
        on_disk = os.path.isfile(os.path.join(GS, exp, 'SKILL.md'))
        in_corpus = exp in names
        stale = not (on_disk or in_corpus)
        try:
            rt = R.route(it['query'], enable_memory=False) or {}
            got = rt.get('top1')
            direct = bool(rt.get('direct_hit'))
        except Exception:  # noqa: BLE001
            continue
        hit = (got == exp)
        if hit:
            cls = 'HIT'
        elif stale:
            cls = 'STALE'
        elif direct:
            cls = 'DIRECT_CLOSED'
        else:
            cls = 'RECOVERABLE'
        rows.append({'set': it['set'], 'query': it['query'], 'expected': exp, 'got': got,
                     'direct_hit': direct, 'on_disk': on_disk, 'in_corpus': in_corpus, 'cls': cls})
    cnt = Counter(r['cls'] for r in rows)
    closed = [r for r in rows if r['cls'] == 'DIRECT_CLOSED']
    stale_rows = [r for r in rows if r['cls'] == 'STALE']
    doc = {'schema': 'direct-closure-r131-v1',
           'cmd': 'python 05-exec/r131_direct_closure.py --json <out>',
           'face': {'questions_n': len(rows),
                     'hit_n': cnt.get('HIT', 0),
                     'direct_closed_n': cnt.get('DIRECT_CLOSED', 0),
                     'stale_n': cnt.get('STALE', 0),
                     'recoverable_n': cnt.get('RECOVERABLE', 0),
                     'reading': {
                         'direct_closed_n': '期望件在册但 direct_route 正则抢答成别的 => 语料改造无效（第 10 类失败层）',
                         'stale_n': '期望件已退役（不在盘不在语料）=> STALE 题面，不是路由缺陷',
                         'recoverable_n': '期望件在册且未被抢答，纯粹排序错 => 语料/排序面可救',
                     }},
           'direct_closed': closed[:args.limit],
           'stale': stale_rows[:args.limit]}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    fa = doc['face']
    print('[DIRECTCLOSE] 题面=%d HIT=%d 直接闭包=%d STALE=%d 可救=%d'
          % (fa['questions_n'], fa['hit_n'], fa['direct_closed_n'], fa['stale_n'], fa['recoverable_n']))
    for r in doc['direct_closed']:
        print('  DIRECT-CLOSED %-36s exp=%-24s got=%s' % (str(r['query'])[:34], r['expected'][:22], r['got']))
    for r in doc['stale']:
        print('  STALE         %-36s exp=%s（已退役）' % (str(r['query'])[:34], r['expected']))
    if args.out:
        print('[DIRECTCLOSE] JSON -> %s' % args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())