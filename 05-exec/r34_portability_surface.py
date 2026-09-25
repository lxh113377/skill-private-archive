# -*- coding: utf-8 -*-
"""r34_portability_surface.py — 第十一维「可移植性」实测（文件级，非 README 宣称）。

为什么量这个：本体系有 C20「技能可移植性棘轮」（焚诀侧，r31 登记为他人红项），
但**从未与对手在同一把尺上比过** —— 而且比的是技能文件本体，不是文档里说"跨平台"。
对手普遍宣称 portable / works anywhere；实物是否真无机器专属路径，一测就知道。

尺（四类机器专属信号，逐文件计数）：
  P1 用户家目录绝对路径  `C:\\Users\\<x>` / `/Users/<x>` / `/home/<x>`
  P2 盘符根路径          `D:\\` `<A-Z>:\\`
  P3 本机用户名明文      出现在文本里的账号名（如 `37533`）
  P4 机器专属工具绝对路径 `Program Files\\...\\python.exe` / `binaries/.../python`

口径与诚实性：
  · 命中 != 缺陷 —— 技能引用**本机已装的解释器**可能是有意设计（本仓 AGENTS 就明文写死首选解释器路径）。
    本维度只回答"能不能原样搬到另一台机器跑"，不判好坏；结论必须与"该技能是否声明了降级路径"一起读。
  · 对手侧按**逐文件**取（gh api contents 原文），不取 README 说法。
  · 分母必须自证：每仓"取到多少个技能文件 / 总清单多少"，取数失败的文件**不计入命中也不计入分母**。

用法：
    python 05-exec/r34_portability_surface.py [--ours] [--json 06-benchmark/portability_rNN_<date>.json]
退出码：0 全部面探测成功 / 1 有仓库取数失败（禁把失败当"0 命中"，R247）/ 2 gh 不可用
"""

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

GS = Path(r"D:\global_skills")
REPOS = {
    "addyosmani/agent-skills": "skills",
    "obra/superpowers": "skills",
    "sickn33/agentic-awesome-skills": "skills",
    "anthropics/skills": "skills",
    "mycelium-hq/ai-brain-starter": "skills",
}
RX = {
    "P1_home_abs": re.compile(r"(?i)([A-Z]:\\\\?Users\\\\|/Users/|/home/[a-z0-9_.-]+/)"),
    "P2_drive_root": re.compile(r"\b[A-Za-z]:\\\\?[A-Za-z]"),
    "P3_username": re.compile(r"37533|/Users/[a-z0-9_.-]+/[a-z]"),
    "P4_tool_abs": re.compile(r"(?i)(Program Files\\\\|binaries/[a-z]+/envs/|\.workbuddy/binaries)"),
}


def gh(args):
    return subprocess.run(["gh"] + args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=90)


def score(text):
    hits = {}
    for k, rx in RX.items():
        n = len(rx.findall(text))
        if n:
            hits[k] = n
    return hits


def scan_dir(root):
    """本体系侧：只扫 SKILL.md 本体（技能入口，最会被原样搬走的那一个文件）。"""
    files = sorted(root.glob("*/SKILL.md"))
    dirty, clean, unreadable = [], 0, []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            unreadable.append(f.name)
            continue
        h = score(text)
        if h:
            dirty.append({"skill": f.parent.name, "hits": h, "bytes": len(text.encode("utf-8"))})
        else:
            clean += 1
    return {"root": str(root), "total": len(files), "clean": clean, "dirty": len(dirty),
            "unreadable": unreadable, "top": sorted(dirty, key=lambda d: -sum(d["hits"].values()))[:12],
            "signal_totals": dict(Counter(k for d in dirty for k in d["hits"]))}


def scan_repo(slug, subdir):
    """对手侧：列该目录下的技能，逐个取 SKILL.md 原文。"""
    r = gh(["api", "repos/%s/contents/%s" % (slug, subdir), "--jq",
            '[.[] | select(.type=="dir") | .name] | join("\\n")'])
    if r.returncode != 0:
        return {"repo": slug, "error": (r.stderr or "")[:120]}
    names = [x.strip() for x in (r.stdout or "").split("\n") if x.strip()]
    dirty = clean = fail = 0
    detail = []
    for n in names[:30]:
        c = gh(["api", "repos/%s/contents/%s/%s/SKILL.md" % (slug, subdir, n), "--jq", ".content"])
        if c.returncode != 0 or not c.stdout.strip():
            fail += 1
            continue
        try:
            import base64
            text = base64.b64decode(c.stdout.strip()).decode("utf-8", "replace")
        except Exception:
            fail += 1
            continue
        h = score(text)
        if h:
            dirty += 1
            detail.append({"skill": n, "hits": h})
        else:
            clean += 1
    return {"repo": slug, "subdir": subdir, "skill_dirs_listed": len(names),
            "files_fetched": dirty + clean, "fetch_failed": fail,
            "clean": clean, "dirty": dirty,
            "dirty_rate": round(dirty / float(dirty + clean), 3) if (dirty + clean) else None,
            "detail": detail[:10]}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--ours", action="store_true", help="只扫本体系侧（不联网取对手）")
    ap.add_argument("--json")
    args = ap.parse_args()

    ours = scan_dir(GS) if GS.exists() else {"error": "global_skills 不存在"}
    print("本体系 %s：SKILL.md %d 个｜机器专属信号命中 %d｜干净 %d｜不可读 %d" % (
        GS, ours.get("total", 0), ours.get("dirty", 0), ours.get("clean", 0), len(ours.get("unreadable", []))))
    print("  信号分布：%s" % ours.get("signal_totals"))
    for d in ours.get("top", [])[:6]:
        print("  · %-34s %s" % (d["skill"], d["hits"]))

    opp = []
    if not args.ours:
        if gh(["--version"]).returncode != 0:
            print("[PORT:UNVERIFIED] gh 不可用 ⇒ 不得输出「对手全部可移植」结论")
            return 2
        for slug, sub in REPOS.items():
            r = scan_repo(slug, sub)
            opp.append(r)
            if "error" in r:
                print("%-38s 取数失败：%s" % (slug, r["error"][:60]))
            else:
                print("%-38s 取到 %d/%d 个 SKILL.md｜命中机器路径 %d（%.0f%%）｜取数失败 %d" % (
                    slug, r["files_fetched"], r["skill_dirs_listed"], r["dirty"],
                    100 * (r["dirty_rate"] or 0), r["fetch_failed"]))
    failed = [r["repo"] for r in opp if "error" in r]
    print("-" * 72)
    print("覆盖根: 本体系 %s（SKILL.md 全量）＋对手 %d 仓（每仓 <=30 个 SKILL.md 原文）"
          % (GS, len(opp)))
    print("口径: 命中!=缺陷（本机解释器可能是有意写死）；只答「能否原样搬走」，结论须与降级路径声明一起读")
    rc = 1 if failed else 0
    print("[PORT:OK] %s" % ("" if not failed else "取数失败仓=%s ⇒ 其 0 命中不可信" % ",".join(failed)))
    if args.json:
        doc = {"schema": "portability-surface-v1", "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
               "readonly": True, "benchmark": "r34 第十一维 可移植性（文件级实测，非 README 宣称）",
               "provenance_cmd": "gh api repos/<s>/contents/skills/<n>/SKILL.md --jq .content | base64 -d",
               "signals": list(RX), "ours": ours, "opposites": opp,
               "denominator": {"repos_ok": len(opp) - len(failed), "repos_failed": failed},
               "caveat": "命中数含正则重复计数，只用于横向相对比较，禁当精确缺陷数；对手每仓抽样上限 30 个技能"}
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(json.dumps(doc, ensure_ascii=False, indent=1))
        print("JSON -> %s" % args.json)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
