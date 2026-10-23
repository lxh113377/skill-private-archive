# -*- coding: utf-8 -*-
# r137_commit_gate_map.py -- 「本次提交该过哪道门」的判定面（第 49 门）。
#
# 存在理由（r137 一手）：r136 盘点出本仓 5 条强制条目（#30 落盘 / #31 处方 / #32 判据面 /
# #33 结论层 / #34 纪律自用）**全部没有流程强制点** —— 门只跑不阻断，hook 全部 exit 0。
# 而 r130 的 pre-commit 刻意不阻断，理由正当：**并行会话也在改同一个仓**，
# 无差别阻断会把我的判据变成「别人的活干不下去」（R269 反面）。
#
# 本件给出第三条路：**按本次变更的归属分级**。
#   ① 变更涉及 05-exec/ 或 06-benchmark/ 或 memory/ 或 AGENTS.md ⇒ 属于「本仓纪律面」，
#      须过对应门；
#   ② 变更只涉及别的面（受管根镜像、_trash 迁移等）⇒ 不属本仓判据面，不阻断。
#
# 本件只做**判定**（本次变更应过哪些门），不自己跑门、不自己阻断 ——
# 执行与阻断留给 pre-commit hook（r130 已装，只是不阻断）。
#
# 用法: python 05-exec/r137_commit_gate_map.py [--staged <件>] [--json <件>]
# 退出码: 0 完成 / 2 输入面不可用（R247 禁按 0 记绿）
import argparse
import io
import re
import json
import os
import subprocess
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUNNER = os.path.join(HERE, 'run_gates.py')

# 纪律面文件前缀 ⇒ 触发对应门
TRIGGERS = [
    ('05-exec/', 'proposal_evidence_face', '改了 05-exec/ 下的判据/工具 ⇒ 新判据须过入库准入门（提案证据面同步）'),
    ('06-benchmark/transmit_proposals.json', 'proposal_evidence_face', '改了转办提案 ⇒ 提案的处方须有读数面支撑（#31/#34）'),
    ('06-benchmark/全量对标报告_', 'causal_evidence_face', '写了报告 ⇒ 因果结论须有实测支撑或显式标注（#33）'),
    ('AGENTS.md', 'gate_table_reconcile', '改了 AGENTS.md 纪律条目 ⇒ 门表对账闸须过（新增门须留对账痕）'),
    ('memory/07-next-steps.md', 'debt_aging', '改了 07 台账 ⇒ 账龄件须重生（写记忆后必算账龄）'),
    ('05-exec/run_gates.py', 'gate_table_reconcile', '改了门表 ⇒ 新增门须有对账登记行（#31 门表闸）'),
    # r152（R150-6 分级阻断）：契约纪律面变更 ⇒ 契约风险预警必须 P0=0（本门 P0>0 即 rc=1）。
    #   刻意**只**挂契约纪律面，不做无差别阻断（R269 反面）。
    (('05-exec/', '06-benchmark/transmit_proposals.json', 'AGENTS.md', 'memory/07-next-steps.md'),
     'contract_lifecycle_face',
     '改了契约纪律面（判据/转办/纪律条目/P0 台账）⇒ 契约全生命周期风险预警须为 P0=0（R152 分级阻断）'),
]


# r162（R159-1 + r137 真缺陷）：closing 形态白名单。
#   · 旧正则过宽：把 06-benchmark/transmit_proposals.json（纪律面，TRIGGERS 第 2 条）未 add 也洗成 closing
#     => 假 SKIP，击穿 r133 第④形态「有未提交改动但暂存为空 = 漏 add，禁按 0 记绿」。
#   · 旧正则又过窄：memory/sessions/volume-snapshots.jsonl（append-only 台账，收尾跑
#     handoff.py volume --snapshot 的必然产物）不在内 => 稳态从 SKIP 掉到 UNVERIFIED rc=2。
#   修法 = 白名单制：只认 append-only 台账族，且纪律面具名件永不进白名单。
CLOSING_ALLOW = (
    '06-benchmark/',
    'memory/sessions/',
    '05-exec/_r55probe_tmp/',
)
CLOSING_DENY = (
    '06-benchmark/transmit_proposals.json',
    '06-benchmark/全量对标报告_',
    'AGENTS.md',
    'memory/07-next-steps.md',
    '05-exec/run_gates.py',
)


def is_closing_form(line):
    """判定一行 git porcelain 输出是否属「收尾产物」形态。

    返回 True/False；line 形态必须是 '<XY> <path>'（git status --porcelain v1）。
    设计约束（r162，X-28 同族：参数形态必须显式校验，禁把任意串当配置）：
      · 只在白名单前缀内认 json/jsonl（append-only 台账或每轮快照）；
      · 命中 DENY（纪律面）一律 False —— 白名单永远不能让纪律面静默过关；
      · 路径含空格或异常形态 => False（不猜）。
    """
    if not line or not isinstance(line, str):
        return False
    # git status --porcelain v1 形态为 XY + 空格 + path，两个状态字符必须先吃掉，
    # 否则 path 仍带状态位（r162 自抓：首版漏吃 XY 导致 t1 假红）。
    if len(line) < 4 or line[2] != ' ':
        return False
    path = line[3:].strip()
    if not path or ' ' in path:
        return False
    if any(path == d or path.startswith(d) for d in CLOSING_DENY):
        return False
    if not path.startswith(CLOSING_ALLOW):
        return False
    return path.endswith('.json') or path.endswith('.jsonl')

def staged_files():
    try:
        p = subprocess.run(['git', 'diff', '--cached', '--name-only'],
                           cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                           errors='replace', timeout=120)
        return [x for x in (p.stdout or '').splitlines() if x.strip()]
    except Exception:
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--staged', default='', help='已暂存文件清单（每行一个）；缺省用 git diff --cached')
    ap.add_argument('--json', dest='out')
    ap.add_argument('--runner', default=RUNNER)
    ap.add_argument('--dirty', default='', help='r162 测试缝：伪造的 git status --porcelain 清单文件（每行一条）；缺省跑真 git')
    args = ap.parse_args()
    if not os.path.isfile(args.runner):
        print('[GATEMAP] UNVERIFIED runner 不存在: %s' % args.runner)
        return 2
    if args.staged and os.path.isfile(args.staged):
        files = [x.strip() for x in io.open(args.staged, encoding='utf-8').read().splitlines() if x.strip()]
    else:
        files = staged_files()
    if not files:
        # r139 修：暂存为空有两形态——① 有提交进行中但漏 add（r133 第④形态，禁按 0 记绿）；
        # ② 工作区干净、无提交进行中（合法稳态，如收尾轮全部已 commit 后）。
        # 判别 = 有无未提交改动：无 ⇒ SKIP（无暂存活动属稳态）；有 ⇒ 维持 UNVERIFIED（漏 add）。
        if args.dirty:
            # r162 测试缝：夹具注入伪造的 porcelain 清单（形态校验：必须是已存在文件）。
            # 缺省仍走真 git —— 生产路径零改动。
            if not os.path.isfile(args.dirty):
                print('[GATEMAP] UNVERIFIED --dirty 指定的文件不存在: %s' % args.dirty)
                return 2
            dirty_files = [x.rstrip() for x in io.open(args.dirty, encoding='utf-8').read().splitlines() if x.strip()]
        else:
            dirty = subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT,
                                   capture_output=True, text=True, encoding="utf-8",
                                   errors='replace', timeout=120)
            dirty_files = [x.rstrip() for x in (dirty.stdout or '').splitlines() if x.strip()]
        # r139 二次修（自抓）：「工作区干净」在收尾稳态下恒不成立——每次跑完全门都会
        # 产生 debt autoregen + gate json + gate_runs.jsonl 等收尾产物。故判据改为：
        # 未提交文件**全部**是收尾产物形态 ⇒ 仍属稳态。
        # r162：形态判定收窄为白名单（is_closing_form）—— 旧正则既过宽（洗掉提案台账漏 add）
        # 又过窄（漏掉 memory/sessions/*.jsonl 收尾台账），两端都实测复现过。
        is_closing = dirty_files and all(is_closing_form(x) for x in dirty_files)
        if not dirty_files or is_closing:
            print('[GATEMAP] SKIP 无暂存活动且未提交件全为收尾产物形态（06-benchmark/*.json[l]）——本门不适用）')
            print('[GATEMAP:SKIP]')
            return 0
        print('[GATEMAP] UNVERIFIED 有未提交改动但暂存清单为空（漏 add？r133 第 ④ 种形态）')
        print('          禁按 0 记绿 —— 空清单会让「该过哪道门」恒为空集')
        return 2
    runner_src = io.open(args.runner, encoding='utf-8').read()
    gates = {}
    for prefix, gid, why in TRIGGERS:
        # r152：prefix 允许为 tuple —— 一门可挂多个触发前缀（gates 以 gid 为键，
        #   同 gid 写两条会互相覆盖 => 想一门多面只能走 tuple）。
        prefixes = prefix if isinstance(prefix, tuple) else (prefix,)
        hit = [f for f in files if any(f.startswith(p) or f == p for p in prefixes)]
        if not hit:
            continue
        needle = chr(34) + 'id' + chr(34) + ': ' + chr(34) + gid + chr(34)
        if needle not in runner_src and not os.path.isfile(os.path.join(HERE, gid + '.py')):
            gates[gid] = {'gates': sorted(set(hit)), 'why': why, 'in_gates_table': False}
        else:
            gates[gid] = {'gates': sorted(set(hit)), 'why': why,
                          'in_gates_table': needle in runner_src}
    doc = {'schema': 'commit-gate-map-r137-v1',
           'cmd': 'python 05-exec/r137_commit_gate_map.py --json <out>',
           'staged_n': len(files),
           'staged': files,
           'required_gates': gates,
           'required_gate_ids': sorted(gates.keys()),
           'in_scope_n': len(gates),
           'reading': {
               'in_scope_n': '本次提交落在本仓纪律面的门数（0 = 不属本仓判据面，不阻断）',
               'required_gate_ids': '本次提交**必须过**的门 id 列表 —— pre-commit 依此逐门跑并按结果阻断',
               'staged_n': '本次暂存文件数',
           },
           'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    print('[GATEMAP] 暂存 %d 个文件｜纪律面门 %d：%s'
          % (len(files), len(gates), ', '.join(sorted(gates.keys())) or '(不在纪律面)'))
    for gid, v in sorted(gates.items()):
        print('  %-26s 触发文件 %s' % (gid, v['gates'][:3]))
    if args.out:
        print('[GATEMAP] JSON -> %s' % args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())