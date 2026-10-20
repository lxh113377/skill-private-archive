# -*- coding: utf-8 -*-
# r141_hook_attribution.py -- 归因到人与次面（第 53 门，R140-4 落地）。
#
# 存在理由（r140 一手，r141 落地）：r140 的印记只记模板 sha + 安装时间，
#   多会话/多人装 hook 时无法归因到「哪次安装、谁装的」—— R140-4 留了这个缺口。
#   r141 给印记加 invoker（git_user / git_email / session / pid）与 reason 两字段，
#   本件独立断言这两字段齐备（与 r140_hook_trace 的六态归因分工：
#   r140 答「哪次安装/怎么漂移的」，本件答「谁、为什么装」）。
#
# 断言（缺一即判红）：
#   A1 印记存在
#   A2 印记含 invoker 且含 git_user
#   A3 印记含 invoker 且含 session（会话标识 —— 多会话归因的关键）
#   A4 印记含 reason 且非空（安装原因；缺省「(未说明)」也算有，但会告警）
#
# 反向验证（#32）：造「无 invoker 的旧印记」「完全无印记」「正常印记」三个变体。
#
# 用法: python 05-exec/r141_hook_attribution.py [--json 06-benchmark/hook_attribution_r141_2026-10-21.json]
# 退出码: 0 全项通过 / 1 有项不通过 / 2 输入面不可用
import argparse
import io
import json
import os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOOKS = os.path.join(ROOT, '.git', 'hooks')
PAIRS = [('pre-commit',), ('post-commit',)]


def read_stamp(p):
    try:
        with io.open(p, encoding='utf-8-sig') as f:
            return json.load(f) or {}
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    args = ap.parse_args()
    if not os.path.isdir(HOOKS):
        print('[ATTR] UNVERIFIED hooks 目录不存在: %s' % HOOKS)
        return 2
    rows = []
    for (name,) in PAIRS:
        sp = os.path.join(HOOKS, name + '.installed')
        stamp = read_stamp(sp) if os.path.isfile(sp) else {}
        inv = stamp.get('invoker') or {}
        reason = stamp.get('reason') or ''
        a1 = bool(stamp)
        a2 = bool(inv.get('git_user'))
        a3 = bool(inv.get('session'))
        a4 = bool(reason)
        vague = (reason == '(未说明)')
        rows.append({'hook': name,
                     'a1_stamp_exists': a1,
                     'a2_has_git_user': a2,
                     'a3_has_session': a3,
                     'a4_has_reason': a4,
                     'reason_vague': vague,
                     'invoker_desc': ('%s@%s' % (inv.get('git_user') or '?',
                                                (inv.get('git_email') or '?').split('@')[0])
                                      if inv else '(无 invoker)'),
                     'session': inv.get('session') or '',
                     'reason': reason})
    bad = []
    for r in rows:
        for k in ('a1_stamp_exists', 'a2_has_git_user', 'a3_has_session', 'a4_has_reason'):
            if not r[k]:
                bad.append({'hook': r['hook'], 'check': k})
    vague = [r['hook'] for r in rows if r['reason_vague']]
    doc = {'schema': 'hook-attribution-r141-v1',
           'cmd': 'python 05-exec/r141_hook_attribution.py --json <out>',
           'face': {'pairs_n': len(rows),
                     'bad_n': len(bad),
                     'reason_vague_n': len(vague),
                     'reading': {
                         'bad_n': ('不通过的断言数。任一不通 = 归因链缺一环，判红。',
                                   'A1 印记存在 / A2 有 git_user / A3 有 session / A4 有 reason'),
                         'reason_vague_n': 'reason 为「(未说明)」的 hook 数 —— 不判红（字段在），但建议补安装原因',
                         'session': '会话标识是多会话归因的关键：同一个人在不同会话装 hook，靠它区分',
                     }},
           'rows': rows,
           'bad': bad,
           'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline=chr(10)) as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    fa = doc['face']
    print('[ATTR] %d 对 hook｜不通过 %d｜reason 含糊 %d'
          % (fa['pairs_n'], fa['bad_n'], fa['reason_vague_n']))
    for r in rows:
        print('  %-12s A1=%s A2=%s A3=%s A4=%s | %s | reason=%s'
              % (r['hook'], r['a1_stamp_exists'], r['a2_has_git_user'],
                 r['a3_has_session'], r['a4_has_reason'],
                 r['invoker_desc'], r['reason'][:34]))
    for b in bad:
        print('  FAIL %s / %s' % (b['hook'], b['check']))
    if args.out:
        print('[ATTR] JSON -> %s' % args.out)
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())