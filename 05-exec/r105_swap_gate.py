# -*- coding: utf-8 -*-
r"""r105_swap_gate.py — 换装判定的第二把尺（描述面）+ X-29 三门槛逐件实测。

为什么再来一把尺：本轮 18 维名册尺判 `[ROSTER:BLIND] misc 36.7% > 30%` ⇒ 「功能缺口」这个
结论按 r60 既定口径上限只能到 UNVERIFIED（分类器盲区未清就不许宣称本地缺这些能力）。
r60 的同题材教训是「抽取器/分类器失明须第二抽取器复算」，故本件**不按 slug 词面**判近邻，
而按**描述语义面**判：拿对手件的 frontmatter description 与本地全量 description 比 token 重合。

三门槛（X-29，逐件都要过，缺任一即不换）：
  G1 可运行：SKILL.md 里声明的执行依赖在本机可用（二进制不在 PATH ⇒ 不装，守 R-ADMIT「先落二进制再落技能」）
  G2 可移植：纯文本件（无 .exe/.dll/.whl/.zip 等二进制 blob；无绝对路径写死到别人机器）
  G3 与本机项目组合有交集：描述域与用户项目名册（医/孝心联/门店/陪聊/焚诀）或本地既有能力域有实义重合
反向门槛 G4：**本地已有同语义件即不换**（描述面 token 重合 >= 4 判 REPEATED，防把同一能力装第二份，
  这正是本仓 r55 记过的「镜像不是免费午餐 / 第二真相源」族）。

退出码：0=出件成功；2=取数面不可达（对手正文取不到 ⇒ 不得凭 slug 猜结论）。
"""
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RAW = ROOT / "05-exec" / "r96_gh_raw.json"
TF = ROOT / "06-benchmark" / "twelve_face_r105_2026-10-04.json"
INDEX = Path(r"C:\Users\37533\Desktop\workspace\焚诀\skill\registry\unified-skills-index.json")
AUTH_TREE = r"D:\global_skills"      # 本地描述面的权威源根（一级 ls，禁递归数 junction）
OUT = ROOT / "06-benchmark" / "swap_gate_r105_2026-10-04.json"

# 本轮逐件过门槛的候选族（选取依据 = 与本机项目组合的先验交集面，非星标排名）
CANDIDATES = [
    ("addyosmani/agent-skills", "browser-testing-with-devtools"),
    ("addyosmani/agent-skills", "context-engineering"),
    ("addyosmani/agent-skills", "code-simplification"),
    ("addyosmani/agent-skills", "constraint-driven-development"),
    ("addyosmani/agent-skills", "idea-refine"),
    ("coreyhaines31/marketingskills", "copywriting"),
    ("coreyhaines31/marketingskills", "content-strategy"),
    ("mattpocock/skills", "diagnosing-bugs"),
    ("mattpocock/skills", "codebase-design"),
    ("vercel-labs/agent-skills", "composition-patterns"),
]
CUR_MAX = 60          # 与本轮 curated 口径一致：>60 件视为聚合/生成式清单，不进逐件判定
# 信噪分离阈：最高重合须高出「它与本地全量的中位重合」这么多，否则该候选的近邻是通用词造出来的假象。
# 取 5 的依据是本轮实测的反例区间 —— 假近邻（copywriting↔xlsx）分离度 = 10-8 = 2，
# 而真近邻对照组（本轮 browser-testing-with-devtools↔browser-cdp）分离度 = 5-0 = 5 ⇒ 5 为可分下界。
# ⚠️ 该阈由**本轮一次实测**标定，样本仅 10 件；下一轮须复核，不得当成长期常数引用（W-20 面自证口径）。
DISCRIMINATION_MARGIN = 5
BIN_RX = re.compile(r"\.(exe|dll|so|dylib|whl|zip|tar|gz|png|jpg|jpeg|gif|ico|woff2?|ttf|pdf)$", re.I)


def toks(s):
    s = (s or "").lower()
    stop = {"the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "use", "when",
            "this", "that", "with", "you", "your", "it", "is", "are", "be", "from", "by",
            "skill", "skills", "use ", "must", "this skill"}
    t = set(re.split(r"[^a-z0-9]+", s)) - {""}
    return t - stop



# r163：gh 解析（与第 64 门 gh_path_face / _lib.gh_cli 同源）。
#   本机 gh 命令名被三方争夺（官方 CLI / npm 第三方包 2.8.9 / 曾经的 0 字节空壳），
#   裸 subprocess.run(["gh", ...]) 在 PATH 序漂移时会静默跑到错实现上 => 取数面按绝对路径调。
def _gh_exe():
    try:
        import _lib
        g = _lib.gh_cli()
        if g:
            return g
    except Exception:
        pass
    import os as _os
    for c in (
        _os.path.join(_os.environ.get("ProgramFiles", r"C:\\Program Files"),
                      "GitHub CLI", "gh.exe"),
        _os.path.expanduser(r"~\\scoop\\shims\\gh.exe"),
    ):
        try:
            if _os.path.isfile(c) and _os.path.getsize(c) > 0:
                return c
        except OSError:
            pass
    return "gh"  # 兜底裸名（调用方若取到非零/异常须具名，不得折算 0）

def gh_api(path):
    try:
        p = subprocess.run([_gh_exe(), "api", path], capture_output=True, text=True, timeout=90)
    except Exception as e:
        return None, "exc:%s" % e
    if p.returncode != 0:
        return None, (p.stderr or "").strip()[:160]
    return p.stdout, None


def idf_table(local_desc):
    """按本地语料算 token 的 IDF：出现在越多件里 ⇒ 越不像「这条能力独有的词」 ⇒ 权重越低。

    为什么用 IDF 而不是继续扩停用词表（r105 一手）：本轮反例命中的共同词是
    `also/any/convert/existing/into/like/my/not/user/wants` —— 这些是**技能描述文体的套话**，
    不是英语停用词，逐条加黑名单永远加不完（且加过头会把真近邻也削掉）。
    套话的共同特征是「在很多件里都出现」，这正是 df/IDF 能自动量到的性质：df 高 ⇒ idf→0。
    本函数只吃本地描述面 ⇒ 权重由被测数据自报，不由我拍（memory: 期望须由被测对象自报）。
    """
    import math
    df = {}
    n = 0
    for d in local_desc.values():
        t = toks(d)
        if not t:
            continue
        n += 1
        for w in t:
            df[w] = df.get(w, 0) + 1
    if not n:
        return {}
    return {w: math.log(float(n) / c) for w, c in df.items()}


def idf_score(a_set, b_set, idf):
    """共有 token 的 IDF 之和；未登录词（只在对手侧出现）按 0 计，不得凭空给权重。"""
    return round(sum(idf.get(w, 0.0) for w in (a_set & b_set)), 3)


def _on_path(cmd):
    """命令是否在本机 PATH。探测失败（异常/rc≠0）一律判「不在」——G1 是门槛不是加分项。"""
    try:
        r = subprocess.run(["bash", "-lc", "command -v %s" % cmd],
                           capture_output=True, text=True, timeout=30)
    except Exception:
        return False
    return r.returncode == 0 and bool((r.stdout or "").strip())


def parse_fm(text):
    """取 frontmatter 的 description（三形态：单行 / 折叠 >/| / 引号续行）。"""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    fm = text[3:end] if end > 0 else text[3:1500]
    m = re.search(r"^description:\s*(.*)$", fm, re.M)
    if not m:
        return ""
    v = m.group(1).strip()
    if v in (">", "|", ">-", "|-", ">+", "|+"):
        lines = []
        for ln in fm[m.end():].splitlines():
            if re.match(r"^\S", ln):
                break
            lines.append(ln.strip())
        return " ".join(lines)
    return v.strip('"\'')


def main():
    if not (RAW.is_file() and TF.is_file() and INDEX.is_file()):
        print("[SWAP:UNVERIFIED] 取数面缺件: raw=%s tf=%s index=%s"
              % (RAW.is_file(), TF.is_file(), INDEX.is_file()))
        return 2
    raw = json.load(io.open(str(RAW), encoding="utf-8"))
    tf = json.load(io.open(str(TF), encoding="utf-8"))
    idx = json.load(io.open(str(INDEX), encoding="utf-8-sig"))

    # 本地描述面取数：**权威源磁盘 SKILL.md 前置**（实测 unified-skills-index.json 的 skills 项
    # 不带 description 键 ⇒ 拿注册表当描述面会得到一张空面，G4 反向门槛就此失效。
    # 第二路留注册表 description 作对照，两路各报 own 计数，不得互相顶替。）
    local_desc = {}
    try:
        names = sorted(os.listdir(AUTH_TREE))       # 铁律 1：skills 根是 junction，禁 os.walk 数它
    except OSError as e:
        print("[SWAP:UNVERIFIED] 权威源根取不到（%s）⇒ 本地描述面为空，不得判重合" % e)
        return 2
    for n in names:
        p = os.path.join(AUTH_TREE, n, "SKILL.md")
        if not os.path.isfile(p):
            continue
        try:
            t = io.open(p, encoding="utf-8-sig", errors="replace").read()
        except Exception:
            continue
        local_desc[n.lower()] = parse_fm(t)
    reg_desc = {}
    for sid, s in (idx.get("skills") or {}).items() if isinstance(idx.get("skills"), dict) else []:
        if isinstance(s, dict):
            reg_desc[str(sid).lower()] = s.get("description") or ""
    n_nodesc = sum(1 for v in local_desc.values() if not v.strip())
    n_regnodesc = sum(1 for v in reg_desc.values() if not v.strip())
    idf = idf_table(local_desc)
    if not idf:
        print("[SWAP:UNVERIFIED] IDF 表为空（本地描述面无可统计 token）⇒ G4 不可判")
        return 2
    # 语言不对称实测（r105）：本尺失效的**根因读数**，不是解释性散文 —— 两侧文本语言不匹配时，
    # 词面重合与 IDF 都会把「英文套话」当成语义信号。数值必须落进产物，下一轮才可比。
    cjk_n = sum(1 for v in local_desc.values() if re.search(r"[\u4e00-\u9fff]", v or ""))
    lang_asym = {"local_desc_n": len(local_desc), "local_desc_with_cjk": cjk_n,
                 "cjk_share": round(cjk_n / float(len(local_desc)), 4),
                 "opponent_desc_lang": "en"}
    if not local_desc or n_nodesc == len(local_desc):
        print("[SWAP:UNVERIFIED] 本地描述面全空（local_n=%d 全为无描述）⇒ G4 不具鉴别力" % len(local_desc))
        return 2

    curated = {}
    for repo, v in (raw.get("repos") or {}).items():
        paths = v.get("skill_md_paths") or []
        if paths and len(paths) <= CUR_MAX and not v.get("tree_truncated"):
            for pp in paths:
                curated.setdefault(os.path.basename(os.path.dirname(pp)).lower(), []).append((repo, pp))

    rows, blocked = [], []
    tree_cache = {}
    desc_cache = {}
    for repo, slug in CANDIDATES:
        hit = [x for x in curated.get(slug, []) if x[0] == repo]
        if not hit:
            blocked.append({"slug": slug, "repo": repo, "why": "不在本轮 curated 面（>60 件或树截断）"})
            continue
        _, path = hit[0]
        body, err = gh_api("repos/%s/contents/%s" % (repo, path))
        if body is None:
            blocked.append({"slug": slug, "repo": repo, "why": "正文取不到:%s" % err})
            continue
        try:
            text = json.loads(body).get("content", "")
            import base64
            text = base64.b64decode(text).decode("utf-8", "replace")
        except Exception as e:
            blocked.append({"slug": slug, "repo": repo, "why": "解码失败:%s" % e})
            continue
        desc = parse_fm(text)
        desc_cache[slug] = desc
        dt = toks(desc)
        # G1 可运行：正文声明的外部命令是否在本机 PATH（缺任一 ⇒ 不装，R-ADMIT「先落二进制再落技能」）
        cmds = sorted(set(re.findall(
            r"(?:^|\s)(npx|uvx|pip|pip3|npm|cargo|go|docker|ffmpeg|pandoc|soffice|libreoffice|ast-grep|rg|gh)\b",
            text, re.M)))
        missing = [c for c in cmds if not _on_path(c)]
        # G4 反向门槛：与本地描述面的语义重合。
        # ⚠️ r105 一手：裸 token 重合**无鉴别力** —— 实测把对手 `copywriting`（营销文案）与本地
        # `xlsx` 量到重合 10，只因双方描述都含 create/edit/data/document 这类通用词；
        # `constraint-driven-development` ↔ `local-realtime-translator` 重合 9 同为假重合。
        # 故 G4 不看「重合数」而看**信噪分离度**：对每个候选，取它与本地全量的重合分布，
        # 只有「最高分明显高出中位数」才算真近邻；否则本件对该候选不具鉴别力 ⇒ 判 UNVERIFIED，
        # 绝不把「量到一个大数」读成「本地已有」（R236 补注③：区间重叠即不可作判据，须改机制）。
        dt = toks(desc)
        scores = sorted(idf_score(dt, toks(ld), idf) for ld in local_desc.values())
        best, best_n = None, 0.0
        for lid, ldesc in local_desc.items():
            n = idf_score(dt, toks(ldesc), idf)
            if n > best_n:
                best, best_n = lid, n
        raw_overlap = len(dt & toks(local_desc[best])) if best else 0
        med = scores[len(scores) // 2] if scores else 0.0
        p95 = scores[int(len(scores) * 0.95)] if scores else 0.0
        sep = best_n - med
        # G2 可移植：同目录是否有二进制 blob（被审对象自己的 blob 面，不是我方磁盘快照）
        if repo not in tree_cache:
            body_t, err_t = gh_api("repos/%s/git/trees/HEAD?recursive=1" % repo)
            paths_all = []
            if body_t:
                try:
                    dt_doc = json.loads(body_t)
                    paths_all = [x.get("path", "") for x in dt_doc.get("tree", [])
                                 if x.get("type") == "blob"]
                except Exception:
                    paths_all = []
            tree_cache[repo] = paths_all if paths_all else None
        allblobs = tree_cache[repo]
        if allblobs is None:
            blocked.append({"slug": slug, "repo": repo, "why": "blob 面取不到 ⇒ G2 不可判（不得当作可移植）"})
            continue
        prefix = path.rsplit("/", 1)[0] + "/"
        bin_hits = [b for b in allblobs if b.startswith(prefix) and BIN_RX.search(b)]
        discriminating = sep >= DISCRIMINATION_MARGIN and best_n > p95
        # 判定统一在标定控制跑完后的第二趟出（阈由实测边界推得，不在这条语句里拍数字）
        rows.append({"slug": slug, "repo": repo, "desc_chars": len(desc),
                     "nearest_local": best, "idf_overlap": best_n,
                     "raw_shared_tokens": raw_overlap,
                     "local_median_idf": med, "local_p95_idf": p95,
                     "separation": round(sep, 3), "per_item_discriminating": discriminating,
                     "binary_in_dir": len(bin_hits), "declared_cmds": cmds,
                     "missing_cmds": missing,
                     "gates": {"G1_runnable": not missing,
                               "G2_portable": not bin_hits,
                               "G4_not_duplicated": None},
                     "verdict": "PENDING"})

    # --- 内置标定控制（r105 一手，W-47「判据必注反例」）-----------------------------
    # 语义上显然不相干的一对：对手 `copywriting`（营销文案）↔ 本地 `xlsx`（电子表格）。
    # 本轮实测裸 token 重合把它量到 10 分（create/edit/data/user/asks 这类通用词造的假近邻），
    # 于是任何「按重合数判 REPEATED」都是假结论。控制失败的后果不是放宽，而是**整条 G4 尺失效**：
    # 全部候选改判 UNVERIFIED，且不据此装/不装任何东西（fail-closed）。
    # 反例对内件的正文须来自本轮真取数（desc_cache），取不到 ⇒ 记「不可判」并同样判尺失效——
    # 不得因为「控制没跑成」就当作「控制通过了」。
    CALIB_NEGATIVES = [("copywriting", "xlsx"), ("content-strategy", "local-vram"),
                       ("constraint-driven-development", "wechat-automation")]
    # 正例锚：语义上**确属同域**的对照对（React 组合模式↔本地 React 最佳实践；
    # 代码简化↔本地 refactoring 技能）。判据必须有正例才谈得上鉴别力。
    CALIB_POSITIVES = [("composition-patterns", "react-best-practices"),
                       ("code-simplification", "refactoring")]
    calib_fail, neg_scores, pos_scores = [], [], []
    for opp_slug, local_slug in CALIB_NEGATIVES:
        od_raw = desc_cache.get(opp_slug)
        if od_raw is None or local_slug not in local_desc:
            calib_fail.append("%s↔%s 不可判(正文或本地件缺面)" % (opp_slug, local_slug))
            continue
        od, ld = toks(od_raw), toks(local_desc[local_slug])
        s = idf_score(od, ld, idf)
        neg_scores.append(s)
        if s >= 1.0:
            calib_fail.append("%s↔%s IDF=%s 共同词=%s" % (opp_slug, local_slug, s, sorted(od & ld)[:8]))
    for opp_slug, local_slug in CALIB_POSITIVES:
        od_raw = desc_cache.get(opp_slug)
        if od_raw is None or local_slug not in local_desc:
            calib_fail.append("正例锚 %s↔%s 不可判(缺面) ⇒ 无对照组即无鉴别力证据" % (opp_slug, local_slug))
            continue
        s = idf_score(toks(od_raw), toks(local_slug and local_desc[local_slug]), idf)
        pos_scores.append(s)
    # 边界值判据（R236 补注③）：应拒的最高分 与 应通过的最低分 若区间重叠 ⇒ 该阈值不可作判据，
    # 唯一正解是继续改机制（此处即宣布本尺失效），而不是调参硬凑。
    n_max = max(neg_scores) if neg_scores else None
    p_min = min(pos_scores) if pos_scores else None
    separable = (n_max is not None and p_min is not None and p_min > n_max)
    DUP_AT = None
    if separable:
        DUP_AT = round((n_max + p_min) / 2.0, 3)
    ruler_blind = bool(calib_fail) or not separable
    if ruler_blind:
        for r in rows:
            r["verdict_before_calib"] = r["verdict"]
            r["verdict"] = "UNVERIFIED"
            r["gates"]["G4_not_duplicated"] = None
            r["calib_blocked"] = True
    print("G4 标定控制: %s ｜ 反例最高=%s 正例最低=%s 可分=%s 判重阈=%s"
          % ("FAIL ⇒ 本尺无鉴别力，全部候选降为 UNVERIFIED" if ruler_blind else "PASS",
             n_max, p_min, separable, DUP_AT))
    for c in calib_fail:
        print("  反例/缺面: %s" % c)

    # 第二趟出判：阈 DUP_AT 由上面实测边界算出；尺失效时一律 UNVERIFIED，绝不带着假阈出结论。
    for r in rows:
        if ruler_blind or not r["per_item_discriminating"]:
            r["verdict"] = "UNVERIFIED"
            r["gates"]["G4_not_duplicated"] = None
            continue
        dup = r["idf_overlap"] >= DUP_AT
        r["gates"]["G4_not_duplicated"] = (not dup)
        if dup:
            r["verdict"] = "REPEATED"
        elif r["binary_in_dir"] or r["missing_cmds"] or not r["desc_chars"]:
            r["verdict"] = "BLOCKED"
        else:
            r["verdict"] = "SWAP"
    if ruler_blind:
        for r in rows:
            r["calib_blocked"] = True

    doc = {"schema": "swap-gate-r105-v2", "generated_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
           "face": {"local_desc_face": "权威源 %s 一级 SKILL.md 前置" % AUTH_TREE,
                    "local_desc_n": len(local_desc), "local_desc_empty_n": n_nodesc,
                    "registry_desc_n": len(reg_desc), "registry_desc_empty_n": n_regnodesc,
                    "curated_slugs": len(curated),
                    "candidates_n": len(CANDIDATES), "judged_n": len(rows), "blocked_n": len(blocked)},
           "ceiling": "本轮 18 维名册尺判 [ROSTER:BLIND] misc 36.7%>30% ⇒ 「本地缺这些功能」上限 UNVERIFIED；"
                      "本件只对逐件取到正文的候选出判，不对 179 条候选出全称结论",
           "rows": rows, "blocked": blocked,
           "calib": {"negatives": CALIB_NEGATIVES, "positives": CALIB_POSITIVES,
                     "blind": ruler_blind, "separable": separable,
                     "neg_max": n_max, "pos_min": p_min, "dup_threshold": DUP_AT,
                     "metric": "共有 token 的 IDF 之和（IDF 由本地描述面自报，不拍常数）",
                     "lang_asymmetry": lang_asym,
                     "failures": calib_fail,
                     "note": "控制不可判一律计入 failures（不得把「没跑成」读成「跑过了」）；"
                             "应拒最高分 >= 应通过最低分 ⇒ 区间重叠，按 R236 补注③ 判该阈值不可作判据"}}
    with io.open(str(OUT), "w", encoding="utf-8", newline="") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    for r in rows:
        print("%-30s verdict=%-11s nearest=%-26s tok=%-2s med=%-2s sep=%-3s bin=%s miss=%s"
              % (r["slug"], r["verdict"], r["nearest_local"], r["idf_overlap"],
                 r["local_median_idf"], r["separation"], r["binary_in_dir"], r["missing_cmds"]))
    for b in blocked:
        print("%-30s BLOCKED  %s" % (b["slug"], b["why"]))
    vc = {}
    for r in rows:
        vc[r["verdict"]] = vc.get(r["verdict"], 0) + 1
    print("\n判定 %d 件 / 阻塞 %d 件 ⇒ 结论分布 %s" % (len(rows), len(blocked), vc))
    print("换装 = %d 件（仅 SWAP 计数；UNVERIFIED 一律不计入「已核对无缺口」）"
          % vc.get("SWAP", 0))
    print("JSON -> %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
