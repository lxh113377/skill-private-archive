# -*- coding: utf-8 -*-
# r161_bounce_back.py -- resident face for rule #37 (never bounce decisions back to the boss).
#
# Why this exists (rule #35: a discipline without a blocking point is not established):
#   round, but a full-disk scan (D:/global_memory / D:/global_skills / fenjue) found NO script carrying
#   those regexes -- the 5 "bounce" filename hits were all ppt-master icon SVGs. So 18/18 was a one-off
#   run with no resident recomputable face; next round a bounce-back could slip through unnoticed.
#
# Design choice (avoids a second source of truth): the 6 patterns are PARSED FROM the rule body at
#   runtime, not copied into this file. If the rule changes its patterns, this face follows it.
#   Fixtures (positive/negative examples) live in r161_bounce_fixtures.json.
#
# Three states: PASS = rule readable + fixtures all correct; FAIL = fixture mismatch (no teeth);
#   UNVERIFIED = rule file missing / no pattern parsed (R247: zero-input must not read as clean).
import argparse, io, json, os, re, sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RULE_PATH = os.environ.get(
    "FJ_RULE37_PATH", "D:/global_memory/core/rule37_never_bounce_back_any_conversation.md")
FIXTURES = os.path.join(HERE, "r161_bounce_fixtures.json")
P_FROM = "\u6211"        # first-person pronoun
P_TO = "\u8001\u5927"   # boss pronoun

ANCHOR_A = "回抛识别"   # rule criterion-1 heading text, matched verbatim
ANCHOR_B = "回抛"
ANCHOR_C = "识别"

# A rule body bullet looks like: - `regex here` (possibly with trailing prose)
BACKTICK_RX = re.compile(r"`([^`]+)`")   # all backticked spans per bullet (rule packs 2 per line)




def load_patterns(rule_path):
    """Parse the criterion-1 regex bullets out of the rule body (verbatim, no paraphrase)."""
    if not os.path.isfile(rule_path):
        return None, "rule body missing: %s" % rule_path
    try:
        lines = io.open(rule_path, encoding="utf-8").read().splitlines()
    except OSError as e:
        return None, "unreadable: %r" % (e,)
    start = None
    for i, ln in enumerate(lines):
        if ANCHOR_A in ln:
            start = i
            break

    if start is None:
        # Fall back: any line carrying the criterion-1 heading words
        for i, ln in enumerate(lines):
            if ANCHOR_B in ln and ANCHOR_C in ln:
                start = i
                break
    if start is None:
        return None, "criterion-1 block not found in rule body"
    pats = []
    # r161 self-catch (3rd): the rule writes a prose line ("判定法 = ...") between the heading and
    # the first bullet, and packs TWO regexes on one bullet (fullwidth-slash separated). Collect
    # every backticked span; stop only after we have collected some and hit a non-bullet line.
    for ln in lines[start + 1:start + 24]:
        found = BACKTICK_RX.findall(ln)
        if found:
            pats.extend(found)
        elif pats and ln.strip() and not ln.strip().startswith("-") and "\u5224\u5b9a\u6cd5" not in ln:
            break
    return pats, "ok"
def normalize(text, pats):
    return (text or "").replace(P_FROM, P_TO)


def find_bounces(text, pats):
    out = []
    for i, p in enumerate(pats):
        for m in re.finditer(p, normalize(text, pats)):
            out.append((i, m.group(0)))
    return out


def selftest(rule_path, fixtures):
    pats, note = load_patterns(rule_path)
    if pats is None:
        print("[BOUNCE] UNVERIFIED %s (R247: zero-input face must not read as clean)" % note)
        return 2
    if not os.path.isfile(fixtures):
        print("[BOUNCE] UNVERIFIED fixtures missing: %s" % fixtures)
        return 2
    fx = json.loads(io.open(fixtures, encoding="utf-8").read())
    pos, neg = fx.get("positive") or [], fx.get("negative") or []
    if not pos or not neg:
        print("[BOUNCE] UNVERIFIED fixtures empty (positive=%d negative=%d)" % (len(pos), len(neg)))
        return 2
    bad = []
    for t in pos:
        if not find_bounces(t, pats):
            bad.append(("MISSED", t))
    for t in neg:
        if find_bounces(t, pats):
            bad.append(("FALSE_POSITIVE", t))
    # Mutation leg: at least one positive must depend on the pronoun replacement
    dep = [t for t in pos if P_TO in normalize(t, pats) and P_TO not in t]
    if not dep:
        bad.append(("NO_DEP_SAMPLE", ""))
    print("[BOUNCE] patterns parsed %d | positive %d | negative %d | mismatch %d"
          % (len(pats), len(pos), len(neg), len(bad)))
    for kind, t in bad:
        print("  %s %s" % (kind, t[:70]))
    if bad:
        print("[BOUNCE:SELFTEST-FAIL] criterion has no teeth => its no-bounce reading is untrustworthy (#32)")
        return 1
    print("[BOUNCE:SELFTEST-PASS] %d positives all hit / %d negatives zero false-positive / mutation leg covered"
          % (len(pos), len(neg)))
    return 0


def scan(path, pats, out_json=None):
    try:
        txt = io.open(path, encoding="utf-8", errors="replace").read()
    except OSError as e:
        print("[BOUNCE] UNVERIFIED text unreadable: %r" % (e,))
        return 2
    hits = []
    for n, ln in enumerate(txt.splitlines(), 1):
        for pi, span in find_bounces(ln, pats):
            hits.append({"line": n, "pattern": pi, "span": span, "text": ln.strip()[:140]})
    face = {"scanned": os.path.basename(path), "hits_n": len(hits),
            "patterns_n": len(pats), "hits": hits[:40]}
    if out_json:
        doc = {"schema": "bounce-back-scan-r161-v1",
               "cmd": "python 05-exec/r161_bounce_back.py --text <file> --json <out>",
               "rule_path": RULE_PATH, "face": face,
               "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M")}
        io.open(out_json, "w", encoding="utf-8", newline=chr(10)).write(
            json.dumps(doc, ensure_ascii=False, indent=1))
    print("[BOUNCE] scanned %s | hits %d (patterns %d)" % (face["scanned"], face["hits_n"], face["patterns_n"]))
    for h in hits[:20]:
        print("  L%-5d p%d  %s" % (h["line"], h["pattern"], h["text"][:100]))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--text", default="")
    ap.add_argument("--json", dest="out")
    args = ap.parse_args()
    pats, note = load_patterns(RULE_PATH)
    if pats is None:
        print("[BOUNCE] UNVERIFIED %s (R247)" % note)
        return 2
    if args.selftest:
        return selftest(RULE_PATH, FIXTURES)
    if args.text:
        return scan(args.text, pats, args.out)
    print("[BOUNCE] patterns %d parsed from rule body; use --selftest or --text <file>" % len(pats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())