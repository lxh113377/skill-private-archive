# -*- coding: utf-8 -*-
"""r33_release_governance.py — 第十维「发布与治理文件面」实测采集器（只读，r33）。

量什么：对手**是否把技能/规则当可发布产品**的四个机读信号 ——
  license（仓库元数据）/ tags / releases / 治理五件是否存在。
为什么量这个（r33 结论前置）：r31 量 CI 存在性、r32 量 CI 有效性，两轮的共同结论是
  「严格度由是否有外部消费者决定，不由星标决定」。发布面正是"有无外部消费者"的**直接证据**，
  比 README 上写不写"production ready"可靠。

计数口径（引用时必须带上，否则会误读）：
  · tags / releases 用 `per_page=100` ⇒ **100 表示"≥100 触顶"，不是精确值**（本表用 `capped` 标记）。
  · 治理件按**根目录**精确文件名探测；`LICENSE` 无扩展名（部分仓用 `LICENSE.md`，两者都探，命中任一记有）。

用法：
    python 05-exec/r33_release_governance.py [--json 06-benchmark/release_governance_rNN_<date>.json]
退出码：0 全部对象探测成功 / 1 有对象探测失败（禁把失败当"没有该文件"，R247）/ 2 gh 不可用
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime

OBJECTS = [
    ("O1", "obra/superpowers"), ("O2", "anthropics/skills"), ("O3", "github/spec-kit"),
    ("O4", "ruvnet/ruflo"), ("O5", "mem0ai/mem0"), ("N-A", "addyosmani/agent-skills"),
    ("N-C", "sickn33/agentic-awesome-skills"), ("N-D", "vercel-labs/skills"),
    ("N-E", "mycelium-hq/ai-brain-starter"), ("O9", "mattpocock/skills"),
    ("N-B", "Fission-AI/OpenSpec"), ("SELF", "lxh113377/skill-private-archive"),
]
GOV_FILES = {
    "LICENSE": ("LICENSE", "LICENSE.md"),
    "SECURITY.md": ("SECURITY.md",),
    "CONTRIBUTING.md": ("CONTRIBUTING.md",),
    "CHANGELOG.md": ("CHANGELOG.md",),
    "CODE_OF_CONDUCT.md": ("CODE_OF_CONDUCT.md",),
}
CAP = 100


def gh(args):
    return subprocess.run(["gh"] + args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=90)


def probe_exists(slug, candidates):
    """返回 (命中?, 取数是否可信)。取数失败 ≠ 文件不存在 ⇒ 必须区分。"""
    trustworthy = False
    for name in candidates:
        r = gh(["api", "repos/%s/contents/%s" % (slug, name), "--jq", ".name"])
        if r.returncode == 0:
            return True, True
        if "404" in (r.stderr or "") or "Not Found" in (r.stderr or ""):
            trustworthy = True
    return False, trustworthy


def count_of(slug, sub):
    r = gh(["api", "repos/%s/%s?per_page=%d" % (slug, sub, CAP), "--jq", "length"])
    try:
        n = int(r.stdout.strip())
    except ValueError:
        return None
    return n


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args()

    if gh(["--version"]).returncode != 0:
        print("[GOV:UNVERIFIED] gh 不可用 ⇒ 拒绝输出「无治理件」结论（取不到不等于没有，R247）")
        return 2

    rows, errs = [], []
    for tag, slug in OBJECTS:
        m = gh(["api", "repos/%s" % slug, "--jq", '"\\(.stargazers_count)\\t\\(.license.spdx_id // \"none\")"'])
        if "\t" not in m.stdout:
            errs.append(slug)
            rows.append({"id": tag, "repo": slug, "error": (m.stderr or "")[:120]})
            continue
        stars, lic = m.stdout.strip().split("\t")
        gov, unsure = {}, []
        for key, cands in GOV_FILES.items():
            hit, ok = probe_exists(slug, cands)
            gov[key] = hit
            if not ok:
                unsure.append(key)
        tg, rl = count_of(slug, "tags"), count_of(slug, "releases")
        rows.append({"id": tag, "repo": slug, "stars": int(stars), "license": lic,
                     "tags": tg, "tags_capped": (tg == CAP), "releases": rl,
                     "releases_capped": (rl == CAP), "gov": gov,
                     "gov_count": sum(1 for v in gov.values() if v), "probe_untrusted": unsure})
        print("%-5s %-42s lic=%-11s tags=%-6s rel=%-6s 治理件=%d/5%s" % (
            tag, slug, lic,
            ("%d+" % tg if tg == CAP else str(tg)), ("%d+" % rl if rl == CAP else str(rl)),
            rows[-1]["gov_count"], ("  探测不可信:%s" % ",".join(unsure)) if unsure else ""))

    doc = {"schema": "release-governance-v1", "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
           "readonly": True,
           "benchmark": "r33 第十维 发布与治理文件面（实物探测，非 README 宣称）",
           "provenance_cmd": "gh api repos/<s>/contents/<f> --jq .name ; gh api repos/<s>/tags?per_page=100 --jq length",
           "input_evidence": {"repos": len(rows), "gov_files_probed": len(GOV_FILES),
                              "probe_cap": CAP},
           "denominator": {"objects_ok": len(rows) - len(errs), "failed": errs},
           "caveat": "tags/releases=100 表示触顶（>=100），禁当精确值引用；"
                     "LICENSE 探测含 LICENSE 与 LICENSE.md 两种命名",
           "objects": rows}
    print("-" * 72)
    print("覆盖根: gh api 只读 GET｜探测面=%d 仓 × %d 治理件 + tags/releases" % (len(rows), len(GOV_FILES)))
    if errs:
        print("[GOV:UNVERIFIED] %d 个对象探测失败：%s ⇒ 其缺失不得记为「无该文件」" % (len(errs), ",".join(errs)))
        rc = 1
    else:
        print("[GOV:OK] %d 个对象全部探测成功" % len(rows))
        rc = 0
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(json.dumps(doc, ensure_ascii=False, indent=1))
        print("JSON -> %s" % args.json)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
