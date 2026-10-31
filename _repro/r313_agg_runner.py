# -*- coding: utf-8 -*-
# r313 轮次 2 机械四连跑 + 两轮均值±极差合表（规矩 B：每题各轮、报分布不报点值）。
# 读判据=_repro/r312a/anchor_judge.py（修毕版）；轮次 1 读数从 _repro 机械件现取，不硬编码。
# 臂自报（字节/行）盘上复验：对四臂各算 sha256 前 8 + 字节 + 行，写进表供与收尾消息对账。
import hashlib, importlib.util as u, io, json, os
A = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
s = u.spec_from_file_location("aj", A + "/_repro/r312a/anchor_judge.py")
M = u.module_from_spec(s); s.loader.exec_module(M)
NAMED = {"task2": "(价格|assets)", "task3": "(订单金额|金额|clean)"}
def load(o):
    return json.loads(io.open(o, encoding="utf-8").read())
def disk(p):
    b = io.open(A + "/" + p, "rb").read()
    return dict(bytes=len(b), lines=b.decode("utf-8", "replace").count(chr(10)) + 1, sha8=hashlib.sha256(b).hexdigest()[:8])
# 轮次 1（现取 _repro）
r1 = {}
j2 = load(A + "/_repro/r309a/mech_r310_final.json")
r1[("task2", "X")] = j2["computable"]["X"]; r1[("task2", "Y")] = j2["computable"]["Y"]
r1[("task3", "X")] = load(A + "/_repro/r312a/mech_X3.json"); r1[("task3", "Y")] = load(A + "/_repro/r312a/mech_Y3.json")
# 轮次 2（本轮新跑；缺臂则标 pending 不假 0）
r2 = {}
pend = []
for task, xs, ys in (("task2", "X2b", "Y2b"), ("task3", "X3b", "Y3b")):
    for arm, code in ((xs, "X"), (ys, "Y")):
        pp = "_temp/r313a/out_%s/optimized_prompt.md" % arm
        lp = "_temp/r313a/out_%s/process_log.md" % arm
        if not (os.path.isfile(A + "/" + pp) and os.path.isfile(A + "/" + lp)):
            pend.append(arm); continue
        r2[(task, code)] = M.score_computable(io.open(A + "/" + pp, encoding="utf-8").read(),
                                               io.open(A + "/" + lp, encoding="utf-8").read(),
                                               named_pat=NAMED[task])
        r2[(task, code)]["_disk"] = disk(pp)
K4 = ["item4_first30", "item5_no_fabricated", "item6_scope", "item8_consistent"]
def q(o): return sum(o[k] for k in K4)
print("[ROUND2] 已判=%s 待=%s" % (sorted(set(k[0] + ":" + k[1] for k in r2)), pend or "无"))
for key in sorted(set(list(r1) + list(r2))):
    task, code = key
    a = r1.get(key); b = r2.get(key)
    line = "  %-12s %s" % ("%s/%s" % key, "轮1=" + (str(q(a)) + "/4 i8=" + str(a["item8_consistent"]) + (" fake=" + str(a.get("item8_fake_sections")) if a.get("item8_fake_sections") else "")) if a else "—")
    if b is not None:
        line += " 轮2=" + str(q(b)) + "/4 i8=" + str(b["item8_consistent"]) + (" fake=" + str(b.get("item8_fake_sections")) if b.get("item8_fake_sections") else "")
    print(line)
json.dump({"round1": {"|".join(k): {kk: v.get(kk) for kk in K4 + ["item8_fake_sections", "item4_frac", "item8_support"]} for k, v in r1.items()},
           "round2": {"|".join(k): {kk: v.get(kk) for kk in K4 + ["item8_fake_sections", "item4_frac", "item8_support", "_disk"]} for k, v in r2.items()},
           "pending": pend},
          io.open(A + "/_temp/r313a/round2_mech.json", "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
print("[SAVED] round2_mech.json")
