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
import subprocess
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOOKS = os.path.join(ROOT, '.git', 'hooks')
PAIRS = [('pre-commit',), ('post-commit',)]
REQ = ('seq', 'installed_at', 'invoker', 'reason')
GENESIS = 'GENESIS'  # r143：哈希链起点（旧无链行视为链首）


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
            # r143 修（#32 抓出「坐标系不一致面」）：原 enumerate(f, 1) 用 1-based 行号，
            # 链验证却按 0-based 索引 —— first_idx=1 时 range(1)=[0] 把**自己**当「之前的行」
            # 自我对照 => 误判「链裂开」。统一 0-based（log 内部索引）。
            for i, line in enumerate(f):
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
        # r143 H6 哈希链完整性（R142-4 落地）：逐行复算 line_hash 且 prev_hash 串联。
        # 任何一行被改 => 该行 line_hash 对不上 => 链断；整体重排/重写同理。
        # 语义裁定（r143 二次收紧，V2 反向验证抓出的漏洞）：
        #   · 初版「全 legacy 不判红」太宽 —— 攻击者删光链字段就能把伪造历史洗成 legacy。
        #   · 收紧为：**末行必须带链，无条件**。新安装永远带链 => 末行无链 =
        #     有人删链/截断/重写（含「全 legacy」态）=> 判红，逼重装补链。
        #   · 中段 legacy 行（仅换机后短期存在）不判红，但 chain_note 显形提醒。
        import hashlib as _hl
        chained = [(idx, o) for idx, o in log
                   if isinstance(o, dict) and o.get('line_hash')]
        legacy_n = len(log) - len(chained)
        h6 = True
        chain_note = ''
        if not log:
            h6 = False
            chain_note = '历史为空'
        elif not chained:
            # 全 legacy：末行必无链 => 判红（初版这里不判红，被 V2 伪造绕过 —— 已收紧）
            h6 = False
            chain_note = '全部 %d 行为 legacy 无链 —— 历史可被整体伪造，须重装补链' % legacy_n
        else:
            first_idx, first = chained[0]
            prev = 'GENESIS'
            if any(isinstance(log[j][1], dict) and log[j][1].get('line_hash')
                   for j in range(first_idx)):
                h6 = False
                chain_note = '带链行之前还有带链行却接不上（链裂开）'
            if h6:
                for idx, o in chained:
                    if o.get('prev_hash') != prev:
                        h6 = False
                        chain_note = 'L%d prev_hash 不接（链断）' % idx
                        break
                    expect = json.dumps({k: v for k, v in o.items() if k != 'line_hash'},
                                        ensure_ascii=False, sort_keys=True)
                    if o.get('line_hash') != _hl.sha256(expect.encode('utf-8')).hexdigest():
                        h6 = False
                        chain_note = 'L%d line_hash 复算不符（行被改）' % idx
                        break
                    prev = o.get('line_hash')
            # 末行必须带链（无条件 —— 防删链洗历史、防截断落回旧版）
            if h6 and chained[-1][0] != log[-1][0]:
                h6 = False
                chain_note = '末行无链（历史被截断/删链洗白/重写后落回旧版）'
        # r144 H7 外部锚点对账（R143-4 落地）：git 内台账 vs git 外日志。
        # 全套自洽伪造（快照+历史一起改）骗得过 H4/H5/H6（都是 git 外状态），
        # 骗不过 H7 —— 台账在 git 里，改它 = 版本历史留痕（提交者/时间可查）。
        anchor_path = os.path.join(ROOT, '06-benchmark', 'hook_install_ledger.json')
        h7 = False
        h7_note = ""
        ent = {}  # r145 防御：except 路径上 ent 可能未定义（宽限判别引用它）
        try:
            ledger = json.load(io.open(anchor_path, encoding="utf-8-sig")) or {}
            ent = (ledger.get("hook") or {}).get(name) or {}
            if not ent:
                h7 = False
                h7_note = "台账无该 hook 条目（台账缺失或被删）"
            elif ent.get("lines") != len(log):
                h7 = False
                h7_note = "台账 lines=%s != 实际日志行数=%s（历史被截断/伪造）" % (ent.get("lines"), len(log))
            elif ent.get("last_line_hash") != ((log[-1][1].get("line_hash") if log and isinstance(log[-1][1], dict) else "") or ""):
                h7 = False
                h7_note = "台账 last_line_hash 与实际末行不符（历史被重写）"
            else:
                h7 = True
                h7_note = "台账与日志一致（外部锚点确认）"
        except Exception as e:
            h7 = False
            h7_note = "台账不可读: %r" % (e,)
        # r145 H7 宽限判别（R144-4 落地）：台账落后但落后的那一行是**本会话自己装的**
        # ⇒ 这是「装了还没提交」的窗口期，非篡改 ⇒ WARNING 不判红。
        # 判别式：台账 lines == 实际行数-1 且 缺的那行 invoker.session ∈ 本机会话标识集。
        # 会话标识集 = 当前 env 会话 + git config user（同人多会话时 pid 不同 session 同）。
        # 反向仍紧：落后 >1 行、或缺的行来自别的会话 ⇒ 维持判红（那不是窗口期）。
        h7_warning = ''
        if not h7 and ent and isinstance(ent.get('lines'), int):
            missing = len(log) - ent['lines']
            last_o = log[-1][1] if log and isinstance(log[-1][1], dict) else {}
            cur_sessions = set()
            for k in ('DSH_SESSION_ID', 'CLAUDE_SESSION_ID', 'TERM_SESSION_ID'):
                if os.environ.get(k):
                    cur_sessions.add(os.environ.get(k))
            cur_users = set()
            try:
                gu = subprocess.run(['git', 'config', 'user.name'], cwd=ROOT,
                                    capture_output=True, text=True, encoding='utf-8',
                                    errors='replace', timeout=60).stdout.strip()
                if gu:
                    cur_users.add(gu)
            except Exception:
                pass
            last_sess = ((last_o.get('invoker') or {}).get('session') or '')
            last_user = ((last_o.get('invoker') or {}).get('git_user') or '')
            same_actor = (last_sess in cur_sessions) if cur_sessions else (last_user in cur_users)
            if missing == 1 and same_actor and ent.get('last_line_hash') == (
                    log[-2][1].get('line_hash') if len(log) >= 2 and isinstance(log[-2][1], dict) else ''):
                h7 = True
                h7_warning = ('台账落后 1 行且缺行系本会话所装（session/user 匹配）'
                              '=> 窗口期宽限，安装后请尽快提交台账')
        # r146 pending 通道（R145-4 落地）：跨会话/跨人窗口期的凭证。
        # 会话 B 的 env 里没有会话 A 的 session 且 git_user 也不同 => 三条件宽限失效 => 误红
        # （r146 量化坐实：_temp/v30_probe.py 跨人跨会话 rc=1）。
        # 解法 = 安装脚本同步写 git 可跟踪的 pending 标记件（记录缺行 line_hash/lines/invoker）；
        # 对账时 pending.line_hash == 实际末行、pending.lines == 实际行数、
        # 且台账 lines == 实际-1 且台账 last_line_hash == 倒数第二行 => 缺行系「已装未提交」=> 宽限。
        # 反向仍紧：伪造 pending 需改工作区 git 跟踪件 => 与伪造台账同强度（留 git 痕迹）。
        if not h7:
            try:
                pend_path = os.path.join(ROOT, '06-benchmark', 'hook_install_pending.json')
                pend = json.load(io.open(pend_path, encoding='utf-8-sig')) or {}
                pent = (pend.get('hook') or {}).get(name) or {}
                last_hash = ((log[-1][1].get('line_hash')
                              if log and isinstance(log[-1][1], dict) else '') or '')
                prev_hash = ((log[-2][1].get('line_hash')
                              if len(log) >= 2 and isinstance(log[-2][1], dict) else '') or '')
                if (pent.get('line_hash') == last_hash
                        and pent.get('lines') == len(log)
                        and isinstance(ent.get('lines'), int)
                        and len(log) - ent['lines'] == 1
                        and ent.get('last_line_hash') == prev_hash):
                    h7 = True
                    h7_warning = ('pending 标记件证实缺行系已装未提交（line_hash/lines 对上）'
                                  '=> 跨会话窗口期宽限，请尽快提交台账与 pending')
            except Exception:
                pass
        rows.append({'hook': name, 'log_lines': len(log),
                     'h1_history_exists': h1, 'h2_rows_complete': h2,
                     'h3_seq_monotonic': h3, 'h4_last_matches_snapshot': h4,
                     'h5_at_least_two': h5,
                     'h6_chain_intact': h6,
                     'h7_anchor_match': h7,
                     'h7_warning': h7_warning,
                     'h7_note': h7_note,
                     'chain_note': chain_note,
                     'legacy_lines_n': legacy_n,
                     'seqs': seqs,
                     'reasons': [o.get('reason') for _, o in log if isinstance(o, dict)],
                     'last_reason': (log[-1][1].get('reason') if log and isinstance(log[-1][1], dict) else '')})
    bad = []
    for r in rows:
        for k in ('h1_history_exists', 'h2_rows_complete', 'h3_seq_monotonic',
                  'h4_last_matches_snapshot', 'h5_at_least_two', 'h6_chain_intact',
                  'h7_anchor_match'):
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
        print('  %-12s lines=%d seq=%s H1=%s H2=%s H3=%s H4=%s H5=%s H6=%s'
              % (r['hook'], r['log_lines'], r['seqs'], r['h1_history_exists'],
                 r['h2_rows_complete'], r['h3_seq_monotonic'],
                 r['h4_last_matches_snapshot'], r['h5_at_least_two'],
                 r['h6_chain_intact']))
        if r.get('chain_note'):
            print('               chain_note=%s (legacy_lines=%s)' % (r['chain_note'], r.get('legacy_lines_n')))
        if r['reasons']:
            print('               reasons=%s' % r['reasons'])
    for b in bad:
        print('  FAIL %s / %s' % (b['hook'], b['check']))
    if args.out:
        print('[HIST] JSON -> %s' % args.out)
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())