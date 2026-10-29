#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""终检：schema 键齐全 + 36 格 + 每件 live/dead/unresolved 计数，供与 md 逐字对账。"""
import json
import os

ROOT = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
d = json.load(open(os.path.join(ROOT, "06-benchmark", "r281_artifact_ab.json"), encoding="utf-8"))
need = ["schema", "rubric_definition", "per_skill", "caliber_note", "blind_procedure", "measured_at", "provenance_cmd"]
print("TOP_MISSING=" + ",".join(k for k in need if k not in d))
print("SCHEMA=" + d["schema"] + " PER=" + str(len(d["per_skill"])) + " MEASURED_AT=" + d["measured_at"])
cells = 0
nulls = 0
for e in d["per_skill"]:
    for k in ["sha_pair", "dims_before", "dims_after", "delta", "uplift_pct"]:
        if k not in e:
            print("MISSING " + e["skill"] + " " + k)
    for side in ("before", "after"):
        det = e["detail_" + side]
        for dm in ("d1", "d2", "d3", "d4", "d5", "d6"):
            cells += 1
            if e["dims_" + side][dm] is None:
                nulls += 1
        s5 = det["d5"]
        print("  " + e["skill"] + "/" + side + " live=" + str(s5["live_n"]) + " dead=" + str(s5["dead_n"]) + " unres=" + str(s5["unresolved_n"]) + " raw=" + str(s5["raw"]))
print("CELLS=" + str(cells) + " NULL_CELLS=" + str(nulls))
print("SUM_BEFORE=" + ",".join(str(e["sum_before"]) for e in d["per_skill"]))
print("SUM_AFTER=" + ",".join(str(e["sum_after"]) for e in d["per_skill"]))
print("UPLIFT=" + ",".join(str(e["uplift_pct"]) for e in d["per_skill"]))
print("LASTLINE=" + d["self_check"]["last_line"])
