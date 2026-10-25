# -*- coding: utf-8 -*-
"""r254_teeth_proof_matrix.py - 逐门证伪矩阵：谁被证明过「能红」（r254 新建，只读）。

存在理由（r254 一手，r253 教训的上一层）：r253 证明「侦测器必须拿已知坏输入验一次」；
  那么下一个问题就是 —— **我有 107 道门，其中几道真的被证明过「能红」？**
  「门跑过」「门是绿的」都不算证明；证明 = 有一个夹具/自检/变异对照，**喂它一个该红的输入并看它红**。

本件对门表逐门判定三种证明形态：
  fixture  : 05-exec 下存在 *fixtures*.py，且其内容提到该门的 script 或 id；
  mutation : 该夹具里出现「变异/MUTATION」字样（即有『把判据改坏必须被抓』的对照）；
  selftest : 该门脚本自身含 selftest（--selftest 路径）。

判据：**关键集**（CRITICAL，= 本目标交付物所依赖的度量与判据门）里每一道都必须有 mutation 或 selftest；
  否则 FAIL 并逐门具名（禁把「没人证伪过」的门算进可信度）。非关键集只统计、不判红。
三态：门表取不到/无夹具面 ⇒ UNVERIFIED(2)。
用法: python 05-exec/r254_teeth_proof_matrix.py [--json <件>]
"""
import argparse
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

CRITICAL = ('free_tools_face', 'tool_skill_matrix', 'workflow_usage_face', 'free_tool_roster_face',
            'roster_audit', 'roster_fixtures', 'source_freshness_scan', 'dup_policy_scan',
            'judge_binding_scan', 'struct_recount_face', 'gov_acceptance_face')


def fixture_files():
    out = []
    for f in sorted(os.listdir(HERE)):
        if f.endswith('.py') and 'fixture' in f:
            out.append(os.path.join(HERE, f))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out', default='')
    args = ap.parse_args(argv)
    try:
        import run_gates as RG
        gates = list(getattr(RG, 'GATES', []))
    except Exception as e:
        print('[PROOFMAT:UNVERIFIED] 取不到门表：%r' % (e,))
        return 2
    fx = fixture_files()
    if not fx:
        print('[PROOFMAT:UNVERIFIED] 没有夹具件 ⇒ 空面不得判绿')
        return 2
    texts = {}
    for f in fx:
        try:
            texts[f] = io.open(f, encoding='utf-8', errors='replace').read()
        except OSError:
            pass
    rows = []
    for g in gates:
        gid = str(g.get('id') or '')
        script = str(g.get('script') or '')
        key = script.replace('.py', '')
        has_fx = any((script and script in t) or (key and key in t) or (gid and gid in t)
                     for t in texts.values())
        has_mut = any((('MUTATION' in t) or ('变异' in t))
                      and ((script and script in t) or (key and key in t) or (gid and gid in t))
                      for t in texts.values())
        sp = os.path.join(HERE, script) if script else ''
        has_st = False
        if sp and os.path.isfile(sp):
            try:
                has_st = 'selftest' in io.open(sp, encoding='utf-8', errors='replace').read()
            except OSError:
                has_st = False
        proof = 'mutation' if has_mut else ('fixture' if has_fx else ('selftest' if has_st else 'NONE'))
        rows.append({'id': gid, 'script': script, 'fixture': has_fx,
                     'mutation': has_mut, 'selftest': has_st, 'proof': proof})
    crit_missing = [r['id'] for r in rows if r['id'] in CRITICAL
                     and not (r['mutation'] or r['selftest'])]
    doc = {'schema': 'teeth-proof-matrix-v1', 'readonly': True,
           'provenance_cmd': 'python 05-exec/r254_teeth_proof_matrix.py --json <件>',
           'gates_n': len(rows), 'fixture_files': [os.path.basename(f) for f in fx],
           'critical': list(CRITICAL), 'critical_missing_proof': crit_missing,
           'rows': rows}
    if args.out:
        op = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
        io.open(op, 'w', encoding='utf-8', newline=chr(10)).write(
            json.dumps(doc, ensure_ascii=False, indent=1))
    byp = {}
    for r in rows:
        byp[r['proof']] = byp.get(r['proof'], 0) + 1
    print('[PROOFMAT] 门 %d 道 ｜ 夹具件 %d 个 ｜ 证明形态分布 %s' % (
        len(rows), len(fx), byp))
    print('  关键集缺证明 = %s' % (crit_missing or '（无）'))
    for r in rows:
        if r['id'] in CRITICAL:
            print('  %-24s proof=%s' % (r['id'], r['proof']))
    if crit_missing:
        print('[PROOFMAT:FAIL] 关键集里 %d 道门从未被证明「能红」⇒ 禁把它算进可信度' % len(crit_missing))
        return 1
    print('[PROOFMAT:PASS] 关键集每道门都有 mutation 或 selftest 证明')
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())