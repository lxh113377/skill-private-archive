# -*- coding: utf-8 -*-
"""r106 story 族现状取数器（对标 _reports/2026-10-06 报告 §16 的每条声明逐条复算）。

取值：python 05-exec/r106_story_face.py [--json 06-benchmark/story_face_r106_2026-10-08.json]
退出码：0=取数成功（不代表结论绿）/ 2=族根取不到或面为空（禁止把「读不到」当「没有」）。
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re

GS = "D:/global_skills"
DRIVE_RE = re.compile(r"[A-Za-z]:[/\\]")
FM_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):")
VER_RE = re.compile(r"\b\d+\.\d+\.\d+\b")
SOFT_LIMIT = 12 * 1024
HARD_LIMIT = 12 * 1024


def read(path):
    try:
        with io.open(path, "r", encoding="utf-8", newline="") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def frontmatter(text):
    """返回 (顶层键列表, 键->值原文)。frontmatter 必须是文件首块 --- 对。"""
    if text is None or not text.startswith("---"):
        return [], {}
    lines = text.split("\n")
    keys, vals, in_fm = [], {}, False
    for ln in lines[1:]:
        if ln.strip() in ("---", "..."):
            if in_fm:
                break
            in_fm = True
            continue
        if not in_fm and ln.strip() == "":
            continue
        m = FM_KEY_RE.match(ln)
        if m and not ln.startswith((" ", "\t")):
            keys.append(m.group(1))
            vals[m.group(1)] = ln[len(m.group(1)) + 1:].strip()
    return keys, vals


def sha256(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()


def walk(root, exts):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git", "node_modules")]
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in exts:
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="json_out", default="")
    args = ap.parse_args()

    skills = sorted(d for d in os.listdir(GS)
                    if d.split("-")[0] == "story" and os.path.isdir(os.path.join(GS, d)))
    if not skills:
        print("[FACE:UNVERIFIED] story 族根取不到目录，GS=%s" % GS)
        return 2

    # 脚本物理复制探测：按内容 sha 归组
    exts = {".js", ".py", ".ps1", ".sh", ".mjs"}
    by_sha, by_name = {}, {}
    for sk in skills:
        root = os.path.join(GS, sk)
        for p in walk(root, exts):
            h = sha256(p)
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            if h:
                by_sha.setdefault(h, []).append({"skill": sk, "path": rel,
                                                 "bytes": os.path.getsize(p)})
            by_name.setdefault(os.path.basename(p), []).append({"skill": sk, "path": rel})

    rows = []
    for sk in skills:
        root = os.path.join(GS, sk)
        skmd = os.path.join(root, "SKILL.md")
        text = read(skmd)
        keys, vals = frontmatter(text)
        refs = os.path.join(root, "references")
        ref_files = os.listdir(refs) if os.path.isdir(refs) else []
        scripts = walk(root, exts)
        md_all = walk(root, {".md"})
        contracts = [os.path.relpath(p, root).replace(os.sep, "/")
                     for p in md_all if "contract" in os.path.basename(p).lower()]
        metas = [os.path.relpath(p, root).replace(os.sep, "/")
                 for p in walk(root, {".json"})
                 if os.path.basename(p) in ("_meta.json", "meta.json")]
        locks = [os.path.relpath(p, root).replace(os.sep, "/")
                 for p in md_all + scripts if "lock" in os.path.basename(p).lower()]
        prog = [os.path.relpath(p, root).replace(os.sep, "/")
                for p in md_all + scripts
                if "progress" in os.path.basename(p).lower()]
        tests = os.path.join(root, "tests")
        drive_hits = sum(len(DRIVE_RE.findall(read(p) or "")) for p in md_all + scripts)
        size = os.path.getsize(skmd) if text is not None else -1
        rows.append({
            "skill": sk,
            "skill_md_bytes": size,
            "over_soft_limit": size > SOFT_LIMIT,
            "fm_keys": keys,
            "fm_version": vals.get("version"),
            "fm_license": vals.get("license"),
            "fm_requires": vals.get("requires"),
            "has_version_history_section": bool(text and re.search(r"^#+.*版本历史", text, re.M)),
            "version_lines": [(i + 1, m.group(0)) for i, ln in enumerate((text or "").split("\n"))
                              for m in [VER_RE.search(ln)] if m][:6],
            "references_count": len(ref_files),
            "script_count": len(scripts),
            "md_count": len(md_all),
            "contract_files": contracts,
            "meta_json_files": metas,
            "lock_files": locks,
            "progress_files": prog,
            "tests_dir": os.path.isdir(tests),
            "drive_letter_hits": drive_hits,
            "dir_bytes": sum(os.path.getsize(p) for p in walk(root, {".md", ".js", ".py", ".ps1",
                                                                     ".json", ".sh", ".txt"})
                             if os.path.exists(p)),
        })

    dup_content = [{"sha256_12": h[:12], "copies": v, "bytes_each": v[0]["bytes"],
                    "distinct_skills": sorted({c["skill"] for c in v})}
                   for h, v in by_sha.items() if len(v) > 1]
    dup_content.sort(key=lambda d: -d["bytes_each"])
    dup_name = [{"basename": n, "skills": sorted({c["skill"] for c in v})}
               for n, v in by_name.items() if len({c["skill"] for c in v}) > 1]

    over = [r["skill"] for r in rows if r["over_soft_limit"]]
    summary = {
        "gs": GS,
        "skill_n": len(skills),
        "over_soft_limit_n": len(over),
        "over_soft_limit": over,
        "max_bytes_skill": max(rows, key=lambda r: r["skill_md_bytes"])["skill"],
        "max_bytes": max(r["skill_md_bytes"] for r in rows),
        "median_bytes": sorted(r["skill_md_bytes"] for r in rows)[len(rows) // 2],
        "fm_version_n": sum(1 for r in rows if r["fm_version"]),
        "fm_license_n": sum(1 for r in rows if r["fm_license"]),
        "fm_requires_n": sum(1 for r in rows if r["fm_requires"]),
        "version_history_n": sum(1 for r in rows if r["has_version_history_section"]),
        "references_zero_n": sum(1 for r in rows if r["references_count"] == 0),
        "contract_file_n": sum(1 for r in rows if r["contract_files"]),
        "lock_file_n": sum(1 for r in rows if r["lock_files"]),
        "tests_dir_n": sum(1 for r in rows if r["tests_dir"]),
        "drive_letter_hits_total": sum(r["drive_letter_hits"] for r in rows),
        "dup_content_groups": dup_content,
        "dup_content_group_n": len(dup_content),
        "dup_name_groups": sorted(dup_name, key=lambda d: d["basename"]),
        "rows": rows,
    }
    print("story 族 n=%s ｜ 超 12KB=%s 个 %s" % (len(skills), len(over), ",".join(over)))
    print("主文件中位=%s B 最大=%s B(%s) ｜ version=%s license=%s requires=%s 版本历史小节=%s"
          % (summary["median_bytes"], summary["max_bytes"], summary["max_bytes_skill"],
             summary["fm_version_n"], summary["fm_license_n"], summary["fm_requires_n"],
             summary["version_history_n"]))
    print("references 零分卷=%s ｜ 含 contract 文件=%s ｜ 含 lock=%s ｜ 有 tests/=%s ｜ 盘符字面量=%s"
          % (summary["references_zero_n"], summary["contract_file_n"], summary["lock_file_n"],
             summary["tests_dir_n"], summary["drive_letter_hits_total"]))
    print("内容级重复脚本组=%s（同 sha 多副本）｜ 同名脚本跨 skill 组=%s"
          % (summary["dup_content_group_n"], len(summary["dup_name_groups"])))
    for d in dup_content[:6]:
        print("  %s %s B × %s 份 -> %s" % (d["sha256_12"], d["bytes_each"], len(d["copies"]),
                                           ",".join(d["distinct_skills"])))
    print("[FACE:MEASURED]")
    if args.json_out:
        with io.open(args.json_out, "w", encoding="utf-8", newline="") as f:
            json.dump(summary, f, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.json_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
