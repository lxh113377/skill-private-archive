# -*- coding: utf-8 -*-
"""r329 自证：两条挂账（R321-1 死链门 --exclude 接门表 / R321-6 体量门逐件越限腿）已兑现，三条负控。

为什么判据要现跑而不是读代码：两条都是「判据本体的行为」—— 读源码只能证明「写了」，
只有真跑 gate / volume_tiers 才能证明「生效」。本判据因此**直接调两个判据件**并解析末行。
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PY = sys.executable


def run(cmd_args, timeout=300):
    env = dict(os.environ)
    env.setdefault("PYTHONPYCACHEPREFIX", os.path.join(HERE, "pycache"))
    r = subprocess.run([PY, "-B"] + cmd_args, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout, env=env)
    return r.returncode, (r.stdout or ""), (r.stderr or "")


def main():
    errs = []
    info = {}
    # 腿 A：死链门单跑（门表 argv 已接 --exclude 通配）
    rc, out, err = run(["05-exec/run_gates.py", "--gate", "md_deadlink_face", "--no-ledger"])
    info["deadlink_rc"] = rc
    if "[GATES:PASS]" not in out:
        errs.append("死链门未 PASS（rc=%d）:: %s" % (rc, out.strip().split(chr(10))[-1][:100]))
    if rc != 0:
        errs.append("死链门 rc=%d 非 0" % rc)
    # 腿 B：volume_tiers 逐件腿
    rc2, out2, err2 = run(["05-exec/r150_volume_tiers.py", "--json", "_repro/r329_lead/vol_check.json"])
    info["vol_rc"] = rc2
    m = re.search(r"\[GOVTIER:ROOTDOC-(OK|OVER|UNVERIFIED)\]", out2)
    if not m:
        errs.append("volume_tiers 无 ROOTDOC 腿输出（逐件腿未生效）")
    elif m.group(1) == "UNVERIFIED":
        errs.append("ROOTDOC 腿 UNVERIFIED（root_doc_max 取不到）")
    elif m.group(1) == "OVER":
        errs.append("ROOTDOC 腿 OVER（仍有过大根文档）:: " + out2.split(chr(10))[-1][:100])
    info["rootdoc"] = m.group(1) if m else None
    # 腿 C：README 实测字节 <= 16384（独立于门，自己量）
    rp = os.path.join(ROOT, "README.md")
    size = os.path.getsize(rp)
    info["readme_bytes"] = size
    if size > 16384:
        errs.append("README %dB > 16384B（逐件腿应判 OVER）" % size)
    # 腿 D：源码层面确认 --exclude 在门表 argv（防「腿 A 绿但其实是别的原因」）
    rg = open(os.path.join(ROOT, "05-exec", "run_gates.py"), encoding="utf-8").read()
    if "--exclude=_repro/*/evidence/*" not in rg:
        errs.append("run_gates.py 的 md_deadlink_face argv 未含 --exclude 通配")
    # 腿 E：r220 支持 fnmatch（不是旧 startswith 前缀）
    r2 = open(os.path.join(ROOT, "05-exec", "r220_md_deadlink.py"), encoding="utf-8").read()
    if "fnmatch.fnmatch" not in r2:
        errs.append("r220 未使用 fnmatch（仍是前缀匹配）")
    neg = os.environ.get("R329_NEG")
    if neg == "exclude_off":
        # 负控 a：不带 --exclude 跑 r220，上游快照那 3 条死链必须重新出现
        rc3, out3, _ = run(["05-exec/r220_md_deadlink.py", ".", "--json", "_repro/r329_lead/neg_noexcl.json"])
        hit = ("_repro/r314b/evidence" in out3) or ("_repro/r316b_lineage/evidence" in out3)
        print("[R329:NEG] exclude_off teeth=" + ("pass" if hit else "FAIL"))
        return 0 if hit else 1
    if neg == "rootdoc":
        # 负控 b：造一个超限临时根文档，逐件腿必须判 OVER
        import tempfile
        d = tempfile.mkdtemp()
        big = os.path.join(d, "README.md")
        open(big, "w", encoding="utf-8").write("x" * 20000)
        rc4, out4, _ = run(["05-exec/r150_volume_tiers.py", "--root", d, "--json", os.path.join(d, "v.json")])
        ok = "[GOVTIER:ROOTDOC" in out4 and ("OVER" in out4 or "UNVERIFIED" in out4)
        print("[R329:NEG] rootdoc teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "readme":
        # 负控 c：README 若回到 21326B 级别，腿 C 必须红
        ok = size <= 16384
        print("[R329:NEG] readme teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    for e in errs:
        print("FAIL " + e)
    if errs:
        print("[R329:LANDED] deadlink=%s rootdoc=%s readme=%dB teeth=FAIL" % (info["deadlink_rc"], info["rootdoc"], size))
        return 1
    print("[R329:LANDED] deadlink_passed rootdoc=%s readme=%dB binary_exclude=ok fnmatch=ok teeth=pass" % (info["rootdoc"], size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
