#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r321b_driver.py —— R321B 只读取证驱动（判据本体逐字未动，只是被调用）。

为什么存在：复核 r320a 普查的 10 条断链，必须跑同一套判据函数
（check_r319a.py 的 path_tokens / norm / local_of / judge）；自写等价口径则结论不可引用。

怎么运作：
 1) importlib 按路径加载 check_r319a 为模块。它的 main() 挂在 __name__ 守卫上，
    import 时模块名是 check_r319a_r321b，不触发 main，零写面副作用。
 2) head_files 走 m.head_tree()：_recon_rows.json 缺件，自动退化成 git ls-tree -r -l HEAD（只读）。
 3) 逐 slug 调 m.judge() 复现 broken 名单，供上层与 entry_scan.r320.json 对账。
 4) 死代码证明：统计 52 件入口全部 token 是否可能含占位符字符集 <>{}*$^|% ——
    path_tokens 的白名单 PATH_OK 本就不含这些字符，所以 norm() 第 122 行的占位符分支打不到。
 5) 修正候选 R1（字母/通配占位形态）与 R2（同行上下文词）只在内存里套，
    再拿真断链反例测三条规则是否仍判红（牙齿 B），并把 split-NN.md 假造进内存树看它消失（牙齿 C）。

只读纪律：只走 m.git 已有读命令通道；不新增 git 写、不写 D:/global_skills、不写 r320a。
"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "r320a", "entry_census", "check_r319a.py")
SPEC = importlib.util.spec_from_file_location("check_r319a_r321b", SRC)
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)
NL = chr(10)
BT = chr(96)


def emit(obj):
    print(json.dumps(obj, ensure_ascii=False, sort_keys=True))


head_files, tree_src = m.head_tree()
head_sha = (m.git(["rev-parse", "HEAD"]) or "").strip()
emit({"stage": "tree", "head_sha": head_sha, "tree_source": tree_src, "tree_rows": len(head_files)})

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

repro = {}
for slug in slugs:
    text = m.entry_at("HEAD", slug) or ""
    broken, orphans, drop, sample, nf = m.judge(slug, text, head_files, up_names, up_dirs, others)
    repro[slug] = {"text": text, "broken": broken, "orphans": orphans, "drop": drop, "files": nf}
emit({"stage": "repro", "skills": len(slugs),
      "broken_total": sum(len(v["broken"]) for v in repro.values()),
      "broken_map": dict((k, v["broken"]) for k, v in repro.items() if v["broken"])})

PH_CHARS = "<>{}*$^|%"
tok_total = 0
tok_with_ph = []
for slug in slugs:
    for tk in m.path_tokens(repro[slug]["text"]):
        tok_total += 1
        if any(c in tk for c in PH_CHARS):
            tok_with_ph.append([slug, tk])
hist = {}
for slug in slugs:
    for k, v in repro[slug]["drop"].items():
        hist[k] = hist.get(k, 0) + v
emit({"stage": "deadcode", "tokens_scanned": tok_total, "tokens_with_ph_chars": len(tok_with_ph),
      "samples": tok_with_ph[:5], "drop_keys": sorted(hist.keys()),
      "placeholder_bucket_count": hist.get("placeholder", 0)})

# ---- 修正候选（只在内存套，判据本体不动） ----
SEP = set(["-", "_", "."])


def trailing_upper_run(stem):
    # R1 核心：取主干末尾连续大写字母串。要求前面是分隔符，
    # 否则 README / AGENTS 这类全大写真实文件名会被误杀。
    i = len(stem)
    while i > 0 and stem[i - 1].isalpha() and stem[i - 1].isupper():
        i -= 1
    run = stem[i:]
    if len(run) < 2 or i == 0:
        return ""
    if stem[i - 1] in SEP:
        return run
    return ""


def is_placeholder_shape(cand):
    # R1：任一路径段含通配 * ? 或以 { < $ 开头，或末段主干以 -NN / _NN 纯大写占位后缀收尾。
    for seg in cand.split("/"):
        if "*" in seg or "?" in seg:
            return True
        if seg[:1] in set(["{", "<", "$"]):
            return True
    last = cand.split("/")[-1]
    stem = last.rsplit(".", 1)[0] if "." in last else last
    return trailing_upper_run(stem) != ""


CTX_NARROW = ["分卷", "迁至"]
CTX_BROAD = ["分卷", "迁至", "模板", "template", "命名", "占位", "placeholder", "pattern"]


def line_ctx(text, cand, words):
    # R2：cand 出现的那一行同时命中上下文词 ⇒ 该行在讲命名规约而非指向具体文件。
    for line in text.split(NL):
        if cand in line and any(w in line for w in words):
            return True
    return False


def judge_variant(slug, text, mode):
    # 先跑现行口径，再只把命中修正规则的 broken 条目移出 broken；存在性检查本身不动。
    broken = m.judge(slug, text, head_files, up_names, up_dirs, others)[0]
    kept, killed = [], []
    for b in broken:
        if mode == "R1" and is_placeholder_shape(b):
            killed.append({"path": b, "by": "R1"})
            continue
        if mode == "R2n" and line_ctx(text, b, CTX_NARROW):
            killed.append({"path": b, "by": "R2n"})
            continue
        if mode == "R2b" and line_ctx(text, b, CTX_BROAD):
            killed.append({"path": b, "by": "R2b"})
            continue
        kept.append(b)
    return kept, killed


variants = {}
for mode in ("R1", "R2n", "R2b"):
    tot_k = 0
    det = {}
    for slug in slugs:
        kept, killed = judge_variant(slug, repro[slug]["text"], mode)
        if killed:
            det[slug] = {"before": len(repro[slug]["broken"]), "after": len(kept),
                         "killed": [x["path"] for x in killed]}
            tot_k += len(killed)
    variants[mode] = {"kills": tot_k, "detail": det}
emit({"stage": "variants", "variants": variants})

# ---- 牙齿 A：注入字面 split-NN.md 与真缺件，看现行口径各自是否计入 ----
slug_a = "story-cover"
base_a = len(repro[slug_a]["broken"])
txt_a = (repro[slug_a]["text"] + NL + "- leg " + BT + "references/split-NN.md" + BT +
         " 和 " + BT + "references/_r321b_absent.md" + BT + NL)
r_a = m.judge(slug_a, txt_a, head_files, up_names, up_dirs, others)[0]
emit({"stage": "teeth_A", "slug": slug_a, "base_broken": base_a, "after_inject": len(r_a),
      "items": r_a, "nn_still_counted": "references/split-NN.md" in r_a})

# ---- 牙齿 B：真断链反例在三条规则下必须仍判红 ----
PROBES = [
    ("story-cover", "references/_r321b_truly_missing.md", "hard-missing"),
    ("story-import", "references/split-11.md", "real-naming-but-absent"),
    ("story-import", "references/split-NN.md", "placeholder-shape"),
    ("html-ppt", "examples/demo-deck/nope.html", "real-dir-but-absent"),
    ("html-ppt", "examples/my-talk/index.html", "census-item"),
    ("story-review", "references/dispatch-NN.md", "placeholder-shape"),
    ("data-analysis", "assets/report_templateX.md", "typo-real-name"),
]
rows = []
for slug, rel, tag in PROBES:
    txt = repro[slug]["text"] + NL + BT + slug + "/" + rel + BT + NL
    now = m.judge(slug, txt, head_files, up_names, up_dirs, others)[0]
    out = {"slug": slug, "probe": rel, "tag": tag, "now_red": rel in now}
    for mode in ("R1", "R2n", "R2b"):
        out["red_" + mode] = rel in judge_variant(slug, txt, mode)[0]
    rows.append(out)
emit({"stage": "teeth_B", "rows": rows})

# ---- 牙齿 C：把 split-NN.md 假造进内存树 ⇒ 该条必须从 broken 消失 ----
fake = dict(head_files)
fake["story-cover/references/split-NN.md"] = 1
n_fake = m.judge("story-cover", repro["story-cover"]["text"], fake, up_names, up_dirs, others)[0]
emit({"stage": "teeth_C", "note": "literal split-NN.md faked into memory tree",
      "broken_after_fake": n_fake, "nn_still_red": "references/split-NN.md" in n_fake})

# ---- 树真值：每个 story-* 的 references/split-*.md 清单（走 m.tree_at 只读） ----
tree_truth = {}
for slug in slugs:
    if not slug.startswith("story-"):
        continue
    sub = m.tree_at("HEAD", slug)
    names = sorted(p.split("/", 2)[-1] for p in sub if p.startswith(slug + "/references/") and "/references/" in p)
    splits = sorted(os.path.basename(x) for x in names if os.path.basename(x).startswith("split-"))
    tree_truth[slug] = {"refs_count": len(names), "splits": splits,
                        "literal_NN": "split-NN.md" in splits}
hp = "html-ppt"
subhp = m.tree_at("HEAD", hp)
tree_truth[hp] = {"examples": sorted(os.path.dirname(p).split("/", 2)[-1] for p in subhp
                                     if p.startswith(hp + "/examples/"))}
emit({"stage": "tree_truth", "tree_truth": tree_truth})
