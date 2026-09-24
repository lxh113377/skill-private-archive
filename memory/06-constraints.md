# 06 - 已知约束

> 本文件记录已知问题、技术债和约束。
> 归档类型：增量（已解决的问题移入归档）
> 注（2026-09-22）：本文件**不是** `SPLIT_TARGETS` 注册目标（本项目默认仅 `07-next-steps` + `05-feature-status` 参与 4KB 语义，见 R199/R226），故体量可超 4KB；确需纳入时用 `handoff.py split "<项目>" --target 06-constraints.md`。
> 注（2026-09-23，A-project-handoff **V3.48.0** 校正注，上一条保留作历史留痕）：本文件已纳入 `trim-shell` **条目归档自愈**（`TRIM_ENTRY_TARGETS`；**仍不入** `SPLIT_TARGETS`）——「已知 Bug / 技术债」两章节内的**已闭环/已修复/已解除**条目前往 `06-constraints.partN.md`；**红线等活载章节**与**未闭环条目**（含含「未修复/未闭环」字样者，fail-safe 保守留守）永久留主卷，故主卷体量可超 4KB 属设计内（不再视为违规）。

## 已知 Bug
<!-- 格式：- [BUG] 描述 — 影响范围 | 状态：未修复/修复中 -->
- [BUG→**部分解决**] `.rule_backup/` 全库备份集中落在 `D:\global_skills\A-memory-start\references\.rule_backup\`（内含 `A-project-handoff.*.bak`）— 影响范围：备份与目标 skill 分离，回滚定位成本高；且 32 个 `.bak` 全部未跟踪，污染 `git status` | 状态：**部分解决**（2026-09-22 第 10 轮复测：文件数 **51**；「未跟踪污染」已解决 —— 该目录随 D7 `172eb88` 被仓库跟踪，`git -C D:\global_skills status --porcelain` 实测**零条**；按「文件×日」分组实测**无一组 >5** ⇒ R198.7 不触发；**仅剩「集中落点」未改** ⇒ 见第 10 轮建议 #4）—— **✅ 校正注（2026-09-23 销账）：已闭环** —— B4 已执行（`rule_editor.py` 备份落点迁出受管根至 `global_memory_archive\_trash\rule_backup`，56 份 .bak 全迁，`undo` 双落点兼容）；本轮实测 `A-memory-start/references/.rule_backup` 下 `.bak` = **0**

- [BUG] **`handoff.py review`/`status` 判据盲区：只判「文件是否被填充」，不做「主卷声明 vs 分卷已完成项」交叉校验** — 影响范围：**健康度评分对失效声明完全免疫**（R220 假通过族新形态）。2026-09-22 第 10 轮实测：`status` 报 **8/8 filled**、`review` 报 **9/9（100%）** 的**同时**，`06-constraints.md` 主卷仍有 3 条已修缺陷写成「未修复」、6 条已闭环技术债仍列，`05-feature-status.part1.md` 仍列 2 项已完成的 🚧 与 1 项已裁定的 ⛔ | 状态：**未修复**（2026-09-22 实测；修法涉受管根 review 判据，属破坏性改动 → 见第 10 轮建议 #11 / 待确认按钮）—— **✅ 校正注（2026-09-23 销账）：已修复** —— 上游由并行会话自行落地（受管根 `b7ba255`，R272 / v3.46.0：`savepoint.py` 新增 `_memory_volume_drift()`、`cmd_review` 接线）；本轮实测 `grep -c _memory_volume_drift savepoint.py` = 2、SKILL.md `version: 3.46.2`；我方独立复验层 a 6/6 + 层 b′ 2/2 + 层 b 3 项目零误报（见 `07-next-steps.part4.md` B8）

- [BUG] **跨会话夹带：`rule_editor.py commit` 按「整文件」提交，工作区存在他人同文件在途改动时会一并入库** — 影响范围：**白名单隔离纪律被静默击穿**（他人在途改动被记入我的提交，其工作区随之变「干净」，双方都误判为「已收口」）。2026-09-23 第 13 轮 r5 实测：我方改 `A-project-handoff/scripts/handoff_lib/splitvol.py` 时，并行会话正把 `"09-workflow-state.md"` 加入 `SPLIT_TARGETS`（其 `handoff.py` / `handoff_lib/audit.py` / `handoff_lib/common.py` / `handoff_lib/flow.py` / `scripts/templates/09-workflow-state.md.tmpl` 仍未提交）⇒ 我方提交 `f6f5b0c` 把该 1 行一并带入。**非数据丢失、未改写其内容**（重编号补丁窗口 0 命中该行，原文入库） | 状态：**未修复**（工具行为层；处置建议 = 提交前逐文件比对 `git -C <root> status --porcelain`，只对「确属本次改动」的文件走 `commit`；或上游在 `commit` 增加「同文件他人改动」预检）—— 本轮处置：**不回滚**（回滚 = 抹掉他人在途工作），只登记 + 知会

- [BUG] **技能计数分母三态不一致（151 / 166 / 167），且历史登记句已失真** — 影响范围：一切以「151」为分母的结论（r10 报告全篇、07 主卷 r13/r17/r17b 三处摘要与「基线校正 103/151」）分母已失效；本项目扫描器按设计跳过 junction 目录，与注册表口径天然差 1。取值命令（三者各自实测，勿硬编码）：注册表口径 = `python 焚诀/eval/verify_truth_consistency.py` 看 C1 行；本仓工具口径 = `python 05-exec/description_baseline_scan.py` 看「SKILL.md 总数」；差集来源 = `ls -d D:/global_skills/*/ ` 中对 `LNK` 模式项（本轮实测 = `rag-eval`）。2026-09-24 r18 实测：C1 = **167**、扫描器 = **166**、r10 报告 = 151（陈旧一周）。 | 状态：**未修复**（本轮已按 R241 在 `06-benchmark/全量对标报告_r18_2026-09-24.md` §0 出校正注 + §5 P1-C 立「统计必须引用 C1 行」规程；改写历史登记句被红线禁止）

## 技术债
<!-- 格式：- [DEBT] 描述 — 建议的还债方式 -->
- [DEBT] **三仓均无 `pre-commit` hook**（2026-09-22 实测：`D:\global_skills` / 焚诀 / `D:\global_memory` 的 `.git/hooks` 仅 `post-commit`，其余全是 `*.sample`）—— 故「mirror / noise / evolution 已挂 `hooks/pre-commit`」（`04-plan/工作流专项建议.md` §4）属**设计意图而非既成事实**；影响：所有「hook 拦截后自动重试」的链路都是死代码（R270 已把 `--fix-mirror` 改为主动前置规避） | 处置：用户 2026-09-22 裁定**暂不补装**（改动面最小，改为「提交后按需跑 `gates`」）；如需恢复提交时拦截，须重新评估 fail-closed 对所有会话的影响
- [DEBT→**已闭环**] **受管根 39 条残留脏项未闭环**（2026-09-22 实测）：` D` **6**（5 个 `.rule_backup/*.bak` 已按 D3 迁 `global_memory_archive\_trash\backup-rotation\...`、`_bm_skillid_migration.json` 已按 #17 迁 `global_skills\_trash\`）+ `??` **33**（`.rule_backup/*.bak`，该仓库本就跟踪此目录）—— **非数据丢失、非本轮引入**（迁移目标磁盘可查） | 处置：需一次「提交迁移删除 + 跟进备份」的 git 提交（破坏性）→ 待确认 D7 | 状态：**已闭环**（D7 已执行，受管根 `172eb88`；2026-09-22 第 10 轮复测 `git -C D:\global_skills status --porcelain` **零条**）

- [DEBT] **「P0 强制注入区」双源定义互不校验，且最大一块注入面无任何棘轮** — 现状（2026-09-24 r18 实测）：① 焚诀 C25（定义在 `焚诀/eval/verify_checks/governance_layer.py:85`，清单在 `truth_constants.INJECT_BUDGET_FILES`）只测 **5 文件 / 61,472B**，硬顶 65,536B；② `焚诀/audit/attention_sim.py` 的 `ctx_tax.p0` 只测 **6 文件 / 16,372B**；两集合**仅 1 个文件重叠**，并集 **10 文件 / 69,494B 已超 C25 硬顶 3,958B，而 C25 仍判 PASS**。③ C25 的 `shell_project AGENTS.md` 按 **cwd 解析** ⇒ 实钉焚诀（5,836B），**其它项目的注入壳完全在预算外**（本项目 AGENTS.md 体量用 `stat -c%s 本仓/AGENTS.md` 取值）。④ 平台技能目录（167 条 name+description，实测 45,173 字符 ≈ 128k 窗口 35.3% = C25 硬顶 2.07 倍）**不被任一棘轮覆盖**，且随技能数线性恶化（一周 151→167 = +10.6%） | 影响范围：预算门禁给出「安全」信号的同时，真实每轮注入成本是它的 2~3 倍 | 还债方式：转焚诀归属会话落 **C29 目录税棘轮 + 注入区口径合一**（判据/数字/命令已备好，见 `06-benchmark/全量对标报告_r18_2026-09-24.md` §6 P0-A/P0-B）；**本项目红线：不代改 `焚诀/eval/`** | 状态：**未修复**（登记待归属会话）
- [DEBT] **P0 真相源被高频改写却无累积语义复核** — `python 05-exec/cumulative_drift_scan.py --days 30 --threshold 5` 实测（2026-09-24，四根合计 316 commits）：本项目 `memory/07-next-steps.md` **35 次/30 天**、`A-project-handoff/SKILL.md` 17、`A-memory-start/SKILL.md` 11、`A-get-memory/SKILL.md` 5；规则/技能类超阈值候选 **16 条**。对标出处：mycelium-hq/ai-brain-starter `scripts/drift-detection.py`（阈值 5 次/30 天）+ Microsoft DELEGATE-52（约 20 次改写损坏 ~25% 内容）。既有 R272 `_memory_volume_drift()` 只查**结构**漂移（主卷 vs 分卷），不查改写频次累积 ⇒ 本轮已借此抓到 1 个真实失真句（见上条 [BUG]） | 影响范围：越承重的句子越可能被改到失真而无人复核 | 还债方式：按扫描器 16 条清单逐条人工语义复核并出「仍然成立/已失真」结论（P0-C，本项目自持，不依赖上游）| 状态：**未修复**（工具已就位，复核进行中）

## 红线（不能改）
<!-- 绝对不能修改的模块/约定 -->
- 阶段 0-3 **只读取证**：不改 `D:\global_skills` 下任何 skill 源文件，只在本工作区写报告（`memory/AGENTS.md` 铁律）
- 阶段 4 起改 skill 文件，**唯一途径 = `rule_editor.py`**；禁 `write_file` 整体重写
- 历史留痕不可改写（R241）：历史报告/日志里的旧数字、旧结论**不得直接改成当前值**，只能加「校正注」
- 受管根（`D:\global_skills` / `D:\global_memory` / `D:\global_memory_archive` / 焚诀）内散落项**只迁 `_trash`，禁止删除**
- 改 `D:\global_skills` 后必须复跑三门禁（mirror / noise / evolution）

## 性能/兼容性约束
<!-- 性能要求、浏览器兼容性、系统兼容性等 -->
- 平台：Windows + PowerShell；Python 用 `C:\Program Files\Python312\python.exe` 或 managed venv
- 跑任何 py 前须设 `PYTHONPYCACHEPREFIX`（防 `__pycache__` 重建在受管根内）
- PowerShell 下 `rg` / `grep` 均不可用 → 降级 `Get-ChildItem | Select-String`（禁静默当 0 命中）
- 记忆单文件硬上限 4KB（`07`/`05` 为 SPLIT_TARGETS，超限由 `split`/`trim-shell` 处理）

## 环境隔离（R196，init 必填）
<!-- 声明当前运行环境模式；dev 禁连 prod 库/密钥；production 操作前必须有近期备份 -->
- env_mode: development（枚举：development / staging / production）
- 红线：dev/staging 禁止连接 production 数据库与 API key
- production 操作前检查：近期备份存在（archive/ 或 DR 快照 ≤7 天）+ 密钥不复用
- 保护文件 .env.prod / .env.production 禁止入库（.gitignore 已含规则）
- ⚠️ 本项目实况：`.git` 存在、**无任何 `.env` 密钥文件**；远端为私有归档仓（非生产环境）

## 范围 / 口径裁定（用户确认，留痕）

- **[裁定 2026-09-22] 自建口径 = HIGH 51 + MID 26 = 77 条**（阶段0 v2 清单，基数 = 注册表 **151** 条 = 磁盘实测）—— 此后所有比例/覆盖率统计**只以此数为分母**
- **[裁定 2026-09-22] LOW（灰区）30 条维持「排除维护范围」**：不入自建维护清单，但**已在册的仍参与路由**
- **[裁定 2026-09-22] EXCLUDE 43 条确认为市场/上游件**，排除
- **已作废基数**：「自建 ≈90 / 基数 169」（v1 时代）**不再引用**；v1 清单原样归档 `archive/scope-v1-169-2026-09-14/`

## 评测集隔离（R196）
<!-- 标注测试专用文件，禁止把训练数据写入测试集；新增评测数据先登记 provenance -->
- 测试专用文件清单：无（本项目不产出评测集）
- 红线：训练/生产数据禁止写入测试专用文件；新增评测数据先登记来源（provenance）
- 相关但非本项目资产：焚诀 `eval/` 下的 BGE 索引与 `verify_truth_consistency.py` 属**外部依赖**，只读调用不改

## 分卷目录
- **卷1** `06-constraints.part1.md` — 已完成条目归档（R224 主壳自愈）
- **卷2** `06-constraints.part2.md` — 06-constraints 分卷（R199 自动拆卷）
- **卷3** `06-constraints.part3.md` — 06-constraints 分卷（R199 自动拆卷）

