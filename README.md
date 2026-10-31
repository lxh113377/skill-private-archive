# 自建 skill 体系优化审计 — 工作区入口

> 更新：2026-10-18（r113）| **跨会话入口 = `memory/07-next-steps.md`（P0 唯一真相源）**
> 权威源：`D:\global_skills`（git）→ 镜像 `C:\Users\37533\.agents\skills`

## 从哪读起（新人 / 新会话，按序）

1. [memory/07-next-steps.md](memory/07-next-steps.md) — P0 未完成项（**唯一入口，先读这个**）
2. [memory/05-feature-status.md](memory/05-feature-status.md) — 已完成 / 进行中 / 阻塞
3. 最近一轮对标报告 — 取值：`Get-ChildItem 06-benchmark -Filter '全量对标报告_r*' | Sort-Object Name | Select-Object -Last 1`（禁硬编码轮号，r110 立规）；历史执行报告见 `05-exec/README.md` 索引
4. [03-audit/自建skill优化审计报告.md](03-audit/自建skill优化审计报告.md) — 阶段3 全量审计结论（P0/P1/P2）
5. [04-plan/实施计划.md](04-plan/实施计划.md) — 阶段4 分批复核与回滚手段
6. [04-plan/迁移替换方案_r113_2026-10-18.md](04-plan/迁移替换方案_r113_2026-10-18.md) — 替换优先级 / 节点 / 验证标准 / 回滚预案（需求 4）
7. [04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md](04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md) — 季度巡检节律与判定规则（需求 5）
8. [06-benchmark/upstream_research_r113_2026-10-18.md](06-benchmark/upstream_research_r113_2026-10-18.md) — 上游候选检索 + 五维评分矩阵（需求 2/3）
9. [06-benchmark/全量对标报告_r119_语料区分度改造首次产生真实质量提升_2026-10-20.md](06-benchmark/全量对标报告_r119_语料区分度改造首次产生真实质量提升_2026-10-20.md) — 需求 6 首次真实正向 delta（生产路由 88.3%→90.1%、REAL_MISS 12→7）+ 11 条 OVERDUE 债务裁决（需求 6/7）

## 六阶段产物地图

| 阶段 | 目录 | 产物 | 状态 |
|---|---|---|---|
| 0 范围裁定 | `00-scope/` | 自建skill清单.md / 注册表失真条目.md / scope_result.json | ✅ 完成 |
| 1 四维机器扫描 | `01-scan/` | scan_report.md / scan_result.json / scan_all.py（`overlap_raw.txt` 已迁 `archive/`，2026-09-23 r8 修正此前未同步的索引） | ✅ 完成（第10轮已补齐；2026-09-23 dry-run scope/scan均exit 0） |
| 2 全量精读 | `02-review/` | 6 份族审计卡（A族 / fenjue / 审计族 / local / story / 其他） | ✅ 完成 |
| 3 审计报告 | `03-audit/` | 自建skill优化审计报告.md | ✅ 完成 |
| 4 实施计划 | `04-plan/` | 实施计划.md / 剩余待办分类清单.md / 工作流专项建议.md | ✅ 完成 |
| 5 执行 | `05-exec/` | README.md（补丁索引）/ 第2轮·第3轮·第10轮执行报告 / 19 个 patch JSON + D1/D4/D5/R270/R271 补丁目录 | ✅ 完成 |
| 记忆 | `memory/` | handoff 8 文件 + 分卷 + P-1 绑定表（AGENTS.md） | ✅ 建档 |

## 边界与铁律

- 阶段 0-3 **只读取证**；阶段 4 起才改 `D:\global_skills`，且**唯一途径 = `rule_editor.py`**（禁 `write_file` 整体重写 skill 文件）。
- 改完必须：重建派生件 → 复跑三门禁（mirror / noise / evolution）。
- 结论一律标注 `✅已实测 / ⚠️部分实测 / ❌未实测`；禁用旧快照、旧记忆、历史报告当现状。
- 落盘编辑前必须输出 `【数据流假设】` 四要素。

## 收口门禁（改完必须复跑）

```powershell
$env:PYTHONPYCACHEPREFIX="$env:TEMP\pycache_verify"
& "C:\Program Files\Python312\python.exe" "D:\global_skills\A-memory-start\references\rule_editor.py" gates
Set-Location 'C:\Users\37533\Desktop\workspace\焚诀'; & "C:\Users\37533\.workbuddy\binaries\python\envs\default\Scripts\python.exe" eval/verify_truth_consistency.py
& "C:\Program Files\Python312\python.exe" "D:\global_skills\A-project-handoff\scripts\handoff.py" review "c:\Users\37533\Desktop\workspace\自建skill优化"
```

> 实测基线（2026-09-22）：`gates` = `mirror=pass noise=pass evolution=pass`；焚诀 `verify` = **15 PASS / 0 FAIL / 0 SKIP**；`handoff review` = 5/9（56%）→ 本轮整改后 **7/9（78%）**。
> ⚠️ **校正注（2026-09-22 第 10 轮，R241 只加注不改写）**：上行为当日**当时为真**的数值。当前实测已推进 —— `handoff review` = **9/9（100%）**（D1 修 3 处判据缺陷后）、`handoff status` = **8/8 sections filled**、焚诀 `verify` = **16 PASS / 0 FAIL / 0 SKIP**（新增 C15/C16）、本项目 HEAD = `632d183`。最新数值以本注为准。
> ⚠️ **追加说明（同日，R241 只加注不改历史）**：
> ① `handoff review` 剩余 2 条 warning **均为上游判据缺陷**所致（非内容缺失），见 `memory/06-constraints.md` [BUG]；
> ② `handoff savepoint` 中途曾 1 次被拒（`焚诀\.codebuddy` 未 gitignore 豁免），已由**并行会话**（焚诀 commit `1f354e9`）解除，最终 **exit 0 通过**——详见 `05-exec/第3轮执行报告.md` 第五-附节（含「活跃工具目录不能迁 `_trash`」与「时间戳盲区」两条教训）。

## 版本控制基线（A-project-handoff 致命纪律 #20）

- 远端：`https://github.com/lxh113377/skill-private-archive.git`（私有归档仓）
- 判据：`git rev-parse HEAD` == `git ls-remote origin main` 的 SHA

## 证据面导航（r53 起；对标 `addyosmani/agent-skills` README 挂 50 个文件链接的做法）

> 入口文档只**指路**、不抄数值：正文数字写成台账字段引用（句柄），
> 由 `python 05-exec/r38_debt_aging.py` 现取；源头取不到必须显形为 None，不得沿用旧值。

### 可再生台账

- [debt_runs.jsonl](06-benchmark/debt_runs.jsonl) — 现值由末行/字段再生，报告不抄数
- [gate_runs.jsonl](06-benchmark/gate_runs.jsonl) — 现值由末行/字段再生，报告不抄数
- [md_claim_face_r52_2026-09-25.json](06-benchmark/md_claim_face_r52_2026-09-25.json) — 现值由末行/字段再生，报告不抄数

### 判据证据件（按体积前 8）

- [description基线_2026-09-24.json](06-benchmark/description基线_2026-09-24.json) — 114474 B
- [skill_structure_rubric_r29_2026-09-24.json](06-benchmark/skill_structure_rubric_r29_2026-09-24.json) — 89748 B
- [skill_structure_rubric_2026-09-24.json](06-benchmark/skill_structure_rubric_2026-09-24.json) — 49522 B
- [rationalizations_robustness_r30_2026-09-25.json](06-benchmark/rationalizations_robustness_r30_2026-09-25.json) — 31719 B
- [r31_section_robustness_2026-09-25.json](06-benchmark/r31_section_robustness_2026-09-25.json) — 31103 B
- [rationalizations_robustness_r30b_2026-09-25.json](06-benchmark/rationalizations_robustness_r30b_2026-09-25.json) — 31101 B
- [catalog_attention_tax_r20_2026-09-24.json](06-benchmark/catalog_attention_tax_r20_2026-09-24.json) — 30879 B
- [r31_section_robustness_after_2026-09-25.json](06-benchmark/r31_section_robustness_after_2026-09-25.json) — 30050 B

### 逐轮对标报告（最近 8 轮）

> **r175 迁出（R166-5 收口）**：本节原文（23,830B）已零改写迁至 [memory/readme-benchmark-reports.md](memory/readme-benchmark-reports.md)，
> README 只留指针 —— 迁出动因 = 本文件每轮注入 30,721B > `root_doc_max` 16,384B（L2 根文档瘦身）。
> 取数口径不变：最新一轮 = `Get-ChildItem 06-benchmark -Filter '全量对标报告_r*' | Sort-Object Name | Select-Object -Last 1`（禁硬编码轮号，r110 立规）。

## r260 起的交付件与需求映射（r261 增补｜入口件落后于交付件的收口）

> 读数时刻：**2026-10-28T17:36:05+0800** ｜ 起点 HEAD **a049ffc**（tag `r260d`）。
> 本节**只写句柄不抄数值**：每条给「现行最新交付件路径 + 该件读数时刻 + 取值命令」；数字一律现取（口径铁律：禁硬编码轮号与计数）。
> 七条需求的原文定义 = [06-benchmark/需求闭环审计件_r227_七项逐条对照_2026-10-25.md](06-benchmark/需求闭环审计件_r227_七项逐条对照_2026-10-25.md) §1 表（该件是 10-25 时刻的对照，**其数值已非现状**，只可引作历史）。

| # | 需求（简写） | 现行最新交付件（路径 = 句柄） | 读数时刻（件内字段现取） | 取值命令 |
|---|---|---|---|---|
| 1 | 全面盘点（功能边界/性能/缺陷/使用反馈） | [06-benchmark/r260_perf_face.json](06-benchmark/r260_perf_face.json)（性能维，本轮首建）＋ [06-benchmark/r260_inventory_defect_face.json](06-benchmark/r260_inventory_defect_face.json)（缺陷/名册/口径面）＋ [06-benchmark/性能维度_r260_2026-10-28.md](06-benchmark/性能维度_r260_2026-10-28.md) | `r260_perf_face.json` 无 `generated_at`，时刻取 `meta.date`；defect 件 = `2026-10-28T15:44:15` | `python.exe -c "import json;m=json.load(open(r'06-benchmark/r260_perf_face.json',encoding='utf-8'))['meta'];print(m['date'],m['denominator'],m['rows'],m['no_trigger'],m['route_ms_measured'])"` 与 `python.exe -c "import json;d=json.load(open(r'06-benchmark/r260_inventory_defect_face.json',encoding='utf-8'));print(d['generated_at'],d['disk_face'])"` |
| 2 | 每件 3–5 个替代候选（社区活跃度/维护状态） | [06-benchmark/quarterly_r260/2026Q4/replacement_matrix.json](06-benchmark/quarterly_r260/2026Q4/replacement_matrix.json)（现行矩阵）＋ [06-benchmark/定向检索复核_r260_2026-10-28.md](06-benchmark/定向检索复核_r260_2026-10-28.md)＋ [06-benchmark/非GitHub社区检索面_r260_2026-10-28.md](06-benchmark/非GitHub社区检索面_r260_2026-10-28.md) | 矩阵 `generated_at = 2026-10-27T17:09:50+00:00` | `python.exe -c "import json;d=json.load(open(r'06-benchmark/quarterly_r260/2026Q4/replacement_matrix.json',encoding='utf-8'));print(d['generated_at'],len(d['rows']))"` |
| 3 | 五维量化矩阵（功能/效率/兼容/文档/社区） | [06-benchmark/r260_local_baseline.json](06-benchmark/r260_local_baseline.json)（本地同尺三态）＋ [06-benchmark/本地同尺基线与compat判别力_r260_2026-10-28.md](06-benchmark/本地同尺基线与compat判别力_r260_2026-10-28.md) ｜ 历史件（182 口径）：[06-benchmark/替代检索与五维评估矩阵_r114_2026-10-18.md](06-benchmark/替代检索与五维评估矩阵_r114_2026-10-18.md) | `2026-10-28T09:13:34+00:00` | `python.exe -c "import json;d=json.load(open(r'06-benchmark/r260_local_baseline.json',encoding='utf-8'));print(d['generated_at'],d['conservation'])"` 再 `python 05-exec/r260_local_baseline.py`（WSL 里 bare `python` 不存在，须用下节解释器绝对路径）（末行期望 `[R260:PASS] 三态守恒 191`） |
| 4 | 分阶段迁移方案（优先级/时间节点/验证标准/回滚预案） | [04-plan/迁移替换方案_r260_日历版.md](04-plan/迁移替换方案_r260_日历版.md)（**带日期里程碑 M1–M7，现行**）＋ [06-benchmark/回滚演练记录_r260_四级全通负控有牙_2026-10-28.md](06-benchmark/回滚演练记录_r260_四级全通负控有牙_2026-10-28.md)＋ [06-benchmark/r260_rollback_drill.json](06-benchmark/r260_rollback_drill.json) ｜ 历史件（182 基数、**一字未改**）：[04-plan/迁移替换方案_r113_2026-10-18.md](04-plan/迁移替换方案_r113_2026-10-18.md)、[04-plan/迁移替换方案_r114_2026-10-18.md](04-plan/迁移替换方案_r114_2026-10-18.md) | 日历版 mtime `2026-10-28T07:43Z`（件内无 `generated_at`，故以 mtime + §0 现读为准） | `python.exe -c "import os,datetime;print(datetime.datetime.utcfromtimestamp(os.path.getmtime(r'04-plan/迁移替换方案_r260_日历版.md')).strftime('%Y-%m-%dT%H:%MZ'))"`；回滚复跑 （脚本内含 checkout/reset ⇒ **本轮禁 git 写，未实跑 = ❌未实测**；四级 4/4 读数引 r260 §7.1；复跑须连 cwd 一起给）（须从工作区根跑，`l2.sh` 判据见 r260 §7.1） |
| 5 | 季度巡检机制 | 判据本体 [05-exec/r113_quarterly_audit.py](05-exec/r113_quarterly_audit.py)＋规范 [04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md](04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md)（其 `:205` 校正注已裁定「182 此后一律以产物现读为准」）＋现行读数 [06-benchmark/quarterly_r260b/2026Q4/audit.json](06-benchmark/quarterly_r260b/2026Q4/audit.json)＋ [06-benchmark/r260_quarterly_silent.json](06-benchmark/r260_quarterly_silent.json) | audit `generated_at = 2026-10-28T15:03:25+0800`（19 步 / `face_ok=true` / `failed_steps=[]`） | `python.exe -c "import json;d=json.load(open(r'06-benchmark/quarterly_r260b/2026Q4/audit.json',encoding='utf-8'));print(d['generated_at'],len(d['steps']),d['face_ok'],d['failed_steps'])"`；**触发器未接线仍为缺口**：`ls .github/workflows/ && grep -c quarterly .github/workflows/*.yml`（**r260 §7.2 当时读数 = 1 件 / 0 命中；本轮 17:50 复跑 = 2 件，`quarterly_audit.yml` 内 quarterly 命中 7 次 ⇒ 触发器已接线**；`git log -1 -- .github/workflows/quarterly_audit.yml` = `12035e5 @2026-10-28 16:12:18 +0800`，晚于 §7.2 的 15:03 读数 ⇒ 按 R241 只在此加校正注、不回写 r260 原文） |
| 6 | 替换后质量提升 ≥30% 且无兼容性问题 | [06-benchmark/全量对标报告_r260_判据四处根因修与两条新常驻门_2026-10-28.md](06-benchmark/全量对标报告_r260_判据四处根因修与两条新常驻门_2026-10-28.md) §8（两种读法并写）＋ [04-plan/要求6验收裁决与收口件_r233_口径B达标口径C不可达_2026-10-25.md](04-plan/要求6验收裁决与收口件_r233_口径B达标口径C不可达_2026-10-25.md)＋ [04-plan/需求6口径对照与决策件_r216_2026-10-25.md](04-plan/需求6口径对照与决策件_r216_2026-10-25.md)＋读数件 [06-benchmark/r260_req6_quality_truth.json](06-benchmark/r260_req6_quality_truth.json) / [06-benchmark/r260_req6_attainability.json](06-benchmark/r260_req6_attainability.json) | truth 件 `2026-10-27T17:02:54+00:00` | `python.exe -c "import json;d=json.load(open(r'06-benchmark/r260_req6_quality_truth.json',encoding='utf-8'));print(d['generated_at'],list(d['faces'].keys())[:6])"` 再 `python 05-exec/r214_req6_attainability.py --selftest`（`rc=1` 即 IMPOSSIBLE 语义 = 该件自身即负向对照） |
| 7 | 四类文档（报告 / 对比表 / 迁移方案 / 维护规范） | 逐轮报告索引 = [memory/readme-benchmark-reports.md](memory/readme-benchmark-reports.md) + 分卷 `part1..part6` + **新增 [part7](memory/readme-benchmark-reports.part7.md)**（r209→r260 + 本轮入口件）＋对比表 [06-benchmark/comparison.md](06-benchmark/comparison.md)＋迁移方案见需求 4＋维护规范见需求 5＋基数口径 [06-benchmark/交付物基数对账_r261_2026-10-28.md](06-benchmark/交付物基数对账_r261_2026-10-28.md) | 本卷 r261（2026-10-28） | `python.exe -c "import glob;print(len(glob.glob(r'06-benchmark/全量对标报告_r*.md')))"`（现读 125）与 `find memory -name "readme-benchmark-reports*.md" -size +4096c | wc -l`（期望 `0`） |

### r321 增补 · 入口可达性维 + 解释器路径校正

> 本节正文按体量治理 R161（`root_doc_max` 16,384B）**整段零改写迁至** [memory/readme-r321-entry-face.md](memory/readme-r321-entry-face.md)。
> 一句话：r320 普查量到新缺陷类「落盘未入口」（624 孤儿 / 4781 KB），r321 复核其中断链 10 条**只有 1 条是真的**、
> 真需逐条补链的下界 259 个（其余 293 个已被目录名覆盖）；同时实测 README 上方「收口门禁」代码块里的
> `C:\Program Files\Python312\python.exe` 本机已不存在（`spawn ENOENT`），改用 venv 3.13.14 或 LibreOffice 3.13.15。
> 交付件句柄与取值命令全在迁移后的分卷里（本文件不抄数，承本节既有口径）。

### 已过期、不得当现状引用的旧件（具名）

| 旧件 | 过期的是**口径**还是**数值** | 为什么不得当现状 |
|---|---|---|
| [03-audit/自建skill优化审计报告.md](03-audit/自建skill优化审计报告.md)（成文 **2026-09-14**） | 口径 + 数值（**103 / 91**） | 该文件 `:4` 的 103/91 是**人工精读面**，无现行产物可复算；91 还带「约」字且与 `:118` 的 `102-11` 自相矛盾。r260 已在其**末尾**追加校正注（`:124` 起），原文按 R241 未改 |
| [00-scope/自建skill清单.md](00-scope/自建skill清单.md)（名册 **2026-09-22**，mtime 09-23） | 名册本体已过期 **36 天**（**150 / 151**） | r260 §5 实测：现盘 191 件里 **45 条从未进这份名册** ⇒ 77/150 两分母源自过期名册；件本身仍是该两个派生分母的唯一来源 ⇒ 只可引作「历史名册」 |
| [04-plan/迁移替换方案_r113_2026-10-18.md](04-plan/迁移替换方案_r113_2026-10-18.md) 与 [04-plan/迁移替换方案_r114_2026-10-18.md](04-plan/迁移替换方案_r114_2026-10-18.md)（**10-18 基数 182**） | 数值（**182**，Oct-18 时点） | 权威面现值 = 191（三条独立通路同值，见对账件 §3 腿 B/D/E）。**182 已被它自己同族的校正注裁定作废**：[后续维护规范_季度巡检机制_r113_2026-10-18.md](04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md) `:205` 原话「此后一律以产物现读为准」⇒ 引 182 当分母 = 违反该注。**两件原文一字未改**（R241 + 本轮禁面），现行版 = [迁移替换方案_r260_日历版.md](04-plan/迁移替换方案_r260_日历版.md) |
| [06-benchmark/需求闭环审计件_r227_七项逐条对照_2026-10-25.md](06-benchmark/需求闭环审计件_r227_七项逐条对照_2026-10-25.md) 与 [04-plan/要求6验收裁决与收口件_r233_口径B达标口径C不可达_2026-10-25.md](04-plan/要求6验收裁决与收口件_r233_口径B达标口径C不可达_2026-10-25.md)（**10-25 数值**） | 数值（`−41.7%` / `90.1%` 等） | 结构（七条需求 ↔ 件）仍可用，数值已被 r260 现读覆盖（口径 B/C 均漂移）⇒ 引用时写明「历史件 @ 2026-10-25」 |
| 本文件「从哪读起」第 3–9 条指向的 r113/r114/r119 件（**Oct-18/Oct-20**） | 数值 | 它们是**入口指路件**、不是最新读数件。r216 / r227 / r233 / r260 / r261 起的全部交付件此前**未挂进本节**（缺陷 ①，实测 `grep -c` 命中 0）⇒ 由本节补口 |

> 基数互斥怎么读：五个数（103/91/150/182/191）**不是同一量的五个值，是五个不同量**（人判自建面 / 真自建估算面 / 三源名册面 / 10-18 权威面 / 现行权威面）。逐条口径、file:line、是否现行、取值命令 = [06-benchmark/交付物基数对账_r261_2026-10-28.md](06-benchmark/交付物基数对账_r261_2026-10-28.md)。
> 自证（判据 + 负向对照，两条均实测）：判据脚本 `_temp/reqmap_r261.py` 的「需求→交付件路径」映射**由本节机器抽取**（正则取表格里非 http 的 md 链接），不另立名册 ⇒ 判据与交付件不会漂移。
> - 正控：`cd 自建skill优化 && export PYTHONPYCACHEPREFIX=/tmp/pycache_r261 && /mnt/c/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe _temp/reqmap_r261.py` ⇒ 实测末行 `RESULT: PASS 7/7`（`rc=0`）
> - 负控（证判据有牙）：`python.exe _temp/reqmap_r261.py --inject memory/readme-benchmark-reports.part99.md` ⇒ 实测 `RESULT: FAIL dead listed: ...` + `rc=1`；第二条 `--inject 06-benchmark/根本不存在_r999.md` 同判红
> - ⚠️ **本轮自曝一处判据缺陷并当场修掉**（D10.2「复跑更绿先怀疑脚本」）：负控最初写成环境变量开关，实测 env 在 WSL→Windows python 互操作下**丢失**（`printenv FOO` 在 bash 里 = `bar`，而 Windows python 读回 `None`）⇒ 负控根本没生效、跑成了假绿 PASS。改走 `argv` 注入后红才显形。教训：**开关要选被检进程真能收到那条通道，跨互操作层的 env 不算**。负控用完即删，仓内不留副本（本文件与对账件即全部写面）

### 复现口径（本轮实测三条环境根因，写给下一个读者）

1. **bare `python.exe` 在本机 WSL 里解析成 `D:''LibreOffice_26.8.1''program''python-core-3.13.15`，不是 managed venv**（实测 `python.exe -c 'import sys;print(sys.executable)'`）。用错解释器跑 `r260_local_baseline.py` 会把 tracked 证据件 `06-benchmark/r260_local_baseline.json` 改写成漂移值（compat 贡献读数 0 → 22）。⇒ 一律显式给绝对路径：WSL 形态 `/mnt/c/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe`／Windows 形态 `C:''Users''37533''.workbuddy''binaries''python''envs''default''Scripts''python.exe`。**本轮那次副作用已按 HEAD blob 逐字节还原**该路径当场复验 `git diff` = 0 字节、`generated_at` 回到 `09:13:34Z`），全程未做 git 写。**但随后又被并发会话改写**（17:55:59Z，非本会话所为）⇒ 我按 #44⑩ **不再 revert 第二次**（该件不在本轮写面白名单），现状与归因见对账件 §8。
2. **任务书给的 `/c/Users/37533/...` 形态在 WSL 下 rc=127**（实测 No such file），须写 `/mnt/c/Users/37533/...`；bare `python` 不存在（`command -v python` 空）。
3. **引号存活规则**：外层双引号包内层双引号会被 bash 吃掉 ⇒ 本文 `python.exe -c "..."` 里的**字典键一律用单引号**。实测反例：写作 `p["face"]` 报 `NameError: name 'face' is not defined`，改 `p['face']` 同一条命令即出数。
