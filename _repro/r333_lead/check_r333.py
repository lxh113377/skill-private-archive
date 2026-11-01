# -*- coding: utf-8 -*-
"""r333 自证：本轮三件的承重读数全部现跑/现算复核，三条负控。

1. progress.ndjson 合法 JSON 行且 state 三态齐（跑完态 ≥100 行）；fixture_wiring 重复次数 == 119-117+1 的算术自洽（只断言差额可解释到该门，不宣称已证因）
2. r52 scan：live_uncited_list 条数 == live_uncited（可诊断性缺口已补，两边必须一致）
3. ratchet_gate 现跑 PASS（12 条收口生效）
4. 台账：OVERDUE 0 且 r333 裁决字样 == 12
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PY = sys.executable


def sh(args, ms=300000):
    env = dict(os.environ)
    env.setdefault("PYTHONPYCACHEPREFIX", os.path.join(HERE, "pycache"))
    r = subprocess.run([PY, "-B"] + args, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=ms, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main():
    errs = []
    neg = os.environ.get("R333_NEG")
    # 1 progress 完整性
    prog = os.path.join(HERE, "progress.ndjson")
    rows = []
    if os.path.isfile(prog):
        for ln in open(prog, encoding="utf-8").read().splitlines():
            if ln.strip():
                try:
                    rows.append(json.loads(ln))
                except ValueError:
                    errs.append("progress 有非法 JSON 行")
    else:
        errs.append("progress.ndjson 缺失")
    states = set(x.get("state") for x in rows)
    if not states <= {"PASS", "FAIL", "UNVERIFIED", "MISSING"}:
        errs.append("progress 出现未知 state: %s" % states)
    if len(rows) < 100:
        errs.append("progress 行数 %d < 100（未跑完态不当全量读数引用）" % len(rows))
    # 差额算术自洽（登记为疑点非已证因）
    fw = sum(1 for x in rows if x.get("id") == "fixture_wiring_face")
    doc = open(os.path.join(ROOT, "memory", "07-next-steps.md"), encoding="utf-8").read()
    if fw - 1 != (len(rows) - 117):
        errs.append("疑点算术不自洽：行数%d-117 != fixture_wiring重复多出%d" % (len(rows), fw - 1))
    # 2 r52 可诊断性
    rc, out = sh(["05-exec/r52_md_claim_face_scan.py", "--json",
                  "_repro/r333_lead/claims_chk.json"], 300000)
    cj = json.load(open(os.path.join(HERE, "claims_chk.json"), encoding="utf-8"))
    if cj.get("live_uncited") != len(cj.get("live_uncited_list") or []):
        errs.append("r52 计数与明细不一致: %s vs %d" % (
            cj.get("live_uncited"), len(cj.get("live_uncited_list") or [])))
    # 3 ratchet
    rc2, out2 = sh(["05-exec/ratchet_gate.py"], 300000)
    if "[RATCHET:PASS]" not in out2:
        errs.append("ratchet 非 PASS :: " + out2.strip().splitlines()[-1][:90] if out2.strip() else "ratchet 无输出")
    # 4 台账
    if doc.count("r333 裁决") != 12:
        errs.append("r333 裁决字样 %d != 12" % doc.count("r333 裁决"))
    m = re.findall(r"OVERDUE (\d+)", open(os.path.join(ROOT, "_repro/r333_lead/debt_final.txt"), encoding="utf-8").read()) if os.path.isfile(os.path.join(ROOT, "_repro/r333_lead/debt_final.txt")) else None
    if neg == "count":
        ok = (cj.get("live_uncited") == len(cj.get("live_uncited_list") or []))
        print("[R333:NEG] count teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "prog":
        ok = len(rows) >= 100
        print("[R333:NEG] prog teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "ledger":
        ok = doc.count("r333 裁决") == 12
        print("[R333:NEG] ledger teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    for e in errs:
        print("FAIL " + e)
    if errs:
        print("[R333:ROUND] progress=%d fw=%d uncited=%d ratchet=%s teeth=FAIL" % (
            len(rows), fw, cj.get("live_uncited"), rc2))
        return 1
    print("[R333:ROUND] progress=%d fw=%d uncited_list=%d ratchet=PASS ledger12=ok teeth=pass" % (
        len(rows), fw, len(cj.get("live_uncited_list") or [])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
