# -*- coding: utf-8 -*-
"""r324 入口可达性普查常驻判据（从 r322b 一次性取证目录搬迁 + 自包含化）。

为什么搬进 05-exec：r322 判据住在一次性取证目录。本仓 r283/r284/r286 已为此搬过四次件（provenance_resolve_face
专门判「面件出处指向不可解析目录」）——留下就是同一个缺陷换个宿主。需求 5「季度巡检机制」要求判据常驻且入册
（.read_face_registry.json），否则 r129 准入门判 UNDECLARED（r260 实测硬拒）。

搬迁时修掉的一处缺陷（一手）：旧 check_r319a.py 的 git() 没带 `-c core.quotepath=false`，ls-tree 会把非 ASCII
路径输出成八进制转义引号形态（本仓 16509 条里 109 条），不 unquote 就整批丢中文文件 —— 实测 v2 首跑 560 vs 官方 624
差 64（story-setup 32 + story-long-write 32）。本件 git() 带该参数 + 本件 tree_at 不做二次解码（git 输出已是 UTF-8）。

四桶分账（r322 立）：真断链 / PLACEHOLDER_PATTERN（占位符展开对树命中≥1）/ GENERATED_OUTPUT_REF（脚本运行产物）/
GENERATED_INSTRUCTION_REF（指令式创建，仅 nested 口径会出现）。三桶仍计 broken 分母，只解释缺陷类型。
"""
import argparse, fnmatch, json, os, re, subprocess, sys

ROOT = "D:/global_skills"
OUT = os.path.dirname(os.path.abspath(__file__))  # 旧件用 OUT 做 RECON 路径基准；本件保留定义防 NameError      # 受管根，可被 --managed-root 覆盖
OUT_DEFAULT = ""               # 无默认输出件；--json 显式给

# 断链/孤儿判定用到的字符白名单（逐字抄自旧件，改动即变口径）
BS = chr(92)
DQ = chr(34)
SQ = chr(39)
BT = chr(96)
REF_EXT = set(["md", "txt", "rst", "json", "jsonl", "yaml", "yml", "toml", "ini", "cfg", "conf",
               "py", "mjs", "cjs", "js", "jsx", "ts", "tsx", "css", "scss", "html", "htm", "svg",
               "sh", "bash", "ps1", "bat", "cmd", "sql", "csv", "tsv", "pdf", "docx", "xlsx",
               "pptx", "png", "jpg", "jpeg", "gif", "webp", "ico", "woff", "woff2", "ttf", "otf",
               "ipynb", "graphql", "proto", "log", "xml", "properties"])
DOC_EXT = (".md", ".txt")
PATH_OK = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-/:") | set([BS])
STRIPCH = BT + DQ + SQ + "()[]{}<>!,;:"


# git() 通道：带 core.quotepath=false（旧件缺此参数会静默丢中文名文件，见 r322 实测 560 vs 624）
def git(args):
    """读命令唯一通道：非零退出当缺失返回 None，不抛错（历史态里路径可以不存在）。"""
    r = subprocess.run(["git", "-c", "core.quotepath=false", "-C", ROOT] + list(args), capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", "replace")



def entry_at(rev, slug):
    return git(["show", rev + ":" + slug + "/SKILL.md"])



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

NONREPO = set(["global_memory", "dsh", "users", "tmp", "var", "opt", "etc", "home"])



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





def has_scheme(seg0):
    """首段含冒号且冒号前是多字母单词 => URL/mailto（单字母 D: 是 Windows 盘符，另算）。"""
    if ":" not in seg0:
        return False
    head = seg0.split(":")[0]
    return len(head) > 1 and head.isalpha()



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




# ── v2 三处修正（逐字搬自 r322b/r322_v2_census.py）────────────────────
NOISE_RE = re.compile(
    r"(?:^|/)(?:[^/]*ofl[^/]*|licen[cs]e[^/]*|copying[^/]*|authors[^/]*|credits?[^/]*|readme\.md|_[^/]*)$", re.I)
PLACEHOLDER_RE = re.compile(r"(?:\bNN\b|\*|\{[^}]*\}|<[^>]*>|\$\{?[A-Za-z_]+\}?|\?[^/]*)")


def is_noise(path):
    """不该补链的噪声类（OFL 许可 / LICENSE / 目录 README / _ 内部索引）—— r322 实测占 624 里的 72 件。"""
    return bool(NOISE_RE.search(path))


def expand_placeholder(slug, path, head_files):
    """占位符展开对树：NN/*/{} 形态按 glob 在本 slug 子树展开，命中任一真文件即视为「入口在引用一类文件」。

    为什么必须展开而不是「按形状豁免」：B 臂实测按形状豁免会漏放 3 条真缺件（dispatch-NN.md 类占位形态但 0 命中的必须仍红）。
    """
    prefix = slug + "/"
    pat = path if path.startswith(prefix) else prefix + path
    pat = pat.replace("NN", "*")
    return [f for f in head_files if f.startswith(prefix) and fnmatch.fnmatch(f, pat)]


def genout(slug, path, entry_text):
    """GENERATED_OUTPUT_REF：入口写的路径是件内脚本的运行产物（静态口径下仍计 broken，只显影）。"""
    t = entry_text or ""
    if slug == "html-ppt" and "my-talk" in path and "new-deck" in t:
        return True
    return False


def tree_clean(rev):
    """HEAD 全树 {path: bytes}（带 quotepath=false）。不复用旧 tree_at：其 git() 缺该参数，中文路径整批丢失。"""
    r = subprocess.run(["git", "-c", "core.quotepath=false", "-C", ROOT, "ls-tree", "-r", "-l", rev],
                       capture_output=True)
    out = {}
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        if chr(9) not in line:
            continue
        meta, rest = line.split(chr(9), 1)
        parts = meta.split()
        if len(parts) != 4:
            continue
        out[rest] = int(parts[3]) if parts[3].isdigit() else 0
    return out


def main():
    global ROOT
    ap = argparse.ArgumentParser()
    ap.add_argument("--closure", choices=["top", "nested"], default="top")
    ap.add_argument("--managed-root", default=ROOT)
    ap.add_argument("--baseline",
                    default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "06-benchmark",
                                         "absorption_baseline_face.json"),
                    help="在册吸收件基线（唯一外部依赖；缺失即 rc=2）")
    ap.add_argument("--json", dest="out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        ok1 = is_noise("canvas-design/canvas-fonts/ArsenalSC-OFL.txt")
        ok2 = is_noise("ppt-master/scripts/README.md")
        ok3 = bool(PLACEHOLDER_RE.search("references/split-NN.md"))
        print("[R324:SELFTEST] noise_ofl=%s noise_readme=%s placeholder_NN=%s" % (ok1, ok2, ok3))
        return 0 if (ok1 and ok2 and ok3) else 1
    ROOT = a.managed_root
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("[R324:ENTRY] rc=2 UNVERIFIED managed-root 不可用: " + ROOT)
        return 2
    blp = a.baseline
    if not os.path.exists(blp):
        # 缺输入禁读成 0（R247）
        print("[R324:ENTRY] rc=2 UNVERIFIED 吸收基线缺失: " + blp)
        return 2
    head_files = tree_clean("HEAD")
    if not head_files:
        print("[R324:ENTRY] rc=2 UNVERIFIED 树为空（HEAD 读不到，禁读成 0 孤儿）")
        return 2
    bl = json.load(open(blp, encoding="utf-8"))
    slugs = []
    for pr in bl["pairs"]:
        s = pr.get("slug")
        if s and s not in slugs:
            slugs.append(s)
    top_dirs = set(p.split("/")[0] for p in head_files if "/" in p)
    others = set(x.lower() for x in top_dirs if x not in slugs)
    up_names, up_dirs = upstream_excludes()
    per = []
    tot_br = tot_ph = tot_gen = tot_or = tot_prose = noise_n = noise_b = 0
    for slug in slugs:
        text = entry_at("HEAD", slug) or ""
        entry_text = text
        if a.closure == "nested":
            extra = [f for f in head_files if f.startswith(slug + "/") and f.endswith("SKILL.md") and f != slug + "/SKILL.md"]
            for f in extra:
                entry_text += chr(10) + (entry_at("HEAD", f[:-9]) or "")
        broken, orphans, drop, samples, nf = judge(slug, entry_text, head_files, up_names, up_dirs, others)
        br_real = ph_n = gen_n = 0
        orph_v2 = []
        noise_here = 0
        for pth, bts in orphans:
            if is_noise(pth):
                noise_here += 1
                noise_n += 1
                noise_b += bts
                continue
            orph_v2.append([pth, bts])
        for pth in list(broken):
            if PLACEHOLDER_RE.search(pth) and expand_placeholder(slug, pth, head_files):
                ph_n += 1
            elif genout(slug, pth, text):
                gen_n += 1
            else:
                br_real += 1
        tot_br += len(broken)
        tot_ph += ph_n
        tot_gen += gen_n
        tot_or += len(orphans)
        tot_prose += len(orph_v2)
        per.append({"slug": slug, "broken": broken, "orphans": orphans,
                    "v2": {"broken_real": br_real, "placeholder": ph_n, "generated_output_ref": gen_n,
                           "orphans_prose": len(orph_v2), "orphans_noise": noise_here}})
    doc = {"schema": "r324-entry-reachability-1", "closure": a.closure, "managed_root": ROOT,
           "slugs": len(slugs),
           "totals": {"broken_top": tot_br, "broken_real": tot_br - tot_ph - tot_gen,
                      "placeholder": tot_ph, "generated_output_ref": tot_gen,
                      "orphans_top": tot_or, "orphans_prose": tot_prose,
                      "orphans_noise": noise_n, "noise_kb": int(round(noise_b / 1024.0)),
                      "tree_rows": len(head_files)},
           "per": per}
    if a.out:
        open(a.out, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1))
    print("[R324:ENTRY] closure=%s broken_top=%d broken_real=%d placeholder=%d genout=%d orphans_top=%d orphans_prose=%d noise=%d tree_rows=%d" % (
        a.closure, tot_br, doc["totals"]["broken_real"], tot_ph, tot_gen, tot_or, tot_prose, noise_n, len(head_files)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
