# -*- coding: utf-8 -*-
r"""r61_semantic_coverage.py — 第 18 维「第三把尺」：语义面覆盖实测（r61 纵深）.

存在理由（r60 一手 + r61 复算）：r60 两把尺都在**词面**上量 —— 第一把尺按 slug 名（misc 盲区
36.4% 被判 UNVERIFIED），第二把尺按 description 的**共享词数**。共享词数不是语义：`ast-grep` 与
`x-longform-post` 能因两个巧合共用词而得 tok=2，`visual-qa` 与 `gstack` 明明同能力却可能零共词。
⇒ r60 那句「37 条真差距候选」的下限其实建立在词面尺上，**从未用生产路由器自己的语义面复算过**。
本件把那一步补上：拿本机生产 BGE 索引（与 unified_router L1 同一份向量）给 r60 的 187 条对手独有件
逐条打分，并与词面档做交叉表 —— 两把尺不一致的条数才是本轮的真读数。

口径纪律：
  * **不设拍脑袋阈值**（R236 补注③）：先用语料自身标定 —— 每条语料的「与最近邻他条的 cosine」
    经验分布即"同一棵技能树里两个不同能力之间的典型距离"，取 p50/p75 两档做**双口径敏感性反算**
    （两档结论同向才敢下句子）。
  * **量不到不得折算成零**（feedback: unavailable is not zero）：BGE 后端不可用 ⇒ rc=2 并
    backend=unavailable，禁止把"没测到"写成"全都不覆盖"或"全都覆盖"。
  * 分母与语料人口**由盘面枚举现取**，索引行数 != skills 条数即判红并印两侧读数。

取值：`python 05-exec/r61_semantic_coverage.py --json 06-benchmark/semantic_coverage_r61_2026-09-30.json`
退出码：0 = 分区守恒且后端可用；1 = 守恒被破坏；2 = UNVERIFIED（后端不可用 / 空面 / 语料人口不自洽）。
"""

import argparse
import io
import json
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GAP_ART = os.path.join(ROOT, "06-benchmark", "capability_gap_r60_2026-09-30.json")
FJ_EVAL = r"C:\Users\37533\Desktop\workspace\焚诀\eval"
SKILLS_JSON = "bge_fullbody_skills.json"
EMB_NPY = "bge_fullbody_embeddings.npy"


def percentile(sorted_vals, q):
    if not sorted_vals:
        return None
    idx = min(len(sorted_vals) - 1, int(round(q * (len(sorted_vals) - 1))))
    return float(sorted_vals[idx])


def load_backend():
    """Return (encode_fn, backend_name, err). Never fake a scorer."""
    if not os.path.isfile(os.path.join(FJ_EVAL, SKILLS_JSON)) or not os.path.isfile(
            os.path.join(FJ_EVAL, EMB_NPY)):
        return None, "missing-index", "焚诀 eval 索引件不在位（%s / %s）" % (SKILLS_JSON, EMB_NPY)
    try:
        import numpy as np
    except Exception as e:                                          # noqa: BLE001
        return None, "missing-numpy", "%s: %s" % (type(e).__name__, e)
    sys.path.insert(0, FJ_EVAL)
    try:
        import bge_layer
    except Exception as e:                                          # noqa: BLE001
        return None, "import-fail", "%s: %s" % (type(e).__name__, e)
    try:
        bge_layer._load_bge()
        model = getattr(bge_layer, "_bge_model", None)
        if model is None:
            return None, "bge-unavailable", "_load_bge() 后 _bge_model 仍为 None（生产侧走 TF-IDF 降级）"
        emb = np.load(os.path.join(FJ_EVAL, EMB_NPY))

        def encode(texts):
            vec = np.asarray(model.encode(texts, normalize_embeddings=True), dtype="float32")
            return vec

        return (encode, emb), "bge(%s)" % getattr(bge_layer, "_bge_backend", "?"), None
    except Exception as e:                                          # noqa: BLE001
        return None, "encode-fail", "%s: %s" % (type(e).__name__, e)


def loadable_corpus(encode):
    """Build the *loadable* population (authority root + marketplace root, unique names) and
    embed it, so the router-index face (169) and the face the session can actually load (428)
    can be measured with the same ruler. Returns (names, matrix, skipped) or None."""
    import numpy as np
    texts, names = [], []
    for root in (r"D:\global_skills", r"C:\Users\37533\.workbuddy\skills-marketplace\skills"):
        if not os.path.isdir(root):
            continue
        for d in sorted(os.listdir(root)):
            p = os.path.join(root, d, "SKILL.md")
            if d.startswith(".") or d in names or not os.path.isfile(p):
                continue
            try:
                raw = io.open(p, encoding="utf-8-sig", errors="replace").read(6000)
            except OSError:
                continue
            m = re.search(r"^---\s*\n(.*?)\n---", raw, re.S)
            body = m.group(1) if m else raw
            dm = re.search(r"^description:\s*(.*)$", body, re.M)
            desc = (dm.group(1) if dm else body)[:600]
            if len(desc.strip()) < 20:
                continue
            names.append(d)
            texts.append(("%s. %s" % (d, re.sub(r"\s+", " ", desc)))[:900])
    if len(names) < 2:
        return None
    return names, np.asarray(encode(texts), dtype="float32"), len(names)


def score_face(items, names, matrix, encode, texts):
    """Tier each opponent item against one corpus face using that face's own calibration band."""
    import numpy as np
    band = []
    for i in range(len(names)):
        sims = matrix @ matrix[i]
        sims[i] = -1.0
        band.append(float(np.max(sims)))
    bs = sorted(band)
    p50, p75 = percentile(bs, 0.50), percentile(bs, 0.75)
    vecs = encode(texts)
    out = {}
    for it, v in zip(items, vecs):
        sims = matrix @ v
        order = [int(j) for j in np.argsort(sims)[::-1][:3]]
        best = float(sims[order[0]])
        tier = ("covered_strong" if best >= p75 else
                "covered_weak" if best >= p50 else "no_neighbour")
        out[it["slug"]] = {"score": round(best, 4), "tier": tier, "top": [names[j] for j in order]}
    return out, {"band_n": len(bs), "p50": round(p50, 4), "p75": round(p75, 4),
                 "min": round(min(bs), 4), "max": round(max(bs), 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    problems = []
    if not os.path.isfile(GAP_ART):
        sys.stderr.write("[SEM:UNVERIFIED] 输入面缺失：%s\n" % GAP_ART)
        return 2
    gap = json.loads(io.open(GAP_ART, encoding="utf-8-sig").read())
    lex_items = gap.get("items") or []
    if not lex_items:
        sys.stderr.write("[SEM:UNVERIFIED] r60 词面件 items 为空，零面不得判过\n")
        return 2

    loaded, backend, err = load_backend()
    if loaded is None:
        doc = {"schema": "semantic-coverage-r61-v1", "readonly": True,
               "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "backend": backend, "backend_error": err, "items": [], "tiers": {},
               "problems": ["backend=%s (%s)" % (backend, err)],
               "note": "量不到不得折算成零：本件不下任何覆盖结论（feedback: unavailable is not zero）"}
        print("[SEM:UNVERIFIED] 语义后端不可用：%s (%s) ⇒ 本轮不产覆盖结论" % (backend, err))
        if args.out:
            _atomic_write(args.out, json.dumps(doc, ensure_ascii=False, indent=1))
        return 2
    encode, emb = loaded

    # ---- 面 A：生产路由器自己的语料（unified_router L1 用的那份向量）
    skills = json.loads(io.open(os.path.join(FJ_EVAL, SKILLS_JSON), encoding="utf-8-sig").read())
    names_a = [s.get("name") or "?" for s in skills]
    if len(names_a) != emb.shape[0]:
        problems.append("语料人口不自洽：skills=%d 但索引行数=%d" % (len(names_a), emb.shape[0]))
        sys.stderr.write("[SEM:FAIL] %s\n" % problems[-1])
        return 1
    # ---- 面 B：会话可加载的全人口（权威源 + 市场缓存根）
    lc = loadable_corpus(encode)
    if lc is None:
        problems.append("可加载面人口 <2 条 ⇒ 面 B 不可测，不得只报面 A 就宣称覆盖")
        names_b, emb_b = None, None
    else:
        names_b, emb_b, _ = lc

    todo = lex_items[: args.limit] if args.limit else lex_items
    texts = [("%s. %s" % (it["slug"], it.get("description") or ""))[:900] for it in todo]

    face_a, cal_a = score_face(todo, names_a, emb, encode, texts)
    face_b, cal_b = (score_face(todo, names_b, emb_b, encode, texts)
                     if names_b else ({}, {}))

    items = []
    for it in todo:
        lex_tok = it["nearest_local"][0]["shared_tokens"] if it.get("nearest_local") else 0
        a, b = face_a[it["slug"]], face_b.get(it["slug"])
        items.append({"slug": it["slug"], "repo": it["repo"], "lexical_tokens": lex_tok,
                      "router_tier": a["tier"], "router_score": a["score"], "router_top": a["top"],
                      "loadable_tier": b["tier"] if b else "unmeasured",
                      "loadable_score": b["score"] if b else None,
                      "loadable_top": b["top"] if b else []})

    def tally(key):
        out = {}
        for x in items:
            out[x[key]] = out.get(x[key], 0) + 1
        return out

    tiers_a, tiers_b = tally("router_tier"), tally("loadable_tier")
    if sum(tiers_a.values()) != len(items) or sum(tiers_b.values()) != len(items):
        problems.append("tiers 之和 != items 长度（两面各自守恒失败）%s %s %d"
                        % (tiers_a, tiers_b, len(items)))

    # ---- 交叉表：词面档（<=2 = r60 判定的"真差距"）× 两个语义档
    crosstab = {}
    for x in items:
        key = ("lexical_gap" if x["lexical_tokens"] <= 2 else "lexical_close")
        crosstab.setdefault(key, {})
        for f in ("router_tier", "loadable_tier"):
            crosstab[key].setdefault(f, {})
            crosstab[key][f][x[f]] = crosstab[key][f].get(x[f], 0) + 1
    gap_items = [x for x in items if x["lexical_tokens"] <= 2]
    # 路由器盲区 = 词面判差距 ∧ 面 A 说没有邻居 ∧ 面 B 说其实有（能力在盘上，只是不在路由索引里）
    router_blind = [x["slug"] for x in gap_items
                    if x["router_tier"] == "no_neighbour" and x["loadable_tier"] != "no_neighbour"]
    confirmed_gap = [x["slug"] for x in gap_items
                     if x["router_tier"] == "no_neighbour" and x["loadable_tier"] == "no_neighbour"]
    lex_overstated = [x["slug"] for x in gap_items if x["loadable_tier"] != "no_neighbour"]
    # 三桶守恒：词面差距件 = 两面无邻居 + 只缺路由索引(盲区) + 两把尺双双否证
    double_refuted = [x["slug"] for x in gap_items
                      if x["loadable_tier"] != "no_neighbour" and x["router_tier"] != "no_neighbour"]
    if len(confirmed_gap) + len(router_blind) + len(double_refuted) != len(gap_items):
        problems.append("词面差距三桶不守恒：%d+%d+%d != %d"
                        % (len(confirmed_gap), len(router_blind), len(double_refuted), len(gap_items)))

    doc = {
        "schema": "semantic-coverage-r61-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "readonly": True,
        "dimension": 18,
        "lens": 3,
        "counting_unit": "r60 词面件 items 逐条（唯一 slug 名）",
        "claims_face": "语义面 = 生产 unified_router L1 所用同一份 BGE 向量（焚诀 eval/%s，行已 L2 归一）"
                       "；档位由**语料自身最近邻 cosine 分布**的 p50/p75 双档划定，非外部拍的阈值"
                       % EMB_NPY,
        "backend": backend,
        "corpus": {"face_A_router_index": {"names": len(names_a), "rows": int(emb.shape[0]),
                                           "dim": int(emb.shape[1])},
                   "face_B_loadable": {"names": len(names_b) if names_b else 0,
                                       "rows": int(emb_b.shape[0]) if emb_b is not None else 0}},
        "calibration": {"face_A_router_index": cal_a, "face_B_loadable": cal_b,
                        "meaning": "各面自身的『一条语料与最近邻他条的 cosine』经验分布；"
                                   "p50/p75 双档做敏感性反算，两档同向才下句子（R236 补注③）"},
        "tiers": {"face_A_router_index": tiers_a, "face_B_loadable": tiers_b},
        "crosstab": crosstab,
        "totals": {"items": len(items), "lexical_gap_items": len(gap_items),
                   "gap_confirmed_both_faces": len(confirmed_gap),
                   "gap_only_in_router_index": len(router_blind),
                   "gap_double_refuted": len(double_refuted),
                   "gap_overturned_by_loadable_face": len(lex_overstated)},
        "router_blind_slugs": router_blind,
        "confirmed_gap_slugs": confirmed_gap,
        "gap_double_refuted_slugs": double_refuted,
        "items": sorted(items, key=lambda x: -(x["loadable_score"] or 0)),
        "problems": problems,
        "note": "面 A = 生产路由索引实际人口（169 件，只覆盖权威源）；面 B = 会话可加载全人口。"
                "两档之差 = 能力在盘上但对路由器不可见 ⇒ r60 的『换装 0 件』结论在两档下同向才成立。",
    }

    print("第三把尺（语义面）｜ 后端=%s ｜ 面A(路由索引) %d 条 %sx%d ｜ 面B(可加载) %d 条"
          % (backend, len(names_a), emb.shape[0], emb.shape[1], len(names_b) if names_b else 0))
    print("  标定带 A: p50=%.3f p75=%.3f ｜ B: p50=%.3f p75=%.3f"
          % (cal_a.get("p50") or 0, cal_a.get("p75") or 0,
             cal_b.get("p50") or 0, cal_b.get("p75") or 0))
    print("  档分布 A: %s\n  档分布 B: %s" % (tiers_a, tiers_b))
    print("  交叉表: %s" % crosstab)
    print("  词面判差距 %d 条 ⇒ 两面都无邻居 %d ｜ 只在路由索引里无邻居(=盲区) %d ｜ 被可加载面否证 %d"
          % (len(gap_items), len(confirmed_gap), len(router_blind), len(lex_overstated)))
    if problems:
        print("[SEM:FAIL] " + " ; ".join(problems))
        rc = 1
    else:
        print("[SEM:PASS] 分区守恒成立，两把尺交叉已出数")
        rc = 0
    if args.out:
        _atomic_write(args.out, json.dumps(doc, ensure_ascii=False, indent=1))
        print("证据件: %s" % args.out)
    return rc


def _atomic_write(path, text):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


if __name__ == "__main__":
    sys.exit(main())
