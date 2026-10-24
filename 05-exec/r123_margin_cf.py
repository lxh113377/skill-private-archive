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
import argparse, io, os, sys, json, time   # r216: argparse/time 为新增 CLI 与输出件命名而补（原文件无 time）
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


def main(argv=None):
    # r216 修两处机械缺陷（只改可复跑性；判定逻辑与三道控制组一字未动）：
    #   ① 输入面原写死 _temp/r123_cf_cases.json —— _temp 被 gitignore 且并行会话按扩展名清过 212 件
    #      （R189-2），全仓亦无该件生成器 ⇒ 本沙箱当年只能靠手里那份手工件跑一次（W-46 死句柄，同 R211-7）。
    #   ② 输出原写死 margin_cf_r123_2026-10-20.json（tracked）⇒ 重跑即原地覆盖历史证据（同 r211 我在 c16 上撞的）。
    # ⚠️ 修完这两处它仍**不能自动跑**：cases 里的 candidate / wrong_domain 是**人工提出的候选语料**
    #    （与 r119_corpus_gate 的 --candidates 同源）。本仓不替老大编造候选 ⇒ 只补 CLI，不补数据。
    ap = argparse.ArgumentParser(description="语料改造安全边际反事实沙箱（输入 = 人工候选件）")
    ap.add_argument("--cases", required=True,
                    help="JSON: {slug: {query, candidate, wrong_domain}}；候选语料须人工提出")
    ap.add_argument("--json", dest="out", default=None,
                    help="输出件（缺省 = 06-benchmark/margin_cf_r123_<日期>.json）")
    ap.add_argument("--force", action="store_true", help="显式允许覆盖已存在的输出件")
    args = ap.parse_args(argv)
    if not os.path.isfile(args.cases):
        print("[MARGINCF:UNVERIFIED] 候选件不存在: %s ⇒ 禁按「无收益」记（R247）；候选语料须人工提出"
              % args.cases)
        return 2
    out_path = args.out or os.path.join(
        ROOT, "06-benchmark", "margin_cf_r123_%s.json" % time.strftime("%Y-%m-%d"))
    if os.path.exists(out_path) and not args.force:
        print("[MARGINCF:REFUSE] 输出件已存在，拒绝原地覆盖历史证据：%s（重算请另指 --json 或 --force）"
              % out_path)
        return 2
    cfg = json.load(io.open(args.cases, encoding="utf-8"))
    if not isinstance(cfg, dict) or not cfg:
        print("[MARGINCF:UNVERIFIED] 候选件为空或形态不对 ⇒ 零输入不得记绿（R247）")
        return 2
    out = []
    for slug, c in cfg.items():
        r = probe(slug, c["query"], c["candidate"], c["wrong_domain"])
        out.append(r)
        print("%-22s base=%-7s cand=%-7s delta=%-8s adv_hit=%-5s neg_hit=%-5s => %s" % (
            slug, r["baseline"]["margin"], r["candidate"]["margin"], r["margin_delta"],
            r["candidate_adversarial"]["hit"], r["negative_control"]["hit"], r["verdict"]))
    tmp = out_path + ".tmp"
    json.dump({"schema": "margin-cf-r123-v2", "cases_file": os.path.relpath(args.cases, ROOT),
               "results": out},
              io.open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, out_path)          # 原子写：禁把证据件写成半截（r112 cache_guard 同族）
    print("JSON -> %s" % os.path.relpath(out_path, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())