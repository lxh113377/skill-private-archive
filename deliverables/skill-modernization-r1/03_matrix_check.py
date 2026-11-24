# -*- coding: utf-8 -*-
"""t3 五维矩阵复算 + 负控判据（需求3）。

独立读 data/matrix.csv 与 03_evaluation_matrix.md 的 §6 汇总表：
1) 逐行校验 weight*score == weighted_contribution、每分带证据句柄/取值命令；
2) 按 object_id 聚合 weighted_contribution 复算 T，与汇总表逐行比对，打印差异断言；
3) 负控：把某候选 fc 分数改 0 -> T 必须变化；注入一处汇总表错值 -> 必须被抓；
4) captain 硬口径自证：unknown=66 / recorded=84 / feedback_cap 全 0 / 排除件不进 CSV。
"""
import os
import csv
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "matrix.csv")
MD = os.path.join(HERE, "03_evaluation_matrix.md")
WEIGHTS = {"fc": 6, "eff": 4, "compat": 4, "docs": 3, "community": 3}
DIMS = ["fc", "eff", "compat", "docs", "community"]


def load_csv():
    with open(CSV, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def parse_md_summary(text):
    seg = text.split("<!-- MATRIX_SUMMARY_BEGIN -->")[1].split("<!-- MATRIX_SUMMARY_END -->")[0]
    out = {}
    for ln in seg.splitlines():
        ln = ln.strip()
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if len(cells) != 8:
            continue
        if cells[0] in ("object_id", "") or cells[0].startswith("---"):
            continue
        out[cells[0]] = {"class": cells[1],
                         "scores": {d: int(cells[2 + i]) for i, d in enumerate(DIMS)},
                         "total": int(cells[7])}
    return out


def recompute(rows):
    # 独立复算：不信任生成器的 total，只按 CSV 的逐行 weight x score 重新求和。
    totals = {}
    scores = {}
    errs = []
    for r in rows:
        oid = r["object_id"]
        d = r["dimension"]
        s = int(r["score"])
        w = int(r["weight"])
        c = int(r["weighted_contribution"])
        if w != WEIGHTS[d]:
            errs.append("weight_mismatch " + oid + " " + d)
        if c != w * s:
            errs.append("contribution_mismatch " + oid + " " + d)
        if not r["evidence_handle"].strip():
            errs.append("evidence_handle_empty " + oid + " " + d)
        if not r["measurement_command"].strip():
            errs.append("command_empty " + oid + " " + d)
        totals[oid] = totals.get(oid, 0) + c
        scores.setdefault(oid, {})[d] = s
    return totals, scores, errs


def compare(rows, md_map):
    totals, scores, errs = recompute(rows)
    for oid, m in md_map.items():
        if oid not in totals:
            errs.append("md_only " + oid)
            continue
        if m["total"] != totals[oid]:
            errs.append("total_diff " + oid)
        for d in DIMS:
            if m["scores"][d] != scores[oid][d]:
                errs.append("score_diff " + oid + " " + d)
    for oid in totals:
        if oid not in md_map:
            errs.append("csv_only " + oid)
    return errs, totals, scores


def main():
    rows = load_csv()
    text = open(MD, "r", encoding="utf-8").read()
    md_map = parse_md_summary(text)
    errs, totals, scores = compare(rows, md_map)
    print("[CHECK] csv_rows=" + str(len(rows)) + " objects=" + str(len(totals))
          + " md_rows=" + str(len(md_map)))
    print("[DIFF_ASSERT] " + str(len(errs)))
    if errs:
        for e in errs[:20]:
            print("  DIFF " + e)
        return 1
    cur = {}
    for r in rows:
        if r["object_type"] == "current" and r["dimension"] == "fc":
            cur[r["object_id"]] = (r["defect_face"], r["feedback_weight_cap"])
    unk = sum(1 for v in cur.values() if v[0] == "unknown(not_scored)")
    rec = sum(1 for v in cur.values() if v[0] == "recorded(84-cohort)")
    cap_bad = sum(1 for r in rows if r["feedback_weight_cap"] != "0")
    excl = sum(1 for r in rows if "directed_lead" in r["object_id"]
               or "family_pad" in r["object_id"])
    print("[CALIBER] unknown=" + str(unk) + " recorded=" + str(rec)
          + " feedback_cap_nonzero=" + str(cap_bad) + " excluded_in_csv=" + str(excl))
    if (unk, rec, cap_bad, excl) != (66, 84, 0, 0):
        print("[CALIBER:RED] 硬口径不符")
        return 1
    placeholder_bad = sum(1 for r in rows if ("<JQ_REPOS>" in r["measurement_command"]
                                              or "<JQ_TREE>" in r["measurement_command"]
                                              or "<JQ_LICENSE>" in r["measurement_command"]))
    unavail = [r for r in rows if r["score_status"] == "UNAVAILABLE"]
    unavail_bad = sum(1 for r in unavail if int(r["score"]) != 0
                      or int(r["weighted_contribution"]) != 0)
    print("[CMD] placeholder_commands=" + str(placeholder_bad))
    print("[SENTINEL] unavailable_rows=" + str(len(unavail)) + " nonzero=" + str(unavail_bad))
    if placeholder_bad or not unavail or unavail_bad:
        print("[SENTINEL:RED] 占位符命令或未计分哨兵不合格")
        return 1
    cand = None
    for oid, s in scores.items():
        if oid.startswith("cand:") and s["fc"] > 0:
            cand = oid
            break
    if cand is None:
        print("[NEGCTRL:GREEN] 无 fc>0 候选，判据失效")
        return 1
    mut = []
    for r in rows:
        rr = dict(r)
        if rr["object_id"] == cand and rr["dimension"] == "fc":
            rr["score"] = "0"
            rr["weighted_contribution"] = "0"
        mut.append(rr)
    t2, _, e2 = recompute(mut)
    original = totals[cand]
    mutated = t2[cand]
    if mutated == original or e2:
        print("[NEGCTRL:GREEN] 改 0 后总分不变或复算报错，判据恒绿 FAIL")
        return 1
    print("[NEGCTRL:RED] 篡改被检出 " + cand + " T=" + str(original)
          + " -> fc=0 => T=" + str(mutated))
    bad = dict(md_map)
    k = next(iter(bad))
    bad[k] = {"class": bad[k]["class"], "scores": dict(bad[k]["scores"]),
              "total": bad[k]["total"] + 1}
    errs_bad, _, _ = compare(rows, bad)
    if not errs_bad:
        print("[NEGCTRL:GREEN] 汇总表注入错值未被抓，判据恒绿 FAIL")
        return 1
    print("[NEGCTRL:RED] 汇总表错值注入被检出 diffs=" + str(len(errs_bad)))
    print("[CHECK] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
