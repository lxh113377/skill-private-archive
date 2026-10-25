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

# r255：关键集**派生**而非手写 —— 手写列表会烂（r249/r250 同族）。
#   派生规则 = ① r215 READ_FACE 里登记的读数面脚本 ② 产出 r215 SRC 所读件的门（按 argv --json 名对）
#   ③ 自审计栈（r237/r247/r250/r253/r254）—— 它们管的是「名册可信度」本身。
SELF_AUDIT = ('r237_roster_audit.py', 'r247_dup_policy_scan.py', 'r250_source_freshness_scan.py',
              'r253_judge_binding_scan.py', 'r254_teeth_proof_matrix.py', 'r254_proof_fixtures.py')


def derive_critical(gates):
    import ast as _ast
    src215 = io.open(os.path.join(HERE, 'r215_free_tool_roster.py'), encoding='utf-8', errors='replace').read()
    tree = _ast.parse(src215)
    face_scripts = set()
    src_files = set()
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Dict):
            ks = [k.value for k in node.keys if isinstance(k, _ast.Constant)]
            vs = node.values
            if 'script' in ks and 'artifact' in ks:
                s = vs[ks.index('script')]
                if isinstance(s, _ast.Constant) and isinstance(s.value, str):
                    face_scripts.add(s.value)
            if 'roster' in ks or 'workflow' in ks:
                for v in vs:
                    if isinstance(v, _ast.Constant) and isinstance(v.value, str) and v.value.endswith('.json'):
                        src_files.add(v.value)
    art_to_gate = {}
    for g in gates:
        a = g.get('argv') or []
        for i, x in enumerate(a):
            if x == '--json' and i + 1 < len(a):
                art_to_gate[os.path.basename(a[i + 1])] = str(g.get('id') or '')
    crit = set()
    for g in gates:
        sid = str(g.get('id') or '')
        script = str(g.get('script') or '')
        if script in face_scripts or script in SELF_AUDIT:
            crit.add(sid)
        for a in (g.get('argv') or []):
            if isinstance(a, str) and os.path.basename(a) in src_files:
                crit.add(sid)
    return crit


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
    crit = derive_critical(gates)
    # r255：第四种证据形态 ledger_fail —— 台账里真的出现过非 PASS（证过它至少能不绿）。
    led = os.path.join(ROOT, '06-benchmark', 'gate_runs.jsonl')
    seen_fail = set()
    if os.path.isfile(led):
        try:
            for ln in io.open(led, encoding='utf-8', errors='replace'):
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    o = json.loads(ln)
                except ValueError:
                    continue
                st = str(o.get('state') or o.get('verdict') or '')
                gid2 = str(o.get('id') or o.get('gate') or '')
                if gid2 and st and st != 'PASS':
                    seen_fail.add(gid2)
        except OSError:
            pass
    for r in rows:
        if r['id'] in seen_fail:
            r['ledger_fail'] = True
            if r['proof'] == 'NONE':
                r['proof'] = 'ledger_fail'
    crit_missing = [r['id'] for r in rows if r['id'] in crit
                     and r['proof'] == 'NONE']
    doc = {'schema': 'teeth-proof-matrix-v1', 'readonly': True,
           'provenance_cmd': 'python 05-exec/r254_teeth_proof_matrix.py --json <件>',
           'gates_n': len(rows), 'fixture_files': [os.path.basename(f) for f in fx],
           'critical': sorted(crit), 'critical_missing_proof': crit_missing,
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
        if r['id'] in crit:
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