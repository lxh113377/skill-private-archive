#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# r278c_metrics.py -- independently authored yardstick for the before/after control arm (v2).
#
# stdlib only; nothing imported from 05-exec, so the reading cannot inherit the rubric it
# is meant to cross-check.
#
# v1 had two self-bugs, caught by cross-checking against shell grep (discipline D10.2):
#   A. headings_raw was always 0. "^ {0,3}#" was applied with findall() over the whole body
#      without re.MULTILINE, so ^ only ever anchored at byte 0. Fixed by compiling MULTILINE.
#   B. clause totals double-counted. "100vh" was matched both by the numeric-vh family and by
#      a separate 100vh pattern; "1920x1080" was matched by 1920, by 1080 and by the composite.
#      Also "100dvh" was matched by NEITHER family, because the digit-before guard rejected the
#      "d". Fixed by (i) making each family structurally disjoint and (ii) masking the composite
#      "1920x1080" hit before counting bare 1920 / bare 1080. Subset tallies such as 100vh are
#      now reported next to the totals and excluded from them, so they inform but never inflate.
#
# Counting contract, restated:
#   family occurrence counts are mutually exclusive, total = their sum,
#   clause_lines = number of distinct lines where any family fires (a line with three hits
#   counts once here, three times in occurrences),
#   every input leg is fail-closed: missing or empty markdown => one UNVERIFIED line,
#   non-zero exit, no JSON. A fetch failure therefore can never read as "before = 0 lines".
#
# usage: python r278c_metrics.py --md FILE --siblings LISTING --label LABEL [--selfcheck]
import argparse
import hashlib
import json
import os
import re
import sys

NL = chr(10)

NUM = "[0-9]+(?:\\.[0-9]+)?"
VIEWPORT_FAMILIES = {
    "vh_numeric": re.compile(NUM + "vh(?![A-Za-z0-9])"),
    "vh_standalone": re.compile(r"(?<![A-Za-z0-9_])vh(?![A-Za-z0-9_])"),
    "vw_numeric": re.compile(NUM + "vw(?![A-Za-z0-9])"),
    "vw_standalone": re.compile(r"(?<![A-Za-z0-9_])vw(?![A-Za-z0-9_])"),
    # dvh/svh/lvh: a digit MAY precede (100dvh), a letter may not, and the next char
    # must not extend the identifier. Numeric-vh above cannot fire here because the letter
    # between the digits and "vh" breaks NUM + "vh"; that is what keeps the families apart.
    "dvh": re.compile(r"(?<![A-Za-z_])dvh(?![A-Za-z0-9_])"),
    "svh_lvh": re.compile(r"(?<![A-Za-z_])[sl]vh(?![A-Za-z0-9_])"),
    "clamp_call": re.compile(r"(?<![A-Za-z0-9_-])clamp\s*\("),
}
VIEWPORT_SUBSET = {
    "100vh": re.compile(r"(?<![0-9.])100vh(?![A-Za-z0-9])"),
}
VIEWPORT_ANY = re.compile("|".join("(?:" + p.pattern + ")" for p in VIEWPORT_FAMILIES.values()))

STAGE_COMPOSITE = re.compile("1920[ \t]*[x\u00d7][ \t]*1080")
STAGE_COMPOSITE_MASK = "STAGEPAIRMASK"
STAGE_FAMILIES = {
    "px_1920": re.compile(r"(?<![0-9A-Za-z_.])1920(?![0-9])"),
    "px_1080": re.compile(r"(?<![0-9A-Za-z_.])1080(?![0-9])"),
    "fixed_stage": re.compile("fixed[ \t_-]*stage", re.IGNORECASE),
}
STAGE_ANY = re.compile("|".join("(?:" + p.pattern + ")" for p in STAGE_FAMILIES.values()) + "|1920[ \t]*[x\u00d7][ \t]*1080", re.IGNORECASE)

# MULTILINE here is the v2 fix for bug A: ^ must anchor per line, not per file
HEAD_RE = re.compile(r"^ {0,3}#{1,6}[ \t]+\S", re.MULTILINE)
FENCE_RE = re.compile(r"^ {0,3}(```|~~~)", re.MULTILINE)


def unverified(reason, code):
    # refuse to emit a reading: no JSON at all, one UNVERIFIED line, non-zero exit
    sys.stdout.write("UNVERIFIED reason=" + reason + NL)
    sys.exit(code)


def split_frontmatter(text):
    # body = text after a leading --- ... --- block; only when line 0 is exactly ---
    parts = text.split(NL)
    if parts and parts[0].strip() == "---":
        for i in range(1, min(len(parts), 200)):
            if parts[i].strip() == "---":
                return NL.join(parts[i + 1:]), i + 1
    return text, 0


def family_counts(families, text):
    return dict((k, len(p.findall(text))) for k, p in families.items())


def stage_counts(text):
    # mask the composite first so 1920x1080 contributes exactly one clause instead of three
    composite = len(STAGE_COMPOSITE.findall(text))
    masked = STAGE_COMPOSITE.sub(STAGE_COMPOSITE_MASK, text)
    fam = family_counts(STAGE_FAMILIES, masked)
    fam["stage_pair_1920x1080"] = composite
    return fam


def clause_lines(any_pattern, text):
    return sum(1 for ln in text.split(NL) if any_pattern.search(ln))


def heading_counts(body):
    # raw = every ATX heading line; prose = headings outside fenced code blocks
    raw = len(HEAD_RE.findall(body))
    prose = 0
    in_fence = False
    for ln in body.split(NL):
        if FENCE_RE.match(ln):
            in_fence = not in_fence
            continue
        if not in_fence and HEAD_RE.match(ln):
            prose += 1
    return raw, prose


def sibling_reference(text, siblings):
    # loose = full path OR basename OR parent-dir-name + slash ; strict = path OR basename
    loose, strict = [], []
    for rel in siblings:
        base = rel.rsplit("/", 1)[-1]
        head = rel.rsplit("/", 1)[0] if "/" in rel else ""
        parent = head.rsplit("/", 1)[-1] if "/" in head else head
        hit_path = rel in text
        hit_base = bool(base) and (base in text)
        hit_parent = bool(parent) and (parent + "/" in text)
        if hit_path or hit_base or hit_parent:
            loose.append(rel)
        if hit_path or hit_base:
            strict.append(rel)
    return loose, strict


def measure(md_path, listing_path, label):
    # shared path for --selfcheck and for the four real states, so the self-test exercises
    # exactly the code that produced the reported numbers
    raw = open(md_path, "rb").read()
    text = raw.decode("utf-8", errors="replace")
    parts = text.split(NL)
    n_lines = len(parts) - 1 if (parts and parts[-1] == "") else len(parts)
    body, fm = split_frontmatter(text)
    vp = family_counts(VIEWPORT_FAMILIES, text)
    st = stage_counts(text)
    sibs = [s for s in [x.strip() for x in open(listing_path, encoding="utf-8").read().split(NL) if x.strip()] if not s.endswith("SKILL.md")]
    loose, strict = sibling_reference(text, sibs)
    h_raw, h_prose = heading_counts(body)
    denom = len(sibs)
    return {
        "label": label,
        "md": md_path,
        "sha256_md": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "lines": n_lines,
        "frontmatter_lines": fm,
        "headings_raw": h_raw,
        "headings_prose": h_prose,
        "viewport_families": vp,
        "viewport_clause_total": sum(vp.values()),
        "viewport_clause_lines": clause_lines(VIEWPORT_ANY, text),
        "viewport_subset_100vh": dict((k, len(p.findall(text))) for k, p in VIEWPORT_SUBSET.items()),
        "fixed_stage_families": st,
        "fixed_stage_clause_total": sum(st.values()),
        "fixed_stage_clause_lines": clause_lines(STAGE_ANY, text),
        "sibling_denom": denom,
        "sibling_loose_hit": len(loose),
        "sibling_strict_hit": len(strict),
        "sibling_loose_rate_pct": round(100.0 * len(loose) / denom, 2) if denom else None,
        "sibling_strict_rate_pct": round(100.0 * len(strict) / denom, 2) if denom else None,
        "listing": listing_path,
    }


# ---- self-check: the judge measures itself before it is allowed to measure the skills ----
def selfcheck(tmpdir):
    # write each probe into a real file and run it through measure(), then assert
    ok = True
    listing = os.path.join(tmpdir, "sc_sibs.txt")
    open(listing, "w", encoding="utf-8").write("a/probe.md" + NL)
    probes = [
        ("100vh", ("vh_numeric", 1), ("dvh", 0), ("clamp_call", 0), ("viewport_clause_total", 1), ("fixed_stage_clause_total", 0)),
        ("height: 100dvh", ("vh_numeric", 0), ("dvh", 1), ("viewport_clause_total", 1), ("fixed_stage_clause_total", 0)),
        ("clamp(1px, 2vw, 3px)", ("clamp_call", 1), ("vw_numeric", 1), ("viewport_clause_total", 2), ("fixed_stage_clause_total", 0)),
        ("stage is 1920x1080", ("viewport_clause_total", 0), ("px_1920", 0), ("px_1080", 0), ("stage_pair_1920x1080", 1), ("fixed_stage_clause_total", 1)),
        ("fixed stage 1920 by 1080", ("fixed_stage", 1), ("px_1920", 1), ("px_1080", 1), ("fixed_stage_clause_total", 3)),
        ("# A" + NL + "~~~" + NL + "## B" + NL + "~~~" + NL + "## C", ("headings_raw", 3), ("headings_prose", 2)),
    ]
    for i, case in enumerate(probes):
        src = case[0]
        expectations = case[1:]
        f = os.path.join(tmpdir, "sc_%d.md" % i)
        open(f, "w", encoding="utf-8").write(src + NL)
        r = measure(f, listing, "selfcheck_%d" % i)
        for key, want in expectations:
            if key in r:
                got = r[key]
            elif key in r["viewport_families"]:
                got = r["viewport_families"][key]
            elif key in r["fixed_stage_families"]:
                got = r["fixed_stage_families"][key]
            else:
                got = "KEY-NOT-FOUND"
            verdict = "PASS" if got == want else "FAIL"
            if verdict == "FAIL":
                ok = False
            sys.stdout.write("SELFCHECK " + verdict + " case=" + str(i) + " key=" + key + " want=" + str(want) + " got=" + str(got) + NL)
    sys.stdout.write("SELFCHECK_RESULT " + ("PASS" if ok else "FAIL") + NL)
    sys.exit(0 if ok else 11)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md")
    ap.add_argument("--siblings")
    ap.add_argument("--label")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        selfcheck(os.path.dirname(os.path.abspath(a.md)) if a.md else os.getcwd())
    if not a.md or not a.siblings or not a.label:
        unverified("args-incomplete", 3)
    # fail-closed gates, one distinct exit code each
    if not os.path.isfile(a.md):
        unverified("md-missing " + a.md, 7)
    if len(open(a.md, "rb").read()) == 0:
        unverified("md-empty " + a.md, 8)
    if not os.path.isfile(a.siblings):
        unverified("siblings-missing " + a.siblings, 9)
    listing = [x.strip() for x in open(a.siblings, encoding="utf-8").read().split(NL) if x.strip()]
    if not listing:
        unverified("siblings-empty " + a.siblings, 10)
    sys.stdout.write(json.dumps(measure(a.md, a.siblings, a.label), ensure_ascii=False, sort_keys=True) + NL)


main()
