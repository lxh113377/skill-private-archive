# -*- coding: utf-8 -*-
# r317 #3：判据双形态重跑对账——先量差距，不动尺（r316 立的「先对账再动尺」）。
# 现状：SECTOK 只认尖括号 <name> ⇒ 臂若用 ## 标题形态段名（Y2d 实抓），其「声称」在 item8 里是盲区。
import importlib.util as u, io, json, os, re
A = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
s = u.spec_from_file_location("aj", A + "/_repro/r312a/anchor_judge.py")
M = u.module_from_spec(s); s.loader.exec_module(M)
def dual_cell(pp, lp):
    p = io.open(A + "/" + pp, encoding="utf-8").read()
    g = io.open(A + "/" + lp, encoding="utf-8").read()
    base = M.score_computable(p, g)
    mentions = sorted(set(re.findall(r"<([a-z][a-z_]{2,19})>", g)))
    rescued = []
    for tag in base["item8_fake_sections"]:
        # 该段名不在 prompt 的尖括号形态里 ⇒ 现形判 fake；查它是否以「## 标题」形态存在于 prompt
        if re.search(r"^\s*#{1,4}\s*<?" + tag + ">?\s*($|[：:])", p, re.M) or re.search(r"^\s*#{1,4}\s*" + tag.replace("_", "[ _]") + r"\b", p, re.M):
            rescued.append(tag)
    return dict(cur_fake=base["item8_fake_sections"], i8=base["item8_consistent"], would_be_rescued=rescued, log_mentions=len(mentions))
CELLS = [
 ("task2|r1|X", "_repro/r309a/out_X2/"), ("task2|r1|Y", "_repro/r309a/out_Y2/"),
 ("task3|r1|X", "_repro/r312a/out_X3/"), ("task3|r1|Y", "_repro/r312a/out_Y3/"),
 ("task2|r2|X", "_repro/r313a/out_R2/out_X2b__"), ("task2|r2|Y", "_repro/r313a/out_R2/out_Y2b__"),
 ("task3|r2|X", "_repro/r313a/out_R2/out_X3b__"), ("task3|r2|Y", "_repro/r313a/out_R2/out_Y3b__"),
 ("task2|r3|X", "_repro/r314a/out_R3/out_X2c__"), ("task2|r3|Y", "_repro/r314a/out_R3/out_Y2c__"),
 ("task3|r3|X", "_repro/r314a/out_R3/out_X3c__"), ("task3|r3|Y", "_repro/r314a/out_R3/out_Y3c__"),
 ("task2|r4|X", "_repro/r316a/out_R4/out_X2d__"), ("task2|r4|Y", "_repro/r316a/out_R4/out_Y2d__"),
 ("task3|r4|X", "_repro/r316a/out_R4/out_X3d__"), ("task3|r4|Y", "_repro/r316a/out_R4/out_Y3d__"),
]
out = {}
print("[DUAL-FORM AUDIT] 16 格双形态对账（不动尺，只量差）：")
for name, base in CELLS:
    pp = base + ("optimized_prompt.md" if base.endswith("/") else "optimized_prompt.md")
    lp = base + ("process_log.md" if base.endswith("/") else "process_log.md")
    if not os.path.isfile(A + "/" + pp):
        print("   %-12s 缺文件" % name); continue
    d = dual_cell(pp, lp)
    out[name] = d
    flag = ""
    if d["would_be_rescued"]:
        flag = " ⇒ 标题形态救回 %s（现形假红）" % d["would_be_rescued"]
    elif d["cur_fake"]:
        flag = " ⇒ 两形态都缺=真捏造"
    print("   %-12s 现fake=%-22s%s" % (name, str(d["cur_fake"]), flag))
red = [k for k, v in out.items() if v["would_be_rescued"]]
print("[DUAL:SUMMARY] 会救回格=%d（%s）；一致格=%d；含标题形态 log 的格=%d" % (
    len(red), ",".join(red) or "无", len(out) - len(red),
    sum(1 for v in out.values() if v["log_mentions"])))
json.dump(out, io.open(A + "/_temp/r317_dualform.json", "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)

