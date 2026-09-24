# -*- coding: utf-8 -*-
"""cumulative_drift_scan.py - r18 P1: cumulative semantic-drift risk scanner (read-only).

Benchmark source: mycelium-hq/ai-brain-starter `scripts/drift-detection.py`, which flags
files edited >= 5 times in 30 days as candidates for human review, citing Microsoft
DELEGATE-52 (frontier LLMs corrupt ~25% of professional content over 20 edits).

Our existing drift machinery (`handoff.py` R272 `_memory_volume_drift()`) checks
*structural* drift (main volume vs sub-volumes). Nothing checks *edit-frequency*
accumulation, which is the class that silently rewrites rule meaning over weeks.

Output: per-file commit counts over a window, plus a flagged list = candidates for
human re-read. Not a verdict. R247 guard: total commits per root must be > 0.

r19 D4 校准（对标 drift-detection.py 实物后修的三处自有判据缺陷）：
  1. 按设计累积项排除（N-E 用 SKIP_PREFIXES 达成同一目的）：`*.partN.md`（R199 自动拆卷）、
     日期命名日志、`sessions/`、`_trash/`、`archive/`、`.bak`、含「自动生成」标记的注入壳。
     r18 基线 16 条候选里有 3 条属此类（07 part5/part8 + 本仓自动生成 AGENTS.md）= 19% 噪声。
     排除**必须可见**： excluded 清单入 JSON，`--show-excluded` 打印，`--no-exclude` 复现旧口径。
  2. RULEISH 此前按子串匹配，`eval/decay_lessons.py` 等**代码文件**因含 "lessons" 被误判为规则类；
     现要求 `.md` 后缀。
  3. `.driftignore`（N-E 同名机制）：`--driftignore <path>` 或仓库根 `.driftignore`，逐行子串匹配。
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import _lib
except Exception:
    _lib = None

ROOTS = {
    "global_skills": Path(r"D:\global_skills"),
    "global_memory": Path(r"D:\global_memory"),
    "fenjue": Path(r"C:\Users\37533\Desktop\workspace\焚诀"),
    "self": Path(r"C:\Users\37533\Desktop\workspace\自建skill优化"),
}
RULEISH = re.compile(r"(SKILL\.md$|AGENTS\.md$|behavior_core|BOOTSTRAP|contract|MEMORY\.md$|lessons|prompts/|07-next-steps|06-constraints)")
THRESHOLD = 5
BY_DESIGN = re.compile(
    r"(\.part\d+\.md$|(^|/)\d{4}-\d{2}-\d{2}(-\d{1,4})?\.md$|(^|/)sessions?/|(^|/)_trash/|"
    r"(^|/)archive/|\.bak$|\.tmp$|(^|/)node_modules/)")
GENERATED_MARKER = "自动生成"


def is_by_design(path, root):
    """按设计累积/机器生成的项——它们改写次数高但不承载「规则语义」，纳入只会稀释信号。"""
    if BY_DESIGN.search(path):
        return True
    fp = root / path
    if fp.suffix.lower() == ".md" and fp.is_file():
        try:
            head = fp.read_text(encoding="utf-8", errors="replace")[:400]
        except OSError:
            return False
        return GENERATED_MARKER in head
    return False


def is_ruleish(path):
    return path.lower().endswith(".md") and bool(RULEISH.search(path))


def load_driftignore(path):
    """.driftignore：逐行子串匹配（对齐 N-E 语义）；# 注释与空行跳过。"""
    pats = []
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return pats
    for line in text.splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            pats.append(s)
    return pats


def matches_ignore(path, pats):
    return next((p for p in pats if p in path), None)


def git(root, args):
    cmd = ["git", "-c", "core.quotepath=false", "-C", str(root)] + args
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    except (subprocess.TimeoutExpired, OSError) as e:
        return None, str(e)
    if p.returncode != 0:
        return None, (p.stderr or p.stdout or "").strip()[:300]
    return p.stdout, None


def scan_root(root, days):
    out, err = git(root, ["rev-parse", "--is-inside-work-tree"])
    if err or (out or "").strip() != "true":
        return None, "not-a-git-repo (%s)" % (err or "no")
    out, err = git(root, ["log", "--since=%d days ago" % days, "--name-only", "--pretty=format:%H"])
    if err:
        return None, err
    counts = {}
    shas = set()
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.fullmatch(r"[0-9a-f]{7,40}", line):
            shas.add(line)
            continue
        counts[line] = counts.get(line, 0) + 1
    return {"commits": len(shas), "counts": counts}, None


def main():
    if _lib is not None:
        _lib.force_utf8_stdout()
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--threshold", type=int, default=THRESHOLD)
    ap.add_argument("--json")
    ap.add_argument("--md")
    ap.add_argument("--no-exclude", action="store_true",
                    help="关闭按设计累积项排除（复现 r18 旧口径，作对照组）")
    ap.add_argument("--show-excluded", action="store_true", help="打印被排除项清单")
    ap.add_argument("--driftignore", help="额外 .driftignore 文件路径（逐行子串匹配）")
    args = ap.parse_args()

    per_root, flagged, excluded = {}, [], []
    for name, root in ROOTS.items():
        data, err = scan_root(root, args.days)
        if err:
            per_root[name] = {"error": err}
            print("%-14s SKIP: %s" % (name, err))
            continue
        ig = load_driftignore(root / ".driftignore")
        if args.driftignore:
            ig += load_driftignore(args.driftignore)
        rows = []
        for path, edits in sorted(data["counts"].items(), key=lambda kv: -kv[1]):
            if edits < args.threshold:
                continue
            if matches_ignore(path, ig):
                excluded.append({"root": name, "path": path, "edits": edits,
                                 "why": "driftignore"})
                continue
            if not args.no_exclude and is_by_design(path, root):
                excluded.append({"root": name, "path": path, "edits": edits,
                                 "why": "by-design（自动拆卷/日志/生成壳/归档）"})
                continue
            fp = root / path
            rows.append({
                "path": path, "edits": edits,
                "bytes": fp.stat().st_size if fp.exists() else None,
                "exists": fp.exists(),
                "ruleish": is_ruleish(path),
            })
        top = sorted(data["counts"].items(), key=lambda kv: -kv[1])[:5]
        per_root[name] = {"commits": data["commits"], "files_touched": len(data["counts"]),
                          "top5": top, "flagged": rows,
                          "driftignore_patterns": len(ig)}
        for r in rows:
            r2 = dict(r)
            r2["root"] = name
            flagged.append(r2)
        print("%-14s commits=%-5d files=%-6d >=%d edits: %d (rule-ish %d, excluded %d)" % (
            name, data["commits"], len(data["counts"]), args.threshold, len(rows),
            sum(1 for r in rows if r["ruleish"]),
            sum(1 for e in excluded if e["root"] == name)))

    total_commits = sum(v.get("commits", 0) for v in per_root.values())
    ok = total_commits > 0
    flagged.sort(key=lambda r: (not r["ruleish"], -r["edits"]))
    print("\n输入非空校验: %s (四根合计提交 %d 条, 窗口 %d 天)" % ("PASS" if ok else "FAIL(R247)", total_commits, args.days))
    print("排除面（可见，不静默）: %d 条%s" % (len(excluded), "；当前为对照组=未排除" if args.no_exclude else ""))
    if args.show_excluded:
        for e in excluded:
            print("  [EXCL] %-14s %-4d次  %-38s %s" % (e["root"], e["edits"], e["why"], e["path"][:60]))
    print("=== 累积漂移候选 (对标 drift-detection.py, 阈值 >=%d 次/%d 天) ===" % (args.threshold, args.days))
    print("规则/技能类优先复核 (%d 条):" % sum(1 for r in flagged if r["ruleish"]))
    for r in flagged:
        if r["ruleish"]:
            print("  %-14s %-4d次  %-6s  %s" % (r["root"], r["edits"], ("%dB" % r["bytes"]) if r["bytes"] else "缺失", r["path"][:78]))
    print("\n复核结论用 N-E 六态判据（禁只写「已看过」）: "
          "drift_detected / softened(守卫被放松) / refinement / additive / neutral_rephrase / uncertain")

    result = {
        "schema": "cumulative-drift-scan-v2",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "readonly": True,
        "window_days": args.days,
        "threshold": args.threshold,
        "exclusions_enabled": not args.no_exclude,
        "verdict_taxonomy": ["drift_detected", "softened", "refinement", "additive",
                             "neutral_rephrase", "uncertain"],
        "evidence": {"total_commits": total_commits, "roots": {k: {kk: vv for kk, vv in v.items() if kk != "flagged"} for k, v in per_root.items()}},
        "flagged_ruleish": [r for r in flagged if r["ruleish"]],
        "flagged_all": flagged,
        "excluded": excluded,
        "note": "candidates for human re-read, not defects; DELEGATE-52 rationale: ~25% content corruption over 20 LLM edits",
    }
    if args.json:
        Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print("\nJSON -> %s" % args.json)
    if args.md:
        md = ["# 累积语义漂移扫描基线 (%s)" % result["generated_at"], "",
              "> 对标 mycelium-hq/ai-brain-starter `scripts/drift-detection.py`（阈值 >=%d 次 / %d 天）。" % (args.threshold, args.days),
              "> 判据依据：Microsoft DELEGATE-52 结论——前沿 LLM 在 20 次改写中约损坏 25% 专业内容。",
              "> 本表是**人工复核候选**，不是缺陷判定；既有 `_memory_volume_drift()` 只查结构漂移，不查改写频次累积。",
              "> v2（r19 D4）：排除按设计累积项（`*.partN.md` 自动拆卷 / 日期日志 / `sessions` / `_trash` / `archive` / 含「自动生成」标记的注入壳）"
              "与 `.driftignore` 命中项；排除清单**在 JSON 内全量留痕**，`--no-exclude` 可复现 v1 旧口径作对照组。",
              "> 复核结论必须落到六态判据之一：`drift_detected` / `softened`（守卫被放松，最危险）/ `refinement` / `additive` / `neutral_rephrase` / `uncertain`。",
              "",
              "| 根 | 窗口内提交 | 触碰文件数 | 超阈值 | 其中规则/技能类 | 排除项 |", "|---|---|---|---|---|---|"]
        for k, v in per_root.items():
            if "error" in v:
                md.append("| %s | SKIP: %s | - | - | - | - |" % (k, v["error"]))
            else:
                md.append("| %s | %d | %d | %d | %d | %d |" % (
                    k, v["commits"], v["files_touched"], len(v["flagged"]),
                    sum(1 for r in v["flagged"] if r["ruleish"]),
                    sum(1 for e in excluded if e["root"] == k)))
        md += ["", "## 规则/技能类超阈值清单（优先复核）", "", "| 根 | 次数 | 现字节 | 路径 |", "|---|---|---|---|"]
        md += ["| %s | %d | %s | `%s` |" % (r["root"], r["edits"], r["bytes"] if r["bytes"] else "缺失", r["path"]) for r in result["flagged_ruleish"]] or ["- 无命中"]
        md += ["", "## 被排除项（按设计累积 / driftignore）", "", "| 根 | 次数 | 原因 | 路径 |", "|---|---|---|---|"]
        md += ["| %s | %d | %s | `%s` |" % (e["root"], e["edits"], e["why"], e["path"]) for e in excluded] or ["- 无"]
        Path(args.md).write_text("\n".join(md) + "\n", encoding="utf-8")
        print("MD   -> %s" % args.md)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
