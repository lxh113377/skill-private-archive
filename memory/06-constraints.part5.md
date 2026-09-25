# 06-constraints.part5.md

<!-- 本卷为 06-constraints.part4.md 的延续 -->

## 已闭环条目归档（R279 活载卷自愈迁移）

- [DEBT] **`fenjue_measure.py:168` 引用不存在的 `behavior_core.md` 路径**（真实位置为 `core/behavior_core.md`）→ 取 size=0，**D1 少算该 P0 文件**（2026-09-22 第 10 轮 `attention_sim.py` 实测告警，属上游口径差异） | 还债方式：改 `fenjue_measure.py` 路径并重跑评分 → 见第 10 轮建议 #8（破坏性）—— **✅ 校正注（2026-09-23 销账）：已闭环** —— B3 已执行；本轮实测 `fenjue_measure.py:182` 已为 `core/behavior_core.md`

- [BUG→**已修复**] **`noise_lint` 二级扫描口径不一致 ⇒ 同一物理目录两套结论、假阳性阻断全部会话 savepoint** — 影响范围：**全局门禁假失败扩散**（四受管根任一违规即拒绝 savepoint）。2026-09-23 实测：`D:\global_memory\_bak`（并行会话在途备份现场）在 `D:\global_memory` 根判 `quarantine`，却经 `焚诀\memory_content`（junction → `D:\global_memory`）在焚诀根判 `VIOL`；同一会话的 savepoint 因此被拒 | 根因三处：① 二级扫描不继承一级 `quarantine` 豁免（一级用、二级漏用）；② 二级子项自身命中 `QUARANTINE_DIRS`（`_bak`）未判豁免；③ junction/符号链接顶层项被按宿主根口径重复判定 | 状态：**已修复（代码层）**（受管根 `d88b5ee`，仅 1 文件；`is_reparse_dir()` 三重回退 + `status_by_name` 留档复用；层a 隔离桩 14/14 含修前修后对照 + 层b `noise` 四根 `[GATE:noise-pass]`）—— ⚠️ **文档同步待补**：`SKILL.md` 版本行 / `version-history.md` / `commands.md §11`（并行会话占用 3.49.0 在途，避免二次夹带；见 `07-next-steps.md` 待办）

- [BUG] **对标整改队列未过「范围裁定」即会引导会话去改别人的技能**（2026-09-24 r29 实测） —— r28 的 H2 按 `verification=false` 体积降序取 top14，实为 `agent-browser`/`docx`/`computer-use-guidance-windows`/`gstack`/`shadcn`/`canvas-design` 等**全数市场/上游件**，越过 2026-09-22 用户裁定（维护面 = HIGH 51 + MID 26 = 77，EXCLUDE 43 / LOW 30 排除）。缺该段 67 条里自建在面仅 **14 条（20.9%）**，再叠判据稳健性过滤后真队列 **3 条**。 | 状态：**已闭环**——机器护栏 `05-exec/r29_scope_filtered_queue.py`（读 `00-scope/自建skill清单.md` 裁定表，越界项只登记不改）；3 条真队列已于 r29 补齐（受管根 `6a4f97b`，复测真队列 3→0）

- [DEBT→**已闭环**] **`06-benchmark/debt_runs.jsonl` 最初两行由未定型版本写出、缺契约必填键** — 影响：契约校验器 [CONTRACT:FAIL] 拦住趋势台账；处置：该两行是本会话 5 分钟内的中间产物（非历史事实记录），**已删除并由定型版本重记 2 行**。被删行所记「裁决前 OVERDUE 22」的真值**未丢失**（完整存于 r38 证据件与 git 历史）。状态：**已闭环**（2026-09-25 r39 实测 `[CONTRACT:PASS]` 15 份 / 13 pattern，台账 2 行有效）| 取值：`python 05-exec/baseline_contract_scan.py --quiet`；`wc -l 06-benchmark/debt_runs.jsonl`
