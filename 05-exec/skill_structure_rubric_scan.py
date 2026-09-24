# -*- coding: utf-8 -*-
"""skill_structure_rubric_scan.py - r18 P1: six-section skill anatomy coverage baseline.

Benchmark source: addyosmani/agent-skills (98.8k stars) fixed SKILL.md anatomy -
  Frontmatter / Overview / When to Use / Process / Rationalizations / Red Flags / Verification
with three stated design choices we currently do not machine-check:
  * "Process, not prose"  - steps + checkpoints + exit criteria, not reference text
  * "Anti-rationalization" - a table of excuses agents use to skip steps
  * "Verification is non-negotiable" - every skill ends with evidence requirements

Companion to `description_baseline_scan.py` (r17 P1-1), which only audits the
frontmatter description. This audits the *body*.

Read-only. Denominator reconciliation is explicit: registry count vs glob count vs
junction-skipped count are all printed, so the 151/166/167 口径 drift cannot silently recur.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import _lib
except Exception:
    _lib = None

GS_ROOT = Path(r"D:\global_skills")

RUBRIC = {
    "overview": [r"##?\s*(概述|简介|定位|是什么|核心逻辑|概览|Overview|What|Why|一句话|项目目标)"],
    "when_to_use": [r"##?\s*(何时使用|何时触发|触发(条件|词|时机)|适用(场景|范围)?|使用场景|边界|范围|When to|Use when|Use this|触发)"],
    "process": [r"##?\s*(流程|步骤|做法|执行|工作流|怎么用|使用方法|标准流程|核心流程|Process|Workflow|Steps|Usage|快速开始|Quick ?Start|用法)"],
    "rationalizations": [r"(理性化|借口|自我说服|偷懒|跳过.{0,6}的(?:借口|理由)|常见托词|Rationali[sz]ation|Anti-Pattern|反模式|不要做的理由)"],
    "red_flags": [r"(危险信号|警示|红线|雷区|踩坑|易错|常见错误|失败模式|注意|禁止事项|警告|Red Flag|Gotcha|Pitfall|Warning|禁)"],
    "verification": [r"(验证|验收|证据|判据|核验|检查清单|退出条件|Verification|Acceptance|Definition of Done|Checklist|门禁|实测)"],
}
RUBRIC_RX = {k: [re.compile(p, re.IGNORECASE) for p in v] for k, v in RUBRIC.items()}
STEPISH = re.compile(r"(?:^|\n)\s*(?:\d+[.、)]|[①-⑳]|第[一二三四五六七八九十0-9]+步|#{2,3}\s*Step)", re.M)


def is_reparse_dir(p):
    try:
        return p.stat(follow_symlinks=False).st_file_attributes & 0x400 != 0
    except (OSError, AttributeError):
        return False


def scan():
    rows, skipped_junction, errors = [], [], []
    for md in sorted(GS_ROOT.glob("*/SKILL.md")):
        name = md.parent.name
        if is_reparse_dir(md.parent):
            skipped_junction.append(name)
            continue
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            errors.append({"skill": name, "error": str(e)})
            continue
        body = text.split("---", 2)[-1] if text.startswith("---") else text
        hit = {k: any(rx.search(body) for rx in rxs) for k, rxs in RUBRIC_RX.items()}
        hit["has_stepish_list"] = bool(STEPISH.search(body))
        rows.append({"skill": name, "bytes": len(text.encode("utf-8")), "sections": hit,
                     "covered": sum(1 for v in hit.values() if v)})
    return rows, skipped_junction, errors


def main():
    if _lib is not None:
        _lib.force_utf8_stdout()
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--md")
    ap.add_argument("--worst", type=int, default=15)
    args = ap.parse_args()

    rows, junctions, errors = scan()
    n = len(rows)
    if n == 0:
        print("FAIL(R247): 枚举到 0 个 SKILL.md，禁止据此下任何覆盖率结论")
        return 1
    per_sec = {k: sum(1 for r in rows if r["sections"][k]) for k in RUBRIC}
    full6 = sum(1 for r in rows if all(r["sections"][k] for k in RUBRIC))
    glob_total = n + len(junctions)

    print("=== 技能六段解剖覆盖率基线 (%s, 对标 addyosmani/agent-skills) ===" % datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("口径对账: 磁盘 glob = %d (本次纳入 %d + junction 跳过 %d: %s) | 解析错误 %d" % (
        glob_total, n, len(junctions), ",".join(junctions) or "-", len(errors))
    )
    print("焚诀注册表口径(取值命令 `python 焚诀/eval/verify_truth_consistency.py` C1 行)须与本表对账后方可引用为分母")
    if _lib is not None:
        for ln in _lib.denominator_lines(_lib.denominator(n, junctions, errors, glob_total=glob_total)):
            print(ln)
    else:
        print("口径对账: _lib 不可用 → 本表分母仅磁盘 glob")
    print()
    print("%-18s %6s %8s" % ("段落", "命中", "占比"))
    for k in RUBRIC:
        print("%-18s %6d %7.1f%%" % (k, per_sec[k], 100.0 * per_sec[k] / n))
    print("%-18s %6d %7.1f%%" % ("六段全含", full6, 100.0 * full6 / n))
    print()
    print("最薄弱段(对标项): rationalizations=%d (%.1f%%) / red_flags=%d (%.1f%%)" % (
        per_sec["rationalizations"], 100.0 * per_sec["rationalizations"] / n,
        per_sec["red_flags"], 100.0 * per_sec["red_flags"] / n))
    worst = sorted(rows, key=lambda r: (r["covered"], -r["bytes"]))[: args.worst]
    print("\n覆盖最少 top %d:" % args.worst)
    for r in worst:
        miss = [k for k in RUBRIC if not r["sections"][k]]
        print("  %-32s %d/6  缺: %s" % (r["skill"], r["covered"], ",".join(miss)))

    result = {
        "schema": "skill-structure-rubric-v1",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "readonly": True,
        "benchmark": "addyosmani/agent-skills six-section anatomy",
        "denominator": {"glob_total": glob_total, "scanned": n, "junction_skipped": junctions, "errors": errors},
        "rubric": list(RUBRIC.keys()),
        "per_section": {k: {"count": per_sec[k], "pct": round(100.0 * per_sec[k] / n, 1)} for k in RUBRIC},
        "all_six": {"count": full6, "pct": round(100.0 * full6 / n, 1)},
        "per_skill": rows,
        "caveat": "keyword-anchor detection, not semantic; anchor absent != section absent (false negatives possible)",
    }
    if args.json:
        Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print("\nJSON -> %s" % args.json)
    if args.md:
        md = ["# 技能六段解剖覆盖率基线 (%s)" % result["generated_at"], "",
              "> 对标 addyosmani/agent-skills（98.8k 星标）固定解剖：Overview / When to Use / Process /",
              "> Rationalizations / Red Flags / Verification。三条设计主张：Process not prose、",
              "> 反理性化表不可省、Verification 证据要求不可省。", "",
              "## 口径对账（防 151/166/167 分母漂移复发）", "",
              "| 项 | 值 |", "|---|---|",
              "| 磁盘 glob 命中 | %d |" % glob_total,
              "| 本次纳入 | %d |" % n,
              "| junction 跳过 | %d (%s) |" % (len(junctions), ", ".join(junctions) or "-"),
              "| 解析错误 | %d |" % len(errors), "",
              "## 段落覆盖", "", "| 段落 | 对标含义 | 命中 | 占比 |", "|---|---|---|---|"]
        gloss = {"overview": "做什么", "when_to_use": "何时用/触发", "process": "步骤化流程",
                 "rationalizations": "反理性化(借口+反驳)", "red_flags": "危险信号", "verification": "验证/证据要求"}
        md += ["| %s | %s | %d | %.1f%% |" % (k, gloss[k], per_sec[k], 100.0 * per_sec[k] / n) for k in RUBRIC]
        md += ["| 六段全含 | - | %d | %.1f%% |" % (full6, 100.0 * full6 / n), "",
               "判据性质：关键词锚点检测，非语义判定；锚点缺失 != 段落缺失（存在假阴性）。", ""]
        Path(args.md).write_text("\n".join(md) + "\n", encoding="utf-8")
        print("MD   -> %s" % args.md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
