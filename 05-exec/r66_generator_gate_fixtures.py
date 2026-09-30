# -*- coding: utf-8 -*-
"""r66 W-46b 第二步夹具：generator 判据（05-exec/r58_generator_coverage.py）与 `--gate` 三态。

设计原则（A-get-memory Step 2.7 判据交付硬判据）：
  ① 夹具先写先看红：每条腿都在「判据缺失/被改坏」时翻红（变异腿 T9–T11 当场证）；
  ② 变异对照：只改被测模块的**那一个**开关，期望腿必须翻红，且红因点名到该腿；
  ③ 挂执行路径：本件注册进 run_gates（第 26 门），不是只在本机手跑。

**不碰真面**：全部腿都在 `mkdtemp` 合成的 05-exec / 06-benchmark / 契约上驱动真模块；
唯一的真机腿（T0）只读调用 `--gate` 取退出码，不改任何文件。
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "r58_generator_coverage.py")


def load_module(path=None):
    spec = importlib.util.spec_from_file_location("r58_generator_coverage_uut", path or TARGET)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def synth(pattern, artifact_name, scripts, self_src="", extra_patterns=None):
    """造合成工作区；scripts = {文件名: 源码}；返回 (root, mod)。"""
    root = tempfile.mkdtemp(prefix="r66_gencov_")
    scr = os.path.join(root, "05-exec")
    bench = os.path.join(root, "06-benchmark")
    sch = os.path.join(scr, "schemas", "r19")
    os.makedirs(bench)
    os.makedirs(sch)
    for name, src in scripts.items():
        with io.open(os.path.join(scr, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(src)
    if artifact_name:
        with io.open(os.path.join(bench, artifact_name), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"schema": "x"}, f)
    arts = {pattern: {"schema_id": "s", "required": [], "types": {}, "invariants": [], "note": "n"}}
    for p in (extra_patterns or []):
        arts[p] = {"schema_id": "s", "required": [], "types": {}, "invariants": [], "note": "n"}
    contract = {"schema": "r19-baseline-contracts-v1", "generated_at": "x",
                "source_of_truth": "x", "benchmark": "x",
                "artifacts": arts, "invariant_docs": {}}
    cpath = os.path.join(root, "contract.json")
    with io.open(cpath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(contract, f, ensure_ascii=False)

    mod = load_module()
    mod.ROOT = root
    mod.CONTRACT = cpath
    mod.BENCH = bench
    mod.SCRIPTS = scr
    mod.SELF_SRC = self_src or mod.SELF_SRC
    return root, mod


def run_gate(mod, argv=("--gate",)):
    buf = io.StringIO()
    old = sys.argv
    sys.argv = ["r58_generator_coverage.py"] + list(argv)
    try:
        with contextlib.redirect_stdout(buf):
            rc = mod.main()
    finally:
        sys.argv = old
    return rc, buf.getvalue()


RESULTS = []


def check(label, ok, detail=""):
    RESULTS.append((label, bool(ok), detail))
    print("  %s %s%s" % ("OK  " if ok else "FAIL", label, ("  | " + detail) if detail and not ok else ""))


def main():
    # ── T0 真机只读腿：本仓真面必须 --gate rc=0（不等于全绿，只证「接得上且当前无死句柄」）
    m = load_module()
    rc0, out0 = run_gate(m)
    check("T0 真机：本仓 --gate rc=0 且打印 [GENCOV:PASS]", rc0 == 0 and "[GENCOV:PASS]" in out0,
          "rc=%s out=%s" % (rc0, out0.strip().splitlines()[-1:]))

    # ── T1/T2 单元：外部判定的两个方向（假阳性 / 假阴性各一条，缺一不可）
    check("T1 单元：noise_falsepositive_* ⇄ noise_lint.py 必须**不**认（假阳性方向）",
          m._external_match("noise_falsepositive_", "noise_lint.py") is False)
    check("T2 单元：attention_sim_raw_* ⇄ attention_sim.py 必须认（假阴性方向）",
          m._external_match("attention_sim_raw_", "attention_sim.py") is True)
    check("T3 单元：全 token 命中档仍生效（debt_aging_* ⇄ r38_debt_aging.py）",
          m._external_match("debt_aging_r", "r38_debt_aging.py") is True)
    check("T4 单元：零 token 不得认（空词干）", m._external_match("", "anything.py") is False)

    # ── T5 单元：_norm 归一化
    check("T5 单元：_norm 剥前导 r<数字>_ 与尾部 _r",
          m._norm("r58_generator_coverage") == m._norm("generator_coverage_r") == "generator_coverage")

    # ── T6 合成：真死句柄仍被抓（这是「路 D 不许放松判据」的反向证据）
    root, mod = synth("ghost_r*.json", "ghost_r1.json",
                      {"unrelated_tool.py": "print('nothing')\n"})
    try:
        rc6, out6 = run_gate(mod)
        check("T6 合成：有件无生成器 ⇒ rc=1 且点名该 pattern",
              rc6 == 1 and "[GENCOV:FAIL]" in out6 and "ghost_r*.json" in out6,
              "rc=%s" % rc6)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # ── T7 合成：零输入（契约 artifacts 空）⇒ rc=2 不得判过（R247）
    root, mod = synth("a_r*.json", "a_r1.json", {"t.py": "print(1)\n"})
    try:
        with io.open(mod.CONTRACT, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"schema": "x", "generated_at": "x", "source_of_truth": "x",
                       "benchmark": "x", "artifacts": {}, "invariant_docs": {}}, f)
        rc7, out7 = run_gate(mod)
        check("T7 合成：零输入 ⇒ rc=2 + [GENCOV:UNVERIFIED]（禁判过）",
              rc7 == 2 and "[GENCOV:UNVERIFIED]" in out7, "rc=%s" % rc7)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # ── T8 合成：只在散文里提到 pattern、无写盘痕迹 ⇒ 不得冒充生成器（零输入之外的降级面）
    prose = "def f():\n    '''该件由 ghost_prose_r*.json 承载'''\n    return 1\n"
    root, mod = synth("ghost_prose_r*.json", "ghost_prose_r1.json", {"reader_only.py": prose})
    try:
        rc8, out8 = run_gate(mod)
        check("T8 合成：散文提及 + 无 WRITE_RX ⇒ 仍判 DEAD_HANDLE（rc=1）",
              rc8 == 1 and "ghost_prose_r*.json" in out8, "rc=%s" % rc8)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # ── T9 合成 + 变异：路 D（自产物按工具名认领）生效 → rc=0；关掉路 D → 翻红 rc=1
    #    合成面刻意让 pattern 的 core 等于 SELF 的 core（generator_coverage）
    self_src = "import json\njson.dump({}, open('out', 'w'))\n"
    root, mod = synth("generator_coverage_r*.json", "generator_coverage_r1.json",
                      {"helper.py": "print(1)\n"})
    try:
        mod.SELF = "r58_generator_coverage.py"
        mod.SELF_SRC = self_src
        rc9a, out9a = run_gate(mod)
        mod.SELF = "r58_unrelated_thing.py"      # 变异：SELF core 变了 ⇒ 路 D 不再认领
        rc9b, out9b = run_gate(mod)
        check("T9 变异：路 D 生效 rc=0 → 失配后翻成 DEAD_HANDLE rc=1",
              rc9a == 0 and "[GENCOV:PASS]" in out9a and rc9b == 1 and "[GENCOV:FAIL]" in out9b,
              "pre_rc=%s post_rc=%s" % (rc9a, rc9b))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # ── T10 变异：把最长词规则改回 all() ⇒ attention 腿必须翻红（证明该规则真在起作用）
    orig = m._external_match
    try:
        def all_only(st, basename):
            toks = [t for t in __import__("re").split(r"[^a-z]+", (st or "").lower()) if len(t) >= 3]
            return bool(toks) and all(t in basename.lower() for t in toks)
        m._external_match = all_only
        check("T10 变异：退回 all() ⇒ attention_sim_raw_* 判不认（T2 那条腿当真会红）",
              m._external_match("attention_sim_raw_", "attention_sim.py") is False)
    finally:
        m._external_match = orig

    # ── T11 反向腿：路 D 只认「归一化后完全相等」，**前缀相同但更长**的 core 不得被认领
    #    （若把相等放松成 startswith，`generator_coverage_extra_r*` 会被 SELF 冒领 ⇒ 本腿翻红）
    root, mod = synth("generator_coverage_extra_r*.json", "generator_coverage_extra_r1.json",
                      {"helper.py": "print(1)\n"})
    try:
        mod.SELF = "r58_generator_coverage.py"
        mod.SELF_SRC = self_src
        rc11, out11 = run_gate(mod)
        check("T11 反向腿：前缀同但 core 更长的 pattern 不被路 D 冒领（rc=1）",
              rc11 == 1 and "generator_coverage_extra_r*.json" in out11, "rc=%s" % rc11)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    n_ok = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    print("-" * 60)
    print("[GATE:fixture-%s] r66 generator 判据夹具 %d/%d" % ("pass" if n_ok == total else "fail", n_ok, total))
    return 0 if n_ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
