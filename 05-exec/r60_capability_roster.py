# -*- coding: utf-8 -*-
r"""r60_capability_roster.py — 第 18 维「能力覆盖名册差集」生成器（r60 新开维度）.

存在理由：r18-r59 的十七个维度全部量的是**纪律面**（结构/描述/CI/供应链/账龄/可移植性...），
从未量过用户本轮原话里的第一维「功能模块覆盖范围」——即「对手有而我没有的能力名册」。
此前所有对比都在比同一批技能写得好不好，没有比**该有的有没有**。

判据面（一项事实只在一处判）：
  * 本件**不判**技能体量/描述质量/结构六段（那四面已有常驻判据）；只判**名册集合差**。
  * 对手选取按星标降序取前 N 且必须实测树里有 SKILL.md；目录型清单仓（README 挂着链接、树里
    0 个 SKILL.md）实测出局，不靠 README 宣称。
  * **计数单位 = 唯一 slug 名**（不是路径条数）。首版实测反例：`thedotmack/claude-mem` 把同一
    组技能复制进 8 个发行变体目录、`ComposioHQ/awesome-claude-skills` 一仓 864 条路径占对手面
    79.8%，按路径计数即把「覆盖率」算在复制件上（counting-unit 错，与「连接≠请求/行≠包含」同族）。
  * **生成分层**：单一父目录下 >=GENEROUS_CATALOG 个兄弟且共享同一后缀者判 `generated_catalog`
    层，单独成行、不进差集结论（那是集成清单不是能力名册）。
  * **盲区显形**：misc 占比 > BLIND_LIMIT 即印 [ROSTER:BLIND] 并把结论标 UNVERIFIED ——
    分类器看不见不等于不存在（Blindness is not zero）。
  * 树被 GitHub 截断（`truncated`）⇒ 该仓标 PARTIAL，不进差集，只登记。
  * 双路星标：search 面与 repos 面是**两个时刻**，星标本就在涨；容差内记为一致并留两值，
    超容差才判红（首版判「必须相等」，被 anthropics 178980 vs 178981 的单次增长判红 —— 那是
    判据缺陷不是数据缺陷，R263）。

取值：`python 05-exec/r60_capability_roster.py --json 06-benchmark/capability_roster_r60_2026-09-30.json`
      （`--skip-fetch` 复用 06-benchmark/roster_evidence/ 留档；`--describe <repo> <slug>` 取单件 frontmatter）
退出码：0 = 守恒成立且无盲区；1 = 守恒被破坏（各层之和 != 总数 / 双路星标超容差）；
        2 = UNVERIFIED（对手面为空 / 本地根取不到 / 无完整树仓 / misc 占比超阈 —— 一律不得静默读成「无差距」，R247）。
"""

import argparse
import base64
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EVIDENCE_DIR = os.path.join(ROOT, "06-benchmark", "roster_evidence")

AUTHORITY = r"D:\global_skills"
MARKETPLACE = r"C:\Users\37533\.workbuddy\skills-marketplace\skills"
PLUGIN_CACHE = r"C:\Users\37533\.qoder-cn\plugins\cache"

SEARCH_ROUTES = [
    ("route_topic", "topic:claude-skills"),
    ("route_name", "skill in:name claude OR agent"),
]
MAX_REPO_DETAIL = 14
STAR_TOL_RATIO = 0.02          # 双路星标容差：2% 内视为同一时刻的不同读数
BLIND_LIMIT = 0.30             # misc 占比超此值 => 分类器失明，结论标 UNVERIFIED
CATALOG_MIN_SIBLINGS = 20      # 同父目录兄弟数达此值 => 判生成式清单层

UNDERSCORE_NONSKILL = ("_trash", "_my-skills")

# 功能域透镜（先匹配先归位；未命中入 misc）。归类层是本轮自定透镜，非各仓官方分类。
DOMAIN_RULES = [
    ("memory_context", ("memory", "mem0", "mem-", "context", "recall", "note", "obsidian", "knowledge", "second-brain", "adhd", "observer")),
    ("planning_workflow", ("plan", "planning", "todo", "task", "workflow", "spec", "prd", "brainstorm", "ticket", "hyperplan", "triage", "step")),
    ("testing_debugging", ("test", "tdd", "debug", "diagnos", "qa", "verify", "dogfood", "assert", "repro", "review-")),
    ("review_refactoring", ("review", "refactor", "lint", "quality", "critique", "polish", "simplify", "simplification")),
    ("backend_api", ("api", "rest", "graphql", "backend", "java", "spring", "node", "server", "endpoint", "postman", "interface")),
    ("frontend_ui", ("ui", "ux", "frontend", "css", "design", "component", "react", "vue", "tailwind", "taste", "style", "styling", "landing", "artifact", "canvas", "brand", "banner", "brutalist", "minimalist", "dashboard", "figma")),
    ("writing_docs", ("doc", "writ", "blog", "readme", "copy", "content", "story", "novel", "essay", "article", "communicat", "email", "coauthor", "changelog", "guideline", "academy", "explain")),
    ("data_analysis", ("data", "analytic", "chart", "viz", "plot", "sql", "database", "excel", "csv", "pandas", "spreadsheet", "query", "cost-report")),
    ("office_documents", ("docx", "xlsx", "pptx", "pdf", "office", "slides", "presentation", "deck", "word", "powerpoint", "epub")),
    ("media_generation", ("image", "video", "audio", "gif", "svg", "art", "render", "ffmpeg", "animation", "music", "voice", "speak", "tts", "photo", "draw", "illustrat", "sprite")),
    ("research_search", ("search", "research", "web", "browse", "scrap", "seo", "news", "last30days", "discover", "trend", "understand", "gist", "summar")),
    ("browser_automation", ("browser", "playwright", "puppeteer", "cdp", "selenium", "puppet")),
    ("mcp_tooling", ("mcp", "tool", "plugin", "connector", "integration", "automation", "compose", "claude-code")),
    ("deploy_infra", ("deploy", "ci", "docker", "kubernetes", "k8s", "cloud", "vercel", "aws", "infra", "hosting", "release", "ship", "publish", "cdn", "unpublished")),
    ("security_privacy", ("security", "vuln", "audit", "pentest", "privacy", "secret", "guard")),
    ("skill_meta", ("skill", "agent", "subagent", "orchestrat", "swarm", "meta", "install", "grill", "domain-model")),
    ("vertical_domain", ("scientif", "academic", "medicine", "medical", "health", "finance", "legal", "market", "sales", "trading", "crypto", "ads", "nature", "physics", "chemistry", "bio", "education", "student", "homework", "exam", "nudge")),
    ("local_ai", ("asr", "ocr", "whisper", "llama", "embedding", "rag", "vlm", "local", "offline", "inference", "vram")),
    ("commerce_ops", ("shop", "store", "ecommerce", "order", "payment", "inventory", "supermarket", "chaoshi")),
]


def gh(*args):
    proc = subprocess.run(["gh", "api"] + list(args), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError("gh api %s rc=%s err=%s" % (list(args), proc.returncode,
                                                       proc.stderr.strip()[:200]))
    return json.loads(proc.stdout)


def domain_of(name):
    low = name.lower()
    for dom, keys in DOMAIN_RULES:
        for k in keys:
            if k in low:
                return dom
    return "misc"


def search_route(label, query):
    doc = gh("search/repositories", "-X", "GET", "-f", "q=" + query,
             "-f", "sort=stars", "-f", "order=desc", "-f", "per_page=20")
    out = [{"repo": it["full_name"], "stars": it["stargazers_count"],
            "pushed_at": it["pushed_at"], "route": label} for it in doc.get("items") or []]
    return out, int(doc.get("total_count") or 0)


def tree_skill_slugs(repo):
    doc = gh("repos/" + repo + "/git/trees/HEAD", "-X", "GET", "-f", "recursive=1")
    slugs = []
    for node in doc.get("tree") or []:
        p = node.get("path") or ""
        if node.get("type") != "blob":
            continue
        if p.endswith("/SKILL.md"):
            slugs.append(p[: -len("/SKILL.md")])
        elif p == "SKILL.md":
            slugs.append(".")
    return slugs, bool(doc.get("truncated")), str(doc.get("sha") or "")


def repo_detail(repo):
    doc = gh("repos/" + repo)
    return {"stars": doc["stargazers_count"], "pushed_at": doc["pushed_at"]}


def detect_catalog_dirs(slugs):
    """Return {parent_dir: [slugs]} for parents that look like generated integration lists."""
    by_parent = {}
    for s in slugs:
        parent = os.path.dirname(s)
        by_parent.setdefault(parent, []).append(s)
    cats = {}
    for parent, kids in by_parent.items():
        if len(kids) < CATALOG_MIN_SIBLINGS:
            continue
        leaves = [os.path.basename(k) for k in kids]
        suffixes = {}
        for l in leaves:
            for tok in ("-" + l.split("-")[-1],):
                suffixes[tok] = suffixes.get(tok, 0) + 1
        top = max(suffixes.items(), key=lambda kv: kv[1]) if suffixes else ("", 0)
        if top[1] >= CATALOG_MIN_SIBLINGS * 0.6:
            cats[parent] = {"members": len(kids), "shared_suffix": top[0], "hits": top[1]}
    return cats


def local_roots():
    faces = []
    for label, path in (("authority", AUTHORITY), ("marketplace", MARKETPLACE)):
        if not os.path.isdir(path):
            faces.append({"id": label, "path": path, "error": "root not a directory", "skills": None})
            continue
        names = [d for d in sorted(os.listdir(path))
                 if not d.startswith(".") and os.path.isfile(os.path.join(path, d, "SKILL.md"))]
        faces.append({"id": label, "path": path, "skills": sorted(names),
                      "underscore_dirs": [d for d in sorted(os.listdir(path))
                                          if d.startswith(UNDERSCORE_NONSKILL)]})
    plug = []
    if os.path.isdir(PLUGIN_CACHE):
        for p in sorted(os.listdir(PLUGIN_CACHE)):
            sd = os.path.join(PLUGIN_CACHE, p, "skills")
            if os.path.isdir(sd):
                plug += ["%s:%s" % (p, d) for d in sorted(os.listdir(sd))
                         if os.path.isfile(os.path.join(sd, d, "SKILL.md"))]
    faces.append({"id": "plugin", "path": PLUGIN_CACHE, "skills": sorted(plug)})
    return faces


def fetch_description(repo, slug):
    """Read one opponent SKILL.md frontmatter description (evidence grade for decisions)."""
    raw = gh("repos/%s/contents/%s/SKILL.md" % (repo, slug))
    text = base64.b64decode(raw["content"]).decode("utf-8", "replace")
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
    body = m.group(1) if m else text[:1200]
    dm = re.search(r"^description:\s*(.+)", body, re.M)
    return (dm.group(1).strip()[:400] if dm else body.strip()[:400])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out")
    ap.add_argument("--max-repos", type=int, default=MAX_REPO_DETAIL)
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--describe", nargs=2, metavar=("REPO", "SLUG"),
                    help="print one opponent skill's frontmatter description and exit")
    args = ap.parse_args()

    if args.describe:
        try:
            print(fetch_description(args.describe[0], args.describe[1]))
            return 0
        except Exception as e:                      # noqa: BLE001
            sys.stderr.write("[DESCRIBE:FAIL] %s\n" % e)
            return 2

    problems = []
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

    by_repo, route_totals = {}, {}
    for label, q in SEARCH_ROUTES:
        items, total = search_route(label, q)
        route_totals[label] = {"query": q, "total_count": total, "returned": len(items)}
        for it in items:
            cur = by_repo.get(it["repo"])
            if cur is None or it["stars"] > cur["stars"]:
                by_repo[it["repo"]] = dict(it, routes=[])
            if label not in by_repo[it["repo"]]["routes"]:
                by_repo[it["repo"]]["routes"].append(label)
    ranked = sorted(by_repo.values(), key=lambda x: -x["stars"])[: args.max_repos]

    repos_out, complete = [], []
    for cand in ranked:
        repo = cand["repo"]
        ev = os.path.join(EVIDENCE_DIR, repo.replace("/", "__") + ".json")
        try:
            if args.skip_fetch and os.path.isfile(ev):
                blob = json.loads(io.open(ev, encoding="utf-8-sig").read())
                slugs, trunc, det = blob["slugs"], blob["truncated"], blob["detail"]
            else:
                slugs, trunc, sha = tree_skill_slugs(repo)
                det = repo_detail(repo)
                _atomic_write(ev, json.dumps({"repo": repo, "sha": sha, "truncated": trunc,
                                              "slugs": slugs, "detail": det},
                                             ensure_ascii=False, indent=1))
        except Exception as e:                      # noqa: BLE001 - 取数失败必须显形
            problems.append("fetch %s failed: %s" % (repo, e))
            continue
        delta = det["stars"] - cand["stars"]
        tol_ok = abs(delta) <= max(2, int(cand["stars"] * STAR_TOL_RATIO))
        if not tol_ok:
            problems.append("dual-route stars超容差 %s search=%s detail=%s delta=%s"
                            % (repo, cand["stars"], det["stars"], delta))
        cats = detect_catalog_dirs(slugs)
        row = {"repo": repo, "stars_search": cand["stars"], "stars_detail": det["stars"],
               "pushed_at": det["pushed_at"], "skill_md_paths": len(slugs),
               "tree_truncated": trunc, "routes": cand["routes"],
               "generated_catalog_dirs": cats,
               "retrieval": ('gh api "repos/%s/git/trees/HEAD?recursive=1" --jq \'.tree|'
                             'map(select(.path|endswith("/SKILL.md")))|length\''
                             ' ; gh api "repos/%s" --jq \'.stargazers_count\'') % (repo, repo)}
        repos_out.append(row)
        if not trunc:
            curated = [s for s in slugs
                       if os.path.dirname(s) not in cats]
            complete.append((repo, curated))

    # 计数单位 = 唯一 slug 名（去发行变体与清单复制）
    name_owner = {}
    for repo, slugs in complete:
        for s in slugs:
            name_owner.setdefault(os.path.basename(s.rstrip("/")), []).append(repo)
    opp_names = sorted(name_owner)
    buckets = {}
    for n in opp_names:
        buckets.setdefault(domain_of(n), []).append(n)
    if sum(len(v) for v in buckets.values()) != len(opp_names):
        problems.append("opponent partition sum != unique names %s" % len(opp_names))

    faces = local_roots()
    local_union = sorted({os.path.basename(s.rstrip("/"))
                          for f in faces if f.get("skills") for s in f["skills"]})
    our_buckets = {}
    for n in local_union:
        our_buckets.setdefault(domain_of(n), []).append(n)
    if sum(len(v) for v in our_buckets.values()) != len(local_union):
        problems.append("local partition sum != unique names %s" % len(local_union))
    if not complete:
        problems.append("no opponent repo with a complete tree => empty face, refuse to judge")
    if not local_union:
        problems.append("local union is empty => roots unreadable, refuse to judge clean")

    blind_share = len(buckets.get("misc", [])) / float(len(opp_names)) if opp_names else 1.0
    rows = []
    for dom in sorted(set(buckets) | set(our_buckets)):
        on = buckets.get(dom, [])
        mine = our_buckets.get(dom, [])
        missing = [n for n in on if n not in set(local_union)]
        contrib = {}
        for n in missing:
            for r in name_owner[n]:
                contrib[r] = contrib.get(r, 0) + 1
        rows.append({"domain": dom, "opponent_unique": len(on), "ours_unique": len(mine),
                     "opponent_only_unique": len(missing),
                     "coverage_pct": round(100.0 * (len(on) - len(missing)) / len(on), 1) if on else None,
                     "top_contrib_repos": sorted(contrib.items(), key=lambda kv: -kv[1])[:3],
                     "opponent_only_sample": missing[:15]})

    doc = {
        "schema": "capability-roster-r60-v2",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "readonly": True,
        "dimension": 18,
        "counting_unit": "unique slug basename (not tree paths); generated-catalog dirs excluded",
        "claims_face": "SKILL.md blob 面（git trees recursive=1，仅未截断仓库，已剔生成式清单目录）；"
                       "星标为 search 面与 repos 面双路读数（两个时刻，容差 2% 内记一致）；"
                       "域分类是本轮自定透镜，非各仓官方分类",
        "search_routes": route_totals,
        "repos": repos_out,
        "totals": {"repos_measured": len(repos_out), "repos_complete": len(complete),
                   "opponent_unique_names": len(opp_names),
                   "local_unique_names": len(local_union),
                   "opponent_only_unique": sum(r["opponent_only_unique"] for r in rows)},
        "blind_share_misc": round(blind_share, 4),
        "blind_limit": BLIND_LIMIT,
        "verdict_state": "UNVERIFIED" if blind_share > BLIND_LIMIT else "MEASURED",
        "domains": rows,
        "local_faces": [{"id": f["id"],
                         "count": len(f["skills"]) if f.get("skills") is not None else 0,
                         "error": f.get("error")} for f in faces],
        "problems": problems,
        "note": "同名即记为已覆盖（保守口径，低估差距不低估自己）；PARTIAL 仓不进差集。",
    }

    print("第 18 维 能力覆盖名册差集 ｜ 对手完整仓 %d ｜ 唯一名册 %d ｜ 本地并集 %d ｜ misc 盲区占比 %.1f%%"
          % (len(complete), len(opp_names), len(local_union), 100 * blind_share))
    print("%-22s %5s %5s %8s %7s" % ("domain", "opp", "ours", "onlyOpp", "cover%"))
    for r in rows:
        print("%-22s %5d %5d %8d %7s" % (r["domain"], r["opponent_unique"], r["ours_unique"],
                                         r["opponent_only_unique"], r["coverage_pct"]))
    if problems:
        print("[ROSTER:FAIL] " + " ; ".join(problems))
        rc = 1
    elif blind_share > BLIND_LIMIT:
        print("[ROSTER:BLIND] misc %.1f%% 超阈 %.0f%% ⇒ 分类器有盲区，本轮结论上限只到 UNVERIFIED"
              % (100 * blind_share, 100 * BLIND_LIMIT))
        rc = 2
    else:
        print("[ROSTER:PASS] 分区守恒成立，盲区在阈内")
        rc = 0
    if args.out:
        _atomic_write(args.out, json.dumps(doc, ensure_ascii=False, indent=1))
        print("证据件: %s" % args.out)
    return rc


def _atomic_write(path, text):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


if __name__ == "__main__":
    sys.exit(main())
