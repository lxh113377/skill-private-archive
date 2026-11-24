# 02 逐 skill 开源替代候选检索报告（需求 2）

> 任务 `t2` ｜ attempt `6b61d923-da4d-41db-a6dc-a4e7614fa51a` ｜ 角色 `oss-researcher` ｜ EVAL_DATE `2026-11-07` ｜ 365 天阈值 `2025-11-07`

> 机器可读母本：[data/candidates.json](data/candidates.json)（`t2-replacement-candidates-v1`）；覆盖判据：[02_candidates_check.py](02_candidates_check.py)。本文所有表由母本渲染，数字一律带取值命令与取值时刻。

> 纪律：阶段 0–3 **只读取证**，未改 `D:/global_skills` 下任何 `SKILL.md`；镜像 `_my-skills` / `.agents/skills` / `eval/` 只读；**未安装任何 skill**；R241 历史数字只加「校正注」，不改写旧报告。

---

## 1 结论摘要

| 判据 | 结果 | 取证 |
|---|---|---|
| 迁移范围分母 | **77** 件（HIGH 51 + MID 26） | t1 `data/inventory.json` 的 `denominator.definition`；LOW 30 灰区、EXCLUDE 43 市场/上游件不在迁移范围 |
| 逐件 3–5 候选 | **77/77 PASS**；共 **377** 条；分布 3 条×3、4 条×2、5 条×72 | `02_candidates_check.py` 正常态 `[CANDIDATES:PASS]` |
| 元数据现测 | **377/377 ✅已实测**（stars / pushed_at / license / archived / forks / open_issues） | `gh api repos/{OWNER}/{REPO}` 本轮现场取值，逐条带 `metadata_command` 与 `measured_at` |
| 维护/社区活跃筛选 | **377/377 active**；archived=0、pushed_at 早于 2025-11-07 = 0 | 判据从 `pushed_at`/`archived` **现场重算**，不采信候选自带标签 |
| 负向对照 | 塞入 `trimstray/test-your-sysadmin-skills`（pushed_at `2024-11-19`，718d）→ **判据报红**；活跃对照保留、archived 对照剔除 | `02_candidates_check.py --negative-control` → `[NEGCTRL:RED]` |
| 全量门禁 | **verdict=FAIL**（`FAIL=7 UNVERIFIED=3`；118 门 / 688029 ms） | 既有/他人在途/设计固有红如实登记，未删 tracked 件凑绿，不阻塞下游（R263/X-9）；写后复跑 118 门 / 885281 ms 同 verdict |

⚠️ **重要口径**：377 条并非 377 个「可直接替换结论」。
- **A 面 66 件 / 323 条**：r114 离线矩阵中 `rel=skill` 的逐件对应替代候选（✅已实测元数据；五维评分来自缓存快照，标 ⚠️部分实测）。
- **B 面 11 件 / 54 条**：语义缺口件的本轮定向 GitHub 检索线索，**元数据 ✅已实测、功能等价性 ❌未实测**，标「候选线索（元数据已实测，功能等价待复核）」，**不得自动升格为替代方案**，需需求 3 的五维矩阵与人工功能复核后再定。
- **族级补位 44 条**：`rel=family` 已隔离到 `family_pads` 且 `not_replacement=true`，按 r292 reading_rule **禁当替代方案引用**。
- **盲区 1 条**：`tradecatlabs/vibe-coding-cn` 现测 `gh: Not Found (HTTP 404)`，具名登记为 ❌未实测，未静默丢弃。

---

## 2 口径、分母与不可外推面

### 2.1 分母

- 清单分类面固定 150 = HIGH 51 + MID 26 + LOW 30 + EXCLUDE 43（`data/inventory.json` → `denominator.definition`）。
- 本任务「纳入迁移范围」= **自建维护口径 HIGH + MID = 77**；LOW 30 仍在册参与路由但属灰区，EXCLUDE 43 为市场/上游件，二者均不作替换分母。
- 现场对账：77 件全部命中 r114 离线矩阵（191 行），`MATRIX77=77 / MISSING=0`；清单 150 件中 146 件有矩阵行，4 件（`cloudbase__skillhub`、`executing-plans`、`pptx`、`slides`）无矩阵行且均不在 HIGH+MID，具名登记。
- 本轮 159 个去重候选仓的 live 实测**恰好全覆盖** 77 件范围的候选面（`SCOPE77_UNIQUE_REPOS=159 / NOT_IN_LIVE=0`）；若按全 150 件口径另需 61 仓、按全 191 行另需 81 仓，属不同面，不矛盾，本文只声明 77 面。

### 2.2 缺陷面（captain m00063 口径修正）

- ✅已实测：`known_defects` 有记录 **84/150**，其余 **66/150** 为空且 `defects_note` 为「未见逐件缺陷记录」。
- 那 66 件是「**无已知缺陷记录**」，**不是「零缺陷」**；本报告逐件标 `未记录（≠零缺陷）`，**不得**用它压低替代意愿，也**不得**把 84/150 外推为全量缺陷分母。

### 2.3 使用反馈面

- ⚠️部分实测：`outcome_unknown_share_pct=99.94`（`rows_total=3110`，`outcome_known_rows=2`，r289 读数）。只有声明加载量/路由计数，几乎无成败结果字段 ⇒ **不可**据此证明旧 skill 效果好或差，`never_seen` 也不是低价值证据。

### 2.4 活跃根漂移

- `D:/global_skills` 并行活跃根观测到 **243→247** 漂移（R269 只登记不擅动）。行数类读数一律现场取并附取值命令，**禁抄 inventory.json 快照当现状**。

### 2.5 取证标签

| 标签 | 含义 |
|---|---|
| ✅已实测 | 本轮 `gh api` 现场取值，带 `measured_at` 与取值命令 |
| ⚠️部分实测 | r114 / 06-benchmark 缓存值带 `fetched_at`，可能与现场值漂移（五维 score、缓存 stars） |
| ❌未实测 | 取证受阻（404）或功能等价性未验证，具名登记盲区 |

---

## 3 三面证据与读取规则

| 面 | 内容 | 证据路径 |
|---|---|---|
| A | r114 离线逐件候选矩阵（191 行；本范围 77 行），每条带 `rel` / `skill_md_n` / 五维 `score` / `verdict` | `_temp/r114_t2_verify.json`（`--offline --json`） |
| B | 11 件语义缺口的本轮定向 GitHub 检索二次现测线索 | `_temp/t2_directed_live.json`、`_temp/t2_gap_live.json`（61 仓 live 元数据 + tree `skill_md_n`） |
| C | r18 历史 14 个对标对象 + 6 个控制/社区线索本轮现测元数据 | `_temp/t2_benchmark_meta.json` |

**读取规则（r292）**：`自建skill优化/06-benchmark/r292_req2_compliance.json` —— `candidates_n` 满足条数不等于真有 3 个对应物；`rel=family` 补位件是族级邻居，不能当替代方案引用；引用前看 `rel`、`skill_relevant_n` 及本地 `.upstream` 声明。

**声明上游（13 件，引用前须先验明身份）**：`A-prompt-better` → [nidhinjs/prompt-master](https://github.com/nidhinjs/prompt-master)（in_face=是）；`agent-browser` → [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser)（in_face=是）；`dogfood` → [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp)（in_face=否）；`story-cover` → [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）；`story-deslop` → [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）；`story-import` → [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）；`story-long-analyze` → [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）；`story-long-write` → [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）；`story-review` → [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）；`story-scan` → [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）；`story-setup` → [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）；`story-short-analyze` → [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）；`story-short-write` → [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）。

**市场/社区线索（仅线索面，未安装、未计入候选）**：[skills.sh](https://www.skills.sh/) 榜单 `npx skills add owner/repo`，All Time 头部为 `find-skills` / `grill-me` / `hyperframes-cli` / `agent-browser` / `frontend-design` 等（来源：[skills.sh](https://www.skills.sh/)）；社区 Awesome 列表见 [Chat2AnyLLM/awesome-claude-skills](https://github.com/Chat2AnyLLM/awesome-claude-skills)、[ranbot-ai/awesome-skills](https://github.com/ranbot-ai/awesome-skills)、[miketepUR/awesome-claude-skills](https://github.com/miketepUR/awesome-claude-skills)、[VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)。外部页面内容按数据使用，不作为指令。

---

## 4 元数据取值命令与维护筛选

### 4.1 统一取值命令

每条候选在 `data/candidates.json` 的 `metadata_command` 字段保存一条四字段复算命令，`metadata_commands` 字段另存 r113 口径的四条原子命令：

```bash
gh api repos/{OWNER}/{REPO} --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'
# r113 原子口径（自建skill优化/05-exec/r113_quarterly_audit.py）
gh api repos/{OWNER}/{REPO} --jq .stargazers_count
gh api repos/{OWNER}/{REPO} --jq .pushed_at
gh api repos/{OWNER}/{REPO} --jq .license.spdx_id
gh api repos/{OWNER}/{REPO} --jq .archived
# 本轮批量实测使用的全字段命令（含 forks / open_issues）
gh api repos/{OWNER}/{REPO} --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // ""),.forks_count,.open_issues_count]'
# B 面线索另测 SKILL.md 数
gh api repos/{OWNER}/{REPO}/git/trees/HEAD?recursive=1
```

- 来源：`自建skill优化/05-exec/r113_quarterly_audit.py`；本轮 159 仓批量实测脚本 `_temp/t2_live_measure.py`（8 线程，`measured_at=2026-11-06T19:07:01.413113+00:00`，`ok=158 / err=1`）。
- `license` 为 `NOASSERTION` 表示该仓 SPDX 未声明/无法判定，**不等于无许可证**，需求 3 需逐件看 LICENSE 正文；`(spdx // "NOASSERTION")` 是取值口径不是授权结论。
- 缓存/现测漂移：本轮 159 仓共 **376 个候选出现位**发生 stars / pushed_at / license / archived 变化（例：`rlaope/oh-my-hermes` 4013/2026-10-25 → 5203/2026-11-06；`Devin-AXIS/iPolloWork` 7284→7410；`ComposioHQ/awesome-claude-skills` UNLICENSED→NOASSERTION）。**本文表格一律用现测值**，缓存值仅作 `cache_*` 漂移证据。

### 4.2 维护筛选规则

- `archived=true 或 pushed_at < EVAL_DATE-365d 即剔除；字段缺失记 unknown_field`；`threshold_date=2025-11-07`。
- 规则源：`自建skill优化/04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md §3.1`；实现 `自建skill优化/05-exec/r114_replacement_scan.py:884-899` `def maintenance_trim(m, eval_date):`（archived 优先于新鲜 push，返回 `archived` / `stale_pushed_at`）。
- 现测：`LIVE_HEALTH {active:158, unmeasured:1}`，158 个 OK 仓 pushed_at 范围 2026-01-26 … 2026-11-06；`archived=0 / stale_pushed_at=0 / pushed_unparsable=0`。
- r114 离线矩阵自身已先裁后出：`maintenance_face {archived_total:17, stale_total:65, trimmed_total:82, rows_affected:58, unknown_field_total:0}`，故离线输出中残留停摆件为 0。

### 4.3 r114 自证命令的写面偏移（如实登记）

- brief 要求 `python 05-exec/r114_replacement_scan.py --offline`；但 `自建skill优化/05-exec/r114_replacement_scan.py:1520-1525` 默认 `out = args.json_out or os.path.join(BENCH, "replacement_matrix_r114_%s.json" % date)`，裸跑会写 `06-benchmark/`，**越出本任务编号写面**。
- 本轮改为加 `--json _temp/r114_t2_verify.json`，产物只落 `_temp/`；命令与输出见 §5。此为执行形态偏移，**不是判据降级**。

---

## 5 覆盖自证、判据与门禁

### 5.1 三条自证命令（✅已实测）

**1）** `cd "自建skill优化" && PYTHONPYCACHEPREFIX=_temp/pycache_t2 "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" 05-exec/r114_replacement_scan.py --offline --json _temp/r114_t2_verify.json`

```text
RC=0 ｜ [REPL:PASS] 逐件候选面守恒 191==191 ｜ MATCHED=166 FAMILY_ONLY=12 NO_OS_CANDIDATE=8 UNVERIFIED=5；JSON -> _temp/r114_t2_verify.json
```

**2）** `cd "自建skill优化" && for r in anthropics/skills obra/superpowers rlaope/oh-my-hermes; do gh api repos/$r --jq "[.full_name,.stargazers_count,.pushed_at,.license.spdx_id,.archived,.description]"; done`

```text
RC=0 ｜ anthropics/skills 188113 / 2026-10-28T19:20:39Z / null；obra/superpowers 313516 / 2026-11-03T23:24:58Z / MIT；rlaope/oh-my-hermes 5203 / 2026-11-06T19:21:23Z / MIT（RC=0）
写后二次抽样（RC=0，stars 继续漂移）：anthropics/skills 188119 / 2026-10-28T19:20:39Z / NOASSERTION；obra/superpowers 313535 / 2026-11-03T23:24:58Z / MIT；rlaope/oh-my-hermes 5204 / 2026-11-06T20:08:01Z / MIT。⇒ 读数按 measured_at 快照，禁写成当前值。
```

**3）** `cd "自建skill优化" && PYTHONPYCACHEPREFIX=_temp/pycache_t2 "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" 05-exec/run_gates.py --json _temp/t2_gate_run.json --no-ledger --timeout 300`

```text
RC=1 ｜ [GATES:FAIL] FAIL=7 UNVERIFIED=3；118 门 / 688029 ms；verdict=FAIL；FAIL=7 UNVERIFIED=3
写后复跑（2026-11-07 04:26）：RC=1 ｜ [GATES:FAIL] FAIL=7 UNVERIFIED=3；118 门 / 885281 ms；verdict=FAIL（同 verdict、同红门清单）
```

### 5.2 覆盖判据（02_candidates_check.py）

```bash
cd "自建skill优化" && PYTHONPYCACHEPREFIX=_temp/pycache_t2 "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" deliverables/skill-modernization-r1/02_candidates_check.py
cd "自建skill优化" && PYTHONPYCACHEPREFIX=_temp/pycache_t2 "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" deliverables/skill-modernization-r1/02_candidates_check.py --negative-control
```

```text
[CANDIDATES:PASS] 分母=77 rows=77 逐件候选 3-5=True 元数据实测=377/377 取值命令=377/377 维护筛选=active 377/377 阈值=2025-11-07 族级补位未计入=True 负控配置=OK
NEGCTRL_LABEL trimstray/test-your-sysadmin-skills 标签=active 实算=stale_pushed_at（判据不采信标签）
NEGCTRL_ACTIVE rlaope/oh-my-hermes -> active（保留）
NEGCTRL_ARCHIVED PleasePrompto/notebooklm-skill -> archived（剔除）
[NEGCTRL:RED] 故意塞入停摆仓 trimstray/test-your-sysadmin-skills（pushed_at=2024-11-19T14:07:11Z，718d）后判据报红（符合预期）: 维护筛选剔除 trimstray/test-your-sysadmin-skills -> stale_pushed_at
```

判据检查项：schema / 分母 77 / 分类和 150 / 77 个唯一 HIGH+MID 行 / 逐件 3–5 且 `candidates_n` 自洽 / `metadata.state=OK` 且 stars·pushed_at·license 齐 / 四条原子 jq 命令齐 / ✅标签 / 无族级补位混入 / 维护筛选从 `pushed_at`·`archived` 重算 / 负控配置 / coverage 自洽 / ≥3 条自证 / 门禁 verdict 登记。

### 5.3 全量门禁（如实登记，不凑绿）

- `verdict=FAIL`；`verdict_reason=FAIL=7 UNVERIFIED=3`；`gates_run=118`，`total_ms=688029`。
- **写后复跑（校正注，不改写上一条历史读数）**：`generated_at=2026-11-07 04:26`，`118 门 / 885281 ms`，`[GATES:FAIL] FAIL=7 UNVERIFIED=3`；REAL_RED=9 / DESIGN_INHERENT_RED=1 / not_covered=3 与写前完全一致，02_* 产物未新增也未洗掉任何红门。取值：`_temp/t2_gate_run.json`（末次覆盖）。
- 真故障红 REAL_RED=9：`gov_acceptance_face`、`ratchet_gate`、`control_char_scan`、`refresh_budget_fixtures`、`budget_contract_fixtures`、`baseline_note_fixtures`、`pages_http_face`、`fixture_wiring_face`、`skill_wiring_face`；设计固有红 DESIGN_INHERENT_RED=1：`gate_run_freshness`。
- 未覆盖 `not_covered` 三项：受管根四门禁 mirror/noise/evolution/stub —— 属 rule_editor 面，取值：python D:\global_skills\A-memory-start\references\rule_editor.py gates；焚诀跨产物真值 C1~C33 —— 取值：python 焚诀\eval\verify_truth_consistency.py；判据变异测试（r19_fixture_mutation_check.py）—— 按需跑，非每轮前置。
- t1 同期为 `FAIL=7 / UNVERIFIED=2`；本轮 UNVERIFIED 增至 3。按 R263/X-9 均为既有/他人在途/设计固有红，**未删任何 tracked 件凑绿**，不阻塞下游需求 3。

---

## 6 负向对照（筛选有牙的自证）

| 类别 | 仓 | stars | pushed_at | license | archived | 期望 | 实测 |
|---|---|---:|---|---|---|---|---|
| 注入夹具（停摆） | [trimstray/test-your-sysadmin-skills](https://github.com/trimstray/test-your-sysadmin-skills) | 11898 | 2024-11-19T14:07:11Z | MIT | false | 剔除 | **`stale_pushed_at` → 判据 RED** |
| 备用停摆对照 | [PanJiaChen/vue-element-admin](https://github.com/PanJiaChen/vue-element-admin) | 90115 | 2024-10-24T11:25:46Z | MIT | false | 剔除 | `stale_pushed_at` |
| archived 对照 | [PleasePrompto/notebooklm-skill](https://github.com/PleasePrompto/notebooklm-skill) | 7784 | 2026-09-10T07:43:47Z | MIT | **true** | 剔除 | `archived`（优先于新鲜 push） |
| 活跃正控 | [rlaope/oh-my-hermes](https://github.com/rlaope/oh-my-hermes) | 5203 | 2026-11-06T18:11:33Z | MIT | false | 保留 | `active` |

- 负控夹具故意把 `maintenance` 标签写成 `active`，判据必须从 `pushed_at` 实算 365 天阈值才报红 —— 证明筛选不采信标签、不是恒绿。
- 检索面负控：查询 `zzzqqxxnotexistr260cd in:name,description,readme` → `total_count=0`（`state=OK`），证明定向检索通道返回真实结果而非恒有值。
- 机制复用：`maintenance_trim({"pushed_at":"2024-11-19","archived":False}, EVAL_DATE) => stale_pushed_at`；`2026-11-06 => None`；`2025-10-28 => None`；`2025-10-27 => stale_pushed_at`（r114 `EVAL_DATE=2026-10-28` 口径）。

---

## 7 逐 skill 候选（77 件）

> 表内 stars / forks / issues / pushed_at / license / archived 均为本轮 `gh api` 现测（✅已实测）；活跃度按 `pushed_at` 距 `2026-11-07` 天数实算；维护判定按 §4.2 现场重算。每条取值命令见各小节「取值命令与匹配理由」。B 面线索的「评分」列为线索分 `lead_score`，**不是**五维总分。

### 7.1 `9b-lightworkflow` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：hermes 中 qwen3.5:9b-agent 干杂活的轻量工作流（agent 能力增强包 + 项目轻记忆）。当用户在项目文件夹下用 hermes 拉起 9b 小模型干杂活（改文件/跑命令/查信息/验证），需要"轻记忆 + agent 能力"组合方案时使用。含模型选型铁律、增强包、轻记忆模板、A/B 验证法、踩坑速查。（desc_len=162；SKILL.md bytes=8832）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=3，skill_relevant_n=3，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [rlaope/oh-my-hermes](https://github.com/rlaope/oh-my-hermes) | 5203 | 413 / 12 | 2026-11-06T18:11:33Z | MIT | 活跃(0d) | `active` | 23/25 (fc5 eff5 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=274；The coding intelligence and skills for Hermes Agent ⚚ just install… |
| 2 | [Devin-AXIS/iPolloWork](https://github.com/Devin-AXIS/iPolloWork) | 7410 | 1135 / 91 | 2026-11-06T09:23:22Z | NOASSERTION | 活跃(1d) | `active` | 18/25 (fc5 eff5 compat1 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=1/5；SKILL.md=109；Enterprise-grade, local-first Agent Workbench for people and agent… |
| 3 | [lennney/stop-that-shit](https://github.com/lennney/stop-that-shit) | 3693 | 76 / 4 | 2026-11-05T12:35:36Z | MIT | 活跃(1d) | `active` | 16/25 (fc2 eff3 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Stop That Shit（别再造史了）｜面向 Codex/GPT 场景的多平台 Hook + Skill Guard：拦截 AI c… |

**取值命令与匹配理由**
1. `rlaope/oh-my-hermes` — `gh api repos/rlaope/oh-my-hermes --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=274；The coding intelligence and skills for Hermes Agent ⚚ just install once. then type 'dag-ulw' to be g ｜ ⚠️缓存→现测：4013/2026-10-25/MIT → 5203/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=274
2. `Devin-AXIS/iPolloWork` — `gh api repos/Devin-AXIS/iPolloWork --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=1/5；SKILL.md=109；Enterprise-grade, local-first Agent Workbench for people and agent teams. A unified multi-engine wor ｜ ⚠️缓存→现测：7284/2026-10-24/NOASSERTION → 7410/2026-11-06T0…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=109
3. `lennney/stop-that-shit` — `gh api repos/lennney/stop-that-shit --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Stop That Shit（别再造史了）｜面向 Codex/GPT 场景的多平台 Hook + Skill Guard：拦截 AI coding agent 无需求的哈希、校验和与任务范围膨胀。 A ｜ ⚠️缓存→现测：3142/2026-10-24/MIT → 3693/2026-11-05T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=2

### 7.2 `A-ask-questions` ｜ HIGH ｜ 候选线索（元数据已实测，功能等价待复核）

- **功能边界**：复杂任务的自决分诊引擎（V3.4.0 · #48）：轮次轴已取消——任何对话任何轮次一律自行拍板并执行，不把决策回抛给老大；老大当轮明说「问我/等挑/先别动」是唯一例外。四类重大按客观条件分流：能做直接做、办不到列待办带实测卡点——当对话开场、需求模糊、方案多解、改动≥3文件或含破坏性动作时触发使用。（desc_len=151；SKILL.md bytes=19426）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：FAMILY_ONLY（candidates_n=5，skill_relevant_n=2，trim=1） ｜ **语义缺口**：是 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：[affaan-m/ECC](https://github.com/affaan-m/ECC)、[morluto/rea](https://github.com/morluto/rea)、[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)（共 3 件，`not_replacement=true`）

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [mattpocock/skills](https://github.com/mattpocock/skills) | 316517 | 26478 / 217 | 2026-11-05T10:40:01Z | MIT | 活跃(2d) | `active` | 线索分 10 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=39；stars=316517；description=Skills for Real Engineers. Straight from my .agents directory. |
| 2 | [obra/superpowers](https://github.com/obra/superpowers) | 313528 | 27892 / 340 | 2026-11-03T23:24:58Z | MIT | 活跃(3d) | `active` | 线索分 10 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=15；stars=313528；description=An agentic skills framework & software development methodology tha… |
| 3 | [anthropics/skills](https://github.com/anthropics/skills) | 188117 | 22190 / 1484 | 2026-10-28T19:20:39Z | NOASSERTION | 活跃(9d) | `active` | 线索分 10 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=20；stars=188117；description=Public repository for Agent Skills |
| 4 | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | 143461 | 13720 / 1645 | 2026-11-06T17:11:19Z | Apache-2.0 | 活跃(0d) | `active` | 线索分 10 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=1；stars=143461；description=Turn any codebase, with its docs, SQL schemas, configs, and PDFs, i… |
| 5 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 113707 | 11885 / 130 | 2026-11-01T19:24:49Z | MIT | 活跃(5d) | `active` | 线索分 10 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=25；stars=113707；description=Production-grade engineering skills for AI coding agents. |

**取值命令与匹配理由**
1. `mattpocock/skills` — `gh api repos/mattpocock/skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=39；stars=316517；description=Skills for Real Engineers. Straight from my .agents directory. ｜ SKILL.md=39 ｜ `gh api repos/mattpocock/skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
2. `obra/superpowers` — `gh api repos/obra/superpowers --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=15；stars=313528；description=An agentic skills framework & software development methodology that works. ｜ SKILL.md=15 ｜ `gh api repos/obra/superpowers/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
3. `anthropics/skills` — `gh api repos/anthropics/skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=20；stars=188117；description=Public repository for Agent Skills ｜ SKILL.md=20 ｜ `gh api repos/anthropics/skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
4. `Graphify-Labs/graphify` — `gh api repos/Graphify-Labs/graphify --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=1；stars=143461；description=Turn any codebase, with its docs, SQL schemas, configs, and PDFs, into a queryable knowledge graph. A /graphify skill for Claude Code, Curso ｜ SKILL.md=1 ｜ `gh api repos/Graphify-Labs/graphify/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
5. `addyosmani/agent-skills` — `gh api repos/addyosmani/agent-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=25；stars=113707；description=Production-grade engineering skills for AI coding agents. ｜ SKILL.md=25 ｜ `gh api repos/addyosmani/agent-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`

### 7.3 `A-get-memory` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：任务后经验反哺引擎。四维度反思+经验分类路由+已有Skill升级检查+漏用Skill审计(根因定位→自解→修复→验证闭环)+用户画像增量更新+项目经验总结(冷启动续接摘要)+技能自我进化(全树自检+经验反哺闭环+进化账本)。每次实质性任务完成后自动触发，确保踩坑经验不流失；V4.6.0 起含 Step9 遗忘/retire 衰减（引用 retire_policy.md，补记忆第四动作防只写不忘）。（desc_len=200；SKILL.md bytes=13020）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=11，trim=1） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 298441 | 44116 / 236 | 2026-11-06T05:29:44Z | MIT | 活跃(1d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instin… |
| 2 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 81071 | 9543 / 654 | 2026-11-06T18:31:29Z | MIT | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swa… |
| 3 | [mksglu/context-mode](https://github.com/mksglu/context-mode) | 33601 | 2306 / 3 | 2026-11-06T15:43:52Z | NOASSERTION | 活跃(0d) | `active` | 21/25 (fc4 eff5 compat4 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=4/5；SKILL.md=11；Context window optimization for AI coding agents. Sandboxes tool ou… |
| 4 | [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) | 18315 | 1510 / 58 | 2026-10-12T02:06:40Z | MIT | 活跃(26d) | `active` | 19/25 (fc4 eff2 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；A comprehensive collection of Agent Skills for context engineering,… |
| 5 | [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) | 30573 | 2983 / 887 | 2026-11-04T11:33:40Z | NOASSERTION | 活跃(3d) | `active` | 16/25 (fc2 eff2 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；TencentDB Agent Memory is a team-level memory hub for AI Agents — tu… |

**取值命令与匹配理由**
1. `affaan-m/ECC` — `gh api repos/affaan-m/ECC --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instincts, memory, security, and research ｜ ⚠️缓存→现测：288271/2026-10-20/MIT → 298441/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1062
2. `ruvnet/ruflo` — `gh api repos/ruvnet/ruflo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swarms, coordinate autonomous workflo ｜ ⚠️缓存→现测：79103/2026-10-25/MIT → 81071/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=389
3. `mksglu/context-mode` — `gh api repos/mksglu/context-mode --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=4/5；SKILL.md=11；Context window optimization for AI coding agents. Sandboxes tool output (98% reduction), persists se ｜ ⚠️缓存→现测：32150/2026-10-24/NOASSERTION → 33601/2026-11-06T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=11
4. `muratcankoylan/Agent-Skills-for-Context-Engineering` — `gh api repos/muratcankoylan/Agent-Skills-for-Context-Engineering --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；A comprehensive collection of Agent Skills for context engineering, multi-agent architectures, and p ｜ ⚠️缓存→现测：18208/2026-10-12/MIT → 18315/2026-10-12T0…/MIT（stars 漂移） ｜ SKILL.md=24
5. `TencentCloud/TencentDB-Agent-Memory` — `gh api repos/TencentCloud/TencentDB-Agent-Memory --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；TencentDB Agent Memory is a team-level memory hub for AI Agents — turning conversations, docs, and c ｜ ⚠️缓存→现测：29900/2026-10-21/NOASSERTION → 30573/2026-11-04T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=2

### 7.4 `A-java-problem` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：课程编程作业与练习总入口（Java 主线 + C++ 分支，龙虾自建，2026-09-07；C++ 分支 2026-10-12 并入）。Java 触发词：Java作业、Java练习、写个Java程序、javac、java编译运行报错、语法基础、面向对象/OOP/类与对象、集合/List/Map、异常处理、IO/文件读写、多线程、Swing、Java实验/实训/实验报告。C++ 触发词：C++作业、C++练习、约瑟夫问题、g++、MinG（desc_len=447；SKILL.md bytes=14494）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [SeleniumHQ/selenium](https://github.com/SeleniumHQ/selenium) | 34576 | 8727 / 190 | 2026-11-06T15:00:41Z | Apache-2.0 | 活跃(0d) | `active` | 17/25 (fc1 eff5 compat3 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；A browser automation framework and ecosystem. |
| 2 | [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | 78931 | 9588 / 1885 | 2026-09-18T07:16:11Z | NOASSERTION | 活跃(50d) | `active` | 17/25 (fc5 eff1 compat3 docs3 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=3/5；SKILL.md=864；A curated list of awesome Claude Skills, resources, and tools for … |
| 3 | [Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide) | 159454 | 46129 / 21 | 2026-10-25T11:47:10Z | Apache-2.0 | 活跃(13d) | `active` | 15/25 (fc1 eff1 compat3 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=1；Java 面试 & 后端通用面试指南，覆盖计算机基础、数据库、分布式、高并发、系统设计与 AI 应用开发 |
| 4 | [composio-community/awesome-codex-skills](https://github.com/composio-community/awesome-codex-skills) | 17228 | 1747 / 331 | 2026-07-26T01:14:54Z | NOASSERTION | 一般(104d) | `active` | 15/25 (fc5 eff0 compat3 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=3/5；SKILL.md=880；A curated list of practical Codex skills for automating workflows … |
| 5 | [jeecgboot/JeecgBoot](https://github.com/jeecgboot/JeecgBoot) | 48390 | 16219 / 7 | 2026-11-05T14:34:39Z | Apache-2.0 | 活跃(1d) | `active` | 13/25 (fc1 eff2 compat3 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；【低代码v2.0，一句话即可生成整个系统】企业级AI低代码平台，一键生成前后端代码甚至整个系统。 AI Skills 一句话画流程、设计… |

**取值命令与匹配理由**
1. `SeleniumHQ/selenium` — `gh api repos/SeleniumHQ/selenium --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；A browser automation framework and ecosystem. ｜ ⚠️缓存→现测：34565/2026-10-25/Apache-2.0 → 34576/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=0
2. `ComposioHQ/awesome-claude-skills` — `gh api repos/ComposioHQ/awesome-claude-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=3/5；SKILL.md=864；A curated list of awesome Claude Skills, resources, and tools for customizing Claude AI workflows ｜ ⚠️缓存→现测：77869/2026-09-18/UNLICENSED → 78931/2026-09-18T0…/NOASSERTION（stars,license 漂移） ｜ SKILL.md=864
3. `Snailclimb/JavaGuide` — `gh api repos/Snailclimb/JavaGuide --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=1；Java 面试 & 后端通用面试指南，覆盖计算机基础、数据库、分布式、高并发、系统设计与 AI 应用开发 ｜ ⚠️缓存→现测：159237/2026-10-16/Apache-2.0 → 159454/2026-10-25T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=1
4. `composio-community/awesome-codex-skills` — `gh api repos/composio-community/awesome-codex-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=3/5；SKILL.md=880；A curated list of practical Codex skills for automating workflows across the Codex CLI and API. ｜ ⚠️缓存→现测：17036/2026-07-26/UNLICENSED → 17228/2026-07-26T0…/NOASSERTION（stars,license 漂移） ｜ SKILL.md=880
5. `jeecgboot/JeecgBoot` — `gh api repos/jeecgboot/JeecgBoot --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；【低代码v2.0，一句话即可生成整个系统】企业级AI低代码平台，一键生成前后端代码甚至整个系统。 AI Skills 一句话画流程、设计表单、生成报表、大屏。内置 AI应用平台涵盖：AI聊天、知识库、 ｜ ⚠️缓存→现测：48276/2026-10-24/Apache-2.0 → 48390/2026-11-05T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=0

### 7.5 `A-memory-start` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：全局记忆入口加载 — 目录索引式按需加载全局记忆。全局记忆启动门禁 Directory-indexed on-demand global memory loader + 执行契约门禁 for HM / WB / CX / TC / ZC. 统一权威源 D:\global_memory\。复杂任务先自然语言+追问澄清需求，再查全局记忆+skill tree按需加载相关skill， 只加载所需内容减少算力浪费。 L1 (MEMORY/SOU（desc_len=986；SKILL.md bytes=12453）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=11，trim=1） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 298441 | 44116 / 236 | 2026-11-06T05:29:44Z | MIT | 活跃(1d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instin… |
| 2 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 81071 | 9543 / 654 | 2026-11-06T18:31:29Z | MIT | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swa… |
| 3 | [mksglu/context-mode](https://github.com/mksglu/context-mode) | 33601 | 2306 / 3 | 2026-11-06T15:43:52Z | NOASSERTION | 活跃(0d) | `active` | 21/25 (fc4 eff5 compat4 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=4/5；SKILL.md=11；Context window optimization for AI coding agents. Sandboxes tool ou… |
| 4 | [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) | 18315 | 1510 / 58 | 2026-10-12T02:06:40Z | MIT | 活跃(26d) | `active` | 19/25 (fc4 eff2 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；A comprehensive collection of Agent Skills for context engineering,… |
| 5 | [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) | 30573 | 2983 / 887 | 2026-11-04T11:33:40Z | NOASSERTION | 活跃(3d) | `active` | 16/25 (fc2 eff2 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；TencentDB Agent Memory is a team-level memory hub for AI Agents — tu… |

**取值命令与匹配理由**
1. `affaan-m/ECC` — `gh api repos/affaan-m/ECC --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instincts, memory, security, and research ｜ ⚠️缓存→现测：288271/2026-10-20/MIT → 298441/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1062
2. `ruvnet/ruflo` — `gh api repos/ruvnet/ruflo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swarms, coordinate autonomous workflo ｜ ⚠️缓存→现测：79103/2026-10-25/MIT → 81071/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=389
3. `mksglu/context-mode` — `gh api repos/mksglu/context-mode --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=4/5；SKILL.md=11；Context window optimization for AI coding agents. Sandboxes tool output (98% reduction), persists se ｜ ⚠️缓存→现测：32150/2026-10-24/NOASSERTION → 33601/2026-11-06T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=11
4. `muratcankoylan/Agent-Skills-for-Context-Engineering` — `gh api repos/muratcankoylan/Agent-Skills-for-Context-Engineering --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；A comprehensive collection of Agent Skills for context engineering, multi-agent architectures, and p ｜ ⚠️缓存→现测：18208/2026-10-12/MIT → 18315/2026-10-12T0…/MIT（stars 漂移） ｜ SKILL.md=24
5. `TencentCloud/TencentDB-Agent-Memory` — `gh api repos/TencentCloud/TencentDB-Agent-Memory --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；TencentDB Agent Memory is a team-level memory hub for AI Agents — turning conversations, docs, and c ｜ ⚠️缓存→现测：29900/2026-10-21/NOASSERTION → 30573/2026-11-04T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=2

### 7.6 `A-project-better` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：项目方向优化器 — 解决开发者对项目后续开发方向迷茫的问题。强制前置「遗留待办盘点」：先扫 memory/07-next-steps（含分卷）、TODO.md、上次未执行区等未完成事项，逐条实测核验并经用户确认，再五源感知（含「判据输入端」：本机绿而 CI 红先比对两侧输入，别先怀疑判据逻辑）+ 六维诊断（功能/技术债/架构/文档交付/体量/前端），产出 P0/P1/P2 建议清单（对账不漏不重，标执行属性），用户挑选或预授权后执行并回（desc_len=717；SKILL.md bytes=8159）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 298441 | 44116 / 236 | 2026-11-06T05:29:44Z | MIT | 活跃(1d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instin… |
| 2 | [nexu-io/open-design](https://github.com/nexu-io/open-design) | 106289 | 12099 / 1371 | 2026-11-06T15:40:39Z | Apache-2.0 | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and o… |
| 3 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 81071 | 9543 / 654 | 2026-11-06T18:31:29Z | MIT | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swa… |
| 4 | [latent-spaces/brag](https://github.com/latent-spaces/brag) | 20537 | 1590 / 17 | 2026-10-23T21:18:13Z | MIT | 活跃(14d) | `active` | 14/25 (fc2 eff0 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；You built it. Now brag. Turn the project you just created into a sho… |
| 5 | [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) | 10821 | 692 / 0 | 2026-11-05T00:59:21Z | MIT | 活跃(2d) | `active` | 14/25 (fc2 eff0 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent skill that generates rich HTML pages or slide decks for diagra… |

**取值命令与匹配理由**
1. `affaan-m/ECC` — `gh api repos/affaan-m/ECC --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instincts, memory, security, and research ｜ ⚠️缓存→现测：288271/2026-10-20/MIT → 298441/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1062
2. `nexu-io/open-design` — `gh api repos/nexu-io/open-design --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and open source. Create motion, prototy ｜ ⚠️缓存→现测：103811/2026-10-25/Apache-2.0 → 106289/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=553
3. `ruvnet/ruflo` — `gh api repos/ruvnet/ruflo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swarms, coordinate autonomous workflo ｜ ⚠️缓存→现测：79103/2026-10-25/MIT → 81071/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=389
4. `latent-spaces/brag` — `gh api repos/latent-spaces/brag --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；You built it. Now brag. Turn the project you just created into a short, shareable launch video with ｜ ⚠️缓存→现测：18425/2026-10-23/MIT → 20537/2026-10-23T2…/MIT（stars 漂移） ｜ SKILL.md=2
5. `nicobailon/visual-explainer` — `gh api repos/nicobailon/visual-explainer --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent skill that generates rich HTML pages or slide decks for diagrams, diff reviews, plan audits, d ｜ ⚠️缓存→现测：10620/2026-10-20/MIT → 10821/2026-11-05T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.7 `A-project-handoff` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：项目记忆管理系统 — 每个项目内建 memory/ 目录（9个结构化记忆文件）+ 混合模式阶段归档 + 回滚恢复 + AI首次加载引导；并承载跨项目「CI 全绿契约」（greencheck.py：四态 GREEN/RED/BLOCKED/UNKNOWN + .ci/contract.json + pre-push 接线 + 通知静音判据：静音态读回 GitHub、裸静音判红）；并承载**工作区体量治理**（handoff.py volu（desc_len=400；SKILL.md bytes=20526）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 298441 | 44116 / 236 | 2026-11-06T05:29:44Z | MIT | 活跃(1d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instin… |
| 2 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 81071 | 9543 / 654 | 2026-11-06T18:31:29Z | MIT | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swa… |
| 3 | [mksglu/context-mode](https://github.com/mksglu/context-mode) | 33601 | 2306 / 3 | 2026-11-06T15:43:52Z | NOASSERTION | 活跃(0d) | `active` | 21/25 (fc4 eff5 compat4 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=4/5；SKILL.md=11；Context window optimization for AI coding agents. Sandboxes tool ou… |
| 4 | [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) | 18315 | 1510 / 58 | 2026-10-12T02:06:40Z | MIT | 活跃(26d) | `active` | 19/25 (fc4 eff2 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；A comprehensive collection of Agent Skills for context engineering,… |
| 5 | [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) | 30573 | 2983 / 887 | 2026-11-04T11:33:40Z | NOASSERTION | 活跃(3d) | `active` | 16/25 (fc2 eff2 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；TencentDB Agent Memory is a team-level memory hub for AI Agents — tu… |

**取值命令与匹配理由**
1. `affaan-m/ECC` — `gh api repos/affaan-m/ECC --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instincts, memory, security, and research ｜ ⚠️缓存→现测：288271/2026-10-20/MIT → 298441/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1062
2. `ruvnet/ruflo` — `gh api repos/ruvnet/ruflo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swarms, coordinate autonomous workflo ｜ ⚠️缓存→现测：79103/2026-10-25/MIT → 81071/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=389
3. `mksglu/context-mode` — `gh api repos/mksglu/context-mode --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=4/5；SKILL.md=11；Context window optimization for AI coding agents. Sandboxes tool output (98% reduction), persists se ｜ ⚠️缓存→现测：32150/2026-10-24/NOASSERTION → 33601/2026-11-06T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=11
4. `muratcankoylan/Agent-Skills-for-Context-Engineering` — `gh api repos/muratcankoylan/Agent-Skills-for-Context-Engineering --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；A comprehensive collection of Agent Skills for context engineering, multi-agent architectures, and p ｜ ⚠️缓存→现测：18208/2026-10-12/MIT → 18315/2026-10-12T0…/MIT（stars 漂移） ｜ SKILL.md=24
5. `TencentCloud/TencentDB-Agent-Memory` — `gh api repos/TencentCloud/TencentDB-Agent-Memory --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；TencentDB Agent Memory is a team-level memory hub for AI Agents — turning conversations, docs, and c ｜ ⚠️缓存→现测：29900/2026-10-21/NOASSERTION → 30573/2026-11-04T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=2

### 7.8 `A-prompt-better` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：Prompt优化器 — 自动按业界最佳实践优化用户提示词。Prompt自动优化 Prompt 优化器——加载后自动将用户发给 AI 的提示词按业界最佳实践优化润色， 再交给 agent 执行。适用于所有需要高质量 prompt 输出的场景。 **自动执行：被调用后立即对当前 user query 走优化流程，无需等待用户二次确认。** 纯闲聊/问候/确认(如"执行"/"好的"/"继续")时跳过。 NOT a general chat s（desc_len=390；SKILL.md bytes=35594）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：[nidhinjs/prompt-master](https://github.com/nidhinjs/prompt-master)（in_face=是）
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | 117973 | 6860 / 69 | 2026-11-06T11:35:30Z | Apache-2.0 | 活跃(1d) | `active` | 23/25 (fc4 eff5 compat5 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=28；🪨 why use many token when few token do trick. Viral skill + proxy … |
| 2 | [github/awesome-copilot](https://github.com/github/awesome-copilot) | 40873 | 5304 / 45 | 2026-11-06T13:41:04Z | MIT | 活跃(0d) | `active` | 22/25 (fc5 eff4 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=466；Community-contributed instructions, agents, skills, and configurat… |
| 3 | [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) | 24649 | 2139 / 169 | 2026-11-06T13:40:16Z | Apache-2.0 | 活跃(0d) | `active` | 22/25 (fc4 eff5 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=33；Security scanner for AI agent skills. Detect vulnerabilities, malic… |
| 4 | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | 185753 | 10280 / 183 | 2026-10-29T11:59:31Z | MIT | 活跃(9d) | `active` | 20/25 (fc4 eff3 compat5 docs3 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Makes your AI agent think like the laziest senior dev in the room. … |
| 5 | [nidhinjs/prompt-master](https://github.com/nidhinjs/prompt-master) | 15601 | 1802 / 30 | 2026-10-22T13:26:18Z | MIT | 活跃(15d) | `active` | 14/25 (fc2 eff0 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A Claude skill that writes the accurate prompts for any AI tool. Zer… |

**取值命令与匹配理由**
1. `JuliusBrussee/caveman` — `gh api repos/JuliusBrussee/caveman --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=28；🪨 why use many token when few token do trick. Viral skill + proxy for coding agents that cuts 65% o ｜ ⚠️缓存→现测：114863/2026-10-25/Apache-2.0 → 117973/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=28
2. `github/awesome-copilot` — `gh api repos/github/awesome-copilot --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=466；Community-contributed instructions, agents, skills, and configurations to help you make the most of ｜ ⚠️缓存→现测：40592/2026-10-30/MIT → 40873/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=466
3. `NVIDIA/SkillSpector` — `gh api repos/NVIDIA/SkillSpector --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=33；Security scanner for AI agent skills. Detect vulnerabilities, malicious patterns, security risks, pr ｜ ⚠️缓存→现测：21398/2026-10-23/Apache-2.0 → 24649/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=33
4. `DietrichGebert/ponytail` — `gh api repos/DietrichGebert/ponytail --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Makes your AI agent think like the laziest senior dev in the room. The best code is the code you nev ｜ ⚠️缓存→现测：175668/2026-10-18/MIT → 185753/2026-10-29T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=13
5. `nidhinjs/prompt-master` — `gh api repos/nidhinjs/prompt-master --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A Claude skill that writes the accurate prompts for any AI tool. Zero tokens or credits wasted. Full ｜ ⚠️缓存→现测：15287/2026-10-22/MIT → 15601/2026-10-22T1…/MIT（stars 漂移） ｜ SKILL.md=1

### 7.9 `A-skill-manager` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：技能全生命周期唯一总管——增/删/改/合并/上架/九端同步/依赖安装/安全审计、注册漂移、路由命中率一站式；触发词质量差需要重生、触发词重生、路由触发词优化亦属本件。当对话中出现主动增删改技能、装删技能、技能不生效、注册漂移、命中率诊断、技能安全审计等任何技能管理意图时加载。触发：加技能、删技能、改技能、合并技能、装技能、技能上架、skill注册、技能同步、技能漂移、命中率、触发词质量差、触发词重生、技能安全、skill依赖、技能清理、（desc_len=292；SKILL.md bytes=10712）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 298441 | 44116 / 236 | 2026-11-06T05:29:44Z | MIT | 活跃(1d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instin… |
| 2 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 81071 | 9543 / 654 | 2026-11-06T18:31:29Z | MIT | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swa… |
| 3 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 113914 | 9885 / 125 | 2026-11-06T18:15:53Z | Apache-2.0 | 活跃(0d) | `active` | 24/25 (fc4 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Persistent Context Across Sessions for Every Agent –  Captures ever… |
| 4 | [topoteretes/cognee](https://github.com/topoteretes/cognee) | 33114 | 3473 / 1101 | 2026-11-06T18:57:58Z | Apache-2.0 | 活跃(0d) | `active` | 22/25 (fc4 eff5 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=23；Cognee is the open-source AI memory platform for agents. Give your … |
| 5 | [MemTensor/MemOS](https://github.com/MemTensor/MemOS) | 12302 | 1111 / 152 | 2026-11-04T06:42:18Z | Apache-2.0 | 活跃(3d) | `active` | 22/25 (fc3 eff5 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Self-evolving memory OS for LLM & AI Agents: ultra-persistent memory… |

**取值命令与匹配理由**
1. `affaan-m/ECC` — `gh api repos/affaan-m/ECC --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instincts, memory, security, and research ｜ ⚠️缓存→现测：288271/2026-10-20/MIT → 298441/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1062
2. `ruvnet/ruflo` — `gh api repos/ruvnet/ruflo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swarms, coordinate autonomous workflo ｜ ⚠️缓存→现测：79103/2026-10-25/MIT → 81071/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=389
3. `thedotmack/claude-mem` — `gh api repos/thedotmack/claude-mem --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Persistent Context Across Sessions for Every Agent –  Captures everything your agent does during ses ｜ ⚠️缓存→现测：102894/2026-10-25/Apache-2.0 → 113914/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=43
4. `topoteretes/cognee` — `gh api repos/topoteretes/cognee --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=23；Cognee is the open-source AI memory platform for agents. Give your AI agents persistent long-term me ｜ ⚠️缓存→现测：32728/2026-10-23/Apache-2.0 → 33114/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=23
5. `MemTensor/MemOS` — `gh api repos/MemTensor/MemOS --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Self-evolving memory OS for LLM & AI Agents: ultra-persistent memory, hybrid-retrieval, and cross-ta ｜ ⚠️缓存→现测：12081/2026-10-24/Apache-2.0 → 12302/2026-11-04T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=7

### 7.10 `agent-browser` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：浏览器自动化 CLI（agent-browser / npx agent-browser）。核心用法：snapshot-and-ref 工作流、命令链式执行、登录与鉴权、流式输出、批量跑页面、截图/录像、tab 并行会话、a11y 审计。Use when 需要驱动浏览器完成点击/填表/截图/多页批量操作，或复用已登录会话。不适用：桌面应用自动化（走 electron）。（desc_len=186；SKILL.md bytes=8389）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：[vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser)（in_face=是）
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | 46281 | 3170 / 494 | 2026-11-06T18:01:53Z | Apache-2.0 | 活跃(0d) | `active` | 19/25 (fc4 eff3 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=11；Browser automation CLI for AI agents |
| 2 | [browser-act/skills](https://github.com/browser-act/skills) | 6325 | 343 / 11 | 2026-11-04T10:27:29Z | MIT | 活跃(3d) | `active` | 18/25 (fc5 eff1 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=103；Browser automation CLI built for AI agents. Break through anti-bot… |
| 3 | [browser-use/browser-harness](https://github.com/browser-use/browser-harness) | 18905 | 1865 / 440 | 2026-11-06T00:07:22Z | MIT | 活跃(1d) | `active` | 17/25 (fc3 eff2 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=3；Let Claude Code, Codex or Cursor use your real Chrome, logged in as … |
| 4 | [mxschmitt/playwright-go](https://github.com/mxschmitt/playwright-go) | 3539 | 250 / 5 | 2026-11-05T21:59:51Z | MIT | 活跃(1d) | `active` | 17/25 (fc2 eff4 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Playwright for Go a browser automation library to control Chromium, … |
| 5 | [SawyerHood/dev-browser](https://github.com/SawyerHood/dev-browser) | 6723 | 439 / 22 | 2026-11-03T21:31:14Z | MIT | 活跃(3d) | `active` | 16/25 (fc2 eff3 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A Claude Skill to give your agent the ability to use a web browser |

**取值命令与匹配理由**
1. `vercel-labs/agent-browser` — `gh api repos/vercel-labs/agent-browser --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=11；Browser automation CLI for AI agents ｜ ⚠️缓存→现测：44898/2026-10-30/Apache-2.0 → 46281/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=11
2. `browser-act/skills` — `gh api repos/browser-act/skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=103；Browser automation CLI built for AI agents. Break through anti-bot walls, hand off to humans across ｜ ⚠️缓存→现测：6273/2026-08-24/MIT → 6325/2026-11-04T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=103
3. `browser-use/browser-harness` — `gh api repos/browser-use/browser-harness --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=3；Let Claude Code, Codex or Cursor use your real Chrome, logged in as you. One prompt to set up. Open ｜ ⚠️缓存→现测：18600/2026-10-25/MIT → 18905/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=3
4. `mxschmitt/playwright-go` — `gh api repos/mxschmitt/playwright-go --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Playwright for Go a browser automation library to control Chromium, Firefox and WebKit with a single ｜ ⚠️缓存→现测：3531/2026-09-14/MIT → 3539/2026-11-05T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=2
5. `SawyerHood/dev-browser` — `gh api repos/SawyerHood/dev-browser --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A Claude Skill to give your agent the ability to use a web browser ｜ ⚠️缓存→现测：6695/2026-10-18/MIT → 6723/2026-11-03T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.11 `audio-deliverable-pipeline` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：音频交付流水线（语音旁白 / 主题音乐 / 可选 MP4）— 固化「local-tts 不可用 → edge-tts 降级 + lameenc 编码 + mutagen/波形双核验」链路。触发：生成语音/旁白/TTS、生成音乐/BGM、作业音频交付、要求 MP3 音频文件。（desc_len=137；SKILL.md bytes=8345）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=10，trim=2） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [scenario-labs/skills](https://github.com/scenario-labs/skills) | 3388 | 292 / 38 | 2026-11-06T18:04:56Z | MIT | 活跃(0d) | `active` | 22/25 (fc5 eff5 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=173；Get production-ready images, video, audio, and 3D from any AI agen… |
| 2 | [wiltodelta/remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks) | 6295 | 588 / 2 | 2026-11-06T01:27:32Z | Apache-2.0 | 活跃(1d) | `active` | 20/25 (fc3 eff4 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Remove visible and invisible AI watermarks from images and video, an… |
| 3 | [LnYo-Cly/ai4j](https://github.com/LnYo-Cly/ai4j) | 438 | 56 / 5 | 2026-10-13T17:22:47Z | Apache-2.0 | 活跃(24d) | `active` | 19/25 (fc3 eff5 compat5 docs4 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=5；Java 8+ agentic SDK: unified LLM access (OpenAI/Anthropic/DashScope/… |
| 4 | [EGSECDA/vocaloid-style-mv-pipeline](https://github.com/EGSECDA/vocaloid-style-mv-pipeline) | 250 | 18 / 0 | 2026-11-04T08:41:28Z | MIT | 活跃(3d) | `active` | 12/25 (fc2 eff0 compat5 docs3 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Production pipeline and Claude Code skill for Vocaloid-style hand-dr… |
| 5 | [equalang/equalang-skill](https://github.com/equalang/equalang-skill) | 78 | 0 / 0 | 2026-11-03T07:35:58Z | Apache-2.0 | 活跃(4d) | `active` | 12/25 (fc2 eff1 compat5 docs3 comm1) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent Skill for Equalang: translate PDF, DOCX, PPTX, XLSX, EPUB, sub… |

**取值命令与匹配理由**
1. `scenario-labs/skills` — `gh api repos/scenario-labs/skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=173；Get production-ready images, video, audio, and 3D from any AI agent: skills that pick the right mode ｜ ⚠️缓存→现测：1126/2026-10-23/MIT → 3388/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=173
2. `wiltodelta/remove-ai-watermarks` — `gh api repos/wiltodelta/remove-ai-watermarks --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Remove visible and invisible AI watermarks from images and video, and AI provenance metadata from im ｜ ⚠️缓存→现测：6115/2026-10-24/Apache-2.0 → 6295/2026-11-06T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=4
3. `LnYo-Cly/ai4j` — `gh api repos/LnYo-Cly/ai4j --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=5；Java 8+ agentic SDK: unified LLM access (OpenAI/Anthropic/DashScope/Doubao/DeepSeek...),unified AI s ｜ ⚠️缓存→现测：435/2026-10-13/Apache-2.0 → 438/2026-10-13T1…/Apache-2.0（stars 漂移） ｜ SKILL.md=5
4. `EGSECDA/vocaloid-style-mv-pipeline` — `gh api repos/EGSECDA/vocaloid-style-mv-pipeline --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Production pipeline and Claude Code skill for Vocaloid-style hand-drawn (手書き) lyric music videos: de ｜ ⚠️缓存→现测：210/2026-10-04/MIT → 250/2026-11-04T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1
5. `equalang/equalang-skill` — `gh api repos/equalang/equalang-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent Skill for Equalang: translate PDF, DOCX, PPTX, XLSX, EPUB, subtitles, pictures, audio and vide ｜ ⚠️缓存→现测：39/2026-10-12/Apache-2.0 → 78/2026-11-03T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.12 `audit-runner-safe-aggregate` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：写聚合 runner 的反掩盖范式 — 依次/并行跑多个子脚本再汇总总 PASS/FAIL 时，防全局 any()/聚合把单个失败洗绿。给出反模式（THE BUG）、正确范式（THE FIX）、关键三原则、陷阱清单与写完必做的验真步骤。Use when 新写或改造 audit_all/test runner/批量检查器类聚合脚本。不适用：单个脚本自身的业务判定。（desc_len=182；SKILL.md bytes=5679）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=7，trim=1） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | 117973 | 6860 / 69 | 2026-11-06T11:35:30Z | Apache-2.0 | 活跃(1d) | `active` | 23/25 (fc4 eff5 compat5 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=28；🪨 why use many token when few token do trick. Viral skill + proxy … |
| 2 | [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) | 18315 | 1510 / 58 | 2026-10-12T02:06:40Z | MIT | 活跃(26d) | `active` | 19/25 (fc4 eff2 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；A comprehensive collection of Agent Skills for context engineering,… |
| 3 | [webdriverio/webdriverio](https://github.com/webdriverio/webdriverio) | 9871 | 2717 / 236 | 2026-11-06T17:06:24Z | MIT | 活跃(0d) | `active` | 19/25 (fc3 eff5 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Next-gen browser and mobile automation test framework for Node.js |
| 4 | [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) | 48225 | 3977 / 555 | 2026-11-04T23:21:44Z | MIT | 活跃(2d) | `active` | 17/25 (fc1 eff5 compat3 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；Local code intelligence for developers and AI agents. Connect code, … |
| 5 | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 63535 | 4118 / 115 | 2026-09-14T19:29:02Z | MIT | 活跃(53d) | `active` | 15/25 (fc2 eff0 compat5 docs3 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A coding-agent skill for multi-phase security audits with independen… |

**取值命令与匹配理由**
1. `JuliusBrussee/caveman` — `gh api repos/JuliusBrussee/caveman --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=28；🪨 why use many token when few token do trick. Viral skill + proxy for coding agents that cuts 65% o ｜ ⚠️缓存→现测：114863/2026-10-25/Apache-2.0 → 117973/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=28
2. `muratcankoylan/Agent-Skills-for-Context-Engineering` — `gh api repos/muratcankoylan/Agent-Skills-for-Context-Engineering --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；A comprehensive collection of Agent Skills for context engineering, multi-agent architectures, and p ｜ ⚠️缓存→现测：18208/2026-10-12/MIT → 18315/2026-10-12T0…/MIT（stars 漂移） ｜ SKILL.md=24
3. `webdriverio/webdriverio` — `gh api repos/webdriverio/webdriverio --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Next-gen browser and mobile automation test framework for Node.js ｜ ⚠️缓存→现测：9856/2026-10-25/MIT → 9871/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=7
4. `DeusData/codebase-memory-mcp` — `gh api repos/DeusData/codebase-memory-mcp --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；Local code intelligence for developers and AI agents. Connect code, docs and infrastructure in a per ｜ ⚠️缓存→现测：47428/2026-10-24/MIT → 48225/2026-11-04T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=0
5. `cloudflare/security-audit-skill` — `gh api repos/cloudflare/security-audit-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A coding-agent skill for multi-phase security audits with independently verified, machine-readable f ｜ ⚠️缓存→现测：53489/2026-09-14/MIT → 63535/2026-09-14T1…/MIT（stars 漂移） ｜ SKILL.md=1

### 7.13 `bigfile-split` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：拆分超大记忆/知识库markdown文件 — 按标题切块+原文件留索引。当单文件超过 4KB 用户硬限时使用，禁止手写拆分脚本重踩行尾陷阱。 Split oversized memory/knowledge-base files via the **composite-pointer + semantic-leaf** paradigm (4KB user hard limit ≤4096B, aligned with 'meta/bi（desc_len=732；SKILL.md bytes=4334）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=7，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | 18796 | 1527 / 75 | 2026-11-06T04:09:40Z | MIT | 活跃(1d) | `active` | 23/25 (fc5 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=197；ARIS ⚔️ (Auto-Research-In-Sleep) — Lightweight Markdown-only skill… |
| 2 | [EverMind-AI/EverOS](https://github.com/EverMind-AI/EverOS) | 13840 | 963 / 43 | 2026-11-06T08:46:28Z | Apache-2.0 | 活跃(1d) | `active` | 21/25 (fc3 eff5 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=5；One portable memory layer for every AI agent: local-first, Markdown-… |
| 3 | [genspark-ai/genoffice](https://github.com/genspark-ai/genoffice) | 11848 | 1640 / 59 | 2026-11-06T12:26:32Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc4 eff4 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Free, open-source AI Office suite: Docs, Sheets, Slides, PDF, Markd… |
| 4 | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | 27923 | 2313 / 11 | 2026-11-04T18:13:42Z | MIT | 活跃(2d) | `active` | 20/25 (fc4 eff3 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=18；Persistent file-based planning for AI coding agents and long-runnin… |
| 5 | [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) | 16226 | 1599 / 25 | 2026-10-25T22:24:31Z | MIT | 活跃(12d) | `active` | 20/25 (fc4 eff3 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=16；Self-organizing AI second brain for Obsidian + Claude Code. Drop an… |

**取值命令与匹配理由**
1. `wanshuiyin/Auto-claude-code-research-in-sleep` — `gh api repos/wanshuiyin/Auto-claude-code-research-in-sleep --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=197；ARIS ⚔️ (Auto-Research-In-Sleep) — Lightweight Markdown-only skills for autonomous ML research: cros ｜ ⚠️缓存→现测：18023/2026-10-24/MIT → 18796/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=197
2. `EverMind-AI/EverOS` — `gh api repos/EverMind-AI/EverOS --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=5；One portable memory layer for every AI agent: local-first, Markdown-native, user-owned, and self-evo ｜ ⚠️缓存→现测：13597/2026-10-22/Apache-2.0 → 13840/2026-11-06T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=5
3. `genspark-ai/genoffice` — `gh api repos/genspark-ai/genoffice --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Free, open-source AI Office suite: Docs, Sheets, Slides, PDF, Markdown and HTML editors with a built ｜ ⚠️缓存→现测：10764/2026-10-24/Apache-2.0 → 11848/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=43
4. `OthmanAdi/planning-with-files` — `gh api repos/OthmanAdi/planning-with-files --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=18；Persistent file-based planning for AI coding agents and long-running tasks. Crash-proof markdown pla ｜ ⚠️缓存→现测：27631/2026-10-24/MIT → 27923/2026-11-04T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=18
5. `AgriciDaniel/claude-obsidian` — `gh api repos/AgriciDaniel/claude-obsidian --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=16；Self-organizing AI second brain for Obsidian + Claude Code. Drop any source and Claude reads, links, ｜ ⚠️缓存→现测：15791/2026-10-22/MIT → 16226/2026-10-25T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=16

### 7.14 `c-cleanup` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：Windows C盘空间清理技能。当用户需要释放C盘空间、清理磁盘、删除不必要的文件时使用此技能。支持分析磁盘使用情况、识别大文件夹、删除工作备份、清理临时文件和回收站。触发词：C盘清理、磁盘空间不足、释放空间、清理备份、c-delete、磁盘清理。（desc_len=125；SKILL.md bytes=37465）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=8，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [OrchestratorInc/agent-orchestrator](https://github.com/OrchestratorInc/agent-orchestrator) | 14176 | 1934 / 906 | 2026-11-06T18:26:55Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc3 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Open-source (Apache-2.0) orchestrator for Claude Code, Codex & 30+ c… |
| 2 | [parcadei/Continuous-Claude-v3](https://github.com/parcadei/Continuous-Claude-v3) | 3948 | 303 / 47 | 2026-01-26T15:27:49Z | MIT | 一般(284d) | `active` | 18/25 (fc5 eff2 compat5 docs4 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=160；Context management for Claude Code. Hooks maintain state via ledge… |
| 3 | [xpf0000/FlyEnv](https://github.com/xpf0000/FlyEnv) | 3342 | 392 / 39 | 2026-11-06T14:54:28Z | BSD-3-Clause | 活跃(0d) | `active` | 18/25 (fc2 eff3 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Native local development environment for Windows, macOS & Linux. A m… |
| 4 | [CursorTouch/Windows-MCP](https://github.com/CursorTouch/Windows-MCP) | 11186 | 1210 / 36 | 2026-11-06T16:35:28Z | MIT | 活跃(0d) | `active` | 17/25 (fc2 eff3 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；MCP Server for Computer Use in Windows |
| 5 | [sixtysevenlf/dsh-blender-plugin](https://github.com/sixtysevenlf/dsh-blender-plugin) | 1663 | 65 / 3 | 2026-11-06T07:45:04Z | BSD-3-Clause | 活跃(1d) | `active` | 16/25 (fc2 eff2 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；DSH × Blender 直连实时插件：15 个模型工具让 AI 驱动 GUI Blender；v2.5 活动状态置顶并可一键暂停 A… |

**取值命令与匹配理由**
1. `OrchestratorInc/agent-orchestrator` — `gh api repos/OrchestratorInc/agent-orchestrator --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Open-source (Apache-2.0) orchestrator for Claude Code, Codex & 30+ coding agents. Plan, run and supe ｜ ⚠️缓存→现测：13596/2026-10-25/Apache-2.0 → 14176/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=7
2. `parcadei/Continuous-Claude-v3` — `gh api repos/parcadei/Continuous-Claude-v3 --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=160；Context management for Claude Code. Hooks maintain state via ledgers and handoffs. MCP execution wit ｜ ⚠️缓存→现测：3946/2026-01-26/MIT → 3948/2026-01-26T1…/MIT（stars 漂移） ｜ SKILL.md=160
3. `xpf0000/FlyEnv` — `gh api repos/xpf0000/FlyEnv --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Native local development environment for Windows, macOS & Linux. A modern alternative to XAMPP, MAMP ｜ ⚠️缓存→现测：3309/2026-10-25/BSD-3-Clause → 3342/2026-11-06T1…/BSD-3-Clause（stars,pushed_at 漂移） ｜ SKILL.md=2
4. `CursorTouch/Windows-MCP` — `gh api repos/CursorTouch/Windows-MCP --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；MCP Server for Computer Use in Windows ｜ ⚠️缓存→现测：10260/2026-10-24/MIT → 11186/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1
5. `sixtysevenlf/dsh-blender-plugin` — `gh api repos/sixtysevenlf/dsh-blender-plugin --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；DSH × Blender 直连实时插件：15 个模型工具让 AI 驱动 GUI Blender；v2.5 活动状态置顶并可一键暂停 AI，原生选中/集合/子元素直送 DSH，随包建模 skill，支 ｜ ⚠️缓存→现测：1266/2026-10-25/BSD-3-Clause → 1663/2026-11-06T0…/BSD-3-Clause（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.15 `chaoshi-admin-inline-edit` ｜ HIGH ｜ 候选线索（元数据已实测，功能等价待复核）

- **功能边界**：超市web管理后台商品编辑——禁弹窗/禁抽屉/禁底部面板，唯一交互为InlineEditForm内联展开（条目正下方）。用户连续3轮纠正后确认的强偏好。含搜索+分类筛选+批量操作+快捷上下架开关的完整ProductsTab模式。触发词：内联编辑、inline edit、管理后台编辑、ProductsTab、商品编辑模式、编辑展开、admin CRUD、禁弹窗。（desc_len=181；SKILL.md bytes=6245）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：NO_OS_CANDIDATE（candidates_n=5，skill_relevant_n=0，trim=0） ｜ **语义缺口**：是 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：[ruvnet/ruflo](https://github.com/ruvnet/ruflo)、[K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)、[Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)、[agentscope-ai/QwenPaw](https://github.com/agentscope-ai/QwenPaw)、[alibaba/open-code-review](https://github.com/alibaba/open-code-review)（共 5 件，`not_replacement=true`）

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [anbeime/skill](https://github.com/anbeime/skill) | 9249 | 821 / 35 | 2026-11-06T08:59:08Z | NOASSERTION | 活跃(1d) | `active` | 线索分 8.18 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [第一遍定向检索] SKILL.md=94；stars=9249；description=收录最全、更新最快的技能Skills商店：精选原创技能包（涵盖文档处理、内容创作、编程开发、机器学习、自动化工作流），全部打包好可… |
| 2 | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | 65481 | 4336 / 53 | 2026-11-06T15:20:25Z | MIT | 活跃(0d) | `active` | 线索分 7.31 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [第一遍定向检索] SKILL.md=1；stars=65481；description=Editorial diagram design for Claude Code, Codex, GitHub Copilot, … |
| 3 | [marmelab/react-admin](https://github.com/marmelab/react-admin) | 26989 | 5473 / 59 | 2026-11-05T15:02:55Z | MIT | 活跃(1d) | `active` | 线索分 4.54 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=2；stars=26989；description=A frontend Framework for single-page applications on top of REST/Gra… |
| 4 | [emdash-cms/emdash](https://github.com/emdash-cms/emdash) | 14203 | 1371 / 234 | 2026-11-06T19:44:34Z | MIT | 活跃(0d) | `active` | 线索分 4.28 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=39；stars=14203；description=EmDash is a full-stack TypeScript CMS based on Astro; the spiritual… |
| 5 | [filamentphp/demo](https://github.com/filamentphp/demo) | 1215 | 572 / 0 | 2026-11-05T10:10:42Z | MIT | 活跃(2d) | `active` | 线索分 4.02 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=2；stars=1215；description=A full-featured demo app built with Filament. |

**取值命令与匹配理由**
1. `anbeime/skill` — `gh api repos/anbeime/skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [第一遍定向检索] SKILL.md=94；stars=9249；description=收录最全、更新最快的技能Skills商店：精选原创技能包（涵盖文档处理、内容创作、编程开发、机器学习、自动化工作流），全部打包好可直接安装使用！同时自动抓取GitHub上万个Skills项目，按分类、更新时间、Star数量整理。The most comprehensive and ｜ SKILL.md=94 ｜ `gh api repos/anbeime/skill/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
2. `cathrynlavery/diagram-design` — `gh api repos/cathrynlavery/diagram-design --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [第一遍定向检索] SKILL.md=1；stars=65481；description=Editorial diagram design for Claude Code, Codex, GitHub Copilot, Cursor, Factory Droid, Qoder, and Pi. 45 diagram types. Self-contained HTML ｜ SKILL.md=1 ｜ `gh api repos/cathrynlavery/diagram-design/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
3. `marmelab/react-admin` — `gh api repos/marmelab/react-admin --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=2；stars=26989；description=A frontend Framework for single-page applications on top of REST/GraphQL APIs, using TypeScript, React and Material Design ｜ SKILL.md=2 ｜ `gh api repos/marmelab/react-admin/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
4. `emdash-cms/emdash` — `gh api repos/emdash-cms/emdash --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=39；stars=14203；description=EmDash is a full-stack TypeScript CMS based on Astro; the spiritual successor to WordPress ｜ SKILL.md=39 ｜ `gh api repos/emdash-cms/emdash/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
5. `filamentphp/demo` — `gh api repos/filamentphp/demo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=2；stars=1215；description=A full-featured demo app built with Filament. ｜ SKILL.md=2 ｜ `gh api repos/filamentphp/demo/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`

### 7.16 `chaoshi-image-optimization` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：超市web图片资产优化流水线——审计→ffmpeg批量WebP压缩→响应式srcset小图生成→问题图替换(ImageGen降级ImageSearch)→代码引用更新→build验证。当需要优化supermarket-web商品图片（体积压缩、格式转换、响应式srcset、问题图替换、引用迁移）时使用。触发词：图片优化、WebP压缩、商品图替换、图片资产治理、chaoshi image、图片瘦身、图片审计、响应式srcset、respo（desc_len=243；SKILL.md bytes=35277）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=7，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 81071 | 9543 / 654 | 2026-11-06T18:31:29Z | MIT | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swa… |
| 2 | [langgenius/dify](https://github.com/langgenius/dify) | 160565 | 25406 / 1205 | 2026-11-06T18:33:42Z | NOASSERTION | 活跃(0d) | `active` | 19/25 (fc3 eff5 compat1 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=7；Build Agentic workflows, RAG pipelines, with rich AI model and tool … |
| 3 | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | 111152 | 7467 / 8 | 2026-11-05T01:12:12Z | MIT | 活跃(2d) | `active` | 17/25 (fc2 eff2 compat5 docs3 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent skills that give coding agents taste: art direction, reference… |
| 4 | [homarr-labs/dashboard-icons](https://github.com/homarr-labs/dashboard-icons) | 9018 | 729 / 35 | 2026-11-06T13:31:39Z | Apache-2.0 | 活跃(0d) | `active` | 14/25 (fc1 eff4 compat3 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；3,400+ curated icons and logos for dashboards and AI agents. SVG, PN… |
| 5 | [level09/enferno](https://github.com/level09/enferno) | 569 | 80 / 1 | 2026-11-05T23:49:46Z | MIT | 活跃(1d) | `active` | 14/25 (fc2 eff2 compat5 docs3 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Lean Flask framework built for coding agents: Vue 3 + Vuetify with n… |

**取值命令与匹配理由**
1. `ruvnet/ruflo` — `gh api repos/ruvnet/ruflo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swarms, coordinate autonomous workflo ｜ ⚠️缓存→现测：79103/2026-10-25/MIT → 81071/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=389
2. `langgenius/dify` — `gh api repos/langgenius/dify --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=7；Build Agentic workflows, RAG pipelines, with rich AI model and tool support on one collaborative wor ｜ ⚠️缓存→现测：159795/2026-10-28/NOASSERTION → 160565/2026-11-06T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=7
3. `Leonxlnx/taste-skill` — `gh api repos/Leonxlnx/taste-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent skills that give coding agents taste: art direction, reference images and a browser check inst ｜ ⚠️缓存→现测：106146/2026-10-30/MIT → 111152/2026-11-05T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1
4. `homarr-labs/dashboard-icons` — `gh api repos/homarr-labs/dashboard-icons --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；3,400+ curated icons and logos for dashboards and AI agents. SVG, PNG and WEBP on a free CDN, plus a ｜ ⚠️缓存→现测：8932/2026-10-23/Apache-2.0 → 9018/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=0
5. `level09/enferno` — `gh api repos/level09/enferno --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Lean Flask framework built for coding agents: Vue 3 + Vuetify with no build step, production-ready a ｜ ⚠️缓存→现测：568/2026-10-22/MIT → 569/2026-11-05T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.17 `chaoshi-web-deploy` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：超市web部署与部署排障唯一权威源（v3 新架构：Cloudflare Pages Functions + D1 + GitHub Pages 双前端）。cloudbase 云函数部署后订单不显示、部署后数据不显示、部署故障排查、部署后页面 404。任何 wrangler pages deploy / gh pages 推送 / d1 execute 前必须先加载本 skill 获取对应模式 checklist，禁止凭记忆裸跑。覆盖两种（desc_len=407；SKILL.md bytes=61876）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 81071 | 9543 / 654 | 2026-11-06T18:31:29Z | MIT | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swa… |
| 2 | [iflytek/skillhub](https://github.com/iflytek/skillhub) | 5372 | 816 / 34 | 2026-11-06T10:25:31Z | Apache-2.0 | 活跃(1d) | `active` | 22/25 (fc4 eff5 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；Self-hosted, open-source agent skill registry for enterprises. Publ… |
| 3 | [agentscope-ai/QwenPaw](https://github.com/agentscope-ai/QwenPaw) | 37422 | 3264 / 1110 | 2026-11-06T10:39:00Z | Apache-2.0 | 活跃(1d) | `active` | 21/25 (fc4 eff5 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=49；Your Personal AI Assistant; easy to install, deploy on your own mac… |
| 4 | [langgenius/dify](https://github.com/langgenius/dify) | 160565 | 25406 / 1205 | 2026-11-06T18:33:42Z | NOASSERTION | 活跃(0d) | `active` | 19/25 (fc3 eff5 compat1 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=7；Build Agentic workflows, RAG pipelines, with rich AI model and tool … |
| 5 | [glitternetwork/pinme](https://github.com/glitternetwork/pinme) | 3754 | 276 / 10 | 2026-09-12T05:23:49Z | MIT | 活跃(56d) | `active` | 17/25 (fc3 eff3 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Deploy Your Frontend in a Single Command. Claude Code Skills support… |

**取值命令与匹配理由**
1. `ruvnet/ruflo` — `gh api repos/ruvnet/ruflo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swarms, coordinate autonomous workflo ｜ ⚠️缓存→现测：79103/2026-10-25/MIT → 81071/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=389
2. `iflytek/skillhub` — `gh api repos/iflytek/skillhub --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；Self-hosted, open-source agent skill registry for enterprises. Publish & version skill packages, gov ｜ ⚠️缓存→现测：5283/2026-10-25/Apache-2.0 → 5372/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=24
3. `agentscope-ai/QwenPaw` — `gh api repos/agentscope-ai/QwenPaw --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=49；Your Personal AI Assistant; easy to install, deploy on your own machine or on the cloud; supports mu ｜ ⚠️缓存→现测：36092/2026-10-23/Apache-2.0 → 37422/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=49
4. `langgenius/dify` — `gh api repos/langgenius/dify --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=7；Build Agentic workflows, RAG pipelines, with rich AI model and tool support on one collaborative wor ｜ ⚠️缓存→现测：159795/2026-10-28/NOASSERTION → 160565/2026-11-06T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=7
5. `glitternetwork/pinme` — `gh api repos/glitternetwork/pinme --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Deploy Your Frontend in a Single Command. Claude Code Skills supported. ｜ ⚠️缓存→现测：3755/2026-09-12/MIT → 3754/2026-09-12T0…/MIT（stars 漂移） ｜ SKILL.md=7

### 7.18 `cloudbase-db-optimize` ｜ MID ｜ 候选线索（元数据已实测，功能等价待复核）

- **功能边界**：CloudBase 云开发文档库（MongoDB 兼容）性能优化流水线——诊断五类根因（缺索引/N+1/无投影/无缓存/分页漏算）→建索引→改批量查询→加字段投影→只读数据 TTL 缓存+写操作失效→验证。当 CloudBase/云开发项目出现查询慢、响应时间长、数据库成为瓶颈时使用。触发词：数据库慢、查询慢、数据库优化、DB优化、性能瓶颈、云开发慢、CloudBase 优化、tcb 数据库、集合索引、createIndex、全集合扫描（desc_len=239；SKILL.md bytes=8389）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：FAMILY_ONLY（candidates_n=5，skill_relevant_n=1，trim=0） ｜ **语义缺口**：是 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：[ruvnet/ruflo](https://github.com/ruvnet/ruflo)、[K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)、[Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)、[agentscope-ai/QwenPaw](https://github.com/agentscope-ai/QwenPaw)（共 4 件，`not_replacement=true`）

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 56317 | 4957 / 80 | 2026-11-02T09:23:27Z | MIT | 活跃(5d) | `active` | 线索分 9.13 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=177；stars=56317；description=Turn any AI agent into an AI Scientist. The #1 Agent Skills librar… |
| 2 | [supabase/agent-skills](https://github.com/supabase/agent-skills) | 3015 | 265 / 527 | 2026-11-05T12:42:22Z | MIT | 活跃(1d) | `active` | 线索分 8.06 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=2；stars=3015；description=Agent Skills to help developers using AI agents with Supabase |
| 3 | [planetscale/database-skills](https://github.com/planetscale/database-skills) | 738 | 68 / 5 | 2026-10-07T18:09:19Z | MIT | 活跃(30d) | `active` | 线索分 8.01 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=4；stars=738；description=Skills for AI agents working with databases |
| 4 | [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 36928 | 4084 / 12 | 2026-11-05T10:43:36Z | MIT | 活跃(2d) | `active` | 线索分 5.74 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=0；stars=36928；description=A curated collection of 1000+ agent skills from official dev teams a… |
| 5 | [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | 166920 | 27042 / 220 | 2026-11-06T01:58:56Z | MIT | 活跃(1d) | `active` | 线索分 5 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [第一遍定向检索] SKILL.md=0；stars=166920；description=A complete AI agency at your fingertips - From frontend wizards … |

**取值命令与匹配理由**
1. `K-Dense-AI/scientific-agent-skills` — `gh api repos/K-Dense-AI/scientific-agent-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=177；stars=56317；description=Turn any AI agent into an AI Scientist. The #1 Agent Skills library for science, used by 250,000+ scientists worldwide. 177 ready-to-use val ｜ SKILL.md=177 ｜ `gh api repos/K-Dense-AI/scientific-agent-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
2. `supabase/agent-skills` — `gh api repos/supabase/agent-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=2；stars=3015；description=Agent Skills to help developers using AI agents with Supabase ｜ SKILL.md=2 ｜ `gh api repos/supabase/agent-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
3. `planetscale/database-skills` — `gh api repos/planetscale/database-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=4；stars=738；description=Skills for AI agents working with databases ｜ SKILL.md=4 ｜ `gh api repos/planetscale/database-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
4. `VoltAgent/awesome-agent-skills` — `gh api repos/VoltAgent/awesome-agent-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=0；stars=36928；description=A curated collection of 1000+ agent skills from official dev teams and the community, compatible with Claude Code, Codex, Gemini CLI, Cursor ｜ SKILL.md=0 ｜ `gh api repos/VoltAgent/awesome-agent-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核
5. `msitarzewski/agency-agents` — `gh api repos/msitarzewski/agency-agents --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [第一遍定向检索] SKILL.md=0；stars=166920；description=A complete AI agency at your fingertips - From frontend wizards to Reddit community ninjas, from whimsy injectors to reality checkers. Each ｜ SKILL.md=0 ｜ `gh api repos/msitarzewski/agency-agents/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核

### 7.19 `code-review` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：项目代码库全面审查 — 性能瓶颈/代码缺陷/可维护性/安全漏洞/重复代码五维扫描（每维都要过，证据落到 file:line），按 严重程度×影响范围 评定优先级并逐项实施优化，输出六字段报告模板。含经验锚点与「借口→反驳」反理性化清单。Use when 用户要「全面审查/代码审查/体检」或要定位某类异常根因。不适用：安全专项深审（走 security-audit）、改结构不改行为（走 refactoring）。（desc_len=207；SKILL.md bytes=5200）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | 18796 | 1527 / 75 | 2026-11-06T04:09:40Z | MIT | 活跃(1d) | `active` | 23/25 (fc5 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=197；ARIS ⚔️ (Auto-Research-In-Sleep) — Lightweight Markdown-only skill… |
| 2 | [tirth8205/code-review-graph](https://github.com/tirth8205/code-review-graph) | 32624 | 2967 / 111 | 2026-11-06T19:05:44Z | MIT | 活跃(0d) | `active` | 21/25 (fc3 eff5 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Local-first code intelligence graph for MCP and CLI. Builds a persis… |
| 3 | [alibaba/open-code-review](https://github.com/alibaba/open-code-review) | 49564 | 3637 / 347 | 2026-11-06T08:35:01Z | Apache-2.0 | 活跃(1d) | `active` | 20/25 (fc3 eff4 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=9；Secure, fast, efficient, battle-tested at Alibaba's scale. Hybrid ar… |
| 4 | [code-yeongyu/oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) | 70744 | 5835 / 2383 | 2026-11-06T19:05:20Z | NOASSERTION | 活跃(0d) | `active` | 20/25 (fc4 eff5 compat1 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=1/5；SKILL.md=64；OmO: Just type "mass ulw" keyword with your prompt. Now you are the… |
| 5 | [CherryHQ/cherry-studio](https://github.com/CherryHQ/cherry-studio) | 53305 | 5186 / 2570 | 2026-11-06T19:05:51Z | AGPL-3.0 | 活跃(0d) | `active` | 20/25 (fc4 eff5 compat1 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=1/5；SKILL.md=40；AI productivity studio with smart chat, autonomous agents, and 300+… |

**取值命令与匹配理由**
1. `wanshuiyin/Auto-claude-code-research-in-sleep` — `gh api repos/wanshuiyin/Auto-claude-code-research-in-sleep --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=197；ARIS ⚔️ (Auto-Research-In-Sleep) — Lightweight Markdown-only skills for autonomous ML research: cros ｜ ⚠️缓存→现测：18023/2026-10-24/MIT → 18796/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=197
2. `tirth8205/code-review-graph` — `gh api repos/tirth8205/code-review-graph --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Local-first code intelligence graph for MCP and CLI. Builds a persistent map of your codebase so AI ｜ ⚠️缓存→现测：32379/2026-10-16/MIT → 32624/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=7
3. `alibaba/open-code-review` — `gh api repos/alibaba/open-code-review --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=9；Secure, fast, efficient, battle-tested at Alibaba's scale. Hybrid architecture code review tool: det ｜ ⚠️缓存→现测：48217/2026-10-22/Apache-2.0 → 49564/2026-11-06T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=9
4. `code-yeongyu/oh-my-openagent` — `gh api repos/code-yeongyu/oh-my-openagent --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=1/5；SKILL.md=64；OmO: Just type "mass ulw" keyword with your prompt. Now you are the master of graph engineering. ｜ ⚠️缓存→现测：70321/2026-10-25/NOASSERTION → 70744/2026-11-06T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=64
5. `CherryHQ/cherry-studio` — `gh api repos/CherryHQ/cherry-studio --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=1/5；SKILL.md=40；AI productivity studio with smart chat, autonomous agents, and 300+ assistants. Unified access to fr ｜ ⚠️缓存→现测：52958/2026-10-25/AGPL-3.0 → 53305/2026-11-06T1…/AGPL-3.0（stars,pushed_at 漂移） ｜ SKILL.md=40

### 7.20 `cross-platform-agent-sync` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：跨平台AI agent行为规则同步方法论。通过junction + 共享文件 + 平台启动文件引用实现"改一处N端响应"。在役端清单**只读不抄**：权威 = '焚诀\eval\truth_constants.json' endpoints.active（2026-09-26 实测七端 wb/tr/cx/hm/zc/oc/qd；cc 弃用 2026-09-08、OpenClaw 退役 2026-09-21、千问办公 qw 退役 2026（desc_len=471；SKILL.md bytes=5445）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | 18796 | 1527 / 75 | 2026-11-06T04:09:40Z | MIT | 活跃(1d) | `active` | 23/25 (fc5 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=197；ARIS ⚔️ (Auto-Research-In-Sleep) — Lightweight Markdown-only skill… |
| 2 | [topoteretes/cognee](https://github.com/topoteretes/cognee) | 33114 | 3473 / 1101 | 2026-11-06T18:57:58Z | Apache-2.0 | 活跃(0d) | `active` | 22/25 (fc4 eff5 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=23；Cognee is the open-source AI memory platform for agents. Give your … |
| 3 | [MemTensor/MemOS](https://github.com/MemTensor/MemOS) | 12302 | 1111 / 152 | 2026-11-04T06:42:18Z | Apache-2.0 | 活跃(3d) | `active` | 22/25 (fc3 eff5 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Self-evolving memory OS for LLM & AI Agents: ultra-persistent memory… |
| 4 | [alibaba/nacos](https://github.com/alibaba/nacos) | 33499 | 13280 / 205 | 2026-11-05T11:52:27Z | Apache-2.0 | 活跃(2d) | `active` | 19/25 (fc2 eff5 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；an easy-to-use dynamic service discovery, configuration and service … |
| 5 | [Agents365-ai/drawio-skill](https://github.com/Agents365-ai/drawio-skill) | 10622 | 729 / 0 | 2026-11-06T03:55:43Z | MIT | 活跃(1d) | `active` | 17/25 (fc2 eff2 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Agent skill that turns natural language, code, Terraform/K8s, SQL, O… |

**取值命令与匹配理由**
1. `wanshuiyin/Auto-claude-code-research-in-sleep` — `gh api repos/wanshuiyin/Auto-claude-code-research-in-sleep --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=197；ARIS ⚔️ (Auto-Research-In-Sleep) — Lightweight Markdown-only skills for autonomous ML research: cros ｜ ⚠️缓存→现测：18023/2026-10-24/MIT → 18796/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=197
2. `topoteretes/cognee` — `gh api repos/topoteretes/cognee --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=23；Cognee is the open-source AI memory platform for agents. Give your AI agents persistent long-term me ｜ ⚠️缓存→现测：32728/2026-10-23/Apache-2.0 → 33114/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=23
3. `MemTensor/MemOS` — `gh api repos/MemTensor/MemOS --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Self-evolving memory OS for LLM & AI Agents: ultra-persistent memory, hybrid-retrieval, and cross-ta ｜ ⚠️缓存→现测：12081/2026-10-24/Apache-2.0 → 12302/2026-11-04T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=7
4. `alibaba/nacos` — `gh api repos/alibaba/nacos --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；an easy-to-use dynamic service discovery, configuration and service management platform for building ｜ ⚠️缓存→现测：33479/2026-10-23/Apache-2.0 → 33499/2026-11-05T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=1
5. `Agents365-ai/drawio-skill` — `gh api repos/Agents365-ai/drawio-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Agent skill that turns natural language, code, Terraform/K8s, SQL, OpenAPI, AsyncAPI, Protobuf and G ｜ ⚠️缓存→现测：10342/2026-10-11/MIT → 10622/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=2

### 7.21 `debugging-fixing` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：系统化诊断并修复 bug/报错/异常行为。覆盖报错栈、测试失败、崩溃、进程卡住不返回、rc=124 恒定超时、daemon 线程或子进程未清理、竞态与共享可变状态、环境变量与路径类失败、页面白屏/本地 HTML 双击无反应/构建产物无内容、进程内引擎故障（wasm/native/Rust FFI/JIT）报错栈短得反常或耗时异常短。Use when 用户说「报错了」「跑不通」「卡住了」「不返回」「白屏」「为什么超时」「crash/闪退/（desc_len=414；SKILL.md bytes=148088）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 81071 | 9543 / 654 | 2026-11-06T18:31:29Z | MIT | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swa… |
| 2 | [morluto/rea](https://github.com/morluto/rea) | 437368 | 108433 / 1586 | 2026-11-06T19:05:22Z | MIT | 活跃(0d) | `active` | 23/25 (fc3 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=5；Reverse engineer anything with agents, from app behavior down to nat… |
| 3 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | 117973 | 6860 / 69 | 2026-11-06T11:35:30Z | Apache-2.0 | 活跃(1d) | `active` | 23/25 (fc4 eff5 compat5 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=28；🪨 why use many token when few token do trick. Viral skill + proxy … |
| 4 | [rtk-ai/rtk](https://github.com/rtk-ai/rtk) | 85739 | 5489 / 1696 | 2026-11-06T18:18:52Z | Apache-2.0 | 活跃(0d) | `active` | 23/25 (fc4 eff5 compat5 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；CLI proxy that reduces LLM token consumption by 60-90% on common de… |
| 5 | [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) | 18315 | 1510 / 58 | 2026-10-12T02:06:40Z | MIT | 活跃(26d) | `active` | 19/25 (fc4 eff2 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；A comprehensive collection of Agent Skills for context engineering,… |

**取值命令与匹配理由**
1. `ruvnet/ruflo` — `gh api repos/ruvnet/ruflo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swarms, coordinate autonomous workflo ｜ ⚠️缓存→现测：79103/2026-10-25/MIT → 81071/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=389
2. `morluto/rea` — `gh api repos/morluto/rea --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=5；Reverse engineer anything with agents, from app behavior down to native binaries. ｜ ⚠️缓存→现测：380073/2026-10-25/MIT → 437368/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=5
3. `JuliusBrussee/caveman` — `gh api repos/JuliusBrussee/caveman --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=28；🪨 why use many token when few token do trick. Viral skill + proxy for coding agents that cuts 65% o ｜ ⚠️缓存→现测：114863/2026-10-25/Apache-2.0 → 117973/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=28
4. `rtk-ai/rtk` — `gh api repos/rtk-ai/rtk --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；CLI proxy that reduces LLM token consumption by 60-90% on common dev commands. Single Rust binary, z ｜ ⚠️缓存→现测：84497/2026-10-23/Apache-2.0 → 85739/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=12
5. `muratcankoylan/Agent-Skills-for-Context-Engineering` — `gh api repos/muratcankoylan/Agent-Skills-for-Context-Engineering --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；A comprehensive collection of Agent Skills for context engineering, multi-agent architectures, and p ｜ ⚠️缓存→现测：18208/2026-10-12/MIT → 18315/2026-10-12T0…/MIT（stars 漂移） ｜ SKILL.md=24

### 7.22 `discover-agent-cli` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：发现Electron桌面应用中隐藏的CLI工具。发现桌面应用隐藏CLI 发现 Electron 桌面应用中隐藏的 CLI 工具。当需要调用某个桌面应用（如 WorkBuddy/TRAE/Cursor/OpenCode 等 coding agent，或 Slack/Discord/Notion 等工具）但"以为没有 CLI"时使用。标准化发现流程：定位安装目录 → 找 bin/ 子目录 → 测试 CLI → 检查 headless 模式（desc_len=322；SKILL.md bytes=8531）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=7，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [ThinkInAIXYZ/deepchat](https://github.com/ThinkInAIXYZ/deepchat) | 6383 | 772 / 10 | 2026-11-06T01:48:41Z | Apache-2.0 | 活跃(1d) | `active` | 22/25 (fc4 eff5 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=25；🐬DeepChat - A smart assistant that connects powerful AI to your pe… |
| 2 | [NanmiCoder/cc-haha](https://github.com/NanmiCoder/cc-haha) | 15338 | 8612 / 205 | 2026-11-05T15:03:01Z | NOASSERTION | 活跃(1d) | `active` | 18/25 (fc3 eff5 compat1 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=4；本地优先的跨平台 Claude Code / AI Agent 桌面工作台：多 Agent 协作、Git Worktree、代码 Dif… |
| 3 | [DayuanJiang/next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io) | 36741 | 3830 / 47 | 2026-11-06T15:13:16Z | Apache-2.0 | 活跃(0d) | `active` | 17/25 (fc1 eff4 compat3 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；Draw and edit draw.io diagrams by chatting with an AI. Web app, desk… |
| 4 | [op7418/CodePilot](https://github.com/op7418/CodePilot) | 6518 | 697 / 413 | 2026-09-22T03:24:52Z | NOASSERTION | 活跃(46d) | `active` | 17/25 (fc3 eff5 compat1 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=9；A multi-model AI agent desktop client — connect any AI provider, ext… |
| 5 | [opensumi/core](https://github.com/opensumi/core) | 3662 | 453 / 286 | 2026-10-15T08:20:10Z | MIT | 活跃(23d) | `active` | 15/25 (fc1 eff5 compat3 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；A framework helps you quickly build AI Native IDE products. MCP Clie… |

**取值命令与匹配理由**
1. `ThinkInAIXYZ/deepchat` — `gh api repos/ThinkInAIXYZ/deepchat --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=25；🐬DeepChat - A smart assistant that connects powerful AI to your personal world ｜ ⚠️缓存→现测：6370/2026-10-24/Apache-2.0 → 6383/2026-11-06T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=25
2. `NanmiCoder/cc-haha` — `gh api repos/NanmiCoder/cc-haha --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=4；本地优先的跨平台 Claude Code / AI Agent 桌面工作台：多 Agent 协作、Git Worktree、代码 Diff、技能市场、多模型、Computer Use、桌面宠物；支持微 ｜ ⚠️缓存→现测：15156/2026-10-23/NOASSERTION → 15338/2026-11-05T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=4
3. `DayuanJiang/next-ai-draw-io` — `gh api repos/DayuanJiang/next-ai-draw-io --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；Draw and edit draw.io diagrams by chatting with an AI. Web app, desktop app, and an MCP server for C ｜ ⚠️缓存→现测：36405/2026-10-24/Apache-2.0 → 36741/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=0
4. `op7418/CodePilot` — `gh api repos/op7418/CodePilot --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=9；A multi-model AI agent desktop client — connect any AI provider, extend with MCP & skills, control f ｜ ⚠️缓存→现测：6506/2026-09-22/NOASSERTION → 6518/2026-09-22T0…/NOASSERTION（stars 漂移） ｜ SKILL.md=9
5. `opensumi/core` — `gh api repos/opensumi/core --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；A framework helps you quickly build AI Native IDE products. MCP Client, supports Model Context Proto ｜ ⚠️缓存→现测：3659/2026-10-15/MIT → 3662/2026-10-15T0…/MIT（stars 漂移） ｜ SKILL.md=0

### 7.23 `dogfood` ｜ HIGH ｜ 候选线索（元数据已实测，功能等价待复核）

- **功能边界**：系统化探索和测试本地Web应用 — 浏览器QA。应用探索测试。适用：本地/开发服务器已启动、需要模拟真实用户走查页面与QA验收时使用；触发词：dogfood、应用探索测试、浏览器QA、页面走查、本地Web测试（desc_len=104；SKILL.md bytes=11882）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：UNVERIFIED（candidates_n=5，skill_relevant_n=0，trim=0） ｜ **语义缺口**：是 ｜ **声明上游**：[microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp)（in_face=否）
- **族级补位（禁当替代引用）**：[stablyai/orca](https://github.com/stablyai/orca)、[ruvnet/RuView](https://github.com/ruvnet/RuView)、[Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)、[langgenius/dify](https://github.com/langgenius/dify)、[Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach)（共 5 件，`not_replacement=true`）

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [petrkindlmann/qa-skills](https://github.com/petrkindlmann/qa-skills) | 253 | 41 / 2 | 2026-10-22T09:52:03Z | MIT | 活跃(16d) | `active` | 线索分 8.01 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=50；stars=253；description=50 QA and test-automation skills for Claude Code, Codex, Cursor, and … |
| 2 | [MylesMCook/browser-probe](https://github.com/MylesMCook/browser-probe) | 0 | 0 / 0 | 2026-03-15T23:53:41Z | MIT | 一般(236d) | `active` | 线索分 7 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [第二遍精确检索] SKILL.md=1；stars=0；description=Exploratory browser testing skill built on agent-browser |
| 3 | [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | 57399 | 4920 / 1164 | 2026-11-06T18:08:41Z | NOASSERTION | 活跃(0d) | `active` | 线索分 6.15 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [第一遍定向检索] SKILL.md=0；stars=57399；description=A hand-picked collection of the finest of resources for the most … |
| 4 | [microsoft/CUAWright](https://github.com/microsoft/CUAWright) | 6093 | 389 / 55 | 2026-10-27T03:03:47Z | MIT | 活跃(11d) | `active` | 线索分 6.12 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=1；stars=6093；description=A simple SWE-style browser+desktop agent framework that achieves SOTA… |
| 5 | [BMayhew/awesome-sites-to-test-on](https://github.com/BMayhew/awesome-sites-to-test-on) | 1120 | 179 / 0 | 2026-10-30T21:24:15Z | NOASSERTION | 活跃(7d) | `active` | 线索分 6.02 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [第一遍定向检索] SKILL.md=1；stars=1120；description=A curated list of sites to practice testing on |

**取值命令与匹配理由**
1. `petrkindlmann/qa-skills` — `gh api repos/petrkindlmann/qa-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=50；stars=253；description=50 QA and test-automation skills for Claude Code, Codex, Cursor, and any Agent Skills Standard runtime. ｜ SKILL.md=50 ｜ `gh api repos/petrkindlmann/qa-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
2. `MylesMCook/browser-probe` — `gh api repos/MylesMCook/browser-probe --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [第二遍精确检索] SKILL.md=1；stars=0；description=Exploratory browser testing skill built on agent-browser ｜ SKILL.md=1 ｜ `gh api repos/MylesMCook/browser-probe/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
3. `hesreallyhim/awesome-claude-code` — `gh api repos/hesreallyhim/awesome-claude-code --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [第一遍定向检索] SKILL.md=0；stars=57399；description=A hand-picked collection of the finest of resources for the most awesome of agents, Claude Code, the undisputed champion of coding companion ｜ SKILL.md=0 ｜ `gh api repos/hesreallyhim/awesome-claude-code/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核
4. `microsoft/CUAWright` — `gh api repos/microsoft/CUAWright --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=1；stars=6093；description=A simple SWE-style browser+desktop agent framework that achieves SOTA results on long-horizon CUA tasks ｜ SKILL.md=1 ｜ `gh api repos/microsoft/CUAWright/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
5. `BMayhew/awesome-sites-to-test-on` — `gh api repos/BMayhew/awesome-sites-to-test-on --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [第一遍定向检索] SKILL.md=1；stars=1120；description=A curated list of sites to practice testing on ｜ SKILL.md=1 ｜ `gh api repos/BMayhew/awesome-sites-to-test-on/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`

### 7.24 `fenjue-lessons-hitrate` ｜ HIGH ｜ 候选线索（元数据已实测，功能等价待复核）

- **功能边界**：Use when 涉及焚诀第四主线 lessons 命中率度量——把"记住教训"升级为"用上教训"，行为指纹扫描+收尾门禁。（desc_len=62；SKILL.md bytes=3275）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：FAMILY_ONLY（candidates_n=5，skill_relevant_n=2，trim=0） ｜ **语义缺口**：是 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：[affaan-m/ECC](https://github.com/affaan-m/ECC)、[morluto/rea](https://github.com/morluto/rea)、[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)（共 3 件，`not_replacement=true`）

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [mem0ai/mem0](https://github.com/mem0ai/mem0) | 68528 | 8143 / 920 | 2026-11-06T16:53:07Z | Apache-2.0 | 活跃(0d) | `active` | 线索分 7.37 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=56；stars=68528；description=The Memory Layer for AI Agents - Drop-in memory infrastructure for … |
| 2 | [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) | 30176 | 2672 / 502 | 2026-11-06T19:42:17Z | Apache-2.0 | 活跃(0d) | `active` | 线索分 6.6 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=17；stars=30176；description=#1 Persistent memory for AI coding agents based on real-world bench… |
| 3 | [Ikalus1988/MisakaNet](https://github.com/Ikalus1988/MisakaNet) | 554 | 228 / 365 | 2026-11-06T19:54:22Z | Apache-2.0 | 活跃(0d) | `active` | 线索分 6.01 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=3；stars=554；description=Re-debugging Solved Failures? No Way. 500+ Evidence-graded fix lessons… |
| 4 | [gepa-ai/gepa](https://github.com/gepa-ai/gepa) | 7317 | 609 / 158 | 2026-11-06T07:05:30Z | MIT | 活跃(1d) | `active` | 线索分 4.15 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=1；stars=7317；description=Optimize prompts, code, and more with AI-powered Reflective Optimizat… |
| 5 | [letta-ai/letta](https://github.com/letta-ai/letta) | 25369 | 2670 / 0 | 2026-10-18T22:28:04Z | Apache-2.0 | 活跃(19d) | `active` | 线索分 3.51 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=0；stars=25369；description=Platform for stateful agents: AI with advanced memory that can learn… |

**取值命令与匹配理由**
1. `mem0ai/mem0` — `gh api repos/mem0ai/mem0 --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=56；stars=68528；description=The Memory Layer for AI Agents - Drop-in memory infrastructure for AI agents and apps. Context that persists. Built for production. ｜ SKILL.md=56 ｜ `gh api repos/mem0ai/mem0/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
2. `rohitg00/agentmemory` — `gh api repos/rohitg00/agentmemory --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=17；stars=30176；description=#1 Persistent memory for AI coding agents based on real-world benchmarks ｜ SKILL.md=17 ｜ `gh api repos/rohitg00/agentmemory/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
3. `Ikalus1988/MisakaNet` — `gh api repos/Ikalus1988/MisakaNet --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=3；stars=554；description=Re-debugging Solved Failures? No Way. 500+ Evidence-graded fix lessons, One MCP Call-->https://misakanet.org ｜ SKILL.md=3 ｜ `gh api repos/Ikalus1988/MisakaNet/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
4. `gepa-ai/gepa` — `gh api repos/gepa-ai/gepa --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=1；stars=7317；description=Optimize prompts, code, and more with AI-powered Reflective Optimization ｜ SKILL.md=1 ｜ `gh api repos/gepa-ai/gepa/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
5. `letta-ai/letta` — `gh api repos/letta-ai/letta --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=0；stars=25369；description=Platform for stateful agents: AI with advanced memory that can learn and self-improve over time. ｜ SKILL.md=0 ｜ `gh api repos/letta-ai/letta/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核

### 7.25 `fenjue-memory-audit` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：焚诀全局记忆三视角融合审计 — 前端体验(40%)+认知工程(40%)+账面健康(20%)=160分制（三视角内部满分各100=维度合计）。覆盖算力消耗感知、skill调用丝滑度、对话舒适度、系统自愈率、版本一致性、大文件分类治理、路由追问能力、经验查找命中率、用户价值占比、可移植性、规则密度等全部维度。30维(D1-D30)测量以 fenjue_measure.py 实跑为准。触发词覆盖原A-memory-align+fenjue-c（desc_len=261；SKILL.md bytes=9768）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 298441 | 44116 / 236 | 2026-11-06T05:29:44Z | MIT | 活跃(1d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instin… |
| 2 | [mksglu/context-mode](https://github.com/mksglu/context-mode) | 33601 | 2306 / 3 | 2026-11-06T15:43:52Z | NOASSERTION | 活跃(0d) | `active` | 21/25 (fc4 eff5 compat4 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=4/5；SKILL.md=11；Context window optimization for AI coding agents. Sandboxes tool ou… |
| 3 | [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) | 18315 | 1510 / 58 | 2026-10-12T02:06:40Z | MIT | 活跃(26d) | `active` | 19/25 (fc4 eff2 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；A comprehensive collection of Agent Skills for context engineering,… |
| 4 | [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) | 30573 | 2983 / 887 | 2026-11-04T11:33:40Z | NOASSERTION | 活跃(3d) | `active` | 16/25 (fc2 eff2 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；TencentDB Agent Memory is a team-level memory hub for AI Agents — tu… |
| 5 | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 63535 | 4118 / 115 | 2026-09-14T19:29:02Z | MIT | 活跃(53d) | `active` | 15/25 (fc2 eff0 compat5 docs3 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A coding-agent skill for multi-phase security audits with independen… |

**取值命令与匹配理由**
1. `affaan-m/ECC` — `gh api repos/affaan-m/ECC --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instincts, memory, security, and research ｜ ⚠️缓存→现测：288271/2026-10-20/MIT → 298441/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1062
2. `mksglu/context-mode` — `gh api repos/mksglu/context-mode --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=4/5；SKILL.md=11；Context window optimization for AI coding agents. Sandboxes tool output (98% reduction), persists se ｜ ⚠️缓存→现测：32150/2026-10-24/NOASSERTION → 33601/2026-11-06T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=11
3. `muratcankoylan/Agent-Skills-for-Context-Engineering` — `gh api repos/muratcankoylan/Agent-Skills-for-Context-Engineering --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；A comprehensive collection of Agent Skills for context engineering, multi-agent architectures, and p ｜ ⚠️缓存→现测：18208/2026-10-12/MIT → 18315/2026-10-12T0…/MIT（stars 漂移） ｜ SKILL.md=24
4. `TencentCloud/TencentDB-Agent-Memory` — `gh api repos/TencentCloud/TencentDB-Agent-Memory --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；TencentDB Agent Memory is a team-level memory hub for AI Agents — turning conversations, docs, and c ｜ ⚠️缓存→现测：29900/2026-10-21/NOASSERTION → 30573/2026-11-04T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=2
5. `cloudflare/security-audit-skill` — `gh api repos/cloudflare/security-audit-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A coding-agent skill for multi-phase security audits with independently verified, machine-readable f ｜ ⚠️缓存→现测：53489/2026-09-14/MIT → 63535/2026-09-14T1…/MIT（stars 漂移） ｜ SKILL.md=1

### 7.26 `hermes-installer` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：安装/下载 Hermes Agent（桌面版与 CLI），含中国大陆 GFW 阻断修复。用于 Hermes 安装失败、下载 Hermes、Hermes-Setup.exe 报 INSTALL DIDN'T FINISH、raw.githubusercontent.com 被拒、git clone 被 RST 等场景。（desc_len=159；SKILL.md bytes=2512）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=3，skill_relevant_n=3，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [rlaope/oh-my-hermes](https://github.com/rlaope/oh-my-hermes) | 5203 | 413 / 12 | 2026-11-06T18:11:33Z | MIT | 活跃(0d) | `active` | 23/25 (fc5 eff5 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=274；The coding intelligence and skills for Hermes Agent ⚚ just install… |
| 2 | [Devin-AXIS/iPolloWork](https://github.com/Devin-AXIS/iPolloWork) | 7410 | 1135 / 91 | 2026-11-06T09:23:22Z | NOASSERTION | 活跃(1d) | `active` | 18/25 (fc5 eff5 compat1 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=1/5；SKILL.md=109；Enterprise-grade, local-first Agent Workbench for people and agent… |
| 3 | [lennney/stop-that-shit](https://github.com/lennney/stop-that-shit) | 3693 | 76 / 4 | 2026-11-05T12:35:36Z | MIT | 活跃(1d) | `active` | 16/25 (fc2 eff3 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Stop That Shit（别再造史了）｜面向 Codex/GPT 场景的多平台 Hook + Skill Guard：拦截 AI c… |

**取值命令与匹配理由**
1. `rlaope/oh-my-hermes` — `gh api repos/rlaope/oh-my-hermes --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=274；The coding intelligence and skills for Hermes Agent ⚚ just install once. then type 'dag-ulw' to be g ｜ ⚠️缓存→现测：4013/2026-10-25/MIT → 5203/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=274
2. `Devin-AXIS/iPolloWork` — `gh api repos/Devin-AXIS/iPolloWork --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=1/5；SKILL.md=109；Enterprise-grade, local-first Agent Workbench for people and agent teams. A unified multi-engine wor ｜ ⚠️缓存→现测：7284/2026-10-24/NOASSERTION → 7410/2026-11-06T0…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=109
3. `lennney/stop-that-shit` — `gh api repos/lennney/stop-that-shit --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Stop That Shit（别再造史了）｜面向 Codex/GPT 场景的多平台 Hook + Skill Guard：拦截 AI coding agent 无需求的哈希、校验和与任务范围膨胀。 A ｜ ⚠️缓存→现测：3142/2026-10-24/MIT → 3693/2026-11-05T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=2

### 7.27 `hook-analyzer-skill` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：视频前三秒钩子分析技能。从分镜拆解结果中提取前三秒分镜数据，为钩子吸引力评估提供结构化上下文。运行脚本 'python scripts/analyze_hook_segments.py "<breakdown_json_file>"' 或通过 stdin 传入 JSON。输出包含前三秒分镜数量、总时长和每个分镜的详细信息（含关键帧 URL）。触发词：钩子分析、前三秒、hook 分析；当分镜已拆解完成、需要评估开场吸引力时使用。（desc_len=215；SKILL.md bytes=5471）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=10，trim=2） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [xberg-io/xberg](https://github.com/xberg-io/xberg) | 9554 | 612 / 40 | 2026-11-06T18:44:42Z | MIT | 活跃(0d) | `active` | 20/25 (fc4 eff5 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=75；Polyglot document intelligence with a Rust core: extract text, meta… |
| 2 | [wiltodelta/remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks) | 6295 | 588 / 2 | 2026-11-06T01:27:32Z | Apache-2.0 | 活跃(1d) | `active` | 20/25 (fc3 eff4 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Remove visible and invisible AI watermarks from images and video, an… |
| 3 | [EL4CTEO/blender-skills](https://github.com/EL4CTEO/blender-skills) | 742 | 75 / 3 | 2026-10-30T20:35:01Z | MIT | 活跃(7d) | `active` | 17/25 (fc4 eff3 compat5 docs3 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=22；Professional Blender 5.2 workflows as Agent Skills for Claude Code,… |
| 4 | [RobLe3/cc-blender-skill](https://github.com/RobLe3/cc-blender-skill) | 145 | 16 / 0 | 2026-10-12T15:39:04Z | MIT | 活跃(25d) | `active` | 16/25 (fc4 eff1 compat5 docs4 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=32；Claude Code skill plugin: drive Blender 5.x like a senior 3D artist… |
| 5 | [liustack/modlens](https://github.com/liustack/modlens) | 4815 | 151 / 4 | 2026-10-23T15:42:48Z | MIT | 活跃(14d) | `active` | 15/25 (fc2 eff1 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；The first vision plugin for DeepSeek Harness, and the vision bridge … |

**取值命令与匹配理由**
1. `xberg-io/xberg` — `gh api repos/xberg-io/xberg --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=75；Polyglot document intelligence with a Rust core: extract text, metadata, images, tables, and structu ｜ ⚠️缓存→现测：9444/2026-10-24/MIT → 9554/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=75
2. `wiltodelta/remove-ai-watermarks` — `gh api repos/wiltodelta/remove-ai-watermarks --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Remove visible and invisible AI watermarks from images and video, and AI provenance metadata from im ｜ ⚠️缓存→现测：6115/2026-10-24/Apache-2.0 → 6295/2026-11-06T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=4
3. `EL4CTEO/blender-skills` — `gh api repos/EL4CTEO/blender-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=22；Professional Blender 5.2 workflows as Agent Skills for Claude Code, Codex, Gemini CLI, Copilot and C ｜ ⚠️缓存→现测：481/2026-10-19/MIT → 742/2026-10-30T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=22
4. `RobLe3/cc-blender-skill` — `gh api repos/RobLe3/cc-blender-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=32；Claude Code skill plugin: drive Blender 5.x like a senior 3D artist via natural language. 10 chain-l ｜ ⚠️缓存→现测：125/2026-10-12/MIT → 145/2026-10-12T1…/MIT（stars 漂移） ｜ SKILL.md=32
5. `liustack/modlens` — `gh api repos/liustack/modlens --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；The first vision plugin for DeepSeek Harness, and the vision bridge for every text-only coding agent ｜ ⚠️缓存→现测：4446/2026-10-23/MIT → 4815/2026-10-23T1…/MIT（stars 漂移） ｜ SKILL.md=1

### 7.28 `html-to-docx-win-fix` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：修复 tencent-docx 内置插件的 setup-html-to-docx.sh 在 Windows/Git Bash 下静默失败（uv 把 MSYS 路径 /c/... 当相对路径 → venv 建到 D:\c\...，且脚本按 Linux 的 bin/python 探测）。触发场景：html-to-docx 环境准备卡在「▶ Creating venv」后无输出、文档转换报 ModuleNotFoundError、或磁盘上出现（desc_len=249；SKILL.md bytes=4554）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=10，trim=2） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [genspark-ai/genoffice](https://github.com/genspark-ai/genoffice) | 11848 | 1640 / 59 | 2026-11-06T12:26:32Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc4 eff4 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Free, open-source AI Office suite: Docs, Sheets, Slides, PDF, Markd… |
| 2 | [bowenliang123/markdown-exporter](https://github.com/bowenliang123/markdown-exporter) | 274 | 69 / 12 | 2026-08-13T02:30:02Z | Apache-2.0 | 活跃(86d) | `active` | 15/25 (fc2 eff3 compat5 docs3 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；An Agent Skill and Dify plugin to transform Markdown to files of DOC… |
| 3 | [appautomaton/document-SKILLs](https://github.com/appautomaton/document-SKILLs) | 181 | 12 / 0 | 2026-10-15T15:04:58Z | MIT | 活跃(22d) | `active` | 15/25 (fc3 eff2 compat5 docs3 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Claude Code and Codex SKILLs for PDF, Excel, Word, and PowerPoint ma… |
| 4 | [Gostyan/docx-skill-4-cn-paper](https://github.com/Gostyan/docx-skill-4-cn-paper) | 475 | 17 / 2 | 2026-07-12T12:49:14Z | MIT | 一般(117d) | `active` | 12/25 (fc2 eff0 compat5 docs3 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；中文论文常用排版格式Skills，适用于课程论文、数模竞赛、毕业论文等场景，让llm agent写word论文或者将.md转.docx时… |
| 5 | [LegalRabbit-AI/legalrabbit-docx-mcp](https://github.com/LegalRabbit-AI/legalrabbit-docx-mcp) | 56 | 6 / 0 | 2026-09-01T06:50:11Z | MIT | 活跃(67d) | `active` | 12/25 (fc2 eff1 compat5 docs3 comm1) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A docx plugin for Codex and Claude Cowork. Uses 2-5X fewer tokens co… |

**取值命令与匹配理由**
1. `genspark-ai/genoffice` — `gh api repos/genspark-ai/genoffice --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Free, open-source AI Office suite: Docs, Sheets, Slides, PDF, Markdown and HTML editors with a built ｜ ⚠️缓存→现测：10764/2026-10-24/Apache-2.0 → 11848/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=43
2. `bowenliang123/markdown-exporter` — `gh api repos/bowenliang123/markdown-exporter --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；An Agent Skill and Dify plugin to transform Markdown to files of DOCX, PPTX, XLSX, PNG, PDF, HTML, M ｜ SKILL.md=1
3. `appautomaton/document-SKILLs` — `gh api repos/appautomaton/document-SKILLs --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Claude Code and Codex SKILLs for PDF, Excel, Word, and PowerPoint manipulation — extraction, forms, ｜ ⚠️缓存→现测：174/2026-10-15/MIT → 181/2026-10-15T1…/MIT（stars 漂移） ｜ SKILL.md=4
4. `Gostyan/docx-skill-4-cn-paper` — `gh api repos/Gostyan/docx-skill-4-cn-paper --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；中文论文常用排版格式Skills，适用于课程论文、数模竞赛、毕业论文等场景，让llm agent写word论文或者将.md转.docx时可调用 ｜ ⚠️缓存→现测：460/2026-07-12/MIT → 475/2026-07-12T1…/MIT（stars 漂移） ｜ SKILL.md=1
5. `LegalRabbit-AI/legalrabbit-docx-mcp` — `gh api repos/LegalRabbit-AI/legalrabbit-docx-mcp --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A docx plugin for Codex and Claude Cowork. Uses 2-5X fewer tokens compared to the Anthropic's docx s ｜ SKILL.md=1

### 7.29 `ican-deploy` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：iCAN 门店 AI 管理智能体（Python/Flask）的部署与地址名册。PythonAnywhere 免费层全自动部署通道（API 只认表单编码 / 控制台需浏览器唤醒 / WSGI 导入期引导执行 / 改默认 wsgi 文件）、环境变量与 DeepSeek 在线 AI 配置、上线验证清单，以及「真实系统 vs 静态快照站 vs 本地离线」的地址名册口径（避免混淆）。触发词：iCAN 部署、重部、PythonAnywhere、部署（desc_len=285；SKILL.md bytes=10286）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 81071 | 9543 / 654 | 2026-11-06T18:31:29Z | MIT | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swa… |
| 2 | [iflytek/skillhub](https://github.com/iflytek/skillhub) | 5372 | 816 / 34 | 2026-11-06T10:25:31Z | Apache-2.0 | 活跃(1d) | `active` | 22/25 (fc4 eff5 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；Self-hosted, open-source agent skill registry for enterprises. Publ… |
| 3 | [agentscope-ai/QwenPaw](https://github.com/agentscope-ai/QwenPaw) | 37422 | 3264 / 1110 | 2026-11-06T10:39:00Z | Apache-2.0 | 活跃(1d) | `active` | 21/25 (fc4 eff5 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=49；Your Personal AI Assistant; easy to install, deploy on your own mac… |
| 4 | [langgenius/dify](https://github.com/langgenius/dify) | 160565 | 25406 / 1205 | 2026-11-06T18:33:42Z | NOASSERTION | 活跃(0d) | `active` | 19/25 (fc3 eff5 compat1 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=7；Build Agentic workflows, RAG pipelines, with rich AI model and tool … |
| 5 | [glitternetwork/pinme](https://github.com/glitternetwork/pinme) | 3754 | 276 / 10 | 2026-09-12T05:23:49Z | MIT | 活跃(56d) | `active` | 17/25 (fc3 eff3 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Deploy Your Frontend in a Single Command. Claude Code Skills support… |

**取值命令与匹配理由**
1. `ruvnet/ruflo` — `gh api repos/ruvnet/ruflo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swarms, coordinate autonomous workflo ｜ ⚠️缓存→现测：79103/2026-10-25/MIT → 81071/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=389
2. `iflytek/skillhub` — `gh api repos/iflytek/skillhub --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=24；Self-hosted, open-source agent skill registry for enterprises. Publish & version skill packages, gov ｜ ⚠️缓存→现测：5283/2026-10-25/Apache-2.0 → 5372/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=24
3. `agentscope-ai/QwenPaw` — `gh api repos/agentscope-ai/QwenPaw --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=49；Your Personal AI Assistant; easy to install, deploy on your own machine or on the cloud; supports mu ｜ ⚠️缓存→现测：36092/2026-10-23/Apache-2.0 → 37422/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=49
4. `langgenius/dify` — `gh api repos/langgenius/dify --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=7；Build Agentic workflows, RAG pipelines, with rich AI model and tool support on one collaborative wor ｜ ⚠️缓存→现测：159795/2026-10-28/NOASSERTION → 160565/2026-11-06T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=7
5. `glitternetwork/pinme` — `gh api repos/glitternetwork/pinme --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Deploy Your Frontend in a Single Command. Claude Code Skills supported. ｜ ⚠️缓存→现测：3755/2026-09-12/MIT → 3754/2026-09-12T0…/MIT（stars 漂移） ｜ SKILL.md=7

### 7.30 `ican-frontend-design-system` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：iCAN 门店 AI 管理智能体（Flask + Jinja + 单 CSS 原生前端）的 V4 设计体系与交付链。含「雾山青」令牌表（色彩/间距/字阶/圆角/高程/动效/图表分类色板）、指标带与分割行范式、44px 触控基线、全站 class 清单，以及「改 dev → 三副本同步 → 重建演示快照集 → quality_gate 第10项」的强制交付命令。触发词：iCAN 前端、门店管理助手界面、改 style.css、V3 设计体（desc_len=288；SKILL.md bytes=59528）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [nexu-io/open-design](https://github.com/nexu-io/open-design) | 106289 | 12099 / 1371 | 2026-11-06T15:40:39Z | Apache-2.0 | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and o… |
| 2 | [Manavarya09/design-extract](https://github.com/Manavarya09/design-extract) | 4815 | 405 / 19 | 2026-11-05T08:50:20Z | MIT | 活跃(2d) | `active` | 20/25 (fc4 eff4 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=26；Extract any website's complete design system with one command. DTCG… |
| 3 | [asgeirtj/system_prompts_leaks](https://github.com/asgeirtj/system_prompts_leaks) | 70938 | 11460 / 22 | 2026-11-06T18:56:42Z | CC0-1.0 | 活跃(0d) | `active` | 18/25 (fc5 eff0 compat5 docs3 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=232；Documented system prompts from Anthropic - Claude Fable 5.1, Opus … |
| 4 | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | 65476 | 4336 / 53 | 2026-11-06T15:20:25Z | MIT | 活跃(0d) | `active` | 18/25 (fc2 eff2 compat5 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Editorial diagram design for Claude Code, Codex, GitHub Copilot, Cur… |
| 5 | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | 111152 | 7467 / 8 | 2026-11-05T01:12:12Z | MIT | 活跃(2d) | `active` | 17/25 (fc2 eff2 compat5 docs3 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent skills that give coding agents taste: art direction, reference… |

**取值命令与匹配理由**
1. `nexu-io/open-design` — `gh api repos/nexu-io/open-design --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and open source. Create motion, prototy ｜ ⚠️缓存→现测：103811/2026-10-25/Apache-2.0 → 106289/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=553
2. `Manavarya09/design-extract` — `gh api repos/Manavarya09/design-extract --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=26；Extract any website's complete design system with one command. DTCG tokens, semantic+primitive+compo ｜ ⚠️缓存→现测：4365/2026-10-23/MIT → 4815/2026-11-05T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=26
3. `asgeirtj/system_prompts_leaks` — `gh api repos/asgeirtj/system_prompts_leaks --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=232；Documented system prompts from Anthropic - Claude Fable 5.1, Opus 5.5, Claude Design, Claude Code. O ｜ ⚠️缓存→现测：70163/2026-10-24/CC0-1.0 → 70938/2026-11-06T1…/CC0-1.0（stars,pushed_at 漂移） ｜ SKILL.md=232
4. `cathrynlavery/diagram-design` — `gh api repos/cathrynlavery/diagram-design --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Editorial diagram design for Claude Code, Codex, GitHub Copilot, Cursor, Factory Droid, Qoder, and P ｜ ⚠️缓存→现测：60806/2026-10-24/MIT → 65476/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1
5. `Leonxlnx/taste-skill` — `gh api repos/Leonxlnx/taste-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent skills that give coding agents taste: art direction, reference images and a browser check inst ｜ ⚠️缓存→现测：106146/2026-10-30/MIT → 111152/2026-11-05T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.31 `local-asr` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：Intel Local Windows ASR (本地离线语音识别). Use this skill when the user, in Chinese or English, asks to transcribe audio or video files, convert speech to text, or extract text from a recording. Trigger on Chinese verbs like 转录（desc_len=861；SKILL.md bytes=4908）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=6，trim=2） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [nexu-io/open-design](https://github.com/nexu-io/open-design) | 106289 | 12099 / 1371 | 2026-11-06T15:40:39Z | Apache-2.0 | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and o… |
| 2 | [openclaw/Peekaboo](https://github.com/openclaw/Peekaboo) | 5444 | 417 / 7 | 2026-11-05T23:37:09Z | MIT | 活跃(1d) | `active` | 21/25 (fc3 eff5 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents… |
| 3 | [SharpAI/DeepCamera](https://github.com/SharpAI/DeepCamera) | 3134 | 490 / 19 | 2026-09-17T00:43:07Z | MIT | 活跃(51d) | `active` | 19/25 (fc4 eff3 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=25；Open-Source AI Camera Skills Platform, AI NVR & CCTV Surveillance. … |
| 4 | [equalang/equalang-skill](https://github.com/equalang/equalang-skill) | 78 | 0 / 0 | 2026-11-03T07:35:58Z | Apache-2.0 | 活跃(4d) | `active` | 12/25 (fc2 eff1 compat5 docs3 comm1) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent Skill for Equalang: translate PDF, DOCX, PPTX, XLSX, EPUB, sub… |
| 5 | [shaom/brand-to-design-md-skill](https://github.com/shaom/brand-to-design-md-skill) | 211 | 18 / 0 | 2026-08-08T03:26:40Z | NOASSERTION | 一般(91d) | `active` | 10/25 (fc2 eff0 compat3 docs3 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=3/5；SKILL.md=1；A portable local skill that turns a public brand URL into a source-a… |

**取值命令与匹配理由**
1. `nexu-io/open-design` — `gh api repos/nexu-io/open-design --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and open source. Create motion, prototy ｜ ⚠️缓存→现测：103811/2026-10-25/Apache-2.0 → 106289/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=553
2. `openclaw/Peekaboo` — `gh api repos/openclaw/Peekaboo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents to capture screenshots of appli ｜ ⚠️缓存→现测：5383/2026-10-24/MIT → 5444/2026-11-05T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=4
3. `SharpAI/DeepCamera` — `gh api repos/SharpAI/DeepCamera --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=25；Open-Source AI Camera Skills Platform, AI NVR & CCTV Surveillance. Local VLM video analysis with Qwe ｜ ⚠️缓存→现测：3110/2026-09-17/MIT → 3134/2026-09-17T0…/MIT（stars 漂移） ｜ SKILL.md=25
4. `equalang/equalang-skill` — `gh api repos/equalang/equalang-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent Skill for Equalang: translate PDF, DOCX, PPTX, XLSX, EPUB, subtitles, pictures, audio and vide ｜ ⚠️缓存→现测：39/2026-10-12/Apache-2.0 → 78/2026-11-03T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=1
5. `shaom/brand-to-design-md-skill` — `gh api repos/shaom/brand-to-design-md-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=3/5；SKILL.md=1；A portable local skill that turns a public brand URL into a source-aware DESIGN.md, extracting visua ｜ ⚠️缓存→现测：209/2026-08-08/UNLICENSED → 211/2026-08-08T0…/NOASSERTION（stars,license 漂移） ｜ SKILL.md=1

### 7.32 `local-computer-use` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：Intel Local Windows Computer Use (本地计算机使用). Use this skill when the user, in Chinese or English, asks to query or change Windows system state/settings in the supported categories. Trigger on Chinese verbs like 打开/开启/关闭/设（desc_len=987；SKILL.md bytes=5863）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=11，trim=1） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [feder-cr/invisible_dots](https://github.com/feder-cr/invisible_dots) | 44 | 7 / 0 | 2026-11-04T09:06:23Z | MIT | 活跃(3d) | `active` | 19/25 (fc2 eff4 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Open-source, self-hosted alternative to OpenAI Dots, Grok Bot. Built… |
| 2 | [NanmiCoder/cc-haha](https://github.com/NanmiCoder/cc-haha) | 15338 | 8612 / 205 | 2026-11-05T15:03:01Z | NOASSERTION | 活跃(1d) | `active` | 18/25 (fc3 eff5 compat1 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=4；本地优先的跨平台 Claude Code / AI Agent 桌面工作台：多 Agent 协作、Git Worktree、代码 Dif… |
| 3 | [feder-cr/invisible_playwright_mcp](https://github.com/feder-cr/invisible_playwright_mcp) | 871 | 118 / 9 | 2026-10-21T20:36:34Z | MIT | 活跃(16d) | `active` | 18/25 (fc2 eff4 compat5 docs5 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Playwright MCP server undetected by anti-bots and captchas: AI agent… |
| 4 | [browser-use/browser-harness](https://github.com/browser-use/browser-harness) | 18905 | 1865 / 440 | 2026-11-06T00:07:22Z | MIT | 活跃(1d) | `active` | 17/25 (fc3 eff2 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=3；Let Claude Code, Codex or Cursor use your real Chrome, logged in as … |
| 5 | [CursorTouch/Windows-MCP](https://github.com/CursorTouch/Windows-MCP) | 11186 | 1210 / 36 | 2026-11-06T16:35:28Z | MIT | 活跃(0d) | `active` | 17/25 (fc2 eff3 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；MCP Server for Computer Use in Windows |

**取值命令与匹配理由**
1. `feder-cr/invisible_dots` — `gh api repos/feder-cr/invisible_dots --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Open-source, self-hosted alternative to OpenAI Dots, Grok Bot. Built to be undetectable by anti-bot ｜ ⚠️缓存→现测：32235/2026-10-25/MIT → 44/2026-11-04T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1
2. `NanmiCoder/cc-haha` — `gh api repos/NanmiCoder/cc-haha --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=4；本地优先的跨平台 Claude Code / AI Agent 桌面工作台：多 Agent 协作、Git Worktree、代码 Diff、技能市场、多模型、Computer Use、桌面宠物；支持微 ｜ ⚠️缓存→现测：15156/2026-10-23/NOASSERTION → 15338/2026-11-05T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=4
3. `feder-cr/invisible_playwright_mcp` — `gh api repos/feder-cr/invisible_playwright_mcp --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Playwright MCP server undetected by anti-bots and captchas: AI agent browses the web on anti-detect ｜ ⚠️缓存→现测：878/2026-10-21/MIT → 871/2026-10-21T2…/MIT（stars 漂移） ｜ SKILL.md=1
4. `browser-use/browser-harness` — `gh api repos/browser-use/browser-harness --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=3；Let Claude Code, Codex or Cursor use your real Chrome, logged in as you. One prompt to set up. Open ｜ ⚠️缓存→现测：18600/2026-10-25/MIT → 18905/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=3
5. `CursorTouch/Windows-MCP` — `gh api repos/CursorTouch/Windows-MCP --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；MCP Server for Computer Use in Windows ｜ ⚠️缓存→现测：10260/2026-10-24/MIT → 11186/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.33 `local-img2img` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：Intel Local Image-to-Image (本地图像编辑). Use this skill when the user asks to modify, edit, restyle, transform, or regenerate an existing image from a source image and a prompt. Trigger on Chinese requests like 修改图片/编辑图片/图生图（desc_len=453；SKILL.md bytes=3786）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=5，trim=2） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [nexu-io/open-design](https://github.com/nexu-io/open-design) | 106289 | 12099 / 1371 | 2026-11-06T15:40:39Z | Apache-2.0 | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and o… |
| 2 | [openclaw/Peekaboo](https://github.com/openclaw/Peekaboo) | 5444 | 417 / 7 | 2026-11-05T23:37:09Z | MIT | 活跃(1d) | `active` | 21/25 (fc3 eff5 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents… |
| 3 | [SharpAI/DeepCamera](https://github.com/SharpAI/DeepCamera) | 3134 | 490 / 19 | 2026-09-17T00:43:07Z | MIT | 活跃(51d) | `active` | 19/25 (fc4 eff3 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=25；Open-Source AI Camera Skills Platform, AI NVR & CCTV Surveillance. … |
| 4 | [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) | 48225 | 3977 / 555 | 2026-11-04T23:21:44Z | MIT | 活跃(2d) | `active` | 17/25 (fc1 eff5 compat3 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；Local code intelligence for developers and AI agents. Connect code, … |
| 5 | [shaom/brand-to-design-md-skill](https://github.com/shaom/brand-to-design-md-skill) | 211 | 18 / 0 | 2026-08-08T03:26:40Z | NOASSERTION | 一般(91d) | `active` | 10/25 (fc2 eff0 compat3 docs3 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=3/5；SKILL.md=1；A portable local skill that turns a public brand URL into a source-a… |

**取值命令与匹配理由**
1. `nexu-io/open-design` — `gh api repos/nexu-io/open-design --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and open source. Create motion, prototy ｜ ⚠️缓存→现测：103811/2026-10-25/Apache-2.0 → 106289/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=553
2. `openclaw/Peekaboo` — `gh api repos/openclaw/Peekaboo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents to capture screenshots of appli ｜ ⚠️缓存→现测：5383/2026-10-24/MIT → 5444/2026-11-05T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=4
3. `SharpAI/DeepCamera` — `gh api repos/SharpAI/DeepCamera --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=25；Open-Source AI Camera Skills Platform, AI NVR & CCTV Surveillance. Local VLM video analysis with Qwe ｜ ⚠️缓存→现测：3110/2026-09-17/MIT → 3134/2026-09-17T0…/MIT（stars 漂移） ｜ SKILL.md=25
4. `DeusData/codebase-memory-mcp` — `gh api repos/DeusData/codebase-memory-mcp --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；Local code intelligence for developers and AI agents. Connect code, docs and infrastructure in a per ｜ ⚠️缓存→现测：47428/2026-10-24/MIT → 48225/2026-11-04T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=0
5. `shaom/brand-to-design-md-skill` — `gh api repos/shaom/brand-to-design-md-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=3/5；SKILL.md=1；A portable local skill that turns a public brand URL into a source-aware DESIGN.md, extracting visua ｜ ⚠️缓存→现测：209/2026-08-08/UNLICENSED → 211/2026-08-08T0…/NOASSERTION（stars,license 漂移） ｜ SKILL.md=1

### 7.34 `local-mineru` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：Intel Local Windows Document Parsing (本地离线文档与图片解析). Use this skill when the user, in Chinese or English, asks to parse, extract, OCR, or convert PDF documents or images to text or Markdown. Trigger on Chinese verbs like（desc_len=910；SKILL.md bytes=5755）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=6，trim=2） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [nexu-io/open-design](https://github.com/nexu-io/open-design) | 106289 | 12099 / 1371 | 2026-11-06T15:40:39Z | Apache-2.0 | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and o… |
| 2 | [openclaw/Peekaboo](https://github.com/openclaw/Peekaboo) | 5444 | 417 / 7 | 2026-11-05T23:37:09Z | MIT | 活跃(1d) | `active` | 21/25 (fc3 eff5 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents… |
| 3 | [SharpAI/DeepCamera](https://github.com/SharpAI/DeepCamera) | 3134 | 490 / 19 | 2026-09-17T00:43:07Z | MIT | 活跃(51d) | `active` | 19/25 (fc4 eff3 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=25；Open-Source AI Camera Skills Platform, AI NVR & CCTV Surveillance. … |
| 4 | [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) | 48225 | 3977 / 555 | 2026-11-04T23:21:44Z | MIT | 活跃(2d) | `active` | 17/25 (fc1 eff5 compat3 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；Local code intelligence for developers and AI agents. Connect code, … |
| 5 | [shaom/brand-to-design-md-skill](https://github.com/shaom/brand-to-design-md-skill) | 211 | 18 / 0 | 2026-08-08T03:26:40Z | NOASSERTION | 一般(91d) | `active` | 10/25 (fc2 eff0 compat3 docs3 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=3/5；SKILL.md=1；A portable local skill that turns a public brand URL into a source-a… |

**取值命令与匹配理由**
1. `nexu-io/open-design` — `gh api repos/nexu-io/open-design --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and open source. Create motion, prototy ｜ ⚠️缓存→现测：103811/2026-10-25/Apache-2.0 → 106289/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=553
2. `openclaw/Peekaboo` — `gh api repos/openclaw/Peekaboo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents to capture screenshots of appli ｜ ⚠️缓存→现测：5383/2026-10-24/MIT → 5444/2026-11-05T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=4
3. `SharpAI/DeepCamera` — `gh api repos/SharpAI/DeepCamera --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=25；Open-Source AI Camera Skills Platform, AI NVR & CCTV Surveillance. Local VLM video analysis with Qwe ｜ ⚠️缓存→现测：3110/2026-09-17/MIT → 3134/2026-09-17T0…/MIT（stars 漂移） ｜ SKILL.md=25
4. `DeusData/codebase-memory-mcp` — `gh api repos/DeusData/codebase-memory-mcp --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；Local code intelligence for developers and AI agents. Connect code, docs and infrastructure in a per ｜ ⚠️缓存→现测：47428/2026-10-24/MIT → 48225/2026-11-04T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=0
5. `shaom/brand-to-design-md-skill` — `gh api repos/shaom/brand-to-design-md-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=3/5；SKILL.md=1；A portable local skill that turns a public brand URL into a source-aware DESIGN.md, extracting visua ｜ ⚠️缓存→现测：209/2026-08-08/UNLICENSED → 211/2026-08-08T0…/NOASSERTION（stars,license 漂移） ｜ SKILL.md=1

### 7.35 `local-ocr-npu` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：Local NPU OCR (本地NPU文字识别). Use this skill when the user wants to extract, recognize, or read text from one or more local image files. Trigger on: - Chinese: 识别/提取/读取/扫描 + 图片/截图/照片/文字/内容, OCR, 文字识别, 文字提取 - English: OCR, e（desc_len=736；SKILL.md bytes=6319）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=9，trim=2） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [nexu-io/open-design](https://github.com/nexu-io/open-design) | 106289 | 12099 / 1371 | 2026-11-06T15:40:39Z | Apache-2.0 | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and o… |
| 2 | [openclaw/Peekaboo](https://github.com/openclaw/Peekaboo) | 5444 | 417 / 7 | 2026-11-05T23:37:09Z | MIT | 活跃(1d) | `active` | 21/25 (fc3 eff5 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents… |
| 3 | [SharpAI/DeepCamera](https://github.com/SharpAI/DeepCamera) | 3134 | 490 / 19 | 2026-09-17T00:43:07Z | MIT | 活跃(51d) | `active` | 19/25 (fc4 eff3 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=25；Open-Source AI Camera Skills Platform, AI NVR & CCTV Surveillance. … |
| 4 | [Anionex/agent-vision-toolkit](https://github.com/Anionex/agent-vision-toolkit) | 1260 | 50 / 8 | 2026-10-13T09:12:47Z | MIT | 活跃(25d) | `active` | 16/25 (fc2 eff3 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；为纯文本模型"看图“设计更好的视觉工具箱和技能，支持多图理解，图片问答，前端UI还原、GUI 自动化等，并可选无缝接入多个主流agent… |
| 5 | [liustack/modlens](https://github.com/liustack/modlens) | 4815 | 151 / 4 | 2026-10-23T15:42:48Z | MIT | 活跃(14d) | `active` | 15/25 (fc2 eff1 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；The first vision plugin for DeepSeek Harness, and the vision bridge … |

**取值命令与匹配理由**
1. `nexu-io/open-design` — `gh api repos/nexu-io/open-design --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and open source. Create motion, prototy ｜ ⚠️缓存→现测：103811/2026-10-25/Apache-2.0 → 106289/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=553
2. `openclaw/Peekaboo` — `gh api repos/openclaw/Peekaboo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents to capture screenshots of appli ｜ ⚠️缓存→现测：5383/2026-10-24/MIT → 5444/2026-11-05T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=4
3. `SharpAI/DeepCamera` — `gh api repos/SharpAI/DeepCamera --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=25；Open-Source AI Camera Skills Platform, AI NVR & CCTV Surveillance. Local VLM video analysis with Qwe ｜ ⚠️缓存→现测：3110/2026-09-17/MIT → 3134/2026-09-17T0…/MIT（stars 漂移） ｜ SKILL.md=25
4. `Anionex/agent-vision-toolkit` — `gh api repos/Anionex/agent-vision-toolkit --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；为纯文本模型"看图“设计更好的视觉工具箱和技能，支持多图理解，图片问答，前端UI还原、GUI 自动化等，并可选无缝接入多个主流agent，直接识别粘贴图片｜ A vision toolkit and ｜ ⚠️缓存→现测：1249/2026-10-13/MIT → 1260/2026-10-13T0…/MIT（stars 漂移） ｜ SKILL.md=1
5. `liustack/modlens` — `gh api repos/liustack/modlens --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；The first vision plugin for DeepSeek Harness, and the vision bridge for every text-only coding agent ｜ ⚠️缓存→现测：4446/2026-10-23/MIT → 4815/2026-10-23T1…/MIT（stars 漂移） ｜ SKILL.md=1

### 7.36 `local-realtime-translator` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：Intel Local Windows Realtime Speech Translator (本地实时语音翻译 / 同声传译). Use when the user wants to translate live speech from the microphone in real time (simultaneous interpretation, "translate as I speak"), or asks to open/s（desc_len=971；SKILL.md bytes=8241）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [nexu-io/open-design](https://github.com/nexu-io/open-design) | 106289 | 12099 / 1371 | 2026-11-06T15:40:39Z | Apache-2.0 | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and o… |
| 2 | [sickn33/agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills) | 49276 | 7151 / 7 | 2026-11-06T17:55:43Z | MIT | 活跃(0d) | `active` | 24/25 (fc5 eff5 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=8851；2,877+ reusable AI agent skills for Claude Code, Codex, Cursor an… |
| 3 | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | 143437 | 13720 / 1641 | 2026-11-06T17:11:19Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc2 eff5 compat5 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Turn any codebase, with its docs, SQL schemas, configs, and PDFs, in… |
| 4 | [tirth8205/code-review-graph](https://github.com/tirth8205/code-review-graph) | 32624 | 2967 / 111 | 2026-11-06T19:05:44Z | MIT | 活跃(0d) | `active` | 21/25 (fc3 eff5 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Local-first code intelligence graph for MCP and CLI. Builds a persis… |
| 5 | [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) | 27026 | 3508 / 89 | 2026-11-01T06:07:26Z | MIT | 活跃(6d) | `active` | 20/25 (fc4 eff3 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=35；Universal SEO skill for Claude Code. 26 sub-skills + 19 sub-agents … |

**取值命令与匹配理由**
1. `nexu-io/open-design` — `gh api repos/nexu-io/open-design --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and open source. Create motion, prototy ｜ ⚠️缓存→现测：103811/2026-10-25/Apache-2.0 → 106289/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=553
2. `sickn33/agentic-awesome-skills` — `gh api repos/sickn33/agentic-awesome-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=8851；2,877+ reusable AI agent skills for Claude Code, Codex, Cursor and Gemini CLI. AAS Core adds local c ｜ ⚠️缓存→现测：48801/2026-10-29/MIT → 49276/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=8851
3. `Graphify-Labs/graphify` — `gh api repos/Graphify-Labs/graphify --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Turn any codebase, with its docs, SQL schemas, configs, and PDFs, into a queryable knowledge graph. ｜ ⚠️缓存→现测：134586/2026-10-23/Apache-2.0 → 143437/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=2
4. `tirth8205/code-review-graph` — `gh api repos/tirth8205/code-review-graph --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Local-first code intelligence graph for MCP and CLI. Builds a persistent map of your codebase so AI ｜ ⚠️缓存→现测：32379/2026-10-16/MIT → 32624/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=7
5. `AgriciDaniel/claude-seo` — `gh api repos/AgriciDaniel/claude-seo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=35；Universal SEO skill for Claude Code. 26 sub-skills + 19 sub-agents covering technical SEO, E-E-A-T, ｜ ⚠️缓存→现测：20126/2026-10-22/MIT → 27026/2026-11-01T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=35

### 7.37 `local-screenshot-qa` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：Intel Local Windows Screenshot Q&A (本地离线截图问答). Use this skill when the user, in Chinese or English, asks to read, describe, or answer questions about a screenshot, screen capture, or image. Trigger on Chinese verbs like（desc_len=1017；SKILL.md bytes=5775）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=10，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [maziyarpanahi/openmed](https://github.com/maziyarpanahi/openmed) | 5784 | 733 / 442 | 2026-11-06T19:06:26Z | Apache-2.0 | 活跃(0d) | `active` | 22/25 (fc4 eff5 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=74；Local-first healthcare AI: clinical NER and HIPAA PII de-identifica… |
| 2 | [openclaw/Peekaboo](https://github.com/openclaw/Peekaboo) | 5444 | 417 / 7 | 2026-11-05T23:37:09Z | MIT | 活跃(1d) | `active` | 21/25 (fc3 eff5 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents… |
| 3 | [siddsachar/row-bot](https://github.com/siddsachar/row-bot) | 1683 | 204 / 36 | 2026-11-06T18:36:12Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc4 eff5 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=50；Row-Bot - Personal AI Sovereignty. A local-first AI assistant with … |
| 4 | [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) | 27026 | 3508 / 89 | 2026-11-01T06:07:26Z | MIT | 活跃(6d) | `active` | 20/25 (fc4 eff3 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=35；Universal SEO skill for Claude Code. 26 sub-skills + 19 sub-agents … |
| 5 | [NanmiCoder/cc-haha](https://github.com/NanmiCoder/cc-haha) | 15338 | 8612 / 205 | 2026-11-05T15:03:01Z | NOASSERTION | 活跃(1d) | `active` | 18/25 (fc3 eff5 compat1 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=4；本地优先的跨平台 Claude Code / AI Agent 桌面工作台：多 Agent 协作、Git Worktree、代码 Dif… |

**取值命令与匹配理由**
1. `maziyarpanahi/openmed` — `gh api repos/maziyarpanahi/openmed --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=74；Local-first healthcare AI: clinical NER and HIPAA PII de-identification on hardware you control. 2,2 ｜ ⚠️缓存→现测：5707/2026-10-25/Apache-2.0 → 5784/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=74
2. `openclaw/Peekaboo` — `gh api repos/openclaw/Peekaboo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents to capture screenshots of appli ｜ ⚠️缓存→现测：5383/2026-10-24/MIT → 5444/2026-11-05T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=4
3. `siddsachar/row-bot` — `gh api repos/siddsachar/row-bot --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=50；Row-Bot - Personal AI Sovereignty. A local-first AI assistant with integrated tools, a personal know ｜ ⚠️缓存→现测：1646/2026-10-24/Apache-2.0 → 1683/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=50
4. `AgriciDaniel/claude-seo` — `gh api repos/AgriciDaniel/claude-seo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=35；Universal SEO skill for Claude Code. 26 sub-skills + 19 sub-agents covering technical SEO, E-E-A-T, ｜ ⚠️缓存→现测：20126/2026-10-22/MIT → 27026/2026-11-01T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=35
5. `NanmiCoder/cc-haha` — `gh api repos/NanmiCoder/cc-haha --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=4；本地优先的跨平台 Claude Code / AI Agent 桌面工作台：多 Agent 协作、Git Worktree、代码 Diff、技能市场、多模型、Computer Use、桌面宠物；支持微 ｜ ⚠️缓存→现测：15156/2026-10-23/NOASSERTION → 15338/2026-11-05T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=4

### 7.38 `local-tts` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：Intel Local Text-to-Speech (本地文字转语音) on Windows AI PCs. Use this skill when the user, in Chinese or English, asks to synthesize / speak / read aloud / clone a voice / generate audio from text. Trigger on Chinese verbs li（desc_len=692；SKILL.md bytes=6569）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=7，trim=2） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [nexu-io/open-design](https://github.com/nexu-io/open-design) | 106289 | 12099 / 1371 | 2026-11-06T15:40:39Z | Apache-2.0 | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and o… |
| 2 | [krillinai/OpenCreator](https://github.com/krillinai/OpenCreator) | 14189 | 1583 / 43 | 2026-11-05T23:26:51Z | Apache-2.0 | 活跃(1d) | `active` | 22/25 (fc4 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=15；Formerly KrillinAI, VideoTranslation and Dubbing Tool. Open-source … |
| 3 | [openclaw/Peekaboo](https://github.com/openclaw/Peekaboo) | 5444 | 417 / 7 | 2026-11-05T23:37:09Z | MIT | 活跃(1d) | `active` | 21/25 (fc3 eff5 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents… |
| 4 | [SharpAI/DeepCamera](https://github.com/SharpAI/DeepCamera) | 3134 | 490 / 19 | 2026-09-17T00:43:07Z | MIT | 活跃(51d) | `active` | 19/25 (fc4 eff3 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=25；Open-Source AI Camera Skills Platform, AI NVR & CCTV Surveillance. … |
| 5 | [equalang/equalang-skill](https://github.com/equalang/equalang-skill) | 78 | 0 / 0 | 2026-11-03T07:35:58Z | Apache-2.0 | 活跃(4d) | `active` | 12/25 (fc2 eff1 compat5 docs3 comm1) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent Skill for Equalang: translate PDF, DOCX, PPTX, XLSX, EPUB, sub… |

**取值命令与匹配理由**
1. `nexu-io/open-design` — `gh api repos/nexu-io/open-design --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and open source. Create motion, prototy ｜ ⚠️缓存→现测：103811/2026-10-25/Apache-2.0 → 106289/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=553
2. `krillinai/OpenCreator` — `gh api repos/krillinai/OpenCreator --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=15；Formerly KrillinAI, VideoTranslation and Dubbing Tool. Open-source AI workspace for creators, powere ｜ ⚠️缓存→现测：13918/2026-10-25/Apache-2.0 → 14189/2026-11-05T2…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=15
3. `openclaw/Peekaboo` — `gh api repos/openclaw/Peekaboo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents to capture screenshots of appli ｜ ⚠️缓存→现测：5383/2026-10-24/MIT → 5444/2026-11-05T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=4
4. `SharpAI/DeepCamera` — `gh api repos/SharpAI/DeepCamera --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=25；Open-Source AI Camera Skills Platform, AI NVR & CCTV Surveillance. Local VLM video analysis with Qwe ｜ ⚠️缓存→现测：3110/2026-09-17/MIT → 3134/2026-09-17T0…/MIT（stars 漂移） ｜ SKILL.md=25
5. `equalang/equalang-skill` — `gh api repos/equalang/equalang-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent Skill for Equalang: translate PDF, DOCX, PPTX, XLSX, EPUB, subtitles, pictures, audio and vide ｜ ⚠️缓存→现测：39/2026-10-12/Apache-2.0 → 78/2026-11-03T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.39 `local-txt2img` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：Intel Local Text-to-Image (本地文字转图片). Use this skill when the user, in Chinese or English, asks to generate/create/draw/paint/make an image or picture from a text prompt. Trigger on Chinese verbs like 生成/画/绘制/出图/文生图 or En（desc_len=491；SKILL.md bytes=5268）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=5，trim=2） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [nexu-io/open-design](https://github.com/nexu-io/open-design) | 106289 | 12099 / 1371 | 2026-11-06T15:40:39Z | Apache-2.0 | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and o… |
| 2 | [openclaw/Peekaboo](https://github.com/openclaw/Peekaboo) | 5444 | 417 / 7 | 2026-11-05T23:37:09Z | MIT | 活跃(1d) | `active` | 21/25 (fc3 eff5 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents… |
| 3 | [SharpAI/DeepCamera](https://github.com/SharpAI/DeepCamera) | 3134 | 490 / 19 | 2026-09-17T00:43:07Z | MIT | 活跃(51d) | `active` | 19/25 (fc4 eff3 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=25；Open-Source AI Camera Skills Platform, AI NVR & CCTV Surveillance. … |
| 4 | [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) | 48225 | 3977 / 555 | 2026-11-04T23:21:44Z | MIT | 活跃(2d) | `active` | 17/25 (fc1 eff5 compat3 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；Local code intelligence for developers and AI agents. Connect code, … |
| 5 | [shaom/brand-to-design-md-skill](https://github.com/shaom/brand-to-design-md-skill) | 211 | 18 / 0 | 2026-08-08T03:26:40Z | NOASSERTION | 一般(91d) | `active` | 10/25 (fc2 eff0 compat3 docs3 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=3/5；SKILL.md=1；A portable local skill that turns a public brand URL into a source-a… |

**取值命令与匹配理由**
1. `nexu-io/open-design` — `gh api repos/nexu-io/open-design --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and open source. Create motion, prototy ｜ ⚠️缓存→现测：103811/2026-10-25/Apache-2.0 → 106289/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=553
2. `openclaw/Peekaboo` — `gh api repos/openclaw/Peekaboo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents to capture screenshots of appli ｜ ⚠️缓存→现测：5383/2026-10-24/MIT → 5444/2026-11-05T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=4
3. `SharpAI/DeepCamera` — `gh api repos/SharpAI/DeepCamera --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=25；Open-Source AI Camera Skills Platform, AI NVR & CCTV Surveillance. Local VLM video analysis with Qwe ｜ ⚠️缓存→现测：3110/2026-09-17/MIT → 3134/2026-09-17T0…/MIT（stars 漂移） ｜ SKILL.md=25
4. `DeusData/codebase-memory-mcp` — `gh api repos/DeusData/codebase-memory-mcp --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；Local code intelligence for developers and AI agents. Connect code, docs and infrastructure in a per ｜ ⚠️缓存→现测：47428/2026-10-24/MIT → 48225/2026-11-04T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=0
5. `shaom/brand-to-design-md-skill` — `gh api repos/shaom/brand-to-design-md-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=3/5；SKILL.md=1；A portable local skill that turns a public brand URL into a source-aware DESIGN.md, extracting visua ｜ ⚠️缓存→现测：209/2026-08-08/UNLICENSED → 211/2026-08-08T0…/NOASSERTION（stars,license 漂移） ｜ SKILL.md=1

### 7.40 `local-vram` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：Intel Local GPU Memory Limit / VRAM Adjust (集成显卡显存调整) on Windows AI PCs. Use this skill when the user, in Chinese or English, asks to limit, adjust, increase, change, or query the GPU shared memory limit. Trigger on Chin（desc_len=812；SKILL.md bytes=5691）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [nexu-io/open-design](https://github.com/nexu-io/open-design) | 106289 | 12099 / 1371 | 2026-11-06T15:40:39Z | Apache-2.0 | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and o… |
| 2 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 81071 | 9543 / 654 | 2026-11-06T18:31:29Z | MIT | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swa… |
| 3 | [xerj-org/xerj](https://github.com/xerj-org/xerj) | 18466 | 1352 / 140 | 2026-11-06T18:27:54Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc2 eff5 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Local-first search engine and MCP server for AI agents. One Rust bin… |
| 4 | [EverMind-AI/EverOS](https://github.com/EverMind-AI/EverOS) | 13840 | 963 / 43 | 2026-11-06T08:46:28Z | Apache-2.0 | 活跃(1d) | `active` | 21/25 (fc3 eff5 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=5；One portable memory layer for every AI agent: local-first, Markdown-… |
| 5 | [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) | 30573 | 2983 / 887 | 2026-11-04T11:33:40Z | NOASSERTION | 活跃(3d) | `active` | 16/25 (fc2 eff2 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；TencentDB Agent Memory is a team-level memory hub for AI Agents — tu… |

**取值命令与匹配理由**
1. `nexu-io/open-design` — `gh api repos/nexu-io/open-design --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and open source. Create motion, prototy ｜ ⚠️缓存→现测：103811/2026-10-25/Apache-2.0 → 106289/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=553
2. `ruvnet/ruflo` — `gh api repos/ruvnet/ruflo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swarms, coordinate autonomous workflo ｜ ⚠️缓存→现测：79103/2026-10-25/MIT → 81071/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=389
3. `xerj-org/xerj` — `gh api repos/xerj-org/xerj --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Local-first search engine and MCP server for AI agents. One Rust binary indexes code, docs, logs, JS ｜ ⚠️缓存→现测：15376/2026-10-25/Apache-2.0 → 18466/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=2
4. `EverMind-AI/EverOS` — `gh api repos/EverMind-AI/EverOS --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=5；One portable memory layer for every AI agent: local-first, Markdown-native, user-owned, and self-evo ｜ ⚠️缓存→现测：13597/2026-10-22/Apache-2.0 → 13840/2026-11-06T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=5
5. `TencentCloud/TencentDB-Agent-Memory` — `gh api repos/TencentCloud/TencentDB-Agent-Memory --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；TencentDB Agent Memory is a team-level memory hub for AI Agents — turning conversations, docs, and c ｜ ⚠️缓存→现测：29900/2026-10-21/NOASSERTION → 30573/2026-11-04T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=2

### 7.41 `oc-dispatch-exec-guard` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：OpenClaw CLI 派发任务执行护栏 — 防止被派发方秒停零产出。含触发场景、已发生三次的症状与根因、派发前必做检查、标准派发模板与 CC 独立评分提示词。Use when 向 openclaw/CLI 派活、或派发后无产出/立即退出。不适用：任务完成后的经验反哺（走 A-get-memory）。（desc_len=152；SKILL.md bytes=5323）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 298441 | 44116 / 236 | 2026-11-06T05:29:44Z | MIT | 活跃(1d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instin… |
| 2 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 81071 | 9543 / 654 | 2026-11-06T18:31:29Z | MIT | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swa… |
| 3 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 113914 | 9885 / 125 | 2026-11-06T18:15:53Z | Apache-2.0 | 活跃(0d) | `active` | 24/25 (fc4 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Persistent Context Across Sessions for Every Agent –  Captures ever… |
| 4 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | 117973 | 6860 / 69 | 2026-11-06T11:35:30Z | Apache-2.0 | 活跃(1d) | `active` | 23/25 (fc4 eff5 compat5 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=28；🪨 why use many token when few token do trick. Viral skill + proxy … |
| 5 | [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 66836 | 5859 / 17 | 2026-11-05T21:24:10Z | MIT | 活跃(1d) | `active` | 21/25 (fc2 eff5 compat5 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；AI agent skill that researches any topic across Reddit, X, YouTube, … |

**取值命令与匹配理由**
1. `affaan-m/ECC` — `gh api repos/affaan-m/ECC --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instincts, memory, security, and research ｜ ⚠️缓存→现测：288271/2026-10-20/MIT → 298441/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1062
2. `ruvnet/ruflo` — `gh api repos/ruvnet/ruflo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swarms, coordinate autonomous workflo ｜ ⚠️缓存→现测：79103/2026-10-25/MIT → 81071/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=389
3. `thedotmack/claude-mem` — `gh api repos/thedotmack/claude-mem --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Persistent Context Across Sessions for Every Agent –  Captures everything your agent does during ses ｜ ⚠️缓存→现测：102894/2026-10-25/Apache-2.0 → 113914/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=43
4. `JuliusBrussee/caveman` — `gh api repos/JuliusBrussee/caveman --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=28；🪨 why use many token when few token do trick. Viral skill + proxy for coding agents that cuts 65% o ｜ ⚠️缓存→现测：114863/2026-10-25/Apache-2.0 → 117973/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=28
5. `mvanhorn/last30days-skill` — `gh api repos/mvanhorn/last30days-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；AI agent skill that researches any topic across Reddit, X, YouTube, HN, Polymarket, and the web - th ｜ ⚠️缓存→现测：65357/2026-10-23/MIT → 66836/2026-11-05T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.42 `office-automation-pro` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：办公自动化专家 — 编写自动发邮件脚本、定时群发、邮件合并、报表自动推送、Excel/Word 批量处理。当用户说"自动发邮件的脚本""定时发送邮件""邮件合并""自动生成报表并发送""办公自动化脚本""批量发邮件""用脚本发通知"时触发。支持 Python（smtplib/email/openpyxl/docx）与 PowerShell 两种实现，含 SMTP 配置、附件、HTML 邮件、计划任务（cron / Windows Tas（desc_len=237；SKILL.md bytes=4575）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=10，trim=2） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [yusufkaraaslan/Skill_Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) | 15288 | 1554 / 55 | 2026-09-30T18:49:17Z | MIT | 活跃(37d) | `active` | 23/25 (fc4 eff5 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=31；Convert documentation websites, GitHub repositories, and PDFs into … |
| 2 | [genspark-ai/genoffice](https://github.com/genspark-ai/genoffice) | 11848 | 1640 / 59 | 2026-11-06T12:26:32Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc4 eff4 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Free, open-source AI Office suite: Docs, Sheets, Slides, PDF, Markd… |
| 3 | [OpenSenseNova/SenseNova-Skills](https://github.com/OpenSenseNova/SenseNova-Skills) | 6035 | 436 / 21 | 2026-11-03T07:27:54Z | MIT | 活跃(4d) | `active` | 18/25 (fc4 eff2 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=83；Modular SenseNova skills for building AI-powered office assistants … |
| 4 | [iOfficeAI/OfficeCLI](https://github.com/iOfficeAI/OfficeCLI) | 33095 | 2259 / 142 | 2026-10-30T06:48:51Z | Apache-2.0 | 活跃(8d) | `active` | 18/25 (fc4 eff2 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；OfficeCLI is the first and best Office suite  purpose-built for AI … |
| 5 | [tfriedel/claude-office-skills](https://github.com/tfriedel/claude-office-skills) | 848 | 120 / 3 | 2026-04-01T11:49:29Z | NOASSERTION | 一般(220d) | `active` | 10/25 (fc3 eff0 compat3 docs3 comm1) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=3/5；SKILL.md=4；Office document creation and editing skills for Claude Code - PPTX, … |

**取值命令与匹配理由**
1. `yusufkaraaslan/Skill_Seekers` — `gh api repos/yusufkaraaslan/Skill_Seekers --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=31；Convert documentation websites, GitHub repositories, and PDFs into Claude AI skills with automatic c ｜ ⚠️缓存→现测：15217/2026-09-30/MIT → 15288/2026-09-30T1…/MIT（stars 漂移） ｜ SKILL.md=31
2. `genspark-ai/genoffice` — `gh api repos/genspark-ai/genoffice --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Free, open-source AI Office suite: Docs, Sheets, Slides, PDF, Markdown and HTML editors with a built ｜ ⚠️缓存→现测：10764/2026-10-24/Apache-2.0 → 11848/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=43
3. `OpenSenseNova/SenseNova-Skills` — `gh api repos/OpenSenseNova/SenseNova-Skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=83；Modular SenseNova skills for building AI-powered office assistants and productivity workflows ｜ ⚠️缓存→现测：5904/2026-10-09/MIT → 6035/2026-11-03T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=83
4. `iOfficeAI/OfficeCLI` — `gh api repos/iOfficeAI/OfficeCLI --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；OfficeCLI is the first and best Office suite  purpose-built for AI agents to read, edit, and automat ｜ ⚠️缓存→现测：32411/2026-10-23/Apache-2.0 → 33095/2026-10-30T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=12
5. `tfriedel/claude-office-skills` — `gh api repos/tfriedel/claude-office-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=3/5；SKILL.md=4；Office document creation and editing skills for Claude Code - PPTX, DOCX, XLSX, and PDF workflows wi ｜ ⚠️缓存→现测：841/2026-04-01/UNLICENSED → 848/2026-04-01T1…/NOASSERTION（stars,license 漂移） ｜ SKILL.md=4

### 7.43 `openclaw-dual-gate-quality-audit` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：OpenClaw双门禁质量审计 — 让 openclaw 先自评，再由 Codex 独立逐文件审计验证，发现虚高后要求修复并实测重评，直到双门禁均 ≥85 分或确认已最优（最多 5 轮）。**仅适用于「审计某个交付物或系统的质量评分」场景**（见下方「何时不用本 skill」）；不做任务进度监督（改投 openclaw-task-supervision）、不做周度维护（改投 openclaw-fenjue-weekly）。触发词：双门禁（desc_len=268；SKILL.md bytes=21587）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 113914 | 9885 / 125 | 2026-11-06T18:15:53Z | Apache-2.0 | 活跃(0d) | `active` | 24/25 (fc4 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Persistent Context Across Sessions for Every Agent –  Captures ever… |
| 2 | [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | 18796 | 1527 / 75 | 2026-11-06T04:09:40Z | MIT | 活跃(1d) | `active` | 23/25 (fc5 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=197；ARIS ⚔️ (Auto-Research-In-Sleep) — Lightweight Markdown-only skill… |
| 3 | [iOfficeAI/AionUi](https://github.com/iOfficeAI/AionUi) | 34072 | 3560 / 886 | 2026-11-05T05:31:20Z | Apache-2.0 | 活跃(2d) | `active` | 22/25 (fc3 eff5 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；Open-source 24/7 Cowork app for OpenClaw, Hermes, Claude Code, Codex… |
| 4 | [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 66836 | 5859 / 17 | 2026-11-05T21:24:10Z | MIT | 活跃(1d) | `active` | 21/25 (fc2 eff5 compat5 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；AI agent skill that researches any topic across Reddit, X, YouTube, … |
| 5 | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 63535 | 4118 / 115 | 2026-09-14T19:29:02Z | MIT | 活跃(53d) | `active` | 15/25 (fc2 eff0 compat5 docs3 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A coding-agent skill for multi-phase security audits with independen… |

**取值命令与匹配理由**
1. `thedotmack/claude-mem` — `gh api repos/thedotmack/claude-mem --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Persistent Context Across Sessions for Every Agent –  Captures everything your agent does during ses ｜ ⚠️缓存→现测：102894/2026-10-25/Apache-2.0 → 113914/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=43
2. `wanshuiyin/Auto-claude-code-research-in-sleep` — `gh api repos/wanshuiyin/Auto-claude-code-research-in-sleep --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=197；ARIS ⚔️ (Auto-Research-In-Sleep) — Lightweight Markdown-only skills for autonomous ML research: cros ｜ ⚠️缓存→现测：18023/2026-10-24/MIT → 18796/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=197
3. `iOfficeAI/AionUi` — `gh api repos/iOfficeAI/AionUi --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；Open-source 24/7 Cowork app for OpenClaw, Hermes, Claude Code, Codex, OpenCode and 20+ more CLI Agen ｜ ⚠️缓存→现测：33752/2026-10-23/Apache-2.0 → 34072/2026-11-05T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=6
4. `mvanhorn/last30days-skill` — `gh api repos/mvanhorn/last30days-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；AI agent skill that researches any topic across Reddit, X, YouTube, HN, Polymarket, and the web - th ｜ ⚠️缓存→现测：65357/2026-10-23/MIT → 66836/2026-11-05T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1
5. `cloudflare/security-audit-skill` — `gh api repos/cloudflare/security-audit-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A coding-agent skill for multi-phase security audits with independently verified, machine-readable f ｜ ⚠️缓存→现测：53489/2026-09-14/MIT → 63535/2026-09-14T1…/MIT（stars 漂移） ｜ SKILL.md=1

### 7.44 `openclaw-fenjue-weekly` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：每周控制 OpenClaw 执行焚诀三项维护（skill 审计 / 树评分 / 记忆优化）。含唯一权威源指针、本 skill 的附加价值、OC CLI 命令速查、Session 分段策略、Phase 0 子 skill 加载与错误处理速查。Use when 到周维护节点或要重跑焚诀周任务。不适用：单任务派发监督（走 openclaw-task-supervision）。（desc_len=186；SKILL.md bytes=4916）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 113914 | 9885 / 125 | 2026-11-06T18:15:53Z | Apache-2.0 | 活跃(0d) | `active` | 24/25 (fc4 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Persistent Context Across Sessions for Every Agent –  Captures ever… |
| 2 | [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | 18796 | 1527 / 75 | 2026-11-06T04:09:40Z | MIT | 活跃(1d) | `active` | 23/25 (fc5 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=197；ARIS ⚔️ (Auto-Research-In-Sleep) — Lightweight Markdown-only skill… |
| 3 | [iOfficeAI/AionUi](https://github.com/iOfficeAI/AionUi) | 34072 | 3560 / 886 | 2026-11-05T05:31:20Z | Apache-2.0 | 活跃(2d) | `active` | 22/25 (fc3 eff5 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；Open-source 24/7 Cowork app for OpenClaw, Hermes, Claude Code, Codex… |
| 4 | [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 66836 | 5859 / 17 | 2026-11-05T21:24:10Z | MIT | 活跃(1d) | `active` | 21/25 (fc2 eff5 compat5 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；AI agent skill that researches any topic across Reddit, X, YouTube, … |
| 5 | [nanocoai/nanoclaw](https://github.com/nanocoai/nanoclaw) | 31085 | 12673 / 1044 | 2026-11-06T18:27:57Z | MIT | 活跃(0d) | `active` | 20/25 (fc4 eff3 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=64；A lightweight alternative to OpenClaw that runs in containers for s… |

**取值命令与匹配理由**
1. `thedotmack/claude-mem` — `gh api repos/thedotmack/claude-mem --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Persistent Context Across Sessions for Every Agent –  Captures everything your agent does during ses ｜ ⚠️缓存→现测：102894/2026-10-25/Apache-2.0 → 113914/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=43
2. `wanshuiyin/Auto-claude-code-research-in-sleep` — `gh api repos/wanshuiyin/Auto-claude-code-research-in-sleep --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=197；ARIS ⚔️ (Auto-Research-In-Sleep) — Lightweight Markdown-only skills for autonomous ML research: cros ｜ ⚠️缓存→现测：18023/2026-10-24/MIT → 18796/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=197
3. `iOfficeAI/AionUi` — `gh api repos/iOfficeAI/AionUi --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；Open-source 24/7 Cowork app for OpenClaw, Hermes, Claude Code, Codex, OpenCode and 20+ more CLI Agen ｜ ⚠️缓存→现测：33752/2026-10-23/Apache-2.0 → 34072/2026-11-05T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=6
4. `mvanhorn/last30days-skill` — `gh api repos/mvanhorn/last30days-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；AI agent skill that researches any topic across Reddit, X, YouTube, HN, Polymarket, and the web - th ｜ ⚠️缓存→现测：65357/2026-10-23/MIT → 66836/2026-11-05T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1
5. `nanocoai/nanoclaw` — `gh api repos/nanocoai/nanoclaw --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=64；A lightweight alternative to OpenClaw that runs in containers for security. Connects to WhatsApp, Te ｜ ⚠️缓存→现测：31009/2026-10-24/MIT → 31085/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=64

### 7.45 `openclaw-task-supervision` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：以 Codex 为监工控制 OpenClaw 执行任务：发送消息或桌面 prompt 文件、审报告、代表用户批准操作、纠错并强制质量门禁，含重试与结果验证。附角色定义、前置条件、流程总览与 CLI 命令参考。Use when 需要把任务派给 openclaw 并盯到验收。不适用：焚诀周度维护（走 openclaw-fenjue-weekly）。（desc_len=173；SKILL.md bytes=34136）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 113914 | 9885 / 125 | 2026-11-06T18:15:53Z | Apache-2.0 | 活跃(0d) | `active` | 24/25 (fc4 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Persistent Context Across Sessions for Every Agent –  Captures ever… |
| 2 | [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | 18796 | 1527 / 75 | 2026-11-06T04:09:40Z | MIT | 活跃(1d) | `active` | 23/25 (fc5 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=197；ARIS ⚔️ (Auto-Research-In-Sleep) — Lightweight Markdown-only skill… |
| 3 | [iOfficeAI/AionUi](https://github.com/iOfficeAI/AionUi) | 34072 | 3560 / 886 | 2026-11-05T05:31:20Z | Apache-2.0 | 活跃(2d) | `active` | 22/25 (fc3 eff5 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；Open-source 24/7 Cowork app for OpenClaw, Hermes, Claude Code, Codex… |
| 4 | [OrchestratorInc/agent-orchestrator](https://github.com/OrchestratorInc/agent-orchestrator) | 14176 | 1934 / 906 | 2026-11-06T18:26:55Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc3 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Open-source (Apache-2.0) orchestrator for Claude Code, Codex & 30+ c… |
| 5 | [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 66836 | 5859 / 17 | 2026-11-05T21:24:10Z | MIT | 活跃(1d) | `active` | 21/25 (fc2 eff5 compat5 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；AI agent skill that researches any topic across Reddit, X, YouTube, … |

**取值命令与匹配理由**
1. `thedotmack/claude-mem` — `gh api repos/thedotmack/claude-mem --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Persistent Context Across Sessions for Every Agent –  Captures everything your agent does during ses ｜ ⚠️缓存→现测：102894/2026-10-25/Apache-2.0 → 113914/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=43
2. `wanshuiyin/Auto-claude-code-research-in-sleep` — `gh api repos/wanshuiyin/Auto-claude-code-research-in-sleep --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=197；ARIS ⚔️ (Auto-Research-In-Sleep) — Lightweight Markdown-only skills for autonomous ML research: cros ｜ ⚠️缓存→现测：18023/2026-10-24/MIT → 18796/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=197
3. `iOfficeAI/AionUi` — `gh api repos/iOfficeAI/AionUi --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；Open-source 24/7 Cowork app for OpenClaw, Hermes, Claude Code, Codex, OpenCode and 20+ more CLI Agen ｜ ⚠️缓存→现测：33752/2026-10-23/Apache-2.0 → 34072/2026-11-05T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=6
4. `OrchestratorInc/agent-orchestrator` — `gh api repos/OrchestratorInc/agent-orchestrator --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Open-source (Apache-2.0) orchestrator for Claude Code, Codex & 30+ coding agents. Plan, run and supe ｜ ⚠️缓存→现测：13596/2026-10-25/Apache-2.0 → 14176/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=7
5. `mvanhorn/last30days-skill` — `gh api repos/mvanhorn/last30days-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；AI agent skill that researches any topic across Reddit, X, YouTube, HN, Polymarket, and the web - th ｜ ⚠️缓存→现测：65357/2026-10-23/MIT → 66836/2026-11-05T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.46 `prompt-consolidation` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：清理多agent提示词中的append-only补丁 — 输出结构化合并版。提示词补丁清理合并 清理多agent提示词文件中的append-only补丁层，输出按功能分章节的干净版本， 并内建V1-V7漏洞验证确保清理不引入新漏洞。 适用于经过多轮迭代后变得臃肿、充满补丁标记的提示词文件。 只做单文件清理，严禁跨文件合并（合并会引入新的V1-V7漏洞）。 触发词：提示词整合、提示词清理、prompt consolidation、清理补丁（desc_len=303；SKILL.md bytes=16145）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=10，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [zenstory-ai/drama-skills](https://github.com/zenstory-ai/drama-skills) | 3869 | 694 / 3 | 2026-11-06T17:39:19Z | MIT | 活跃(0d) | `active` | 20/25 (fc4 eff4 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；开源 AI 短剧/漫剧创作 skill 合集：剧本、角色资产、分镜 storyboard、图片/视频提示词、审查，适配 Claude … |
| 2 | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | 55635 | 4230 / 40 | 2026-11-06T08:36:34Z | NOASSERTION | 活跃(1d) | `active` | 19/25 (fc3 eff5 compat1 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=5；Academic Research Skills for Claude Code: research → write → review … |
| 3 | [blader/humanizer](https://github.com/blader/humanizer) | 65579 | 5185 / 16 | 2026-10-28T07:17:33Z | MIT | 活跃(10d) | `active` | 16/25 (fc2 eff1 compat5 docs3 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent skill that removes signs of AI-generated writing from text |
| 4 | [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) | 5459 | 474 / 17 | 2026-11-05T08:27:07Z | MIT | 活跃(2d) | `active` | 16/25 (fc3 eff2 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=9；Skill that audits and rewrites content to remove AI writing patterns… |
| 5 | [Nanako0129/sepia](https://github.com/Nanako0129/sepia) | 3662 | 228 / 6 | 2026-11-03T05:53:57Z | MIT | 活跃(4d) | `active` | 16/25 (fc3 eff2 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；De-AI writing skill for any Agent Skills-compatible agent (77+ via t… |

**取值命令与匹配理由**
1. `zenstory-ai/drama-skills` — `gh api repos/zenstory-ai/drama-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；开源 AI 短剧/漫剧创作 skill 合集：剧本、角色资产、分镜 storyboard、图片/视频提示词、审查，适配 Claude Code 与 Codex &#124; Open-source AI sho ｜ ⚠️缓存→现测：3326/2026-10-20/MIT → 3869/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=12
2. `Imbad0202/academic-research-skills` — `gh api repos/Imbad0202/academic-research-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=5；Academic Research Skills for Claude Code: research → write → review → revise → finalize ｜ ⚠️缓存→现测：54267/2026-10-28/NOASSERTION → 55635/2026-11-06T0…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=5
3. `blader/humanizer` — `gh api repos/blader/humanizer --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent skill that removes signs of AI-generated writing from text ｜ ⚠️缓存→现测：60349/2026-10-16/MIT → 65579/2026-10-28T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1
4. `conorbronsdon/avoid-ai-writing` — `gh api repos/conorbronsdon/avoid-ai-writing --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=9；Skill that audits and rewrites content to remove AI writing patterns. Use it with your favorite agen ｜ ⚠️缓存→现测：5229/2026-10-20/MIT → 5459/2026-11-05T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=9
5. `Nanako0129/sepia` — `gh api repos/Nanako0129/sepia --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；De-AI writing skill for any Agent Skills-compatible agent (77+ via the Skills CLI), with native plug ｜ ⚠️缓存→现测：3463/2026-10-15/MIT → 3662/2026-11-03T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=6

### 7.47 `prompt-system-audit` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：多agent提示词系统逻辑一致性审计 + 数据层验证。提示词系统审计。适用：提示词/规则体系改动后需要做逻辑一致性与数据层漂移审计时使用；触发词：提示词审计、一致性审计、prompt-system-audit、规则体检（desc_len=109；SKILL.md bytes=33023）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [Ar9av/obsidian-wiki](https://github.com/Ar9av/obsidian-wiki) | 3693 | 371 / 7 | 2026-11-05T09:28:11Z | MIT | 活跃(2d) | `active` | 20/25 (fc4 eff4 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=40；Framework for AI agents to build and maintain a digital brain throu… |
| 2 | [zenstory-ai/drama-skills](https://github.com/zenstory-ai/drama-skills) | 3869 | 694 / 3 | 2026-11-06T17:39:19Z | MIT | 活跃(0d) | `active` | 20/25 (fc4 eff4 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；开源 AI 短剧/漫剧创作 skill 合集：剧本、角色资产、分镜 storyboard、图片/视频提示词、审查，适配 Claude … |
| 3 | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | 55635 | 4230 / 40 | 2026-11-06T08:36:34Z | NOASSERTION | 活跃(1d) | `active` | 19/25 (fc3 eff5 compat1 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=5；Academic Research Skills for Claude Code: research → write → review … |
| 4 | [blader/humanizer](https://github.com/blader/humanizer) | 65579 | 5185 / 16 | 2026-10-28T07:17:33Z | MIT | 活跃(10d) | `active` | 16/25 (fc2 eff1 compat5 docs3 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent skill that removes signs of AI-generated writing from text |
| 5 | [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) | 5459 | 474 / 17 | 2026-11-05T08:27:07Z | MIT | 活跃(2d) | `active` | 16/25 (fc3 eff2 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=9；Skill that audits and rewrites content to remove AI writing patterns… |

**取值命令与匹配理由**
1. `Ar9av/obsidian-wiki` — `gh api repos/Ar9av/obsidian-wiki --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=40；Framework for AI agents to build and maintain a digital brain through Obsidian wiki &#124; Memory System ｜ ⚠️缓存→现测：3618/2026-10-21/MIT → 3693/2026-11-05T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=40
2. `zenstory-ai/drama-skills` — `gh api repos/zenstory-ai/drama-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；开源 AI 短剧/漫剧创作 skill 合集：剧本、角色资产、分镜 storyboard、图片/视频提示词、审查，适配 Claude Code 与 Codex &#124; Open-source AI sho ｜ ⚠️缓存→现测：3326/2026-10-20/MIT → 3869/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=12
3. `Imbad0202/academic-research-skills` — `gh api repos/Imbad0202/academic-research-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=5；Academic Research Skills for Claude Code: research → write → review → revise → finalize ｜ ⚠️缓存→现测：54267/2026-10-28/NOASSERTION → 55635/2026-11-06T0…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=5
4. `blader/humanizer` — `gh api repos/blader/humanizer --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent skill that removes signs of AI-generated writing from text ｜ ⚠️缓存→现测：60349/2026-10-16/MIT → 65579/2026-10-28T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1
5. `conorbronsdon/avoid-ai-writing` — `gh api repos/conorbronsdon/avoid-ai-writing --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=9；Skill that audits and rewrites content to remove AI writing patterns. Use it with your favorite agen ｜ ⚠️缓存→现测：5229/2026-10-20/MIT → 5459/2026-11-05T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=9

### 7.48 `report-generator-skill` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：视频分析报告生成技能。整合分镜拆解数据和钩子分析结果，生成 Markdown 格式的专业视频分析报告。运行脚本 'python scripts/generate_report.py <breakdown_json> [hook_analysis_json]'，输出完整的 Markdown 报告，包含基本信息、前三秒钩子分析、分镜概览、BGM分析、场景分析等章节。（desc_len=182；SKILL.md bytes=5209）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=11，trim=1） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [kangarooking/cangjie-skill](https://github.com/kangarooking/cangjie-skill) | 12282 | 1443 / 21 | 2026-10-02T03:17:52Z | MIT | 活跃(36d) | `active` | 20/25 (fc4 eff3 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=47；把书、长视频、播客等高价值内容蒸馏成可执行的 Agent Skills（Distill high-value content from… |
| 2 | [wiltodelta/remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks) | 6295 | 588 / 2 | 2026-11-06T01:27:32Z | Apache-2.0 | 活跃(1d) | `active` | 20/25 (fc3 eff4 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Remove visible and invisible AI watermarks from images and video, an… |
| 3 | [ningzimu/codex-ppt-skill](https://github.com/ningzimu/codex-ppt-skill) | 7685 | 363 / 3 | 2026-10-13T13:04:15Z | MIT | 活跃(24d) | `active` | 17/25 (fc2 eff3 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；GPT-Image-2 PPT Generator Skill for Creating Image-Based PowerPoint … |
| 4 | [Akxan/ppt-agent-skill](https://github.com/Akxan/ppt-agent-skill) | 180 | 49 / 0 | 2026-05-11T00:47:17Z | MIT | 一般(180d) | `active` | 12/25 (fc2 eff1 compat5 docs3 comm1) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；🎨 World-class AI presentation generator · 26 styles · 18 charts · b… |
| 5 | [chuspeeism/dashi-ppt-skill](https://github.com/chuspeeism/dashi-ppt-skill) | 10430 | 887 / 16 | 2026-11-06T08:26:30Z | AGPL-3.0 | 活跃(1d) | `active` | 9/25 (fc2 eff0 compat1 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=1/5；SKILL.md=1；An AI-agent skill that generates browser-editable presentations from… |

**取值命令与匹配理由**
1. `kangarooking/cangjie-skill` — `gh api repos/kangarooking/cangjie-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=47；把书、长视频、播客等高价值内容蒸馏成可执行的 Agent Skills（Distill high-value content from books, long-form videos, podcast ｜ ⚠️缓存→现测：11696/2026-10-02/MIT → 12282/2026-10-02T0…/MIT（stars 漂移） ｜ SKILL.md=47
2. `wiltodelta/remove-ai-watermarks` — `gh api repos/wiltodelta/remove-ai-watermarks --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Remove visible and invisible AI watermarks from images and video, and AI provenance metadata from im ｜ ⚠️缓存→现测：6115/2026-10-24/Apache-2.0 → 6295/2026-11-06T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=4
3. `ningzimu/codex-ppt-skill` — `gh api repos/ningzimu/codex-ppt-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；GPT-Image-2 PPT Generator Skill for Creating Image-Based PowerPoint Presentations in Codex and Other ｜ ⚠️缓存→现测：7273/2026-10-13/MIT → 7685/2026-10-13T1…/MIT（stars 漂移） ｜ SKILL.md=1
4. `Akxan/ppt-agent-skill` — `gh api repos/Akxan/ppt-agent-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；🎨 World-class AI presentation generator · 26 styles · 18 charts · benchmarked against Linear/Anthro ｜ ⚠️缓存→现测：165/2026-05-11/MIT → 180/2026-05-11T0…/MIT（stars 漂移） ｜ SKILL.md=1
5. `chuspeeism/dashi-ppt-skill` — `gh api repos/chuspeeism/dashi-ppt-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=1/5；SKILL.md=1；An AI-agent skill that generates browser-editable presentations from multiple visual themes, exporta ｜ ⚠️缓存→现测：9907/2026-09-12/AGPL-3.0 → 10430/2026-11-06T0…/AGPL-3.0（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.49 `shell-encoding-pitfalls` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：中文 Windows + Git Bash 下的 shell 编码与编辑坑修复：curl 传中文致请求体乱码、字符串替换不生效、Edit 显示成功但运行仍报旧错、变量名一字之差耗时半小时、Write 把 .ps1 存成 UTF-8 无 BOM 使 PowerShell 解析中文报错、PowerShell 双引号串改 .sh 时 $() 与反引号被当场展开把文件灌成重复嵌套（且 .git/hooks 非跟踪、git 还原不了）、git c（desc_len=395；SKILL.md bytes=16853）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [siddsachar/row-bot](https://github.com/siddsachar/row-bot) | 1683 | 204 / 36 | 2026-11-06T18:36:12Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc4 eff5 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=50；Row-Bot - Personal AI Sovereignty. A local-first AI assistant with … |
| 2 | [mksglu/context-mode](https://github.com/mksglu/context-mode) | 33601 | 2306 / 3 | 2026-11-06T15:43:52Z | NOASSERTION | 活跃(0d) | `active` | 21/25 (fc4 eff5 compat4 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=4/5；SKILL.md=11；Context window optimization for AI coding agents. Sandboxes tool ou… |
| 3 | [Tencent/BrowserSkill](https://github.com/Tencent/BrowserSkill) | 10119 | 730 / 149 | 2026-11-06T12:18:10Z | MIT | 活跃(0d) | `active` | 19/25 (fc2 eff5 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Let AI agents use your real, logged-in browser without interrupting … |
| 4 | [SnailSploit/Claude-Red](https://github.com/SnailSploit/Claude-Red) | 10445 | 1402 / 43 | 2026-10-12T15:02:40Z | MIT | 活跃(25d) | `active` | 17/25 (fc4 eff2 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=79；claude-red is a curated library of offensive security skills design… |
| 5 | [openclaw/lobster](https://github.com/openclaw/lobster) | 1281 | 291 / 3 | 2026-11-06T00:20:35Z | MIT | 活跃(1d) | `active` | 17/25 (fc2 eff4 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Lobster is a Openclaw-native workflow shell: a typed, local-first “m… |

**取值命令与匹配理由**
1. `siddsachar/row-bot` — `gh api repos/siddsachar/row-bot --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=50；Row-Bot - Personal AI Sovereignty. A local-first AI assistant with integrated tools, a personal know ｜ ⚠️缓存→现测：1646/2026-10-24/Apache-2.0 → 1683/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=50
2. `mksglu/context-mode` — `gh api repos/mksglu/context-mode --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=4/5；SKILL.md=11；Context window optimization for AI coding agents. Sandboxes tool output (98% reduction), persists se ｜ ⚠️缓存→现测：32150/2026-10-24/NOASSERTION → 33601/2026-11-06T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=11
3. `Tencent/BrowserSkill` — `gh api repos/Tencent/BrowserSkill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Let AI agents use your real, logged-in browser without interrupting your work. CLI + extension for b ｜ ⚠️缓存→现测：9516/2026-10-23/MIT → 10119/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=2
4. `SnailSploit/Claude-Red` — `gh api repos/SnailSploit/Claude-Red --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=79；claude-red is a curated library of offensive security skills designed for the Claude skills system. ｜ ⚠️缓存→现测：8889/2026-10-12/MIT → 10445/2026-10-12T1…/MIT（stars 漂移） ｜ SKILL.md=79
5. `openclaw/lobster` — `gh api repos/openclaw/lobster --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Lobster is a Openclaw-native workflow shell: a typed, local-first “macro engine” that turns skills/t ｜ ⚠️缓存→现测：1276/2026-10-22/MIT → 1281/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.50 `static-site-batch-audit-fix` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：纯静态HTML站点批量审计+修复+验证流水线。当需要对多文件HTML/CSS/JS站点做全站扫描、批量文本替换、一致性修复（品牌名/lang/ARIA/favicon/meta）、开源项目对标后的缺陷清单执行、暗色模式与适老化字号改造、并用浏览器复验计算样式时使用。触发词：静态站点审计、批量修复HTML、全站替换、static site audit、batch fix、HTML批量修复、多页面修复、站点一致性修复、全站扫描、多页站改文案（desc_len=259；SKILL.md bytes=14405）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=11，trim=1） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | 80005 | 7372 / 238 | 2026-11-06T18:54:48Z | Apache-2.0 | 活跃(0d) | `active` | 23/25 (fc4 eff5 compat5 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=26；Write HTML. Render video. Built for agents. |
| 2 | [tirth8205/code-review-graph](https://github.com/tirth8205/code-review-graph) | 32624 | 2967 / 111 | 2026-11-06T19:05:44Z | MIT | 活跃(0d) | `active` | 21/25 (fc3 eff5 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Local-first code intelligence graph for MCP and CLI. Builds a persis… |
| 3 | [samugit83/redamon](https://github.com/samugit83/redamon) | 3311 | 698 / 18 | 2026-11-05T18:47:16Z | MIT | 活跃(1d) | `active` | 20/25 (fc4 eff3 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=19；Open-source, self-hosted AI penetration testing framework: maps you… |
| 4 | [glitternetwork/pinme](https://github.com/glitternetwork/pinme) | 3754 | 276 / 10 | 2026-09-12T05:23:49Z | MIT | 活跃(56d) | `active` | 17/25 (fc3 eff3 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Deploy Your Frontend in a Single Command. Claude Code Skills support… |
| 5 | [Jakeschincariol/replica-skill](https://github.com/Jakeschincariol/replica-skill) | 7907 | 1406 / 19 | 2026-10-03T12:07:53Z | MIT | 活跃(34d) | `active` | 16/25 (fc4 eff1 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=11；Eleven free Claude skills that clone any app: reverse-engineer it, … |

**取值命令与匹配理由**
1. `heygen-com/hyperframes` — `gh api repos/heygen-com/hyperframes --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=26；Write HTML. Render video. Built for agents. ｜ ⚠️缓存→现测：75789/2026-10-30/Apache-2.0 → 80005/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=26
2. `tirth8205/code-review-graph` — `gh api repos/tirth8205/code-review-graph --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Local-first code intelligence graph for MCP and CLI. Builds a persistent map of your codebase so AI ｜ ⚠️缓存→现测：32379/2026-10-16/MIT → 32624/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=7
3. `samugit83/redamon` — `gh api repos/samugit83/redamon --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=19；Open-source, self-hosted AI penetration testing framework: maps your attack surface into a graph, au ｜ ⚠️缓存→现测：3210/2026-10-22/MIT → 3311/2026-11-05T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=19
4. `glitternetwork/pinme` — `gh api repos/glitternetwork/pinme --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Deploy Your Frontend in a Single Command. Claude Code Skills supported. ｜ ⚠️缓存→现测：3755/2026-09-12/MIT → 3754/2026-09-12T0…/MIT（stars 漂移） ｜ SKILL.md=7
5. `Jakeschincariol/replica-skill` — `gh api repos/Jakeschincariol/replica-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=11；Eleven free Claude skills that clone any app: reverse-engineer it, rebuild it, test it for bugs, the ｜ ⚠️缓存→现测：5316/2026-10-03/MIT → 7907/2026-10-03T1…/MIT（stars 漂移） ｜ SKILL.md=11

### 7.51 `story-cover` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：小说封面生成。根据书名、作者名自动分析题材风格，调用 GPT-Image-2 直接生成含标题和署名的专业级网文封面。触发方式：/story-cover、/封面、「帮我做个封面」「生成封面图」「做个小说封面」「封面设计」。（desc_len=110；SKILL.md bytes=1909）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：[worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [krillinai/OpenCreator](https://github.com/krillinai/OpenCreator) | 14189 | 1583 / 43 | 2026-11-05T23:26:51Z | Apache-2.0 | 活跃(1d) | `active` | 22/25 (fc4 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=15；Formerly KrillinAI, VideoTranslation and Dubbing Tool. Open-source … |
| 2 | [wiltodelta/remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks) | 6295 | 588 / 2 | 2026-11-06T01:27:32Z | Apache-2.0 | 活跃(1d) | `active` | 20/25 (fc3 eff4 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Remove visible and invisible AI watermarks from images and video, an… |
| 3 | [img2threejs/img2threejs](https://github.com/img2threejs/img2threejs) | 20384 | 1721 / 120 | 2026-11-05T08:38:00Z | Apache-2.0 | 活跃(2d) | `active` | 19/25 (fc2 eff4 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Rebuild the object in a reference image as a code-only, procedural, … |
| 4 | [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | 77610 | 10324 / 448 | 2026-11-03T17:42:02Z | AGPL-3.0 | 活跃(3d) | `active` | 18/25 (fc5 eff3 compat1 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=1/5；SKILL.md=140；World's first open-source, agentic video production system. 12 pro… |
| 5 | [GargantuaX/gemini-watermark-remover](https://github.com/GargantuaX/gemini-watermark-remover) | 5719 | 830 / 19 | 2026-10-26T19:06:44Z | MIT | 活跃(11d) | `active` | 18/25 (fc2 eff4 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A high-performance, 100% client-side tool for removing Gemini AI ima… |

**取值命令与匹配理由**
1. `krillinai/OpenCreator` — `gh api repos/krillinai/OpenCreator --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=15；Formerly KrillinAI, VideoTranslation and Dubbing Tool. Open-source AI workspace for creators, powere ｜ ⚠️缓存→现测：13918/2026-10-25/Apache-2.0 → 14189/2026-11-05T2…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=15
2. `wiltodelta/remove-ai-watermarks` — `gh api repos/wiltodelta/remove-ai-watermarks --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Remove visible and invisible AI watermarks from images and video, and AI provenance metadata from im ｜ ⚠️缓存→现测：6115/2026-10-24/Apache-2.0 → 6295/2026-11-06T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=4
3. `img2threejs/img2threejs` — `gh api repos/img2threejs/img2threejs --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Rebuild the object in a reference image as a code-only, procedural, quality-gated, animation-ready T ｜ ⚠️缓存→现测：19196/2026-10-21/Apache-2.0 → 20384/2026-11-05T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=2
4. `calesthio/OpenMontage` — `gh api repos/calesthio/OpenMontage --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=1/5；SKILL.md=140；World's first open-source, agentic video production system. 12 production pipelines, 100+ tools, 700 ｜ ⚠️缓存→现测：71689/2026-10-24/AGPL-3.0 → 77610/2026-11-03T1…/AGPL-3.0（stars,pushed_at 漂移） ｜ SKILL.md=140
5. `GargantuaX/gemini-watermark-remover` — `gh api repos/GargantuaX/gemini-watermark-remover --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A high-performance, 100% client-side tool for removing Gemini AI image & video watermarks. Built wit ｜ ⚠️缓存→现测：5672/2026-10-04/MIT → 5719/2026-10-26T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.52 `story-deslop` ｜ HIGH ｜ 候选线索（元数据已实测，功能等价待复核）

- **功能边界**：网文去AI味。检测并清除文本中的AI写作痕迹，让文字回归自然、非模板化。触发方式：/story-deslop、/去AI味、「去AI味」「这篇太AI了」「网文去AI味」。（desc_len=84；SKILL.md bytes=10917）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：FAMILY_ONLY（candidates_n=5，skill_relevant_n=1，trim=0） ｜ **语义缺口**：是 ｜ **声明上游**：[worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）
- **族级补位（禁当替代引用）**：[wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)、[coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills)、[EverMind-AI/EverOS](https://github.com/EverMind-AI/EverOS)、[genspark-ai/genoffice](https://github.com/genspark-ai/genoffice)（共 4 件，`not_replacement=true`）

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [sickn33/agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills) | 49278 | 7151 / 7 | 2026-11-06T17:55:43Z | MIT | 活跃(0d) | `active` | 线索分 8.99 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=9016；stars=49278；description=2,926+ reusable AI agent skills for Claude Code, Codex, Cursor an… |
| 2 | [samber/cc-skills](https://github.com/samber/cc-skills) | 242 | 18 / 3 | 2026-11-01T07:26:23Z | MIT | 活跃(6d) | `active` | 线索分 8 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=21；stars=242；description=🧑‍🎨 A collection of agentic skills that works |
| 3 | [alchaincyf/tramstop-skill](https://github.com/alchaincyf/tramstop-skill) | 56 | 10 / 0 | 2026-10-13T06:55:51Z | MIT | 活跃(25d) | `active` | 线索分 8 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=1；stars=56；description=电车站.skill — 人味不是删出来的。Evidence-based de-slop skill: 四层AI味模型+真实素材注入，来自四版本… |
| 4 | [NulightJens/humanizer-stack](https://github.com/NulightJens/humanizer-stack) | 379 | 29 / 2 | 2026-07-24T16:33:23Z | NOASSERTION | 一般(105d) | `active` | 线索分 7.01 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=2；stars=379；description=Two-pass pipeline for removing AI writing tells from outward-facing te… |
| 5 | [GetBindu/awesome-claude-code-and-skills](https://github.com/GetBindu/awesome-claude-code-and-skills) | 207 | 292 / 175 | 2026-10-07T19:39:29Z | Apache-2.0 | 活跃(30d) | `active` | 线索分 5 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [第一遍定向检索] SKILL.md=0；stars=207；description=A collection of Claude Skills |

**取值命令与匹配理由**
1. `sickn33/agentic-awesome-skills` — `gh api repos/sickn33/agentic-awesome-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=9016；stars=49278；description=2,926+ reusable AI agent skills for Claude Code, Codex, Cursor and Gemini CLI. AAS Core adds local catalog discovery, agent-owned selection ｜ SKILL.md=9016 ｜ `gh api repos/sickn33/agentic-awesome-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
2. `samber/cc-skills` — `gh api repos/samber/cc-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=21；stars=242；description=🧑‍🎨 A collection of agentic skills that works ｜ SKILL.md=21 ｜ `gh api repos/samber/cc-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
3. `alchaincyf/tramstop-skill` — `gh api repos/alchaincyf/tramstop-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=1；stars=56；description=电车站.skill — 人味不是删出来的。Evidence-based de-slop skill: 四层AI味模型+真实素材注入，来自四版本盲测实验 ｜ SKILL.md=1 ｜ `gh api repos/alchaincyf/tramstop-skill/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
4. `NulightJens/humanizer-stack` — `gh api repos/NulightJens/humanizer-stack --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=2；stars=379；description=Two-pass pipeline for removing AI writing tells from outward-facing text: a surface pass plus a structural pass grounded in the StoryScope s ｜ SKILL.md=2 ｜ `gh api repos/NulightJens/humanizer-stack/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
5. `GetBindu/awesome-claude-code-and-skills` — `gh api repos/GetBindu/awesome-claude-code-and-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [第一遍定向检索] SKILL.md=0；stars=207；description=A collection of Claude Skills ｜ SKILL.md=0 ｜ `gh api repos/GetBindu/awesome-claude-code-and-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核

### 7.53 `story-import` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：逆向导入已有小说。将已写好的小说（半成品或完本）反向解析为标准项目目录结构，兼容 story-long-write / story-short-write 后续写作流程；内部复用 story-long-analyze / story-short-analyze 的拆解管道，按篇幅自动分流。触发方式：/story-import、「导入小说」「反向解析」「导入」「把我的书导进来」。（desc_len=190；SKILL.md bytes=10095）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=8，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：[worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [EverMind-AI/EverOS](https://github.com/EverMind-AI/EverOS) | 13840 | 963 / 43 | 2026-11-06T08:46:28Z | Apache-2.0 | 活跃(1d) | `active` | 21/25 (fc3 eff5 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=5；One portable memory layer for every AI agent: local-first, Markdown-… |
| 2 | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | 27923 | 2313 / 11 | 2026-11-04T18:13:42Z | MIT | 活跃(2d) | `active` | 20/25 (fc4 eff3 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=18；Persistent file-based planning for AI coding agents and long-runnin… |
| 3 | [zenstory-ai/drama-skills](https://github.com/zenstory-ai/drama-skills) | 3869 | 694 / 3 | 2026-11-06T17:39:19Z | MIT | 活跃(0d) | `active` | 20/25 (fc4 eff4 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；开源 AI 短剧/漫剧创作 skill 合集：剧本、角色资产、分镜 storyboard、图片/视频提示词、审查，适配 Claude … |
| 4 | [zenstory-ai/oh-story-claudecode](https://github.com/zenstory-ai/oh-story-claudecode) | 8359 | 1178 / 10 | 2026-11-06T18:01:03Z | MIT | 活跃(0d) | `active` | 19/25 (fc4 eff3 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Claude Code / Codex / OpenCode agent skills for writing Chinese web… |
| 5 | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | 55635 | 4230 / 40 | 2026-11-06T08:36:34Z | NOASSERTION | 活跃(1d) | `active` | 19/25 (fc3 eff5 compat1 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=5；Academic Research Skills for Claude Code: research → write → review … |

**取值命令与匹配理由**
1. `EverMind-AI/EverOS` — `gh api repos/EverMind-AI/EverOS --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=5；One portable memory layer for every AI agent: local-first, Markdown-native, user-owned, and self-evo ｜ ⚠️缓存→现测：13597/2026-10-22/Apache-2.0 → 13840/2026-11-06T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=5
2. `OthmanAdi/planning-with-files` — `gh api repos/OthmanAdi/planning-with-files --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=18；Persistent file-based planning for AI coding agents and long-running tasks. Crash-proof markdown pla ｜ ⚠️缓存→现测：27631/2026-10-24/MIT → 27923/2026-11-04T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=18
3. `zenstory-ai/drama-skills` — `gh api repos/zenstory-ai/drama-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；开源 AI 短剧/漫剧创作 skill 合集：剧本、角色资产、分镜 storyboard、图片/视频提示词、审查，适配 Claude Code 与 Codex &#124; Open-source AI sho ｜ ⚠️缓存→现测：3326/2026-10-20/MIT → 3869/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=12
4. `zenstory-ai/oh-story-claudecode` — `gh api repos/zenstory-ai/oh-story-claudecode --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Claude Code / Codex / OpenCode agent skills for writing Chinese web novels (网文): 扫榜、拆文、写作、去AI味、封面全流程 ｜ ⚠️缓存→现测：7971/2026-10-23/MIT → 8359/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=13
5. `Imbad0202/academic-research-skills` — `gh api repos/Imbad0202/academic-research-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=5；Academic Research Skills for Claude Code: research → write → review → revise → finalize ｜ ⚠️缓存→现测：54267/2026-10-28/NOASSERTION → 55635/2026-11-06T0…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=5

### 7.54 `story-long-analyze` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：长篇网文拆文。深度拆解爆款长篇小说的黄金三章、人设架构、爽点设计、节奏控制。单一深度拆解管道：跑完黄金三章（Stage 1）后产出快速预览报告并询问是否继续全量拆解，确认后从 Stage 2 续跑逐章摘要、聚合分析、设定关系、汇总报告，全程产物落盘 拆文库/{书名}/。触发方式：/story-long-analyze、/长篇拆文、「帮我拆这本书」「拆这本书」「分析黄金三章」「深度拆解」「完整拆解」「系统拆解」或提供小说文本文件路径——全（desc_len=228；SKILL.md bytes=6187）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=3，skill_relevant_n=3，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：[worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [EverMind-AI/EverOS](https://github.com/EverMind-AI/EverOS) | 13840 | 963 / 43 | 2026-11-06T08:46:28Z | Apache-2.0 | 活跃(1d) | `active` | 21/25 (fc3 eff5 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=5；One portable memory layer for every AI agent: local-first, Markdown-… |
| 2 | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | 27923 | 2313 / 11 | 2026-11-04T18:13:42Z | MIT | 活跃(2d) | `active` | 20/25 (fc4 eff3 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=18；Persistent file-based planning for AI coding agents and long-runnin… |
| 3 | [zenstory-ai/oh-story-claudecode](https://github.com/zenstory-ai/oh-story-claudecode) | 8359 | 1178 / 10 | 2026-11-06T18:01:03Z | MIT | 活跃(0d) | `active` | 19/25 (fc4 eff3 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Claude Code / Codex / OpenCode agent skills for writing Chinese web… |

**取值命令与匹配理由**
1. `EverMind-AI/EverOS` — `gh api repos/EverMind-AI/EverOS --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=5；One portable memory layer for every AI agent: local-first, Markdown-native, user-owned, and self-evo ｜ ⚠️缓存→现测：13597/2026-10-22/Apache-2.0 → 13840/2026-11-06T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=5
2. `OthmanAdi/planning-with-files` — `gh api repos/OthmanAdi/planning-with-files --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=18；Persistent file-based planning for AI coding agents and long-running tasks. Crash-proof markdown pla ｜ ⚠️缓存→现测：27631/2026-10-24/MIT → 27923/2026-11-04T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=18
3. `zenstory-ai/oh-story-claudecode` — `gh api repos/zenstory-ai/oh-story-claudecode --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Claude Code / Codex / OpenCode agent skills for writing Chinese web novels (网文): 扫榜、拆文、写作、去AI味、封面全流程 ｜ ⚠️缓存→现测：7971/2026-10-23/MIT → 8359/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=13

### 7.55 `story-long-write` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：长篇网文写作。从大纲到正文，辅助长篇网络小说的创作，包括世界观、人物、情节线管理。触发方式：/story-long-write、/写长篇、「帮我开书」「写大纲」「日更」「续写」「继续写」「修改第X章」「回炉」「重写第X章」。（desc_len=112；SKILL.md bytes=3035）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=5，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：[worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [EverMind-AI/EverOS](https://github.com/EverMind-AI/EverOS) | 13840 | 963 / 43 | 2026-11-06T08:46:28Z | Apache-2.0 | 活跃(1d) | `active` | 21/25 (fc3 eff5 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=5；One portable memory layer for every AI agent: local-first, Markdown-… |
| 2 | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | 27923 | 2313 / 11 | 2026-11-04T18:13:42Z | MIT | 活跃(2d) | `active` | 20/25 (fc4 eff3 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=18；Persistent file-based planning for AI coding agents and long-runnin… |
| 3 | [zenstory-ai/oh-story-claudecode](https://github.com/zenstory-ai/oh-story-claudecode) | 8359 | 1178 / 10 | 2026-11-06T18:01:03Z | MIT | 活跃(0d) | `active` | 19/25 (fc4 eff3 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Claude Code / Codex / OpenCode agent skills for writing Chinese web… |
| 4 | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | 55635 | 4230 / 40 | 2026-11-06T08:36:34Z | NOASSERTION | 活跃(1d) | `active` | 19/25 (fc3 eff5 compat1 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=5；Academic Research Skills for Claude Code: research → write → review … |
| 5 | [realrossmanngroup/no_ai_slop_writing_rules](https://github.com/realrossmanngroup/no_ai_slop_writing_rules) | 709 | 81 / 2 | 2026-05-30T20:41:20Z | NOASSERTION | 一般(160d) | `active` | 10/25 (fc3 eff0 compat3 docs3 comm1) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=3/5；SKILL.md=4；Claude Code reference: write in Louis Rossmann's voice, never like A… |

**取值命令与匹配理由**
1. `EverMind-AI/EverOS` — `gh api repos/EverMind-AI/EverOS --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=5；One portable memory layer for every AI agent: local-first, Markdown-native, user-owned, and self-evo ｜ ⚠️缓存→现测：13597/2026-10-22/Apache-2.0 → 13840/2026-11-06T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=5
2. `OthmanAdi/planning-with-files` — `gh api repos/OthmanAdi/planning-with-files --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=18；Persistent file-based planning for AI coding agents and long-running tasks. Crash-proof markdown pla ｜ ⚠️缓存→现测：27631/2026-10-24/MIT → 27923/2026-11-04T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=18
3. `zenstory-ai/oh-story-claudecode` — `gh api repos/zenstory-ai/oh-story-claudecode --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Claude Code / Codex / OpenCode agent skills for writing Chinese web novels (网文): 扫榜、拆文、写作、去AI味、封面全流程 ｜ ⚠️缓存→现测：7971/2026-10-23/MIT → 8359/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=13
4. `Imbad0202/academic-research-skills` — `gh api repos/Imbad0202/academic-research-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=5；Academic Research Skills for Claude Code: research → write → review → revise → finalize ｜ ⚠️缓存→现测：54267/2026-10-28/NOASSERTION → 55635/2026-11-06T0…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=5
5. `realrossmanngroup/no_ai_slop_writing_rules` — `gh api repos/realrossmanngroup/no_ai_slop_writing_rules --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=3/5；SKILL.md=4；Claude Code reference: write in Louis Rossmann's voice, never like AI slop. Portable CLAUDE.md plus ｜ ⚠️缓存→现测：705/2026-05-30/UNLICENSED → 709/2026-05-30T2…/NOASSERTION（stars,license 漂移） ｜ SKILL.md=4

### 7.56 `story-review` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：多视角对抗式审查。full/lean 模式在已部署 reviewer agents 时并行 spawn；缺失/异常 agents 或 spawn 失败时自动降级 solo，参考文件不可读时使用内置 rubric fallback。触发方式：/story-review、/审查、「审查一下」「帮我审一下」。（desc_len=152；SKILL.md bytes=11709）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=8，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：[worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | 18796 | 1527 / 75 | 2026-11-06T04:09:40Z | MIT | 活跃(1d) | `active` | 23/25 (fc5 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=197；ARIS ⚔️ (Auto-Research-In-Sleep) — Lightweight Markdown-only skill… |
| 2 | [backnotprop/plannotator](https://github.com/backnotprop/plannotator) | 9874 | 745 / 175 | 2026-11-06T19:01:25Z | Apache-2.0 | 活跃(0d) | `active` | 20/25 (fc4 eff5 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=19；Annotate and review coding agent plans and code diffs visually, sha… |
| 3 | [zenstory-ai/drama-skills](https://github.com/zenstory-ai/drama-skills) | 3869 | 694 / 3 | 2026-11-06T17:39:19Z | MIT | 活跃(0d) | `active` | 20/25 (fc4 eff4 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；开源 AI 短剧/漫剧创作 skill 合集：剧本、角色资产、分镜 storyboard、图片/视频提示词、审查，适配 Claude … |
| 4 | [zenstory-ai/oh-story-claudecode](https://github.com/zenstory-ai/oh-story-claudecode) | 8359 | 1178 / 10 | 2026-11-06T18:01:03Z | MIT | 活跃(0d) | `active` | 19/25 (fc4 eff3 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Claude Code / Codex / OpenCode agent skills for writing Chinese web… |
| 5 | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | 55635 | 4230 / 40 | 2026-11-06T08:36:34Z | NOASSERTION | 活跃(1d) | `active` | 19/25 (fc3 eff5 compat1 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=5；Academic Research Skills for Claude Code: research → write → review … |

**取值命令与匹配理由**
1. `wanshuiyin/Auto-claude-code-research-in-sleep` — `gh api repos/wanshuiyin/Auto-claude-code-research-in-sleep --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=197；ARIS ⚔️ (Auto-Research-In-Sleep) — Lightweight Markdown-only skills for autonomous ML research: cros ｜ ⚠️缓存→现测：18023/2026-10-24/MIT → 18796/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=197
2. `backnotprop/plannotator` — `gh api repos/backnotprop/plannotator --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=19；Annotate and review coding agent plans and code diffs visually, share with your team, send feedback ｜ ⚠️缓存→现测：9624/2026-10-25/Apache-2.0 → 9874/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=19
3. `zenstory-ai/drama-skills` — `gh api repos/zenstory-ai/drama-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；开源 AI 短剧/漫剧创作 skill 合集：剧本、角色资产、分镜 storyboard、图片/视频提示词、审查，适配 Claude Code 与 Codex &#124; Open-source AI sho ｜ ⚠️缓存→现测：3326/2026-10-20/MIT → 3869/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=12
4. `zenstory-ai/oh-story-claudecode` — `gh api repos/zenstory-ai/oh-story-claudecode --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Claude Code / Codex / OpenCode agent skills for writing Chinese web novels (网文): 扫榜、拆文、写作、去AI味、封面全流程 ｜ ⚠️缓存→现测：7971/2026-10-23/MIT → 8359/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=13
5. `Imbad0202/academic-research-skills` — `gh api repos/Imbad0202/academic-research-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=5；Academic Research Skills for Claude Code: research → write → review → revise → finalize ｜ ⚠️缓存→现测：54267/2026-10-28/NOASSERTION → 55635/2026-11-06T0…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=5

### 7.57 `story-scan` ｜ HIGH ｜ 候选线索（元数据已实测，功能等价待复核）

- **功能边界**：长篇/短篇网文扫榜统一入口。长篇：起点/番茄/七猫/晋江/刺猬猫；短篇：知乎盐言/点众/黑岩/七猫短篇。触发：/story-scan、/扫榜、「长篇什么火」「短篇什么火」「起点排行」「知乎故事排行」「短篇扫榜」。（desc_len=106；SKILL.md bytes=6452）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：FAMILY_ONLY（candidates_n=5，skill_relevant_n=1，trim=0） ｜ **语义缺口**：是 ｜ **声明上游**：[worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）
- **族级补位（禁当替代引用）**：[wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)、[coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills)、[EverMind-AI/EverOS](https://github.com/EverMind-AI/EverOS)、[genspark-ai/genoffice](https://github.com/genspark-ai/genoffice)（共 4 件，`not_replacement=true`）

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode) | 8359 | 1178 / 10 | 2026-11-06T18:01:03Z | MIT | 活跃(0d) | `active` | 线索分 8.17 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=14；stars=8359；description=AI 写网文全流程 skill 包：扫榜选材、拆解爆款、大纲细纲、长篇设定与伏笔追踪、短篇反转、去AI味与封面生成，适配 Claude … |
| 2 | [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 36928 | 4084 / 12 | 2026-11-05T10:43:36Z | MIT | 活跃(2d) | `active` | 线索分 5.74 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=0；stars=36928；description=A curated collection of 1000+ agent skills from official dev teams a… |
| 3 | [jivoi/awesome-osint](https://github.com/jivoi/awesome-osint) | 30811 | 4266 / 2 | 2026-11-04T06:17:35Z | NOASSERTION | 活跃(3d) | `active` | 线索分 1.62 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [第一遍定向检索] SKILL.md=0；stars=30811；description=:scream: A curated list of amazingly awesome OSINT |
| 4 | [cipher387/osint_stuff_tool_collection](https://github.com/cipher387/osint_stuff_tool_collection) | 9074 | 1092 / 2 | 2026-11-06T19:36:41Z | GPL-3.0 | 活跃(0d) | `active` | 线索分 1.18 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [第一遍定向检索] SKILL.md=0；stars=9074；description=A collection of several hundred online tools for OSINT |
| 5 | [punkpeye/awesome-remote-mcp-servers](https://github.com/punkpeye/awesome-remote-mcp-servers) | 2716 | 3287 / 2082 | 2026-11-06T17:47:35Z | MIT | 活跃(0d) | `active` | 线索分 1.05 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=0；stars=2716；description=A collection of remote MCP servers. |

**取值命令与匹配理由**
1. `worldwonderer/oh-story-claudecode` — `gh api repos/worldwonderer/oh-story-claudecode --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=14；stars=8359；description=AI 写网文全流程 skill 包：扫榜选材、拆解爆款、大纲细纲、长篇设定与伏笔追踪、短篇反转、去AI味与封面生成，适配 Claude Code / Codex / Antigravity / OpenCode 等 ｜ Agent skill pack for writing C ｜ SKILL.md=14 ｜ `gh api repos/worldwonderer/oh-story-claudecode/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
2. `VoltAgent/awesome-agent-skills` — `gh api repos/VoltAgent/awesome-agent-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=0；stars=36928；description=A curated collection of 1000+ agent skills from official dev teams and the community, compatible with Claude Code, Codex, Gemini CLI, Cursor ｜ SKILL.md=0 ｜ `gh api repos/VoltAgent/awesome-agent-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核
3. `jivoi/awesome-osint` — `gh api repos/jivoi/awesome-osint --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [第一遍定向检索] SKILL.md=0；stars=30811；description=:scream: A curated list of amazingly awesome OSINT ｜ SKILL.md=0 ｜ `gh api repos/jivoi/awesome-osint/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核
4. `cipher387/osint_stuff_tool_collection` — `gh api repos/cipher387/osint_stuff_tool_collection --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [第一遍定向检索] SKILL.md=0；stars=9074；description=A collection of several hundred online tools for OSINT ｜ SKILL.md=0 ｜ `gh api repos/cipher387/osint_stuff_tool_collection/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核
5. `punkpeye/awesome-remote-mcp-servers` — `gh api repos/punkpeye/awesome-remote-mcp-servers --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=0；stars=2716；description=A collection of remote MCP servers. ｜ SKILL.md=0 ｜ `gh api repos/punkpeye/awesome-remote-mcp-servers/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核

### 7.58 `story-setup` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：网文写作工具集基础设施部署。为 Claude Code / OpenCode / Codex / ZCode / OpenClaw / Reasonix 提供内置适配；Web AI / 通用 Agent 可走 skills + AGENTS.md 文件模式。触发方式：/story-setup、$story-setup、「准备写书」「帮我搭一下环境」「配置写作项目」。（desc_len=184；SKILL.md bytes=6998）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：[worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 298441 | 44116 / 236 | 2026-11-06T05:29:44Z | MIT | 活跃(1d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instin… |
| 2 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 113914 | 9885 / 125 | 2026-11-06T18:15:53Z | Apache-2.0 | 活跃(0d) | `active` | 24/25 (fc4 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Persistent Context Across Sessions for Every Agent –  Captures ever… |
| 3 | [cheaper-inference/OmniRoute](https://github.com/cheaper-inference/OmniRoute) | 85126 | 12829 / 611 | 2026-11-06T18:58:22Z | MIT | 活跃(0d) | `active` | 24/25 (fc4 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=53；Never stop coding. Free MIT AI gateway: one endpoint, 375 providers… |
| 4 | [iOfficeAI/AionUi](https://github.com/iOfficeAI/AionUi) | 34072 | 3560 / 886 | 2026-11-05T05:31:20Z | Apache-2.0 | 活跃(2d) | `active` | 22/25 (fc3 eff5 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；Open-source 24/7 Cowork app for OpenClaw, Hermes, Claude Code, Codex… |
| 5 | [wshobson/agents](https://github.com/wshobson/agents) | 42259 | 4464 / 6 | 2026-11-05T15:57:30Z | MIT | 活跃(1d) | `active` | 22/25 (fc5 eff4 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=185；Multi-harness agentic plugin marketplace for Claude Code, Codex, C… |

**取值命令与匹配理由**
1. `affaan-m/ECC` — `gh api repos/affaan-m/ECC --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=1062；The agent harness performance optimization system. Skills, instincts, memory, security, and research ｜ ⚠️缓存→现测：288271/2026-10-20/MIT → 298441/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1062
2. `thedotmack/claude-mem` — `gh api repos/thedotmack/claude-mem --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Persistent Context Across Sessions for Every Agent –  Captures everything your agent does during ses ｜ ⚠️缓存→现测：102894/2026-10-25/Apache-2.0 → 113914/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=43
3. `cheaper-inference/OmniRoute` — `gh api repos/cheaper-inference/OmniRoute --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=53；Never stop coding. Free MIT AI gateway: one endpoint, 375 providers (150+ free), 1,400+ models Kimi, ｜ ⚠️缓存→现测：80857/2026-10-25/MIT → 85126/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=53
4. `iOfficeAI/AionUi` — `gh api repos/iOfficeAI/AionUi --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；Open-source 24/7 Cowork app for OpenClaw, Hermes, Claude Code, Codex, OpenCode and 20+ more CLI Agen ｜ ⚠️缓存→现测：33752/2026-10-23/Apache-2.0 → 34072/2026-11-05T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=6
5. `wshobson/agents` — `gh api repos/wshobson/agents --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=185；Multi-harness agentic plugin marketplace for Claude Code, Codex, Cursor, OpenCode, GitHub Copilot, G ｜ ⚠️缓存→现测：41656/2026-10-24/MIT → 42259/2026-11-05T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=185

### 7.59 `story-short-analyze` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：短篇网文拆文。拆解爆款短篇小说（番茄短篇 / 故事会 / 知乎盐选 / 追妻 / 世情 / 重生 / 虐渣等通俗题材）的故事核、结构、情感线、反转设计、写作手法、共鸣层次。单一全量拆解管道：跑完 Stage 2-6 产出完整拆文报告，落盘到 拆文库/{书名}/，下游 story-short-write 同时读拆文报告 + 情节节点 + 写作手法 + 原文 + _meta.json 写下一篇。触发方式：/story-short-analy（desc_len=308；SKILL.md bytes=9787）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=6，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：[worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [zenstory-ai/drama-skills](https://github.com/zenstory-ai/drama-skills) | 3869 | 694 / 3 | 2026-11-06T17:39:19Z | MIT | 活跃(0d) | `active` | 20/25 (fc4 eff4 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；开源 AI 短剧/漫剧创作 skill 合集：剧本、角色资产、分镜 storyboard、图片/视频提示词、审查，适配 Claude … |
| 2 | [zenstory-ai/oh-story-claudecode](https://github.com/zenstory-ai/oh-story-claudecode) | 8359 | 1178 / 10 | 2026-11-06T18:01:03Z | MIT | 活跃(0d) | `active` | 19/25 (fc4 eff3 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Claude Code / Codex / OpenCode agent skills for writing Chinese web… |
| 3 | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | 55635 | 4230 / 40 | 2026-11-06T08:36:34Z | NOASSERTION | 活跃(1d) | `active` | 19/25 (fc3 eff5 compat1 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=5；Academic Research Skills for Claude Code: research → write → review … |
| 4 | [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | 12979 | 1506 / 19 | 2026-10-31T14:53:23Z | MIT | 活跃(6d) | `active` | 14/25 (fc2 eff1 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；A toolbox of film styles made in code for Claude Code: 59 ready to u… |
| 5 | [eternityspring/shuohao-skills](https://github.com/eternityspring/shuohao-skills) | 6148 | 864 / 2 | 2026-10-26T03:32:47Z | Apache-2.0 | 活跃(12d) | `active` | 14/25 (fc3 eff0 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；AI 短剧制作的 skill 集合：拆角色、排大纲、出场景与道具设定、写剧本、切分镜 &#124; Agent skills for A… |

**取值命令与匹配理由**
1. `zenstory-ai/drama-skills` — `gh api repos/zenstory-ai/drama-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；开源 AI 短剧/漫剧创作 skill 合集：剧本、角色资产、分镜 storyboard、图片/视频提示词、审查，适配 Claude Code 与 Codex &#124; Open-source AI sho ｜ ⚠️缓存→现测：3326/2026-10-20/MIT → 3869/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=12
2. `zenstory-ai/oh-story-claudecode` — `gh api repos/zenstory-ai/oh-story-claudecode --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Claude Code / Codex / OpenCode agent skills for writing Chinese web novels (网文): 扫榜、拆文、写作、去AI味、封面全流程 ｜ ⚠️缓存→现测：7971/2026-10-23/MIT → 8359/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=13
3. `Imbad0202/academic-research-skills` — `gh api repos/Imbad0202/academic-research-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=5；Academic Research Skills for Claude Code: research → write → review → revise → finalize ｜ ⚠️缓存→现测：54267/2026-10-28/NOASSERTION → 55635/2026-11-06T0…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=5
4. `lemomo-ai/lemo-opuscar` — `gh api repos/lemomo-ai/lemo-opuscar --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；A toolbox of film styles made in code for Claude Code: 59 ready to use, and your own. Each style is ｜ ⚠️缓存→现测：6782/2026-10-24/MIT → 12979/2026-10-31T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=2
5. `eternityspring/shuohao-skills` — `gh api repos/eternityspring/shuohao-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；AI 短剧制作的 skill 集合：拆角色、排大纲、出场景与道具设定、写剧本、切分镜 &#124; Agent skills for AI short-drama production — character ｜ ⚠️缓存→现测：5046/2026-10-24/Apache-2.0 → 6148/2026-10-26T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=7

### 7.60 `story-short-write` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：短篇网文写作。辅助短篇小说创作，从构思到成稿，聚焦情绪拉扯与节奏把控。触发方式：/story-short-write、/写短篇、「帮我写一篇短篇」「写个盐言故事」。（desc_len=82；SKILL.md bytes=10913）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=6，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：[worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)（in_face=否）
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [zenstory-ai/drama-skills](https://github.com/zenstory-ai/drama-skills) | 3869 | 694 / 3 | 2026-11-06T17:39:19Z | MIT | 活跃(0d) | `active` | 20/25 (fc4 eff4 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；开源 AI 短剧/漫剧创作 skill 合集：剧本、角色资产、分镜 storyboard、图片/视频提示词、审查，适配 Claude … |
| 2 | [zenstory-ai/oh-story-claudecode](https://github.com/zenstory-ai/oh-story-claudecode) | 8359 | 1178 / 10 | 2026-11-06T18:01:03Z | MIT | 活跃(0d) | `active` | 19/25 (fc4 eff3 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Claude Code / Codex / OpenCode agent skills for writing Chinese web… |
| 3 | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | 55635 | 4230 / 40 | 2026-11-06T08:36:34Z | NOASSERTION | 活跃(1d) | `active` | 19/25 (fc3 eff5 compat1 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=5；Academic Research Skills for Claude Code: research → write → review … |
| 4 | [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | 12979 | 1506 / 19 | 2026-10-31T14:53:23Z | MIT | 活跃(6d) | `active` | 14/25 (fc2 eff1 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；A toolbox of film styles made in code for Claude Code: 59 ready to u… |
| 5 | [eternityspring/shuohao-skills](https://github.com/eternityspring/shuohao-skills) | 6148 | 864 / 2 | 2026-10-26T03:32:47Z | Apache-2.0 | 活跃(12d) | `active` | 14/25 (fc3 eff0 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；AI 短剧制作的 skill 集合：拆角色、排大纲、出场景与道具设定、写剧本、切分镜 &#124; Agent skills for A… |

**取值命令与匹配理由**
1. `zenstory-ai/drama-skills` — `gh api repos/zenstory-ai/drama-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；开源 AI 短剧/漫剧创作 skill 合集：剧本、角色资产、分镜 storyboard、图片/视频提示词、审查，适配 Claude Code 与 Codex &#124; Open-source AI sho ｜ ⚠️缓存→现测：3326/2026-10-20/MIT → 3869/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=12
2. `zenstory-ai/oh-story-claudecode` — `gh api repos/zenstory-ai/oh-story-claudecode --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Claude Code / Codex / OpenCode agent skills for writing Chinese web novels (网文): 扫榜、拆文、写作、去AI味、封面全流程 ｜ ⚠️缓存→现测：7971/2026-10-23/MIT → 8359/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=13
3. `Imbad0202/academic-research-skills` — `gh api repos/Imbad0202/academic-research-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=5；Academic Research Skills for Claude Code: research → write → review → revise → finalize ｜ ⚠️缓存→现测：54267/2026-10-28/NOASSERTION → 55635/2026-11-06T0…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=5
4. `lemomo-ai/lemo-opuscar` — `gh api repos/lemomo-ai/lemo-opuscar --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；A toolbox of film styles made in code for Claude Code: 59 ready to use, and your own. Each style is ｜ ⚠️缓存→现测：6782/2026-10-24/MIT → 12979/2026-10-31T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=2
5. `eternityspring/shuohao-skills` — `gh api repos/eternityspring/shuohao-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；AI 短剧制作的 skill 集合：拆角色、排大纲、出场景与道具设定、写剧本、切分镜 &#124; Agent skills for AI short-drama production — character ｜ ⚠️缓存→现测：5046/2026-10-24/Apache-2.0 → 6148/2026-10-26T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=7

### 7.61 `testing` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：编写和运行测试验证代码正确性 — 六阶段流程：目标识别、框架选择（pytest/jest/go test/JUnit）、定位与结构、编写（含 Property-based 与 Mutation testing）、运行与覆盖报告。Use when 用户说写测试/增加测试/测试覆盖或行为不稳（flaky）。不适用：完工前证据核验（走 verification-before-completion）。（desc_len=198；SKILL.md bytes=7946）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=11，trim=1） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | 117973 | 6860 / 69 | 2026-11-06T11:35:30Z | Apache-2.0 | 活跃(1d) | `active` | 23/25 (fc4 eff5 compat5 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=28；🪨 why use many token when few token do trick. Viral skill + proxy … |
| 2 | [career-ops-hq/career-ops](https://github.com/career-ops-hq/career-ops) | 80680 | 14848 / 416 | 2026-11-06T18:58:11Z | MIT | 活跃(0d) | `active` | 23/25 (fc4 eff5 compat5 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Open-source AI job search agent and job finder: scan job boards, sc… |
| 3 | [modelcontextprotocol/inspector](https://github.com/modelcontextprotocol/inspector) | 11248 | 1558 / 15 | 2026-11-05T23:07:44Z | NOASSERTION | 活跃(1d) | `active` | 22/25 (fc4 eff5 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；Visual testing tool for MCP servers |
| 4 | [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) | 24649 | 2139 / 169 | 2026-11-06T13:40:16Z | Apache-2.0 | 活跃(0d) | `active` | 22/25 (fc4 eff5 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=33；Security scanner for AI agent skills. Detect vulnerabilities, malic… |
| 5 | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | 27923 | 2313 / 11 | 2026-11-04T18:13:42Z | MIT | 活跃(2d) | `active` | 20/25 (fc4 eff3 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=18；Persistent file-based planning for AI coding agents and long-runnin… |

**取值命令与匹配理由**
1. `JuliusBrussee/caveman` — `gh api repos/JuliusBrussee/caveman --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=28；🪨 why use many token when few token do trick. Viral skill + proxy for coding agents that cuts 65% o ｜ ⚠️缓存→现测：114863/2026-10-25/Apache-2.0 → 117973/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=28
2. `career-ops-hq/career-ops` — `gh api repos/career-ops-hq/career-ops --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；Open-source AI job search agent and job finder: scan job boards, score each job 1-5 against your CV ｜ ⚠️缓存→现测：77073/2026-10-25/MIT → 80680/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=13
3. `modelcontextprotocol/inspector` — `gh api repos/modelcontextprotocol/inspector --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=12；Visual testing tool for MCP servers ｜ ⚠️缓存→现测：11143/2026-10-25/NOASSERTION → 11248/2026-11-05T2…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=12
4. `NVIDIA/SkillSpector` — `gh api repos/NVIDIA/SkillSpector --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=33；Security scanner for AI agent skills. Detect vulnerabilities, malicious patterns, security risks, pr ｜ ⚠️缓存→现测：21398/2026-10-23/Apache-2.0 → 24649/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=33
5. `OthmanAdi/planning-with-files` — `gh api repos/OthmanAdi/planning-with-files --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=18；Persistent file-based planning for AI coding agents and long-running tasks. Crash-proof markdown pla ｜ ⚠️缓存→现测：27631/2026-10-24/MIT → 27923/2026-11-04T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=18

### 7.62 `utf8-encoding-fix` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：修复中文 Windows 下 Write 工具写出 UTF-8 乱码：含概述、检测脚本与检测步骤、修复流程与修复步骤、以及验证步骤（改完必验，不靠肉眼）。Use when 刚写入的中文文件出现乱码/编码异常。不适用：shell 管道编码与 PowerShell BOM 问题（走 shell-encoding-pitfalls）。（desc_len=165；SKILL.md bytes=8341）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [OrchestratorInc/agent-orchestrator](https://github.com/OrchestratorInc/agent-orchestrator) | 14176 | 1934 / 906 | 2026-11-06T18:26:55Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc3 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Open-source (Apache-2.0) orchestrator for Claude Code, Codex & 30+ c… |
| 2 | [getsentry/MobileBuildMCP](https://github.com/getsentry/MobileBuildMCP) | 6546 | 329 / 36 | 2026-11-03T15:33:30Z | MIT | 活跃(3d) | `active` | 20/25 (fc4 eff5 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；A Model Context Protocol (MCP) server and CLI that provides tools f… |
| 3 | [Tencent/BrowserSkill](https://github.com/Tencent/BrowserSkill) | 10119 | 730 / 149 | 2026-11-06T12:18:10Z | MIT | 活跃(0d) | `active` | 19/25 (fc2 eff5 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Let AI agents use your real, logged-in browser without interrupting … |
| 4 | [browser-act/skills](https://github.com/browser-act/skills) | 6325 | 343 / 11 | 2026-11-04T10:27:29Z | MIT | 活跃(3d) | `active` | 18/25 (fc5 eff1 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=103；Browser automation CLI built for AI agents. Break through anti-bot… |
| 5 | [parcadei/Continuous-Claude-v3](https://github.com/parcadei/Continuous-Claude-v3) | 3948 | 303 / 47 | 2026-01-26T15:27:49Z | MIT | 一般(284d) | `active` | 18/25 (fc5 eff2 compat5 docs4 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=160；Context management for Claude Code. Hooks maintain state via ledge… |

**取值命令与匹配理由**
1. `OrchestratorInc/agent-orchestrator` — `gh api repos/OrchestratorInc/agent-orchestrator --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Open-source (Apache-2.0) orchestrator for Claude Code, Codex & 30+ coding agents. Plan, run and supe ｜ ⚠️缓存→现测：13596/2026-10-25/Apache-2.0 → 14176/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=7
2. `getsentry/MobileBuildMCP` — `gh api repos/getsentry/MobileBuildMCP --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=13；A Model Context Protocol (MCP) server and CLI that provides tools for agent use when working on iOS ｜ ⚠️缓存→现测：6506/2026-10-22/MIT → 6546/2026-11-03T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=13
3. `Tencent/BrowserSkill` — `gh api repos/Tencent/BrowserSkill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Let AI agents use your real, logged-in browser without interrupting your work. CLI + extension for b ｜ ⚠️缓存→现测：9516/2026-10-23/MIT → 10119/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=2
4. `browser-act/skills` — `gh api repos/browser-act/skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=103；Browser automation CLI built for AI agents. Break through anti-bot walls, hand off to humans across ｜ ⚠️缓存→现测：6273/2026-08-24/MIT → 6325/2026-11-04T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=103
5. `parcadei/Continuous-Claude-v3` — `gh api repos/parcadei/Continuous-Claude-v3 --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=160；Context management for Claude Code. Hooks maintain state via ledgers and handoffs. MCP execution wit ｜ ⚠️缓存→现测：3946/2026-01-26/MIT → 3948/2026-01-26T1…/MIT（stars 漂移） ｜ SKILL.md=160

### 7.63 `video-breakdown-skill` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：视频分镜拆解技能——把视频文件或 URL 拆成分镜（镜头）序列，产出 breakdown.json（时长/分辨率/分镜边界/关键帧/音频电平）。是 hook-analyzer-skill（前三秒钩子提取）与 report-generator-skill（分析报告生成）的共同上游。运行脚本 'python scripts/process_video.py "<video_path_or_url>" --json-out breakdown（desc_len=324；SKILL.md bytes=6892）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [ruvnet/RuView](https://github.com/ruvnet/RuView) | 102702 | 13322 / 550 | 2026-11-06T17:29:32Z | MIT | 活跃(0d) | `active` | 24/25 (fc4 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=54；π RuView turns commodity WiFi signals into real-time spatial intell… |
| 2 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | 17443 | 1658 / 11 | 2026-10-29T16:17:26Z | Apache-2.0 | 活跃(8d) | `active` | 16/25 (fc2 eff2 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；AI video skill for Claude Code & Codex — cinematic product videos wi… |
| 3 | [cclank/lanshu-awesome-ai-video-kit](https://github.com/cclank/lanshu-awesome-ai-video-kit) | 445 | 105 / 9 | 2026-10-07T03:31:17Z | MIT | 活跃(31d) | `active` | 14/25 (fc3 eff1 compat5 docs3 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；做企业 AI 视频项目逼出来的工具包 · 411 prompt · 15 模型 · 7 Claude Skill · 14 篇方法论 |
| 4 | [feicaiclub/video-spec-builder](https://github.com/feicaiclub/video-spec-builder) | 1072 | 126 / 3 | 2026-05-18T06:21:03Z | MIT | 一般(173d) | `active` | 12/25 (fc2 eff0 compat5 docs3 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；video-spec-builder —— 把我想做个视频逼成一份精确到秒的分镜脚本 video-spec.md,交给 HyperFra… |
| 5 | [sunxiayi/make-blender-education-video-skill](https://github.com/sunxiayi/make-blender-education-video-skill) | 67 | 13 / 0 | 2026-07-25T04:33:31Z | MIT | 一般(105d) | `active` | 11/25 (fc2 eff0 compat5 docs3 comm1) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A Codex and Claude Code skill for creating fact-checked cinematic ed… |

**取值命令与匹配理由**
1. `ruvnet/RuView` — `gh api repos/ruvnet/RuView --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=54；π RuView turns commodity WiFi signals into real-time spatial intelligence, vital sign monitoring, an ｜ ⚠️缓存→现测：99481/2026-10-25/MIT → 102702/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=54
2. `Vincentwei1021/video-shotcraft` — `gh api repos/Vincentwei1021/video-shotcraft --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；AI video skill for Claude Code & Codex — cinematic product videos with Remotion: 152 shot recipe car ｜ ⚠️缓存→现测：13468/2026-10-17/Apache-2.0 → 17443/2026-10-29T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=1
3. `cclank/lanshu-awesome-ai-video-kit` — `gh api repos/cclank/lanshu-awesome-ai-video-kit --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；做企业 AI 视频项目逼出来的工具包 · 411 prompt · 15 模型 · 7 Claude Skill · 14 篇方法论 ｜ ⚠️缓存→现测：429/2026-10-07/MIT → 445/2026-10-07T0…/MIT（stars 漂移） ｜ SKILL.md=7
4. `feicaiclub/video-spec-builder` — `gh api repos/feicaiclub/video-spec-builder --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；video-spec-builder —— 把我想做个视频逼成一份精确到秒的分镜脚本 video-spec.md,交给 HyperFrames 渲染。一条命令装到 Claude Code / Curs ｜ ⚠️缓存→现测：1042/2026-05-18/MIT → 1072/2026-05-18T0…/MIT（stars 漂移） ｜ SKILL.md=1
5. `sunxiayi/make-blender-education-video-skill` — `gh api repos/sunxiayi/make-blender-education-video-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A Codex and Claude Code skill for creating fact-checked cinematic educational videos with Blender ｜ ⚠️缓存→现测：60/2026-07-25/MIT → 67/2026-07-25T0…/MIT（stars 漂移） ｜ SKILL.md=1

### 7.64 `video-whisper-transcribe` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：用 ffmpeg + OpenAI Whisper 从视频提取音频并转录为文字。支持含特殊字符（中文引号等）的路径，输出 txt + json（含时间戳）。适用于字幕提取、词汇标注、视频内容分析等场景。（desc_len=101；SKILL.md bytes=5816）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | 17443 | 1658 / 11 | 2026-10-29T16:17:26Z | Apache-2.0 | 活跃(8d) | `active` | 16/25 (fc2 eff2 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；AI video skill for Claude Code & Codex — cinematic product videos wi… |
| 2 | [cclank/lanshu-awesome-ai-video-kit](https://github.com/cclank/lanshu-awesome-ai-video-kit) | 445 | 105 / 9 | 2026-10-07T03:31:17Z | MIT | 活跃(31d) | `active` | 14/25 (fc3 eff1 compat5 docs3 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；做企业 AI 视频项目逼出来的工具包 · 411 prompt · 15 模型 · 7 Claude Skill · 14 篇方法论 |
| 3 | [equalang/equalang-skill](https://github.com/equalang/equalang-skill) | 78 | 0 / 0 | 2026-11-03T07:35:58Z | Apache-2.0 | 活跃(4d) | `active` | 12/25 (fc2 eff1 compat5 docs3 comm1) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent Skill for Equalang: translate PDF, DOCX, PPTX, XLSX, EPUB, sub… |
| 4 | [feicaiclub/video-spec-builder](https://github.com/feicaiclub/video-spec-builder) | 1072 | 126 / 3 | 2026-05-18T06:21:03Z | MIT | 一般(173d) | `active` | 12/25 (fc2 eff0 compat5 docs3 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；video-spec-builder —— 把我想做个视频逼成一份精确到秒的分镜脚本 video-spec.md,交给 HyperFra… |
| 5 | [sunxiayi/make-blender-education-video-skill](https://github.com/sunxiayi/make-blender-education-video-skill) | 67 | 13 / 0 | 2026-07-25T04:33:31Z | MIT | 一般(105d) | `active` | 11/25 (fc2 eff0 compat5 docs3 comm1) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A Codex and Claude Code skill for creating fact-checked cinematic ed… |

**取值命令与匹配理由**
1. `Vincentwei1021/video-shotcraft` — `gh api repos/Vincentwei1021/video-shotcraft --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；AI video skill for Claude Code & Codex — cinematic product videos with Remotion: 152 shot recipe car ｜ ⚠️缓存→现测：13468/2026-10-17/Apache-2.0 → 17443/2026-10-29T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=1
2. `cclank/lanshu-awesome-ai-video-kit` — `gh api repos/cclank/lanshu-awesome-ai-video-kit --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；做企业 AI 视频项目逼出来的工具包 · 411 prompt · 15 模型 · 7 Claude Skill · 14 篇方法论 ｜ ⚠️缓存→现测：429/2026-10-07/MIT → 445/2026-10-07T0…/MIT（stars 漂移） ｜ SKILL.md=7
3. `equalang/equalang-skill` — `gh api repos/equalang/equalang-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent Skill for Equalang: translate PDF, DOCX, PPTX, XLSX, EPUB, subtitles, pictures, audio and vide ｜ ⚠️缓存→现测：39/2026-10-12/Apache-2.0 → 78/2026-11-03T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=1
4. `feicaiclub/video-spec-builder` — `gh api repos/feicaiclub/video-spec-builder --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；video-spec-builder —— 把我想做个视频逼成一份精确到秒的分镜脚本 video-spec.md,交给 HyperFrames 渲染。一条命令装到 Claude Code / Curs ｜ ⚠️缓存→现测：1042/2026-05-18/MIT → 1072/2026-05-18T0…/MIT（stars 漂移） ｜ SKILL.md=1
5. `sunxiayi/make-blender-education-video-skill` — `gh api repos/sunxiayi/make-blender-education-video-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；A Codex and Claude Code skill for creating fact-checked cinematic educational videos with Blender ｜ ⚠️缓存→现测：60/2026-07-25/MIT → 67/2026-07-25T0…/MIT（stars 漂移） ｜ SKILL.md=1

### 7.65 `vp-perspective-audit` ｜ HIGH ｜ 候选线索（元数据已实测，功能等价待复核）

- **功能边界**：副总视角审计——预判每个agent的行为模式，而不只是读它的配置文件。通过三层递进模型（信息层→决策层→行为层），构建每个agent的心智模型，预测它收到指令后的完整行为链：会怎么理解、怎么决策、怎么行动、在哪犯错。不是调度员视角（检查流程对不对），是管理者视角（预判每个员工的行为模式）。适用范围仅限于"需预判 agent 行为链"的诊断场景（见下方「何时不用本 skill」）。触发词：副总视角、员工思维、VP perspective、（desc_len=272；SKILL.md bytes=15307）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：FAMILY_ONLY（candidates_n=5，skill_relevant_n=1，trim=0） ｜ **语义缺口**：是 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：[affaan-m/ECC](https://github.com/affaan-m/ECC)、[morluto/rea](https://github.com/morluto/rea)、[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)、[obra/superpowers](https://github.com/obra/superpowers)（共 4 件，`not_replacement=true`）

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 56317 | 4957 / 80 | 2026-11-02T09:23:27Z | MIT | 活跃(5d) | `active` | 线索分 9.13 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=177；stars=56317；description=Turn any AI agent into an AI Scientist. The #1 Agent Skills librar… |
| 2 | [anbeime/skill](https://github.com/anbeime/skill) | 9249 | 821 / 35 | 2026-11-06T08:59:08Z | NOASSERTION | 活跃(1d) | `active` | 线索分 8.18 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [第一遍定向检索] SKILL.md=94；stars=9249；description=收录最全、更新最快的技能Skills商店：精选原创技能包（涵盖文档处理、内容创作、编程开发、机器学习、自动化工作流），全部打包好可… |
| 3 | [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) | 53590 | 5070 / 9 | 2026-10-30T13:21:07Z | MIT | 活跃(7d) | `active` | 线索分 6.07 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=0；stars=53590；description=The awesome collection of OpenClaw skills. 5,400+ skills filtered an… |
| 4 | [BehiSecc/awesome-claude-skills](https://github.com/BehiSecc/awesome-claude-skills) | 10361 | 1977 / 75 | 2026-11-02T12:16:33Z | NOASSERTION | 活跃(4d) | `active` | 线索分 5.21 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=0；stars=10361；description=A curated list of Claude Skills. |
| 5 | [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | 166920 | 27042 / 220 | 2026-11-06T01:58:56Z | MIT | 活跃(1d) | `active` | 线索分 5 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=0；stars=166920；description=A complete AI agency at your fingertips - From frontend wizards to … |

**取值命令与匹配理由**
1. `K-Dense-AI/scientific-agent-skills` — `gh api repos/K-Dense-AI/scientific-agent-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=177；stars=56317；description=Turn any AI agent into an AI Scientist. The #1 Agent Skills library for science, used by 250,000+ scientists worldwide. 177 ready-to-use val ｜ SKILL.md=177 ｜ `gh api repos/K-Dense-AI/scientific-agent-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
2. `anbeime/skill` — `gh api repos/anbeime/skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [第一遍定向检索] SKILL.md=94；stars=9249；description=收录最全、更新最快的技能Skills商店：精选原创技能包（涵盖文档处理、内容创作、编程开发、机器学习、自动化工作流），全部打包好可直接安装使用！同时自动抓取GitHub上万个Skills项目，按分类、更新时间、Star数量整理。The most comprehensive and ｜ SKILL.md=94 ｜ `gh api repos/anbeime/skill/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
3. `VoltAgent/awesome-openclaw-skills` — `gh api repos/VoltAgent/awesome-openclaw-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=0；stars=53590；description=The awesome collection of OpenClaw skills. 5,400+ skills filtered and categorized from the official OpenClaw Skills Registry.🦞 ｜ SKILL.md=0 ｜ `gh api repos/VoltAgent/awesome-openclaw-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核
4. `BehiSecc/awesome-claude-skills` — `gh api repos/BehiSecc/awesome-claude-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=0；stars=10361；description=A curated list of Claude Skills. ｜ SKILL.md=0 ｜ `gh api repos/BehiSecc/awesome-claude-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核
5. `msitarzewski/agency-agents` — `gh api repos/msitarzewski/agency-agents --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=0；stars=166920；description=A complete AI agency at your fingertips - From frontend wizards to Reddit community ninjas, from whimsy injectors to reality checkers. Each ｜ SKILL.md=0 ｜ `gh api repos/msitarzewski/agency-agents/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核

### 7.66 `wb-git-commit-recipe` ｜ HIGH ｜ 候选线索（元数据已实测，功能等价待复核）

- **功能边界**：WorkBuddy Bash 环境下 git commit 触发 pre-commit hook 链必失败的根因诊断与修复配方。典型症状为 FatalError: git failed. Is it installed...，pre-commit 日志内 Executable 'git' not found。当在 WB Bash 提交带 pre-commit 钩子的仓库失败、或 hook 链内子进程报 Executable not fo（desc_len=279；SKILL.md bytes=8919）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：FAMILY_ONLY（candidates_n=5，skill_relevant_n=1，trim=0） ｜ **语义缺口**：是 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：[ruvnet/ruflo](https://github.com/ruvnet/ruflo)、[K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)、[Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)、[agentscope-ai/QwenPaw](https://github.com/agentscope-ai/QwenPaw)（共 4 件，`not_replacement=true`）

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 113707 | 11885 / 130 | 2026-11-01T19:24:49Z | MIT | 活跃(5d) | `active` | 线索分 10 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=25；stars=113707；description=Production-grade engineering skills for AI coding agents. |
| 2 | [luongnv89/claude-howto](https://github.com/luongnv89/claude-howto) | 46662 | 5713 / 52 | 2026-11-03T09:18:42Z | MIT | 活跃(4d) | `active` | 线索分 6.93 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=37；stars=46662；description=A visual, example-driven guide to Claude Code — from basic concepts… |
| 3 | [prowler-cloud/prowler](https://github.com/prowler-cloud/prowler) | 15184 | 2485 / 460 | 2026-11-06T13:35:31Z | Apache-2.0 | 活跃(0d) | `active` | 线索分 6.3 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [第一遍定向检索] SKILL.md=39；stars=15184；description=This repo hosts Prowler OSS (CLI and Local Server). Prowler is t… |
| 4 | [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | 57399 | 4920 / 1164 | 2026-11-06T18:08:41Z | NOASSERTION | 活跃(0d) | `active` | 线索分 6.15 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=0；stars=57399；description=A hand-picked collection of the finest of resources for the most awe… |
| 5 | [Gentleman-Programming/gentleman-guardian-angel](https://github.com/Gentleman-Programming/gentleman-guardian-angel) | 1201 | 170 / 54 | 2026-07-08T08:13:58Z | MIT | 一般(122d) | `active` | 线索分 3.02 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=6；stars=1201；description=😇 Gentleman Guardian Angel (gga) - Provider-agnostic code review usi… |

**取值命令与匹配理由**
1. `addyosmani/agent-skills` — `gh api repos/addyosmani/agent-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=25；stars=113707；description=Production-grade engineering skills for AI coding agents. ｜ SKILL.md=25 ｜ `gh api repos/addyosmani/agent-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
2. `luongnv89/claude-howto` — `gh api repos/luongnv89/claude-howto --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=37；stars=46662；description=A visual, example-driven guide to Claude Code — from basic concepts to advanced agents, with copy-paste templates that bring immediate value ｜ SKILL.md=37 ｜ `gh api repos/luongnv89/claude-howto/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
3. `prowler-cloud/prowler` — `gh api repos/prowler-cloud/prowler --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [第一遍定向检索] SKILL.md=39；stars=15184；description=This repo hosts Prowler OSS (CLI and Local Server). Prowler is the world’s most widely used open-source cloud security platform that automat ｜ SKILL.md=39 ｜ `gh api repos/prowler-cloud/prowler/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
4. `hesreallyhim/awesome-claude-code` — `gh api repos/hesreallyhim/awesome-claude-code --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=0；stars=57399；description=A hand-picked collection of the finest of resources for the most awesome of agents, Claude Code, the undisputed champion of coding companion ｜ SKILL.md=0 ｜ `gh api repos/hesreallyhim/awesome-claude-code/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核
5. `Gentleman-Programming/gentleman-guardian-angel` — `gh api repos/Gentleman-Programming/gentleman-guardian-angel --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=6；stars=1201；description=😇 Gentleman Guardian Angel (gga) - Provider-agnostic code review using AI. Use Claude, Gemini, Codex, Ollama to enforce your coding standard ｜ SKILL.md=6 ｜ `gh api repos/Gentleman-Programming/gentleman-guardian-angel/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`

### 7.67 `wechat-automation` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：微信自动化（Windows wxauto v4 / macOS Accessibility API）：消息监听与提取、输入框控制、Agent 架构模式与安装配置。Use when 要监听微信消息、提取聊天内容或据此写自动化 Agent。不适用：微信语音转文字（走 wechat-voice-transcription）。（desc_len=160；SKILL.md bytes=20209）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=11，trim=1） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [siddsachar/row-bot](https://github.com/siddsachar/row-bot) | 1683 | 204 / 36 | 2026-11-06T18:36:12Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc4 eff5 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=50；Row-Bot - Personal AI Sovereignty. A local-first AI assistant with … |
| 2 | [zhayujie/CowAgent](https://github.com/zhayujie/CowAgent) | 47818 | 10417 / 42 | 2026-11-06T04:02:33Z | MIT | 活跃(1d) | `active` | 20/25 (fc3 eff5 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=3；Open-source personal AI assistant & Agent Harness. Plans tasks, runs… |
| 3 | [kangarooking/cangjie-skill](https://github.com/kangarooking/cangjie-skill) | 12282 | 1443 / 21 | 2026-10-02T03:17:52Z | MIT | 活跃(36d) | `active` | 20/25 (fc4 eff3 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=47；把书、长视频、播客等高价值内容蒸馏成可执行的 Agent Skills（Distill high-value content from… |
| 4 | [nexu-io/html-anything](https://github.com/nexu-io/html-anything) | 9441 | 904 / 65 | 2026-11-06T11:19:07Z | Apache-2.0 | 活跃(1d) | `active` | 18/25 (fc4 eff3 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=81；✨ The agentic HTML editor — your local AI agent writes the HTML, yo… |
| 5 | [googleworkspace/cli](https://github.com/googleworkspace/cli) | 32142 | 1986 / 139 | 2026-11-03T01:37:22Z | Apache-2.0 | 活跃(4d) | `active` | 18/25 (fc4 eff2 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=95；Google Workspace CLI — one command-line tool for Drive, Gmail, Cale… |

**取值命令与匹配理由**
1. `siddsachar/row-bot` — `gh api repos/siddsachar/row-bot --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=50；Row-Bot - Personal AI Sovereignty. A local-first AI assistant with integrated tools, a personal know ｜ ⚠️缓存→现测：1646/2026-10-24/Apache-2.0 → 1683/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=50
2. `zhayujie/CowAgent` — `gh api repos/zhayujie/CowAgent --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=3；Open-source personal AI assistant & Agent Harness. Plans tasks, runs tools and skills, self-evolves ｜ ⚠️缓存→现测：47566/2026-10-25/MIT → 47818/2026-11-06T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=3
3. `kangarooking/cangjie-skill` — `gh api repos/kangarooking/cangjie-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=47；把书、长视频、播客等高价值内容蒸馏成可执行的 Agent Skills（Distill high-value content from books, long-form videos, podcast ｜ ⚠️缓存→现测：11696/2026-10-02/MIT → 12282/2026-10-02T0…/MIT（stars 漂移） ｜ SKILL.md=47
4. `nexu-io/html-anything` — `gh api repos/nexu-io/html-anything --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=81；✨ The agentic HTML editor — your local AI agent writes the HTML, you ship it. 🚀 75 Skills × 9 Surfa ｜ ⚠️缓存→现测：9236/2026-10-13/Apache-2.0 → 9441/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=81
5. `googleworkspace/cli` — `gh api repos/googleworkspace/cli --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=95；Google Workspace CLI — one command-line tool for Drive, Gmail, Calendar, Sheets, Docs, Chat, Admin, ｜ ⚠️缓存→现测：31862/2026-10-06/Apache-2.0 → 32142/2026-11-03T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=95

### 7.68 `wechat-voice-transcription` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：微信语音 .silk 转文字：pilk 解码为裸 PCM → ffmpeg 补 WAV 头 → whisper 转写（必须用 Python312 并清 PYTHONPATH）。含一次性前置条件、一键脚本快速路径与脚本内部逻辑的手动步骤。Use when 拿到 .silk/微信语音要出文字。不适用：通用音频转录（走 local-asr / openai-whisper-api）。（desc_len=190；SKILL.md bytes=3508）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=11，trim=1） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [nexu-io/open-design](https://github.com/nexu-io/open-design) | 106289 | 12099 / 1371 | 2026-11-06T15:40:39Z | Apache-2.0 | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and o… |
| 2 | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | 80005 | 7372 / 238 | 2026-11-06T18:54:48Z | Apache-2.0 | 活跃(0d) | `active` | 23/25 (fc4 eff5 compat5 docs4 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=26；Write HTML. Render video. Built for agents. |
| 3 | [krillinai/OpenCreator](https://github.com/krillinai/OpenCreator) | 14189 | 1583 / 43 | 2026-11-05T23:26:51Z | Apache-2.0 | 活跃(1d) | `active` | 22/25 (fc4 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=15；Formerly KrillinAI, VideoTranslation and Dubbing Tool. Open-source … |
| 4 | [openclaw/Peekaboo](https://github.com/openclaw/Peekaboo) | 5444 | 417 / 7 | 2026-11-05T23:37:09Z | MIT | 活跃(1d) | `active` | 21/25 (fc3 eff5 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents… |
| 5 | [equalang/equalang-skill](https://github.com/equalang/equalang-skill) | 78 | 0 / 0 | 2026-11-03T07:35:58Z | Apache-2.0 | 活跃(4d) | `active` | 12/25 (fc2 eff1 compat5 docs3 comm1) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent Skill for Equalang: translate PDF, DOCX, PPTX, XLSX, EPUB, sub… |

**取值命令与匹配理由**
1. `nexu-io/open-design` — `gh api repos/nexu-io/open-design --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=553；The 1st Collaborative AI Design Agent Workspace. Local-first and open source. Create motion, prototy ｜ ⚠️缓存→现测：103811/2026-10-25/Apache-2.0 → 106289/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=553
2. `heygen-com/hyperframes` — `gh api repos/heygen-com/hyperframes --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=26；Write HTML. Render video. Built for agents. ｜ ⚠️缓存→现测：75789/2026-10-30/Apache-2.0 → 80005/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=26
3. `krillinai/OpenCreator` — `gh api repos/krillinai/OpenCreator --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=15；Formerly KrillinAI, VideoTranslation and Dubbing Tool. Open-source AI workspace for creators, powere ｜ ⚠️缓存→现测：13918/2026-10-25/Apache-2.0 → 14189/2026-11-05T2…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=15
4. `openclaw/Peekaboo` — `gh api repos/openclaw/Peekaboo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=4；Peekaboo is a macOS CLI & optional MCP server that enables AI agents to capture screenshots of appli ｜ ⚠️缓存→现测：5383/2026-10-24/MIT → 5444/2026-11-05T2…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=4
5. `equalang/equalang-skill` — `gh api repos/equalang/equalang-skill --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Agent Skill for Equalang: translate PDF, DOCX, PPTX, XLSX, EPUB, subtitles, pictures, audio and vide ｜ ⚠️缓存→现测：39/2026-10-12/Apache-2.0 → 78/2026-11-03T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.69 `win-toolchain-pitfalls` ｜ MID ｜ 逐件对应替代候选

- **功能边界**：本机（Windows + WorkBuddy + Git Bash）工具链陷阱速查与对策。当命令"静默无输出/exit code 恒 0/返回 0 结果/文件不存在/工具 command not found"，或需要跑 Python、uv、git、回收站删除、HTML→DOCX 时使用本表速查。每条都含实测证据与对照，避免把"工具环境问题"误判成"代码缺陷"。（desc_len=181；SKILL.md bytes=20776）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [genspark-ai/genoffice](https://github.com/genspark-ai/genoffice) | 11848 | 1640 / 59 | 2026-11-06T12:26:32Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc4 eff4 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Free, open-source AI Office suite: Docs, Sheets, Slides, PDF, Markd… |
| 2 | [evalstate/fast-agent](https://github.com/evalstate/fast-agent) | 3959 | 461 / 43 | 2026-11-06T06:48:19Z | Apache-2.0 | 活跃(1d) | `active` | 21/25 (fc3 eff5 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=3；Code, Build and Evaluate agents - excellent Model and Skills/MCP/ACP… |
| 3 | [Manavarya09/design-extract](https://github.com/Manavarya09/design-extract) | 4815 | 405 / 19 | 2026-11-05T08:50:20Z | MIT | 活跃(2d) | `active` | 20/25 (fc4 eff4 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=26；Extract any website's complete design system with one command. DTCG… |
| 4 | [apify/crawlee](https://github.com/apify/crawlee) | 26359 | 1748 / 126 | 2026-11-06T17:26:12Z | Apache-2.0 | 活跃(0d) | `active` | 17/25 (fc1 eff5 compat3 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；Crawlee—A web scraping and browser automation library for Node.js to… |
| 5 | [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) | 28889 | 3115 / 1 | 2026-11-04T03:28:47Z | MIT | 活跃(3d) | `active` | 15/25 (fc2 eff1 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Huashu Design 3.0 · 在 agent 里打一句话，拿回能交付的设计：网页 / App 原型 / 可编辑 PPTX / … |

**取值命令与匹配理由**
1. `genspark-ai/genoffice` — `gh api repos/genspark-ai/genoffice --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Free, open-source AI Office suite: Docs, Sheets, Slides, PDF, Markdown and HTML editors with a built ｜ ⚠️缓存→现测：10764/2026-10-24/Apache-2.0 → 11848/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=43
2. `evalstate/fast-agent` — `gh api repos/evalstate/fast-agent --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=3；Code, Build and Evaluate agents - excellent Model and Skills/MCP/ACP/A2A Support ｜ ⚠️缓存→现测：3947/2026-10-23/Apache-2.0 → 3959/2026-11-06T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=3
3. `Manavarya09/design-extract` — `gh api repos/Manavarya09/design-extract --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=26；Extract any website's complete design system with one command. DTCG tokens, semantic+primitive+compo ｜ ⚠️缓存→现测：4365/2026-10-23/MIT → 4815/2026-11-05T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=26
4. `apify/crawlee` — `gh api repos/apify/crawlee --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=1/5 compat=3/5；SKILL.md=0；Crawlee—A web scraping and browser automation library for Node.js to build reliable crawlers. In Jav ｜ ⚠️缓存→现测：26256/2026-10-23/Apache-2.0 → 26359/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=0
5. `alchaincyf/huashu-design` — `gh api repos/alchaincyf/huashu-design --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Huashu Design 3.0 · 在 agent 里打一句话，拿回能交付的设计：网页 / App 原型 / 可编辑 PPTX / 动画 / 信息图 · 六个候选挑三个方向 · 84 种带样张的风 ｜ ⚠️缓存→现测：26158/2026-10-23/MIT → 28889/2026-11-04T0…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.70 `windows-bash-cli-interop-pitfalls` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：Windows bash (Git Bash/MSYS2) 调用外部 CLI 或现代构建工具时的语法兼容坑合集。覆盖：bash extglob 吞 PowerShell $_ 变量、Vite 8 Rolldown 拒绝对象式 manualChunks 等。触发词：$_ 被吞、extglob、PowerShell 内联失败、manualChunks 报错、Rolldown、Vite 8 build 失败、bash 调 PowerShell（desc_len=260；SKILL.md bytes=7511）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [OrchestratorInc/agent-orchestrator](https://github.com/OrchestratorInc/agent-orchestrator) | 14176 | 1934 / 906 | 2026-11-06T18:26:55Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc3 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Open-source (Apache-2.0) orchestrator for Claude Code, Codex & 30+ c… |
| 2 | [parcadei/Continuous-Claude-v3](https://github.com/parcadei/Continuous-Claude-v3) | 3948 | 303 / 47 | 2026-01-26T15:27:49Z | MIT | 一般(284d) | `active` | 18/25 (fc5 eff2 compat5 docs4 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=160；Context management for Claude Code. Hooks maintain state via ledge… |
| 3 | [xpf0000/FlyEnv](https://github.com/xpf0000/FlyEnv) | 3342 | 392 / 39 | 2026-11-06T14:54:28Z | BSD-3-Clause | 活跃(0d) | `active` | 18/25 (fc2 eff3 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Native local development environment for Windows, macOS & Linux. A m… |
| 4 | [CursorTouch/Windows-MCP](https://github.com/CursorTouch/Windows-MCP) | 11186 | 1210 / 36 | 2026-11-06T16:35:28Z | MIT | 活跃(0d) | `active` | 17/25 (fc2 eff3 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；MCP Server for Computer Use in Windows |
| 5 | [sixtysevenlf/dsh-blender-plugin](https://github.com/sixtysevenlf/dsh-blender-plugin) | 1663 | 65 / 3 | 2026-11-06T07:45:04Z | BSD-3-Clause | 活跃(1d) | `active` | 16/25 (fc2 eff2 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；DSH × Blender 直连实时插件：15 个模型工具让 AI 驱动 GUI Blender；v2.5 活动状态置顶并可一键暂停 A… |

**取值命令与匹配理由**
1. `OrchestratorInc/agent-orchestrator` — `gh api repos/OrchestratorInc/agent-orchestrator --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Open-source (Apache-2.0) orchestrator for Claude Code, Codex & 30+ coding agents. Plan, run and supe ｜ ⚠️缓存→现测：13596/2026-10-25/Apache-2.0 → 14176/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=7
2. `parcadei/Continuous-Claude-v3` — `gh api repos/parcadei/Continuous-Claude-v3 --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=160；Context management for Claude Code. Hooks maintain state via ledgers and handoffs. MCP execution wit ｜ ⚠️缓存→现测：3946/2026-01-26/MIT → 3948/2026-01-26T1…/MIT（stars 漂移） ｜ SKILL.md=160
3. `xpf0000/FlyEnv` — `gh api repos/xpf0000/FlyEnv --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Native local development environment for Windows, macOS & Linux. A modern alternative to XAMPP, MAMP ｜ ⚠️缓存→现测：3309/2026-10-25/BSD-3-Clause → 3342/2026-11-06T1…/BSD-3-Clause（stars,pushed_at 漂移） ｜ SKILL.md=2
4. `CursorTouch/Windows-MCP` — `gh api repos/CursorTouch/Windows-MCP --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；MCP Server for Computer Use in Windows ｜ ⚠️缓存→现测：10260/2026-10-24/MIT → 11186/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1
5. `sixtysevenlf/dsh-blender-plugin` — `gh api repos/sixtysevenlf/dsh-blender-plugin --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；DSH × Blender 直连实时插件：15 个模型工具让 AI 驱动 GUI Blender；v2.5 活动状态置顶并可一键暂停 AI，原生选中/集合/子元素直送 DSH，随包建模 skill，支 ｜ ⚠️缓存→现测：1266/2026-10-25/BSD-3-Clause → 1663/2026-11-06T0…/BSD-3-Clause（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.71 `windows-cli-utf8-wrapper` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：Python subprocess 调用外部 CLI 工具的 UTF-8 安全包装。中文 Windows（CP936/GBK）下经 shell 管道或 subprocess 传含中文 prompt 会乱码、静默失败或输出为空；本件列出问题场景与反模式（PowerShell 管道直传、cmd echo 管道、subprocess 不带 encoding、PowerShell Out-File 重定向）及正确包装。不适用：Git Bash（desc_len=269；SKILL.md bytes=9562）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [OrchestratorInc/agent-orchestrator](https://github.com/OrchestratorInc/agent-orchestrator) | 14176 | 1934 / 906 | 2026-11-06T18:26:55Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc3 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Open-source (Apache-2.0) orchestrator for Claude Code, Codex & 30+ c… |
| 2 | [parcadei/Continuous-Claude-v3](https://github.com/parcadei/Continuous-Claude-v3) | 3948 | 303 / 47 | 2026-01-26T15:27:49Z | MIT | 一般(284d) | `active` | 18/25 (fc5 eff2 compat5 docs4 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=160；Context management for Claude Code. Hooks maintain state via ledge… |
| 3 | [xpf0000/FlyEnv](https://github.com/xpf0000/FlyEnv) | 3342 | 392 / 39 | 2026-11-06T14:54:28Z | BSD-3-Clause | 活跃(0d) | `active` | 18/25 (fc2 eff3 compat5 docs5 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Native local development environment for Windows, macOS & Linux. A m… |
| 4 | [CursorTouch/Windows-MCP](https://github.com/CursorTouch/Windows-MCP) | 11186 | 1210 / 36 | 2026-11-06T16:35:28Z | MIT | 活跃(0d) | `active` | 17/25 (fc2 eff3 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；MCP Server for Computer Use in Windows |
| 5 | [sixtysevenlf/dsh-blender-plugin](https://github.com/sixtysevenlf/dsh-blender-plugin) | 1663 | 65 / 3 | 2026-11-06T07:45:04Z | BSD-3-Clause | 活跃(1d) | `active` | 16/25 (fc2 eff2 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；DSH × Blender 直连实时插件：15 个模型工具让 AI 驱动 GUI Blender；v2.5 活动状态置顶并可一键暂停 A… |

**取值命令与匹配理由**
1. `OrchestratorInc/agent-orchestrator` — `gh api repos/OrchestratorInc/agent-orchestrator --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Open-source (Apache-2.0) orchestrator for Claude Code, Codex & 30+ coding agents. Plan, run and supe ｜ ⚠️缓存→现测：13596/2026-10-25/Apache-2.0 → 14176/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=7
2. `parcadei/Continuous-Claude-v3` — `gh api repos/parcadei/Continuous-Claude-v3 --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=160；Context management for Claude Code. Hooks maintain state via ledgers and handoffs. MCP execution wit ｜ ⚠️缓存→现测：3946/2026-01-26/MIT → 3948/2026-01-26T1…/MIT（stars 漂移） ｜ SKILL.md=160
3. `xpf0000/FlyEnv` — `gh api repos/xpf0000/FlyEnv --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=2；Native local development environment for Windows, macOS & Linux. A modern alternative to XAMPP, MAMP ｜ ⚠️缓存→现测：3309/2026-10-25/BSD-3-Clause → 3342/2026-11-06T1…/BSD-3-Clause（stars,pushed_at 漂移） ｜ SKILL.md=2
4. `CursorTouch/Windows-MCP` — `gh api repos/CursorTouch/Windows-MCP --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；MCP Server for Computer Use in Windows ｜ ⚠️缓存→现测：10260/2026-10-24/MIT → 11186/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1
5. `sixtysevenlf/dsh-blender-plugin` — `gh api repos/sixtysevenlf/dsh-blender-plugin --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；DSH × Blender 直连实时插件：15 个模型工具让 AI 驱动 GUI Blender；v2.5 活动状态置顶并可一键暂停 AI，原生选中/集合/子元素直送 DSH，随包建模 skill，支 ｜ ⚠️缓存→现测：1266/2026-10-25/BSD-3-Clause → 1663/2026-11-06T0…/BSD-3-Clause（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.72 `windows-gitbash-chinese-path-pit` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：Git Bash 调用 Node 系 CLI（openclaw/claude/gemini/codex 等 node launcher）传中文路径必失败的两种模式、根因与三步治本解法（先把目标文件 cp 到全 ASCII 路径、用 Windows 反斜杠传参、CLI 内部读写无需绕）。Use when 经 Git Bash 向 node CLI 传含中文路径参数。不适用：纯 Python subprocess 管道编码（走 window（desc_len=240；SKILL.md bytes=6068）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件
- **盲区 ❌未实测**：[tradecatlabs/vibe-coding-cn](https://github.com/tradecatlabs/vibe-coding-cn) → `gh: Not Found (HTTP 404)`；gh api 现测 404，❌未实测，不计入 ✅候选

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 113914 | 9885 / 125 | 2026-11-06T18:15:53Z | Apache-2.0 | 活跃(0d) | `active` | 24/25 (fc4 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Persistent Context Across Sessions for Every Agent –  Captures ever… |
| 2 | [cheaper-inference/OmniRoute](https://github.com/cheaper-inference/OmniRoute) | 85126 | 12829 / 611 | 2026-11-06T18:58:22Z | MIT | 活跃(0d) | `active` | 24/25 (fc4 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=53；Never stop coding. Free MIT AI gateway: one endpoint, 375 providers… |
| 3 | [iOfficeAI/AionUi](https://github.com/iOfficeAI/AionUi) | 34072 | 3560 / 886 | 2026-11-05T05:31:20Z | Apache-2.0 | 活跃(2d) | `active` | 22/25 (fc3 eff5 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；Open-source 24/7 Cowork app for OpenClaw, Hermes, Claude Code, Codex… |
| 4 | [OrchestratorInc/agent-orchestrator](https://github.com/OrchestratorInc/agent-orchestrator) | 14176 | 1934 / 906 | 2026-11-06T18:26:55Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc3 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Open-source (Apache-2.0) orchestrator for Claude Code, Codex & 30+ c… |

**取值命令与匹配理由**
1. `thedotmack/claude-mem` — `gh api repos/thedotmack/claude-mem --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=43；Persistent Context Across Sessions for Every Agent –  Captures everything your agent does during ses ｜ ⚠️缓存→现测：102894/2026-10-25/Apache-2.0 → 113914/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=43
2. `cheaper-inference/OmniRoute` — `gh api repos/cheaper-inference/OmniRoute --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=53；Never stop coding. Free MIT AI gateway: one endpoint, 375 providers (150+ free), 1,400+ models Kimi, ｜ ⚠️缓存→现测：80857/2026-10-25/MIT → 85126/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=53
3. `iOfficeAI/AionUi` — `gh api repos/iOfficeAI/AionUi --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；Open-source 24/7 Cowork app for OpenClaw, Hermes, Claude Code, Codex, OpenCode and 20+ more CLI Agen ｜ ⚠️缓存→现测：33752/2026-10-23/Apache-2.0 → 34072/2026-11-05T0…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=6
4. `OrchestratorInc/agent-orchestrator` — `gh api repos/OrchestratorInc/agent-orchestrator --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Open-source (Apache-2.0) orchestrator for Claude Code, Codex & 30+ coding agents. Plan, run and supe ｜ ⚠️缓存→现测：13596/2026-10-25/Apache-2.0 → 14176/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=7

### 7.73 `windows-native-ocr` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：Use when 需要 OCR 识图(中文/英文)：Windows 原生 OCR 引擎+零模型下载，装 ocr 命令。（desc_len=59；SKILL.md bytes=2722）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=5，trim=1） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [Portwood-Global-Solutions/Portwood](https://github.com/Portwood-Global-Solutions/Portwood) | 132 | 38 / 48 | 2026-11-05T18:06:57Z | Apache-2.0 | 活跃(1d) | `active` | 17/25 (fc3 eff2 compat5 docs5 comm2) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Free, native document generation for Salesforce. PDF, DOCX, XLSX, PP… |
| 2 | [Anionex/agent-vision-toolkit](https://github.com/Anionex/agent-vision-toolkit) | 1260 | 50 / 8 | 2026-10-13T09:12:47Z | MIT | 活跃(25d) | `active` | 16/25 (fc2 eff3 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；为纯文本模型"看图“设计更好的视觉工具箱和技能，支持多图理解，图片问答，前端UI还原、GUI 自动化等，并可选无缝接入多个主流agent… |
| 3 | [liustack/modlens](https://github.com/liustack/modlens) | 4815 | 151 / 4 | 2026-10-23T15:42:48Z | MIT | 活跃(14d) | `active` | 15/25 (fc2 eff1 compat5 docs4 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；The first vision plugin for DeepSeek Harness, and the vision bridge … |
| 4 | [A9T9/RPA](https://github.com/A9T9/RPA) | 2101 | 422 / 15 | 2026-11-04T08:03:08Z | NOASSERTION | 活跃(3d) | `active` | 9/25 (fc1 eff1 compat1 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=1/5 compat=1/5；SKILL.md=0；Browser and desktop automation with an MCP server for AI assistants.… |
| 5 | [TejasS1233/opencode-parser](https://github.com/TejasS1233/opencode-parser) | 71 | 4 / 1 | 2026-09-29T09:18:34Z | MIT | 活跃(39d) | `active` | 9/25 (fc0 eff2 compat3 docs3 comm1) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=0/5 compat=3/5；SKILL.md=0；Parse any file in opencode. Supports PDF, DOCX, XLSX, PPTX, images, … |

**取值命令与匹配理由**
1. `Portwood-Global-Solutions/Portwood` — `gh api repos/Portwood-Global-Solutions/Portwood --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=7；Free, native document generation for Salesforce. PDF, DOCX, XLSX, PPTX — merge tags, images, barcode ｜ ⚠️缓存→现测：129/2026-10-24/Apache-2.0 → 132/2026-11-05T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=7
2. `Anionex/agent-vision-toolkit` — `gh api repos/Anionex/agent-vision-toolkit --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；为纯文本模型"看图“设计更好的视觉工具箱和技能，支持多图理解，图片问答，前端UI还原、GUI 自动化等，并可选无缝接入多个主流agent，直接识别粘贴图片｜ A vision toolkit and ｜ ⚠️缓存→现测：1249/2026-10-13/MIT → 1260/2026-10-13T0…/MIT（stars 漂移） ｜ SKILL.md=1
3. `liustack/modlens` — `gh api repos/liustack/modlens --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；The first vision plugin for DeepSeek Harness, and the vision bridge for every text-only coding agent ｜ ⚠️缓存→现测：4446/2026-10-23/MIT → 4815/2026-10-23T1…/MIT（stars 漂移） ｜ SKILL.md=1
4. `A9T9/RPA` — `gh api repos/A9T9/RPA --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=1/5 compat=1/5；SKILL.md=0；Browser and desktop automation with an MCP server for AI assistants. Record macros or write JavaScri ｜ ⚠️缓存→现测：2088/2026-10-20/NOASSERTION → 2101/2026-11-04T0…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=0
5. `TejasS1233/opencode-parser` — `gh api repos/TejasS1233/opencode-parser --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=0/5 compat=3/5；SKILL.md=0；Parse any file in opencode. Supports PDF, DOCX, XLSX, PPTX, images, EPUB, HTML, Markdown, Jupyter, a ｜ ⚠️缓存→现测：65/2026-09-29/MIT → 71/2026-09-29T0…/MIT（stars 漂移） ｜ SKILL.md=0

### 7.74 `workbuddy-mcp` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：WorkBuddy MCP 连接器总控 — 腾讯文档/QQ邮箱/知识星球/轻流/ima/金山文档/WPS/kdocs/canva/mastergo/edgeone/云开发等连接器场景优先调用 mcp__workbuddy__* 工具；含前置自检与桥接故障恢复。（desc_len=130；SKILL.md bytes=4299）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=12，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [googleapis/mcp-toolbox](https://github.com/googleapis/mcp-toolbox) | 16818 | 1791 / 432 | 2026-11-06T17:02:51Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc3 eff4 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；MCP Toolbox for Databases is an open source MCP server for databases… |
| 2 | [agentscope-ai/QwenPaw](https://github.com/agentscope-ai/QwenPaw) | 37422 | 3264 / 1110 | 2026-11-06T10:39:00Z | Apache-2.0 | 活跃(1d) | `active` | 21/25 (fc4 eff5 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=49；Your Personal AI Assistant; easy to install, deploy on your own mac… |
| 3 | [t8y2/dbx](https://github.com/t8y2/dbx) | 29369 | 2677 / 1663 | 2026-11-06T18:21:57Z | Apache-2.0 | 活跃(0d) | `active` | 21/25 (fc2 eff5 compat5 docs5 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；25 MB lightweight cross-platform database client for 100+ databases,… |
| 4 | [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) | 35714 | 4350 / 68 | 2026-08-31T04:32:44Z | Apache-2.0 | 活跃(68d) | `active` | 19/25 (fc5 eff2 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=820；817 structured cybersecurity skills for AI agents · Mapped to 6 fr… |
| 5 | [vibheksoni/stealth-browser-mcp](https://github.com/vibheksoni/stealth-browser-mcp) | 3341 | 409 / 0 | 2026-11-05T18:35:03Z | MIT | 活跃(1d) | `active` | 15/25 (fc2 eff2 compat5 docs3 comm3) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Stealth browser automation for AI agents over MCP and the Chrome Dev… |

**取值命令与匹配理由**
1. `googleapis/mcp-toolbox` — `gh api repos/googleapis/mcp-toolbox --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；MCP Toolbox for Databases is an open source MCP server for databases. ｜ ⚠️缓存→现测：16718/2026-10-23/Apache-2.0 → 16818/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=6
2. `agentscope-ai/QwenPaw` — `gh api repos/agentscope-ai/QwenPaw --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=49；Your Personal AI Assistant; easy to install, deploy on your own machine or on the cloud; supports mu ｜ ⚠️缓存→现测：36092/2026-10-23/Apache-2.0 → 37422/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=49
3. `t8y2/dbx` — `gh api repos/t8y2/dbx --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；25 MB lightweight cross-platform database client for 100+ databases, including MySQL, PostgreSQL, SQ ｜ ⚠️缓存→现测：27699/2026-10-25/Apache-2.0 → 29369/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=1
4. `mukul975/Anthropic-Cybersecurity-Skills` — `gh api repos/mukul975/Anthropic-Cybersecurity-Skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=820；817 structured cybersecurity skills for AI agents · Mapped to 6 frameworks: MITRE ATT&CK, NIST CSF 2 ｜ ⚠️缓存→现测：34965/2026-08-31/Apache-2.0 → 35714/2026-08-31T0…/Apache-2.0（stars 漂移） ｜ SKILL.md=820
5. `vibheksoni/stealth-browser-mcp` — `gh api repos/vibheksoni/stealth-browser-mcp --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=2/5 compat=5/5；SKILL.md=1；Stealth browser automation for AI agents over MCP and the Chrome DevTools Protocol: navigation, netw ｜ ⚠️缓存→现测：3271/2026-10-24/MIT → 3341/2026-11-05T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=1

### 7.75 `workflow-preflight-check` ｜ HIGH ｜ 逐件对应替代候选

- **功能边界**：多agent工作流预执行验证 — 模拟所有步骤预检。工作流预检 多agent工作流预执行验证（preflight check）。在实际执行pipeline前，逐项检查执行链完整性： 文件/路径存在性、CLI工具可用性、skill可加载性、agent可达性、输出路径可写性， 输出结构化预检报告（GREEN/YELLOW/RED三级判定）。 适用于任何多步骤、多agent协作的工作流在执行前的"模拟一遍"验证。 触发词：预检、preflig（desc_len=277；SKILL.md bytes=11159）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：MATCHED（candidates_n=5，skill_relevant_n=10，trim=0） ｜ **语义缺口**：否 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：0 件

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 81071 | 9543 / 654 | 2026-11-06T18:31:29Z | MIT | 活跃(0d) | `active` | 25/25 (fc5 eff5 compat5 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swa… |
| 2 | [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) | 24649 | 2139 / 169 | 2026-11-06T13:40:16Z | Apache-2.0 | 活跃(0d) | `active` | 22/25 (fc4 eff5 compat5 docs4 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=33；Security scanner for AI agent skills. Detect vulnerabilities, malic… |
| 3 | [activepieces/activepieces](https://github.com/activepieces/activepieces) | 25400 | 4442 / 859 | 2026-11-06T18:33:14Z | NOASSERTION | 活跃(0d) | `active` | 21/25 (fc4 eff5 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=17；AI Agents & MCPs & AI Workflow Automation • (~400 MCP servers for A… |
| 4 | [eigent-ai/eigent](https://github.com/eigent-ai/eigent) | 15755 | 1887 / 261 | 2026-11-05T17:55:26Z | Apache-2.0 | 活跃(1d) | `active` | 20/25 (fc3 eff5 compat5 docs3 comm4) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；Eigent: The Open Source Cowork Desktop - Local and Free Alternative … |
| 5 | [langgenius/dify](https://github.com/langgenius/dify) | 160565 | 25406 / 1205 | 2026-11-06T18:33:42Z | NOASSERTION | 活跃(0d) | `active` | 19/25 (fc3 eff5 compat1 docs5 comm5) | ✅已实测（GitHub 元数据） | rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=7；Build Agentic workflows, RAG pipelines, with rich AI model and tool … |

**取值命令与匹配理由**
1. `ruvnet/ruflo` — `gh api repos/ruvnet/ruflo --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=5/5 compat=5/5；SKILL.md=389；🌊 The original agent harness. Deploy intelligent multi-player swarms, coordinate autonomous workflo ｜ ⚠️缓存→现测：79103/2026-10-25/MIT → 81071/2026-11-06T1…/MIT（stars,pushed_at 漂移） ｜ SKILL.md=389
2. `NVIDIA/SkillSpector` — `gh api repos/NVIDIA/SkillSpector --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=33；Security scanner for AI agent skills. Detect vulnerabilities, malicious patterns, security risks, pr ｜ ⚠️缓存→现测：21398/2026-10-23/Apache-2.0 → 24649/2026-11-06T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=33
3. `activepieces/activepieces` — `gh api repos/activepieces/activepieces --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=4/5 compat=5/5；SKILL.md=17；AI Agents & MCPs & AI Workflow Automation • (~400 MCP servers for AI agents) • AI Automation / AI Ag ｜ ⚠️缓存→现测：25210/2026-10-25/NOASSERTION → 25400/2026-11-06T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=17
4. `eigent-ai/eigent` — `gh api repos/eigent-ai/eigent --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=5/5；SKILL.md=6；Eigent: The Open Source Cowork Desktop - Local and Free Alternative to Claude Cowork and Codex ｜ ⚠️缓存→现测：15654/2026-10-24/Apache-2.0 → 15755/2026-11-05T1…/Apache-2.0（stars,pushed_at 漂移） ｜ SKILL.md=6
5. `langgenius/dify` — `gh api repos/langgenius/dify --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据） @2026-11-06T19:07:01.413113+00:00 ｜ rel=skill；五维 fc=3/5 compat=1/5；SKILL.md=7；Build Agentic workflows, RAG pipelines, with rich AI model and tool support on one collaborative wor ｜ ⚠️缓存→现测：159795/2026-10-28/NOASSERTION → 160565/2026-11-06T1…/NOASSERTION（stars,pushed_at 漂移） ｜ SKILL.md=7

### 7.76 `wps-knowledgebase` ｜ HIGH ｜ 候选线索（元数据已实测，功能等价待复核）

- **功能边界**：WPS/zhishi（WPS知识库）云端知识库：列表/详情、文件树、智能问答（ask SSE）、分享链接、创建关闭与文件 CRUD、导入上传与格式转换（OTL 下载限制见正文）。 当用户用中文只说「知识库」「我的知识库」「在知识库里查/搜/问」「从知识库找答案」「知识库问答」「zhishi」「kwiki」或英文 knowledge base / ask，且意图是云端 Skills Hub 里的内容而非仅搜索本地仓库文件时，必须使用本 s（desc_len=313；SKILL.md bytes=21475）
- **缺陷面**：已记录 ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：NO_OS_CANDIDATE（candidates_n=5，skill_relevant_n=0，trim=0） ｜ **语义缺口**：是 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：[ruvnet/ruflo](https://github.com/ruvnet/ruflo)、[K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)、[Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)、[agentscope-ai/QwenPaw](https://github.com/agentscope-ai/QwenPaw)、[alibaba/open-code-review](https://github.com/alibaba/open-code-review)（共 5 件，`not_replacement=true`）

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [daymade/claude-code-skills](https://github.com/daymade/claude-code-skills) | 1517 | 232 / 0 | 2026-11-06T19:35:29Z | MIT | 活跃(0d) | `active` | 线索分 8.03 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=121；stars=1517；description=Professional Claude Code skills marketplace featuring production-re… |
| 2 | [sundial-org/awesome-openclaw-skills](https://github.com/sundial-org/awesome-openclaw-skills) | 674 | 100 / 50 | 2026-03-07T06:57:19Z | NOASSERTION | 一般(245d) | `active` | 线索分 7.01 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=948；stars=674；description=Top OpenClaw skills, with the most popular and useful ones. |
| 3 | [zackchewa/awesome-china-mcp](https://github.com/zackchewa/awesome-china-mcp) | 158 | 23 / 0 | 2026-11-06T01:58:41Z | CC0-1.0 | 活跃(1d) | `active` | 线索分 3 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=0；stars=158；description=Curated index of MCP servers for Chinese apps — connect your AI agent … |
| 4 | [alvinreal/awesome-opensource-ai](https://github.com/alvinreal/awesome-opensource-ai) | 4993 | 760 / 40 | 2026-11-06T08:34:53Z | CC0-1.0 | 活跃(1d) | `active` | 线索分 1.1 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [第一遍定向检索] SKILL.md=0；stars=4993；description=Curated list of the best truly open-source AI projects, models, to… |
| 5 | [aymericdamien/TopDeepLearning](https://github.com/aymericdamien/TopDeepLearning) | 6417 | 1261 / 21 | 2026-07-15T02:19:53Z | MIT | 一般(115d) | `active` | 线索分 0.13 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [第一遍定向检索] SKILL.md=0；stars=6417；description=A list of popular github projects related to deep learning |

**取值命令与匹配理由**
1. `daymade/claude-code-skills` — `gh api repos/daymade/claude-code-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=121；stars=1517；description=Professional Claude Code skills marketplace featuring production-ready skills for enhanced development workflows. ｜ SKILL.md=121 ｜ `gh api repos/daymade/claude-code-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
2. `sundial-org/awesome-openclaw-skills` — `gh api repos/sundial-org/awesome-openclaw-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=948；stars=674；description=Top OpenClaw skills, with the most popular and useful ones. ｜ SKILL.md=948 ｜ `gh api repos/sundial-org/awesome-openclaw-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
3. `zackchewa/awesome-china-mcp` — `gh api repos/zackchewa/awesome-china-mcp --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=0；stars=158；description=Curated index of MCP servers for Chinese apps — connect your AI agent to 高德地图, 12306, 小红书, 飞书, 语雀, A股 and more. The open-source 'Composio fo ｜ SKILL.md=0 ｜ `gh api repos/zackchewa/awesome-china-mcp/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核
4. `alvinreal/awesome-opensource-ai` — `gh api repos/alvinreal/awesome-opensource-ai --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [第一遍定向检索] SKILL.md=0；stars=4993；description=Curated list of the best truly open-source AI projects, models, tools, and infrastructure. Daily updated. ｜ SKILL.md=0 ｜ `gh api repos/alvinreal/awesome-opensource-ai/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核
5. `aymericdamien/TopDeepLearning` — `gh api repos/aymericdamien/TopDeepLearning --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [第一遍定向检索] SKILL.md=0；stars=6417；description=A list of popular github projects related to deep learning ｜ SKILL.md=0 ｜ `gh api repos/aymericdamien/TopDeepLearning/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核

### 7.77 `天眼一下` ｜ MID ｜ 候选线索（元数据已实测，功能等价待复核）

- **功能边界**：使用本地 'tyc' 命令查询天眼查企业数据。适用于企业主体核验、合作方/客户/供应商风险评估、股东和实控人分析、受益所有人、关联关系路径、司法诉讼、执行失信、行政处罚、经营真实性、招投标、资质许可、知识产权、董监高、历史沿革、行业企业发现，以及生成简短商查摘要。查询前使用 'tyc login' 完成 OAuth 鉴权。（desc_len=162；SKILL.md bytes=10371）
- **缺陷面**：未记录（≠零缺陷） ｜ **使用反馈**：⚠️部分实测（outcome_unknown 99.94%）
- **r114**：FAMILY_ONLY（candidates_n=5，skill_relevant_n=2，trim=0） ｜ **语义缺口**：是 ｜ **声明上游**：无
- **族级补位（禁当替代引用）**：[affaan-m/ECC](https://github.com/affaan-m/ECC)、[morluto/rea](https://github.com/morluto/rea)、[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)（共 3 件，`not_replacement=true`）

| # | 候选仓 | stars | forks / issues | 最近 push | license | 活跃度 | 维护 | 评分 | 取证 | 匹配理由（截断） |
|---:|---|---:|---:|---|---|---|---|---:|---|---|
| 1 | [7onez/cti-expert](https://github.com/7onez/cti-expert) | 622 | 90 / 3 | 2026-10-22T06:44:50Z | NOASSERTION | 活跃(16d) | `active` | 线索分 8.01 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=1；stars=622；description=CTI Expert — Cyber Threat Intelligence & OSINT analysis skill for Clau… |
| 2 | [freestylefly/canghe-skills](https://github.com/freestylefly/canghe-skills) | 475 | 103 / 3 | 2026-06-08T09:57:52Z | NOASSERTION | 一般(152d) | `active` | 线索分 7.01 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=31；stars=475；description=苍何的技能skills仓库，搜集好用的 skills，辅助提效 |
| 3 | [Demogorgon314/kimi-datasource](https://github.com/Demogorgon314/kimi-datasource) | 0 | 0 / 0 | 2026-10-19T04:55:05Z | MIT | 活跃(19d) | `active` | 线索分 6 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=1；stars=0；description=Standalone **CLI** for the structured **Kimi Data Sources included with … |
| 4 | [zackchewa/awesome-china-mcp](https://github.com/zackchewa/awesome-china-mcp) | 158 | 23 / 0 | 2026-11-06T01:58:41Z | CC0-1.0 | 活跃(1d) | `active` | 线索分 3 | ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） | [精选种子] SKILL.md=0；stars=158；description=Curated index of MCP servers for Chinese apps — connect your AI agent … |

**取值命令与匹配理由**
1. `7onez/cti-expert` — `gh api repos/7onez/cti-expert --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=1；stars=622；description=CTI Expert — Cyber Threat Intelligence & OSINT analysis skill for Claude Code / Codex. 120+ commands, 57 techniques, 79 typed MCP tools, det ｜ SKILL.md=1 ｜ `gh api repos/7onez/cti-expert/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
2. `freestylefly/canghe-skills` — `gh api repos/freestylefly/canghe-skills --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=31；stars=475；description=苍何的技能skills仓库，搜集好用的 skills，辅助提效 ｜ SKILL.md=31 ｜ `gh api repos/freestylefly/canghe-skills/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
3. `Demogorgon314/kimi-datasource` — `gh api repos/Demogorgon314/kimi-datasource --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=1；stars=0；description=Standalone **CLI** for the structured **Kimi Data Sources included with your existing Kimi subscription** ｜ SKILL.md=1 ｜ `gh api repos/Demogorgon314/kimi-datasource/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测`
4. `zackchewa/awesome-china-mcp` — `gh api repos/zackchewa/awesome-china-mcp --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'` ｜ ✅已实测（GitHub 元数据）/ ❌未实测（功能等价性） @2026-11-06T19:55:08.981142+00:00 ｜ [精选种子] SKILL.md=0；stars=158；description=Curated index of MCP servers for Chinese apps — connect your AI agent to 高德地图, 12306, 小红书, 飞书, 语雀, A股 and more. The open-source 'Composio fo ｜ SKILL.md=0 ｜ `gh api repos/zackchewa/awesome-china-mcp/git/trees/HEAD?recursive=1`（tree `OK`） ｜ 功能等价性 `❌未实测` ｜ SKILL.md=0：目录/清单型仓库，非逐件 skill 仓，需功能复核

---

## 8 C 面：r18 对标对象与社区/控制仓现测元数据

> R241 **校正注**：brief 写「12 个对标对象」，`自建skill优化/06-benchmark/全量对标报告_r18_2026-09-24.md:36-64` 实列 **14** 个（O1–O8 + N-A–N-F）；此处只加校正注，**不改写旧报告任何旧数字**。另 `自建skill优化/06-benchmark/comparison.md:128-129` 曾把 owner 写成 `mycelium/ai-brain-starter`，真实全名为 `mycelium-hq/ai-brain-starter`；`comparison.md:5-8` 已声明常驻页刻意不列 star 数，需数字时用 `gh api repos/<owner>/<repo> --jq '"\(.stargazers_count)|\(.pushed_at)"'`。

| # | 角色 | 仓 | stars | forks / issues | pushed_at | license | archived | 取值命令 |
|---:|---|---|---:|---:|---|---|---|---|
| 1 | r18 对标对象 #1 | [obra/superpowers](https://github.com/obra/superpowers) | 313505 | 27892 / 340 | 2026-11-03T23:24:58Z | MIT | 否 | `gh api repos/obra/superpowers --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 2 | r18 对标对象 #2 | [anthropics/skills](https://github.com/anthropics/skills) | 188110 | 22189 / 1484 | 2026-10-28T19:20:39Z | NOASSERTION | 否 | `gh api repos/anthropics/skills --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 3 | r18 对标对象 #3 | [github/spec-kit](https://github.com/github/spec-kit) | 148147 | 13307 / 198 | 2026-11-06T19:09:39Z | MIT | 否 | `gh api repos/github/spec-kit --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 4 | r18 对标对象 #4 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 81071 | 9543 / 654 | 2026-11-06T18:31:29Z | MIT | 否 | `gh api repos/ruvnet/ruflo --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 5 | r18 对标对象 #5 | [mem0ai/mem0](https://github.com/mem0ai/mem0) | 68527 | 8143 / 920 | 2026-11-06T16:53:07Z | Apache-2.0 | 否 | `gh api repos/mem0ai/mem0 --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 6 | r18 对标对象 #6 | [letta-ai/letta](https://github.com/letta-ai/letta) | 25369 | 2670 / 0 | 2026-10-18T22:28:04Z | Apache-2.0 | 否 | `gh api repos/letta-ai/letta --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 7 | r18 对标对象 #7 | [GreatScottyMac/roo-code-memory-bank](https://github.com/GreatScottyMac/roo-code-memory-bank) | 1669 | 182 / 11 | 2025-05-15T16:26:44Z | Apache-2.0 | 否 | `gh api repos/GreatScottyMac/roo-code-memory-bank --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 8 | r18 对标对象 #8 | [GreatScottyMac/context-portal](https://github.com/GreatScottyMac/context-portal) | 768 | 77 / 24 | 2026-01-27T00:06:16Z | Apache-2.0 | 否 | `gh api repos/GreatScottyMac/context-portal --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 9 | r18 对标对象 #9 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 113697 | 11885 / 130 | 2026-11-01T19:24:49Z | MIT | 否 | `gh api repos/addyosmani/agent-skills --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 10 | r18 对标对象 #10 | [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | 74158 | 5092 / 199 | 2026-11-06T18:06:55Z | MIT | 否 | `gh api repos/Fission-AI/OpenSpec --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 11 | r18 对标对象 #11 | [sickn33/agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills) | 49277 | 7151 / 7 | 2026-11-06T17:55:43Z | MIT | 否 | `gh api repos/sickn33/agentic-awesome-skills --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 12 | r18 对标对象 #12 | [vercel-labs/skills](https://github.com/vercel-labs/skills) | 38365 | 3341 / 802 | 2026-11-06T02:37:48Z | MIT | 否 | `gh api repos/vercel-labs/skills --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 13 | r18 对标对象 #13 | [mycelium-hq/ai-brain-starter](https://github.com/mycelium-hq/ai-brain-starter) | 50 | 42 / 54 | 2026-11-06T13:01:56Z | MIT | 否 | `gh api repos/mycelium-hq/ai-brain-starter --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 14 | r18 对标对象 #14 | [lucasrosati/claude-code-memory-setup](https://github.com/lucasrosati/claude-code-memory-setup) | 1059 | 94 / 5 | 2026-10-21T04:30:45Z | MIT | 否 | `gh api repos/lucasrosati/claude-code-memory-setup --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 15 | 停摆负控 | [trimstray/test-your-sysadmin-skills](https://github.com/trimstray/test-your-sysadmin-skills) | 11898 | 1737 / 20 | 2024-11-19T14:07:11Z | MIT | 否 | `gh api repos/trimstray/test-your-sysadmin-skills --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 16 | 停摆负控 | [PanJiaChen/vue-element-admin](https://github.com/PanJiaChen/vue-element-admin) | 90115 | 30216 / 1399 | 2024-10-24T11:25:46Z | MIT | 否 | `gh api repos/PanJiaChen/vue-element-admin --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 17 | archived 负控 | [PleasePrompto/notebooklm-skill](https://github.com/PleasePrompto/notebooklm-skill) | 7784 | 907 / 0 | 2026-09-10T07:43:47Z | MIT | 是 | `gh api repos/PleasePrompto/notebooklm-skill --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 18 | 社区线索 | [miketepUR/awesome-claude-skills](https://github.com/miketepUR/awesome-claude-skills) | 0 | 0 / 0 | 2026-10-02T18:06:38Z | MIT | 否 | `gh api repos/miketepUR/awesome-claude-skills --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 19 | 社区线索 | [Chat2AnyLLM/awesome-claude-skills](https://github.com/Chat2AnyLLM/awesome-claude-skills) | 153 | 42 / 6 | 2026-11-06T16:26:48Z | NOASSERTION | 否 | `gh api repos/Chat2AnyLLM/awesome-claude-skills --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |
| 20 | 社区线索 | [ranbot-ai/awesome-skills](https://github.com/ranbot-ai/awesome-skills) | 8 | 6 / 8 | 2026-11-06T14:14:44Z | NOASSERTION | 否 | `gh api repos/ranbot-ai/awesome-skills --jq '[.full_name,.stargazers_count,.pushed_at,(.license.spdx_id // "NOASSERTION"),.archived,(.description // "")]'` |

- 14 个对标对象 pushed_at 范围 2025-05-15 … 2026-11-06，`archived=false`；其中 `GreatScottyMac/roo-code-memory-bank`（2025-05-15）与 `GreatScottyMac/context-portal`（2026-01-27）在本轮 365 天阈值（2025-11-07）下分别为 **停摆** 与 **active**，按 r113 规则前者不得进入新候选面，此处仅作 r18 历史对象的现测校正注。
- 6 个控制/社区仓均带本轮 `gh api` 取值命令；社区线索（[skills.sh](https://www.skills.sh/) / Awesome 列表）只作线索面，**未安装任何 skill**。

---

## 9 盲区、退路与红线

| 项 | 登记 |
|---|---|
| 取证受阻 | `tradecatlabs/vibe-coding-cn` → `gh: Not Found (HTTP 404)`，仅影响 `windows-gitbash-chinese-path-pit` 的 1 个候选出现位，标 ❌未实测并排除出 ✅候选；该 skill 仍有 4 条现测候选，满足 3–5。 |
| 退路 | GitHub API 限流/不可达时复用 `python 05-exec/r114_replacement_scan.py --offline --json _temp/...` 缓存面（缓存出处 `06-benchmark/pool_cache_r217.json` + 432 个 loose 文件，`pack_generated_at=2026-10-25`），并具名登记盲区，**禁静默丢弃**。 |
| 功能等价性 | B 面 11 件 / 54 条为线索面，❌未实测；不得据此直接执行替换，交需求 3 五维矩阵 + 需求 4 迁移验证。 |
| 许可证 | `NOASSERTION` 需逐件看 LICENSE 正文；r114 五维 score 的 `compat` 已做 license cap，但缓存快照标 ⚠️部分实测。 |
| 写面 | 仅 `02_replacement_candidates.md`、`data/candidates.json`、`02_candidates_check.py`；未写他人编号文件；批量实测/中间产物只落 `自建skill优化/_temp/`。 |
| 受管源 | 未改 `D:/global_skills` 任何 `SKILL.md`；真实全量替换列入迁移计划分阶段节点，改受管源须走 `rule_editor.py` + 双硬前提。 |
| 历史 | 未改写 `06-benchmark/全量对标报告_r*.md` 旧数字；未使用可能由他人在途生成的 `06-benchmark/replacement_matrix_shadowstrict.json`。 |

---

## 10 复算入口（附录）

```bash
# 覆盖判据（正常态 + 负控）
cd "自建skill优化" && PYTHONPYCACHEPREFIX=_temp/pycache_t2 "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" deliverables/skill-modernization-r1/02_candidates_check.py
cd "自建skill优化" && PYTHONPYCACHEPREFIX=_temp/pycache_t2 "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" deliverables/skill-modernization-r1/02_candidates_check.py --negative-control

# 三条自证
cd "自建skill优化" && PYTHONPYCACHEPREFIX=_temp/pycache_t2 "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" 05-exec/r114_replacement_scan.py --offline --json _temp/r114_t2_verify.json
cd "自建skill优化" && for r in anthropics/skills obra/superpowers rlaope/oh-my-hermes; do gh api repos/$r --jq '[.full_name,.stargazers_count,.pushed_at,.license.spdx_id,.archived,.description]'; done
cd "自建skill优化" && PYTHONPYCACHEPREFIX=_temp/pycache_t2 "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" 05-exec/run_gates.py --json _temp/t2_gate_run.json --no-ledger --timeout 300

# 单仓现场复算（把 {OWNER}/{REPO} 换成表内任一 repo）
gh api repos/{OWNER}/{REPO} --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'
```

> 本文由 `data/candidates.json` 渲染；两件若不一致，以机器可读母本 + `02_candidates_check.py` 复跑结果为准。
