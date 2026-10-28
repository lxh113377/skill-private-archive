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
# Three matrices, three denominators (R260-9: never quote a number without naming its face).
#   MATRIX         = r20 artifact the maintenance-trim legs were first measured on; the reports
#                     already cite its numbers, so those legs stay on it (R241: no re-attribution).
#   LICENSE_MATRIX = the artifact the license legs read. r262 moved it to the BODY-AWARE matrix
#                     (r261 had license_class but NO license_body_class: M6 recomputed
#                     license_class(lic, None) and compared to the recorded value computed the same
#                     way => None == None => the leg agreed vacuously, i.e. another always-green
#                     leg, which is the defect class I kept catching all session).
# Re-pointing both at one file would silently re-attribute committed readings (R241).
MATRIX = os.path.join(ROOT, "06-benchmark", "r260_matrix_trimmed.json")
LICENSE_MATRIX = os.path.join(ROOT, "06-benchmark", "r262_matrix_bodied.json")
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
    # ---- r261: license_class ordering legs (R260-1). Each of these is a bug that the
    # docstring names as already-bitten-once: AGPL/LGPL contain the substring GPL, CC-BY-SA
    # shares a prefix with CC-BY, and UNLICENSE (public domain, mergeable) differs from
    # UNLICENSED (no license) by two letters. A single wrong order flips a whole family to
    # the wrong cap, so each pair is pinned separately rather than spot-checking one case.
    EXPECT = {"AGPL-3.0": "copyleft", "GPL-3.0": "copyleft", "LGPL-3.0": "weak-copyleft",
              "MPL-2.0": "weak-copyleft", "CC-BY-SA-4.0": "copyleft", "CC-BY-4.0": "permissive",
              "MIT": "permissive", "Apache-2.0": "permissive", "UNLICENSE": "permissive",
              "UNLICENSED": "none", "NOASSERTION": "unknown", "": "none",
              "Weird-Custom-1.0": "unknown"}
    bad = {k: (R.license_class(k), v) for k, v in EXPECT.items() if R.license_class(k) != v}
    ck("t8 license_class ordering (%d cases incl. AGPL/LGPL/CC-BY-SA prefix traps)" % len(EXPECT),
       not bad, sorted(bad)[:3])
    # t9: the cap must only lower, never raise. permissive keeps its full score, copyleft is
    # clamped; if someone flips min() to max() this leg goes red.
    base = {"skill_md_exact_n": 4, "blob_n": 120, "test_path_n": 30, "workflow_n": 5,
            "readme_n": 2, "docs_md_n": 9, "tree_state": "OK", "archived": False,
            "stars": 900, "pushed_at": str(ev)}
    def compat_of(lic):
        m = dict(base)
        m["license"] = lic
        return R.score5(m)[0]["compat"]
    ck("t9 copyleft clamped below permissive (%s vs %s)" % (compat_of("AGPL-3.0"), compat_of("MIT")),
       compat_of("AGPL-3.0") < compat_of("MIT"))
    ck("t10 NOASSERTION/unknown clamped strictly below permissive but above copyleft",
       compat_of("MIT") > compat_of("NOASSERTION") > compat_of("AGPL-3.0"),
       (compat_of("MIT"), compat_of("NOASSERTION"), compat_of("AGPL-3.0")))
    # t11 rollback switch must restore the pre-r261 behaviour exactly (it is the documented
    # escape hatch; a switch that changes nothing is worse than no switch).
    m_agpl = dict(base)
    m_agpl["license"] = "AGPL-3.0"
    ck("t11 --no-license-cap restores cap-off score (AGPL %s -> %s)" % (
       R.score5(m_agpl)[0]["compat"], R.score5(m_agpl, license_cap=False)[0]["compat"]),
       R.score5(m_agpl, license_cap=False)[0]["compat"] == 5
       and R.score5(m_agpl)[0]["compat"] < 5)
    # t12 the subclass check is the real tooth, so the label states the two facts actually
    # asserted: AGPL and GPL share one class (strong copyleft) while LGPL is a *different*
    # class (weak copyleft). Written the naive way ("GPL in u" before the AGPL/LGPL branches)
    # all three collapse into one class and this leg goes red - that is the bug class pinned.
    ck("t12 AGPL==GPL (strong copyleft) while LGPL is a separate class (ordering load-bearing)",
       R.license_class("AGPL-3.0") == R.license_class("GPL-3.0") == "copyleft"
       and R.license_class("LGPL-3.0") != R.license_class("AGPL-3.0"))
    # ---- r262 body-level license legs (R261-6). Each one pins a form I actually hit or fixed.
    # Shapes are copied from real LICENSE bodies fetched via gh api (key sentences kept verbatim),
    # not invented ideal strings.
    KUBE = ("KUBESPHERE IS LICENSED UNDER THE APACHE LICENSE 2.0, WITH THE FOLLOWING "
            "ADDITIONAL CONDITIONS: EXPLICIT PERMISSION OR A COMMERCIAL LICENSE FROM "
            "THE PRODUCER IS REQUIRED FOR COMMERCIAL USE")
    STD_APACHE = ("LICENSED UNDER THE APACHE LICENSE, VERSION 2.0 (THE LICENSE); YOU MAY "
                  "NOT USE THIS FILE EXCEPT IN COMPLIANCE WITH THE LICENSE")
    OP7418 = ("YOU MAY MAKE USE OF THE LICENSED WORK, PROVIDED THAT YOU MAY NOT USE THE "
              "LICENSED WORK FOR A COMMERCIAL\n                      PURPOSE")
    CCNC = ("THIS WORK IS LICENSED UNDER THE CREATIVE COMMONS "
            "ATTRIBUTION-NONCOMMERCIAL 4.0 INTERNATIONAL LICENSE")
    ck("t13 apache-with-conditions -> restricted (kubesphere false-negative regression)",
       R.classify_body(KUBE)[1] == "restricted", R.classify_body(KUBE)[:2])
    # My first cut used the generic phrase MAY NOT USE, which is part of the STANDARD Apache header
    # (verified on kubesphere) => every Apache repo would be clamped to cap=1: systemic false
    # positive that would have killed the best candidates. This leg is the regression pin.
    ck("t14 standard Apache header must NOT be restricted (false-positive guard)",
       R.classify_body(STD_APACHE)[1] != "restricted", R.classify_body(STD_APACHE)[:2])
    # Legal texts hard-wrap: op7418 splits the phrase across a newline, so matching must collapse
    # whitespace, else a restricted repo passes as permissive (measured in the real 20-repo face).
    ck("t15 line-wrapped phrase still caught via whitespace collapse (op7418)",
       R.classify_body(OP7418)[1] == "restricted", R.classify_body(OP7418)[2])
    ck("t16 CC-BY-NC not swallowed by the CC-BY prefix (ordering false-negative, Imbad0202)",
       R.classify_body(CCNC)[1] == "restricted", R.classify_body(CCNC)[:2])
    ck("t17 body evidence overrides the API field (NOASSERTION -> restricted, else unknown)",
       R.license_class("NOASSERTION", "restricted") == "restricted"
       and R.license_class("NOASSERTION") == "unknown")
    # Mutation leg for the rollback switch: --no-license-body must restore the API-only score.
    # If the switch were a no-op the gate would still be green while the escape hatch is broken.
    _m = dict(base)
    _m["license"] = "NOASSERTION"
    _m["license_body_class"] = "restricted"
    _on = R.score5(_m)[0]["compat"]
    _off = R.score5(_m, use_body=False)[0]["compat"]
    # t18 first cut passed the tuple (_on, _off) as the CONDITION. ck(name, cond, detail): a
    # non-empty tuple is always truthy => the leg could never fail. I authored an always-green leg
    # while spending this whole session removing them (gate 111, deadlink surface) - caught by
    # re-reading my own printed output, not by the gate. cond is now boolean-only; the readings
    # move into the name so the printed line still carries the numbers.
    ck("t18 use_body switch changes compat %s -> %s (rollback hatch is load-bearing)" % (_on, _off),
       _on == R.LICENSE_CAPS["restricted"] and _off == R.LICENSE_CAPS["unknown"],
       (_on, _off))
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
 
 
def license_live_legs(R):
    """License face on the body-aware matrix (r262): ten legs M1-M10. Unavailable input => None.

    Why a second artifact: the maintenance legs read the r260 file, whose numbers the committed
    reports already cite; re-pointing them at a re-generated matrix would silently re-attribute
    those readings (R241 + the R260-9 denominator rule).
    """
    if not os.path.isfile(LICENSE_MATRIX):
        print("  [LIC:FACE-MISSING] %s" % os.path.relpath(LICENSE_MATRIX, ROOT))
        return None
    try:
        d = json.load(io.open(LICENSE_MATRIX, encoding="utf-8-sig"))
    except Exception as e:
        print("  [LIC:FACE-UNPARSABLE] %r" % (e,))
        return None
    lf, rows = d.get("license_face"), d.get("rows")
    if not lf or not rows:
        print("  [LIC:FACE-FIELDS-MISSING] license_face / rows absent")
        return None
    slots = [c for r in rows for c in (r.get("candidates") or [])]
    # r262 修（两处）：① 类别元组漏 restricted ⇒ 正文证明「需商业授权 / 非商业」的仓不在判据眼里，
    #   M2 失去对该档的牙；② 这里原先**自己重算** license_class(lic)（不带正文档），与矩阵落盘的
    #   license_class 成双源（R260-5 同族）⇒ 门与生产读数可以各说各话。改为读生产已落的字段，
    #   另用 M6 腿做「重算 == 落盘」的一致性校验（一致性才是门该管的事，不是再算一遍当结论）。
    RISK_SET = ("copyleft", "weak-copyleft", "restricted")
    at5 = sum(1 for c in slots
              if c.get("license_class") in RISK_SET and c["score5"]["compat"] == 5)
    covered = sum(1 for c in slots if c.get("license_class"))
    risky = [r for r in rows if r.get("license_risk")]
    named = sorted(r["slug"] for r in risky)
    unsurfaced = [r["slug"] for r in risky if not (r.get("permissive_alternatives_emitted") or [])]
    # 漂移与违规各算一次（旧写法在元组的三个位置重复同一段推导式：既难读，又因为我多写一个右括号
    #   直接把文件写炸 —— r262 实测 SyntaxError line 222。算一次、引用多次。）
    drift6 = [c for c in slots
              if R.license_class(c.get("license"), c.get("license_body_class"))
              != c.get("license_class")]
    viol7 = [c for c in slots
             if c.get("license_class") in R.LICENSE_CAPS
             and c["score5"]["compat"] > R.LICENSE_CAPS[c["license_class"]]]
    # r262 M10: emitted slots whose API field is the lying shape (NOASSERTION/empty) but that carry
    # no body evidence => the evidence pack was not refreshed for this matrix generation. Without
    # this leg such a slot scores as unknown (cap=4, only a weak penalty) while M2-M9 stay green:
    # the gate would then measure the pack it happens to hold instead of the face it was given.
    # Scope = emitted candidates only; unemitted repos change no reading, counting them would
    # invent a red that proves nothing.
    noev10 = sorted({c["repo"] for c in slots
                     if (c.get("license") or "").upper() in ("NOASSERTION", "")
                     and not c.get("license_body_class")})
    print("  [LIC] slots=%d risky_at_5=%d covered=%d risky_rank0=%d unsurfaced=%d drift=%d capviol=%d uncovered=%d"
          % (len(slots), at5, covered, len(risky), len(unsurfaced), len(drift6), len(viol7), len(noev10)))
    return [
        (bool(lf.get("enabled")),
         "M1 license cap enabled in the pipeline (switching it off goes red)", lf.get("enabled")),
        # Label states the set actually tested (copyleft + weak-copyleft + restricted): after
        # r262 the restricted class is in scope too, so the old label understated coverage.
        (at5 == 0,
         "M2 no risky-class slot (copyleft/weak/restricted) keeps compat=5; measured=%d" % at5,
         at5),
        (covered == len(slots) and covered == int(lf.get("slots_emitted") or -1),
         "M3 every emitted candidate carries license_class (%d/%d, face says %s)"
         % (covered, len(slots), lf.get("slots_emitted")), covered),
        (named == sorted(lf.get("risky_rank0_rows") or []),
         "M4 face-level risky list matches per-row flags (%d rows)" % len(named), named),
        (not unsurfaced,
         "M5 every risky rank0 row surfaces a named mergeable alternative (%d missing)"
         % len(unsurfaced), unsurfaced),
        # M6 单源一致性：逐件用**同一函数同一口径**重算档位，必须等于生产落盘值。
        #   这条腿专门防「门自己另算一套」：任一处（面统计/门/生产）漏改参数即红。
        (not drift6,
         "M6 recorded license_class == recomputed-with-body (single source); drift=%d"
         % len(drift6),
         [(c["repo"], c.get("license_class"),
           R.license_class(c.get("license"), c.get("license_body_class"))) for c in drift6[:3]]),
        # M7 上限真的生效：凡档位属禁合入族，compat 不得超过该档 cap（cap 只降不升的可执行面）。
        (not viol7,
         "M7 every classed slot honours its cap; violations=%d" % len(viol7),
         [(c["repo"], c["license_class"], c["score5"]["compat"],
           R.LICENSE_CAPS[c["license_class"]]) for c in viol7[:3]]),
        # M8/M9 non-vacuity guards for M6/M7 (added the moment the hole was visible).
        # If the evidence pack ever goes missing, license_body_class is None everywhere:
        # M6 then compares None to None and M7 has nothing to check, so both would pass
        # while proving nothing. These two legs require the face to positively show that
        # body evidence exists and that the switch was on when the face was produced.
        (int(((lf.get("body_evidence") or {}).get("restricted_by_body")) or 0) > 0,
         "M8 body evidence present on face (restricted=%s) so M6/M7 cannot be vacuous" %
         ((lf.get("body_evidence") or {}).get("restricted_by_body")),
         lf.get("body_evidence")),
        (bool(((lf.get("body_evidence") or {}).get("enabled"))),
         "M9 license body switch enabled in the produced face",
         (lf.get("body_evidence") or {}).get("enabled")),
        (not noev10,
         "M10 emitted NOASSERTION/empty slots all carry body evidence; uncovered=%d" % len(noev10),
         noev10[:4])
        ]


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
        # Both production faces must be readable. Losing either one is UNVERIFIED, never a
        # silent skip - a skipped face would report green while nothing was measured (R247).
        mnt = live_legs(R, thr)
        lic = license_live_legs(R)
        live = (mnt or []) + (lic or [])
        face_missing = (mnt is None) or (lic is None)
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
    # 计数从 ROWS 现算，不写死：r261 加许可腿后这里仍印「in-process 8 + production 4」
    #   而实跑 13 + 9 —— 上一轮我修的是「selftest-only 谎报生产面」，这次修的是同族的
    #   「数字写死会随加腿漂移」。派生式没有可漂移的余地。
    n_t = sum(1 for ok, n, _ in ROWS if n[:1] == "t")
    n_l = sum(1 for ok, n, _ in ROWS if n[:1] == "L")
    n_m = sum(1 for ok, n, _ in ROWS if n[:1] == "M")
    # The parenthetical is derived too: naming a fixed range (t8-t12) went stale the moment t13-t18
    # landed, which is the same "declaration exceeds measurement" class as hardcoding the counts.
    # Counting by keyword in the name was wrong the first time (only t8/t11 contain the word
    # "license" => it printed "license legs 2" while t8-t18 is eleven legs). Derive from the leg
    # NUMBER instead: the license group is every t-leg numbered 8 or higher.
    n_lic = sum(1 for ok, n, _ in ROWS
                if n[:1] == "t" and len(n) > 1 and n[1].isdigit()
                and int(n[1:].split()[0]) >= 8)
    desc = ("in-process %d legs (t3/t4 must-red + t7 mutation + license legs %d)" % (n_t, n_lic))
    if not args.selftest_only:
        # 生产面两组分别报数：合并成一个数就看不出许可腿有没有跑
        desc += " + production %d legs (maintenance %d + license %d)" % (n_l + n_m, n_l, n_m)
    print("[GATE:mtfix-pass] %s" % desc)
    return 0
 
 
if __name__ == "__main__":
    sys.exit(main())
