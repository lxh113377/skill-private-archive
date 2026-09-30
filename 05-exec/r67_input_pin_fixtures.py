# -*- coding: utf-8 -*-
"""R58-1 夹具：仓外输入固定面（`05-exec/r67_input_pin_guard.py`）。

设计原则（A-get-memory Step 2.7 判据交付硬判据）：
  ① 夹具先写先看红；② 变异对照（只翻被测模块的**那一个**开关，期望腿必须翻）；③ 挂执行路径（注册进 run_gates 第 27 门）。
**不碰真面**：junction 一律造在 mkdtemp 合成面里（`mklink /J` 无需管理员），真机腿（T0）只读调用 `--gate`。
"""
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "r67_input_pin_guard.py")


def load_module():
    spec = importlib.util.spec_from_file_location("r67_input_pin_uut", TARGET)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mklink_junction(link, target):
    """造真 junction；返回 (ok, msg)。"""
    r = subprocess.run(["cmd", "/c", "mklink", "/J", link, target],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode == 0, ((r.stdout or "") + (r.stderr or "")).strip()


RESULTS = []


def check(label, ok, detail=""):
    RESULTS.append((label, bool(ok)))
    print("  %s %s%s" % ("OK  " if ok else "FAIL", label, ("  | " + detail) if detail and not ok else ""))


def main():
    m = load_module()

    # ── T0 真机只读腿：本仓声明的镜像面必须全钉在权威源
    #    台账写进临时件（夹具不得改被测产物，A-get-memory ⑦）；声明面仍读真 truth_constants（只读）
    tmp_ledger = os.path.join(tempfile.mkdtemp(prefix="r67_led_"), "input_pins.jsonl")
    rc0 = m.main(["--gate", "--ledger", tmp_ledger])
    check("T0 真机：本仓 --gate rc=0（12 条镜像面全钉权威源）", rc0 == 0, "rc=%s" % rc0)

    base = tempfile.mkdtemp(prefix="r67_pin_")
    try:
        auth = os.path.join(base, "auth")
        os.makedirs(auth)
        other = os.path.join(base, "other")
        os.makedirs(other)
        jgood = os.path.join(base, "j_good")
        jbad = os.path.join(base, "j_bad")
        realdir = os.path.join(base, "plain_dir")
        os.makedirs(realdir)
        ok1, msg1 = mklink_junction(jgood, auth)
        ok2, msg2 = mklink_junction(jbad, other)
        if not (ok1 and ok2):
            # 能力缺失时如实记 UNVERIFIED，不静默跳过（A-get-memory ⑧）
            print("  ⚠️ mklink 不可用（%s / %s）⇒ junction 三条腿记 UNVERIFIED" % (msg1, msg2))

        # ── T1 真实 junction 指向权威根 ⇒ ok
        p1 = m.probe_face(jgood, auth)
        check("T1 真 junction 指向权威根 ⇒ ok=True", p1["ok"] is True and p1["kind"] == "junction",
              str(p1))

        # ── T2 真实目录（非 junction）⇒ 必须判不 OK
        p2 = m.probe_face(realdir, auth)
        check("T2 真实目录（非 junction）⇒ ok=False 且点名 junction",
              p2["ok"] is False and "junction" in p2["why"], str(p2))

        # ── T3 声明 null ⇒ declared=False（不得静默丢）
        p3 = m.probe_face(None, auth)
        check("T3 声明 null ⇒ declared=False", p3["declared"] is False and p3["kind"] == "not_declared",
              str(p3))

        # ── T4 不存在 ⇒ kind=missing
        p4 = m.probe_face(os.path.join(base, "nope"), auth)
        check("T4 路径不存在 ⇒ kind=missing", p4["kind"] == "missing" and p4["ok"] is False, str(p4))

        # ── T5 junction 指向别处 ⇒ 必须判不 OK
        p5 = m.probe_face(jbad, auth)
        check("T5 junction 指向别处 ⇒ ok=False 且点名目标不等",
              p5["ok"] is False and "!=" in p5["why"], str(p5))

        # ── T6 judge：零输入（paths 空）⇒ rc=2，禁判过（R247）
        rc6, rp6 = m.judge({"paths": {}, "junction_paths": {"a": {}}, "endpoints": {"active": ["a"]}}, [])
        check("T6 judge 零输入 ⇒ rc=2", rc6 == 2, "rc=%s" % rc6)

        # ── T7 judge：缺 active ⇒ rc=2
        rc7, _ = m.judge({"paths": {"global_skills": "x"}, "junction_paths": {}, "endpoints": {}}, [])
        check("T7 judge 缺声明项 ⇒ rc=2", rc7 == 2, "rc=%s" % rc7)

        # ── T8 judge：有违约 ⇒ rc=1 且 violations 点名
        rc8, rp8 = m.judge(
            {"paths": {"global_skills": "S", "global_memory": "M"},
             "junction_paths": {"a": {"skills": "S"}},
             "endpoints": {"active": ["a"]}},
            [{"label": "a.skills", "path": "S",
              "probe": {"declared": True, "exists": True, "kind": "dir", "target": "T", "ok": False,
                        "why": "不是 junction"}}])
        check("T8 judge 有违约 ⇒ rc=1 且点名 a.skills",
              rc8 == 1 and [v["label"] for v in rp8["violations"]] == ["a.skills"], "rc=%s" % rc8)

        # ── T9 变异：关掉 REQUIRE_JUNCTION ⇒ 同一对象（真实目录，canon 取它自己）判定翻绿
        #    对照组：开着守卫时同一对象必须判不 OK（两侧样本同一，只翻开关）
        p9_on = m.probe_face(realdir, realdir)
        try:
            m.REQUIRE_JUNCTION = False
            p9_off = m.probe_face(realdir, realdir)
        finally:
            m.REQUIRE_JUNCTION = True
        check("T9 变异：junction 守卫生效时判 False、关掉后翻 True（该守卫确在承担 T2 的判定）",
              p9_on["ok"] is False and p9_off["ok"] is True, "%s / %s" % (p9_on, p9_off))

        # ── T10 变异：关掉 REQUIRE_TARGET_EQ ⇒ T5 那条腿的期望必须翻
        try:
            m.REQUIRE_TARGET_EQ = False
            p10 = m.probe_face(jbad, auth)
        finally:
            m.REQUIRE_TARGET_EQ = True
        check("T10 变异：关掉目标比对 ⇒ 指错目标被判 ok（即 T5 的期望确由该守卫承担）",
              p10["ok"] is True, str(p10))

        # ── T11 pin_face：真仓 pinned / 不存在路径 unreachable
        pin = m.pin_face(os.path.dirname(HERE))
        pin_bad = m.pin_face(os.path.join(base, "nope"))
        check("T11 pin_face：真仓 state=pinned 且有 head/dirty_digest；不存在 ⇒ unreachable",
              pin.get("state") == "pinned" and pin.get("head") and pin.get("dirty_digest")
              and pin_bad.get("state") == "unreachable", "%s / %s" % (pin, pin_bad))

        # ── T12 自洽正反两向：同份 → True；差一份 → False
        a = [{"root": "R", "state": "pinned", "head": "abc", "dirty_digest": "d1"}]
        b = [{"root": "R", "state": "pinned", "head": "abc", "dirty_digest": "d2"}]
        ok_fwd, ok_rev = m.self_consistent(a, a), m.self_consistent(a, b)
        check("T12 自洽：同份 True / 差一份 False（写一份判另一份须拒）",
              ok_fwd is True and ok_rev is False, "%s / %s" % (ok_fwd, ok_rev))
    finally:
        shutil.rmtree(base, ignore_errors=True)

    n_ok = sum(1 for _, ok in RESULTS if ok)
    total = len(RESULTS)
    print("-" * 60)
    print("[GATE:fixture-%s] r67 输入固定面夹具 %d/%d" % ("pass" if n_ok == total else "fail", n_ok, total))
    return 0 if n_ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
