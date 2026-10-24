# -*- coding: utf-8 -*-
r"""r211_classify_reds_fixtures.py — 第 91 门：红门分类（REAL vs DESIGN-INHERENT）的行为级双向夹具。

存在理由（r212 落 R211-3，一手）：本仓 CI 近 30 run 27 红，逐行归因后红因恒为**同一道门**
gate_run_freshness —— 它评的是「本机最近一次全量门禁有没有干净跑完」，读本机已提交台账，
本机有活债时必红，属职责内。但它在 CI 页面上与真故障红**完全同形**，读起来像 CI 挂了。
分类逻辑本身若写错（把 meta 门算进真故障、或把真故障消音进 meta），后果比没有分类更坏：
它会让我以为「红是设计内的」从而放过真缺陷。故必须常驻双向证据。

七腿：c1 元门红只进 design_inherent；c2 普通 FAIL 进 real；c3 UNVERIFIED 进 real（不消音，R247）；
c4 PASS/SKIPPED 两桶都不进；c5 守恒 |real|+|meta| == 红门数（X-24 枚举器纪律）；
c6 rc 语义未被分类改动（aggregate 仍按全量含 meta 判 FAIL —— 摘掉 meta 就是消音，R263 反向）；
m1 变异：摘掉门表 meta 标记 ⇒ c1 必须转红（证它测的是分桶本身，非恒真），并验证复原不残留。

全程零网络、不起子进程（只 import 被测模块 + 合成 rows）⇒ portable=True。
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RESULTS = []


def load_rg():
    spec = importlib.util.spec_from_file_location("rg_cls", os.path.join(HERE, "run_gates.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, str(detail)))
    print("%-4s %s%s" % ("PASS" if cond else "FAIL", name,
                          "" if cond else "  <-- " + str(detail)[:200]))


ROWS = [
    {"id": "gate_run_freshness", "state": "FAIL"},
    {"id": "ratchet_gate", "state": "FAIL"},
    {"id": "control_char_scan", "state": "PASS"},
    {"id": "some_unverified", "state": "UNVERIFIED"},
    {"id": "skipped_one", "state": "SKIPPED"},
]


def main():
    rg = load_rg()
    if not hasattr(rg, "classify_reds"):
        ck("前置：run_gates 暴露 classify_reds（缺即判红，不许当通过）", False, "attribute missing")
        return finish()

    saved_meta = set(g["id"] for g in rg.GATES if g.get("meta"))
    ck("前置：门表里确有一道 meta=True 的门（否则分桶无鉴别对象）", bool(saved_meta), sorted(saved_meta))

    real, meta = rg.classify_reds(ROWS)
    ck("c1 元门红只进 design_inherent、不进 real",
       meta == ["gate_run_freshness"] and "gate_run_freshness" not in real, "real=%s meta=%s" % (real, meta))
    ck("c2 普通门 FAIL 进 real", "ratchet_gate" in real, real)
    ck("c3 UNVERIFIED 进 real（不得消音，R247）", "some_unverified" in real, real)
    ck("c4 PASS / SKIPPED 不入任何红桶",
       not ({"control_char_scan", "skipped_one"} & set(real + meta)), (real, meta))
    n_bad = len([r for r in ROWS if r["state"] in ("FAIL", "UNVERIFIED", "MISSING")])
    ck("c5 守恒：两桶之和 == 红门数（不重不漏）", len(real) + len(meta) == n_bad, (len(real), len(meta), n_bad))
    ck("c6 rc 语义未改：aggregate 仍按全量含 meta 判 FAIL", rg.aggregate(ROWS)[0] == 1, rg.aggregate(ROWS))

    # m1 变异：摘掉 meta 标记（= 分类失效）⇒ 元门必须落进 real
    for g in rg.GATES:
        if g.get("meta"):
            g.pop("meta")
    real2, meta2 = rg.classify_reds(ROWS)
    ck("m1 变异：摘掉 meta 标记 ⇒ 元门落进 real（证 c1 测分桶本身，非恒真）",
       meta2 == [] and "gate_run_freshness" in real2, "real2=%s meta2=%s" % (real2, meta2))
    for g in rg.GATES:
        if g["id"] in saved_meta:
            g["meta"] = True
    real3, meta3 = rg.classify_reds(ROWS)
    ck("m1b 复原后分桶回到原状（变异不残留）", (real3, meta3) == (real, meta), (real3, meta3))
    return finish()


def finish():
    ok = sum(1 for r in RESULTS if r[0])
    total = len(RESULTS)
    print("\n夹具合计: %d 项，通过 %d，失败 %d" % (total, ok, total - ok))
    print("[GATE:fixture-fail]" if total != ok else "[GATE:fixture-pass]")
    return 0 if total == ok else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    raise SystemExit(main())
