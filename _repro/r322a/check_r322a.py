# -*- coding: utf-8 -*-
"""r322a 自证：断言 verdict.json 的守恒与枚举，三负控证明判据有牙（内存注入）。"""
import copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(HERE, "verdict.json")
ENUM = {"NESTED_IS_ENTRY", "NESTED_NOT_ENTRY", "MIXED", "UNVERIFIED"}


def run(d):
    errs = []
    if d["verdict"] not in ENUM:
        errs.append("verdict 枚举外: " + str(d["verdict"]))
    t = d["totals"]
    if t["top_level"] + t["nested"] != t["skill_md_all"]:
        errs.append("totals 守恒破")
    for row in d["fake_orphan_by_skill"]:
        if row["covered_by_nested"] + row["true_orphan"] != row["orphans"]:
            errs.append("fake_orphan 守恒破: " + row["slug"])
    if not d.get("loader_fact"):
        errs.append("loader_fact 空")
    return errs


def main():
    d = json.load(open(V, encoding="utf-8"))
    errs = run(d)
    neg = os.environ.get("R322A_NEG")
    if neg == "enum":
        d2 = copy.deepcopy(d); d2["verdict"] = "DONE"
        errs = run(d2)
        print("[R322A:NEG] enum teeth=" + ("pass" if errs else "FAIL"))
        return 0 if errs else 1
    if neg == "conserve":
        d2 = copy.deepcopy(d); d2["fake_orphan_by_skill"][0]["true_orphan"] += 1
        errs = run(d2)
        print("[R322A:NEG] conserve teeth=" + ("pass" if errs else "FAIL"))
        return 0 if errs else 1
    if neg == "loader":
        d2 = copy.deepcopy(d); d2["loader_fact"] = ""
        errs = run(d2)
        print("[R322A:NEG] loader teeth=" + ("pass" if errs else "FAIL"))
        return 0 if errs else 1
    for e in errs:
        print("FAIL " + e)
    n_fake = sum(r["covered_by_nested"] for r in d["fake_orphan_by_skill"])
    if errs:
        print("[R322A:CLOSURE] verdict=%s fake_orphans=%d teeth=FAIL" % (d["verdict"], n_fake))
        return 1
    print("[R322A:CLOSURE] verdict=%s fake_orphans=%d teeth=pass" % (d["verdict"], n_fake))
    return 0


if __name__ == "__main__":
    sys.exit(main())
