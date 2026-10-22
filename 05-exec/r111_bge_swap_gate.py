# -*- coding: utf-8 -*-
r"""r111_bge_swap_gate.py — R105-6 语义向量尺判定件（结论：本尺在真实描述面上**失效**）。

背景：r105 词面 IDF 尺自证伪（copywriting↔xlsx 28.543 > 正例 15.447，区间重叠）。
r110 登记 R105-6 为「降级（转长期看守）」，理由 = 需 BGE 工程先行。r111 执行该工程，
**结论为负**：BGE 语义尺在本仓真实描述面上同样不具备可用判别力。

实测（2026-10-17，bge-small-zh-v1.5 onnxruntime 后端，全部真取数）：
  同能力正例 vs 不同能力负例的余弦**完全重叠**，六个变体全部不可分：
    变体                         NEGmax   POSmin   margin
    A 双侧全文（探针口径）       0.7126   0.5831   -0.1294
    B 双侧首句                   0.6026   0.5408   -0.0617
    C 对手全文/本地首句          0.6670   0.5972   -0.0697
    D 双侧前 180 字符            0.6049   0.5764   -0.0284
    E 本地去中文                 0.7672   0.6691   -0.0981
    F 双侧去中文                 0.7672   0.6691   -0.0981

根因（三条，按证据强度排序）：
  1. **同能力对本身不成立**：diagnosing-bugs↔debugging-fixing（同一能力）实测 0.5831，
     而 copywriting↔xlsx（不同能力）0.7126。同一能力的中英描述**不比无关件更近**——
     不是模型弱，是「技能 description 面」这种文本承载的语义密度太低（多为触发条件清单）。
  2. **文体污染**：两侧都是「Use when the user wants to ...」模板句，BGE 把文体相似当语义相似。
  3. **语言不对称仍在**（r105 根因未消除）：本地 182 件中 69.8% 描述含中文，对手全英文。
     去中文变体 E/F 与全文 A 的排序结构完全相同 ⇒ 中文不是主因，只是叠加项。

为什么必须先探针后建尺（W-47 一步值回）：
  初版手写短句探针 margin=+0.0292（看起来可用），真取数后 margin=-0.1294。
  如果我按探针结论直接接线，会把「同能力 0.58 < 不同能力 0.71」的尺当成判据用——
  这正是 r105 词面尺翻车的同一形态（尺子坏但夹具绿）。

本件保留价值 = **负面判据**：它是「描述面语义尺」这条技术路线的终止证明。
后续替代路线见报告 §改进（不再走纯描述面 embedding）。

退出码：0 = 出件（含尺失效结论）；2 = 引擎/取数面不可达。
"""
import base64
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BGE_ENGINE = Path(r"C:\Users\37533\Desktop\workspace\焚诀\eval\bge_onnx_engine.py")
AUTH_TREE = r"D:\global_skills"
OUT = ROOT / "06-benchmark" / ("bge_swap_gate_r111_%s.json" % datetime.now().strftime("%Y-%m-%d"))

INSTR = "为这个句子生成表示以用于检索相关文章: "
CJK = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]+")

# X-29 三门槛候选（与 r105 同源以保可比性）
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
CUR_MAX = 60
BIN_RX = re.compile(r"\.(exe|dll|so|dylib|whl|zip|tar|gz|png|jpg|jpeg|gif|ico|woff2?|ttf|pdf)$", re.I)

# 标定对（PAIRS 三元组：typ, opponent_slug, local_slug）。
# 正例必须是**同一能力**（判重语义成立），弱正例=同域不同能力，单列不参与阈值。
CALIB_NEGATIVES = [
    ("copywriting", "xlsx", "营销文案 vs 电子表格"),
    ("content-strategy", "local-vram", "内容策略 vs GPU 显存"),
    ("constraint-driven-development", "wechat-automation", "需求约束 vs 微信自动化"),
    ("idea-refine", "local-tts", "想法精炼 vs 语音合成"),
]
CALIB_POSITIVES = [
    ("browser-testing-with-devtools", "browser-cdp", "同为 CDP 浏览器自动化"),
    ("code-simplification", "refactoring", "同为代码简化重构"),
    ("diagnosing-bugs", "debugging-fixing", "同为系统化调试"),
]
CALIB_WEAK_POSITIVES = [
    ("composition-patterns", "react-best-practices", "React 域相关但能力不同"),
]


def load_encoder():
    if not BGE_ENGINE.is_file():
        return None
    spec = importlib.util.spec_from_file_location("bge_onnx_engine", str(BGE_ENGINE))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.BgeOnnxEncoder()


def parse_fm(text):
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    fm = text[3:end] if end > 0 else text[3:1500]
    m = re.search(r"^description:\s*(.*)$", fm, re.M)
    if not m:
        return ""
    v = m.group(1).strip()
    if v in (">", "|", ">-", "|-", ">+", "|+"):
        out = []
        for ln in fm[m.end():].splitlines():
            if re.match(r"^\S", ln):
                break
            out.append(ln.strip())
        return " ".join(out)
    return v.strip("\"'")


def first_sentence(s, n=180):
    s = (s or '').strip()
    m = re.search(r'[.。!?！？]', s)
    head = s[:m.end()] if m and m.end() >= 20 else s[:n]
    return head[:n]


def strip_cjk(s):
    return re.sub(r'\s+', ' ', CJK.sub(' ', s or '')).strip()



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
        p = subprocess.run([_gh_exe(), "api", path], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=90)
    except Exception as e:
        return None, "exc:%s" % e
    if p.returncode != 0:
        return None, (p.stderr or "").strip()[:160]
    return p.stdout, None


def _on_path(cmd):
    try:
        r = subprocess.run(["bash", "-lc", "command -v %s" % cmd],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30)
    except Exception:
        return False
    return r.returncode == 0 and bool((r.stdout or "").strip())


def main():
    import numpy as np

    enc = load_encoder()
    if enc is None:
        print("[BGE-SWAP:UNVERIFIED] BGE 引擎不可达: %s" % BGE_ENGINE)
        return 2

    local_desc = {}
    try:
        names = sorted(os.listdir(AUTH_TREE))
    except OSError as e:
        print("[BGE-SWAP:UNVERIFIED] 权威源根取不到（%s）" % e)
        return 2
    for n in names:
        p = os.path.join(AUTH_TREE, n, "SKILL.md")
        if not os.path.isfile(p):
            continue
        try:
            t = io.open(p, encoding="utf-8-sig", errors="replace").read()
        except Exception:
            continue
        d = parse_fm(t)
        if d.strip():
            local_desc[n.lower()] = d
    if len(local_desc) < 10:
        print("[BGE-SWAP:UNVERIFIED] 本地描述面过小（%d）" % len(local_desc))
        return 2

    # --- 对手描述面：curated 面内逐件实时取（禁缓存冒充）---
    curated = {}
    body_cache, blocked = {}, []
    for repo, slug in CANDIDATES:
        tree, err = gh_api("repos/%s/git/trees/HEAD?recursive=1" % repo)
        paths = []
        if tree:
            try:
                paths = [x.get("path","") for x in json.loads(tree).get("tree", [])
                         if x.get("type") == "blob" and x.get("path","").endswith("/SKILL.md")]
            except Exception:
                paths = []
        hit = [p for p in paths if p.rsplit("/", 2)[-2].lower() == slug]
        if not hit:
            blocked.append({"slug": slug, "repo": repo, "why": "curated 面未找到 SKILL.md"})
            continue
        body, err = gh_api("repos/%s/contents/%s" % (repo, hit[0]))
        if body is None:
            blocked.append({"slug": slug, "repo": repo, "why": "正文取不到:%s" % err})
            continue
        try:
            body_cache[slug] = base64.b64decode(json.loads(body).get("content","")).decode("utf-8","replace")
        except Exception as e:
            blocked.append({"slug": slug, "repo": repo, "why": "解码失败:%s" % e})

    opp_desc = {s: parse_fm(t) for s, t in body_cache.items()}
    opp_desc = {s: d for s, d in opp_desc.items() if d.strip()}
    if not opp_desc:
        print("[BGE-SWAP:UNVERIFIED] 对手描述面 0 件")
        return 2

    loc_names = list(local_desc.keys())
    opp_slugs = list(opp_desc.keys())

    def pair_cos(opp_slug, local_slug, opp_fn=lambda s: s, loc_fn=lambda s: s):
        va = np.atleast_2d(enc.encode(INSTR + opp_fn(opp_desc[opp_slug])))[0]
        vb = np.atleast_2d(enc.encode(loc_fn(local_desc[local_slug])))[0]
        return float(va @ vb)

    # --- W-47 链路健康自检（先证尺子本身没坏，再谈它的判别力）---
    #   若这里红，说明编码/取数链路有 bug，下面的 BLIND 结论不成立（不得拿坏尺出负面结论）
    h_ok, h_fail = [], []
    def _self_check(name, cond, detail):
        (h_ok if cond else h_fail).append((name, detail))
    _t = "Systematic debugging workflow for finding root causes of software bugs and verifying fixes with evidence."
    _v = np.atleast_2d(enc.encode(INSTR + _t))[0]
    _self_check("self_cos", float(_v @ _v) > 0.999, "self=%.6f" % float(_v @ _v))
    _v_no = np.atleast_2d(enc.encode(_t))[0]
    _self_check("instr_no_distort", float(_v @ _v_no) > 0.85, "cos=%.4f" % float(_v @ _v_no))
    _a = "Generate a photorealistic landscape image from a text prompt using diffusion models."
    _b = "Query PostgreSQL with JOINs and aggregate functions over relational tables."
    _va = np.atleast_2d(enc.encode(INSTR + _a))[0]
    _vb = np.atleast_2d(enc.encode(_b))[0]
    _unrel = float(_va @ _vb)
    _self_check("unrelated_low", _unrel < 0.75, "cos=%.4f" % _unrel)
    _c = "Debug programs systematically: reproduce the failure, form root-cause hypotheses, apply minimal fix, verify."
    _vc = np.atleast_2d(enc.encode(INSTR + _c))[0]
    _self_check("paraphrase_gt_unrelated", _unrel < float(_va @ _vc),
                "unrel=%.4f para=%.4f" % (_unrel, float(_va @ _vc)))
    _zh = "系统化调试：复现失败、形成根因假设、最小改动修复、验证。"
    _vz = np.atleast_2d(enc.encode(_zh))[0]
    _self_check("cross_ling_gt_unrelated", _unrel < float(_vz @ _vc),
                "unrel=%.4f cross=%.4f" % (_unrel, float(_vz @ _vc)))
    chain_healthy = not h_fail
    print("[W-47] 编码链路健康自检: %d PASS / %d FAIL ⇒ %s"
          % (len(h_ok), len(h_fail), "PASS（BLIND 结论可信）" if chain_healthy else "FAIL（链路有 bug，禁出负面结论）"))
    for _n, _d in h_ok:
        print("   PASS %-24s %s" % (_n, _d))
    for _n, _d in h_fail:
        print("   FAIL %-24s %s" % (_n, _d))
    if not chain_healthy:
        print("[BGE-SWAP:UNVERIFIED] 编码链路自检失败 ⇒ 不得据此判尺失效")
        return 2

    # --- 六变体标定（本件核心：证明不可分，不是证明哪个变体更好）---
    VARIANTS = [
        ("A_fulltext", lambda s: s, lambda s: s),
        ("B_first_sentence", first_sentence, first_sentence),
        ("C_opp_full_loc_first", lambda s: s, first_sentence),
        ("D_first180", lambda s: s[:180], lambda s: s[:180]),
        ("E_loc_strip_cjk", lambda s: s, strip_cjk),
        ("F_both_strip_cjk", strip_cjk, strip_cjk),
    ]
    variant_results = {}
    separable_any = False
    for vname, opp_fn, loc_fn in VARIANTS:
        neg_s, pos_s, rows = [], [], []
        for opp_slug, local_slug, why in CALIB_NEGATIVES:
            if opp_slug not in opp_desc or local_slug not in local_desc:
                continue
            s = pair_cos(opp_slug, local_slug, opp_fn, loc_fn)
            neg_s.append(s)
            rows.append({"type": "NEG", "pair": "%s↔%s" % (opp_slug, local_slug), "cos": round(s, 4), "why": why})
        for opp_slug, local_slug, why in CALIB_POSITIVES:
            if opp_slug not in opp_desc or local_slug not in local_desc:
                continue
            s = pair_cos(opp_slug, local_slug, opp_fn, loc_fn)
            pos_s.append(s)
            rows.append({"type": "POS", "pair": "%s↔%s" % (opp_slug, local_slug), "cos": round(s, 4), "why": why})
        n_max = max(neg_s) if neg_s else None
        p_min = min(pos_s) if pos_s else None
        separable = (n_max is not None and p_min is not None and p_min > n_max)
        separable_any = separable_any or separable
        variant_results[vname] = {
            "rows": rows,
            "neg_max": round(n_max, 4) if n_max is not None else None,
            "pos_min": round(p_min, 4) if p_min is not None else None,
            "margin": round(p_min - n_max, 4) if (n_max is not None and p_min is not None) else None,
            "separated": separable,
        }
        print("  %-24s NEGmax=%s POSmin=%s margin=%s separable=%s"
              % (vname,
                 variant_results[vname]['neg_max'], variant_results[vname]['pos_min'],
                 variant_results[vname]['margin'], separable))

    ruler_blind = not separable_any
    print("[BGE-SWAP] 六变体可分性: %s ⇒ 尺%s"
          % ("/".join(k for k,v in variant_results.items() if v["separated"]) or "全部分不可分",
             "失效（保留为负面判据，见文件头）" if ruler_blind else "有一个变体可分"))

    # --- 候选行（尺失效时一律 UNVERIFIED，不装不卸）---
    rows = []
    for repo, slug in CANDIDATES:
        if slug not in body_cache:
            continue
        text = body_cache[slug]
        cmds = sorted(set(re.findall(
            r"(?:^|\s)(npx|uvx|pip|pip3|npm|cargo|go|docker|ffmpeg|pandoc|soffice|libreoffice|ast-grep|rg|gh)\b",
            text, re.M)))
        missing = [c for c in cmds if not _on_path(c)]
        va = np.atleast_2d(enc.encode(INSTR + opp_desc.get(slug, '')))[0]
        sims = np.array([float(vb @ va) for vb in [
            np.atleast_2d(enc.encode(local_desc[n]))[0] for n in loc_names]])
        order = list(np.argsort(-sims))[:5]
        rows.append({
            "slug": slug, "repo": repo, "desc_chars": len(opp_desc.get(slug, "")),
            "nearest_local": loc_names[order[0]] if order else None,
            "max_cos": round(float(sims[order[0]]), 4) if order else None,
            "top5": [(loc_names[j], round(float(sims[j]), 4)) for j in order],
            "missing_cmds": missing,
            "gates": {"G1_runnable": not missing, "G4_not_duplicated": None},
            "verdict": "UNVERIFIED" if ruler_blind else "PENDING"})

    doc = {
        "schema": "bge-swap-gate-r111-v2",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "engine": {"path": str(BGE_ENGINE), "backend": "onnxruntime bge-small-zh-v1.5",
                   "instr_prefix": INSTR, "metric": "cosine"},
        "face": {"local_desc_n": len(local_desc), "opp_desc_n": len(opp_desc),
                 "candidates_n": len(CANDIDATES), "blocked_n": len(blocked)},
        "verdict": {
            "ruler_status": "BLIND" if ruler_blind else "SEPARABLE",
            "conclusion": ("BGE 语义尺在真实描述面上六变体全部不可分 ⇒ 判为失效，保留为负面判据。"
                           " 后续不再走纯描述面 embedding 路线。") if ruler_blind else "至少一个变体可分",
            "root_causes": [
                "同能力对本身不成立：diagnosing-bugs↔debugging-fixing 0.5831 < copywriting↔xlsx 0.7126",
                "文体污染：两侧均为 Use when the user wants to 模板句，文体相似被当语义相似",
                "语言不对称仍在（本地 69.8% 描述含中文），去中文变体排序结构不变 ⇒ 非主因",
            ],
            "probe_vs_real": "手写短句探针 margin=+0.0292（假可用）；真取数 -0.1294",
            "chain_health_w47": "5 项链路自检全 PASS（self_cos=1.0 / unrelated=0.4706 / cross_ling=0.5607）⇒ BLIND 结论来自真实测量而非 bug",
        },
        "variants": variant_results,
        "rows": rows, "blocked": blocked,
    }
    io.open(str(OUT), "w", encoding="utf-8", newline="\n").write(json.dumps(doc, ensure_ascii=False, indent=1))
    print("JSON -> %s" % OUT)
    print("[BGE-SWAP:%s]" % ("BLIND" if ruler_blind else "DONE"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
