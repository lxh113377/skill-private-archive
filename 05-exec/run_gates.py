# -*- coding: utf-8 -*-
"""run_gates.py — 本仓门禁聚合 runner（r31 / 对标新维度 N12「自动化验收面」的自持落地）。

对标实物（证据：`06-benchmark/ci_evidence/`，r31 逐份 gh api 取原文）：
  · mycelium-hq/ai-brain-starter `template-purity.yml`：
    "the identical check runs locally pre-push, in the write-time hook, and here in CI —
     one source of truth" ⇒ 同一份判据逻辑必须能被 N 个调用点复用，而不是每个调用点各抄一遍命令行。
  · mycelium `behavioral-install-eval.yml`：
    "exits 2 (loud INFRA error) when ANTHROPIC_API_KEY is missing, so a dead repo secret can
     never read as a green skip" ⇒ 判据跑不起来 ≠ 判据通过；必须有 PASS/FAIL 之外的第三态。
  · sickn33/agentic-awesome-skills `ci.yml`：5 个独立 job（pr-policy / source-validation /
    pr-evidence / artifact-preview / main-validation-and-sync），互不短路 ⇒ 一处红不得遮住其余四面。

本仓原状（r31 实测）：`memory/AGENTS.md` 的「项目门禁命令」是 5 段 `&&` 串联 ⇒
  ① 第一段红即短路，后 4 段是否仍绿**不可知**；
  ② 无任何覆盖根自证（违本仓 R20-2「预算/上限类门禁须自证覆盖根清单」）；
  ③ 无耗时基线（对标报告「性能」维度我们只有对手数字、没有自家数字）。

三态判据（本 runner 的核心）：
  PASS       rc == 0 且 输出含该门的 pass_token
  FAIL       rc != 0
  UNVERIFIED rc == 0 但 输出缺 pass_token（静默跳过 / 标记改名 / 脚本被截断 —— 一律不得算绿，R247）
聚合：任一 FAIL 或 UNVERIFIED ⇒ exit 1；门脚本本身缺失 ⇒ exit 2（禁「跑不到就算过」）。

用法：
    python 05-exec/run_gates.py                    # 本机全跑（含依赖绝对路径的门）
    python 05-exec/run_gates.py --portable-only    # 只跑跨机可复现子集（CI 用），其余显式记 SKIPPED
    python 05-exec/run_gates.py --json 06-benchmark/gate_run_r31.json
退出码：0 全绿 / 1 有 FAIL 或 UNVERIFIED / 2 门脚本缺失或环境不满足
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
# r32：执行台账。每跑一次 runner 追加一行（origin 区分本机/CI）。
# 台账随仓提交 ⇒ CI 能反过来判「本机专属门还在不在被人跑」；这是本仓与对手 CI 的用法差：
# 对手的 CI 判代码，我们额外用 CI 盯「人有没有停跑」（依据见 06-benchmark/ci_health_r32_*.json）。
LEDGER = os.path.join(REPO, "06-benchmark", "gate_runs.jsonl")
ORIGIN = "ci" if os.environ.get("GITHUB_ACTIONS") == "true" else "local"

# 单一真相源：门禁清单只在这里维护。AGENTS.md / CI / 会话内手工跑，都走本表。
GATES = [
    {
        "id": "r19_scan_fixtures",
        "script": "r19_scan_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": False,
        "not_portable_reason":
            "层b 真机接线 subprocess 调 cumulative_drift_scan.py / description_baseline_scan.py / "
            "claim_truth_scan.py，三者读 D:\\global_skills ∪ 焚诀 ∪ D:\\global_memory"
            "（r31 静态实测：各含 1-2 处本机绝对根）⇒ 离机必红，刻意不入 CI",
        "covers": ["05-exec/cumulative_drift_scan.py 排除判据", "05-exec/skill_structure_rubric_scan.py 口径",
                   "05-exec/description_baseline_scan.py PROCESS_RE", "05-exec/_lib.py denominator()"],
        "why": "判据可信度：已知答案 36 例 + 真机接线 19 例",
    },
    {
        "id": "r19_baseline_contract_fixtures",
        "script": "r19_baseline_contract_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["05-exec/baseline_contract_scan.py", "05-exec/schemas/r19/baseline-contracts.json"],
        "why": "契约校验器自身的夹具（含 r31 授权代际列表 t11/t12）",
    },
    {
        "id": "baseline_contract_scan",
        "script": "baseline_contract_scan.py",
        "argv": ["--quiet"],
        "pass_token": "[CONTRACT:PASS]",
        "portable": True,
        "covers": ["06-benchmark/*.json 机器证据结构（份数/pattern 数不硬编码，取值：该门 --json 输出的 files_checked 与 artifacts 长度）"],
        "why": "产物 schema/必填/类型/不变式事前拒收",
    },
    {
        "id": "ratchet_gate",
        "script": "ratchet_gate.py",
        "argv": [],
        "pass_token": "[RATCHET:PASS]",
        "portable": False,
        "not_portable_reason": "取值需读 焚诀 eval/truth_constants.json 与 D:\\global_skills 实测字节，跨机不可复现",
        "covers": ["06-benchmark/inject_ratchet_baseline.json", "D:\\global_skills 注入面", "焚诀 truth_constants"],
        "why": "注入面/度量六项只降不升棘轮（r34 加第 6 项 username_in_skill_files）",
    },
    {
        "id": "control_char_scan",
        "script": "control_char_scan.py",
        "argv": ["."],
        "pass_token": "[CTRL:CLEAN]",
        "portable": True,
        "covers": ["本仓全部文本面（r31 实测 376 个面）"],
        "why": "拦「肉眼看不见、但让引用检索不到」的 C0 ∪ DEL",
    },
    {
        # r35 H-1：把 r34「我自己把 AGENTS.md 写成 0 字节」那次事故的**自觉型规则**升级成机器型
        "id": "tracked_empty_check",
        "script": "r35_tracked_empty.py",
        "argv": [],
        "pass_token": "[EMPTY:PASS]",
        "portable": True,
        "covers": ["本仓全部 tracked 文本件（.md/.py/.json/.jsonl/.yml/.txt/.ps1/.sh/.toml 等）",
                   "二进制/未知扩展跳过但如实计数，不静默当通过"],
        "why": "拦「写崩/截断留下的 0 字节件」——r34 我曾把 memory/AGENTS.md 写成 0 字节，靠 Git 基线才恢复",
    },
    {
        # r39 W-3：债务趋势台账的 fail-closed 夹具（拒写脏行 + 延期不得冒充已裁决）
        "id": "debt_ledger_fixtures",
        "script": "r39_debt_ledger_fixtures.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": True,
        "covers": ["05-exec/r38_debt_aging.py 的 append_ledger 与 classify_item",
                   "05-exec/schemas/r19/baseline-contracts.json 的 debt_runs.jsonl 行契约"],
        "why": "锁死三件：脏测量值不得进趋势线；挂账到期必须回判 OVERDUE；origin 取值域封闭 local/ci",
    },
    {
        # r37 H-4：把「判据自己会不会报错」变成常驻门（本轮实测：噪声门连红 7 轮全是假阳性）
        "id": "noise_tracked_stub",
        "script": "r37_noise_tracked_stub.py",
        "argv": [],
        "pass_token": "[GATE:fixture-pass]",
        "portable": False,
        "not_portable_reason":
            "层a 需在 %TEMP% 建真实 git 仓并 git commit（要 git 身份），层b 断言两个真实受管根"
            "（焚诀 / global_memory）的已知假阳性必须清零 —— 换机无这两根即无意义",
        "covers": ["D:\\global_skills\\A-project-handoff\\scripts\\noise_lint.py",
                   "受管根 strict allowlist 放行面", "二级深扫 .git 例外"],
        "why": "锁死「已跟踪根部文件不误判 + .git 运行态不深扫 + 放行面不外溢」三件，"
               "防任何一次再为凑绿而放宽判据（R263/R220）",
    },
    {
        # r32 H-2：本仓独有一门 —— 用台账反证「本机专属门还在被跑」。CI 里也能跑（读已提交台账）。
        "id": "gate_run_freshness",
        "script": "r32_gate_freshness.py",
        "argv": [],
        "pass_token": "[FRESH:PASS]",
        "portable": True,
        "covers": ["06-benchmark/gate_runs.jsonl 执行台账",
                   "间接盯住 ratchet_gate / r19_scan_fixtures 两台机专属门是否仍被人跑"],
        "why": "防判据僵尸化（对手实测：spec-kit 50% run 停在 action_required，从未产生判定）",
        "meta": True,   # 元判据：它评的是「台账本身」，不得把它的红写进台账 verdict（否则一次引导期红会永久自锁，r32 实测）
    },
]

# 显式声明本 runner **不覆盖**的面，防止聚合绿被读成「所有门禁都绿」（R20-2）。
NOT_COVERED = [
    "受管根四门禁 mirror/noise/evolution/stub —— 属 rule_editor 面，取值："
    "python D:\\global_skills\\A-memory-start\\references\\rule_editor.py gates",
    "焚诀跨产物真值 C1~C33 —— 取值：python 焚诀\\eval\\verify_truth_consistency.py",
    "判据变异测试（r19_fixture_mutation_check.py）—— 按需跑，非每轮前置",
]


def run_gate(gate, timeout):
    """执行单门，返回 (state, rc, elapsed_ms, tail)。脚本缺失 ⇒ ('MISSING', ...)。"""
    path = os.path.join(HERE, gate["script"])
    if not os.path.exists(path):
        return "MISSING", 2, 0, "脚本不存在: %s" % path
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, path] + list(gate["argv"]),
                           cwd=REPO, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return "FAIL", 124, int((time.time() - t0) * 1000), "TIMEOUT after %ss" % timeout
    elapsed = int((time.time() - t0) * 1000)
    out = (p.stdout or "") + (p.stderr or "")
    if p.returncode == 2:
        state = "UNVERIFIED"          # 门自报「取不到真相源/台账不可判」⇒ 同样不得算绿（R247）
    elif p.returncode != 0:
        state = "FAIL"
    elif gate["pass_token"] not in out:
        state = "UNVERIFIED"          # rc=0 但标记不见 = 静默跳过，不得算绿
    else:
        state = "PASS"
    tail = " | ".join(l for l in out.strip().splitlines() if l.strip())[-200:]
    return state, p.returncode, elapsed, tail


def aggregate(results):
    """聚合判据。⛔ 禁止 any()/all() 掩盖单门状态（本仓 audit-runner-safe-aggregate 教训）：
    必须逐门取状态后按状态集合判定，且非零门须能被点名。"""
    states = [r["state"] for r in results]
    n_pass, n_fail = states.count("PASS"), states.count("FAIL")
    n_unv, n_miss = states.count("UNVERIFIED"), states.count("MISSING")
    if n_miss:
        return 2, "MISSING=%d" % n_miss
    bad = n_fail + n_unv
    if bad:
        return 1, "FAIL=%d UNVERIFIED=%d" % (n_fail, n_unv)
    return 0, "PASS=%d（无 FAIL / 无 UNVERIFIED / 无 MISSING）" % n_pass


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--portable-only", action="store_true", help="只跑跨机可复现子集（CI 用）")
    ap.add_argument("--gate", action="append", default=[], help="只跑指定门 id（可重复）")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--json")
    ap.add_argument("--no-ledger", action="store_true",
                    help="不追加执行台账（只读试跑用；默认追加，供 gate_run_freshness 判新鲜度）")
    args = ap.parse_args()

    rows = []
    total_ms = 0
    print("=== 本仓门禁聚合 runner (%s) ===" % datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("工作根: %s" % REPO)
    for g in GATES:
        if args.gate and g["id"] not in args.gate:
            continue
        if args.portable_only and not g["portable"]:
            print("%-32s SKIPPED-BY-DESIGN  %s" % (g["id"], g.get("not_portable_reason", "未声明原因")))
            rows.append({"id": g["id"], "state": "SKIPPED", "rc": None, "elapsed_ms": 0,
                         "portable": False, "covers": g["covers"]})
            continue
        state, rc, ms, tail = run_gate(g, args.timeout)
        total_ms += ms
        print("%-32s %-11s rc=%-4s %5dms  %s" % (g["id"], state, rc, ms, g["why"]))
        print("      覆盖根: %s" % " ; ".join(g["covers"]))
        if state != "PASS":
            print("      末输出: %s" % tail)
        rows.append({"id": g["id"], "state": state, "rc": rc, "elapsed_ms": ms,
                     "portable": g["portable"], "covers": g["covers"], "tail": tail})

    if not rows:
        print("[GATES:UNVERIFIED] 选中的门为 0 个，禁止判「全绿」（R247）")
        return 2

    rc, why = aggregate(rows)
    n = len([r for r in rows if r["state"] != "SKIPPED"])
    if not args.no_ledger:
        # 台账只记事实，不记推测；git 取不到就写 None（不得因为取不到就跳过整行 —— 那会伪造连续性）
        head = None
        try:
            h = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"],
                               capture_output=True, text=True, timeout=20)
            head = h.stdout.strip() or None
        except Exception:
            head = None
        # 台账的 `verdict` 只记**实质门**（排除 meta=True 的新鲜度门）：
        # 新鲜度门评的是台账自己，若把它的引导期红写进 verdict，就会出现
        # 「一次空台账 ⇒ 永久 FAIL」的自锁（r32 实测复现过）。`overall` 仍如实记全量结论供审计。
        meta_ids = {g["id"] for g in GATES if g.get("meta")}
        rc_sub, why_sub = aggregate([r for r in rows if r["id"] not in meta_ids])
        entry = {"ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "origin": ORIGIN,
                 "verdict": "PASS" if rc_sub == 0 else ("FAIL" if rc_sub == 1 else "MISSING"),
                 "verdict_reason": why_sub,
                 "overall": "PASS" if rc == 0 else ("FAIL" if rc == 1 else "MISSING"),
                 "mode": "portable-only" if args.portable_only else "full",
                 "gates_run": n, "skipped": len(rows) - n, "total_ms": total_ms,
                 "head": head, "per_gate": {r["id"]: r["state"] for r in rows}}
        try:
            with open(LEDGER, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as e:
            print("⚠️ 台账写入失败（不影响本轮判定，但会让 gate_run_freshness 下一轮报 UNVERIFIED）: %s" % e)
    print("-" * 72)
    print("执行 %d 门 / 跳过 %d 门 / 合计耗时 %d ms（均值 %d ms/门）"
          % (n, len([r for r in rows if r["state"] == "SKIPPED"]), total_ms,
             int(total_ms / n) if n else 0))
    print("本 runner 不覆盖（聚合绿不等于这些也绿）：")
    for s in NOT_COVERED:
        print("  · %s" % s)
    if rc == 0:
        print("[GATES:PASS] %s" % why)
    elif rc == 1:
        print("[GATES:FAIL] %s" % why)
    else:
        print("[GATES:MISSING] %s" % why)

    if args.json:
        doc = {"schema": "gate-run-v1", "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
               "readonly": True, "mode": "portable-only" if args.portable_only else "full",
               "gates": rows, "not_covered": NOT_COVERED,
               "verdict": "PASS" if rc == 0 else ("FAIL" if rc == 1 else "MISSING"),
               "verdict_reason": why, "total_ms": total_ms, "gates_run": n}
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.json)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
