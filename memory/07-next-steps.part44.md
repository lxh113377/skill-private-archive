# 07-next-steps.part44.md

<!-- 本卷为 07-next-steps.part43.md 的延续 -->

## 最近对话摘要（历史）

- [ ] R76-1 项目/医 09 头回填收尾：待该文件在途收口后跑 flow <医> --fix-header（V3.115.0 判据会自行显形）（由 flow 登记；状态: todo）
- [x] R58-1 第17维纵深：把「仓外输入固定」推广到受管根 clone/镜像面（21 道门读本地字节，与 CI 读 checkout 字节同构）（由 flow 登记；状态: todo）
- [x] W-46b 清 noise_falsepositive_*.json 死句柄（补生成器或按 R241 摘牌留注），再把「pattern 必须有生成器」接进 run_gates 判红（r58 误报率 30.6% 已量清，真死句柄仅 1 条）（由 flow 登记；状态: todo）
- [ ] VOL-2A600 体量治理[L1 记忆卷] memory/07-next-steps.md — 主卷注入面超告警线：按条数归档（savepoint 摘要归档 / trim-shell）或把长校正注迁分卷；P0 与红线内容禁自动改（由 flow 登记；状态: todo）
- [ ] R57-3 推荐:注入壳 AGENTS.md 29,293B / TODO.md 31,909B 超 root_doc_max 16KB——走 trim-shell 迁历史条目（VOL-858E6/VOL-D908D 的落地）（由 flow 登记；状态: todo）
- [x] R57-2 推荐:memory/08-ac-obs.md（4,102B 超 4KB）裁口径——入 SPLIT_TARGETS 还是加豁免册（flow --verify-ac 整卷解析 08，拆卷会打断 AC 判定）（由 flow 登记；状态: todo）
- [x] R57-1 推荐:rule_editor gates 输出截断机器化——mirror 明细须逐条打印（本轮因只看 tail 误判「他人脏项」，跑 check-skill-mirror.ps1 原文才发现 13 项全是自己的）（由 flow 登记；状态: todo）
- [x] VOL-D908D 体量治理[L2 根文档] TODO.md — 注入壳瘦身：历史条目迁 memory/ 分卷，壳内只留指针（handoff.py trim-shell）（由 flow 登记；状态: todo）
- [ ] VOL-858E6 体量治理[L2 根文档] AGENTS.md — 注入壳瘦身：历史条目迁 memory/ 分卷，壳内只留指针（handoff.py trim-shell）（由 flow 登记；状态: todo）
- [x] VOL-1BFD2 体量治理[L1 记忆卷] memory/08-ac-obs.md — 非 4KB 拆卷目标：先裁口径（是否入 SPLIT_TARGETS / 加豁免册），禁自动拆（由 flow 登记；状态: todo）
- [x] R19-3 本仓9份基线JSON落 schemas/r19 契约族+校验器（由 flow 登记；状态: todo）

- [x] 阶段2 按族分批全量精读 102 个自建 skill —— 6 份族审计卡，7 批（2026-09-14）
- [x] 裁定 LOW 灰区 33 个归属 —— 用户裁定 **排除**（2026-09-14）
- [x] `A-memory-start` Step 0.6 补 PowerShell `&` 调用符与 venv 降级链 —— `c3dba47`
- [x] `direct_map` 误命中复核 —— ⚠️ 复核已完成、**修正未做**，已上提主卷 P0 第 1 条

## 最近对话摘要（历史）

- 2026-09-14 — 阶段0 完成：三源交叉裁定自建清单，判定逻辑两轮修正（① `user_created=false` -4 权重过重误杀本地目录 → 改硬排除市场信号；② 补 frontmatter homepage 第四源）。结论 自建 102 / EXCLUDE 34 / 灰区 33 / 注册表失真 42；同时 init 项目记忆（10 文件 + P-1 绑定表 11 行）。

- [x] **【P1·待办 W-13（r43 新立）】** 账龄尺改用**标题锚点**定位待办（现按行号）： 【r49 裁决=执行完毕｜标题锚点定位已落地于 05-exec/r38_debt_aging.py:88 find_item_line() 与 05-exec/r46_mark_verdict.py:37 find_item_lines()，全链零行号索引（r44 提交 017595e）】

- [x] **【P0·下轮首推 W-11（r42 Phase 4 已写测试未落地）】** 账龄尺补两态两档：① `REPEAT`（同一条被改期 >=2 次 ⇒ 单列，禁无限滚延期）；② 宽限期按优先级分档 `GRACE_BY_PRIORITY = P0:2 / P1:4 / P2:8`（现统一 2 轮，P2 长期项被误判 OVERDUE 制造噪音）。失败测试已入库：`python 05-exec/r39_debt_ledger_fixtures.py` → t30/t32/t33/t34 红，落地即转绿。 【r44 裁决=执行完毕｜已落地 `find_item_line()`（只认未勾选项、多命中由调用方拒写），t40/t41/t42/t46 四例覆盖；D55 那类行号漂移不再有写入错位风险】
