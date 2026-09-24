# P1-2 交接记忆评测基线（v1）

> 生成：2026-09-24 08:59 ｜ 项目：`C:\Users\37533\Desktop\workspace\自建skill优化` ｜ 场景集：`06-benchmark/memory_eval_scenarios_v1.json`（12 场景）
> 判据：正则确定性命中（零 LLM）；召回面 = 目标节主卷 + partN 分卷 + memory/AGENTS.md。

| id | 节 | 类型 | 结果 | 命中文件 | 问题 |
|---|---|---|---|---|---|
| M01 | 01 | normal | ✅ | 01-goal.md | 本项目目标是什么？（阶段划分关键词） |
| M02 | 02 | normal | ✅ | 02-structure.md | 执行证据目录是哪个？ |
| M03 | 03 | normal | ✅ | 03-tech-stack.md | 本机首选 Python 解释器路径？ |
| M04 | 04 | normal | ✅ | 04-file-map.md | 阶段0/1 唯一可复跑脚本是哪个？ |
| M05 | 05 | normal | ✅ | 05-feature-status.part11.md | 第 13 轮 noise_lint 修补的根因结论是什么（关键词）？ |
| M06 | 06 | normal | ✅ | 06-constraints.md | 受管根内散落项的处置红线是什么？ |
| M07 | 07 | normal | ✅ | 07-next-steps.md | P0-2 AC 收敛机器化的落地命令形态？ |
| M08 | 08 | normal | ✅ | 08-ac-obs.md | 阶段0 自建清单裁定可复跑的验收标准编号？ |
| M09 | 09 | normal | ✅ | 09-workflow-state.md | 动态工作流状态文件的 schema 标识？ |
| M10 | 06 | trap | ✅ | 06-constraints.md | 【陷阱·销账类】`.rule_backup` 备份集中落点问题现在是什么状态？（应答：已 |
| M11 | 07 | trap | ✅ | 07-next-steps.md | 【陷阱·销账类】11 个一次性脚本归档这件事完成了吗？（应答：已归档至 archive/ |
| M12 | 05 | trap | ✅ | 05-feature-status.part11.md | 【陷阱·状态类】06 注入壳瘦身（P1-3a）最终结果？（应答：已执行，-6,435B， |

**基线分：12/12 recall（100%）**

## 后续

- review 报告接入（handoff.py review 读取评测行）与 LLM 语义级场景为增补项；
- FAIL 项 = 记忆盲区候选：先核「内容缺失」还是「措辞漂移」，再补场景或补内容。
