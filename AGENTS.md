# AGENTS.md — 自建skill优化（索引壳，R161 拆卷）

> **本节只放路由与红线；正文权威源在 `memory/`，本壳不含第二真相源。**
> 降级史与迁移前快照取值：`git log --oneline -- AGENTS.md`（r109 I-7 起；本件已跟踪，git 可回滚）。
> 分卷份数一律现读：`Get-ChildItem memory -Filter 07-next-steps.part*.md | Measure-Object`（旧注手抄的 part 号实测已漂）。
> 旧注所引备份路径 `05-exec/mark_backup/AGENTS.md.r109_before_index_shell` 经 r216 实测**已不存在**（死指针已删）。

## 启动顺序（每次进来先做）

1. **`memory/07-next-steps.md`** = 跨会话唯一入口、P0 唯一真相源（handoff 致命纪律 #1）。超限部分在 `07-next-steps.partN.md`。
2. 需要状态 → `memory/05-feature-status.md`（含 partN）；需要约束/红线全文 → `memory/06-constraints.md`（含 partN）。
3. 需要目录结构 → `memory/02-structure.md`（`sync` 自动刷新，**本壳不再复制树**，防陈旧副本）。
4. 复杂任务先 `A-memory-start` → 按 `memory/AGENTS.md` P-1 绑定表加载技能，禁裸跑。
5. `TODO.md` / `README.md` 是**索引**，不是入口。

## 分卷目录

| 节 | 权威文件 | 说明 |
|---|---|---|
| 01 目标 | `memory/01-goal.md` | 六阶段目标 + 范围裁定口径 |
| 02 结构 | `memory/02-structure.md` | 目录树（sync 自动更新）+ 模块说明 |
| 03 技术栈 | `memory/03-tech-stack.md` | 运行环境 + 外部依赖 |
| 04 文件地图 | `memory/04-file-map.md` | 核心逻辑文件/配置表 |
| 05 功能状态 | `memory/05-feature-status.md`（+ partN） | 已完成/进行中/阻塞 |
| 06 已知约束 | `memory/06-constraints.md`（+ partN；part6–16 = #30–#48 纪律正文） | 已知 Bug / 技术债 / 红线全文 |
| 07 下一步 | `memory/07-next-steps.md`（+ partN） | **P0 真相源** |
| 08 验收 | `memory/08-ac-obs.md` | AC-OBS 列表 |
| 09 工作流态 | `memory/09-workflow-state.md` | 批次与在途 |
| — | `memory/AGENTS.md` | P-1 项目级 Skill 绑定表（命中即加载） |
| — | `05-exec/README.md` | 执行证据索引（补丁 ↔ P0 ↔ commit） |

## 一句话项目定位

对 `D:\global_skills` 自建技能体系做全量体检与优化，产出「审计 + 逐项实施计划 + 执行证据」，六阶段推进；
**对标轮次报告**逐轮落 `06-benchmark/全量对标报告_rNN_*.md`。当前最新轮次取值：`Get-ChildItem 06-benchmark -Filter '全量对标报告_r*' | Sort-Object Name | Select-Object -Last 1 -ExpandProperty Name`（禁硬编码轮号，r110 立规——旧值 r108 系 2026-10-16 当时态）。

## 口径裁定（用户确认，禁换分母）

- 自建口径 = **HIGH 51 + MID 26 = 77 条**（阶段0 v2）；注册表基数按磁盘实测现值复算（`disk_registry_diff.py`，r108 实测 182⇄182 三类全 0）。
- LOW 灰区 30 条 = 排除维护范围（已在册仍参与路由）；EXCLUDE 43 条 = 市场/上游件。
- **已作废基数**「自建 ≈90 / 基数 169」禁止再引用。权威清单 = `00-scope/自建skill清单.md`。

## 红线（不能改 · 摘要；全文见 `06-constraints.md`）

1. 阶段 0-3 **只读取证**：不改 `D:\global_skills` 任何源文件，只在本工作区写报告。
2. 阶段 4 起改 skill 文件**唯一途径 = `rule_editor.py`**；禁 write 整体重写；镜像 `_my-skills`/`.agents\skills` **只读**。
3. **历史留痕不可改写（R241）**：旧报告旧数字只能加「校正注」，禁直接改成当前值。
4. 受管根散落项**只迁 `_trash`，禁止删除**；禁用 `_bak` 作落点。
5. 改 `D:\global_skills` 后必跑三门禁（mirror / noise / evolution）+ `disk_registry_diff` 三类全 0。
6. **焚诀 `eval/` 只读调用不改**；派生件（registry/skill_content/BGE）禁手改。
7. 破坏性动作双硬前提（备份已落 `_trash` + Git 可回滚）满足才可自动批准并留痕，缺任一回落待确认。

## 门禁与取值命令

正本 = `memory/AGENTS.md`「项目门禁命令」节（A-memory-start R193 读的就是那一行）+ `05-exec/README.md`。
本壳**不复制命令清单**：复制即第二真相源（违本壳自身声明），且旧注手抄的「29 门」实测已漂到 93 门。
门数现读：`python -c` 读 run_gates.GATES 长度；注入面现读：`python 05-exec/ratchet_gate.py`。
Python 首选 managed venv `%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe`
（系统 Python 会假红：numpy/jinja2/networkx 缺）；跑任何 py 前设 `PYTHONPYCACHEPREFIX`。

## 纪律条目正文（#30..#48）

正本 = `memory/06-constraints.part6.md`..`.part16.md`（r154 归档，原文零改写）。
⛔ 新增纪律条目**先落 memory 分卷**，壳内只加指针。

## 已知坑（本壳级必读三条；其余见 `06-constraints.md`）

- 聚合 runner 的 stdout **禁落项目根**（noise 顶层 VIOL）**也禁落 tracked 件**（Out-File 截零 → `tracked_empty_check` 判红）；正解 = gitignore 命中的 `_temp/` 或只留 `--json` 快照。
- **写记忆卷之后必须重算账龄件**：顺序 = 先改 07 台账 → 后跑 `r38_debt_aging.py`；已连踩 3 轮（r119/r121/r122），症状与补救全文正本 = `memory/07-next-steps.part84.md`（R122-1 已机械化）。
- 受管根提交落地 ≠ 交付：必复算 `git merge-base --is-ancestor <sha> HEAD`（并行 rebase 会把你的提交甩出主线，一手 `b9e5d90e`）。

