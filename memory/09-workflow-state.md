# 09 - 动态工作流任务状态（状态唯一源）

> schema: fenjue-workflow-state-v1 | 本文件是**动态工作流引擎读取的任务状态表**（引擎侧唯一取数面）。
> 与 `07-next-steps.md` 的关系（按实现写，不写愿望）：`flow --sync` **只把 09 的 done/todo 勾选同步到 07**
> ——匹配到同一条目则改勾选位，匹配不到则在对应章节**追加**一行；若 07 已标完成而 09 不是 done，
> 它打印冲突并交人工裁决，**不覆盖 07**。任务表为空时 `--sync` 直接返回，此时 07 完全由人工维护。
> 因此：07 仍是项目台账的权威叙述面（可手工写）；09 只是引擎的任务视图，二者靠 sync 对齐勾选位。
> 状态枚举：`todo` / `doing` / `done` / `blocked`；批次：`P0` / `P1` / `P2`（`--next` **只在当前批次内取**：本批全 done 才进下一批；本批有 doing/blocked 而无可启动 todo 时**不跨批**，只列未完结项）。
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
| R19-1 | P0 | 注入面失真句批次整改(端数/版本戳10句+流程入描述24条+六段最小规范) | blocked | - | 轮93复查窗口仍关闭:焚诀根62条在途(57→62继续恶化,其中5条已staged),四输出面仍全M.另mcp-builder已入册(True,取值见r93汇报)但窗口仍被在途+四面M双重堵死 | 2026-10-01 14:07 | - |
| R19-2 | P0 | 转焚诀 C29/C30/C31 判据(目录税棘轮+注入区合一+计数断言内容级门禁) | blocked | - | 焚诀 eval 只读红线，待归属会话 | 2026-09-24 17:57 | - |
| R19-3 | P1 | 本仓9份基线JSON落 schemas/r19 契约族+校验器 | done | - | - | 2026-09-24 18:50 | 06-benchmark/baseline_contract_check_2026-09-24.json |
| VOL-1BFD2 | P1 | 体量治理[L1 记忆卷] memory/08-ac-obs.md — 非 4KB 拆卷目标：先裁口径（是否入 SPLIT_TARGETS / 加豁免册），禁自动拆 | done | - | - | 2026-09-25 21:30 | D:/global_skills/A-project-handoff/references/version-history.md#V3.57.0 豁免计量册条目 |
| VOL-858E6 | P1 | 体量治理[L2 根文档] AGENTS.md — 注入壳瘦身：历史条目迁 memory/ 分卷，壳内只留指针（handoff.py trim-shell） | blocked | - | r58 实测推翻 trim-shell 药方：根 AGENTS.md 是生成壳，体量=07 P0 面(70,919B)的函数，唯一收敛须逐条人工裁决 P0（红线禁自动改）⇒ 转 W-48 | 2026-09-26 12:30 | - |
| VOL-D908D | P1 | 体量治理[L2 根文档] TODO.md — 注入壳瘦身：历史条目迁 memory/ 分卷，壳内只留指针（handoff.py trim-shell） | done | - | - | 2026-09-26 12:30 | - |
| R57-1 | P1 | 推荐:rule_editor gates 输出截断机器化——mirror 明细须逐条打印（本轮因只看 tail 误判「他人脏项」，跑 check-skill-mirror.ps1 原文才发现 13 项全是自己的） | done | - | - | 2026-09-25 21:30 | D:/global_skills/A-memory-start/references/rule_editor.py#GATE_DETAIL_LINES 明细打印（违规样本 13 项全见 + 正例 -Fix 后绿） |
| R57-2 | P1 | 推荐:memory/08-ac-obs.md（4,102B 超 4KB）裁口径——入 SPLIT_TARGETS 还是加豁免册（flow --verify-ac 整卷解析 08，拆卷会打断 AC 判定） | done | - | - | 2026-09-25 21:30 | volume_gov_stub.py 26/26（豁免册不判红 + 不在册照判两侧） |
| R57-3 | P1 | 推荐:注入壳 AGENTS.md 29,293B / TODO.md 31,909B 超 root_doc_max 16KB——走 trim-shell 迁历史条目（VOL-858E6/VOL-D908D 的落地） | todo | - | - | 2026-09-25 21:06 | - |
| VOL-2A600 | P1 | 体量治理[L1 记忆卷] memory/07-next-steps.md — 主卷注入面超告警线：按条数归档（savepoint 摘要归档 / trim-shell）或把长校正注迁分卷；P0 与红线内容禁自动改 | blocked | - | 摘要已按条数归档（主壳 138,304B→119,610B，-18,694B）；余量为 P0 活债 70KB + 分卷目录 36KB，须逐条人工裁决（禁自动改 P0） | 2026-09-25 21:49 | - |
| W-46b | P1 | 清 noise_falsepositive_*.json 死句柄（补生成器或按 R241 摘牌留注），再把「pattern 必须有生成器」接进 run_gates 判红（r58 误报率 30.6% 已量清，真死句柄仅 1 条） | done | - | - | 2026-09-30 23:42 | 06-benchmark/全量对标报告_r66_W46b生成器面接线判红_2026-09-30.md |
| R58-1 | P1 | 第17维纵深：把「仓外输入固定」推广到受管根 clone/镜像面（21 道门读本地字节，与 CI 读 checkout 字节同构） | done | - | - | 2026-09-30 23:51 | 06-benchmark/全量对标报告_r67_R58-1仓外输入固定面本地面_2026-09-30.md |
| R76-1 | P1 | 项目/医 09 头回填收尾：待该文件在途收口后跑 flow <医> --fix-header（V3.115.0 判据会自行显形） | blocked | - | 轮94复查:09可解析(P2体量9todo),文件本身无在途,work输出停9-29,今日有体量体检(项目有人在);fix-header为写动作,待归属方执行,不代跑 | 2026-10-01 14:11 | - |
| R76-2 | P1 | 项目/陪聊 09 回填件提交：被其自有 pre-commit 交付件判据拦红（s08.png 从工作树消失 + SoulIsle 品牌分叉，均非本次引入），待归属方处置 | blocked | - | 轮94复查:归属方正在场作业(HEAD今日r88,18处M含品牌文档+新brand checker待入库);s08 tracked且留档在位,无删除项;回填提交待其收口,不代提交 | 2026-10-01 14:11 | - |
| R76-3 | P1 | M-4 接管试点：挑 1 条降级看守条目走完 claim→complete（命令在 r63 报告 §7 已固化） | done | - | - | 2026-10-01 03:19 | 06-benchmark/takeover_R76-3_M-1_evidence_2026-10-01.json |
| R76-4 | P2 | 通用「文档句子⇄行为」一致性判据（r74 §6 遗留 #1；轮76 补轮只把 09 头部引用块这一面机器化，通用面仍敞口。批次回到 P2 = 受管根 V3.116.0 已修「P2 无落点 ⇒ --check 永红」缺口，本行即常驻真面样本） | todo | - | - | 2026-10-01 01:56 | - |
| R76-5 | P1 | C33 类级缺口：焚诀 eval/build_memory_index.py 的 EXCLUDED 名册缺 .tmp 条目 ⇒ 任何会话在 GM 根用 .tmp/ 当暂存就会拦全库提交（本仓红线：焚诀 eval 只读，须归属方收口） | todo | - | - | 2026-10-01 02:43 | - |

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
- [2026-09-26 12:30] VOL-D908D todo → done
- [2026-09-26 12:30] VOL-858E6 todo → blocked（r58 实测推翻 trim-shell 药方：根 AGENTS.md 是生成壳，体量=07 P0 面(70,919B)的函数，唯一收敛须逐条人工裁决 P0（红线禁自动改）⇒ 转 W-48）
- [2026-09-26 12:31] W-46b 新增（P1，todo）
- [2026-09-26 12:31] R58-1 新增（P1，todo）
- [2026-09-30 23:42] W-46b todo → done
- [2026-09-30 23:51] R58-1 todo → done
- [2026-10-01 01:34] R19-1 blocked → blocked（轮76 实测窗口未开：焚诀根 42 条在途（其中 5 条已 staged＝他人提交在途），且 build_indexes --apply 的四个输出面 bge_fullbody_embeddings.npy / direct_map.json / truth_constants.json / inject_budget_ledger.jsonl 全部为 M ⇒ 强推必覆盖他人产物并把输出卷进他人那次提交）
- [2026-10-01 01:34] R76-1 新增（P1，todo）
- [2026-10-01 01:34] R76-2 新增（P1，todo）
- [2026-10-01 01:56] R76-3 新增（P1，todo）
- [2026-10-01 01:56] R76-4 新增（P2，todo）
- [2026-10-01 02:43] R76-5 新增（P1，todo）
- [2026-10-01 03:16] R76-3 todo → doing
- [2026-10-01 03:19] R76-3 doing → done
- [2026-10-01 03:56] R19-1 blocked → blocked（轮79复查窗口仍关闭:焚诀根57条在途(较轮76的42条增加,其中5条已staged=他人提交在途仍在),build_indexes四个输出面bge_fullbody_embeddings.npy/direct_map.json/truth_constants.json/inject_budget_ledger.jsonl全部仍为M.强推必覆盖他人产物）
- [2026-10-01 14:07] R19-1 blocked → blocked（轮93复查窗口仍关闭:焚诀根62条在途(57→62继续恶化,其中5条已staged),四输出面仍全M.另mcp-builder已入册(True,取值见r93汇报)但窗口仍被在途+四面M双重堵死）
- [2026-10-01 14:11] R76-1 todo → blocked（轮94复查:09可解析(P2体量9todo),文件本身无在途,work输出停9-29,今日有体量体检(项目有人在);fix-header为写动作,待归属方执行,不代跑）
- [2026-10-01 14:11] R76-2 todo → blocked（轮94复查:归属方正在场作业(HEAD今日r88,18处M含品牌文档+新brand checker待入库);s08 tracked且留档在位,无删除项;回填提交待其收口,不代提交）

## 分卷目录

<!-- 本文件超 4KB 时由 flow 自动调用拆卷能力，分卷索引写于此节（R199 体量治理） -->
