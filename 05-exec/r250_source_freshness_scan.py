# -*- coding: utf-8 -*-
"""r250_source_freshness_scan.py - 名册源件新鲜度审计（r250 新建，只读）。

存在理由（r250 一手）：r249 抓到「门跑了 ≠ 产物更新」（第 67 门 argv 为空、从不落盘，名册读我手工快照）。
  本轮把同类**枚举一遍**：核名册/审计读的每个源件「谁写的、何时写的」。实测 16 个源件里 **6 个无门声明产出**，
  其中四件是真问题：
    free_tools_latest.json（名册**行清单**）  停 10-24 22:42 —— 陈旧两天（产出者 free_tools_face argv 为空）
    gh_billing_latest.json（r241 官方计费面）  产物只在手工跑时更新（建了面但没进表）
    turnstile_usage_latest.json（r242 面）     同上
    route_truth_latest.json（召回真值面）      产出者 r209 根本不在表
  本件把这套核查机械化：

  判据 A（来源）：名册读的每个源件必须在某道门的 argv 里被声明为 --json 输出；
            豁免 = 人工维护的配置表（tool_carrier_patterns.json）与 r* 退回项（手工快照，已被 canonical 取代）。
  判据 B（新鲜度）：源件 mtime 不得早于最近一次门跑（gate_runs.jsonl 的 mtime）超过 GRACE 小时；
            陈旧件具名列出（不判红 —— 有的源件本就低频，但要**看得见**）。

为什么要独立成门而不是塞进 r215：r215 的牙管**值**（一致/口径），本件管**来源与新鲜度** ——
  两者是不同的问题：值全对但源件陈旧（r249/r250 四次实例）照样是错读数。

三态：A 违例 ⇒ FAIL(1)；只有 B 陈旧 ⇒ PASS 但逐件印出【陈旧】；import 面取不到 ⇒ UNVERIFIED(2)。
用法: python 05-exec/r250_source_freshness_scan.py [--json <件>] [--grace-hours 6]
"""
import argparse
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
B = os.path.join(ROOT, '06-benchmark')
sys.path.insert(0, HERE)

WHITELIST = ('tool_carrier_patterns.json',)


def gate_outputs():
    import run_gates as RG
    outs = {}
    for g in getattr(RG, 'GATES', []):
        a = g.get('argv') or []
        for i, x in enumerate(a):
            if x == '--json' and i + 1 < len(a):
                outs[os.path.basename(a[i + 1])] = g.get('id')
    return outs


def roster_sources():
    import r215_free_tool_roster as ros
    srcs = []
    for k, fn in ros.SRC.items():
        srcs.append(('%s' % k, fn))
    for tool, spec in (ros.READ_FACE or {}).items():
        if spec.get('artifact'):
            srcs.append(('readface:%s' % tool, spec['artifact']))
    return srcs


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out', default='')
    ap.add_argument('--grace-hours', dest='grace', type=float, default=6.0)
    args = ap.parse_args(argv)
    try:
        outs = gate_outputs()
        srcs = roster_sources()
    except Exception as e:
        print('[SRCFRESH:UNVERIFIED] 取不到门表或名册源表（面变了？）：%r' % (e,))
        return 2
    if not outs or not srcs:
        print('[SRCFRESH:UNVERIFIED] 门声明产出为 0 或源件为 0 ⇒ 空面不得判绿')
        return 2
    ref = os.path.join(B, 'gate_runs.jsonl')
    ref_mt = os.path.getmtime(ref) if os.path.isfile(ref) else None
    orphan = []
    rows = []
    for k, fn in srcs:
        if '*' in fn or fn in WHITELIST:
            rows.append((k, fn, 'EXEMPT', None, False))
            continue
        decl = outs.get(fn)
        fp = os.path.join(B, fn)
        mt = os.path.getmtime(fp) if os.path.isfile(fp) else None
        stale = bool(ref_mt and mt and (ref_mt - mt) > args.grace * 3600)
        if not decl:
            orphan.append(fn)
        rows.append((k, fn, decl or 'NO', mt, stale))
    stale_files = [r[1] for r in rows if r[4]]
    doc = {'schema': 'source-freshness-v1', 'readonly': True,
           'provenance_cmd': 'python 05-exec/r250_source_freshness_scan.py --json <件>',
           'gate_declared_outputs': len(outs), 'roster_sources': len(srcs),
           'reference_gate_runs_mtime': ref_mt, 'grace_hours': args.grace,
           'orphans': orphan, 'stale': stale_files,
           'rows': [{'use': r[0], 'file': r[1], 'declared_by': r[2],
                     'mtime': r[3], 'stale': r[4]} for r in rows]}
    if args.out:
        op = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
        io.open(op, 'w', encoding='utf-8', newline=chr(10)).write(
            json.dumps(doc, ensure_ascii=False, indent=1))
    print('[SRCFRESH] 门声明产出 %d 件 ｜ 名册源件 %d 件 ｜ 陈旧 %d 件' % (
        len(outs), len(srcs), len(stale_files)))
    for r in rows:
        if r[2] == 'NO':
            print('  无门产出: %s（%s）' % (r[1], r[0]))
        elif r[4]:
            print('  【陈旧】%s（%s）mtime=%s' % (
                r[1], r[0], time.strftime('%m-%d %H:%M', time.localtime(r[3]))))
    if orphan:
        print('[SRCFRESH:FAIL] %d 个源件无门声明产出 ⇒ 只能靠我手工跑，会静默陈旧' % len(orphan))
        return 1
    print('[SRCFRESH:PASS] 名册源件均有门逐轮产出（陈旧 %d 件已逐件印出，不判红）' % len(stale_files))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())