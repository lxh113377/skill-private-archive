import json, hashlib, io
W = {"exact":1.0,"usable-suboptimal":0.75,"wrong":0.5,"blindspot":0.4}
P = r"C:/Users/37533/Desktop/workspace/焚诀/eval/layered_testset.json"
raw = open(P,"rb").read()
sha = hashlib.sha256(raw).hexdigest()
print("TESTSET_SHA256_NOW", sha)
print("TESTSET_SHA256_BASELINE", "e1d700258d2b55ad2515df98bd35dd051154b9870222266b0e4852b33c4a0856")
print("SHA_MATCH", sha == "e1d700258d2b55ad2515df98bd35dd051154b9870222266b0e4852b33c4a0856")
ts = json.loads(raw.decode("utf-8"))
all_w = 0.0; n = 0
jp = {}
for g in ts:
    for c in g.get("queries", []):
        n += 1; w = W.get(c.get("judge","exact"), 0.5); all_w += w
        jp.setdefault(g.get("tier"), {"n":0,"w":0.0})
        jp[g["tier"]]["n"] += 1; jp[g["tier"]]["w"] += w
print("FULL_N", n, "FULL_CEILING", round(all_w/n*100,1))
for t,v in jp.items():
    print("TIER", t, "n", v["n"], "ceiling", round(v["w"]/v["n"]*100,1))
# 干净面复算：与 blindset_leak_manifest.json 的 score_clean_only 对齐
lm = json.load(open(r"C:/Users/37533/Desktop/workspace/焚诀/eval/blindset_leak_manifest.json", encoding="utf-8"))
clean = [e for e in lm["entries"] if e["status"]=="CLEAN"]
cw = sum(W[e["judge"]] for e in clean)
cn = len(clean)
print("CLEAN_N", cn, "CLEAN_CEILING_RECOMPUTED", round(cw/cn*100,1), "vs_recorded", lm["score_clean_only"]["pct"])
# 多标签不变性：权重只来自 judge 标签，加多少个 acceptable 都不改分母/分子
print("MULTILABEL_CEILING_INVARIANT", round(all_w/n*100,1), "-> with any-of-N accepted, weights unchanged =>", round(all_w/n*100,1))
print("ROTATION", json.load(open(r"C:/Users/37533/Desktop/workspace/焚诀/eval/blindset_rotation.json", encoding="utf-8")))
bl = json.load(open(r"C:/Users/37533/Desktop/workspace/焚诀/eval/blindset_gate_baseline.json", encoding="utf-8"))
print("BASELINE_VERSION", bl["blindset_version"], "ALLOW_DROP", bl["allow_drop_pp"], "HARDFLOOR", bl["hard_floor_pct"])
# 是否存在的 knob：统计 frozen_blind_eval.py 的 argparse / argv 用法
src = open(r"C:/Users/37533/Desktop/workspace/焚诀/eval/frozen_blind_eval.py", encoding="utf-8").read()
print("HAS_ARGPARSE", "import argparse" in src, "HAS_MULTILABEL_KW", any(k in src for k in ("acceptable","aliases","also_ok","multilabel","labels")))