# -*- coding: utf-8 -*-
# r130_gate_table_reconcile.py — 门表变更对账闸（R129-5 落地）。
#
# 存在理由：r126 新判据直接进巡检、直接出报告数字，45 条假红流进两份文档；
# r128 把对账做成机器（第 40 门）、r129 把入库做成准入门（第 41 门），
# 但两者都还只是「跑的时候报」，**没有任何机制要求新增门必须留下对账痕迹**。
# 本件补上这一环：门表（GATES）每次新增门，必须能在台账里找到它对应的对账/夹具记录，
# 否则判红。
#
# 判据形态（可复算、不靠自觉）：
#   ① 取门表快照：当前 GATES 的 id 集合 vs 上一个提交（HEAD~1）的 GATES id 集合；
#   ② 新增门 = 差集；
#   ③ 每个新增门必须在 06-benchmark/gate_reconcile_registry.json 里有登记行
#      （该登记行由「跑一次对账/夹具」时写入，见 --record）；
#   ④ 缺登记 ⇒ 判红并具名。
#
# 用法: python 05-exec/r130_gate_table_reconcile.py [--record <门id> --evidence <路径>]
# 退出码: 0 全登记 / 1 有新增门缺登记 / 2 输入面不可用
import argparse
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUNNER = os.path.join(HERE, 'run_gates.py')
REGISTRY = os.path.join(ROOT, '06-benchmark', 'gate_reconcile_registry.json')


def gate_ids_from_source(src):
    # 从 runner 源码里抠出 GATES 表的 id（不 import，避免副作用）
    # r130 自抓三（解析污染）：初版用 startswith('"id":') 把 run_gate 里两处
    #   rows.append({"id": ...}) 也当成门 ⇒ 43 个「门」里有 2 个是假的。
    #   收紧为：**行首恰 8 个空格**（GATES 表项的固定缩进）+ **行尾恰为一个逗号**。
    out = []
    for line in src.splitlines():
        if not line.startswith('        "id": '):
            continue
        s = line.strip()
        if not s.endswith(','):
            continue
        v = s.split(':', 1)[1].strip().rstrip(',').strip('"')
        if v:
            out.append(v)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--record', help='把某个门登记为「已对账」（写入台账）')
    ap.add_argument('--evidence', default='', help='对账证据路径（登记行必填）')
    ap.add_argument('--json', dest='out')
    args = ap.parse_args()

    if not os.path.isfile(RUNNER):
        print('[GATETABLE] UNVERIFIED runner 不存在: %s' % RUNNER)
        return 2

    reg = {}
    if os.path.isfile(REGISTRY):
        try:
            reg = (json.loads(io.open(REGISTRY, encoding='utf-8').read()) or {}).get('gates') or {}
        except Exception:
            reg = {}

    # --record 形态：登记一个门（须带证据）
    if args.record:
        if not args.evidence:
            print('[GATETABLE] REFUSE --record 须同时给 --evidence（无证据的登记等于装饰）')
            return 1
        ev = args.evidence
        full = ev if os.path.isabs(ev) else os.path.join(ROOT, ev)
        if not os.path.isfile(full):
            print('[GATETABLE] REFUSE 证据文件不存在: %s' % ev)
            return 1
        reg[args.record] = {'evidence': ev,
                          'at': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}
        doc = {'schema': 'gate-reconcile-registry-r130-v1', 'gates': reg}
        os.makedirs(os.path.dirname(REGISTRY), exist_ok=True)
        with io.open(REGISTRY, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print('[GATETABLE] REGISTERED %s（证据 %s）' % (args.record, ev))
        return 0

    # r130 自抓二（第二次假绿）：改比 HEAD 仍抓不到 —— 因为**新门一旦提交，HEAD 就含它了**。
    # 闸门要比的不是 git 历史，而是**上一次对账时的门表快照**（本工具自己的台账）。
    # git 只作为「快照缺失时」的冷启动兜底。
    cur = gate_ids_from_source(io.open(RUNNER, encoding='utf-8').read())
    prev = reg.get('_snapshot_gate_ids') or []
    cold_start = not prev
    if cold_start:
        try:
            prev_src = subprocess.run(['git', 'show', 'HEAD:05-exec/run_gates.py'],
                                   cwd=ROOT, capture_output=True, text=True,
                                   encoding='utf-8', errors='replace', timeout=120).stdout
            prev = gate_ids_from_source(prev_src) if prev_src else []
            print('[GATETABLE] 冷启动：台账无快照，改用 HEAD 门表做首次比对（之后一律用快照）')
        except Exception:
            prev = []
    added = [g for g in cur if g not in prev]
    missing = [g for g in added if g not in reg]
    removed = [g for g in prev if g not in cur]
    if not missing:
        # 全部新增门都已登记 => 把当前门表写回快照，下一轮就以它为基线。
        # 冷启动也写：否则每次跑都是冷启动，永远没有基线（r130 首跑自抓）。
        doc = {'schema': 'gate-reconcile-registry-r130-v1', 'gates': reg}
        doc['gates']['_snapshot_gate_ids'] = cur
        doc['gates']['_snapshot_at'] = __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')
        os.makedirs(os.path.dirname(REGISTRY), exist_ok=True)
        with io.open(REGISTRY, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    print('[GATETABLE] 门表 %d 门（基线 %d）｜新增 %d｜移除 %d｜未登记 %d'
          % (len(cur), len(prev), len(added), len(removed), len(missing)))
    if removed:
        print('[GATETABLE] 移除 %s（门禁数减少须人工确认，防误删）' % ', '.join(removed))
    for g in missing:
        print('  UNREGISTERED 新增门 %s 无对账登记行 ⇒ 请先跑对账/夹具再 --record' % g)
    return 1 if missing else 0


if __name__ == '__main__':
    raise SystemExit(main())