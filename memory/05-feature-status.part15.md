# 05-feature-status 分卷 15 — 已完成：2026-09-24 r19b 标注驱动续做轮

> 由主卷 `## ✅ 已完成` 条目级归档迁入（R224 口径；正文零改写，仅整块迁移）。
> 迁入原因：主壳 05 已近 4KB 硬上限，新增长条目必须落分卷，主壳只留一行指针。

- **r19b 标注驱动续做轮（2026-09-24，第 20 轮 b 段，QD 端）** — 用户对 r19 回复里的「两条未闭环升级建议 + 三条下一步」加标注（无附加文字）⇒ 按既有授权直接做完能做的部分：
  - **R19-3（契约族）✅ 完成**：新建 `05-exec/schemas/r19/baseline-contracts.json`（8 个 pattern / 13 条具名不变式，对标 AAS `schemas/aas-v1/` 的「事前拒收」思路缩小到本仓基线件）+ `05-exec/baseline_contract_scan.py`（schema 字面量 / required 点路径 / types / invariants 四类判据 + R247「契约面空或 pattern 零命中 = FAIL」）；**严格 TDD**：先写 `05-exec/r19_baseline_contract_fixtures.py` 并实跑看红（`FAIL RED 前置：validator 不存在`）→ 实现 → **18/18 `[GATE:fixture-pass]`**（含层 b 真跑 8 份基线全合规 + 层 b′ 对照组「污染 schema 必须变红」）。根因（实测）：r19 把 drift 扫描 schema v1→v2 并新增 `excluded` 字段，下游按 v1 读会**静默拿不到排除面**。
  - **「交付判据类工具前强制跑夹具门禁」由自觉型升级为机器型 ✅**：新建 `05-exec/r19_fixture_mutation_check.py` 变异测试（未变异对照组必须 PASS + 4 项关键判据变异必须全部被拦），实跑 **4/4 `[GATE:MUTATION-PASS]`** ⇒ 补齐 footer 要求的「对照=已取（两侧实测）」；并把三条夹具/契约命令写进 `memory/AGENTS.md` 新增的「项目门禁命令」段（A-memory-start V9.8/R193 读取该段，修改类任务动手前先跑）= 挂到执行路径上，不再靠自觉。
  - **注入面端数失真 6 句当场改口 ✅**：`A-memory-start` `SKILL.md` L60 平台枚举、L92 五端适配、L131 File Resolution、L135 权威源、L139 意图路由 + `contract.md` L10/L85 → 全部改「八端」（H1 的 `V9.7.0 瘦身版` 版本戳改为无戳表述）；受管根 `961bad6` + `33fcffd`（版本 10.67.0→**10.68.0**，version_history 补条目，C13 PASS）。范围纪律：**只改正文与版本历史，不碰 frontmatter description**（description 是注册表/BGE/skill_content 派生件镜像，改它须整链重建；按「派生件三方脱节」教训留待 R19-1 重建窗口）。复扫 `claim_truth_scan.py`：候选 **10 → 4**，`A-memory-start/SKILL.md` 端数族归零。
  - 验证与留痕：`check-skill-mirror.ps1 -Fix`（单向 源→镜像）后 **mirror/noise/evolution 三门 pass**（stub 仍一红 = 焚诀在途 C29，现 29 PASS/1 FAIL）；逃生门 `--allow-collide` 用 1 次并归因（同会话同版本分两笔收口，因第二笔 `replace` 漏加 `--no-commit` 提前入库，非跨会话撞号）。
  - **新登记跨会话夹带（反向形态）**：我在 `contract.md` 的在途 hunks 被并行会话提交 `4b75d80` 一并带走（其提交说明未提及端数改动）——内容未丢失、未改写，归属失真；处置同 r18 `f6f5b0c`：**不回滚**（回滚=抹他人在途），只登记。
