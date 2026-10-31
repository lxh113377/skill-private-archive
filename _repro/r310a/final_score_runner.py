# -*- coding: utf-8 -*-
"""r310 合判执行：机械判据（item8 补强后）对双臂终判。manual 键=judge 的 X/Y（映射文件 X=before_130）。
人判四项两方（C 臂与我方 B1 重试臂）都是 4/4 同分 ⇒ 取共同读数。"""
import json, subprocess, sys, io, os
PY = sys.executable
B = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_temp/r309a"
manual = {"X": {"1": 1, "2": 1, "3": 1, "7": 1}, "Y": {"1": 1, "2": 1, "3": 1, "7": 1}}
cmd = [PY, "-B", os.path.join(B, "anchor_judge.py"),
       "--x-prompt", os.path.join(B, "out_X2/optimized_prompt.md"), "--x-log", os.path.join(B, "out_X2/process_log.md"),
       "--y-prompt", os.path.join(B, "out_Y2/optimized_prompt.md"), "--y-log", os.path.join(B, "out_Y2/process_log.md"),
       "--manual", json.dumps(manual), "--json", os.path.join(B, "mech_r310_final.json")]
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
print("[FINAL rc=%d]" % r.returncode)
for l in (r.stdout or "").strip().splitlines():
    print("  " + l[:168])
if (r.stderr or "").strip():
    print("  ERR:", r.stderr.strip().splitlines()[-1][:150])
d = json.load(io.open(B + "/mech_r310_final.json", encoding="utf-8"))
for side in ("X", "Y"):
    s = d.get("computable", {}).get(side) or d.get(side) or {}
    print("  %s fake_sections=%s item8=%s" % (side, s.get("item8_fake_sections"), s.get("item8_consistent")))

