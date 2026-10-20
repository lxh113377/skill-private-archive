# -*- coding: utf-8 -*-
# r130_mark_superseded.py -- 给已被取代的判据产物批量标注 superseded_by（R129-3 落地）。
#
# 存在理由：r128 的全仓对账普查发现 21 份含逐条读数的产物里，
# route_miss_attr_r117 有 5 条假红（20 条中仅 15 条与 route() 一致）。
# 但该产物文件名不带取代标记，后人「按 mtime 取最新文件」时仍可能取到它当成现行结论。
# r129 已给 r117_route_miss_attr.py 的脚本加了 superseded_by 字段，历史产物还没有。
#
# 本件只写这三个字段（取代者 / 取代理由 / 标注时间），不动任何读数。
#
# 用法: python 05-exec/r130_mark_superseded.py [--dry-run] [--json <出件>]
# 退出码: 0 完成 / 2 输入面不可用
import argparse
import glob
import io
import json
import os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, '06-benchmark')

# 跨脚本 / 跨轮取代关系（显式列出，避免「按 round 号自动推」猜错）
CROSS_SUPERSEDED = [
    ('route_miss_attr_r117_', 'route_miss_attr_r123_*.json（r119 起改用实测口径；r117 有 5 条假红）'),
    ('route_miss_attr_r119_2026-10-20.json', 'route_miss_attr_r123_*.json（r123 是当前最新）'),
    ('route_miss_attr_r119b_', 'route_miss_attr_r123_*.json（同上）'),
    ('route_miss_attr_r119c_', 'route_miss_attr_r123_*.json（同上）'),
    ('route_miss_attr_r122_', 'route_miss_attr_r123_*.json（同上）'),
    ('layer_attr_r118_', 'tag_closure_r127_*.json（r126 第 9 类失败层给出可达/不可达，比 layer 名更直接）'),
    ('layer_attr_r119_', 'tag_closure_r127_*.json（同上）'),
    ('domain_mismatch_r120_', 'tag_closure_r127_*.json（r127 指出 r120 用 raw classify_domain 会高估脆弱面）'),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--json', dest='out')
    args = ap.parse_args()
    if not os.path.isdir(BENCH):
        print('[SUP] UNVERIFIED 产物目录不存在: %s' % BENCH)
        return 2
    marked = []
    for prefix, reason in CROSS_SUPERSEDED:
        for p in sorted(glob.glob(os.path.join(BENCH, prefix + '*'))):
            if not p.endswith('.json'):
                continue
            try:
                with io.open(p, encoding='utf-8-sig') as f:
                    d = json.load(f)
            except Exception:
                continue
            if not isinstance(d, dict) or d.get('superseded_by'):
                continue
            d['superseded_by'] = reason
            d['superseded_reason'] = 'r130 批量标注：r128 对账普查已实证本件有假红或口径被取代'
            d['superseded_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            if not args.dry_run:
                with io.open(p, 'w', encoding='utf-8', newline=chr(10)) as f:
                    json.dump(d, f, ensure_ascii=False, indent=1)
            marked.append(os.path.basename(p))
    print('[SUP] 标注 %d 份产物（%s）' % (len(marked), 'dry-run' if args.dry_run else '已落盘'))
    for m in marked:
        print('  MARKED %s' % m)
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline=chr(10)) as f:
            json.dump({'schema': 'mark-superseded-r130-v1', 'marked': marked},
                      f, ensure_ascii=False, indent=1)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())