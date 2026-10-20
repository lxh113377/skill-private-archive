# -*- coding: utf-8 -*-
r"""r123_margin_cf.py — 语料改造的安全边际反事实沙箱（R122-2 修复版 + R122-3 对抗腿）。

## 存在理由
r122 用「只 encode description 单行」的沙箱做加固决策，实测**系统性偏差约 2 倍**
（单行 0.1219 vs 全文 800 字 0.0596），导致把「无益改动」判成 HARDENED 并落地，
事后靠对抗场景 + 完整语料复测才发现应回滚（受管根 f957117 → r123 回滚 3760ce0）。

## 本件两道修正
① **语料口径对齐 build_indexes.py**：候选 description 换回 SKILL.md 原文后取前 800 字符
   再 encode（原沙箱直接 encode 单行，与生产语料不同源 ⇒ 偏差约 2 倍）。
② **新增对抗腿**：把该件 domain 临时改成错误域，量「域错分后是否仍 hit」——
   margin 高不等于抗域扰动（R122-3：稳健性的正确度量是对抗场景）。

## 判定口径（三态，禁二值）
  HARDENED_AND_ROBUST : margin 提升 **且** 对抗场景仍 hit ⇒ 才建议落地
  MARGIN_ONLY         : margin 提升但对抗场景翻车 ⇒ 禁落地（提的正是脆弱面）
  NO_GAIN             : margin 未提升 ⇒ 不落地（r122 三件即此态，被旧沙箱误判）

## 双向对照
  负控（无关正文）必须能把该件弄丢 ⇒ 证语料行确有影响力（非空转）。
"""
import io, os, sys, json
sys.path.insert(0, r'C:\Users\37533\Desktop\workspace\焚诀\eval')
os.environ['FENJUE_ROUTE_TRACE'] = '0'
import numpy as np, bge_onnx_engine
enc = bge_onnx_engine.BgeOnnxEncoder()
EVAL = r'C:\Users\37533\Desktop\workspace\焚诀\eval'
base = np.asarray(np.load(os.path.join(EVAL, 'bge_fullbody_embeddings.npy'), mmap_mode='r'), dtype='float32')
skills = json.load(io.open(os.path.join(EVAL, 'bge_fullbody_skills.json'), encoding='utf-8'))
names = [s['name'] if isinstance(s, dict) else s for s in skills]
idx = {n: i for i, n in enumerate(names)}
import bge_layer, unified_router as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def install(arr, mods=None):
    sk = skills
    if mods:
        sk = [dict(s) for s in skills]
        for s in sk:
            if s.get("name") in mods:
                s["domain"] = mods[s["name"]]
    bge_layer._bge_emb = arr; bge_layer._bge_skills = sk; bge_layer._bge_model = enc
    bge_layer._BGE_PROBE_DONE = True; bge_layer._bge_backend = "onnx-sim"
    bge_layer._QEMB_CACHE.clear()


def measure(slug, q):
    res = R.route(q, enable_memory=False)
    cs = res.get("candidates") or []
    e = next((c["score"] for c in cs if c["name"] == slug), None)
    t2 = cs[1]["score"] if len(cs) > 1 else None
    return {"top1": cs[0]["name"] if cs else None,
            "exp_score": e,
            "margin": round(e - t2, 4) if (e is not None and t2 is not None) else None,
            "hit": (cs[0]["name"] == slug) if cs else False}


def full_text(slug, desc_line):
    """R122-2 修：候选 description 换回原文，取前 800 字符（与 build_indexes 同源）。"""
    p = os.path.join(r"D:/global_skills", slug, "SKILL.md")
    lines = io.open(p, encoding="utf-8", errors="replace").read().split(chr(10))
    for i, l in enumerate(lines):
        if l.startswith("description:"):
            lines[i] = desc_line
            break
    return chr(10).join(lines)[:800]


def probe(slug, q, cand_desc, wrong_domain):
    b = measure(slug, q)
    arr = np.array(base, dtype="float32", copy=True)
    v = np.asarray(enc.encode([full_text(slug, cand_desc)]), dtype="float32")[0]
    arr[idx[slug]] = v; install(arr)
    c = measure(slug, q)
    # 对抗腿：候选 + 域错分
    install(arr, {slug: wrong_domain})
    ca = measure(slug, q)
    # 负控：无关正文
    neg = io.open(os.path.join(ROOT, "05-exec", "r117_route_miss_attr.py"), encoding="utf-8").read()[:800]
    v2 = np.asarray(enc.encode([full_text(slug, neg)]), dtype="float32")[0]
    a2 = np.array(base, dtype="float32", copy=True); a2[idx[slug]] = v2
    install(a2)
    n = measure(slug, q)
    install(base)
    delta = (c["margin"] - b["margin"]) if (c["margin"] is not None and b["margin"] is not None) else None
    if delta is not None and delta > 0 and ca["hit"]:
        verdict = "HARDENED_AND_ROBUST"
    elif delta is not None and delta > 0:
        verdict = "MARGIN_ONLY"
    else:
        verdict = "NO_GAIN"
    return {"slug": slug, "query": q, "baseline": b, "candidate": c,
            "candidate_adversarial": ca, "negative_control": n,
            "margin_delta": delta, "verdict": verdict}


def main():
    cfg = json.load(io.open(os.path.join(ROOT, "_temp", "r123_cf_cases.json"), encoding="utf-8"))
    out = []
    for slug, c in cfg.items():
        r = probe(slug, c["query"], c["candidate"], c["wrong_domain"])
        out.append(r)
        print("%-22s base=%-7s cand=%-7s delta=%-8s adv_hit=%-5s neg_hit=%-5s => %s" % (
            slug, r["baseline"]["margin"], r["candidate"]["margin"], r["margin_delta"],
            r["candidate_adversarial"]["hit"], r["negative_control"]["hit"], r["verdict"]))
    json.dump({"schema": "margin-cf-r123-v1", "results": out},
              io.open(os.path.join(ROOT, "06-benchmark", "margin_cf_r123_2026-10-20.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("JSON -> 06-benchmark/margin_cf_r123_2026-10-20.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())