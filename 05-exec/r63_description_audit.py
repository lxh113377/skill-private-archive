#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r63 H-1：description 双要素全量审计（169 件）。

anthropics 官方口径：description 是路由第一信号，须含两要素——
  ① 做什么（what）② 何时用（when）。
r62 抽样 10 抽 9 仅 4/9 含"何时用"信号 ⇒ 本件全量扫出基线。
只读扫描；产物落 06-benchmark/description_dual_r63_*.json。
"""
import io
import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GS = Path(r"D:\global_skills")
DESC_CAP = 1024  # anthropics 官方单字段上限（r18 目录税基线同口径）

# "何时用"信号词（r62 同源 + 扩充；对中英 description 双语生效）
WHEN_RE = re.compile(
    r"(何时用|什么时候|当.{0,12}(时|的时候)|适用[于在]?|用于|用来|要.{0,6}时|需要.{0,4}时|"
    r"时使用|时触发|时激活|时加载|触发|场景|Use when|When to use|whenever|"
    r"for use (in|when|with)|if you need|scenario)",
    re.IGNORECASE,
)
# "做什么"信号：以动词性陈述开头（宽松判据：长度 ≥12 且非纯名词罗列）
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
DESC_RE = re.compile(r"^description\s*:\s*(.*)$", re.MULTILINE)


def git_head():
    try:
        return subprocess.run(
            ["git", "ls-remote", "origin", "main"], cwd=ROOT, capture_output=True,
            text=True, timeout=20).stdout.split()[0]
    except Exception:
        return "unavailable"


def parse_description(text):
    m = FRONTMATTER_RE.search(text)
    if not m:
        return None
    fm = m.group(1)
    d = DESC_RE.search(fm)
    if not d:
        return None
    # 单行形；折叠形（>- / |-）取后续缩进行
    val = d.group(1).strip()
    # plain 折叠形：首行有内容 + 缩进续行（workflow-preflight-check 形态）也属多行
    lines = []
    for line in fm[d.end():].splitlines()[1:]:
        if line.strip() and not line.startswith((" ", "\t")):
            break
        lines.append(line.strip())
    if lines:
        val = (val + " " + " ".join(x for x in lines if x)).strip()
    return val


def audit_one(skill, text):
    desc = parse_description(text)
    item = {"skill": skill, "has_field": desc is not None, "chars": 0,
            "what_signal": False, "when_signal": False, "verdict": "FAIL"}
    if desc is None:
        item["verdict"] = "MISSING"
        return item
    item["chars"] = len(desc)
    # what_signal：非空且长度达标即算（首版「不以句号结尾」判据误杀正常陈述句，假阴性）
    item["what_signal"] = len(desc) >= 12
    item["when_signal"] = bool(WHEN_RE.search(desc))
    item["over_cap"] = item["chars"] > DESC_CAP
    item["verdict"] = ("OVER_CAP" if item["over_cap"]
                       else "DUAL" if (item["what_signal"] and item["when_signal"])
                       else "NO_WHEN" if item["what_signal"] else "THIN")
    return item


def main():
    out_items = []
    for d in sorted(GS.iterdir()):
        if not d.is_dir() or d.name == "_trash":
            continue
        f = d / "SKILL.md"
        if not f.is_file():
            continue
        try:
            text = io.open(f, encoding="utf-8-sig", errors="replace").read()
        except OSError as e:
            out_items.append({"skill": d.name, "verdict": "UNREADABLE", "err": str(e)})
            continue
        out_items.append(audit_one(d.name, text))
    by = {}
    for it in out_items:
        by[it["verdict"]] = by.get(it["verdict"], 0) + 1
    worst = sorted(
        (x for x in out_items if x["verdict"] in ("THIN", "NO_WHEN", "MISSING")),
        key=lambda x: (x["verdict"] != "MISSING", x.get("chars", 0)))
    result = {
        "schema": "description-dual-v1",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "head": {"source": "D:/global_skills/*/SKILL.md frontmatter",
                 "commit": git_head(), "method": __file__},
        "cap": DESC_CAP,
        "summary": {"total": len(out_items), **by,
                    "dual_rate_pct": round(100 * by.get("DUAL", 0) / max(len(out_items), 1), 1)},
        "worst_first": worst[:20],
        "items": out_items,
    }
    if "--json" in sys.argv:
        i = sys.argv.index("--json")
        dest = Path(sys.argv[i + 1]) if i + 1 < len(sys.argv) else (
            ROOT / "06-benchmark" / ("r63_description_dual_%s.json" % time.strftime("%Y-%m-%d")))
        dest.parent.mkdir(parents=True, exist_ok=True)
        with io.open(dest, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=1)
        print("JSON ->", dest)
    print("total=%d DUAL=%d NO_WHEN=%d THIN=%d MISSING=%d OVER_CAP=%d dual_rate=%.1f%%"
          % (len(out_items), by.get("DUAL", 0), by.get("NO_WHEN", 0), by.get("THIN", 0),
             by.get("MISSING", 0), by.get("OVER_CAP", 0), result["summary"]["dual_rate_pct"]))
    print("-- worst 10 --")
    for w in worst[:10]:
        print(" ", w["verdict"], w["skill"], w.get("chars", 0))


if __name__ == "__main__":
    main()
