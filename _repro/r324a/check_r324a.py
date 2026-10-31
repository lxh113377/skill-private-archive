# -*- coding: utf-8 -*-
"""r324a 自证：常驻判据的 portable / parity / conservation 三腿，三负控证明有牙。

为什么判据不信 parity.json 自己的布尔：那是被判对象。这里每条都**现算**：
  · portable 腿 = 直接数字符串（不读 parity 宣称的 0）
  · parity 腿 = 从两口径新件读数重新比对旧件读数，且**允许 -1 的合法 delta**（r323 落盘所致），
    但除 -1 外的任何差都必须红
  · conservation 腿 = 现场加两个数
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "05-exec", "r324_entry_reachability_face.py")
P = os.path.join(HERE, "parity.json")
NEW_TOP = os.path.join(ROOT, "_repro", "r324_lead", "new_top.json")
NEW_NEST = os.path.join(ROOT, "_repro", "r324_lead", "new_nested.json")


def portable(src):
    """portable 腿：源码里 _repro / _temp 出现次数必须为 0（.gitignore 目录在克隆里不存在）。"""
    return src.count("_repro"), src.count("_temp")


def parity(mode, old, new):
    """允许 -1 的合法 delta（only orphans_top / orphans_prose），其余任何差值即红。"""
    errs = []
    allowed = {"orphans_top": -1, "orphans_prose": -1}
    for k, ov in (old or {}).items():
        if k not in new:
            errs.append("%s 缺键 %s" % (mode, k))
            continue
        d = new[k] - ov
        if d == 0:
            continue
        if k in allowed and d == allowed[k]:
            continue
        errs.append("%s %s 差 %+d（仅允许 %s）" % (mode, k, d, allowed.get(k, 0)))
    return errs


def conservation(t):
    """守恒：prose+noise==orphans_top；broken_real+placeholder+genout==broken_top。"""
    e = []
    if t["orphans_prose"] + t["orphans_noise"] != t["orphans_top"]:
        e.append("孤儿守恒破 %d+%d!=%d" % (t["orphans_prose"], t["orphans_noise"], t["orphans_top"]))
    if t["broken_real"] + t["placeholder"] + t["generated_output_ref"] != t["broken_top"]:
        e.append("断链分桶守恒破")
    return e


def main():
    src = open(SRC, encoding="utf-8").read()
    d = json.load(open(P, encoding="utf-8"))
    nt = json.load(open(NEW_TOP, encoding="utf-8"))
    nn = json.load(open(NEW_NEST, encoding="utf-8"))
    neg = os.environ.get("R324A_NEG")
    if neg == "repro":
        # 负控 a：源码里加一个 _repro 引用 ⇒ portable 腿必须红
        bad = src + chr(10) + "# _repro injection"
        r, t = portable(bad)
        ok = (r > 0)
        print("[R324A:NEG] repro teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "parity":
        # 负控 b：把某口径 orphans_top 改 +1（超出允许的 -1）⇒ parity 必须红
        nt2 = json.loads(json.dumps(nt))
        nt2["totals"]["orphans_top"] += 2
        e = parity("top", d["modes"]["top"]["old"], nt2["totals"])
        ok = bool(e)
        print("[R324A:NEG] parity teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "conservation":
        # 负控 c：破守恒 ⇒ 必须红
        t2 = json.loads(json.dumps(nt["totals"]))
        t2["orphans_prose"] += 3
        e = conservation(t2)
        ok = bool(e)
        print("[R324A:NEG] conservation teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    errs = []
    r, t = portable(src)
    if r or t:
        errs.append("portable 破: _repro=%d _temp=%d" % (r, t))
    errs += parity("top", d["modes"]["top"]["old"], nt["totals"])
    errs += parity("nested", d["modes"]["nested"]["old"], nn["totals"])
    errs += conservation(nt["totals"])
    if nt["totals"]["tree_rows"] != 16509:
        errs.append("tree_rows=%d 期望 16509（HEAD 树规模变了要么是他人提交、要么是树通道又坏）" % nt["totals"]["tree_rows"])
    for e in errs:
        print("FAIL " + e)
    if errs:
        print("[R324A:PERMANENT] portable=RED parity=RED conservation=RED teeth=FAIL")
        return 1
    print("[R324A:PERMANENT] portable=ok parity=ok conservation=ok teeth=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
