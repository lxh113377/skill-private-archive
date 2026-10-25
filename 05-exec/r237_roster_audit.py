# -*- coding: utf-8 -*-
'''r237_roster_audit.py - 名册四层独立复算审计（r237 新建，只读）。

为什么需要它：r215-r236 逐轮把名册做成四层可复算产物，但**每一层都是它自己那道门算的** ——
  名册只是把门的产物拼起来。谁也没验过「门算得对不对」。本件**不复用任何门内函数**：
  自己走盘、自己计数（只借 r163 的正则源 = 权威定义），把四层逐工具与名册对账。

  r237 首跑结果：10 个工具四层全对（漂移 0）。唯一「不一致」是 Pages-Functions —— 它在第 67 门尺里、
  但不在免费工具名册的 10 行里（TOOLS 11 键 vs 名册 10 行，两边分母不同的已知口径差，见台账 R216-2），
  故本件把「不在名册的工具」单列为 known_not_in_roster，不计入漂移。

判据（三态）：漂移 0 ⇒ PASS(0)；有漂移 ⇒ FAIL(1) 并逐工具印「复算值 != 名册值」；
  源件缺 / 面为空 ⇒ UNVERIFIED(2)（R247 禁按 0 记绿）。
用法: python 05-exec/r237_roster_audit.py [--json <件>]
'''
import argparse
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
B = os.path.join(ROOT, '06-benchmark')
sys.path.insert(0, HERE)
from r163_tool_skill_matrix import TOOLS  # 只借正则源（权威定义）

GS = 'D:/global_skills'
CODE_EXT = ('.py', '.sh', '.ps1', '.mjs', '.js', '.ts', '.sql')
WEXTS = ('.py', '.sh', '.ps1', '.yml', '.yaml', '.js', '.ts', '.sql', '.toml')
EXCL = ('r163_tool_skill_matrix.py', 'r214_tool_carrier_face.py',
        'tool_carrier_patterns.json', 'r218_workflow_usage_face.py', 'r215_free_tool_roster.py')
PROBE = ('_face', '_fixtures', 'probe', 'matrix', 'check', 'stage', 'debt', 'gate')
FMARKS = ('.git', 'SKILL.md')
SKIP = ('node_modules', '.git', 'dist', '.wrangler', 'archive', '__pycache__')


def layer1():
    '''skill 目录：提到件数 / 代码级件数（自走盘）'''
    men, exe = {}, {}
    for slug in sorted(os.listdir(GS)):
        sd = os.path.join(GS, slug)
        if not os.path.isfile(os.path.join(sd, 'SKILL.md')):
            continue
        try:
            blob = [io.open(os.path.join(sd, 'SKILL.md'), encoding='utf-8', errors='replace').read()]
        except OSError:
            continue
        code = []
        for sub in ('references', 'scripts'):
            d = os.path.join(sd, sub)
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d))[:25]:
                fp = os.path.join(d, fn)
                if not os.path.isfile(fp) or os.path.getsize(fp) >= 200000:
                    continue
                try:
                    txt = io.open(fp, encoding='utf-8', errors='replace').read()
                except OSError:
                    continue
                blob.append(txt)
                if fn.endswith(CODE_EXT):
                    code.append(txt)
        b = chr(10).join(blob)
        c = chr(10).join(code)
        for tool, pat in TOOLS.items():
            if re.search(pat, b, re.I):
                men.setdefault(tool, set()).add(slug)
            if c and re.search(pat, c, re.I):
                exe.setdefault(tool, set()).add(slug)
    return men, exe


def layer2():
    '''工作流面：排除探针件与写模式的件，逐工具真调用计数（自走盘）'''
    files = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in ('.git', '__pycache__', '_trash', '_bak',
                                             'node_modules', '_temp', '06-benchmark',
                                             '07-archive', '.venv')]
        for f in fns:
            if not f.endswith(WEXTS):
                continue
            fp = os.path.join(dp, f)
            if os.path.basename(fp) in EXCL:
                continue
            if ((os.sep + 'hooks' + os.sep) in fp or '05-exec' in fp
                    or (os.sep + '.github') in fp):
                files.append(fp)
    res = {}
    for tool, pat in TOOLS.items():
        n = 0
        for fp in files:
            if any(h in os.path.basename(fp).lower() for h in PROBE):
                continue
            try:
                t = io.open(fp, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            n += len(re.findall(pat, t, re.I))
        res[tool] = n
    return res, len(files)


def layer3():
    '''项目仓：剪掉嵌套 .git / 同目录 SKILL.md 的外来面，逐工具计数（自走盘）'''
    cand = sorted(glob.glob(os.path.join(B, 'tool_skill_matrix_r*.json')),
                  key=os.path.getmtime)
    mx = None
    for fp in reversed(cand):
        try:
            d = json.load(io.open(fp, encoding='utf-8'))
        except (OSError, ValueError):
            continue
        if d.get('third_face'):
            mx = d
            break
    if mx is None:
        return None, None
    roots = (mx.get('third_face') or {}).get('roots') or []
    res = {}
    for root in roots:
        for dp, dns, fns in os.walk(root):
            keep = []
            for d in dns:
                if d in SKIP:
                    continue
                sub = os.path.join(dp, d)
                if any(os.path.exists(os.path.join(sub, mk)) for mk in FMARKS):
                    continue
                keep.append(d)
            dns[:] = keep
            for f in fns:
                if not f.endswith(CODE_EXT):
                    continue
                fp = os.path.join(dp, f)
                try:
                    if os.path.getsize(fp) > 200000:
                        continue
                    t = io.open(fp, encoding='utf-8', errors='replace').read()
                except OSError:
                    continue
                for tool, pat in TOOLS.items():
                    n = len(re.findall(pat, t, re.I))
                    if n:
                        res[tool] = res.get(tool, 0) + n
    return res, roots


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out', default='')
    args = ap.parse_args(argv)
    rf = os.path.join(B, 'free_tool_roster_latest.json')
    if not os.path.isfile(rf):
        print('[ROSTER-AUDIT:UNVERIFIED] 名册件缺失 ⇒ 无可对账面（R247）')
        return 2
    if not os.path.isdir(GS):
        print('[ROSTER-AUDIT:UNVERIFIED] global_skills 面取不到 ⇒ 层1 无分母（R247）')
        return 2
    ros = json.load(io.open(rf, encoding='utf-8'))
    rost = {it['tool']: it for it in (ros.get('items') or [])}
    if not rost:
        print('[ROSTER-AUDIT:UNVERIFIED] 名册 items 为空 ⇒ 空面不得判对')
        return 2
    men, exe = layer1()
    wf, wface = layer2()
    th, roots = layer3()
    if th is None:
        print('[ROSTER-AUDIT:UNVERIFIED] 取不到含 third_face 的矩阵件 ⇒ 层3 无分母（R247）')
        return 2
    drift = []
    known = []
    for tool in sorted(TOOLS):
        if tool not in rost:
            known.append(tool)
            continue
        it = rost[tool]
        pairs = (
            ('层1提到', len(men.get(tool) or []), len(it.get('mention_skills') or [])),
            ('层1代码', len(exe.get(tool) or []), len(it.get('exec_skills') or [])),
            ('层2', wf.get(tool, 0), it.get('wf_real_hits') or 0),
            ('层3', th.get(tool, 0), it.get('third_hits') or 0),
        )
        bad = ['%s %s!=%s' % (k, a, b) for k, a, b in pairs if a != b]
        if bad:
            drift.append('%s: %s' % (tool, ' / '.join(bad)))
    doc = {'schema': 'roster-audit-v1', 'readonly': True,
           'provenance_cmd': 'python 05-exec/r237_roster_audit.py --json <件>',
           'roster_tools': len(rost), 'tools_in_matrix_only': known,
           'workflow_face_files': wface, 'third_roots': roots,
           'drift': drift,
           'per_tool': {t: {'l1_mention': len(men.get(t) or []),
                            'l1_exec': len(exe.get(t) or []),
                            'l2': wf.get(t, 0), 'l3': th.get(t, 0)} for t in sorted(rost)}}
    if args.out:
        op = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
        io.open(op, 'w', encoding='utf-8', newline=chr(10)).write(
            json.dumps(doc, ensure_ascii=False, indent=1))
    print('[ROSTER-AUDIT] 名册 %d 工具 / 工作流面 %d 件 / 项目仓 %d 个' % (
        len(rost), wface, len(roots or [])))
    for t in known:
        print('  [已在第 67 门尺内、不在名册] %s（已知分母差，见台账 R216-2，不计漂移）' % t)
    for d in drift:
        print('  漂移: ' + d)
    if drift:
        print('[ROSTER-AUDIT:FAIL] 独立复算与名册不一致 %d 项' % len(drift))
        return 1
    print('[ROSTER-AUDIT:PASS] 四层逐工具独立复算与名册一致（漂移 0；只借正则源，其余全自走盘）')
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())