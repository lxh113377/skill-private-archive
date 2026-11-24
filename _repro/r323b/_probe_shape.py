import json, statistics
ts = json.load(open(r"C:/Users/37533/Desktop/workspace/焚诀/eval/layered_testset.json", encoding="utf-8"))
qs = []
for g in ts:
    for c in g.get("queries", []):
        qs.append((g.get("tier"), c.get("query"), len(c.get("query") or "")))
L = [x[2] for x in qs]
print("N", len(L), "MEAN", round(statistics.mean(L),1), "MEDIAN", statistics.median(L), "MIN", min(L), "MAX", max(L))
for thr in (30, 60, 100, 200):
    print("LEN_GT", thr, sum(1 for v in L if v > thr), "pct", round(sum(1 for v in L if v>thr)/len(L)*100,1))
by = {}
for t, q, n in qs:
    by.setdefault(t, []).append(n)
for t, v in by.items():
    print("TIER_LEN", t, "n", len(v), "mean", round(statistics.mean(v),1), "max", max(v))
print("LONGEST_SAMPLE", max(qs, key=lambda x: x[2])[1][:160])
print("SHORTEST_SAMPLE", min(qs, key=lambda x: x[2])[1])