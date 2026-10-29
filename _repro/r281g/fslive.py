#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""列出 fs 两态 d5 live 清单与差集，供 md 逐字引用。"""
import json
import os

ROOT = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
d = json.load(open(os.path.join(ROOT, "06-benchmark", "r281_artifact_ab.json"), encoding="utf-8"))
for e in d["per_skill"]:
    if e["skill"] != "frontend-slides":
        continue
    lb = e["detail_before"]["d5"]["live_list"]
    la = e["detail_after"]["d5"]["live_list"]
    print("BEFORE=" + json.dumps(lb, ensure_ascii=False))
    print("AFTER=" + json.dumps(la, ensure_ascii=False))
    print("ADDED=" + json.dumps([x for x in la if x not in lb], ensure_ascii=False))
    print("REMOVED=" + json.dumps([x for x in lb if x not in la], ensure_ascii=False))
    print("DEAD=" + json.dumps(e["detail_after"]["d5"]["dead_list"], ensure_ascii=False))
    print("D2_LINES=" + json.dumps([e["detail_before"]["d2"], e["detail_after"]["d2"]], ensure_ascii=False))
