# -*- coding: utf-8 -*-
"""r29_scope_filtered_queue.py - 把对标整改队列先过「自建口径」再排序（只读）。

存在理由：r28 的 H2 队列按"体积大的先补"排，实测 top14 全是市场/上游件
（docx / shadcn / agent-browser / canvas-design ...）。本项目 2026-09-22 范围裁定
把维护面限定为 HIGH 51 + MID 26 = 77 条，EXCLUDE 43 + LOW 30 排除在维护范围外 ⇒
不过滤的队列会引导会话去改别人的技能，属越界动作。本工具把裁定文件变成机器护栏。
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SCOPE_MD = HERE / "00-scope" / "自建skill清单.md"
DIRTY_SKILLS = {  # 受管根 git status --porcelain 实测（2026-09-24 r29），并行会话在途
    "A-project-better", "A-skill-manager", "ican-frontend-design-system",
    "cloudbase__skillhub", "github", "sq-cleanmgr-c",
}


def force_out():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def parse_scope(path=SCOPE_MD):
    """Return {skill: tier} for HIGH/MID/LOW/EXCLUDE sections of the v2 裁定表."""
    if not path.exists():
        return None, "裁定文件不存在: %s" % path
    tiers, cur = {}, None
    for ln in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s*(HIGH|MID|LOW|EXCLUDE)", ln)
        if m:
            cur = m.group(1)
            continue
        if ln.startswith("## "):
            cur = None
            continue
        if cur:
            nm = re.match(r"^\|\s*`([^`]+)`\s*\|", ln)
            if nm:
                tiers[nm.group(1)] = cur
    return tiers, None


def main():
    force_out()
    ap = argparse.ArgumentParser()
    ap.add_argument("--rubric-json", default=str(HERE / "06-benchmark" /
                                                 "skill_structure_rubric_r29_2026-09-24.json"))
    ap.add_argument("--section", default="verification", choices=["verification", "rationalizations"])
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--json")
    args = ap.parse_args()

    tiers, err = parse_scope()
    if err:
        print("FAIL(R247): %s -> 无裁定文件不得出队列" % err)
        return 2
    counts = {}
    for v in tiers.values():
        counts[v] = counts.get(v, 0) + 1
    print("自建口径裁定: %s（合计 %d；本项目维护面 = HIGH+MID = %d）" % (
        ", ".join("%s=%d" % (k, counts[k]) for k in ("HIGH", "MID", "LOW", "EXCLUDE") if k in counts),
        len(tiers), counts.get("HIGH", 0) + counts.get("MID", 0)))

    rub = json.loads(Path(args.rubric_json).read_text(encoding="utf-8"))
    rows = rub.get("per_skill") or []
    if not rows:
        print("FAIL(R247): rubric JSON 无 per_skill，空输入不得当「0 缺口」")
        return 2
    n_all = len(rows)
    missing = [r for r in rows if not r["sections_both"].get(args.section)]
    in_scope = [r for r in missing if tiers.get(r["skill"]) in ("HIGH", "MID")]
    out_of_scope = [r for r in missing if tiers.get(r["skill"]) not in ("HIGH", "MID")]
    unlisted = [r for r in missing if r["skill"] not in tiers]

    print("\n=== 段 %s 缺失面按自建口径拆分（宽口径判据）===" % args.section)
    print("纳入扫描 %d | 缺该段 %d (%.1f%%) | 其中自建在维护面 %d | 非自建 %d | 裁定表未收录 %d" % (
        n_all, len(missing), 100.0 * len(missing) / n_all,
        len(in_scope), len(out_of_scope), len(unlisted)))
    print("=> 真实可动面只有 %d 条（%.1f%% of 缺段），其余 %d 条越界（市场/上游/灰区）" % (
        len(in_scope), 100.0 * len(in_scope) / max(1, len(missing)), len(out_of_scope) + len(unlisted)))

    in_scope.sort(key=lambda r: -r["bytes"])
    print("\n队列 top %d（自建 · 体积降序 · 标出并行会话在途）:" % args.top)
    for r in in_scope[: args.top]:
        flag = " ⚠在途(勿动)" if r["skill"] in DIRTY_SKILLS else ""
        print("  %-34s %7dB  tier=%-4s%s" % (r["skill"], r["bytes"], tiers[r["skill"]], flag))
    busy = [r["skill"] for r in in_scope if r["skill"] in DIRTY_SKILLS]
    print("\n在途冲突项 %d: %s" % (len(busy), ", ".join(busy) or "-"))
    if unlisted:
        print("\n裁定表未收录（磁盘新增于 2026-09-22 裁定之后，需重出裁定表才能判定归属）%d: %s" % (
            len(unlisted), ", ".join(r["skill"] for r in unlisted)))
    print("\n越界项 top10（只登记不改）: %s" % ", ".join(r["skill"] for r in out_of_scope[:10]))

    if args.json:
        Path(args.json).write_text(json.dumps({
            "schema": "scope-filtered-queue-v1",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "readonly": True,
            "section": args.section,
            "scope_source": str(SCOPE_MD),
            "tier_counts": counts,
            "scanned": n_all, "missing": len(missing),
            "in_scope": [{"skill": r["skill"], "bytes": r["bytes"], "tier": tiers[r["skill"]],
                          "in_flight": r["skill"] in DIRTY_SKILLS} for r in in_scope],
            "out_of_scope": [r["skill"] for r in out_of_scope],
            "unlisted": unlisted and [r["skill"] for r in unlisted] or [],
            "caveat": "DIRTY_SKILLS 是 r29 一次实测的并行会话在途快照，复用前必须重跑 git status 核对",
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print("JSON -> %s" % args.json)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as exc:
        sys.stderr.write("UNEXPECTED_FAILURE: %r -> 退出码 2\n" % (exc,))
        raise SystemExit(2)
