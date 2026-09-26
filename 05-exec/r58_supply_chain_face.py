# -*- coding: utf-8 -*-
"""r58 第 17 维取值件生成器：供应链安全面（动作固定 + 依赖更新 + 漏洞/密钥防护）。

对手名册沿用 comparison.md 的常驻集；每一面都取**两路**（r51/r52/r56 三轮实证：
单路取数在本赛道必翻车 —— `/actions/workflows` 含平台侧条目、`open_issues` 含 PR）。

测的四面：
  A 动作固定面：`.github/workflows/*` 里 `uses:` 引用中 pin 到 40 位 commit SHA 的比例
    （浮动 `@v4`/`@main` 是 tag/branch 移动即生效的供应链入口，GitHub 官方推荐 pin 到不可变 SHA）
  B 依赖更新面：`.github/dependabot.yml` 是否存在（谁替你把 A 的 SHA 往前推）
  C 漏洞/密钥面：workflow 正文含 codeql / dependency-review / secret 扫描者计数 + SECURITY.md 存在性
  D issue 面：`open_issues_count`（含 PR）与 `/issues?state=open`（纯 issue）**双列**，只写一路即虚高
"""
import datetime
import glob
import io
import json
import os
import re
import subprocess
import sys

REPOS = ["github/spec-kit", "obra/superpowers", "anthropics/skills", "addyosmani/agent-skills",
         "ruvnet/ruflo", "mem0ai/mem0", "sickn33/agentic-awesome-skills",
         "vercel-labs/skills", "mycelium-hq/ai-brain-starter", "pre-commit/pre-commit"]
# ⚠️ r58 实测纠错：本仓常驻页 comparison.md 把它写成 `mycelium/ai-brain-starter`，该 owner 下 404；
#    真名 = `mycelium-hq/ai-brain-starter`（`gh api repos/mycelium-hq/ai-brain-starter` 实连通）。
#    教训：对手全名必须 `gh api` 实测，不能从本页表头抄（P0.1 严禁猜测标识符）。
USES_RX = re.compile(r"^\s*(?:-\s*)?uses:\s*([^#\s]+)", re.M)
SHA_RX = re.compile(r"@[0-9a-f]{40}$")
VULN_RX = re.compile(r"codeql|dependency-review|secret[-_ ]?scan|gitleaks|trufflehog|snyk|osv", re.I)


def gh(args):
    p = subprocess.run(["gh"] + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, p.stdout, p.stderr


def contents_dir(repo, path):
    """目录清单（仅取文件名清单，正文不在此处）。
    ⚠️ 实测教训（r58 首跑）：`contents/<目录>` 返回的条目 **不含 content 内联正文**，
    据此判 `uses:` 会得到「全仓 0 处引用」的假结果 —— 必须逐文件走 raw Accept 再取一次。"""
    rc, out, err = gh(["api", "repos/%s/contents/%s" % (repo, path)])
    if rc != 0:
        return None, (err or "").strip()[:90]
    try:
        data = json.loads(out)
    except ValueError:
        return None, "非 JSON 响应"
    if isinstance(data, dict):
        data = [data]
    return [{"name": e.get("name", ""), "path": e.get("path", ""), "size": e.get("size", 0)}
            for e in data if e.get("type") == "file"], ""


def raw_file(repo, path):
    rc, out, _ = gh(["api", "-H", "Accept: application/vnd.github.raw+json",
                     "repos/%s/contents/%s" % (repo, path)])
    return out if rc == 0 and out else ""


def uses_face(bodies):
    total = pinned = 0
    floating = []
    for name, body in bodies:
        for m in USES_RX.finditer(body):
            ref = m.group(1)
            total += 1
            if SHA_RX.search(ref):
                pinned += 1
            else:
                floating.append("%s:%s" % (name, ref))
    return total, pinned, floating


def repo_retrieval(repo):
    """逐仓 ≥2 条独立取值命令，**换行拼接为单个字符串**。
    W-28 不变式的实现是 `re.split(r"[;；\\n]", str(item["retrieval"]))` ⇒ 给 list 会被 str() 成
    `"['a', 'b']"`（无分隔符）而判「不足两条」—— r58 首跑即栽在此，教训：接线前先读判据本体。"""
    return "\n".join([
        "gh api -H \"Accept: application/vnd.github.raw+json\" \"repos/%s/contents/.github/workflows/<file>\""
        "  # 逐文件取正文，本件 uses_total / uses_pinned_sha 即由这些正文数出" % repo,
        "gh api \"repos/%s/contents/.github/workflows\" --jq '.[].name'  # 自有 workflow 文件清单面（分母）" % repo,
        "gh api \"repos/%s/actions/workflows\" --jq .total_count  # API 总计面（含平台侧条目），对照 api_total_face" % repo,
        "gh api \"repos/%s/contents/.github/dependabot.yml\" --jq .name  # 404 即不存在（dependabot_yml 面）" % repo,
    ])


def main():
    argv = sys.argv[1:]
    out_json = argv[argv.index("--json") + 1] if "--json" in argv else None
    rows = []
    for repo in REPOS:
        wf, wf_err = contents_dir(repo, ".github/workflows")
        if wf is None:
            rows.append({"repo": repo, "workflow_dir_readable": False, "wf_error": wf_err,
                         "retrieval": repo_retrieval(repo)})
            print("  %-34s workflows 目录取不到：%s" % (repo, wf_err[:60]))
            continue
        bodies = []
        unread = []
        for w in wf:
            if not re.search(r"\.ya?ml$", w["name"]):
                continue
            body = raw_file(repo, w["path"])
            (bodies.append((w["name"], body)) if body else unread.append(w["name"]))
        total, pinned, floating = uses_face(bodies)
        rc, out, _ = gh(["api", "repos/%s/actions/workflows" % repo])
        api_face = json.loads(out).get("total_count") if rc == 0 else None
        dep_rc, _, _ = gh(["api", "repos/%s/contents/.github/dependabot.yml" % repo])
        sec_rc, _, _ = gh(["api", "repos/%s/contents/SECURITY.md" % repo])
        vuln_files = sorted(n for n, b in bodies if VULN_RX.search(b))
        rc2, out2, _ = gh(["api", "repos/%s" % repo])
        meta = json.loads(out2) if rc2 == 0 else {}
        # D 面双列：open_issues_count 含 PR；纯 issue 面走 search（r51 实测两路差 1.5–3.5 倍）
        rc3, out3, _ = gh(["api", "search/issues", "-f", "q=repo:%s is:issue is:open" % repo,
                           "-f", "per_page=1"])
        try:
            pure_issues = json.loads(out3).get("total_count") if rc3 == 0 else None
        except ValueError:
            pure_issues = None
        rows.append({
            "repo": repo, "workflow_dir_readable": True,
            "own_workflow_files": len(bodies), "unreadable_workflows": unread,
            "uses_total": total, "uses_pinned_sha": pinned,
            "pin_ratio_pct": (round(100.0 * pinned / total, 1) if total else None),
            "floating_sample": floating[:6],
            "api_total_face": api_face,
            "face_delta": (None if api_face is None else api_face - len(bodies)),
            "dependabot_yml": dep_rc == 0, "security_md": sec_rc == 0,
            "vuln_scan_workflows": vuln_files,
            "open_issues_incl_pr": meta.get("open_issues_count"),
            "pure_issue_face": pure_issues,
            "issue_face_delta": (None if (meta.get("open_issues_count") is None or pure_issues is None)
                                 else meta.get("open_issues_count") - pure_issues),
            "default_branch": meta.get("default_branch"),
            "pushed_at": meta.get("pushed_at"),
            "retrieval": repo_retrieval(repo)})
        print("  %-34s wf=%-3d uses=%-4d pin到SHA=%-4d %-7s dependabot=%-5s SECURITY=%-5s 漏洞面=%d api总计面=%s 差=%s" % (
            repo, len(bodies), total, pinned,
            ("%.0f%%" % (100.0 * pinned / total)) if total else "n/a",
            dep_rc == 0, sec_rc == 0, len(vuln_files), api_face,
            None if api_face is None else api_face - len(bodies)))

    # 我方侧不走 API 走本地文件：origin 上的 gates.yml 在 push 之前仍是旧字节，按 API 取会
    # 得到「与本报告结论相反」的面；本地工作树才是本体系 21 道门实际读到的那一份。
    own = []
    own_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           ".github", "workflows")
    own_bodies = []
    for f in sorted(glob.glob(os.path.join(own_dir, "*.yml")) + glob.glob(os.path.join(own_dir, "*.yaml"))):
        own_bodies.append((os.path.basename(f),
                           io.open(f, encoding="utf-8", errors="replace").read()))
    o_total, o_pinned, o_float = uses_face(own_bodies)
    own.append({"repo": "lxh113377/skill-private-archive",
                "face_note": "取**本地工作树**而非 origin：push 之前远端仍是改动前的 gates.yml，按 API 取会得出与本报告结论相反的面",
                "own_workflow_files": len(own_bodies), "uses_total": o_total,
                "uses_pinned_sha": o_pinned,
                "pin_ratio_pct": (round(100.0 * o_pinned / o_total, 1) if o_total else None),
                "floating_sample": o_float,
                "dependabot_yml": os.path.isfile(os.path.join(os.path.dirname(own_dir), "dependabot.yml")),
                "security_md": os.path.isfile(os.path.join(os.path.dirname(own_dir), "SECURITY.md")),
                "vuln_scan_workflows": [n for n, b in own_bodies if VULN_RX.search(b)],
                "retrieval": "\n".join([
                    "grep -rn \"uses:\" .github/workflows/   # lxh113377/skill-private-archive 本地工作树引用面",
                    "python 05-exec/r58_action_pin_guard.py  # 同一面的常驻判据口径（含 P2 配对 / P3 空面）",
                    "ls .github/dependabot.yml .github/SECURITY.md  # lxh113377/skill-private-archive 存在性面"])})
    print("  %-34s wf=%-3d uses=%-4d pin到SHA=%-4d dependabot=%s" % (
        "本仓（本地工作树）", len(own_bodies), o_total, o_pinned, own[0]["dependabot_yml"]))

    ok = [r for r in rows if r["workflow_dir_readable"]]
    doc = {"schema": "supply-chain-face-v1",
           "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "readonly": True,
           "enumerator": "05-exec/r58_supply_chain_face.py::main（contents 目录单次调用取正文 + /actions/workflows 双路）",
           "repos": rows,
           "own_repo_local_face": own,
           "face_totals": {"repos_measured": len(ok),
                           "with_dependabot": sum(1 for r in ok if r["dependabot_yml"]),
                           "with_security_md": sum(1 for r in ok if r["security_md"]),
                           "with_vuln_workflow": sum(1 for r in ok if r["vuln_scan_workflows"]),
                           "uses_total": sum(r["uses_total"] for r in ok),
                           "uses_pinned_sha": sum(r["uses_pinned_sha"] for r in ok)},
           "cross_check": {"repos_requested": len(REPOS), "repos_measured": len(ok),
                           "repos_unreadable": len(REPOS) - len(ok)},
           "claims_face": "每仓两路并列：`.github/workflows` contents 目录面（自有文件，含正文）与 `/actions/workflows.total_count`（API 总计面，含平台侧条目）；差值 face_delta 显式记录，不做单路结论",
           "retrieval": "\n".join([
               "python 05-exec/r58_supply_chain_face.py --json 06-benchmark/supply_chain_face_r58_2026-09-26.json",
               "逐仓 retrieval 字段：本件每行自带 ≥2 条独立取值命令（W-28 口径），件顶这条只是重跑入口"]),
           "decision_needed": ["本仓 gates.yml 两行浮动 uses 是否 pin 到 SHA（属供应链加固，改动可回滚）",
                               "是否新增 dependabot.yml 盯 github-actions 生态"]}
    print("-" * 66)
    t = doc["face_totals"]
    print("对手合计：measured=%d dependabot=%d SECURITY.md=%d 漏洞workflow=%d ｜ uses 引用 %d 处、pin 到 SHA %d 处（%.1f%%）" % (
        t["repos_measured"], t["with_dependabot"], t["with_security_md"], t["with_vuln_workflow"],
        t["uses_total"], t["uses_pinned_sha"],
        100.0 * t["uses_pinned_sha"] / t["uses_total"] if t["uses_total"] else 0.0))
    if out_json:
        d = os.path.dirname(out_json)
        if d:
            os.makedirs(d, exist_ok=True)
        with io.open(out_json, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print("写出 %s" % out_json)
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
