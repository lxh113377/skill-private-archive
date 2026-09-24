# -*- coding: utf-8 -*-
"""r31_ci_surface.py — 对手「自动化验收面」实测采集器（只读，无写盘到受管根）。

对标口径（r31 N12）：量的是**对手判据在哪个执行面上跑**，实物 = `.github/workflows/*.yml` 实数，
不接受 README 宣称（r31 已因此推翻 comparison.md 落后项 #6，见报告 §7.5）。

用法：
    python 05-exec/r31_ci_surface.py [--json 06-benchmark/ci_surface_rNN_<date>.json]
只读性：全程仅 `gh api` GET；不 checkout、不写任何对手仓、不改本仓除 --json 指定件外的任何文件。
退出码：0 全部对象取数成功 / 1 有对象取数失败（禁把失败当 0 门，R247）/ 2 gh 不可用
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime

OBJECTS = [
    ("O1", "obra/superpowers"), ("O2", "anthropics/skills"), ("O3", "github/spec-kit"),
    ("O4", "ruvnet/ruflo"), ("O5", "mem0ai/mem0"), ("O6", "letta-ai/letta"),
    ("O7", "GreatScottyMac/roo-code-memory-bank"), ("O8", "GreatScottyMac/context-portal"),
    ("N-A", "addyosmani/agent-skills"), ("N-B", "Fission-AI/OpenSpec"),
    ("N-C", "sickn33/agentic-awesome-skills"), ("N-D", "vercel-labs/skills"),
    ("N-E", "mycelium-hq/ai-brain-starter"), ("N-F", "lucasrosati/claude-code-memory-setup"),
    ("O9", "mattpocock/skills"),
]
LOCAL_REPO = "lxh113377/skill-private-archive"


def gh(args):
    return subprocess.run(["gh"] + args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out = [0] * len(xs)
    for pos, i in enumerate(order):
        out[i] = pos + 1
    return out


def spearman(a, b):
    n = len(a)
    if n < 3:
        return None
    ra, rb = rank(a), rank(b)
    d2 = sum((ra[i] - rb[i]) ** 2 for i in range(n))
    return round(1 - 6 * d2 / (n * (n * n - 1)), 3)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="06-benchmark/ci_surface_latest.json")
    args = ap.parse_args()

    if gh(["--version"]).returncode != 0:
        print("[CI-SURFACE:UNVERIFIED] gh 不可用 ⇒ 拒绝输出「0 workflow」结论（R247）")
        return 2

    rows = []
    for tag, slug in OBJECTS:
        m = gh(["api", "repos/" + slug, "--jq",
                '"\\(.stargazers_count)\\t\\(.pushed_at[0:10])\\t\\(.open_issues_count)"'])
        if "\t" not in m.stdout:
            rows.append({"id": tag, "repo": slug, "error": (m.stderr or "")[:120]})
            continue
        stars, pushed, issues = m.stdout.strip().split("\t")
        w = gh(["api", "repos/%s/contents/.github/workflows" % slug, "--jq",
                '[.[] | select(.name | endswith(".yml")) | .name] | join(",")'])
        names = [x for x in (w.stdout or "").strip().split(",") if x.endswith(".yml")]
        rows.append({"id": tag, "repo": slug, "stars": int(stars), "pushed_at": pushed,
                     "open_issues": int(issues), "workflow_count": len(names),
                     "workflow_names": names})

    failed = [r["id"] for r in rows if "error" in r]
    ok = len(rows) - len(failed)
    loc = gh(["api", "repos/%s/contents/.github/workflows" % LOCAL_REPO, "--jq",
              '[.[] | select(.name | endswith(".yml")) | .name] | join(",")'])
    local_names = [x for x in (loc.stdout or "").strip().split(",") if x.endswith(".yml")]

    got = [r for r in rows if "error" not in r]
    rho = spearman([r["stars"] for r in got], [r["workflow_count"] for r in got])
    doc = {
        "schema": "ci-surface-v1", "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "readonly": True,
        "benchmark": "r31 N12 自动化验收面（对手实物 = .github/workflows/*.yml 实数，非 README 宣称）",
        "provenance_cmd": 'gh api repos/<slug>/contents/.github/workflows --jq \'[.[]|select(.name|endswith(".yml"))|.name]|join(",")\'',
        "denominator": {"objects": len(rows), "api_calls_ok": ok, "failed_ids": failed},
        "input_evidence": {"repos_queried": len(rows),
                          "workflows_total": sum(r.get("workflow_count", 0) for r in got)},
        "statistics": {"spearman_stars_vs_workflows": rho,
                       "note": "ρ≈0 或负 ⇒ 星标不是 CI 严格度的代理指标；选对手按机制同构度，不按星标（r31）"},
        "objects": rows,
        "local": {"repo": LOCAL_REPO, "workflow_names": local_names,
                  "coverage_note": "gates.yml 只跑可移植 3/5 门，其余显式 SKIPPED-BY-DESIGN"},
        "note": "只算 .yml；spec-kit/OpenSpec/lucas 的 workflows 目录内含说明 .md，已按扩展名排除",
    }
    with open(args.json, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print("对象 %d（取数成功 %d，失败 %s）/ workflow 合计 %d / Spearman(stars,wf)=%s"
          % (len(rows), ok, failed or "无", doc["input_evidence"]["workflows_total"], rho))
    print("JSON -> %s" % args.json)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
