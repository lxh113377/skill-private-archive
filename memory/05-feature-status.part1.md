# 05-feature-status.part1.md

<!-- 本卷为 05-feature-status.md 的延续 -->

## ⛔ 阻塞

- HM 实况核验（2026-09-14）：磁盘旁证 4 处存在（`~/.hermes`、`AppData\Roaming\hermes`、`AppData\Local\hermes`、`D:\hermes`）；但 `hermes\skills` 是**分类树真实目录**（16 类，非 junction）、`hermes\memories` 为**空目录** → 整体 junction 有遮蔽风险，方案待定

- q-2 焚诀路由索引重建（2026-09-14，焚诀 `6a06d74` / GM `244937e`）：黑名单补 8 项 → `retire_reconcile --repair` → `build_registry`（168==168）→ `build_indexes --apply` → 双仓提交
  - 验收：`verify` **13 PASS / 1 FAIL**（C1/C6 修复；仅剩无关的 C14 时效）；`retire_reconcile` PASS；**路由器 top1 死件 `skill-install` → 在役 `skill-manager`**
  - 根因：`retire_skill.py` 有目录存在性校验 + 当年退役走手工删目录 → 漏登记黑名单 → 对账永远 PASS
- q-3 HM 技能共享（2026-09-14）：`hermes\skills\global-skills\` = 真目录 + **162 个技能 junction**
  - **以 B′ 替代用户所选的 C**（附硬证据：HM manifest 键 `apple\apple-notes\SKILL.md` = 2 级，C 会让 HM 扫不到任何全局技能且遮蔽自有 81 个）
  - 中途排除 raw junction 的 **15 条 `_trash` 退役件误命中**
  - 待办已闭环：HM 口径统一（焚诀 `f145f7f` 改 C4 代码）+ 记忆接入（`memories` junction 已完成）

- 批2 剩余 P0 单点修复（2026-09-19，commit `eb77870`，7 文件）：剩余 5 个单点 P0 一次收口
  - **P0-5** `chaoshi-image-optimization`：ffmpeg 硬编码 `ffmpeg-8.1.1-full_build`（实测本机已升 `9.0` → Step2/2.5/3 脚本必崩）→ 4 处改**动态探测**（`(Get-Command ffmpeg).Source` + WinGet 包目录枚举兜底 + throw 兜底）；实跑解析到 `ffmpeg-9.0-full_build` 且 `ffmpeg -version` 通过 ✅；version 1.1.0→1.2.0
  - **P0-6** `fenjue-routing-health-check`：CHECK-3 写死 `VERSION_LOCK.part1..4`（**实测实为 `part1` + `part15`~`part29` 共 16 卷** → 漏 12 卷，产出假阴性）→ 步骤 1/5 改**动态枚举** `VERSION_LOCK.part*.md`；version 2.5.1→2.5.2 + 版本历史行
  - **P0-10** `hook-analyzer-skill` / `report-generator-skill`：共同上游 `video-breakdown-skill` 实测 `Test-Path=False` → 示例命令行标注悬空并注释掉不可执行行；两件 version 1.0.0→1.0.1（**补建上游 vs 两件退役 仍待裁定**）
  - **P0-12** `openclaw-fenjue-weekly`：收尾门禁平台枚举 `六端(OC/WB/CC/TC/HM/CX)` → **在役端 `OC/WB/TR/CX/HM`**（口径 = `cross_platform_map.json`）；version 2.0.1→2.0.2 + 版本历史行
  - **P0-14** `cross-platform-agent-sync/references/cps.part8.md`：删 `A-memory-align` 死引用行（全库 0 命中）；SKILL.md version 1.2.0→1.2.1
  - 验收：`rule_editor.py gates` → `mirror=pass noise=pass evolution=pass`；19 处补丁 dry-run 全命中；7 文件读盘复核全对
  - ⚠️ 工具坑：`replace` 对**删除类补丁**恒报 `[verify] FAIL 未找到: <旧文本>`（回退搜旧文本的误报），写盘实际成功

## 🚧 进行中

- 阶段5 工作流专项（2026-09-14）→ `04-plan/工作流专项建议.md`：闭环落地率实测（七步 3.9% / footer 协议 2.0% / 门禁 24.5%）、footer 四处收敛方案、direct_map 误命中修正 5 步
- 阶段4 实际改动 skill — **等用户确认**（阶段0-4 全程只读，未碰 `D:\global_skills` 一个字节）（A族5 / fenjue5 / 审计15 / local10 / story11 / 其他族 4 批 57 = 103 个，7 批全部落盘）
  - 附带成果：最后一批推翻 11 个「自建」判定（市场/上游件），真自建量修正为约 91 个

## 📋 计划中

- 阶段2 全量精读（102 个，按族分批）
- 阶段3 审计报告 + P0/P1/P2 分级
- 阶段4 逐项实施计划
- 阶段5 工作流专项 + 注册表修正 + 合并评估

## ⛔ 阻塞

- LOW 灰区 33 个归属待用户裁定（阻塞阶段2 精读范围）
