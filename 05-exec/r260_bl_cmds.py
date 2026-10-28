import json, collections, statistics
d = json.load(open("06-benchmark/r260_local_baseline.json", encoding="utf-8"))
rows = [x for x in d["rows"] if not str(x["slug"]).startswith("r260-")]
print("non-selftest rows", len(rows))
lc = collections.Counter(); 
for dim in ("fc","eff","compat","docs","community"):
    lc[dim] = dict(collections.Counter(x["local"]["score5"][dim] for x in rows))
print("LOCAL DIM HIST", json.dumps(lc, ensure_ascii=False))
tot = [x["local"]["score_total"] for x in rows]
print("local total median/mean/range", statistics.median(tot), round(sum(tot)/len(tot),2), min(tot), max(tot))
hist = dict(sorted(collections.Counter(x["delta_cmp4"] for x in rows).items(), key=lambda kv: (kv[0] is None, kv[0])))
print("DELTA HIST", hist)
print("delta mean", round(sum(x["delta_cmp4"] for x in rows if x["delta_cmp4"] is not None)/len(rows),2))
rel = collections.Counter(x.get("rank0_rel") for x in rows)
print("rank0_rel", dict(rel))
for want in ("skill","family"):
    vs = [x["delta_cmp4"] for x in rows if x.get("rank0_rel")==want and x["delta_cmp4"] is not None]
    print(want, len(vs), round(sum(vs)/len(vs),2) if vs else None)
ct = d["compat_teeth"]
print("ENTROPY", ct.get("entropy_bits"))
print("RANK_FLIP", json.dumps(ct.get("rank_flip"), ensure_ascii=False)[:420])
print("SATURATION", json.dumps(ct.get("subleg_saturation"), ensure_ascii=False)[:300])
print("BELOWMAX", json.dumps(ct.get("below_max_cause"), ensure_ascii=False)[:260])
print("VARIES", ct.get("rows_where_compat_varies_among_candidates"))
print("DISTRIBUTION", json.dumps(ct.get("dim_distribution_in_matrix"), ensure_ascii=False)[:260])