# 03 五维量化对比评估矩阵（需求3）

- 生成时间：`2026-11-06T22:32:27.608615+00:00`；评估日 `EVAL_DATE=2026-11-07`；角色 matrix-analyst / t3。
- 证据状态：候选侧 ✅已实测（本轮现场 `gh api`）；现有侧 ✅已实测（本轮现场文件系统）；质量口径旁证 ⚠️部分实测。
- 只读取证：本轮**未改** `D:/global_skills` 下任何 `SKILL.md` 或源文件；镜像与 `eval/` 只读。R241 历史报告旧数字只加校正注、不改写。
- 禁抄快照：t2 `candidates.json` 的 `metadata.stars` 为 2026-11-06 取值；本轮现场复取漂移实测：rlaope/oh-my-hermes t2=5203 -> live=5204；现场命令 `gh api repos/rlaope/oh-my-hermes --jq '{full_name,stars:.stargazers_count,pushed_at,spdx:(.license.spdx_id // "UNLICENSED"),archived,forks:.forks_count,open_issues:.open_issues_count,default_branch,description}'`。故一律以本轮 `measured_at` 为准，t2 值仅留作漂移对照。

## 1. 评分方法与对象定义

**唯一量尺** = `05-exec/r114_replacement_scan.py:790-863` 的 `score5(m, license_cap=True, use_body=True)`，返回 `(s, sum(s.values()), fc_caliber)`，五维各 0-5 分。本件用 `importlib.util.spec_from_file_location` 直接加载该模块，**不重写锚点**（防主观漂移、防两处实现分叉）。

- 现有件对象 = `D:/global_skills/<slug>/` 子树（150 件，含 LOW/EXCLUDE，分母口径见 §5）；输入由 `r114.tree_counts(paths)` 现场扫描生成，`tree_state=OK`，`stars=0`，`pushed_at` = 该目录最后一次 git 提交日期。
- 候选对象 = GitHub 仓默认分支全树（323 条 `rel=skill` 真替代，去重 147 仓）；输入由现场 `gh api repos/<full>` + `gh api repos/<full>/git/trees/<br>?recursive=1` 生成，`NOASSERTION` 另取 `repos/<full>/license` 正文交 `r114.classify_body()` 归一（R247 双向：取不到留 `None`，不猜宽松也不猜受限）。
- 两侧**同一函数、同一锚点、同一输入构造规则**：`score5` 不认识「本地件」或「候选」，只认识一张 doc。原始 doc 全量落 `_temp/t3_matrix/local_meta.json` / `live_meta.json`，每个分数的 `evidence_handle` 带 doc 的 sha256 前 12 位，可回溯到具体快照。
- 现场取值命令（逐仓，随分给出；字面量见下方代码块，CSV `measurement_command` 列已展开）：`python -B 03_matrix_build.py --show-local <slug>` / `--show-repo <OWNER/REPO>` 可打印任一对象的完整输入 doc。

**字面 jq 表达式（同 05-exec/r114_replacement_scan.py:339-414 的字段面）**：
```
gh api repos/<OWNER>/<REPO> --jq '{full_name,stars:.stargazers_count,pushed_at,spdx:(.license.spdx_id // "UNLICENSED"),archived,forks:.forks_count,open_issues:.open_issues_count,default_branch,description}'
gh api "repos/<OWNER>/<REPO>/git/trees/<br>?recursive=1" --jq '[.truncated, [.tree[] | select(.type=="blob") | .path]]'
gh api repos/<OWNER>/<REPO>/license --jq '{spdx:(.license.spdx_id // ""),content}'  # 仅 NOASSERTION 触发
```

## 2. 五维权重与 0-5 分档锚点（可操作，防主观漂移）

权重取整数、和 = 20，故 `T = SUM(w_d x s_d)` 直接落在 0-100，无需归一化除法。

| 维度 | 权重 | 占比 | 定权理由 |
|---|---:|---:|---|
| 功能完整性 fc | 6 | 30% | 需求①功能边界为替代首要条件；但 fc 由 SKILL.md 计数代理，存在 bundle-scale 盲区（§9），不单独决定迁移 |
| 运行效率 eff | 4 | 20% | 需求①性能；本地仅 26/77 有 r260 路由耗时实测、51/77 NO_TRIGGER，故降权 |
| 兼容性 compat | 4 | 20% | 需求⑥「无兼容性问题」硬约束，与 eff 同权 |
| 文档完善度 docs | 3 | 15% | 迁移可执行性 |
| 社区支持度 community | 3 | 15% | 需求③社区支持度；但使用反馈 99.94% outcome_unknown ⇒ **权重上限 15%**，且只用 GitHub 元数据代理 |

**fc 功能完整性**（`sm = skill_md_exact_n`，缺失时回退 `skill_md_n`；`blob_n` = 对象文件数）：

| 分 | 锚点（可机械判定） |
|---:|---|
| 0 | `sm is None`（树不可用）或 `sm == 0` 且 `blob_n <= 50` |
| 1 | `sm == 0` 且 `blob_n > 50` |
| 2 | `1 <= sm <= 2` |
| 3 | `3 <= sm <= 10` |
| 4 | `11 <= sm <= 100` |
| 5 | `sm > 100` |

**eff 运行效率**（`tn = test_path_n`，`wn = workflow_n`）：`eff = min(5, A + B)`，`A = 0 if tn==0 else min(3, 1 + (tn>20) + (tn>200))`，`B = 0 if wn==0 else min(2, 1 + (wn>3))`。即 0=无测试路径无工作流；1=仅 1..20 测试路径或 1..3 工作流之一；2..5 按两路叠加；`tn>200` 且 `wn>3` 封顶 5。

**compat 兼容性**：`base = (2 if license != UNLICENSED else 0) + (0 if archived else 1) + (2 if sm else 0)`；`compat = min(5, base, LICENSE_CAPS[license_class(license, license_body_class)])`。档位上限 `copyleft=1 / restricted=1 / weak-copyleft=2 / unknown=4 / permissive=5 / none=5`（cap 只降不升；`NOASSERTION` 走正文指纹，R247）。

**docs 文档完善度**（`rn = readme_n`，`dn = docs_md_n`）：`docs = min(5, (2 if rn else 0) + (1 if dn>5 else 0) + (1 if dn>40 else 0) + (1 if tree_state==OK else 0))`。

**community 社区支持度**（`st = stars`，`pushed_at` 取前 10 位日期）：`community = min(5, count(100,1000,10000,50000 : st >= th) + (1 if pushed_at >= 2026-07-01 else 0))`。阈值沿用 r114 内建常量（其 EVAL_DATE=2026-10-28 口径），本轮不改为 2026-11-07 派生值，以保同尺可比。

## 3. unknown / 弱证据的双向中性规则（captain 硬口径）

- **缺陷面 84/150**：`inventory.json` 仅 84 件有逐件 `known_defects`，其余 **66 件** `defects_note`=「未见逐件缺陷记录」。`matrix.csv` 的 `defect_face` 列逐行标 `unknown(not_scored)`；**这 66 件一律不记为「零缺陷/满分」，也不得拿 84 当全量分母外推缺陷率**。
- **规则（双向中性）**：本矩阵**没有任何一维**把缺陷面写进分子或分母 —— 有记录的 84 件不扣分、未记录的 66 件不加分；候选侧同样不因「未见缺陷记录」加分（`defect_face=n/a(candidate)`）。故该规则对旧 skill 与候选**均不单向有利**。若 t4 需要缺陷面结论，须另起逐件取证，不得由本矩阵外推。
- **使用反馈面 = 弱证据**：r289 实测 `outcome_unknown_share_pct=99.94`（`rows_total=3110` / `outcome_known_rows=2`）。**禁**作为「社区支持度」或「运行效率」的实测定分依据；`matrix.csv` 的 `feedback_weight_cap` 列恒为 **0**（权重上限显式落列），仅作 ⚠️部分实测旁证。`r289_never_seen` 不得写成满意度/成功率。
- **r115 四层质量口径**：L1 layered 291 条 Top-1 88.3%（含 63.6% 泄漏题加成 +7.7pp）；L2 frozen 10 条 70.0%（净化 87.5%，n 太小仅哨兵）；L3 污染命中；L4 干净面 = L1+L3 派生。**引用 L1 必须同屏给 L4**。与 r114 A/B 的 38.2% **不可比、禁相减**（生产路由是 `eval/unified_router.py::route()`，r114 的 `hybrid_match()` 只是三方法对照近似实现）。本矩阵**不**把任何质量口径读数写进分数，权重 0、⚠️旁证。
- **r114/r260 A/B 旁证**：`06-benchmark/r260_req6_quality_ab.json` 99 queries，hybrid Top-1 38.2%（Wilson CI 28.8–48.6）；`delta_pp=0.0`、区间重叠(幅度落在抽样抖动内)、`verdict_rule = 区间分离 且 delta_rel_pct>=30 才可写提升>=30%`。**区间重叠禁写「提升」(P1-23)**；Top-1 是路由命中率，不是任务完成好坏。需求⑥的 >=30% 质量提升由 t6 用独立 A/B 验收，本矩阵不代判。
- **目录缺失 4 件**（`cloudbase__skillhub` / `executing-plans` / `pptx` / `slides`）：现场 `test -d` 为 false，5 维记 0 且 `score_status=UNAVAILABLE`、证据 `未实测（目录缺失，0=哨兵不参与排序）`；**不纳入均值/优劣比较**，具名登记为盲区，禁静默丢弃。
- **54 条定向线索 + 44 条族级补位**：t2 `reading_rule` 明示 `rel=family` 补位是族级邻居、`directed_lead` 功能等价 ❌未实测，**禁当替代方案引用** ⇒ 本轮登记但不计分、不进 `matrix.csv`、不进汇总表（§9 列明）。

## 4. 加权总分公式与手算样例

```
T = SUM_d ( w_d x s_d ),  w = (fc=6, eff=4, compat=4, docs=3, community=3), SUM(w) = 20
s_d in [0,5]  =>  T in [0,100];  0-5 等价分 T5 = T / 20
逐行复算：matrix.csv 的 weighted_contribution = weight x score，按 object_id 求和即 T
```

**手算样例**（取自本轮现场值，非硬编码样例）：`cand:9b-lightworkflow::rlaope/oh-my-hermes`

- 功能完整性 (fc)：s=5 x w=6 = 30，累计 30
- 运行效率 (eff)：s=5 x w=4 = 20，累计 50
- 兼容性 (compat)：s=5 x w=4 = 20，累计 70
- 文档完善度 (docs)：s=5 x w=3 = 15，累计 85
- 社区支持度 (community)：s=3 x w=3 = 9，累计 94
- 合计 `T = 94`（0-100），`T5 = 4.7`（0-5）。

## 5. 分母、覆盖面与活跃根现场复算

- 盘点分母 150 = HIGH 51 + MID 26 + LOW 30 + EXCLUDE 43（t1 inventory，captain 已复核：逐件证据 150/150、三条守恒 True、负控报红）；自建维护口径 = HIGH+MID = **77**。
- 本矩阵对象 = 150 件现有 skill + 323 条 `rel=skill` 真替代 = **473** 个对象 x 5 维 = **2365** 行 `matrix.csv`。
- 活跃根现场复算（✅已实测，禁抄 t1 快照）：一级目录 `194`、一级直属 SKILL.md `190`、全深度 SKILL.md（case-sensitive、不跟随 junction）`243`；大小写不敏感 `find -iname skill.md` = `246`（多出的 3 个是小写 skill.md：cloudbase/references/cloudbase-agent/{py,ts}/skill.md、dingtalk-misc/references/skill.md）。
- **247 漂移归因（本轮现场破案）**：Python `os.walk` 跟随 junction `/d/global_skills/rag-eval -> /c/Users/37533/.agents/skills/rag-eval` 且大小写不敏感，读到 247；GNU `find` 默认不跟随 junction 且 `-name` 大小写敏感，读到 243（t1 快照同口径）。两者都是**同一时刻的现场值**，差 4 来自 junction 目标内的 1 个 SKILL.md + 3 个小写 skill.md，**不是活跃根真的又漂移**；按 R269 只登记、不擅动受管源。禁把 243/247 任一值当维护分母（维护分母恒 = 77）。
- 取值命令：`find /d/global_skills -mindepth 1 -maxdepth 1 -type d | wc -l` / `find /d/global_skills -maxdepth 2 -name SKILL.md | wc -l` / `find /d/global_skills -type f -name SKILL.md | wc -l` / `find /d/global_skills -type f -iname skill.md | wc -l`。

## 6. 汇总表（机器可读，03_matrix_check.py 复算对账）

<!-- MATRIX_SUMMARY_BEGIN -->
| object_id | class | fc | eff | compat | docs | community | weighted_total |
|---|---|---:|---:|---:|---:|---:|---:|
| current:9b-lightworkflow | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:A-ask-questions | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:A-get-memory | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:A-java-problem | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:A-memory-start | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:A-project-better | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:A-project-handoff | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:A-prompt-better | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:A-skill-manager | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:agent-browser | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:ai-video-homework-pipeline | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:algorithmic-art | EXCLUDE | 2 | 0 | 5 | 1 | 1 | 38 |
| current:audio-deliverable-pipeline | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:audit-runner-safe-aggregate | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:bigfile-split | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:brainstorming | LOW | 2 | 0 | 5 | 1 | 1 | 38 |
| current:brand-guidelines | EXCLUDE | 2 | 0 | 5 | 1 | 1 | 38 |
| current:browser-cdp | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:byted-bp-cdn-pagesdeploy | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:byted-mediakit-shared | EXCLUDE | 2 | 0 | 5 | 1 | 1 | 38 |
| current:byted-seedance-video-generate | EXCLUDE | 2 | 0 | 5 | 1 | 1 | 38 |
| current:byted-seedream-image-generate | EXCLUDE | 2 | 0 | 5 | 1 | 1 | 38 |
| current:c-cleanup | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:canvas-design | EXCLUDE | 2 | 0 | 5 | 1 | 1 | 38 |
| current:chaoshi-admin-inline-edit | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:chaoshi-image-optimization | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:chaoshi-web-deploy | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:chart-visualization | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:cloudbase-db-optimize | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:cloudbase__skillhub | EXCLUDE | 0 | 0 | 0 | 0 | 0 | 0 |
| current:code-review | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:coding-agent | LOW | 2 | 0 | 5 | 1 | 1 | 38 |
| current:computer-use-guidance-windows | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:consulting-analysis | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:cross-platform-agent-sync | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:data-analysis | LOW | 2 | 0 | 5 | 1 | 1 | 38 |
| current:data-visualization | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:debugging-fixing | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:defuddle | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:diagram-maker | LOW | 2 | 0 | 5 | 1 | 1 | 38 |
| current:discover-agent-cli | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:doc-coauthoring | LOW | 2 | 0 | 4 | 1 | 1 | 34 |
| current:docx | EXCLUDE | 2 | 0 | 4 | 1 | 1 | 34 |
| current:dogfood | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:electron | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:elon-musk-perspective | EXCLUDE | 2 | 0 | 5 | 3 | 1 | 44 |
| current:executing-plans | LOW | 0 | 0 | 0 | 0 | 0 | 0 |
| current:fenjue-lessons-hitrate | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:fenjue-memory-audit | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:figma | EXCLUDE | 2 | 0 | 4 | 1 | 1 | 34 |
| current:find-skills | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:first-principles-decomposer | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:frontend-design | EXCLUDE | 2 | 0 | 5 | 1 | 1 | 38 |
| current:frontend-skill | EXCLUDE | 2 | 0 | 5 | 1 | 1 | 38 |
| current:frontend-slides | EXCLUDE | 2 | 0 | 5 | 3 | 1 | 44 |
| current:github | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:gsap | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:gstack | EXCLUDE | 4 | 3 | 5 | 3 | 1 | 68 |
| current:hermes-installer | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:hook-analyzer-skill | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:html-ppt | EXCLUDE | 2 | 0 | 5 | 3 | 1 | 44 |
| current:html-to-docx-win-fix | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:hyperframes | LOW | 2 | 0 | 5 | 1 | 1 | 38 |
| current:hyperframes-cli | LOW | 2 | 0 | 5 | 1 | 1 | 38 |
| current:hyperframes-media | LOW | 2 | 0 | 5 | 1 | 1 | 38 |
| current:hyperframes-registry | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:ican-deploy | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:ican-frontend-design-system | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:internal-comms | EXCLUDE | 2 | 0 | 5 | 1 | 1 | 38 |
| current:json-canvas | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:knowledge-capture | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:local-asr | MID | 2 | 1 | 3 | 1 | 1 | 34 |
| current:local-computer-use | MID | 2 | 1 | 3 | 1 | 1 | 34 |
| current:local-img2img | MID | 2 | 1 | 3 | 1 | 1 | 34 |
| current:local-mineru | MID | 2 | 1 | 3 | 1 | 1 | 34 |
| current:local-ocr-npu | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:local-realtime-translator | MID | 2 | 1 | 3 | 1 | 1 | 34 |
| current:local-screenshot-qa | MID | 2 | 1 | 3 | 1 | 1 | 34 |
| current:local-tts | MID | 2 | 1 | 3 | 1 | 1 | 34 |
| current:local-txt2img | MID | 2 | 1 | 3 | 1 | 1 | 34 |
| current:local-vram | MID | 2 | 1 | 3 | 1 | 1 | 34 |
| current:mcporter | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:meeting-intelligence | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:nano-pdf | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:node-inspect-debugger | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:notion-cli | EXCLUDE | 2 | 0 | 5 | 1 | 1 | 38 |
| current:obsidian-bases | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:obsidian-cli | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:obsidian-markdown | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:oc-dispatch-exec-guard | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:office-automation-pro | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:openai-whisper-api | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:openclaw-dual-gate-quality-audit | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:openclaw-fenjue-weekly | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:openclaw-task-supervision | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:oracle | EXCLUDE | 2 | 0 | 5 | 1 | 1 | 38 |
| current:pdf | EXCLUDE | 2 | 0 | 4 | 1 | 1 | 34 |
| current:pixelle-api-ensure | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:pptx | EXCLUDE | 0 | 0 | 0 | 0 | 0 | 0 |
| current:prompt-consolidation | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:prompt-system-audit | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:python-debugpy | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:refactoring | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:report-generator-skill | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:research-documentation | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:screenshot | EXCLUDE | 2 | 0 | 5 | 1 | 1 | 38 |
| current:shadcn | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:shell-encoding-pitfalls | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:slides | EXCLUDE | 0 | 0 | 0 | 0 | 0 | 0 |
| current:spec-to-implementation | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:spike | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:sq-cleanmgr-c | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:static-site-batch-audit-fix | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:story | LOW | 2 | 0 | 5 | 1 | 1 | 38 |
| current:story-cover | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:story-deslop | HIGH | 2 | 0 | 5 | 1 | 1 | 38 |
| current:story-import | HIGH | 2 | 0 | 5 | 1 | 1 | 38 |
| current:story-long-analyze | HIGH | 2 | 0 | 5 | 1 | 1 | 38 |
| current:story-long-write | HIGH | 2 | 0 | 5 | 1 | 1 | 38 |
| current:story-review | HIGH | 2 | 0 | 5 | 1 | 1 | 38 |
| current:story-scan | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:story-setup | HIGH | 2 | 0 | 5 | 1 | 1 | 38 |
| current:story-short-analyze | HIGH | 2 | 0 | 5 | 1 | 1 | 38 |
| current:story-short-write | HIGH | 2 | 0 | 5 | 1 | 1 | 38 |
| current:taskflow | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:taskflow-inbox-triage | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:test-driven-development | LOW | 2 | 0 | 5 | 1 | 1 | 38 |
| current:testing | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:theme-factory | EXCLUDE | 2 | 0 | 5 | 1 | 1 | 38 |
| current:ui-ux-pro-max | EXCLUDE | 2 | 2 | 5 | 1 | 1 | 46 |
| current:utf8-encoding-fix | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:video-breakdown-skill | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:video-frames | EXCLUDE | 2 | 0 | 3 | 1 | 1 | 30 |
| current:video-whisper-transcribe | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:vp-perspective-audit | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:wb-git-commit-recipe | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:web-design-guidelines | LOW | 2 | 0 | 3 | 1 | 1 | 30 |
| current:wechat-automation | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:wechat-voice-transcription | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:win-toolchain-pitfalls | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| current:windows-bash-cli-interop-pitfalls | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:windows-cli-utf8-wrapper | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:windows-gitbash-chinese-path-pit | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:windows-native-ocr | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:workbuddy-mcp | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:workflow-preflight-check | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:wps-knowledgebase | HIGH | 2 | 0 | 3 | 1 | 1 | 30 |
| current:writing-plans | LOW | 2 | 0 | 5 | 1 | 1 | 38 |
| current:xlsx | EXCLUDE | 2 | 0 | 4 | 1 | 1 | 34 |
| current:天眼一下 | MID | 2 | 0 | 3 | 1 | 1 | 30 |
| cand:9b-lightworkflow::rlaope/oh-my-hermes | HIGH | 5 | 5 | 5 | 5 | 3 | 94 |
| cand:9b-lightworkflow::Devin-AXIS/iPolloWork | HIGH | 5 | 5 | 1 | 4 | 3 | 75 |
| cand:9b-lightworkflow::lennney/stop-that-shit | HIGH | 3 | 3 | 5 | 3 | 3 | 68 |
| cand:A-get-memory::affaan-m/ECC | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:A-get-memory::ruvnet/ruflo | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:A-get-memory::mksglu/context-mode | HIGH | 4 | 4 | 1 | 5 | 4 | 71 |
| cand:A-get-memory::muratcankoylan/Agent-Skills-for-Context-Engineering | HIGH | 4 | 2 | 5 | 4 | 4 | 76 |
| cand:A-get-memory::TencentCloud/TencentDB-Agent-Memory | HIGH | 2 | 2 | 5 | 3 | 4 | 61 |
| cand:A-java-problem::SeleniumHQ/selenium | HIGH | 1 | 5 | 3 | 4 | 4 | 62 |
| cand:A-java-problem::ComposioHQ/awesome-claude-skills | HIGH | 5 | 1 | 3 | 3 | 5 | 70 |
| cand:A-java-problem::Snailclimb/JavaGuide | HIGH | 1 | 1 | 3 | 5 | 5 | 52 |
| cand:A-java-problem::composio-community/awesome-codex-skills | HIGH | 5 | 0 | 3 | 3 | 4 | 63 |
| cand:A-java-problem::jeecgboot/JeecgBoot | HIGH | 1 | 2 | 3 | 3 | 4 | 47 |
| cand:A-memory-start::affaan-m/ECC | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:A-memory-start::ruvnet/ruflo | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:A-memory-start::mksglu/context-mode | HIGH | 4 | 4 | 1 | 5 | 4 | 71 |
| cand:A-memory-start::muratcankoylan/Agent-Skills-for-Context-Engineering | HIGH | 4 | 2 | 5 | 4 | 4 | 76 |
| cand:A-memory-start::TencentCloud/TencentDB-Agent-Memory | HIGH | 2 | 2 | 5 | 3 | 4 | 61 |
| cand:A-project-better::affaan-m/ECC | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:A-project-better::nexu-io/open-design | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:A-project-better::ruvnet/ruflo | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:A-project-better::latent-spaces/brag | HIGH | 2 | 0 | 5 | 3 | 4 | 53 |
| cand:A-project-better::nicobailon/visual-explainer | HIGH | 2 | 0 | 5 | 3 | 4 | 53 |
| cand:A-project-handoff::affaan-m/ECC | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:A-project-handoff::ruvnet/ruflo | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:A-project-handoff::mksglu/context-mode | HIGH | 4 | 4 | 1 | 5 | 4 | 71 |
| cand:A-project-handoff::muratcankoylan/Agent-Skills-for-Context-Engineering | HIGH | 4 | 2 | 5 | 4 | 4 | 76 |
| cand:A-project-handoff::TencentCloud/TencentDB-Agent-Memory | HIGH | 2 | 2 | 5 | 3 | 4 | 61 |
| cand:A-prompt-better::JuliusBrussee/caveman | HIGH | 4 | 5 | 5 | 4 | 5 | 91 |
| cand:A-prompt-better::github/awesome-copilot | HIGH | 5 | 4 | 5 | 4 | 4 | 90 |
| cand:A-prompt-better::NVIDIA/SkillSpector | HIGH | 4 | 5 | 5 | 4 | 4 | 88 |
| cand:A-prompt-better::DietrichGebert/ponytail | HIGH | 4 | 3 | 5 | 3 | 5 | 80 |
| cand:A-prompt-better::nidhinjs/prompt-master | HIGH | 2 | 0 | 5 | 3 | 4 | 53 |
| cand:A-skill-manager::affaan-m/ECC | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:A-skill-manager::ruvnet/ruflo | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:A-skill-manager::thedotmack/claude-mem | HIGH | 4 | 5 | 5 | 5 | 5 | 94 |
| cand:A-skill-manager::topoteretes/cognee | HIGH | 4 | 5 | 5 | 4 | 4 | 88 |
| cand:A-skill-manager::MemTensor/MemOS | HIGH | 3 | 5 | 5 | 5 | 4 | 85 |
| cand:agent-browser::vercel-labs/agent-browser | MID | 4 | 3 | 5 | 3 | 4 | 77 |
| cand:agent-browser::browser-act/skills | MID | 5 | 1 | 5 | 4 | 3 | 75 |
| cand:agent-browser::browser-use/browser-harness | MID | 3 | 2 | 5 | 3 | 4 | 67 |
| cand:agent-browser::mxschmitt/playwright-go | MID | 2 | 4 | 5 | 3 | 3 | 66 |
| cand:agent-browser::SawyerHood/dev-browser | MID | 2 | 3 | 5 | 3 | 3 | 62 |
| cand:audio-deliverable-pipeline::scenario-labs/skills | MID | 5 | 5 | 5 | 4 | 3 | 91 |
| cand:audio-deliverable-pipeline::wiltodelta/remove-ai-watermarks | MID | 3 | 4 | 5 | 5 | 3 | 78 |
| cand:audio-deliverable-pipeline::LnYo-Cly/ai4j | MID | 3 | 5 | 5 | 4 | 2 | 76 |
| cand:audio-deliverable-pipeline::EGSECDA/vocaloid-style-mv-pipeline | MID | 2 | 0 | 5 | 3 | 2 | 47 |
| cand:audio-deliverable-pipeline::equalang/equalang-skill | MID | 2 | 1 | 5 | 3 | 1 | 48 |
| cand:audit-runner-safe-aggregate::JuliusBrussee/caveman | HIGH | 4 | 5 | 5 | 4 | 5 | 91 |
| cand:audit-runner-safe-aggregate::muratcankoylan/Agent-Skills-for-Context-Engineering | HIGH | 4 | 2 | 5 | 4 | 4 | 76 |
| cand:audit-runner-safe-aggregate::webdriverio/webdriverio | HIGH | 3 | 5 | 5 | 3 | 3 | 76 |
| cand:audit-runner-safe-aggregate::DeusData/codebase-memory-mcp | HIGH | 1 | 5 | 3 | 4 | 4 | 62 |
| cand:audit-runner-safe-aggregate::cloudflare/security-audit-skill | HIGH | 2 | 0 | 5 | 3 | 5 | 56 |
| cand:bigfile-split::wanshuiyin/Auto-claude-code-research-in-sleep | HIGH | 5 | 4 | 5 | 5 | 4 | 93 |
| cand:bigfile-split::EverMind-AI/EverOS | HIGH | 3 | 5 | 5 | 4 | 4 | 82 |
| cand:bigfile-split::genspark-ai/genoffice | HIGH | 4 | 4 | 5 | 4 | 4 | 84 |
| cand:bigfile-split::OthmanAdi/planning-with-files | HIGH | 4 | 3 | 5 | 4 | 4 | 80 |
| cand:bigfile-split::AgriciDaniel/claude-obsidian | HIGH | 4 | 3 | 5 | 4 | 4 | 80 |
| cand:c-cleanup::OrchestratorInc/agent-orchestrator | HIGH | 4 | 4 | 5 | 5 | 4 | 87 |
| cand:c-cleanup::parcadei/Continuous-Claude-v3 | HIGH | 5 | 2 | 5 | 4 | 2 | 76 |
| cand:c-cleanup::xpf0000/FlyEnv | HIGH | 2 | 3 | 5 | 5 | 3 | 68 |
| cand:c-cleanup::CursorTouch/Windows-MCP | HIGH | 2 | 3 | 5 | 3 | 4 | 65 |
| cand:c-cleanup::sixtysevenlf/dsh-blender-plugin | HIGH | 2 | 4 | 5 | 4 | 3 | 69 |
| cand:chaoshi-image-optimization::ruvnet/ruflo | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:chaoshi-image-optimization::langgenius/dify | HIGH | 3 | 5 | 1 | 5 | 5 | 72 |
| cand:chaoshi-image-optimization::Leonxlnx/taste-skill | HIGH | 2 | 2 | 5 | 3 | 5 | 64 |
| cand:chaoshi-image-optimization::homarr-labs/dashboard-icons | HIGH | 1 | 4 | 3 | 3 | 3 | 52 |
| cand:chaoshi-image-optimization::level09/enferno | HIGH | 2 | 2 | 5 | 3 | 2 | 55 |
| cand:chaoshi-web-deploy::ruvnet/ruflo | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:chaoshi-web-deploy::iflytek/skillhub | HIGH | 4 | 5 | 5 | 5 | 3 | 88 |
| cand:chaoshi-web-deploy::agentscope-ai/QwenPaw | HIGH | 4 | 5 | 5 | 3 | 4 | 85 |
| cand:chaoshi-web-deploy::langgenius/dify | HIGH | 3 | 5 | 1 | 5 | 5 | 72 |
| cand:chaoshi-web-deploy::glitternetwork/pinme | HIGH | 3 | 3 | 5 | 3 | 3 | 68 |
| cand:code-review::wanshuiyin/Auto-claude-code-research-in-sleep | HIGH | 5 | 4 | 5 | 5 | 4 | 93 |
| cand:code-review::tirth8205/code-review-graph | HIGH | 3 | 5 | 5 | 4 | 4 | 82 |
| cand:code-review::alibaba/open-code-review | HIGH | 3 | 4 | 5 | 4 | 4 | 78 |
| cand:code-review::code-yeongyu/oh-my-openagent | HIGH | 4 | 5 | 1 | 5 | 5 | 78 |
| cand:code-review::CherryHQ/cherry-studio | HIGH | 4 | 5 | 1 | 5 | 5 | 78 |
| cand:cross-platform-agent-sync::wanshuiyin/Auto-claude-code-research-in-sleep | HIGH | 5 | 4 | 5 | 5 | 4 | 93 |
| cand:cross-platform-agent-sync::topoteretes/cognee | HIGH | 4 | 5 | 5 | 4 | 4 | 88 |
| cand:cross-platform-agent-sync::MemTensor/MemOS | HIGH | 3 | 5 | 5 | 5 | 4 | 85 |
| cand:cross-platform-agent-sync::alibaba/nacos | HIGH | 2 | 5 | 5 | 3 | 4 | 73 |
| cand:cross-platform-agent-sync::Agents365-ai/drawio-skill | HIGH | 2 | 2 | 5 | 4 | 4 | 64 |
| cand:debugging-fixing::ruvnet/ruflo | MID | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:debugging-fixing::morluto/rea | MID | 3 | 5 | 5 | 5 | 5 | 88 |
| cand:debugging-fixing::JuliusBrussee/caveman | MID | 4 | 5 | 5 | 4 | 5 | 91 |
| cand:debugging-fixing::rtk-ai/rtk | MID | 4 | 5 | 5 | 4 | 5 | 91 |
| cand:debugging-fixing::muratcankoylan/Agent-Skills-for-Context-Engineering | MID | 4 | 2 | 5 | 4 | 4 | 76 |
| cand:discover-agent-cli::ThinkInAIXYZ/deepchat | MID | 4 | 5 | 5 | 5 | 3 | 88 |
| cand:discover-agent-cli::NanmiCoder/cc-haha | MID | 3 | 5 | 1 | 5 | 4 | 69 |
| cand:discover-agent-cli::DayuanJiang/next-ai-draw-io | MID | 1 | 4 | 3 | 5 | 4 | 61 |
| cand:discover-agent-cli::op7418/CodePilot | MID | 3 | 5 | 1 | 5 | 3 | 66 |
| cand:discover-agent-cli::opensumi/core | MID | 1 | 5 | 3 | 3 | 3 | 56 |
| cand:fenjue-memory-audit::affaan-m/ECC | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:fenjue-memory-audit::mksglu/context-mode | HIGH | 4 | 4 | 1 | 5 | 4 | 71 |
| cand:fenjue-memory-audit::muratcankoylan/Agent-Skills-for-Context-Engineering | HIGH | 4 | 2 | 5 | 4 | 4 | 76 |
| cand:fenjue-memory-audit::TencentCloud/TencentDB-Agent-Memory | HIGH | 2 | 2 | 5 | 3 | 4 | 61 |
| cand:fenjue-memory-audit::cloudflare/security-audit-skill | HIGH | 2 | 0 | 5 | 3 | 5 | 56 |
| cand:hermes-installer::rlaope/oh-my-hermes | HIGH | 5 | 5 | 5 | 5 | 3 | 94 |
| cand:hermes-installer::Devin-AXIS/iPolloWork | HIGH | 5 | 5 | 1 | 4 | 3 | 75 |
| cand:hermes-installer::lennney/stop-that-shit | HIGH | 3 | 3 | 5 | 3 | 3 | 68 |
| cand:hook-analyzer-skill::xberg-io/xberg | MID | 4 | 5 | 5 | 3 | 3 | 82 |
| cand:hook-analyzer-skill::wiltodelta/remove-ai-watermarks | MID | 3 | 4 | 5 | 5 | 3 | 78 |
| cand:hook-analyzer-skill::EL4CTEO/blender-skills | MID | 4 | 3 | 5 | 3 | 2 | 71 |
| cand:hook-analyzer-skill::RobLe3/cc-blender-skill | MID | 4 | 1 | 5 | 4 | 2 | 66 |
| cand:hook-analyzer-skill::liustack/modlens | MID | 2 | 1 | 5 | 4 | 3 | 57 |
| cand:html-to-docx-win-fix::genspark-ai/genoffice | MID | 4 | 4 | 5 | 4 | 4 | 84 |
| cand:html-to-docx-win-fix::bowenliang123/markdown-exporter | MID | 2 | 3 | 5 | 3 | 2 | 59 |
| cand:html-to-docx-win-fix::appautomaton/document-SKILLs | MID | 3 | 2 | 5 | 3 | 2 | 61 |
| cand:html-to-docx-win-fix::Gostyan/docx-skill-4-cn-paper | MID | 2 | 0 | 5 | 3 | 2 | 47 |
| cand:html-to-docx-win-fix::LegalRabbit-AI/legalrabbit-docx-mcp | MID | 2 | 1 | 5 | 3 | 1 | 48 |
| cand:ican-deploy::ruvnet/ruflo | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:ican-deploy::iflytek/skillhub | HIGH | 4 | 5 | 5 | 5 | 3 | 88 |
| cand:ican-deploy::agentscope-ai/QwenPaw | HIGH | 4 | 5 | 5 | 3 | 4 | 85 |
| cand:ican-deploy::langgenius/dify | HIGH | 3 | 5 | 1 | 5 | 5 | 72 |
| cand:ican-deploy::glitternetwork/pinme | HIGH | 3 | 3 | 5 | 3 | 3 | 68 |
| cand:ican-frontend-design-system::nexu-io/open-design | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:ican-frontend-design-system::Manavarya09/design-extract | HIGH | 4 | 4 | 5 | 4 | 3 | 81 |
| cand:ican-frontend-design-system::asgeirtj/system_prompts_leaks | HIGH | 5 | 0 | 5 | 3 | 5 | 74 |
| cand:ican-frontend-design-system::cathrynlavery/diagram-design | HIGH | 2 | 2 | 5 | 4 | 5 | 67 |
| cand:ican-frontend-design-system::Leonxlnx/taste-skill | HIGH | 2 | 2 | 5 | 3 | 5 | 64 |
| cand:local-asr::nexu-io/open-design | MID | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:local-asr::openclaw/Peekaboo | MID | 3 | 5 | 5 | 5 | 3 | 82 |
| cand:local-asr::SharpAI/DeepCamera | MID | 4 | 3 | 5 | 4 | 3 | 77 |
| cand:local-asr::equalang/equalang-skill | MID | 2 | 1 | 5 | 3 | 1 | 48 |
| cand:local-asr::shaom/brand-to-design-md-skill | MID | 2 | 0 | 3 | 3 | 2 | 39 |
| cand:local-computer-use::feder-cr/invisible_dots | MID | 2 | 4 | 5 | 4 | 1 | 63 |
| cand:local-computer-use::NanmiCoder/cc-haha | MID | 3 | 5 | 1 | 5 | 4 | 69 |
| cand:local-computer-use::feder-cr/invisible_playwright_mcp | MID | 2 | 4 | 5 | 5 | 2 | 69 |
| cand:local-computer-use::browser-use/browser-harness | MID | 3 | 2 | 5 | 3 | 4 | 67 |
| cand:local-computer-use::CursorTouch/Windows-MCP | MID | 2 | 3 | 5 | 3 | 4 | 65 |
| cand:local-img2img::nexu-io/open-design | MID | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:local-img2img::openclaw/Peekaboo | MID | 3 | 5 | 5 | 5 | 3 | 82 |
| cand:local-img2img::SharpAI/DeepCamera | MID | 4 | 3 | 5 | 4 | 3 | 77 |
| cand:local-img2img::DeusData/codebase-memory-mcp | MID | 1 | 5 | 3 | 4 | 4 | 62 |
| cand:local-img2img::shaom/brand-to-design-md-skill | MID | 2 | 0 | 3 | 3 | 2 | 39 |
| cand:local-mineru::nexu-io/open-design | MID | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:local-mineru::openclaw/Peekaboo | MID | 3 | 5 | 5 | 5 | 3 | 82 |
| cand:local-mineru::SharpAI/DeepCamera | MID | 4 | 3 | 5 | 4 | 3 | 77 |
| cand:local-mineru::DeusData/codebase-memory-mcp | MID | 1 | 5 | 3 | 4 | 4 | 62 |
| cand:local-mineru::shaom/brand-to-design-md-skill | MID | 2 | 0 | 3 | 3 | 2 | 39 |
| cand:local-ocr-npu::nexu-io/open-design | MID | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:local-ocr-npu::openclaw/Peekaboo | MID | 3 | 5 | 5 | 5 | 3 | 82 |
| cand:local-ocr-npu::SharpAI/DeepCamera | MID | 4 | 3 | 5 | 4 | 3 | 77 |
| cand:local-ocr-npu::Anionex/agent-vision-toolkit | MID | 2 | 3 | 5 | 3 | 3 | 62 |
| cand:local-ocr-npu::liustack/modlens | MID | 2 | 1 | 5 | 4 | 3 | 57 |
| cand:local-realtime-translator::nexu-io/open-design | MID | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:local-realtime-translator::sickn33/agentic-awesome-skills | MID | 5 | 5 | 5 | 5 | 4 | 97 |
| cand:local-realtime-translator::Graphify-Labs/graphify | MID | 2 | 5 | 5 | 4 | 5 | 79 |
| cand:local-realtime-translator::tirth8205/code-review-graph | MID | 3 | 5 | 5 | 4 | 4 | 82 |
| cand:local-realtime-translator::AgriciDaniel/claude-seo | MID | 4 | 3 | 5 | 4 | 4 | 80 |
| cand:local-screenshot-qa::maziyarpanahi/openmed | MID | 4 | 5 | 5 | 5 | 3 | 88 |
| cand:local-screenshot-qa::openclaw/Peekaboo | MID | 3 | 5 | 5 | 5 | 3 | 82 |
| cand:local-screenshot-qa::siddsachar/row-bot | MID | 4 | 5 | 5 | 4 | 3 | 85 |
| cand:local-screenshot-qa::AgriciDaniel/claude-seo | MID | 4 | 3 | 5 | 4 | 4 | 80 |
| cand:local-screenshot-qa::NanmiCoder/cc-haha | MID | 3 | 5 | 1 | 5 | 4 | 69 |
| cand:local-tts::nexu-io/open-design | MID | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:local-tts::krillinai/OpenCreator | MID | 4 | 4 | 5 | 5 | 4 | 87 |
| cand:local-tts::openclaw/Peekaboo | MID | 3 | 5 | 5 | 5 | 3 | 82 |
| cand:local-tts::SharpAI/DeepCamera | MID | 4 | 3 | 5 | 4 | 3 | 77 |
| cand:local-tts::equalang/equalang-skill | MID | 2 | 1 | 5 | 3 | 1 | 48 |
| cand:local-txt2img::nexu-io/open-design | MID | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:local-txt2img::openclaw/Peekaboo | MID | 3 | 5 | 5 | 5 | 3 | 82 |
| cand:local-txt2img::SharpAI/DeepCamera | MID | 4 | 3 | 5 | 4 | 3 | 77 |
| cand:local-txt2img::DeusData/codebase-memory-mcp | MID | 1 | 5 | 3 | 4 | 4 | 62 |
| cand:local-txt2img::shaom/brand-to-design-md-skill | MID | 2 | 0 | 3 | 3 | 2 | 39 |
| cand:local-vram::nexu-io/open-design | MID | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:local-vram::ruvnet/ruflo | MID | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:local-vram::xerj-org/xerj | MID | 3 | 5 | 5 | 5 | 4 | 85 |
| cand:local-vram::EverMind-AI/EverOS | MID | 3 | 5 | 5 | 4 | 4 | 82 |
| cand:local-vram::TencentCloud/TencentDB-Agent-Memory | MID | 2 | 2 | 5 | 3 | 4 | 61 |
| cand:oc-dispatch-exec-guard::affaan-m/ECC | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:oc-dispatch-exec-guard::ruvnet/ruflo | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:oc-dispatch-exec-guard::thedotmack/claude-mem | HIGH | 4 | 5 | 5 | 5 | 5 | 94 |
| cand:oc-dispatch-exec-guard::JuliusBrussee/caveman | HIGH | 4 | 5 | 5 | 4 | 5 | 91 |
| cand:oc-dispatch-exec-guard::mvanhorn/last30days-skill | HIGH | 2 | 5 | 5 | 4 | 5 | 79 |
| cand:office-automation-pro::yusufkaraaslan/Skill_Seekers | MID | 4 | 5 | 5 | 5 | 4 | 91 |
| cand:office-automation-pro::genspark-ai/genoffice | MID | 4 | 4 | 5 | 4 | 4 | 84 |
| cand:office-automation-pro::OpenSenseNova/SenseNova-Skills | MID | 4 | 2 | 5 | 4 | 3 | 73 |
| cand:office-automation-pro::iOfficeAI/OfficeCLI | MID | 4 | 2 | 5 | 3 | 4 | 73 |
| cand:office-automation-pro::tfriedel/claude-office-skills | MID | 3 | 0 | 3 | 3 | 1 | 42 |
| cand:openclaw-dual-gate-quality-audit::thedotmack/claude-mem | HIGH | 4 | 5 | 5 | 5 | 5 | 94 |
| cand:openclaw-dual-gate-quality-audit::wanshuiyin/Auto-claude-code-research-in-sleep | HIGH | 5 | 4 | 5 | 5 | 4 | 93 |
| cand:openclaw-dual-gate-quality-audit::iOfficeAI/AionUi | HIGH | 3 | 5 | 5 | 5 | 4 | 85 |
| cand:openclaw-dual-gate-quality-audit::mvanhorn/last30days-skill | HIGH | 2 | 5 | 5 | 4 | 5 | 79 |
| cand:openclaw-dual-gate-quality-audit::cloudflare/security-audit-skill | HIGH | 2 | 0 | 5 | 3 | 5 | 56 |
| cand:openclaw-fenjue-weekly::thedotmack/claude-mem | HIGH | 4 | 5 | 5 | 5 | 5 | 94 |
| cand:openclaw-fenjue-weekly::wanshuiyin/Auto-claude-code-research-in-sleep | HIGH | 5 | 4 | 5 | 5 | 4 | 93 |
| cand:openclaw-fenjue-weekly::iOfficeAI/AionUi | HIGH | 3 | 5 | 5 | 5 | 4 | 85 |
| cand:openclaw-fenjue-weekly::mvanhorn/last30days-skill | HIGH | 2 | 5 | 5 | 4 | 5 | 79 |
| cand:openclaw-fenjue-weekly::nanocoai/nanoclaw | HIGH | 4 | 3 | 5 | 4 | 4 | 80 |
| cand:openclaw-task-supervision::thedotmack/claude-mem | HIGH | 4 | 5 | 5 | 5 | 5 | 94 |
| cand:openclaw-task-supervision::wanshuiyin/Auto-claude-code-research-in-sleep | HIGH | 5 | 4 | 5 | 5 | 4 | 93 |
| cand:openclaw-task-supervision::iOfficeAI/AionUi | HIGH | 3 | 5 | 5 | 5 | 4 | 85 |
| cand:openclaw-task-supervision::OrchestratorInc/agent-orchestrator | HIGH | 4 | 4 | 5 | 5 | 4 | 87 |
| cand:openclaw-task-supervision::mvanhorn/last30days-skill | HIGH | 2 | 5 | 5 | 4 | 5 | 79 |
| cand:prompt-consolidation::zenstory-ai/drama-skills | HIGH | 4 | 4 | 5 | 4 | 3 | 81 |
| cand:prompt-consolidation::Imbad0202/academic-research-skills | HIGH | 3 | 5 | 1 | 5 | 5 | 72 |
| cand:prompt-consolidation::blader/humanizer | HIGH | 2 | 1 | 5 | 3 | 5 | 60 |
| cand:prompt-consolidation::conorbronsdon/avoid-ai-writing | HIGH | 3 | 2 | 5 | 3 | 3 | 64 |
| cand:prompt-consolidation::Nanako0129/sepia | HIGH | 3 | 2 | 5 | 3 | 3 | 64 |
| cand:prompt-system-audit::Ar9av/obsidian-wiki | HIGH | 4 | 4 | 5 | 4 | 3 | 81 |
| cand:prompt-system-audit::zenstory-ai/drama-skills | HIGH | 4 | 4 | 5 | 4 | 3 | 81 |
| cand:prompt-system-audit::Imbad0202/academic-research-skills | HIGH | 3 | 5 | 1 | 5 | 5 | 72 |
| cand:prompt-system-audit::blader/humanizer | HIGH | 2 | 1 | 5 | 3 | 5 | 60 |
| cand:prompt-system-audit::conorbronsdon/avoid-ai-writing | HIGH | 3 | 2 | 5 | 3 | 3 | 64 |
| cand:report-generator-skill::kangarooking/cangjie-skill | MID | 4 | 3 | 5 | 4 | 4 | 80 |
| cand:report-generator-skill::wiltodelta/remove-ai-watermarks | MID | 3 | 4 | 5 | 5 | 3 | 78 |
| cand:report-generator-skill::ningzimu/codex-ppt-skill | MID | 2 | 3 | 5 | 4 | 3 | 65 |
| cand:report-generator-skill::Akxan/ppt-agent-skill | MID | 2 | 1 | 5 | 3 | 1 | 48 |
| cand:report-generator-skill::chuspeeism/dashi-ppt-skill | MID | 2 | 0 | 1 | 3 | 4 | 37 |
| cand:shell-encoding-pitfalls::siddsachar/row-bot | MID | 4 | 5 | 5 | 4 | 3 | 85 |
| cand:shell-encoding-pitfalls::mksglu/context-mode | MID | 4 | 4 | 1 | 5 | 4 | 71 |
| cand:shell-encoding-pitfalls::Tencent/BrowserSkill | MID | 3 | 5 | 5 | 4 | 4 | 82 |
| cand:shell-encoding-pitfalls::SnailSploit/Claude-Red | MID | 4 | 2 | 5 | 3 | 4 | 73 |
| cand:shell-encoding-pitfalls::openclaw/lobster | MID | 2 | 4 | 5 | 3 | 3 | 66 |
| cand:static-site-batch-audit-fix::heygen-com/hyperframes | HIGH | 4 | 5 | 5 | 4 | 5 | 91 |
| cand:static-site-batch-audit-fix::tirth8205/code-review-graph | HIGH | 3 | 5 | 5 | 4 | 4 | 82 |
| cand:static-site-batch-audit-fix::samugit83/redamon | HIGH | 4 | 3 | 5 | 5 | 3 | 80 |
| cand:static-site-batch-audit-fix::glitternetwork/pinme | HIGH | 3 | 3 | 5 | 3 | 3 | 68 |
| cand:static-site-batch-audit-fix::Jakeschincariol/replica-skill | HIGH | 4 | 1 | 5 | 3 | 3 | 66 |
| cand:story-cover::krillinai/OpenCreator | HIGH | 4 | 4 | 5 | 5 | 4 | 87 |
| cand:story-cover::wiltodelta/remove-ai-watermarks | HIGH | 3 | 4 | 5 | 5 | 3 | 78 |
| cand:story-cover::img2threejs/img2threejs | HIGH | 2 | 4 | 5 | 4 | 4 | 72 |
| cand:story-cover::calesthio/OpenMontage | HIGH | 5 | 3 | 1 | 4 | 5 | 73 |
| cand:story-cover::GargantuaX/gemini-watermark-remover | HIGH | 2 | 4 | 5 | 4 | 3 | 69 |
| cand:story-import::EverMind-AI/EverOS | HIGH | 3 | 5 | 5 | 4 | 4 | 82 |
| cand:story-import::OthmanAdi/planning-with-files | HIGH | 4 | 3 | 5 | 4 | 4 | 80 |
| cand:story-import::zenstory-ai/drama-skills | HIGH | 4 | 4 | 5 | 4 | 3 | 81 |
| cand:story-import::zenstory-ai/oh-story-claudecode | HIGH | 4 | 3 | 5 | 4 | 3 | 77 |
| cand:story-import::Imbad0202/academic-research-skills | HIGH | 3 | 5 | 1 | 5 | 5 | 72 |
| cand:story-long-analyze::EverMind-AI/EverOS | HIGH | 3 | 5 | 5 | 4 | 4 | 82 |
| cand:story-long-analyze::OthmanAdi/planning-with-files | HIGH | 4 | 3 | 5 | 4 | 4 | 80 |
| cand:story-long-analyze::zenstory-ai/oh-story-claudecode | HIGH | 4 | 3 | 5 | 4 | 3 | 77 |
| cand:story-long-write::EverMind-AI/EverOS | HIGH | 3 | 5 | 5 | 4 | 4 | 82 |
| cand:story-long-write::OthmanAdi/planning-with-files | HIGH | 4 | 3 | 5 | 4 | 4 | 80 |
| cand:story-long-write::zenstory-ai/oh-story-claudecode | HIGH | 4 | 3 | 5 | 4 | 3 | 77 |
| cand:story-long-write::Imbad0202/academic-research-skills | HIGH | 3 | 5 | 1 | 5 | 5 | 72 |
| cand:story-long-write::realrossmanngroup/no_ai_slop_writing_rules | HIGH | 3 | 0 | 3 | 3 | 1 | 42 |
| cand:story-review::wanshuiyin/Auto-claude-code-research-in-sleep | HIGH | 5 | 4 | 5 | 5 | 4 | 93 |
| cand:story-review::backnotprop/plannotator | HIGH | 4 | 5 | 5 | 4 | 3 | 85 |
| cand:story-review::zenstory-ai/drama-skills | HIGH | 4 | 4 | 5 | 4 | 3 | 81 |
| cand:story-review::zenstory-ai/oh-story-claudecode | HIGH | 4 | 3 | 5 | 4 | 3 | 77 |
| cand:story-review::Imbad0202/academic-research-skills | HIGH | 3 | 5 | 1 | 5 | 5 | 72 |
| cand:story-setup::affaan-m/ECC | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:story-setup::thedotmack/claude-mem | HIGH | 4 | 5 | 5 | 5 | 5 | 94 |
| cand:story-setup::cheaper-inference/OmniRoute | HIGH | 4 | 5 | 5 | 5 | 5 | 94 |
| cand:story-setup::iOfficeAI/AionUi | HIGH | 3 | 5 | 5 | 5 | 4 | 85 |
| cand:story-setup::wshobson/agents | HIGH | 5 | 4 | 5 | 4 | 4 | 90 |
| cand:story-short-analyze::zenstory-ai/drama-skills | HIGH | 4 | 4 | 5 | 4 | 3 | 81 |
| cand:story-short-analyze::zenstory-ai/oh-story-claudecode | HIGH | 4 | 3 | 5 | 4 | 3 | 77 |
| cand:story-short-analyze::Imbad0202/academic-research-skills | HIGH | 3 | 5 | 1 | 5 | 5 | 72 |
| cand:story-short-analyze::lemomo-ai/lemo-opuscar | HIGH | 2 | 1 | 5 | 3 | 4 | 57 |
| cand:story-short-analyze::eternityspring/shuohao-skills | HIGH | 3 | 0 | 5 | 3 | 3 | 56 |
| cand:story-short-write::zenstory-ai/drama-skills | HIGH | 4 | 4 | 5 | 4 | 3 | 81 |
| cand:story-short-write::zenstory-ai/oh-story-claudecode | HIGH | 4 | 3 | 5 | 4 | 3 | 77 |
| cand:story-short-write::Imbad0202/academic-research-skills | HIGH | 3 | 5 | 1 | 5 | 5 | 72 |
| cand:story-short-write::lemomo-ai/lemo-opuscar | HIGH | 2 | 1 | 5 | 3 | 4 | 57 |
| cand:story-short-write::eternityspring/shuohao-skills | HIGH | 3 | 0 | 5 | 3 | 3 | 56 |
| cand:testing::JuliusBrussee/caveman | MID | 4 | 5 | 5 | 4 | 5 | 91 |
| cand:testing::career-ops-hq/career-ops | MID | 4 | 5 | 5 | 4 | 5 | 91 |
| cand:testing::modelcontextprotocol/inspector | MID | 4 | 5 | 5 | 4 | 4 | 88 |
| cand:testing::NVIDIA/SkillSpector | MID | 4 | 5 | 5 | 4 | 4 | 88 |
| cand:testing::OthmanAdi/planning-with-files | MID | 4 | 3 | 5 | 4 | 4 | 80 |
| cand:utf8-encoding-fix::OrchestratorInc/agent-orchestrator | MID | 4 | 4 | 5 | 5 | 4 | 87 |
| cand:utf8-encoding-fix::getsentry/MobileBuildMCP | MID | 4 | 5 | 5 | 3 | 3 | 82 |
| cand:utf8-encoding-fix::Tencent/BrowserSkill | MID | 3 | 5 | 5 | 4 | 4 | 82 |
| cand:utf8-encoding-fix::browser-act/skills | MID | 5 | 1 | 5 | 4 | 3 | 75 |
| cand:utf8-encoding-fix::parcadei/Continuous-Claude-v3 | MID | 5 | 2 | 5 | 4 | 2 | 76 |
| cand:video-breakdown-skill::ruvnet/RuView | MID | 4 | 5 | 5 | 5 | 5 | 94 |
| cand:video-breakdown-skill::Vincentwei1021/video-shotcraft | MID | 2 | 3 | 5 | 3 | 4 | 65 |
| cand:video-breakdown-skill::cclank/lanshu-awesome-ai-video-kit | MID | 3 | 1 | 5 | 3 | 2 | 57 |
| cand:video-breakdown-skill::feicaiclub/video-spec-builder | MID | 2 | 0 | 5 | 3 | 2 | 47 |
| cand:video-breakdown-skill::sunxiayi/make-blender-education-video-skill | MID | 2 | 0 | 5 | 3 | 1 | 44 |
| cand:video-whisper-transcribe::Vincentwei1021/video-shotcraft | MID | 2 | 3 | 5 | 3 | 4 | 65 |
| cand:video-whisper-transcribe::cclank/lanshu-awesome-ai-video-kit | MID | 3 | 1 | 5 | 3 | 2 | 57 |
| cand:video-whisper-transcribe::equalang/equalang-skill | MID | 2 | 1 | 5 | 3 | 1 | 48 |
| cand:video-whisper-transcribe::feicaiclub/video-spec-builder | MID | 2 | 0 | 5 | 3 | 2 | 47 |
| cand:video-whisper-transcribe::sunxiayi/make-blender-education-video-skill | MID | 2 | 0 | 5 | 3 | 1 | 44 |
| cand:wechat-automation::siddsachar/row-bot | HIGH | 4 | 5 | 5 | 4 | 3 | 85 |
| cand:wechat-automation::zhayujie/CowAgent | HIGH | 3 | 5 | 5 | 3 | 4 | 79 |
| cand:wechat-automation::kangarooking/cangjie-skill | HIGH | 4 | 3 | 5 | 4 | 4 | 80 |
| cand:wechat-automation::nexu-io/html-anything | HIGH | 4 | 3 | 5 | 3 | 3 | 74 |
| cand:wechat-automation::googleworkspace/cli | HIGH | 4 | 2 | 5 | 3 | 4 | 73 |
| cand:wechat-voice-transcription::nexu-io/open-design | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:wechat-voice-transcription::heygen-com/hyperframes | HIGH | 4 | 5 | 5 | 4 | 5 | 91 |
| cand:wechat-voice-transcription::krillinai/OpenCreator | HIGH | 4 | 4 | 5 | 5 | 4 | 87 |
| cand:wechat-voice-transcription::openclaw/Peekaboo | HIGH | 3 | 5 | 5 | 5 | 3 | 82 |
| cand:wechat-voice-transcription::equalang/equalang-skill | HIGH | 2 | 1 | 5 | 3 | 1 | 48 |
| cand:win-toolchain-pitfalls::genspark-ai/genoffice | MID | 4 | 4 | 5 | 4 | 4 | 84 |
| cand:win-toolchain-pitfalls::evalstate/fast-agent | MID | 3 | 5 | 5 | 5 | 3 | 82 |
| cand:win-toolchain-pitfalls::Manavarya09/design-extract | MID | 4 | 4 | 5 | 4 | 3 | 81 |
| cand:win-toolchain-pitfalls::apify/crawlee | MID | 1 | 5 | 3 | 4 | 4 | 62 |
| cand:win-toolchain-pitfalls::alchaincyf/huashu-design | MID | 2 | 1 | 5 | 3 | 4 | 57 |
| cand:windows-bash-cli-interop-pitfalls::OrchestratorInc/agent-orchestrator | HIGH | 4 | 4 | 5 | 5 | 4 | 87 |
| cand:windows-bash-cli-interop-pitfalls::parcadei/Continuous-Claude-v3 | HIGH | 5 | 2 | 5 | 4 | 2 | 76 |
| cand:windows-bash-cli-interop-pitfalls::xpf0000/FlyEnv | HIGH | 2 | 3 | 5 | 5 | 3 | 68 |
| cand:windows-bash-cli-interop-pitfalls::CursorTouch/Windows-MCP | HIGH | 2 | 3 | 5 | 3 | 4 | 65 |
| cand:windows-bash-cli-interop-pitfalls::sixtysevenlf/dsh-blender-plugin | HIGH | 2 | 4 | 5 | 4 | 3 | 69 |
| cand:windows-cli-utf8-wrapper::OrchestratorInc/agent-orchestrator | HIGH | 4 | 4 | 5 | 5 | 4 | 87 |
| cand:windows-cli-utf8-wrapper::parcadei/Continuous-Claude-v3 | HIGH | 5 | 2 | 5 | 4 | 2 | 76 |
| cand:windows-cli-utf8-wrapper::xpf0000/FlyEnv | HIGH | 2 | 3 | 5 | 5 | 3 | 68 |
| cand:windows-cli-utf8-wrapper::CursorTouch/Windows-MCP | HIGH | 2 | 3 | 5 | 3 | 4 | 65 |
| cand:windows-cli-utf8-wrapper::sixtysevenlf/dsh-blender-plugin | HIGH | 2 | 4 | 5 | 4 | 3 | 69 |
| cand:windows-gitbash-chinese-path-pit::thedotmack/claude-mem | HIGH | 4 | 5 | 5 | 5 | 5 | 94 |
| cand:windows-gitbash-chinese-path-pit::cheaper-inference/OmniRoute | HIGH | 4 | 5 | 5 | 5 | 5 | 94 |
| cand:windows-gitbash-chinese-path-pit::iOfficeAI/AionUi | HIGH | 3 | 5 | 5 | 5 | 4 | 85 |
| cand:windows-gitbash-chinese-path-pit::OrchestratorInc/agent-orchestrator | HIGH | 4 | 4 | 5 | 5 | 4 | 87 |
| cand:windows-native-ocr::Portwood-Global-Solutions/Portwood | HIGH | 3 | 2 | 5 | 5 | 2 | 67 |
| cand:windows-native-ocr::Anionex/agent-vision-toolkit | HIGH | 2 | 3 | 5 | 3 | 3 | 62 |
| cand:windows-native-ocr::liustack/modlens | HIGH | 2 | 1 | 5 | 4 | 3 | 57 |
| cand:windows-native-ocr::A9T9/RPA | HIGH | 1 | 1 | 1 | 3 | 3 | 32 |
| cand:windows-native-ocr::TejasS1233/opencode-parser | HIGH | 0 | 2 | 3 | 3 | 1 | 32 |
| cand:workbuddy-mcp::googleapis/mcp-toolbox | HIGH | 3 | 4 | 5 | 5 | 4 | 81 |
| cand:workbuddy-mcp::agentscope-ai/QwenPaw | HIGH | 4 | 5 | 5 | 3 | 4 | 85 |
| cand:workbuddy-mcp::t8y2/dbx | HIGH | 2 | 5 | 5 | 5 | 4 | 79 |
| cand:workbuddy-mcp::mukul975/Anthropic-Cybersecurity-Skills | HIGH | 5 | 2 | 5 | 3 | 4 | 79 |
| cand:workbuddy-mcp::vibheksoni/stealth-browser-mcp | HIGH | 2 | 2 | 5 | 3 | 3 | 58 |
| cand:workflow-preflight-check::ruvnet/ruflo | HIGH | 5 | 5 | 5 | 5 | 5 | 100 |
| cand:workflow-preflight-check::NVIDIA/SkillSpector | HIGH | 4 | 5 | 5 | 4 | 4 | 88 |
| cand:workflow-preflight-check::activepieces/activepieces | HIGH | 4 | 5 | 5 | 3 | 4 | 85 |
| cand:workflow-preflight-check::eigent-ai/eigent | HIGH | 3 | 5 | 5 | 3 | 4 | 79 |
| cand:workflow-preflight-check::langgenius/dify | HIGH | 3 | 5 | 1 | 5 | 5 | 72 |
<!-- MATRIX_SUMMARY_END -->

## 7. 分组统计（加权总分 0-100）

| 面 | SCORED 对象数 | UNAVAILABLE 未计分数 | 均值 | 最小 | 最大 |
|---|---:|---:|---:|---:|---:|
| candidate/HIGH | 203 | 0 | 78.0 | 32 | 100 |
| candidate/MID | 120 | 0 | 72.91 | 37 | 100 |
| current/EXCLUDE | 40 | 3 | 35.4 | 30 | 68 |
| current/HIGH | 51 | 0 | 31.25 | 30 | 38 |
| current/LOW | 29 | 1 | 32.9 | 30 | 38 |
| current/MID | 26 | 0 | 31.38 | 30 | 34 |

该统计仅纳入 SCORED 对象；UNAVAILABLE 的 5 维 0 哨兵不纳入均值/优劣比较（§3）。数值只说明「作为可替换资产包的工程完成度」分布，**不是业务功能强弱结论**；fc 由 SKILL.md 计数代理，仓级 bundle 天然高于单件 skill 目录（见 §9 盲区），t4 迁移优先级不得只按 T 排序。

## 8. 负控、自证命令、门禁与退路

- **自证（差异断言 0）**：`cd 自建skill优化 && PYTHONPYCACHEPREFIX=_temp/pycache "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -B deliverables/skill-modernization-r1/03_matrix_check.py` → 打印 `[DIFF_ASSERT] 0`，逐对象复算 `matrix.csv` 的 `weighted_contribution` 求和并与 §6 汇总表逐行比对。
- **负控**：`03_matrix_check.py` 把样例候选的 `fc` 分数改 0，重算 T，断言 `T_prime != T` 并打印 `[NEGCTRL:RED] 篡改被检出`；另注入一处汇总表错值断言被抓。负控只作用于内存副本，不写回 `matrix.csv`。
- **现场取值命令**：候选 `gh api repos/<OWNER>/<REPO> --jq .` + `gh api "repos/<OWNER>/<REPO>/git/trees/<br>?recursive=1" --jq .`；现有件 `find D:/global_skills/<slug> -type f`；活跃根 `find /d/global_skills -type f -name SKILL.md | wc -l`。每个分数在 `matrix.csv` 的 `evidence_handle` / `measurement_command` 两列可逐行追溯。
- **全量门禁（本轮实测，取自 `_temp/t3_gates.json`，非硬编码）**：`cd 自建skill优化 && PYTHONPYCACHEPREFIX=_temp/pycache "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -B 05-exec/run_gates.py --json _temp/t3_gates.json` → `verdict=FAIL`、`verdict_reason=FAIL=7 UNVERIFIED=2`、`gates_run=118`、`generated_at=2026-11-07 06:16`、`schema=gate-run-v1`。红门分类：`REAL_RED=8`（gov_acceptance_face / ratchet_gate / control_char_scan / refresh_budget_fixtures / budget_contract_fixtures / baseline_note_fixtures / fixture_wiring_face / skill_wiring_face）+ `DESIGN_INHERENT_RED=1`（gate_run_freshness）。其中 `control_char_scan` 脏件是**既有** `D:\app-cache\skill-fenjue\自建skill优化\_temp\r295a\meta_raw.json`（非 t3 的 03_* 产物，本轮定点 `CTRL_SCAN CLEAN`）；其余为既有 / 他人在途 / 设计固有红。按 R263/X-9 如实登记、不删 tracked 件凑绿，与 t1（FAIL=7/UNVERIFIED=2）、t2（FAIL=7/UNVERIFIED=3）同源，不阻塞下游 t4/t5/t6。详见 §10。
- **证据句柄独立回溯（生成器重读落盘缓存 + CSV 现场复算）**：`[RECOMP] doc_hash_recomputable=297 bad=0` / `[HANDLE] rows=2365 traceable=2365 bad=0`；独立外部复跑 `python -B _temp/t3_matrix/verify_handles.py` → `[VERIFY] PASS`。每个分数的 `evidence_handle` 都能回溯到本轮现场快照 doc 的 `doc_hash`（sha256 前 12 位），4 件目录缺失 UNAVAILABLE doc 也落完整 hash。
- **退路**：取证受阻 ⇒ `python 05-exec/r114_replacement_scan.py --offline --json _temp/t3_matrix/r114_offline.json` 复用缓存；`03_matrix_build.py --offline` 复用 `_temp/t3_matrix/live_meta.json`；两者都失败的对象标 `UNAVAILABLE` 并具名登记盲区，禁静默丢弃。

## 9. 盲区、边界与下游接口

- **B1 bundle-scale 不对称（结构性，双向披露）**：同一锚点下，候选是「整仓」、现有件是「单件 skill 目录」，仓级 SKILL.md 数天然更高。所有对象在 `evidence_handle` 带 `blob_n` 所在 doc 的 sha，读者可用 `--show-repo` / `--show-local` 核对 `skill_md_exact_n`；本矩阵测的是**资产包工程完成度**，不是单件业务功能等价性。t4 的功能等价结论须另做人审，不得由 T 直接推出。
- **B2 运行效率是代理**：`eff` 数的是测试路径与 CI 工作流，不是执行耗时；本地 r260 仅 26/77 有 `route_ms_med`、51/77 NO_TRIGGER，已在 `notes` 列逐行登记。
- **B3 社区支持度无 outcome 数据**：99.94% outcome_unknown，只有 stars / pushed_at / forks 代理，权重封顶 15%。
- **B4 取证失败登记**：现场失败且离线缓存亦缺的仓，标 `UNAVAILABLE` + ❌未实测，下轮巡检补取。
- **B5 排除对象登记（不计分、不进 CSV/汇总表）**：98 条 = 54 `directed_lead`（功能等价 ❌未实测）+ 44 `family_pad`（族级邻居 `not_replacement=true`）；无重复计数。t2 语义缺口 11 件（A-ask-questions、chaoshi-admin-inline-edit、cloudbase-db-optimize、dogfood、fenjue-lessons-hitrate、story-deslop、story-scan、vp-perspective-audit、wb-git-commit-recipe、wps-knowledgebase、天眼一下）只有线索、无真替代，须在 t4 单列「语义缺口」处置。
- **B6 community/stars 通道结构性不可比**：本地单件 skill 无 GitHub stars，doc 固定 `stars=0`，community 仅由 `pushed_at` 新鲜度贡献；候选整仓可用 stars 四档。两侧虽共用 `score5`，输入面并不等价，t4 **不得**把 community 差值写成「社区支持度优于本地」的绝对结论；公平比较须在 t6 用同一业务指标独立 A/B。
- **下游接口**：t4 迁移计划按 (现有 skill, 候选) 对取 `weighted_total` 与逐维分数做优先级输入，叠加 t2 的 `rel_strength` / `match_reason`、需求⑥的 A/B 验证与兼容性验证；t5 季度巡检把本脚本的现场复取与 `maintenance_trim`（archived / pushed_at < EVAL_DATE-365d）纳入例行。

## 10. 门禁实测记录（本轮，禁硬编码）

- 命令：`cd 自建skill优化 && PYTHONPYCACHEPREFIX=_temp/pycache "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -B 05-exec/run_gates.py --json _temp/t3_gates.json > _temp/t3_gates.log 2>&1`（后台 job；`GATE_RC=1` 为门禁判红的程序退出码，非执行失败，job 状态 completed）。
- 输出：`_temp/t3_gates.json` → `verdict=FAIL` / `verdict_reason=FAIL=7 UNVERIFIED=2` / `gates_run=118` / `generated_at=2026-11-07 06:16` / `total_ms=871788`；日志末行 `[GATES:FAIL] FAIL=7 UNVERIFIED=2`。
- runner 自报不覆盖：受管根四门禁 mirror/noise/evolution/stub —— 属 rule_editor 面，取值：python D:\global_skills\A-memory-start\references\rule_editor.py gates；焚诀跨产物真值 C1~C33 —— 取值：python 焚诀\eval\verify_truth_consistency.py；判据变异测试（r19_fixture_mutation_check.py）—— 按需跑，非每轮前置。本轮阶段0-3 只读取证，未触发受管根四门禁。
- 红门归因：`REAL_RED=8`（gov_acceptance_face / ratchet_gate / control_char_scan / refresh_budget_fixtures / budget_contract_fixtures / baseline_note_fixtures / fixture_wiring_face / skill_wiring_face）+ `DESIGN_INHERENT_RED=1`（gate_run_freshness）；`control_char_scan` 现场 tail 摘要：`重跑仍 FAIL ⇒ 判真红 | 首跑: 622 个面 / 脏 1 / 跳过二进制 121 === |   [CTRL:HIT] D:\app-cache\skill-fenjue\自建skill优化\_temp\r295a\meta_raw.json ×6 码位=[127] 首偏移=[328, 1506, 2723]` … 脏件 `D:\app-cache\skill-fenjue\自建skill优化\_temp\r295a\meta_raw.json` 为既有件，**无一门由 t3 的 03_* 产物触发**，本轮 4 件产物 + `data/matrix.csv` 定点 `CTRL_SCAN CLEAN`；其余为既有 / 他人在途 / 设计固有红。
- 处置：按 R263/X-9 如实登记、不删 tracked 件凑绿、不改写历史报告（R241）；与 t1/t2 同源既有红，按既有判据不阻塞下游 t4/t5/t6。

<!-- 生成脚本：03_matrix_build.py；复算/负控：03_matrix_check.py；数据：data/matrix.csv -->
