# -*- coding: utf-8 -*-
r"""r39_debt_ledger_fixtures.py — 账龄**趋势台账**的夹具（TDD：先看红，再实现）。

W-3（r38 立）：`r38_debt_aging.py` 只会报当期值，看不到**斜率**，
棘轮也就无法区分「这轮涨了」与「一直在涨」。对位本仓已有的 `06-benchmark/gate_runs.jsonl`
（r32 第 6 门靠它盯人），本轮给债务也建一条 run 台账。

被测对象：`05-exec/r38_debt_aging.py::append_ledger(path, doc, origin)`
期望行为：
  1) 每次实跑**追加一行**（append-only，last-wins），字段含 ts/origin/open_total/overdue/undated/head/grace_rounds；
  2) **自洽校验不过 ⇒ 一行都不写**（分类之和 != open_total 时禁把脏数据写进趋势线，R247）；
  3) 台账行必须能被契约校验器的 jsonl 分支逐字段接受（取值域封闭：origin 只允许 local/ci）；
  4) 已存在的台账不得被覆盖（防"重写历史趋势"）。
退出码：0 全过 / 1 有失败（含实现未落地时的红阶段）
"""

import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-54s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load_aging():
    spec = importlib.util.spec_from_file_location("r38da", str(HERE / "r38_debt_aging.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def doc(by, open_total=10, head="abc1234"):
    return {"generated_at": "2026-09-25T11:00:00", "grace_rounds": 2, "current_round": 39,
            "evidence": {"open_total": open_total}, "by_class": by,
            "schema": "debt-aging-v1"}


def main():
    da = load_aging()
    if not hasattr(da, "append_ledger"):
        ck("RED 前置：r38_debt_aging 暴露 append_ledger", False,
           "函数不存在 —— 本次运行即 TDD 红阶段（先看失败再实现）")
        print("\n夹具合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), 0, len(RESULTS)))
        print("[GATE:fixture-fail]")
        return 1

    tmp = Path(tempfile.mkdtemp(prefix="r39_ledger_"))
    led = tmp / "debt_runs.jsonl"

    good = doc({"OVERDUE": 4, "ACTIVE": 3, "DECIDED": 2, "UNDATED": 1})
    n = da.append_ledger(str(led), good, origin="local")
    rows = [json.loads(x) for x in io.open(led, encoding="utf-8").read().splitlines() if x.strip()]
    ck("t1 自洽通过 → 写 1 行且返回写入数", n == 1 and len(rows) == 1, str(rows)[:180])
    ck("t2 行含全部必填字段",
       all(k in rows[0] for k in ("ts", "origin", "open_total", "overdue", "undated",
                                  "active", "decided", "head", "grace_rounds")), str(rows[0])[:200])
    ck("t3 数值取自 by_class 而非再算一遍", rows[0]["overdue"] == 4 and rows[0]["undated"] == 1,
       str(rows[0])[:160])

    da.append_ledger(str(led), doc({"OVERDUE": 2, "ACTIVE": 4, "DECIDED": 3, "UNDATED": 1}), origin="local")
    rows2 = [json.loads(x) for x in io.open(led, encoding="utf-8").read().splitlines() if x.strip()]
    ck("t4 append-only：第二次跑变 2 行且首行未被改写",
       len(rows2) == 2 and rows2[0]["overdue"] == 4 and rows2[1]["overdue"] == 2, str(rows2)[:200])

    before = io.open(led, encoding="utf-8").read()
    n3 = da.append_ledger(str(led), doc({"OVERDUE": 9, "ACTIVE": 9, "DECIDED": 0, "UNDATED": 0},
                                        open_total=10), origin="local")
    ck("t5 分类之和(18) != open_total(10) → 一行都不写",
       n3 == 0 and io.open(led, encoding="utf-8").read() == before, "ret=%s" % n3)
    n4 = da.append_ledger(str(led), doc({"OVERDUE": 1, "ACTIVE": 1}), origin="local")
    ck("t6 缺 ACTIVE/UNDATED 键（分类面不完整）→ 拒写而非按 0 补", n4 == 0, "ret=%s" % n4)
    ck("t7 取值域外 origin 拒写（防伪造 CI 记录）",
       da.append_ledger(str(led), good, origin="ci-typo") == 0,
       str(da.append_ledger(str(led), good, origin="ci-typo")))

    # 与契约校验器真接线：台账必须能被 jsonl 分支逐字段接受
    rep = tmp / "r.json"
    p = subprocess.run([sys.executable, str(HERE / "baseline_contract_scan.py"),
                        "--dir", str(tmp), "--json", str(rep)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=300)
    out = (p.stdout or "") + (p.stderr or "")
    row = next((a for a in json.loads(io.open(rep, encoding="utf-8").read()).get("artifacts", [])
                if a.get("glob") == "debt_runs.jsonl"), None)
    ck("t8 契约里有 debt_runs.jsonl pattern 且命中 1 个文件",
       row is not None and row.get("files") == 1, str(row) + out[-160:])
    ck("t9 契约逐字段接受台账（violations == 0）",
       row is not None and row.get("violations") == 0, str(row)[:200])
    # 反例：往台账塞一行越界 origin，契约必须点名
    with io.open(led, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": "2026-09-25T11:30:00", "origin": "robot",
                            "open_total": 10, "overdue": 1, "active": 1, "decided": 1,
                            "undated": 1, "head": "deadbee", "grace_rounds": 2}) + "\n")
    rep2 = tmp / "r2.json"
    subprocess.run([sys.executable, str(HERE / "baseline_contract_scan.py"),
                    "--dir", str(tmp), "--json", str(rep2)],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    row2 = next((a for a in json.loads(io.open(rep2, encoding="utf-8").read()).get("artifacts", [])
                 if a.get("glob") == "debt_runs.jsonl"), {})
    det = json.loads(io.open(rep2, encoding="utf-8").read()).get("violations_detail", [])
    ck("t10 反例：越界 origin 的一行必被契约拦住并点名取值域",
       row2.get("violations", 0) > 0 and any("origin" in x for x in det), str(det)[:220])

    # --- r39 W-0 前置：延期(挂账至 rNN) 不得冒充"已裁决"，且到期必须反判红 ---
    now = 39
    c, d1 = da.classify_item("【待办 X（r31 登记）】 还欠着 【r39 账龄裁决=挂账至 r41｜等他人在途】", now)
    ck("t11 挂账至未来轮 → DEFERRED（不并入 DECIDED 蒙混过关）", c == "DEFERRED", "%s %s" % (c, d1))
    c2, d2 = da.classify_item("【待办 Y（r31 登记）】 【r38 账龄裁决=挂账至 r39｜到期未动】", now)
    ck("t12 挂账目标已到（目标轮 == 本轮）→ 重新 OVERDUE（到期追讨）",
       c2 == "OVERDUE", "%s %s" % (c2, d2))
    c2b, d2b = da.classify_item("【待办 Y2（r31 登记）】 【r38 账龄裁决=挂账至 r37｜早已过期】", now)
    ck("t12b 挂账目标已过轮 → OVERDUE", c2b == "OVERDUE", "%s %s" % (c2b, d2b))
    c3, d3 = da.classify_item("【待办 Z（r31 登记）】 【r38 账龄裁决=作废｜实测已闭环】", now)
    ck("t13 终局裁决（作废）→ DECIDED", c3 == "DECIDED", "%s %s" % (c3, d3))
    ck("t14 分类枚举必须含 DEFERRED（五态之和才等于总数）",
       "DEFERRED" in da.TAXONOMY, str(da.TAXONOMY))
    led2 = tmp / "debt_runs2.jsonl"
    n5 = da.append_ledger(str(led2), doc({"OVERDUE": 1, "ACTIVE": 1, "DECIDED": 1, "UNDATED": 1,
                                          "DEFERRED": 6}, open_total=10), origin="local")
    rowd = (json.loads(io.open(led2, encoding="utf-8").read().splitlines()[0])
            if os.path.exists(led2) and io.open(led2, encoding="utf-8").read().strip() else {})
    ck("t15 台账行须承载 deferred 计数（趋势线要能区分延期与终局）",
       n5 == 1 and rowd.get("deferred") == 6, "%s %s" % (n5, str(rowd)[:150]))
    ck("t16 反例：五态之和 != open_total 仍须拒写",
       da.append_ledger(str(led2), doc({"OVERDUE": 1, "ACTIVE": 1, "DECIDED": 1, "UNDATED": 1,
                                         "DEFERRED": 9}, open_total=10), origin="local") == 0, "")

    # --- r39 自纠：棘轮指标不得把证据件轮次写死在 glob 里 ---
    import importlib.util as ilu
    rg_spec = ilu.spec_from_file_location("rg39", str(HERE / "ratchet_gate.py"))
    rg = ilu.module_from_spec(rg_spec)
    rg_spec.loader.exec_module(rg)
    bench = tmp / "bench"
    bench.mkdir()
    def ev(name, overdue):
        io.open(bench / name, "w", encoding="utf-8", newline="").write(json.dumps(
            {"schema": "debt-aging-v2", "grace_rounds": 2, "current_round": 39,
             "evidence": {"open_total": 56},
             "by_class": {"OVERDUE": overdue, "ACTIVE": 9, "DECIDED": 11,
                          "UNDATED": 13, "DEFERRED": 56 - overdue - 9 - 11 - 13}}))
    ev("debt_aging_r38_2026-09-25.json", 22)
    ev("debt_aging_r39_2026-09-25.json", 0)
    rg.BENCH = bench
    import time
    old_v = rg.overdue_debt_items()
    time.sleep(1.1)
    ev("debt_aging_r40_2026-09-25.json", 7)
    new_v = rg.overdue_debt_items()
    ck("t17 指标读最新一份证据件（轮次不得写死在 glob 里）",
       (old_v, new_v) == (0, 7), "old=%s new=%s" % (old_v, new_v))
    io.open(bench / "debt_aging_r41_x.json", "w", encoding="utf-8", newline="").write(json.dumps(
        {"evidence": {"open_total": 3},
         "by_class": {"OVERDUE": 9, "ACTIVE": 9, "DECIDED": 9, "UNDATED": 9, "DEFERRED": 9}}))
    ck("t19 最新一份四态之和 != open_total → 指标 None（脏证据不得放行）",
       rg.overdue_debt_items() is None, str(rg.overdue_debt_items()))

    # --- r40 W-4：延期堆必须有**独立**回归保护，否则"换个地方堆债"无人看守 ---
    bench3 = tmp / "bench3"
    bench3.mkdir()
    def ev3(name, overdue, deferred):
        """合成**自洽**证据件：open_total 恒等于五态之和（否则测的是 fail-closed 而非跟涨）。"""
        by = {"OVERDUE": overdue, "ACTIVE": 9, "DECIDED": 11, "UNDATED": 13, "DEFERRED": deferred}
        io.open(bench3 / name, "w", encoding="utf-8", newline="").write(json.dumps(
            {"schema": "debt-aging-v2", "evidence": {"open_total": sum(by.values())},
             "by_class": by}))
    ev3("debt_aging_r39_a.json", 0, 23)
    rg.BENCH = bench3
    ck("t20 ratchet_gate 暴露第 8 指标 deferred_debt_items", hasattr(rg, "deferred_debt_items"), "")
    ck("t21 METRIC_NAMES 含 deferred_debt_items（否则指标不进棘轮=白写）",
       "deferred_debt_items" in rg.METRIC_NAMES, str(rg.METRIC_NAMES))
    ck("t22 取值正确：读最新证据件的 DEFERRED 态",
       getattr(rg, "deferred_debt_items", lambda: None)() == 23,
       str(getattr(rg, "deferred_debt_items", None)))
    import time as _tm
    ev3("debt_aging_r40_b.json", 5, 30)
    _tm.sleep(1.1)
    ck("t23 反例：延期堆增长时指标如实跟涨（不沿用旧值）",
       getattr(rg, "deferred_debt_items", lambda: None)() == 30, "")
    io.open(bench3 / "debt_aging_r41_c.json", "w", encoding="utf-8", newline="").write(json.dumps(
        {"schema": "debt-aging-v2", "evidence": {"open_total": 40},
         "by_class": {"OVERDUE": 1, "ACTIVE": 1, "DECIDED": 1, "UNDATED": 1, "DEFERRED": 1}}))
    ck("t25 脏证据（之和 != open_total）→ deferred 指标同样 None（与 overdue 同等 fail-closed）",
       rg.deferred_debt_items() is None if hasattr(rg, "deferred_debt_items") else False, "")

    # --- r41 W-8 真根因：一行有多个裁决标记时必须取最新（last-wins），不得被旧挂账劫持 ---
    two = ("【P0·待办 X（r31 登记）】 正文 "
           "【r38 账龄裁决=挂账至 r40｜当时阻塞】 【r41 裁决=作废（被 r35 分类取代）】")
    c8, d8 = da.classify_item(two, 41)
    ck("t26 W-8 反例：旧挂账 + 新终局裁决 → 取最新 DECIDED（last-wins）",
       c8 == "DECIDED", "%s %s" % (c8, d8))
    two2 = ("【P0·待办 Y（r31 登记）】 【r38 账龄裁决=作废】 【r41 裁决=挂账至 r44｜探针未建】")
    c9, d9 = da.classify_item(two2, 41)
    ck("t27 反例方向相反：新标记是延期 → 最新为准判 DEFERRED（不得被旧作废豁免）",
       c9 == "DEFERRED", "%s %s" % (c9, d9))
    two3 = ("【P0·待办 Z（r31 登记）】 【r40 裁决=挂账至 r41｜到期未动】")
    c10, d10 = da.classify_item(two3, 41)
    ck("t28 目标轮 == 本轮即到期（不是宽限一轮）", c10 == "OVERDUE", "%s %s" % (c10, d10))

    # --- r42 反"延期 treadmill"：多次改期必须显形；宽限期须按优先级分档 ---
    two_def = ("【P0·待办 A（r31 登记）】 正文 【r38 账龄裁决=挂账至 r40｜旧】 "
               "【r40 裁决=挂账至 r41｜中】 【r41 裁决=挂账至 r44｜新】")
    c1, d1 = da.classify_item(two_def, 42)
    ck("t30 同一条被改期 3 次 → 判 REPEAT（延期堆不得静默滚动）",
       c1 == "REPEAT", "%s %s" % (c1, d1))
    one_def = "【P0·待办 B（r41 登记）】 【r41 裁决=挂账至 r44｜首次延期】"
    c2, d2 = da.classify_item(one_def, 42)
    ck("t31 反例：只延期 1 次仍算 DEFERRED（不一刀切惩罚）", c2 == "DEFERRED", "%s %s" % (c2, d2))
    ck("t32 REPEAT 必须进分类枚举（五态之和才等于总数）", "REPEAT" in da.TAXONOMY, str(da.TAXONOMY))
    p0_over = "【P0·待办 C（r38 登记）】 账龄 3 轮仍未动"
    c3, _ = da.classify_item(p0_over, 42)
    c4, _ = da.classify_item(p0_over.replace("P0", "P2"), 42)
    ck("t33 宽限期按优先级分档：P0 超 2 轮即 OVERDUE、P2 3 轮仍 ACTIVE",
       (c3, c4) == ("OVERDUE", "ACTIVE"), "%s %s" % (c3, c4))
    ck("t34 GRACE 分档表可读（值不写死在函数体内）", isinstance(getattr(da, "GRACE_BY_PRIORITY", None), dict),
       str(getattr(da, "GRACE_BY_PRIORITY", None)))

    # --- r44 W-13 标题锚点定位 + W-12 裁决清单完整性（r42/r43 两轮点名未落地）---
    # 语义定死：missing = 在账（未勾选且存在）且「无任意裁决标记」或「最后一次挂账已到期」；
    #          已勾选项与已消失项不算 missing；未来挂账不算 missing（但会被 REPEAT 显形）。
    L = ["- [ ] 【P0·待办 A（r41 登记）】 正文甲 【r43 裁决=挂账至 r46】",
         "- [x] 【P0·待办 B（r41 登记）】 已闭环",
         "- [ ] 【P0·待办 C（r42 登记）】 正文丙",
         "- [ ] 【P1·待办 C（r42 登记）】 正文丙"]
    ck("t40 W-13 唯一标题 → 命中 1 行", da.find_item_line(L, "待办 A") == [1], str(da.find_item_line(L, "待办 A")))
    ck("t41 反例：标题重复 → 命中多行，调用方必须拒写而非挑第一行",
       len(da.find_item_line(L, "待办 C")) == 2, str(da.find_item_line(L, "待办 C")))
    ck("t42 已勾选项不参与定位（禁往闭环条目上写裁决）",
       da.find_item_line(L, "待办 B") == [], str(da.find_item_line(L, "待办 B")))
    gap = da.adjudication_gap(["待办 A", "待办 B", "待办 C", "待办 D"], L, "r44")
    ck("t43 W-12 完整性：无标记的在账项全列 missing（含重复登记两份），已闭环/已消失/未来挂账不算",
       gap == ["待办 C", "待办 C"], str(gap))
    L2 = ["- [ ] 【P0·待办 C（r42 登记）】 正文丙 【r44 裁决=降级（转长期看守）】",
          "- [ ] 【P1·待办 C（r42 登记）】 正文丙 【r44 裁决=降级（转长期看守）】"]
    ck("t44 两份都拿到本轮终局裁决 → missing 归零（机制不永远红）",
       da.adjudication_gap(["待办 C"], L2, "r44") == [], str(da.adjudication_gap(["待办 C"], L2, "r44")))
    L3 = ["- [ ] 【P0·待办 A（r41 登记）】 正文甲 【r41 裁决=挂账至 r43】"]
    ck("t45 反例：最后一次挂账已到期（r43 <= 本轮 r44）→ 仍算 missing，不得当已裁",
       da.adjudication_gap(["待办 A"], L3, "r44") == ["待办 A"], str(da.adjudication_gap(["待办 A"], L3, "r44")))
    ck("t46 多命中时 missing 逐行计（防只裁第一行就宣称完成）",
       len(da.adjudication_gap(["待办 C"], L, "r44")) == 2, str(da.adjudication_gap(["待办 C"], L, "r44")))

    fails = [r for r in RESULTS if not r[0]]
    print("\n夹具合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    if fails:
        print("[GATE:fixture-fail]")
        for ok_, name, detail in fails:
            print("  FAIL %s | %s" % (name, detail))
        return 1
    print("[GATE:fixture-pass]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
