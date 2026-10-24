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




def _gate_src(name, tail_line, exit_code, flaky=False):
    """造一个会自计次数的假门脚本：计数器文件记录它真被跑了几次（行为级取证，不看代码）。"""
    NL = chr(10)
    q = chr(34)
    lines = [
        "import os, sys",
        "D = os.path.dirname(os.path.abspath(__file__))",
        "CNT = os.path.join(D, " + q + name + ".cnt" + q + ")",
        "k = 0",
        "if os.path.isfile(CNT):",
        "    k = int(open(CNT).read().strip() or 0)",
        "open(CNT, " + q + "w" + q + ").write(str(k + 1))",
    ]
    if flaky:
        lines.append("if k == 0:")
        lines.append("    print(" + q + "boom on first run" + q + ")")
        lines.append("    sys.exit(2)")
        lines.append("print(" + q + "[GATE:fixture-pass]" + q + ")")
        lines.append("sys.exit(0)")
    else:
        lines.append("print(" + q + tail_line + q + ")")
        lines.append("sys.exit(%d)" % exit_code)
    return NL.join(lines) + NL


def run_retry_cases(mod, tmpdir):
    """重试分流 + FLAKY rc 的行为级取证：四类门各跑一次，用计数器判重跑与否。

    存在理由（r201）：本轮我反复打 Cloudflare GraphQL 建门把配额耗光，runner 的
    「非 PASS 一律退避 3 秒重跑一次」把一次探测放大成两次，三门同轮 UNVERIFIED。
    上一轮我只在 TEMP 里写了 8 个纯函数用例 —— 件已随清场消失（正是本仓登记过的
    「临时自证 = 没有自证」）。故改为常驻行为级腿：测的是真 subprocess 跑了几次。
    """
    tmp = str(tmpdir)
    if not os.path.isdir(tmp):
        os.makedirs(tmp)
    specs = [
        ("quota", "q_gate.py",
         "Rate limiter budget depleted. Please try again after 5 minutes", 2, False, False),
        ("transient", "t_gate.py",
         "URLError SSLEOFError EOF occurred in violation of protocol", 2, False, False),
        ("flaky", "f_gate.py", "", 2, True, False),
        ("nretry", "n_gate.py",
         "URLError SSLEOFError EOF occurred in violation of protocol", 2, False, True),
    ]
    out = {}
    for key, script, tail, code, flaky, nretry in specs:
        open(os.path.join(tmp, script), "w", encoding="utf-8", newline="").write(
            _gate_src(script, tail, code, flaky))
        gate = {"id": key, "script": script, "argv": [],
                "pass_token": "[GATE:fixture-pass]", "portable": True,
                "covers": ["fake"], "why": "fixture"}
        if nretry:
            gate["no_retry"] = True
        mod.HERE = tmp
        state, rc, _ms, _tail = mod.run_gate(gate, 60)
        cp = os.path.join(tmp, script + ".cnt")
        cnt = int(open(cp).read().strip() or 0) if os.path.isfile(cp) else 0
        out[key] = {"state": state, "rc": rc, "count": cnt}
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
    # ---- 层 a：重试分流 + FLAKY rc 自证（r201 立）----
    # 配额类确定性拒绝不得重跑（重跑必再失败且白烧配额）；网络瞬态照旧重跑一次
    # （R125 竞态识别不放宽）；FLAKY 转 PASS 时 rc 必须是**决定该状态那一次**的值。
    rtry = run_retry_cases(rg, tmp / "retry_a")
    ck("a11 配额类确定性拒绝不重跑（一次探测就是一次，禁放大回路）",
       rtry["quota"]["count"] == 1 and rtry["quota"]["state"] == "UNVERIFIED",
       str(rtry["quota"]))
    ck("a12 网络瞬态照旧重跑一次（R125 竞态识别不放宽）",
       rtry["transient"]["count"] == 2, str(rtry["transient"]))
    ck("a13 FLAKY 转 PASS 时 rc 必须是第二次实跑值（禁 PASS 配 rc=2）",
       rtry["flaky"]["state"] == "PASS" and rtry["flaky"]["rc"] == 0, str(rtry["flaky"]))
    ck("a14 门显式声明 no_retry 优先于分流（门说别再跑就不跑）",
       rtry["nretry"]["count"] == 1, str(rtry["nretry"]))

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
        # M3 已撤（r201）：原锚 'if not g.get("covers")' 不在 run_gates.py 内
        # （covers 强制只存在于本夹具 a8 那一行），replace 恒为 no-op ⇒ 该锁空转多轮。
        # 要重加须先给 runner 一个真正的 covers 强制点，再针对它写变异。
        ("M4 SKIPPED 也算过 + FAIL 被掩盖（all() 聚合）",
         src.replace("    bad = n_fail + n_unv\n    if bad:",
                     "    bad = 0 if all(r[\"state\"] in (\"PASS\", \"FAIL\") for r in results) else n_unv\n    if bad:")),
        ("M5 配额分流失效（_quota_limited 恒 False）⇒ 放大回路复活",
         src.replace("    return any(k in low for k in QUOTA_SIGNALS)", "    return False")),
        ("M6 FLAKY 转 PASS 仍报首跑 rc（r201 修过的自相矛盾）",
         src.replace('return "PASS", rc2, elapsed + el2, (',
                     'return "PASS", p.returncode, elapsed + el2, (')),
    ]
    caught = 0
    for label, patched in muts:
        # r201 加 no-op 守卫（一手：M3 的锚 'if not g.get("covers")' 在
        # run_gates.py 里根本不存在 —— covers 强制实际只在夹具自己的 a8 行。于是
        # src.replace(...) 静默无效、变异体 == 原体，而循环里那条
        # 'if not nc and label.startswith("M3")' 恰好把 no-op 记成"拦住"，
        # 这条锁已空转多轮。原则：变异测试必须先自证"变异真的改到了源码"，
        # 否则它测的是空气，却给出一个通过的计数。
        if patched == src:
            print("     %-46s 锚未命中任何源码 ⇒ 本条变异无效（夹具缺陷，不算拦住）"
                  % label)
            continue
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
        # （原 M3 特判已随 M3 一并撤除：它把 no-op 记成拦住）
        if label.startswith(("M5", "M6")):
            c2 = run_retry_cases(m, os.path.join(str(tmp), "retry_" + label[:2]))
            if label.startswith("M5") and c2["quota"]["count"] != 1:
                bad.append("配额类被重跑（放大回路复活）count=%s" % c2["quota"]["count"])
            if label.startswith("M6") and not (c2["flaky"]["state"] == "PASS"
                                               and c2["flaky"]["rc"] == 0):
                bad.append("FLAKY 转 PASS 但 rc 非第二次实跑值 rc=%s" % c2["flaky"]["rc"])
        if bad:
            caught += 1
            print("     %-46s 拦住：%s" % (label, "; ".join(bad)))
        else:
            print("     %-46s 未被拦住 <<<" % label)
    ck("层c 变异 5 项全部被拦（对照=已取；M5/M6 为 r201 新增，M3 因空锁被撤）", caught == 5, "caught=%d/5" % caught)

    # ---- 层 d：挂进执行路径 ----
    ag = (HERE.parent / "memory" / "AGENTS.md")
    txt = ag.read_text(encoding="utf-8") if ag.exists() else ""
    ck("层d run_gates.py 已写进项目门禁命令（否则又是一条只写不跑的判据）",
       "run_gates.py" in txt, "memory/AGENTS.md 未引用")

    # ---- 层 e：r105 pass_token 列表化（一门多合法绿态时不得把具名看守读成 UNVERIFIED）----
    th = getattr(rg, "_token_hit", None)
    ck("e1 判据存在性：run_gates 暴露 _token_hit（缺则本层未接线）", callable(th), type(th).__name__)
    if callable(th):
        ck("e2 正例 列表：rc=0 且输出含 -watch ⇒ 命中（r105 一手：单串比对把这判成 UNVERIFIED）",
           th(["[GATE:retired-face-pass]", "[GATE:retired-face-watch]"],
              "[GATE:retired-face-watch] 2 retired skill(s) still on disk") is True, "n/a")
        ck("e3 反例 列表：两个标记都不在输出里 ⇒ 仍不命中（列表不得用来掩盖改名/静默跳过，R247）",
           th(["[GATE:retired-face-pass]", "[GATE:retired-face-watch]"], "Traceback ...") is False, "n/a")
        ck("e4 向后兼容：单串形态行为与旧 `in` 判定逐字一致",
           (th("[X:PASS]", "a [X:PASS] b") is True and th("[X:PASS]", "nothing") is False), "n/a")
        ck("e5 反例 空列表不得恒真（空面不能当「匹配上了」）",
           th([], "anything at all") is False, "n/a")
        _g = [x for x in rg.GATES if x["id"] == "retired_face"]
        ck("e6 接线：retired_face 门的 pass_token 现值确实含两个标记（不是只加了夹具没改门）",
           len(_g) == 1 and isinstance(_g[0]["pass_token"], list)
           and "[GATE:retired-face-watch]" in _g[0]["pass_token"],
           str(_g[0]["pass_token"]) if _g else "gate 不在表")

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
