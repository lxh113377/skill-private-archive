# data · 季度巡检可复跑清单（t5 配套）

> 写面：自建skill优化/deliverables/skill-modernization-r1/data/quarterly_check.md（t5 独占编号）
> 主报告：自建skill优化/deliverables/skill-modernization-r1/05_inspection_regime.md
> 用法：每季度按 B 顺序逐条打勾；每条命令都给期望末行；C 的负控必须至少跑 N1 一次；数字一律现场复算，禁抄本清单或旧快照的值（R241 / 禁硬编码当前值）。
> 环境（每条命令前）：`$py = Join-Path $env:USERPROFILE ".workbuddy\binaries\python\envs\default\Scripts\python.exe"`；`$env:PYTHONPYCACHEPREFIX = Join-Path $env:TEMP "pycache_t5"`；workdir = `D:/app-cache/skill-fenjue/自建skill优化`（用 `git rev-parse --show-toplevel` 核对）。

## A. 现役资产逐条取值命令（三面现读确认在役）

| # | 面 | 资产路径 | 取值命令 | 期望 / 在役证据 |
|---|---|---|---|---|
| A1 | CI 节律 cron | 自建skill优化/.github/workflows/quarterly_audit.yml:34 | `grep -n "cron:" .github/workflows/quarterly_audit.yml` | `cron: "0 22 1 1,4,7,10 *"`（季度首日 06:00 UTC+8） |
| A2 | 三态纪律 | 同文件:9 | `git show HEAD:.github/workflows/quarterly_audit.yml` | `CADENCE:UNVERIFIED` 与 `CADENCE:FAIL` 都算红 |
| A3 | workflow 接线 | 同文件:49-53 | 同上 | r260 / r58_action_pin_guard / r58_action_pin_fixtures 三判据 |
| A4 | action pin + dependabot | 同文件:14-18,44-45,56；自建skill优化/.github/dependabot.yml | `python -B 05-exec/r58_action_pin_guard.py` | `[GATE:actionpin-pass]`（P1 全 pin / P2 dependabot / P3 面非空） |
| A5 | CI 盯人 | 自建skill优化/.github/workflows/gates.yml:6-9,27,63 | `grep -n "portable-only" .github/workflows/gates.yml` | 每日 06:17 UTC+8；只有 CI 记录 ⇒ FAIL；两台机门 SKIPPED-BY-DESIGN |
| A6 | 一键脚本 | 自建skill优化/05-exec/r113_quarterly_audit.py:11-24,278,285,299,330-345 | `python 05-exec/r113_quarterly_audit.py --help` | 编排 r112→r114→r117→r115；原子替换 + cache-guard；`--no-side-write` 隔离 |
| A7 | 替代扫描 | 自建skill优化/05-exec/r114_replacement_scan.py:153,245,273,1520-1555 | `python -B 05-exec/r114_replacement_scan.py --offline --quiet --json _temp/{季}/repl_offline.json` | `[REPL:PASS] 逐件候选面守恒 ...` |
| A8 | 质量口径 | 自建skill优化/05-exec/r115_quality_truth.py:2,26,43 | `python 05-exec/r115_quality_truth.py --help` | 唯一口径 = 生产 route()；r114 38.2% 不可比，R241 只加校正注 |
| A9 | 维护规范 | 自建skill优化/04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md:235-244,248-260 | `grep -n "失败语义" 04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md` | §6 失败语义 / §7 分工不重叠 |
| A10 | 干跑对照件 | 自建skill优化/06-benchmark/r276_quarterly_inspection_dryrun.json | `grep -n "schema" 06-benchmark/r276_quarterly_inspection_dryrun.json` | F1–F5 五面 + improvements I1/I2/I3 + negative_control |

> `git ls-files -- .github/workflows/ .github/dependabot.yml 05-exec/r113_quarterly_audit.py 05-exec/r114_replacement_scan.py 05-exec/r115_quality_truth.py 05-exec/r260_quarterly_cadence.py 05-exec/r58_action_pin_guard.py 05-exec/r58_action_pin_fixtures.py 06-benchmark/pool_cache_r217.json 06-benchmark/r276_quarterly_inspection_dryrun.json` → ✅已实测全部入库（本轮实跑，10/10 命中）。

## B. 当季执行清单（按顺序，逐条打勾）

- [ ] B0 前置：`git rev-parse --show-toplevel` = `D:/app-cache/skill-fenjue/自建skill优化`；`git status --porcelain` 他人脏项只登记（R269）；`Get-FileHash -Algorithm SHA256 06-benchmark\local_frontmatter.json, 06-benchmark\pool_cache_r217.json, 06-benchmark\replacement_matrix_shadowstrict.json, 06-benchmark\quarterly_cadence_latest.json, 06-benchmark\gate_runs.jsonl` 存基线。
- [ ] B1 节律正向：`python -B 05-exec/r260_quarterly_cadence.py --json _temp/{季}/cadence.json` → `[CADENCE:PASS]` rc=0（本轮实跑，龄期读数随日期漂移，禁抄值）。
- [ ] B2 判据自证：`python -B 05-exec/r260_quarterly_cadence.py --selftest` → `[CADENCE:SELFTEST-PASS] 5 腿 ...` rc=0。
- [ ] B3 pin 守卫：`python -B 05-exec/r58_action_pin_guard.py` → `[GATE:actionpin-pass]`；`python -B 05-exec/r58_action_pin_fixtures.py` → `[GATE:stub-pass] 11/11`（含 b2 变异必红）。
- [ ] B4 pin SHA 复算：按 自建skill优化/.github/workflows/quarterly_audit.yml:18 的三条 `gh api repos/actions/checkout/git/ref/tags/v4 --jq .object.sha` 逐条对账（本轮 ❌未实测，需 GH 凭据）。
- [ ] B5 隔离预览：`python -B 05-exec/r113_quarterly_audit.py --offline --no-side-write --out-dir _temp/{季}/preview`；读 `_temp/{季}/preview/{季度}/audit.error.json` 的 `face_ok` / `failed_steps` / `upstream_meta` / `side_write_policy`。本轮 → `face_ok=false`、失败步 `miss_migration,tag_face`、`[QUARTERLY:DEGRADED]` rc=2（按设计降级，非假绿）。
- [ ] B6 正式深度巡检（面齐才跑）：`python 05-exec/r113_quarterly_audit.py`；GH 限流退路 `python 05-exec/r113_quarterly_audit.py --offline` 并在台账具名 9 上游仓 `SKIPPED_OFFLINE` 盲区。失败语义：主产物原样保留 + `audit.error.json` + rc=2；`python 05-exec/r113_cache_guard_face.py` → `[CACHEGUARD:PASS]`（✅本轮写交付件后补跑实得 `CACHEGUARD_RC=0`，覆盖根：05-exec .py 315 件 / 取数面 147 件 / 裸写违规 0）。
- [ ] B7 替代面：`python -B 05-exec/r114_replacement_scan.py --offline --quiet --json _temp/{季}/repl_offline.json` → `[REPL:PASS] 逐件候选面守恒 191==191 ｜ MATCHED=166 FAMILY_ONLY=12 NO_OS_CANDIDATE=8 UNVERIFIED=5`（本轮实跑读数，禁抄当「当前值」，须现跑复算）；冷缓存缺面 ⇒ 具名 `UNVERIFIED` 禁补 0。
- [ ] B8 质量口径：`python 05-exec/r115_quality_truth.py` → `[QUALITY:PROD] ...`；r114 `hybrid 38.2%` 只作旁证，禁相减。
- [ ] B9 门禁全量：`python -B 05-exec/run_gates.py --json _temp/{季}/gates_full.json` → 如实记 `verdict`（本轮 `FAIL` / `FAIL=7 UNVERIFIED=4` / `gates_run=118` / rc=1）；禁删 tracked 件凑绿。
- [ ] B10 门禁 CI 面：`python -B 05-exec/run_gates.py --portable-only --json _temp/{季}/gates_ci.json` → 本轮 `执行 55 门 / 跳过 63 门` / `[GATES:FAIL] FAIL=5 UNVERIFIED=0` / rc=1；`gate_run_freshness` 单列 DESIGN_INHERENT_RED。
- [ ] B11 盯人：`gh run list --workflow quarterly-audit-heartbeat`；`python 05-exec/r32_gate_freshness.py`；`python 05-exec/r32_ci_health.py --json _temp/{季}/ci_health.json`。
- [ ] B12 零改动对账：重跑 B0 的 `Get-FileHash` 与基线逐字符比对；本轮三件 side-write 目标 `A668D0865AB798C6` / `9D7543156535E95B` / `618255469EA08F80` 不变；`git diff --stat -- 05-exec/r260_quarterly_cadence.py` 空；两件变化（quarterly_cadence_latest.json / gate_runs.jsonl）归因到 run_gates 写面（自建skill优化/05-exec/run_gates.py:1849,54,2258），非 r113 副作用。
- [ ] B13 归档：台账 append-only；旧产物数字只加「校正注」（R241）；受管根全程只读；真实替换走迁移计划 + `rule_editor.py` + 双硬前提。
- [ ] B14 workflow 对账：`git diff -- .github/workflows/` 期望无输出（本轮未改 workflow；E7 判不齐，X-1 / 两台机专属门边界）。

## C. 负向对照（至少跑 N1 一次；证明判据有牙，不是恒绿）

- [ ] N1 伪造「已超龄」产物 ⇒ CADENCE 门必须红（✅本轮已实测）：
  1. `New-Item -ItemType Directory -Force _temp/r260_negctrl/05-exec, _temp/r260_negctrl/06-benchmark/quarterly_neg/2020Q1`
  2. `Copy-Item 05-exec/r260_quarterly_cadence.py _temp/r260_negctrl/05-exec/r260_quarterly_cadence.py`
  3. 写 `_temp/r260_negctrl/06-benchmark/quarterly_neg/2020Q1/audit.json`：`{"schema":"negctrl","generated_at":"2020-01-01T00:00:00"}`
  4. 隔离第二腿：把当下 `06-benchmark/replacement_matrix_shadowstrict.json` 复制到 `_temp/r260_negctrl/06-benchmark/replacement_matrix_shadowstrict.json`
  5. 在 `_temp/r260_negctrl` 下跑 `python -B 05-exec/r260_quarterly_cadence.py --max-days 100`
  6. 期望末行：`[CADENCE:FAIL] 季度巡检超龄 ⇒ 跑 python 05-exec/r113_quarterly_audit.py --offline`，rc=1（本轮实得 `季产物超龄 2502.1 天 > 上限 100 天`）。
  7. 负控副本留在 `_temp/`（`.gitignore:16` 忽略），用完不删以留证；禁移进 tracked 面。
- [ ] N2 判据变异：`python -B 05-exec/r260_quarterly_cadence.py --selftest` 的 t2（300 天必须红）/ t4（恒 0 变异把超龄读成绿）⇒ 5/5；`python -B 05-exec/r58_action_pin_fixtures.py` 的 b2（真仓 SHA→@v4 必红）⇒ 11/11。✅已实测。
- [ ] N3 cache-guard：B5 的 `failed_steps` 非空时，核 `_temp/{季}/preview/{季度}/audit.error.json` 有 `face_ok=false` + `side_write_policy.shadow_matrix_fence_action="restored"` + 主产物 `audit.json` 未创建 + B12 三件 sha 不变。✅已实测。
- [ ] N4（⚠️历史干跑件记载，本轮未复跑）：`自建skill优化/06-benchmark/r276_quarterly_inspection_dryrun.json:324-365` —— F4 输入件指向不存在 ⇒ `[QI:UNVERIFIED] unverified=[F4]` rc=2；四面齐 ⇒ `[QI:PASS] faces=5 unverified=0` rc=0。引用须标注「干跑件记载」。
- [ ] N5（❌未实测）：GH `git/objects/{sha}` 404 存在性腿（报告 E6）；I2/I3 的 verify 命令盘上无脚本，不得假装跑过。

## D. 退路与盲区登记

| 触发 | 退路命令 | 具名登记 | 本轮状态 |
|---|---|---|---|
| GH API 限流 / 401 | `python -B 05-exec/r114_replacement_scan.py --offline --quiet --json _temp/{季}/repl_offline.json`；r113 `--offline` | 9 上游仓 `SKIPPED_OFFLINE`；`cache_miss` 具名 | ✅已实测 `[REPL:PASS]` rc=0 |
| 取数失败 / 面不全 | 不覆写主产物，`audit.error.json` 留痕，rc=2 | `failed_steps` / `face_reason` / `upstream_meta` | ✅已实测 `[QUARTERLY:DEGRADED]` |
| 门禁报红 | 如实记 `verdict`，先修判据再动手（R263） | `REAL_RED` vs `DESIGN_INHERENT_RED` 分类只改展示不改 rc | ✅已实测 full FAIL / portable FAIL |
| 委派第二意见缺席 | 本机串行逐条现读 + 附取值命令 | `AgentTeams member delegation limit (0) reached` | ⚠️设计边界，不重试 |
| 两台机专属门 | `--portable-only` + `SKIPPED-BY-DESIGN` | X-1 禁复制技能语料 | ✅已实测（workflow 现读） |
| 需求 6 阈值 | 只登记交 owner | `[REQ6:IMPOSSIBLE] 需 114.8 > 上限 95.2` | ✅已实测登记 |
| 旧快照当现状 | 一律现跑复算 | R241 只留档 + 校正注 | ✅已实测 |

> 结论标注：✅已实测 = 本轮有命令输出或文件句柄；⚠️部分实测 = 有现读/历史记载但缺本轮复跑；❌未实测 = 盘上无件或需外部凭据，禁写成完成。
