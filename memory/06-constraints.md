# 06 - 已知约束

> 本文件记录已知问题、技术债和约束。
> 归档类型：增量（已解决的问题移入归档）
> 注（2026-09-22）：本文件**不是** `SPLIT_TARGETS` 注册目标（本项目默认仅 `07-next-steps` + `05-feature-status` 参与 4KB 语义，见 R199/R226），故体量可超 4KB；确需纳入时用 `handoff.py split "<项目>" --target 06-constraints.md`。

## 已知 Bug
<!-- 格式：- [BUG] 描述 — 影响范围 | 状态：未修复/修复中 -->
- [BUG] `handoff.py review` 判 `08-ac-obs.md: 3 个验收标准，格式正确`，实际这 3 条全在 `<!-- 示例： ... -->` 注释内 — 影响范围：**假通过**，交付就绪度被高估；根因 `handoff_lib/savepoint.py:632` 用 `re.findall(r"AC-OBS-\d+", content)` 全文匹配、不剔注释 | 状态：**未修复**（2026-09-22 实测，属破坏性改动，待确认 D1）
- [BUG] `handoff.py review` 判 `05-feature-status.md: 没有记录任何功能状态`，实际该文件有 10 条已完成条目 — 影响范围：**假阴性**，误导为「记忆未填」；根因同文件 `:594` 正则 `^-\s*(\[x\]|\[ \]|[✅🚧📋])` 只认 `- ✅` 形态，不认「`## ✅ 已完成` + 普通 `- 描述`」写法 | 状态：**未修复**（2026-09-22 实测，待确认 D1）
- [BUG] `handoff.py status` 判 `02-structure.md ✅ filled (auto-synced)`，同日 `review` 判 `尚未运行 sync，目录树为空` — 影响范围：同一文件两子命令结论相反，门禁口径自相矛盾（`status` 只数非空行） | 状态：**未修复**（2026-09-22 实测，待确认 D1）
- [BUG] `.rule_backup/` 全库备份集中落在 `D:\global_skills\A-memory-start\references\.rule_backup\`（内含 `A-project-handoff.*.bak`）— 影响范围：备份与目标 skill 分离，回滚定位成本高；且 32 个 `.bak` 全部未跟踪，污染 `git status` | 状态：**未修复**（2026-09-22 实测，待确认 D3）

- [BUG→已解除] `handoff.py savepoint` 于 2026-09-22 01:17 **曾被拒**：`[GATE:noise-fail]` VIOL `焚诀\.codebuddy\` —— 该目录是**运行中 IDE 的会话数据**（当日日志 mtime 分钟级），**不是 agent 交付物**。⚠️ 关键教训：**#17 字面处置「迁 `_trash`」在此是错的**（会破坏活动工具状态）；正确出口 = `noise_lint` 既有机制「被 `.gitignore` 命中 → 降级 `quarantine`」 — 状态：**已解除**（并行会话 2026-09-22 01:20:13 补 `焚诀\.gitignore:9` 的 `.codebuddy/`，commit `1f354e9`）→ `noise` 复跑 `[GATE:noise-pass]`（四根 violation=0），本项目 `savepoint` 复跑 **exit 0「本次对话已安全落盘」**
  - 归属说明（⚠️不能确证）：本会话确实执行过 `Set-Location …\焚诀`（cwd 曾为焚诀），故**可能是写入方之一**；但该目录性质为「活跃 IDE 会话数据」，同一时段另有并行会话在焚诀作业，无法单方归因。教训已吸收：跨受管根跑脚本改用 `Push-Location` + `Pop-Location`（本会话后段已改）

## 技术债
<!-- 格式：- [DEBT] 描述 — 建议的还债方式 -->
- [DEBT] 记忆层与实况脱节（`01-goal` 六阶段目标 0 勾选 / `03`+`04` 空模板 / `06` 四节全空 / `08` 零条真实 AC）— 还债方式：本轮已回填（2026-09-22，见 `05-exec/第3轮执行报告.md`）
- [DEBT] 三重同义状态源（`TODO.md` / `memory/07-next-steps.md` / `memory/05-feature-status.md`）已实测漂移 — 还债方式：定 `memory/07` 为 P0 唯一真相源，`TODO.md` 降级为「阶段状态总表（索引）」（2026-09-22 已改）
- [DEBT] 工作区 git 仅 1 次提交（`49ff0d6` baseline）→ 无回滚粒度 — 还债方式：按主题逐步 commit（本轮改动待确认 D4）
- [DEBT] `archive/` 为空目录 —— 归档机制从未执行（违反 handoff 致命纪律 #4「archive = 安全网」）— 还债方式：阶段切换前先 `handoff.py archive`
- [DEBT] `01-scan/overlap_raw.txt`（282,977B）为阶段1 原始中间产物，滞留交付目录 — 还债方式：迁 `archive/`（待确认 D3）
- [DEBT] `05-exec/` 19 个 patch JSON 无索引 — 还债方式：本轮已补 `05-exec/README.md`（2026-09-22）
- [DEBT] skill 数口径四数不一（记忆 169 / verify C1 实测 120 / 顶层目录 152 / 全盘 SKILL.md 205）→ 现行 P0 基数不可用 — 还债方式：先裁定口径再复核注册表（待确认 D2）

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

## 评测集隔离（R196）
<!-- 标注测试专用文件，禁止把训练数据写入测试集；新增评测数据先登记 provenance -->
- 测试专用文件清单：无（本项目不产出评测集）
- 红线：训练/生产数据禁止写入测试专用文件；新增评测数据先登记来源（provenance）
- 相关但非本项目资产：焚诀 `eval/` 下的 BGE 索引与 `verify_truth_consistency.py` 属**外部依赖**，只读调用不改
