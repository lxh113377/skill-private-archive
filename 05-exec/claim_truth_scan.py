# -*- coding: utf-8 -*-
"""claim_truth_scan.py — 规则/技能正文里的「计数类断言」与真相源对账（r19，只读）。

触发根因（r19 P0-C 第 2 批人工复核实测）：
  `D:\\global_skills\\A-memory-start\\SKILL.md` 正文与 frontmatter description 仍写
  「五端统一 / <HM/WB/CX/TC/ZC> / OC 已退役 2026-09-21」，而焚诀真相源
  `eval/truth_constants.json` 的 `endpoints.active` = **8 端**（wb/tr/cx/hm/zc/oc/qw/qd，
  oc 由 OpenCode 于 09-23 接管复用、qw/qd 于 09-24 入役）。该文件**每轮注入**，
  失真句因此每轮都被喂给模型。C1~C28 里没有一条覆盖「技能正文的端数表述 == 真相源」：
  C3 只比 platform_tiers 与 ENDPOINTS（焚诀内部两件派生件自比），C13 只比 frontmatter
  版本与版本历史，C16 只比 STATUS 产物——**技能正文不在任何内容级对账面上**。

对标来源：
  · 焚诀自身 C16「关键产物内容 == 真相源」（补 mtime 盲区）——本脚本把它从
    「STATUS 产物」扩到「技能/规则正文」这一从未覆盖的面；
  · mycelium-hq/ai-brain-starter `scripts/drift-detection.py`——改写频次只是候选，
    语义失真要靠**与权威源对账**才判得出来。

判据（三族，全部只给候选，人工裁决；R241 禁为变绿改写规则本体）：
  F1 端数族：文本出现「N端 / 四端~九端中文数字 / <A/B/C/...> 端枚举 / 「X 已退役/弃用」」
     → 与 truth_constants endpoints.active 数量与代号集合比对；
  F2 技能数族：文本出现裸「NNN 技能 / NNN 条技能 / 基数 NNN」→ 与注册表 count 比对
     （容忍 ±0；历史句由上下文「当时/原为/已作废」标记豁免，见 EXEMPT_RE）；
  F3 版本族：`A-xxx V vNN.NN(.NN)` 与磁盘 frontmatter version 比对（仅对 global_skills 下文件）。

输出：stdout 候选清单 + --json 全量 + --md 基线。退出码 0=无候选 / 1=有候选 / 2=真相源不可读
（真相源不可读时**禁止**当作「零失真」，R247）。
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

FENJUE = Path(r"C:\Users\37533\Desktop\workspace\焚诀")
GS = Path(r"D:\global_skills")
TRUTH = FENJUE / "eval" / "truth_constants.json"

# 受检文本面：每轮/高频注入的规则与技能正文（可按 --target 扩展）
DEFAULT_TARGETS = [
    GS / "A-memory-start" / "SKILL.md",
    GS / "A-memory-start" / "references" / "contract.md",
    GS / "A-project-handoff" / "SKILL.md",
    GS / "A-get-memory" / "SKILL.md",
    GS / "A-project-better" / "SKILL.md",
    GS / "A-skill-manager" / "SKILL.md",
    FENJUE / "memory" / "AGENTS.md",
]

CN_NUM = {"四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
RE_NDUAN = re.compile(r"([四五六七八九十]|\d+)\s*端")
RE_ENUM = re.compile(r"<\s*([A-Z]{2}(?:/[A-Z]{2,4}){2,})\s*>")
RE_RETIRE = re.compile(r"([A-Z]{2})\s*(?:端)?\s*(?:已退役|已弃用|已下线|已移除|退役)")
RE_SKILLCOUNT = re.compile(r"(?<![\d.])(\d{3})\s*(?:个|条)?\s*(?:skills|技能|SKILL\.md)"
                          r"|基数\s*(\d{3})|注册表\s*(\d{3})")
RE_VER = re.compile(r"([A-Za-z0-9_\-]+)\s+[Vv](\d+(?:\.\d+){1,2})\b")
# 历史豁免：明确标注为「当时为真 / 原文保留 / 已作废 / 校正注」的行不参与判定
EXEMPT_RE = re.compile(r"(当时|原为|旧口径|已作废|原文保留|校正注|历史|不再引用|迁入|瘦身)")
HIST_SECTION = re.compile(r"(版本历史|变更历史|version_history|V1[0-9]?\.\d+\.\d+ \(20\d\d)")


def load_truth():
    try:
        data = json.loads(TRUTH.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        return None, "%s: %s" % (type(e).__name__, e)
    eps = (data.get("endpoints") or {}).get("active") or []
    if not eps:
        return None, "endpoints.active 为空（判据不可信）"
    return {"active": eps, "n": len(eps)}, None


def registry_count():
    if _lib is None:
        return None
    reg = _lib.registry_denominator()
    return reg.get("count") if reg.get("available") else None


def classify_line(line):
    """返回该行所属断言族（端数族再细分：枚举/中文数字/退役声明）。"""
    if EXEMPT_RE.search(line) or HIST_SECTION.search(line):
        return None
    fams = []
    if RE_ENUM.search(line):
        fams.append("endpoint_enum")
    if RE_NDUAN.search(line):
        fams.append("endpoint_count")
    if RE_RETIRE.search(line):
        fams.append("endpoint_retire_claim")
    if RE_SKILLCOUNT.search(line):
        fams.append("skill_count")
    if RE_VER.search(line):
        fams.append("version_claim")
    return fams or None


def norm_tokens(enum_text):
    return [t for t in enum_text.upper().split("/") if t]


LABEL_TO_CODE = {"HM": "hm", "WB": "wb", "CX": "cx", "TC": "tr", "TR": "tr", "ZC": "zc",
                 "OC": "oc", "QW": "qw", "QD": "qd", "CC": "cc"}


def scan_file(path, truth, reg_count):
    out = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as e:
        return [{"file": str(path), "error": str(e), "family": "unreadable"}]
    for i, line in enumerate(lines, 1):
        fams = classify_line(line)
        if not fams:
            continue
        for fam in fams:
            verdict = {"family": fam, "file": str(path), "line": i, "text": line.strip()[:200]}
            if fam == "endpoint_count":
                m = RE_NDUAN.search(line)
                raw = m.group(1)
                n = CN_NUM.get(raw) or (int(raw) if raw.isdigit() else None)
                if n is not None and n != truth["n"]:
                    verdict["claim"] = "%s端 = %d" % (raw, n)
                    verdict["truth"] = "active %d 端 %s" % (truth["n"], truth["active"])
                    out.append(verdict)
            elif fam == "endpoint_enum":
                toks = norm_tokens(RE_ENUM.search(line).group(1))
                codes = {LABEL_TO_CODE.get(t) for t in toks}
                missing = sorted(set(truth["active"]) - codes - {None})
                if len(toks) != truth["n"] or missing:
                    verdict["claim"] = "/".join(toks)
                    verdict["truth"] = "缺 %s（真值 %d 端）" % (missing, truth["n"])
                    out.append(verdict)
            elif fam == "endpoint_retire_claim":
                code = RE_RETIRE.search(line).group(1).lower()
                if code in truth["active"]:
                    verdict["claim"] = "%s 声称已退役/弃用" % code.upper()
                    verdict["truth"] = "%s 在 endpoints.active 内（09-23 起由 OpenCode 接管复用）" % code
                    out.append(verdict)
            elif fam == "skill_count" and reg_count:
                m = RE_SKILLCOUNT.search(line)
                num = next((g for g in m.groups() if g), None)
                if num and int(num) != reg_count:
                    verdict["claim"] = num
                    verdict["truth"] = "注册表 count=%d" % reg_count
                    out.append(verdict)
            elif fam == "version_claim":
                m = RE_VER.search(line)
                name, claimed = m.group(1), m.group(2)
                fp = GS / name / "SKILL.md"
                if fp.is_file():
                    mv = re.search(r"^version:\s*([0-9.]+)",
                                   fp.read_text(encoding="utf-8", errors="replace"), re.M)
                    if mv and mv.group(1) != claimed:
                        verdict["claim"] = "%s V%s" % (name, claimed)
                        verdict["truth"] = "frontmatter version: %s" % mv.group(1)
                        out.append(verdict)
    return out


def main():
    if _lib is not None:
        _lib.force_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--md")
    ap.add_argument("--target", action="append", help="追加受检文件（可多次）")
    args = ap.parse_args()

    truth, err = load_truth()
    if err:
        print("FAIL(真相源不可读，禁止判零失真): %s" % err)
        return 2
    reg_count = registry_count()
    targets = list(DEFAULT_TARGETS) + [Path(t) for t in (args.target or [])]
    print("=== 计数断言对账扫描 (%s) ===" % datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("真相源: endpoints.active=%d 端 %s ｜ 注册表 count=%s ｜ 取值: %s / %s" % (
        truth["n"], truth["active"], reg_count, TRUTH,
        r"焚诀/skill/registry/disk_manifest.json"))
    present = [t for t in targets if t.exists()]
    missing = [str(t) for t in targets if not t.exists()]
    if not present:
        print("FAIL(R247): 受检文本面为空，禁止据此判「零失真」")
        return 2
    cands = []
    for t in present:
        rows = scan_file(t, truth, reg_count)
        cands += rows
        print("  %-58s 候选 %d" % ("/".join(t.parts[-2:]), len(rows)))
    if missing:
        print("  缺失（不计入判定）: %s" % ", ".join(missing))
    fam_order = ["endpoint_enum", "endpoint_count", "endpoint_retire_claim",
                 "skill_count", "version_claim"]
    print("\n=== 失真候选 %d 条（人工裁决，禁自动改写）===" % len(cands))
    for fam in fam_order:
        rows = [c for c in cands if c["family"] == fam]
        if not rows:
            continue
        print("--- %s (%d) ---" % (fam, len(rows)))
        for c in rows[:12]:
            print("  %s:%d  声称[%s] vs 真值[%s]" % (
                "/".join(Path(c["file"]).parts[-2:]), c["line"],
                c.get("claim", "-"), c.get("truth", "-")))
            print("      句: %s" % c["text"][:110])
    result = {
        "schema": "claim-truth-scan-v1",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "readonly": True,
        "truth": truth,
        "registry_count": reg_count,
        "targets_present": [str(t) for t in present],
        "targets_missing": missing,
        "candidates": cands,
        "exempt_rule": "含「当时/原为/已作废/原文保留/校正注/历史/瘦身」或版本历史章节的行豁免（R241）",
        "note": "候选非判决；技能正文此前不在任何内容级对账门禁面上（C3/C13/C16 均不覆盖）",
    }
    if args.json:
        Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print("\nJSON -> %s" % args.json)
    if args.md:
        md = ["# 计数断言对账基线 (%s)" % result["generated_at"], "",
              "> 对标：焚诀 C16「产物内容 == 真相源」外推到**技能正文面**；"
              "根因 = r19 P0-C 第 2 批人工复核实测到「每轮注入的 SKILL.md 仍写五端，真相源八端」。",
              "> 只出候选，人工裁决；历史留痕行按 R241 豁免（见 `exempt_rule`）。", "",
              "| 项 | 值 |", "|---|---|",
              "| endpoints.active | %d 端 %s |" % (truth["n"], ", ".join(truth["active"])),
              "| 注册表 count | %s |" % reg_count,
              "| 受检文件 | %d（缺失 %d） |" % (len(present), len(missing)),
              "| 失真候选 | %d |" % len(cands), "",
              "| 族 | 文件:行 | 声称 | 真值 |", "|---|---|---|---|"]
        md += ["| %s | `%s:%d` | %s | %s |" % (c["family"], "/".join(Path(c["file"]).parts[-2:]),
                                               c["line"], c.get("claim", "-"), c.get("truth", "-"))
               for c in cands] or ["| - | - | - | 无候选 |"]
        Path(args.md).write_text("\n".join(md) + "\n", encoding="utf-8")
        print("MD   -> %s" % args.md)
    return 1 if cands else 0


if __name__ == "__main__":
    raise SystemExit(main())
