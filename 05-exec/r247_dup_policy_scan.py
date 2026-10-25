# -*- coding: utf-8 -*-
"""r247_dup_policy_scan.py - 共用策略不得有两份（r247 新建，只读 AST 扫描）。

存在理由（r247 一手，把 r242 的教训机械化）：r242 抓到一次真事故 —— 排除名单 EXCL 在 r218 与 r237
  各写了一份，我改了其中一份、另一份没跟 ⇒ 审计把自己算进 Turnstile 命中（28!=25），表现为**假漂移**，
  两边互相指责。当时结论是「策略单一来源、算法独立」，但那条结论只写在注释与报告里，**没人机械地查**。

本件把它变成判据：

  单源类（SINGLE_SOURCE）：这些名字是「谁算工作流面 / 名册口径」这种契约 —— 全仓**只能有 1 件**定义它。
  同值类（SAME_VALUE）：允许多件（各脚本自己的常量），但**值必须一致**。
  不在名单内：EXTS / SKIP / ROOTS —— 它们服务不同面，强行统一反而失真（用途不同 ≠ 策略双份）。

判据三态：全满足 ⇒ PASS(0)；单源名出现在 ≥2 件、或同值名取值不一 ⇒ FAIL(1) 逐名具名；
  扫不到任何目标常量（面变了/路径错）⇒ UNVERIFIED(2)（R247：空面不得判绿）。
用法: python 05-exec/r247_dup_policy_scan.py [--json <件>]
"""
import argparse
import ast
import collections
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
E = HERE

SINGLE_SOURCE = ('EXCL', 'PROBE_HINT', 'MEASURE_HINT', 'CALL_CTX',
                 'READ_FACE', 'NO_READ_FACE', 'READ_STATES', 'BLOCKER', 'BLOCKER_CLASSES',
                 'TOOLS', 'LEGIT_DUP', 'INPUT_HINTS')
SAME_VALUE = ('CODE_EXT', 'DB')


def scan():
    defs = collections.defaultdict(list)
    files = 0
    for f in sorted(os.listdir(E)):
        if not f.endswith('.py'):
            continue
        fp = os.path.join(E, f)
        try:
            tree = ast.parse(io.open(fp, encoding='utf-8', errors='replace').read())
        except SyntaxError:
            continue
        files += 1
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            for tg in node.targets:
                if not isinstance(tg, ast.Name):
                    continue
                if tg.id not in SINGLE_SOURCE and tg.id not in SAME_VALUE:
                    continue
                try:
                    val = ast.literal_eval(node.value)
                except Exception:
                    val = '<non-literal>'
                defs[tg.id].append((f, val))
    return defs, files


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out', default='')
    args = ap.parse_args(argv)
    defs, files = scan()
    if not defs:
        print('[DUPPOL:UNVERIFIED] 扫不到任何目标常量（面变了或路径错）⇒ 空面不得判绿')
        return 2
    bad = []
    detail = {}
    for name in SINGLE_SOURCE:
        got = defs.get(name) or []
        detail[name] = [f for f, _ in got]
        if len(got) > 1:
            bad.append('%s 单源名出现在 %d 件：%s' % (name, len(got), [f for f, _ in got]))
    for name in SAME_VALUE:
        got = defs.get(name) or []
        detail[name] = [f for f, _ in got]
        vals = {repr(v) for _f, v in got}
        if len(got) > 1 and len(vals) > 1:
            bad.append('%s 多件但取值不一：%s' % (name, [(f, repr(v)[:60]) for f, v in got]))
    doc = {'schema': 'dup-policy-scan-v1', 'readonly': True,
           'provenance_cmd': 'python 05-exec/r247_dup_policy_scan.py --json <件>',
           'files_parsed': files,
           'single_source': {k: detail.get(k) for k in SINGLE_SOURCE},
           'same_value': {k: detail.get(k) for k in SAME_VALUE},
           'note': 'EXTS/SKIP/ROOTS 不在名单：它们服务不同面，强行统一反而失真。',
           'violations': bad}
    if args.out:
        op = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
        io.open(op, 'w', encoding='utf-8', newline=chr(10)).write(
            json.dumps(doc, ensure_ascii=False, indent=1))
    print('[DUPPOL] 解析 %d 件 ｜ 单源名 %d 个 / 同值名 %d 个' % (
        files, len(SINGLE_SOURCE), len(SAME_VALUE)))
    for b in bad:
        print('  违规: ' + b)
    if bad:
        print('[DUPPOL:FAIL] 共用策略被写了两份 %d 处（两份不同步时会表现为假漂移，r242 一手）' % len(bad))
        return 1
    print('[DUPPOL:PASS] 共用策略均为单源或同值（EXTS/SKIP/ROOTS 按用途不同豁免）')
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())