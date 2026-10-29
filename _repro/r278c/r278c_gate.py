#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# r278c_gate.py -- independent recomputation gate for r278_before_after_control.json.
#
# Why it exists: the deliverable is my own prose and my own numbers, so trusting it would be
# self-attestation. This gate re-derives every reported byte count from the repository through
# a different channel (subprocess -> git show -> len(stdout bytes)) instead of reusing the
# numbers the earlier measure printed, and recomputes every delta from the stored arm pairs.
# Any mismatch fails the gate.
#
# C10 is the live negative control: a bogus sha is pushed through the very fetch function that
# C9 uses. It must come back non-zero, and a non-zero fetch is UNVERIFIED -- never a 0-byte
# reading. Without that leg a silently broken fetch would produce "before = 0" and the deltas
# would still tie out arithmetically, which is exactly the假绿 this arm must not ship.
#
# checks: C1 schema | C2 both arms per item | C3 >=5 shared numeric metrics |
#   C4 scalar delta recomputation | C5 family delta recomputation |
#   C6 each sha row carries the command that produced it (>=1 git-log row per item) |
#   C7 rollback evidence (cat-file + backup list + verdict) |
#   C8 both negative-control legs documented with rc values |
#   C9 bytes re-derived from git == stored bytes, four arms |
#   C10 live negative control | C11 managed root still clean

import argparse
import json
import subprocess
import sys

REPO = "D:/global_skills"
ITEMS = ["test-driven-development", "frontend-slides"]
SCALAR_KEYS = [
    "bytes", "lines", "headings_raw", "headings_prose",
    "viewport_clause_total", "viewport_clause_lines",
    "fixed_stage_clause_total", "fixed_stage_clause_lines",
    "sibling_loose_hit", "sibling_strict_hit",
    "sibling_loose_rate_pct", "sibling_strict_rate_pct", "sibling_denom",
]
FAMILY_KEYS = ["viewport_families", "fixed_stage_families"]
LF = chr(10)
results = []


def check(name, ok, detail):
    # one recorded outcome; a False is always surfaced, never swallowed
    results.append((name, bool(ok), detail))


def git_bytes(refspec):
    # fetch a blob and return (returncode, byte_length, first stderr line).
    # returncode != 0 means UNVERIFIED: byte_length 0 is an artifact of failure, not data.
    p = subprocess.run(["git", "-C", REPO, "show", refspec],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err = (p.stderr or b"").decode("utf-8", "replace").strip()
    return p.returncode, len(p.stdout or b""), err.split(LF)[0]


def git_text(args):
    p = subprocess.run(["git", "-C", REPO] + args,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--neg-live", action="store_true")
    a = ap.parse_args()

    if a.neg_live:
        rc, n, err = git_bytes("deadbeef1234567:frontend-slides/SKILL.md")
        if rc != 0:
            print("NEGCONTROL_UNVERIFIED rc=" + str(rc) + " len_reported=" + str(n) + " err=" + err)
            print("NEGCONTROL_VERDICT refused: a fetch failure is UNVERIFIED, not 0 bytes of text")
            return 0
        print("NEGCONTROL_FAIL nonexistent sha was accepted (rc=0)")
        return 1

    doc = json.load(open(a.json, encoding="utf-8"))
    mb = doc.get("metrics_before", {})
    ma = doc.get("metrics_after", {})
    dl = doc.get("delta", {})

    check("C1_schema", doc.get("schema") == "before-after-control-v1",
          "schema=" + str(doc.get("schema")))
    both = [i for i in ITEMS if i in mb and i in ma]
    check("C2_both_arms_per_item", len(both) == len(ITEMS), "armed_items=" + str(both))

    counts = {}
    for i in ITEMS:
        if i in mb and i in ma:
            shared = [k for k in SCALAR_KEYS
                      if isinstance(mb[i].get(k), (int, float)) and isinstance(ma[i].get(k), (int, float))]
            counts[i] = len(shared)
    check("C3_at_least_5_metrics", all(counts.get(i, 0) >= 5 for i in ITEMS), str(counts))

    bad = []
    for i in ITEMS:
        if i not in dl or i not in mb or i not in ma:
            bad.append(i + ":missing")
            continue
        for k in SCALAR_KEYS:
            if k in dl[i]:
                want = round(ma[i][k] - mb[i][k], 2)
                if abs(float(dl[i][k]) - want) > 0.011:
                    bad.append(i + "." + k + " stored=" + str(dl[i][k]) + " recomputed=" + str(want))
        for fk in FAMILY_KEYS:
            got = dl[i].get(fk + "_delta", {})
            for key, v in got.items():
                try:
                    want = ma[i][fk][key] - mb[i][fk][key]
                except KeyError:
                    bad.append(i + "." + fk + "." + key + ":key-missing")
                    continue
                if v != want:
                    bad.append(i + "." + fk + "." + key + " stored=" + str(v) + " recomputed=" + str(want))
    check("C4_C5_delta_recomputation", not bad, "mismatches=" + str(bad[:6]) + " n=" + str(len(bad)))

    rows = doc.get("shas_used", [])
    no_cmd = [str(r.get("sha", "?"))[:12] for r in rows if not str(r.get("command", "")).strip()]
    per_item_log = {}
    for i in ITEMS:
        per_item_log[i] = sum(1 for r in rows
                              if r.get("item") == i and "log" in str(r.get("command", "")))
    check("C6_shas_have_commands", (not no_cmd) and all(per_item_log[i] >= 1 for i in ITEMS),
          "rows=" + str(len(rows)) + " missing_cmd=" + str(no_cmd) + " gitlog_rows=" + str(per_item_log))

    rb = doc.get("rollback_evidence", {})
    rbad = []
    for i in ITEMS:
        e = rb.get(i, {}) or {}
        if not e.get("cat_file_e"):
            rbad.append(i + ":no-cat-file")
        if not e.get("backup_files"):
            rbad.append(i + ":no-backup-list")
        if "FEASIBLE" not in str(e.get("verdict", "")):
            rbad.append(i + ":no-verdict")
    check("C7_rollback_evidence", not rbad, str(rbad))

    nc = doc.get("negative_controls", {}) or {}
    fl = nc.get("fetch_leg", [])
    ml = nc.get("measure_leg", [])
    rc_fl = sum(1 for x in fl if "rc" in str(x))
    rc_ml = sum(1 for x in ml if "rc" in str(x))
    check("C8_negative_controls_documented", len(fl) >= 2 and len(ml) >= 2 and rc_fl >= 2 and rc_ml >= 2,
          "fetch_leg=" + str(len(fl)) + "(rc " + str(rc_fl) + ") measure_leg=" + str(len(ml)) + "(rc " + str(rc_ml) + ")")

    specs = {}
    specs[("test-driven-development", "before")] = "079b91f3~1:test-driven-development/SKILL.md"
    specs[("test-driven-development", "after")] = "HEAD:test-driven-development/SKILL.md"
    specs[("frontend-slides", "before")] = "6394cbae~1:frontend-slides/SKILL.md"
    specs[("frontend-slides", "after")] = "HEAD:frontend-slides/SKILL.md"
    stored = {}
    stored[("test-driven-development", "before")] = mb["test-driven-development"]["bytes"]
    stored[("test-driven-development", "after")] = ma["test-driven-development"]["bytes"]
    stored[("frontend-slides", "before")] = mb["frontend-slides"]["bytes"]
    stored[("frontend-slides", "after")] = ma["frontend-slides"]["bytes"]
    recon = []
    mism = []
    for k in specs:
        rc, n, err = git_bytes(specs[k])
        if rc != 0:
            mism.append(str(k) + ":UNVERIFIED rc=" + str(rc) + " (0 bytes NOT counted as a reading)")
        elif n != stored[k]:
            mism.append(k[0] + "-" + k[1] + ": git=" + str(n) + " json=" + str(stored[k]))
        else:
            recon.append(k[0][:3] + "-" + k[1] + "=" + str(n))
    check("C9_bytes_recomputed_from_git", (not mism) and len(recon) == 4,
          "ok=" + str(recon) + " bad=" + str(mism))

    rc, n, err = git_bytes("deadbeef1234567:frontend-slides/SKILL.md")
    check("C10_live_negative_control", rc != 0,
          "bogus sha rc=" + str(rc) + " (must be nonzero; its length " + str(n) + " must never enter a delta)")

    rc, out = git_text(["status", "--porcelain", "--", "test-driven-development", "frontend-slides"])
    dirty = len([x for x in out.split(LF) if x.strip()])
    check("C11_managed_root_clean", rc == 0 and dirty == 0, "rc=" + str(rc) + " dirty_lines=" + str(dirty))

    npass = sum(1 for _, ok, _ in results if ok)
    for name, ok, detail in results:
        print(("PASS " if ok else "FAIL ") + name + " :: " + str(detail)[:220])
    if npass == len(results):
        print("GATE_PASS r278_before_after_control checks=" + str(len(results)) + " bad=0")
        return 0
    print("GATE_FAIL checks=" + str(len(results)) + " bad=" + str(len(results) - npass))
    return 1


sys.exit(main())
