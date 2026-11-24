# skill-modernization-r1 汇总索引与证据链（需求7）

> 本目录 README 是 t7 汇总索引：四类文档、五份主源件、判据命令、期望末行、负控与退路。所有当前值以命令/源件为准，R241 旧快照数字不复制为当前值。

## 1. 交付件索引

| 文档 | 覆盖需求 | 主源件 | 判据命令 | 期望末行 | 负向对照 |
|---|---|---|---|---|---|
| [问题分析报告.md](问题分析报告.md) | ① + ⑦ | `01_skill_inventory.md`, `data/inventory.json` | `python -B deliverables/skill-modernization-r1/01_coverage_check.py` | `[COVERAGE:PASS] 分母=150 分类之和=150 相等断言=True 逐件证据=150/150 受管根三类守恒=True` | `01_coverage_check.py --negative-control` → `[NEGCTRL:RED]` |
| [对比评估表.md](对比评估表.md) | ② + ③ + ⑦ | `02_replacement_candidates.md`, `data/candidates.json`, `03_evaluation_matrix.md`, `data/matrix.csv` | `python -B deliverables/skill-modernization-r1/02_candidates_check.py`；`python -B deliverables/skill-modernization-r1/03_matrix_check.py` | `[CANDIDATES:PASS] …`；`[CHECK] PASS` | `02_candidates_check.py --negative-control`；`03_matrix_check.py` 内置两条 `[NEGCTRL:RED]` |
| [迁移执行计划.md](迁移执行计划.md) | ④ + ⑥接口 + ⑦ | `04_migration_plan.md`, `04_migration_batches.json` | `python -B deliverables/skill-modernization-r1/04_plan_check.py`；`python -B deliverables/skill-modernization-r1/04_protected_guard.py` | `[PLAN:CHECK] PASS`；`[PROTGUARD:CLEAN]` | `04_plan_check.py --negative-control` / `--negative-control-protected` / `04_protected_guard.py --negative-control` → `[NEGCTRL:RED]`×3 |
| [后续维护规范文档.md](后续维护规范文档.md) | ⑤ + ⑥ + ⑦ | `05_inspection_regime.md`, `data/quarterly_check.md`, `06_quality_validation.md` | `python -B 05-exec/r260_quarterly_cadence.py --selftest`；`python -B deliverables/skill-modernization-r1/06_quality_check.py` | `[CADENCE:SELFTEST-PASS]`；`[QUALITY:IMPOSSIBLE]`（rc=1，如实报未达标） | cadence 伪超龄负控 `[CADENCE:FAIL]`；`06_quality_check.py --negative-control` → `[NEGCTRL:RED]` |
| [README.md](README.md) | ⑦ 索引与证据链 | `data/summary_manifest.json` | `python -B deliverables/skill-modernization-r1/07_coverage_check.py` | `[COVERAGE:PASS] 需求覆盖=7/7 差异=0` | `07_coverage_check.py --negative-control` → `[NEGCTRL:RED]` |

## 2. 01–06 源件与各自判据命令、期望末行

| 编号 | 源件 | 判据 / 取值命令 | 期望末行 |
|---|---|---|---|
| 01 | `01_skill_inventory.md`, `data/inventory.json`, `01_coverage_check.py` | `python -B deliverables/skill-modernization-r1/01_coverage_check.py` | `[COVERAGE:PASS] 分母=150 分类之和=150 相等断言=True 逐件证据=150/150 受管根三类守恒=True` |
| 02 | `02_replacement_candidates.md`, `data/candidates.json`, `02_candidates_check.py` | `python -B deliverables/skill-modernization-r1/02_candidates_check.py` | `[CANDIDATES:PASS] 分母=77 rows=77 逐件候选 3-5=True 元数据实测=377/377 取值命令=377/377 维护筛选=active 377/377 阈值=2025-11-07 族级补位未计入=True 负控配置=OK` |
| 03 | `03_evaluation_matrix.md`, `03_matrix_build.py`, `03_matrix_check.py`, `data/matrix.csv` | `python -B deliverables/skill-modernization-r1/03_matrix_check.py` | `[CHECK] PASS`（同跑打印 `[DIFF_ASSERT] 0` 与两条内置 `[NEGCTRL:RED]`） |
| 04 | `04_migration_plan.md`, `04_migration_batches.json`, `04_plan_check.py`, `04_protected_guard.py` | `python -B deliverables/skill-modernization-r1/04_plan_check.py`；`python -B deliverables/skill-modernization-r1/04_protected_guard.py` | `[PLAN:CHECK] PASS`；`[PROTGUARD:CLEAN]` |
| 05 | `05_inspection_regime.md`, `data/quarterly_check.md` | `python -B 05-exec/r260_quarterly_cadence.py --selftest`；`python 05-exec/r114_replacement_scan.py --offline` | `[CADENCE:SELFTEST-PASS]`；`[REPL:PASS] 逐件候选面守恒 191==191 | MATCHED=166 FAMILY_ONLY=12 NO_OS_CANDIDATE=8 UNVERIFIED=5` |
| 06 | `06_quality_validation.md`, `06_quality_check.py`, `data/06_quality_verdict.json` | `python -B deliverables/skill-modernization-r1/06_quality_check.py` | `[QUALITY:IMPOSSIBLE]`（正常态 rc=1，如实报需求6未达标，非故障） |

## 3. 覆盖矩阵（7/7）与数字交叉校验

| 需求 | 主文档章节 | 机器判据 |
|---|---|---|
| ① 全量盘点现有 skill | `问题分析报告.md` §1–§2 | `07_coverage_check.py` REQ1 锚点 |
| ② 逐个检索 3-5 替代 | `对比评估表.md` §1 | `07_coverage_check.py` REQ2 锚点 |
| ③ 五维量化矩阵 | `对比评估表.md` §2–§4 | `07_coverage_check.py` REQ3 锚点 |
| ④ 分阶段迁移替换 | `迁移执行计划.md` §1–§5 | `07_coverage_check.py` REQ4 锚点 |
| ⑤ 长效季度巡检 | `后续维护规范文档.md` §1–§2 | `07_coverage_check.py` REQ5 锚点 |
| ⑥ 质量提升≥30%与兼容性 | `后续维护规范文档.md` §3；`迁移执行计划.md` §4 | `07_coverage_check.py` REQ6 锚点 + `06_quality_check.py` |
| ⑦ 四类文档与索引 | 四文档 + 本 README | `07_coverage_check.py` REQ7 锚点 |

自证命令（workdir=`自建skill优化`，先 `export PYTHONPYCACHEPREFIX=_temp/pycache`，Python 用 managed venv）：

```bash
python -B deliverables/skill-modernization-r1/07_coverage_check.py
python -B deliverables/skill-modernization-r1/07_numeric_check.py
python -B 05-exec/run_gates.py --json _temp/t7_gates_full.json
```

期望末行分别：`[COVERAGE:PASS] 需求覆盖=7/7 差异=0`、`[NUMERIC:PASS] 差异 0`、run_gates 的 JSON verdict 如实记录（真红不洗绿）。t7 现跑 `_temp/t7_gates_full.json` 为 `generated_at=2026-11-07 09:39 / gates_run=118 / verdict=FAIL / verdict_reason=FAIL=7 UNVERIFIED=4 / real_red=10 / design_inherent_red=1`；按 R263/X-9 如实登记，不删 tracked 件凑绿。负控：`07_coverage_check.py --negative-control` 与 `07_numeric_check.py --negative-control` 均须 `[NEGCTRL:RED]`。

## 4. 定稿口径与红线

- 分母：清单 `150 = HIGH51+MID26+LOW30+EXCLUDE43`；维护替换面 `77=HIGH+MID`；LOW30 灰区、EXCLUDE43 市场/上游件禁入替换分母。
- T 差约 90% 是结构性假象：现有件 `31.87` / 候选件 `76.11` / 差 `44.24`，禁止写「替换后提升 139%」；结构性锁死 ≠ 质量落后。
- 需求6：t6 裁决 (c) 如实证否；`ceiling_score=95.2 < need_score_relative_reading=114.8`；`[REQ6:IMPOSSIBLE]`；禁止假完成。
- t4 定稿：`replaceable=57 P0=5 P1=24 P2=28 gaps=11 holds=9`、`rollback 88/88`、`[PLAN:CHECK] PASS`、`[PROTGUARD:CLEAN]`；P0 五件含 `chaoshi-web-deploy`，`A-skill-manager` 为 `protected_hold`。
- unknown `66` 双向中性；`feedback_weight_cap=0`；r115 L1 引用必须同屏给 L4；r114 hybrid `38.2%` 不同源禁相减。
- 只读取证：阶段0-3 不改 `D:/global_skills` 任何 SKILL.md/源文件；真实替换走 `rule_editor.py` + 双硬前提；R241 旧数字只加校正注；门禁真红如实记 verdict，禁删 tracked 件凑绿。
- 结论标记：✅已实测 / ⚠️部分实测 / ❌未实测。GH 限流退路 `r114_replacement_scan.py --offline` 并具名盲区。

## 5. 退路

取证受阻（GH API 限流）→ `python 05-exec/r114_replacement_scan.py --offline` 复用缓存，具名登记 9 上游仓 `SKIPPED_OFFLINE`；run_gates 真红按 R263/X-9 如实记，不删 tracked 件；r113 离线按设计 `[QUARTERLY:DEGRADED] rc=2`，主产物不覆写；真实替换后的 A/B 尚未执行，后续按 `迁移执行计划.md` §3–§4 与 `后续维护规范文档.md` §3.2 复验。
