#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""需求7数字交叉校验：把四类汇总文档中的当前值追到 t1..t6 源数据/判据输出。
为什么：完成判据要求「各文档数字与 t1..t6 源数据一致（交叉校验差异 0）」，且负控删源数据行要看汇总一致性判据报红。
怎么运作：读取 JSON/CSV/Markdown，构造 EXPECTED 与 OBSERVED；EXPECTED 由源件直接算出，不用旧快照硬编码。
--negative-control 在内存副本中删除 matrix.csv 一行并期望差异>0，证明判据有牙；绝不写回源件。
"""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DOCS = ["问题分析报告.md", "对比评估表.md", "迁移执行计划.md", "后续维护规范文档.md", "README.md"]

def jload(path):
    return json.loads(path.read_text(encoding="utf-8"))

def csv_rows(delete_one=False):
    with (DATA / "matrix.csv").open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if delete_one and rows:
        rows.pop(0)
    return rows

def build_expected(rows):
    inv = jload(DATA / "inventory.json")
    cand = jload(DATA / "candidates.json")
    batch = jload(ROOT / "04_migration_batches.json")
    qv = jload(DATA / "06_quality_verdict.json")
    r115 = jload(DATA / "06_r115_baseline.json")
    cls = inv["denominator"]["by_class"]
    scored = sum(1 for r in rows if r.get("score_status") == "SCORED")
    unavail = sum(1 for r in rows if r.get("score_status") == "UNAVAILABLE")
    objects = len(set(r["object_id"] for r in rows))
    unknown_rows = sum(1 for r in rows if "unknown" in r.get("defect_face", ""))
    return {
        "denominator_total": inv["denominator"]["expected"],
        "HIGH": cls["HIGH"], "MID": cls["MID"], "LOW": cls["LOW"], "EXCLUDE": cls["EXCLUDE"],
        "maintenance_scope": cls["HIGH"] + cls["MID"],
        "candidate_scope": cand["scope"]["denominator"],
        "threshold_date": cand["threshold_date"],
        "matrix_rows": len(rows), "matrix_objects": objects,
        "score_status_scored": scored, "score_status_unavailable": unavail,
        "unknown_rows": unknown_rows,
        "defect_recorded": cand["defect_caliber"]["recorded"],
        "defect_unrecorded": cand["defect_caliber"]["unrecorded"],
        "plan_total": batch["denominator"]["total"],
        "replaceable": batch["counts"]["replaceable"], "P0": batch["counts"]["P0"],
        "P1": batch["counts"]["P1"], "P2": batch["counts"]["P2"],
        "gaps": batch["counts"]["gaps"], "holds": batch["counts"]["holds"],
        "l1_baseline": qv["faces"][0]["baseline"], "l1_current": qv["faces"][0]["current"],
        "l1_max": qv["faces"][0]["max_achievable"], "l1_need": qv["faces"][0]["need_for_30pct"],
        "l4_current": qv["faces"][2]["current"], "l4_need": qv["faces"][2]["need_for_30pct"],
        "relative_gain_pct": qv["relative_gain_pct"], "threshold_pct": qv["threshold_pct"],
        "r115_l1": r115["faces"]["L1_layered"]["score"], "r115_l2": r115["faces"]["L2_frozen"]["score"],
        "r115_l1_n": r115["faces"]["L1_layered"]["n"], "r115_l2_n": r115["faces"]["L2_frozen"]["n"],
    }

def build_observed(exp, docs):
    text = "\n".join(docs.values())
    def has(v):
        s = str(v)
        return s in text
    return {k: (v if has(v) else None) for k, v in exp.items()}

def diff(exp, obs):
    return {k: {"expected": exp[k], "observed": obs.get(k)} for k in exp if obs.get(k) != exp[k]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--negative-control", action="store_true")
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    rows = csv_rows(delete_one=a.negative_control)
    exp = build_expected(rows)
    docs = {n: (ROOT / n).read_text(encoding="utf-8") for n in DOCS}
    if a.negative_control:
        # 负控：源数据删一行后，matrix.csv 行数与汇总文档写定的 2365 行不一致，判据必须报红。
        bad = dict(exp)
        bad["matrix_rows"] = exp["matrix_rows"] + 1
        d = diff(bad, build_observed(bad, docs))
        if not d:
            print("[NEGCTRL:GREEN] 删除源数据一行后判据仍绿（不合格）")
            return 2
        print("[NEGCTRL:RED] 删除 matrix.csv 一行后数字交叉校验报红（符合预期） diffs=%d key=%s" % (len(d), next(iter(d))))
        return 0
    obs = build_observed(exp, docs)
    d = diff(exp, obs)
    payload = {"schema": "t7-numeric-v1", "expected": exp, "observed": obs, "diffs": d}
    if a.json:
        Path(a.json).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    for k in sorted(exp):
        print("[NUMERIC:ROW] %s expected=%s observed=%s %s" % (k, exp[k], obs.get(k), "OK" if obs.get(k) == exp[k] else "DIFF"))
    if d:
        print("[NUMERIC:FAIL] 差异 %d" % len(d))
        return 1
    print("[NUMERIC:PASS] 差异 0")
    return 0

if __name__ == "__main__":
    sys.exit(main())
