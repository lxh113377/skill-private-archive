import json, collections, re, io
d = json.load(open("06-benchmark/r260_local_baseline.json", encoding="utf-8"))
rows = [x for x in d["rows"] if not str(x["slug"]).startswith("r260-")]
ct = d["compat_teeth"]
print("share_at_max compat", ct["dim_distribution_in_matrix"]["compat"]["share_at_max"])
print("below_max", ct["below_max_cause"])
print("copleft_at_5", json.dumps(ct.get("copleft_at_5"), ensure_ascii=False)[:300])
# rank0 位上是 copyleft 的行：逐行看 rank0_license
CL = ("AGPL", "GPL", "LGPL", "CC-BY-SA")
cop = [(x["slug"], x.get("rank0_repo"), x.get("rank0_license")) for x in rows
       if any(k in str(x.get("rank0_license") or "").upper() for k in CL)]
print("copyleft rank0 rows", len(cop))
for c in cop: print("   ", c)
fam13 = [x["slug"] for x in rows if x.get("rank0_rel") == "family"]
print("family-rel rows", len(fam13))
lic5 = sum(1 for x in rows if x["local"]["score5"]["compat"] == 5)
print("local compat=5 (有 LICENSE 类文件)", lic5)
# 指纹表家族数：从脚本源码里读表
src = io.open("05-exec/r260_local_baseline.py", encoding="utf-8").read()
m = re.search(r"LICENSE_FINGERPRINTS\s*=\s*\{", src)
print("fingerprint table anchor found", bool(m))