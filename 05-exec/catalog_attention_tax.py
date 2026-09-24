# -*- coding: utf-8 -*-
"""catalog_attention_tax.py - r18 P0: measure the skill-catalog injection surface.

Why: two ratchets already exist and both PASS, yet neither sees the biggest forced
injection block.
  * C25 inject budget  = 5 files, 61,472 B / hard cap 65,536 B
  * attention_sim P0   = 6 files, 16,372 B / 5,457 tokens
  * platform skill catalog (name + frontmatter description of every registered skill)
    is injected every turn and is unmeasured by either.

Benchmark source: sickn33/agentic-awesome-skills `--risk/--category/--tags` reduced
install + docs/users/agent-overload-recovery.md (runtime skill-set slimming), and
lucasrosati/claude-code-memory-setup's quantified per-session token claims.

Output: total chars/tokens, per-skill ranking (trim candidates), and growth vs the
skill-count baseline. Read-only; emits a remediation queue, changes nothing.
"""

import argparse
import collections
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
PLUGIN_MANIFEST = (Path.home() / ".qoder-cn" / "plugins" / "installed_plugins_v2.json")
C25_BASELINE = 61472
C25_HARD_CAP = 65536
WINDOW_TOKENS = 128000
ANTHROPIC_DESC_CAP = 1024


def is_reparse_dir(p):
    try:
        return p.stat(follow_symlinks=False).st_file_attributes & 0x400 != 0
    except (OSError, AttributeError):
        return False


def get_desc(text):
    m = re.search(r"^description:\s*(.*)$", text, re.M)
    if not m:
        return None
    lines = text.splitlines()
    idx = next((i for i, l in enumerate(lines) if l.startswith("description:")), None)
    buf = [m.group(1).strip()]
    if idx is not None:
        for s in lines[idx + 1:]:
            if s.strip() and s[0] in " \t":
                buf.append(s.strip())
            else:
                break
    return " ".join(x for x in buf if x not in ("|", ">", "-")).strip()


def scan():
    rows, junctions = [], []
    for md in sorted(GS_ROOT.glob("*/SKILL.md")):
        name = md.parent.name
        if is_reparse_dir(md.parent):
            junctions.append(name)
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        desc = get_desc(text) or ""
        rows.append({"skill": name, "desc_chars": len(desc),
                     "line": "%s: %s" % (name, desc)})
    return rows, junctions


def scan_plugins(manifest_path):
    """Active plugin skills, resolved through installed_plugins_v2.json.

    cache/ keeps superseded versions on disk; only installPath entries in the
    manifest are actually injected, so counting the whole cache tree overstates
    the tax (measured: 57 SKILL.md on disk vs the manifest-selected set).
    """
    try:
        man = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, "manifest unreadable (%s)" % e
    rows, missing = [], []
    for key, entries in (man.get("plugins") or {}).items():
        for ent in entries if isinstance(entries, list) else [entries]:
            ip = Path(ent.get("installPath", ""))
            if not ip.is_dir():
                missing.append(key)
                continue
            for md in sorted(ip.glob("skills/*/SKILL.md")):
                desc = get_desc(md.read_text(encoding="utf-8", errors="replace")) or ""
                rows.append({"skill": "%s/%s" % (key.split("@")[0], md.parent.name),
                             "desc_chars": len(desc), "visible": ent.get("userVisible", True)})
    return rows, missing


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
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--plugin-manifest", default=PLUGIN_MANIFEST,
                    help="Qoder installed_plugins_v2.json；传 none 关闭插件面")
    args = ap.parse_args()

    rows, junctions = scan()
    n = len(rows)
    if n == 0:
        print("FAIL(R247): 0 skills enumerated - refuse to report a tax figure")
        return 1
    total = sum(r["desc_chars"] for r in rows)
    names_overhead = sum(len(r["skill"]) for r in rows)
    grand = total + names_overhead
    pct_window = 100.0 * grand / WINDOW_TOKENS
    over_cap = [r for r in rows if r["desc_chars"] > ANTHROPIC_DESC_CAP]
    rows.sort(key=lambda r: -r["desc_chars"])

    prows, pmissing, perr = [], [], None
    plugin_on = bool(args.plugin_manifest) and str(args.plugin_manifest).lower() != "none"
    if plugin_on:
        prows, pmissing = scan_plugins(args.plugin_manifest)
        if prows is None:
            prows, perr, pmissing = [], pmissing, []
    ptotal = sum(r["desc_chars"] for r in prows)
    pnames = sum(len(r["skill"]) for r in prows)
    pgrand = ptotal + pnames
    cgrand = grand + pgrand
    cpct = 100.0 * cgrand / WINDOW_TOKENS

    print("=== 技能目录注意力税实测 (%s) ===" % datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("枚举: %d 纳入 + %d junction 跳过(%s)" % (n, len(junctions), ",".join(junctions) or "-"))
    if _lib is not None:
        for ln in _lib.denominator_lines(_lib.denominator(n, junctions, [])):
            print(ln)
    else:
        print("口径对账: _lib 不可用 → 本表分母仅磁盘 glob，禁止引用为全库分母")
    print("description 字符合计 : %d   (+ name %d) = %d" % (total, names_overhead, grand))
    print("按 1 CJK 字符 ~= 1 token: ~%d tokens/轮 = 上下文窗口(128k)的 %.1f%%" % (grand, pct_window))
    print("对照 C25: 基线 %dB / 硬顶 %dB -> 目录块是硬顶的 %.2f 倍" % (C25_BASELINE, C25_HARD_CAP, grand * 3.0 / C25_HARD_CAP))
    print("超 anthropics 官方 description 上限(%d 字符)的技能: %d" % (ANTHROPIC_DESC_CAP, len(over_cap)))
    print("中位数 %d 字符 / 最长 %d 字符" % (rows[n // 2]["desc_chars"], rows[0]["desc_chars"]))
    print()
    print("--- 第四口径：插件技能面（不在 D:\\global_skills / 注册表 / 任何门禁内）---")
    if not plugin_on:
        print("  已按 --plugin-manifest none 关闭")
    elif perr:
        print("  清单不可读: %s → 本表分母仅自建面，禁止引用为全注入面" % perr)
    else:
        ptop = sorted(prows, key=lambda r: -r["desc_chars"])
        print("  活跃插件技能 %d 条（清单 %s；缓存目录树含更多历史版本，按 manifest 选定项计数）"
              % (len(prows), Path(args.plugin_manifest).name))
        if pmissing:
            print("  ⚠ manifest 指向但盘上缺失的插件: %s" % ", ".join(pmissing))
        print("  description %d + name %d = %d 字符（中位 %d / 最长 %d）" % (
            ptotal, pnames, pgrand,
            ptop[len(ptop) // 2]["desc_chars"] if ptop else 0,
            ptop[0]["desc_chars"] if ptop else 0))
        print("  按插件计数: %s" % ", ".join(
            "%s=%d" % (k, v) for k, v in sorted(
                collections.Counter(r["skill"].split("/")[0] for r in prows).items(),
                key=lambda kv: -kv[1])[:12]))
        print()
        print("=== 合计注入面（自建 + 插件）===")
        print("  %d 技能 / %d 字符 ≈ %d tokens/轮 = 128k 窗口的 %.1f%% = C25 硬顶 %.2f 倍" % (
            n + len(prows), cgrand, cgrand, cpct, cgrand * 3.0 / C25_HARD_CAP))
        print("  仅看自建面会低估 %.1f%%（%d vs %d 字符）" % (
            100.0 * pgrand / grand if grand else 0, grand, cgrand))
    print()
    print("裁剪候选 top %d（每轮省字符数）:" % args.top)
    for r in rows[: args.top]:
        print("  %-32s %5d 字符" % (r["skill"], r["desc_chars"]))
    head = sum(r["desc_chars"] for r in rows[:20])
    print("=> 前 20 条合计 %d 字符 = 全目录的 %.1f%%" % (head, 100.0 * head / total))

    result = {
        "schema": "catalog-attention-tax-v1",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "readonly": True,
        "denominator": {"scanned": n, "junction_skipped": junctions},
        "desc_chars_total": total,
        "name_chars_total": names_overhead,
        "grand_chars": grand,
        "est_tokens_per_turn": grand,
        "pct_of_128k_window": round(pct_window, 2),
        "vs_c25_hard_cap_ratio": round(grand * 3.0 / C25_HARD_CAP, 2),
        "over_official_cap": [{"skill": r["skill"], "chars": r["desc_chars"]} for r in over_cap],
        "median_chars": rows[n // 2]["desc_chars"],
        "max_chars": rows[0]["desc_chars"],
        "trim_queue": rows[:40],
        "token_model_caveat": "1 CJK char ~= 1 token is the same convention as attention_sim bytes//3; tokenizer-exact counting not available offline",
        "plugin_surface": {
            "measured": bool(plugin_on) and perr is None,
            "manifest": str(args.plugin_manifest),
            "count": len(prows),
            "desc_chars": ptotal,
            "name_chars": pnames,
            "grand_chars": pgrand,
            "by_plugin": dict(collections.Counter(r["skill"].split("/")[0] for r in prows)),
            "missing_installPath": pmissing,
            "error": perr,
            "gate_coverage": "NOT covered by 焚诀 C1 registry / C25 / C20 / C27 / C28 (all scoped to D:\\global_skills)",
        },
        "combined": {"skills": n + len(prows), "grand_chars": cgrand,
                     "est_tokens_per_turn": cgrand, "pct_of_128k_window": round(cpct, 2),
                     "vs_c25_hard_cap_ratio": round(cgrand * 3.0 / C25_HARD_CAP, 2)},
    }
    if args.json:
        Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print("\nJSON -> %s" % args.json)
    if args.md:
        md = ["# 技能目录注意力税基线 (%s)" % result["generated_at"], "",
              "> 对标 sickn33/agentic-awesome-skills 的 reduced-install / overload-recovery 机制。",
              "> 本块**不被任何现有棘轮覆盖**：C25 只测 5 个文件，attention_sim P0 只测 6 个文件。", "",
              "| 项 | 值 |", "|---|---|",
              "| 纳入技能 | %d (另 junction %d: %s) |" % (n, len(junctions), ", ".join(junctions) or "-"),
              "| description 字符合计 | %d |" % total,
              "| + name 字符 | %d = 合计 %d |" % (names_overhead, grand),
              "| 估算 tokens/轮 | ~%d（1 CJK 字符 ~ 1 token） |" % grand,
              "| 占 128k 窗口 | %.1f%% |" % pct_window,
              "| vs C25 硬顶 65,536B | %.2f 倍 |" % (grand * 3.0 / C25_HARD_CAP),
              "| 中位/最长 description | %d / %d 字符 |" % (result["median_chars"], result["max_chars"]),
              "| 超官方 1024 字符上限 | %d 条 |" % len(over_cap),
              "| **插件技能面（第四口径）** | **%d 条 / %d 字符**（门禁零覆盖） |" % (len(prows), pgrand),
              "| **合计注入面** | **%d 技能 / %d 字符 ≈ %d tokens/轮 = 窗口 %.1f%% = C25 硬顶 %.2f 倍** |" % (
                  n + len(prows), cgrand, cgrand, cpct, cgrand * 3.0 / C25_HARD_CAP),
              "| 只看自建面低估 | %.1f%% |" % (100.0 * pgrand / grand if grand else 0), "",
              "## 裁剪候选队列 (top %d)" % args.top, "", "| 技能 | 字符 | 每轮收益 |", "|---|---|---|"]
        md += ["| `%s` | %d | %d |" % (r["skill"], r["desc_chars"], r["desc_chars"]) for r in rows[: args.top]]
        md += ["", "## 口径注", "",
               "- token 折算沿用 `attention_sim.py` 的 `bytes//3` 同族近似，非 tokenizer 精确值。",
               "- 目录块由平台注入，本项目**无法直接删减**；可控杠杆只有两条：单条 description 长度、在册技能数。",
               "- 前 20 条占全目录 %.1f%% —— 尾部裁剪的边际收益集中且可复跑。" % (100.0 * head / total), ""]
        Path(args.md).write_text("\n".join(md) + "\n", encoding="utf-8")
        print("MD   -> %s" % args.md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
