# -*- coding: utf-8 -*-
"""r32_ci_health.py — 量「CI 到底有没有在判定」，而不是「有没有 CI」（r32 第九维）。

r31 量的是**存在性**（workflow 文件数）。本轮发现那格数字会骗人：
    github/spec-kit   18 个 workflow，近 50 run 里 **50% 停在 action_required**（从未出判定），success 30%
    vercel-labs/skills 3 个 workflow，60% action_required，success 24%
    mem0ai/mem0       34 个 workflow，success 54%
    ruvnet/ruflo      29 个 workflow，success 94% / 中位 160 s
    mycelium(36★)     11 个 workflow，success 84% / 中位 22 s   ← 与本体系最同构者仍是最优形态
⇒ 「判据在 CI 里」的真值要用 **run 结论分布 + 心跳是否断** 来量，文件数只是必要条件。

职责边界（刻意）：本工具**只测不拦** —— 网络/鉴权失败不该阻断本地落盘（否则离线即不能干活）。
「必须有人跑门禁」的压力由 `r32_gate_freshness.py`（读执行台账，CI 里也执行）承担。

用法：
    python 05-exec/r32_ci_health.py [--per-page 50] [--max-age-hours 36] [--json 件.json]
退出码：0 本仓 CI 健康 / 1 不健康（心跳断 或 成功率低于阈值）/ 2 UNVERIFIED（gh 不可用、无 run、取不到）
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone

OPPOSITES = [
    "obra/superpowers", "anthropics/skills", "github/spec-kit", "ruvnet/ruflo",
    "mem0ai/mem0", "addyosmani/agent-skills", "sickn33/agentic-awesome-skills",
    "vercel-labs/skills", "mycelium-hq/ai-brain-starter", "lucasrosati/claude-code-memory-setup",
    "mattpocock/skills", "Fission-AI/OpenSpec",
]
SELF = "lxh113377/skill-private-archive"
SUCCESS_FLOOR = 0.60  # 低于此成功率 ⇒ 判据虽在跑但长期不绿，视为无效面（r32 取自对手分布中位）


def gh(args):
    return subprocess.run(["gh"] + args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=90)


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def sample(slug, per_page):
    p = gh(["api", "repos/%s/actions/runs?per_page=%d" % (slug, per_page), "--jq", ".workflow_runs"])
    if p.returncode != 0 or not p.stdout.strip():
        return None
    try:
        runs = json.loads(p.stdout)
    except ValueError:
        return None
    if not isinstance(runs, list) or not runs:
        return None
    c = {}
    for r in runs:
        key = r.get("conclusion") or ("in_progress" if r.get("status") != "completed" else "unknown")
        c[key] = c.get(key, 0)  + 1
    done = [r for r in runs if r.get("status") == "completed"]
    durs = []
    for r in done:
        a, b = r.get("run_started_at") or r.get("created_at"), r.get("updated_at")
        if a and b:
            d = (ts(b) - ts(a)).total_seconds()
            if d >= 0:
                durs.append(d)
    durs.sort()
    latest = max((r.get("created_at") for r in runs if r.get("created_at")), default=None)
    tot = len(runs)
    return {"repo": slug, "runs": tot, "conclusions": c,
            "success_rate": round(c.get("success", 0) / tot, 3),
            "failure_rate": round(c.get("failure", 0) / tot, 3),
            "action_required_rate": round(c.get("action_required", 0) / tot, 3),
            "skipped_rate": round(c.get("skipped", 0) / tot, 3),
            "median_duration_s": (durs[len(durs) // 2] if durs else None),
            "last_run_at": latest,
            "branches": len({r.get("head_branch") for r in runs})}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-page", type=int, default=50)
    ap.add_argument("--max-age-hours", type=int, default=36, help="本仓心跳阈值（gates.yml 为每日 cron）")
    ap.add_argument("--skip-opposites", action="store_true")
    ap.add_argument("--json")
    args = ap.parse_args()

    if gh(["--version"]).returncode != 0:
        print("[CI-HEALTH:UNVERIFIED] gh 不可用 ⇒ 不得把「取不到」读成「健康」或「不健康」（R247）")
        return 2

    rows = []
    targets = ([SELF] if args.skip_opposites else [SELF] + OPPOSITES)
    for slug in targets:
        r = sample(slug, args.per_page)
        if r is None:
            print("%-42s 无可读 run（跳过，不计入判定）" % slug)
            rows.append({"repo": slug, "error": "no_runs"})
            continue
        rows.append(r)
        print("%-42s n=%2d success=%4.0f%% failure=%4.0f%% action_required=%4.0f%% 中位=%s last=%s" % (
            r["repo"], r["runs"], 100 * r["success_rate"], 100 * r["failure_rate"],
            100 * r["action_required_rate"],
            ("%.0fs" % r["median_duration_s"]) if r["median_duration_s"] is not None else "-",
            r["last_run_at"] or "-"))

    me = next((r for r in rows if r.get("repo") == SELF and "error" not in r), None)
    if me is None:
        print("[CI-HEALTH:UNVERIFIED] 本仓 run 历史取不到（gh 鉴权面或尚无 run）")
        return 2
    age_h = None
    if me["last_run_at"]:
        age_h = round((datetime.now(timezone.utc) - ts(me["last_run_at"])).total_seconds() / 3600.0, 2)
    reasons = []
    if age_h is None:
        reasons.append("无 last_run_at")
    elif age_h > args.max_age_hours:
        reasons.append("心跳断：最近 run 距今 %.1f h > 阈值 %d h（cron 每日档已失效？）" % (age_h, args.max_age_hours))
    if me["success_rate"] < SUCCESS_FLOOR:
        reasons.append("success=%.0f%% < 地板 %.0f%% ⇒ 判据在跑但长期不绿" % (
            100 * me["success_rate"], 100 * SUCCESS_FLOOR))
    state = "FAIL" if reasons else "PASS"
    print("-" * 72)
    print("覆盖根: gh api（只读 GET）｜窗口=近 %d run｜心跳阈值=%d h｜成功率地板=%.0f%%" % (
        args.per_page, args.max_age_hours, 100 * SUCCESS_FLOOR))
    print("判据面: 仅 %s 参与 verdict；对手行只作对照，不参与本仓判定" % SELF)
    print("[CI-HEALTH:%s] %s" % (state, "；".join(reasons) if reasons else
                                 "心跳 %.1f h 内且 success=%.0f%% ≥ 地板" % (age_h, 100 * me["success_rate"])))

    if args.json:
        doc = {"schema": "ci-health-v1", "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
               "readonly": True,
               "benchmark": "r32 第九维 CI 有效性（run 结论分布 + 心跳，非 workflow 文件数）",
               "provenance_cmd": 'gh api repos/<slug>/actions/runs?per_page=50 --jq .workflow_runs',
               "window_runs": args.per_page, "heartbeat_max_age_hours": args.max_age_hours,
               "success_floor": SUCCESS_FLOOR,
               "self": me, "self_state": state, "self_reasons": reasons,
               "opposites": [r for r in rows if r.get("repo") != SELF],
               "note": "本工具只测不拦：网络/鉴权失败不得阻断本地落盘；强制面由 r32_gate_freshness.py 承担"}
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.json)
    return 0 if state == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
