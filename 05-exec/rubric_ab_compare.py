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
from skill_structure_rubric_scan import RUBRIC_RX, GS_ROOT, is_reparse_dir  # 同一把尺

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


def apply_rubric(text):
    body = text.split("---", 2)[-1] if text.startswith("---") else text
    return {k: any(rx.search(body) for rx in rxs) for k, rxs in RUBRIC_RX.items()}


def local_baseline(limit=400):
    rows = []
    for md in sorted(GS_ROOT.glob("*/SKILL.md"))[:limit]:
        if is_reparse_dir(md.parent):
            continue
        try:
            rows.append(apply_rubric(md.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            continue
    return rows


def summarize(name, hits):
    n = len(hits)
    if not n:
        return {"name": name, "n": 0}
    per = {k: round(100.0 * sum(1 for h in hits if h[k]) / n, 1) for k in RUBRIC_RX}
    per["all_six"] = round(100.0 * sum(1 for h in hits if all(h[k] for k in RUBRIC_RX)) / n, 1)
    per.update({"name": name, "n": n})
    return per


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", nargs="*", default=REPOS)
    ap.add_argument("--cap", type=int, default=30, help="每仓最多取多少个 SKILL.md（防超大仓拉爆）")
    ap.add_argument("--json")
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
            hits.append(apply_rubric(t))
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
    print("\n=== 六段解剖 A/B（同一把尺，全部实测真实文件）===")
    print("%-34s %5s %s" % ("对象", "n", "".join("%14s" % c[:13] for c in cols)))
    for r in rows:
        print("%-34s %5d %s" % (r["name"], r["n"], "".join("%13.1f%%" % r.get(c, 0.0) for c in cols)))
    print("\n读法：本体系 all_six 与对手同为 0 时说明「六段齐备」并非行业既成标准，")
    print("      但单段差距（尤其 rationalizations / verification）才是可借的实物做法。")
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"schema": "rubric-ab-v1", "rows": rows, "repos_requested": args.repos,
             "cap": args.cap, "rubric_source": "skill_structure_rubric_scan.RUBRIC_RX"},
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
