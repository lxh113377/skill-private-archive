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

# ---- r29 M2: frontmatter-compatible calibre ------------------------------
# r28 declared bias: our skills write "做什么/何时用" into the frontmatter
# description, addyosmani writes them as body headings. A heading-only ruler
# therefore produced systematic false negatives in overview / when_to_use.
# 'body' keeps the r18/r28 calibre untouched; 'both' adds a frontmatter fallback.
FM_RUBRIC_FIELDS = ("description", "when_to_use", "trigger", "triggers", "summary", "purpose")
_FM_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(.*)$")
try:
    from description_baseline_scan import TRIGGER_RE, PROCESS_RE, MIN_DO_LEN
except Exception as exc:  # pragma: no cover
    raise ImportError(
        "frontmatter calibre reuses the r17 description criteria as its single source; "
        "import failed: %r" % (exc,))


def frontmatter_fields(text):
    """Top-level YAML keys of the leading fence as {key: joined_text}.

    Hand-rolled: only needs top-level scalars and block scalars, and pyyaml is
    not guaranteed on every interpreter this tool runs under.
    """
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            end = i
            break
    if end is None:
        return {}
    fields, cur, buf = {}, None, []

    def flush():
        if cur is not None:
            fields[cur] = "\n".join(buf).strip()

    for ln in lines[1:end]:
        m = _FM_KEY.match(ln) if ln[:1] not in (" ", "\t") else None
        if m:
            flush()
            cur = m.group(1)
            v = m.group(2).strip()
            buf = [] if v in ("|", ">", "|-", ">-", "|+", ">+") else [v]
        elif cur is not None:
            buf.append(ln.strip())
    flush()
    return fields


def rubric_hits(text, calibre="both"):
    """Apply RUBRIC_RX at the given calibre. Returns {section: bool}.

    calibre='body' -> heading/body anchors only (the r18/r28 original ruler).
    calibre='both' -> body anchor OR frontmatter anchor (M2 dual calibre). The
      frontmatter side deliberately reuses the r17 description criteria
      (做什么=MIN_DO_LEN, 何时用=TRIGGER_RE, 流程=PROCESS_RE) for the three
      heading-shaped sections, because RUBRIC_RX anchors those with a leading
      '#' and can never match prose. The other three sections keep their own
      keyword anchors, which are already heading-free.
    """
    body = text.split("---", 2)[-1] if text.startswith("---") else text
    out = {}
    if calibre == "body":
        for k, rxs in RUBRIC_RX.items():
            out[k] = any(rx.search(body) for rx in rxs)
        return out
    fields = frontmatter_fields(text)
    desc = (fields.get("description") or "").strip()
    fm_all = "\n".join(v for k, v in fields.items() if k in FM_RUBRIC_FIELDS)
    for k, rxs in RUBRIC_RX.items():
        hit = any(rx.search(body) for rx in rxs)
        if not hit:
            if k == "overview":
                hit = len(desc) >= MIN_DO_LEN
            elif k == "when_to_use":
                hit = bool(TRIGGER_RE.search(fm_all))
            elif k == "process":
                hit = bool(PROCESS_RE.search(fm_all))
            else:
                hit = any(rx.search(fm_all) for rx in rxs)
        out[k] = hit
    return out


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
        hit_both = rubric_hits(text, calibre="both")
        hit["has_stepish_list"] = bool(STEPISH.search(body))
        rows.append({"skill": name, "bytes": len(text.encode("utf-8")), "sections": hit,
                     "sections_both": hit_both,
                     "covered": sum(1 for k in RUBRIC if hit[k]),
                     "has_stepish_list": hit["has_stepish_list"],
                     "covered_both": sum(1 for k in RUBRIC if hit_both[k])})
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
    per_sec_both = {k: sum(1 for r in rows if r["sections_both"][k]) for k in RUBRIC}
    full6 = sum(1 for r in rows if all(r["sections"][k] for k in RUBRIC))
    full6_both = sum(1 for r in rows if all(r["sections_both"][k] for k in RUBRIC))
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
    print("%-16s %8s %9s %10s %9s" % ("段落", "正文口径", "占比", "+frontmatter", "占比"))
    for k in RUBRIC:
        print("%-16s %8d %8.1f%% %10d %8.1f%%" % (
            k, per_sec[k], 100.0 * per_sec[k] / n,
            per_sec_both[k], 100.0 * per_sec_both[k] / n))
    print("%-16s %8d %8.1f%% %10d %8.1f%%" % (
        "六段全含", full6, 100.0 * full6 / n, full6_both, 100.0 * full6_both / n))
    print("口径说明：正文口径=r18/r28 原尺（只认标题锚点）；+frontmatter=宽口径，"
          "overview/when_to_use/process 复用 r17 description 判据，禁与正文口径混列")
    print()
    print("最薄弱段(对标项): rationalizations=%d (%.1f%%) / red_flags=%d (%.1f%%)" % (
        per_sec["rationalizations"], 100.0 * per_sec["rationalizations"] / n,
        per_sec["red_flags"], 100.0 * per_sec["red_flags"] / n))
    worst = sorted(rows, key=lambda r: (r["covered"], -r["bytes"]))[: args.worst]
    print("\n覆盖最少 top %d（正文口径排序，宽口径同列）:" % args.worst)
    for r in worst:
        miss = [k for k in RUBRIC if not r["sections"][k]]
        miss_b = [k for k in RUBRIC if not r["sections_both"][k]]
        print("  %-32s 正文 %d/6 (缺 %s) | 宽口径 %d/6 (缺 %s)" % (
            r["skill"], r["covered"], ",".join(miss) or "-",
            r["covered_both"], ",".join(miss_b) or "-"))

    result = {
        "schema": "skill-structure-rubric-v2",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "readonly": True,
        "benchmark": "addyosmani/agent-skills six-section anatomy",
        "denominator": {"glob_total": glob_total, "scanned": n, "junction_skipped": junctions, "errors": errors},
        "rubric": list(RUBRIC.keys()),
        "per_section": {k: {"count": per_sec[k], "pct": round(100.0 * per_sec[k] / n, 1)} for k in RUBRIC},
        "all_six": {"count": full6, "pct": round(100.0 * full6 / n, 1)},
        "per_section_both": {k: {"count": per_sec_both[k],
                                 "pct": round(100.0 * per_sec_both[k] / n, 1)} for k in RUBRIC},
        "all_six_both": {"count": full6_both, "pct": round(100.0 * full6_both / n, 1)},
        "per_skill": rows,
        "caveat": "keyword-anchor detection, not semantic; anchor absent != section absent (false negatives possible). "
                  "Two calibres: 'sections'/'per_section' = body-heading only (r18/r28 ruler, comparable to a "
                  "heading-based reading of opponents); 'sections_both'/'per_section_both' = M2 wide calibre that also "
                  "credits frontmatter description (reuses r17 criteria: 做什么>=15 chars, 何时用=TRIGGER_RE, 流程=PROCESS_RE). "
                  "Never mix the two in one sentence.",
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
              "## 段落覆盖", "", "| 段落 | 对标含义 | 正文口径命中 | 占比 | 宽口径命中 | 宽口径占比 |",
              "|---|---|---|---|---|---|"]
        gloss = {"overview": "做什么", "when_to_use": "何时用/触发", "process": "步骤化流程",
                 "rationalizations": "反理性化(借口+反驳)", "red_flags": "危险信号", "verification": "验证/证据要求"}
        md += ["| %s | %s | %d | %.1f%% | %d | %.1f%% |" % (
               k, gloss[k], per_sec[k], 100.0 * per_sec[k] / n,
               per_sec_both[k], 100.0 * per_sec_both[k] / n) for k in RUBRIC]
        md += ["| 六段全含 | - | %d | %.1f%% | %d | %.1f%% |" % (
               full6, 100.0 * full6 / n, full6_both, 100.0 * full6_both / n), "",
               "判据性质：关键词锚点检测，非语义判定；锚点缺失 != 段落缺失（存在假阴性）。", "",
               "两列口径不可混用：正文口径 = r18/r28 原尺（只认标题锚点，对把「做什么/何时用」写进 frontmatter 的一方有系统性假阴性）；"
               "宽口径 = r29 M2 新增，frontmatter description 亦可命中（复用 r17 description 判据）。", ""]
        Path(args.md).write_text("\n".join(md) + "\n", encoding="utf-8")
        print("MD   -> %s" % args.md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
