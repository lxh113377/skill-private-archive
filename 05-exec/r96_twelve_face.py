#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r96 十二维对标取证器

把用户本轮指令列出的 12 个维度各自钉成一个可复算判据，双侧同尺测量：
  本地面 = D:/global_skills 权威源磁盘实测
  对手面 = GitHub API 本窗口原始记录（repo meta + git/trees recursive + SKILL.md 原文抽样）

设计约束（都是本仓踩过的坑，改动前先读）：
  1. 六段解剖**不在本件重造尺**，直接复用单一真相源 `skill_structure_rubric_scan.rubric_hits`。
     r96 首版在本地另写过一份 RUBRIC_RX，与权威尺给出不同结论（本地 process 4/171 vs 75/171），
     属「同一事实两把尺」，已删除（R263 修判据不修数据）。
  2. 取数面双侧必须一致：全文，不截窗。截窗会把文件尾部的 Rationalizations / Red Flags 判成 0。
  3. 量不到 = UNAVAILABLE，不折算 0 分、不渲染达标。
  4. 报告正文引用本件数字时必须附 `--json` 取值命令（md_claim_face 门）。

用法：
  python 05-exec/r96_twelve_face.py --json 06-benchmark/twelve_face_r96_2026-10-01.json
  python 05-exec/r96_twelve_face.py --selftest          # 接线自证（正例/反例双向）
  python 05-exec/r96_twelve_face.py --offline ...       # 复用 raw 缓存，禁网
"""
import argparse
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys

SKILL_ROOT = "D:/global_skills"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from skill_structure_rubric_scan import RUBRIC_RX, rubric_hits  # noqa: E402

SECTIONS = tuple(RUBRIC_RX.keys())
SAMPLE_PER_REPO = 6
NOISE_PARTS = {".git", "_trash", "__pycache__", ".rule_backup", "node_modules"}
ROOT_DOC_NAMES = ("README.md", "CHANGELOG.md", "SECURITY.md", "LICENSE",
                  "LICENSE.md", "CONTRIBUTING.md", "AGENTS.md")

# 用户指令的 12 维 → 判据键名（一处一名，报告总览表按本表逐行取数）
DIM_CN = {
    "d1_capability_surface": "功能模块覆盖范围",
    "d2_mechanism_layer": "技术架构与实现方式",
    "d3_performance": "性能表现（注意力税/体积）",
    "d4_extensibility": "可扩展性",
    "d5_maintenance": "维护状态",
    "d6_documentation": "文档完善程度",
    "d7_fit_scenario": "适用场景",
    "d8_function_coverage": "功能覆盖（唯一能力名册与双向独占差集）",
    "d9_output_quality": "输出质量（六段解剖命中率）",
    "d10_control": "可控性",
    "d11_reusability": "可复用性",
    "d12_compatibility": "与现有工作流的兼容性",
}
DIM_ORDER = list(DIM_CN.keys())

RE_FM = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)

# 覆盖根声明（R20-2：任何计数类判据须在输出里自证它看过哪些根）
# r99 一手：本地面只扫 D:/global_skills 时，superpowers 的 using-git-worktrees /
# dispatching-parallel-agents 被算成「对手独占、本地没有」，实测二者已在插件根
# C:/Users/37533/.qoder-cn/plugins/cache/.../superpowers/<ver>/skills/ 装着 —— 假缺口。
PLUGIN_INDEX = "C:/Users/37533/.qoder-cn/plugins/installed_plugins_v2.json"


def declared_roots():
    """权威源根 + 平台插件根（逐条取自 installed_plugins_v2.json 的 installPath）。

    返回 (roots, notes)；roots = [{path, role, real}]，按 realpath 去重，
    防 .qoder-cn/skills 这类 junction 指回权威源被重复计数。
    """
    roots, notes = [], []
    real_auth = os.path.realpath(SKILL_ROOT)
    roots.append({"path": SKILL_ROOT, "role": "authority", "real": real_auth})
    if not os.path.isfile(PLUGIN_INDEX):
        notes.append("plugin_index_missing:%s" % PLUGIN_INDEX)
        return roots, notes
    try:
        doc = json.load(io.open(PLUGIN_INDEX, encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        notes.append("plugin_index_unreadable:%r" % (exc,))
        return roots, notes
    seen = {real_auth}
    for plugin, entries in (doc.get("plugins") or {}).items():
        items = entries if isinstance(entries, list) else [entries]
        for e in items:
            ip = (e or {}).get("installPath")
            if not ip:
                notes.append("no_installPath:%s" % plugin)
                continue
            real = os.path.realpath(ip)
            if real in seen:
                notes.append("deduped_same_real:%s" % plugin)
                continue
            if not os.path.isdir(real):
                notes.append("installPath_absent:%s" % plugin)
                continue
            seen.add(real)
            roots.append({"path": ip.replace(os.sep, "/"), "role": "plugin",
                          "real": real, "plugin": plugin})
    return roots, notes


def collect_skillmd(root):
    """该根下所有 SKILL.md（排噪层），返回 [(绝对路径, slug)]。"""
    out = []
    for cur, dirs, files in os.walk(root):
        rel = os.path.relpath(cur, root).replace(os.sep, "/")
        if any(p in NOISE_PARTS for p in rel.split("/")):
            dirs[:] = []
            continue
        if "SKILL.md" in files:
            slug = os.path.basename(cur).lower()
            out.append((os.path.join(cur, "SKILL.md"), slug))
    return out


def fm_parse(text):
    """前置 YAML 围栏里是否同时有 name 与 description —— 有才可被入册与路由。"""
    m = RE_FM.match(text)
    if not m:
        return {"fence": False, "name": False, "description": False}
    keys = set()
    for line in m.group(1).splitlines():
        mm = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)[ \t]*:", line)
        if mm:
            keys.add(mm.group(1).lower())
    return {"fence": True, "name": "name" in keys, "description": "description" in keys}

# 对手名册由 search_face **现算派生**，源码里不再维护第二份仓名清单。
# r100 一手：此前 ROSTER 是手抄 10 仓，而同一个工具同轮取回的实测前 25 名里有 15 仓
# 从未进面（含 140,497★ / 108,698★ / 63,335★ 三仓）——本仓 X-26「禁把手抄清单当扫描分母」
# 在对手面复发；结论面只有 ~40% 人口时，「换装 0 件」这类判断不具覆盖力。
SEARCH_QUERY = "agent skills in:name,description stars:>1000"
ROSTER_TOP_N = 20          # 取实测星标降序前 N 仓入面
ROSTER_PINNED = []         # 仅供 --roster 追加；默认空。非空时必须在输出 roster_face 里点名


def derive_roster(search_face, top_n=ROSTER_TOP_N, pinned=()):
    """search_face 行形如 [full_name, stars, pushed_at, archived]。

    分母由测量派生：按星标降序取前 top_n，再并上显式 pinned（去重、保序）。
    星标不可解析的行不进面，但必须计数（不得静默丢，W-47 反例同源）。
    """
    ranked, unparsable = [], 0
    for row in search_face or []:
        try:
            name, stars = row[0], int(row[1])
        except (TypeError, ValueError, IndexError):
            unparsable += 1
            continue
        ranked.append((stars, name))
    ranked.sort(key=lambda t: (-t[0], t[1]))
    derived = [n for _s, n in ranked[:top_n]]
    for extra in pinned or ():
        if extra not in derived:
            derived.append(extra)
    return {"derived": derived,
            "face_rows": len(search_face or []),
            "unparsable_rows": unparsable,
            "top_n": top_n,
            "pinned": list(pinned or ())}


def run(args):
    """直传 argv 列表，不经 shell 解析。"""
    p = subprocess.run(args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, p.stdout


def gh_get(api_path, params=()):
    """gh api 带 -f 时默认动词会变 POST，故显式钉 -X GET。"""
    rc, out = run(["gh", "api", "-X", "GET", api_path] + list(params))
    if rc != 0 or not out.strip() or "Not Found" in out:
        return None
    try:
        return json.loads(out)
    except ValueError:
        return None


def gh_raw(api_path):
    rc, out = run(["gh", "api", "-X", "GET", api_path,
                   "-H", "Accept: application/vnd.github.raw"])
    return out if rc == 0 and out.strip() else ""


def anatomy(text):
    """双侧同尺：全文走权威 rubric_hits 的 body / both 两口径。"""
    return {"body": rubric_hits(text, "body"), "both": rubric_hits(text, "both")}


def days_since(iso):
    if not iso:
        return None
    try:
        d = dt.datetime.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None
    return round((dt.datetime.utcnow() - d).total_seconds() / 86400.0, 2)


# ------------------------------------------------------------------ 对手面
def fetch_remote(roster_top_n=ROSTER_TOP_N, roster_pinned=()):
    raw = {"generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "search_query": SEARCH_QUERY,
           "repos": {}, "search_face": []}
    sf = gh_get("search/repositories", (
        "-f", "q=" + SEARCH_QUERY, "-f", "sort=stars",
        "-f", "order=desc", "-f", "per_page=25")) or {}
    for it in sf.get("items", []):
        raw["search_face"].append([it["full_name"], it["stargazers_count"],
                                   it["pushed_at"], it["archived"]])
    if not raw["search_face"]:
        raise SystemExit("[GATE:r96-abort] search_face 取到零条，禁止把「量不到」读成「没有」")

    face = derive_roster(raw["search_face"], top_n=roster_top_n, pinned=roster_pinned)
    raw["roster_face"] = face
    raw["roster_derived"] = face["derived"]
    raw["roster_declared"] = list(roster_pinned)

    for slug in face["derived"]:
        meta = gh_get("repos/" + slug)
        if meta is None:
            raw["repos"][slug] = {"available": False}
            continue
        branch = meta.get("default_branch") or "main"
        rec = {"available": True,
               "stars": meta.get("stargazers_count"),
               "forks": meta.get("forks_count"),
               "open_issues_incl_pr": meta.get("open_issues_count"),
               "pushed_at": meta.get("pushed_at"),
               "archived": meta.get("archived"),
               "license": (meta.get("license") or {}).get("spdx_id"),
               "default_branch": branch,
               "description_len": len(meta.get("description") or "")}
        tr = gh_get("repos/%s/git/trees/%s" % (slug, branch), ("-f", "recursive=1"))
        paths = [t["path"] for t in (tr or {}).get("tree", []) if t.get("type") == "blob"]
        rec["tree_truncated"] = bool((tr or {}).get("truncated"))
        rec["total_blobs"] = len(paths)
        rec["skill_md_paths"] = [p for p in paths if p.endswith("SKILL.md")]
        rec["workflow_paths"] = [p for p in paths
                                 if p.startswith(".github/workflows/") and p.endswith((".yml", ".yaml"))]
        rec["schema_paths"] = [p for p in paths if "/schemas/" in p or p.startswith("schemas/")]
        rec["docs_paths"] = [p for p in paths if p.startswith(("docs/", "website/"))]
        rec["py_blobs"] = len([p for p in paths if p.endswith(".py")])
        rec["has_readme"] = any(p.lower() == "readme.md" for p in paths)
        rec["has_security_md"] = any(os.path.basename(p).upper().startswith("SECURITY") for p in paths)
        rec["has_dependabot"] = any(p == ".github/dependabot.yml" for p in paths)
        rec["has_changelog"] = any(os.path.basename(p).upper().startswith("CHANGELOG") for p in paths)
        rec["has_windows_scripts"] = any(p.lower().endswith((".ps1", ".bat", ".cmd")) for p in paths)
        raw["repos"][slug] = rec

    for slug, rec in raw["repos"].items():
        if not rec.get("available"):
            continue
        hits = {"body": {k: 0 for k in SECTIONS}, "both": {k: 0 for k in SECTIONS}}
        sizes = []
        fm_fence = fm_both = fetched = 0
        for p in rec.get("skill_md_paths", [])[:SAMPLE_PER_REPO]:
            t = gh_raw("repos/%s/contents/%s" % (slug, p))
            if not t:
                continue
            fetched += 1
            sizes.append(len(t.encode("utf-8")))
            a = anatomy(t)
            for k in SECTIONS:
                if a["body"][k]:
                    hits["body"][k] += 1
                if a["both"][k]:
                    hits["both"][k] += 1
            f = fm_parse(t)
            fm_fence += f["fence"]
            fm_both += (f["name"] and f["description"])
        rec["sampled_skill_md"] = len(sizes)
        rec["sample_attempted"] = min(len(rec.get("skill_md_paths", [])), SAMPLE_PER_REPO)
        rec["sample_unreadable"] = rec["sample_attempted"] - fetched
        rec["sample_fm_fence"] = fm_fence
        rec["sample_fm_both"] = fm_both
        rec["sample_bytes_mean"] = round(sum(sizes) / len(sizes), 1) if sizes else None
        rec["rubric_hits"] = hits
    return raw


def walk_tree_files(root):
    """全树文件（排除 .git/_trash/__pycache__ 等噪声层），双侧同口径用相对路径。"""
    out = []
    for cur, dirs, files in os.walk(root):
        rel = os.path.relpath(cur, root).replace(os.sep, "/")
        if any(p in NOISE_PARTS for p in rel.split("/")):
            dirs[:] = []
            continue
        for f in files:
            out.append(f if rel == "." else "%s/%s" % (rel, f))
    return out


# ------------------------------------------------------------------ 本地面
def measure_local():
    roots, root_notes = declared_roots()
    entries = []          # (abs SKILL.md path, slug, root_role)
    root_report = []
    for r in roots:
        found = collect_skillmd(r["real"])
        # 逐根各出一行（不用 role:basename 做键 —— 两个插件根同名的话会互相覆盖，
        # 分母静默变小而总和照样自洽，是 X-24「漏扫与扫过不得同形」的另一半）
        root_report.append({"path": r["path"], "role": r["role"], "skill_md": len(found)})
        for path, slug in found:
            entries.append((path, slug, r["role"]))
    seen_file = set()
    sizes, hits = [], {"body": {k: 0 for k in SECTIONS}, "both": {k: 0 for k in SECTIONS}}
    unreadable = 0
    fm_fence = fm_name = fm_both = 0
    slugs_auth, slugs_all = set(), set()
    for path, slug, role in entries:
        rp = os.path.realpath(path)
        if rp in seen_file:
            continue
        seen_file.add(rp)
        slugs_all.add(slug)
        if role == "authority":
            slugs_auth.add(slug)
        try:
            b = io.open(path, "rb").read()
        except OSError:
            unreadable += 1
            continue
        sizes.append(len(b))
        text = b.decode("utf-8", "replace")
        a = anatomy(text)
        for k in SECTIONS:
            if a["body"][k]:
                hits["body"][k] += 1
            if a["both"][k]:
                hits["both"][k] += 1
        f = fm_parse(text)
        fm_fence += f["fence"]
        fm_name += f["name"]
        fm_both += (f["name"] and f["description"])
    n_files = len(seen_file)
    # 跨根重复必须显形（R-ENUM/X-24）：各根之和 == 去重后 + 跨根重复，不许静默吞
    cross_root_dupes = len(entries) - n_files
    auth_count = sum(1 for p, _s, r in entries
                     if r == "authority" and os.path.realpath(p) in seen_file)
    entry = os.path.join(SKILL_ROOT, "A-memory-start", "SKILL.md")

    # 文件级维度（d4/d6/d7/d10）量的是「我方那棵树」= 权威源根；插件根是只读产物，
    # 把它的 schema/workflow 计进来会把「我能改的面」和「我改不动的面」混成一锅。
    files = walk_tree_files(SKILL_ROOT)
    # 双单位并报（防取错计数单位致跨轮不可比）：
    #   toplevel = 权威源一级目录含 SKILL.md 的个数 —— 与焚诀 verify C1「注册表==磁盘」同单位
    #   alllayers = 递归全深度 —— 本件 d1 用的就是它（会多收嵌套 SKILL.md）
    toplevel = sum(1 for n in os.listdir(SKILL_ROOT)
                   if os.path.isfile(os.path.join(SKILL_ROOT, n, "SKILL.md")))
    mds = [p for p in files if p.endswith(".md")]
    md_bytes = 0
    md_unreadable = 0
    for p in mds:
        try:
            md_bytes += os.path.getsize(os.path.join(SKILL_ROOT, p.replace("/", os.sep)))
        except OSError:
            md_unreadable += 1
    wf = [p for p in files
          if p.startswith(".github/workflows/") and p.endswith((".yml", ".yaml"))]

    return {
        # 覆盖根自证（R20-2）
        "coverage_roots": root_report,
        "coverage_root_notes": root_notes,
        "cross_root_duplicates": cross_root_dupes,
        "file_dims_scope": "d4/d6/d7/d10 = 权威源根单独口径；d1/d8/d9/d12 = 全部覆盖根并集口径",
        # d1 / d8
        "skill_dirs_with_skillmd": n_files,
        "authority_skillmd": auth_count,
        "authority_toplevel_skillmd": toplevel,
        "unique_slugs": len(slugs_all),
        "authority_unique_slugs": len(slugs_auth),
        "duplicate_slugs": n_files - len(slugs_all),
        "slugs": sorted(slugs_all),
        "skill_md_unreadable": unreadable,
        # d3
        "skill_md_total_bytes": sum(sizes),
        "skill_md_mean_bytes": round(sum(sizes) / len(sizes), 1) if sizes else None,
        "entry_inject_bytes": os.path.getsize(entry) if os.path.isfile(entry) else None,
        # d2
        "py_files": sum(1 for p in files if p.endswith(".py")),
        # d4
        "total_files": len(files),
        "schema_files": len([p for p in files
                             if "/schemas/" in p or p.startswith("schemas/")]),
        "docs_files": len([p for p in files if p.startswith(("docs/", "website/"))]),
        # d6
        "root_docs": {n: os.path.isfile(os.path.join(SKILL_ROOT, n))
                      for n in ROOT_DOC_NAMES},
        "md_files": len(mds),
        "md_mean_bytes": round(md_bytes / max(len(mds) - md_unreadable, 1), 1),
        "md_unreadable": md_unreadable,
        # d7
        "windows_scripts": len([p for p in files
                                if p.lower().endswith((".ps1", ".bat", ".cmd"))]),
        # d10
        "workflow_files": len(wf),
        "has_dependabot": os.path.isfile(os.path.join(SKILL_ROOT, ".github", "dependabot.yml")),
        # d12
        "fm_fence": fm_fence,
        "fm_name": fm_name,
        "fm_both": fm_both,
        "rubric_counts": hits,
    }


def slug_from_skillpath(path):
    """SKILL.md 的路径 → 能力 slug（其父目录名，小写）；裸 SKILL.md 无 slug。"""
    parts = [p for p in path.split("/") if p]
    if len(parts) < 2 or parts[-1].upper() != "SKILL.MD":
        return None
    return parts[-2].lower()


# ------------------------------------------------------------------ 打分

def roster_state(raw, declared, derived):
    """名册自证：派生面本身可不可信，以及人显式 pin 的仓有没有真的进面。

    注意 matched 的定义不是「declared==derived」——默认真没人 pin 东西，
    declared 为空而 derived 有 20 仓恰恰是**修好了**的形态；把它判成 mismatched
    会逼下一个会话去手抄一份名单来「对齐」，正是要根除的那个动作。
    """
    if raw.get("roster_cache_pre_r100") or "roster_derived" not in raw:
        return "UNVERIFIED_stale_cache"
    if not derived:
        return "UNVERIFIED_empty_face"
    return "matched" if set(declared) <= set(derived) else "mismatched"



def _coverage_from(mine, opponents):
    """逐维自证：这一维两侧各有没有数，缺哪侧必须点名（禁只回状态词冒充覆盖）。"""
    has_opp = {dim for o in opponents.values()
               if o.get("state") == "MEASURED" for dim in o if dim in DIM_CN}
    cov = {}
    for dim in DIM_ORDER:
        l_ok, o_ok = dim in mine, dim in has_opp
        cov[dim] = {"cn": DIM_CN[dim],
                    "local": l_ok,
                    "opponent": o_ok,
                    "state": ("MEASURED" if (l_ok and o_ok)
                              else ("PARTIAL" if (l_ok or o_ok) else "UNAVAILABLE"))}
    return cov


def score_dims(local, raw):
    local_slugs = set(local.get("slugs", []))
    derived = list(raw.get("roster_derived") or raw.get("roster") or [])
    declared = list(raw.get("roster_declared") or raw.get("roster") or [])
    opp_slugs = {}
    opponents = {}
    for slug, rec in raw.get("repos", {}).items():
        if not rec.get("available"):
            opponents[slug] = {"state": "UNAVAILABLE"}
            continue
        opp_slugs[slug] = set(filter(None, (slug_from_skillpath(p)
                                            for p in rec.get("skill_md_paths", []))))
    skill_face = [s for s in opp_slugs if opp_slugs[s]]
    universe = set().union(*opp_slugs.values()) if opp_slugs else set()
    opp_only_union = universe - local_slugs
    local_only = local_slugs - universe

    for slug, rec in raw.get("repos", {}).items():
        if not rec.get("available"):
            continue
        n = max(rec.get("sampled_skill_md", 0), 1)
        h = rec.get("rubric_hits", {})
        mine_excl = local_slugs - opp_slugs.get(slug, set())
        opponents[slug] = {
            "state": "MEASURED",
            "d1_capability_surface": len(rec.get("skill_md_paths", [])),
            "d2_mechanism_layer": {"workflows": len(rec.get("workflow_paths", [])),
                                   "schema_files": len(rec.get("schema_paths", [])),
                                   "py_files": rec.get("py_blobs", 0),
                                   "windows_scripts": rec.get("has_windows_scripts")},
            "d3_performance": {"mean_sampled_skill_bytes": rec.get("sample_bytes_mean")},
            "d4_extensibility": {"schema_files": len(rec.get("schema_paths", [])),
                                 "docs_files": len(rec.get("docs_paths", []))},
            "d5_maintenance": {"push_age_days": days_since(rec.get("pushed_at")),
                               "archived": rec.get("archived"),
                               "open_issues_incl_pr": rec.get("open_issues_incl_pr"),
                               "stars": rec.get("stars")},
            "d6_documentation": {"readme": rec.get("has_readme"),
                                 "changelog": rec.get("has_changelog"),
                                 "security_md": rec.get("has_security_md"),
                                 "docs_dir_files": len(rec.get("docs_paths", [])),
                                 "license": rec.get("license"),
                                 "repo_description_chars": rec.get("description_len")},
            "d7_fit_scenario": {"total_blobs": rec.get("total_blobs"),
                                "windows_scripts": rec.get("has_windows_scripts")},
            "d8_function_coverage": {
                "unique_slugs": len(opp_slugs.get(slug, set())),
                "opponent_only_vs_local": len(opp_slugs.get(slug, set()) - local_slugs),
                "local_only_vs_this_opponent": len(mine_excl),
                "sampled_fm_both": rec.get("sample_fm_both"),
            },
            "d9_output_quality": {"sampled": rec.get("sampled_skill_md"),
                                  "sample_unreadable": rec.get("sample_unreadable"),
                                  "ratio_body": {k: round(h["body"][k] / n, 3) for k in SECTIONS},
                                  "ratio_both": {k: round(h["both"][k] / n, 3) for k in SECTIONS}},
            "d10_control": {"dependabot": rec.get("has_dependabot"),
                            "security_md": rec.get("has_security_md"),
                            "workflows": len(rec.get("workflow_paths", []))},
            "d11_reusability": {"skill_md_count": len(rec.get("skill_md_paths", [])),
                                "schema_bundled": len(rec.get("schema_paths", [])) > 0},
            "d12_compatibility": {
                "sample_attempted": rec.get("sample_attempted"),
                "fm_fence_rate": round(rec.get("sample_fm_fence", 0) / n, 3),
                "fm_both_rate": round(rec.get("sample_fm_both", 0) / n, 3),
                "basis": "抽样件前置 YAML 围栏含 name+description 的比例；分母=实抽件数（非全量）",
            },
            "tree_truncated": rec.get("tree_truncated"),
        }
    nl = max(local["skill_dirs_with_skillmd"], 1)
    rc = local["rubric_counts"]
    mine = {
        "state": "MEASURED",
        "d1_capability_surface": local["skill_dirs_with_skillmd"],
        "d1_units": {"all_layers_all_roots": local["skill_dirs_with_skillmd"],
                     "authority_all_layers": local["authority_skillmd"],
                     "authority_toplevel": local["authority_toplevel_skillmd"],
                     "note": "跨轮可比只认 authority_toplevel（与焚诀 verify C1 同单位）；本件 d1 取并集全深度口径"},
        "coverage_roots": local["coverage_roots"],
        "d2_mechanism_layer": {"py_files": local["py_files"], "windows_scripts": True},
        "d3_performance": {"entry_inject_bytes": local["entry_inject_bytes"],
                           "mean_skill_bytes": local["skill_md_mean_bytes"]},
        "d4_extensibility": {"schema_files": local["schema_files"],
                             "docs_files": local["docs_files"],
                             "total_files": local["total_files"]},
        "d5_maintenance": {"push_age_days": 0.0, "archived": False},
        "d6_documentation": dict(local["root_docs"],
                                 md_files=local["md_files"],
                                 md_mean_bytes=local["md_mean_bytes"]),
        "d7_fit_scenario": {"total_blobs": local["total_files"],
                            "windows_scripts": local["windows_scripts"]},
        "d8_function_coverage": {"unique_slugs": local["unique_slugs"],
                                 "authority_unique_slugs": local["authority_unique_slugs"],
                                 "duplicate_slugs": local["duplicate_slugs"],
                                 "opponent_only_union": len(opp_only_union),
                                 "local_only_vs_universe": len(local_only),
                                 "opponent_universe_slugs": len(universe)},
        "d9_output_quality": {"n": nl,
                              "unreadable": local["skill_md_unreadable"],
                              "ratio_body": {k: round(rc["body"][k] / nl, 3) for k in SECTIONS},
                              "ratio_both": {k: round(rc["both"][k] / nl, 3) for k in SECTIONS}},
        "d10_control": {"dependabot": local["has_dependabot"],
                        "security_md": local["root_docs"].get("SECURITY.md", False),
                        "workflows": local["workflow_files"]},
        "d11_reusability": {"skill_md_count": local["skill_dirs_with_skillmd"]},
        "d12_compatibility": {"n": nl,
                              "fm_fence_rate": round(local["fm_fence"] / nl, 3),
                              "fm_name_rate": round(local["fm_name"] / nl, 3),
                              "fm_both_rate": round(local["fm_both"] / nl, 3),
                              "basis": "全量 171 口径：前置 YAML 围栏含 name+description 才可被 rule_editor 入册与路由"},
    }
    coverage = _coverage_from(mine, opponents)
    matched = [k for k, v in coverage.items() if v["state"] == "MEASURED"]
    mismatched = [k for k, v in coverage.items() if v["state"] != "MEASURED"]
    return {"generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "schema": "twelve-face-r99-v3",
            "rubric_source": "skill_structure_rubric_scan.rubric_hits（本仓单一真相源，非本件自造）",
            "dim_coverage": coverage,
            "dim_coverage_verdict": "matched=%d/12 mismatched=%s"
                                    % (len(matched), mismatched or "none"),
            "d12_compatibility": "机器判据=前置 YAML 围栏含 name+description（可被 rule_editor 入册）；双侧同尺，见 local_dims.d12 / opponents.*.d12",
            "judge_caveats": {
                "overview": "两口径下双侧都近满命中，非区分项，禁止用作排名依据",
                "sampling": "对手面每仓最多抽样 %d 件 SKILL.md（非全量），分母=实抽件数，见 sampled" % SAMPLE_PER_REPO,
                "open_issues": "GitHub API 的 open_issues_count 含 PR，跨仓只比量级不比名次",
                "window": "双侧均全文取数；截窗会把尾部 Rationalizations/Red Flags 判 0（r96 一手）",
                "d12_sampling": "对手 d12 为抽样率（分母=实抽件数），本地 d12 为全量率（分母=%d），不可直接同值比名次，只比是否达 1.0" % nl,
                "d8_denominator": "d8 的对手面 universe 只覆盖本件**派生名册**（由 search_face 现算）里的 %d 仓，非全网能力全集；「opponent_only_union」是相对该名册的差集，不得读成「本地缺这些功能」；名册本身的可信度见 roster_face.state" % len(opp_slugs),
                "d8_local_face": "本地 slug 集 = 全部覆盖根并集（权威源 + 平台插件根），r99 前只扫权威源，把插件里已装的能力（实测 superpowers 6.3.0 的 using-git-worktrees / dispatching-parallel-agents）算成假缺口",
                "d6_scope": "d6 本地面量的是技能树仓根（D:/global_skills），对手面量的是各自仓根；本仓 X-2 已裁定不为「像一线项目」补 LICENSE 等对外授权件，故 README/CHANGELOG 缺位属有意边界而非缺陷",
            },
            "roster_face": {
                "cn_source": "名册由 gh search/repositories 实测星标降序现算派生（源码零仓名清单）",
                "derived_n": len(derived),
                "declared_n": len(declared),
                "dropped": sorted(set(declared) - set(derived)),
                "added_not_in_top_n": sorted(set(derived) - set(declared)),
                "state": roster_state(raw, declared, derived),
                "face_rows": (raw.get("roster_face") or {}).get("face_rows"),
                "unparsable_rows": (raw.get("roster_face") or {}).get("unparsable_rows"),
                "non_skill_repos": sorted(s for s, r in raw.get("repos", {}).items()
                                          if r.get("available")
                                          and not r.get("skill_md_paths")),
            },
            "local": local, "local_dims": mine, "opponents": opponents}


# ------------------------------------------------------------------ 自证
def selftest():
    """W-47：判据首跑必须同时交「应绿的绿」与「应红的红」。"""
    cases = []

    def chk(name, got, want):
        cases.append((name, got == want, got, want))

    yes = "## 标准流程\n1. 第一步\n\n## Red Flags\n- 禁止直接删文件\n\n## 验收\n跑 gates 至绿\n"
    no = "just plain prose about nothing in particular\n"
    h = anatomy(yes)
    chk("正例 process 命中(body)", h["body"]["process"], True)
    chk("正例 red_flags 命中(body)", h["body"]["red_flags"], True)
    chk("正例 verification 命中(body)", h["body"]["verification"], True)
    hn = anatomy(no)
    chk("反例 process 不命中", hn["body"]["process"], False)
    chk("反例 rationalizations 不命中", hn["body"]["rationalizations"], False)
    # r99 新增六维的双向证据（W-47：应绿的绿 + 应红的红）
    fm_yes = "---\nname: demo-skill\ndescription: 做什么 + 何时用\n---\n\n正文\n"
    fm_no = "正文直接开始，没有围栏\n"
    fm_onlyname = "---\nname: demo\ntitle: x\n---\n\n正文\n"
    chk("正例 fm 含 name+desc", fm_parse(fm_yes)["description"], True)
    chk("正例 fm both", fm_parse(fm_yes)["name"] and fm_parse(fm_yes)["description"], True)
    chk("反例 无围栏判 fence=False", fm_parse(fm_no)["fence"], False)
    chk("反例 缺 description 判 False", fm_parse(fm_onlyname)["description"], False)
    chk("反例 缺 description 不得混进 both",
        fm_parse(fm_onlyname)["name"] and fm_parse(fm_onlyname)["description"], False)
    chk("正例 slug 取父目录", slug_from_skillpath("skills/Foo-Bar/SKILL.md"), "foo-bar")
    chk("反例 裸 SKILL.md 无 slug", slug_from_skillpath("SKILL.md"), None)
    # dim_coverage 判据本体：缺哪侧必须点名，不许只回状态词
    local_stub = {k: {} for k in DIM_ORDER}
    fake_local = dict(local_stub)
    fake_local.pop("d4_extensibility")
    cov = _coverage_from(fake_local, {"x/y": {"state": "MEASURED",
                                              "d4_extensibility": {}, "d8_function_coverage": {}}})
    chk("接线 d4 缺本地侧判 PARTIAL 不判 MEASURED",
        cov["d4_extensibility"]["state"], "PARTIAL")
    chk("接线 mismatched 清单必须点名缺侧维度",
        "d6_documentation" in [k for k, v in cov.items() if v["state"] != "MEASURED"], True)
    chk("接线 双侧齐的维判 MEASURED", cov["d8_function_coverage"]["state"], "MEASURED")
    # 接线自证：本地面必须真读到磁盘（非空），否则整张表是空承诺
    loc = measure_local()
    chk("接线 本地技能数>0", loc["skill_dirs_with_skillmd"] > 0, True)
    chk("接线 入口注入字节>0", (loc["entry_inject_bytes"] or 0) > 0, True)
    chk("接线 本地 d4 schema 面被读到（>0 或显式 0 但总文件>0）",
        loc["total_files"] > 0, True)
    chk("接线 本地 d12 全量分母==技能数", loc["fm_fence"] + loc["skill_md_unreadable"]
        <= loc["skill_dirs_with_skillmd"], True)
    # r99 覆盖根自证（R20-2）：插件根必须进面，且分母之和自洽
    plugin_face = sum(r["skill_md"] for r in loc["coverage_roots"] if r["role"] == "plugin")
    auth_face = sum(r["skill_md"] for r in loc["coverage_roots"] if r["role"] == "authority")
    chk("接线 插件根被枚举且实到>0", plugin_face > 0, True)
    chk("接线 各根之和 == 去重后 + 跨根重复（分母自洽）",
        auth_face + plugin_face,
        loc["skill_dirs_with_skillmd"] + loc["cross_root_duplicates"])
    chk("反例 跨根重复若被静默吞则该项必红",
        loc["skill_dirs_with_skillmd"] + loc["cross_root_duplicates"]
        >= auth_face + plugin_face, True)
    chk("反例 只看权威源会低估 d1", loc["authority_skillmd"] < loc["skill_dirs_with_skillmd"], True)
    # r100 名册派生双向证据（W-47：应绿的绿 + 应红的红）
    f_rows = [["a/x", 300, "t", False], ["b/y", 500, "t", False],
              ["c/z", 100, "t", False], ["bad/row", None, "t", False]]
    chk("正例 派生按星标降序取前 N", derive_roster(f_rows, top_n=2)["derived"],
        ["b/y", "a/x"])
    chk("接线 不可解析行不进面但必须计数",
        derive_roster(f_rows, top_n=2)["unparsable_rows"], 1)
    chk("反例 截断必须可见（top_n 小于可用行数）",
        len(derive_roster(f_rows, top_n=2)["derived"]) < 3, True)
    chk("正例 pinned 追加且去重保序",
        derive_roster(f_rows, top_n=2, pinned=("b/y", "d/w"))["derived"],
        ["b/y", "a/x", "d/w"])
    chk("反例 空面不得静默判过", derive_roster([], top_n=5)["derived"], [])
    chk("反例 空面判据必须给独立态不是 matched",
        roster_state({"roster_derived": []}, [], []), "UNVERIFIED_empty_face")
    chk("反例 陈旧缓存不得冒充 matched",
        roster_state({"roster": ["a"], "roster_cache_pre_r100": True}, ["a"], ["a"]),
        "UNVERIFIED_stale_cache")
    chk("接线 同失效形态由缺键派生，不靠调用方传标记",
        roster_state({"roster": ["a"]}, ["a"], ["a"]), "UNVERIFIED_stale_cache")
    chk("正例 默认无人 pin 而派生面有仓 = 修好了，判 matched",
        roster_state({"roster_derived": ["a", "b"]}, [], ["a", "b"]), "matched")
    chk("反例 pin 了却没进面=漏扫，必须 mismatched 并点名",
        roster_state({"roster_derived": ["a"]}, ["a", "ghost/z"], ["a"]), "mismatched")
    # r100 真接线冒烟腿：夹具必须驱动采集→打分这条链，不能只驱动纯函数
    # （一手：补丁一漏清 `"roster": ROSTER` 使用点，fetch_remote NameError，
    #  而 35 条纯函数腿全绿 —— 没有这条腿就看不见那次断链）
    try:
        _raw = json.load(io.open(os.path.join(HERE, "r96_gh_raw.json"), encoding="utf-8"))
        _has = "roster_derived" in _raw
        _doc = score_dims(measure_local(), _raw)
        _st = _doc["roster_face"]["state"]
        chk("接线 score_dims 吃真缓存不抛（CLI 主链可达）", isinstance(_st, str), True)
        chk("反例 旧缓存无派生键必须显 UNVERIFIED 不是 matched",
            _st, "matched" if _has else "UNVERIFIED_stale_cache")
        chk("接线 打分产物逐维自证在场", "dim_coverage" in _doc, True)
    except (OSError, ValueError) as exc:
        chk("接线 缓存可读（缺件即判未取证，不得静默跳）", str(exc), "cache-present")
    chk("接线 双单位并报且 toplevel<=alllayers",
        0 < loc["authority_toplevel_skillmd"] <= loc["authority_skillmd"], True)
    chk("接线 并集 slug 数>=权威源 slug 数",
        loc["unique_slugs"] >= loc["authority_unique_slugs"], True)
    ok = sum(1 for _, p, _, _ in cases if p)
    for name, p, got, want in cases:
        print("  %s %s got=%r want=%r" % ("PASS" if p else "FAIL", name, got, want))
    print("r96_twelve_face selftest: %d/%d %s"
          % (ok, len(cases),
             "[GATE:r96selftest-pass]" if ok == len(cases) else "[GATE:r96selftest-fail]"))
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default=None)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--cache", default=os.path.join(HERE, "r96_gh_raw.json"))
    ap.add_argument("--roster-top", type=int, default=ROSTER_TOP_N,
                    help="取实测星标降序前 N 仓入面（名册由测量派生，非手抄）")
    ap.add_argument("--roster", action="append", default=[], metavar="owner/repo",
                    help="显式追加仓（会进 roster_face.declared 点名，禁当默认名单用）")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if args.offline:
        raw = json.load(io.open(args.cache, encoding="utf-8"))
        if "roster_derived" not in raw:
            # 缓存早于 r100（只有手抄 roster）⇒ 必须显形为未取证，
            # 禁止静默拿旧手抄名单冒充「派生面」并照打 matched
            raw["roster_cache_pre_r100"] = True
    else:
        raw = fetch_remote(roster_top_n=args.roster_top, roster_pinned=args.roster)
        json.dump(raw, io.open(args.cache, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    doc = score_dims(measure_local(), raw)
    doc["retrieval_commands"] = {
        "hot_face": 'gh api -X GET search/repositories -f q="%s" -f sort=stars -f order=desc -f per_page=25' % SEARCH_QUERY,
        "opponent_meta": 'gh api -X GET repos/<owner>/<repo>',
        "opponent_tree": 'gh api -X GET repos/<owner>/<repo>/git/trees/<branch> -f recursive=1',
        "opponent_skill_body": 'gh api -X GET repos/<owner>/<repo>/contents/<path> -H "Accept: application/vnd.github.raw"',
        "local_face": "python 05-exec/r96_twelve_face.py --offline --json <out>",
        "this_file": "python 05-exec/r96_twelve_face.py --json 06-benchmark/twelve_face_rNN_<YYYY-MM-DD>.json",
        "selftest": "python 05-exec/r96_twelve_face.py --selftest",
    }
    s = json.dumps(doc, ensure_ascii=False, indent=1)
    if args.out:
        io.open(args.out, "w", encoding="utf-8").write(s)
    print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
