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


def main():
    for fn in (p1_roster_audit, p2_dup_policy, p3_freshness, p4_judge_binding):
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