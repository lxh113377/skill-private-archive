# AGENTS.md — 自建skill优化

> 自动生成: 2026-09-23 06:27:56


## 最近对话摘要
- **2026-09-23（第 13 轮 r1–r6）** — 性能瓶颈三维实测分析 → P0-1/P0-2 落地（A-memory-start -64% / contract -58%） → 上游 trim-shell 双重盲区修复（V3.47.0）→ **06 纳入口径 V3.48.0**（注入壳 -6,435B/轮） → **noise_lint 假阳性根因修**（`d88b5ee`，savepoint 由被拒→安全落盘）。**逐轮全量记录（原样，零改写）见 `07-next-steps.part7.md`**

---

# 01 - 项目目标

## 项目名称
自建skill优化

## 一句话描述
对 `D:\global_skills` 下用户自建的 skill 及其搭载的工作流做全量体检与优化设计，产出「审计报告 + 逐项实施计划」，分 6 阶段推进。

## 核心价值
- 解决「自建 skill 到底哪些算自建、哪些该修、哪些该合并」长期无清单、靠记忆拍脑袋的问题
- 四个维度同时体检：触发命中率与路由 / 体积注意力税 / 死链·过时引用·规则冲突 / 重复合并与工作流闭环
- 产出可直接执行的整改清单（目标文件 + 改动 + 验证命令 + 回滚手段），而不是一份看完就忘的评论

## 范围裁定（2026-09-22 用户确认「维持」）

- **自建口径 = HIGH 51 + MID 26 = 77 条**（阶段0 v2 清单；基数 = 注册表 **151** 条 = 磁盘实测，焚诀 verify C1 全等）
- **LOW（灰区）30 条**：维持 v1 口径「排除维护范围」—— 不入自建维护清单，但**已在册的仍参与路由**
- **EXCLUDE 43 条**：确认为市场/上游件，排除
- 权威范围文件 = `00-scope/自建skill清单.md`（v2）；v1（169 时代）已原样归档 `archive/scope-v1-169-2026-09-14/`
- ⚠️ 已作废基数：项目记忆旧称「自建 ≈90 / 基数 169」**不再引用**（详见 `05-exec/第3轮执行报告.md` 第十节）

## 当前阶段目标
- [x] 阶段0 范围裁定：三源交叉判定自建清单，产出高/中/低置信度名单与注册表失真条目 —— `00-scope/`（3 文件）
- [x] 阶段1 四维机器扫描：复用 `焚诀\audit\` 现成脚本建基线与评分表 —— `01-scan/`（4 文件）；⚠️ `attention_sim.py` / `content_snr.py` / `negative_tag_audit.py` 仍未跑
- [x] 阶段2 全量精读：按族分批精读全部自建 skill，产出结构化审计卡 —— `02-review/` 6 份族审计卡（7 批）
- [x] 阶段3 审计报告：四维综合结论 + P0/P1/P2 分级清单 —— `03-audit/自建skill优化审计报告.md`
- [x] 阶段4 实施计划：逐项的目标文件 / 改动内容 / 验证命令 / 回滚手段，按 P0→P1→P2 分批 —— `04-plan/实施计划.md`（5 批 40+ 项）
- [ ] 阶段5 工作流专项：七步闭环落地率、footer 协议、三道门禁、`direct_map` 误命中修正 —— 🚧 进行中：三门禁已绿、闭环落地率已实测、`direct_map` 误命中与**7 个死目标全数修正**（焚诀 `bf5e284`）、注册表 `user_created` 口径已裁定为 **151 条**（焚诀 `28daf6e`）

## 已完成目标
- [x] 阶段0-4 主体交付（2026-09-14）—— 六阶段中前五阶段产物齐备
- [x] 批1/批2/批3/批4 实施（2026-09-14 ~ 09-19）—— 路径漂移 34 处、死链 6 项、12 个 skill 拆卷/元数据、P0 单点修复 5 项
- [x] 项目版本控制基线（2026-09-21）—— `.git` + `.gitignore` + 私有远端 + SHA 核对达标（handoff 致命纪律 #20）

---

# 02 - 仓库结构

```
├── .codebuddy/
│   ├── plans/
│   │   └── 自建skill体系优化审计_33834ceb.md
│   └── settings.local.json
├── 00-scope/
│   ├── scope_result.json
│   ├── 注册表失真条目.md
│   └── 自建skill清单.md
├── 01-scan/
│   ├── scan_all.py
│   ├── scan_report.md
│   └── scan_result.json
├── 02-review/
│   ├── A族_精读.md
│   ├── fenjue族_精读.md
│   ├── local族_精读.md
│   ├── skill审计族_精读.md
│   ├── story族_精读.md
│   └── 其他族_精读.md
├── 03-audit/
│   └── 自建skill优化审计报告.md
├── 04-plan/
│   ├── 剩余待办分类清单.md
│   ├── 实施计划.md
│   └── 工作流专项建议.md
├── 05-exec/
│   ├── D1-patches/
│   │   ├── d5_gap_note.txt
│   │   ├── p1.json
│   │   ├── p1_anchor.txt
│   │   ├── p1_inserted.txt
│   │   ├── p2_savepoint.json
│   │   ├── p3_projcmds.json
│   │   ├── p4_version.json
│   │   ├── p5_vh.json
│   │   └── README.md
│   ├── A5_patch.json
│   ├── direct_map_dead_targets.json
│   ├── direct_map_dead_targets.py
│   ├── patch_P0-10_hook-analyzer.json
│   ├── patch_P0-10_report-generator.json
│   ├── patch_P0-10b_hook-analyzer.json
│   ├── patch_P0-10b_report-generator.json
│   ├── patch_P0-12_openclaw-fenjue-weekly.json
│   ├── patch_P0-14_cps-part8.json
│   ├── patch_P0-14_cps-skillmd.json
│   ├── patch_P0-2_cps-part1.json
│   ├── patch_P0-2_cps-part2.json
│   ├── patch_P0-2_cps-part3.json
│   ├── patch_P0-2_cps-part4.json
│   ├── patch_P0-2_cps-part5.json
│   ├── patch_P0-2_cps-part6.json
│   ├── patch_P0-2_cps-part7.json
│   ├── patch_P0-2_cps-part8.json
│   ├── patch_P0-2_cps-skillmd.json
│   ├── patch_P0-5_chaoshi-image.json
│   ├── patch_P0-6_fenjue-routing.json
│   ├── README.md
│   ├── user_created_audit.json
│   ├── user_created_audit.py
│   ├── 第2轮执行报告.md
│   └── 第3轮执行报告.md
├── .aiexclude
├── AGENTS.md
├── README.md
└── TODO.md
```

## 模块说明
- `00-scope/` — 阶段0 范围裁定：自建清单 + 注册表失真条目 + 原始打分数（`scope_result.json`）
- `01-scan/` — 阶段1 四维机器扫描：报告 + 结果 JSON + 重叠原始件 + **唯一可复跑脚本 `scan_all.py`**
- `02-review/` — 阶段2 全量精读：6 份族审计卡（A族 / fenjue / 审计族 / local / story / 其他）
- `03-audit/` — 阶段3 审计报告：四维结论 + P0/P1/P2 分级
- `04-plan/` — 阶段4 实施计划与阶段5 专项建议（含验证命令 + 回滚手段）
- `05-exec/` — 阶段4/5 **执行证据**：`README.md`（补丁索引）+ 2 份轮次报告 + 19 个 patch JSON
- `memory/` — handoff 8 文件 + 分卷 + `AGENTS.md`（P-1 绑定表）+ `archive/`（安全网，**当前为空**）
- `.codebuddy/` — 平台元数据（plans / 记忆），已在 `.gitignore` 内，不入库

---

# 03 - 技术栈

（未检测到技术栈配置文件）

## 构建与部署
- 构建：无构建流程。产物为 Markdown 报告 + JSON 数据 + patch JSON，直接落盘。
- 部署：无部署。唯一"发布"动作 = `git commit` + `git push` 到私有归档仓
  `https://github.com/lxh113377/skill-private-archive.git`（基线判据：`git rev-parse HEAD` == `git ls-remote origin main`）。

## 运行时要求
- **执行环境**：Windows + PowerShell 7（core）。
- **Python**：本机实测可用 `C:\Program Files\Python312\python.exe`（首选）；焚诀门禁用 managed venv
  `C:\Users\37533\.workbuddy\binaries\python\envs\default\Scripts\python.exe`（依赖已对齐，含 onnxruntime BGE 后端）。
- **必设环境变量**：`PYTHONPYCACHEPREFIX`（防 `__pycache__` 重建在受管根内）。
- **外部依赖（脚本级，非包管理）**：
  - `D:\global_skills\A-project-handoff\scripts\handoff.py` —— 项目记忆管理（init/sync/review/savepoint/split/noise）
  - `D:\global_skills\A-memory-start\references\rule_editor.py` —— 受管根规则文件编辑 + 三门禁（mirror/noise/evolution）
  - `C:\Users\37533\Desktop\workspace\焚诀\eval\` —— `unified_router.py`（路由）/ `verify_truth_consistency.py`（真相源）
- **编码**：全部 UTF-8，无 BOM。

---

# 04 - 核心文件地图

### 文档: `README.md`

## 核心逻辑文件
| 文件 | 作用 | 类型 |
|---|---|---|
| `README.md` | **工作区入口**：读法顺序 + 六阶段产物地图 + 门禁复跑命令 | 文档 |
| `memory/07-next-steps.md` | **跨会话唯一入口**；P0 唯一真相源（handoff 致命纪律 #1） | 状态 |
| `memory/05-feature-status.md` | 已完成 / 进行中 / 阻塞 | 状态 |
| `memory/AGENTS.md` | P-1 项目级 Skill 绑定表（命中即加载，防漏用） | 绑定 |
| `TODO.md` | 阶段状态总表（**索引，非入口**）；指向 `memory/07` | 索引 |
| `01-scan/scan_all.py` | 阶段0/1 唯一可复跑工具：三源交叉裁定 + 四维机器扫描 | **脚本**（20,274B） |
| `00-scope/自建skill清单.md` | 自建清单裁定结论（HIGH/MID/LOW + 排除信号） | 结论 |
| `00-scope/注册表失真条目.md` | 注册表 `user_created` 失真条目 | 结论 |
| `01-scan/scan_report.md` | 阶段1 四维机器扫描报告 | 结论 |
| `02-review/*_精读.md` | 6 份族审计卡（A族 / fenjue / 审计族 / local / story / 其他） | 结论 |
| `03-audit/自建skill优化审计报告.md` | 阶段3 全量审计结论（P0 25 项分级） | 结论 |
| `04-plan/实施计划.md` | 阶段4 逐项实施计划（含验证命令 + 回滚手段） | 计划 |
| `04-plan/工作流专项建议.md` | 阶段5 工作流专项（闭环落地率 / footer / direct_map 5 步） | 计划 |
| `05-exec/README.md` | 执行证据索引（19 个 patch JSON ↔ P0 编号 ↔ commit） | 索引 |
| `05-exec/第3轮执行报告.md` | 2026-09-22 四维体检 + 建议清单 + 待确认破坏性项 | 报告 |
| `01-scan/overlap_raw.txt` | 阶段1 原始重叠扫描件（282,977B，**中间产物**，待归档） | 原始件 |

## 配置文件
| 文件 | 作用 |
|---|---|
| `.gitignore` | 生成物 / 备份叠层 / 编辑器元数据（含 `.codebuddy/`）/ 密钥四类边界；已实测生效 |
| `.aiexclude` | 让 AI 搜索跳过噪声目录（init 自动生成） |
| `.codebuddy/plans/自建skill体系优化审计_33834ceb.md` | 平台生成的会话计划（.gitignore 已排除，不入库） |

---

# 05 - 功能状态

## ✅ 已完成

- 上游根因修：**noise_lint 二级扫描三处口径一致性修补**（2026-09-23 第 13 轮 r6，受管根 `d88b5ee`，仅 1 文件 44 行）：① 一级豁免传递（一级判 `quarantine` 的顶层项不再深扫，顺带留档免重复调 git）；② 二级子项自身命中 `QUARANTINE_DIRS`（如 `_bak`）即跳过（与一级同一判定入口）；③ junction/符号链接顶层项跳过二级扫描（内容归目标根口径，覆盖不丢只去重，新增 `is_reparse_dir()`）；验证 = 层a 隔离桩 **14/14**（含修前/修后对照：修前报 `sub/_bak`+`ignored_dir/_bak`+`jnk/_bak` 三处假阳性 vs 修后 0；三类真散落修前修后均判 VIOL）+ 层b `noise` 四根复跑 **`[GATE:noise-pass]`**（焚诀 38/15/**0**）；本项目 savepoint 由被拒 → **安全落盘**；⚠️ 版本行/版本历史/`commands.md §11` 三处文档同步**暂缓**（并行会话已占用 3.49.0 正在改这三个文件，避免二次夹带）
- 上游口径落地：**06-约束卷纳入「条目归档自愈」**（2026-09-23 第 13 轮 r5，A-project-handoff **V3.48.0**）：① 设计 = `TRIM_ENTRY_TARGETS`（07+05+06）与 `SPLIT_TARGETS` **解耦**——06 含红线等必须始终可见章节，通用拆卷会搬走它们，故只走条目归档；② 判据 = `closed_marker`（已修复/已闭环/已解除/已销账 且 不含 未修复/未闭环/部分解决/待观察…）+ **留痕章节白名单**（只迁「已知 Bug」「技术债」）+ **分区不变式**（归档∪留守 = 原文，只搬不移除/不复制）；③ 配套：承接卷就地续拆、CLI 迁后复跑拆卷、`volume_health` 活载卷只读可见；④ 验证 = 层a 隔离桩 **34/34** + 既有 V3.47.0 桩 15/15 复跑全绿（07/05 零回归）+ 层b 真机（焚诀 06 零变更；本项目 06 13,075B→7,097B 迁 13 条、行守恒 missing=0/dup=0、红线留主卷）；⑤ 收益 = 本项目注入壳 **33,029B → 26,594B（-6,435B/轮）**，其中 06 节 12,148B→6,182B

## 分卷目录
- **卷1** `05-feature-status.part1.md` — 进行中 / 计划中 / 阻塞
- **卷2** `05-feature-status.part2.md` — 已完成：2026-09-19 第 3 轮（P0-2 收口 + 补建上游 + 注册表重建）
- **卷3** `05-feature-status.part3.md` — 已完成：2026-09-22 第 4 轮（D1–D5 授权项执行结果）
- **卷4** `05-feature-status.part4.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷5** `05-feature-status.part5.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷6** `05-feature-status.part6.md` — 已完成：2026-09-22 第 10 轮（Step 0 首次实跑 + 记忆层回写 + 阶段1 补齐 + B1–B7 授权执行）
- **卷7** `05-feature-status.part7.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷8** `05-feature-status.part8.md` — 已完成：2026-09-23 第 13 轮（性能瓶颈三维实测分析）
- **卷9** `05-feature-status.part9.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷10** `05-feature-status.part10.md` — 05-feature-status 分卷（R199 自动拆卷）


---

# 06 - 已知约束

## 已知 Bug
- [BUG→**部分解决**] `.rule_backup/` 全库备份集中落在 `D:\global_skills\A-memory-start\references\.rule_backup\`（内含 `A-project-handoff.*.bak`）— 影响范围：备份与目标 skill 分离，回滚定位成本高；且 32 个 `.bak` 全部未跟踪，污染 `git status` | 状态：**部分解决**（2026-09-22 第 10 轮复测：文件数 **51**；「未跟踪污染」已解决 —— 该目录随 D7 `172eb88` 被仓库跟踪，`git -C D:\global_skills status --porcelain` 实测**零条**；按「文件×日」分组实测**无一组 >5** ⇒ R198.7 不触发；**仅剩「集中落点」未改** ⇒ 见第 10 轮建议 #4）—— **✅ 校正注（2026-09-23 销账）：已闭环** —— B4 已执行（`rule_editor.py` 备份落点迁出受管根至 `global_memory_archive\_trash\rule_backup`，56 份 .bak 全迁，`undo` 双落点兼容）；本轮实测 `A-memory-start/references/.rule_backup` 下 `.bak` = **0**

- [BUG] **`handoff.py review`/`status` 判据盲区：只判「文件是否被填充」，不做「主卷声明 vs 分卷已完成项」交叉校验** — 影响范围：**健康度评分对失效声明完全免疫**（R220 假通过族新形态）。2026-09-22 第 10 轮实测：`status` 报 **8/8 filled**、`review` 报 **9/9（100%）** 的**同时**，`06-constraints.md` 主卷仍有 3 条已修缺陷写成「未修复」、6 条已闭环技术债仍列，`05-feature-status.part1.md` 仍列 2 项已完成的 🚧 与 1 项已裁定的 ⛔ | 状态：**未修复**（2026-09-22 实测；修法涉受管根 review 判据，属破坏性改动 → 见第 10 轮建议 #11 / 待确认按钮）—— **✅ 校正注（2026-09-23 销账）：已修复** —— 上游由并行会话自行落地（受管根 `b7ba255`，R272 / v3.46.0：`savepoint.py` 新增 `_memory_volume_drift()`、`cmd_review` 接线）；本轮实测 `grep -c _memory_volume_drift savepoint.py` = 2、SKILL.md `version: 3.46.2`；我方独立复验层 a 6/6 + 层 b′ 2/2 + 层 b 3 项目零误报（见 `07-next-steps.part4.md` B8）

- [BUG] **跨会话夹带：`rule_editor.py commit` 按「整文件」提交，工作区存在他人同文件在途改动时会一并入库** — 影响范围：**白名单隔离纪律被静默击穿**（他人在途改动被记入我的提交，其工作区随之变「干净」，双方都误判为「已收口」）。2026-09-23 第 13 轮 r5 实测：我方改 `A-project-handoff/scripts/handoff_lib/splitvol.py` 时，并行会话正把 `"09-workflow-state.md"` 加入 `SPLIT_TARGETS`（其 `handoff.py` / `handoff_lib/audit.py` / `handoff_lib/common.py` / `handoff_lib/flow.py` / `scripts/templates/09-workflow-state.md.tmpl` 仍未提交）⇒ 我方提交 `f6f5b0c` 把该 1 行一并带入。**非数据丢失、未改写其内容**（重编号补丁窗口 0 命中该行，原文入库） | 状态：**未修复**（工具行为层；处置建议 = 提交前逐文件比对 `git -C <root> status --porcelain`，只对「确属本次改动」的文件走 `commit`；或上游在 `commit` 增加「同文件他人改动」预检）—— 本轮处置：**不回滚**（回滚 = 抹掉他人在途工作），只登记 + 知会

## 技术债
- [DEBT] **三仓均无 `pre-commit` hook**（2026-09-22 实测：`D:\global_skills` / 焚诀 / `D:\global_memory` 的 `.git/hooks` 仅 `post-commit`，其余全是 `*.sample`）—— 故「mirror / noise / evolution 已挂 `hooks/pre-commit`」（`04-plan/工作流专项建议.md` §4）属**设计意图而非既成事实**；影响：所有「hook 拦截后自动重试」的链路都是死代码（R270 已把 `--fix-mirror` 改为主动前置规避） | 处置：用户 2026-09-22 裁定**暂不补装**（改动面最小，改为「提交后按需跑 `gates`」）；如需恢复提交时拦截，须重新评估 fail-closed 对所有会话的影响
- [DEBT→**已闭环**] **受管根 39 条残留脏项未闭环**（2026-09-22 实测）：` D` **6**（5 个 `.rule_backup/*.bak` 已按 D3 迁 `global_memory_archive\_trash\backup-rotation\...`、`_bm_skillid_migration.json` 已按 #17 迁 `global_skills\_trash\`）+ `??` **33**（`.rule_backup/*.bak`，该仓库本就跟踪此目录）—— **非数据丢失、非本轮引入**（迁移目标磁盘可查） | 处置：需一次「提交迁移删除 + 跟进备份」的 git 提交（破坏性）→ 待确认 D7 | 状态：**已闭环**（D7 已执行，受管根 `172eb88`；2026-09-22 第 10 轮复测 `git -C D:\global_skills status --porcelain` **零条**）

## 红线（不能改）
- 阶段 0-3 **只读取证**：不改 `D:\global_skills` 下任何 skill 源文件，只在本工作区写报告（`memory/AGENTS.md` 铁律）
- 阶段 4 起改 skill 文件，**唯一途径 = `rule_editor.py`**；禁 `write_file` 整体重写
- 历史留痕不可改写（R241）：历史报告/日志里的旧数字、旧结论**不得直接改成当前值**，只能加「校正注」
- 受管根（`D:\global_skills` / `D:\global_memory` / `D:\global_memory_archive` / 焚诀）内散落项**只迁 `_trash`，禁止删除**
- 改 `D:\global_skills` 后必须复跑三门禁（mirror / noise / evolution）

## 性能/兼容性约束
- 平台：Windows + PowerShell；Python 用 `C:\Program Files\Python312\python.exe` 或 managed venv
- 跑任何 py 前须设 `PYTHONPYCACHEPREFIX`（防 `__pycache__` 重建在受管根内）
- PowerShell 下 `rg` / `grep` 均不可用 → 降级 `Get-ChildItem | Select-String`（禁静默当 0 命中）
- 记忆单文件硬上限 4KB（`07`/`05` 为 SPLIT_TARGETS，超限由 `split`/`trim-shell` 处理）

## 环境隔离（R196，init 必填）
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
- 测试专用文件清单：无（本项目不产出评测集）
- 红线：训练/生产数据禁止写入测试专用文件；新增评测数据先登记来源（provenance）
- 相关但非本项目资产：焚诀 `eval/` 下的 BGE 索引与 `verify_truth_consistency.py` 属**外部依赖**，只读调用不改

## 分卷目录
- **卷1** `06-constraints.part1.md` — 已完成条目归档（R224 主壳自愈）
- **卷2** `06-constraints.part2.md` — 06-constraints 分卷（R199 自动拆卷）
- **卷3** `06-constraints.part3.md` — 06-constraints 分卷（R199 自动拆卷）


---

# 07 - 下一步

## 最近对话摘要

- **2026-09-23（第 13 轮 r1–r6）** — 性能瓶颈三维实测分析 → P0-1/P0-2 落地（A-memory-start -64% / contract -58%） → 上游 trim-shell 双重盲区修复（V3.47.0）→ **06 纳入口径 V3.48.0**（注入壳 -6,435B/轮） → **noise_lint 假阳性根因修**（`d88b5ee`，savepoint 由被拒→安全落盘）。**逐轮全量记录（原样，零改写）见 `07-next-steps.part7.md`**

## P0 — 必须做

- [ ] **【待观察·他人在途】** 受管根未提交改动（2026-09-23 01:35 实测 `git -C D:\global_skills status --porcelain` = 6 条）：`gstack` / `local-computer-use` / `local-realtime-translator` / `local-screenshot-qa` / `chaoshi-image-optimization` / `chaoshi-web-deploy` 各自 `SKILL.md` 为 `M` —— 按 R269 与 P-1 铁律**只登记不擅动**，待对应会话自行收口。**历史复核（第 12 轮 / r4 原文）见 `07-next-steps.part7.md`**。**第 13 轮 r5 复核（2026-09-23 06:10）**：实测 **10 条**（`M` 8：`gstack` / `local-computer-use` / `local-realtime-translator` / `local-screenshot-qa` / `chaoshi-image-optimization` 各自 `SKILL.md` **+ A-project-handoff 在途功能 3 文件** `scripts/handoff.py` / `handoff_lib/audit.py` / `handoff_lib/common.py`；`??` 2：`handoff_lib/flow.py` / `scripts/templates/09-workflow-state.md.tmpl`）—— 新增 5 条源自并行会话的「动态工作流状态（09 节）」功能，按 R269 **只登记不擅动**（本轮对该 skill 的改动已用 `rule_editor` 单文件收口，见下条 r5 事故登记）
- [ ] **【待观察·焚诀在途债】** `gate_stub_runner` 实测 `[GATE:stub-fail]`（2026-09-23 01:35）：① 桩 `stub_c16_memory` 2/3——正例样本硬编码总分 `181.6` vs 活体评分卡 `183.9`（判据样本与活体口径漂移，R263 补注①形态，须由移动总分的会话裁决）；② 未登记桩判据 C17/C18/C19（registry 冻结于 09-22 后新增）。均非本轮引入（本轮仅改 A-project-handoff 文案，焚诀 eval 零触碰），按 R269 登记待其归属会话收口。**历史复核（第 12 轮 / r4 原文）见 `07-next-steps.part7.md`**
- [ ] **【待观察·新节缺失】** `09-workflow-state.md`：并行会话在途功能（`handoff_lib/common.py` 已把该文件列为第 9 个记忆节 + `templates/09-workflow-state.md.tmpl` 模板已落盘但**未提交**）⇒ 本项目 `status` 现报 **8/9**（该节 `❌ missing`）。按 R269 **不擅动**（模板/口径仍在途，避免与归属会话冲突）；待其提交收口后按官方模板补建该节并复跑 status/review
- [ ] **【待观察·跨会话夹带】** 受管根 `f6f5b0c`（本轮 V3.48.0 提交）**夹带**了并行会话在 `handoff_lib/splitvol.py` 的在途改动 1 行（`SPLIT_TARGETS` 增 `"09-workflow-state.md"`）—— 根因：`rule_editor.py commit` 按**整文件**提交，而同文件存在他人未提交改动；**非数据丢失、未改写其内容**（重编号补丁窗口 0 命中该行，内容原样入库），但归属与「已收口」判断失真。处置：**不回滚**（回滚=抹掉他人在途工作），只登记 + 提交前逐文件比对 `git status --porcelain`；已按 R241 在 `06-constraints.md` 留痕
- [ ] **【待办·文档同步】** noise_lint 修补（受管根 `d88b5ee`，2026-09-23 r6）的**三处文档同步待补**：`SKILL.md` 版本行、`references/version-history.md` 条目、`commands.md §11` 豁免口径说明 —— 暂缓原因 = 并行会话已把 `version: 3.49.0` 与这三个文件纳入在途改动（其 `handoff_v3.50` 系功能），此刻补写必然二次夹带他人改动。**处置**：待其提交收口后，按 3.49.0 → 下一版补登记（若其条目已含本修补则只需核对）；登记证据 = 本轮 commit `d88b5ee` 的提交信息已完整记述修补内容与验证
- [ ] **【P1 待授权·可选】** 性能方案剩余项（2026-09-23，详见 `05-exec/性能瓶颈分析与优化方案.md`）：P1-3a 本项目注入壳瘦身——**✅ 校正注（2026-09-23 r3 裁定：本轮不做，销账）**：实测 06 主文件 12,148B 无上游分卷/自愈机制（SPLIT_TARGETS 只注册 07/05，trim-shell 判据只认「✅/已完成」章节而 06 是 [BUG]/[DEBT] 留痕形态），收敛须逐条改写原文——违 R241「只加注不改写」精神且无机器护栏，**不擅建结构**；如要做须上游先裁 06 分卷口径（登记为上游建议，非本项目待办）。**✅ 校正注（2026-09-23 r5 销账）**：用户授权后上游口径已落地（A-project-handoff **V3.48.0**：`TRIM_ENTRY_TARGETS` 与 `SPLIT_TARGETS` 解耦 + `closed_marker` 判据 + 留痕章节白名单 + 分区不变式），本项目 06 实测 **13,075B → 7,097B**（迁出 13 条 → part1/part2），注入壳 06 节 **12,148B → 6,182B**、整壳 **33,029B → 26,594B（-6,435B/轮）**。P1-4 unified_router direct_hit 短路（上游焚诀，每轮省 ~1.1s；**项目红线明文「焚诀 eval/ 只读调用不改」**，转焚诀归属会话）；P2 三项观察不动
## 分卷目录
- **卷1** `07-next-steps.part1.md` — 历史待办与已完成条目（2026-09-22 已按实测销账）
- **卷2** `07-next-steps.part2.md` — 已完成：批2 剩余 P0 与 q-2/q-3 收口
- **卷3** `07-next-steps.part3.md` — 最近对话摘要（历史）
- **卷4** `07-next-steps.part4.md` — 07-next-steps 分卷（R199 自动拆卷）
- **卷5** `07-next-steps.part5.md` — 07-next-steps 分卷（R199 自动拆卷）
- **卷6** `07-next-steps.part6.md` — 最近对话摘要（历史轮次，2026-09-23 第 13 轮 r3 迁入，正文零改写）
- **卷7** `07-next-steps.part7.md` — 最近对话摘要（第 13 轮 r1–r6 全量记录，2026-09-23 原样迁入）
- **卷8** `07-next-steps.part8.md` — 07-next-steps 分卷（R199 自动拆卷）


---

# 08 - AC-OBS 验收标准

## 验收标准列表

- AC-OBS-01: 用户登录功能 → 输入正确账密点击登录，跳转到首页 | 截图 + URL变化
- AC-OBS-02: API返回数据正确 → GET /api/users 返回200 + JSON数组 | API响应
- AC-OBS-03: 页面响应速度 → Lighthouse评分 > 90 | 测试输出
-->

- [ ] AC-OBS-01: 阶段0 自建清单裁定可复跑 → 跑 `01-scan/scan_all.py --stage scope` 退出码 0 且 `00-scope/` 下 3 个产物齐备（清单 / 失真条目 / scope_result.json） | 测试输出
- [ ] AC-OBS-02: 阶段1 四维扫描可复跑 → 跑 `01-scan/scan_all.py --stage scan` 退出码 0 且 `01-scan/scan_result.json` 可被 JSON 解析 | 测试输出
- [x] AC-OBS-03: 注册表与磁盘集合一致 → 焚诀 `verify_truth_consistency.py` 打印 `✅ C1 … 注册表 == 磁盘`（2026-09-22 实测 120 skills） | 测试输出
- [x] AC-OBS-04: 三门禁全绿 → `rule_editor.py gates` 退出码 0 且打印 `mirror=pass noise=pass evolution=pass`（2026-09-22 实测） | 测试输出
- [x] AC-OBS-05: 记忆可交接 → `handoff.py savepoint <项目>` 退出码 0（07 P0 非空 + P-1 绑定表存在 + 门禁 PASS）—— 2026-09-22 实测 **exit 0「本次对话已安全落盘」**；P0 未完成 8 项、`coldstart --check` 6 行全等、`noise` = `[GATE:noise-pass]` | 测试输出
- [ ] AC-OBS-06: 记忆完整性达标 → `handoff.py review <项目>` 输出 `Score: 9/9` 且 warnings = 0 —— 2026-09-22 实测 **7/9（78%）**，剩 2 条均为上游判据缺陷（假阴性 + 注释未剔） | 测试输出
- [ ] AC-OBS-07: 改动可回滚且已离机 → `git log --oneline` 每个主题 ≥1 提交，且 `git rev-parse HEAD` == `git ls-remote origin main` 的 SHA（致命纪律 #20）—— 待 D4 授权 | 测试输出
- [ ] AC-OBS-08: 交付物入口可达 → 从 `README.md` 的「六阶段产物地图」出发，每行列出的路径 `Test-Path` 全为 `True` | 测试输出

     `handoff.py review` 会把它计入（`savepoint.py:632` 全文匹配不剔注释）→ 实测输出
     「8 个 AC-OBS，但只有 11 个格式正确」（11 > 8 自相矛盾），该子命令的 AC 计数不可信。
     处置遵循 R263：**不改数据去凑判据**，缺陷本身登记为 `06-constraints.md` 的 [BUG]，修复待确认 D1。 -->

