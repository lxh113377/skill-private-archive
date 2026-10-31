#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r321b_resolve.py —— 修正候选 R3（占位符展开对树）实测，只读、判据本体不动。

为什么存在：只按名字形状豁免（R1）会把真断链里恰好全大写的文件名一起放过；
R3 不放宽存在性检查本身，而是把占位符形态当 glob 去 HEAD 树里展开：
展开命中 >=1 个真实文件 => 记 PLACEHOLDER_PATTERN、从 broken 分母剔除并单独计数；
展开命中 0 个 => 仍判红。真断链因此不可能被一起放过。

怎么运作：末段主干的纯大写占位后缀（-NN / -XXX）展开为 [0-9]{1,4} 或 [A-Z]{2,}；
* -> 段内任意；? -> 单字符；{x}/<x>/$VAR -> 整段任意；其余字符 re.escape 保字面。
对普查报出的每条 broken，在本 slug 的树文件集上做整路径正则匹配并计数。
"""
import importlib.util
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "r320a", "entry_census", "check_r319a.py")
SPEC = importlib.util.spec_from_file_location("check_r319a_r321b2", SRC)
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


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
SEP = "-_."


def upper_tail(stem):
    # 返回末段主干结尾的纯大写占位串（要求前面是分隔符），无则空串
    i = len(stem)
    while i > 0 and stem[i - 1].isalpha() and stem[i - 1].isupper():
        i -= 1
    run = stem[i:]
    if len(run) < 2 or i == 0 or stem[i - 1] not in SEP:
        return "", 0
    return run, i


def shape(cand):
    # 判断是否占位形态，并给出可用于对树展开的正则；非占位返回 (False, None)
    if "*" in cand or "?" in cand or "{" in cand or "<" in cand or "$" in cand:
        pass
    else:
        last = cand.split("/")[-1]
        stem = last.rsplit(".", 1)[0] if "." in last else last
        run, _pos = upper_tail(stem)
        if not run:
            return False, None
    parts = cand.split("/")
    body = []
    for idx, seg in enumerate(parts):
        is_last = idx == len(parts) - 1
        buf = []
        i = 0
        while i < len(seg):
            ch = seg[i]
            if ch == "*":
                buf.append("[^/]*")
                i += 1
                continue
            if ch == "?":
                buf.append("[^/]")
                i += 1
                continue
            if ch == "$":
                j = i + 1
                while j < len(seg) and (seg[j].isalnum() or seg[j] == "_"):
                    j += 1
                buf.append("[^/]+")
                i = j
                continue
            if ch in "{<":
                close = "}" if ch == "{" else ">"
                j = seg.find(close, i)
                if j > 0:
                    buf.append("[^/]+")
                    i = j + 1
                    continue
            if is_last and ch.isalpha() and ch.isupper():
                stem = seg.rsplit(".", 1)[0] if "." in seg else seg
                run, pos = upper_tail(stem)
                if run and i == pos:
                    buf.append("(?:[0-9]{1,4}|[A-Z]{2,})")
                    i += len(run)
                    continue
            buf.append(re.escape(ch))
            i += 1
        body.append("".join(buf))
    return True, re.compile("^" + "/".join(body) + "$")


if __name__ == "__main__":
    res = []
    for slug in sorted(slugs):
        text = m.entry_at("HEAD", slug) or ""
        broken = m.judge(slug, text, head_files, up_names, up_dirs, others)[0]
        pre = slug + "/"
        own = sorted(p[len(pre):] for p in head_files if p.startswith(pre))
        for b in broken:
            isph, rx = shape(b)
            hits = sorted(x for x in own if rx is not None and rx.match(x))
            res.append({"slug": slug, "path": b, "ph_shape": isph, "expand_hits": len(hits),
                        "hits_sample": hits[:12],
                        "verdict": "PLACEHOLDER_PATTERN" if isph and hits else "RED"})
    emit({"stage": "r3", "rows": res, "red": [r["slug"] + "/" + r["path"] for r in res if r["verdict"] == "RED"],
          "killed": sum(1 for r in res if r["verdict"] == "PLACEHOLDER_PATTERN")})

