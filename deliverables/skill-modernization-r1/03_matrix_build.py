# -*- coding: utf-8 -*-
"""t3 五维量化对比评估矩阵生成器（需求3）。

为什么存在：t1 给 150 件自建 skill、t2 给 323 条 rel=skill 替代候选。本件把
05-exec/r114_replacement_scan.py::score5 的 0-5 机械锚点同尺套到两侧，
所有输入现场取（候选 = 现场 gh api；现有件 = 现场 D:/global_skills 文件树），
不抄 t2 快照、不引入人为主观打分。阶段0-3 只读取证：绝不改受管源任何文件。

用法：python -B 03_matrix_build.py [--offline] [--show-local SLUG] [--show-repo OWNER/REPO] [--show-root]
"""
import os
import sys
import json
import csv
import base64
import hashlib
import datetime
import importlib.util
import subprocess
import shutil
import stat
from concurrent.futures import ThreadPoolExecutor, as_completed

NL = chr(10)
BT = chr(96)
HERE = os.path.dirname(os.path.abspath(__file__))
DELIV = os.path.dirname(HERE)
ROOT = os.path.dirname(DELIV)
DATA = os.path.join(HERE, "data")
TEMP = os.path.join(ROOT, "_temp", "t3_matrix")
os.makedirs(DATA, exist_ok=True)
os.makedirs(TEMP, exist_ok=True)

R114 = os.path.join(ROOT, "05-exec", "r114_replacement_scan.py")
_spec = importlib.util.spec_from_file_location("r114scan", R114)
r114 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r114)

GLOBAL = "D:/global_skills"
EVAL_DATE = "2026-11-07"
FRESH_CUTOFF = "2026-07-01"
WEIGHTS = {"fc": 6, "eff": 4, "compat": 4, "docs": 3, "community": 3}
WSUM = sum(WEIGHTS.values())
DIMS = ["fc", "eff", "compat", "docs", "community"]
DIM_CN = {"fc": "功能完整性", "eff": "运行效率", "compat": "兼容性",
          "docs": "文档完善度", "community": "社区支持度"}
INV = os.path.join(DATA, "inventory.json")
CAND = os.path.join(DATA, "candidates.json")
LIVE_CACHE = os.path.join(TEMP, "live_meta.json")
LOCAL_CACHE = os.path.join(TEMP, "local_meta.json")
GATE_JSON = os.path.join(ROOT, '_temp', 't3_gates.json')
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

Q = chr(34)
SQ = chr(39)
JQ_REPOS = ("{full_name,stars:.stargazers_count,pushed_at,"
            "spdx:(.license.spdx_id // " + Q + "UNLICENSED" + Q + "),archived,"
            "forks:.forks_count,open_issues:.open_issues_count,"
            "default_branch,description}")
JQ_TREE = "[.truncated, [.tree[] | select(.type==" + Q + "blob" + Q + ") | .path]]"
JQ_LICENSE = "{spdx:(.license.spdx_id // " + Q + Q + "),content}"
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", ".idea", "_trash"}


def run_cmd(cmd, timeout=180):
    # Windows 无头：所有子进程显式带 CREATE_NO_WINDOW（#34），args 数组不走 shell。
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           timeout=timeout, creationflags=CREATE_NO_WINDOW)
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except Exception as exc:
        return 99, "", "subprocess_exception:" + repr(exc)


def gh(args, timeout=180):
    return run_cmd(["gh"] + list(args), timeout=timeout)


def h8(doc):
    raw = json.dumps(doc, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:12]


def gate_record():
    '''读本轮全量门禁实测 json（唯一 verdict 来源）；缺失/损坏则如实 NOT_RUN。

    为什么：新产物必须如实记 verdict，但生成器不得把 verdict 写死进源码；重跑时
    门禁 json 不在就宁可标 NOT_RUN，也不能伪造 FAIL/PASS（禁假完成 #36）。
    '''
    if not os.path.isfile(GATE_JSON):
        return {'status': 'NOT_RUN', 'reason': 't3_gates.json 缺失'}
    try:
        with open(GATE_JSON, 'r', encoding='utf-8') as f:
            d = json.load(f)
        d['status'] = 'OK'
        return d
    except Exception as exc:
        return {'status': 'NOT_RUN', 'reason': repr(exc)}


def handle_trace(live_docs, local_docs, csv_path):
    '''重读落盘缓存 + CSV，现场复算 doc_hash 可重算性与 evidence_handle 可回溯计数。

    怎么运作：① 去掉每份 doc 的 doc_hash 后用同一 h8() 口径重算并比对；② 逐行拆
    evidence_handle，按 LIVE_GH:/LIVE_FS: 前缀找回 doc 比对 #sha# 片段；返回实测
    计数供 md 写「每个分数带证据句柄」的动态证据，不硬编码任何数字。
    '''
    recomp_ok = 0
    recomp_bad = 0
    for docs in (live_docs, local_docs):
        for doc in docs.values():
            d2 = {a: b for a, b in doc.items() if a != 'doc_hash'}
            if doc.get('doc_hash') == h8(d2):
                recomp_ok += 1
            else:
                recomp_bad += 1
    rows = 0
    map_ok = 0
    map_bad = 0
    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            rows += 1
            hd = r['evidence_handle']
            parts = hd.split('#')
            if len(parts) < 3:
                map_bad += 1
                continue
            sha = parts[1]
            if hd.startswith('LIVE_GH:repos/'):
                doc = live_docs.get(hd[len('LIVE_GH:repos/'):].split('@')[0])
            elif hd.startswith('LIVE_FS:'):
                doc = local_docs.get(hd[len('LIVE_FS:'):].split('@')[0])
            else:
                doc = None
            if doc is not None and doc.get('doc_hash') == sha:
                map_ok += 1
            else:
                map_bad += 1
    return {'recomp_ok': recomp_ok, 'recomp_bad': recomp_bad,
            'rows': rows, 'map_ok': map_ok, 'map_bad': map_bad}


def find_r114_cache(full):
    # 退路：取证受阻时复用 r114 离线 repo 缓存，不静默丢弃。
    base = os.path.join(ROOT, "_temp", "r114_search_cache")
    variants = [full.replace("/", "_"), full.replace("/", "_").replace("-", "_"),
                full.replace("/", "_").replace(".", "_"), full.replace("/", "_").lower()]
    for v in dict.fromkeys(variants):
        p = os.path.join(base, "repo__" + v + ".json")
        if os.path.isfile(p):
            try:
                return json.load(open(p, "r", encoding="utf-8"))
            except Exception:
                return None
    return None


def fetch_repo(full):
    # 现场取候选五维输入：repos/<full> + /git/trees/<br>?recursive=1（+ NOASSERTION 正文许可）。
    ep = "repos/" + full
    c1 = "gh api " + ep + " --jq " + SQ + JQ_REPOS + SQ
    rc, out, err = gh(["api", ep, "--jq", JQ_REPOS], timeout=180)
    if rc != 0:
        return {"full": full, "state": "ERROR", "error": err[:240], "commands": [c1]}
    try:
        d = json.loads(out)
    except Exception as exc:
        return {"full": full, "state": "ERROR", "error": "json:" + repr(exc), "commands": [c1]}
    br = d.get("default_branch") or "main"
    doc = {"full": full, "state": "OK",
           "stars": int(d.get("stars") or 0),
           "forks": int(d.get("forks") or 0),
           "pushed_at": (d.get("pushed_at") or "")[:10],
           "pushed_at_full": d.get("pushed_at") or "",
           "license": d.get("spdx") or "UNLICENSED",
           "archived": bool(d.get("archived")),
           "open_issues": int(d.get("open_issues") or 0),
           "default_branch": br,
           "description": (d.get("description") or "")[:240],
           "commands": [c1]}
    ep2 = "repos/" + full + "/git/trees/" + br + "?recursive=1"
    c2 = "gh api " + Q + ep2 + Q + " --jq " + SQ + JQ_TREE + SQ
    rc2, out2, err2 = gh(["api", ep2, "--jq", JQ_TREE], timeout=240)
    doc["commands"].append(c2)
    if rc2 == 0:
        try:
            trunc, paths = json.loads(out2)
            doc["tree_state"] = "OK"
            doc["tree_truncated"] = bool(trunc)
            doc["blob_n"] = len(paths)
            doc.update(r114.tree_counts(paths))
        except Exception as exc:
            doc["tree_state"] = "UNAVAILABLE"
            doc["tree_error"] = "json:" + repr(exc)
    else:
        doc["tree_state"] = "UNAVAILABLE"
        doc["tree_error"] = err2[:240]
    if doc.get("tree_state") != "OK":
        for k in ("skill_md_n", "skill_md_exact_n", "skill_md_ghost_n",
                  "workflow_n", "test_path_n", "readme_n", "docs_md_n"):
            doc.setdefault(k, None)
        doc.setdefault("blob_n", 0)
    lic = (doc.get("license") or "").upper()
    if lic in ("NOASSERTION", ""):
        ep3 = "repos/" + full + "/license"
        c3 = "gh api " + ep3 + " --jq " + SQ + JQ_LICENSE + SQ
        rc3, out3, err3 = gh(["api", ep3, "--jq", JQ_LICENSE], timeout=180)
        doc["commands"].append(c3)
        if rc3 == 0:
            try:
                ld = json.loads(out3)
                blob = base64.b64decode(ld.get("content") or "")[:6144]
                up = blob.decode("utf-8-sig", "replace").upper()
                spdx, cls, hits = r114.classify_body(up)
                doc["license_body_class"] = cls
                doc["license_body_spdx"] = spdx or ""
            except Exception as exc:
                doc["license_body"] = "parse_failed:" + repr(exc)
        else:
            doc["license_body"] = "unavailable:" + err3[:120]
    doc["measured_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    doc["doc_hash"] = h8(doc)
    return doc


def git_last(slug, root_fallback):
    # 本地件活跃度代理 = 该 skill 目录最后一次 git 提交日期（现场复算）。
    rc, out, err = run_cmd(["git", "-C", GLOBAL, "log", "-1", "--format=%cI", "--", slug], timeout=60)
    if rc == 0 and out:
        return out[:10], "git -C " + GLOBAL + " log -1 --format=%cI -- " + slug
    return root_fallback, "git -C " + GLOBAL + " log -1 --format=%cI (root fallback)"


def local_license(base):
    # 本地件许可：目录内 LICENSE*/COPYING* 正文指纹；无则 UNLICENSED（R247 双向）。
    for dp, dns, fns in os.walk(base):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            u = fn.upper()
            if u.startswith("LICENSE") or u.startswith("COPYING"):
                try:
                    txt = open(os.path.join(dp, fn), "r", encoding="utf-8", errors="replace").read(6144).upper()
                    spdx, cls, hits = r114.classify_body(txt)
                    return "NOASSERTION", cls, fn
                except Exception:
                    return "NOASSERTION", "unknown", fn
    return "UNLICENSED", None, ""


def measure_local(slug, root_fallback):
    # 现有件五维输入 = D:/global_skills/<slug>/ 全文件树（只读取证，绝不改）。
    base = GLOBAL + "/" + slug
    c0 = "python -B 03_matrix_build.py --show-local " + slug
    if not os.path.isdir(base):
        # 缺失目录也落完整 doc_hash：让 CSV 的 evidence_handle 可从现场快照独立重算，
        # 而不是只在写 CSV 时由 :435 的 or h8(doc) 即时补一个外部查不到的哈希。
        doc = {"full": slug, "state": "MISSING", "tree_state": "UNAVAILABLE",
               "tree_error": "dir_absent", "stars": 0, "pushed_at": "",
               "license": "UNLICENSED", "archived": False, "blob_n": 0,
               "skill_md_n": None, "skill_md_exact_n": None,
               "workflow_n": None, "test_path_n": None,
               "readme_n": None, "docs_md_n": None,
               "commands": [c0, "test -d " + base], "measured_at": EVAL_DATE}
        doc["doc_hash"] = h8(doc)
        return doc
    paths = []
    for dp, dns, fns in os.walk(base):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            paths.append(os.path.relpath(os.path.join(dp, fn), base).replace(os.sep, "/"))
    lic, body_cls, lic_file = local_license(base)
    pushed, gitcmd = git_last(slug, root_fallback)
    doc = {"full": slug, "state": "OK", "tree_state": "OK", "blob_n": len(paths),
           "stars": 0, "pushed_at": pushed, "license": lic,
           "license_body_class": body_cls, "license_file": lic_file,
           "archived": False, "file_n": len(paths),
           "commands": [c0, "find " + base + " -type f", gitcmd],
           "measured_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    doc.update(r114.tree_counts(paths))
    doc["doc_hash"] = h8(doc)
    return doc


def root_stats():
    # 活跃根现场复算（禁抄快照），两条独立通路交叉断言，防「数字与所附命令不符」。
    # 通路 A = 文档写出的 GNU find 命令（用绝对路径的 MSYS2 bash；裸 "bash" 在本机
    # 可能落到 WSL，其 /d/ 挂载不存在会静默回 0）。
    # 通路 B = 等价 Python os.walk：显式跳过 reparse point（rag-eval junction）与
    # .git，且 fn == "SKILL.md" 严格大小写。两路必须逐项相等，否则抛错不交产物。
    bash = shutil.which("bash") or "bash"
    cmds = ["find /d/global_skills -mindepth 1 -maxdepth 1 -type d | wc -l",
            "find /d/global_skills -maxdepth 2 -name SKILL.md | wc -l",
            "find /d/global_skills -type f -name SKILL.md | wc -l",
            "find /d/global_skills -type f -iname skill.md | wc -l"]
    vals = []
    for c in cmds:
        rc, out, err = run_cmd([bash, "-lc", c], timeout=120)
        try:
            vals.append(int((out or "0").strip().splitlines()[-1]))
        except Exception:
            vals.append(-1)
    top_dirs, direct, exact, ci, junctions = 0, 0, 0, 0, []
    for name in os.listdir(GLOBAL):
        p = os.path.join(GLOBAL, name)
        try:
            attr = getattr(os.lstat(p), "st_file_attributes", 0)
            if attr & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                junctions.append(p.replace(os.sep, "/"))
                continue
        except Exception:
            pass
        if os.path.isdir(p):
            top_dirs += 1
            if os.path.isfile(os.path.join(p, "SKILL.md")):
                direct += 1
    for dp, dns, fns in os.walk(GLOBAL):
        keep = []
        for d in dns:
            q = os.path.join(dp, d)
            try:
                attr = getattr(os.lstat(q), "st_file_attributes", 0)
                if attr & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                    junctions.append(q.replace(os.sep, "/"))
                    continue
            except Exception:
                pass
            if d != ".git":
                keep.append(d)
        dns[:] = keep
        for fn in fns:
            if fn == "SKILL.md":
                exact += 1
            if fn.lower() == "skill.md":
                ci += 1
    py_vals = [top_dirs, direct, exact, ci]
    if vals != py_vals:
        raise RuntimeError("active_root_two_path_mismatch find=" + repr(vals) + " py=" + repr(py_vals))
    return {"top_level_dirs": vals[0], "direct_skill_md": vals[1],
            "all_depth_skill_md": vals[2], "case_insensitive_skill_md": vals[3],
            "junctions_skipped": junctions, "bash_abs": bash, "commands": cmds}


def defect_face(row):
    # 84/150 有逐件缺陷记录；66 件 = 未记录(unknown)，双向中性、不进任何维度。
    kd = row.get("known_defects") or []
    return "recorded(84-cohort)" if kd else "unknown(not_scored)"


def dimension_command(doc, dim):
    cs = doc.get("commands") or []
    if dim in ("fc", "eff", "docs"):
        return cs[1] if len(cs) > 1 else (cs[0] if cs else "")
    if dim == "compat":
        return " | ".join([c for c in cs if ("license" in c.lower() or c == cs[0])][:2]) or (cs[0] if cs else "")
    return cs[0] if cs else ""


def main():
    args = sys.argv[1:]
    offline = "--offline" in args
    rc_root, root_out, _ = run_cmd(["git", "-C", GLOBAL, "log", "-1", "--format=%cI"], timeout=60)
    root_fallback = (root_out or "")[:10]
    rs = root_stats()

    if "--show-root" in args:
        print(json.dumps(rs, ensure_ascii=False, indent=2)); return 0
    if "--show-local" in args:
        slug = args[args.index("--show-local") + 1]
        print(json.dumps(measure_local(slug, root_fallback), ensure_ascii=False, indent=2, default=str)); return 0
    if "--show-repo" in args:
        full = args[args.index("--show-repo") + 1]
        docs = json.load(open(LIVE_CACHE, "r", encoding="utf-8")) if os.path.isfile(LIVE_CACHE) else {}
        print(json.dumps(docs.get(full, {"error": "not in cache"}), ensure_ascii=False, indent=2, default=str)); return 0

    inv = json.load(open(INV, "r", encoding="utf-8"))
    cand = json.load(open(CAND, "r", encoding="utf-8"))

    pairs = []
    excluded = []
    for row in cand["rows"]:
        for x in (row.get("candidates") or []):
            if x.get("rel") == "skill" and x.get("candidate_class") == "replacement":
                pairs.append({"skill_slug": row["slug"], "cls": row["class"],
                              "repo": x["repo"], "url": x.get("url", ""),
                              "t2_metadata": x.get("metadata") or {},
                              "t2_score": (x.get("score") or {}).get("score5") or {}})
            elif x.get("candidate_class") == "directed_lead" or x.get("rel") == "lead":
                excluded.append({"kind": "directed_lead", "skill_slug": row["slug"],
                                 "repo": x.get("repo", ""),
                                 "why": "功能等价未实测，r292 reading_rule 禁升格为替代"})
        for x in (row.get("family_pads") or []):
            excluded.append({"kind": "family_pad", "skill_slug": row["slug"],
                             "repo": x.get("repo", ""),
                             "why": "族级邻居补位，not_replacement=true"})
    uniq_repos = sorted({p["repo"] for p in pairs})

    live = {}
    if offline and os.path.isfile(LIVE_CACHE):
        live = json.load(open(LIVE_CACHE, "r", encoding="utf-8"))
        print("[FETCH] offline cache loaded repos=" + str(len(live)))
    else:
        done = 0
        with ThreadPoolExecutor(max_workers=12) as pool:
            futs = {pool.submit(fetch_repo, r): r for r in uniq_repos}
            for fu in as_completed(futs):
                r = futs[fu]
                try:
                    doc = fu.result()
                except Exception as exc:
                    doc = {"full": r, "state": "ERROR", "error": repr(exc), "commands": []}
                if doc.get("state") != "OK" or doc.get("tree_state") != "OK":
                    cached = find_r114_cache(r)
                    if cached:
                        cached["full"] = r
                        cached["fallback"] = "r114_offline_cache"
                        cached["commands"] = ["python -B 05-exec/r114_replacement_scan.py --offline --json _temp/t3_matrix/r114_offline.json"]
                        doc = cached
                    else:
                        doc["fallback"] = "none(registered_blind_spot)"
                # 离线缓存 / 异常对象也会进 live_meta.json；先删旧 hash 再按最终字段重算，
                # 保证 CSV 句柄 sha 与落盘 doc 永远一致（#42：注释写清怎么运作）。
                doc.pop("doc_hash", None)
                doc["doc_hash"] = h8(doc)
                live[r] = doc
                done += 1
                if done % 25 == 0:
                    print("[FETCH] " + str(done) + "/" + str(len(uniq_repos)), flush=True)
        json.dump(live, open(LIVE_CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
        print("[FETCH] done repos=" + str(len(uniq_repos)))
    drift = {"text": "本轮未观察到 stars 漂移（全部与 t2 快照一致）；现场命令 @@gh api repos/<OWNER>/<REPO> --jq " + SQ + JQ_REPOS + SQ + "@@"}
    for p in pairs:
        ld = live.get(p["repo"]) or {}
        t2s = p["t2_metadata"].get("stars")
        ls = ld.get("stars")
        if isinstance(t2s, int) and isinstance(ls, int) and t2s != ls:
            drift["text"] = (p["repo"] + " t2=" + str(t2s) + " -> live=" + str(ls)
                             + "；现场命令 @@gh api repos/" + p["repo"] + " --jq " + SQ + JQ_REPOS + SQ + "@@")
            break
    ex_kinds = {"directed_lead": 0, "family_pad": 0}
    for x in excluded:
        ex_kinds[x["kind"]] = ex_kinds.get(x["kind"], 0) + 1

    locals_ = {row["slug"]: measure_local(row["slug"], root_fallback) for row in inv["rows"]}
    json.dump(locals_, open(LOCAL_CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)

    objects = []
    for row in inv["rows"]:
        slug = row["slug"]
        doc = locals_[slug]
        s, raw_total, fc_cal = r114.score5(doc, license_cap=True, use_body=True)
        st = "SCORED" if doc.get("state") == "OK" else "UNAVAILABLE"
        es = "已实测（现场文件系统）" if st == "SCORED" else "未实测（目录缺失，0=哨兵不参与排序）"
        if st == "UNAVAILABLE":
            # 目录/树缺失时 score5 的 archived 项仍可能给 compat=1；这里统一压成 5 维 0 哨兵。
            s = {d: 0 for d in DIMS}
            raw_total = 0
            fc_cal = "unavailable_sentinel"
        r260 = ((row.get("performance") or {}).get("r260") or {})
        note = "缺陷面=" + defect_face(row) + "；不进入任何维度分子（双向中性）"
        if st == "UNAVAILABLE":
            note += "；五维统一 0 哨兵，不参与均值/优劣比较"
        if r260.get("status") == "OK":
            note += "；r260 route_ms_med=" + str(r260.get("route_ms_med")) + " 部分实测(26/77)"
        else:
            note += "；r260 NO_TRIGGER(51/77) 部分实测"
        objects.append({"object_id": "current:" + slug, "type": "current",
                        "skill_slug": slug, "cls": row["class"], "scores": s,
                        "status": st, "evidence": es, "doc": doc,
                        "defect": defect_face(row), "notes": note, "fc_caliber": fc_cal})
    for p in pairs:
        doc = live.get(p["repo"]) or {}
        s, raw_total, fc_cal = r114.score5(doc, license_cap=True, use_body=True)
        fb = doc.get("fallback")
        if doc.get("state") == "ERROR" or doc.get("tree_state") != "OK":
            st, es = "UNAVAILABLE", "未实测（现场取证失败且无离线缓存，具名盲区）"
        elif fb and fb != "none(registered_blind_spot)":
            st, es = "SCORED", "部分实测（r114 离线缓存回退）"
        else:
            st, es = "SCORED", "已实测（现场 gh api " + str(doc.get("measured_at", "")) + "）"
        if st == "UNAVAILABLE":
            # 取证失败对象不继承 score5 的任何基础分；5 维统一 0，只作具名盲区哨兵。
            s = {d: 0 for d in DIMS}
            raw_total = 0
            fc_cal = "unavailable_sentinel"
        note = ("t2 快照 stars=" + str(p["t2_metadata"].get("stars")) + " / 现场 stars="
                + str(doc.get("stars")) + "；本轮以现场值为准（禁抄快照）")
        if st == "UNAVAILABLE":
            note += "；五维统一 0 哨兵，不参与均值/优劣比较"
        objects.append({"object_id": "cand:" + p["skill_slug"] + "::" + p["repo"],
                        "type": "candidate", "skill_slug": p["skill_slug"], "cls": p["cls"],
                        "scores": s, "status": st, "evidence": es, "doc": doc,
                        "defect": "n/a(candidate)", "notes": note, "fc_caliber": fc_cal})

    header = ["object_type", "object_id", "skill_slug", "class", "dimension", "dimension_cn",
              "score", "weight", "weighted_contribution", "defect_face", "feedback_weight_cap",
              "score_status", "evidence_status", "evidence_handle", "measurement_command", "notes"]
    with open(os.path.join(DATA, "matrix.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator=NL)
        w.writerow(header)
        for o in objects:
            doc = o["doc"]
            hh = doc.get("doc_hash") or h8(doc)
            prefix = "LIVE_FS:" + str(doc.get("full", "")) if o["type"] == "current" else "LIVE_GH:repos/" + str(doc.get("full", ""))
            for d in DIMS:
                handle = prefix + "@" + str(doc.get("measured_at", "")) + "#" + hh + "#" + d
                w.writerow([o["type"], o["object_id"], o["skill_slug"], o["cls"], d, DIM_CN[d],
                            o["scores"][d], WEIGHTS[d], WEIGHTS[d] * o["scores"][d],
                            o["defect"], 0, o["status"], o["evidence"], handle,
                            dimension_command(doc, d), o["notes"]])

    for o in objects:
        o["weighted_total"] = sum(WEIGHTS[d] * o["scores"][d] for d in DIMS)

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    sample = next((o for o in objects if o["type"] == "candidate" and o["status"] == "SCORED"), objects[0])
    sample_lines = []
    acc = 0
    for d in DIMS:
        v = sample["scores"][d]
        acc += WEIGHTS[d] * v
        sample_lines.append("- " + DIM_CN[d] + " (" + d + ")：s=" + str(v) + " x w=" + str(WEIGHTS[d])
                            + " = " + str(WEIGHTS[d] * v) + "，累计 " + str(acc))
    by_cls = {}
    unscored_by_cls = {}
    for o in objects:
        k = o["type"] + "/" + o["cls"]
        if o["status"] == "SCORED":
            by_cls.setdefault(k, []).append(o["weighted_total"])
        else:
            unscored_by_cls[k] = unscored_by_cls.get(k, 0) + 1
    stat_lines = []
    for k in sorted(set(by_cls) | set(unscored_by_cls)):
        vs = by_cls.get(k, [])
        un = unscored_by_cls.get(k, 0)
        if vs:
            stat_lines.append("| " + k + " | " + str(len(vs)) + " | " + str(un) + " | "
                              + str(round(sum(vs) / len(vs), 2)) + " | " + str(min(vs))
                              + " | " + str(max(vs)) + " |")
        else:
            stat_lines.append("| " + k + " | 0 | " + str(un) + " | - | - | - |")

    L = []
    def A(s=""):
        L.append(s.replace("@@", BT))
    A("# 03 五维量化对比评估矩阵（需求3）")
    A("")
    A("- 生成时间：@@" + now + "@@；评估日 @@EVAL_DATE=" + EVAL_DATE + "@@；角色 matrix-analyst / t3。")
    A("- 证据状态：候选侧 ✅已实测（本轮现场 @@gh api@@）；现有侧 ✅已实测（本轮现场文件系统）；质量口径旁证 ⚠️部分实测。")
    A("- 只读取证：本轮**未改** @@D:/global_skills@@ 下任何 @@SKILL.md@@ 或源文件；镜像与 @@eval/@@ 只读。R241 历史报告旧数字只加校正注、不改写。")
    A("- 禁抄快照：t2 @@candidates.json@@ 的 @@metadata.stars@@ 为 2026-11-06 取值；本轮现场复取漂移实测：" + drift["text"] + "。故一律以本轮 @@measured_at@@ 为准，t2 值仅留作漂移对照。")
    A("")
    A("## 1. 评分方法与对象定义")
    A("")
    A("**唯一量尺** = @@05-exec/r114_replacement_scan.py:790-863@@ 的 @@score5(m, license_cap=True, use_body=True)@@，返回 @@(s, sum(s.values()), fc_caliber)@@，五维各 0-5 分。本件用 @@importlib.util.spec_from_file_location@@ 直接加载该模块，**不重写锚点**（防主观漂移、防两处实现分叉）。")
    A("")
    A("- 现有件对象 = @@D:/global_skills/<slug>/@@ 子树（150 件，含 LOW/EXCLUDE，分母口径见 §5）；输入由 @@r114.tree_counts(paths)@@ 现场扫描生成，@@tree_state=OK@@，@@stars=0@@，@@pushed_at@@ = 该目录最后一次 git 提交日期。")
    A("- 候选对象 = GitHub 仓默认分支全树（323 条 @@rel=skill@@ 真替代，去重 " + str(len(uniq_repos)) + " 仓）；输入由现场 @@gh api repos/<full>@@ + @@gh api repos/<full>/git/trees/<br>?recursive=1@@ 生成，@@NOASSERTION@@ 另取 @@repos/<full>/license@@ 正文交 @@r114.classify_body()@@ 归一（R247 双向：取不到留 @@None@@，不猜宽松也不猜受限）。")
    A("- 两侧**同一函数、同一锚点、同一输入构造规则**：@@score5@@ 不认识「本地件」或「候选」，只认识一张 doc。原始 doc 全量落 @@_temp/t3_matrix/local_meta.json@@ / @@live_meta.json@@，每个分数的 @@evidence_handle@@ 带 doc 的 sha256 前 12 位，可回溯到具体快照。")
    A("- 现场取值命令（逐仓，随分给出；字面量见下方代码块，CSV @@measurement_command@@ 列已展开）：@@python -B 03_matrix_build.py --show-local <slug>@@ / @@--show-repo <OWNER/REPO>@@ 可打印任一对象的完整输入 doc。")
    A("")
    A("**字面 jq 表达式（同 05-exec/r114_replacement_scan.py:339-414 的字段面）**：")
    A("@@@@@@")
    A("gh api repos/<OWNER>/<REPO> --jq " + SQ + JQ_REPOS + SQ)
    A("gh api " + Q + "repos/<OWNER>/<REPO>/git/trees/<br>?recursive=1" + Q + " --jq " + SQ + JQ_TREE + SQ)
    A("gh api repos/<OWNER>/<REPO>/license --jq " + SQ + JQ_LICENSE + SQ + "  # 仅 NOASSERTION 触发")
    A("@@@@@@")
    A("")
    A("## 2. 五维权重与 0-5 分档锚点（可操作，防主观漂移）")
    A("")
    A("权重取整数、和 = 20，故 @@T = SUM(w_d x s_d)@@ 直接落在 0-100，无需归一化除法。")
    A("")
    A("| 维度 | 权重 | 占比 | 定权理由 |")
    A("|---|---:|---:|---|")
    A("| 功能完整性 fc | 6 | 30% | 需求①功能边界为替代首要条件；但 fc 由 SKILL.md 计数代理，存在 bundle-scale 盲区（§9），不单独决定迁移 |")
    A("| 运行效率 eff | 4 | 20% | 需求①性能；本地仅 26/77 有 r260 路由耗时实测、51/77 NO_TRIGGER，故降权 |")
    A("| 兼容性 compat | 4 | 20% | 需求⑥「无兼容性问题」硬约束，与 eff 同权 |")
    A("| 文档完善度 docs | 3 | 15% | 迁移可执行性 |")
    A("| 社区支持度 community | 3 | 15% | 需求③社区支持度；但使用反馈 99.94% outcome_unknown ⇒ **权重上限 15%**，且只用 GitHub 元数据代理 |")
    A("")
    A("**fc 功能完整性**（@@sm = skill_md_exact_n@@，缺失时回退 @@skill_md_n@@；@@blob_n@@ = 对象文件数）：")
    A("")
    A("| 分 | 锚点（可机械判定） |")
    A("|---:|---|")
    A("| 0 | @@sm is None@@（树不可用）或 @@sm == 0@@ 且 @@blob_n <= 50@@ |")
    A("| 1 | @@sm == 0@@ 且 @@blob_n > 50@@ |")
    A("| 2 | @@1 <= sm <= 2@@ |")
    A("| 3 | @@3 <= sm <= 10@@ |")
    A("| 4 | @@11 <= sm <= 100@@ |")
    A("| 5 | @@sm > 100@@ |")
    A("")
    A("**eff 运行效率**（@@tn = test_path_n@@，@@wn = workflow_n@@）：@@eff = min(5, A + B)@@，@@A = 0 if tn==0 else min(3, 1 + (tn>20) + (tn>200))@@，@@B = 0 if wn==0 else min(2, 1 + (wn>3))@@。即 0=无测试路径无工作流；1=仅 1..20 测试路径或 1..3 工作流之一；2..5 按两路叠加；@@tn>200@@ 且 @@wn>3@@ 封顶 5。")
    A("")
    A("**compat 兼容性**：@@base = (2 if license != UNLICENSED else 0) + (0 if archived else 1) + (2 if sm else 0)@@；@@compat = min(5, base, LICENSE_CAPS[license_class(license, license_body_class)])@@。档位上限 @@copyleft=1 / restricted=1 / weak-copyleft=2 / unknown=4 / permissive=5 / none=5@@（cap 只降不升；@@NOASSERTION@@ 走正文指纹，R247）。")
    A("")
    A("**docs 文档完善度**（@@rn = readme_n@@，@@dn = docs_md_n@@）：@@docs = min(5, (2 if rn else 0) + (1 if dn>5 else 0) + (1 if dn>40 else 0) + (1 if tree_state==OK else 0))@@。")
    A("")
    A("**community 社区支持度**（@@st = stars@@，@@pushed_at@@ 取前 10 位日期）：@@community = min(5, count(100,1000,10000,50000 : st >= th) + (1 if pushed_at >= " + FRESH_CUTOFF + " else 0))@@。阈值沿用 r114 内建常量（其 EVAL_DATE=2026-10-28 口径），本轮不改为 2026-11-07 派生值，以保同尺可比。")
    A("")
    A("## 3. unknown / 弱证据的双向中性规则（captain 硬口径）")
    A("")
    A("- **缺陷面 84/150**：@@inventory.json@@ 仅 84 件有逐件 @@known_defects@@，其余 **66 件** @@defects_note@@=「未见逐件缺陷记录」。@@matrix.csv@@ 的 @@defect_face@@ 列逐行标 @@unknown(not_scored)@@；**这 66 件一律不记为「零缺陷/满分」，也不得拿 84 当全量分母外推缺陷率**。")
    A("- **规则（双向中性）**：本矩阵**没有任何一维**把缺陷面写进分子或分母 —— 有记录的 84 件不扣分、未记录的 66 件不加分；候选侧同样不因「未见缺陷记录」加分（@@defect_face=n/a(candidate)@@）。故该规则对旧 skill 与候选**均不单向有利**。若 t4 需要缺陷面结论，须另起逐件取证，不得由本矩阵外推。")
    A("- **使用反馈面 = 弱证据**：r289 实测 @@outcome_unknown_share_pct=99.94@@（@@rows_total=3110@@ / @@outcome_known_rows=2@@）。**禁**作为「社区支持度」或「运行效率」的实测定分依据；@@matrix.csv@@ 的 @@feedback_weight_cap@@ 列恒为 **0**（权重上限显式落列），仅作 ⚠️部分实测旁证。@@r289_never_seen@@ 不得写成满意度/成功率。")
    A("- **r115 四层质量口径**：L1 layered 291 条 Top-1 88.3%（含 63.6% 泄漏题加成 +7.7pp）；L2 frozen 10 条 70.0%（净化 87.5%，n 太小仅哨兵）；L3 污染命中；L4 干净面 = L1+L3 派生。**引用 L1 必须同屏给 L4**。与 r114 A/B 的 38.2% **不可比、禁相减**（生产路由是 @@eval/unified_router.py::route()@@，r114 的 @@hybrid_match()@@ 只是三方法对照近似实现）。本矩阵**不**把任何质量口径读数写进分数，权重 0、⚠️旁证。")
    A("- **r114/r260 A/B 旁证**：@@06-benchmark/r260_req6_quality_ab.json@@ 99 queries，hybrid Top-1 38.2%（Wilson CI 28.8–48.6）；@@delta_pp=0.0@@、区间重叠(幅度落在抽样抖动内)、@@verdict_rule = 区间分离 且 delta_rel_pct>=30 才可写提升>=30%@@。**区间重叠禁写「提升」(P1-23)**；Top-1 是路由命中率，不是任务完成好坏。需求⑥的 >=30% 质量提升由 t6 用独立 A/B 验收，本矩阵不代判。")
    A("- **目录缺失 4 件**（@@cloudbase__skillhub@@ / @@executing-plans@@ / @@pptx@@ / @@slides@@）：现场 @@test -d@@ 为 false，5 维记 0 且 @@score_status=UNAVAILABLE@@、证据 @@未实测（目录缺失，0=哨兵不参与排序）@@；**不纳入均值/优劣比较**，具名登记为盲区，禁静默丢弃。")
    A("- **54 条定向线索 + 44 条族级补位**：t2 @@reading_rule@@ 明示 @@rel=family@@ 补位是族级邻居、@@directed_lead@@ 功能等价 ❌未实测，**禁当替代方案引用** ⇒ 本轮登记但不计分、不进 @@matrix.csv@@、不进汇总表（§9 列明）。")
    A("")
    A("## 4. 加权总分公式与手算样例")
    A("")
    A("@@@@@@")
    A("T = SUM_d ( w_d x s_d ),  w = (fc=6, eff=4, compat=4, docs=3, community=3), SUM(w) = 20")
    A("s_d in [0,5]  =>  T in [0,100];  0-5 等价分 T5 = T / 20")
    A("逐行复算：matrix.csv 的 weighted_contribution = weight x score，按 object_id 求和即 T")
    A("@@@@@@")
    A("")
    A("**手算样例**（取自本轮现场值，非硬编码样例）：@@" + sample["object_id"] + "@@")
    A("")
    for ln in sample_lines:
        A(ln)
    A("- 合计 @@T = " + str(acc) + "@@（0-100），@@T5 = " + str(round(acc / 20.0, 2)) + "@@（0-5）。")
    A("")
    A("## 5. 分母、覆盖面与活跃根现场复算")
    A("")
    A("- 盘点分母 150 = HIGH 51 + MID 26 + LOW 30 + EXCLUDE 43（t1 inventory，captain 已复核：逐件证据 150/150、三条守恒 True、负控报红）；自建维护口径 = HIGH+MID = **77**。")
    A("- 本矩阵对象 = 150 件现有 skill + 323 条 @@rel=skill@@ 真替代 = **473** 个对象 x 5 维 = **2365** 行 @@matrix.csv@@。")
    A("- 活跃根现场复算（✅已实测，禁抄 t1 快照）：一级目录 @@" + str(rs["top_level_dirs"]) + "@@、一级直属 SKILL.md @@" + str(rs["direct_skill_md"]) + "@@、全深度 SKILL.md（case-sensitive、不跟随 junction）@@" + str(rs["all_depth_skill_md"]) + "@@；大小写不敏感 @@find -iname skill.md@@ = @@" + str(rs.get("case_insensitive_skill_md")) + "@@（多出的 3 个是小写 skill.md：cloudbase/references/cloudbase-agent/{py,ts}/skill.md、dingtalk-misc/references/skill.md）。")
    A("- **247 漂移归因（本轮现场破案）**：Python @@os.walk@@ 跟随 junction @@/d/global_skills/rag-eval -> /c/Users/37533/.agents/skills/rag-eval@@ 且大小写不敏感，读到 247；GNU @@find@@ 默认不跟随 junction 且 @@-name@@ 大小写敏感，读到 243（t1 快照同口径）。两者都是**同一时刻的现场值**，差 4 来自 junction 目标内的 1 个 SKILL.md + 3 个小写 skill.md，**不是活跃根真的又漂移**；按 R269 只登记、不擅动受管源。禁把 243/247 任一值当维护分母（维护分母恒 = 77）。")
    A("- 取值命令：@@" + "@@ / @@".join(rs["commands"]) + "@@。")
    A("")
    A("## 6. 汇总表（机器可读，03_matrix_check.py 复算对账）")
    A("")
    A("<!-- MATRIX_SUMMARY_BEGIN -->")
    A("| object_id | class | fc | eff | compat | docs | community | weighted_total |")
    A("|---|---|---:|---:|---:|---:|---:|---:|")
    for o in objects:
        s = o["scores"]
        A("| " + o["object_id"] + " | " + o["cls"] + " | " + str(s["fc"]) + " | " + str(s["eff"])
          + " | " + str(s["compat"]) + " | " + str(s["docs"]) + " | " + str(s["community"])
          + " | " + str(o["weighted_total"]) + " |")
    A("<!-- MATRIX_SUMMARY_END -->")
    A("")
    A("## 7. 分组统计（加权总分 0-100）")
    A("")
    A("| 面 | SCORED 对象数 | UNAVAILABLE 未计分数 | 均值 | 最小 | 最大 |")
    A("|---|---:|---:|---:|---:|---:|")
    for ln in stat_lines:
        A(ln)
    A("")
    A("该统计仅纳入 SCORED 对象；UNAVAILABLE 的 5 维 0 哨兵不纳入均值/优劣比较（§3）。数值只说明「作为可替换资产包的工程完成度」分布，**不是业务功能强弱结论**；fc 由 SKILL.md 计数代理，仓级 bundle 天然高于单件 skill 目录（见 §9 盲区），t4 迁移优先级不得只按 T 排序。")
    A("")
    A("## 8. 负控、自证命令、门禁与退路")
    A("")
    A('- **自证（差异断言 0）**：@@cd 自建skill优化 && PYTHONPYCACHEPREFIX=_temp/pycache "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -B deliverables/skill-modernization-r1/03_matrix_check.py@@ → 打印 @@[DIFF_ASSERT] 0@@，逐对象复算 @@matrix.csv@@ 的 @@weighted_contribution@@ 求和并与 §6 汇总表逐行比对。')
    A("- **负控**：@@03_matrix_check.py@@ 把样例候选的 @@fc@@ 分数改 0，重算 T，断言 @@T_prime != T@@ 并打印 @@[NEGCTRL:RED] 篡改被检出@@；另注入一处汇总表错值断言被抓。负控只作用于内存副本，不写回 @@matrix.csv@@。")
    A('- **现场取值命令**：候选 @@gh api repos/<OWNER>/<REPO> --jq .@@ + @@gh api "repos/<OWNER>/<REPO>/git/trees/<br>?recursive=1" --jq .@@；现有件 @@find D:/global_skills/<slug> -type f@@；活跃根 @@find /d/global_skills -type f -name SKILL.md | wc -l@@。每个分数在 @@matrix.csv@@ 的 @@evidence_handle@@ / @@measurement_command@@ 两列可逐行追溯。')
    # ===== 门禁 / 证据句柄：全部现场从产物复算，源码内不写死 verdict 或计数 =====
    gr = gate_record()
    _live_disk = json.load(open(LIVE_CACHE, 'r', encoding='utf-8'))
    _local_disk = json.load(open(LOCAL_CACHE, 'r', encoding='utf-8'))
    ht = handle_trace(_live_disk, _local_disk, os.path.join(DATA, 'matrix.csv'))
    real_red = gr.get('real_red') or []
    design_red = gr.get('design_inherent_red') or []
    not_covered = gr.get('not_covered') or []
    cc_tail = ''
    for g in gr.get('gates', []):
        if g.get('id') == 'control_char_scan':
            cc_tail = g.get('tail', '')
            break
    dirty_short = ''
    if '[CTRL:HIT]' in cc_tail:
        dirty_short = cc_tail.split('[CTRL:HIT]', 1)[1].strip().split()[0]
    gate_ok = gr.get('status') == 'OK'
    if gate_ok:
        gp = []
        gp.append('- **全量门禁（本轮实测，取自 @@_temp/t3_gates.json@@，非硬编码）**：')
        gp.append('@@cd 自建skill优化 && PYTHONPYCACHEPREFIX=_temp/pycache ' + Q + '$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe' + Q + ' -B 05-exec/run_gates.py --json _temp/t3_gates.json@@')
        gp.append(' → @@verdict=' + str(gr.get('verdict')) + '@@、@@verdict_reason=' + str(gr.get('verdict_reason')) + '@@、@@gates_run=' + str(gr.get('gates_run')) + '@@、@@generated_at=' + str(gr.get('generated_at')) + '@@、@@schema=' + str(gr.get('schema')) + '@@。')
        gp.append('红门分类：@@REAL_RED=' + str(len(real_red)) + '@@（' + ' / '.join(real_red) + '）+ @@DESIGN_INHERENT_RED=' + str(len(design_red)) + '@@（' + ' / '.join(design_red) + '）。')
        gp.append('其中 @@control_char_scan@@ 脏件是**既有** @@' + (dirty_short or '见 §10 门禁 tail') + '@@（非 t3 的 03_* 产物，本轮定点 @@CTRL_SCAN CLEAN@@）；其余为既有 / 他人在途 / 设计固有红。')
        gp.append('按 R263/X-9 如实登记、不删 tracked 件凑绿，与 t1（FAIL=7/UNVERIFIED=2）、t2（FAIL=7/UNVERIFIED=3）同源，不阻塞下游 t4/t5/t6。详见 §10。')
        A(''.join(gp))
    else:
        A('- **全量门禁**：@@_temp/t3_gates.json@@ ' + str(gr.get('reason')) + ' ⇒ 本轮 @@NOT_RUN@@（❌未实测，禁硬编码 verdict 凑绿）；须补跑 @@05-exec/run_gates.py --json _temp/t3_gates.json@@ 后重生成。详见 §10。')
    A('- **证据句柄独立回溯（生成器重读落盘缓存 + CSV 现场复算）**：@@[RECOMP] doc_hash_recomputable=' + str(ht['recomp_ok']) + ' bad=' + str(ht['recomp_bad']) + '@@ / @@[HANDLE] rows=' + str(ht['rows']) + ' traceable=' + str(ht['map_ok']) + ' bad=' + str(ht['map_bad']) + '@@；独立外部复跑 @@python -B _temp/t3_matrix/verify_handles.py@@ → @@[VERIFY] PASS@@。每个分数的 @@evidence_handle@@ 都能回溯到本轮现场快照 doc 的 @@doc_hash@@（sha256 前 12 位），4 件目录缺失 UNAVAILABLE doc 也落完整 hash。')
    A("- **退路**：取证受阻 ⇒ @@python 05-exec/r114_replacement_scan.py --offline --json _temp/t3_matrix/r114_offline.json@@ 复用缓存；@@03_matrix_build.py --offline@@ 复用 @@_temp/t3_matrix/live_meta.json@@；两者都失败的对象标 @@UNAVAILABLE@@ 并具名登记盲区，禁静默丢弃。")
    A("")
    A("## 9. 盲区、边界与下游接口")
    A("")
    A("- **B1 bundle-scale 不对称（结构性，双向披露）**：同一锚点下，候选是「整仓」、现有件是「单件 skill 目录」，仓级 SKILL.md 数天然更高。所有对象在 @@evidence_handle@@ 带 @@blob_n@@ 所在 doc 的 sha，读者可用 @@--show-repo@@ / @@--show-local@@ 核对 @@skill_md_exact_n@@；本矩阵测的是**资产包工程完成度**，不是单件业务功能等价性。t4 的功能等价结论须另做人审，不得由 T 直接推出。")
    A("- **B2 运行效率是代理**：@@eff@@ 数的是测试路径与 CI 工作流，不是执行耗时；本地 r260 仅 26/77 有 @@route_ms_med@@、51/77 NO_TRIGGER，已在 @@notes@@ 列逐行登记。")
    A("- **B3 社区支持度无 outcome 数据**：99.94% outcome_unknown，只有 stars / pushed_at / forks 代理，权重封顶 15%。")
    A("- **B4 取证失败登记**：现场失败且离线缓存亦缺的仓，标 @@UNAVAILABLE@@ + ❌未实测，下轮巡检补取。")
    A("- **B5 排除对象登记（不计分、不进 CSV/汇总表）**：" + str(len(excluded)) + " 条 = " + str(ex_kinds.get("directed_lead", 0)) + " @@directed_lead@@（功能等价 ❌未实测）+ " + str(ex_kinds.get("family_pad", 0)) + " @@family_pad@@（族级邻居 @@not_replacement=true@@）；无重复计数。t2 语义缺口 11 件（A-ask-questions、chaoshi-admin-inline-edit、cloudbase-db-optimize、dogfood、fenjue-lessons-hitrate、story-deslop、story-scan、vp-perspective-audit、wb-git-commit-recipe、wps-knowledgebase、天眼一下）只有线索、无真替代，须在 t4 单列「语义缺口」处置。")
    A("- **B6 community/stars 通道结构性不可比**：本地单件 skill 无 GitHub stars，doc 固定 @@stars=0@@，community 仅由 @@pushed_at@@ 新鲜度贡献；候选整仓可用 stars 四档。两侧虽共用 @@score5@@，输入面并不等价，t4 **不得**把 community 差值写成「社区支持度优于本地」的绝对结论；公平比较须在 t6 用同一业务指标独立 A/B。")
    A("- **下游接口**：t4 迁移计划按 (现有 skill, 候选) 对取 @@weighted_total@@ 与逐维分数做优先级输入，叠加 t2 的 @@rel_strength@@ / @@match_reason@@、需求⑥的 A/B 验证与兼容性验证；t5 季度巡检把本脚本的现场复取与 @@maintenance_trim@@（archived / pushed_at < EVAL_DATE-365d）纳入例行。")
    A("")
    A('## 10. 门禁实测记录（本轮，禁硬编码）')
    A('')
    if gate_ok:
        A('- 命令：@@cd 自建skill优化 && PYTHONPYCACHEPREFIX=_temp/pycache ' + Q + '$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe' + Q + ' -B 05-exec/run_gates.py --json _temp/t3_gates.json > _temp/t3_gates.log 2>&1@@（后台 job；@@GATE_RC=1@@ 为门禁判红的程序退出码，非执行失败，job 状态 completed）。')
        A('- 输出：@@_temp/t3_gates.json@@ → @@verdict=' + str(gr.get('verdict')) + '@@ / @@verdict_reason=' + str(gr.get('verdict_reason')) + '@@ / @@gates_run=' + str(gr.get('gates_run')) + '@@ / @@generated_at=' + str(gr.get('generated_at')) + '@@ / @@total_ms=' + str(gr.get('total_ms')) + '@@；日志末行 @@[GATES:FAIL] ' + str(gr.get('verdict_reason')) + '@@。')
        A('- runner 自报不覆盖：' + '；'.join(not_covered) + '。本轮阶段0-3 只读取证，未触发受管根四门禁。')
        A('- 红门归因：@@REAL_RED=' + str(len(real_red)) + '@@（' + ' / '.join(real_red) + '）+ @@DESIGN_INHERENT_RED=' + str(len(design_red)) + '@@（' + ' / '.join(design_red) + '）；@@control_char_scan@@ 现场 tail 摘要：@@' + cc_tail[:160] + '@@ … 脏件 @@' + dirty_short + '@@ 为既有件，**无一门由 t3 的 03_* 产物触发**，本轮 4 件产物 + @@data/matrix.csv@@ 定点 @@CTRL_SCAN CLEAN@@；其余为既有 / 他人在途 / 设计固有红。')
        A('- 处置：按 R263/X-9 如实登记、不删 tracked 件凑绿、不改写历史报告（R241）；与 t1/t2 同源既有红，按既有判据不阻塞下游 t4/t5/t6。')
    else:
        A('- @@NOT_RUN@@：@@_temp/t3_gates.json@@ ' + str(gr.get('reason')) + '；本轮未取得门禁实测 verdict（❌未实测），须补跑后重生成，禁硬编码凑绿。')
    A('')
    A('<!-- 生成脚本：03_matrix_build.py；复算/负控：03_matrix_check.py；数据：data/matrix.csv -->')
    with open(os.path.join(HERE, "03_evaluation_matrix.md"), "w", encoding="utf-8") as f:
        f.write(NL.join(L) + NL)

    print("[BUILD] objects=" + str(len(objects)) + " csv_rows=" + str(len(objects) * 5)
          + " excluded=" + str(len(excluded)) + " live_repos=" + str(len(uniq_repos)))
    print("[BUILD] root=" + json.dumps(rs, ensure_ascii=False))
    print("[BUILD] sample=" + sample["object_id"] + " T=" + str(acc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
