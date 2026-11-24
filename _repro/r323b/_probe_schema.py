import json, collections, sys
P = r"C:/Users/37533/Desktop/workspace/焚诀/eval/layered_testset.json"
ts = json.load(open(P, encoding="utf-8"))
print("TOPLEVEL_TYPE", type(ts).__name__, "len", len(ts))
print("TIER_KEYS", [list(g.keys()) for g in ts][:3])
fields = collections.Counter()
accum = collections.Counter()
judges = collections.Counter()
exp_types = collections.Counter()
listval = []
nq = 0
for g in ts:
    fields.update(g.keys())
    for c in g.get("queries", []):
        nq += 1
        accum.update(c.keys())
        judges[c.get("judge", "<absent>")] += 1
        e = c.get("expected_skill", "<absent>")
        exp_types[type(e).__name__] += 1
        if isinstance(e, list): listval.append((g.get("tier"), c.get("query"), e))
print("N_QUERIES", nq)
print("GROUP_FIELDS", dict(fields))
print("QUERY_FIELDS", dict(accum))
print("JUDGE_DIST", dict(judges))
print("EXPECTED_TYPE_DIST", dict(exp_types))
print("LIST_VALUED_EXPECTED", len(listval))
W = {"exact":1.0,"usable-suboptimal":0.75,"wrong":0.5,"blindspot":0.4}
sumw = 0.0
for g in ts:
    for c in g.get("queries", []):
        sumw += W.get(c.get("judge","exact"), 0.5)
print("MAX_ACHIEVABLE_NOW", round(sumw/nq*100,1), "total_w", round(sumw,3), "n", nq)
# 多标签候选：若一条 query 允许多个 acceptable skill，上限不变（权重相同），只是命中更容易
print("SAMPLE_FIRST", json.dumps(ts[0]["queries"][0], ensure_ascii=False))
for g in ts:
    if g.get("tier") and any(k for k in ("short","cli","fault","negative","skills") if k in str(g.get("tier"))):
        print("SAMPLE_TIER", g.get("tier"), json.dumps(g["queries"][0], ensure_ascii=False))
        break
for g in ts:
    for c in g.get("queries", []):
        if c.get("judge") != "exact":
            print("SAMPLE_NONEXACT", g.get("tier"), json.dumps(c, ensure_ascii=False))
            break
    else:
        continue
    break