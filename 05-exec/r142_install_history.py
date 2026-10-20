# -*- coding: utf-8 -*-
# r142_install_history.py -- 安装历史可回溯面（第 54 门，R141-4 落地）。
#
# 存在理由（r141 一手，r142 量化坐实）：r141 的 .installed 是**快照**，每装一次就被覆盖，
#   只能归因到最近一次安装。r142 实测：装 2 次后，第 1 次的 reason 在整套 .git/hooks/ 里
#   搜不到 —— 历史彻底丢失。
#
# 解法 = 追加式历史：r138_install_hooks.py 除写快照外，还向 .installed.log 追加一行 JSONL。
# 本件断言这份历史可用：
#   H1 历史文件存在且非空
#   H2 每行都是合法 JSON 且含 seq / installed_at / invoker / reason
#   H3 seq 严格单调递增（无重号、无乱序）
#   H4 末行与快照一致（同一次安装写两处，不许只写一处）
#   H5 历史条数 >= 2（至少能看出「追加」真的在发生）
#
# 反向验证（#32）：造「只有快照无历史」「历史被清」「seq 乱序」三个变体。
#
# 用法: python 05-exec/r142_install_history.py [--json 06-benchmark/install_history_r142_2026-10-21.json]
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
REQ = ('seq', 'installed_at', 'invoker', 'reason')


def read_json(p):
    try:
        with io.open(p, encoding='utf-8-sig') as f:
            return json.load(f) or {}
    except Exception:
        return {}


def read_log(p):
    rows = []
    try:
        with io.open(p, encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f, 1):
                s = line.strip()
                if not s:
                    continue
                try:
                    rows.append((i, json.loads(s)))
                except Exception:
                    rows.append((i, None))
    except Exception:
        pass
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    args = ap.parse_args()
    if not os.path.isdir(HOOKS):
        print('[HIST] UNVERIFIED hooks 目录不存在: %s' % HOOKS)
        return 2
    rows = []
    for (name,) in PAIRS:
        logp = os.path.join(HOOKS, name + '.installed.log')
        snap = read_json(os.path.join(HOOKS, name + '.installed'))
        log = read_log(logp) if os.path.isfile(logp) else []
        h1 = bool(log)
        h2 = all(isinstance(o, dict) and all(o.get(k) for k in REQ)
                 for _, o in log) and bool(log)
        seqs = [o.get('seq') for _, o in log if isinstance(o, dict)]
        h3 = bool(seqs) and all(isinstance(s, int) for s in seqs) and all(
            seqs[i] < seqs[i + 1] for i in range(len(seqs) - 1))
        h4 = False
        if log and isinstance(log[-1][1], dict) and snap:
            last = log[-1][1]
            h4 = (last.get('installed_at') == snap.get('installed_at')
                  and last.get('template_sha256') == snap.get('template_sha256'))
        h5 = len(log) >= 2
        rows.append({'hook': name, 'log_lines': len(log),
                     'h1_history_exists': h1, 'h2_rows_complete': h2,
                     'h3_seq_monotonic': h3, 'h4_last_matches_snapshot': h4,
                     'h5_at_least_two': h5,
                     'seqs': seqs,
                     'reasons': [o.get('reason') for _, o in log if isinstance(o, dict)],
                     'last_reason': (log[-1][1].get('reason') if log and isinstance(log[-1][1], dict) else '')})
    bad = []
    for r in rows:
        for k in ('h1_history_exists', 'h2_rows_complete', 'h3_seq_monotonic',
                  'h4_last_matches_snapshot', 'h5_at_least_two'):
            if not r[k]:
                bad.append({'hook': r['hook'], 'check': k})
    doc = {'schema': 'install-history-r142-v1',
           'cmd': 'python 05-exec/r142_install_history.py --json <out>',
           'face': {'pairs_n': len(rows),
                     'bad_n': len(bad),
                     'reading': {
                         'bad_n': ('不通过的断言数。任一不通 = 安装历史不可回溯，判红。',
                                   'H1 历史存在非空 / H2 每行四要素齐 / H3 seq 单调增 /',
                                   'H4 末行与快照一致 / H5 至少 2 条（证明追加真的在发生）'),
                         'h5_at_least_two': ('刻意要求 >= 2：只装过一次时机历史与快照等价，',
                                              '看不出「追加」是否真的工作；装过两次才能证伪'),
                     }},
           'rows': rows,
           'bad': bad,
           'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline=chr(10)) as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    fa = doc['face']
    print('[HIST] %d 对 hook｜不通过 %d' % (fa['pairs_n'], fa['bad_n']))
    for r in rows:
        print('  %-12s lines=%d seq=%s H1=%s H2=%s H3=%s H4=%s H5=%s'
              % (r['hook'], r['log_lines'], r['seqs'], r['h1_history_exists'],
                 r['h2_rows_complete'], r['h3_seq_monotonic'],
                 r['h4_last_matches_snapshot'], r['h5_at_least_two']))
        if r['reasons']:
            print('               reasons=%s' % r['reasons'])
    for b in bad:
        print('  FAIL %s / %s' % (b['hook'], b['check']))
    if args.out:
        print('[HIST] JSON -> %s' % args.out)
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())