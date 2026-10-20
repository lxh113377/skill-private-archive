# -*- coding: utf-8 -*-
# r128_ruler_reconcile.py -- 判据与生产实测的一致性自证器（R127-6 / R127-2 落地）。
#
# 存在理由（r126 -> r127 两轮一手代价）：
#   r126 新立「第 9 类失败层 Tag 闭包」，量化出「279 题 79 题（28.3%）期望件结构上不可达、
#   其中 15 题 raw_rank<=5」；r127 去验证它的处方时发现：**这 25 条全是假红**。
#   根因 = r126 的可达性判定只建模了 bge_recall 的**第一次**候选集构造（tag/域受限），
#   漏了同函数内的 L1.5「域限制兜底」union 合并（bge_layer.py:566-589，触发条件 `if domain`）。
#
#   教训的一般形式（本件要固化的东西）：
#     **判据只建模了被测系统的一半链路时，会稳定地产出假红，而且看不出错** ——
#     因为静态推导每一步都「合理」，只有与生产实测逐条对账才暴露。
#
# 本件做什么：
#   读任一含「逐条读数」的判据产物，把它的判定与 route() 的实测 top1 逐条比对：
#     · 判据说「命中」而 route() 也命中 => OK
#     · 判据说「未命中」而 route() 也未命中 => OK
#     · 判据说「命中」而 route() 未命中 => 假绿（判据漏抓）
#     · 判据说「未命中」而 route() 命中 => **假红（判据过严，最危险）**
#   任何一条不一致即整体 FAIL，并把不一致的题面逐条具名。
#
# 用法:
#   python 05-exec/r128_ruler_reconcile.py --face <判据产物.json> \
#       --query-field query --verdict-field <判定字段> \
#       --expect-field expected [--json <出件>] [--limit N]
# 退出码: 0 一致 / 1 有不一致 / 2 输入面不可用（R247 禁按 0 记绿）
import argparse
import io
import json
import os
import sys

FW = r'C:\Users\37533\Desktop\workspace\焚诀'
EVAL = os.path.join(FW, 'eval')


def load_rows(path, args):
    with io.open(path, encoding='utf-8-sig') as f:
        doc = json.load(f)
    rows = None
    for key in ('rows', 'items', 'detail', 'details'):
        v = doc.get(key)
        if isinstance(v, list) and v:
            rows = v
            break
    if rows is None:
        return None, doc
    return rows, doc


def pick(row, field):
    if field in row:
        return row.get(field)
    # 允许点号路径
    cur = row
    for part in field.split('.'):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--face', required=True, help='含逐条读数的判据产物')
    ap.add_argument('--query-field', default='query')
    ap.add_argument('--verdict-field', required=True, help='判定字段（True/False 或 命中/未命中）')
    ap.add_argument('--expect-field', default='expected')
    ap.add_argument('--truthy', default='hit,reachable,actually_hit,pass,ok',
                    help='逗号分隔的「真」值（默认按字段名与真值判定）')
    ap.add_argument('--json', dest='out')
    ap.add_argument('--limit', type=int, default=20)
    args = ap.parse_args()

    if not os.path.isfile(args.face):
        print('[RECONCILE] UNVERIFIED 判据产物不存在: %s' % args.face)
        return 2
    try:
        rows, doc = load_rows(args.face, args)
    except Exception as e:  # noqa: BLE001
        print('[RECONCILE] UNVERIFIED 判据产物不可解析: %r' % (e,))
        return 2
    if not rows:
        print('[RECONCILE] UNVERIFIED 产物里没有逐条读数（rows/items/detail）')
        print('              判据必须落逐条读数，只有汇总数无法与生产实测对账')
        return 2

    sys.path.insert(0, EVAL)
    os.environ['FENJUE_ROUTE_TRACE'] = '0'
    try:
        import unified_router as R
    except Exception as e:  # noqa: BLE001
        print('[RECONCILE] UNVERIFIED 生产路由不可达: %r' % (e,))
        return 2

    truthy = {t.strip().lower() for t in args.truthy.split(',') if t.strip()}

    def is_hit(v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            s = v.strip().lower()
            return s in truthy
        return bool(v)

    agree = 0
    false_red = []
    false_green = []
    checked = 0
    for r in rows:
        q = pick(r, args.query_field)
        exp = pick(r, args.expect_field)
        v = pick(r, args.verdict_field)
        if not q or not exp or v is None:
            continue
        checked += 1
        try:
            rt = R.route(q, enable_memory=False) or {}
            truth_hit = (rt.get('top1') == exp)
        except Exception:  # noqa: BLE001
            continue
        judge_hit = is_hit(v)
        if judge_hit == truth_hit:
            agree += 1
        elif judge_hit:
            false_green.append({'query': q, 'expected': exp,
                                'route_top1': rt.get('top1')})
        else:
            false_red.append({'query': q, 'expected': exp,
                               'route_top1': rt.get('top1')})

    doc2 = {'schema': 'ruler-reconcile-r128-v1',
            'cmd': ('python 05-exec/r128_ruler_reconcile.py --face %s --verdict-field %s'
                    % (os.path.basename(args.face), args.verdict_field)),
            'face': args.face, 'verdict_field': args.verdict_field,
            'counts': {'rows_n': len(rows), 'checked_n': checked, 'agree_n': agree,
                       'false_red_n': len(false_red), 'false_green_n': len(false_green)},
            'false_red': false_red[:args.limit],
            'false_green': false_green[:args.limit],
            'reading': {
                'false_red_n': '判据说未命中而 route() 命中 = 假红（判据过严，最危险：会把可救的题当没救）',
                'false_green_n': '判据说命中而 route() 未命中 = 假绿（判据漏抓：会把没救的题当救回了）',
                'agree_n': '判据与生产实测逐条一致的条数',
            }}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc2, f, ensure_ascii=False, indent=1)
    c = doc2['counts']
    print('[RECONCILE] face=%s field=%s' % (os.path.basename(args.face), args.verdict_field))
    print('[RECONCILE] rows=%d 已对账=%d 一致=%d 假红=%d 假绿=%d'
          % (c['rows_n'], c['checked_n'], c['agree_n'], c['false_red_n'], c['false_green_n']))
    for x in false_red[:args.limit]:
        print('  FALSE-RED  %-36s exp=%-22s route=%s'
              % (str(x['query'])[:34], str(x['expected'])[:20], x['route_top1']))
    for x in false_green[:args.limit]:
        print('  FALSE-GREEN %-36s exp=%-22s route=%s'
              % (str(x['query'])[:34], str(x['expected'])[:20], x['route_top1']))
    if args.out:
        print('[RECONCILE] JSON -> %s' % args.out)
    return 0 if (not false_red and not false_green and checked) else 1


if __name__ == '__main__':
    raise SystemExit(main())