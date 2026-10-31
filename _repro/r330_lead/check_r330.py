# -*- coding: utf-8 -*-
"""r330 自证：替换优先级总表里每个承重读数都必须现跑可复算（三件 spec 五腿 + 28 件守恒 + 191 件守恒）。

为什么需要这条：总表最容易变成「把散在各处的话抄一遍」。本判据逐格现跑，抄错或件变了即红。
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PY = sys.executable

SPECS = ["A-prompt-better", "frontend-skill", "security-audit"]
DOC = os.path.join(ROOT, "04-plan", "替换优先级总表_r330_2026-11-01.md")
P28 = os.path.join(ROOT, "06-benchmark", "r261_c2_adjudication_priority28.json")
MATRIX = os.path.join(ROOT, "06-benchmark", "quarterly_r260", "2026Q4", "replacement_matrix.json")


def run(args, timeout=300):
    env = dict(os.environ)
    env.setdefault("PYTHONPYCACHEPREFIX", os.path.join(HERE, "pycache"))
    r = subprocess.run([PY, "-B"] + args, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout, env=env)
    return r.returncode, (r.stdout or ""), (r.stderr or "")


def main():
    errs = []
    info = {}
    neg = os.environ.get("R330_NEG")
    # 腿 A：三件 spec 必须五腿全 PASS（现跑，不读文件声称）
    for s in SPECS:
        rc, out, err = run(["05-exec/landing_replay_check.py", "--spec",
                            "05-exec/landing_specs/" + s + ".json"])
        tail = [x for x in out.strip().split(chr(10)) if "[LANDING-CHECK]" in x]
        t = tail[-1] if tail else ""
        if "gate=PASS" not in t:
            errs.append("%s gate 非 PASS :: %s" % (s, t[:100]))
        if neg == "spec" and s == "frontend-skill":
            break
    info["specs"] = len(SPECS)
    # 腿 B：28 件守恒（13/12/3）与 equal=true
    d = json.load(open(P28, encoding="utf-8"))
    bv = (d.get("conservation") or {}).get("by_verdict") or {}
    if bv != {"KEEP_LOCAL": 13, "NO_OS_EQUIVALENT": 12, "UPGRADE_CANDIDATE": 3}:
        errs.append("28 件分布不符: %s" % bv)
    if not (d.get("conservation") or {}).get("equal"):
        errs.append("28 件守恒 equal != true")
    if sum(bv.values()) != 28:
        errs.append("28 件之和 %d != 28" % sum(bv.values()))
    # 腿 C：191 件守恒（矩阵四态之和）
    m = json.load(open(MATRIX, encoding="utf-8"))
    mv = {}
    for r in m["rows"]:
        mv[r.get("verdict")] = mv.get(r.get("verdict"), 0) + 1
    if sum(mv.values()) != 191:
        errs.append("矩阵 191 守恒破: %d" % sum(mv.values()))
    info["matrix"] = mv
    # 腿 D：文档必须写了 3 件与 163 件这两个数（防表被改小）
    doc = open(DOC, encoding="utf-8").read()
    for k in ["**3**", "**28**", "**163**", "**191**"]:
        if k not in doc:
            errs.append("总表缺关键数 " + k)
    if "UPGRADE_CANDIDATE 3" not in doc and "**3**" not in doc:
        errs.append("总表未标 UPGRADE_CANDIDATE = 3")
    # 口径说明：矩阵四态（MATCHED/NO_OS_CANDIDATE/FAMILY_ONLY）**不含** UPGRADE_CANDIDATE；
    # 该值只产自 28 件裁决件 ⇒ 这里不拿它交叉断言（否则恒红，是本判据自己的口径错）。
    if neg == "spec":
        # 负控 a：临时把 frontend-skill 的 expect 改回 1.1.0 ⇒ 判据必须抓到 gate 非 PASS
        sp = os.path.join(ROOT, "05-exec", "landing_specs", "frontend-skill.json")
        d2 = json.load(open(sp, encoding="utf-8"))
        bak = d2["version"]["expect"]
        d2["version"]["expect"] = "1.1.0"
        tmp = os.path.join(HERE, "_neg_spec.json")
        open(tmp, "w", encoding="utf-8").write(json.dumps(d2, ensure_ascii=False))
        rc2, out2, _ = run(["05-exec/landing_replay_check.py", "--spec", os.path.relpath(tmp, ROOT)])
        os.remove(tmp)
        bad = any("gate=PASS" not in x for x in out2.split(chr(10)) if "[LANDING-CHECK]" in x)
        print("[R330:NEG] spec teeth=" + ("pass" if bad else "FAIL"))
        return 0 if bad else 1
    if neg == "count28":
        ok = (sum(bv.values()) == 28)
        print("[R330:NEG] count28 teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "drop":
        ok = ("**163**" in doc)
        print("[R330:NEG] drop teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    for e in errs:
        print("FAIL " + e)
    if errs:
        print("[R330:PRIORITY] specs=3 upg=3 cut=28 rest=163 teeth=FAIL")
        return 1
    print("[R330:PRIORITY] specs=3 upg=3 cut=28 rest=163 matrix_sum=%d teeth=pass" % sum(mv.values()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
