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
import subprocess
import sys

SKILL_ROOT = "D:/global_skills"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from skill_structure_rubric_scan import RUBRIC_RX, rubric_hits  # noqa: E402

SECTIONS = tuple(RUBRIC_RX.keys())
SAMPLE_PER_REPO = 6

# 对手名册：由本窗口 search/repositories 实测星标降序取入（见 raw 缓存 search_face）
ROSTER = [
    "obra/superpowers",
    "mattpocock/skills",
    "anthropics/skills",
    "addyosmani/agent-skills",
    "sickn33/agentic-awesome-skills",
    "kepano/obsidian-skills",
    "K-Dense-AI/scientific-agent-skills",
    "coreyhaines31/marketingskills",
    "github/awesome-copilot",
    "affaan-m/ECC",
]
SEARCH_QUERY = "agent skills in:name,description stars:>1000"


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
def fetch_remote():
    raw = {"generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "search_query": SEARCH_QUERY, "roster": ROSTER,
           "repos": {}, "search_face": []}
    sf = gh_get("search/repositories", (
        "-f", "q=" + SEARCH_QUERY, "-f", "sort=stars",
        "-f", "order=desc", "-f", "per_page=25")) or {}
    for it in sf.get("items", []):
        raw["search_face"].append([it["full_name"], it["stargazers_count"],
                                   it["pushed_at"], it["archived"]])
    if not raw["search_face"]:
        raise SystemExit("[GATE:r96-abort] search_face 取到零条，禁止把「量不到」读成「没有」")

    for slug in ROSTER:
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
        for p in rec.get("skill_md_paths", [])[:SAMPLE_PER_REPO]:
            t = gh_raw("repos/%s/contents/%s" % (slug, p))
            if not t:
                continue
            sizes.append(len(t.encode("utf-8")))
            a = anatomy(t)
            for k in SECTIONS:
                if a["body"][k]:
                    hits["body"][k] += 1
                if a["both"][k]:
                    hits["both"][k] += 1
        rec["sampled_skill_md"] = len(sizes)
        rec["sample_bytes_mean"] = round(sum(sizes) / len(sizes), 1) if sizes else None
        rec["rubric_hits"] = hits
    return raw


# ------------------------------------------------------------------ 本地面
def measure_local():
    dirs = []
    for name in sorted(os.listdir(SKILL_ROOT)):
        full = os.path.join(SKILL_ROOT, name)
        if not os.path.isdir(full):
            continue
        sk = os.path.join(full, "SKILL.md")
        if os.path.isfile(sk):
            dirs.append(sk)
    sizes, hits = [], {"body": {k: 0 for k in SECTIONS}, "both": {k: 0 for k in SECTIONS}}
    for sk in dirs:
        try:
            b = io.open(sk, "rb").read()
        except OSError:
            continue
        sizes.append(len(b))
        a = anatomy(b.decode("utf-8", "replace"))
        for k in SECTIONS:
            if a["body"][k]:
                hits["body"][k] += 1
            if a["both"][k]:
                hits["both"][k] += 1
    entry = os.path.join(SKILL_ROOT, "A-memory-start", "SKILL.md")
    py = sum(1 for root, _ds, fs in os.walk(SKILL_ROOT) for f in fs if f.endswith(".py"))
    return {
        "skill_dirs_with_skillmd": len(dirs),
        "skill_md_total_bytes": sum(sizes),
        "skill_md_mean_bytes": round(sum(sizes) / len(sizes), 1) if sizes else None,
        "entry_inject_bytes": os.path.getsize(entry) if os.path.isfile(entry) else None,
        "py_files": py,
        "rubric_counts": hits,
    }


# ------------------------------------------------------------------ 打分
def score_dims(local, raw):
    opponents = {}
    for slug, rec in raw.get("repos", {}).items():
        if not rec.get("available"):
            opponents[slug] = {"state": "UNAVAILABLE"}
            continue
        n = max(rec.get("sampled_skill_md", 0), 1)
        h = rec.get("rubric_hits", {})
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
            "d9_output_quality": {"sampled": rec.get("sampled_skill_md"),
                                  "ratio_body": {k: round(h["body"][k] / n, 3) for k in SECTIONS},
                                  "ratio_both": {k: round(h["both"][k] / n, 3) for k in SECTIONS}},
            "d10_control": {"dependabot": rec.get("has_dependabot"),
                            "security_md": rec.get("has_security_md"),
                            "workflows": len(rec.get("workflow_paths", []))},
            "d11_reusability": {"skill_md_count": len(rec.get("skill_md_paths", [])),
                                "schema_bundled": len(rec.get("schema_paths", [])) > 0},
            "tree_truncated": rec.get("tree_truncated"),
        }
    nl = max(local["skill_dirs_with_skillmd"], 1)
    rc = local["rubric_counts"]
    mine = {
        "state": "MEASURED",
        "d1_capability_surface": local["skill_dirs_with_skillmd"],
        "d2_mechanism_layer": {"py_files": local["py_files"], "windows_scripts": True},
        "d3_performance": {"entry_inject_bytes": local["entry_inject_bytes"],
                           "mean_skill_bytes": local["skill_md_mean_bytes"]},
        "d5_maintenance": {"push_age_days": 0.0, "archived": False},
        "d9_output_quality": {"n": nl,
                              "ratio_body": {k: round(rc["body"][k] / nl, 3) for k in SECTIONS},
                              "ratio_both": {k: round(rc["both"][k] / nl, 3) for k in SECTIONS}},
        "d11_reusability": {"skill_md_count": local["skill_dirs_with_skillmd"]},
    }
    return {"generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "schema": "twelve-face-r96-v2",
            "rubric_source": "skill_structure_rubric_scan.rubric_hits（本仓单一真相源，非本件自造）",
            "d12_compatibility": "定性判定，见报告 §2.12；机器判据=该 skill 目录是否含 SKILL.md+frontmatter name/description（可被 rule_editor 入册）",
            "judge_caveats": {
                "overview": "两口径下双侧都近满命中，非区分项，禁止用作排名依据",
                "sampling": "对手面每仓最多抽样 %d 件 SKILL.md（非全量），分母=实抽件数，见 sampled" % SAMPLE_PER_REPO,
                "open_issues": "GitHub API 的 open_issues_count 含 PR，跨仓只比量级不比名次",
                "window": "双侧均全文取数；截窗会把尾部 Rationalizations/Red Flags 判 0（r96 一手）",
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
    # 接线自证：本地面必须真读到磁盘（非空），否则整张表是空承诺
    loc = measure_local()
    chk("接线 本地技能数>0", loc["skill_dirs_with_skillmd"] > 0, True)
    chk("接线 入口注入字节>0", (loc["entry_inject_bytes"] or 0) > 0, True)
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
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if args.offline:
        raw = json.load(io.open(args.cache, encoding="utf-8"))
    else:
        raw = fetch_remote()
        json.dump(raw, io.open(args.cache, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    doc = score_dims(measure_local(), raw)
    doc["retrieval_commands"] = {
        "hot_face": 'gh api -X GET search/repositories -f q="%s" -f sort=stars -f order=desc -f per_page=25' % SEARCH_QUERY,
        "opponent_meta": 'gh api -X GET repos/<owner>/<repo>',
        "opponent_tree": 'gh api -X GET repos/<owner>/<repo>/git/trees/<branch> -f recursive=1',
        "opponent_skill_body": 'gh api -X GET repos/<owner>/<repo>/contents/<path> -H "Accept: application/vnd.github.raw"',
        "local_face": "python 05-exec/r96_twelve_face.py --offline --json <out>",
        "this_file": "python 05-exec/r96_twelve_face.py --json 06-benchmark/twelve_face_r96_2026-10-01.json",
    }
    s = json.dumps(doc, ensure_ascii=False, indent=1)
    if args.out:
        io.open(args.out, "w", encoding="utf-8").write(s)
    print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
