# -*- coding: utf-8 -*-
"""rule_conflict_scan.py - r18 P0: cross-document rule contradiction detector (read-only).

Benchmark source: mycelium-hq/ai-brain-starter `scripts/check-rule-conflicts.py`
(catches `always X` vs `never X` on shared nouns at write time; Engram-inspired).

Two deterministic channels, no LLM, no tokenizer:
  CH1 declared_conflict  - rule files that *admit* an unresolved conflict in their own text
                           (keywords: 不一致 / 口径不一 / 两套 / 待定 / 矛盾 / 冲突 / 未决).
  CH2 polarity_exclusive - a MUST-rule and a FORBID-rule whose object phrases share a
                           contiguous CJK substring >= MIN_TERM chars.

Output is a CANDIDATE list for human adjudication, never an auto-verdict
(over-match is expected and cheap; silent under-report is not).

R247 guard: prints input-non-empty evidence (files / lines / rules per channel) and
refuses to label "0 conflict" when any scanned file is empty or unreadable.
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
except Exception:  # pragma: no cover - fallback keeps the tool standalone
    _lib = None

GS = Path(r"D:\global_skills")
GM = Path(r"D:\global_memory")
PROJ = Path(r"C:\Users\37533\Desktop\workspace\自建skill优化")

DEFAULT_FILES = [
    GM / "core" / "behavior_core.md",
    GM / "core" / "BOOTSTRAP.md",
    GM / "core" / "BOOTSTRAP.part1.md",
    GM / "core" / "BOOTSTRAP.part2.md",
    GM / "prompts" / "workflow_seven_step.md",
    GM / "AGENTS.md",
    GS / "A-memory-start" / "SKILL.md",
    GS / "A-memory-start" / "references" / "contract.md",
    PROJ / "memory" / "AGENTS.md",
    PROJ / "AGENTS.md",
]

POS_RE = re.compile(r"(必须|必做|务必|强制|恒必填|缺一不可|一律|应当|须在|需在|要先)")
NEG_RE = re.compile(r"(禁止|严禁|不得|不可|不要|不允许|不准|勿|禁做|排除在外)")
DECLARED_RE = re.compile(r"(不一致|口径不一|两套|待裁|待定|未决|互相矛盾|自相矛盾|既有冲突|规则冲突)")
SPLIT_RE = re.compile(r"[，。；、：:！？\n|]")
MIN_TERM = 4
MAX_PHRASE = 26


def read(path):
    try:
        t = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return None, str(e)
    return t, None


def phrases(line, rx):
    """Object phrases following each polarity marker."""
    out = []
    for m in rx.finditer(line):
        tail = line[m.end():]
        seg = SPLIT_RE.split(tail)[0].strip()
        seg = re.sub(r"[*_`>#\[\]]", "", seg)[:MAX_PHRASE]
        if len(seg) >= MIN_TERM:
            out.append(seg)
    return out


def longest_common_cjk(a, b, min_len=MIN_TERM):
    ca = re.findall(r"[\u4e00-\u9fff]{1}", a)
    cb = re.findall(r"[\u4e00-\u9fff]{1}", b)
    la, lb = len(ca), len(cb)
    if la == 0 or lb == 0:
        return None
    prev = [0] * (lb + 1)
    best, best_end = 0, 0
    for i in range(1, la + 1):
        cur = [0] * (lb + 1)
        for j in range(1, lb + 1):
            if ca[i - 1] == cb[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best, best_end = cur[j], j
        prev = cur
    if best < min_len:
        return None
    return "".join(cb[best_end - best:best_end])


def scan(files):
    declared, rules, missing, empty = [], [], [], []
    for p in files:
        if not p.exists():
            missing.append(str(p))
            continue
        text, err = read(p)
        if err:
            missing.append("%s (%s)" % (p, err))
            continue
        lines = text.splitlines()
        if not lines or not text.strip():
            empty.append(str(p))
            continue
        for ln, line in enumerate(lines, 1):
            s = line.strip()
            if len(s) < 8 or s.startswith("<!--"):
                continue
            loc = "%s/%s:%d" % (p.parent.name, p.name, ln)
            if DECLARED_RE.search(s):
                declared.append({"loc": loc, "text": s[:200]})
            pos = phrases(s, POS_RE)
            neg = phrases(s, NEG_RE)
            if pos or neg:
                rules.append({"loc": loc, "pos": pos, "neg": neg, "text": s[:160]})
    return declared, rules, missing, empty


def polarity_pairs(rules):
    cands = {}
    n = len(rules)
    for i in range(n):
        ri = rules[i]
        if not ri["pos"]:
            continue
        for j in range(n):
            if j == i:
                continue
            rj = rules[j]
            if not rj["neg"]:
                continue
            for a in ri["pos"]:
                for b in rj["neg"]:
                    term = longest_common_cjk(a, b)
                    if not term:
                        continue
                    key = (term, ri["loc"], rj["loc"])
                    if key not in cands:
                        cands[key] = {
                            "term": term,
                            "must": {"loc": ri["loc"], "phrase": a, "text": ri["text"]},
                            "forbid": {"loc": rj["loc"], "phrase": b, "text": rj["text"]},
                        }
    out = sorted(cands.values(), key=lambda d: (-len(d["term"]), d["term"], d["must"]["loc"]))
    return out


def main():
    if _lib is not None:
        _lib.force_utf8_stdout()
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="full result JSON output path")
    ap.add_argument("--md", help="markdown baseline output path")
    ap.add_argument("--max-pairs", type=int, default=40)
    args = ap.parse_args()

    files = [f for f in DEFAULT_FILES]
    declared, rules, missing, empty = scan(files)
    pairs = polarity_pairs(rules)
    present = len(files) - len(missing)

    result = {
        "schema": "rule-conflict-scan-v1",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "readonly": True,
        "benchmark": "mycelium-hq/ai-brain-starter scripts/check-rule-conflicts.py",
        "input_evidence": {
            "files_listed": len(files),
            "files_present": present,
            "files_missing": missing,
            "files_empty": empty,
            "polarity_rules": len(rules),
            "declared_hits": len(declared),
            "pair_candidates": len(pairs),
        },
        "declared_conflicts": declared,
        "polarity_candidates": pairs[: args.max_pairs],
        "note": "candidates only; adjudication is human (R241 - no rule body deleted to go green)",
    }

    ok_input = present >= 3 and len(rules) >= 20 and not empty
    print("=== 规则冲突扫描 (%s, 对标 ai-brain-starter check-rule-conflicts) ===" % result["generated_at"])
    print("输入证据: 文件 %d/%d 存在, 极性规则 %d 条, 自述冲突 %d 条, 互斥候选 %d 组" % (
        present, len(files), len(rules), len(declared), len(pairs)))
    verdict = "PASS" if ok_input else "FAIL(R247 输入面不足，禁止判 0)"
    print("输入非空校验: %s" % verdict)
    if missing:
        print("缺失文件(不计入判定): %s" % ", ".join("/".join(Path(m).parts[-2:]) for m in missing))
    print()
    print("--- CH1 自述冲突(规则文本自己承认的未决口径) ---")
    for d in declared:
        print("  [%s] %s" % (d["loc"], d["text"][:120]))
    if not declared:
        print("  (无命中 - 需人工复扫确认，不得直接判过)")
    print()
    print("--- CH2 极性互斥候选(共用词 >= %d 字) top %d ---" % (MIN_TERM, min(args.max_pairs, len(pairs))))
    for c in pairs[: args.max_pairs]:
        print("  词[%s]  必须@%s(%s)  vs  禁止@%s(%s)" % (
            c["term"], c["must"]["loc"], c["must"]["phrase"][:14],
            c["forbid"]["loc"], c["forbid"]["phrase"][:14]))
    if not pairs:
        print("  (无命中 - 需人工复扫确认，不得直接判过)")

    if args.json:
        Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print("\nJSON -> %s" % args.json)
    if args.md:
        md = ["# 规则冲突扫描基线 (%s)" % result["generated_at"], "",
              "> 对标 mycelium-hq/ai-brain-starter `scripts/check-rule-conflicts.py`；只读取证，候选非判决。",
              "", "## 输入证据", "",
              "| 项 | 值 |", "|---|---|",
              "| 文件(存在/列出) | %d/%d |" % (present, len(files)),
              "| 极性规则条数 | %d |" % len(rules),
              "| CH1 自述冲突 | %d |" % len(declared),
              "| CH2 互斥候选 | %d |" % len(pairs), "",
              "## CH1 自述冲突", ""]
        md += ["- `%s` %s" % (d["loc"], d["text"]) for d in declared] or ["- 无命中"]
        md += ["", "## CH2 极性互斥候选 (top %d)" % min(args.max_pairs, len(pairs)), "",
               "| 共用词 | 必须侧 | 禁止侧 |", "|---|---|---|"]
        md += ["| %s | `%s` %s | `%s` %s |" % (
            c["term"], c["must"]["loc"], c["must"]["phrase"], c["forbid"]["loc"], c["forbid"]["phrase"])
            for c in pairs[: args.max_pairs]]
        Path(args.md).write_text("\n".join(md) + "\n", encoding="utf-8")
        print("MD   -> %s" % args.md)
    return 0 if ok_input else 1


if __name__ == "__main__":
    raise SystemExit(main())
