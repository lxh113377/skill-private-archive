# -*- coding: utf-8 -*-
# r199_workers_fixtures.py - fixtures for the Workers quota reader (W-47 both directions).
#
# The load-bearing invariant: an absent or malformed payload must never be read as zero usage.
# MEASURED 0 and UNVERIFIED must stay distinguishable, otherwise a credential/scope outage would
# look like "you are well inside your quota" - the exact false-green this whole round is about.
import importlib.util as _u
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TARGET = os.path.join(HERE, "r199_workers_face.py")
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-56s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load():
    spec = _u.spec_from_file_location("wf", TARGET)
    mod = _u.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    if not os.path.isfile(TARGET):
        ck("t0 module exists", False, TARGET)
        print("[GATE:fixture-fail]")
        return 1
    m = load()

    good = {"data": {"viewer": {"accounts": [
        {"workersInvocationsAdaptive": [{"sum": {"requests": 42}}]},
        {"workersInvocationsAdaptive": [{"sum": {"requests": 8}}]}]}}}
    ck("t1 sums across accounts", m.sum_invocations(good) == 50, m.sum_invocations(good))

    empty = {"data": {"viewer": {"accounts": [{"workersInvocationsAdaptive": []}]}}}
    ck("t2 genuine zero stays 0 (MEASURED), not None", m.sum_invocations(empty) == 0,
       m.sum_invocations(empty))

    ck("t3 requests 缺失（只剩 errors）=> None，不得把不完整结构当 0",
       m.sum_invocations({"data": {"viewer": {"accounts": [
           {"workersInvocationsAdaptive": [{"sum": {"errors": 3}}]}]}}}) is None)

    # the four anti-false-green shapes must all be None, never 0
    shapes = [
        ("no data key", {"errors": [{"message": "boom"}]}),
        ("accounts null", {"data": {"viewer": {"accounts": None}}}),
        ("accounts empty list", {"data": {"viewer": {"accounts": []}}}),
        ("dataset key absent", {"data": {"viewer": {"accounts": [{}]}}}),
        ("sum not int", {"data": {"viewer": {"accounts": [
            {"workersInvocationsAdaptive": [{"sum": {"requests": "NaN"}}]}]}}}),
        ("sum is bool", {"data": {"viewer": {"accounts": [
            {"workersInvocationsAdaptive": [{"sum": {"requests": True}}]}]}}}),
    ]
    bad = []
    for label, doc in shapes:
        v = m.sum_invocations(doc)
        if v is not None:
            bad.append((label, v))
    ck("t4 six malformed shapes => None (never read as zero usage)", not bad, bad[:3])

    ck("t5 classify_err flags scope outages explicitly",
       "scope" in m.classify_err({"errors": [{"message": "Could not access resource"}]}),
       m.classify_err({"errors": [{"message": "Could not access resource"}]}))
    ck("t6 no errors => empty string (not a false gap)", m.classify_err({"data": {}}) == "")

    a, b = m.month_window()
    ck("t7 window starts on day one and ends tomorrow 00:00Z",
       a.endswith("-01T00:00:00.000Z") and b.endswith("T00:00:00.000Z") and a < b, (a, b))

    tok, src_path = m.oauth_token()
    ck("t8 token readable from a real credential path (r198 said it could not be found)",
       bool(tok) and "xdg" in src_path, ("len=%d" % len(tok), src_path))

    fails = [r for r in RESULTS if not r[0]]
    print("")
    print("夹具合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    print("[GATE:fixture-fail]" if fails else "[GATE:fixture-pass]")
    return 1 if fails else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
