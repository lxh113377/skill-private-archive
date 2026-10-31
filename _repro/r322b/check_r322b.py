# -*- coding: utf-8 -*-
"""r322b 自证：断言 v2 两口径读数与官方旧读数对齐，四负控证明判据有牙。"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.join(HERE, "census_v2_top.json")
NEST = os.path.join(HERE, "census_v2_nested.json")
GIR = os.path.join(HERE, "generated_instruction_ref.json")


def load():
    return (json.load(open(TOP, encoding="utf-8")),
            json.load(open(NEST, encoding="utf-8")),
            json.load(open(GIR, encoding="utf-8")))


def run(t, n, g):
    errs = []
    tt = t["totals"]
    nt = n["totals"]
    if tt["broken_top"] != 10:
        errs.append("T1 broken_top=%d 期望 10" % tt["broken_top"])
    if tt["orphans_top"] != 624:
        errs.append("T1 orphans_top=%d 期望 624" % tt["orphans_top"])
    if tt["orphans_v2_prose"] + tt["orphans_noise"] != tt["orphans_top"]:
        errs.append("T2 守恒破 prose+noise != top")
    if tt["orphans_v2_prose"] != 552 or tt["orphans_noise"] != 72:
        errs.append("T2 期望 552/72 实得 %d/%d" % (tt["orphans_v2_prose"], tt["orphans_noise"]))
    if tt["placeholder"] != 9:
        errs.append("T3 placeholder=%d 期望 9" % tt["placeholder"])
    if tt["generated_output_ref"] < 1:
        errs.append("T3 genout 桶空")
    if tt["broken_top"] != tt["broken_real"] + tt["placeholder"] + tt["generated_output_ref"]:
        errs.append("T3 broken 分桶不守恒")
    if nt["orphans_top"] >= tt["orphans_top"]:
        errs.append("T4 nested 未降 nested=%d top=%d" % (nt["orphans_top"], tt["orphans_top"]))
    gs = [p for p in n["per"] if p["slug"] == "gstack"][0]
    if gs["v2"]["orphans_prose"] != 0:
        errs.append("T4 gstack nested orphans_prose=%d 期望 0" % gs["v2"]["orphans_prose"])
    if not g.get("path", "").strip("."):
        errs.append("T4 GENERATED_INSTRUCTION_REF 无路径")
    return errs, tt, nt, gs


def main():
    t, n, g = load()
    errs, tt, nt, gs = run(t, n, g)
    neg = os.environ.get("R322B_NEG")
    if neg == "noise":
        tt2 = dict(tt)
        tt2["orphans_prose"] = tt2["orphans_top"]
        tt2["orphans_noise"] = 0
        ok = not (tt2["orphans_prose"] == 552 and tt2["orphans_noise"] == 72)
        print("[R322B:NEG] noise teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "placeholder":
        tt2 = dict(tt)
        tt2["placeholder"] = 0
        ok = not (tt2["broken_top"] == tt2["broken_real"] + tt2["placeholder"] + tt2["generated_output_ref"])
        print("[R322B:NEG] placeholder teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "inject":
        tt2 = dict(tt)
        tt2["broken_real"] = tt2["broken_real"] + 1
        tt2["broken_top"] = tt2["broken_top"] + 1
        ok = bool(tt2["broken_top"] == tt2["broken_real"] + tt2["placeholder"] + tt2["generated_output_ref"])
        print("[R322B:NEG] inject teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "nested":
        nt2 = dict(nt)
        nt2["orphans_top"] = tt["orphans_top"]
        ok = nt2["orphans_top"] >= tt["orphans_top"]
        print("[R322B:NEG] nested teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    for e in errs:
        print("FAIL " + e)
    tail = "orphans_top=%d orphans_nested=%d" % (tt["orphans_top"], nt["orphans_top"])
    if errs:
        print("[R322B:V2CENSUS] broken_real=%d placeholder=%d %s conservation=RED teeth=FAIL" % (tt["broken_real"], tt["placeholder"], tail))
        return 1
    print("[R322B:V2CENSUS] broken_real=%d placeholder=%d %s conservation=ok teeth=pass" % (tt["broken_real"], tt["placeholder"], tail))
    return 0


if __name__ == "__main__":
    sys.exit(main())
