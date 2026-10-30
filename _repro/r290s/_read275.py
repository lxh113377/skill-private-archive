# -*- coding: utf-8 -*-
"""现读 r275 两件面件的 security-audit 行（字段名先 print sorted(keys) 再引用，禁猜）。"""
import io, json, os
B = "06-benchmark"
for name in ("r275_different_impl_triage.json", "r275_three_channel_intersection.json"):
    d = json.load(io.open(os.path.join(B, name), encoding="utf-8"))
    print("== %s rows=%d" % (name, len(d["rows"])))
    print("   row0 keys:", sorted(d["rows"][0].keys()))
    for r in d["rows"]:
        if r.get("skill") == "security-audit":
            print("   HIT keys:", sorted(r.keys()))
            print("   HIT:", json.dumps(r, ensure_ascii=False)[:1200])
    else:
        pass
print("triage skills:", [r["skill"] for r in json.load(io.open(os.path.join(B, "r275_different_impl_triage.json"), encoding="utf-8"))["rows"]])
