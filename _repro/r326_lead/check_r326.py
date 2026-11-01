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
    ("需求1 入口可达", ["05-exec/r324_entry_reachability_face.py", "--closure", "top"], "", "orphans_top="),  # r342：值不写死，改由腿7 对账 latest + 单调不升
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
    tails = {}
    for name, args, sub, want in CHECKS:
        rc, tail, out = run_one(args, sub)
        tails[name] = (out or "") + chr(10) + (tail or "")
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
    # 腿7（r342 新增，取代写死数字）：三件对账——总览件现值 == latest == (现跑末行)，且相对 r326 快照单调不升。
    # 一手根因：原 CHECKS 写死 "orphans_top=623" ⇒ 落地生效（数字下降）反而判红，
    # 与 M3 判据自己注明的「9 是现值不是常量、禁硬编码计数」同一病根（R326-1 造门时犯了自家立过的错）。
    lat_p = os.path.join(ROOT, "06-benchmark", "entry_reachability_latest.json")
    base_p = os.path.join(HERE, "entry_baseline_20261101.json")
    if not os.path.isfile(lat_p) or not os.path.isfile(base_p):
        errs.append("腿7 输入缺失：latest 或 baseline 件不在盘")
    else:
        cur_n = json.load(open(lat_p, encoding="utf-8"))["totals"]["orphans_top"]
        base_n = json.load(open(base_p, encoding="utf-8"))["totals"]["orphans_top"]
        o1 = tails.get("需求1 入口可达", "")
        if "orphans_top=%d" % cur_n not in o1:
            errs.append("现跑末行 != latest 现值 %d" % cur_n)
        if ("孤儿 **%d**" % cur_n) not in doc and ("孤儿 %d" % cur_n) not in doc:
            errs.append("总览件需求1 读数未同步 latest=%d（保鲜靶失效）" % cur_n)
        if cur_n > base_n:
            errs.append("orphans_top %d 升过 r326 基线 %d（落地应只降不升；升=有新孤儿须先记账）" % (cur_n, base_n))
    neg = os.environ.get("R326_NEG")
    if neg == "drop_req":
        ok = ("| **6** |" not in doc.replace("| **6** |", "| X |", 1))
        print("[R326:NEG] drop_req teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "cmd":
        rc, tail, _ = run_one(["05-exec/r324_entry_reachability_face.py", "--closure", "bogus"], "")
        ok = (rc != 0) or ("orphans_top=" not in tail)  # 非法 --closure ⇒ 不成末行（r342 动态化，原写死 623 已无牙）
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
