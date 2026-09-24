# 规则冲突扫描基线 (2026-09-24 17:46)

> 对标 mycelium-hq/ai-brain-starter `scripts/check-rule-conflicts.py`；只读取证，候选非判决。

## 输入证据

| 项 | 值 |
|---|---|
| 文件(存在/列出) | 9/10 |
| 极性规则条数 | 97 |
| CH1 自述冲突 | 5 |
| CH2 互斥候选 | 6 |

## CH1 自述冲突

- `core/behavior_core.md:2` > ⚠️ **2026-09-22 校正注**：本文件（V41，22锚点，P0.x 编号体系）与 R174 卷（`core/behavior_core_rules_p8*.md`）**计数口径不一致** —— 用户裁定「每轮"老大。"开头」由 P0 降为 **P1**（**要求不变**）后，R174 卷重排为 **P0 #1-#17 + P1 1 条（V37）**；该条**本文件 P0.x 列表中
- `core/BOOTSTRAP.part1.md:12` - ⚠️ **计数口径冲突（既有，未修）**：本行 V41/22锚点 ↔ `core/MEMORY.md` V37/17锚点 ↔ `core/behavior_core_appendix.md` V36/18锚点，三处不一致，待统一（2026-09-22 发现并留痕）
- `memory/AGENTS.md:13` | 审计视角：预判 agent 行为链/死链/规则冲突 | vp-perspective-audit |
- `自建skill优化/AGENTS.md:21` - 四个维度同时体检：触发命中率与路由 / 体积注意力税 / 死链·过时引用·规则冲突 / 重复合并与工作流闭环
- `自建skill优化/AGENTS.md:306` 「8 个 AC-OBS，但只有 11 个格式正确」（11 > 8 自相矛盾），该子命令的 AC 计数不可信。

## CH2 极性互斥候选 (top 6)

| 共用词 | 必须侧 | 禁止侧 |
|---|---|---|
| 工具调用 | `references/contract.md:35` 步骤（并行工具调用 | `A-memory-start/SKILL.md:69` 统计或输出工具调用数 |
| 工具调用 | `references/contract.md:35` 步骤（并行工具调用 | `references/contract.md:10` 输出工具调用数量 |
| 工具调用 | `references/contract.md:35` 步骤（并行工具调用 | `references/contract.md:28` 以数量形式表达或输出（不写"工具调用数 X/Y"等） |
| 工具调用 | `references/contract.md:35` 步骤（并行工具调用 | `references/contract.md:55` 统计或输出工具调用数 |
| 显式声明 | `core/BOOTSTRAP.part2.md:12` 显式声明「你是子代理/子进程 | `core/behavior_core.md:161` 用时须显式声明「未实时查证」 |
| 用户立规 | `A-memory-start/SKILL.md:69` 静默（用户 2026-09-21 立规 | `core/behavior_core.md:150` 迎合）— 2026-09-21 用户立规 |
