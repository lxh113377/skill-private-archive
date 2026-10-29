#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R281G 明细导出：把 JSON 的逐维 raw / 死链 / flag 支持集打成一页，供写报告时引用。"""
import json
import os

ROOT = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
p = os.path.join(ROOT, "06-benchmark", "r281_artifact_ab.json")
d = json.load(open(p, encoding="utf-8"))
print("SCHEMA=" + d["schema"] + " MEASURED_AT=" + d["measured_at"] + " PER=" + str(len(d["per_skill"])))
print("TOPKEYS=" + ",".join(d.keys()))
print("EDGES=" + json.dumps(d["rubric_definition"]["EDGES"], ensure_ascii=False))
for e in d["per_skill"]:
    print("@@@ " + e["skill"] + " before_full=" + e["sha_pair"]["before_full"][:12] + " base_sha=" + e["sha_pair"]["baseline_sha"])
    print("  drift=" + json.dumps(e.get("post_baseline_drift"), ensure_ascii=False))
    print("  probe=" + str(e["dim6_probe"]["decidable"]) + " reason=" + e["dim6_probe"]["reason"])
    print("  supported=" + ",".join(e["dim6_probe"]["supported"]))
    print("  cmds=" + json.dumps(e["dim6_probe"]["cmds"], ensure_ascii=False))
    for side in ("before", "after"):
        det = e["detail_" + side]
        print("  [" + side + "] d1=" + json.dumps(det["d1"], ensure_ascii=False))
        print("  [" + side + "] d5live=" + json.dumps(det["d5"]["live_list"], ensure_ascii=False))
        print("  [" + side + "] d5dead=" + json.dumps(det["d5"]["dead_list"], ensure_ascii=False))
        print("  [" + side + "] d5unres=" + json.dumps(det["d5"]["unresolved_list"], ensure_ascii=False))
        print("  [" + side + "] d6raw=" + str(det["d6"]["raw"]) + " flags=" + ",".join(det["d6"]["flags"]) + " bad=" + ",".join(det["d6"]["bad"]))
    print("  raw_before=" + json.dumps(e["raw_before"], ensure_ascii=False))
    print("  raw_after=" + json.dumps(e["raw_after"], ensure_ascii=False))
    print("  dims_before=" + json.dumps(e["dims_before"], ensure_ascii=False))
    print("  dims_after=" + json.dumps(e["dims_after"], ensure_ascii=False))
    print("  delta=" + json.dumps(e["delta"], ensure_ascii=False))
    print("  sums=" + json.dumps([e["sum_before"], e["sum_after"]], ensure_ascii=False) + " uplift=" + str(e["uplift_pct"]))
    print("  uplift_inputs=" + json.dumps(e.get("uplift_inputs"), ensure_ascii=False))
    print("  blind=" + json.dumps(e["blind"], ensure_ascii=False))
    print("  text_sha=" + json.dumps(e.get("text_sha256"), ensure_ascii=False))
print("@@@ SELF_CHECK " + json.dumps(d["self_check"], ensure_ascii=False))
