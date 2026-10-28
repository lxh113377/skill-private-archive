# -*- coding: utf-8 -*-
"""r260_maintenance_trim_fixtures.py -- 3.1 maintenance-trim judge proof (resident gate).
 
Why a separate gate instead of only editing r114: this repo keeps hitting W-46 (a judge written
but never wired to any execution path). Once 3.1 stops being prose and becomes code, nothing must
be able to silently delete that code line without a gate going red. So this face pins two things:
  (a) maintenance_trim boundary behaviour, built in-process (t1-t7 incl. one MUST-be-red leg and
      one mutation leg, per W-47 fourth leg / D10.2);
  (b) the production matrix face: filter enabled, zero surviving violations inside top-5,
      trimmed_total > 0, and the face threshold self-consistent with eval_date.
 
Reading a shared artifact for (a) would blame another session drift for my own judge (r252),
hence in-process construction. For (b) the matrix is the point, so it is read but never written.
 
Exit codes match run_gates: 0 all pass / 1 any leg red / 2 input face unavailable (R247:
missing artifact must not be recorded as zero violations).
"""
import argparse
import io
import json
import os
import sys
from datetime import date, timedelta
 
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
MATRIX = os.path.join(ROOT, "06-benchmark", "r260_matrix_trimmed.json")
ROWS = []
 
 
def ck(name, cond, detail=""):
    """Record and print one leg immediately: detail must carry the measured value, otherwise a
    reader cannot tell "asserted true" apart from "never measured" (#32 form 1)."""
    ROWS.append((bool(cond), name, str(detail)[:200]))
    mark = "" if cond else "  <-- got: " + str(detail)[:170]
    print("%-4s %s%s" % ("PASS" if cond else "FAIL", name, mark))
 
 
def in_process_legs():
    import r114_replacement_scan as R
    ev = R.EVAL_DATE
    thr = ev - timedelta(days=R.TWELVE_MONTHS_DAYS)
    # t0: the threshold is read from the judge under test; this gate never keeps its own copy
    # (two definitions of one constant always drift - R263/R280 family).
    ck("t0 threshold read from the judge under test", R.TWELVE_MONTHS_DAYS == 365 and thr < ev,
       (str(ev), str(thr), R.TWELVE_MONTHS_DAYS))
    ck("t1 active repo kept",
       R.maintenance_trim({"archived": False, "pushed_at": str(ev)}, ev) is None)
    # t2 boundary: the rule uses strictly-earlier, so the threshold day itself is not a violation
    # (same caliber as the owner live_probe in r260_trim_violations.json).
    ck("t2 boundary date (== threshold) not a violation",
       R.maintenance_trim({"archived": False, "pushed_at": thr.strftime("%Y-%m-%d")}, ev) is None,
       thr.strftime("%Y-%m-%d"))
    ck("t3 one day before threshold MUST be stale_pushed_at",
       R.maintenance_trim({"archived": False,
                           "pushed_at": (thr - timedelta(days=1)).strftime("%Y-%m-%d")}, ev)
       == "stale_pushed_at")
    ck("t4 archived MUST win over a fresh push date",
       R.maintenance_trim({"archived": True, "pushed_at": str(ev)}, ev) == "archived")
    # R247 both directions: a missing field must not fake a violation, and must not fake health
    # (the latter is surfaced as unknown_field by the caller, not silenced here).
    ck("t5 missing pushed_at kept (never guess a violation)",
       R.maintenance_trim({"archived": False}, ev) is None)
    ck("t6 unparsable pushed_at kept",
       R.maintenance_trim({"archived": False, "pushed_at": "not-a-date"}, ev) is None)
    # Mutation leg: writing <= instead of < must break t2, proving t2 is not a tautology.
    def mutated(m, eval_date):
        if m.get("archived"):
            return "archived"
        p = str(m.get("pushed_at") or "")[:10]
        if len(p) < 10:
            return None
        d = date(int(p[0:4]), int(p[5:7]), int(p[8:10]))
        if d <= eval_date - timedelta(days=R.TWELVE_MONTHS_DAYS):
            return "stale_pushed_at"
        return None
 
    ck("t7 mutation (<= instead of <) breaks t2 => t2 carries weight",
       mutated({"archived": False, "pushed_at": thr.strftime("%Y-%m-%d")}, ev) == "stale_pushed_at")
    return R, thr
 
 
def live_legs(R, thr):
    """Production face: four legs. Input unavailable => None, caller answers UNVERIFIED."""
    if not os.path.isfile(MATRIX):
        print("  [MT:FACE-MISSING] %s" % os.path.relpath(MATRIX, ROOT))
        return None
    try:
        d = json.load(io.open(MATRIX, encoding="utf-8-sig"))
    except Exception as e:
        print("  [MT:FACE-UNPARSABLE] %r" % (e,))
        return None
    mf, rows = d.get("maintenance_face"), d.get("rows")
    if not mf or not rows:
        print("  [MT:FACE-FIELDS-MISSING] maintenance_face / rows absent")
        return None
    ev = date(*[int(x) for x in str(mf.get("eval_date", "")).split("-")])
    left, unknown, slots = 0, 0, 0
    for r in rows:
        cs = r.get("candidates") or []
        slots += len(cs)
        for c in cs:
            if R.maintenance_trim(c, ev):
                left += 1
        unknown += int(r.get("maintenance_unknown_field_n") or 0)
    print("  [MT] slots=%d residual=%d trimmed=%s rows=%d unknown_field=%d"
          % (slots, left, mf.get("trimmed_total"), len(rows), unknown))
    trimmed = int(mf.get("trimmed_total") or 0)
    return [(bool(mf.get("enabled")), "L1 pipeline switch on (disabling it goes red)", mf.get("enabled")),
            (left == 0, "L2 zero surviving violations in top-5 (measured %d)" % left, left),
            (trimmed > 0, "L3 trimmed_total>0 proves the filter ran (%d)" % trimmed, trimmed),
            (str(mf.get("threshold_date") or "") == thr.strftime("%Y-%m-%d"),
             "L4 face threshold self-consistent with eval_date", mf.get("threshold_date"))]
 
 
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest-only", action="store_true",
                    help="only in-process legs (no production matrix read)")
    ap.add_argument("--json", dest="out")
    args = ap.parse_args()
    R, thr = in_process_legs()
    live = []
    face_missing = False
    if not args.selftest_only:
        live = live_legs(R, thr) or []
        face_missing = not live
    for ok, name, detail in live:
        ROWS.append((bool(ok), name, detail))
        print("%-4s %s%s" % ("PASS" if ok else "FAIL", name,
                              "" if ok else "  <-- " + str(detail)))
    n_fail = sum(1 for ok, _, _ in ROWS if not ok)
    print("legs total %d | pass %d | fail %d" % (len(ROWS), len(ROWS) - n_fail, n_fail))
    if args.out:
        doc = {"schema": "r260-maintenance-trim-fixtures-v1", "readonly": True,
               "provenance_cmd": "python 05-exec/r260_maintenance_trim_fixtures.py --json <件>",
               "matrix": os.path.relpath(MATRIX, ROOT),
               "eval_date": str(R.EVAL_DATE), "threshold_date": thr.strftime("%Y-%m-%d"),
               "selftest_only": bool(args.selftest_only),
               "legs": [{"name": n, "ok": bool(o), "detail": dt} for o, n, dt in ROWS],
               "fail_n": n_fail}
        io.open(args.out, "w", encoding="utf-8", newline=chr(10)).write(
            json.dumps(doc, ensure_ascii=False, indent=1))
        print("JSON -> %s" % args.out)
    if n_fail:
        print("[GATE:mtfix-fail] red legs: %s" % [n for ok, n, _ in ROWS if not ok][:5])
        return 1
    if face_missing:
        print("[GATE:mtfix-unverified] production face unavailable => not green (R247)")
        return 2
    # 末行必须只说本轮真跑过的腿：selftest-only 时生产面根本没读，写「production 4 legs」
    # 就是让声明超出实测（本仓 #32/#36 同族，也是 md_claim 那条门反对的形态）。
    scope = ("in-process 8 legs (t3/t4 must-red + t7 mutation)"
             if args.selftest_only else
             "in-process 8 legs (t3/t4 must-red + t7 mutation) + production 4 legs")
    print("[GATE:mtfix-pass] %s" % scope)
    return 0
 
 
if __name__ == "__main__":
    sys.exit(main())
