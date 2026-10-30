# 需求 6 执行级可复算面 · 两态字面命令真跑 A/B（R285-L）· 2026-10-30

> 结论标记：**已实测** —— test-driven-development 与 frontend-slides 两件本运行真跑，ui-ux-pro-max 一件引用 Lead 读数。

这一件量的不是「文档写得好不好」，而是「文档里字面写出来的命令，在这台机器上按原样能不能跑、跑完有没有真的把东西落到盘上」。
做法：取改前/改后两份 SKILL.md 文本（只读 git show），从文本里抽字面命令（查询型 --help / --version / whoami 不进分母）。
每条命令的 argv 手工硬列在 _repro/r285l/r285_cmds.json，绝不按空白切词（r281 就是这么把 -p 带空格的项目名拆坏造成假红）。
占位符按文中语义换成真实输入（本运行现造 2 页 .pptx 与 2 页 HTML deck），每个臂用自己独立且跑前清空的输出目录。

## 1. 总表（三件并列）

| 件 | 改前 ref | 改后 ref | 来源 | 臂 | 字面命令 | 实跑 | 工具链缺 | 需外部账号 | rc=0 | 占位未解 | 落盘件数 | 声明兑现 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **ui-ux-pro-max** | `30b84b20~1` | `30b84b20` | CITED, NOT RE-RUN: Lead reading of 2026-10-29 (r281 caliber: --help probe counts in the denominator) | A | 1 | 1 | 0 | 0 | **0** | 0 | 0 | N |
|  |  |  |  | B | 2 | 2 | 0 | 0 | **1** | 0 | 1 | Y |
| **test-driven-development** | `079b91f3~1` | `079b91f3` | MEASURED IN THIS RUN (R285-L) | A | 4 | 3 | 1 | 0 | **3** | 0 | 0 | Y |
|  |  |  |  | B | 4 | 3 | 1 | 0 | **3** | 0 | 0 | Y |
| **frontend-slides** | `3681df5e` | `89efb3e6` | MEASURED IN THIS RUN (R285-L) | A | 7 | 5 | 0 | 2 | **3** | 0 | 5 | Y |
|  |  |  |  | B | 7 | 5 | 0 | 2 | **3** | 0 | 5 | Y |

三件汇总（与判据末行同形）：`rows=3 commands_ok=7/13 artifacts_before=5 artifacts_after=6`

**怎么读这张表**：test-driven-development 与 frontend-slides 两件的改前/改后读数**逐项相等**。这不是测量失败，而是这两次改动本身没碰命令面。
diff 显示前者只多了一行指向 writing-good-tests.md 的插入行（无新命令）；后者的改动全在版式规则（100vh 改为固定 1920x1080 舞台）、模板包指针与版本历史。
三个脚本本体两态 sha256 完全相同：extract-pptx.py 4f5e7603c99b / deploy.sh 74a1103519a6 / export-pdf.sh 16336202904f。
所以「字面命令集、实跑数、rc=0、落盘件数、声明兑现」五项全部相同。r281 那件有 +22.22% 是因为它新增了一条真能跑且真能持久化的命令；这两件没有这类新增。
> 取值：`node _repro/r285l/r285_validate.mjs`（期望末行 `[EXEC-AB] rows=3 commands_ok=7/13
> artifacts_before=5 artifacts_after=6`；注意**不要**带 `-B`，本机 node 拒绝该选项 rc=9）。
> 逐件读数与两处 PDF 体积读 `06-benchmark/r285_exec_commands_ab.json` 的
> rows[skill=frontend-slides].arms.B.persisted_artifacts（每项自带 bytes）与 doc_claim_sub。


**与两态无关的一条脚本级实测事实**（两臂同形，故不进差值）：export-pdf.sh 按文中字面把 output.pdf 占位写成相对路径时 rc=1，且产物被它自己的清理步骤删掉——脚本先 cd 进 mktemp 目录再跑 node，相对的 OUTPUT_PDF 落进临时目录，随后 rm -rf。同一命令把占位符解析成绝对路径即 rc=0 并真落盘（20979B / 13958B）。即文档字面写法在本机不成立，改前改后都不成立。
deploy.sh 两臂都停在 Vercel 登录引导之后 connect ETIMEDOUT（本机无该账号凭据，本运行不创建外部凭据），记为环境边界：不计入 rc_zero，也不计为文档缺陷。

## 2. 口径（分子分母写死，与 JSON 的 caliber_note 同源）

- **commands_found**：count of distinct literal command strings the extractor finds in THAT arm's SKILL.md text (triggers: python/python3/py, bash scripts/*.sh, npm test, pytest, cargo test, pip install, npx, open [), after removing inline-code backticks and dropping query-only forms (--help / --version / whoami / login). Denominator of every ratio in this file.
- **runnable**：of those commands, how many were actually executed on this machine. A command whose toolchain is absent (cargo) is counted in commands_found and in blocked_not_runnable, and NEVER in runnable, rc_zero or artifacts.
- **rc_zero**：numerator = number of runnable commands whose operative exit code was 0 in their normal (expected-to-pass) state. Expected-failure probes (state=RED, the doc's own Verify RED step) are excluded from the numerator and are reported separately as evidence for doc_claim_met.
- **operative_rc**：argv_resolved when cmdspec declared one (bare pytest is not on PATH in the managed venv), else argv_literal. Both argv lists are in detail_rows.
- **needs_external_account**：commands whose script reaches a third-party account gate before it can produce anything (deploy.sh: prints the Vercel login guide, then blocks on connect ETIMEDOUT). Counted in commands_found, excluded from runnable / rc_zero / artifacts, and never counted as a doc defect: this run creates no external credential.
- **variant_rows**：rows with primary === false are extra runs of the SAME doc literal with a different placeholder resolution (export-pdf with an absolute output path). They are evidence for the sub-claims and are NOT counted in commands_found, runnable, rc_zero or artifacts.
- **placeholder_unresolved**：commands whose placeholders could not be resolved to a real input. All were resolved in this run (fixture .pptx and deck.html were built for it), so this is 0 everywhere; nothing is silently counted as failure.
- **persisted_artifacts**：files newly appearing in that arm's OWN declared output directories, which are wiped before the arm runs and never shared between arms (the r283 contamination lesson). Paths are relative to the arm directory.
- **doc_claim_met**：binary. test-driven-development: the doc worked example must fail before the feature exists (RED rc!=0) and pass after (GREEN rc=0). frontend-slides: extracted-slides.json written by the doc-literal extract command must contain >=2 slides; the PDF half is reported separately as sub-claims (relative form vs absolute form) because the two differ. ui-ux-pro-max (cited): >=1 doc-literal command returning rc=0 that persists a design-system artifact.
- **unverified_rule**：any arm whose commands could not be executed at all is reported UNVERIFIED with the command and its stderr and is excluded from both sides of every delta.
- **not_measured**：this file measures executability and persistence only. It does not measure business quality, does not re-run the ui-ux-pro-max pair, and does not judge whether the produced artifacts are good.

## 3. 逐件逐命令明细

### ui-ux-pro-max

- 改前 `30b84b20~1` / 改后 `30b84b20`；来源：CITED, NOT RE-RUN: Lead reading of 2026-10-29 (r281 caliber: --help probe counts in the denominator)
- 引用读数（不在本件复算）：`Q_A=18 Q_B=22 uplift=22.22%`，出处 `r281_execution_ab.json` + `执行级AB_r281_2026-10-29.md`
- ref 对账：brief 给的改前/改后对（3c72867d / 3da30832）与 Lead 实测所用对（30b84b20~1 / 30b84b20）不同：四个 SKILL.md blob 互异（git rev-parse 实测 c13098fa / 60e20aa0 / 2c2500e5 / 8a371876）。本行引用的是 Lead 已核的那一对，brief 那一对本运行未复跑，标 未实测。

> 引用行：本运行未复跑，逐条出处见 r281 两件（执行级AB_r281_2026-10-29.md 第 3 节维 3）。

### test-driven-development

- 改前 `079b91f3~1` / 改后 `079b91f3`；来源：MEASURED IN THIS RUN (R285-L)
- 本件机械判定的文档声明：Verify RED then Verify GREEN: the worked example test must fail before the feature exists and pass after it does.
- 臂文本：A `sha12=8ee8a57d45a2 / 11635B` ｜ B `sha12=e970555276c3 / 11760B`
- 查询型已排除（不进分母）：A [] ｜ B []

#### 臂 A —— 4 条字面命令 / 5 次实跑（其中变体 0 次）

| # | 文中字面命令（状态） | 实跑 argv 尾段 | rc | stdout B | 新落盘 | 备注 |
|---|---|---|---|---|---|---|
| 1 | `npm test path/to/test.test.ts`（RED） | `C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js test path/to/test.test.ts` | 1 | 1016 | 0 |  |
| 2 | `npm test path/to/test.test.ts`（GREEN） | `C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js test path/to/test.test.ts` | 0 | 211 | 0 |  |
| 3 | `npm test`（normal） | `Program Files/nodejs/node.exe C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js test` | 0 | 191 | 0 |  |
| 4 | `pytest`（normal） | `C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe -m pytest` | 0 | 501 | 0 |  |
| 5 | `cargo test`（normal） | `cargo test` | ENOENT/ENOENT | 0 | 0 | TOOLCHAIN-ABSENT: cargo not installed on this machine (probe rc/spawn error recorded in results). Not counted in runnable, rc_zero or artifacts. |

- 该臂声明输出目录新落盘：无（这些命令只报告结果、不落工件）
- 声明兑现：Y —— RED rc=1 / GREEN rc=0; test body is the doc worked example (rejects empty email)

#### 臂 B —— 4 条字面命令 / 5 次实跑（其中变体 0 次）

| # | 文中字面命令（状态） | 实跑 argv 尾段 | rc | stdout B | 新落盘 | 备注 |
|---|---|---|---|---|---|---|
| 1 | `npm test path/to/test.test.ts`（RED） | `C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js test path/to/test.test.ts` | 1 | 1015 | 0 |  |
| 2 | `npm test path/to/test.test.ts`（GREEN） | `C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js test path/to/test.test.ts` | 0 | 212 | 0 |  |
| 3 | `npm test`（normal） | `Program Files/nodejs/node.exe C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js test` | 0 | 191 | 0 |  |
| 4 | `pytest`（normal） | `C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe -m pytest` | 0 | 501 | 0 |  |
| 5 | `cargo test`（normal） | `cargo test` | ENOENT/ENOENT | 0 | 0 | TOOLCHAIN-ABSENT: cargo not installed on this machine (probe rc/spawn error recorded in results). Not counted in runnable, rc_zero or artifacts. |

- 该臂声明输出目录新落盘：无（这些命令只报告结果、不落工件）
- 声明兑现：Y —— RED rc=1 / GREEN rc=0; test body is the doc worked example (rejects empty email)

### frontend-slides

- 改前 `3681df5e` / 改后 `89efb3e6`；来源：MEASURED IN THIS RUN (R285-L)
- 本件机械判定的文档声明：Phase 4 declares PPTX extraction to slide titles, content summaries and image counts; Phase 6B declares an HTML to PDF deliverable.
- 臂文本：A `sha12=e76ddd898d42 / 20073B` ｜ B `sha12=6b9b0953aa26 / 23312B`
- 查询型已排除（不进分母）：A ["npx vercel --version","npx vercel whoami"] ｜ B ["npx vercel --version","npx vercel whoami"]

#### 臂 A —— 7 条字面命令 / 9 次实跑（其中变体 2 次）

| # | 文中字面命令（状态） | 实跑 argv 尾段 | rc | stdout B | 新落盘 | 备注 |
|---|---|---|---|---|---|---|
| 1 | `npx playwright install chromium`（normal） | `playwright install chromium` | 0 | 0 | 0 |  |
| 2 | `pip install python-pptx`（normal） | `pip install python-pptx` | 0 | 739 | 0 |  |
| 3 | `python scripts/extract-pptx.py <input.pptx> <output_dir>`（normal） | `scripts/extract-pptx.py fixture.pptx out_extract` | 0 | 153 | 3 |  |
| 4 | `bash scripts/deploy.sh <path-to-presentation>`（normal） | `C:/Program Files/Git/bin/bash.exe scripts/deploy.sh my-deck` | SIGNAL:SIGTERM/ETIMEDOUT | 835 | 0 | 需外部账号（环境边界，非文档缺陷） |
| 5 | `bash scripts/deploy.sh ./my-deck/`（normal） | `C:/Program Files/Git/bin/bash.exe scripts/deploy.sh ./my-deck/` | SIGNAL:SIGTERM/ETIMEDOUT | 835 | 0 | 需外部账号（环境边界，非文档缺陷） |
| 6 | `bash scripts/export-pdf.sh <path-to-html> [output.pdf]`（normal） | `scripts/export-pdf.sh my-deck/index.html out_pdf/deck.pdf` | 1 | 7793 | 0 |  |
| 7 | `bash scripts/export-pdf.sh <path-to-html> [output.pdf] --compact`（normal） | `my-deck/index.html out_pdf_compact/deck.pdf --compact` | 1 | 1026 | 0 |  |
| 8 | `bash scripts/export-pdf.sh <path-to-html> [output.pdf]`（normal） | `Users\37533\Desktop\workspace\skill焚诀\自建skill优化\_temp\r285l\work\run\fs_A/out_pdf/deck.pdf` | 0 | 1382 | 1 | 变体：占位符改绝对路径 |
| 9 | `bash scripts/export-pdf.sh <path-to-html> [output.pdf] --compact`（normal） | `p\workspace\skill焚诀\自建skill优化\_temp\r285l\work\run\fs_A/out_pdf_compact/deck.pdf --compact` | 0 | 1466 | 1 | 变体：占位符改绝对路径 |

- 该臂声明输出目录新落盘：`out_extract/assets/slide1_img1.png (54B)` `out_extract/assets/slide2_img1.png (54B)` `out_extract/extracted-slides.json (675B)` `out_pdf/deck.pdf (20979B)` `out_pdf_compact/deck.pdf (13958B)`
- 声明兑现：Y —— extracted-slides.json slides=2; out_pdf/deck.pdf=true; out_pdf_compact/deck.pdf=true size=20979B compact size=13958B
- 子声明（逐项机械判定）：{"pptx_extract_met":"Y","pdf_export_relative_form_met":"N","pdf_export_absolute_form_met":"Y","deploy_met":"N (needs a logged-in Vercel account: both deploy rows reach the login guide then block on connect ETIMEDOUT; environment boundary, not a doc defect)"}

#### 臂 B —— 7 条字面命令 / 9 次实跑（其中变体 2 次）

| # | 文中字面命令（状态） | 实跑 argv 尾段 | rc | stdout B | 新落盘 | 备注 |
|---|---|---|---|---|---|---|
| 1 | `npx playwright install chromium`（normal） | `playwright install chromium` | 0 | 265 | 0 |  |
| 2 | `pip install python-pptx`（normal） | `pip install python-pptx` | 0 | 739 | 0 |  |
| 3 | `python scripts/extract-pptx.py <input.pptx> <output_dir>`（normal） | `scripts/extract-pptx.py fixture.pptx out_extract` | 0 | 153 | 3 |  |
| 4 | `bash scripts/deploy.sh <path-to-presentation>`（normal） | `C:/Program Files/Git/bin/bash.exe scripts/deploy.sh my-deck` | SIGNAL:SIGTERM/ETIMEDOUT | 835 | 0 | 需外部账号（环境边界，非文档缺陷） |
| 5 | `bash scripts/deploy.sh ./my-deck/`（normal） | `C:/Program Files/Git/bin/bash.exe scripts/deploy.sh ./my-deck/` | SIGNAL:SIGTERM/ETIMEDOUT | 835 | 0 | 需外部账号（环境边界，非文档缺陷） |
| 6 | `bash scripts/export-pdf.sh <path-to-html> [output.pdf]`（normal） | `scripts/export-pdf.sh my-deck/index.html out_pdf/deck.pdf` | 1 | 942 | 0 |  |
| 7 | `bash scripts/export-pdf.sh <path-to-html> [output.pdf] --compact`（normal） | `my-deck/index.html out_pdf_compact/deck.pdf --compact` | 1 | 1026 | 0 |  |
| 8 | `bash scripts/export-pdf.sh <path-to-html> [output.pdf]`（normal） | `Users\37533\Desktop\workspace\skill焚诀\自建skill优化\_temp\r285l\work\run\fs_B/out_pdf/deck.pdf` | 0 | 1382 | 1 | 变体：占位符改绝对路径 |
| 9 | `bash scripts/export-pdf.sh <path-to-html> [output.pdf] --compact`（normal） | `p\workspace\skill焚诀\自建skill优化\_temp\r285l\work\run\fs_B/out_pdf_compact/deck.pdf --compact` | 0 | 1466 | 1 | 变体：占位符改绝对路径 |

- 该臂声明输出目录新落盘：`out_extract/assets/slide1_img1.png (54B)` `out_extract/assets/slide2_img1.png (54B)` `out_extract/extracted-slides.json (675B)` `out_pdf/deck.pdf (20979B)` `out_pdf_compact/deck.pdf (13958B)`
- 声明兑现：Y —— extracted-slides.json slides=2; out_pdf/deck.pdf=true; out_pdf_compact/deck.pdf=true size=20979B compact size=13958B
- 子声明（逐项机械判定）：{"pptx_extract_met":"Y","pdf_export_relative_form_met":"N","pdf_export_absolute_form_met":"Y","deploy_met":"N (needs a logged-in Vercel account: both deploy rows reach the login guide then block on connect ETIMEDOUT; environment boundary, not a doc defect)"}

## 4. 负向对照（两条腿，都有实测输出）

**腿 1 · 同文必同读**：已实跑：把 test-driven-development 的 B 臂文本换成 A 臂那份 `SUBSTITUTED:tdd_A.md` 之后，两臂读数逐字相等 **PASS**

臂 B 的 ref 写成 SUBSTITUTED 是显式说明它不再是 079b91f3。同一份文本必须给同一组读数；若这里不相等，说明尺子在按臂序或目录名打分，整表作废。

| 字段 | 臂 A（原改前文） | 臂 B（换成 A 那份） |
|---|---|---|
| commands_found | 4 | 4 |
| runnable | 3 | 3 |
| blocked_not_runnable | 1 | 1 |
| needs_external_account | 0 | 0 |
| rc_zero | 3 | 3 |
| placeholder_unresolved | 0 | 0 |
| persisted_artifacts | 0 | 0 |
| doc_claim_met | "Y" | "Y" |
| doc_claim_sub | null | null |
| executions | 5 | 5 |
| variant_executions | 0 | 0 |
| 文本 sha12 | 8ee8a57d45a2 | 8ee8a57d45a2 |

**腿 2 · 改 rc 必报 MISMATCH**：把某条命令的 rc 由 0 改成 1 写进交付件 JSON 的临时副本，再用同一把尺对副本重算，校验器必须点名 MISMATCH 字段。实测 stdout（副本用完即删）：

```text
[NEGCTL2] tampered field = ui-ux-pro-max.arms.B.rc_zero 1 -> 0
[NEGCTL2][validator] [NEGCTL-1] identical=true PASS: identical text -> identical readings, field by field
[NEGCTL2][validator] [MISMATCH ui-ux-pro-max.arms.B.rc_zero: stored=0 recomputed=1]
[NEGCTL2][validator] [EXEC-AB] rows=3 commands_ok=7/13 artifacts_before=5 artifacts_after=6
[NEGCTL2] validator_exit=2 named_field=YES copy_deleted=YES
[NEGCTL2] PASS: teeth confirmed (MISMATCH named, non-zero exit, copy removed)
```

## 5. 取文本、跑数与复算判据

```bash
git -C D:/global_skills show 079b91f3~1:test-driven-development/SKILL.md  (before)
git -C D:/global_skills show 079b91f3:test-driven-development/SKILL.md    (after)
git -C D:/global_skills show 3681df5e:frontend-slides/SKILL.md            (before)
git -C D:/global_skills show 89efb3e6:frontend-slides/SKILL.md            (after)
ui-ux-pro-max pair NOT re-run; readings copied from C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/06-benchmark/r281_execution_ab.json
cd C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化 && node _repro/r285l/r285_measure.mjs run
cd C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化 && node _repro/r285l/r285_validate.mjs   (this file's own recomputation gate)
cd C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化 && ONLY=tdd node _repro/r285l/r285_measure.mjs sub _repro/r285l/texts/tdd_A.md   (negative control 1)
cd C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化 && node _repro/r285l/r285_negctl2.mjs   (negative control 2, tamper then delete copy)
```

判据命令 = 重跑本件自己的脚本（不跑任何人的门），期望末行：

```text
[EXEC-AB] rows=3 commands_ok=7/13 artifacts_before=5 artifacts_after=6
```

**这是可执行性与持久化，不等于业务质量**：rc=0 与落盘件数只说明文档给了跑得通的路径，
不说明产出的设计系统、deck 或测试好不好看、能不能上线、用户是否买账；两件本臂实测差值为零，
也不代表这两次改动没有价值——它落在版式不变量与测试纪律上，那两条不在本件的尺子量程内。

measured_at：2026-10-29T23:54:14.436Z ｜ 证据文件 sha256：02eac5247643e2b61002b3437b8925a61242e1a2482a6e7c9bc738542daff38e
