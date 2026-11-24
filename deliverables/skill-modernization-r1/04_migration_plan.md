# 04 · 分阶段迁移替换方案（需求4）

> 任务 t4 / member `migration-architect` / attempt `205bb8df-7d74-4324-9d5b-2168e60bb84d`。

> **写面白名单**：`自建skill优化/deliverables/skill-modernization-r1/04_migration_plan.md`、`04_migration_batches.json`、`04_plan_check.py` 三件，均 `04_*` 编号，与 01/02/03/05 他人写面不相交；另只读复用 captain 所有件 `04_protected_guard.py`（本轮不改写、只引用其输出）。

> **纪律**：阶段 0-3 只读取证，本轮未改 `D:/global_skills` 下任何 `SKILL.md`/源文件；镜像 `_my-skills` 与 `.agents/skills` 只读；`eval/` 焚诀只读件未改；R241 历史数字只加校正注、不改写；每个数字附取值命令/句柄；结论逐条标 ✅已实测 / ⚠️部分实测 / ❌未实测；禁假完成（#36）；禁「请老大手动」（#29/#48）。

> **性质**：本文件是「分阶段执行计划」。**真实全量替换列入 §3 阶段门时间节点，本轮不执行任何替换**；改受管源须走 `rule_editor.py` + 双硬前提。

> **自证入口**：`python -B 自建skill优化/deliverables/skill-modernization-r1/04_plan_check.py` → 末行 `[PLAN:CHECK] PASS`；批次负控 `... --negative-control` → `[NEGCTRL:RED]`；保护件注入负控 `... --negative-control-protected` → `[NEGCTRL:RED]`（验真正文一致性门，防半修正态假绿）。

---

## 0. Goal / Architecture / Tech Stack / Spec / Global Constraints

### 0.1 Goal

把 t1（150 件盘点）、t2（77 件 × 3-5 候选）、t3（473 对象 × 5 维矩阵）的证据，收敛成可执行的 P0/P1/P2 分批替换方案：每件 skill 有优先级、阶段门时间节点、可复跑验证标准、可解析回滚预案；11 件语义缺口单列「自建升级/保持」。

### 0.2 Architecture（两仓 + 四层）

| 层 | 实体 | 现场定位 | 取值命令 |
|---|---|---|---|
| 归档审计仓 | `自建skill优化`（git 仓根） | `git -C 自建skill优化 rev-parse --show-toplevel` = `D:/app-cache/skill-fenjue/自建skill优化`；`describe --tags` = `r344`；HEAD = `617c8cf` | `git -C 自建skill优化 describe --tags; git -C 自建skill优化 rev-parse --short HEAD` |

| 受管源仓 | `D:/global_skills`（**独立** git 仓） | HEAD = `afec0a7e`；现有 tag 仅 `backup/pre-cleanup-20261016`，且 `git describe --tags` 报 `fatal: No tags can describe` | `git -C D:/global_skills rev-parse --short HEAD; git -C D:/global_skills tag -l` |

| 数据面 | t1 `data/inventory.json`(150) / t2 `data/candidates.json`(77, 377 cand) / t3 `data/matrix.csv`(2365 行) | 同目录 | `python -B deliverables/skill-modernization-r1/04_plan_check.py --stats` |

| 判据面 | `04_plan_check.py` | 同目录 | `python -B deliverables/skill-modernization-r1/04_plan_check.py` |

⚠️**关键**：`D:/app-cache/skill-fenjue` 与 `D:/app-cache` **不是** git 仓（`fatal: not a git repository (or any of the parent directories): .git`）。归档仓 rNN tag 与受管源仓是**两个仓**，回滚命令必须显式 `git -C <repo>`，禁止混用一个 `git describe`。

### 0.3 Tech Stack

- Windows + PowerShell（`自建skill优化/memory/06-constraints.md:107`）；Python = managed venv `%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe`（现场 `Test-Path=True`）；`C:\Program Files\Python312\python.exe` 现场 `Test-Path=False`。跑任何 py 前须 `$env:PYTHONPYCACHEPREFIX="_temp/pycache"`（`06-constraints.md:108`）。

- 改 skill **唯一途径** = `D:/global_skills/A-memory-start/references/rule_editor.py`（`06-constraints.md:100`、`memory/AGENTS.md:72`）。CLI 子命令（现场现读 `rule_editor.py:1672-1741`）：`show | append | insert | replace | undo | commit | gates`；`replace` 支持 `--old/--new/--old-file/--new-file/--patch/--dry-run`；`commit` 支持可重复 `--file` + `--desc`；`gates` 支持 `--json/--verify-log/--gate`。**禁 `write_file` 整体重写**。

- 门禁 = `python 05-exec/run_gates.py`（`05-exec/run_gates.py:20-29` 三态 PASS/FAIL/UNVERIFIED，任一 FAIL 或 UNVERIFIED ⇒ exit 1）。门数现读 `python -c "import run_gates; print(len(run_gates.GATES))"`，禁手抄。

- GitHub 取证受阻退路 = `python 05-exec/r114_replacement_scan.py --offline --json _temp/t4_repl_offline.json`（t5 §1.3 实跑 `[REPL:PASS] 逐件候选面守恒 191==191`）；限流时具名登记盲区，禁静默丢弃。

### 0.4 Spec（计划产物契约）

| 编号 | 产物 | 内容 |
|---|---|---|
| S1 | `04_migration_plan.md` | P0/P1/P2 分批 + 阶段门时间节点 + 逐批验证标准 + 逐批回滚命令 + 试点范围 + 150 行全量 disposition |

| S2 | `04_migration_batches.json` | 机器可读分批、锚点、算法、11 缺口 / 9 HOLD（含 1 件 protected_hold） / LOW / EXCLUDE 名单 |

| S3 | `04_plan_check.py` | 每条回滚命令语法 + 路径存在性静态校验（打印 条数/通过数）、四件套完整性、负控 |

### 0.5 Global Constraints（硬红线，逐条带证据路径与复算命令）

| 约束 | 证据路径 | 现场复算命令 |
|---|---|---|
| 阶段 0-3 只读取证 | `自建skill优化/memory/06-constraints.md:99` | `git -C D:/global_skills status --porcelain` |

| 阶段 4 改 skill 唯一途径 `rule_editor.py` | `06-constraints.md:100`；`memory/AGENTS.md:72` | `Test-Path "D:/global_skills/A-memory-start/references/rule_editor.py"` |

| 破坏性动作双硬前提（备份落 `_trash` + Git 可回滚） | `自建skill优化/AGENTS.md:51`；`A-skill-manager/references/intent-crud.md:3-5,31-41` | `Test-Path "D:/global_skills/_trash"` + `git -C D:/global_skills tag -l` |

| R241 历史不改写 / X-9 禁删 tracked 凑绿 | `06-constraints.md:101`；`memory/AGENTS.md:113` | `git -C 自建skill优化 status --porcelain -- 06-benchmark/` |

| 改受管根后必跑三门禁 + 派生件重建 | `06-constraints.md:103`；`AGENTS.md:59`；`memory/AGENTS.md:72` | `python "D:/global_skills/A-memory-start/references/rule_editor.py" gates` |

| annotated tag `rNN` 版本锚 | `memory/AGENTS.md:55` | `git -C 自建skill优化 tag -l` |

| 区间回滚 `git revert rNN..HEAD` | `memory/AGENTS.md:58` | `git -C 自建skill优化 describe --tags` |

| X-2 禁补 LICENSE / 开 release（私有归档仓，无发布流水线） | `memory/AGENTS.md:63` | `Test-Path "自建skill优化/LICENSE"` |

| X-29 补件先答「谁引用它」；明显更好需 可运行+可移植+有交集 三者齐备 | `memory/AGENTS.md:114` | §2.5 / §2.6 逐件登记 |

| 共享仓提交点名路径，禁裸 `git commit` | `D:/global_skills/A-project-handoff/SKILL.md:107` | `git -C D:/global_skills status --porcelain` |

| 门禁如实记 verdict，禁为凑绿删件 | brief；`05-exec/run_gates.py:20-29` | §10 |

| 质量口径唯一 = r115 第⑨段 | `05-exec/r115_quality_truth.py:2,26,43` | `python 05-exec/r115_quality_truth.py` |

---

## 1. 口径与 T 使用边界（captain m00020 硬纠偏）

### 1.1 禁止直接按 T 排序优先级

captain（m00020）独立复算 t3 后判定：`T` 差值**不能**当替代收益；本计划 §2 的优先级完全由「结构可比面」生成，`T` 只作旁证。`03_evaluation_matrix.md:581` 原文亦写明「数值只说明作为可替换资产包的工程完成度分布，**不是业务功能强弱结论**，t4 迁移优先级不得只按 T 排序」。

> **[captain 修正 2026-11-07 07:55] 迁移前置检查（硬约束，机器闸）**
> 对每个待替换件，必须先查 `D:/global_skills/_my-skills/registry.json` 的 `protected_skills` 名单；命中即降级为 `protected_hold`，**禁替换**，仅允许经 `rule_editor.py` 自建增量升级。
> 保护名单取值命令（captain m00117 指定）：`python -c "import json,io;d=json.load(io.open(r'D:/global_skills/_my-skills/registry.json',encoding='utf-8'));print(sorted(d.get('protected_skills',{}).keys()))"` → ✅已实测 rc=0，期望输出 `['A-skill-manager']`。
> 机器闸可复跑：`python -B deliverables/skill-modernization-r1/04_protected_guard.py` → 期望 `[PROTGUARD:CLEAN] 替换批次内无注册表保护件`（负控 `--negative-control` 须 `[NEGCTRL:RED]`）。
> **本次命中并已修正**：`A-skill-manager`（registry.json:5-9，reason=「用户自建核心管理技能——所有技能增删改查唯一入口」；SKILL.md:10-12 自述 21 技能融合体）—— 已移出 P0 → `protected_hold`；P0 补位 `chaoshi-web-deploy`（idx=19，同公式复算）。
> 其余 4 件 P0（`prompt-consolidation` / `windows-bash-cli-interop-pitfalls` / `windows-cli-utf8-wrapper` / `windows-gitbash-chinese-path-pit`）与补位件 `chaoshi-web-deploy` 对照该名单 ✅已实测均不命中 protected_skills，允许进入替换批次。
> 修正后守恒：**77 = P0 5 + P1 24 + P2 28 + gaps 11 + holds 9**。

## 1.2 T 差 44.24 的「约 90% 结构性校正」（引用 T 差必须同屏给出本表）

| 维度 | 现有件均值 | 候选均值 | 差距×权重 | 占 T 差 | 可比性 |
|---|---:|---:|---:|---:|---|
| eff 运行效率 | 0.09 | 3.56 | 13.87 | 31.3% | ❌ 结构性不可比 |

| docs 文档完善 | 1.03 | 4.08 | 9.15 | 20.7% | ❌ 结构性不可比 |

| fc 功能完整性 | 1.96 | 3.38 | 8.52 | 19.3% | ❌ 结构件不可比 |

| community 社区 | 0.97 | 3.73 | 8.26 | 18.7% | ❌ 结构性不可比 |

| compat 兼容性 | 3.43 | 4.54 | 4.43 | 10.0% | ⚠️ 相对可比 |

**四项不可比合计 = 31.3+20.7+19.3+18.7 = 90.0%**；唯一相对可比的 `compat` 仅 10.0%。上表来源 = captain m00020 独立复算（⚠️部分实测：本轮沿用其维度分解，未重跑其逐仓取数脚本）；t3 `03_evaluation_matrix.md:594`(B1 bundle-scale)、`:599`(B6 community/stars 通道不可比) 为同向佐证（✅已实测，现读）。

**根因**：`05-exec/r114_replacement_scan.py:790-863` 的 `score5` 锚点按「GitHub 整仓」设计（README / docs / tests / workflows / stars），而现有件是「本地单件 skill 目录」，形态不同 ⇒ eff/docs/fc/community 被形态锁死，不是业务能力弱。

### 1.3 结构形态现场复扫（本轮独立复算，✅已实测）

取值命令（在 managed venv 或 Node 内读 `D:/global_skills` 一级目录）：
```powershell
Get-ChildItem -Directory "D:/global_skills" | Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") } | Measure-Object
Get-ChildItem -Directory "D:/global_skills" | Where-Object { Test-Path (Join-Path $_.FullName "README.md") } | Measure-Object
Get-ChildItem -Directory "D:/global_skills" | Where-Object { Test-Path (Join-Path $_.FullName "docs") } | Measure-Object
Get-ChildItem -Directory "D:/global_skills" | Where-Object { Test-Path (Join-Path $_.FullName "tests") } | Measure-Object
Get-ChildItem -Directory "D:/global_skills" | Where-Object { Test-Path (Join-Path $_.FullName ".github/workflows") } | Measure-Object
```
| 面 | 本轮现场值 | 比率 | captain m00020 现场值 | 分母差异登记 |
|---|---:|---:|---|---|
| 含 SKILL.md 的一级目录 | 190 | 100% | 146 现存目录 | ⚠️活跃根漂移：与 t1 `06-benchmark` 的 243→247 同族；按 R269 只登记、不擅动，不改历史判据 |

| 有根 README.md | 7 | 3.7% | 4/146 = 2.7% | 同上 |

| 有 docs/ | 3 | 1.6% | 2/146 = 1.4% | 同上 |

| 有 tests/ | 9 | 4.7% | 10/146 = 6.8% | 同上 |

| 有 .github/workflows | 1 | 0.5% | 1/146 = 0.7% | 同上 |

| 仅 1 个 SKILL.md | 190 | 100.0% | 144/146 | 同上 |

| SKILL.md 总数 | 190 | — | — | 本轮 `find` 等价计数 |

两个分母（190 vs 146）都指向同一结论：README/docs/tests/workflows 通道在现有件近乎全缺、`stars=0` 恒定，故 §1.2 的 90% 结构性校正成立。`community` 本地侧方差为 0（`03_evaluation_matrix.md:599`）。

### 1.4 T 的使用边界（写死）

1. `T` **只**度量「作为可替换资产包的工程完成度」，**不是**业务功能强弱，也不是替代收益。

2. 本计划任何位置引用 `T` 或 `T` 差（现有 mean=31.87 / 候选 mean=76.11 / 差 44.24，来源 `03_evaluation_matrix.md:574-581`），**必须同屏给出 §1.2 的「约 90% 来自结构性形态差异」校正**。

3. 排序键只用 `compat`（唯一相对可比维）+ `known_defects` + `rel=skill 已确认候选数` + 缺失能力面；`fc/eff/docs/community` 与 `T` 均不进排序公式。

---

## 2. 结构可比优先级算法与 150 行全量 disposition

### 2.1 算法（复算命令）

```text
compat_gain      = max(compat of rel=="skill" candidates) - compat of current:<slug>   // 取自 data/matrix.csv
known_defects_n  = len(data/inventory.json.rows[i].known_defects)                     // 84/150 有记录，66 未记录≠零缺陷
rel_skill_n      = count(data/candidates.json.rows[i].candidates where rel=="skill") // 323 真替代 / 54 线索
missing          = semantic_gap OR rel_skill_n==0 OR compat_gain<=0 OR score not finite
priority_index   = 4*compat_gain + 2*known_defects_n + min(rel_skill_n,5) + (class=="HIGH"?2:0) - 99*missing
```
复算入口：`python -B 自建skill优化/deliverables/skill-modernization-r1/04_plan_check.py --stats`（打印 §2.2 全部计数与守恒）。`T` 不在公式内。

### 2.2 分母与守恒（✅已实测，取自 data/*.json / matrix.csv）

| 面 | 值 | 取值命令 |
|---|---:|---|
| HIGH / MID / LOW / EXCLUDE | 51 / 26 / 30 / 43 = 150 | `python -B deliverables/skill-modernization-r1/01_coverage_check.py` |

| 替换分母（HIGH+MID） | 77 | `memory/06-constraints.md:122`（只以此数为分母） |

| replaceable | 57 = P0 5 + P1 24 + P2 28 | `04_plan_check.py --stats` |

| 语义缺口（自建升级/保持） | 11 | `04_plan_check.py --stats` |

| HOLD（无 compat 正增益 / 含 1 件 protected_hold） | 9 | `04_plan_check.py --stats` |

| 守恒 | 57+11+9 = 77；LOW 30 + EXCLUDE 43 = 73；合计 150 | 同上 |

⚠️部分实测：`known_defects` 仅 84/150 有记录、66 件未记录**不等于零缺陷**；`usage_feedback` 99.94% `outcome_unknown`，故 `feedback_weight_cap=0`，反馈只作旁证、不进分子/分母（t3 §3）。

### 2.3 150 行全量 disposition 表（每件 skill 都有优先级/处置）

| # | slug | class | 批次/处置 | cur_compat | best_compat | gain | defects_n | rel_n | index | 首选候选 |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 9b-lightworkflow | HIGH | P2 | 3 | 5 | 2 | 0 | 3 | 13 | lennney/stop-that-shit |
| 2 | A-ask-questions | HIGH | SELF-UPGRADE（语义缺口） | 3 |  |  | 0 | 0 |  | — |
| 3 | A-get-memory | HIGH | P1 | 3 | 5 | 2 | 0 | 5 | 15 | affaan-m/ECC |
| 4 | A-java-problem | HIGH | HOLD（无正增益） | 3 |  |  | 0 | 5 |  | — |
| 5 | A-memory-start | HIGH | P1 | 3 | 5 | 2 | 1 | 5 | 17 | affaan-m/ECC |
| 6 | A-project-better | HIGH | P1 | 3 | 5 | 2 | 0 | 5 | 15 | affaan-m/ECC |
| 7 | A-project-handoff | HIGH | P1 | 3 | 5 | 2 | 0 | 5 | 15 | affaan-m/ECC |
| 8 | A-prompt-better | HIGH | P1 | 3 | 5 | 2 | 1 | 5 | 17 | DietrichGebert/ponytail |
| 9 | A-skill-manager | HIGH | PROTECTED_HOLD（禁替换） | 3 | 5 | 2 | 2 | 5 | 19 | — |
| 10 | agent-browser | MID | P2 | 3 | 5 | 2 | 0 | 5 | 13 | browser-act/skills |
| 11 | ai-video-homework-pipeline | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 12 | algorithmic-art | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 13 | audio-deliverable-pipeline | MID | P2 | 3 | 5 | 2 | 0 | 5 | 13 | EGSECDA/vocaloid-style-mv-pipeline |
| 14 | audit-runner-safe-aggregate | HIGH | P1 | 3 | 5 | 2 | 0 | 5 | 15 | cloudflare/security-audit-skill |
| 15 | bigfile-split | HIGH | P1 | 3 | 5 | 2 | 0 | 5 | 15 | AgriciDaniel/claude-obsidian |
| 16 | brainstorming | LOW | LOW-KEEP（季度观察） | 5 |  |  |  |  |  | — |
| 17 | brand-guidelines | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 18 | browser-cdp | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 19 | byted-bp-cdn-pagesdeploy | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 20 | byted-mediakit-shared | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 21 | byted-seedance-video-generate | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 22 | byted-seedream-image-generate | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 23 | c-cleanup | HIGH | P1 | 3 | 5 | 2 | 1 | 5 | 17 | CursorTouch/Windows-MCP |
| 24 | canvas-design | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 25 | chaoshi-admin-inline-edit | HIGH | SELF-UPGRADE（语义缺口） | 3 |  |  | 1 | 0 |  | — |
| 26 | chaoshi-image-optimization | HIGH | P1 | 3 | 5 | 2 | 1 | 5 | 17 | Leonxlnx/taste-skill |
| 27 | chaoshi-web-deploy | HIGH | P0 | 3 | 5 | 2 | 2 | 5 | 19 | agentscope-ai/QwenPaw |
| 28 | chart-visualization | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 29 | cloudbase-db-optimize | MID | SELF-UPGRADE（语义缺口） | 3 |  |  | 1 | 0 |  | — |
| 30 | cloudbase__skillhub | EXCLUDE | EXCLUDE（R241 不迁移） | 0 |  |  |  |  |  | — |
| 31 | code-review | HIGH | P1 | 3 | 5 | 2 | 1 | 5 | 17 | alibaba/open-code-review |
| 32 | coding-agent | LOW | LOW-KEEP（季度观察） | 5 |  |  |  |  |  | — |
| 33 | computer-use-guidance-windows | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 34 | consulting-analysis | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 35 | cross-platform-agent-sync | HIGH | P1 | 3 | 5 | 2 | 0 | 5 | 15 | Agents365-ai/drawio-skill |
| 36 | data-analysis | LOW | LOW-KEEP（季度观察） | 5 |  |  |  |  |  | — |
| 37 | data-visualization | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 38 | debugging-fixing | MID | P1 | 3 | 5 | 2 | 1 | 5 | 15 | JuliusBrussee/caveman |
| 39 | defuddle | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 40 | diagram-maker | LOW | LOW-KEEP（季度观察） | 5 |  |  |  |  |  | — |
| 41 | discover-agent-cli | MID | P2 | 3 | 5 | 2 | 0 | 5 | 13 | ThinkInAIXYZ/deepchat |
| 42 | doc-coauthoring | LOW | LOW-KEEP（季度观察） | 4 |  |  |  |  |  | — |
| 43 | docx | EXCLUDE | EXCLUDE（R241 不迁移） | 4 |  |  |  |  |  | — |
| 44 | dogfood | HIGH | SELF-UPGRADE（语义缺口） | 3 |  |  | 2 | 0 |  | — |
| 45 | electron | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 46 | elon-musk-perspective | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 47 | executing-plans | LOW | LOW-KEEP（季度观察） | 0 |  |  |  |  |  | — |
| 48 | fenjue-lessons-hitrate | HIGH | SELF-UPGRADE（语义缺口） | 3 |  |  | 0 | 0 |  | — |
| 49 | fenjue-memory-audit | HIGH | P2 | 3 | 5 | 2 | 0 | 5 | 15 | affaan-m/ECC |
| 50 | figma | EXCLUDE | EXCLUDE（R241 不迁移） | 4 |  |  |  |  |  | — |
| 51 | find-skills | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 52 | first-principles-decomposer | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 53 | frontend-design | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 54 | frontend-skill | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 55 | frontend-slides | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 56 | github | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 57 | gsap | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 58 | gstack | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 59 | hermes-installer | HIGH | P2 | 3 | 5 | 2 | 0 | 3 | 13 | lennney/stop-that-shit |
| 60 | hook-analyzer-skill | MID | P1 | 3 | 5 | 2 | 2 | 5 | 17 | EL4CTEO/blender-skills |
| 61 | html-ppt | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 62 | html-to-docx-win-fix | MID | P2 | 3 | 5 | 2 | 0 | 5 | 13 | appautomaton/document-SKILLs |
| 63 | hyperframes | LOW | LOW-KEEP（季度观察） | 5 |  |  |  |  |  | — |
| 64 | hyperframes-cli | LOW | LOW-KEEP（季度观察） | 5 |  |  |  |  |  | — |
| 65 | hyperframes-media | LOW | LOW-KEEP（季度观察） | 5 |  |  |  |  |  | — |
| 66 | hyperframes-registry | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 67 | ican-deploy | HIGH | P2 | 3 | 5 | 2 | 0 | 5 | 15 | agentscope-ai/QwenPaw |
| 68 | ican-frontend-design-system | HIGH | P1 | 3 | 5 | 2 | 1 | 5 | 17 | asgeirtj/system_prompts_leaks |
| 69 | internal-comms | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 70 | json-canvas | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 71 | knowledge-capture | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 72 | local-asr | MID | P2 | 3 | 5 | 2 | 1 | 5 | 15 | equalang/equalang-skill |
| 73 | local-computer-use | MID | P2 | 3 | 5 | 2 | 1 | 5 | 15 | browser-use/browser-harness |
| 74 | local-img2img | MID | P2 | 3 | 5 | 2 | 1 | 5 | 15 | nexu-io/open-design |
| 75 | local-mineru | MID | P2 | 3 | 5 | 2 | 1 | 5 | 15 | nexu-io/open-design |
| 76 | local-ocr-npu | MID | P2 | 3 | 5 | 2 | 1 | 5 | 15 | Anionex/agent-vision-toolkit |
| 77 | local-realtime-translator | MID | P2 | 3 | 5 | 2 | 1 | 5 | 15 | AgriciDaniel/claude-seo |
| 78 | local-screenshot-qa | MID | P2 | 3 | 5 | 2 | 1 | 5 | 15 | AgriciDaniel/claude-seo |
| 79 | local-tts | MID | P2 | 3 | 5 | 2 | 1 | 5 | 15 | equalang/equalang-skill |
| 80 | local-txt2img | MID | P2 | 3 | 5 | 2 | 1 | 5 | 15 | nexu-io/open-design |
| 81 | local-vram | MID | P1 | 3 | 5 | 2 | 2 | 5 | 17 | EverMind-AI/EverOS |
| 82 | mcporter | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 83 | meeting-intelligence | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 84 | nano-pdf | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 85 | node-inspect-debugger | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 86 | notion-cli | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 87 | obsidian-bases | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 88 | obsidian-cli | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 89 | obsidian-markdown | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 90 | oc-dispatch-exec-guard | HIGH | P1 | 3 | 5 | 2 | 2 | 5 | 19 | affaan-m/ECC |
| 91 | office-automation-pro | MID | P2 | 3 | 5 | 2 | 1 | 5 | 15 | genspark-ai/genoffice |
| 92 | openai-whisper-api | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 93 | openclaw-dual-gate-quality-audit | HIGH | P1 | 3 | 5 | 2 | 2 | 5 | 19 | cloudflare/security-audit-skill |
| 94 | openclaw-fenjue-weekly | HIGH | P1 | 3 | 5 | 2 | 1 | 5 | 17 | iOfficeAI/AionUi |
| 95 | openclaw-task-supervision | HIGH | P1 | 3 | 5 | 2 | 1 | 5 | 17 | iOfficeAI/AionUi |
| 96 | oracle | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 97 | pdf | EXCLUDE | EXCLUDE（R241 不迁移） | 4 |  |  |  |  |  | — |
| 98 | pixelle-api-ensure | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 99 | pptx | EXCLUDE | EXCLUDE（R241 不迁移） | 0 |  |  |  |  |  | — |
| 100 | prompt-consolidation | HIGH | P0 | 3 | 5 | 2 | 3 | 5 | 21 | blader/humanizer |
| 101 | prompt-system-audit | HIGH | P1 | 3 | 5 | 2 | 2 | 5 | 19 | Ar9av/obsidian-wiki |
| 102 | python-debugpy | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 103 | refactoring | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 104 | report-generator-skill | MID | P2 | 3 | 5 | 2 | 0 | 5 | 13 | Akxan/ppt-agent-skill |
| 105 | research-documentation | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 106 | screenshot | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 107 | shadcn | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 108 | shell-encoding-pitfalls | MID | P2 | 3 | 5 | 2 | 1 | 5 | 15 | openclaw/lobster |
| 109 | slides | EXCLUDE | EXCLUDE（R241 不迁移） | 0 |  |  |  |  |  | — |
| 110 | spec-to-implementation | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 111 | spike | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 112 | sq-cleanmgr-c | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 113 | static-site-batch-audit-fix | HIGH | P1 | 3 | 5 | 2 | 2 | 5 | 19 | glitternetwork/pinme |
| 114 | story | LOW | LOW-KEEP（季度观察） | 5 |  |  |  |  |  | — |
| 115 | story-cover | HIGH | P2 | 3 | 5 | 2 | 0 | 5 | 15 | GargantuaX/gemini-watermark-remover |
| 116 | story-deslop | HIGH | SELF-UPGRADE（语义缺口） | 5 |  |  | 0 | 0 |  | — |
| 117 | story-import | HIGH | HOLD（无正增益） | 5 |  |  | 1 | 5 |  | — |
| 118 | story-long-analyze | HIGH | HOLD（无正增益） | 5 |  |  | 3 | 3 |  | — |
| 119 | story-long-write | HIGH | HOLD（无正增益） | 5 |  |  | 3 | 5 |  | — |
| 120 | story-review | HIGH | HOLD（无正增益） | 5 |  |  | 1 | 5 |  | — |
| 121 | story-scan | HIGH | SELF-UPGRADE（语义缺口） | 3 |  |  | 1 | 0 |  | — |
| 122 | story-setup | HIGH | HOLD（无正增益） | 5 |  |  | 0 | 5 |  | — |
| 123 | story-short-analyze | HIGH | HOLD（无正增益） | 5 |  |  | 1 | 5 |  | — |
| 124 | story-short-write | HIGH | HOLD（无正增益） | 5 |  |  | 1 | 5 |  | — |
| 125 | taskflow | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 126 | taskflow-inbox-triage | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 127 | test-driven-development | LOW | LOW-KEEP（季度观察） | 5 |  |  |  |  |  | — |
| 128 | testing | MID | P2 | 3 | 5 | 2 | 0 | 5 | 13 | career-ops-hq/career-ops |
| 129 | theme-factory | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 130 | ui-ux-pro-max | EXCLUDE | EXCLUDE（R241 不迁移） | 5 |  |  |  |  |  | — |
| 131 | utf8-encoding-fix | MID | P1 | 3 | 5 | 2 | 2 | 5 | 17 | browser-act/skills |
| 132 | video-breakdown-skill | MID | P2 | 3 | 5 | 2 | 1 | 5 | 15 | cclank/lanshu-awesome-ai-video-kit |
| 133 | video-frames | EXCLUDE | EXCLUDE（R241 不迁移） | 3 |  |  |  |  |  | — |
| 134 | video-whisper-transcribe | MID | P1 | 3 | 5 | 2 | 2 | 5 | 17 | cclank/lanshu-awesome-ai-video-kit |
| 135 | vp-perspective-audit | HIGH | SELF-UPGRADE（语义缺口） | 3 |  |  | 1 | 0 |  | — |
| 136 | wb-git-commit-recipe | HIGH | SELF-UPGRADE（语义缺口） | 3 |  |  | 0 | 0 |  | — |
| 137 | web-design-guidelines | LOW | LOW-KEEP（季度观察） | 3 |  |  |  |  |  | — |
| 138 | wechat-automation | HIGH | P2 | 3 | 5 | 2 | 0 | 5 | 15 | googleworkspace/cli |
| 139 | wechat-voice-transcription | HIGH | P2 | 3 | 5 | 2 | 0 | 5 | 15 | equalang/equalang-skill |
| 140 | win-toolchain-pitfalls | MID | P2 | 3 | 5 | 2 | 0 | 5 | 13 | alchaincyf/huashu-design |
| 141 | windows-bash-cli-interop-pitfalls | HIGH | P0 | 3 | 5 | 2 | 3 | 5 | 21 | CursorTouch/Windows-MCP |
| 142 | windows-cli-utf8-wrapper | HIGH | P0 | 3 | 5 | 2 | 3 | 5 | 21 | CursorTouch/Windows-MCP |
| 143 | windows-gitbash-chinese-path-pit | HIGH | P0 | 3 | 5 | 2 | 3 | 4 | 20 | cheaper-inference/OmniRoute |
| 144 | windows-native-ocr | HIGH | P2 | 3 | 5 | 2 | 0 | 5 | 15 | Anionex/agent-vision-toolkit |
| 145 | workbuddy-mcp | HIGH | P2 | 3 | 5 | 2 | 0 | 5 | 15 | agentscope-ai/QwenPaw |
| 146 | workflow-preflight-check | HIGH | P1 | 3 | 5 | 2 | 1 | 5 | 17 | activepieces/activepieces |
| 147 | wps-knowledgebase | HIGH | SELF-UPGRADE（语义缺口） | 3 |  |  | 2 | 0 |  | — |
| 148 | writing-plans | LOW | LOW-KEEP（季度观察） | 5 |  |  |  |  |  | — |
| 149 | xlsx | EXCLUDE | EXCLUDE（R241 不迁移） | 4 |  |  |  |  |  | — |
| 150 | 天眼一下 | MID | SELF-UPGRADE（语义缺口） | 3 |  |  | 0 | 0 |  | — |
### 2.4 P0 / P1 / P2 分批定义

| 批次 | 件数 | 选择依据 | 阶段门 |
|---|---:|---|---|
| **P0 试点** | 5 | 先排除 `protected_skills` 命中件，再按 priority_index 取前 5 且 `D:/global_skills/<slug>/SKILL.md` 现场存在（✅已实测） | G0 → G1 → G2 |

| **P1 首批扩展** | 24 | 排除 protected 后 replaceable 排名 6–29 | G3 |

| **P2 全量替换 + 复评** | 28 | 其余 replaceable + 9 HOLD 复评（含 1 件 protected_hold 禁替换） + 11 缺口升级通道 | G4 → G5 |

机器可读名单见 `04_migration_batches.json` 的 `P0` / `P1` / `P2` 三键。

### 2.5 11 件语义缺口：单列「自建升级/保持」，**不替换**（captain m00020 硬要求）

t2 `semantic_gap=true`；`03_evaluation_matrix.md:598`(B5) 明写这 11 件「只有线索、无真替代」。54 条 `directed_lead` 仅元数据 ✅已实测、功能等价 ❌未实测，按 X-29 不升格为替代；44 条 `family_pad` 为族级邻居 `not_replacement=true`。

| slug | 处置 | 依据 | 升级通道（走 `rule_editor.py`，非替换） |
|---|---|---|---|
| 天眼一下 | 自建升级 / 保持 | `data/candidates.json` semantic_gap=true；rel=skill 候选数 0 | G4 若 t6 A/B 找到 可运行+可移植+有交集 三者齐备的候选，才转 P2；否则保持 |
| A-ask-questions | 自建升级 / 保持 | `data/candidates.json` semantic_gap=true；rel=skill 候选数 0 | G4 若 t6 A/B 找到 可运行+可移植+有交集 三者齐备的候选，才转 P2；否则保持 |
| chaoshi-admin-inline-edit | 自建升级 / 保持 | `data/candidates.json` semantic_gap=true；rel=skill 候选数 0 | G4 若 t6 A/B 找到 可运行+可移植+有交集 三者齐备的候选，才转 P2；否则保持 |
| cloudbase-db-optimize | 自建升级 / 保持 | `data/candidates.json` semantic_gap=true；rel=skill 候选数 0 | G4 若 t6 A/B 找到 可运行+可移植+有交集 三者齐备的候选，才转 P2；否则保持 |
| dogfood | 自建升级 / 保持 | `data/candidates.json` semantic_gap=true；rel=skill 候选数 0 | G4 若 t6 A/B 找到 可运行+可移植+有交集 三者齐备的候选，才转 P2；否则保持 |
| fenjue-lessons-hitrate | 自建升级 / 保持 | `data/candidates.json` semantic_gap=true；rel=skill 候选数 0 | G4 若 t6 A/B 找到 可运行+可移植+有交集 三者齐备的候选，才转 P2；否则保持 |
| story-deslop | 自建升级 / 保持 | `data/candidates.json` semantic_gap=true；rel=skill 候选数 0 | G4 若 t6 A/B 找到 可运行+可移植+有交集 三者齐备的候选，才转 P2；否则保持 |
| story-scan | 自建升级 / 保持 | `data/candidates.json` semantic_gap=true；rel=skill 候选数 0 | G4 若 t6 A/B 找到 可运行+可移植+有交集 三者齐备的候选，才转 P2；否则保持 |
| vp-perspective-audit | 自建升级 / 保持 | `data/candidates.json` semantic_gap=true；rel=skill 候选数 0 | G4 若 t6 A/B 找到 可运行+可移植+有交集 三者齐备的候选，才转 P2；否则保持 |
| wb-git-commit-recipe | 自建升级 / 保持 | `data/candidates.json` semantic_gap=true；rel=skill 候选数 0 | G4 若 t6 A/B 找到 可运行+可移植+有交集 三者齐备的候选，才转 P2；否则保持 |
| wps-knowledgebase | 自建升级 / 保持 | `data/candidates.json` semantic_gap=true；rel=skill 候选数 0 | G4 若 t6 A/B 找到 可运行+可移植+有交集 三者齐备的候选，才转 P2；否则保持 |
### 2.6 9 件 HOLD（8 件无 compat 正增益 + 1 件 protected_hold 禁替换）

| slug | cur_compat | best_compat | rel_n | 原因 |
|---|---:|---:|---:|---|
| A-java-problem | 3 | 3 | 5 | best_compat ≤ cur_compat，按结构可比面不产生正收益；G4 用 t6 同业务指标 A/B 复评，禁靠 T 差值强推 |
| story-import | 5 | 5 | 5 | best_compat ≤ cur_compat，按结构可比面不产生正收益；G4 用 t6 同业务指标 A/B 复评，禁靠 T 差值强推 |
| story-long-analyze | 5 | 5 | 3 | best_compat ≤ cur_compat，按结构可比面不产生正收益；G4 用 t6 同业务指标 A/B 复评，禁靠 T 差值强推 |
| story-long-write | 5 | 5 | 5 | best_compat ≤ cur_compat，按结构可比面不产生正收益；G4 用 t6 同业务指标 A/B 复评，禁靠 T 差值强推 |
| story-review | 5 | 5 | 5 | best_compat ≤ cur_compat，按结构可比面不产生正收益；G4 用 t6 同业务指标 A/B 复评，禁靠 T 差值强推 |
| story-setup | 5 | 5 | 5 | best_compat ≤ cur_compat，按结构可比面不产生正收益；G4 用 t6 同业务指标 A/B 复评，禁靠 T 差值强推 |
| story-short-analyze | 5 | 5 | 5 | best_compat ≤ cur_compat，按结构可比面不产生正收益；G4 用 t6 同业务指标 A/B 复评，禁靠 T 差值强推 |
| story-short-write | 5 | 5 | 5 | best_compat ≤ cur_compat，按结构可比面不产生正收益；G4 用 t6 同业务指标 A/B 复评，禁靠 T 差值强推 |
| A-skill-manager | 3 | 5 | 5 | **protected_hold 禁替换**（`_my-skills/registry.json` protected_skills：所有技能增删改查唯一入口）；仅允许经 `rule_editor.py` 自建增量升级，不进入任何替换批次 |
### 2.7 LOW 30 / EXCLUDE 43（不进替换分母，但逐件有处置）

- LOW 30：`LOW-KEEP`，保持现状，纳入 t5 季度巡检观察面（`05_inspection_regime.md:24-35`，`自建skill优化/.github/workflows/quarterly_audit.yml:34` cron `0 22 1 1,4,7,10 *`）。

- EXCLUDE 43：`EXCLUDE`，按 R241 历史判据不迁移，不改 `06-benchmark/全量对标报告_r*.md` 旧数字，只加校正注。

---

## 3. 阶段门时间节点（取代日历；X-2 本仓无发布流水线）

captain m00020 §四：需求④的「时间节点」以**阶段门**为准（进入条件 / 验证通过条件 / 回滚触发条件），不用日历日期；`memory/AGENTS.md:63` X-2 明写不得为「像一线」补 LICENSE / 开 release。若需相对周次，见 §3.2，且每格注明依赖哪道门。

### 3.1 门定义

| 门 | 进入条件 | 验证通过条件 | 回滚触发条件 |
|---|---|---|---|
| **G0 基线门** | t1/t2/t3 三件交付件 + 本计划三件落盘 | `04_plan_check.py` PASS；双仓 `git describe --tags` 可解析；`git -C D:/global_skills status --porcelain` 干净或差异具名 | 任一硬前提缺位 ⇒ 不进入 G1，不写受管源 |

| **G1 试点进入门** | G0 PASS；P0 5 件 `SKILL.md` 存在；双硬前提命令实跑 rc=0 | 备份落 `_trash` 且 `Test-Path` 为真；annotated tag `r345` 建成且 `git describe --tags` 解析到它 | 备份或 tag 任一失败 ⇒ 禁改 skill，停在只读取证态 |

| **G2 试点验收门** | P0 5 件经 `rule_editor.py` 写入完成 | 三门禁 PASS；`run_gates.py` verdict 与基线一致或改善（既有红不新增）；r115 质量口径不劣化；A/B 无业务逻辑回归 / 无兼容性问题 | 任一失败 ⇒ 立即触发 §4.7 回滚 |

| **G3 P1 门** | G2 PASS；P1 24 件候选元数据复取（`gh api` 或 `r114 --offline` 退路并具名盲区） | 候选守恒；`04_plan_check.py --stats` 计数不变 | 元数据面不可用且离线缓存亦缺 ⇒ 该件标 UNVERIFIED 并顺延，禁补 0 |

| **G4 P2 门** | G3 PASS；9 HOLD 复评结论落盘（含 1 件 protected_hold 禁替换）；11 缺口升级通道登记 | 复评/登记可复算；无 X-29 三门槛不齐的强推 | 三门槛不齐 ⇒ 维持「自建升级/保持」 |

| **G5 全量收口门** | G4 PASS；t5 季度巡检接线 | 需求⑥ A/B 达 ≥30% 且业务逻辑不受影响、无兼容性问题（口径见 §7.3/§7.4） | 需求⑥ 未达 ⇒ 停在全量替换后的观察态，禁宣告完成 |

### 3.2 相对周次（仅在需要排期时使用，每格绑定门）

| 周次 | 绑定门 | 允许动作 |
|---|---|---|
| W1 | G0 | 只读取证、计划/判据落盘、双仓锚点校验 |

| W2 | G1 → G2 | P0 5 件试点；未过 G2 则回滚并留在 W2，不进 W3 |

| W3 | G3 | P1 24 件（按 G3 通过件数推进，可按件切分） |

| W4 | G4 | P2 28 件 + 9 HOLD 复评（含 1 件 protected_hold 禁替换） + 11 缺口登记 |

| W5 | G5 | 需求⑥ A/B 收口；不达阈值则停在观察态 |

> W1–W5 是**相对周次**，不是日历日期；推进条件是上一道门 PASS，故不存在「到点必须发版」。

### 3.3 逐批时间节点表

| 批次 | 进入门 | 验收门 | 回滚门 | 相对周次 |
|---|---|---|---|---|
| P0 | G1 | G2 | G2 失败即触发 | W2 |

| P1 | G3（依赖 G2 PASS） | G3 验证通过条件 | G3 触发条件 | W3 |

| P2 | G4（依赖 G3 PASS） | G5 | G4/G5 触发条件 | W4–W5 |

---

## 4. P0 试点替换（5 件，每件四件套齐全）

### 4.0 试点范围与选择依据

范围 = `prompt-consolidation`、`windows-bash-cli-interop-pitfalls`、`windows-cli-utf8-wrapper`、`windows-gitbash-chinese-path-pit`、`chaoshi-web-deploy`（✅已实测：`D:/global_skills/<slug>/SKILL.md` 均存在，排除 protected 后按 priority_index 取前 5）。选择依据 = §2.1 结构可比公式；**不按 T 排序**。`A-skill-manager` 命中 protected_skills 已排除，改入 `protected_hold`（§4.6）。试点只在这 5 件内做，不扩散到其余 72 件。

每件固定四件套：**(a)** 唯一途径 `rule_editor.py` 说明与命令；**(b)** 双硬前提命令（备份落 `_trash` + Git 可回滚 annotated tag）；**(c)** 可复跑验证标准；**(d)** 可解析回滚命令（含 tag 锚 `rNN` 与 `git describe`）。

> 前置环境（所有命令块共用，PowerShell）：
```powershell
$env:PYTHONPYCACHEPREFIX = "_temp/pycache"
$PY = "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
$RE = "D:/global_skills/A-memory-start/references/rule_editor.py"
```
> `$PY` 现场 `Test-Path=True`；`$RE` 现场 `Test-Path=True`（`glob` 唯一命中 1 件）。`_temp/t4_p0/*.old.md` / `*.new.md` 由 G1 进入门在隔离区物化：`.old.md` = `rule_editor.py show` 输出，`.new.md` = 首选候选经 `gh api repos/<OWNER>/<REPO>` 取回的正文；物化落在 `_temp/`，不碰 tracked 件。
### 4.1 P0-1 `prompt-consolidation`

| 项 | 值 | 取值命令 |
|---|---|---|
| class / priority_index | HIGH / 21 | `04_plan_check.py --stats` |

| cur_compat / best_compat / gain | 3 / 5 / +2 | `data/matrix.csv` dimension=compat |

| known_defects_n / rel_skill_n | 3 / 5 | `data/inventory.json` / `data/candidates.json` |

| 首选候选（compat 最优） | `blader/humanizer` | `data/matrix.csv` object_id=`cand:prompt-consolidation::blader/humanizer` |

| ⚠️ T 使用边界 | T 仅旁证资产包工程完成度；引用 T 差须同屏给 §1.2 约 90% 结构性校正 | `03_evaluation_matrix.md:581,594,599` |

**(a) 唯一途径 `rule_editor.py`**：按 `06-constraints.md:100` / `memory/AGENTS.md:72`，改 `D:/global_skills/prompt-consolidation/SKILL.md` 只能经 `rule_editor.py` 的 `show → replace --dry-run → replace → commit → gates`，禁 `write_file` 整体重写。`rule_editor.py:1672-1741` 确认这些子命令与参数均存在。

```powershell
& $PY -B $RE show --file "D:/global_skills/prompt-consolidation/SKILL.md" --lines 1-200
& $PY -B $RE replace --file "D:/global_skills/prompt-consolidation/SKILL.md" --old-file "_temp/t4_p0/prompt-consolidation.old.md" --new-file "_temp/t4_p0/prompt-consolidation.new.md" --dry-run
& $PY -B $RE replace --file "D:/global_skills/prompt-consolidation/SKILL.md" --old-file "_temp/t4_p0/prompt-consolidation.old.md" --new-file "_temp/t4_p0/prompt-consolidation.new.md"
& $PY -B $RE commit --file "D:/global_skills/prompt-consolidation/SKILL.md" --desc "t4 P0-1 replace prompt-consolidation via blader/humanizer"
& $PY -B $RE gates
```
**(b) 双硬前提命令**（`自建skill优化/AGENTS.md:51`；G1 进入门前执行，rc=0 才允许 (a)）：

```powershell
# H1 备份落 _trash（破坏性动作硬前提之一）
Copy-Item -Recurse -Force "D:/global_skills/prompt-consolidation" "D:/global_skills/_trash/t4_p0_prompt-consolidation"
Test-Path "D:/global_skills/_trash/t4_p0_prompt-consolidation/SKILL.md"
# H2 Git 可回滚：annotated tag 锚 + describe 可解析（两仓分别建锚）
git -C "D:/global_skills" tag -a r345 -m "t4 P0 pre-change anchor r345"
git -C "D:/global_skills" describe --tags --abbrev=0
git -C "自建skill优化" tag -a r345 -m "t4 P0 deliverables anchor r345"
git -C "自建skill优化" describe --tags
```
**(c) 可复跑验证标准**（G2；命令可重复执行、末行可比对）：

```powershell
& $PY -B $RE gates
& $PY -B "自建skill优化/05-exec/run_gates.py" --json "_temp/t4_p0_prompt-consolidation_gates.json"
& $PY -B "自建skill优化/05-exec/r115_quality_truth.py"
& $PY -B "自建skill优化/deliverables/skill-modernization-r1/04_plan_check.py"
powershell -File "C:/Users/37533/Desktop/workspace/焚诀/skill/sync/check-skill-mirror.ps1"
```
判据：`rule_editor.py gates` 四门禁 PASS；`run_gates.py` verdict 与 G0 基线一致或改善（既有 7 FAIL / 2 UNVERIFIED 不新增，按 R263/X-9 如实登记不凑绿）；r115 第⑨段质量口径不劣化；`check-skill-mirror.ps1` **不带 `-Fix`** 只读检查（`memory/AGENTS.md:137` 明写 `rule_editor.py commit` 只落权威源不自动同步镜像，禁顺手 `-Fix` 凑绿）；`04_plan_check.py` 末行 `[PLAN:CHECK] PASS`。

**(d) 可解析回滚命令**（标记 `@rollback`，由 `04_plan_check.py` 逐条静态校验；含 tag 锚 `r345` 与 `git describe`、`r345..HEAD` 区间回滚）：

```powershell
# @rollback BATCH=P0 SKILL=prompt-consolidation ANCHOR=r345
# (a) 唯一途径撤销权威源写入
& $PY -B $RE undo --file "D:/global_skills/prompt-consolidation/SKILL.md" --force
# (b) 双硬前提复核：备份已在 _trash + Git 可回滚
Test-Path "D:/global_skills/_trash/t4_p0_prompt-consolidation/SKILL.md"
git -C "D:/global_skills" status --porcelain
# (c) tag 锚解析（G1 进入门已建 annotated tag r345）
git -C "D:/global_skills" tag -l "r345"
git -C "D:/global_skills" describe --tags --abbrev=0
git -C "自建skill优化" describe --tags
# (d) 区间回滚，含 r345..HEAD
git -C "D:/global_skills" revert --no-edit r345..HEAD
git -C "自建skill优化" revert --no-edit r345..HEAD
# (e) 从 _trash 恢复备份（双硬前提的备份腿）
Copy-Item -Recurse -Force "D:/global_skills/_trash/t4_p0_prompt-consolidation/SKILL.md" "D:/global_skills/prompt-consolidation/SKILL.md"
# (f) 可复跑验证
& $PY -B "自建skill优化/05-exec/run_gates.py" --json "_temp/t4_p0_rollback_gates.json"
& $PY -B "自建skill优化/deliverables/skill-modernization-r1/04_plan_check.py"
```

### 4.2 P0-2 `windows-bash-cli-interop-pitfalls`

| 项 | 值 | 取值命令 |
|---|---|---|
| class / priority_index | HIGH / 21 | `04_plan_check.py --stats` |

| cur_compat / best_compat / gain | 3 / 5 / +2 | `data/matrix.csv` dimension=compat |

| known_defects_n / rel_skill_n | 3 / 5 | `data/inventory.json` / `data/candidates.json` |

| 首选候选（compat 最优） | `CursorTouch/Windows-MCP` | `data/matrix.csv` object_id=`cand:windows-bash-cli-interop-pitfalls::CursorTouch/Windows-MCP` |

| ⚠️ T 使用边界 | T 仅旁证资产包工程完成度；引用 T 差须同屏给 §1.2 约 90% 结构性校正 | `03_evaluation_matrix.md:581,594,599` |

**(a) 唯一途径 `rule_editor.py`**：按 `06-constraints.md:100` / `memory/AGENTS.md:72`，改 `D:/global_skills/windows-bash-cli-interop-pitfalls/SKILL.md` 只能经 `rule_editor.py` 的 `show → replace --dry-run → replace → commit → gates`，禁 `write_file` 整体重写。`rule_editor.py:1672-1741` 确认这些子命令与参数均存在。

```powershell
& $PY -B $RE show --file "D:/global_skills/windows-bash-cli-interop-pitfalls/SKILL.md" --lines 1-200
& $PY -B $RE replace --file "D:/global_skills/windows-bash-cli-interop-pitfalls/SKILL.md" --old-file "_temp/t4_p0/windows-bash-cli-interop-pitfalls.old.md" --new-file "_temp/t4_p0/windows-bash-cli-interop-pitfalls.new.md" --dry-run
& $PY -B $RE replace --file "D:/global_skills/windows-bash-cli-interop-pitfalls/SKILL.md" --old-file "_temp/t4_p0/windows-bash-cli-interop-pitfalls.old.md" --new-file "_temp/t4_p0/windows-bash-cli-interop-pitfalls.new.md"
& $PY -B $RE commit --file "D:/global_skills/windows-bash-cli-interop-pitfalls/SKILL.md" --desc "t4 P0-2 replace windows-bash-cli-interop-pitfalls via CursorTouch/Windows-MCP"
& $PY -B $RE gates
```
**(b) 双硬前提命令**（`自建skill优化/AGENTS.md:51`；G1 进入门前执行，rc=0 才允许 (a)）：

```powershell
# H1 备份落 _trash（破坏性动作硬前提之一）
Copy-Item -Recurse -Force "D:/global_skills/windows-bash-cli-interop-pitfalls" "D:/global_skills/_trash/t4_p0_windows-bash-cli-interop-pitfalls"
Test-Path "D:/global_skills/_trash/t4_p0_windows-bash-cli-interop-pitfalls/SKILL.md"
# H2 Git 可回滚：annotated tag 锚 + describe 可解析（两仓分别建锚）
git -C "D:/global_skills" tag -a r345 -m "t4 P0 pre-change anchor r345"
git -C "D:/global_skills" describe --tags --abbrev=0
git -C "自建skill优化" tag -a r345 -m "t4 P0 deliverables anchor r345"
git -C "自建skill优化" describe --tags
```
**(c) 可复跑验证标准**（G2；命令可重复执行、末行可比对）：

```powershell
& $PY -B $RE gates
& $PY -B "自建skill优化/05-exec/run_gates.py" --json "_temp/t4_p0_windows-bash-cli-interop-pitfalls_gates.json"
& $PY -B "自建skill优化/05-exec/r115_quality_truth.py"
& $PY -B "自建skill优化/deliverables/skill-modernization-r1/04_plan_check.py"
powershell -File "C:/Users/37533/Desktop/workspace/焚诀/skill/sync/check-skill-mirror.ps1"
```
判据：`rule_editor.py gates` 四门禁 PASS；`run_gates.py` verdict 与 G0 基线一致或改善（既有 7 FAIL / 2 UNVERIFIED 不新增，按 R263/X-9 如实登记不凑绿）；r115 第⑨段质量口径不劣化；`check-skill-mirror.ps1` **不带 `-Fix`** 只读检查（`memory/AGENTS.md:137` 明写 `rule_editor.py commit` 只落权威源不自动同步镜像，禁顺手 `-Fix` 凑绿）；`04_plan_check.py` 末行 `[PLAN:CHECK] PASS`。

**(d) 可解析回滚命令**（标记 `@rollback`，由 `04_plan_check.py` 逐条静态校验；含 tag 锚 `r345` 与 `git describe`、`r345..HEAD` 区间回滚）：

```powershell
# @rollback BATCH=P0 SKILL=windows-bash-cli-interop-pitfalls ANCHOR=r345
# (a) 唯一途径撤销权威源写入
& $PY -B $RE undo --file "D:/global_skills/windows-bash-cli-interop-pitfalls/SKILL.md" --force
# (b) 双硬前提复核：备份已在 _trash + Git 可回滚
Test-Path "D:/global_skills/_trash/t4_p0_windows-bash-cli-interop-pitfalls/SKILL.md"
git -C "D:/global_skills" status --porcelain
# (c) tag 锚解析（G1 进入门已建 annotated tag r345）
git -C "D:/global_skills" tag -l "r345"
git -C "D:/global_skills" describe --tags --abbrev=0
git -C "自建skill优化" describe --tags
# (d) 区间回滚，含 r345..HEAD
git -C "D:/global_skills" revert --no-edit r345..HEAD
git -C "自建skill优化" revert --no-edit r345..HEAD
# (e) 从 _trash 恢复备份（双硬前提的备份腿）
Copy-Item -Recurse -Force "D:/global_skills/_trash/t4_p0_windows-bash-cli-interop-pitfalls/SKILL.md" "D:/global_skills/windows-bash-cli-interop-pitfalls/SKILL.md"
# (f) 可复跑验证
& $PY -B "自建skill优化/05-exec/run_gates.py" --json "_temp/t4_p0_rollback_gates.json"
& $PY -B "自建skill优化/deliverables/skill-modernization-r1/04_plan_check.py"
```

### 4.3 P0-3 `windows-cli-utf8-wrapper`

| 项 | 值 | 取值命令 |
|---|---|---|
| class / priority_index | HIGH / 21 | `04_plan_check.py --stats` |

| cur_compat / best_compat / gain | 3 / 5 / +2 | `data/matrix.csv` dimension=compat |

| known_defects_n / rel_skill_n | 3 / 5 | `data/inventory.json` / `data/candidates.json` |

| 首选候选（compat 最优） | `CursorTouch/Windows-MCP` | `data/matrix.csv` object_id=`cand:windows-cli-utf8-wrapper::CursorTouch/Windows-MCP` |

| ⚠️ T 使用边界 | T 仅旁证资产包工程完成度；引用 T 差须同屏给 §1.2 约 90% 结构性校正 | `03_evaluation_matrix.md:581,594,599` |

**(a) 唯一途径 `rule_editor.py`**：按 `06-constraints.md:100` / `memory/AGENTS.md:72`，改 `D:/global_skills/windows-cli-utf8-wrapper/SKILL.md` 只能经 `rule_editor.py` 的 `show → replace --dry-run → replace → commit → gates`，禁 `write_file` 整体重写。`rule_editor.py:1672-1741` 确认这些子命令与参数均存在。

```powershell
& $PY -B $RE show --file "D:/global_skills/windows-cli-utf8-wrapper/SKILL.md" --lines 1-200
& $PY -B $RE replace --file "D:/global_skills/windows-cli-utf8-wrapper/SKILL.md" --old-file "_temp/t4_p0/windows-cli-utf8-wrapper.old.md" --new-file "_temp/t4_p0/windows-cli-utf8-wrapper.new.md" --dry-run
& $PY -B $RE replace --file "D:/global_skills/windows-cli-utf8-wrapper/SKILL.md" --old-file "_temp/t4_p0/windows-cli-utf8-wrapper.old.md" --new-file "_temp/t4_p0/windows-cli-utf8-wrapper.new.md"
& $PY -B $RE commit --file "D:/global_skills/windows-cli-utf8-wrapper/SKILL.md" --desc "t4 P0-3 replace windows-cli-utf8-wrapper via CursorTouch/Windows-MCP"
& $PY -B $RE gates
```
**(b) 双硬前提命令**（`自建skill优化/AGENTS.md:51`；G1 进入门前执行，rc=0 才允许 (a)）：

```powershell
# H1 备份落 _trash（破坏性动作硬前提之一）
Copy-Item -Recurse -Force "D:/global_skills/windows-cli-utf8-wrapper" "D:/global_skills/_trash/t4_p0_windows-cli-utf8-wrapper"
Test-Path "D:/global_skills/_trash/t4_p0_windows-cli-utf8-wrapper/SKILL.md"
# H2 Git 可回滚：annotated tag 锚 + describe 可解析（两仓分别建锚）
git -C "D:/global_skills" tag -a r345 -m "t4 P0 pre-change anchor r345"
git -C "D:/global_skills" describe --tags --abbrev=0
git -C "自建skill优化" tag -a r345 -m "t4 P0 deliverables anchor r345"
git -C "自建skill优化" describe --tags
```
**(c) 可复跑验证标准**（G2；命令可重复执行、末行可比对）：

```powershell
& $PY -B $RE gates
& $PY -B "自建skill优化/05-exec/run_gates.py" --json "_temp/t4_p0_windows-cli-utf8-wrapper_gates.json"
& $PY -B "自建skill优化/05-exec/r115_quality_truth.py"
& $PY -B "自建skill优化/deliverables/skill-modernization-r1/04_plan_check.py"
powershell -File "C:/Users/37533/Desktop/workspace/焚诀/skill/sync/check-skill-mirror.ps1"
```
判据：`rule_editor.py gates` 四门禁 PASS；`run_gates.py` verdict 与 G0 基线一致或改善（既有 7 FAIL / 2 UNVERIFIED 不新增，按 R263/X-9 如实登记不凑绿）；r115 第⑨段质量口径不劣化；`check-skill-mirror.ps1` **不带 `-Fix`** 只读检查（`memory/AGENTS.md:137` 明写 `rule_editor.py commit` 只落权威源不自动同步镜像，禁顺手 `-Fix` 凑绿）；`04_plan_check.py` 末行 `[PLAN:CHECK] PASS`。

**(d) 可解析回滚命令**（标记 `@rollback`，由 `04_plan_check.py` 逐条静态校验；含 tag 锚 `r345` 与 `git describe`、`r345..HEAD` 区间回滚）：

```powershell
# @rollback BATCH=P0 SKILL=windows-cli-utf8-wrapper ANCHOR=r345
# (a) 唯一途径撤销权威源写入
& $PY -B $RE undo --file "D:/global_skills/windows-cli-utf8-wrapper/SKILL.md" --force
# (b) 双硬前提复核：备份已在 _trash + Git 可回滚
Test-Path "D:/global_skills/_trash/t4_p0_windows-cli-utf8-wrapper/SKILL.md"
git -C "D:/global_skills" status --porcelain
# (c) tag 锚解析（G1 进入门已建 annotated tag r345）
git -C "D:/global_skills" tag -l "r345"
git -C "D:/global_skills" describe --tags --abbrev=0
git -C "自建skill优化" describe --tags
# (d) 区间回滚，含 r345..HEAD
git -C "D:/global_skills" revert --no-edit r345..HEAD
git -C "自建skill优化" revert --no-edit r345..HEAD
# (e) 从 _trash 恢复备份（双硬前提的备份腿）
Copy-Item -Recurse -Force "D:/global_skills/_trash/t4_p0_windows-cli-utf8-wrapper/SKILL.md" "D:/global_skills/windows-cli-utf8-wrapper/SKILL.md"
# (f) 可复跑验证
& $PY -B "自建skill优化/05-exec/run_gates.py" --json "_temp/t4_p0_rollback_gates.json"
& $PY -B "自建skill优化/deliverables/skill-modernization-r1/04_plan_check.py"
```

### 4.4 P0-4 `windows-gitbash-chinese-path-pit`

| 项 | 值 | 取值命令 |
|---|---|---|
| class / priority_index | HIGH / 20 | `04_plan_check.py --stats` |

| cur_compat / best_compat / gain | 3 / 5 / +2 | `data/matrix.csv` dimension=compat |

| known_defects_n / rel_skill_n | 3 / 4 | `data/inventory.json` / `data/candidates.json` |

| 首选候选（compat 最优） | `cheaper-inference/OmniRoute` | `data/matrix.csv` object_id=`cand:windows-gitbash-chinese-path-pit::cheaper-inference/OmniRoute` |

| ⚠️ T 使用边界 | T 仅旁证资产包工程完成度；引用 T 差须同屏给 §1.2 约 90% 结构性校正 | `03_evaluation_matrix.md:581,594,599` |

**(a) 唯一途径 `rule_editor.py`**：按 `06-constraints.md:100` / `memory/AGENTS.md:72`，改 `D:/global_skills/windows-gitbash-chinese-path-pit/SKILL.md` 只能经 `rule_editor.py` 的 `show → replace --dry-run → replace → commit → gates`，禁 `write_file` 整体重写。`rule_editor.py:1672-1741` 确认这些子命令与参数均存在。

```powershell
& $PY -B $RE show --file "D:/global_skills/windows-gitbash-chinese-path-pit/SKILL.md" --lines 1-200
& $PY -B $RE replace --file "D:/global_skills/windows-gitbash-chinese-path-pit/SKILL.md" --old-file "_temp/t4_p0/windows-gitbash-chinese-path-pit.old.md" --new-file "_temp/t4_p0/windows-gitbash-chinese-path-pit.new.md" --dry-run
& $PY -B $RE replace --file "D:/global_skills/windows-gitbash-chinese-path-pit/SKILL.md" --old-file "_temp/t4_p0/windows-gitbash-chinese-path-pit.old.md" --new-file "_temp/t4_p0/windows-gitbash-chinese-path-pit.new.md"
& $PY -B $RE commit --file "D:/global_skills/windows-gitbash-chinese-path-pit/SKILL.md" --desc "t4 P0-4 replace windows-gitbash-chinese-path-pit via cheaper-inference/OmniRoute"
& $PY -B $RE gates
```
**(b) 双硬前提命令**（`自建skill优化/AGENTS.md:51`；G1 进入门前执行，rc=0 才允许 (a)）：

```powershell
# H1 备份落 _trash（破坏性动作硬前提之一）
Copy-Item -Recurse -Force "D:/global_skills/windows-gitbash-chinese-path-pit" "D:/global_skills/_trash/t4_p0_windows-gitbash-chinese-path-pit"
Test-Path "D:/global_skills/_trash/t4_p0_windows-gitbash-chinese-path-pit/SKILL.md"
# H2 Git 可回滚：annotated tag 锚 + describe 可解析（两仓分别建锚）
git -C "D:/global_skills" tag -a r345 -m "t4 P0 pre-change anchor r345"
git -C "D:/global_skills" describe --tags --abbrev=0
git -C "自建skill优化" tag -a r345 -m "t4 P0 deliverables anchor r345"
git -C "自建skill优化" describe --tags
```
**(c) 可复跑验证标准**（G2；命令可重复执行、末行可比对）：

```powershell
& $PY -B $RE gates
& $PY -B "自建skill优化/05-exec/run_gates.py" --json "_temp/t4_p0_windows-gitbash-chinese-path-pit_gates.json"
& $PY -B "自建skill优化/05-exec/r115_quality_truth.py"
& $PY -B "自建skill优化/deliverables/skill-modernization-r1/04_plan_check.py"
powershell -File "C:/Users/37533/Desktop/workspace/焚诀/skill/sync/check-skill-mirror.ps1"
```
判据：`rule_editor.py gates` 四门禁 PASS；`run_gates.py` verdict 与 G0 基线一致或改善（既有 7 FAIL / 2 UNVERIFIED 不新增，按 R263/X-9 如实登记不凑绿）；r115 第⑨段质量口径不劣化；`check-skill-mirror.ps1` **不带 `-Fix`** 只读检查（`memory/AGENTS.md:137` 明写 `rule_editor.py commit` 只落权威源不自动同步镜像，禁顺手 `-Fix` 凑绿）；`04_plan_check.py` 末行 `[PLAN:CHECK] PASS`。

**(d) 可解析回滚命令**（标记 `@rollback`，由 `04_plan_check.py` 逐条静态校验；含 tag 锚 `r345` 与 `git describe`、`r345..HEAD` 区间回滚）：

```powershell
# @rollback BATCH=P0 SKILL=windows-gitbash-chinese-path-pit ANCHOR=r345
# (a) 唯一途径撤销权威源写入
& $PY -B $RE undo --file "D:/global_skills/windows-gitbash-chinese-path-pit/SKILL.md" --force
# (b) 双硬前提复核：备份已在 _trash + Git 可回滚
Test-Path "D:/global_skills/_trash/t4_p0_windows-gitbash-chinese-path-pit/SKILL.md"
git -C "D:/global_skills" status --porcelain
# (c) tag 锚解析（G1 进入门已建 annotated tag r345）
git -C "D:/global_skills" tag -l "r345"
git -C "D:/global_skills" describe --tags --abbrev=0
git -C "自建skill优化" describe --tags
# (d) 区间回滚，含 r345..HEAD
git -C "D:/global_skills" revert --no-edit r345..HEAD
git -C "自建skill优化" revert --no-edit r345..HEAD
# (e) 从 _trash 恢复备份（双硬前提的备份腿）
Copy-Item -Recurse -Force "D:/global_skills/_trash/t4_p0_windows-gitbash-chinese-path-pit/SKILL.md" "D:/global_skills/windows-gitbash-chinese-path-pit/SKILL.md"
# (f) 可复跑验证
& $PY -B "自建skill优化/05-exec/run_gates.py" --json "_temp/t4_p0_rollback_gates.json"
& $PY -B "自建skill优化/deliverables/skill-modernization-r1/04_plan_check.py"
```

### 4.5 P0-5 `chaoshi-web-deploy`

> **[captain 2026-11-07 07:58 定点修正]** 本节原为 `A-skill-manager`。该件是注册表保护件
> （`_my-skills/registry.json:5-9` protected_skills，reason=「用户自建核心管理技能——所有技能增删改查唯一入口」；
> `SKILL.md:10-12` 自述「技能生命周期唯一总管 / 21 个技能管理类技能融合」），**禁替换**，已移入 `protected_hold`。
> P0 按同一 index 公式从 P1 补位本件（idx=19，P1 内并列最高且字典序首个）。
> 原节全文按 R241 留痕原则不删除，归档于 `_temp/t4_p0_retired_A-skill-manager_section.md`。

| 项 | 值 | 取值命令 |
|---|---|---|
| class / priority_index | HIGH / 19 | `04_plan_check.py --stats` |

| cur_compat / best_compat / gain | 3 / 5 / +2 | `data/matrix.csv` dimension=compat |

| known_defects_n / rel_skill_n | 2 / 5 | `data/inventory.json` / `data/candidates.json` |

| 补位来源 | P1（原 idx=19 并列首位，字典序首个） | `04_migration_batches.json` P0[4].backfilled_by |

| ⚠️ T 使用边界 | T 仅旁证资产包工程完成度；引用 T 差须同屏给 §1.2 约 90% 结构性校正 | `03_evaluation_matrix.md:581,594,599` |

**(a) 唯一途径 `rule_editor.py`**：按 `06-constraints.md:100` / `memory/AGENTS.md:72`，改 `D:/global_skills/chaoshi-web-deploy/SKILL.md` 只能经 `rule_editor.py` 的 `show -> replace --dry-run -> replace -> commit -> gates`，禁 `write_file` 整体重写。

```powershell
& $PY -B $RE show --file "D:/global_skills/chaoshi-web-deploy/SKILL.md" --lines 1-200
& $PY -B $RE replace --file "D:/global_skills/chaoshi-web-deploy/SKILL.md" --old-file "_temp/t4_p0/chaoshi-web-deploy.old.md" --new-file "_temp/t4_p0/chaoshi-web-deploy.new.md" --dry-run
& $PY -B $RE replace --file "D:/global_skills/chaoshi-web-deploy/SKILL.md" --old-file "_temp/t4_p0/chaoshi-web-deploy.old.md" --new-file "_temp/t4_p0/chaoshi-web-deploy.new.md"
& $PY -B $RE commit --file "D:/global_skills/chaoshi-web-deploy/SKILL.md" --desc "t4 P0-5 upgrade chaoshi-web-deploy"
& $PY -B $RE gates
```

**(b) 双硬前提命令**（`自建skill优化/AGENTS.md:51`；G1 进入门前执行，rc=0 才允许 (a)）：

```powershell
# H1 备份落 _trash
Copy-Item -Recurse -Force "D:/global_skills/chaoshi-web-deploy" "D:/global_skills/_trash/t4_p0_chaoshi-web-deploy"
Test-Path "D:/global_skills/_trash/t4_p0_chaoshi-web-deploy/SKILL.md"
# H2 Git 可回滚：annotated tag 锚 + describe 可解析（两仓分别建锚）
git -C "D:/global_skills" tag -a r345 -m "t4 P0 pre-change anchor r345"
git -C "D:/global_skills" describe --tags --abbrev=0
git -C "自建skill优化" tag -a r345 -m "t4 P0 deliverables anchor r345"
git -C "自建skill优化" describe --tags
```

**(c) 可复跑验证标准**（G2）：

```powershell
& $PY -B $RE gates
& $PY -B "自建skill优化/05-exec/run_gates.py" --json "_temp/t4_p0_chaoshi-web-deploy_gates.json"
& $PY -B "自建skill优化/05-exec/r115_quality_truth.py"
& $PY -B "自建skill优化/deliverables/skill-modernization-r1/04_protected_guard.py"
```

**(d) 可解析回滚命令**（标记 `@rollback`，由 `04_plan_check.py` 逐条静态校验；含 tag 锚 `r345` 与 `git describe`、`r345..HEAD` 区间回滚）：

```powershell
# @rollback BATCH=P0 SKILL=chaoshi-web-deploy ANCHOR=r345
& $PY -B $RE undo --file "D:/global_skills/chaoshi-web-deploy/SKILL.md" --force
git -C "D:/global_skills" tag -l
git -C "D:/global_skills" describe --tags
git -C "D:/global_skills" revert --no-edit r345..HEAD
git -C "自建skill优化" revert --no-edit r345..HEAD
Copy-Item -Recurse -Force "D:/global_skills/_trash/t4_p0_chaoshi-web-deploy/SKILL.md" "D:/global_skills/chaoshi-web-deploy/SKILL.md"
& $PY -B "自建skill优化/05-exec/run_gates.py" --json "_temp/t4_p0_rollback_gates.json"
& $PY -B "自建skill优化/deliverables/skill-modernization-r1/04_plan_check.py"
```

### 4.6 protected_hold：`A-skill-manager`（禁替换）

| 项 | 值 | 依据 |
|---|---|---|
| 处置 | **protected_hold —— 禁替换，仅允许自建增量升级** | `_my-skills/registry.json:5-9` protected_skills |
| 身份 | 技能生命周期唯一总管；21 个技能管理类技能融合体 | `A-skill-manager/SKILL.md:10-12` |
| 若替换的后果 | 拆除「所有技能增删改查唯一入口」⇒ 达不成需求6「原有业务逻辑不受影响」 | captain 裁定 2026-11-07 |
| 允许的改动路径 | `rule_editor.py` 自建增量升级（非替换） | `06-constraints.md:100` |
| 机器闸 | `python -B deliverables/skill-modernization-r1/04_protected_guard.py` -> `[PROTGUARD:CLEAN]` | 本轮新增 |

```powershell
# 迁移前置检查：命中保护名单即降级为 protected_hold
& $PY -B "自建skill优化/deliverables/skill-modernization-r1/04_protected_guard.py"
# 期望末行: [PROTGUARD:CLEAN] 替换批次内无注册表保护件
```

### 4.7 P0 整批回滚预案（批次级，标记 @rollback）

触发 = G2 任一验证条件失败；作用域 = P0 全部 5 件 + 归档仓本批交付件。

```powershell
# @rollback BATCH=P0-BATCH ANCHOR=r345
# (a) 唯一途径：逐件撤销（5 件，路径取自 04_migration_batches.json 的 P0 键）
& $PY -B $RE undo --file "D:/global_skills/prompt-consolidation/SKILL.md" --force
& $PY -B $RE undo --file "D:/global_skills/windows-bash-cli-interop-pitfalls/SKILL.md" --force
& $PY -B $RE undo --file "D:/global_skills/windows-cli-utf8-wrapper/SKILL.md" --force
& $PY -B $RE undo --file "D:/global_skills/windows-gitbash-chinese-path-pit/SKILL.md" --force
& $PY -B $RE undo --file "D:/global_skills/chaoshi-web-deploy/SKILL.md" --force
# (b) 双硬前提复核：备份落在 _trash + Git 可回滚
Test-Path "D:/global_skills/_trash"
git -C "D:/global_skills" status --porcelain
# (c) tag 锚与 git describe
git -C "D:/global_skills" tag -l "r345"
git -C "D:/global_skills" describe --tags --abbrev=0
git -C "自建skill优化" describe --tags
# (d) 区间回滚 r345..HEAD
git -C "D:/global_skills" revert --no-edit r345..HEAD
git -C "自建skill优化" revert --no-edit r345..HEAD
# (e) 可复跑验证
& $PY -B "自建skill优化/05-exec/run_gates.py" --json "_temp/t4_p0_batch_rollback_gates.json"
& $PY -B "自建skill优化/deliverables/skill-modernization-r1/04_plan_check.py"
```
---

## 5. P1 分批替换（24 件）

范围 = `04_migration_batches.json` 的 `P1` 键（24 件，排除 protected 后 priority_index 排名 6–29）。进入门 G3（依赖 G2 PASS）。

**(a) 唯一途径**：同 §4 —— 每件经 `rule_editor.py show → replace --dry-run → replace → commit → gates`，参数与 `rule_editor.py:1672-1741` 一致；禁整体重写。批量用 `04_migration_batches.json` 的 P1 名单生成逐件 `--file`，不裸跑 `git commit`（`A-project-handoff/SKILL.md:107`）。

**(b) 双硬前提命令**（G3 进入门，tag 锚 `r346`）：整树备份落**仓外** `D:/global_memory_archive/_trash`（现场 `Test-Path=True`），避免 `Copy-Item -Recurse` 把目标放进源目录造成自递归；P0 的逐件备份仍在 `D:/global_skills/_trash`。

```powershell
Copy-Item -Recurse -Force "D:/global_skills" "D:/global_memory_archive/_trash/t4_p1_backup"
Test-Path "D:/global_memory_archive/_trash/t4_p1_backup"
git -C "D:/global_skills" tag -a r346 -m "t4 P1 pre-change anchor r346"
git -C "D:/global_skills" describe --tags --abbrev=0
git -C "自建skill优化" tag -a r346 -m "t4 P1 deliverables anchor r346"
git -C "自建skill优化" describe --tags
```
**(c) 逐批验证标准**：`rule_editor.py gates` PASS；`run_gates.py --json _temp/t4_p1_gates.json` verdict 与 G0 基线一致或改善；`r115_quality_truth.py` 不劣化；`check-skill-mirror.ps1`（只读，无 `-Fix`）；`04_plan_check.py` PASS；候选元数据守恒（限流退路 `python 05-exec/r114_replacement_scan.py --offline --json _temp/t4_repl_offline.json`，具名盲区登记）。

**(d) 回滚预案（含 tag 锚 · git describe · `r346..HEAD`）**：

```powershell
# @rollback BATCH=P1 ANCHOR=r346
# (a) 唯一途径撤销：按 04_migration_batches.json 的 P1 名单逐件 rule_editor.py undo
& $PY -B $RE undo --file "D:/global_skills/9b-lightworkflow/SKILL.md" --force
# (b) 双硬前提复核：_trash 备份 + Git 可回滚
Test-Path "D:/global_memory_archive/_trash/t4_p1_backup"
git -C "D:/global_skills" status --porcelain
# (c) tag 锚与 git describe
git -C "D:/global_skills" tag -l "r346"
git -C "D:/global_skills" describe --tags --abbrev=0
git -C "自建skill优化" describe --tags
# (d) 区间回滚 r346..HEAD
git -C "D:/global_skills" revert --no-edit r346..HEAD
git -C "自建skill优化" revert --no-edit r346..HEAD
# (e) 从 _trash 恢复 + 可复跑验证
Copy-Item -Recurse -Force "D:/global_memory_archive/_trash/t4_p1_backup/*" "D:/global_skills/"
& $PY -B "自建skill优化/05-exec/run_gates.py" --json "_temp/t4_p1_rollback_gates.json"
& $PY -B "自建skill优化/deliverables/skill-modernization-r1/04_plan_check.py"
```
> P1 名单逐件命令模板与 P0 同构，`--file` 取自 `04_migration_batches.json` 的 `P1` 键；上面 `9b-lightworkflow` 为名单内实存件示例（✅已实测 `D:/global_skills/9b-lightworkflow/SKILL.md` 存在），执行时按名单循环展开，不写占位符。

---

## 6. P2 全量替换（28 件）+ 复评通道

范围 = `04_migration_batches.json` 的 `P2` 键（28 件）；另含 9 件 HOLD 复评（§2.6，其中 1 件 protected_hold 禁替换）与 11 件语义缺口升级登记（§2.5）。进入门 G4（依赖 G3 PASS），收口门 G5。

**(a) 唯一途径**：同 §4/§5，`rule_editor.py` 逐件 `show → replace --dry-run → replace → commit → gates`；退役旧版若发生，走 `A-skill-manager/references/lifecycle-delete.md`(R-DELETE) 的双份核对 + 整体移出 `D:/global_skills` 到 `_trash` + 登记黑名单 + 派生件重建（`intent-crud.md:31-41`）；禁 `rm -rf`（`lifecycle-delete.md:29-30`）。

**(b) 双硬前提命令**（G4 进入门，tag 锚 `r347`）：整树备份落**仓外** `D:/global_memory_archive/_trash`，理由同 §5(b)。

```powershell
Copy-Item -Recurse -Force "D:/global_skills" "D:/global_memory_archive/_trash/t4_p2_backup"
Test-Path "D:/global_memory_archive/_trash/t4_p2_backup"
git -C "D:/global_skills" tag -a r347 -m "t4 P2 pre-change anchor r347"
git -C "D:/global_skills" describe --tags --abbrev=0
git -C "自建skill优化" tag -a r347 -m "t4 P2 deliverables anchor r347"
git -C "自建skill优化" describe --tags
```
**(c) 逐批验证标准**：G5 = 需求⑥ A/B（§7.3）+ 三门禁 + `run_gates.py` verdict 不新增红 + r115 质量口径不劣化 + `check-skill-mirror.ps1` 只读 + `04_plan_check.py` PASS + t5 季度巡检接线（`自建skill优化/.github/workflows/quarterly_audit.yml:34`）。

**(d) 回滚预案（含 tag 锚 · git describe · `r347..HEAD`）**：

```powershell
# @rollback BATCH=P2 ANCHOR=r347
# (a) 唯一途径撤销：按 04_migration_batches.json 的 P2 名单逐件 rule_editor.py undo
& $PY -B $RE undo --file "D:/global_skills/9b-lightworkflow/SKILL.md" --force
# (b) 双硬前提复核：_trash 备份 + Git 可回滚
Test-Path "D:/global_memory_archive/_trash/t4_p2_backup"
git -C "D:/global_skills" status --porcelain
# (c) tag 锚与 git describe
git -C "D:/global_skills" tag -l "r347"
git -C "D:/global_skills" describe --tags --abbrev=0
git -C "自建skill优化" describe --tags
# (d) 区间回滚 r347..HEAD
git -C "D:/global_skills" revert --no-edit r347..HEAD
git -C "自建skill优化" revert --no-edit r347..HEAD
# (e) 从 _trash 恢复 + 可复跑验证
Copy-Item -Recurse -Force "D:/global_memory_archive/_trash/t4_p2_backup/*" "D:/global_skills/"
& $PY -B "自建skill优化/05-exec/run_gates.py" --json "_temp/t4_p2_rollback_gates.json"
& $PY -B "自建skill优化/deliverables/skill-modernization-r1/04_plan_check.py"
```
---

## 7. 验证标准（可复跑，逐批共用）

### 7.1 结构 / 兼容性门

| 判据 | 命令 | 通过条件 |
|---|---|---|
| 受管根四门禁 | `python "D:/global_skills/A-memory-start/references/rule_editor.py" gates` | mirror / noise / evolution / stub 全 PASS |

| 归档仓全量门禁 | `python 05-exec/run_gates.py --json _temp/t4_gates.json` | verdict 与 G0 基线一致或改善；FAIL/UNVERIFIED 不新增（R263/X-9 如实记红） |

| 交付件判据 | `python -B deliverables/skill-modernization-r1/04_plan_check.py` | 末行 `[PLAN:CHECK] PASS` |

| 镜像只读核对 | `powershell -File "C:/Users/37533/Desktop/workspace/焚诀/skill/sync/check-skill-mirror.ps1"` | 无 `-Fix`；差异具名登记 |

| 控制字符 | `python 05-exec/control_char_scan.py deliverables/skill-modernization-r1` | 04_* 四件（含 captain 只读件）`CTRL_SCAN CLEAN`；既有 `_temp/r295a/meta_raw.json` 红如实登记 |

### 7.2 质量口径唯一性（r115）

`05-exec/r115_quality_truth.py:2,26,43`：主指标必须测生产路由 `eval/unified_router.py::route()`，不是 eval 内 `hybrid_match`；与 r114 的 38.2% 不可比、禁相减。四层（t1 `data/inventory.json` `quality_truth.four_layers`）：L1 layered 291 条 Top-1 88.3%（含 63.6% 泄漏题加成 +7.7pp）；L2 frozen 10 条 70.0%（净化 87.5%，n 太小仅哨兵）；L3 污染；L4 干净面。**引用 L1 必须同屏给 L4**。

### 7.3 需求⑥接口（业务逻辑不受影响 / 无兼容性问题 / ≥30%）

t3 `03_evaluation_matrix.md:600` 下游接口：本计划按 (现有 skill, 候选) 对叠加 t2 的 `rel_strength` / `match_reason`，由需求⑥ owner 跑同一业务指标 A/B；`compat` 是唯一相对可比维，故兼容性判据以 t6 A/B 为准，不由 T 差值推出。`feedback_weight_cap=0`（99.94% outcome_unknown），A/B 必须自采 outcome，禁拿反馈面凑数。

### 7.4 算术边界登记（⚠️部分实测，禁假完成）

t5 `05_inspection_regime.md:48` / `_temp/t5_qi/2026Q4/audit.error.json:156` 记有 `[REQ6:IMPOSSIBLE] 阈值在本面算术不可达（需 114.8 > 上限 95.2）`。本计划**不宣称** ≥30% 已达成：G5 由需求⑥ owner 在独立 A/B 面判定；若仍不可达则停在观察态并具名登记（#36 禁假完成）。

---

## 8. 回滚命令静态校验（`04_plan_check.py`）

判据脚本对 markdown 内**每个** `# @rollback` 标记的代码块逐条做：① 语法静态校验（引号成对、命令前缀白名单、无尖括号占位、无禁用人工措辞）；② 路径存在性（块内 `D:/`、`C:/`、`自建skill优化/` 字面路径逐条 `os.path.exists`，`_temp/`、`_trash/t4_` 运行期路径按规则豁免）；③ 四件套完整性（`rule_editor.py`、`_trash`、`tag -a rNN`、`describe --tags`、`revert`、`rNN..HEAD`、两仓 `git -C`、可复跑验证）；④ 批次覆盖（P0 5 件 + P0-BATCH + P1 + P2 全部存在）；⑤ 正文一致性（§2.3 表 P0/PROTECTED_HOLD 标注与 `04_migration_batches.json` 对齐、P0-BATCH 回滚块 undo 名单恰等于 5 个 P0 slug 且不含保护件、全文无旧数字/旧名单残留）。

```text
cd 自建skill优化
$env:PYTHONPYCACHEPREFIX = "_temp/pycache"
& "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -B deliverables/skill-modernization-r1/04_plan_check.py
& "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -B deliverables/skill-modernization-r1/04_plan_check.py --negative-control
& "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -B deliverables/skill-modernization-r1/04_plan_check.py --negative-control-protected
```
期望末行：正常 `[PLAN:CHECK] PASS`；批次负控 `[NEGCTRL:RED] 删除 P1 回滚块被检出`；保护件注入负控 `[NEGCTRL:RED] P0-BATCH 注入保护件被正文一致性门检出`。三条都在内存副本上跑，**不写回** markdown（判据有牙、不是恒绿）。

保护件注入负控验真的是本次缺陷本身：把 P0-BATCH 回滚块的 `chaoshi-web-deploy` undo 在内存副本里改回 `A-skill-manager`，正文一致性 ③（undo 名单须恰等于 5 个 P0 slug 且不含 protected）必须报红；若只靠旧串黑名单命中而 ③ 未抓到，负控判 GREEN 并退出 1（✅已实测）。

```text
$ python -B deliverables/skill-modernization-r1/04_plan_check.py --negative-control-protected
[NEGCTRL:RED] P0-BATCH 注入保护件被正文一致性门检出（failures=3，P0-BATCH 相关=2）
```

**迁移前置机器闸 `04_protected_guard.py` 两条输出**（captain 所有件，只读引用、本轮未改写；✅已实测）：

```text
$ python -B deliverables/skill-modernization-r1/04_protected_guard.py
[PROTGUARD] registry=D:/global_skills/_my-skills/registry.json
[PROTGUARD] protected=['A-skill-manager']
[PROTGUARD] replacement_scope_n=57
[PROTGUARD:CLEAN] 替换批次内无注册表保护件
$ python -B deliverables/skill-modernization-r1/04_protected_guard.py --negative-control
[PROTGUARD] registry=D:/global_skills/_my-skills/registry.json
[PROTGUARD] protected=['A-skill-manager']
[PROTGUARD] replacement_scope_n=58
[NEGCTRL:RED] 注入保护件 ['A-skill-manager'] 后判据报红（符合预期）
```

---

## 9. 退路、盲区与委派登记

| 项 | 登记 |
|---|---|
| GitHub API 限流 | `python 05-exec/r114_replacement_scan.py --offline --json _temp/t4_repl_offline.json` 复用缓存；离线未命中 ⇒ `SKIPPED_OFFLINE` 具名盲区（`r114_replacement_scan.py:245/:273/:1520-1555`），禁静默丢弃、禁补 0 |

| 上游版本面全盲 | t5 隔离预览 `_temp/t5_qi/2026Q4/audit.error.json:164-177` 记 9 上游仓全 `SKIPPED_OFFLINE`，离线不等于「替代已扫全」 |

| 活跃根漂移 | t1 登记 243→247，本轮结构复扫分母 190 vs captain 146；按 R269 只登记、不擅动、不改历史判据 |

| 委派缺席 | 两次 `tools.subagent` 被 `AgentTeams member delegation limit (0) reached; report to the captain instead of spawning another agent` 拒（设计边界）；skip_reason = 团队委派上限 0，Lead 自干并登记（AGENTS.md #44 被团队策略覆盖） |

| 第二意见 | captain m00020 的独立复算作为第二意见纳入 §1；未另起子代理 |

| D:/global_skills 无可用 describe tag | 现场 `fatal: No tags can describe afec0a7e…`；故 G1/G3/G4 进入门**先建** annotated tag r345/r346/r347，回滚命令再以该锚做 `revert rNN..HEAD`，不依赖既有旧 tag |

---

## 10. 门禁实测记录（禁硬编码，本轮现跑）

> 本节已由 t4 现跑 `python 05-exec/run_gates.py --json _temp/t4_gates.json` 回填（句柄 `_temp/t4_gates.json` generated_at=2026-11-07 07:24）；`GATE_RC=1` 为聚合判红的程序退出码，不是执行失败。红门按 R263/X-9 如实登记，禁为凑绿删 tracked 件。

| 项 | 值 |
|---|---|
| 命令 | `cd 自建skill优化; $env:PYTHONPYCACHEPREFIX="_temp/pycache"; & "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -B 05-exec/run_gates.py --json _temp/t4_gates.json` |
| verdict | **FAIL** ✅已实测（句柄 `_temp/t4_gates.json` 的 `schema=gate-run-v1`；`_temp/t4_gates.log`（UTF-16LE）末行 `[GATES:FAIL] FAIL=7 UNVERIFIED=2`；`GATE_RC=1` 为聚合判红退出码，非执行失败） |
| verdict_reason | `FAIL=7 UNVERIFIED=2`（取值：`python -c "import json;d=json.load(open('_temp/t4_gates.json'));print(d['verdict'],d['verdict_reason'],d['gates_run'],d['generated_at'])"`；期望末行 `FAIL FAIL=7 UNVERIFIED=2 118 2026-11-07 07:24`） |
| gates_run / generated_at | `118` / `2026-11-07 07:24`（同上 JSON 字段句柄；日志解码取值 `buf.toString('utf16le')`，不得按 UTF-8 直读） |
| 红门具名 | `gov_acceptance_face`, `ratchet_gate`, `control_char_scan`, `refresh_budget_fixtures`, `budget_contract_fixtures`(UNVERIFIED), `baseline_note_fixtures`(UNVERIFIED), `gate_run_freshness`, `fixture_wiring_face`, `skill_wiring_face`；`real_red` 8 项、`design_inherent_red` 1 项（取值：`_temp/t4_gates.json` 的 `gates[].state` 与顶层 `real_red`/`design_inherent_red`） |
| 与 t1/t2/t3 对照 | t1 FAIL=7/UNVERIFIED=2；t2 FAIL=7/UNVERIFIED=3；t3 FAIL=7/UNVERIFIED=2、gates_run=118（`03_evaluation_matrix.md:604-608`）；t5 FAIL=7/UNVERIFIED=4（`05_inspection_regime.md:14`）；t4 本轮 FAIL=7/UNVERIFIED=2、gates_run=118，与 t3 同型，未新增 04_* 产物红 |
| 04_* 四件（含 captain 只读件）定点 | `python 05-exec/control_char_scan.py deliverables/skill-modernization-r1` ⇒ `[CTRL:CLEAN] 无非法控制符`（04_* 四件逐字节复扫亦 CLEAN）；全仓门 `control_char_scan` 的 629 面 / 脏 1 来自既有 `_temp/r295a/meta_raw.json` ×6 码位 `[127]`，按 R263/X-9 如实登记、不删 tracked 件凑绿、不归因本轮 |

> **[R241 校正注 2026-11-07]** 本表 `FAIL=7 UNVERIFIED=2 / 118 门` 为 t4 首版（补正前）全量门禁实测原值，按 R241 保留不改；captain m00117 退回补正仅定点改 P0-5 与守恒数（`replaceable` 58→57、`P1` 25→24、`holds` 8→9），本轮**未重跑全量门禁**，以 `04_plan_check.py` 与 `04_protected_guard.py` 两条机器闸为补正判据；旧数只在此加注，不改写。
>
> **未重跑全量门禁的依据（如实登记，非静默省略）**：① 全量门禁 118 门测的是既有全仓红（`real_red` 8 + `design_inherent_red` 1），对「P0-5 是否移出保护件 / 守恒是否成立」零增量判别力；② 重跑会改写 `_temp/t4_gates.json` 的 `generated_at` 与 `gates[].state` 快照，使本表 07:24 句柄与文件不再一致、与 R241「旧数只加校正注不改写」冲突；③ 补正判据链以定点闸门闭环：`04_plan_check.py` normal / `--negative-control` / `--negative-control-protected` / `--stats`、`04_protected_guard.py` normal / `--negative-control`、保护名单现场取值、`04_*` 四件定点 `control_char_scan`。补正后任一新增异常仍会由 `04_plan_check.py` 的正文一致性 ①–④ 与回滚命令静态校验当场报红。







## 11. Self-Review（writing-plans 契约）

| 检查项 | 结论 |
|---|---|
| Goal / Architecture / Tech Stack / Spec / Global Constraints | §0 齐 |

| 每件 skill 的 Files / Interfaces / Steps | §2.3 全量 150 行 + `04_migration_batches.json` 接口 + §4/§5/§6 逐批步骤 |

| Exact commands with expected output | §4 每件 (a)(b)(c)(d) 四套命令 + §8 期望末行 |

| No Placeholders | 命令中无尖括号占位；`$PY`/`$RE`/`$env:` 为 PowerShell 变量，非占位 |

| 每个 P0 四件套 | §4.1–§4.5 各含 (a) rule_editor.py (b) 双硬前提 (c) 可复跑验证 (d) 含 tag 锚与 git describe 的 revert 命令 |

| 禁「请老大手动」 | 全文无；全部 CLI / API 无头命令（#29/#48） |

| §10 门禁实测 | 已回填 `_temp/t4_gates.json` verdict=FAIL / FAIL=7 UNVERIFIED=2 / 118 门；既有红按 R263/X-9 登记，04_* 定点 `[CTRL:CLEAN]` |

| 负控 | `04_plan_check.py --negative-control` 删一批回滚块 ⇒ `[NEGCTRL:RED]`；`--negative-control-protected` 注入保护件到 P0-BATCH ⇒ `[NEGCTRL:RED]`；`04_protected_guard.py --negative-control` 注入保护件到替换面 ⇒ `[NEGCTRL:RED]` |

| 只读取证 | 本轮未改 D:/global_skills；写面 3 件 `04_*`（plan / batches / check）+ 只读复用 captain 所有件 `04_protected_guard.py` 1 件（未改写），合计定点扫描面 4 件，与 §10 口径一致 |

