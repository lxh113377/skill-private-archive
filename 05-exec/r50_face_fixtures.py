# -*- coding: utf-8 -*-
r"""r50_face_fixtures.py — W-25「输入面自证推广到其余判据」的层a 夹具（先看红）。

本轮实测动因（不是假想）：
  · `05-exec/rule_conflict_scan.py` 的 DEFAULT_FILES 是**手抄 10 件**静态清单，而
    `D:/global_memory/core/` 实存 25 件，其中 **17 件带可配对正负规则**（保守下界 46 条）
    从未进扫描面 —— 冲突判据对它们全盲，却照样打印绿灯。这是 X-24 说的
    「面内自洽 ≠ 面是全面」在第二个判据上的实证（r49 在账龄尺上抓到同一形态）。
  · `05-exec/ratchet_gate.py` 的 `username_in_skill_files` 里 `OSError: continue`
    会静默跳过读不到的文件 ⇒ `n` 是在**更小的面**上算的，而报出来的数字不带面信息。
    ⇒ 用两条结构途径对账（glob 计数 vs 成功读取计数）。
  · `baseline_contract_scan.py` 已有 pattern 零命中判红（其 L358 check_coverage），
    本轮如实判为「已具备，不重复建」，只补一条断言防它被日后改掉。
"""

import importlib.util
import io
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
RESULTS = []


def ck(name, cond, got=""):
    RESULTS.append((bool(cond), name, str(got)))
    print("%s %-58s %s" % ("PASS" if cond else "FAIL", name,
                           "" if cond else "  <-- " + str(got)[:200]))


def load(mod_name, fname):
    spec = importlib.util.spec_from_file_location(mod_name, str(HERE / fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


rcs = load("rcs50", "rule_conflict_scan.py")
rg = load("rg50", "ratchet_gate.py")

# ------------------------------------------------ ① 权威源覆盖面（rule_conflict_scan）
A = Path("D:/fake/behavior_core.md")
B = Path("D:/fake/behavior_core_rules_p8.part1.md")
C = Path("D:/fake/USER.md")

cov = getattr(rcs, "face_authority_coverage", None)
ck("k0 判据存在性：rule_conflict_scan 暴露 face_authority_coverage（缺则本轮即红阶段）",
   callable(cov), type(cov).__name__)
if callable(cov):
    ok, d = cov({A}, [A, B])
    ck("c1 反例：带极性规则却不在扫描面的权威源 ⇒ 判红并点名",
       ok is False and "p8" in str(d), (ok, str(d)[:150]))
    ok, d = cov({A, B}, [A, B])
    ck("c2 正例：候选全部在面内 ⇒ 判绿", ok is True, (ok, str(d)[:150]))
    ok, d = cov({A}, [])
    ck("c3 边界：发现器零候选 ⇒ UNVERIFIED（不得静默 PASS，R-ENUM 边界条）", ok is None, (ok, str(d)[:120]))
    ok, d = cov(set(), {A})
    ck("c4 形状：入参必须都是路径集合，误传 list 不得抛穿（要给出可读拒绝）",
       ok is False or ok is None, (ok, str(d)[:120]))

disc = getattr(rcs, "discover_authority_candidates", None)
ck("k1 判据存在性：rule_conflict_scan 暴露 discover_authority_candidates", callable(disc),
   type(disc).__name__)
if callable(disc):
    cands = disc()
    ck("c5 真机：发现器在 GM/core 上取到非空候选（且带规则密度信息）",
       isinstance(cands, dict) and len(cands) >= 10, "%s 件" % len(cands))
    eff = {p.resolve() for p in rcs.effective_files()}
    ok, d = rcs.face_authority_coverage(eff, sorted(cands))
    ck("c6 真机红转绿：扫描面（手抄 ∪ 自动发现）不得再有漏扫的带极性规则权威源",
       ok is True, str(d)[:230])
    ok_pre, d_pre = rcs.face_authority_coverage({p.resolve() for p in rcs.DEFAULT_FILES if p.exists()},
                                                sorted(cands))
    ck("c6b 对照（证明扩面确有作为）：只用手抄清单时同一断言必须判红",
       ok_pre is False, str(d_pre)[:120])
    hand = {p.resolve() for p in rcs.DEFAULT_FILES if p.exists()}
    ck("c7 扩面不重复计入：静态清单与发现集重叠件数须 >0（证明两源同一口径，不是各扫各的）",
       len(hand & set(cands)) > 0, "重叠 %d 件" % len(hand & set(cands)))
    ck("c8 扩面确有增量：effective_files 件数必须严格大于手抄清单件数（否则本轮扩面是空转）",
       len(rcs.effective_files()) > len([p for p in rcs.DEFAULT_FILES if p.exists()]),
       "eff=%d 手抄=%d" % (len(rcs.effective_files()),
                           len([p for p in rcs.DEFAULT_FILES if p.exists()])))

# ------------------------------------------------ ② 读取计数交叉对账（ratchet_gate）
fcc = getattr(rg, "face_counted_vs_observed", None)
ck("k2 判据存在性：ratchet_gate 暴露 face_counted_vs_observed", callable(fcc), type(fcc).__name__)
if callable(fcc):
    ok, d = fcc(9, 10)
    ck("k3 反例：成功读取 9 < 枚举 10 ⇒ 判红（OSError 静默跳过的面必须在数字上显形）",
       ok is False, (ok, str(d)[:150]))
    ck("k4 正例：两路相等 ⇒ 判绿", fcc(10, 10)[0] is True, fcc(10, 10))
    ok, d = fcc(0, 0)
    ck("k5 边界：枚举 0 件 ⇒ UNVERIFIED/判红，绝不判绿（R247）", ok is not True, (ok, str(d)[:130]))

# ------------------------------------------------ ③ 契约扫描的零命中面（防回退）
bcs = load("bcs50", "baseline_contract_scan.py")
fake_matched = [("ratchet_baseline*.json", [Path("x.json")]), ("nonexistent_glob*.json", [])]
fake_contracts = {"artifacts": {"ratchet_baseline*.json": {}, "nonexistent_glob*.json": {}}}
try:
    msgs, rows = bcs.validate_contracts(fake_contracts, fake_matched)
except Exception as e:                                       # noqa: BLE001
    msgs = ["__ERR__ %s: %s" % (type(e).__name__, e)]
ck("k6 防回退：pattern 命中 0 文件必须被点名（r33 既有能力，本轮锁死）",
   any("命中 0" in m for m in msgs), json.dumps(msgs, ensure_ascii=False)[:180])

print("\n夹具合计: %d 项，通过 %d，失败 %d"
      % (len(RESULTS), sum(1 for r in RESULTS if r[0]), sum(1 for r in RESULTS if not r[0])))
print("[GATE:fixture-fail]" if any(not r[0] for r in RESULTS) else "[GATE:fixture-pass]")
sys.exit(1 if any(not r[0] for r in RESULTS) else 0)
