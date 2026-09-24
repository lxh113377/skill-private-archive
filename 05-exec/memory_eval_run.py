# -*- coding: utf-8 -*-
"""memory_eval_run.py — P1-2 交接记忆评测 runner（确定性，零 LLM）。

用法：
    python memory_eval_run.py --project <项目根> [--scenarios <场景集.json>] [--md <报告.md>]

判据：场景 check.pattern 在目标节文件（主卷 + partN 分卷 + memory/AGENTS.md）中
      regex 命中 = recall 成功。陷阱题同判据（正则本身编码了「应答形态」）。
退出码：0 = 全过；1 = 有 FAIL。
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

SECTION_FILES = {
    "01": ["01-goal.md"],
    "02": ["02-structure.md"],
    "03": ["03-tech-stack.md"],
    "04": ["04-file-map.md"],
    "05": ["05-feature-status.md", "05-feature-status.part*.md"],
    "06": ["06-constraints.md", "06-constraints.part*.md"],
    "07": ["07-next-steps.md", "07-next-steps.part*.md"],
    "08": ["08-ac-obs.md"],
    "09": ["09-workflow-state.md"],
}


def section_targets(mem_dir, section):
    pats = SECTION_FILES.get(section, [])
    files = []
    for p in pats:
        if "*" in p:
            files.extend(sorted(mem_dir.glob(p)))
        else:
            f = mem_dir / p
            if f.exists():
                files.append(f)
    # AGENTS.md（P-1 绑定表）属于记忆体系一部分，参与召回面
    ag = mem_dir / "AGENTS.md"
    if ag.exists():
        files.append(ag)
    return files


def run(project, scenario_path):
    mem_dir = Path(project).resolve() / "memory"
    if not mem_dir.exists():
        raise SystemExit("🔴 memory/ 不存在: {0}".format(mem_dir))
    spec = json.loads(Path(scenario_path).read_text(encoding="utf-8"))
    results = []
    for sc in spec["scenarios"]:
        files = section_targets(mem_dir, sc["section"])
        pat = re.compile(sc["check"]["pattern"],
                         re.IGNORECASE if "i" in sc["check"].get("flags", "") else 0)
        hit_file = None
        for f in files:
            try:
                if pat.search(f.read_text(encoding="utf-8", errors="replace")):
                    hit_file = f.name
                    break
            except OSError:
                continue
        results.append({
            "id": sc["id"], "section": sc["section"],
            "kind": sc.get("kind", "normal"),
            "question": sc["question"],
            "hit_file": hit_file,
            "pass": hit_file is not None,
        })
    return results


def main():
    ap = argparse.ArgumentParser(description="交接记忆评测 runner（确定性）")
    ap.add_argument("project", help="项目根路径")
    ap.add_argument("--scenarios", default=str(Path(__file__).resolve().parent.parent
                                               / "06-benchmark" / "memory_eval_scenarios_v1.json"))
    ap.add_argument("--md", help="基线报告输出路径")
    args = ap.parse_args()

    results = run(args.project, args.scenarios)
    n_pass = sum(1 for r in results if r["pass"])
    total = len(results)

    # V3.52.1 review 接入：结果落盘 memory/sessions/memory-eval.jsonl（append-only，last wins）
    try:
        rec_dir = Path(args.project).resolve() / "memory" / "sessions"
        rec_dir.mkdir(parents=True, exist_ok=True)
        rec = {"ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               "total": total, "passed": n_pass,
               "scenario_file": str(Path(args.scenarios).resolve())}
        with open(rec_dir / "memory-eval.jsonl", "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError as e:
        print("⚠️ memory-eval.jsonl 落盘失败（不影响评测）: {0}".format(e))

    print("=== 交接记忆评测（{0}） ===".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
    for r in results:
        print("  {0} {1} [{2}节{3}] {4}  → {5}".format(
            "✅" if r["pass"] else "❌", r["id"], r["section"],
            "·陷阱" if r["kind"] == "trap" else "",
            r["question"][:38], r["hit_file"] or "MISS"))
    print("📊 [MEMORY-EVAL: {0}/{1} recall]".format(n_pass, total))
    print("   判据 = 正则确定性命中（零 LLM）；语义级 recall 为后续增补项")
    if args.md:
        lines = [
            "# P1-2 交接记忆评测基线（v1）",
            "",
            "> 生成：{0} ｜ 项目：`{1}` ｜ 场景集：`06-benchmark/memory_eval_scenarios_v1.json`（{2} 场景）".format(
                datetime.now().strftime("%Y-%m-%d %H:%M"), Path(args.project).resolve(), total),
            "> 判据：正则确定性命中（零 LLM）；召回面 = 目标节主卷 + partN 分卷 + memory/AGENTS.md。",
            "",
            "| id | 节 | 类型 | 结果 | 命中文件 | 问题 |",
            "|---|---|---|---|---|---|",
        ]
        for r in results:
            lines.append("| {0} | {1} | {2} | {3} | {4} | {5} |".format(
                r["id"], r["section"], r["kind"], "✅" if r["pass"] else "❌",
                r["hit_file"] or "MISS", r["question"].replace("|", "\\|")[:44]))
        lines += ["", "**基线分：{0}/{1} recall（{2:.0f}%）**".format(
            n_pass, total, n_pass / total * 100), "",
            "## 后续", "",
            "- review 报告接入（handoff.py review 读取评测行）与 LLM 语义级场景为增补项；",
            "- FAIL 项 = 记忆盲区候选：先核「内容缺失」还是「措辞漂移」，再补场景或补内容。",
        ]
        Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("MD -> {0}".format(args.md))
    raise SystemExit(0 if n_pass == total else 1)


if __name__ == "__main__":
    main()
