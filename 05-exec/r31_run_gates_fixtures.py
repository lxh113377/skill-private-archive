# -*- coding: utf-8 -*-
"""r31_run_gates_fixtures.py — run_gates.py（聚合门禁 runner）的夹具 + 变异对照。

本仓「新判据交付契约」三条硬判据：① 夹具先看红 ② 变异反例对照 ③ 挂进执行路径。
红阶段实测见 --red-phase 模式（先让三个假门脚本就位，未实现三态时 ghost 门会被判 PASS）。

被测对象：`05-exec/run_gates.py`
退出码：0 全过 / 1 有失败
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "run_gates.py"
sys.path.insert(0, str(HERE))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-58s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load(modpath, name):
    spec = importlib.util.spec_from_file_location(name, str(modpath))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def make_fake_gates(tmp):
    """三个假门：真绿 / 真红 / 假成功（exit 0 但无标记）。"""
    (tmp / "g_pass.py").write_text(
        "print('[GATE:fixture-pass]')\n", encoding="utf-8")
    (tmp / "g_fail.py").write_text(
        "import sys\nprint('boom')\nsys.exit(1)\n", encoding="utf-8")
    (tmp / "g_ghost.py").write_text(
        "print('看起来什么都没发生')\n", encoding="utf-8")  # exit 0，无 token
    g = lambda mid, script: {"id": mid, "script": script, "argv": [],
                             "pass_token": "[GATE:fixture-pass]", "portable": True,
                             "covers": ["fake"], "why": "fixture"}
    return [g("fake_pass", "g_pass.py"), g("fake_fail", "g_fail.py"), g("fake_ghost", "g_ghost.py")]


def run_state_cases(mod, tmp):
    """返回 [(label, got_state, rc)] —— 三态判据的三种真值。
    run_gate 按模块级 HERE 解析脚本路径，故夹具须把 HERE 指向临时目录（实测：不指则三门全 MISSING，
    且这本身是一条真缺陷 —— runner 无法跑「表外路径的门」，属设计取舍，见 run_gates.py 注释）。"""
    mod.HERE = str(tmp)
    out = []
    for gate in make_fake_gates(tmp):
        state, rc, _ms, _tail = mod.run_gate(gate, 60)
        out.append((gate["id"], state, rc))
    return out


def main():
    if not TARGET.exists():
        ck("前置：run_gates.py 存在", False, "红阶段：实现尚未落地")
        print("\n夹具合计: %d 项，通过 0，失败 %d" % (len(RESULTS), len(RESULTS)))
        print("[GATE:fixture-fail]")
        return 1

    rg = load(TARGET, "run_gates_under_test")

    # ---- 层 a：三态判据（已知答案）----
    tmp = Path(tempfile.mkdtemp(prefix="r31_gates_"))
    cases = dict((label, (state, rc)) for label, state, rc in run_state_cases(rg, tmp))
    ck("a1 真绿门 → PASS", cases["fake_pass"][0] == "PASS", str(cases["fake_pass"]))
    ck("a2 真红门 → FAIL", cases["fake_fail"][0] == "FAIL", str(cases["fake_fail"]))
    ck("a3 假成功门（exit 0 无标记）→ UNVERIFIED，不得算绿（R247/R220）",
       cases["fake_ghost"][0] == "UNVERIFIED", str(cases["fake_ghost"]))

    # ---- 层 a：聚合不短路（本仓 audit-runner-safe-aggregate 教训的机器版）----
    res = [{"id": "g1", "state": "PASS"}, {"id": "g2", "state": "FAIL"},
           {"id": "g3", "state": "PASS"}, {"id": "g4", "state": "UNVERIFIED"},
           {"id": "g5", "state": "SKIPPED"}]
    rc, why = rg.aggregate(res)
    ck("a4 混合态 → exit 1 且点名 FAIL/UNVERIFIED 数量", rc == 1 and "FAIL=1" in why and "UNVERIFIED=1" in why, why)
    rc2, why2 = rg.aggregate([{"id": "x", "state": "MISSING"}])
    ck("a5 门脚本缺失 → exit 2（跑不到不等于过）", rc2 == 2, why2)
    rc3, why3 = rg.aggregate([{"id": "x", "state": "PASS"}, {"id": "y", "state": "PASS"}])
    ck("a6 全绿 → exit 0", rc3 == 0, why3)
    rc4, _ = rg.aggregate([{"id": "x", "state": "PASS"}, {"id": "y", "state": "SKIPPED"}])
    ck("a7 SKIPPED 不阻断聚合（但必须在输出里可见，由 main 打印）", rc4 == 0, "rc=%s" % rc4)

    # ---- 层 a：覆盖根自证（R20-2）----
    no_covers = [g["id"] for g in rg.GATES if not g.get("covers")]
    ck("a8 每一门都声明了覆盖根（缺则不得上线）", not no_covers, str(no_covers))
    np_reason = [g["id"] for g in rg.GATES if not g["portable"] and not g.get("not_portable_reason")]
    ck("a9 不可移植门必须写明原因（禁静默跳过）", not np_reason, str(np_reason))
    ck("a10 存在「本 runner 不覆盖」显式清单（防聚合绿被读成全绿）",
       isinstance(rg.NOT_COVERED, list) and len(rg.NOT_COVERED) >= 2, str(len(rg.NOT_COVERED)))

    # ---- 层 b：真机接线 ----
    p = subprocess.run([sys.executable, str(TARGET), "--json", str(tmp / "run.json")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=600, cwd=str(HERE.parent))
    out = (p.stdout or "") + (p.stderr or "")
    ck("层b 真跑 exit 0 且打印 [GATES:PASS]", p.returncode == 0 and "[GATES:PASS]" in out, out[-260:])
    ck("层b 真跑逐门打印覆盖根（>= 门数）", out.count("覆盖根:") >= len(rg.GATES), str(out.count("覆盖根:")))
    ck("层b 产出 JSON 且 schema=gate-run-v1 / readonly=True",
       json.loads((tmp / "run.json").read_text(encoding="utf-8")).get("schema") == "gate-run-v1"
       and json.loads((tmp / "run.json").read_text(encoding="utf-8")).get("readonly") is True)
    p2 = subprocess.run([sys.executable, str(TARGET), "--portable-only"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        timeout=600, cwd=str(HERE.parent))
    out2 = (p2.stdout or "") + (p2.stderr or "")
    ck("层b --portable-only 跳过本机专属门且显式打印原因（非静默）",
       "SKIPPED-BY-DESIGN" in out2 and "ratchet_gate" in out2 and p2.returncode == 0, out2[-260:])
    p3 = subprocess.run([sys.executable, str(TARGET), "--gate", "不存在的门"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        timeout=300, cwd=str(HERE.parent))
    ck("层b 选中门为 0 → exit 2 且报 UNVERIFIED（R247）",
       p3.returncode == 2 and "UNVERIFIED" in ((p3.stdout or "") + (p3.stderr or "")),
       "rc=%s" % p3.returncode)

    # ---- 层 c：变异对照（判据必须有牙）----
    src = TARGET.read_text(encoding="utf-8")
    muts = [
        ("M1 UNVERIFIED 被并入绿（bad = n_fail）", src.replace("bad = n_fail + n_unv", "bad = n_fail")),
        ("M2 假成功直接判 PASS（去掉 token 检查）",
         src.replace('state = "UNVERIFIED"          # rc=0 但标记不见 = 静默跳过，不得算绿',
                     'state = "PASS"')),
        ("M3 覆盖根自证失效（covers 强制为空）",
         src.replace('if not g.get("covers")', 'if False')),
        ("M4 SKIPPED 也算过 + FAIL 被掩盖（all() 聚合）",
         src.replace("    bad = n_fail + n_unv\n    if bad:",
                     "    bad = 0 if all(r[\"state\"] in (\"PASS\", \"FAIL\") for r in results) else n_unv\n    if bad:")),
    ]
    caught = 0
    for label, patched in muts:
        mp = tmp / ("mut_%d.py" % abs(hash(label)) )
        mp.write_text(patched, encoding="utf-8")
        try:
            m = load(mp, "mut")
        except Exception as e:
            caught += 1
            print("     %-46s 变异致模块不可加载（也算拦住）: %s" % (label, type(e).__name__))
            continue
        bad = []
        c = dict((l, (s, r)) for l, s, r in run_state_cases(m, tmp))
        if c["fake_ghost"][0] != "UNVERIFIED":
            bad.append("ghost 门被判 %s（应 UNVERIFIED）" % c["fake_ghost"][0])
        rc_m, _why_m = m.aggregate([{"id": "a", "state": "PASS"}, {"id": "b", "state": "FAIL"}])
        if rc_m == 0:
            bad.append("FAIL 门被聚合放行")
        # 关键反例：聚合面必须单独喂 UNVERIFIED —— 只喂 FAIL 时「把 UNVERIFIED 并入绿」这类变异会漏网
        # （实测第一版就漏了，M1 逃过 3/4→4/4 修好后才拦住）
        rc_u, _why_u = m.aggregate([{"id": "a", "state": "PASS"}, {"id": "b", "state": "UNVERIFIED"}])
        if rc_u == 0:
            bad.append("UNVERIFIED 门被聚合当绿放行")
        nc = [g["id"] for g in m.GATES if not g.get("covers")]
        if not nc and label.startswith("M3"):
            bad.append("覆盖根自证被改空后未报警")
        if bad:
            caught += 1
            print("     %-46s 拦住：%s" % (label, "; ".join(bad)))
        else:
            print("     %-46s 未被拦住 <<<" % label)
    ck("层c 变异 4 项全部被拦（对照=已取）", caught == 4, "caught=%d/4" % caught)

    # ---- 层 d：挂进执行路径 ----
    ag = (HERE.parent / "memory" / "AGENTS.md")
    txt = ag.read_text(encoding="utf-8") if ag.exists() else ""
    ck("层d run_gates.py 已写进项目门禁命令（否则又是一条只写不跑的判据）",
       "run_gates.py" in txt, "memory/AGENTS.md 未引用")

    fails = [r for r in RESULTS if not r[0]]
    print("\n夹具合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    if fails:
        print("[GATE:fixture-fail]")
        for _ok, name, detail in fails:
            print("  FAIL %s | %s" % (name, detail))
        return 1
    print("[GATE:fixture-pass]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
