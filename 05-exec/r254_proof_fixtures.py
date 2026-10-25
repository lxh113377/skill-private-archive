# -*- coding: utf-8 -*-
"""r254_proof_fixtures.py - 四道关键门的「能红」证明（r254 新建）。

存在理由（r254 一手）：r254 的逐门证伪矩阵（r254_teeth_proof_matrix.py）实测关键集里四道门 proof=NONE ——
  roster_audit / dup_policy_scan / source_freshness_scan / judge_binding_scan。它们的验证当初都做过
  （变异注入、已知坏版本回溯），但**只活在某一轮对话里**，没有落成仓内可复跑的证明 ⇒ 矩阵判它们
  「没人证伪过」。本件用**进程内 monkeypatch 强制制造该红的情形**，把证明落盘：

  p1 roster_audit        ：把 layer1/2/3/5 换成空面 ⇒ 与名册必然漂移 ⇒ 必须 rc=1 且具名漂移
  p2 dup_policy_scan     ：把 scan() 换成「同一个单源名出现在 2 件」⇒ 必须 rc=1 且具名违规
  p3 source_freshness_scan：把源表换成含一个无门产出件 ⇒ 必须 rc=1 且具名孤儿
  p4 judge_binding_scan  ：喂一个含「吞异常 try 内引用未绑定名」的临时件 ⇒ 必须 rc=1 且具名该名与 SILENT

为什么用进程内而不是改盘上件：r251/r252 两次实测，改盘上件会被并发门跑覆盖或被吞异常掩掉。
判据：四条都 rc≠0 且带预期关键字 ⇒ [GATE:prooffix-pass] rc=0；任一不红 ⇒ [GATE:prooffix-fail] rc=1。
"""
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

OK = []
BAD = []


def ck(name, cond, detail=''):
    (OK if cond else BAD).append(name)
    print('  %-52s %s %s' % (name, 'PASS' if cond else 'FAIL', str(detail)[:90]))


def call_main(mod, argv=None):
    '''调用模块 main()，捕获 stdout，返回 (rc, 文本)。'''
    buf = []
    old = sys.stdout

    class _Cap:
        def write(self, s):
            buf.append(s)
        def flush(self):
            pass
        def reconfigure(self, **kw):
            pass
    sys.stdout = _Cap()
    try:
        rc = mod.main(argv if argv is not None else [])
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else 1
    except Exception as e:
        rc = 99
        buf.append('__CRASH__ ' + repr(e))
    finally:
        sys.stdout = old
    return rc, ''.join(buf)


def p1_roster_audit():
    import r237_roster_audit as M
    M.layer1 = lambda: ({}, {})
    M.layer2 = lambda: ({}, 0)
    M.layer3 = lambda: ({}, [])
    M.layer5 = lambda: {}
    rc, out = call_main(M, [])
    ck('p1 roster_audit 空复算 ⇒ 必须判漂移 rc≠0', rc != 0 and 'ROSTER-AUDIT:FAIL' in out,
       'rc=%d' % rc)


def p2_dup_policy():
    import r247_dup_policy_scan as M
    M.scan = lambda: ({'EXCL': [('a.py', ('x',)), ('b.py', ('x',))]}, 2)
    rc, out = call_main(M, [])
    ck('p2 dup_policy_scan 单源名两件 ⇒ 必须 rc≠0 且具名 EXCL',
       rc != 0 and 'DUPPOL:FAIL' in out and 'EXCL' in out, 'rc=%d' % rc)


def p3_freshness():
    import r250_source_freshness_scan as M
    M.gate_outputs = lambda: {'known.json': 'some_gate'}
    M.roster_sources = lambda: [('use', 'orphan_missing.json')]
    rc, out = call_main(M, [])
    ck('p3 source_freshness_scan 孤儿源 ⇒ 必须 rc≠0 且具名该件',
       rc != 0 and 'SRCFRESH:FAIL' in out and 'orphan_missing.json' in out, 'rc=%d' % rc)


def p4_judge_binding():
    import r253_judge_binding_scan as M
    d = tempfile.mkdtemp(prefix='proof254_')
    fp = os.path.join(d, 'bad_case.py')
    io.open(fp, 'w', encoding='utf-8', newline=chr(10)).write(
        'def f():' + chr(10) +
        '    try:' + chr(10) +
        '        v = never_bound_xyz[1]' + chr(10) +
        '    except Exception:' + chr(10) +
        '        v = set()' + chr(10) +
        '    return v' + chr(10))
    old_default = list(M.DEFAULT)
    M.DEFAULT = [fp]
    rc, out = call_main(M, [])
    M.DEFAULT = old_default
    ok = rc != 0 and 'JUDGEBIND:FAIL' in out and 'never_bound_xyz' in out and 'SILENT' in out
    ck('p4 judge_binding_scan 吞异常+未绑定 ⇒ 必须 rc≠0 且具名 SILENT', ok, 'rc=%d' % rc)


def p5_recall_face():
    # r255 观察（已落待办 R255-2，属他人件不代改）：源件读不到时该面**崩溃**（TypeError）而非报 UNVERIFIED。
    #   本腿只断言「能不绿」（rc≠0），并把形态记进 detail，供下轮追。
    import r208_recall_face as M
    M._read = lambda *a, **k: None
    rc, out = call_main(M, [])
    shape = 'CRASH' if '__CRASH__' in out else 'rc=%d' % rc
    ck('p5 recall_face 源件读不到 ⇒ 必须 rc≠0（形态：%s）' % shape, rc != 0, shape)


def p6_ingress_face():
    # r255 同 p5：崩溃形态，已落待办 R255-2。
    import r213_ingress_face as M
    M._read = lambda *a, **k: None
    rc, out = call_main(M, [])
    shape = 'CRASH' if '__CRASH__' in out else 'rc=%d' % rc
    ck('p6 ingress_face 源件读不到 ⇒ 必须 rc≠0（形态：%s）' % shape, rc != 0, shape)


def p7_tool_carrier_face():
    import r214_tool_carrier_face as M
    M._read = lambda *a, **k: None
    rc, out = call_main(M, [])
    ck('p7 tool_carrier_face 源件读不到 ⇒ 必须 rc≠0', rc != 0, 'rc=%d' % rc)


def p8_sqlite_usage_face():
    import r243_sqlite_usage_face as M
    old = M.DB
    M.DB = os.path.join(M.ROOT, '_temp', 'proof254_no_such.sqlite')   # 必须同盘（原给 C: 路径触发 relpath ValueError，是我这条腿的 bug）
    try:
        rc, out = call_main(M, [])
    finally:
        M.DB = old
    ck('p8 sqlite_usage_face 库不存在 ⇒ 必须 rc≠0 且 UNVERIFIED',
       rc != 0 and 'UNVERIFIED' in out, 'rc=%d' % rc)


def p9_gh_billing_face():
    import r241_gh_billing_face as M
    M.gh_api = lambda *a, **k: (1, 'poisoned_by_proof254')
    rc, out = call_main(M, [])
    ck('p9 gh_billing_face 端点不可达 ⇒ 必须 rc≠0 且 UNVERIFIED',
       rc != 0 and 'UNVERIFIED' in out, 'rc=%d' % rc)


def p10_turnstile_usage_face():
    import r242_turnstile_usage_face as M
    import r199_workers_face as W
    old = W.oauth_token
    W.oauth_token = lambda *a, **k: (None, 'poisoned_by_proof254')
    try:
        rc, out = call_main(M, [])
    finally:
        W.oauth_token = old
    ck('p10 turnstile_usage_face 凭据取不到 ⇒ 必须 rc≠0 且 UNVERIFIED',
       rc != 0 and 'UNVERIFIED' in out, 'rc=%d' % rc)


def p11_route_truth_measure():
    # r255 自抓：首版 patch route 无效（那条路在 main 里另有前置判定）⇒ 改打「探针名册缺失」这条 UNVERIFIED 路。
    import r209_route_truth_measure as M
    old = M.PROBES
    M.PROBES = os.path.join(M.ROOT, '06-benchmark', '__no_such_probes__.json')
    try:
        rc, out = call_main(M, [])
    finally:
        M.PROBES = old
    ck('p11 route_truth_measure 探针名册缺失 ⇒ 必须 rc≠0 且 UNVERIFIED',
       rc != 0 and 'UNVERIFIED' in out, 'rc=%d' % rc)


def p12_judge_binding_criterion_c():
    # r256：判据 C（吞成空结论）也要能被证伪 —— 造一个含 `except: gaps = set()` 的临时件。
    import r253_judge_binding_scan as M
    d = tempfile.mkdtemp(prefix='proof256_')
    fp = os.path.join(d, 'empty_conclusion.py')
    io.open(fp, 'w', encoding='utf-8', newline=chr(10)).write(
        'def f():' + chr(10) +
        '    try:' + chr(10) +
        '        x = load()' + chr(10) +
        '    except Exception:' + chr(10) +
        '        gaps = set()' + chr(10) +
        '    return gaps' + chr(10))
    old = list(M.DEFAULT)
    M.DEFAULT = [fp]
    rc, out = call_main(M, [])
    M.DEFAULT = old
    ck('p12 judge_binding_scan 判据C 吞成空结论 ⇒ 必须 rc≠0 且具名 gaps',
       rc != 0 and '判据C' in out and 'gaps' in out, 'rc=%d' % rc)


def main():
    for fn in (p1_roster_audit, p2_dup_policy, p3_freshness, p4_judge_binding,
               p5_recall_face, p6_ingress_face, p7_tool_carrier_face, p8_sqlite_usage_face,
               p9_gh_billing_face, p10_turnstile_usage_face, p11_route_truth_measure,
               p12_judge_binding_criterion_c):
        try:
            fn()
        except Exception as e:
            ck(fn.__name__ + ' 可执行', False, repr(e))
    n = len(OK) + len(BAD)
    print('证明夹具合计: %d 项，通过 %d，失败 %d' % (n, len(OK), len(BAD)))
    if BAD:
        print('[GATE:prooffix-fail]')
        return 1
    print('[GATE:prooffix-pass]')
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())