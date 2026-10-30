"""R301C 负向对照两腿（与正式读数共用 fresh_judge.classify）。"""
import io
import json
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OUT)
import fresh_judge as J

d = json.load(io.open(os.path.join(OUT, "fresh_scan.json"), encoding="utf-8"))
pairs = d["pairs"]

cand = None
for p in pairs:
    if p["state"] in ("BEHIND", "CURRENT", "LOCAL_AHEAD") and p["local_last_updated"] and p["upstream_pushed_at"]:
        cand = p
        break
if cand is None:
    print("LEG_A RESULT: FAIL 无同时具备两侧日期的对，取数路径未通")
    print("LEG_B RESULT: FAIL 取数路径未通")
    sys.exit(0)
print("LEG_A_BASE slug=%s repo=%s local_last_updated=%s upstream_pushed_at=%s real_state=%s" % (cand["slug"], cand["repo"], cand["local_last_updated"], cand["upstream_pushed_at"], cand["state"]))
s1 = J.classify(cand["local_last_updated"], "2000-01-01")
print("LEG_A1 in=(local=%s, upstream=%s 人为改旧) out=%s expect=LOCAL_AHEAD %s" % (cand["local_last_updated"], "2000-01-01", s1, "PASS" if s1 == "LOCAL_AHEAD" else "FAIL"))
s2 = J.classify(cand["local_last_updated"], None)
print("LEG_A2 in=(local=%s, upstream=None) out=%s expect=UNKNOWN %s" % (cand["local_last_updated"], s2, "PASS" if s2 == "UNKNOWN" else "FAIL"))
s3 = J.classify(None, cand["upstream_pushed_at"])
print("LEG_A3 in=(local=None, upstream=%s) out=%s expect=UNKNOWN %s" % (cand["upstream_pushed_at"], s3, "PASS" if s3 == "UNKNOWN" else "FAIL"))

real = [p for p in pairs if p["state"] in ("BEHIND", "CURRENT")]
print("LEG_B n_real_nonunknown=%d need>=5" % len(real))
for p in real[:8]:
    print("LEG_B slug=%s repo=%s local_last_updated=%s upstream_pushed_at=%s state=%s cmd=%s" % (p["slug"], p["repo"], p["local_last_updated"], p["upstream_pushed_at"], p["state"], p["evidence_cmd"]))
if len(real) >= 5:
    print("LEG_B RESULT: PASS n=%d" % len(real))
else:
    print("LEG_B RESULT: FAIL 取数路径未通（非 UNKNOWN 少于 5 对）")
a_ok = (s1 == "LOCAL_AHEAD" and s2 == "UNKNOWN" and s3 == "UNKNOWN")
print("LEG_A RESULT: %s" % ("PASS" if a_ok else "FAIL"))