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

        # ── T13/T14 diff_files 清单：截断必须显式声明，且计数与摘要仍按全量算（R-ENUM）
        def synth_repo(n_dirty):
            d = tempfile.mkdtemp(prefix="r67_repo_", dir=base)
            subprocess.run(["git", "init", "-q", d], capture_output=True)
            with io.open(os.path.join(d, "base.txt"), "w", encoding="utf-8", newline="\n") as f:
                f.write("base\n")
            subprocess.run(["git", "-C", d, "add", "base.txt"], capture_output=True)
            subprocess.run(["git", "-C", d, "-c", "user.email=t@t", "-c", "user.name=t",
                            "commit", "-q", "-m", "base"], capture_output=True)
            for i in range(n_dirty):
                with io.open(os.path.join(d, "f%03d.txt" % i), "w", encoding="utf-8",
                             newline="\n") as f:
                    f.write("x\n")
            return d

        big = synth_repo(45)
        pb = m.pin_face(big, diff_cap=40)
        check("T13 截断：45 条未提交 ⇒ diff_files 恰 40 条 + diff_truncated=True + dirty_n 仍 45",
              pb.get("dirty_n") == 45 and len(pb.get("diff_files") or []) == 40
              and pb.get("diff_truncated") is True, "%s" % {k: pb.get(k) for k in
                                                            ("dirty_n", "diff_truncated")})
        small = synth_repo(3)
        ps = m.pin_face(small)
        check("T14 不截断：3 条未提交 ⇒ diff_files 3 条 + diff_truncated=False",
              ps.get("dirty_n") == 3 and len(ps.get("diff_files") or []) == 3
              and ps.get("diff_truncated") is False, "%s" % {k: ps.get(k) for k in
                                                             ("dirty_n", "diff_truncated")})

        # ── T15/T17 跨轮趋势：同一面 pin 变 2 次 ⇒ changes==2；关掉计数钩子 ⇒ 必须归零
        rows = [
            {"ts": "t1", "faces": [{"root": "A", "state": "pinned", "head": "h1",
                                    "dirty_digest": "d1", "dirty_n": 1}]},
            {"ts": "t2", "faces": [{"root": "A", "state": "pinned", "head": "h1",
                                    "dirty_digest": "d2", "dirty_n": 2}]},
            {"ts": "t3", "faces": [{"root": "A", "state": "pinned", "head": "h2",
                                    "dirty_digest": "d3", "dirty_n": 3}]},
        ]
        t = m.trend_of(rows)["A"]
        check("T15 趋势：pin 变 2 次 / 出现 3 行 / 最新未提交 3 条 / 最近变动 t3",
              t["changes"] == 2 and t["rows"] == 3 and t["latest_dirty_n"] == 3
              and t["last_change_ts"] == "t3", str(t))
        try:
            m.TREND_COUNT_CHANGES = False
            t_mut = m.trend_of(rows)["A"]
        finally:
            m.TREND_COUNT_CHANGES = True
        check("T17 变异：关掉变动计数钩子 ⇒ changes 归零（即 T15 的期望确由该判定承担）",
              t_mut["changes"] == 0, str(t_mut))

        # ── T16 趋势空台账必须 rc=2（只读报告模式先于落账，故该支在 CLI 上真实可达）
        rc16 = m.main(["--trend", "--ledger", os.path.join(base, "no_such_ledger.jsonl")])
        check("T16 趋势：空台账 ⇒ rc=2（零输入不得判过 R247）", rc16 == 2, "rc=%s" % rc16)

        # ── T18/T19 增量落账：未变面清单清空 + 留 diff_inherit；已变面全量保留
        prev_row = {"ts": "t1", "faces": [{"root": "A", "state": "pinned", "head": "h1",
                                           "dirty_digest": "d1", "diff_files": ["p"]}]}
        same_f = [{"root": "A", "state": "pinned", "head": "h1", "dirty_digest": "d1",
                   "diff_files": ["x"], "diff_truncated": False}]
        chg_f = [{"root": "A", "state": "pinned", "head": "h2", "dirty_digest": "d9",
                  "diff_files": ["y"], "diff_truncated": False}]
        pf_same = m.payload_faces(same_f, [prev_row])[0]
        pf_chg = m.payload_faces(chg_f, [prev_row])[0]
        check("T18 增量落账：未变面清单清空且留 diff_inherit=t1；已变面清单保留",
              pf_same["diff_files"] == [] and pf_same.get("diff_inherit") == "t1"
              and pf_chg["diff_files"] == ["y"] and "diff_inherit" not in pf_chg,
              "%s / %s" % (pf_same, pf_chg))
        try:
            m.INHERIT_UNCHANGED = False
            pf_mut = m.payload_faces(same_f, [prev_row])[0]
        finally:
            m.INHERIT_UNCHANGED = True
        check("T19 变异：关掉增量钩子 ⇒ 未变面清单不再清空（即 T18 的省体量确由该守卫承担）",
              pf_mut["diff_files"] == ["x"], str(pf_mut))

        # ── T20/T21 热度排序：热度降序 -> 路径升序；关掉钩子退化路径序
        files = [" B m/z.md", " M a/x.md", "?? c/y.md"]
        heat = {"?? c/y.md": 5, " M a/x.md": 5, " B m/z.md": 1}
        ordered = m.order_diff_files(files, heat)
        check("T20 热度排序：热度 5 的两条在前且按路径升序，热度 1 的在后",
              ordered == [" M a/x.md", "?? c/y.md", " B m/z.md"], str(ordered))
        try:
            m.ORDER_BY_HEAT = False
            ordered_mut = m.order_diff_files(files, heat)
        finally:
            m.ORDER_BY_HEAT = True
        check("T20 变异：关掉热度钩子 ⇒ 退化为纯路径序（即热度排序确由该守卫承担）",
              ordered_mut == sorted(files), str(ordered_mut))
        check("T21 热度索引：同路径跨行出现次数累加",
              m.heat_index([{"faces": [{"diff_files": ["a", "b"]}]},
                            {"faces": [{"diff_files": ["a"]}]}]) == {"a": 2, "b": 1})

        # ── T22 关键不变量：热度**不得**进入 dirty_digest（否则热度一变就假报 pin 变动）
        d_noheat = m.pin_face(small)
        d_heat = m.pin_face(small, heat={"?? f000.txt": 99})
        check("T22 不变量：同一批未提交字节，两种热度口径下 dirty_digest 必须相同（但 diff_order 变）",
              d_noheat["dirty_digest"] == d_heat["dirty_digest"]
              and d_noheat["diff_order"] == "path" and d_heat["diff_order"] == "heat",
              "%s / %s" % (d_noheat.get("diff_order"), d_heat.get("diff_order")))

        # ── T23 继承指针指向「最近一次全量行」，不是紧邻上一行；无全量行 ⇒ 保留清单不写空指针
        hist3 = [
            {"ts": "tA", "faces": [{"root": "A", "state": "pinned", "head": "h1",
                                    "dirty_digest": "d1", "diff_files": ["full"]}]},
            {"ts": "tB", "faces": [{"root": "A", "state": "pinned", "head": "h1",
                                    "dirty_digest": "d1", "diff_files": [],
                                    "diff_inherit": "tA"}]},
        ]
        same_now = [{"root": "A", "state": "pinned", "head": "h1", "dirty_digest": "d1",
                     "diff_files": ["x"], "diff_truncated": False}]
        pf3 = m.payload_faces(same_now, hist3)[0]
        no_full = m.payload_faces(same_now, [{"ts": "tB", "faces": [
            {"root": "A", "state": "pinned", "head": "h1", "dirty_digest": "d1",
             "diff_files": []}]}])[0]
        check("T23 继承指针指向最近一次全量行 tA（而非紧邻的空壳 tB）；无全量行则保留清单",
              pf3.get("diff_inherit") == "tA" and pf3["diff_files"] == []
              and "diff_inherit" not in no_full and no_full["diff_files"] == ["x"],
              "%s / %s" % (pf3, no_full))
    finally:
        shutil.rmtree(base, ignore_errors=True)

    n_ok = sum(1 for _, ok in RESULTS if ok)
    total = len(RESULTS)
    print("-" * 60)
    print("[GATE:fixture-%s] r67 输入固定面夹具 %d/%d" % ("pass" if n_ok == total else "fail", n_ok, total))
    return 0 if n_ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
