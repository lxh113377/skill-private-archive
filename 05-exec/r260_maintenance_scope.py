# -*- coding: utf-8 -*-
"""r260_maintenance_scope.py -- same 3.1 rule read across four denominators in one pass.

Why this exists (R260-9 / X-24 family): three batches of evidence each reported a "3.1 violation
count" and all were right -- r225 production top-5 face = 2; filtered top-5 = 0 residual;
pre-trim full pool = 82; directed-search face = 12. If downstream quotes one number without
naming its denominator, it will collide with another round reading and look like ledger drift.
This tool prints all four denominators together, so the citation format becomes fixed:
"N cases (face=..., slot denominator=...)".

Caliber discipline:
  * the rule body is imported from the judge under test (r114.maintenance_trim) -- never
    re-implemented here (two copies of one threshold always drift; R263/R280 family).
  * read-only: no matrix artifact is written.
  * an unavailable denominator is named and demotes the run to UNVERIFIED, never to 0 (R247).
"""
import io
import json
import os
import sys
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")
sys.path.insert(0, HERE)
import r114_replacement_scan as R

TRIM = R.maintenance_trim
EV = R.EVAL_DATE


def load(name):
    p = os.path.join(BENCH, name)
    if not os.path.isfile(p):
        return None, "MISSING " + name
    try:
        return json.load(io.open(p, encoding="utf-8-sig")), None
    except Exception as e:
        return None, "UNPARSABLE %s (%r)" % (name, e)


def main():
    print("[MT-SCOPE] eval_date=%s threshold_date=%s (12 months = %d days, read from the judge)"
          % (EV, (EV - timedelta(days=R.TWELVE_MONTHS_DAYS)), R.TWELVE_MONTHS_DAYS))
    bad = 0

    # A / B：同一判据分别打到未过滤的生产矩阵与过滤后的新矩阵 top-5
    for label, name in (("A top-5 production (r225)", "replacement_matrix_r225.json"),
                        ("B top-5 after filter", "r260_matrix_trimmed.json")):
        doc, err = load(name)
        if doc is None:
            print("  %-28s => %s (UNVERIFIED, not 0)" % (label, err))
            bad += 1
            continue
        slots, viol, hit = 0, 0, set()
        for r in (doc.get("rows") or []):
            for c in (r.get("candidates") or []):
                slots += 1
                if TRIM(c, EV):
                    viol += 1
                    hit.add(r.get("slug"))
        print("  %-28s => %d cases / slots=%d / rows=%d %s"
              % (label, viol, slots, len(hit), sorted(hit)[:3]))

    # C：剔前全池（含从未进 top-5 的候选）—— 用矩阵件自己的逐件审计字段
    doc, err = load("r260_matrix_trimmed.json")
    if doc is None:
        print("  C pre-trim pool => %s" % err)
        bad += 1
    else:
        n = sum(len(r.get("maintenance_trimmed") or []) for r in doc.get("rows") or [])
        aff = [r.get("slug") for r in doc.get("rows") or [] if (r.get("maintenance_trim_n") or 0) > 0]
        mf = doc.get("maintenance_face") or {}
        print("  %-28s => %d cases / rows=%d (face archived=%s stale=%s trimmed_total=%s)"
              % ("C pre-trim pool (all candidates)", n, len(aff),
                 mf.get("archived_total"), mf.get("stale_total"), mf.get("trimmed_total")))
        if n != int(mf.get("trimmed_total") or -1):
            print("     [MT-SCOPE:MISMATCH] 逐件之和 %d != 面级 %s（两处必有一处失真）" % (n, mf.get("trimmed_total")))
            bad += 1

    # D：定向检索面（owner 的 A 件），并与其件内自报对账
    doc, err = load("r260_directed_search.json")
    if doc is None:
        print("  D directed face => %s" % err)
        bad += 1
    else:
        # 字段名以件内实测为准（首版我按 items/slug/results 猜 ⇒ slots=0，而 0 又一路走到 PASS：
        # 那是**本腿自己没牙**，不是社区没问题。真名 = items[].skill + items[].top3。
        slots = viol = 0
        hit = set()
        for it in (doc.get("items") or []):
            for c in (it.get("top3") or []):
                slots += 1
                if TRIM(c, EV):
                    viol += 1
                    hit.add(it.get("skill"))
        if slots == 0:
            # 零输入不得判过（R247）：宁可具名 UNVERIFIED，也不许把「我没解析到候选」记成 0 例。
            print("  D directed-search face => slots=0 ⇒ 件形态变了或字段名猜错（UNVERIFIED，不记 0）")
            bad += 1
        pct = (100.0 * viol / slots) if slots else None
        print("  %-28s => %d cases / slots=%d / skills=%d%s"
              % ("D directed-search face", viol, slots, len(hit),
                 "" if pct is None else " (%.1f%%)" % pct))
        # 与 owner 自报对账：sweep 在 r260_trim_violations.json 里（不在定向件），两处都要读。
        tdoc, _ = load("r260_trim_violations.json")
        own = (tdoc or {}).get("directed_search_face_sweep") or {}
        if own:
            print("     vs owner-reported: %s" % json.dumps(own, ensure_ascii=False)[:300])
    print("rule source: %s (zero re-implementation here)" % os.path.basename(R.__file__))
    if bad:
        print("[MT-SCOPE:UNVERIFIED] %d denominators unavailable => not recorded as 0 (R247)" % bad)
        return 2
    print("[MT-SCOPE:PASS] four denominators read in one pass; cite as N cases (face=..., slots=...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
