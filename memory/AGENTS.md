# AGENTS.md — 自建skill优化 项目级 Skill 绑定表（P-1，A-project-handoff）

> 手动维护。agent 检测到本项目路径时第一动作 Read 本文件；命中触发条件 → 加载对应 skill，禁裸跑。

## Skill 强制绑定（命中即加载）

| 触发条件 | 必加载 skill |
|---------|-------------|
| 任何项目修改操作（代码/记忆/技能/文档/配置） | A-project-handoff |
| 每轮复杂任务开场 | A-memory-start |
| 任务结束/复盘/经验沉淀 | A-get-memory |
| 动手前需求澄清 | A-ask-questions |
| 审计视角：预判 agent 行为链/死链/规则冲突 | vp-perspective-audit |
| 注册表 user_created 标记失真 / 死链 / orphan | data-layer-consistency-fix |
| 同类 skill 合并评估（local-* / story-* / 审计族） | skill-merge |
| 路由健康度 / 领域计数 / 版本线自洽 | fenjue-routing-health-check |
| 提示词结构深度审计（V1-V7） | prompt-system-audit |
| 触发命中率全量审计 | skill-hitrate-full-audit |

## 铁律

- `memory/07-next-steps.md` P0 永不为空；`savepoint` 后才能结束对话
- 阶段 0-3 为只读取证阶段：不修改 `D:\global_skills` 下任何 skill 源文件，只在本工作区写报告
- 阶段 4 起改 skill 文件，唯一途径 = `rule_editor.py`，禁 `write_file` 整体重写；改完重建派生件 + 复跑三门禁（mirror / noise / evolution）
- 任何结论须标注 ✅已实测 / ⚠️部分实测 / ❌未实测；禁止用旧快照、旧记忆、历史报告当现状
- 落盘编辑前必须输出 `【数据流假设】` 四要素（来源/流向/结构/异常），缺一不得编辑
