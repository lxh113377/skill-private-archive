#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读出 JSON 里 ux 那一块与 self_check，供报告逐字引用。"""
import json
import os

ROOT = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
d = json.load(open(os.path.join(ROOT, "06-benchmark", "r281_artifact_ab.json"), encoding="utf-8"))
for e in d["per_skill"]:
    if e["skill"] != "ui-ux-pro-max":
        continue
    keys = ["raw_before", "raw_after", "dims_before", "dims_after", "delta", "uplift_pct",
            "uplift_inputs", "blind", "decidable_dims", "excluded_dims", "text_sha256"]
    print(json.dumps(dict((k, e[k]) for k in keys), ensure_ascii=False, indent=1))
print("SELF_CHECK=" + json.dumps(d["self_check"], ensure_ascii=False))
print("MEASURED_AT=" + d["measured_at"])
