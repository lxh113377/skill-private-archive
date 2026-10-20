# -*- coding: utf-8 -*-
# r139_hook_sync.py -- 恢复源与实装件逐字节一致面（第 51 门，R138-4 落地）。
#
# 存在理由（r138 一手，r139 实测坐实）：r138 建了 hook 健在性自检（第 50 门）与脚本化恢复，
#   但收尾时留了条残留（R138-4）：`05-exec/hook_templates/*.sh`（恢复源）与 `.git/hooks/`（实装件）
#   是两份拷贝，**没有任何判据守着它们一致**。
#   r139 实测证明这个风险真实：往 `.git/hooks/pre-commit` 追加一行（模拟「装 hook 都是直接改那里」的
#   真实习惯）⇒ 第 50 门仍报 `8/8 通过`，而模板与实装 `match=False`。
#   ⇒ 会出现「自检绿但下次恢复装出旧版」—— 比 hook 丢失更隐蔽。
#
# 本件逐项断言：
#   S1 恢复源存在（pre-commit.sh / post-commit.sh）
#   S2 实装件存在
#   S3 两者逐字节一致（SHA256）
#   S4 恢复源在 git 内被跟踪（否则 clone 后无源可恢复）
#
# 反向验证（#32）：造「只改实装件」「模板被删」两个变体，确认判据能报出来。
#
# 用法: python 05-exec/r139_hook_sync.py [--json 06-benchmark/hook_sync_r139_2026-10-21.json]
# 退出码: 0 全项通过 / 1 有项不通过 / 2 输入面不可用
import argparse
import hashlib
import io
import json
import os
import subprocess
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TPL = os.path.join(HERE, 'hook_templates')
HOOKS = os.path.join(ROOT, '.git', 'hooks')
PAIRS = [('pre-commit.sh', 'pre-commit'), ('post-commit.sh', 'post-commit')]


def sha(p):
    h = hashlib.sha256()
    try:
        with io.open(p, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ''


def git_tracked(rel):
    try:
        p = subprocess.run(['git', 'ls-files', '--error-unmatch', rel],
                           cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                           errors='replace', timeout=120)
        return p.returncode == 0
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    args = ap.parse_args()
    if not os.path.isdir(TPL):
        print('[HOOKSYNC] UNVERIFIED 恢复源目录不存在: %s' % TPL)
        return 2
    rows = []
    for tpl, name in PAIRS:
        tp = os.path.join(TPL, tpl)
        hp = os.path.join(HOOKS, name)
        trel = os.path.join('05-exec', 'hook_templates', tpl)
        s1 = os.path.isfile(tp)
        s2 = os.path.isfile(hp)
        s3 = False
        th = hh = ''
        if s1 and s2:
            th = sha(tp)
            hh = sha(hp)
            s3 = (th == hh)
        s4 = git_tracked(trel) if s1 else False
        rows.append({'hook': name, 'template': tpl,
                     's1_source_exists': s1, 's2_installed_exists': s2,
                     's3_byte_identical': s3, 's4_source_git_tracked': s4,
                     'template_sha': th[:16], 'installed_sha': hh[:16]})
    bad = []
    for r in rows:
        for k in ('s1_source_exists', 's2_installed_exists', 's3_byte_identical', 's4_source_git_tracked'):
            if not r[k]:
                bad.append({'hook': r['hook'], 'check': k})
    doc = {'schema': 'hook-sync-r139-v1',
           'cmd': 'python 05-exec/r139_hook_sync.py --json <out>',
           'face': {'pairs_n': len(rows),
                     'bad_n': len(bad),
                     'reading': {
                         'bad_n': ('不通过的断言数。任一不通 = 恢复源与实装件已漂移（或源丢失）',
                                   '=> 下次一键恢复会装出旧版，属于「自检绿但恢复错」类隐患'),
                         's3_byte_identical': '模板与实装件 SHA256 逐字节相同',
                         's4_source_git_tracked': '恢复源在 git 内被跟踪（否则 clone 后无源可恢复）',
                     }},
           'rows': rows,
           'bad': bad,
           'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline=chr(10)) as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    fa = doc['face']
    print('[HOOKSYNC] %d 对 hook｜不通过断言 %d' % (fa['pairs_n'], fa['bad_n']))
    for r in rows:
        print('  %-12s S1=%s S2=%s S3(byte-identical)=%s S4(git-tracked)=%s'
              % (r['hook'], r['s1_source_exists'], r['s2_installed_exists'],
                 r['s3_byte_identical'], r['s4_source_git_tracked']))
    for b in bad:
        print('  FAIL %s / %s' % (b['hook'], b['check']))
    if args.out:
        print('[HOOKSYNC] JSON -> %s' % args.out)
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())