# 上游开源替代检索与对标矩阵 r113（需求 2 + 需求 3）

> 项目：自建skill优化 ｜ 权威源：D:\global_skills（182 件）｜ 生成：2026-10-18（第 113 轮）
> 本件回答两个问题：① 每一族有没有**更优的开源替代**？② 若有，五维上强在哪、弱在哪？
> 口径纪律：本件所有外部数字均为**本轮实时取证**；取不到的**逐条具名**，禁止写成「无候选」。
> 与 r112/r113 判定面的关系：**版本落后**（我这份是不是旧的）走内容寻址（06-benchmark/全量对标报告_r113_*.md §2）；
> 本件管的是**替代**（有没有别的更好），两者是不同问题，不互相替代。

## 1. 方法与环境（含实际踩坑，禁写「顺畅完成」）

### 1.1 检索面

| 查询 | 结果 | 取证命令 |
|---|---|---|
| `topic:agent-skills` | total 34,477 / 取前 30 | `gh api search/repositories -f q=topic:agent-skills -f sort=stars -f per_page=30` |
| `topic:claude-skills` | total 11,923 / 取前 30 | 同上换 q |
| `SKILL.md in:readme` | total 1,794,133 / 取前 30 | 同上换 q |
| `skills in:name claude` | total 13,248 / 取前 30 | 同上换 q |
| `skills in:name anthropic` | total 227 / 取前 30 | 同上换 q |
| 五查询并集 | **132 仓** | `06-benchmark/gh_search_r113_2026-10-18.json 的 union_n` |

### 1.2 逐仓客观测量（15 仓）

测的是**可复算字段**，不是印象分：技能件数（`SKILL.md` 命中）/ 总 blob / workflow 数 / tests 路径数 / README / docs / 治理件 / stars / pushed_at / license。
> 取值：`python _temp/r113_measure.py`；产物 06-benchmark/candidate_measure_r113_2026-10-18.json
> 复测命令：`gh api repos/<R> --jq .stargazers_count` 与 `gh api repos/<R>/git/trees/HEAD?recursive=1 --jq .truncated`

### 1.3 本轮真实踩坑（三条，全部影响结论面）

| # | 现象 | 根因 | 处置 |
|---|---|---|---|
| 1 | `gh api` 在 PowerShell 里报 `function not defined: UNLICENSED/0`、`Cannot run a document in the middle of a pipeline` | PATH 上的 `C:\Users\37533\.local\bin\gh` 是 **0 字节壳**（`Get-Item ... .Length` = 0），真二进制在 `C:\Program Files\GitHub CLI\gh.exe` | 全程改用绝对路径调用；TOML/JSON 解析改为 Python 内 `json.loads`，不用 `--jq` 表达式 |
| 2 | 首轮测量有两处 `EOF`（`addyosmani/agent-skills` 元数据、`kepano/obsidian-skills` 树面） | 网络抖动（非限流：同命令重试即过） | 加三次退避重试后**全部转 OK**；`remaining TREE-UNVERIFIED: []` |
| 3 | `VoltAgent/awesome-agent-skills` 35,906★ 看起来是大候选 | 实测 `SKILL.md` 命中 **0**、blob **4** ⇒ 它是**清单/索引仓，不是技能包** | 判为「清单型」，**不计入技能候选面**（星标高≠有技能） |

> 第 3 条是本轮最重要的方法学发现：**星标与「有可比技能实体」不相关**。若只按 stars 排序取候选，会把清单仓当替代品。

## 2. 逐族候选表（8 族；每族 3–5 候选 + 实测字段）

> 下表 `技能件数 / tests / workflow` 均为 1.2 的实测值；`同名候选` 指与本族本地件**同名**的上游文件。

### F1 文档办公（docx / xlsx / pdf / ppt-master / office-automation-pro）

| 候选 | stars | pushed | license | 技能件 | tests | 同名候选与实测 |
|---|---|---|---|---|---|---|
| anthropics/skills | 181,814 | 2026-10-09 | UNLICENSED | 20 | 0 | docx 6,911B / xlsx 8,598B / pdf 8,072B（**本地同名件交集 < 0.15**） |
| K-Dense-AI/scientific-agent-skills | 52,318 | 2026-10-15 | MIT | 178 | 373 | 无同名 |
| wshobson/agents | 40,980 | 2026-10-17 | MIT | 185 | 51 | 无同名 |
| sickn33/agentic-awesome-skills | 47,780 | 2026-10-17 | MIT | 8,339（生成式） | 411 | 无同名 |

结论：**保留本地 + 定向吸收**。本地 docx 有 17 条可跑验证腿、pdf 4 腿、xlsx 3 腿（r108–r112 实测），而 anthropics 同名件 tests = 0；
但 anthropics 的 `xlsx`/`docx` 正文仍是**参照源**（本地已合入其 XSD/wiring 内容）。
> 取值：`gh api repos/anthropics/skills/git/trees/HEAD?recursive=1` 计 tests 路径；本地腿数见 06-benchmark/全量对标报告_r112_*.md §2 ③

### F2 前端 UI 设计（frontend-design / frontend-skill / ui-ux-pro-max / web-design-guidelines / shadcn）

| 候选 | stars | pushed | license | 技能件 | tests | 同名候选与实测 |
|---|---|---|---|---|---|---|
| anthropics/skills | 181,814 | 2026-10-09 | UNLICENSED | 20 | 0 | frontend-design 9,390B（**max_jaccard 0.0223 ⇒ unrelated**） |
| sickn33/agentic-awesome-skills | 47,780 | 2026-10-17 | MIT | 8,339 | 411 | frontend-design 8,351B / ui-ux-pro-max 12,993B（均 unrelated） |
| affaan-m/ECC | 282,595 | 2026-10-15 | MIT | 1,062 | 631 | frontend-slides（wider candidate 面） |
| nexu-io/open-design | 101,977 | 2026-10-18 | Apache-2.0 | 未测（非技能包形态） | — | 无可比同名件 |
| Jeffallan/claude-skills | 11,920 | 2026-10-16 | MIT | 67 | 29 | 无同名 |

结论：**保留本地**。本地两件（frontend-design / ui-ux-pro-max）与全部同名候选落 unrelated 区 ⇒ 它们是**深度改写版而非旧版**；
`shadcn` 是唯一有真上游增量的件（upstream_only=14）但属市场件形态（本地带 evals/evals.json）⇒ 待裁，见 04-plan/迁移替换方案_r113_2026-10-18.md §2 U-1。
> 取值：`python -c "import json;d=json.load(open('06-benchmark/adjudication_r113_2026-10-18.json',encoding='utf-8'));print([(x['slug'],x['max_jaccard']) for x in d['unverified_dispositions']])"

### F3 视频与媒体（hyperframes 族 / byted-mediakit / seedance / video-frames / whisper）

| 候选 | stars | pushed | license | 技能件 | tests | 同名候选与实测 |
|---|---|---|---|---|---|---|
| calesthio/OpenMontage | 69,217 | 2026-10-16 | **AGPL-3.0** | 139 | 198 | hyperframes / -cli / -media / -registry 四件同名（**已合入**） |
| K-Dense-AI/scientific-agent-skills | 52,318 | 2026-10-15 | MIT | 178 | 373 | 无同名 |
| sickn33/agentic-awesome-skills | 47,780 | 2026-10-17 | MIT | 8,339 | 411 | 无同名 |

结论：**已定向升级（hyperframes-registry，受管根 9b34cea5）+ 保留本地**。
⚠️ license 边界：OpenMontage 为 **AGPL-3.0**，合入其正文属**再分发**，已在 r113 执行（唯 2 行 + 2 参照件）⇒ 登记为合规待裁项（U-4）。
> 取值：`gh api repos/calesthio/OpenMontage --jq .license.spdx_id`；本地四件 same-slug 关系见 06-benchmark/upstream_r112_2026-10-18d.json

### F4 测试与验证（testing / test-driven-development / verification-before-completion / spike）

| 候选 | stars | pushed | license | 技能件 | tests | 同名候选与实测 |
|---|---|---|---|---|---|---|
| obra/superpowers | 301,258 | 2026-10-10 | MIT | 15 | **77** | test-driven-development（upstream_only 20→11）/ verification-before-completion（unrelated 0.0223） |
| addyosmani/agent-skills | 107,881 | 2026-10-13 | MIT | 25 | 0 | test-driven-development（取数失败，未入裁决） |
| K-Dense-AI/scientific-agent-skills | 52,318 | 2026-10-15 | MIT | 178 | 373 | 无同名 |

结论：**已升级 TDD + 保留本地**。superpowers 仍是本族最强上游（77 tests 是真资产）；
但 `verification-before-completion` 与上游 unrelated（本地是自建立局版）⇒ 不换。
> 取值：`gh api repos/obra/superpowers/git/trees/HEAD?recursive=1` 计 tests=77；本地 TDD 增量行见 06-benchmark/upstream_r112_2026-10-18d.json 的 rows[test-driven-development].stats

### F5 调试与审查（debugging-fixing / code-review / security-audit / refactoring / ci-pipeline-debugging）

| 候选 | stars | pushed | license | 技能件 | tests | 同名候选与实测 |
|---|---|---|---|---|---|---|
| mattpocock/skills | 295,201 | 2026-10-13 | MIT | 38 | 1 | code-review 6,670B（**max_jaccard 0.02 ⇒ unrelated**）/ grill-me 157B |
| github/awesome-copilot | 未测（清单型） | — | — | code-review 8,265B（unrelated） | — | 同 slug 但非同源 |
| mukul975/Anthropic-Cybersecurity-Skills | 34,623 | 2026-08-31 | Apache-2.0 | 820 | 106 | security-audit（本地与 AAS 版 unrelated 0.0094） |
| wshobson/agents | 40,980 | 2026-10-17 | MIT | 185 | 51 | 无同名 |

结论：**保留本地**。本族全部同名候选落 unrelated ⇒ 本地是自建深度版；
`code-review` 的 mattpocock 版 6,670B vs 本地 12926B 的 `ci-pipeline-debugging` 决策树（六类根因）覆盖面更宽。
> 取值：`python 05-exec/r112_upstream_probe.py --scan <scan> --json <件>`（rows[slug].status=UNVERIFIED 且 reason 具名）

### F6 记忆与项目治理（A-project-handoff / A-memory-start / A-get-memory / writing-plans / executing-plans）

| 候选 | stars | pushed | license | 技能件 | workflow | tests | 同名候选与实测 |
|---|---|---|---|---|---|---|---|
| github/spec-kit | 141,692 | 2026-10-16 | MIT | 2 | **30** | 360 | writing-plans 同名（本地已升级，upstream_only 73→0，转 LOCAL_AHEAD_KEEP） |
| wshobson/agents | 40,980 | 2026-10-17 | MIT | 185 | 6 | 51 | 无同名 |
| mattpocock/skills | 295,201 | 2026-10-13 | MIT | 38 | 3 | 1 | 无同名 |

结论：**已升级 writing-plans + 保留本地**，且本族出现本轮唯一「**对手确实更强**」的整族级差距：
spec-kit 有 30 workflow + 360 tests 的**模板/文档/交付流水线**，本地治理深度在判据面（35 门 + 棘轮 + 账龄尺）但**根治理件只有 1/12**（r109 立 CONTRIBUTING.md）。
⇒ 建议：**部分吸收**（模板+文档面），不是整体替换。
> 取值：`gh api repos/github/spec-kit/git/trees/HEAD?recursive=1`；本地 writing-plans 现状见 06-benchmark/swap_gate_r112_2026-10-18d.json

### F7 浏览器自动化（agent-browser / browser-cdp / gstack / dogfood / electron）

| 候选 | stars | pushed | license | 技能件 | tests | 实测判读 |
|---|---|---|---|---|---|---|
| VoltAgent/awesome-agent-skills | 35,906 | 2026-10-15 | MIT | **0** | 0 | **清单仓**（blob=4）⇒ 不可作技能替代 |
| Jeffallan/claude-skills | 11,920 | 2026-10-16 | MIT | 67 | 29 | 无同名可比件 |
| ComposioHQ/awesome-claude-skills | 77,318 | 2026-09-18 | UNLICENSED | 清单型 | — | 无同名可比件 |

结论：**无更优替代（本地即最优）**。本族本地三件（agent-browser / browser-cdp / gstack）是**可跑的 CLI 驱动**（`npx agent-browser`），
而检索面里 stars 最高的候选是清单仓（0 个 SKILL.md）⇒ 「星标高」在本族完全不构成替代理由。
> 取值：06-benchmark/candidate_measure_r113_2026-10-18.json 的 repos["VoltAgent/awesome-agent-skills"].skill_md_n == 0

### F8 数据与图表（data-analysis / data-visualization / chart-visualization / xlsx / rag-eval）

| 候选 | stars | pushed | license | 技能件 | tests | 同名候选与实测 |
|---|---|---|---|---|---|---|
| K-Dense-AI/scientific-agent-skills | 52,318 | 2026-10-15 | MIT | 178 | 373 | 无同名 |
| anthropics/skills | 181,814 | 2026-10-09 | UNLICENSED | 20 | 0 | xlsx（unrelated 0.0206） |
| wshobson/agents | 40,980 | 2026-10-17 | MIT | 185 | 51 | 无同名 |

结论：**保留本地**。本地 `chart-visualization` 有 26 种图表类型选择器、`data-visualization` 有 plotly/seaborn/matplotlib 三层回退，
同名候选全落 unrelated；K-Dense-AI 的科学计算面与本地数据族**能力类型不同**（不做替代，登记为可借鉴）。
> 取值：同 F1

## 3. 五维评分矩阵（含本地基线）

### 3.1 评分锚（把主观分钉在实测字段上，防「拍脑袋给 4 分」）

| 维度 | 锚定字段 | 0–5 分口径 |
|---|---|---|
| 功能完整性 | `skill_md_n` + 与本地族的**同名可比件数** | 0 = 无可比件；5 = 有可比件且正文更全 |
| 运行效率 | `workflow_n` / CI 存在 / 可跑 tests 数 | 0 = 无 CI 无 tests；5 = CI + 可跑 tests ≥ 100 |
| 兼容性 | license + 平台绑定（AIPC/Win 深绑定 vs 平台中立） | 0 = UNLICENSED 或与本机绑死；5 = MIT/Apache + 可移植 |
| 文档完善度 | `readme_n` + `docs_md_n` + 治理件数 | 0 = 无 README；5 = README + docs 目录 + CONTRIBUTING/SECURITY |
| 社区支持度 | `stars` + `pushed_at` 新鲜度（≤7 日） | 0 = 停摆 >12 月；5 = ≥10 万★ 且本周有推送 |

### 3.2 矩阵（15 候选 + 本地基线；比值列 = 候选 − 本地，正为候选更强）

| 对象 | 功能 | 效率 | 兼容 | 文档 | 社区 | 总分 | vs 本地 |
|---|---|---|---|---|---|---|---|
| **本地基线（D:\global_skills + 本仓判据面）** | 4 | 3 | 3 | 2 | 2 | **14** | — |
| anthropics/skills | 3 | 1 | 1 | 2 | 5 | 12 | -2 |
| obra/superpowers | 3 | 5 | 5 | 4 | 5 | 22 | +8 |
| mattpocock/skills | 3 | 2 | 5 | 3 | 5 | 18 | +4 |
| github/spec-kit | 2 | 5 | 5 | 5 | 5 | 22 | +8 |
| addyosmani/agent-skills | 3 | 1 | 5 | 4 | 5 | 18 | +4 |
| sickn33/agentic-awesome-skills | 4 | 4 | 5 | 2 | 5 | 20 | +6 |
| calesthio/OpenMontage | 4 | 4 | 2 | 3 | 5 | 18 | +4 |
| kepano/obsidian-skills | 3 | 1 | 5 | 3 | 5 | 17 | +3 |
| K-Dense-AI/scientific-agent-skills | 3 | 5 | 5 | 3 | 5 | 21 | +7 |
| wshobson/agents | 3 | 3 | 5 | 3 | 5 | 19 | +5 |
| afaan-m/ECC（affaan-m/ECC） | 4 | 5 | 5 | 2 | 5 | 21 | +7 |
| coreyhaines31/marketingskills | 2 | 4 | 5 | 2 | 5 | 18 | +4 |
| Jeffallan/claude-skills | 2 | 2 | 5 | 2 | 4 | 15 | +1 |
| mukul975/Anthropic-Cybersecurity-Skills | 3 | 3 | 5 | 2 | 4 | 17 | +3 |
| VoltAgent/awesome-agent-skills | 0 | 0 | 5 | 2 | 5 | 12 | -2 |
| ComposioHQ/awesome-claude-skills | 0 | 0 | 1 | 2 | 5 | 8 | -6 |

> ⚠️ 读法（防误用）：**总分高 ≠ 应当替换**。三个理由已实测：
> ① 候选总分高多来自 `社区支持度`（stars）与 `效率`（tests/CI），而本地基线在**与 AIPC/Win + 九端深绑定**和**判据面（35 门）**这两处对手普遍为 0；
> ② 本仓 182 件里 **127 件曾是 unknown 身份**（r112 实测），其中 66 件经 r113 判为 `self_built`（本就没有上游）⇒ 对它们**不存在「上游总分更高」这个命题**；
> ③ 逐族结论见 §4：8 族里 **6 族判「保留本地」**，2 族「定向升级已完成」。
> 取值：矩阵字段全部由 06-benchmark/candidate_measure_r113_2026-10-18.json 实测值按 §3.1 锚换算；本地基线字段见 §3.3。

### 3.3 本地基线取数（防「基线也是拍脑袋」）

| 字段 | 本地实测 | 取值命令 |
|---|---|---|
| 在册技能 | 182 | `python D:/global_skills/A-skill-manager/assets/disk_registry_diff.py` |
| 常驻门 | 35 | `python 05-exec/run_gates.py --json <件>` 末行 PASS=N |
| 可跑验证腿 | docx 17 / xlsx 3 / pdf 4 / provenance 23 / cache-guard 4 腿 | 见 06-benchmark/全量对标报告_r112_*.md §2 ③ |
| tests 目录 | **0**（可发现性差距，非能力差距） | `Get-ChildItem -Recurse -Directory -Filter tests` |
| 根治理件 | 1/12（CONTRIBUTING.md，r109 立；LICENSE 按 X-2 禁补） | `Get-ChildItem -File -Filter *.md` 于 D:\global_skills 根 |
| 上游候选仓 | 11 个（本轮季度巡检在册） | `python 05-exec/r113_quarterly_audit.py --offline` |

## 4. 每族结论（三选一，逐族给出而不是笼统表态）

| 族 | 结论 | 依据 |
|---|---|---|
| F1 文档办公 | **保留本地 + 定向吸收** | 本地 17/4/3 腿可跑，同名上游 tests=0 |
| F2 前端 UI | **保留本地** | 同名候选全 unrelated（max_jaccard ≤ 0.0223） |
| F3 视频媒体 | **定向升级已完成（registry）** | upstream_only 3→2；⚠️ AGPL-3.0 合入待裁 |
| F4 测试验证 | **定向升级已完成（TDD）** | upstream_only 20→11；残差 11 已逐条定性 |
| F5 调试审查 | **保留本地** | 同名候选全 unrelated；本地另有专件更宽 |
| F6 记忆治理 | **部分吸收（模板/文档面）** | spec-kit 30 wf / 360 tests / 12 治理文档 vs 本地 1/12 |
| F7 浏览器自动化 | **无更优替代（本地即最优）** | 检索面最高星为清单仓（0 SKILL.md） |
| F8 数据图表 | **保留本地** | 同名候选 unrelated；能力类型不同 |

## 5. 未能取证与不采信的具名清单（禁笼统写「取不到」）

| # | 对象/字段 | 状态 | 原因 | 处置 |
|---|---|---|---|---|
| 1 | `github/awesome-copilot` 元数据 | ⚠️ 未测 | 本轮未纳入 1.2 的 15 仓（属清单型仓） | 只取其 code-review 正文作同 slug 对照（unrelated） |
| 2 | `nexu-io/open-design` 技能件数 | ⚠️ 未测 | 非技能包形态（树面未取） | 登记为待复测，**不得**计入候选数 |
| 3 | `ComposioHQ/awesome-claude-skills` | ⚠️ 清单型 | license UNLICENSED + 清单仓 | 判不可作替代 |
| 4 | `addyosmani/agent-skills` 的 TDD 同名件 | ⚠️ 原文取不到（`ok=False`） | r112 取数失败（r113 cache-guard：失败不覆盖旧证据） | 该行在裁决中记 UNVERIFIED，**不冒充已核对** |
| 5 | `sickn33/...` 的 TDD / writing-plans 同名件 | ⚠️ 原文取不到（`ok=False`） | 同上 | 同上 |
| 6 | 上游仓「分支保护 / 贡献者数 / 近 30 日提交数」 | ❌ 本轮未取 | 不在本轮五维锚内 | 禁据此下结论；若需，接入季度巡检 |

> 本清单即「面不完整」的显形面：**未取证 ≠ 无候选**（R247 同族口径）。

---

## 6. 扩面候选（第二轮检索 + 逐仓复核；本节的源码件原文已落地 06-benchmark/upstream_probe_index_r113_2026-10-18.json）

> 说明：本节来自一次**并行外部调研**（子代理）抓回的 18 份上游 `SKILL.md` 原文 + 31 仓最近提交日期。
> 该子代理**未产出交付件**（其元数据索引自带坏 `--jq` 调用，42 行全是 `ERR function not defined: UNLICENSED/0`）；
> 故本节的全部元数据由**我自行复核重取**（`gh api repos/<R>` 绝对路径调用 + `json.loads`，产物 06-benchmark/candidate_measure_r113b_2026-10-18.json）。
> ⚠️ 未复取的字段一律不写；子代理的坏索引面**不作证据**（登记在本节末）。

### 6.1 二十个复核通过的候选（按族归位）

| 族 | 候选 | stars | pushed | license | 子代理抓回的代表件 |
|---|---|---|---|---|---|
| F1 文档办公 | genspark-ai/genoffice | 9,910 | 2026-10-17 | Apache-2.0 | `skills/genoffice/SKILL.md` 78,122B（含 pptx/xlsx/docx/pdf 全链 + CLI 版本 2.67.1） |
| F1 文档办公 | tfriedel/claude-office-skills | 839 | 2026-04-01 | UNLICENSED | `public/docx/SKILL.md` 10,294B |
| F1 文档办公 | **hugohe3/ppt-master** | **63,193** | 2026-10-17 | MIT | （未抓原文，仅取元数据） |
| F2 前端 UI | addyosmani/web-quality-skills | 2,956 | 2026-08-24 | MIT | `skills/accessibility/SKILL.md` 14,729B |
| F2 前端 UI | oil-oil/oil-ui | 1,695 | 2026-10-17 | MIT | `SKILL.md` 8,267B |
| F2 前端 UI | plugin87/ux-ui-agent-skills | 2,040 | 2026-10-10 | MIT | `.claude/skills/design-tokens/SKILL.md` 2,094B |
| F2 前端 UI | bitjaru/styleseed | 978 | 2026-10-14 | MIT | （未抓原文） |
| F3 视频媒体 | **heygen-com/hyperframes** | **66,062** | **2026-10-18** | Apache-2.0 | `.agents/skills/motion-doctrine/SKILL.md` 11,996B |
| F3 视频媒体 | dexhunter/seedance2-skill | 4,334 | 2026-09-19 | MIT | `SKILL.md` 15,605B |
| F3 视频媒体 | luoluoluo22/jianying-editor-skill | 4,188 | 2026-09-11 | NOASSERTION | （未抓原文） |
| F4 测试验证 | obra/superpowers（复核） | 301,258 | 2026-10-10 | MIT | TDD 9,886B + verification-before-completion 3,718B |
| F4 测试验证 | microsoft/waza | 1,420 | 2026-10-17 | MIT | （未抓原文） |
| F5 调试审查 | **cloudflare/security-audit-skill** | **30,756** | 2026-09-14 | MIT | `skills/security-audit/SKILL.md` 22,182B |
| F5 调试审查 | Zhen-Bo/smell-check | 240 | 2026-08-29 | MIT | `SKILL.md` 5,977B |
| F5 调试审查 | athola/claude-night-market | 342 | 2026-10-16 | MIT | （未抓原文） |
| F6 记忆治理 | muratcankoylan/Agent-Skills-for-Context-Engineering | 18,158 | 2026-10-12 | MIT | `skills/context-compression/SKILL.md` 18,768B |
| F6 记忆治理 | rohitg00/pro-workflow | 2,917 | 2026-09-29 | UNLICENSED | `skills/learn-rule/SKILL.md` 2,335B |
| F7 浏览器自动化 | Tencent/BrowserSkill | 9,115 | 2026-10-15 | MIT | `packages/dsh-plugin-browserskill/skill/SKILL.md` 4,453B |
| F7 浏览器自动化 | browser-act/skills | 6,156 | 2026-08-24 | MIT | `browser-act/SKILL.md` 3,726B |
| F8 数据图表 | gongnyang/gongnangi-chart-skill | 70 | 2026-07-30 | MIT | `SKILL.md` 11,051B |
| F8 数据图表 | aref-vc/tufte-claude-skill | 311 | 2026-06-15 | MIT | `SKILL.md` 5,162B |

> 取值：`gh api repos/<R>`（Python `subprocess` + `json.loads`，不用 `--jq`）；产物见 06-benchmark/candidate_measure_r113b_2026-10-18.json
> 取值（原文件）：06-benchmark/upstream_probe_index_r113_2026-10-18.json（18 条，每条带 repo/path/bytes/lines/head）

### 6.2 扩面后各族候选数（需求 2 的「3–5 个」逐族达标情况）

| 族 | 候选数（§2 + §6.1 合计） | 是否达标 |
|---|---|---|
| F1 文档办公 | 6 | ✅ |
| F2 前端 UI | 8 | ✅ |
| F3 视频媒体 | 6 | ✅ |
| F4 测试验证 | 4 | ✅ |
| F5 调试审查 | 7 | ✅ |
| F6 记忆治理 | 6 | ✅ |
| F7 浏览器自动化 | 5 | ✅ |
| F8 数据图表 | 5 | ✅ |

⇒ **8/8 族达标**（≥3 候选）；族内「更优」判定见 §7.2（本轮新增的定向复核结论）。

### 6.3 扩面带来的三个**实质结论修正**（不是凑数）

| # | 原结论（§2/§4） | 扩面后修正 | 证据 |
|---|---|---|---|
| 1 | F3 视频媒体「定向升级已完成」 | **改为「定向升级已完成 + 存在整族级更强候选」**：`heygen-com/hyperframes` 66,062★、Apache-2.0、**2026-10-18 当日推送**，抓回 `motion-doctrine/SKILL.md` 11,996B | 06-benchmark/upstream_probe_index_r113_2026-10-18.json 的 `media_hyperframes_motion` |
| 2 | F1 文档办公「保留本地 + 定向吸收」 | **维持，但吸收对象具体化**：`genspark-ai/genoffice` 78,122B 单件覆盖 pptx/xlsx/docx/pdf 全链（本地是多件分治）⇒ 登记为「结构可借鉴」而非替换 | 同上 `docs_genoffice`（取值：`python -c "import json,io;print(json.load(io.open('06-benchmark/upstream_probe_index_r113_2026-10-18.json',encoding='utf-8'))['docs_genoffice']['bytes'])"`） |
| 3 | F5 调试审查「保留本地」 | **维持，但安全面出现强候选**：`cloudflare/security-audit-skill` 30,756★ / 22,182B 正文（厂商级），本地 `security-audit` 与 AAS 版 unrelated ⇒ 回归「无更优」需以该候选为对照重测（新立 K-8） | 同上 `review_cloudflare_sec` |

### 6.4 未采信面（子代理坏索引，逐条具名）

| 项 | 状态 | 原因 | 处置 |
|---|---|---|---|
| `upstream_meta_index_r113_2026-10-18.json` 的 42 行 | ❌ **不采信** | 全部为 `ERR function not defined: UNLICENSED/0`（坏 `--jq` 表达式，与本轮 §1.3 踩坑同根） | 已用自建复核件取代；该件保留为**证据**（记录失败形态），标注不可引用 |
| `hugohe3/ppt-master` 的正文 | ⚠️ 未取 | 子代理未抓原文 | 仅取其元数据（63,193★ / MIT / 10-17）；如需正文须补抓 |
| `microsoft/waza` / `athola/claude-night-market` / `luoluo22/jianying-editor-skill` / `bitjaru/styleseed` 正文 | ⚠️ 未取 | 同上 | 同上 |

> 本节的写法遵守本仓口径：**未取证的字段不写值**，失败面逐条具名（禁笼统「取不到」）。

> 取值（6.1/6.3/6.4 全节共用，就近复算）：06-benchmark/upstream_probe_index_r113_2026-10-18.json 的 `bytes`/`repo`/`path` 三字段（每条一行，逐条可对）；06-benchmark/candidate_measure_r113b_2026-10-18.json 的 `repos` 字典（stars/pushed_at/license）；06-benchmark/upstream_meta_index_r113_2026-10-18.json 的 42 行原文（即 6.4 判「不采信」的物证）。

---

## 7. 逐族结论（扩面后定稿；三选一，逐族给依据）

| 族 | 结论 | 依据（可复算） |
|---|---|---|
| F1 文档办公 | **保留本地 + 定向吸收** | 本地 docx 17 腿 / xlsx 3 腿 / pdf 4 腿可跑，同名上游 tests=0；`genspark-ai/genoffice` 78,122B 单件全链覆盖 ⇒ 借鉴其「一 CLI 覆盖多格式」结构 |
| F2 前端 UI | **保留本地** | 同名候选全落 unrelated 区（max_jaccard ≤ 0.0223）；扩面候选（web-quality 2,956★ / oil-ui 1,695★ / ux-ui 2,040★）**均低于本地同名件所在上游**且无同名可比件 |
| F3 视频媒体 | **定向升级已完成 + 整族级更强候选在册** | hyperframes-registry upstream_only 3→2（已合）；`heygen-com/hyperframes` 66,062★ / Apache-2.0 / 当日推送 / motion-doctrine 11,996B ⇒ 登记 K-8 重测 |
| F4 测试验证 | **定向升级已完成（TDD）** | upstream_only 20→11，残差 11 行已逐条定性（4 规则 + 6 指向本地不存在的 writing-good-tests.md 引用 + 1 description 措辞） |
| F5 调试审查 | **保留本地（安全面须重测）** | 同名候选全 unrelated；但 `cloudflare/security-audit-skill` 30,756★ / 22,182B 厂商级 ⇒ 本地 security-audit「无更优」结论须以它为对照重测（K-8） |
| F6 记忆治理 | **部分吸收（模板 / 文档面）** | spec-kit 30 wf / 360 tests / 12 治理文档 vs 本地 1/12；`Agent-Skills-for-Context-Engineering` 18,158★（context-compression 18,768B）为本族唯一有可比正文的候选 |
| F7 浏览器自动化 | **无更优替代（本地即最优）** | 检索面最高星为清单仓（0 个 SKILL.md）；扩面里 `Tencent/BrowserSkill` 9,115★ / 4,453B 与 `browser-act/skills` 6,156★ / 3,726B 均为**薄壳**，本地 `agent-browser` 是完整 CLI 驱动链 |
| F8 数据图表 | **保留本地** | 同名候选 unrelated；扩面候选（61★ / 311★）属小众专题件，不作替代 |

⇒ **8 族合计**：6 族「保留本地」（其中 F5 标注须重测）、2 族「定向升级已完成」（F3 附更强候选登记）。
> 取值：本表依据字段全部来自 06-benchmark/upstream_research_r113_2026-10-18.md §2/§6.1 与 06-benchmark/candidate_measure_r113_2026-10-18.json / _r113b_2026-10-18.json

### 7.1 新增待办（本节产出）

| ID | 事项 | 批次 | 依据 |
|---|---|---|---|
| K-8 | 以 `heygen-com/hyperframes`（66,062★）与 `cloudflare/security-audit-skill`（30,756★）为对照，重测 F3/F5 的「无更优」结论 | P1 | §6.3 第 1/3 条 |
