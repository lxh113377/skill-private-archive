# -*- coding: utf-8 -*-
# r138_hook_health.py -- 阻断机制健在性自检面（第 50 门，R137-4 落地）。
#
# 存在理由（r137 一手）：r137 装了分级阻断的 pre-commit，但收尾时发现一个残留 ——
#   `.git/hooks/` **不在 git 里**（tracked hooks = 0）⇒ 换机 / 重装 / clone 即全丢，
#   而本仓此前没有任何判据回答「hook 还在吗、还完整吗」。
#   r130 与 r137 两次装 hook，装完都没再核过。
#
# 本件逐项断言（缺一即判红，禁按 0 记绿）：
#   H1 pre-commit 存在且非空
#   H2 pre-commit 含 exit 1（有阻断能力 —— 否则等于没装，r136 盘点的病）
#   H3 pre-commit 含分级判定的入口（r137_commit_gate_map.py）
#   H4 pre-commit 含逃生阀 SKIP_COMMIT_GATES
#   H5 pre-commit 用 --no-ledger 试跑（不污染门禁台账）
#   H6 post-commit 存在（自动推送链）
#   H7 判定面脚本存在（r137_commit_gate_map.py）
#   H8 判定面可跑（跑一次，rc ∈ {0,2} 都算可跑；UNVERIFIED=2 是设计内的合法态）
#
# 反向验证（#32）：造「hook 被删」「exit 1 被抹掉」两个变体，确认判据能报出来。
#
# 用法: python 05-exec/r138_hook_health.py [--json 06-benchmark/hook_health_r138_2026-10-21.json]
# 退出码: 0 全项通过 / 1 有项不通过 / 2 输入面不可用
import argparse
import io
import json
import os
import subprocess
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOOKS = os.path.join(ROOT, '.git', 'hooks')
PRE = os.path.join(HOOKS, 'pre-commit')
POST = os.path.join(HOOKS, 'post-commit')
MAP = os.path.join(HERE, 'r137_commit_gate_map.py')

CHECKS = [
    ('H1 pre-commit 存在且非空', 'pre_exists'),
    ('H2 pre-commit 含 exit 1（有阻断能力）', 'pre_exit1'),
    ('H3 pre-commit 含分级判定入口', 'pre_map'),
    ('H4 pre-commit 含逃生阀 SKIP_COMMIT_GATES', 'pre_skip'),
    ('H5 pre-commit 用 --no-ledger 试跑', 'pre_noledger'),
    ('H6 post-commit 存在（自动推送链）', 'post_exists'),
    ('H7 判定面脚本存在', 'map_exists'),
    ('H8 判定面可跑', 'map_runnable'),
]


def read(p):
    try:
        return io.open(p, encoding='utf-8', errors='replace').read()
    except Exception:
        return ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    ap.add_argument('--hooks-dir', default=HOOKS)
    args = ap.parse_args()
    hd = args.hooks_dir
    pre = os.path.join(hd, 'pre-commit')
    post = os.path.join(hd, 'post-commit')
    presrc = read(pre)
    r = {}
    r['pre_exists'] = bool(presrc.strip())
    r['pre_exit1'] = 'exit 1' in presrc
    r['pre_map'] = 'r137_commit_gate_map' in presrc
    r['pre_skip'] = 'SKIP_COMMIT_GATES' in presrc
    r['pre_noledger'] = 'no-ledger' in presrc
    r['post_exists'] = os.path.isfile(post)
    r['map_exists'] = os.path.isfile(MAP)
    r['map_runnable'] = False
    if r['map_exists']:
        try:
            p = subprocess.run(['python', MAP, '--json', os.path.join(ROOT, '_temp', 'hook_health_map.json')],
                               cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                               errors='replace', timeout=300)
            # rc ∈ {0, 2} 都算「可跑」：0 = 判定完成；2 = 输入面不可用（设计内的合法态）
            r['map_runnable'] = p.returncode in (0, 2)
        except Exception:
            r['map_runnable'] = False
    rows = [{'id': k, 'name': n, 'ok': bool(r.get(k))} for n, k in CHECKS]
    bad = [x for x in rows if not x['ok']]
    doc = {'schema': 'hook-health-r138-v1',
           'cmd': 'python 05-exec/r138_hook_health.py --json <out>',
           'face': {'checks_n': len(rows),
                     'ok_n': len(rows) - len(bad),
                     'bad_n': len(bad),
                     'hooks_tracked_in_git': 0,
                     'reading': {
                         'bad_n': '不通过项数。任一不通 = 阻断机制缺一件，判红。',
                         'hooks_tracked_in_git': '恒 0（.git/hooks 不在 git 内）—— 这是本门存在的理由：hook 健在性必须被自检，因为它不可被 git 恢复。',
                     }},
           'rows': rows,
           'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    fa = doc['face']
    print('[HOOKHEALTH] %d/%d 通过｜不通过 %d' % (fa['ok_n'], fa['checks_n'], fa['bad_n']))
    for x in rows:
        print('  %-4s %s' % ('PASS' if x['ok'] else 'FAIL', x['name']))
    if args.out:
        print('[HOOKHEALTH] JSON -> %s' % args.out)
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())