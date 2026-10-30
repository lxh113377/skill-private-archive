# -*- coding: utf-8 -*-
"""R305B merge-plan validator. Why this exists: the swap round needs a machine gate,
not a prose promise, that refuses a dst outside the skill dir and refuses land on a
candidate path outside the measured landable corpus. How it works: dst_in_skill_dir
is pure string arithmetic on the relative path; check_file_entry enforces the action
set, the dst rule and the land-source rule; run_legs feeds three synthetic rows (two
negative, one positive) so the gate proves it has teeth instead of being always green."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN_PATH = os.path.join(HERE, "merge_plan.json")
ACTIONS = ("land", "drop", "block")
NL = chr(10)

def dst_in_skill_dir(dst):
    """Return (ok, code). Relative-only: absolute, drive-letter and any parent hop are refused."""
    if not isinstance(dst, str) or dst.strip() == "":
        return False, "DST_MISSING"
    d = dst.strip().replace(chr(92), "/")
    if d.startswith("/"):
        return False, "DST_ABSOLUTE"
    if len(d) >= 2 and d[1] == ":":
        return False, "DST_DRIVE_LETTER"
    parts = [p for p in d.split("/") if p not in ("", ".")]
    if len(parts) == 0:
        return False, "DST_EMPTY"
    for p in parts:
        if p == "..":
            return False, "DST_OUTSIDE_SKILL_DIR"
    return True, "OK"

def check_file_entry(entry, skill):
    """Collect every row-level violation; empty list means the row may land as written."""
    errs = []
    src = entry.get("src")
    act = entry.get("action")
    dst = entry.get("dst")
    if act not in ACTIONS:
        errs.append("ACTION_UNKNOWN")
    if not isinstance(src, str) or src.strip() == "":
        errs.append("SRC_MISSING")
    why = entry.get("why")
    if not isinstance(why, str) or why.strip() == "":
        errs.append("WHY_MISSING")
    if act == "land":
        ok, code = dst_in_skill_dir(dst)
        if not ok:
            errs.append(code)
        if src not in skill.get("landable_src", []):
            errs.append("SRC_NOT_LANDABLE")
    else:
        if dst is not None:
            errs.append("DST_ON_NON_LAND")
    return errs

def run_legs(skill):
    """Two negative legs must be rejected and the positive leg accepted; return (text, passed)."""
    legs = []
    row_a = {"src": "references/copy.md", "action": "land", "dst": "../other-skill/x.md", "why": "negative leg A"}
    ea = check_file_entry(row_a, skill)
    legs.append(("[LEG-A] dst=../other-skill/x.md -> " + ("REJECTED:" + ",".join(ea) if ea else "ACCEPTED"), len(ea) > 0))
    row_b = {"src": "assets/charts.js", "action": "land", "dst": "assets/charts.js", "why": "negative leg B"}
    eb = check_file_entry(row_b, skill)
    legs.append(("[LEG-B] src=assets/charts.js action=land -> " + ("REJECTED:" + ",".join(eb) if eb else "ACCEPTED"), len(eb) > 0))
    row_c = {"src": "references/copy.md", "action": "land", "dst": "references/copy.md", "why": "positive leg C"}
    ec = check_file_entry(row_c, skill)
    legs.append(("[LEG-C+] dst=references/copy.md -> " + ("REJECTED:" + ",".join(ec) if ec else "ACCEPTED"), len(ec) == 0))
    return legs

def main():
    with open(PLAN_PATH, "r", encoding="utf-8") as fh:
        plan = json.load(fh)
    sys.stdout.write("[R305B:KEYS] " + ",".join(sorted(plan.keys())) + NL)
    skills = plan.get("skills", [])
    counts = {"land": 0, "drop": 0, "block": 0}
    bad = []
    for skill in skills:
        for entry in skill.get("files", []):
            errs = check_file_entry(entry, skill)
            if errs:
                bad.append(str(skill.get("slug")) + ":" + str(entry.get("src")) + ":" + ",".join(errs))
            counts[entry.get("action")] = counts.get(entry.get("action"), 0) + 1
    legs = run_legs(skills[1] if len(skills) > 1 else skills[0])
    for text, _ok in legs:
        sys.stdout.write(text + NL)
    for row in bad:
        sys.stdout.write("[R305B:BAD] " + row + NL)
    leg_ok = all(ok for _t, ok in legs)
    plan_ok = len(skills) == 2 and not bad
    sys.stdout.write("[R305B:VERDICT] " + ("PASS" if (leg_ok and plan_ok) else "FAIL") + NL)
    total = sum(counts.values())
    sys.stdout.write("[R305B:PLAN] skills=" + str(len(skills)) + " files=" + str(total) + " land=" + str(counts["land"]) + " drop=" + str(counts["drop"]) + " block=" + str(counts["block"]) + " dropped_refs=" + str(len(plan.get("dropped_refs", []))) + " blocked=" + str(len(plan.get("blocked", []))) + NL)
    return 0 if (leg_ok and plan_ok) else 1

if __name__ == "__main__":
    sys.exit(main())
