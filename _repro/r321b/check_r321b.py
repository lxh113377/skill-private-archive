#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_r321b.py -- R321B self-proof: read broken_verify.json, assert the evidence
dossier is well-formed and the gate has teeth.

Why this exists: upstream r320a census reported 10 broken links; R321B re-verifies which
are real and which are template-placeholder false positives. The dossier must be
re-computable by someone else, so it must not be able to pass with empty fields.

How it works (any failed assertion => rc=1 and teeth=fail reason; all pass => teeth=pass):
 1) schema literal == r321b-broken-verify-1; skills_head must be a 40-hex sha.
 2) len(items) == 10, matching census broken_total.
 3) counts real+placeholder+other == 10 AND reconciled item-by-item against items[].kind;
    summing alone would let 3-in-real + 7-in-other still total 10.
 4) every item: path/kind/entry_line/tree_truth/cmd non-empty, exit must be int (not bool),
    kind must be in {REAL_BROKEN, PLACEHOLDER_FALSE, OTHER}. Empty cmd = no provenance.
 5) every proposed_fix: rule non-empty, kills non-negative int, keeps_red must hold >=1
    non-empty string -- a fix with no counter-example is a loosened gate and must be red.
 6) cross-check: kills may not exceed placeholder count.

Run: set PYTHONPYCACHEPREFIX then  python -B _repro/r321b/check_r321b.py
Expected last line: [R321B:BROKEN] real=1 placeholder=9 teeth=pass
Negative control: add --negctl to inject 8 defect shapes in memory and re-run.
"""
import copy
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(HERE, "broken_verify.json")
KINDS = set(["REAL_BROKEN", "PLACEHOLDER_FALSE", "OTHER"])
REQUIRED = ["path", "kind", "entry_line", "tree_truth", "cmd"]
COUNT_KEYS = ["real", "placeholder", "other"]
KIND_OF = {"real": "REAL_BROKEN", "placeholder": "PLACEHOLDER_FALSE", "other": "OTHER"}


def fail(msg):
    print("[R321B:BROKEN] teeth=fail " + msg)
    return 1


def load():
    return json.loads(open(DOC, encoding="utf-8").read())


def check(doc):
    if doc.get("schema") != "r321b-broken-verify-1":
        return fail("schema_mismatch " + str(doc.get("schema")))
    head = doc.get("skills_head") or ""
    if not re.match("^[0-9a-f]{40}$", head):
        return fail("skills_head_not_40hex " + str(head))
    items = doc.get("items")
    if not isinstance(items, list):
        return fail("items_not_list")
    if len(items) != 10:
        return fail("items_len=" + str(len(items)) + " expected 10 (census broken_total)")
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            return fail("item[" + str(i) + "] not object")
        for k in REQUIRED:
            v = it.get(k)
            if not isinstance(v, str) or v.strip() == "":
                return fail("item[" + str(i) + "]." + k + " empty or missing")
        if it["kind"] not in KINDS:
            return fail("item[" + str(i) + "].kind invalid: " + repr(it["kind"]))
        e = it.get("exit")
        if isinstance(e, bool) or not isinstance(e, int):
            return fail("item[" + str(i) + "].exit not int: " + repr(e))
    c = doc.get("counts") or {}
    for k in COUNT_KEYS:
        if isinstance(c.get(k), bool) or not isinstance(c.get(k), int):
            return fail("counts." + k + " not int: " + repr(c.get(k)))
    ssum = 0
    for k in COUNT_KEYS:
        ssum += c[k]
    if ssum != 10:
        return fail("counts_sum=" + str(ssum) + " != 10")
    tally = {}
    for it in items:
        tally[it["kind"]] = tally.get(it["kind"], 0) + 1
    for k in COUNT_KEYS:
        if tally.get(KIND_OF[k], 0) != c[k]:
            return fail("counts_vs_kind_mismatch on " + k + " counts=" + str(c[k]) +
                        " tally=" + str(tally.get(KIND_OF[k], 0)))
    fixes = doc.get("proposed_fix")
    if not isinstance(fixes, list) or len(fixes) < 2:
        return fail("proposed_fix must be list with >=2 candidates")
    for i, fx in enumerate(fixes):
        if not isinstance(fx, dict):
            return fail("proposed_fix[" + str(i) + "] not object")
        r = fx.get("rule")
        if not isinstance(r, str) or r.strip() == "":
            return fail("proposed_fix[" + str(i) + "].rule empty")
        kk = fx.get("kills")
        if isinstance(kk, bool) or not isinstance(kk, int) or kk < 0:
            return fail("proposed_fix[" + str(i) + "].kills not non-negative int")
        if kk > c["placeholder"]:
            return fail("proposed_fix[" + str(i) + "].kills=" + str(kk) + " exceeds placeholder=" + str(c["placeholder"]))
        kr = fx.get("keeps_red")
        if not isinstance(kr, list) or len(kr) < 1:
            return fail("proposed_fix[" + str(i) + "].keeps_red must hold >=1 counter-example (no teeth)")
        for j, x in enumerate(kr):
            if not isinstance(x, str) or x.strip() == "":
                return fail("proposed_fix[" + str(i) + "].keeps_red[" + str(j) + "] empty")
    return 0


def negctl(doc):
    # Inject each defect shape into a deepcopy; the gate must catch every one.
    bad = [
        ("empty_kind", lambda d: d["items"][0].__setitem__("kind", "")),
        ("missing_cmd", lambda d: d["items"][3].__setitem__("cmd", "")),
        ("items_9", lambda d: d["items"].pop()),
        ("counts_sum_9", lambda d: d["counts"].__setitem__("placeholder", 8)),
        ("kind_tally_drift", lambda d: d["items"][1].__setitem__("kind", "REAL_BROKEN")),
        ("clear_keeps_red", lambda d: d["proposed_fix"][0].__setitem__("keeps_red", [])),
        ("blank_entry_line", lambda d: d["items"][5].__setitem__("entry_line", "  ")),
        ("kills_over_placeholder", lambda d: d["proposed_fix"][1].__setitem__("kills", 40)),
    ]
    rc_all = 0
    for name, mutate in bad:
        d2 = copy.deepcopy(doc)
        mutate(d2)
        r = check(d2)
        print("NEGCTL " + name + " => rc=" + str(r) + " " + ("caught" if r else "MISSED"))
        if r == 0:
            rc_all = 1
    if check(copy.deepcopy(doc)) != 0:
        print("NEGCTL pristine_document_regressed")
        rc_all = 1
    return rc_all


def main():
    if not os.path.exists(DOC):
        return fail("missing " + DOC)
    doc = load()
    if "--negctl" in sys.argv:
        if negctl(doc):
            return fail("negative_control_missed_defect")
    rc = check(doc)
    if rc:
        return rc
    c = doc["counts"]
    print("[R321B:BROKEN] real=" + str(c["real"]) + " placeholder=" + str(c["placeholder"]) + " teeth=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
