# -*- coding: utf-8 -*-
# r130_latent_trend.py -- latent 两态计数的趋势面（R129-4 落地）。
#
# 存在理由：r129 把 latent 语义的「正常」定义从硬编码改成实测两态计数
# （latent_rescued_n / latent_realized_n），单轮读数已落进 r128 的产物。
# 但单轮读数只回答「现在多少」，回答不了「在变好还是变坏」。
# 本件把历次读数攒成趋势台账，并给出两个方向性读数：
#   · rescued_ratio = rescued / (rescued + realized) —— 潜在面被救回的比例；
#     比例上升 => L1.5 兜底在变强；比例下降 => 兜底在变弱，是提前预警。
#   · delta_vs_prev = 本轮 ratio - 上轮 ratio
#
# 用法: python 05-exec/r130_latent_trend.py [--record <件>] [--json <出件>]
# 退出码: 0 完成 / 1 无历史可比 / 2 输入面不可用
import argparse
import io
import json
import os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TREND = os.path.join(ROOT, '06-benchmark', 'latent_trend.json')


def read_counts(path):
    with io.open(path, encoding='utf-8-sig') as f:
        doc = json.load(f)
    c = (doc or {}).get('counts') or {}
    return int(c.get('latent_rescued_n') or 0), int(c.get('latent_realized_n') or 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--record', help='从该对账产物读两态计数并记入趋势台账')
    ap.add_argument('--json', dest='out')
    args = ap.parse_args()

    hist = []
    if os.path.isfile(TREND):
        try:
            hist = (json.loads(io.open(TREND, encoding='utf-8').read()) or {}).get('history') or []
        except Exception:
            hist = []

    if args.record:
        p = args.record if os.path.isabs(args.record) else os.path.join(ROOT, args.record)
        if not os.path.isfile(p):
            print('[TREND] UNVERIFIED 产物不存在: %s' % args.record)
            return 2
        try:
            res, real = read_counts(p)
        except Exception as e:  # noqa: BLE001
            print('[TREND] UNVERIFIED 产物里没有 latent 两态计数: %r' % (e,))
            print('           该产物须由 r128_ruler_reconcile.py --semantics latent 生成')
            return 2
        hist.append({'at': datetime.now().strftime('%Y-%m-%d %H:%M'),
                   'source': os.path.basename(args.record),
                   'rescued_n': res, 'realized_n': real})
        doc = {'schema': 'latent-trend-r130-v1', 'history': hist}
        os.makedirs(os.path.dirname(TREND), exist_ok=True)
        with io.open(TREND, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print('[TREND] RECORDED %s rescued=%d realized=%d（累计 %d 条）'
              % (os.path.basename(args.record), res, real, len(hist)))

    if not hist:
        print('[TREND] 无历史记录 => 趋势不可算（须先 --record 一次）')
        return 1

    for h in hist:
        tot = h['rescued_n'] + h['realized_n']
        h['rescued_ratio'] = round(h['rescued_n'] / tot, 4) if tot else None
    last = hist[-1]
    prev = hist[-2] if len(hist) >= 2 else None
    delta = None
    if prev and last['rescued_ratio'] is not None and prev.get('rescued_ratio') is not None:
        delta = round(last['rescued_ratio'] - prev['rescued_ratio'], 4)
    direction = None
    if delta is not None:
        direction = '兜底在变强' if delta > 0 else ('兜底在变弱（预警）' if delta < 0 else '持平')
    doc = {'schema': 'latent-trend-r130-v1', 'history': hist,
           'latest': {'rescued_n': last['rescued_n'],
                     'realized_n': last['realized_n'],
                     'rescued_ratio': last['rescued_ratio'],
                     'delta_vs_prev': delta,
                     'direction': direction}}
    with io.open(TREND, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    print('[TREND] 样本 %d | 本轮 rescued=%d realized=%d ratio=%s | delta=%s（%s）'
          % (len(hist), last['rescued_n'], last['realized_n'],
             last['rescued_ratio'], delta, direction))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())