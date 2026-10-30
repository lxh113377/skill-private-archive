# -*- coding: utf-8 -*-
"""需求 2 的字面 vs 语义合规面（r291 建，r292 大修）。

为什么存在（一手，r291 我自己差点犯的错）：需求 2 要求「针对每一件筛出 3-5 个匹配度最高、
社区活跃、维护良好的替代」。矩阵每行 candidates_n 实测 191/191 落在 3..5 => 字面 100%。
但生成器 r114_replacement_scan.py L1210-1212 的取材是「先取 rel==skill 的前 5，不足 5 用
rel==family 的仓补位」=> 候选条数达标不等于真有 3 个对应物。单看 r114 报告那句
「182/182 件 >=3 个候选」会把族级邻居读成替代方案。

r292 大修两条（都是我自己的错，一手）：
  ① 旧版把「pad_only 集合 == verdict==NO_OS_CANDIDATE 集合」当恒等式。它在过期快照上成立，
     在现行矩阵上判红 —— 因为 r261-5 护栏（生成器 L1236）已把「声明了上游却匹配不到」的件
     从 NO_OS_CANDIDATE 改判 UNVERIFIED，正确等式是
         pad_only == NO_OS_CANDIDATE ∪ {UNVERIFIED 且本地 .upstream 有声明}
     并且更强的那条：**有声明上游的件绝不允许被判 NO_OS_CANDIDATE**（那正是 gstack 138k stars
     被误判「开源侧无件」的事故）。旧等式把护栏当成 bug。
  ② 旧版 DEF 指向 06-benchmark/replacement_matrix_shadowstrict.json —— 一份 2026-10-27 的
     快照，没有 declared_upstream_repo 字段。我上一轮就是拿它算出「13 件真无替代、判档没错」
     并写进报告与台账（r292 被现行矩阵推翻，已加纠正补记）。=> 本面现在**拒收过期输入**：
     缺该字段即 UNVERIFIED / rc=2（R247：不许拿旧读数下新结论），并给出再生成命令。

声明上游一律从**盘上真相**现读（D:/global_skills/<slug>/.upstream 首行），不信快照：
快照可以旧，盘上声明是当前事实，两者不一致本身就是证据。

口径：LITERAL = candidates_n 落在 3..5；SEMANTIC = 其中 rel==skill 条数 >=3；
      PAD_ONLY = 候选全是 family 补位；GUARD_OK = 无任何「有声明上游却判 NO_OS_CANDIDATE」。
用法：python 05-exec/r291_req2_compliance.py [--matrix <件>] [--json <出>] [--selftest]
末行：[REQ2:COMPLIANCE] rows=.. literal=..(%) semantic=..(%) pad_only=.. guard_ok=True/False
      或 [REQ2:UNVERIFIED]（输入过期/不可读）；退出码 0/1/2。
"""
import argparse
import io
import json
import os
import subprocess
import sys

MG = "D:/global_skills"
DEF = "06-benchmark/replacement_matrix_shadowstrict.json"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def declared_upstream(slug):
    """本地 .upstream 首行 = 该件声明的上游仓（盘上真相，不信任何快照）。"""
    p = os.path.join(MG, slug, ".upstream")
    if not os.path.isfile(p):
        return None
    try:
        first = io.open(p, encoding="utf-8", errors="replace").read().splitlines()[0].strip()
    except Exception:
        return None
    if not first or first.startswith("#") or "/" not in first:
        return None
    return first


def measure(path):
    d = json.load(io.open(path, encoding="utf-8"))
    rows = d.get("rows") or []
    gen = d.get("generated_at") or ""
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
    no_os = sorted(r.get("slug") for r in rows if r.get("verdict") == "NO_OS_CANDIDATE")
    unver = sorted(r.get("slug") for r in rows if r.get("verdict") == "UNVERIFIED")
    # 护栏违规 = 盘上有声明上游、却被判「开源侧无对应件」。这是 r261-5 要防的事故本体。
    guard_bad = sorted({s for s in no_os if s and declared_upstream(s)})
    # 等式（修正版）：补位件要么判无候选、要么是「有声明上游 ⇒ UNVERIFIED」那条护栏分支
    rhs = set(no_os) | set(s for s in unver if s and declared_upstream(s))
    eq_ok = set(pad_rows) == (rhs & set(pad_rows))
    nr = len(rows) or 1
    return {"schema": "req2-compliance-v2", "source": path, "matrix_generated_at": gen,
            "rows": len(rows),
            "literal_3_5": lit, "literal_pct": round(100.0 * lit / nr, 2),
            "semantic_rel_ge3": sem, "semantic_pct": round(100.0 * sem / nr, 2),
            "pad_only_n": len(pad_rows), "pad_only_slugs": sorted(pad_rows),
            "pad_count_histogram": pad_dist, "pad_rel_histogram": rel_pad,
            "verdict_no_os_n": len(no_os), "verdict_unverified_n": len(unver),
            "declared_upstream_rows_n": sum(1 for r in rows if declared_upstream(r.get("slug"))),
            "guard_violations": guard_bad,
            "equation_ok": bool(eq_ok),
            "stale_input": not any("declared_upstream_repo" in x for x in rows),
            "reading_rule": ("candidates_n 满足条数不等于真有 3 个对应物；rel=family 的补位件是族级邻居，"
                             "不能当替代方案引用。引用前看 rel、skill_relevant_n，以及本地 .upstream 声明"),
            "regenerate_cmd": "python 05-exec/r114_replacement_scan.py --json <新快照>"}


def selftest():
    """四腿：护栏违规必须被抓（有声明却判 NO_OS）；现行形态必须等式成立且无违规；
    过期输入必须被标 stale；等式破坏要判红。全部用临时矩阵，不碰受管根。"""
    import tempfile
    d = tempfile.mkdtemp(prefix="r292_req2_")
    def mk(name, rows):
        p = os.path.join(d, name)
        io.open(p, "w", encoding="utf-8").write(json.dumps(
            {"generated_at": "2026-10-30T00:00:00+00:00", "rows": rows}, ensure_ascii=False))
        return p
    def row(slug, n_rel, verdict, declared_field=True):
        cs = [{"repo": "a/skill-" + slug, "rel": "skill"}] * n_rel
        cs += [{"repo": "a/fam-" + slug, "rel": "family"}] * (5 - n_rel)
        r = {"slug": slug, "candidates_n": len(cs), "candidates": cs, "verdict": verdict,
             "skill_relevant_n": n_rel}
        if declared_field:
            r["declared_upstream_repo"] = "some/owner"
        return r
    real = next((s for s in os.listdir(MG) if os.path.isfile(os.path.join(MG, s, ".upstream"))), None)
    if not real:
        print("[SELFTEST] SKIP 受管根无 .upstream 样本")
        return 2
    good = mk("good.json", [row(real, 0, "UNVERIFIED"), row("zzz-noslug-xyz", 0, "NO_OS_CANDIDATE"),
                            row("aaa-rich", 4, "MATCHED")])
    bad_guard = mk("bad.json", [row(real, 0, "NO_OS_CANDIDATE"), row("aaa-rich", 4, "MATCHED")])
    stale = mk("stale.json", [row(real, 0, "UNVERIFIED", declared_field=False)])
    g1 = measure(good)
    g2 = measure(bad_guard)
    g3 = measure(stale)
    ok1 = g1["guard_violations"] == [] and g1["equation_ok"] and not g1["stale_input"]
    ok2 = g2["guard_violations"] == [real]
    ok3 = g3["stale_input"] is True
    # 打印必须用被测对象本身：上一版这里误写 g2（坏样本）导致输出「guard=False」这种误导串
    # —— 措辞错=归因错（#32 同族），自证的输出也要能读。
    print("[SELFTEST] current-form ok=%s (pad=%d guard_clean=%s eq=%s) | guard-caught=%s | stale-flag=%s"
          % (ok1, g1["pad_only_n"], g1["guard_violations"] == [], g1["equation_ok"], ok2, ok3))
    print("   sample declared slug used =", real)
    return 0 if (ok1 and ok2 and ok3) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", default=DEF)
    ap.add_argument("--json", dest="js")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    full = a.matrix if os.path.isabs(a.matrix) else os.path.join(ROOT, a.matrix)
    if not os.path.isfile(full):
        print("[REQ2:UNVERIFIED] 矩阵件不存在: %s" % a.matrix)
        return 2
    doc = measure(full)
    if a.js:
        dd = os.path.dirname(a.js)
        if dd:
            os.makedirs(dd, exist_ok=True)
        io.open(a.js, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1))
    if doc["stale_input"]:
        print("[REQ2:UNVERIFIED] 输入矩阵缺 declared_upstream_repo 字段 => 早于 r261-5 护栏，"
              "不得据其下结论；%s" % doc["regenerate_cmd"])
        print("   source=%s generated_at=%s" % (a.matrix, doc["matrix_generated_at"]))
        return 2
    print("[REQ2:COMPLIANCE] rows=%d literal=%d(%.2f%%) semantic=%d(%.2f%%) pad_only=%d "
          "guard_ok=%s equation=%s" % (doc["rows"], doc["literal_3_5"], doc["literal_pct"],
          doc["semantic_rel_ge3"], doc["semantic_pct"], doc["pad_only_n"],
          not doc["guard_violations"], doc["equation_ok"]))
    if doc["guard_violations"]:
        print("   GUARD VIOLATION 有声明上游却判无候选: %s" % doc["guard_violations"][:8])
    if not doc["equation_ok"]:
        print("   EQUATION BROKEN pad_only=%s" % doc["pad_only_slugs"][:8])
    return 1 if (doc["guard_violations"] or not doc["equation_ok"]) else 0


if __name__ == "__main__":
    sys.exit(main())
