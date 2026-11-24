# 05 · 长效季度巡检机制（需求 5）

> 任务：t5（inspection-engineer / attempt ef4aaf73-d974-471e-9f8b-8a786d639794）
> 目标：每季度对仓库内所有依赖的开源 skill 做一次版本与替代方案扫描，及时发现更优开源替代；复用已有资产，禁重复造轮子。
> 写面：自建skill优化/deliverables/skill-modernization-r1/05_inspection_regime.md（t5 独占编号）；配套清单 = 自建skill优化/deliverables/skill-modernization-r1/data/quarterly_check.md。
> 纪律：阶段 0-3 只读取证，不改 D:/global_skills 下任何 SKILL.md/源文件；镜像 _my-skills 与 .agents/skills 只读；eval/ 焚诀只读件不改；R241 历史数字只加校正注；本轮 workflow diff = 空（不新增/修订 .github/workflows/，理由见 §3 与 §4）。
> 读数纪律：所有数字附取值命令或句柄，禁硬编码「当前值」；结论逐条标 ✅已实测 / ⚠️部分实测 / ❌未实测。

## 0. 结论摘要

- ✅已实测：现状三面（CI 节律 / 一键脚本 / 替代扫描）全部在役，逐条取值命令见 §1 与配套清单 A。
- ✅已实测：三态节律门（PASS / FAIL / UNVERIFIED）+ 伪造「已超龄」负控报红（rc=1），判据有牙，见 §5。
- ✅已实测：一键脚本 r113 离线预览按设计降级（rc=2，主产物未覆写、留痕 audit.error.json、tracked side-write 三件 sha 不变）；替代面 r114 离线退路守恒通过。
- ⚠️部分实测：run_gates 全量 118 门 verdict=FAIL（FAIL=7 UNVERIFIED=4）、portable 55 门 FAIL=5 —— 如实记红，不删 tracked 件凑绿（R263/X-9）；其中 gate_run_freshness 属设计内红。
- ⚠️部分实测：独立第二意见缺席 —— 3 条 subagent 委派全被 AgentTeams member delegation limit (0) 拒，属设计边界，本机串行复核代替，见 §6。
- ❌未实测：r276 dryrun 里 I2/I3 的新增脚本与 JSON 在盘上不存在，其「可运行」腿无证据，按 X-29 不推荐本轮落地。

## 1. 现状盘点（三面逐条现读确认在役）

### 1.1 CI 节律看门狗

| 面 | 现读位置 | 取值命令 | 在役证据 |
|---|---|---|---|
| 季度 cron | 自建skill优化/.github/workflows/quarterly_audit.yml:34 | `grep -n "cron:" .github/workflows/quarterly_audit.yml` | `cron: "0 22 1 1,4,7,10 *"`（每季度首日 06:00 UTC+8；只限 dom=1 与月份，不写 dow） |
| workflow_dispatch / permissions / runner | 同文件:35-42 | `git show HEAD:.github/workflows/quarterly_audit.yml` | `workflow_dispatch: {}`、`permissions: contents: read`、`runs-on: ubuntu-latest` |
| 三态纪律 | 同文件:9 | 同上 | 「CADENCE:UNVERIFIED（面取不到）与 CADENCE:FAIL（真超龄）都算红」 |
| 判据脚本接线 | 同文件:49-53 | 同上 | `python 05-exec/r260_quarterly_cadence.py --max-days 100` / `r58_action_pin_guard.py` / `r58_action_pin_fixtures.py` |
| action pin + dependabot | 同文件:14-18,44-45,56；自建skill优化/.github/dependabot.yml | `python -B 05-exec/r58_action_pin_guard.py` | 三个 uses 全 40 位 SHA；P2 dependabot 声明 github-actions 生态 |
| 产物上传 | 同文件:55-63 | 同上 | `upload-artifact@v4` + `if-no-files-found: error` |
| CI 盯人（反向用法） | 自建skill优化/.github/workflows/gates.yml:6-9,27,63 | `grep -n "portable-only" .github/workflows/gates.yml` | 每日 06:17 UTC+8 跑 portable 子集；只有 CI 记录 ⇒ FAIL；两台机专属门显式 SKIPPED-BY-DESIGN（X-1 设计边界） |

✅已实测（正向）：`python -B 05-exec/r260_quarterly_cadence.py --json _temp/t5_cadence_now.json` → `[CADENCE] 最新季产物=06-benchmark\quarterly_r260c\2026Q4\audit.json（2026-10-28T16:26:30）`、`季产物龄期 9.4 天 ≤ 100`、`[CADENCE:MATRIX] shadowstrict 龄期 7.2 天 ≤ 100`、`[CADENCE:PASS]`、rc=0。
⚠️注意：上面 9.4/7.2 天是本机现跑读数，会随日期漂移；复算一律重跑取值命令，禁引用本节数字当「当前值」（R241 同族）。
✅已实测（判据自证）：`python -B 05-exec/r260_quarterly_cadence.py --selftest` → `[CADENCE:SELFTEST-PASS] 5 腿含 t2 必须仍红 + t4 变异 + t5 真接线`，rc=0（tempfile 不碰真件，X-20）。
✅已实测（守卫）：`python -B 05-exec/r58_action_pin_guard.py` → `[GATE:actionpin-pass]` 引用合计 5 处（外部 5/本地 0）、已 pin 5、浮动 0、P2 OK、P3 输入面非空，rc=0；`python -B 05-exec/r58_action_pin_fixtures.py` → `[GATE:stub-pass]` 11/11，含 n1 浮动 tag / n2 分支 / n3 SHA 39 位 / n4 无 dependabot / n5 缺 github-actions / n6 空目录 / n7 目录不存在 / b2 真仓变异 SHA→@v4 必红，rc=0。
取值句柄：`_temp/t5_cadence_now.json`（schema r260-quarterly-cadence-v1）；历史快照 `06-benchmark/quarterly_cadence_latest.json` 只作 R241 留档，不当现状。

### 1.2 一键脚本（r113 编排链）

现读 自建skill优化/05-exec/r113_quarterly_audit.py:11-24：编排 r112 身份/上游探针/换装门/画像面 → r114 替代候选（第⑥段）→ r114_quality_ab（第⑦段，旁证）→ r117 路由 miss 归因（第⑧段）→ r115 质量口径（第⑨段唯一质量口径）→ domain/tag/trace/swap/req6 等后续段。
- 反「取数失败销毁证据」：同文件:21-24 —— 主产物恒写 `quarterly/{季度}/audit.json`，失败写 `audit.error.json`，只有全部步骤可用才原子替换（:278 `atomic_write_json` 先写 `.tmp` 再 `os.replace`）；:285 `capture_bytes` / :299 `restore_capture` 把非白名单静默写面（local_frontmatter.json、pool_cache_r217.json、replacement_matrix_shadowstrict.json）在预览后原位复原、新内容迁 `--out-dir` 留证不销毁。
- 参数（:330-345）：`--quarter` / `--out-dir` / `--json` / `--offline` / `--quiet` / `--no-side-write`；缺省会改写 06-benchmark/local_frontmatter.json 与 pool_cache_r217.json，故本轮用隔离预览。
- 取值命令（正式季度执行）：`python 05-exec/r113_quarterly_audit.py`（联网）或 brief 指定的 `python 05-exec/r113_quarterly_audit.py --offline`；对照件 `06-benchmark/r276_quarterly_inspection_dryrun.json`。

✅已实测（隔离预览，防污染 tracked 面）：`python -B 05-exec/r113_quarterly_audit.py --offline --no-side-write --out-dir _temp/t5_qi` → `取数面不完整（失败步: miss_migration,tag_face）⇒ 主产物未覆写（旧件保留），痕迹入 _temp\t5_qi\2026Q4\audit.error.json` / `[QUARTERLY:DEGRADED] 面不可用 ⇒ rc=2（R247：零输入/全失败不得记绿）` / `R113_RC=2`。
✅已实测（零改动对账）：`Get-FileHash` 前 16 位 —— 06-benchmark\local_frontmatter.json `A668D0865AB798C6` 不变、pool_cache_r217.json `9D7543156535E95B` 不变、replacement_matrix_shadowstrict.json `618255469EA08F80` 不变；`git diff --stat -- 05-exec/r260_quarterly_cadence.py` 为空（本轮未改判据）。另两件 quarterly_cadence_latest.json / gate_runs.jsonl 的 sha 变化已归因到并发 `run_gates` 的写面（自建skill优化/05-exec/run_gates.py:1849 与 :54/:2258），与 r113 无关，禁误记为 r113 副作用。
✅已实测（链内读数，句柄 `_temp/t5_qi/2026Q4/audit.error.json`）：provenance 权威源 191 件 / 语料 slug 3692（:12）；替代面「池 743 仓（15 条查询，api=0 cache=464）｜ 候选实测 392 仓」「四态 MATCHED=166 FAMILY_ONLY=12 NO_OS_CANDIDATE=8 UNVERIFIED=5 ｜ 守恒 191==191 OK」（:52）；quality_truth `[QUALITY:PROD] L1=90.7% L2=65.0% L4=87.5%`（:108）；upstream_meta 9 上游仓全 `SKIPPED_OFFLINE`（:164-177）—— 离线即上游版本面全盲，必须具名登记，禁当「替代已扫全」。
⚠️部分实测：失败步 miss_migration（r217_miss_migration.py:330/369 traceback）与 tag_face（`[TAGFACE:UNVERIFIED] 输入面不可读/零项`）；此外 `[REQ6:IMPOSSIBLE] 阈值在本面算术不可达（需 114.8 > 上限 95.2）`（:156）—— 属需求 6 的算术边界，t5 只登记、不改判据。

### 1.3 替代扫描（r114）

现读 自建skill优化/05-exec/r114_replacement_scan.py:153/:245/:273/:1520-1555：候选池 = `06-benchmark/pool_cache_r217.json` 入库包 + 活散件；`search(q, cache, offline, stats)` 离线未命中 ⇒ `stats["cache_miss"]+=1` 且返回 `{"state":"SKIPPED_OFFLINE","rows":[]}`（具名盲区不静默丢）；联网走 `gh api search/repositories`，失败逐条 `note_error` + `UNVERIFIED`；`save_cache` 只写成功结果；产物 tmp + `os.replace` 原子替换；末行 `[REPL:PASS] 逐件候选面守恒 ...`。
- 取值命令（退路）：`python -B 05-exec/r114_replacement_scan.py --offline --quiet --json _temp/{季}/repl_offline.json`。
- 取值命令（链内）：`python 05-exec/r114_replacement_scan.py --offline`（由 r113 第⑥段带 `--pool-pack` / `--offline` 调用，见 r113:399-406）。

✅已实测：`R114_OFFLINE_RC=0` / `[REPL:PASS] 逐件候选面守恒 191==191 ｜ MATCHED=166 FAMILY_ONLY=12 NO_OS_CANDIDATE=8 UNVERIFIED=5` / `JSON -> _temp\t5_repl_offline.json`。这正是 brief 指定的 GitHub API 限流退路，可运行已证。
✅已实测（质量口径唯一性）：自建skill优化/05-exec/r115_quality_truth.py:2 更正 r114 口径错误（主指标必须测生产路由 route()，不是 eval 内 hybrid_match）；:26 不删 r114 历史结论，按 R241 只挂校正注；:43 明写「与 r114 的 38.2% 不可比（不同函数）禁相减」。故 `quality_ab` 的 `[QUALITY:MEASURED] method=hybrid top1=38.2 ...` 只作旁证，季度结论一律取 r115 第九段。

## 2. 差距（按可归因面逐条）

| ID | 差距 | 证据句柄 | 判定 |
|---|---|---|---|
| G1 | 节律门只盯 1 类季产物面 + 1 件 shadowstrict | 自建skill优化/05-exec/r260_quarterly_cadence.py:37-38,60；自建skill优化/06-benchmark/r276_quarterly_inspection_dryrun.json:244「F5 watch_scope=[quarterly*/audit.json]（1 类）；F1/F2/F3/F4 的 generated_at 无任何超龄告警面」 | ✅已实测（代码+干跑件现读） |
| G2 | action pin 守卫只判形态（40 位 hex），查不出「形态合法但仓库不存在」的 SHA | 自建skill优化/.github/workflows/quarterly_audit.yml:21-24（原文登记为 07 台账接手项，合法方向 = 加 gh api git/objects/{sha} 存在性腿，404 ⇒ 具名 FAIL） | ✅已实测（原文现读）；❌未实测（存在性腿未落地） |
| G3 | 离线 = 上游 9 仓版本面全盲；失败步使主产物按设计不覆写 | `_temp/t5_qi/2026Q4/audit.error.json:160-163,164-177,275-285` | ✅已实测（具名盲区已显影，非静默丢） |
| G4 | r114 离线缓存冷启动：换机/缓存清场 ⇒ 决策件 UNVERIFIED 禁补 0 | 自建skill优化/06-benchmark/r276_quarterly_inspection_dryrun.json:324-365（F3/F5 与 negative_control） | ⚠️部分实测（退路本轮有缓存故通过；无缓存形态仅干跑件记载） |
| G5 | 门禁如实红：full 118 门 verdict=FAIL（FAIL=7 UNVERIFIED=4）、portable 55 门 FAIL=5 | `_temp/t5_gates_full.json:1594-1612`；pwsh-446 尾 | ✅已实测（禁为凑绿删 tracked 件 R263/X-9；gate_run_freshness 属设计内红） |
| G6 | 独立第二意见缺席：3 条 subagent 全被 `AgentTeams member delegation limit (0) reached` 拒 | 本轮委派记录 | ⚠️部分实测（设计边界，本机串行复核代替，不重试） |
| G7 | 需求 6 的 30% 阈值在本面算术不可达（需 114.8 > 上限 95.2） | `_temp/t5_qi/2026Q4/audit.error.json:156,241-273` | ✅已实测（t5 只登记，交需求 6 owner，不改判据） |

## 3. 增强建议（X-29 三门槛逐条标注）

X-29 权威原文（自建skill优化/memory/AGENTS.md:114）：「补件前先答『谁引用它』，答不出即不补；同理对手能力『明显更好』的门槛 = **可运行 + 可移植 + 与本机项目组合有交集** 三者同时成立（r60 实测 37 条真差距候选里 0 件三者齐备）」。本轮把同一门槛套到每条增强项；三者不齐一律不落地，只登记待办。

| ID | 增强项 | 可运行 | 可移植 | 与本机项目组合有交集 | 三者齐备 | 处置 |
|---|---|---|---|---|---|---|
| E1 | 把 r114 `--offline` 退路 + 三态红纪律 + sha 零改动对账写进季度 SOP（纯文档，本轮已落地于 §4 与配套清单） | ✅ 本轮实跑 `R114_OFFLINE_RC=0` / `[REPL:PASS] 守恒 191==191` | ✅ 只依赖仓内 tracked 池包与 stdlib，无 D:/global_skills 现扫 | ✅ 直接服务「复用已有资产、禁重复造轮子」 | ✅ 齐备 | ✅ 本轮落地（写面 = 两份交付件） |
| E2 | 伪造超龄负控夹具常态化（复制 r260 到 `_temp/r260_negctrl` + 造 2020-01-01 的 audit.json） | ✅ C3 实跑 `[CADENCE:FAIL]` rc=1 | ✅ 纯 stdlib + tempfile，不碰真件（X-20） | ✅ 直接验 quarterly_audit.yml 的三态红 | ✅ 齐备 | ✅ 本轮落地为 SOP 步骤 + 清单 C |
| E3 | I1：扩 r260 `newest_audit()` 为多面龄期扫描（F5 watch_scope 1→5 面：audit + r263 + r271 + r264 + r262） | ⚠️ 基座 r260 本轮实跑 PASS，但扩展后代码未落地、未跑夹具 | ✅ 纯 stdlib 无外部凭据 | ✅ 干跑件:298-305 明写覆盖 1→5 面，五面全是本仓 06-benchmark 产物 | ⚠️ 不齐（可运行腿缺扩展后实测） | ⚠️ 仅登记 P1 待办：改判据须带夹具与负控（quarterly_audit.yml:21-26「本轮不顺手改判据」）；不推翻 R241 |
| E4 | I2：新增 05-exec/r277_sidecar_backfill_proposal.py（只读反查候选 .upstream，产出建议件） | ❌ `Test-Path` = False，盘上无此脚本 | ⚠️ 依赖 r262 件级 MATCHED 缓存（本机数据面） | ✅ 干跑件:306-313「F1 入口覆盖 55/191，入口未覆盖 136 可降至理论 16」 | ❌ 不齐 | ❌ 不推荐本轮落地；登记为待办，禁凭空造文件 |
| E5 | I3：新增 06-benchmark/r277_quarterly_verdict.json（四态合成） | ❌ `Test-Path` = False；干跑件:319 `verify_cmd=null`，`verify_cmd_unavailable` 明写「原指向一件在任何盘上都已不存在的脚本」 | ❌ 连复算入口都不存在 | ✅ 干跑件:317 明写合成 F1/F2/F3/F4 | ❌ 不齐 | ❌ 不推荐本轮落地 |
| E6 | action pin 增加「SHA 必须可解析」存在性腿（gh api repos/{owner}/{repo}/git/objects/{sha}，404 ⇒ 具名 FAIL） | ⚠️ gh.exe 在 `C:\Program Files\GitHub CLI\gh.exe`（本轮核对），但 404 判定未实跑 | ⚠️ 依赖 GitHub API 凭据/限流；本机无 token 会 401，需绑定 offline 具名 UNVERIFIED 退路 | ✅ 三个 pin 都在 quarterly_audit.yml:14-16 | ⚠️ 不齐 | ⚠️ 仅登记 07 台账接手项（与 quarterly_audit.yml:21-24 一致），不擅自改判据 |
| E7 | 改 workflow 增加 CI 深度巡检 | ❌ 现役 quarterly_audit.yml 已覆盖节律/三态/pin/dependabot；把 r113 深度巡检搬进 CI 会现扫 D:/global_skills + managed venv ⇒ runner 必假红 | ❌ 违 X-1「禁为凑 CI 覆盖把技能语料复制进归档仓」 | ❌ 两台机专属门是设计边界（gates.yml:8-9） | ❌ 不齐 | ❌ 本轮 workflow diff = 空；`git diff -- .github/workflows/` 期望无输出 |

> 决策：本轮不改 05-exec/、不改 .github/workflows/、不改 06-benchmark/ tracked 件，只交付两份文档 + 隔离区证据。理由 = 复用已有资产（brief 硬要求）+ R241 不推翻历史判据 + X-29 三门槛未齐的代码级增强不落地 + X-1/两台机专属门边界。
> 回滚：两份交付件为 untracked 新文件，撤销 = 直接删这两件（不涉及任何 tracked 件迁走/改名，X-9）。

## 4. 季度执行 SOP（复用现役资产，不重造轮子）

前置（T-7）：
1. 环境与根：`$py = Join-Path $env:USERPROFILE ".workbuddy\binaries\python\envs\default\Scripts\python.exe"`；`$env:PYTHONPYCACHEPREFIX = Join-Path $env:TEMP "pycache_t5"`；`git rev-parse --show-toplevel` 必须 = `D:/app-cache/skill-fenjue/自建skill优化`（工作目录 D:\app-cache\skill-fenjue 本身不是 git 仓）。
2. 他人脏项只登记：`git status --porcelain`（本轮已有多条他人在途 M/??，按 R269 不擅动）。
3. sha 基线五件（取值命令：`Get-FileHash -Algorithm SHA256 06-benchmark\local_frontmatter.json, 06-benchmark\pool_cache_r217.json, 06-benchmark\replacement_matrix_shadowstrict.json, 06-benchmark\quarterly_cadence_latest.json, 06-benchmark\gate_runs.jsonl`），供事后零改动对账。

季度首日（CI 自动，人工复核）：
4. CI：quarterly-audit-heartbeat 按 `:34` cron 触发；复算 `grep -n "cron:" .github/workflows/quarterly_audit.yml`；三态任一红即开人跟进（UNVERIFIED 也算红）。
5. 本地同跑面：`python -B 05-exec/r260_quarterly_cadence.py --json _temp/{季}/cadence.json`、`python -B 05-exec/r260_quarterly_cadence.py --selftest`、`python -B 05-exec/r58_action_pin_guard.py`、`python -B 05-exec/r58_action_pin_fixtures.py`。四个 pin 的 SHA 复算命令见 quarterly_audit.yml:18（`gh api repos/actions/checkout/git/ref/tags/v4 --jq .object.sha` 等三条）。

深度巡检（本机，正式季度执行）：
6. 先隔离预览（不污染 tracked 面）：`python -B 05-exec/r113_quarterly_audit.py --offline --no-side-write --out-dir _temp/{季}/preview`，读 `_temp/{季}/preview/{季度}/audit.error.json` 的 `face_ok` / `failed_steps` / `upstream_meta`。
7. 面齐再正式跑：`python 05-exec/r113_quarterly_audit.py`（联网；GH 限流则 `python 05-exec/r113_quarterly_audit.py --offline` 并在台账具名登记 9 上游仓 SKIPPED_OFFLINE 盲区）。失败语义按 自建skill优化/04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md:235-244 §6：任一步失败 ⇒ 主产物原样保留上一季好件 + 痕迹入 audit.error.json + rc=2，禁记绿；`python 05-exec/r113_cache_guard_face.py` 须印 `[CACHEGUARD:PASS]`。
8. 替代面单跑（退路）：`python -B 05-exec/r114_replacement_scan.py --offline --quiet --json _temp/{季}/repl_offline.json`，末行须 `[REPL:PASS] 逐件候选面守恒 ...`；缓存冷启动失败 ⇒ 具名 `UNVERIFIED` 禁补 0。
9. 质量口径：`python 05-exec/r115_quality_truth.py`（第⑨段唯一口径）；r114 的 38.2% 只作旁证，R241 只加校正注，禁与 r115 读数相减。

门禁与盯人：
10. `python -B 05-exec/run_gates.py --json _temp/{季}/gates_full.json` 与 `python -B 05-exec/run_gates.py --portable-only --json _temp/{季}/gates_ci.json`；如实记 `verdict`，禁为凑绿删/迁/改名 tracked 件（R263/X-9）；`gate_run_freshness` 红属设计内（只有 CI 记录 ⇒ FAIL），复算 `python 05-exec/r32_gate_freshness.py`。
11. CI 盯人：`gh run list --workflow quarterly-audit-heartbeat`；`python 05-exec/r32_ci_health.py --json _temp/{季}/ci_health.json`（近 ≤50 run 结论分布 + 心跳）。

归档与回滚：
12. 台账 append-only（`06-benchmark/gate_runs.jsonl`），旧数字只加「校正注」（R241）；产物写面必须 `--json _temp/...` 或用 runner 自带原子替换（r113:278 / r114:1523-1525），禁手抄当前值。
13. 受管根（D:/global_skills、_my-skills、.agents/skills、eval/）全程只读；真实替换列入迁移计划分阶段时间节点，改受管源须走 `rule_editor.py` + 双硬前提，本任务不执行。
14. 回滚：预览/负控全部落在被 `.gitignore:16` 忽略的 `_temp/`（本轮 `git check-ignore -v _temp\t5_cadence_now.json` 命中）；撤销 = 删隔离区副本；tracked 件一律不动。

## 5. 判据与负控（有牙验证）

正向（✅已实测）：
- P1 `python -B 05-exec/r260_quarterly_cadence.py --json _temp/t5_cadence_now.json` → `[CADENCE:PASS]` rc=0（含 `[CADENCE:MATRIX]` 第二腿）。
- P2 `python -B 05-exec/r260_quarterly_cadence.py --selftest` → `[CADENCE:SELFTEST-PASS]` 5 腿 rc=0。
- P3 `python -B 05-exec/r58_action_pin_guard.py` → `[GATE:actionpin-pass]` rc=0；`python -B 05-exec/r58_action_pin_fixtures.py` → `[GATE:stub-pass]` 11/11 rc=0。
- P4 `python -B 05-exec/r114_replacement_scan.py --offline --quiet --json _temp/t5_repl_offline.json` → `[REPL:PASS] 守恒 191==191` rc=0。
- P5 `python -B 05-exec/r113_quarterly_audit.py --offline --no-side-write --out-dir _temp/t5_qi` → `[QUARTERLY:DEGRADED]` rc=2（按设计降级，主产物未覆写、留痕、三件 sha 不变）—— 判据的「失败不假绿」腿。
- P6 `python -B 05-exec/run_gates.py --json _temp/t5_gates_full.json` → `verdict=FAIL` / `FAIL=7 UNVERIFIED=4` / `gates_run=118` / `GATES_FULL_RC=1`；`--portable-only` → `执行 55 门 / 跳过 63 门` / `[GATES:FAIL] FAIL=5 UNVERIFIED=0` / `GATES_RC=1`。如实记红（brief 自证命令 `python 05-exec/run_gates.py --json` 已跑）。

- P7 `python -B 05-exec/r113_cache_guard_face.py` → `[CACHEGUARD:PASS] 取数脚本的证据缓存写点全部声明守卫（2 在面 / 取数面 147）` / `CACHEGUARD_RC=0`（写交付件之后补跑；覆盖根 05-exec .py 315 件、裸写违规 0）。

负控（✅已实测，证明门有牙）：
- N1 伪造「已超龄」产物：复制真脚本到 `_temp/r260_negctrl/05-exec/r260_quarterly_cadence.py`，造 `_temp/r260_negctrl/06-benchmark/quarterly_neg/2020Q1/audit.json`（`generated_at="2020-01-01T00:00:00"`），并放一份当下 `replacement_matrix_shadowstrict.json` 隔离第二腿；在 `_temp/r260_negctrl` 下跑 `python -B 05-exec/r260_quarterly_cadence.py --max-days 100` → `[CADENCE] 最新季产物=06-benchmark\quarterly_neg\2020Q1\audit.json（2020-01-01T00:00:00）` / `季产物超龄 2502.1 天 > 上限 100 天` / `[CADENCE:FAIL] 季度巡检超龄 ⇒ 跑 python 05-exec/r113_quarterly_audit.py --offline`，rc=1。⇒ 红，不是恒绿。（写后复验：两份交付件落盘后在同一目录再跑该命令，仍得 `季产物超龄 2502.1 天 > 上限 100 天` / `[CADENCE:FAIL]` / `NEGCTRL_RC=1`，证明写文档动作未破坏负控夹具。）
- N2 判据变异：`r58_action_pin_fixtures.py` 的 b2 把真仓一个 40 位 SHA 改成 `@v4` ⇒ 必红（11/11 内含）；r260 `--selftest` 的 t2（300 天必须红）与 t4（恒 0 变异把超龄读成绿）⇒ 5/5。
- N3 cache-guard：r113 离线预览里 `failed_steps=["miss_migration","tag_face"]` ⇒ `audit.error.json` 落痕、主产物 `audit.json` 未创建、tracked side-write 三件 sha 不变、`side_write_policy.shadow_matrix_fence_action="restored"`、新内容迁 `_temp/t5_qi/2026Q4` 留证。⇒ 取数失败不销毁证据。
- ⚠️部分实测（历史干跑件的负控，本轮只现读未复跑）：`自建skill优化/06-benchmark/r276_quarterly_inspection_dryrun.json:324-365` 记 F4 输入件指向不存在 ⇒ `[QI:UNVERIFIED] unverified=[F4]` rc=2；四面齐 ⇒ `[QI:PASS] faces=5 unverified=0` rc=0。R241 不改写，引用时标「干跑件记载」。
- ❌未实测：GH API `git/objects/{sha}` 404 存在性腿（E6）；I2/I3 的 verify 命令（盘上无脚本）。

## 6. 盲区与退路（具名登记，禁静默丢弃）

| 盲区 | 处置 / 退路 | 结论 |
|---|---|---|
| GH API 限流 / 无凭据 | `python -B 05-exec/r114_replacement_scan.py --offline --quiet --json _temp/{季}/repl_offline.json` 复用 `06-benchmark/pool_cache_r217.json`；上游 9 仓标 `SKIPPED_OFFLINE`，在台账具名 | ✅已实测 PASS（191==191） |
| 离线预览失败步 miss_migration / tag_face | 按 §4 步骤 6-7 先预览再正式；主产物按设计不覆写 | ✅已实测降级 rc=2 |
| 委派第二意见 | 3 条 subagent 全被 `AgentTeams member delegation limit (0) reached` 拒 ⇒ 设计边界，本机串行复核 + 逐条现读代替，不重试、不冒充独立评审 | ⚠️部分实测 |
| 门禁真红 | 如实记 `verdict=FAIL`，不删/迁/改名 tracked 件凑绿；`gate_run_freshness` 单列 DESIGN_INHERENT_RED | ✅已实测 |
| 两台机专属门 | gates.yml `SKIPPED-BY-DESIGN` 显式打印；X-1 禁复制技能语料；「CI 绿」定义 = portable 子集全绿 ≠ 本机 full 全绿 | ✅已实测（workflow 现读 + portable 实跑） |
| 需求 6 算术边界 | `[REQ6:IMPOSSIBLE]` 只登记，交需求 6 owner；t5 不改判据 | ✅已实测登记 |
| 历史快照 | `06-benchmark/r276_gate_run.json`（generated_at 2026-10-29 21:32，verdict=FAIL）与 `quarterly_cadence_latest.json`（2026-10-28T16:26:30）按 R241 只留档，禁当现状 | ✅已实测（现读 + 现跑复算） |
| 写面隔离 | 所有预览/负控/门禁 JSON 落 `_temp/`（`.gitignore:16` 命中）；交付件仅两份 untracked 新文件 | ✅已实测 |

> 收尾：本轮未改任何受管源文件、未改任何 tracked workflow / 05-exec / 06-benchmark 件；两份交付件为唯一写面。所有「已实测」结论均附可复跑取值命令或文件句柄。
