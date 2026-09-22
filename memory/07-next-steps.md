# 07 - 下一步

> 归档类型：增量（已完成项移入分卷）
> **⚠️ 这是新对话恢复上下文的入口文件；P0 永远不能空。**
> **真相源口径（2026-09-22 实测校准）**：P0 只放经实测确认**未完成**的项；已完成项一律迁入分卷 `- [x]`，不再滞留主卷。

## 最近对话摘要

- **2026-09-23（第 13 轮 r1–r6）** — 性能瓶颈三维实测分析 → P0-1/P0-2 落地（A-memory-start -64% / contract -58%） → 上游 trim-shell 双重盲区修复（V3.47.0）→ **06 纳入口径 V3.48.0**（注入壳 -6,435B/轮） → **noise_lint 假阳性根因修**（`d88b5ee`，savepoint 由被拒→安全落盘）。**逐轮全量记录（原样，零改写）见 `07-next-steps.part7.md`**

## P0 — 必须做

- [ ] **【待观察·他人在途】** 受管根未提交改动（2026-09-23 01:35 实测 `git -C D:\global_skills status --porcelain` = 6 条）：`gstack` / `local-computer-use` / `local-realtime-translator` / `local-screenshot-qa` / `chaoshi-image-optimization` / `chaoshi-web-deploy` 各自 `SKILL.md` 为 `M` —— 按 R269 与 P-1 铁律**只登记不擅动**，待对应会话自行收口。**历史复核（第 12 轮 / r4 原文）见 `07-next-steps.part7.md`**。**第 13 轮 r5 复核（2026-09-23 06:10）**：实测 **10 条**（`M` 8：`gstack` / `local-computer-use` / `local-realtime-translator` / `local-screenshot-qa` / `chaoshi-image-optimization` 各自 `SKILL.md` **+ A-project-handoff 在途功能 3 文件** `scripts/handoff.py` / `handoff_lib/audit.py` / `handoff_lib/common.py`；`??` 2：`handoff_lib/flow.py` / `scripts/templates/09-workflow-state.md.tmpl`）—— 新增 5 条源自并行会话的「动态工作流状态（09 节）」功能，按 R269 **只登记不擅动**（本轮对该 skill 的改动已用 `rule_editor` 单文件收口，见下条 r5 事故登记）
- [ ] **【待观察·焚诀在途债】** `gate_stub_runner` 实测 `[GATE:stub-fail]`（2026-09-23 01:35）：① 桩 `stub_c16_memory` 2/3——正例样本硬编码总分 `181.6` vs 活体评分卡 `183.9`（判据样本与活体口径漂移，R263 补注①形态，须由移动总分的会话裁决）；② 未登记桩判据 C17/C18/C19（registry 冻结于 09-22 后新增）。均非本轮引入（本轮仅改 A-project-handoff 文案，焚诀 eval 零触碰），按 R269 登记待其归属会话收口。**历史复核（第 12 轮 / r4 原文）见 `07-next-steps.part7.md`**
- [ ] **【待观察·新节缺失】** `09-workflow-state.md`：并行会话在途功能（`handoff_lib/common.py` 已把该文件列为第 9 个记忆节 + `templates/09-workflow-state.md.tmpl` 模板已落盘但**未提交**）⇒ 本项目 `status` 现报 **8/9**（该节 `❌ missing`）。按 R269 **不擅动**（模板/口径仍在途，避免与归属会话冲突）；待其提交收口后按官方模板补建该节并复跑 status/review
- [ ] **【待观察·跨会话夹带】** 受管根 `f6f5b0c`（本轮 V3.48.0 提交）**夹带**了并行会话在 `handoff_lib/splitvol.py` 的在途改动 1 行（`SPLIT_TARGETS` 增 `"09-workflow-state.md"`）—— 根因：`rule_editor.py commit` 按**整文件**提交，而同文件存在他人未提交改动；**非数据丢失、未改写其内容**（重编号补丁窗口 0 命中该行，内容原样入库），但归属与「已收口」判断失真。处置：**不回滚**（回滚=抹掉他人在途工作），只登记 + 提交前逐文件比对 `git status --porcelain`；已按 R241 在 `06-constraints.md` 留痕
- [ ] **【待办·文档同步】** noise_lint 修补（受管根 `d88b5ee`，2026-09-23 r6）的**三处文档同步待补**：`SKILL.md` 版本行、`references/version-history.md` 条目、`commands.md §11` 豁免口径说明 —— 暂缓原因 = 并行会话已把 `version: 3.49.0` 与这三个文件纳入在途改动（其 `handoff_v3.50` 系功能），此刻补写必然二次夹带他人改动。**处置**：待其提交收口后，按 3.49.0 → 下一版补登记（若其条目已含本修补则只需核对）；登记证据 = 本轮 commit `d88b5ee` 的提交信息已完整记述修补内容与验证
- [ ] **【P1 待授权·可选】** 性能方案剩余项（2026-09-23，详见 `05-exec/性能瓶颈分析与优化方案.md`）：P1-3a 本项目注入壳瘦身——**✅ 校正注（2026-09-23 r3 裁定：本轮不做，销账）**：实测 06 主文件 12,148B 无上游分卷/自愈机制（SPLIT_TARGETS 只注册 07/05，trim-shell 判据只认「✅/已完成」章节而 06 是 [BUG]/[DEBT] 留痕形态），收敛须逐条改写原文——违 R241「只加注不改写」精神且无机器护栏，**不擅建结构**；如要做须上游先裁 06 分卷口径（登记为上游建议，非本项目待办）。**✅ 校正注（2026-09-23 r5 销账）**：用户授权后上游口径已落地（A-project-handoff **V3.48.0**：`TRIM_ENTRY_TARGETS` 与 `SPLIT_TARGETS` 解耦 + `closed_marker` 判据 + 留痕章节白名单 + 分区不变式），本项目 06 实测 **13,075B → 7,097B**（迁出 13 条 → part1/part2），注入壳 06 节 **12,148B → 6,182B**、整壳 **33,029B → 26,594B（-6,435B/轮）**。P1-4 unified_router direct_hit 短路（上游焚诀，每轮省 ~1.1s；**项目红线明文「焚诀 eval/ 只读调用不改」**，转焚诀归属会话）；P2 三项观察不动
## 分卷目录
- **卷1** `07-next-steps.part1.md` — 历史待办与已完成条目（2026-09-22 已按实测销账）
- **卷2** `07-next-steps.part2.md` — 已完成：批2 剩余 P0 与 q-2/q-3 收口
- **卷3** `07-next-steps.part3.md` — 最近对话摘要（历史）
- **卷4** `07-next-steps.part4.md` — 07-next-steps 分卷（R199 自动拆卷）
- **卷5** `07-next-steps.part5.md` — 07-next-steps 分卷（R199 自动拆卷）
- **卷6** `07-next-steps.part6.md` — 最近对话摘要（历史轮次，2026-09-23 第 13 轮 r3 迁入，正文零改写）
- **卷7** `07-next-steps.part7.md` — 最近对话摘要（第 13 轮 r1–r6 全量记录，2026-09-23 原样迁入）
- **卷8** `07-next-steps.part8.md` — 07-next-steps 分卷（R199 自动拆卷）

