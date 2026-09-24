# -*- coding: utf-8 -*-
"""rubric_ab_compare.py - r28: 把本体系的六段解剖尺架到对标项目的真实 SKILL.md 上（只读，需 gh 登录）

方法论修正：r10~r27 的所有结构对比都是"我们的源码 vs 对手的 README 宣称"。
本脚本改为同一把尺量双方真实文件：RUBRIC 判据直接复用 skill_structure_rubric_scan.py（单一真相源）。

退出码：0=完成（含双方数据）；1=对手侧取到文件但本方基线缺失；2=取证失败（gh 不可用/零文件，按 R247 不出结论）。
"""

import argparse
import base64
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill_structure_rubric_scan import (RUBRIC_RX, GS_ROOT, is_reparse_dir,
                                          rubric_hits)  # 同一把尺（r29 起含双口径）

REPOS = ["obra/superpowers", "addyosmani/agent-skills", "anthropics/skills", "mattpocock/skills"]


def gh(args):
    try:
        p = subprocess.run(["gh"] + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
    except (subprocess.TimeoutExpired, OSError) as e:
        return None, str(e)
    if p.returncode != 0:
        return None, (p.stderr or p.stdout or "").strip()[:200]
    return p.stdout, None


def skill_paths(repo):
    out, err = gh(["api", "repos/%s/git/trees/HEAD?recursive=1" % repo, "--jq", ".tree[].path"])
    if err:
        return None, err
    return [l.strip() for l in (out or "").splitlines() if l.strip().endswith("SKILL.md")], None


def fetch(repo, path):
    out, err = gh(["api", "repos/%s/contents/%s" % (repo, path), "--jq", ".content"])
    if err:
        return None
    try:
        return base64.b64decode("".join(out.split())).decode("utf-8", errors="replace")
    except Exception:
        return None


def collect(text):
    """同一文件跑两口径：body=r18/r28 原尺，both=r29 M2 宽口径（含 frontmatter 兜底）。"""
    return {"body": rubric_hits(text, calibre="body"),
            "both": rubric_hits(text, calibre="both")}


def local_baseline(limit=400):
    rows = []
    for md in sorted(GS_ROOT.glob("*/SKILL.md"))[:limit]:
        if is_reparse_dir(md.parent):
            continue
        try:
            rows.append(collect(md.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            continue
    return rows


def summarize(name, items):
    """items = [{body:{...}, both:{...}}]；输出两口径各自的逐列百分比。"""
    n = len(items)
    out = {"name": name, "n": n}
    if not n:
        return out
    for cal in ("body", "both"):
        per = {k: round(100.0 * sum(1 for it in items if it[cal][k]) / n, 1) for k in RUBRIC_RX}
        per["all_six"] = round(100.0 * sum(
            1 for it in items if all(it[cal][k] for k in RUBRIC_RX)) / n, 1)
        out[cal] = per
    return out


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", nargs="*", default=REPOS)
    ap.add_argument("--cap", type=int, default=30, help="每仓最多取多少个 SKILL.md（防超大仓拉爆）")
    ap.add_argument("--json")
    ap.add_argument("--against", help="与已归档 JSON 对账正文口径（防改尺时静默动了历史数字）")
    args = ap.parse_args()

    ours = summarize("本体系 D:\\global_skills", local_baseline())
    if ours["n"] == 0:
        print("FAIL(R247): 本方基线枚举 0，无法对比")
        return 2
    rows = [ours]
    fetched_any = 0
    for repo in args.repos:
        paths, err = skill_paths(repo)
        if err:
            print("  %-34s 取清单失败: %s" % (repo, err))
            continue
        use = paths[: args.cap]
        hits, failed = [], 0
        for p in use:
            t = fetch(repo, p)
            if t is None:
                failed += 1
                continue
            hits.append(collect(t))
        if not hits:
            print("  %-34s 无可用文件（清单 %d，取回失败 %d）" % (repo, len(paths), failed))
            continue
        fetched_any += 1
        rows.append(summarize(repo, hits))
        print("  %-34s 树内 %d 个 SKILL.md，实取 %d 个（失败 %d）" % (repo, len(paths), len(hits), failed))

    if fetched_any == 0:
        print("FAIL(R247): 对手侧一个文件都没取到，禁止输出对比结论")
        return 2

    cols = list(RUBRIC_RX.keys()) + ["all_six"]
    for cal, title in (("body", "正文口径（r18/r28 原尺，只认标题锚点）"),
                       ("both", "宽口径（r29 M2：frontmatter description 亦可命中）")):
        print("\n=== 六段解剖 A/B · %s ===" % title)
        print("%-34s %5s %s" % ("对象", "n", "".join("%14s" % c[:13] for c in cols)))
        for r in rows:
            per = r.get(cal) or {}
            print("%-34s %5d %s" % (r["name"], r["n"],
                                    "".join("%13.1f%%" % per.get(c, 0.0) for c in cols)))
    print("\n差值（宽口径 - 正文口径，仅本体系一列说明口径水分有多大）:")
    ours_b, ours_x = rows[0].get("body") or {}, rows[0].get("both") or {}
    print("  " + "  ".join("%s %+.1f" % (c, ours_x.get(c, 0.0) - ours_b.get(c, 0.0)) for c in cols))
    print("\n读法：两口径禁止混列引用。rationalizations / verification 两列在两口径下差值最小，"
          "\n     ⇒ 这两段才是真缺口；overview / when_to_use 的差距里含标题风格差异，须以宽口径为准。")
    if args.against:
        # 只对本方一行做逐列对账：对手侧星标/文件数会随上游漂移，不是"改尺"的判据。
        old = json.loads(Path(args.against).read_text(encoding="utf-8"))
        prev = None
        for r in old.get("rows", []):
            if r.get("name") == rows[0]["name"] or "global_skills" in str(r.get("name", "")):
                prev = r
                break
        if prev is None:
            print("\n对账 %s: 归档里找不到本方行 -> 无法对账，判失败" % args.against)
            return 2
        prev_body = prev.get("body", prev)  # v1 行是扁平的，本身就是正文口径
        drift = []
        for c in cols:
            a, b = float(prev_body.get(c, 0.0)), float(ours_b.get(c, 0.0))
            if abs(a - b) > 0.05:
                drift.append("%s %.1f->%.1f" % (c, a, b))
        if drift:
            print("\n对账 %s: 正文口径漂移 %s（改尺不得动历史数字）" % (args.against, "; ".join(drift)))
            return 2
        print("\n对账 %s: 正文口径 %d 列全等 ✅（宽口径为新增列，未触碰历史判据）" % (args.against, len(cols)))
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"schema": "rubric-ab-v2", "rows": rows, "repos_requested": args.repos,
             "cap": args.cap, "calibres": ["body", "both"],
             "rubric_source": "skill_structure_rubric_scan.RUBRIC_RX",
             "frontmatter_calibre_source": "description_baseline_scan.{TRIGGER_RE,PROCESS_RE,MIN_DO_LEN}"},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print("JSON -> %s" % args.json)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as exc:
        sys.stderr.write("UNEXPECTED_FAILURE: %r -> 退出码 2（取证失败不得当结论）\n" % (exc,))
        raise SystemExit(2)
