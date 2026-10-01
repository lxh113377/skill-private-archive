#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r99 十一/十二维本地面探针（只读取证，不写盘）

用途：验证 r96_twelve_face.py 缺失的 d4/d6/d7/d8/d10/d12 六维在本地面
到底能不能取到数、取到的是不是真值。取证通过后才把它并进判据本体
（R236：门禁/判据命令须先实跑再写进文档或据其下结论）。
"""
import io
import os
import re
import sys

SKILL_ROOT = "D:/global_skills"
NOISE_PARTS = {".git", "_trash", "__pycache__", ".rule_backup", "node_modules"}

RE_FM = re.compile(r"\A---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|\Z)", re.S)


def fm_fields(text):
    """Return (has_name, has_desc, field_names) from a leading YAML fence."""
    m = RE_FM.match(text)
    if not m:
        return False, False, []
    keys = []
    for line in m.group(1).splitlines():
        mm = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:", line)
        if mm:
            keys.append(mm.group(1).lower())
    has_name = "name" in keys
    has_desc = "description" in keys
    return has_name, has_desc, keys


def walk_files(root):
    out = []
    for cur, dirs, files in os.walk(root):
        rel = os.path.relpath(cur, root).replace(os.sep, "/")
        if any(p in NOISE_PARTS for p in rel.split("/")):
            dirs[:] = []
            continue
        for f in files:
            out.append((os.path.join(rel, f).replace(os.sep, "/")
                        if rel != "." else f).lstrip("/"))
    return out


def main():
    dirs = sorted(n for n in os.listdir(SKILL_ROOT)
                  if os.path.isdir(os.path.join(SKILL_ROOT, n)))
    skill_dirs = [n for n in dirs
                  if os.path.isfile(os.path.join(SKILL_ROOT, n, "SKILL.md"))]

    files = walk_files(SKILL_ROOT)
    schemas = [p for p in files if "/schemas/" in p or p.startswith("schemas/")]
    docs = [p for p in files if p.startswith(("docs/", "website/"))]
    win = [p for p in files if p.lower().endswith((".ps1", ".bat", ".cmd"))]
    mds = [p for p in files if p.endswith(".md")]
    root_docs = {n: os.path.isfile(os.path.join(SKILL_ROOT, n))
                 for n in ("README.md", "CHANGELOG.md", "SECURITY.md",
                           "LICENSE", "LICENSE.md", "CONTRIBUTING.md",
                           "AGENTS.md", ".gitignore")}
    dependabot = os.path.isfile(os.path.join(SKILL_ROOT, ".github", "dependabot.yml"))
    workflows = [p for p in files
                 if p.startswith(".github/workflows/") and p.endswith((".yml", ".yaml"))]

    n_name = n_desc = n_both = 0
    slugs = set()
    bad_read = 0
    for name in skill_dirs:
        slugs.add(name.lower())
        path = os.path.join(SKILL_ROOT, name, "SKILL.md")
        try:
            text = io.open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            bad_read += 1
            continue
        has_name, has_desc, _ = fm_fields(text)
        n_name += has_name
        n_desc += has_desc
        n_both += (has_name and has_desc)

    print("== d4 可扩展性 ==")
    print("  schema_files=%d  docs_dir_files=%d  total_files=%d"
          % (len(schemas), len(docs), len(files)))
    print("== d6 文档完善 ==")
    print("  root_docs=%s" % root_docs)
    print("  md_files=%d  mean_md_bytes=%.0f"
          % (len(mds), sum(os.path.getsize(os.path.join(SKILL_ROOT, p.replace('/', os.sep)))
                           for p in mds) / max(len(mds), 1)))
    print("== d7 适用场景 ==")
    print("  windows_scripts=%d" % len(win))
    print("== d8 功能覆盖 ==")
    print("  skill_dirs=%d  unique_slugs=%d  (dup_slugs=%d)"
          % (len(skill_dirs), len(slugs), len(skill_dirs) - len(slugs)))
    print("== d10 可控性 ==")
    print("  workflows=%d  dependabot=%s  security_md=%s"
          % (len(workflows), dependabot, root_docs.get("SECURITY.md")))
    print("== d12 工作流兼容性（frontmatter 可解析即入库可路由）==")
    print("  parsed=%d/%d  has_name=%d  has_desc=%d  both=%d  unreadable=%d"
          % (n_name + n_desc > 0, len(skill_dirs), n_name, n_desc, n_both, bad_read))
    print("  rates: name=%.3f desc=%.3f both=%.3f"
          % (n_name / max(len(skill_dirs), 1), n_desc / max(len(skill_dirs), 1),
             n_both / max(len(skill_dirs), 1)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
