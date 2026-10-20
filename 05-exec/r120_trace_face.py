# -*- coding: utf-8 -*-
r'''r120_trace_face.py -- 生产流量面常驻读数（R120-4 落地）。

存在理由（r120 一手）：
  r120 首次分析 `eval/route_trace.jsonl` 即得出结论「路由缺口集中在合成评测题面，
  不在真实使用」——332 个唯一真实 query、LOW 置信仅 3 个。但那是**一次性脚本**，
  而生产流量每天都在新增 ⇒ 不常驻就等于「结论永远停留在 10-20 那一天」。

本件把该分析固化为常驻面，四个子读数：
  ① volume    —— 总行数 / 时间跨度 / 日均
  ② uniques   —— 去测试串后唯一 query 数（噪声串形态可配置扩展）
  ③ confidence—— HIGH/MEDIUM/LOW 分布 + LOW 集具名（低置信 = 潜在误路由）
  ④ freshness —— 末条时间距今天数（断流告警）

口径红线：
  · 噪声串判定用**形态白名单**（`^轮\d+` / `^另一个全新问句` / `唯一串` / `zzd+` 等），
    命中即剔除并**计数**（禁静默丢分母）；
  · 只读 jsonl，不写任何文件；
  · 文件缺失/解析全失败 ⇒ rc=2（R247 禁按 0 记绿）。

用法：python 05-exec/r120_trace_face.py --json 06-benchmark/trace_face_r120_2026-10-20.json
退出码：0 完成 / 2 输入面不可用
'''
import argparse
import io
import json
import os
import re
import sys
from datetime import datetime

TRACE = r'C:\Users\37533\Desktop\workspace\焚诀\eval\route_trace.jsonl'

# r120 实测噪声串形态（111 个 LOW 里 108 个命中）；新增形态只增不减
NOISE_PATTERNS = [
    r'^轮\d+',
    r'^另一个全新问句',
    r'^唯一串',
    r'^zzd+',
    r'^健康态问句',
    r'^全新验证',
    r'^测试',
    r'^smoke',
]
NOISE_RE = re.compile('|'.join(NOISE_PATTERNS))


def parse_ts(s):
    for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S%z'):
        try:
            return datetime.strptime(s, fmt)
        except (ValueError, TypeError):
            continue
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    args = ap.parse_args()

    if not os.path.isfile(TRACE):
        print('[TRACEFACE] UNVERIFIED 流量文件缺失: %s（R247 禁按 0 记绿）' % TRACE)
        return 2
    rows, bad = [], 0
    with io.open(TRACE, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                bad += 1
    if not rows:
        print('[TRACEFACE] UNVERIFIED 零行可解析（bad=%d）⇒ 禁按 0 记绿' % bad)
        return 2

    tss = [parse_ts(r.get('ts') or '') for r in rows]
    tss = [t for t in tss if t]
    span_days = None
    if len(tss) >= 2:
        span_days = round((max(tss) - min(tss)).total_seconds() / 86400.0, 2)
    freshness_days = None
    if tss:
        freshness_days = round((datetime.now() - max(tss)).total_seconds() / 86400.0, 2)

    noise_n = 0
    empty_n = 0
    uniq = {}
    for r in rows:
        q = (r.get('q') or '').strip()
        if not q:
            empty_n += 1          # r120b 自抓：空 q 行原来被静默跳过 ⇒ 守恒不成立
            continue
        if NOISE_RE.search(q):
            noise_n += 1
            continue
        uniq[q] = uniq.get(q, 0) + 1

    conf = {}
    low = []
    for r in rows:
        c = r.get('confidence') or 'UNKNOWN'
        conf[c] = conf.get(c, 0) + 1
        if c == 'LOW':
            low.append({'q': (r.get('q') or '')[:80], 'top1': r.get('top1'),
                        'ts': r.get('ts')})
    src = {}
    for r in rows:
        s = r.get('src') or 'unknown'
        src[s] = src.get(s, 0) + 1

    doc = {
        'schema': 'trace-face-r120-v1',
        'cmd': 'python 05-exec/r120_trace_face.py --json <out>',
        'source': TRACE,
        'face': {
            'rows_n': len(rows),
            'bad_lines_n': bad,
            'noise_n': noise_n,
            'empty_q_n': empty_n,
            'unique_n': len(uniq),
            'span_days': span_days,
            'freshness_days': freshness_days,
            'confidence': conf,
            'low_n': len(low),
            'src': src,
            'conservation_ok': (noise_n + empty_n + sum(uniq.values())) == len(rows),
        },
        'low_confidence': low[:50],
        'noise_patterns': NOISE_PATTERNS,
        'reading': {
            'unique_n': '去测试串后的唯一真实 query 数 —— 真实使用面规模',
            'low_n': 'LOW 置信条数（潜在误路由，需人读）',
            'freshness_days': '末条距今天数；>7 天 ⇒ 生产已断流或文件被轮换（告警不判红）',
            'conservation_ok': '噪声数 + 空 q 数 + 唯一 query 计数和 == 总行数（分母不许静默变小）',
        },
    }
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    f = doc['face']
    print('[TRACEFACE] rows=%d bad=%d noise=%d unique=%d span=%sdays fresh=%sdays'
          % (f['rows_n'], f['bad_lines_n'], f['noise_n'], f['unique_n'],
             f['span_days'], f['freshness_days']))
    print('[TRACEFACE] confidence=%s low=%d src=%s'
          % (json.dumps(f['confidence'], ensure_ascii=False), f['low_n'],
             json.dumps(f['src'], ensure_ascii=False)))
    print('[TRACEFACE] conservation_ok=%s' % f['conservation_ok'])
    if args.out:
        print('[TRACEFACE] JSON -> %s' % args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())