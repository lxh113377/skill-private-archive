# -*- coding: utf-8 -*-
"""需求 2 的字面 vs 语义合规面（r291）。

为什么要单独建（一手，r291 我自己差点犯的错）：需求 2 要求「针对每一件筛出 3-5 个匹配度最高、
社区活跃、维护良好的替代」。矩阵每行都有 candidates_n，实测 191/191 落在 3..5 ⇒ 字面 100%。
但生成器 05-exec/r114_replacement_scan.py L1210-1212 的取材是：先取 rel=="skill" 的前 5，
不足 5 时用 rel=="family" 的仓**补位**。于是「候选数 >=3」里相当一部分是族级补位件，不是该技能的
对应物。单看 r114 报告那句「182/182 件 >=3 个候选」会得出错误结论（本轮我差点就这么说）——
数据没骗人，是报表口径会误导。本面把两种口径分开报，并具名到件。

口径（全部现读，不硬编码）：
  LITERAL  = candidates_n 落在 3..5 的件数（字面满足需求 2 的条数要求）
  SEMANTIC = 其中 rel=="skill" 的条数 >=3 的件数（真有 3 个以上对应物）
  PAD_ONLY = 候选 5/5 全是 family 补位（开源侧无对应物，verdict 应为 NO_OS_CANDIDATE）

一致性自证：PAD_ONLY 的件集合必须等于 verdict==NO_OS_CANDIDATE 的件集合 —— 不等就说明补位与
判档脱钩（分档没看补位），那是真缺陷，本面判红而不是闭眼报数。
"""
import argparse, io, json, os, sys

DEF = "06-benchmark/replacement_matrix_shadowstrict.json"


def measure(path):
    d = json.load(io.open(path, encoding="utf-8"))
    rows = d.get("rows") or []
    lit = sem = 0
    pad_rows, pad_dist, rel_pad = [], {}, {}
    for r in rows:
        cs = r.get("candidates") or []
        n_rel = sum(1 for c in cs if isinstance(c, dict) and c.get("rel") == "skill")
        n = int(r.get("candidates_n") or len(cs))
        if 3 <= n <= 5:
            lit += 1
        if n_rel >= 3:
            sem += 1
        if cs and n_rel == 0:
            pad_rows.append(r.get("slug"))
        p = len(cs) - n_rel
        if p:
            pad_dist[str(p)] = pad_dist.get(str(p), 0) + 1
            for c in cs:
                if isinstance(c, dict) and c.get("rel") != "skill":
                    rel_pad[c.get("rel")] = rel_pad.get(c.get("rel"), 0) + 1
    verdict_pad = sorted(r.get("slug") for r in rows if r.get("verdict") == "NO_OS_CANDIDATE")
    n = len(rows) or 1
    return {"schema": "req2-compliance-v1", "source": path, "rows": len(rows),
            "literal_3_5": lit, "literal_pct": round(100.0 * lit / n, 2),
            "semantic_rel_ge3": sem, "semantic_pct": round(100.0 * sem / n, 2),
            "pad_only_n": len(pad_rows), "pad_only_slugs": sorted(pad_rows),
            "pad_count_histogram": pad_dist, "pad_rel_histogram": rel_pad,
            "verdict_no_os_n": len(verdict_pad),
            "consistency_pad_eq_verdict": sorted(pad_rows) == verdict_pad,
            "reading_rule": "candidates_n 满足条数不等于真有 3 个对应物；rel=family 的补位件是族级邻居，不能当替代方案引用（引用前先看 rel 与 skill_relevant_n）"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", default=DEF)
    ap.add_argument("--json", dest="js")
    a = ap.parse_args()
    if not os.path.isfile(a.matrix):
        print("[REQ2:UNVERIFIED] 矩阵件不存在: %s" % a.matrix)
        return 2
    doc = measure(a.matrix)
    if a.js:
        dd = os.path.dirname(a.js)
        if dd:
            os.makedirs(dd, exist_ok=True)
        io.open(a.js, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1))
    print("[REQ2:COMPLIANCE] rows=%d literal=%d(%.2f%%) semantic=%d(%.2f%%) pad_only=%d consistency=%s"
          % (doc["rows"], doc["literal_3_5"], doc["literal_pct"], doc["semantic_rel_ge3"],
             doc["semantic_pct"], doc["pad_only_n"], doc["consistency_pad_eq_verdict"]))
    if not doc["consistency_pad_eq_verdict"]:
        print("[REQ2:FAIL] pad_only 集合 != verdict==NO_OS_CANDIDATE 集合 => 分档与补位脱钩")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
