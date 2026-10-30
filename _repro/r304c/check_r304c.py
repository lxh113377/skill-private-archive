# -*- coding: utf-8 -*-
r"""check_r304c.py (C1/r304c): independent judgement for C5 merged-state + candidate script runnability.

Why: no number is copied from any document. members / cap / live are read at run time out of
05-exec/ratchet_gate.py via importlib (inject_union_paths, hard_caps, inject_union_bytes), and the
merged state is recomputed from the folding deltas declared in admission_c5_scripts.json.

How it runs: load the admission doc -> recompute the C5 verdict -> print two negative-control legs ->
print the fixed last line. The last line token is what the parent greps; both legs must stay non-green.
r"""
import ast
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = Path("C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/05-exec/ratchet_gate.py")
ADMIT = HERE / "admission_c5_scripts.json"


def load_gate():
    # load by file path so the gate module own WS/HERE resolve to the project root, not to this file
    spec = importlib.util.spec_from_file_location("rg_admit", str(GATE))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def c5_verdict(live, deltas, members, cap):
    # deltas = [(path, bytes)]; only member-set paths are summed, so out-of-list writes can never move C5
    counted = 0
    counted_paths = []
    for p, d in deltas:
        if p in members:
            counted += int(d)
            counted_paths.append(p)
    merged = int(live) + counted
    if not isinstance(cap, int):
        return "unverified", merged, counted, counted_paths
    return ("ok" if merged <= cap else "bad"), merged, counted, counted_paths


def script_state(present, check_rc, run_rc):
    # ladder: missing path => FAIL; any rc absent (never run) => unverified; any rc != 0 => FAIL; both 0 => OK
    if not present:
        return "FAIL"
    if check_rc is None or run_rc is None:
        return "unverified"
    if check_rc != 0:
        return "FAIL"
    if run_rc != 0:
        return "FAIL"
    return "OK"


def main():
    gate = load_gate()
    members = sorted(gate.inject_union_paths())
    cap = gate.hard_caps().get("inject_union_bytes")
    live = gate.inject_union_bytes()
    doc = json.loads(ADMIT.read_text(encoding="utf-8"))
    print("admission keys:", sorted(doc.keys()))
    c5 = doc["c5"]
    deltas = [(row[0], row[1]) for row in c5["folding_rule"]["deltas"]]
    state, merged, counted, counted_paths = c5_verdict(live, deltas, set(members), cap)
    scripts = doc.get("scripts") or []
    ok = sum(1 for s in scripts if s.get("state") == "OK")
    fail = sum(1 for s in scripts if s.get("state") != "OK")
    print("members=%d cap=%s live=%s admitted=%s recomputed=%s merged=%s counted=%d"
          % (len(members), cap, live, c5["state"], state, merged, counted))
    neg_a = script_state(False, 0, 0)
    print("[NEG-A] script_state(present=False, check_rc=0, run_rc=0) -> %s" % neg_a)
    member0 = members[0]
    big = (cap or 65536) * 10
    st_b1, mv_b1, cnt_b1, _ = c5_verdict(live, [(member0, big)], set(members), cap)
    print("[NEG-B1] delta=%d on member path -> state=%s merged=%s" % (big, st_b1, mv_b1))
    st_b2, mv_b2, cnt_b2, _ = c5_verdict(live, [("D:/__not_a_member__/x.md", big)], set(members), cap)
    print("[NEG-B2] delta=%d on non-member path -> state=%s merged=%s" % (big, st_b2, mv_b2))
    print("[R304C:ADMIT] c5=%s members=%d live=%d merged=%d cap=%s scripts=%d scripts_ok=%d scripts_fail=%d"
          % (state, len(members), live, merged, cap, len(scripts), ok, fail))
    return 0


if __name__ == "__main__":
    sys.exit(main())
