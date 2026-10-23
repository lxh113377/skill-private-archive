# -*- coding: utf-8 -*-
"""r32_gate_freshness.py — 判「本仓门禁最近是否还在被真跑」（r32 H-2，防僵尸化）。

存在理由（r32 对手实测，见 `06-benchmark/ci_health_r32_2026-09-25.json`）：
    github/spec-kit    近 50 run 里 **50% 停在 action_required**（从未产生判定），success 仅 30%
    vercel-labs/skills 近 50 run 里 60% action_required，success 24%
    mem0ai/mem0        34 个 workflow，success 54%
    ⇒ 「有 workflow / 有判据文件」不等于「判据在起作用」。
    本仓还有一层对手没有的风险：r31 实测 **5 门里 2 门本质本机专属**（仓内 tracked SKILL.md 本体 = 0 个，
    CI 里没有语料，参数化也造不出资产面）⇒ 这两门一旦没人跑，CI 依旧全绿，**没有任何地方会报警**。
    本判据就是补这个洞：把「人还在本机跑门禁」变成一条 **CI 也能执行** 的可见判据（台账被随仓提交）。

三态（沿用 run_gates 的 R247 语义）：
    PASS        最近一次「本机」记录是 PASS 且距今 ≤ max_days
    FAIL        无本机记录（只有 CI 记录）/ 最近一次未过 / 超过 max_days
    UNVERIFIED  台账为空 / ts 不可解析 / origin 出现未知取值 ⇒ 一律不算过，也不允许"当作很新"

用法：
    python 05-exec/r32_gate_freshness.py [--max-days 7] [--json 06-benchmark/freshness_r32.json]
退出码：0 PASS / 1 FAIL / 2 UNVERIFIED
"""

import argparse
import io
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LEDGER = os.path.join(os.path.dirname(HERE), "06-benchmark", "gate_runs.jsonl")
ORIGIN_DOMAIN = ("local", "ci")
TS_FMT = "%Y-%m-%dT%H:%M:%S"

# 反假绿要点：CI 记录**不得**冒充本机记录 —— CI 绿只证明可移植门在跑，
# 本机专属门（ratchet_gate / r19_scan_fixtures）有没有被跑，只能由本机台账说话。


def load_ledger(path):
    """读 JSONL 台账。文件不存在 ⇒ 返回空列表（由 judge 判 UNVERIFIED，不得当 0 违规）。"""
    rows = []
    if not os.path.exists(path):
        return rows
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                rows.append({"_broken_json": line[:80]})
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def judge(rows, now=None, max_days=7):
    """返回 (state, why)。rows 为台账逐条 dict。"""
    now = now or datetime.now()
    rows = list(rows)
    if not rows:
        return "UNVERIFIED", "台账为空（没跑过不等于跑得干净，R247）"
    for r in rows:
        if "_broken_json" in r:
            return "UNVERIFIED", "台账存在不可解析行=%r" % r["_broken_json"]
    bad_origin = [r.get("origin") for r in rows if r.get("origin") not in ORIGIN_DOMAIN]
    if bad_origin:
        return "UNVERIFIED", "台账存在未知 origin=%r，取值域=%s ⇒ 判据不可信" % (
            sorted(set(map(str, bad_origin))), list(ORIGIN_DOMAIN))
    for r in rows:
        try:
            r["_t"] = datetime.strptime(str(r.get("ts")), TS_FMT)
        except ValueError:
            return "UNVERIFIED", "ts 不可解析=%r（既不当作很新，也不当作很旧）" % r.get("ts")
    local = [r for r in rows if r.get("origin") == "local"]
    if not local:
        return "FAIL", "台账只有 CI 记录、无本机记录 ⇒ 本机专属门无人执行（CI 绿不能替人证明，%d 条全为 ci）" % len(rows)
    last = max(local, key=lambda r: r["_t"])
    age_days = (now - last["_t"]).total_seconds() / 86400.0
    if last.get("verdict") != "PASS":
        return "FAIL", "最近一次本机门禁未过（verdict=%s，%.1f 天前）" % (last.get("verdict"), age_days)
    if age_days > max_days:
        return "FAIL", "最近一次本机 PASS 已在 %.1f 天前（阈值 max_days=%d 天）⇒ 判据已僵尸化" % (age_days, max_days)
    return "PASS", "最近本机 PASS 距今 %.2f 天 ≤ max_days=%d；台账共 %d 条（本机 %d / CI %d）" % (
        age_days, max_days, len(rows), len(local), len(rows) - len(local))


MARK = {"PASS": "[FRESH:PASS]", "FAIL": "[FRESH:FAIL]", "UNVERIFIED": "[FRESH:UNVERIFIED]"}
RC = {"PASS": 0, "FAIL": 1, "UNVERIFIED": 2}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    ap.add_argument("--max-days", type=int, default=7)
    ap.add_argument("--json")
    args = ap.parse_args()

    rows = load_ledger(args.ledger)
    state, why = judge(rows, now=datetime.now(), max_days=args.max_days)
    print("=== 门禁执行新鲜度判据（r32 H-2）===")
    print("台账: %s（%d 条）" % (args.ledger, len(rows)))
    print("阈值: max_days=%d 天｜来源域: %s｜时间格式: %s" % (args.max_days, list(ORIGIN_DOMAIN), TS_FMT))
    print("覆盖根: 本机专属门 = ratchet_gate / r19_scan_fixtures（仓内无 SKILL.md 语料，CI 永远看不到）")
    print("%s %s" % (MARK[state], why))
    if args.json:
        doc = {"schema": "gate-freshness-v1",
               "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
               "readonly": True, "benchmark": "r32 判据僵尸化防护",
               "ledger": args.ledger, "rows": len(rows), "max_days": args.max_days,
               "origin_domain": list(ORIGIN_DOMAIN), "state": state, "why": why,
               "coverage": ["06-benchmark/gate_runs.jsonl"]}
        with io.open(args.json, "w", encoding="utf-8") as f:
            f.write(json.dumps(doc, ensure_ascii=False, indent=1))
        print("JSON -> %s" % args.json)
    return RC[state]


if __name__ == "__main__":
    raise SystemExit(main())
