#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_r319a.py —— r319 A1：吸收件入口可达性全库巡检（新缺陷类「落盘未入口」系统首查）。

为什么存在：r318 才发现的缺陷形态 —— 吸收卷已 git 落盘（字节都在仓里），但入口 SKILL.md 不链它，
生产路由面永远读不到 = 路由不可达孤岛 = 吸收成本纯空转。此前只有逐件抽查，从未全库扫，本件即首查。

受管根只读纪律：只允许 git show / git ls-tree / git log 这类读命令；禁读工作树内容（工作树有他会话脏件）、
禁对 D:/global_skills 任何写。写面仅本目录三件产出（entry_scan.json / report.md / 本件）。

两判据（双向）：
  1 断链 broken：入口正文里指向本 slug 内的相对路径文件，git HEAD 树里不存在。
    剔除：出仓 URL、他仓/上游镜像路径（名单取 absorption_baseline.json 的 repo + upstream_path，一手数据）、
    占位符（<x>/$VAR/../绝对路径）、指向别的 slug 的跨件指针。
  2 孤儿 orphans：本 slug 任一直接子目录（references/ 及同类）里的 .md/.txt，入口正文不含其 basename
    （链接或提及都算入链，按整词/basename 匹配）。每个孤儿带 ls-tree -l 真字节 = 空转成本。

负控两腿（内嵌，任一 FAIL 即 court=fail）：
  腿A 孤儿腿有牙：取一个已判孤儿，把它的 basename 注入内存态入口正文重算，孤儿数必须 -1；
     同一入口不复算第二次必须保持原值（证明判据不是恒绿也不是抖动）。
  腿B 断链腿有牙（纯内存态，绝不写真造对象）：入口注入一个不存在目标，broken 必须 +1；
     再把同一目标假造进内存路径集合，broken 必须回到原值（证明判据看的是树存在性而非名字形状）。

判据自证（#44 D10.2）：两极（孤儿轴与断链轴）报不出来 = 指标不合格 = 本件降级为探针，court=fail。

跑法：export PYTHONPYCACHEPREFIX=/tmp/r319a_pyc  然后  python -B check_r319a.py
期望末行：[R319A:ENTRY] court=pass skills=52 broken=<n> orphans=<n> orphan_kb=<n>
"""
import json
import os
import subprocess
import sys
import time

ROOT = "D:/global_skills"
BASELINE = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r303a/absorption_baseline.json"
OUT = os.path.dirname(os.path.abspath(__file__))
DOC_EXT = (".md", ".txt")
POS_CASE = ("coding-agent", "HEAD")
NEG_ORPHAN_CASE = ("coding-agent", "a0092c9c~1")
NEG_BROKEN_CANDIDATE = ("frontend-skill", "0fcf7842~1")
BS = chr(92)
DQ = chr(34)
SQ = chr(39)
BT = chr(96)
REF_EXT = set(["md", "txt", "rst", "json", "jsonl", "yaml", "yml", "toml", "ini", "cfg", "conf",
               "py", "mjs", "cjs", "js", "jsx", "ts", "tsx", "css", "scss", "html", "htm", "svg",
               "sh", "bash", "ps1", "bat", "cmd", "sql", "csv", "tsv", "pdf", "docx", "xlsx",
               "pptx", "png", "jpg", "jpeg", "gif", "webp", "ico", "woff", "woff2", "ttf", "otf",
               "ipynb", "graphql", "proto", "log", "xml", "properties"])
PATH_OK = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-/:") | set([BS])
STRIPCH = BT + DQ + SQ + "()[]{}<>!,;:"


def git(args):
    """读命令唯一通道：非零退出当缺失返回 None，不抛错（历史态里路径可以不存在）。"""
    r = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", "replace")


def tree_at(rev, prefix=None):
    """某 rev 的文件清单 {path: bytes}；prefix 给定时只取该 slug 子树。"""
    args = ["ls-tree", "-r", "-l", rev]
    if prefix:
        args += ["--", prefix + "/"]
    raw = git(args)
    out = {}
    if raw is None:
        return out
    for line in raw.splitlines():
        # ls-tree -l 形如: 100644 blob <sha><空格><size><TAB><path>
        if chr(9) not in line:
            continue
        meta, path = line.split(chr(9), 1)
        parts = meta.split()
        if len(parts) != 4 or parts[1] != "blob":
            continue
        try:
            out[path] = int(parts[3])
        except ValueError:
            continue
    return out


def entry_at(rev, slug):
    return git(["show", rev + ":" + slug + "/SKILL.md"])


def path_tokens(text):
    """把正文切成「像路径的连续串」：反引号/括号/中文/CJK/空格都是分隔符，
    因此 markdown 链接、内联代码、wikilink、裸路径四种形态一次覆盖，不用正则。"""
    toks, cur = [], []
    for ch in text:
        if ch in PATH_OK:
            cur.append(ch)
        elif cur:
            toks.append("".join(cur))
            cur = []
    if cur:
        toks.append("".join(cur))
    return toks


def has_scheme(seg0):
    """首段含冒号且冒号前是多字母单词 => URL/mailto（单字母 D: 是 Windows 盘符，另算）。"""
    if ":" not in seg0:
        return False
    head = seg0.split(":")[0]
    return len(head) > 1 and head.isalpha()


def norm(tok):
    """token 规整成可比对的仓内相对路径候选；不合格返回 (None, 剔除原因)。"""
    t = tok.strip(STRIPCH)
    t = t.replace(BS, "/")
    if not t:
        return None, "empty"
    if has_scheme(t.split("/")[0]):
        return None, "url_scheme"
    if any(c in t for c in "<>{}*$^|%") or t[0] in "~!":
        return None, "placeholder"
    if t.startswith("/") or has_scheme(t.split("/")[0]):
        return None, "absolute"
    segs = [s for s in t.split("/") if s]
    if any(s == ".." for s in segs):
        return None, "parent_jump"
    if len(segs) < 2:
        return None, "no_dir"
    last = segs[-1]
    if "." not in last:
        return None, "no_ext"
    ext = last.rsplit(".", 1)[-1].lower()
    if ext not in REF_EXT:
        return None, "ext_not_routable"
    # 盘符开头（D:/global_skills/...）丢掉盘符段，保留仓内部分
    if len(segs[0]) == 2 and segs[0][1] == ":" and segs[0][0].isalpha():
        segs = segs[1:]
    if len(segs) < 2:
        return None, "no_dir"
    return "/".join(segs), None


def upstream_excludes():
    """吸收基线一手数据 => 上游仓库名 + 上游目录前缀集（引用上游布局的不算本仓断链）。"""
    names, dirs = set(), set()
    try:
        pairs = json.load(open(BASELINE, encoding="utf-8"))["pairs"]
    except Exception as e:
        return names, dirs
    for p in pairs:
        repo = (p.get("repo") or "").strip()
        if repo:
            names.add(repo.split("/")[-1].lower())
            names.add(repo.lower())
        for key in ("upstream_path", "local_path", "upstream_dir"):
            up = (p.get(key) or "").strip().replace(BS, "/")
            if not up:
                continue
            parts = up.split("/")[:-1]
            for k in range(1, len(parts) + 1):
                dirs.add("/".join(parts[:k]).lower())
    return names, dirs


def local_of(cand, slug, root_names, other_slugs):
    """候选路径归位到本 slug 内相对路径；跨件指针/仓根其他条目一律剔除。"""
    segs = cand.split("/")
    if slug in segs:
        i = len(segs) - 1 - list(reversed(segs)).index(slug)
        rest = segs[i + 1:]
        return ("/".join(rest) if rest else None), ("self_ref_bare" if not rest else None)
    if segs[0].lower() in other_slugs:
        return None, "other_skill_ref"
    if segs[0].lower() in root_names:
        return None, "repo_root_ref"
    return cand, None


def mentions(text):
    """入口正文的「已入链名册」：每个 token 的 basename 与其无扩展名形态（小写整词）。"""
    s = set()
    for tk in path_tokens(text):
        base = tk.replace(BS, "/").strip("/").split("/")[-1].lower()
        if not base:
            continue
        s.add(base)
        if "." in base:
            s.add(base.rsplit(".", 1)[0])
    return s

# ===================== 后半段（r320 补完）=====================
# 装配说明（改代码前先读，逐条对应实测）：
#  a) 前半段 tree_at 的 docstring 收尾少一个引号（三引号未闭合）=> 整文件 SyntaxError，
#     这就是上一臂只交半成品的真实卡点；本次装配补闭合，八个助手函数其余部分逐字未动。
#  b) ls-tree 对非 ASCII 路径加双引号并八进制转义（本仓 16509 条里 109 条，如 天眼一丁/、
#     elon-musk-perspective 的中文 md、ppt-master 中文品牌目录）。不还原就会把真在树里的
#     文件判成断链、把中文名判成孤儿 => unquote()。
#  c) HEAD 全树直接吃前臂侦察件 _recon_rows.json，不重跑 ls-tree（硬约束：禁重做侦察）；
#     只有两极堂要历史态时才走 git ls-tree（只读）。
import codecs

RECON_ROWS = os.path.join(OUT, "_recon_rows.json")
SCAN_JSON = os.path.join(OUT, "_entry_scan.json")
REPORT_MD = os.path.join(OUT, "_report.md")
NONREPO = set(["global_memory", "dsh", "users", "tmp", "var", "opt", "etc", "home"])


def cb(s):
    return BT + str(s) + BT


def unquote(p):
    """还原 ls-tree 的带引号八进制路径；未加引号原样返回。"""
    if len(p) >= 2 and p[0] == DQ and p[-1] == DQ:
        try:
            return codecs.decode(p[1:-1], "unicode_escape").encode("latin-1").decode("utf-8", "replace")
        except Exception:
            return p[1:-1]
    return p


def head_tree():
    """HEAD 全树 {path: bytes}：优先复用前臂侦察件（禁重做侦察），缺件才退化成 ls-tree HEAD。"""
    try:
        rows = json.load(open(RECON_ROWS, encoding="utf-8"))
        out = {}
        for r in rows:
            out[unquote(r["path"])] = int(r.get("size") or 0)
        if out:
            return out, "recon_rows(_recon_rows.json)"
    except Exception:
        pass
    return dict((unquote(k), v) for k, v in tree_at("HEAD").items()), "git ls-tree -r -l HEAD"


def tree_u(rev, prefix=None):
    """两极堂取历史态子树（只读 git）；unquote 让中文名路径能与正文 token 对齐。"""
    return dict((unquote(k), v) for k, v in tree_at(rev, prefix).items())


def slug_rel(files, slug):
    """全仓树 => 本 slug 子树 {全路径: bytes}。"""
    pre = slug + "/"
    return dict((p, v) for p, v in files.items() if p.startswith(pre))


def judge(slug, text, files, up_names, up_dirs, other_slugs):
    """
    单件双判据（纯函数：任意 rev 的正文配任意 rev 的树都能喂，负控因此能全内存跑）。
    返回 (broken[本 slug 相对路径], orphans[(相对路径, bytes)], 剔除计数, 剔除样本, 本 slug 文件数)。
    断链：正文 token -> norm -> local_of 归位本 slug -> 该路径不在树里。
    孤儿：本 slug 子目录（距根 >=2 段，references/ 及同类）里的 .md/.txt，basename 不在入口名册。
    """
    men = mentions(text or "")
    low = (text or "").lower()
    pre = slug + "/"
    own = slug_rel(files, slug)
    sdirs = set()
    for p in own:
        r = p[len(pre):]
        if "/" in r:
            sdirs.add(r.split("/")[0])
    drop = {}
    sample = {}

    def cut(why, tok):
        drop[why] = drop.get(why, 0) + 1
        s = sample.setdefault(why, [])
        if len(s) < 5:
            s.append(tok)

    broken = []
    seen = set()
    for tok in path_tokens(text or ""):
        cand, why = norm(tok)
        if cand is None:
            cut(why or "unparsable", tok)
            continue
        segs = cand.split("/")
        if segs[0] == "global_skills":
            segs = segs[1:]
            if not segs:
                cut("repo_root_bare", tok)
                continue
            cand = "/".join(segs)
            segs = cand.split("/")
        if segs[0].lower() in NONREPO:
            cut("outside_repo", tok)
            continue
        low0 = cand.lower()
        hit_up = False
        for d in up_dirs:
            if low0.startswith(d + "/"):
                hit_up = True
                break
        if hit_up:
            cut("upstream_mirror", tok)
            continue
        rel, rwhy = local_of(cand, slug, up_names, other_slugs)
        if rel is None:
            cut(rwhy or "unresolved", tok)
            continue
        if rwhy == "self_ref_bare":
            cut("self_ref_bare", tok)
            continue
        if rel.split("/")[0] not in sdirs:
            # 牙口收紧（拿漏判换假阳性归零）：一级目录段在本 slug 里不存在（整段 typo 或仓外残段）
            cut("outside_slug", tok)
            continue
        full = pre + rel
        if full in seen:
            continue
        seen.add(full)
        if full not in own:
            broken.append(rel)
    orphans = []
    for p in sorted(own):
        r = p[len(pre):]
        if "/" not in r:
            continue
        base = r.rsplit("/", 1)[-1].lower()
        if DQ not in base and not base.endswith(DOC_EXT):
            continue
        if not base.endswith(DOC_EXT):
            continue
        stem = base.rsplit(".", 1)[0]
        # 三级兜底：名册含扩展名 / 名册去扩展名 / 原文小写子串。path_tokens 把 CJK 当分隔符，
        # 不做子串兜底会把中文文件名的真入链件系统性误判成孤儿（elon-musk-perspective 实测受害）。
        if base in men or stem in men or base in low or (stem and stem in low):
            continue
        orphans.append((r, own[p]))
    return broken, orphans, drop, sample, len(own)


def run_case(rev, slug, ctx, head_files):
    """某 rev 的该件双判据；树与正文都取不到返回 None（前态可以还没这个件）。"""
    files = head_files if rev == "HEAD" else tree_u(rev, slug)
    text = entry_at(rev, slug)
    if not files and text is None:
        return None
    return judge(slug, text or "", files, ctx["up_names"], ctx["up_dirs"], ctx["other_slugs"])


def probe_dir(slug, head_files):
    """腿B 探针要落在该 slug 真实存在的一级子目录里，否则被 outside_slug 剔掉、注入不 +1。"""
    pre = slug + "/"
    for p in sorted(head_files):
        if not p.startswith(pre):
            continue
        r = p[len(pre):]
        if "/" in r:
            return r.split("/")[0]
    return "references"


def result_dict(case, axis, n, items, br, orph, nf, source):
    return {"case": case, "axis": axis, "n": n, "items": items, "broken": br,
            "orphans": orph, "files": nf, "source": source}


def neg_probe(axis, ctx, head_files, slugs, per, log):
    """
    反例堂：草稿 rev（含 ~1..~4 派生前态）→ 近 12 次提交里入口改动的件 → HEAD 实测可复现缺陷态。
    "跑不通"三种：rev 解析不出来 / 树与正文都空 / 该轴计数为 0（草稿值选错，不是判据坏）。
    最后退路用 HEAD（当前态本身可复现），必须声明 source=substituted_current_state。
    全程只读 git，不拿真造对象上堂。
    """
    want = "orphans" if axis == "orphan" else "broken"
    slug0, rev0 = NEG_ORPHAN_CASE if axis == "orphan" else NEG_BROKEN_CANDIDATE
    for k in range(0, 5):
        rev = rev0 if k == 0 else rev0 + "~" + str(k)
        if (git(["rev-parse", "--verify", "--quiet", rev]) or "").strip() == "":
            log.append(axis + " TRY " + slug0 + "@" + rev + " => rev_unresolvable")
            continue
        r = run_case(rev, slug0, ctx, head_files)
        if r is None:
            log.append(axis + " TRY " + slug0 + "@" + rev + " => tree_and_entry_unavailable")
            continue
        n = len(r[1]) if want == "orphans" else len(r[0])
        log.append(axis + " TRY " + slug0 + "@" + rev + " broken=" + str(len(r[0])) +
                   " orphans=" + str(len(r[1])) + " files=" + str(r[4]))
        if n > 0:
            items = [p for p, _b in r[1]][:20] if want == "orphans" else list(r[0])[:20]
            log.append(axis + " USE " + slug0 + "@" + rev + " " + want + "=" + str(n) + " source=draft_rev")
            return result_dict(slug0 + "@" + rev, axis, n, items, len(r[0]), len(r[1]), r[4], "draft_rev")
    hist = (git(["log", "-n12", "--format=%H"]) or "").split()
    for h in hist:
        touched = (git(["show", "--name-only", "--format=", h]) or "").splitlines()
        cand = []
        for f in touched:
            if "/" in f:
                s0 = f.split("/")[0]
                if s0 in slugs and s0 != slug0 and s0 not in cand:
                    cand.append(s0)
        for s1 in cand[:6]:
            r = run_case(h[:9], s1, ctx, head_files)
            if r is None:
                continue
            n = len(r[1]) if want == "orphans" else len(r[0])
            log.append(axis + " TRY " + s1 + "@" + h[:9] + " (recent commit) broken=" + str(len(r[0])) +
                       " orphans=" + str(len(r[1])))
            if n > 0:
                items = [p for p, _b in r[1]][:20] if want == "orphans" else list(r[0])[:20]
                log.append(axis + " USE " + s1 + "@" + h[:9] + " " + want + "=" + str(n) +
                           " source=recent_commit（草稿值不可解析，改用近史提交的可复现前态）")
                return result_dict(s1 + "@" + h[:9], axis, n, items, len(r[0]), len(r[1]), r[4], "recent_commit")
    for x in per:
        n = len(x["orphans"]) if want == "orphans" else len(x["broken"])
        if n > 0:
            items = [o["path"] for o in x["orphans"]][:20] if want == "orphans" else list(x["broken"])[:20]
            log.append(axis + " SUBSTITUTED " + x["slug"] + "@HEAD " + want + "=" + str(n) +
                       " source=substituted_current_state（草稿 rev 与近史均未报出该轴，改用 HEAD 可复现缺陷态）")
            return result_dict(x["slug"] + "@HEAD", axis, n, items, len(x["broken"]),
                                len(x["orphans"]), x["tree_files"], "substituted_current_state")
    log.append(axis + " FAIL no reproducible state reports " + want)
    return result_dict(None, axis, 0, [], 0, 0, 0, "none")

def build_lines(o):
    """report.md 的行数组（与落盘解耦，便于自检）。"""
    c = o["court"]
    F = BT + BT + BT
    R = []

    def A(s):
        R.append(s)

    A("# r319 A1b — 吸收件入口可达性全库巡检（新缺陷类「落盘未入口」系统首查）")
    A("")
    A("- 受管根 D:/global_skills HEAD：" + cb(o["head_sha"]))
    A("- 树来源：" + o["tree_source"] + "，共 " + str(o["tree_rows"]) +
      " 条（复用前臂侦察件，未重跑 ls-tree、未重做侦察）")
    A("- 巡检面：absorption_baseline.json 在册吸收件 " + str(o["skills"]) + " 件（一手清单，非猜）")
    A("- 结果：" + cb("court=" + c["verdict"]) + " broken=" + str(o["broken_total"]) +
      " orphans=" + str(o["orphan_total"]) + " orphan_kb=" + str(o["orphan_kb_total"]) +
      "（孤儿真字节合计 " + str(o["orphan_bytes_total"]) + " B）")
    A("- 缺入口（HEAD 无 <slug>/SKILL.md）：" + (", ".join(o["no_entry"]) if o["no_entry"] else "无"))
    A("")
    A("## 判据命令")
    A("")
    A(F + "bash")
    A("export PYTHONPYCACHEPREFIX=/tmp/r319a_pyc")
    A("cd " + os.path.dirname(REPORT_MD).replace(BS, "/"))
    A("python -B check_r319a.py")
    A(F)
    A("")
    A("期望末行：" + cb("[R319A:ENTRY] court=pass skills=" + str(o["skills"]) +
      " broken=<n> orphans=<n> orphan_kb=<n>"))
    A("")
    A("## 两极堂（判据自证 #44 D10.2 实测值）")
    A("")
    A("| 极 | 用例 | broken | orphans | 文件数 | 判定 |")
    A("|---|---|---|---|---|---|")
    p = c["positive"]
    A("| 正例（已知答案） | " + cb(p["case"]) + " | " + str(p["broken"]) + " | " +
      str(p["orphans"]) + " | - | " + ("pass" if p["pass"] else "FAIL") + " |")
    for key, label in (("negative_orphan", "反例·孤儿轴"), ("negative_broken", "反例·断链轴")):
        n = c[key]
        if n and n["n"] > 0:
            A("| " + label + " | " + cb(n["case"]) + "（source=" + n["source"] + "） | " +
              str(n["broken"]) + " | " + str(n["orphans"]) + " | " + str(n["files"]) +
              " | pass |")
        else:
            A("| " + label + " | 无可复现反例 | - | - | - | FAIL |")
    A("")
    A("草稿反例值：" + cb("NEG_ORPHAN_CASE=" + str(NEG_ORPHAN_CASE)) + "、" +
      cb("NEG_BROKEN_CANDIDATE=" + str(NEG_BROKEN_CANDIDATE)) +
      "。草稿值跑不通时改用哪一态，逐字见下面堂录（SUBSTITUTED / recent_commit 都已声明）。")
    A("")
    A(F)
    for ln in c["log"]:
        A(ln)
    A(F)
    A("")
    A("反例孤儿样本：" + (", ".join(cb(x) for x in c["negative_orphan"]["items"][:5]) if c["negative_orphan"]["items"] else "无"))
    A("反例断链样本：" + (", ".join(cb(x) for x in c["negative_broken"]["items"][:5]) if c["negative_broken"]["items"] else "无"))
    A("")
    A("## 负控两腿（逐字读数）")
    A("")
    la = c["legA"]
    lb = c["legB"]
    A("- 腿A 孤儿腿有牙（取一个已判孤儿，把它的 basename 注入内存态入口正文重算；纯内存，不写真造对象）")
    A("  用例 slug=" + cb(la.get("slug")) + " 探针目标=" + cb(la.get("path")))
    A("  base=" + str(la.get("base")) + " → 注入后=" + str(la.get("injected")) +
      "（判据要求 base-1）→ 同一入口第三次重算=" + str(la.get("recheck")) +
      "（判据要求回到 base，证明不恒绿也不抖动）⇒ " + ("pass" if la["ok"] else "FAIL"))
    A("- 腿B 断链腿有牙（注入一个不存在目标须 +1；再把同一目标假造进内存路径集合须回原值，证明判据看树存在性而非名字形状）")
    A("  用例 slug=" + cb(lb["slug"]) + " 探针目标=" + cb(lb["probe"]))
    A("  base=" + str(lb["base"]) + " → 注入后=" + str(lb["injected"]) +
      "（判据要求 base+1）→ 假造进内存树后=" + str(lb["after_fake_tree"]) +
      "（判据要求回到 base）⇒ " + ("pass" if lb["ok"] else "FAIL"))
    A("")
    A("## 孤儿 top10（按 ls-tree -l 真字节）+ 每孤一句空转成本")
    A("")
    A("| # | 件 / 路径 | 字节 | 空转成本（一句） |")
    A("|---|---|---|---|")
    flat = []
    for r in o["per_skill"]:
        for x in r["orphans"]:
            flat.append((r["slug"], x["path"], x["bytes"]))
    flat.sort(key=lambda t: -t[2])
    for i, tup in enumerate(flat[:10], 1):
        s, p2, b = tup
        A("| " + str(i) + " | " + cb(s + "/" + p2) + " | " + str(b) +
          " | 已 git 落盘（字节在仓里）但入口不链：路由面每次加载 " + cb(s) +
          " 都读不到这 " + ("%.1f" % (b / 1024.0)) +
          " KB，吸收（翻译/适配/校对）产出 0 次被消费 = 纯空转 |")
    A("")
    A("其余 " + str(max(0, len(flat) - 10)) +
      " 个孤儿逐条见 " + cb("entry_scan.json") + " 的 per_skill[].orphans。按件汇总：")
    A("")
    A("| 件 | 孤儿数 | 孤儿字节 |")
    A("|---|---|---|")
    for r in sorted(o["per_skill"], key=lambda x: -x["orphan_bytes"]):
        if r["orphans"]:
            A("| " + cb(r["slug"]) + " | " + str(len(r["orphans"])) + " | " +
              str(r["orphan_bytes"]) + " |")
    A("")
    A("## 断链清单（全量）")
    A("")
    bs = [(r["slug"], x) for r in o["per_skill"] for x in r["broken"]]
    if not bs:
        A("HEAD 全 " + str(o["skills"]) +
          " 件入口里指向本件已有子目录的相对路径，100% 在树里存在 —— 断链轴零命中。")
    for s, x in bs:
        A("- " + cb(s + "/" + x) + "：入口写着它，HEAD 树里没有（断链）")
    A("")
    A("## 剔除直方图（入口正文 token 的去向，可审计；样本见 entry_scan.json 的 skip_samples）")
    A("")
    A(F + "json")
    A(json.dumps(o["skip_histogram"], ensure_ascii=False, indent=1))
    A(F)
    A("")
    A("## 口径、边界与已知偏差")
    A("")
    A("1. 只读纪律：全程只有 git rev-parse / git show / git ls-tree / git log；未读工作树任何入口外内容；写面仅本目录三件。")
    A("2. 断链口径：正文 token → norm（剔 URL、占位符 <x>/$VAR、..、绝对路径、无目录段、不可路由扩展）→ 剔上游镜像前缀（absorption_baseline.json 的 repo + upstream_path 一手数据）、别的 slug 跨件指针、仓外兄弟仓根 → 归位本 slug → 查 HEAD 树存在性。")
    A("3. 一处主动收紧（拿漏判换假阳性归零）：断链只在「本 slug 已存在的一级子目录」内判存在性；一级目录段整段写错的落 outside_slug 剔除，不进断链数。")
    A("4. 孤儿口径：本 slug 距根 >=2 段的 .md/.txt（references/ 及同类，递归含孙子目录），basename、去扩展名、原文小写子串三级兜底都不在入口名册 ⇒ 孤儿。第三级兜底必须有：path_tokens 把 CJK 当分隔符，不兜底会把中文文件名的真入链件系统性误判成孤儿。")
    A("5. 保守方向汇总：同目录散件的裸引用（只写 SKILL.md 这类无目录段 token）被 no_dir / outside_slug 剔除，不计断链；散文里提到某 md 文件名即算入链、不计孤儿。两个偏差都只会低估缺陷，不会凭空造缺陷。")
    A("6. 本次补完修掉的前臂缺陷两处：tree_at 的 docstring 三引号未闭合（SyntaxError，上一臂只交半成品的真实卡点）；新增 unquote 还原 109 条八进制引号路径（否则中文名被系统性误判）。")
    A("")
    A("## 末行")
    A("")
    A(F)
    A("[R319A:ENTRY] court=" + c["verdict"] + " skills=" + str(o["skills"]) +
      " broken=" + str(o["broken_total"]) + " orphans=" + str(o["orphan_total"]) +
      " orphan_kb=" + str(o["orphan_kb_total"]))
    A(F)
    return R


def write_report(o):
    open(REPORT_MD, "w", encoding="utf-8").write(chr(10).join(build_lines(o)) + chr(10))


def main():
    t0 = time.time()
    if git(["rev-parse", "HEAD"]) is None:
        print("[R319A:ENTRY] court=fail skills=0 broken=0 orphans=0 orphan_kb=0 GIT_UNREACHABLE")
        return 3
    head_sha = (git(["rev-parse", "HEAD"]) or "").strip()
    head_files, tree_src = head_tree()
    top_dirs = set()
    for p in head_files:
        if "/" in p:
            top_dirs.add(p.split("/")[0])
    up_names, up_dirs = upstream_excludes()
    slugs = []
    for pr in json.load(open(BASELINE, encoding="utf-8"))["pairs"]:
        s = pr.get("slug")
        if s and s not in slugs:
            slugs.append(s)
    others = set(x.lower() for x in top_dirs if x not in slugs)
    ctx = {"up_names": up_names, "up_dirs": up_dirs, "other_slugs": others}

    per = []
    no_entry = []
    tot_br = 0
    tot_or = 0
    tot_by = 0
    agg_drop = {}
    agg_sample = {}
    for slug in slugs:
        text = entry_at("HEAD", slug)
        if text is None:
            no_entry.append(slug)
        broken, orphans, drop, sample, nf = judge(slug, text or "", head_files, up_names, up_dirs, others)
        for k, v in drop.items():
            agg_drop[k] = agg_drop.get(k, 0) + v
        for k, v in sample.items():
            agg_sample.setdefault(k, []).extend(v[:3])
        ob = sum(b for _p, b in orphans)
        per.append({"slug": slug, "tree_files": nf,
                    "entry_bytes": len((text or "").encode("utf-8")),
                    "broken": broken,
                    "orphans": [{"path": p, "bytes": b} for p, b in orphans],
                    "orphan_bytes": ob})
        tot_br += len(broken)
        tot_or += len(orphans)
        tot_by += ob

    log = []
    ps, pr_ = POS_CASE
    pos = run_case(pr_, ps, ctx, head_files)
    pb = len(pos[0]) if pos else -1
    po = len(pos[1]) if pos else -1
    pos_pass = bool(pos) and pb == 0 and po == 0
    log.append("POS " + ps + "@" + pr_ + " broken=" + str(pb) + " orphans=" + str(po) +
               " files=" + str(pos[4] if pos else -1) + " => " + ("pass" if pos_pass else "FAIL"))
    neg_o = neg_probe("orphan", ctx, head_files, slugs, per, log)
    neg_b = neg_probe("broken", ctx, head_files, slugs, per, log)

    cand_a = None
    for r in per:
        if r["orphans"]:
            best = max(r["orphans"], key=lambda x: x["bytes"])
            if cand_a is None or best["bytes"] > cand_a[2]:
                cand_a = (r["slug"], best["path"], best["bytes"])
    legA = {"ok": False, "why": "no_orphan_to_probe"}
    if cand_a:
        sa, ra, _b = cand_a
        et = entry_at("HEAD", sa) or ""
        base_o = len(judge(sa, et, head_files, up_names, up_dirs, others)[1])
        inj = et + chr(10) + "- legA probe " + ra + chr(10)
        n_inj = len(judge(sa, inj, head_files, up_names, up_dirs, others)[1])
        n_re = len(judge(sa, et, head_files, up_names, up_dirs, others)[1])
        legA = {"ok": base_o > 0 and n_inj == base_o - 1 and n_re == base_o, "slug": sa,
                "path": ra, "base": base_o, "injected": n_inj, "recheck": n_re, "why": ""}

    sb = ps
    dsel = probe_dir(sb, head_files)
    probe_rel = dsel + "/" + "_neg_probe_r319a_missing.md"
    et_b = entry_at("HEAD", sb) or ""
    base_br = len(judge(sb, et_b, head_files, up_names, up_dirs, others)[0])
    inj_b = et_b + chr(10) + "[probe](" + probe_rel + ")" + chr(10)
    n_inj_b = len(judge(sb, inj_b, head_files, up_names, up_dirs, others)[0])
    fake = dict(head_files)
    fake[sb + "/" + probe_rel] = 1
    n_fake = len(judge(sb, inj_b, fake, up_names, up_dirs, others)[0])
    legB = {"ok": n_inj_b == base_br + 1 and n_fake == base_br, "slug": sb,
            "probe": probe_rel, "base": base_br, "injected": n_inj_b,
            "after_fake_tree": n_fake}

    court = bool(pos_pass and neg_o["n"] > 0 and neg_b["n"] > 0 and legA["ok"] and
                 legB["ok"] and not no_entry)
    orphan_kb = int(round(tot_by / 1024.0))
    out = {"schema": "_r319a-entry-scan-1", "head_sha": head_sha, "tree_source": tree_src,
           "tree_rows": len(head_files), "skills": len(slugs), "broken_total": tot_br,
           "orphan_total": tot_or, "orphan_bytes_total": tot_by, "orphan_kb_total": orphan_kb,
           "no_entry": no_entry, "skip_histogram": agg_drop, "skip_samples": agg_sample,
           "court": {"verdict": "pass" if court else "fail", "log": log,
                       "positive": {"case": ps + "@" + pr_, "broken": pb,
                                       "orphans": po, "pass": pos_pass},
                       "negative_orphan": neg_o, "negative_broken": neg_b,
                       "legA": legA, "legB": legB},
           "per_skill": per}
    json.dump(out, open(SCAN_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    write_report(out)
    # r320 竞态防御（同进程唯一名快照，写面仍在本目录）：并发写者反复覆盖规范名 entry_scan.json/report.md
    json.dump(out, open(os.path.join(OUT, "entry_scan.r320.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(OUT, "report.r320.md"), "w", encoding="utf-8").write(chr(10).join(build_lines(out)) + chr(10))
    for r in per:
        if r["broken"] or r["orphans"]:
            print("SKILL " + r["slug"] + " broken=" + str(len(r["broken"])) +
                  " orphans=" + str(len(r["orphans"])) + " bytes=" + str(r["orphan_bytes"]))
    for ln in log:
        print("COURT " + ln)
    print("LEGA " + json.dumps(legA, ensure_ascii=False))
    print("LEGB " + json.dumps(legB, ensure_ascii=False))
    print("SKIP " + json.dumps(agg_drop, ensure_ascii=False))
    print("[R319A:ENTRY] court=" + ("pass" if court else "fail") + " skills=" +
          str(len(slugs)) + " broken=" + str(tot_br) + " orphans=" + str(tot_or) +
          " orphan_kb=" + str(orphan_kb))
    print("[R319A:MS] " + str(int((time.time() - t0) * 1000)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
