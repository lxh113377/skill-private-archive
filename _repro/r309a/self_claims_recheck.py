# -*- coding: utf-8 -*-
"""r309 对 Y2 臂自报的**盘上复算**（自述不算证据）：字节/行数、两条铁律各 2 次、
I3 Agentic Warning 是否逐字在、hard_constraints 前置位置、以及「与文档断言的对应」探针。
X2 同表核一遍（两臂同尺）。"""
import io, json
def probe(tag):
    p = io.open("_temp/r309a/out_%s/optimized_prompt.md" % tag, encoding="utf-8").read()
    lg = io.open("_temp/r309a/out_%s/process_log.md" % tag, encoding="utf-8").read()
    b = len(p.encode("utf-8")); lb = len(lg.encode("utf-8"))
    r = {"tag": tag, "prompt_bytes": b, "log_bytes": lb,
         "价各": p.count("价格"), "assets各": p.count("assets"),
         "I3逐字": "scope locks" in p or "scope lock" in p,
         "ToT/MoE正面推荐": ("Tree of Thought" in p and "不" not in p.split("Tree of Thought")[0][-12:]) or ("Mixture of Experts" in p and "不" not in p.split("Mixture of Experts")[0][-12:]),
         "log行数": len([x for x in lg.splitlines() if x.strip() and not x.strip().startswith("#")])}
    return r
out = [probe(t) for t in ("X2", "Y2")]
for r in out:
    print(json.dumps(r, ensure_ascii=False))
# Y2 自报 7566/5051 与 15.9% 的核对
y = [r for r in out if r["tag"] == "Y2"][0]
print("[核对] Y2 自报 prompt=7566 实得=%s | log 自报 5051 实得=%s | 铁律各 2 次：价=%s assets=%s" % (
    y["prompt_bytes"], y["log_bytes"], y["价各"], y["assets各"]))
x = [r for r in out if r["tag"] == "X2"][0]
print("[核对] X2 自报 7209 实得=%s" % x["prompt_bytes"])

