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
    Path(r"C:\\Users\\37533\\.qoder-cn") / "agents.md",   # r40 L-4 修：原写 GM/AGENTS.md（实测不存在，死输入面）→ 改指真实在役的 QD 注入壳
    GS / "A-memory-start" / "SKILL.md",
    GS / "A-memory-start" / "references" / "contract.md",
    PROJ / "memory" / "AGENTS.md",
    PROJ / "AGENTS.md",
]

AUTHORITY_DIRS = [GM / "core"]     # 规则分卷的落点：新增分卷由 discover_authority_candidates 自动进面
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


def discover_authority_candidates(dirs=None):
    """**发现**带可配对正负规则的权威源，返回 {Path: (n_pos, n_neg)}。

    存在理由（r50 实测）：`DEFAULT_FILES` 是手抄清单，只 10 件；而 `GM/core/` 实存 25 件，
    其中 17 件带可配对正负规则（`behavior_core_rules_p1..p8` 及其分卷 = 22 锚点规则的正文所在）
    —— 手抄清单永远扫不到后来新增的分卷，冲突判据对它们全盲却照样绿灯（X-24 的第二处实证）。
    发现规则要写死成"形状"（同目录下 *.md 且 pos≥1 且 neg≥1），不得再靠人记得加。
    """
    out = {}
    for d in (dirs or AUTHORITY_DIRS):
        try:
            found = sorted(Path(d).glob("*.md"))
        except OSError:
            continue
        for f in found:
            try:
                t = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            p, n = len(POS_RE.findall(t)), len(NEG_RE.findall(t))
            if p >= 1 and n >= 1:
                out[f.resolve()] = (p, n)
    return out


def face_authority_coverage(listed, candidates):
    """覆盖面自证：带极性规则的权威源若不在扫描面内 ⇒ 判红并点名（返回 (ok, detail)）。"""
    try:
        L = {Path(x).resolve() for x in listed}
        keys = candidates.keys() if isinstance(candidates, dict) else candidates
        C = [Path(x).resolve() for x in keys]
    except (TypeError, OSError, AttributeError) as e:
        return (False, "入参不可解析（%s）⇒ 覆盖面未自证，不得判绿" % type(e).__name__)
    if not C:
        return (None, "发现器零候选 ⇒ 覆盖面未行使（R-ENUM 边界条：零输入不得静默 PASS）")
    miss = [c for c in C if c not in L]
    if miss:
        return (False, "%d/%d 件带可配对正负规则的权威源不在扫描面内：%s ⇒ 冲突判据对它们全盲"
                % (len(miss), len(C), ", ".join(p.name for p in miss[:6])))
    return (True, "%d 件带极性规则的权威源全部在扫描面内（含自动发现的规则分卷）" % len(C))


def effective_files():
    """扫描面 = 手抄核心清单 ∪ 自动发现的权威源分卷（去重、保持清单在前，便于与历史证据对账）。"""
    cands = discover_authority_candidates()
    have = {p.resolve() for p in DEFAULT_FILES}
    return [p for p in DEFAULT_FILES if p.exists()] + [p for p in sorted(cands) if p not in have]


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


def on_write_check(candidate, authority_files):
    """r34 M-1 · 写时冲突检查（对标 mycelium `check-rule-conflicts-on-write.py`）。

    与批量模式 `scan(DEFAULT_FILES)` 的差别不是快慢，是**发现时点**：
    批量模式在改动入库后出候选清单等人工裁；本函数在**落盘前**只拿"待写的这一个文件"
    去撞权威源，命中即 rc=1，让"写进去才发现互斥"没有下一次。

    三态（R247 口径，任一侧覆盖为空都不得判 CLEAN）：
      UNVERIFIED  候选不存在/空/无极性规则句；权威源全部不可读或规则数为 0
      CONFLICT    至少一组「必须 ↔ 禁止」共享 >=MIN_TERM 字的 CJK 子串，且**候选侧参与**
      CLEAN       两侧覆盖均非空且无跨侧配对
    """
    cand = Path(candidate)
    auths = [Path(p) for p in authority_files]
    _cd, cand_rules, c_missing, c_empty = scan([cand])
    _ad, auth_rules, a_missing, a_empty = scan(auths)
    unreadable = [str(x) for x in (a_missing + a_empty)]
    res = {"schema": "on-write-v1", "candidate": str(cand), "authority_files": [str(p) for p in auths],
           "rules_candidate": len(cand_rules), "rules_authority": len(auth_rules),
           "unreadable": unreadable, "state": "CLEAN", "why": "", "pairs": []}

    if c_missing or c_empty:
        res.update(state="UNVERIFIED",
                   why="候选文件不可读或为空（%s）" % (c_missing + c_empty))
        return res
    if not cand_rules:
        res.update(state="UNVERIFIED",
                   why="候选内无「必须/禁止」类极性规则句 ⇒ 写时检查无对象，不得当作「无冲突」")
        return res
    if not auth_rules:
        res.update(state="UNVERIFIED",
                   why="权威源侧规则数为 0（不可读/为空: %s）⇒ 无鉴别力，禁止判 CLEAN（假绿最危险形态）"
                       % (unreadable or "无文件"))
        return res

    cand_name = cand.name
    pairs = polarity_pairs(cand_rules + auth_rules)
    pairs = [p for p in pairs if cand_name in (p["must"]["loc"] + p["forbid"]["loc"])]
    res["pairs"] = pairs
    if pairs:
        res.update(state="CONFLICT",
                   why="%d 组跨侧互斥候选（含候选自身），先裁后写；禁改权威源凑绿（R263）" % len(pairs))
    return res


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
    ap.add_argument("--on-write", metavar="FILE",
                    help="r34 M-1 写时模式：只检这一个待写入文件与权威源是否互斥（rc=1 即拦）")
    ap.add_argument("--against", action="append", default=[],
                    help="写时模式的权威源，可重复；缺省用 DEFAULT_FILES")
    args = ap.parse_args()

    if args.on_write:
        res = on_write_check(args.on_write, args.against or DEFAULT_FILES)
        print("=== 写时冲突检查（r34 M-1，对标 mycelium check-rule-conflicts-on-write）===")
        print("候选: %s（极性规则 %d 条）" % (res["candidate"], res["rules_candidate"]))
        print("权威: %d 个文件（极性规则 %d 条）%s" % (
            len(res["authority_files"]), res["rules_authority"],
            "｜不可读/空: %s" % ",".join(res["unreadable"]) if res["unreadable"] else ""))
        print("规则: 两侧均非空才具鉴别力；配对要求候选侧参与（MIN_TERM=%d）" % MIN_TERM)
        if res["state"] == "CONFLICT":
            print("[ONWRITE:CONFLICT] %s" % res["why"])
            for p in res["pairs"][:10]:
                print("  · 共享词「%s」｜必须@%s ↔ 禁止@%s"
                      % (p["term"], p["must"]["loc"], p["forbid"]["loc"]))
        elif res["state"] == "UNVERIFIED":
            print("[ONWRITE:UNVERIFIED] %s（R247：取不到/无覆盖不得判过）" % res["why"])
        else:
            print("[ONWRITE:CLEAN] 未发现与权威源互斥的新规则")
        return 1 if res["state"] == "CONFLICT" else (0 if res["state"] == "CLEAN" else 2)

    files = effective_files()                       # r50 W-25：手抄清单 ∪ 自动发现的规则分卷
    declared, rules, missing, empty = scan(files)
    cands = discover_authority_candidates()
    f_cov = face_authority_coverage({p.resolve() for p in files}, cands)
    pairs = polarity_pairs(rules)
    present = len(files) - len(missing)
    print("扫描面 %d 件（手抄 %d + 自动发现 %d）｜权威源覆盖自证：%s ｜ %s"
          % (len(files), len([p for p in DEFAULT_FILES if p.exists()]),
             len(files) - len([p for p in DEFAULT_FILES if p.exists()]),
             {True: "OK", False: "FAIL", None: "UNVERIFIED"}[f_cov[0]], f_cov[1]))

    result = {
        "schema": "rule-conflict-scan-v1",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "readonly": True,
        "benchmark": "mycelium-hq/ai-brain-starter scripts/check-rule-conflicts.py",
        "input_evidence": {
            "files_declared": len(files), "files_listed": len(files),
            "files_present": present,
            "files_missing": missing,
            "files_empty": empty,
            "polarity_rules": len(rules),
            "authority_candidates": len(cands),
            "authority_coverage": {True: "OK", False: "FAIL", None: "UNVERIFIED"}[f_cov[0]],
            "authority_coverage_detail": f_cov[1],
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
