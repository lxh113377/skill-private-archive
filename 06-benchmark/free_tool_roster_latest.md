# 免费工具 x 工作流 x skill 搭配名册（生成物，勿手改）

生成命令：python 05-exec/r215_free_tool_roster.py --json <件>

## 依据面（五道判据当前读数）

| 判据 | 量什么 | 读数 |
|---|---|---|
| 163 | 工具在本机能不能跑 | 名册 10 项 |
| 93 | 每个工具是否至少被一个 skill 承载 | 工具 10 / 扫描 2009 卷 / 未承载 0 |
| 92 | 每轮入口会不会把话术派到写着答案的卷 | 判 8 / 缺口 0 |
> 依据面取值：163 见 free_tools_latest.json；93 见 tool_carrier_latest.json 与 tool_skill_matrix_probe.json；92 见 ingress_latest.json；88 见 recall_latest.json 与 route_truth_latest.json。再生命令见文件头。
| 88 | 窗口 / BGE 真值 / 任务语句三层 | 窗口 3、真值 2、任务 7 命中 6、缺口 3 |

## 搭配总表（一眼版）

| 工具 | ① skill 提到/代码 | ② 工作流真调用 | ③ 项目仓（剪后·含注释占比） | ④ 读数面 | ⑤ 用量 | 卡点/状态 |
|---|---|---|---|---|---|---|
| GitHub | 23 / 2 | 34 | 49（注释占比 0.49） | MEASURED | 27664.0 分钟（官方计费·账号级·端点默认窗口） | READY |
| Cloudflare-D1 | 2 / 0 | 3 | 147（注释占比 0.156） | MEASURED | 8.99 MiB | READY |
| Cloudflare-R2 | 1 / 0 | 0 | 0 | GAP_SERVICE | 未量 | [平台能力缺口] |
| Cloudflare-Pages | 5 / 2 | 7 | 250（注释占比 0.151） | MEASURED | 236283 次 | READY |
| Cloudflare-Workers | 1 / 0 | 0 | 1（注释占比 1.0·仅注释） | MEASURED | 0 次 | [口径盲区] |
| SQLite | 4 / 3 | 24 | 127（注释占比 0.139） | MEASURED | 13.13 MiB（本地库体量·非额度） | READY |
| VS Code | 7 / 1 | 0 | 0 | 无读数面 | 未量 | [桌面 GUI 承载（非调用面）] |
| Cloudflare-Turnstile | 3 / 0 | 27 | 3（注释占比 1.0·仅注释） | MEASURED | 0 次（校验请求） | READY |
| Resend | 1 / 1 | 0 | 0 | 无读数面 | 未量 | GAP_CRED |
| Upstash-Redis | 0 / 0 | 0 | 0 | 无读数面 | 未量 | [外部凭据缺口] |

汇总：四层齐备（有代码级/有工作流调用/项目仓有命中/读数 MEASURED）= **3** 项；有真调用（工作流或代码级任一）= 7 项；带卡点归因 = 4 项；无读数面 = 3 项。

（总表取值：同下各节；每行都由 items 计算，禁手写 —— 牙 r6 校验行数与工具集合。）

## 目标对口（这份册子回答了什么）

- **「这些免费开发者工具」** = **10** 项：GitHub、Cloudflare-D1、Cloudflare-R2、Cloudflare-Pages、Cloudflare-Workers、SQLite、VS Code、Cloudflare-Turnstile、Resend、Upstash-Redis
- **「搭配上了」**（有真调用：skill 代码级 ∨ 工作流真调用）= **7** 项；四层齐备（含读数 MEASURED）= **3** 项。
- **「有官方额度读数」**（第 ⑤ 层给出数值）= **6** 项：GitHub 27664.0、Cloudflare-D1 8.99、Cloudflare-Pages 236283、Cloudflare-Workers 0、SQLite 13.13、Cloudflare-Turnstile 0
- **「合理」= 不能用的都具名了**：带卡点归因 **4** 项 —— Cloudflare-R2[平台能力缺口]；Cloudflare-Workers[口径盲区]；VS Code[桌面 GUI 承载（非调用面）]；Upstash-Redis[外部凭据缺口]
- **无读数面**（本地/桌面侧，非缺口）= **3** 项；**每一项的零都带取值命令**（见下各节行内「取值」）。
- 交叉校验：第 ④ 层 MEASURED 而第 ⑤ 层无数值的工具 = **0** 项（牙 r7 要求为 0）。

## 逐工具搭配态

### GitHub - READY

- 两把尺：提到 23 件 ｜ 代码真调用 2 件
    提到 = A-get-memory, A-memory-start, A-project-better, A-project-handoff, A-skill-manager, chaoshi-image-optimization, chaoshi-web-deploy, ci-pipeline-debugging, consulting-analysis, doc-coauthoring, docker-e2e-gate, github, gstack, healthcare-eval-harness, hyperframes, hyperframes-registry, oracle, security-audit, shell-encoding-pitfalls, story, ui-ux-pro-max, verification-before-completion, win-toolchain-pitfalls
    可执行 = A-project-handoff, gstack
    （取值：tool_skill_matrix_latest.json 的 per_tool / per_tool_exec[GitHub]；该件 generated_at=2026-10-28 17:10）
- 三层读数：
    ① skill 目录（第 67 门）：提到 23 ｜ 代码真调用 2
    ② 工作流脚本（第 94 门 r222 第二把尺，探针件不计入）：真调用 34
        调用它的非探针件 = quarterly_audit.yml, r113_quarterly_audit.py, r19_feedback_append.py, r31_ci_surface.py, r32_ci_health.py, r33_release_governance.py, r34_portability_surface.py, r58_action_pin_guard.py, r60_capability_roster.py, r60_capability_roster_describe.py, r60_upstream_backfill.py
    ③ 项目仓（第 67 门 r226 third_face，已剪 vendored 外来面）：49
        命中所在件 = backupLiveness.test.js, benchmark-peers.mjs, bracketLexer.test.js, cache_bump_guard.py, check-backup-liveness.mjs, check-branch-protection.mjs, check-changelog.mjs, check-cron-health.mjs, check-d1-remote-usage.mjs, check-d1-roundtrips.mjs, check-delivery-claims.mjs, check-escape-hatch-log.mjs, check-gate-parity.mjs, check-head-closure.mjs, check-limit-provenance.mjs, check-pr-has-tests.mjs, check-remote-divergence.mjs, ciWorkflow.test.ts, ci_diag_r96.py, cronHealth.test.js
        质量拆分：命中行 49，其中注释行 24（占比 0.49）
    （② 取值：workflow_usage_latest.json 的 tools[].real_hits，窗口面 177/297 件、真调用合计 95；
     ③ 取值：tool_skill_matrix_latest.json 的 third_face.per_tool，4358 件 / 2 仓 / 剪外来面 10 个）
- 读数型真调用（第 4 层）：**MEASURED**（读得到数）
    （取值：r241_gh_billing_face.py --json gh_billing_latest.json 的 state）
- 本月/当前用量：**27664.0 分钟（官方计费·账号级·端点默认窗口）**（折后净额 $ 0.0）　窗口：['2026-08-01', '2026-10-01']
    （取值：r241_gh_billing_face.py --json gh_billing_latest.json 的 minutes_total）
- 守它的判据：163 + 87 + 93
- 工作流触点：A-project-handoff 的 git_autopush 钩子模板（本仓 post-commit 即其落地）+ 第 87 门读 autopush 末行 rc；私有仓分钟用满是已付代价
- 触点在位核验（在位≠已接入）：A-project-handoff -> IN_SKILL_DESC
- 任务语句实测：
    - CI 红了 -> HIT_DIRECT（top1=ci-pipeline-debugging，期望件=ci-pipeline-debugging）
    - 钩子静默推送 -> HIT（top1=win-toolchain-pitfalls，期望件=win-toolchain-pitfalls）
    - Actions 分钟 -> HIT（top1=chaoshi-web-deploy，期望件=chaoshi-web-deploy）

### Cloudflare-D1 - READY

- 两把尺：提到 2 件 ｜ 代码真调用 0 件
    提到 = chaoshi-web-deploy, win-toolchain-pitfalls
    可执行 = 无
    （取值：tool_skill_matrix_latest.json 的 per_tool / per_tool_exec[Cloudflare-D1]；该件 generated_at=2026-10-28 17:10）
- 三层读数：
    ① skill 目录（第 67 门）：提到 2 ｜ 代码真调用 0
    ② 工作流脚本（第 94 门 r222 第二把尺，探针件不计入）：真调用 3
        调用它的非探针件 = r119_cand_regress.py, r119_cand_sandbox.py
    ③ 项目仓（第 67 门 r226 third_face，已剪 vendored 外来面）：147
        命中所在件 = _health.js, _middleware.js, backup-print-data.mjs, backupPrintData.test.js, backupRestore.test.js, batchProducts.test.js, check-cli-entrypoints.mjs, check-d1-remote-usage.mjs, check-d1-roundtrips.mjs, check-governance-framework.mjs, cliEntrypoints.test.js, d1RemoteUsage.test.js, d1RoundTrips.test.js, db.js, event_sink.js, events.js, fix_face_claims.py, fix_face_claims2.py, fix_u333.py, fix_verify_cause.py
        质量拆分：命中行 147，其中注释行 23（占比 0.156）
    （② 取值：workflow_usage_latest.json 的 tools[].real_hits，窗口面 177/297 件、真调用合计 95；
     ③ 取值：tool_skill_matrix_latest.json 的 third_face.per_tool，4358 件 / 2 仓 / 剪外来面 10 个）
- 读数型真调用（第 4 层）：**MEASURED**（读得到数）
    （取值：r196_quota_face.py --json quota_face_latest.json 的 rows/cloudflare_d1/state）
- 本月/当前用量：**8.99 MiB**（占名册声称上限 0.176）　窗口：5 GiB 存储
    （取值：r196_quota_face.py --json quota_face_latest.json 的 rows/cloudflare_d1/mib）
- 守它的判据：163 + 88 任务层 + 93
- 工作流触点：A-memory-start 的 quickref 额度专章（r196_quota_face 现读行数/写入）+ chaoshi-web-deploy 的 d1 execute 部署链
- 触点在位核验（在位≠已接入）：A-memory-start -> MENTIONS
- 触点在位核验（在位≠已接入）：chaoshi-web-deploy -> IN_SKILL_DESC
- 触点在位核验（在位≠已接入）：r196_quota_face（判据件） -> GATE_FILE_MENTIONS
- 任务语句实测：
    - D1 查额度 -> HIT（top1=A-memory-start，期望件=A-memory-start）

### Cloudflare-R2 - GAP_SERVICE

- 两把尺：提到 1 件 ｜ 代码真调用 0 件
    提到 = chaoshi-image-optimization
    可执行 = 无
    （取值：tool_skill_matrix_latest.json 的 per_tool / per_tool_exec[Cloudflare-R2]；该件 generated_at=2026-10-28 17:10）
- 三层读数：
    ① skill 目录（第 67 门）：提到 1 ｜ 代码真调用 0
    ② 工作流脚本（第 94 门 r222 第二把尺，探针件不计入）：真调用 0
    ③ 项目仓（第 67 门 r226 third_face，已剪 vendored 外来面）：0
    （② 取值：workflow_usage_latest.json 的 tools[].real_hits，窗口面 177/297 件、真调用合计 95；
     ③ 取值：tool_skill_matrix_latest.json 的 third_face.per_tool，4358 件 / 2 仓 / 剪外来面 10 个）
- **零层归因：[平台能力缺口]** R2 未在账号启用（wrangler 与 REST 同回 10042，官方提示需 Dashboard 启用）；档位 2 实测打开 dash.cloudflare.com 即命中 CF 安全质询页（「正在进行安全验证」+ 质询 iframe），在登录前被挡 ⇒ 属平台+条款同意缺口 ∧ 自动化通道被平台自身反机器人质询拦截，非本机凭据问题（对照 /accounts=200 已证 API 凭据活着）
    （取值：python 05-exec/r201_r2_enable_face.py --json 06-benchmark/r2_enable_latest.json（state=GAP_SERVICE / code=10042）；浏览器档位取证：06-benchmark/r2_dashboard_probe_2026-10-25.txt（agent-browser 只读快照））
- 读数型真调用（第 4 层）：**GAP_SERVICE**（读数面真实状态（未读到数））
    （取值：r201_r2_enable_face.py --json r2_enable_latest.json 的 state）
- 本月/当前用量：未量（未登记用量路径；未量不等于 0）
- 守它的判据：163 + 88 任务层 + 93
- 工作流触点：chaoshi-image-optimization 的 R2 外置专章（干跑读数 + 阻断现状）
- 触点在位核验（在位≠已接入）：chaoshi-image-optimization -> IN_SKILL_DESC
- 任务语句实测：
    - R2 开桶 -> MISS（top1=libreoffice-headless-win，期望件=chaoshi-image-optimization）

### Cloudflare-Pages - READY

- 两把尺：提到 5 件 ｜ 代码真调用 2 件
    提到 = A-project-handoff, byted-bp-cdn-pagesdeploy, chaoshi-image-optimization, chaoshi-web-deploy, verification-before-completion
    可执行 = A-project-handoff, byted-bp-cdn-pagesdeploy
    （取值：tool_skill_matrix_latest.json 的 per_tool / per_tool_exec[Cloudflare-Pages]；该件 generated_at=2026-10-28 17:10）
- 三层读数：
    ① skill 目录（第 67 门）：提到 5 ｜ 代码真调用 2
    ② 工作流脚本（第 94 门 r222 第二把尺，探针件不计入）：真调用 7
        调用它的非探针件 = r119_cand_regress.py, r119_cand_sandbox.py
    ③ 项目仓（第 67 门 r226 third_face，已剪 vendored 外来面）：250
        命中所在件 = act_part1.py, act_part2.py, add_deploy_note.py, add_ledger109.py, add_rows95.py, add_rows95b.py, admin_contrast_test.py, admin_responsive_test.py, admin_script.js, admin_static_render_test.py, analytics.js, cf_builds.py, cf_check.py, cf_check2.py, cf_check3.py, cf_check4.py, check-api-native-e2e.mjs, check-api-parity.mjs, check-catalog-facts.mjs, check-functions-build.mjs
        质量拆分：命中行 239，其中注释行 36（占比 0.151）
    （② 取值：workflow_usage_latest.json 的 tools[].real_hits，窗口面 177/297 件、真调用合计 95；
     ③ 取值：tool_skill_matrix_latest.json 的 third_face.per_tool，4358 件 / 2 仓 / 剪外来面 10 个）
- 读数型真调用（第 4 层）：**MEASURED**（读得到数）
    （取值：r200_pages_face.py --json pages_http_latest.json 的 row/state）
- 本月/当前用量：**236283 次**　窗口：2026-10-01~2026-10-29
    （取值：r200_pages_face.py --json pages_http_latest.json 的 row/requests_total）
- 守它的判据：163 + 92 + 93
- 工作流触点：chaoshi-web-deploy 部署权威入口（direct_map 10 pattern，任务话术直连命中）
- 触点在位核验（在位≠已接入）：chaoshi-web-deploy -> IN_SKILL_DESC
- 任务语句实测：
    - Pages 部署 -> HIT_DIRECT（top1=chaoshi-web-deploy，期望件=chaoshi-web-deploy）

### Cloudflare-Workers - READY

- 两把尺：提到 1 件 ｜ 代码真调用 0 件
    提到 = chaoshi-web-deploy
    可执行 = 无
    （取值：tool_skill_matrix_latest.json 的 per_tool / per_tool_exec[Cloudflare-Workers]；该件 generated_at=2026-10-28 17:10）
- 三层读数：
    ① skill 目录（第 67 门）：提到 1 ｜ 代码真调用 0
    ② 工作流脚本（第 94 门 r222 第二把尺，探针件不计入）：真调用 0
    ③ 项目仓（第 67 门 r226 third_face，已剪 vendored 外来面）：1
        命中所在件 = check-functions-build.mjs
        质量拆分：命中行 1，其中注释行 1（占比 1.0）⇒ **仅注释提及，不是在跑它**
    （② 取值：workflow_usage_latest.json 的 tools[].real_hits，窗口面 177/297 件、真调用合计 95；
     ③ 取值：tool_skill_matrix_latest.json 的 third_face.per_tool，4358 件 / 2 仓 / 剪外来面 10 个）
- **零层归因：[口径盲区]** 我的真实用法是**读数型**：走 CF GraphQL analytics 读调用数（token 见证据件），而形态级正则只认部署形态的三类写法 ⇒ 它看不见读数型搭配（不为此写假调用凑数）
    （取值：python 05-exec/r199_workers_face.py --json 06-benchmark/workers_quota_latest.json（真跑 MEASURED）；token workersInvocationsAdaptive 见该件 L50/L108）
- 读数型真调用（第 4 层）：**MEASURED**（读得到数）
    （取值：r199_workers_face.py --json workers_quota_latest.json 的 row/state）
- 本月/当前用量：**0 次**　窗口：2026-10-01~2026-10-29
    （取值：r199_workers_face.py --json workers_quota_latest.json 的 row/invocations_month）
- 守它的判据：163 + 88 任务层 + 93
- 工作流触点：A-memory-start 的 quickref 额度专章（r199_workers_face 现读调用数）；跨 zone 聚合分母差异已写 §9.16
- 触点在位核验（在位≠已接入）：A-memory-start -> MENTIONS
- 触点在位核验（在位≠已接入）：r199_workers_face（判据件） -> GATE_FILE_MENTIONS
- 任务语句实测：
    - Workers 调用量 -> HIT（top1=A-memory-start，期望件=A-memory-start）

### SQLite - READY

- 两把尺：提到 4 件 ｜ 代码真调用 3 件
    提到 = data-analysis, fenjue-memory-audit, ican-deploy, web-access
    可执行 = data-analysis, fenjue-memory-audit, web-access
    （取值：tool_skill_matrix_latest.json 的 per_tool / per_tool_exec[SQLite]；该件 generated_at=2026-10-28 17:10）
- 三层读数：
    ① skill 目录（第 67 门）：提到 4 ｜ 代码真调用 3
    ② 工作流脚本（第 94 门 r222 第二把尺，探针件不计入）：真调用 24
        调用它的非探针件 = r203_ledger_index.py
    ③ 项目仓（第 67 门 r226 third_face，已剪 vendored 外来面）：127
        命中所在件 = 0001_init.sql, 0002_admin.sql, [[path]].js, actionAuthz.test.js, backup-print-data.mjs, backupPrintData.test.js, backupRestore.test.js, catalogFacts.test.js, check-action-authz.mjs, check-d1-roundtrips.mjs, check-governance-framework.mjs, check-pii-inventory.mjs, check-schema-drift.mjs, ciWorkflow.test.ts, d1-quota.mjs, d1RoundTrips.test.js, metered-d1.mjs, migrate-ai-calls.sql, migrate-event-log.sql, migrate-promotions.sql
        质量拆分：命中行 115，其中注释行 16（占比 0.139）
    （② 取值：workflow_usage_latest.json 的 tools[].real_hits，窗口面 177/297 件、真调用合计 95；
     ③ 取值：tool_skill_matrix_latest.json 的 third_face.per_tool，4358 件 / 2 仓 / 剪外来面 10 个）
- 读数型真调用（第 4 层）：**MEASURED**（读得到数）
    （取值：r243_sqlite_usage_face.py --json sqlite_usage_latest.json 的 state）
- 本月/当前用量：**13.13 MiB（本地库体量·非额度）**（合计行数 45745）　窗口：2026-10-28T17:13:03
    （取值：r243_sqlite_usage_face.py --json sqlite_usage_latest.json 的 size_mib）
- 守它的判据：163 + 85 + 93
- 工作流触点：r203_ledger_index 用 SQLite 做门禁台账派生索引（读面与盲区均实测）
- 触点在位核验（在位≠已接入）：r203_ledger_index（判据件） -> GATE_FILE_MENTIONS
- 任务语句实测：名册无对应条目（不编造）

### VS Code - READY

- 两把尺：提到 7 件 ｜ 代码真调用 1 件
    提到 = A-java-problem, A-project-handoff, c-cleanup, cloudbase, computer-use-guidance-windows, discover-agent-cli, electron
    可执行 = A-project-handoff
    （取值：tool_skill_matrix_latest.json 的 per_tool / per_tool_exec[VS Code]；该件 generated_at=2026-10-28 17:10）
- 三层读数：
    ① skill 目录（第 67 门）：提到 7 ｜ 代码真调用 1
    ② 工作流脚本（第 94 门 r222 第二把尺，探针件不计入）：真调用 0
    ③ 项目仓（第 67 门 r226 third_face，已剪 vendored 外来面）：0
    （② 取值：workflow_usage_latest.json 的 tools[].real_hits，窗口面 177/297 件、真调用合计 95；
     ③ 取值：tool_skill_matrix_latest.json 的 third_face.per_tool，4358 件 / 2 仓 / 剪外来面 10 个）
- **零层归因：[桌面 GUI 承载（非调用面）]** ('已入尺（第 67 门现含 VS Code 模式）。承载点在技能手册层：A-java-problem 的验收步骤要求人跑', 'VS Code GUI（Ctrl+Shift+B → F5 停 main() 退出码 0），并沉淀了两个 GUI-only 坑；', '工作流侧本就无调用面 —— 我的产出是文件与提交，不需要开编辑器。CLI（code）在机，', '但可用不等于该用：不为把计数做非零而写假调用。')
    （取值：python 05-exec/r163_tool_skill_matrix.py --json 件（per_tool['VS Code'] = 提到/代码级两把尺）；承载原文：D:/global_skills/A-java-problem/log/iteration-log.md 的 2026-10-12 C++ 条目）
- 读数型真调用（第 4 层）：无读数面 —— 编辑器本体，无平台额度概念 ⇒ （用量 = 装机与扩展，属桌面侧，未入本尺）（无读数面 ≠ 0）
- 本月/当前用量：未量（未登记用量路径；未量不等于 0）
- 守它的判据：163 + 93
- 工作流触点：r163_free_tools_face 的 probe_vscode（which + 非 0 字节 + 真跑 --version）
- 触点在位核验（在位≠已接入）：r163_free_tools_face（判据件） -> GATE_FILE_MENTIONS
- 任务语句实测：名册无对应条目（不编造）

### Cloudflare-Turnstile - READY

- 两把尺：提到 3 件 ｜ 代码真调用 0 件
    提到 = A-memory-start, chaoshi-image-optimization, win-toolchain-pitfalls
    可执行 = 无
    （取值：tool_skill_matrix_latest.json 的 per_tool / per_tool_exec[Cloudflare-Turnstile]；该件 generated_at=2026-10-28 17:10）
- 三层读数：
    ① skill 目录（第 67 门）：提到 3 ｜ 代码真调用 0
    ② 工作流脚本（第 94 门 r222 第二把尺，探针件不计入）：真调用 27
        调用它的非探针件 = r163_turnstile_admin.py, r209_route_truth_measure.py, r247_dup_policy_scan.py, r250_source_freshness_scan.py
    ③ 项目仓（第 67 门 r226 third_face，已剪 vendored 外来面）：3
        命中所在件 = backend.js, client.ts, errorSemantics.test.js
        质量拆分：命中行 3，其中注释行 3（占比 1.0）⇒ **仅注释提及，不是在跑它**
    （② 取值：workflow_usage_latest.json 的 tools[].real_hits，窗口面 177/297 件、真调用合计 95；
     ③ 取值：tool_skill_matrix_latest.json 的 third_face.per_tool，4358 件 / 2 仓 / 剪外来面 10 个）
- 读数型真调用（第 4 层）：**MEASURED**（读得到数）
    （取值：r242_turnstile_usage_face.py --json turnstile_usage_latest.json 的 state）
- 本月/当前用量：**0 次（校验请求）**　窗口：['2026-10-03', '2026-10-28']
    （取值：r242_turnstile_usage_face.py --json turnstile_usage_latest.json 的 count_total）
- 守它的判据：163 + 88 任务层(DISPUTED) + 93
- 工作流触点：r163_turnstile_face 与 r163_turnstile_admin 曾全链接通，后按老大要求移除 = 决定而非待搭缺口
- 触点在位核验（在位≠已接入）：r163_turnstile_admin（判据件） -> GATE_FILE_MENTIONS
- 触点在位核验（在位≠已接入）：r163_turnstile_face（判据件） -> GATE_FILE_MENTIONS
- 任务语句实测：
    - Turnstile -> DISPUTED（top1=codebuddy-chat-web，期望件=chaoshi-image-optimization）

### Resend - GAP_CRED

- 两把尺：提到 1 件 ｜ 代码真调用 1 件
    提到 = office-automation-pro
    可执行 = office-automation-pro
    （取值：tool_skill_matrix_latest.json 的 per_tool / per_tool_exec[Resend]；该件 generated_at=2026-10-28 17:10）
- 三层读数：
    ① skill 目录（第 67 门）：提到 1 ｜ 代码真调用 1
    ② 工作流脚本（第 94 门 r222 第二把尺，探针件不计入）：真调用 0
    ③ 项目仓（第 67 门 r226 third_face，已剪 vendored 外来面）：0
    （② 取值：workflow_usage_latest.json 的 tools[].real_hits，窗口面 177/297 件、真调用合计 95；
     ③ 取值：tool_skill_matrix_latest.json 的 third_face.per_tool，4358 件 / 2 仓 / 剪外来面 10 个）
- 读数型真调用（第 4 层）：无读数面 —— 有月度额度（免费 3000 封）但**全机无凭据**（env 0 命中、.env/.dev.vars 键名与它无关、全 workspace grep 只命中我自己的旧门产物）；档位 2 可打开发 signup 但需账号持有人建号+条款同意 ⇒ #29 例外类（凭据缺口 ∧ 第三方账号授权），不是没有读数面（无读数面 ≠ 0）
- 本月/当前用量：未量（未登记用量路径；未量不等于 0）
- 守它的判据：163 + 93
- 工作流触点：r163_tool_skill_matrix 已把它列入零引用核查面；仅 HTTP API 无 CLI，凭据缺 ⇒ 尚未接入任何工作流
- 触点在位核验（在位≠已接入）：r163_tool_skill_matrix（判据件） -> GATE_FILE_MENTIONS
- 任务语句实测：名册无对应条目（不编造）

### Upstash-Redis - GAP_CRED

- 两把尺：提到 0 件 ｜ 代码真调用 0 件
    提到 = 无
    可执行 = 无
    （取值：tool_skill_matrix_latest.json 的 per_tool / per_tool_exec[Upstash-Redis]；该件 generated_at=2026-10-28 17:10）
- 三层读数：
    ① skill 目录（第 67 门）：提到 0 ｜ 代码真调用 0
    ② 工作流脚本（第 94 门 r222 第二把尺，探针件不计入）：真调用 0
    ③ 项目仓（第 67 门 r226 third_face，已剪 vendored 外来面）：0
    （② 取值：workflow_usage_latest.json 的 tools[].real_hits，窗口面 177/297 件、真调用合计 95；
     ③ 取值：tool_skill_matrix_latest.json 的 third_face.per_tool，4358 件 / 2 仓 / 剪外来面 10 个）
- **零层归因：[外部凭据缺口]** 仅有 REST 无 CLI，且本机未配 UPSTASH_* 凭据 ⇒ 无法接入；这是凭据缺口，不是搭配意愿问题
    （取值：python 05-exec/r163_free_tools_face.py --json 06-benchmark/free_tools_latest.json（该工具 state=GAP_CRED））
- 读数型真调用（第 4 层）：无读数面 —— 有月度额度（免费 50 万命令）但**全机无凭据**（同上探查）；档位 2 console 探查挂起后已终止，该通道结论不依赖它 ⇒ 凭据缺口，不是没有读数面（无读数面 ≠ 0）
- 本月/当前用量：未量（未登记用量路径；未量不等于 0）
- 守它的判据：163 + 93
- 工作流触点：r163_tool_skill_matrix 报其零引用（唯一 ADVISORY 项）；仅 REST 无 CLI，凭据缺 ⇒ 未接入
- 触点在位核验（在位≠已接入）：r163_tool_skill_matrix（判据件） -> GATE_FILE_MENTIONS
- 任务语句实测：名册无对应条目（不编造）

