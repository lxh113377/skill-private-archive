# 06 - 已知约束

> 本文件记录已知问题、技术债和约束。
> 归档类型：增量（已解决的问题移入归档）
> 注（2026-09-22）：本文件**不是** `SPLIT_TARGETS` 注册目标（本项目默认仅 `07-next-steps` + `05-feature-status` 参与 4KB 语义，见 R199/R226），故体量可超 4KB；确需纳入时用 `handoff.py split "<项目>" --target 06-constraints.md`。

## 已知 Bug
<!-- 格式：- [BUG] 描述 — 影响范围 | 状态：未修复/修复中 -->
- [BUG→**已修复**] `handoff.py review` 判 `08-ac-obs.md: 3 个验收标准，格式正确`，实际这 3 条全在 `<!-- 示例： ... -->` 注释内 — 影响范围：**假通过**，交付就绪度被高估；根因 `handoff_lib/savepoint.py:632` 用 `re.findall(r"AC-OBS-\d+", content)` 全文匹配、不剔注释 | 状态：**已修复**（受管根 `7cc7d4d`，`A-project-handoff` **V3.42.0**；`common.py` 新增 `strip_html_comments()` 作单一真相源；层a 隔离桩 11/11 + 层b 含对照；本项目 `review` 56% → **100%**）
- [BUG→**已修复**] `handoff.py review` 判 `05-feature-status.md: 没有记录任何功能状态`，实际该文件有 10 条已完成条目 — 影响范围：**假阴性**，误导为「记忆未填」；根因同文件 `:594` 正则 `^-\s*(\[x\]|\[ \]|[✅🚧📋])` 只认 `- ✅` 形态，不认「`## ✅ 已完成` + 普通 `- 描述`」写法 | 状态：**已修复**（同上；新增 `has_feature_entries()` 兼容章节式；层b 反例 = 注释-only 合成项目仍报「没有定义 AC-OBS」，防线未放松）
- [BUG→**已修复**] `handoff.py status` 判 `02-structure.md ✅ filled (auto-synced)`，同日 `review` 判 `尚未运行 sync，目录树为空` — 影响范围：同一文件两子命令结论相反，门禁口径自相矛盾（`status` 只数非空行） | 状态：**已修复**（同上；`status` 结构类先判 `is_sync_placeholder()` 再累加计数，两子命令现同结论）
- [BUG→**部分解决**] `.rule_backup/` 全库备份集中落在 `D:\global_skills\A-memory-start\references\.rule_backup\`（内含 `A-project-handoff.*.bak`）— 影响范围：备份与目标 skill 分离，回滚定位成本高；且 32 个 `.bak` 全部未跟踪，污染 `git status` | 状态：**部分解决**（2026-09-22 第 10 轮复测：文件数 **51**；「未跟踪污染」已解决 —— 该目录随 D7 `172eb88` 被仓库跟踪，`git -C D:\global_skills status --porcelain` 实测**零条**；按「文件×日」分组实测**无一组 >5** ⇒ R198.7 不触发；**仅剩「集中落点」未改** ⇒ 见第 10 轮建议 #4）—— **✅ 校正注（2026-09-23 销账）：已闭环** —— B4 已执行（`rule_editor.py` 备份落点迁出受管根至 `global_memory_archive\_trash\rule_backup`，56 份 .bak 全迁，`undo` 双落点兼容）；本轮实测 `A-memory-start/references/.rule_backup` 下 `.bak` = **0**

- [BUG→已解除] `handoff.py savepoint` 于 2026-09-22 01:17 **曾被拒**：`[GATE:noise-fail]` VIOL `焚诀\.codebuddy\` —— 该目录是**运行中 IDE 的会话数据**（当日日志 mtime 分钟级），**不是 agent 交付物**。⚠️ 关键教训：**#17 字面处置「迁 `_trash`」在此是错的**（会破坏活动工具状态）；正确出口 = `noise_lint` 既有机制「被 `.gitignore` 命中 → 降级 `quarantine`」 — 状态：**已解除**（并行会话 2026-09-22 01:20:13 补 `焚诀\.gitignore:9` 的 `.codebuddy/`，commit `1f354e9`）→ `noise` 复跑 `[GATE:noise-pass]`（四根 violation=0），本项目 `savepoint` 复跑 **exit 0「本次对话已安全落盘」**
  - 归属说明（⚠️不能确证）：本会话确实执行过 `Set-Location …\焚诀`（cwd 曾为焚诀），故**可能是写入方之一**；但该目录性质为「活跃 IDE 会话数据」，同一时段另有并行会话在焚诀作业，无法单方归因。教训已吸收：跨受管根跑脚本改用 `Push-Location` + `Pop-Location`（本会话后段已改）

- [BUG] **`handoff.py review`/`status` 判据盲区：只判「文件是否被填充」，不做「主卷声明 vs 分卷已完成项」交叉校验** — 影响范围：**健康度评分对失效声明完全免疫**（R220 假通过族新形态）。2026-09-22 第 10 轮实测：`status` 报 **8/8 filled**、`review` 报 **9/9（100%）** 的**同时**，`06-constraints.md` 主卷仍有 3 条已修缺陷写成「未修复」、6 条已闭环技术债仍列，`05-feature-status.part1.md` 仍列 2 项已完成的 🚧 与 1 项已裁定的 ⛔ | 状态：**未修复**（2026-09-22 实测；修法涉受管根 review 判据，属破坏性改动 → 见第 10 轮建议 #11 / 待确认按钮）—— **✅ 校正注（2026-09-23 销账）：已修复** —— 上游由并行会话自行落地（受管根 `b7ba255`，R272 / v3.46.0：`savepoint.py` 新增 `_memory_volume_drift()`、`cmd_review` 接线）；本轮实测 `grep -c _memory_volume_drift savepoint.py` = 2、SKILL.md `version: 3.46.2`；我方独立复验层 a 6/6 + 层 b′ 2/2 + 层 b 3 项目零误报（见 `07-next-steps.part4.md` B8）

## 技术债
<!-- 格式：- [DEBT] 描述 — 建议的还债方式 -->
- [DEBT] **三仓均无 `pre-commit` hook**（2026-09-22 实测：`D:\global_skills` / 焚诀 / `D:\global_memory` 的 `.git/hooks` 仅 `post-commit`，其余全是 `*.sample`）—— 故「mirror / noise / evolution 已挂 `hooks/pre-commit`」（`04-plan/工作流专项建议.md` §4）属**设计意图而非既成事实**；影响：所有「hook 拦截后自动重试」的链路都是死代码（R270 已把 `--fix-mirror` 改为主动前置规避） | 处置：用户 2026-09-22 裁定**暂不补装**（改动面最小，改为「提交后按需跑 `gates`」）；如需恢复提交时拦截，须重新评估 fail-closed 对所有会话的影响
- [DEBT→**已闭环**] 记忆层与实况脱节（`01-goal` 六阶段目标 0 勾选 / `03`+`04` 空模板 / `06` 四节全空 / `08` 零条真实 AC）— 还债方式：本轮已回填（2026-09-22，见 `05-exec/第3轮执行报告.md`） | 状态：**已闭环**（`handoff.py status` 实测 **8/8 sections filled**）
- [DEBT→**已闭环**] 三重同义状态源（`TODO.md` / `memory/07-next-steps.md` / `memory/05-feature-status.md`）已实测漂移 — 还债方式：定 `memory/07` 为 P0 唯一真相源，`TODO.md` 降级为「阶段状态总表（索引）」（2026-09-22 已改） | 状态：**已闭环**（`TODO.md` 首行已写「非入口」并指向 `memory/07-next-steps.md`）
- [DEBT→**已闭环**] 工作区 git 仅 1 次提交（`49ff0d6` baseline）→ 无回滚粒度 — 还债方式：按主题逐步 commit（本轮改动待确认 D4） | 状态：**已闭环**（D4 起按主题拆分提交，实测 HEAD = `632d183`，累计 14 次提交）
- [DEBT→**已闭环**] `archive/` 为空目录 —— 归档机制从未执行（违反 handoff 致命纪律 #4「archive = 安全网」）— 还债方式：阶段切换前先 `handoff.py archive` | 状态：**已闭环**（实测 `archive/` 含 4 文件：`overlap_raw.txt` + `scope-v1-169-2026-09-14/` 3 件；`handoff.py status` 报 `Archived phases: scope-v1-169-2026-09-14`）
- [DEBT→**已闭环**] `01-scan/overlap_raw.txt`（282,977B）为阶段1 原始中间产物，滞留交付目录 — 还债方式：迁 `archive/`（待确认 D3） | 状态：**已闭环**（D3 已迁 `archive/overlap_raw.txt`）
- [DEBT→**已闭环**] `05-exec/` 19 个 patch JSON 无索引 — 还债方式：本轮已补 `05-exec/README.md`（2026-09-22） | 状态：**已闭环**（索引实测覆盖 19/19）
- [DEBT→**已闭环**] skill 数口径四数不一（记忆 169 / verify C1 实测 120 / 顶层目录 152 / 全盘 SKILL.md 205）→ 现行 P0 基数不可用 — 还债方式：先裁定口径再复核注册表（待确认 D2） | 状态：**已闭环**（口径裁定 = 注册表 **151**；焚诀 `verify` C1 实测「注册表 == 磁盘 (151 skills)」）

- [DEBT→**已闭环**] **受管根 39 条残留脏项未闭环**（2026-09-22 实测）：` D` **6**（5 个 `.rule_backup/*.bak` 已按 D3 迁 `global_memory_archive\_trash\backup-rotation\...`、`_bm_skillid_migration.json` 已按 #17 迁 `global_skills\_trash\`）+ `??` **33**（`.rule_backup/*.bak`，该仓库本就跟踪此目录）—— **非数据丢失、非本轮引入**（迁移目标磁盘可查） | 处置：需一次「提交迁移删除 + 跟进备份」的 git 提交（破坏性）→ 待确认 D7 | 状态：**已闭环**（D7 已执行，受管根 `172eb88`；2026-09-22 第 10 轮复测 `git -C D:\global_skills status --porcelain` **零条**）

- [DEBT] **焚诀 `NEGATIVE_TAG_MAP` 残留 7 个 ghost 键 + 7 处 ghost 引用**（2026-09-22 第 10 轮实测，`negative_tag_audit.py` 报 `健康率 72.5%` / `RESULT: FAIL`）：`skill-install` / `skill-creator` / `skills-security-check` / `install-skill-dependency` / `deep-research-pro` / `cloudbase-webapp-deploy-debug` / `clawhub` —— **7 个全部实测 `disk=False` 且不在注册表**（非判据假阳性，R263 已先证）。根因：D2 只系统性复扫了**直连表**（`direct_map`），**未同步复扫负标签表**（`tag_layer.py:NEGATIVE_TAG_MAP`） | 还债方式：清理 7 个 ghost 键 + 7 处引用后复跑 `negative_tag_audit.py`（健康率应 → 100%）+ `test_router_regression.py` ALL PASS → 见第 10 轮建议 #5（破坏性）—— **✅ 校正注（2026-09-23 销账）：已闭环** —— B1 已执行；本轮实测 `negative_tag_audit.py` = 健康率 100% / `RESULT: PASS`
- [DEBT] **`fenjue_measure.py:168` 引用不存在的 `behavior_core.md` 路径**（真实位置为 `core/behavior_core.md`）→ 取 size=0，**D1 少算该 P0 文件**（2026-09-22 第 10 轮 `attention_sim.py` 实测告警，属上游口径差异） | 还债方式：改 `fenjue_measure.py` 路径并重跑评分 → 见第 10 轮建议 #8（破坏性）—— **✅ 校正注（2026-09-23 销账）：已闭环** —— B3 已执行；本轮实测 `fenjue_measure.py:182` 已为 `core/behavior_core.md`

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
