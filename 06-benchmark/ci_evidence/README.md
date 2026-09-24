# ci_evidence/ — 对手 workflow 原文留档（r31 第八维证据件）

**用途**：r31 新增对标维度「自动化验收面」的**实物证据**。此前 13 轮读的是对手 README，
本轮改读其 `.github/workflows/*.yml` 原文，逐行核实「判据到底在哪里执行」。
保留原文是为让后续会话能复验本报告的每一条引用，而不是只能引用我的转述。

**来源与许可**（均为 GitHub 公开仓的仓库内文件，经 `gh api` 以只读方式取得）：

| 文件 | 来源 | 取得方式 |
|---|---|---|
| `mycelium_behavioral-install-eval.yml` | `mycelium-hq/ai-brain-starter` @ main | `gh api repos/mycelium-hq/ai-brain-starter/contents/.github/workflows/<f> --jq .content` 后接 base64 解码 |
| `mycelium_release-drift-heartbeat.yml` | 同上 | 同上 |
| `mycelium_template-purity.yml` | 同上 | 同上 |
| `mycelium_personal-pii-scrub.yml` | 同上 | 同上 |
| `aas_ci.yml` / `aas_skill-review.yml` / `aas_repo-hygiene.yml` | `sickn33/agentic-awesome-skills` @ main | 同上（owner/repo 替换） |
| `addyosmani_test-plugin-install.yml` | `addyosmani/agent-skills` @ main | 同上 |

**取数时间**：2026-09-25 05:2x–05:3x（各仓 `pushed_at` 见 `../ci_surface_r31_2026-09-25.json`）。

**使用铁律（本仓口径）**：引用其中任何一句作为「对手做法」时，必须写明**文件路径 + 行内原文**，
不得写成「某项目有 XX」。r31 正是靠这条把常驻页落后项 #6 判定为误引（详见报告 §1.2② 与 §7.5）。
本目录文件为**第三方原件副本**，不属本仓资产，禁止就地编辑；需要新版本请重新取数并另存带日期件。
