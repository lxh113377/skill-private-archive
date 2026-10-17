# 07 分卷 part73 — r112 摘要与四项新待办

> 迁卷动因：R199/主壳体量治理。主卷只留一行摘要指针，本卷承接 r112 全部细节与新增待办。

## r112 摘要（2026-10-17，goal 轮：第 19 维开维 + 四项工程改造）

**一句话**：把用户痛点「市面上的 skill 比我新，我还在用旧的」开成第 19 维「版本落后面」，用**内容寻址**（非相似度）建面；同时把 31 门里 5 门红归零、并首次真升级 1 件上游件。

### ① 门禁面归零（改造 1，高优先级）

- **根因**：`inject_union_bytes` 实测 64,280 > 基线 62,854（+1,426）；逐件实测定位到 `D:/global_memory/core/behavior_core.md` 工作树 17,441B vs git HEAD 13,438B（并行会话在途 #26「闭环即收声」/ #27「Agent 不代办取消」两节，+4,003B，未提交）。
- **处置**：走 `ratchet_gate.py --raise-baseline` 唯一窄门（commit=df4d006 / path 在注入面内 / delta=1426 逐字节相等 / reason 四要素），基线 62,854→64,280，累计留账 9 条。**不代提交他人受管根在途件**（R269）。
- **连坐**：重跑 `r38_debt_aging.py --json` 重生账龄件，消除相对新鲜前置把三债务态转 unknown 的 4 门连坐。
- **取值**：`python 05-exec/run_gates.py --json <件>` → `[GATES:PASS] PASS=32`。

### ② 第 19 维收口（改造 2，高优先级）

- **开工实测**：182 件里 declared=20 / inferred=35 / **unknown=127**（69.8% 连上游身份都没有），能裁决的面只有 39 件（21.4%）。
- **落件**：`r112_provenance_scan.py`（身份三档）/ `r112_provenance_pin.py`（内容寻址 pin 台账，append-only）/ `r112_upstream_probe.py`（六态关系）/ `r112_swap_gate.py`（五态裁决）/ `r112_provenance_face.py`（离线常驻门）/ `r112_provenance_fixtures.py`（23 腿含 3 变异）。
