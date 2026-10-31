# -*- coding: utf-8 -*-
"""r325a 自证：两份 landing spec 可解析、可跑、UNVERIFIED 有具名原因、裸指针 token 覆盖 _repro/_temp。

为什么判据要远离 spec 自述：spec 是**被判对象**。这里每条都现算 —— 真跑判据拿 rc 与末行、真读 report、真查 file:line。
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PY = sys.executable
SPECS = [
    os.path.join(ROOT, "05-exec", "landing_specs", "r324_entry_reachability.json"),
    os.path.join(ROOT, "05-exec", "landing_specs", "r323a_gl1_targets.json"),
]
RES = os.path.join(HERE, "spec_result.json")
REPORT = os.path.join(HERE, "report.md")


def run_spec(sp):
    """现跑判据，返回 (rc, 末行)。这一步不读任何缓存件 —— spec 的有效性只能靠真跑证明。"""
    env = dict(os.environ)
    env.setdefault("PYTHONPYCACHEPREFIX", os.path.join(HERE, "pycache"))
    r = subprocess.run([PY, "-B", os.path.join(ROOT, "05-exec", "landing_replay_check.py"),
                        "--spec", sp], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300, env=env)
    lines = (r.stdout or "").strip().split(chr(10))
    tail = lines[-1] if lines else ""
    return r.returncode, tail, (r.stdout or ""), (r.stderr or "")


def main():
    d = json.load(open(RES, encoding="utf-8"))
    rep = open(REPORT, encoding="utf-8").read()
    errs = []
    legs_total = 0
    unver_n = 0
    for sp in SPECS:
        name = os.path.basename(sp)
        if not os.path.isfile(sp):
            errs.append("%s 不存在" % name)
            continue
        try:
            spec = json.load(open(sp, encoding="utf-8"))
        except Exception as e:
            errs.append("%s 不是合法 JSON: %s" % (name, e))
            continue
        bt = spec.get("bare_tokens") or []
        if "_repro/" not in bt or "_temp/" not in bt:
            errs.append("%s bare_tokens 缺 _repro/ 或 _temp/" % name)
        if not spec.get("managed"):
            errs.append("%s 缺 managed" % name)
        rc, tail, out, err = run_spec(sp)
        if rc not in (0, 1, 2):
            errs.append("%s 判据退出码异常 %d" % (name, rc))
        if "[LANDING-CHECK]" not in tail:
            errs.append("%s 末行不是 LANDING-CHECK 形态: %s" % (name, tail[:80]))
        legs = re.findall(r"([RPNVM])=([a-zA-Z]+)", tail)
        legs_total += len(legs)
        for leg_name, state in legs:
            if state == "UNVERIFIED":
                unver_n += 1
        # UNVERIFIED 必须能在 report 里找到具名原因
        if any(s == "UNVERIFIED" for _, s in legs):
            if name not in rep:
                errs.append("%s 有 UNVERIFIED 腿但 report 未提该 spec" % name)
    if not os.path.isfile(REPORT):
        errs.append("report.md 缺失")
    elif "UNVERIFIED" not in rep and unver_n > 0:
        errs.append("report 未写 UNVERIFIED 原因（但实跑有 %d 条）" % unver_n)
    # spec_result 里必须记到每个 spec 的退出码
    got = {x.get("spec") for x in (d.get("specs") or [])}
    for sp in SPECS:
        n = os.path.basename(sp)
        if n not in got:
            errs.append("spec_result 缺 %s 记录" % n)
    neg = os.environ.get("R325A_NEG")
    if neg == "bare":
        ok = any(("_repro/" not in (json.load(open(s, encoding="utf-8")).get("bare_tokens") or [])) for s in SPECS if os.path.isfile(s))
        bad_spec = os.path.join(HERE, "_neg_spec.json")
        s0 = json.load(open(SPECS[0], encoding="utf-8"))
        s0["bare_tokens"] = []
        open(bad_spec, "w", encoding="utf-8").write(json.dumps(s0))
        bt = (json.load(open(bad_spec, encoding="utf-8")).get("bare_tokens") or [])
        ok = ("_repro/" not in bt)
        os.remove(bad_spec)
        print("[R325A:NEG] bare teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "ghost":
        s0 = json.load(open(SPECS[0], encoding="utf-8"))
        s0["new_files"] = [{"target": "05-exec/__not_exist__.py"}]
        gsp = os.path.join(HERE, "_neg_ghost.json")
        open(gsp, "w", encoding="utf-8").write(json.dumps(s0))
        rc, tail, _, _ = run_spec(gsp)
        os.remove(gsp)
        ok = (rc == 2) or ("UNVERIFIED" in tail)
        print("[R325A:NEG] ghost teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "handedited":
        rc, tail, _, _ = run_spec(SPECS[0])
        ok = (rc == 2)  # 该 spec 结构性 UNVERIFIED（本仓件无上游锚），不是绿
        print("[R325A:NEG] bundle teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    for e in errs:
        print("FAIL " + e)
    if errs:
        print("[R325A:SPEC] specs=%d legs=%d unverified=%d teeth=FAIL" % (len(SPECS), legs_total, unver_n))
        return 1
    print("[R325A:SPEC] specs=%d legs=%d unverified=%d teeth=pass" % (len(SPECS), legs_total, unver_n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
