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
- **销账必须逐条对照分卷 `partN` 的已完成条目**（2026-09-22 用户裁定，替代「改上游 review 判据」方案）：`handoff.py status` 报 `8/8`、`review` 报 `9/9（100%）`**均只判「文件是否被填充」**，不做「主卷声明 vs 分卷已完成项」交叉校验 ⇒ **分数 100% ≠ 记忆与实况一致**。凡判定「项目记忆是否过期 / 某项是否已完成」，**必须同时读主卷 + 全部分卷，逐条比对 `## ✅ 已完成` 区块**；禁止仅凭 `status`/`review` 分数或主卷单方声明下结论（实证：2026-09-22 第 10 轮，主卷 3 条已修 [BUG] 与 8 条已闭环 [DEBT] 在 100% 分数下长期滞留）。
- **环境脏项从外部引入时只登记不擅动**（R269）：受管根出现的**非本项目**散落项（如并行会话在途快照）先查 mtime / 提交序 / 生产脚本溯源，确认归属后**登记为待观察**；禁止为让 `savepoint` 通过而擅自迁移他人在途文件（2026-09-22 实证：`D:\global_memory\_bak\07nextsteps_20260922_142621` = 并行会话改 GM 07-next-steps 前的手工快照）。
