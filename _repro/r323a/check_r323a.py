# -*- coding: utf-8 -*-
"""r323a 自证（Lead 补写：A 臂只交 2 件、漏 check_r323a.py）。

为什么判据必须独立：gate_result.json 是**被判对象**，若判据只读它内部的 ok 字段就是自证自话。
所以这里做三件事：① 从 gate_result 的结构现算守恒（不读它的 ok）；② 用 git 现核每个 CLEAN 件真的 porcelain 空；
③ 三负控证明判据有牙（内存注入 DIRTY 进 can_land / 造 unknown slug / 改总数）。
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, "gate_result.json")
GIT = r"C:/Program Files/Git/bin/git.exe"
ROOT = r"D:/global_skills"


def porcelain(path):
    """现核：真实 porcelain 输出。判据不信 gate_result 里的 rows，自己再跑一次 git。"""
    try:
        r = subprocess.run([GIT, "-c", "core.quotepath=false", "-C", ROOT,
                            "status", "--porcelain", "--", path],
                           capture_output=True, text=True, encoding="utf-8", timeout=120)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return (r.stdout or "").strip()


def run(d, live=True):
    errs = []
    items = d.get("items") or {}
    can, blk, unk = d.get("can_land") or [], d.get("blocked") or [], d.get("unknown") or []
    n = len(d.get("targets") or [])
    # 1 守恒：三态之和 == targets（现算，不读 d["counts"]）
    if len(can) + len(blk) + len(unk) != n:
        errs.append("守恒破: can=%d blk=%d unk=%d != targets=%d" % (len(can), len(blk), len(unk), n))
    # 2 互斥：一个 slug 不得同时出现在 can 与 blk
    cs, bs, us = set(x["slug"] for x in can), set(x["slug"] for x in blk), set(x["slug"] for x in unk)
    if cs & bs or cs & us or bs & us:
        errs.append("互斥破: 同件落在两态 %s" % ((cs & bs) or (cs & us) or (bs & us)))
    # 3 blocked 每件必须具名脏标记
    for b in blk:
        if not (b.get("markers") or []):
            errs.append("blocked 无脏标记: " + b["slug"])
    # 4 live：CLEAN 件的真实 porcelain 必须为空（判据自己跑 git，不看 gate_result）
    if live:
        for c in can:
            p = porcelain(c["path"])
            if p is None:
                errs.append("git 读不到: " + c["path"])
            elif p != "":
                errs.append("假 CLEAN: %s 实际 porcelain=%r" % (c["slug"], p[:60]))
    return errs, n, len(can), len(blk), len(unk)


def main():
    d = json.load(open(G, encoding="utf-8"))
    neg = os.environ.get("R323A_NEG")
    if neg == "dirty_in_can":
        # 负控 a：把 DIRTY 件塞进 can_land ⇒ 守恒破（它同时仍在 blocked）
        import copy
        d2 = copy.deepcopy(d)
        if d2["blocked"]:
            d2["can_land"].append({"slug": d2["blocked"][0]["slug"], "path": d2["blocked"][0]["path"]})
        errs, *_ = run(d2, live=False)
        ok = bool(errs)
        print("[R323A:NEG] dirty_in_can teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "ghost":
        # 负控 b：造一个 unknown slug 又同时塞进 can ⇒ 互斥破
        import copy
        d2 = copy.deepcopy(d)
        d2["can_land"].append({"slug": "ghost-skill", "path": "ghost-skill/SKILL.md"})
        d2["unknown"].append({"slug": "ghost-skill", "path": "ghost-skill/SKILL.md"})
        errs, *_ = run(d2, live=False)
        ok = bool(errs)
        print("[R323A:NEG] ghost teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "count":
        # 负控 c：把 targets 砍掉一件 ⇒ 守恒破
        import copy
        d2 = copy.deepcopy(d)
        d2["targets"] = d2["targets"][:-1]
        errs, *_ = run(d2, live=False)
        ok = bool(errs)
        print("[R323A:NEG] count teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    errs, n, nc, nb, nu = run(d)
    for e in errs:
        print("FAIL " + e)
    if errs:
        print("[R323A:GL1] targets=%d clean=%d dirty=%d unk=%d gate=RED teeth=FAIL" % (n, nc, nb, nu))
        return 1
    print("[R323A:GL1] targets=%d clean=%d dirty=%d gate=ok teeth=pass" % (n, nc, nb))
    return 0


if __name__ == "__main__":
    sys.exit(main())
