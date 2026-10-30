"""R301C 判定脚本：读 fresh_scan.json，末行输出固定六字段读数。sampled = 成功取回并解析的上游样本数。"""
import collections
import io
import json
import os

d = json.load(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fresh_scan.json"), encoding="utf-8"))
pairs = d["pairs"]
c = collections.Counter(p["state"] for p in pairs)
sampled = sum(1 for s in d["samples"] if s.get("sampled_state") == "VERIFIED")
att = len(d["samples"])
print("pairs=%d behind=%d current=%d local_ahead=%d unknown=%d sampled_attempted=%d" % (len(pairs), c["BEHIND"], c["CURRENT"], c["LOCAL_AHEAD"], c["UNKNOWN"], att))
print("[R301C:FRESH] pairs=%d behind=%d current=%d local_ahead=%d unknown=%d sampled=%d" % (len(pairs), c["BEHIND"], c["CURRENT"], c["LOCAL_AHEAD"], c["UNKNOWN"], sampled))