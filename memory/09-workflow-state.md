# 09 - 动态工作流任务状态（状态唯一源）

> schema: fenjue-workflow-state-v1 | 本文件是本项目**任务状态的唯一权威源**。
> `07-next-steps.md`（主壳 + 分卷）是由 `flow --sync` **单向回写**的派生台账——禁止手工改 07 的状态标记（改了会在下次 sync 被覆盖）。
> 状态枚举：`todo` / `doing` / `done` / `blocked`；批次：`P0` / `P1` / `P2`（`--next` 按 P0 → P1 → P2 顺序取批）。
> 用法：`handoff.py flow <项目路径> --status | --next | --start --id X | --done --id X [--evidence P] | --block --id X --reason R | --sync | --check | --add ...`

## 任务表

<!--
字段约定（机器解析，**勿改列名与列序**）：
| id | 批次 | 标题 | 状态 | 依赖 | 阻塞 | 更新于 | 证据 |
- id      唯一标识，建议 `<批次>-<序号>`；重复 = 解析报错
- 批次    P0 / P1 / P2；`--next` 依此顺序取批，本批全 done 才进下一批
- 标题    简短描述（不含 `|` 字符）
- 状态    todo / doing / done / blocked；其他值 = 解析报错
- 依赖    任务 id 逗号分隔；`-` 表示无依赖。依赖未 done 时 `--start` 拒绝
- 阻塞    `blocked` 状态必填原因；其余状态写 `-`
- 更新于  `YYYY-MM-DD HH:MM`（由 flow 自动写入）
- 证据    `done` 时填验收证据路径；其余写 `-`

示例行（在本注释内，不参与解析）：
| P0-1 | P0 | 示例任务 | todo | - | - | 2026-09-23 07:00 | - |
-->

| id | 批次 | 标题 | 状态 | 依赖 | 阻塞 | 更新于 | 证据 |
|----|----|----|----|----|----|----|----|
| R19-1 | P0 | 注入面失真句批次整改(端数/版本戳10句+流程入描述24条+六段最小规范) | blocked | - | 派生件重建窗口未开且 global_skills 28 条在途 | 2026-09-24 17:57 | - |
| R19-2 | P0 | 转焚诀 C29/C30/C31 判据(目录税棘轮+注入区合一+计数断言内容级门禁) | blocked | - | 焚诀 eval 只读红线，待归属会话 | 2026-09-24 17:57 | - |
| R19-3 | P1 | 本仓9份基线JSON落 schemas/r19 契约族+校验器 | done | - | - | 2026-09-24 18:50 | 06-benchmark/baseline_contract_check_2026-09-24.json |
| VOL-1BFD2 | P1 | 体量治理[L1 记忆卷] memory/08-ac-obs.md — 非 4KB 拆卷目标：先裁口径（是否入 SPLIT_TARGETS / 加豁免册），禁自动拆 | done | - | - | 2026-09-25 21:30 | D:/global_skills/A-project-handoff/references/version-history.md#V3.57.0 豁免计量册条目 |
| VOL-858E6 | P1 | 体量治理[L2 根文档] AGENTS.md — 注入壳瘦身：历史条目迁 memory/ 分卷，壳内只留指针（handoff.py trim-shell） | todo | - | - | 2026-09-25 20:53 | - |
| VOL-D908D | P1 | 体量治理[L2 根文档] TODO.md — 注入壳瘦身：历史条目迁 memory/ 分卷，壳内只留指针（handoff.py trim-shell） | todo | - | - | 2026-09-25 20:53 | - |
| R57-1 | P1 | 推荐:rule_editor gates 输出截断机器化——mirror 明细须逐条打印（本轮因只看 tail 误判「他人脏项」，跑 check-skill-mirror.ps1 原文才发现 13 项全是自己的） | done | - | - | 2026-09-25 21:30 | D:/global_skills/A-memory-start/references/rule_editor.py#GATE_DETAIL_LINES 明细打印（违规样本 13 项全见 + 正例 -Fix 后绿） |
| R57-2 | P1 | 推荐:memory/08-ac-obs.md（4,102B 超 4KB）裁口径——入 SPLIT_TARGETS 还是加豁免册（flow --verify-ac 整卷解析 08，拆卷会打断 AC 判定） | done | - | - | 2026-09-25 21:30 | volume_gov_stub.py 26/26（豁免册不判红 + 不在册照判两侧） |
| R57-3 | P1 | 推荐:注入壳 AGENTS.md 29,293B / TODO.md 31,909B 超 root_doc_max 16KB——走 trim-shell 迁历史条目（VOL-858E6/VOL-D908D 的落地） | todo | - | - | 2026-09-25 21:06 | - |
| VOL-2A600 | P1 | 体量治理[L1 记忆卷] memory/07-next-steps.md — 主卷注入面超告警线：按条数归档（savepoint 摘要归档 / trim-shell）或把长校正注迁分卷；P0 与红线内容禁自动改 | blocked | - | 摘要已按条数归档（主壳 138,304B→119,610B，-18,694B）；余量为 P0 活债 70KB + 分卷目录 36KB，须逐条人工裁决（禁自动改 P0） | 2026-09-25 21:49 | - |

## 推进记录

<!-- append-only，最新在下；由 flow --start / --done / --block 自动追加 -->

- [2026-09-24 17:57] R19-1 新增（P0，todo）
- [2026-09-24 17:57] R19-1 todo → blocked（派生件重建窗口未开且 global_skills 28 条在途）
- [2026-09-24 17:57] R19-2 新增（P0，todo）
- [2026-09-24 17:57] R19-2 todo → blocked（焚诀 eval 只读红线，待归属会话）
- [2026-09-24 17:57] R19-3 新增（P1，todo）
- [2026-09-24 18:50] R19-3 todo → done
- [2026-09-25 20:53] 体量体检登记 3 项（待判断项转任务，id 前缀 VOL-）
- [2026-09-25 21:06] R57-1 新增（P1，todo）
- [2026-09-25 21:06] R57-2 新增（P1，todo）
- [2026-09-25 21:06] R57-3 新增（P2，todo）
- [2026-09-25 21:30] 体量体检登记 1 项（待判断项转任务，id 前缀 VOL-）
- [2026-09-25 21:30] VOL-1BFD2 todo → done
- [2026-09-25 21:30] R57-1 todo → done
- [2026-09-25 21:30] R57-2 todo → done
- [2026-09-25 21:49] VOL-2A600 todo → blocked（摘要已按条数归档（主壳 138,304B→119,610B，-18,694B）；余量为 P0 活债 70KB + 分卷目录 36KB，须逐条人工裁决（禁自动改 P0））

## 分卷目录

<!-- 本文件超 4KB 时由 flow 自动调用拆卷能力，分卷索引写于此节（R199 体量治理） -->
