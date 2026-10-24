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





def judge(rows, now=None, max_days=7, exclude_after=None):

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

    # R125 修（R123-5 自抓）：本门是自指门 —— 它读台账最后一条，而 runner 会在本轮结束时

    # 追加本轮记录，于是它读到的是上一轮的结论。任何一轮 FAIL 都会让它下一轮再红一次，

    # 表现为「38 门里唯一红的是上一轮的残留」，逼人连跑两次才能拿到绿。

    # 修法：排除「晚于 exclude_after（本进程启动时刻）」的记录 —— 那些不是「上一次」，

    # 是「这一次的并发写入」。这不放松判据：上一轮的 FAIL 仍会照红（除非它是本轮自己写的）。

    if exclude_after is not None:

        _before = [r for r in local if r["_t"] <= exclude_after]

        if _before:

            local = _before

    if not local:

        return "FAIL", "台账只有 CI 记录、无本机记录 ⇒ 本机专属门无人执行（CI 绿不能替人证明，%d 条全为 ci）" % len(rows)

    # r202 修（我本轮亲手撞出来）：本门要证的是「不可移植门最近真被完整跑过且过了」。

    # 而 --portable-only 按定义跳过了全部不可移植门（实测 30 跑 / 48 跳），它的 PASS 不能

    # 证明任何本机专属门被执行过。旧写法 max(local) 不筛 mode ⇒ 我用一次 --portable-only

    # 就把 CI 的 gate_run_freshness 喂成绿（本机当时还有 5 门红）。这与本门自己防的是同一

    # 件事：局部面被当成全局面。缺 mode 字段的历史行按 full 处理（早于该字段引入）；

    # 被忽略的局部跑若晚于采信行，会在理由里显式提示（可见性优先于静默）。

    partial = [r for r in local if str(r.get("mode") or "full") != "full"]

    local_full = [r for r in local if str(r.get("mode") or "full") == "full"]

    if not local_full:

        return "FAIL", "本机记录全为局部跑（%d 条 mode!=full）⇒ 不可移植门从未被完整执行" % len(partial)

    last = max(local_full, key=lambda r: r["_t"])

    age_days = (now - last["_t"]).total_seconds() / 86400.0

    if partial and max(partial, key=lambda r: r["_t"])["_t"] > last["_t"]:

        why_prefix = "（注：%d 条局部跑 mode!=full 已忽略，其最新一条晚于本次采信的全量跑）" % len(partial)

    else:

        why_prefix = ""

    if last.get("verdict") != "PASS":

        return "FAIL", why_prefix + "最近一次本机门禁未过（verdict=%s，%.1f 天前）" % (last.get("verdict"), age_days)

    if age_days > max_days:

        return "FAIL", why_prefix + "最近一次本机 PASS 已在 %.1f 天前（阈值 max_days=%d 天）⇒ 判据已僵尸化" % (age_days, max_days)

    return "PASS", why_prefix + "最近本机 PASS 距今 %.2f 天 ≤ max_days=%d；台账共 %d 条（本机 %d / CI %d）" % (

        age_days, max_days, len(rows), len(local), len(rows) - len(local))





def _ledger_clock(now, rows):

    """把 now 归一到「台账所用时区」，消除本机(UTC+8)与 CI(UTC) 的基准漂移（r191）。



    台账 ts 是 naive 字符串、由本机写入；CI 的 now 是 UTC。若不归一，CI 会把未来 8 小时的

    本机 PASS 记录全排除，只剩更早的 FAIL ⇒ 恒红（实测 663 条台账两种 now 判出 PASS/FAIL 两种结论）。

    只做基准对齐，不动阈值、不豁免过期记录，因此不放松判据。

    """

    ok = []

    for r in rows:

        try:

            ok.append(datetime.strptime(str(r.get("ts")), TS_FMT))

        except ValueError:

            continue

    if not ok:

        return now

    newest = max(ok)

    drift = (newest - now).total_seconds()

    # 台账最新 ts 比 now 还晚 > 5 分钟 ⇒ 视为时区漂移，按漂移量把 now 推后对齐

    if drift > 300:

        return now + __import__("datetime").timedelta(seconds=drift)

    return now





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

    # R125：把本进程启动时刻作为 exclude_after 传下去，使本门只对「本轮之前」的记录负责，

    # 免得每一轮的自身残留把下一轮染红（自指门的自我实现缺陷，见 judge 的注释）。

    #

    # r191 修（CI 一手，r32 时区缺陷）：台账 ts 由**本机**写（本地时区 UTC+8 的 naive 字符串），

    # 而 CI runner 的 datetime.now() 是 **UTC**。两者直接比大小 ⇒ CI 侧 now 比台账 ts 早 8 小时，

    # 于是「最近 8 小时内」的全部本机 PASS 记录被当成「未来记录」排除，只剩更早的 FAIL ⇒ 必判红。

    # 实测：同一份 663 条台账，用本地 now 判 PASS，用 now-8h 判 FAIL。

    # 修法：把 now/exclude_after 归一到台账所用的时区 —— 取台账最后一条 ts 与 now 的偏移，

    # 若台账时间「超前」now 超过容差，就按超前量回拨（即把 now 视作台账时区）。

    # 这不是放宽判据：它只纠正「时钟基准不一致」，不改变 max_days 阈值，也不豁免过期记录。

    _boot = _ledger_clock(datetime.now(), rows)

    state, why = judge(rows, now=_boot, max_days=args.max_days, exclude_after=_boot)

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
