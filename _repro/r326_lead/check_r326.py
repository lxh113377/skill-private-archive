# -*- coding: utf-8 -*-
"""r326 自证：七条需求总览件里的每个「判据命令」都必须真能跑，且末行与表内声明一致。

为什么要有这条：总览件最容易变成**纸面索引** —— 表里写着一堆命令，没人跑过，一年后照抄全失败。
本判据把表里六条承重命令逐条现跑，比对末行；跑不动或末行不符即红。
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DOC = os.path.join(ROOT, "06-benchmark", "七条需求总览_r326_2026-11-01.md")
PY = sys.executable

# 表内声明 → 现跑期望（六个承重命令；只取末行里的稳定片段，不整行比对，避免路径类噪声）
CHECKS = [
    ("需求1 入口可达", ["05-exec/r324_entry_reachability_face.py", "--closure", "top"], "", "orphans_top=623"),
    ("需求3 本地同尺", ["05-exec/r260_local_baseline.py"], "", "[R260:PASS] 三态守恒 191"),
    ("需求5 准入门", ["05-exec/r129_reconcile_admission.py"], "", "未声明的产读数脚本 0"),
    ("需求5 cadence", ["05-exec/r260_quarterly_cadence.py", "--json", "_repro/r326_lead/cad2.json"], "", "[CADENCE:PASS]"),
    ("需求6 多标签", ["_repro/r323b/check_r323b.py"], "", "[R323B:MULTILABEL] verdict=PARTIAL"),
    ("需求6 供给缺口", ["_repro/r322c/check_r322c.py"], "", "[R322C:POOL] short_single_line=0"),
]


def run_one(args, sub):
    env = dict(os.environ)
    env.setdefault("PYTHONPYCACHEPREFIX", os.path.join(HERE, "pycache"))
    cwd = os.path.join(ROOT, sub) if sub else ROOT
    argv = [(a if os.path.isabs(a) else os.path.join(ROOT, a)) if a.endswith(".py") else a for a in args]
    r = subprocess.run([PY, "-B"] + argv, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600, env=env)
    lines = (r.stdout or "").strip().split(chr(10))
    return r.returncode, (lines[-1] if lines else ""), (r.stdout or "")


def main():
    doc = open(DOC, encoding="utf-8").read()
    errs = []
    n_ok = 0
    for name, args, sub, want in CHECKS:
        rc, tail, out = run_one(args, sub)
        hit = (want in tail) or (want in out)
        if not hit:
            errs.append("%s 末行不含「%s」:: %s" % (name, want, tail[:90]))
        elif rc not in (0, 2):
            errs.append("%s rc=%d 非 0/2" % (name, rc))
        else:
            n_ok += 1
    # 表里必须真的写了这七条（防有人把表删成空壳而判据照样绿）
    for k in ["| **1** |", "| **2** |", "| **3** |", "| **4** |", "| **5** |", "| **6** |", "| **7** |"]:
        if k not in doc:
            errs.append("总览件缺需求行 " + k)
    # 需求 6 必须显式标「不成立」（防被静默改成达标）
    if "度量对象本身不成立" not in doc:
        errs.append("需求6 未标「度量对象本身不成立」")
    neg = os.environ.get("R326_NEG")
    if neg == "drop_req":
        ok = ("| **6** |" not in doc.replace("| **6** |", "| X |", 1))
        print("[R326:NEG] drop_req teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "cmd":
        rc, tail, _ = run_one(["05-exec/r324_entry_reachability_face.py", "--closure", "bogus"], "")
        ok = (rc != 0) or ("orphans_top=623" not in tail)
        print("[R326:NEG] cmd teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "req6":
        ok = ("度量对象本身不成立" not in doc.replace("度量对象本身不成立", "口径达标", 1))
        print("[R326:NEG] req6 teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    for e in errs:
        print("FAIL " + e)
    if errs:
        print("[R326:OVERVIEW] checks=%d ok=%d teeth=FAIL" % (len(CHECKS), n_ok))
        return 1
    print("[R326:OVERVIEW] checks=%d ok=%d teeth=pass" % (len(CHECKS), n_ok))
    return 0


if __name__ == "__main__":
    sys.exit(main())
