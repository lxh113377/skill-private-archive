# -*- coding: utf-8 -*-
# r138_install_hooks.py -- 把 git hooks 从「手工写、易丢失」变成「一条命令重装且自证」。
#
# 存在理由（r137 一手）：r137 装了分级阻断的 pre-commit，但收尾发现 .git/hooks/ 不在 git 里
#   （tracked hooks = 0）=> 换机 / clone / 重装即全丢，而当时没有任何判据能发现这件事。
#   r130 与 r137 两次装 hook，装完都没再核过 —— 「阻断机制不可恢复」比「没有阻断机制」更危险，
#   因为它让人以为有。
#
# 本件做两件事：
#   1) 从 git 跟踪的模板（05-exec/hook_templates/*.sh）安装到 .git/hooks/；
#   2) 装完立刻自证（跑 r138_hook_health.py），不通则判红。
#
# 用法: python 05-exec/r138_install_hooks.py [--dry-run] [--json <件>]
# 退出码: 0 安装且自证通过 / 1 自证不通过 / 2 输入面不可用
import argparse
import io
import json
import os
import shutil
import stat
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TPL = os.path.join(HERE, 'hook_templates')
HOOKS = os.path.join(ROOT, '.git', 'hooks')
HEALTH = os.path.join(HERE, 'r138_hook_health.py')
TARGETS = [('pre-commit.sh', 'pre-commit'), ('post-commit.sh', 'post-commit')]


def install(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    try:
        mode = os.stat(dst).st_mode
        os.chmod(dst, mode | stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)
    except Exception:
        pass
    return os.path.getsize(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--json', dest='out')
    args = ap.parse_args()
    if not os.path.isdir(TPL):
        print('[INSTALL] UNVERIFIED 模板目录不存在: %s' % TPL)
        return 2
    if not os.path.isfile(HEALTH):
        print('[INSTALL] UNVERIFIED 自证工具不存在: %s' % os.path.basename(HEALTH))
        return 2
    rows = []
    for tpl, name in TARGETS:
        s = os.path.join(TPL, tpl)
        d = os.path.join(HOOKS, name)
        if not os.path.isfile(s):
            rows.append({'hook': name, 'template': tpl, 'installed': False,
                          'note': '模板缺失（跳过，非致命）'})
            continue
        if args.dry_run:
            rows.append({'hook': name, 'template': tpl, 'installed': False,
                          'note': 'dry-run', 'size': os.path.getsize(s)})
            continue
        try:
            sz = install(s, d)
            rows.append({'hook': name, 'template': tpl, 'installed': True, 'size': sz})
        except Exception as e:
            rows.append({'hook': name, 'template': tpl, 'installed': False,
                          'note': repr(e)})
    if args.dry_run:
        n = len([r for r in rows if r.get('note') == 'dry-run'])
        print('[INSTALL] dry-run：将安装 %d 个 hook（未实际写入）' % n)
        for r in rows:
            print('  WOULD-INSTALL %s <- %s (%s B)' % (r['hook'], r['template'], r.get('size', '?')))
        return 0
    rc = 2
    hout = ''
    try:
        p = subprocess.run([sys.executable, HEALTH], cwd=ROOT, capture_output=True,
                           text=True, encoding='utf-8', errors='replace', timeout=300)
        rc = p.returncode
        hout = (p.stdout or '') + (p.stderr or '')
    except Exception as e:
        hout = repr(e)
    line = ''
    for l in hout.splitlines():
        if l.startswith('[HOOKHEALTH]'):
            line = l.strip()
            break
    doc = {'schema': 'install-hooks-r138-v1',
           'cmd': 'python 05-exec/r138_install_hooks.py --json <out>',
           'face': {'installed_n': sum(1 for r in rows if r.get('installed')),
                     'rows_n': len(rows),
                     'self_check_rc': rc,
                     'self_check_line': line,
                     'reading': {
                         'self_check_rc': '装完立刻跑 hook 健在性自检的退出码；非 0 = 装好了但缺件，须判红',
                         'installed_n': '实际安装成功的 hook 数',
                     }},
           'rows': rows}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline=chr(10)) as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    fa = doc['face']
    print('[INSTALL] 安装 %d/%d | 自证 rc=%d | %s'
          % (fa['installed_n'], fa['rows_n'], fa['self_check_rc'], line or '(无读数)'))
    for r in rows:
        print('  %-12s %s %s' % (r['hook'], 'INSTALLED' if r.get('installed') else 'SKIPPED', r.get('note', '')))
    if args.out:
        print('[INSTALL] JSON -> %s' % args.out)
    return 0 if rc == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())