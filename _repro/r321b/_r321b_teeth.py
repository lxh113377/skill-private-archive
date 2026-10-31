#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r321b_teeth.py —— R3 的牙口实测（负向对照，纯内存，不写真造对象）。

怎么运作：对每条探针，先确认现行口径判红，再套 R3：
  1 硬缺件（无占位形态）=> R3 必须仍红
  2 真实命名但树里没有（split-11.md）=> R3 必须仍红
  3 占位形态但树里 0 命中（dispatch-NN.md 在 story-review）=> R3 必须仍红（防 Goodhart 关键条）
  4 全大写真实名（STYLE_PRESETS.md 那类形态）=> R3 不误杀
  5 普查报出的 html-ppt/examples/my-talk/index.html => R3 必须仍红
最后反向验一次：把 split-NN.md 假造进内存树，R3 与现行口径都应消掉该条（存在性优先）。
"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "r320a", "entry_census", "check_r319a.py")
SPEC = importlib.util.spec_from_file_location("check_r319a_r321b3", SRC)
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)
import re
RS = importlib.util.spec_from_file_location("r321b_resolve", os.path.join(HERE, "_r321b_resolve.py"))
rs = importlib.util.module_from_spec(RS)
RS.loader.exec_module(rs)


def emit(obj):
    print(json.dumps(obj, ensure_ascii=False, sort_keys=True))


head_files, tree_src = m.head_tree()
up_names, up_dirs = m.upstream_excludes()
slugs = []
for pr in json.load(open(m.BASELINE, encoding="utf-8"))["pairs"]:
    s = pr.get("slug")
    if s and s not in slugs:
        slugs.append(s)
top_dirs = set()
for p in head_files:
    if "/" in p:
        top_dirs.add(p.split("/")[0])
others = set(x.lower() for x in top_dirs if x not in slugs)


def own_list(files, slug):
    pre = slug + "/"
    return sorted(p[len(pre):] for p in files if p.startswith(pre))


def r3_verdict(files, slug, rel):
    isph, rx = rs.shape(rel)
    hits = [x for x in own_list(files, slug) if rx is not None and rx.match(x)]
    return ("PLACEHOLDER_PATTERN" if isph and hits else "RED"), len(hits)


PROBES = [
    ("story-cover", "references/_r321b_truly_missing.md", "hard-missing"),
    ("story-import", "references/split-11.md", "real-name-absent"),
    ("story-review", "references/dispatch-NN.md", "placeholder-zero-hit"),
    ("story-review", "references/split-NN.md", "placeholder-with-hit"),
    ("data-analysis", "assets/STYLE_PRESETS.md", "allcaps-real-name"),
    ("data-analysis", "assets/report_template.md", "real-file-present"),
    ("html-ppt", "examples/my-talk/index.html", "census-item"),
    ("html-ppt", "examples/demo-deck/nope.html", "real-dir-absent"),
    ("frontend-slides", "STYLE_PRESETS.md", "n/a-single-seg"),
]
rows = []
for slug, rel, tag in PROBES:
    text = (m.entry_at("HEAD", slug) or "") + chr(10) + m.BT + rel + m.BT + chr(10)
    now = rel in m.judge(slug, text, head_files, up_names, up_dirs, others)[0]
    v, nhits = r3_verdict(head_files, slug, rel)
    rows.append({"slug": slug, "probe": rel, "tag": tag, "now_red": now,
                 "r3_verdict": v, "r3_hits": nhits, "r3_stays_red": v == "RED"})
emit({"stage": "r3_teeth", "rows": rows})

fake = dict(head_files)
fake["story-cover/references/split-NN.md"] = 1
v2, h2 = r3_verdict(fake, "story-cover", "references/split-NN.md")
now2 = "references/split-NN.md" in m.judge("story-cover", m.entry_at("HEAD", "story-cover") or "", fake, up_names, up_dirs, others)[0]
emit({"stage": "r3_reverse", "fake_tree_verdict": v2, "fake_tree_hits": h2, "now_red_after_fake": now2})
