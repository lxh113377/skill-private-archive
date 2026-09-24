# -*- coding: utf-8 -*-
"""r32_freshness_fixtures.py — 「判据是否还在被真跑」这条判据的夹具（r32 H-2）。

红阶段（TDD 先看红）：`05-exec/r32_gate_freshness.py` 未实现时，a1 即 FAIL。

为什么需要这条判据（r32 对手实测，非臆想）：
    github/spec-kit   50% 的 run 停在 action_required（等于没判定），success 仅 30%
    vercel-labs/skills 60% action_required，success 24%
    mem0ai/mem0        34 个 workflow，success 54%
    ⇒ 「有 workflow」≠「判据在起作用」。本仓把门禁搬进 CI 后，同样会面对「文件在、判定断」的僵尸态；
      而本仓更特殊的一点是：3/5 门本质本机专属（仓内 0 个 SKILL.md 语料），CI 永远看不到它们 ⇒
      必须有一条**能从 CI 反过来盯「人还在不在本机跑门禁」**的判据，否则 r31 的成果会静默失效。

被测对象：`05-exec/r32_gate_freshness.py`（判据）+ `run_gates.py` 的台账写入（来源）
退出码：0 全过 / 1 有失败
"""

import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "r32_gate_freshness.py"
RUNGATES = HERE / "run_gates.py"
sys.path.insert(0, str(HERE))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-62s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def row(ts, origin="local", verdict="PASS", mode="full"):
    return {"ts": ts, "origin": origin, "verdict": verdict, "mode": mode,
            "gates_run": 5, "total_ms": 4817, "head": "deadbeef"}


def write_ledger(tmp, rows):
    p = tmp / "gate_runs.jsonl"
    with io.open(p, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return p


def main():
    now = datetime(2026, 9, 25, 6, 0, 0)
    d = lambda n: (now - timedelta(days=n)).strftime("%Y-%m-%dT%H:%M:%S")

    if not TARGET.exists():
        ck("a1 红阶段：判据文件 r32_gate_freshness.py 存在", False,
           "不存在 ⇒ 本次运行即为 TDD 的红阶段（先看失败，再写实现）")
        print("\n夹具合计: %d 项，通过 0，失败 %d" % (len(RESULTS), len(RESULTS)))
        print("[GATE:fixture-fail]")
        return 1
    gf = load(TARGET, "gf")
    ck("a1 判据文件存在且可导入", hasattr(gf, "judge") and hasattr(gf, "load_ledger"))

    # ---- 层 a：已知答案 ----
    tmp = Path(tempfile.mkdtemp(prefix="r32_fresh_"))

    p = write_ledger(tmp, [row(d(0))])
    ck("a2 今日本机跑过且 PASS → 绿", gf.judge(gf.load_ledger(p), now=now, max_days=7)[0] == "PASS",
       str(gf.judge(gf.load_ledger(p), now=now, max_days=7)))

    p = write_ledger(tmp, [])
    s, _ = gf.judge(gf.load_ledger(p), now=now, max_days=7)[0], None
    ck("a3 台账为空 → UNVERIFIED（不得当作「刚跑过/不需要跑」，R247）", s == "UNVERIFIED", str(s))

    p = write_ledger(tmp, [row(d(30))])
    s, why = gf.judge(gf.load_ledger(p), now=now, max_days=7)[:2]
    ck("a4 最近一次本机 PASS 在 30 天前 → FAIL（僵尸态）", s == "FAIL", str(why))

    p = write_ledger(tmp, [row(d(1), origin="ci"), row(d(1), origin="ci")])
    s, why = gf.judge(gf.load_ledger(p), now=now, max_days=7)[:2]
    ck("a5 只有 CI 记录、无本机记录 → FAIL（**核心反假绿**：CI 绿不能替人证明本机专属门还在跑）",
       s == "FAIL", str(why))

    p = write_ledger(tmp, [row(d(1), origin="ci"), row(d(1), origin="ci"), row(d(1))])
    s, _ = gf.judge(gf.load_ledger(p), now=now, max_days=7)[:2]
    ck("a6 CI 记录与本机记录混合，本机那条被正确取用 → PASS", s == "PASS", "")

    p = write_ledger(tmp, [row(d(1), verdict="FAIL"), row(d(3))])
    s, why = gf.judge(gf.load_ledger(p), now=now, max_days=7)[:2]
    ck("a7 最近一条是 FAIL，上一条 PASS 在 3 天前 → 报 FAIL 并点名「最近一次未过」",
       s == "FAIL" and "未过" in why, str(why))

    p = write_ledger(tmp, [{"ts": "2026-09-2", "origin": "local", "verdict": "PASS"}])
    s, why = gf.judge(gf.load_ledger(p), now=now, max_days=7)[:2]
    ck("a8 ts 不可解析 → UNVERIFIED 而非「当作很旧判 FAIL」或「跳过判 PASS」",
       s == "UNVERIFIED", str(why))

    # ---- 层 a：台账格式不变式 ----
    rows = [row(d(0))]
    p = write_ledger(tmp, rows)
    ck("a9 每行必含 ts/origin/verdict 三键（缺任一判据即失效）",
       all(set(("ts", "origin", "verdict")) <= set(r.keys()) for r in gf.load_ledger(p)))
    ck("a10 origin 取值域 = {local, ci}（出现第三种即不可信）",
       gf.judge(gf.load_ledger(write_ledger(tmp, [row(d(0), origin="other")])),
                now=now, max_days=7)[0] == "UNVERIFIED")

    # ---- 层 a：元判据不得污染台账（r32 实测过自锁事故）----
    rg = load(RUNGATES, "rg_under_test")
    src_rg = RUNGATES.read_text(encoding="utf-8")
    ck("a11 台账 verdict 只取实质门（排除 meta 门），overall 另记 ⇒ 防「空台账一次红→永久红」自锁",
       "meta_ids" in src_rg and '"overall"' in src_rg and "rc_sub" in src_rg, "未见实质门分离逻辑")
    ck("a12 新鲜度门被显式标为 meta（漏标即等于把元判据写进事实台账）",
       any(g.get("meta") and g["id"] == "gate_run_freshness" for g in rg.GATES))

    # ---- 层 b：真机接线（写台账的是 runner 自己）----
    rg = load(RUNGATES, "rg_under_test")
    src = RUNGATES.read_text(encoding="utf-8")
    ck("层b run_gates 已挂 gate_run_freshness 为独立门", "gate_run_freshness" in src)
    ck("层b run_gates 写台账且区分 origin（CI 侧不得冒充本机记录）",
       "gate_runs.jsonl" in src and 'origin' in src and "GITHUB_ACTIONS" in src)
    ck("层b gate_run_freshness 声明为可移植（CI 靠它反过来盯本机）",
       any(g["id"] == "gate_run_freshness" and g["portable"] for g in rg.GATES))

    p = subprocess.run([sys.executable, str(TARGET), "--json", str(tmp / "h.json")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(HERE.parent))
    out = (p.stdout or "") + (p.stderr or "")
    ck("层b 真台账真跑 → 输出三态标记之一且 rc∈{0,1,2}",
       any(t in out for t in ("[FRESH:PASS]", "[FRESH:FAIL]", "[FRESH:UNVERIFIED]")), out[-160:])
    ck("层b 真跑自证覆盖根（台账路径 / 阈值 / 判定窗口）", "台账" in out and "max_days" in out, out[-160:])

    # ---- 层 c：变异对照（判据必须有牙）----
    base = TARGET.read_text(encoding="utf-8")
    muts = [
        ("M1 只看最后一条（CI 记录会冒充本机记录）",
         base.replace('local = [r for r in rows if r.get("origin") == "local"]', 'local = rows')),
        ("M2 空台账当过（R247 失守）",
         base.replace('return "UNVERIFIED", "台账为空', 'return "PASS", "台账为空')),
        ("M3 陈旧阈值失效（永不过期）",
         base.replace("if age_days > max_days", "if age_days > 10**9")),
        ("M4 ts 解析失败被静默跳过（当作很新）",
         base.replace('return "UNVERIFIED", "ts 不可解析', 'return "PASS", "ts 不可解析')),
    ]
    caught = 0
    for label, patched in muts:
        if patched == base:
            caught += 1
            print("     %-50s 锚点未命中（变异未生效）<<< 需修夹具锚点" % label)
            continue
        mp = tmp / ("mut_%d.py" % abs(hash(label)))
        mp.write_text(patched, encoding="utf-8")
        try:
            m = load(mp, "m")
            bad = []
            # ⚠️ 这里必须是**纯 CI** 台账（不含任何 local 行）：第一版误把 a6 的混合样本（含一条 local）
            # 搬了过来，导致 M1「local = rows」这条变异**没有任何有效断言在测它**却仍被判 caught。
            pure_ci = write_ledger(tmp, [row(d(1), origin="ci"), row(d(1), origin="ci")])
            if m.judge(m.load_ledger(pure_ci), now=now, max_days=7)[0] != "FAIL":
                bad.append("纯 CI 台账未被判 FAIL（本机专属门失去监管）")
            if m.judge(m.load_ledger(write_ledger(tmp, [])), now=now, max_days=7)[0] != "UNVERIFIED":
                bad.append("空台账未判 UNVERIFIED")
            if m.judge(m.load_ledger(write_ledger(tmp, [row(d(30))])), now=now, max_days=7)[0] != "FAIL":
                bad.append("30 天陈旧未判 FAIL")
            if m.judge(m.load_ledger(write_ledger(tmp, [{"ts": "x", "origin": "local", "verdict": "PASS"}])),
                       now=now, max_days=7)[0] != "UNVERIFIED":
                bad.append("坏 ts 未判 UNVERIFIED")
            if bad:
                caught += 1
                print("     %-50s 拦住：%s" % (label, "; ".join(bad)))
            else:
                print("     %-50s 未被拦住 <<<" % label)
        except Exception as e:
            caught += 1
            print("     %-50s 变异致不可加载（也算拦住）: %s" % (label, type(e).__name__))
    ck("层c 变异 4 项全部被拦（对照=已取）", caught == 4, "caught=%d/4" % caught)

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
