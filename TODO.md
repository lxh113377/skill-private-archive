# TODO — 阶段状态总表（索引，**非入口**）

> **入口声明（2026-09-22 修正）**：跨会话**唯一入口 = `memory/07-next-steps.md`**（A-project-handoff 致命纪律 #1）。本文件只做「六阶段状态总表」，**不承载 P0** —— 此前本文件自称「唯一入口」，与 handoff 法定入口冲突，已消解。
> 更新：2026-09-22 | 当前阶段：**阶段0-4 完成，阶段5 进行中（三项已绿 / 两项未做）**
> 权威范围：`00-scope/自建skill清单.md` | 权威源：`D:\global_skills`（git）→ 镜像 `C:\Users\37533\.agents\skills`
> 三处分工（消三重同义源）：查「下一步做什么」→ `memory/07-next-steps.md`；查「哪个阶段到哪」→ 本表；查「上一轮干了啥」→ `05-exec/README.md`。

## 六阶段状态总表（2026-09-22 实测）

| 阶段 | 状态 | 产物 | 未闭环项 |
|---|---|---|---|
| 0 范围裁定 | ✅ 完成 | `00-scope/`（3 文件） | — |
| 1 四维机器扫描 | ⚠️ 部分 | `01-scan/`（4 文件） | `attention_sim.py` / `content_snr.py` / `negative_tag_audit.py` 未跑；缺「通配符引用」死链检测 |
| 2 全量精读 | ✅ 完成 | `02-review/`（6 份族卡，7 批） | — |
| 3 审计报告 | ✅ 完成 | `03-audit/`（P0 25 项分级） | — |
| 4 实施计划 + 执行 | ✅ 完成（4 批） | `04-plan/` + `05-exec/` | 批5 其余项（用户裁定「只做 b」，b 已完成） |
| 5 工作流专项 | 🚧 进行中 | `04-plan/工作流专项建议.md` | ① `direct_map` 误命中 ② 注册表 `user_created` 失真复核（基数待裁定） |
| 记忆层 | ✅ 建档（本轮回填） | `memory/` 8 文件 + 分卷 + P-1 | `archive/` 为空（归档机制从未执行） |

## 🔴 第 4 轮进度（2026-09-22）

- [x] **A-project-better 四维体检**（用户按钮选定口径）→ `05-exec/第3轮执行报告.md`：四源感知 + 5 项门禁实跑 + 四维诊断 + 10 条建议清单
- [x] **7 项非破坏性整改落盘**：07 主卷 P0 重写 + part1 销账 / 05 清失效阻塞 / 01-goal 勾选 / 02·03·04 回填 / 06 补 Bug·DEBT / 08 补 8 条真实 AC / 新增 `README.md` + `05-exec/README.md` + 第3轮报告
- [x] **门禁实测基线**：`handoff review` 5/9（56%）→ 本轮整改后复跑见第 3 轮报告；`rule_editor.py gates` 三门禁全绿；焚诀 `verify` **15 PASS / 0 FAIL / 0 SKIP**
- [x] **savepoint 一度被拒 → 已解除**：受管根 `焚诀\.codebuddy\`（**运行中 IDE 会话数据**，非交付物）未在 `.gitignore` 豁免 → `[GATE:noise-fail]`；并行会话 01:20:13 补 `焚诀\.gitignore`（commit `1f354e9`）后 `noise` = `[GATE:noise-pass]`，本项目 `savepoint` 复跑 **exit 0**。⚠️ 教训：活跃工具目录**不能**按 #17 字面迁 `_trash`
- [x] **D1 修 3 处门禁判据缺陷**（受管根 `7cc7d4d`，A-project-handoff **V3.42.0**）：假通过（AC 未剔注释）/ 假阴性（05 不认章节式）/ 口径矛盾（status≠review）；三函数下沉 `common.py` 单一真相源；层a 11/11 + 层b 含对照；本项目 `review` **56% → 100%**
- [x] **D2 阶段5 两项**（焚诀 `bf5e284`，已推送 SHA 一致）：① 直连表 —— 收窄 vp 过泛 pattern + **复扫 7 死目标 / 11 条死直连全数修正**，死目标归零、回归 **ALL PASS**；② 注册表 `user_created` 口径裁定为 **120 条**，「42 条失真」**不复现**，2 条真脏数据登记 P2
- [x] **D3 归档与轮转**：`.rule_backup` 40 → **35**（5 份迁 `_trash\backup-rotation\`）；`overlap_raw.txt`(283KB) → `archive/`
- [x] **D5 GM 日志空档留痕**：追加「R9 事故 · 每日日志空档说明（事后补记）」，**不补造当日日志**；`[GATE:evolution-pass]`
- [x] **D4 提交推送**：工作区 5 提交（`5c00034` / `b1801f7` / `c55d2ea` / `84ad487` / `9ca53f1`），逐路径白名单暂存；HEAD == `origin/main` ✅；status 干净
- [x] **① 阶段0 清单按 151 重出**：先修 `scan_all.py` 失效源（`platform-oc.json` 随 OC 退役被删 → 改在役端并集）；v1 三件原样归档 `archive/scope-v1-169-2026-09-14/`；v2 = **HIGH 51 / MID 26 / LOW 30 / EXCLUDE 43**（自建 **77**，失真 41）
- [x] **② 31 件入册**：摘除 `retired_skills` **100→69** → 注册表 **120→151** → `build_indexes --apply` 守恒 PASS；**顺带修 C6（GM note 引用 V1.22）与 C16（STATUS 家族内容过期，用生成器重出）** → 焚诀 `verify` **16 PASS / 0 FAIL**；双仓提交（焚诀 `28daf6e` / GM `575ca99`，SHA 一致）
- [x] **R269 落盘**（受管根 `f1e941a`，A-memory-start **V10.62.0**）：「同项门禁两入口结论不一致 → 先查对象 mtime + 仓库提交序 + 当下复跑，再谈判据缺陷」；伴生结论「活跃工具目录走 gitignore 豁免而非迁 `_trash`」；区内追加（区数 6 不变，落盘后 275 行 / 62,003B）
- [x] **④ A-project-handoff 工作流升级：删除 → 回收站**（受管根 `49789bb`，**V3.43.0**）：新增 `handoff_lib/recycle.py` + CLI `recycle`（`--list`/`--restore`）+ **致命纪律 #21** + `commands.md` §18；**系统回收站优先**（`FOF_ALLOWUNDO`）、**`_trash` 回落**、两路写 manifest + 还原指引；**防静默永久删除**（无回收站卷先探测再显式回落）；`audit forget` 硬删点改走回收站。验证 **18/18**（层a 含哈希级复原与两条反例 + 层b 真机实测 `method=recycle_bin`）
- 🔎 **本轮新发现**：GM 每日日志 09-09~09-20 空档 12 天（R9 事故未回填）；**skill 数口径更新为注册表 151 条**（磁盘含 SKILL.md 151 == 注册表，C1 全等）；31 件入册的**真实原因 = 退役黑名单未随「重装回磁盘」更新**；新入册 31 件在 `D:\global_skills` 仍是 `??` 未跟踪；**`rule_editor.py commit --fix-mirror` 未生效**（须手工 `check-skill-mirror.ps1 -Fix`）

## 🔴 第 3 轮进度（2026-09-19）

- [x] **批2 剩余 P0 单点修复（commit `eb77870`，7 文件 / 19 处补丁）**：P0-5 `chaoshi-image-optimization` ffmpeg 硬编码 `8.1.1`（实测已升 9.0 → 脚本必崩）→ 动态探测；P0-6 `fenjue-routing-health-check` CHECK-3 写死 `part1..4` → 动态枚举（实测 16 卷，旧文漏 12 卷致假阴性）；P0-10 `hook-analyzer`/`report-generator` 上游 `video-breakdown-skill` 不存在 → 标注悬空；P0-12 `openclaw-fenjue-weekly` 收尾门禁枚举 → 在役端 `OC/WB/TR/CX/HM`；P0-14 删 `A-memory-align` 死引用行
- [x] 三门禁 `mirror=pass noise=pass evolution=pass`；工作区仅剩他人 `github/_skillhub_meta.json`
- [x] **P0-2 残留收口（commit `4715713`，9 文件）**：`cross-platform-agent-sync` CC/QW 平台口径对齐在役端 `OC/WB/TR/CX/HM`（删 CC 平台表行/端口字典/启动文件段，QW 特例段改留痕，`5端/四端`→在役端）；v1.2.1→1.3.0
- [x] **P0-10 补建上游 `video-breakdown-skill`（commit `e145651`）**：新建分镜拆解 skill（机械层产 breakdown.json + 语义层留 agent）；端到端实测 3 分镜/9 关键帧，两个下游 exit 0；下游示例回填；两件 v1.0.1→1.0.2
- [x] **注册表重建（焚诀 `284cd75` / GM `6c0fc70`）**：磁盘 169 == 注册表 169（+video-breakdown-skill / +control-ui）；`session-logs` 补退役黑名单剔除解 fail-closed；守恒 PASS 169；路由器 top1 命中新 skill；`verify` 12 PASS / 2 FAIL（C13/C14 均非本轮引入）
- [ ] **下一轮首选**：阶段5 剩余 —— ① `direct_map` 误命中修正 ② 注册表 `user_created` 失真按当前 169 条重新实测复核
- [ ] **待裁定**：`story-*` 4 件平台名（判为上游结构性引用，建议保留原文）；遗留 10 文件复核中 3 条待逐条判断

## 🔴 第 2 轮进度（2026-09-14）

- [x] **批3.1 `A-project-handoff` 拆卷**：85,508B → 3,827B（≤4KB），`references/` 5 卷，内容零丢失 — commit `f8bc12f`
- [x] **拆卷回归修复 `V3.37.1`**：`coldstart --check` 因锚点迁出 SKILL.md 而 exit 1（会误拒所有项目 savepoint）→ `handoff.py cmd_coldstart` 加锚点回退链 — 实测 `✅ 6 行逐行 diff 全等`
- [x] 批4 元数据：`ican-frontend-design-system` 1.0.0→4.0.0；`dogfood`/`testing` 补 `version`
- [x] 校正记忆滞后：磁盘早于记忆已有 A1/A2/A3-A5/退役6件/批1/批2/批3其余 的提交，旧 P0「待用户确认」已失效
- [ ] **批1 剩余**：弃用平台名清理（`windows-cli-utf8-wrapper`/`discover-agent-cli`/`workflow-preflight-check`/`vp-perspective-audit` 等，需内容判断）
- [ ] **live bug**：`焚诀` 路由索引(09-10) 仍含 6 个已退役件（`skill-install` 实测为 top1）→ 需在焚诀完整重建派生件
- [ ] **待用户裁定**：①HM 平台口径双源冲突 ②灰区归属 ③批5 合并/退役逐项

## 阶段0 范围裁定 ✅ 已完成（2026-09-14）

**目标**：裁定「哪些算自建」，产出可信清单。
**验收**：三源交叉打分 + 硬排除市场信号 + 灰区单列 ✅ 达成

- [x] 定位权威源：`unified-skills-index.json`(174) / `platform-oc.json`(自建38) / `disk_manifest.json`(174) — 子代理实测
- [x] 实测基线：磁盘 169 目录、SKILL.md 合计 1.89MB、`A-project-handoff` 84KB 最大
- [x] 写 `01-scan/scan_all.py`（三源交叉 + 硬排除 + homepage 第四源）
- [x] 产出 `00-scope/自建skill清单.md` / `注册表失真条目.md` / `scope_result.json`
- [x] 项目记忆 init（10 文件 + P-1 绑定表）

**结论（2026-09-14 二次修正后）**：自建 **85**（HIGH 67 + MID 18）| EXCLUDE 54 | 灰区 LOW 30 | 注册表 `user_created` 失真 **36** 条

**二次修正说明（阶段2 精读反哺阶段0）**：原「本地原生+无 LICENSE+非 skillhub」判据不足以区分市场包——**市场包同样可无 LICENSE 地落在 `D:\global_skills`**。新增 4 类排除信号后重跑：
| 信号 | 命中 |
|---|---|
| `_meta.json`/`meta.json` 含 `ownerId`/`publishedAt`/`download_count` | deep-research-pro、multi-search-engine、sq-cleanmgr-c、github、ui-ux-pro-max、first-principles-decomposer、**local-asr/computer-use/realtime-translator/tts/txt2img** |
| `evals/evals.json`、`evaluations/` 官方评测件 | shadcn、knowledge-capture、meeting-intelligence、research-documentation、spec-to-implementation |
| frontmatter `name` 以 `notion-` 开头且与目录名错配 | （已由上一信号覆盖） |
| 精读人工判定 | electron、skill-install、taskflow、taskflow-inbox-triage |

**两处踩坑已修正（防回归）**：
1. `metadata.openclaw` 曾作独立排除信号 → **误伤 story-* 11 个**。该字段只表示「与 openclaw 兼容」，非「非自建」，已移除
2. 发布元数据初版含 `slug` → 过泛，已收窄为仅 `ownerId`/`publishedAt`/`download_count`

## 阶段1 四维机器扫描 ✅ 已完成（2026-09-14）

- [x] `scan_all.py --stage scan --apply` → `scan_report.md` + `scan_result.json`
- [x] `焚诀\audit\semantic_overlap_audit.py` → 重叠原始报告 `01-scan/overlap_raw.txt`
- [x] 两轮判据修正（死链 48→4 去跨项目误报；YAML `description: |` 多行块解析修正，弱触发 82→9）

**核心结论（102 个自建）**
| 维度 | 数据 |
|---|---|
| 体积 | 超 4KB **83/102（81%）**；`A-project-handoff` 84KB 且 refs=0 无分卷（最严重）、`chaoshi-web-deploy` 39KB refs=0、`openclaw-task-supervision` 33KB refs=0、`prompt-system-audit` 30KB refs=0 |
| 触发 | description <40 字 9 个；`sq-cleanmgr-c` **len=0（无 description，路由永不命中）**、`A-ask-questions` 29（核心 skill 偏短） |
| 死链 | **4 个（Test-Path 实测确认不存在）**：`story-setup` 引 scripts/generate-codex-agents.py + sync-opencode.py、`A-get-memory` 引 scripts/trace_view.py、`wps-knowledgebase` 引 references/workflow.md + scripts/run.js（该 skill 仅剩 SKILL.md）、`bigfile-split` 引 scripts/ic_parts_manifest.json |
| 弃用平台名 | 25 个命中 QW/QoderWork/QClaw/Claude Code/HM/Hermes（含 `hermes-installer` 正当引用 Hermes 的误报） |
| 合并候选 | 4 簇：审计路由族 5 个（sim 0.82-0.88）、story 长短篇 3 对（0.911/0.853/0.845）、清理族 c-cleanup↔sq-cleanmgr-c（0.872）、编码族 shell-encoding-pitfalls↔utf8-encoding-fix（0.803） |

**未完成 / 记入待办**
- [ ] `attention_sim.py`（注意力税蒙特卡洛）与 `content_snr.py`（信噪比）未实跑 — 参数已确认可用，待下轮
- [ ] `negative_tag_audit.py`（误命中）未跑
- [ ] 路由实测：`unified_router.py` 批量跑自建 skill 典型查询（已知 1 例误直连：审计查询 → `vp-perspective-audit`）

## 阶段2 全量精读 🚧 进行中（1/6 批，依赖阶段1）

按族分批，用 code-explorer 子代理并行，只回传审计卡：
- [x] **A族（5）** → `02-review/A族_精读.md`（2026-09-14）
  - 5/5 主文件全破 4KB 且零分卷（84,818 / 36,065 / 30,802 / 28,672 / 10,742 B）；全库 `*.part*.md` 实测 **0 个**，R199 拆卷从未作用于 skill 自身
  - A-project-handoff 84,818 B（20.7 倍）最严重，且它自己用 `split` 强制他处拆卷 → **双标 P0**
  - 新增死链 `A-get-memory` 引 `scripts/wf_*.ps1`（通配符，阶段1 正则未覆盖）
  - 版本元数据漂移：A-project-handoff 差 13 个版本（3.22.0 vs V3.35.0）
  - 平台弃用名残留 7 处（自身已声明四端=OC/WB/TR/CX 却未清理正文）
  - `.rule_backup/` 248 个 .bak、同日同文件 8 份，违反自家 R198.7（>5 份即轮转）
  - 闭环声明不齐：门禁 3/5、七步 3/5、footer 2/5
- [ ] fenjue族（5）+ 审计族（skill-* / prompt-system-audit ~10）
- [x] **local族（10）+ story族（11）** → `02-review/local族_精读.md`、`story族_精读.md`（2026-09-14）
  - **local：不整体合并**（与直觉相反）。判据三否：共享脚手架 8/10 但只能共享代码不能共享正文（各带 2-10GB 模型）；模态互斥，合并=10 倍注意力税；3 组触发冲突无法在单 description 内排序。执行：合并 2 组（img2img+txt2img→`local-image-gen`；vram→并入 computer-use）+ 抽 `_shared/local-runtime`（省 platform.exe 376KB×9 等 9 份重复）+ 薄路由 `local-router` 仲裁 OCR 三方
  - **story：只合并 1 对**（11→10）。`scan`(0.845) 纯平台参数 → 合并为 `story-scan --length=long|short`；`write`(**0.911 全库最高**) 与 `analyze`(0.853) **保留** —— 长篇状态机 vs 短篇单次成稿，且 analyze 有 6 个同名不同体 references，无法参数化。建议新增 ~2KB `story` 路由 skill
  - [P1] `agents_version: 22` 双写在 story-setup:18/39/222/230 与 story-review:39 → 封死升级；setup 硬编码「13 个 SKILL.md」实测仅 12
  - [P1] local-vram 文档与实现漂移：SKILL.md 无门禁但 run.ps1:50-53 会硬退；6/10 local meta.json 的 description 退化为字面量 `"|"`
- [ ] 其他族：chaoshi / ican / windows / openclaw / 9b / c-cleanup / wechat / wps 等
- [x] **fenjue族（5）** → `02-review/fenjue族_精读.md`（2026-09-14）
  - ~~**P0 崩溃级**：`fenjue-advisor-scoring` 核心评分门 = CC、`fenjue-cc-audit-cycle` 全流程"发 CC 审计" —— CC 已弃用 2026-09-08，二者**当前不可执行**~~
  - 🔄 **用户裁决（2026-09-14）：二者日常已不再使用** → 处置从「修 CC 恢复可用」改为 **退役候选**（走 skill-merge 的合并/归档路径，而非修复）。CC 崩溃问题随之失效，不再占用阶段 4 排期；但需确认是否有反向引用（见下条待办）
  - `fenjue-advisor-scoring`:265 自定"超 4KB 记 0 分"，自身 25.17KB 无分卷 → 自我击穿
  - `fenjue-routing-health-check`:227 指向不存在的 VERSION_LOCK.part2/3/4 → 执行得 **0 条假阴性**
  - 评分制三套并行：150分(advisor-scoring) / 160分(memory-audit) / 80分达标(cc-audit-cycle)
  - 5/5 无 footer、无七步闭环；advisor-scoring 连收尾门禁都没有
- [x] **审计族（15）** → `02-review/skill审计族_精读.md`（含**合并决策**）
  - **合并决策：15 → 8 顶层 + 3 references**，消除 5 组真重复 + 3 处门禁口径冲突
  - P0：`prompt-system-audit` 的 V8/V9 围绕不存在的 `common_prompts.md`（全盘 0 命中）；`data-layer-consistency-fix` 4 处注册表路径死链；`skill-trigger-diagnosis` 安全网脚本死链致 Phase4 全废
  - **路由误命中根因定位**：`vp-perspective-audit` 缺「何时不用我」负向边界（同族 hitrate-full-audit:19-23 有该列）+ description 含"适用于任何多 agent 系统" → 触发面覆盖全族
  - 15/15 超 4KB、无七步无 footer、9/15 无版本历史
- [x] **local族（10）+ story族（11）** → `02-review/local族_精读.md`、`story族_精读.md`（2026-09-14）
  - **local：不整体合并**（与直觉相反）。判据三否：共享脚手架 8/10 但只能共享代码不能共享正文（各带 2-10GB 模型）；模态互斥，合并=10 倍注意力税；3 组触发冲突无法在单 description 内排序。执行：合并 2 组（img2img+txt2img→`local-image-gen`；vram→并入 computer-use）+ 抽 `_shared/local-runtime`（省 platform.exe 376KB×9 等 9 份重复）+ 薄路由 `local-router` 仲裁 OCR 三方
  - **story：只合并 1 对**（11→10）。`scan`(0.845) 纯平台参数 → 合并为 `story-scan --length=long|short`；`write`(**0.911 全库最高**) 与 `analyze`(0.853) **保留** —— 长篇状态机 vs 短篇单次成稿，且 analyze 有 6 个同名不同体 references，无法参数化。建议新增 ~2KB `story` 路由 skill
  - [P1] `agents_version: 22` 双写在 story-setup:18/39/222/230 与 story-review:39 → 封死升级；setup 硬编码「13 个 SKILL.md」实测仅 12
  - [P1] local-vram 文档与实现漂移：SKILL.md 无门禁但 run.ps1:50-53 会硬退；6/10 local meta.json 的 description 退化为字面量 `"|"`
- [ ] 其他族：chaoshi / ican / windows / openclaw / 9b / c-cleanup / wechat / wps 等
- [ ] 产出 `02-review/` 六份审计卡

## 阶段3 审计报告 ⬜（依赖阶段2）
- [ ] `03-audit/自建skill优化审计报告.md`：四维结论 + 全量问题表（带实测命令与证据）+ P0/P1/P2 分级

## 阶段4 实施计划 ⬜（依赖阶段3）
- [ ] `04-plan/实施计划.md`：逐项 目标文件 / 改动 / 验证命令 / 回滚手段，按 P0→P1→P2 分批

## 阶段5 工作流专项 ⬜（依赖阶段4）
- [ ] 用 `data-layer-consistency-fix` 修 42 条 `user_created` 失真 + 死链 + orphan
- [ ] 用 `skill-merge` 评估 local-* / story-* / 审计族合并
- [ ] 七步闭环落地率 / footer 协议 / 三门禁（mirror·noise·evolution）
- [ ] direct_map 误命中修正（本会话实测：「优化自建skill」误直连 `vp-perspective-audit`）
- [ ] 收尾 `A-get-memory` 反哺

## 待人工裁定（阻塞项）

| # | 事项 | 阻塞什么 | 建议 |
|---|------|---------|------|
| 1 | LOW 灰区 33 个归属（github/gsap/obsidian-*/spike/story/browser-cdp 等） | 阶段2 精读范围 | 建议：带 homepage 的已排除；其余 31 个多为社区包，`story`/`browser-cdp` 需用户确认 |
| 2 | 42 条 `user_created` 失真是否直接改注册表 | 阶段5 | 改前须 `build_registry.py --apply` 重建派生件并复跑门禁 |
| ~~3~~ | ~~HM 口径冲突~~ | — | ✅ **已裁决 2026-09-14：用户确认「HM 又下回来了」** → HM 恢复为在役端；`hermes-installer`、`9b-lightworkflow` **保留**；扫描脚本弃用名单已移除 Hermes/HM |

## 已记录但未闭环的升级建议

- ✅ **已闭环（2026-09-14, commit `f2853ec`）**：`A-get-memory` Step 2.3.1 闭环语义修订 → **V4.25.0**（旧文「命中任一项 → 立即升级该技能」→ 改「本轮立即判断可否闭环（能改则改；不能改须写明阻塞点+登记待办，禁止只标"待定"）」）
- 🆕 **新发现（P1，待修）**：`rule_editor.py` 编号预检**跨文件版本体系误判** —— 提交 `A-get-memory` 的 V4.25.0 时，预检拿**全库最大 V10.28.0**（属 `A-memory-start`）作基准，fail-closed 拦截；实际各 skill 有独立版本线（A-get-memory 自有 V4.x）。已用 `--allow-collide` 放行（逃生门留痕 1 次）。**修法建议：预检基准改为「同文件版本历史最大号」，而非全库最大**

- ✅ **已闭环三连（2026-09-14）**：① `vp-perspective-audit` 补「何时不用本 skill」负向边界段 + 收窄 description + 删 `A-memory-align` 死链（**V1.2.0**）② `A-project-handoff` 冷启动声明与 Step 7 实际行为对齐（**V3.36.0**，`coldstart --check` 6 行逐行 diff 全等）③ `prompt-system-audit` V8 真相源校正（**V1.5.0**，`common_prompts.md` 实测 0 命中 → 改为在役真相源清单，保留判定逻辑）
- ✅ **已闭环（2026-09-14, commit `7f8287a`, R234）**：编号预检跨文件体系误判**已修复** —— V 基准由「全库最大」改为**按 major 分段**（新增 `v_by_major`），仅同 major 才判越界。三场景隔离测试全过：跨体系 V4.26.0 **放行**／同体系 V10.20.0 **仍拦**／V10.29.0 放行。修复后首次提交 `7f8287a` **正常放行，逃生门零新增**（此前被迫放行共 4 次）

- ✅ **已闭环（2026-09-14, commit `c3dba47`）**：`A-memory-start` Step 0.6 补 PowerShell `&` 调用符说明（本会话实测 ParserError）
- `vp-perspective-audit`：审计类查询直连过宽，建议收窄到审计族 skill
- ❌ **已撤销**：「A-project-handoff init 后补跑 A-get-memory Step 7 生成 EXPERIENCE.md」——实测 `A-get-memory/references/step7_project_handoff.md` V4.6.0 已降级（明令不再 Write 独立 EXPERIENCE.md，与 07 重叠）。原建议基于过时认知，撤销
- 🆕 **派生新条目（P2）**：`A-project-handoff` 的 init 冷启动声明（SKILL.md §1 + cmd_init 输出）仍写「新项目建议同步 A-get-memory Step 7 生成 EXPERIENCE.md 经验层」，**引用了已降级行为** → 应改为「读 handoff 07 即可，不落盘双份」。属跨 skill 双源漂移第 5 例

---

## 阶段4 执行进度（实际改动 `D:\global_skills`，2026-09-14 起）

### 本轮补充（2026-09-14 末）

| 项 | 内容 | 状态 | 证据 |
|---|---|---|---|
| **B5-1** | **57 个遗留未提交改动处置** | ✅ 完成 | 按来源分 3 个 commit：① `A-memory-start/references/contract.md`（R232 配套漏提交）`f2d9faf` ② `cloudbase__skillhub` 市场包升级 2.33.2→2.34.2 + 2 新文件 + `github` 元数据 ③ `A-java-problem` 1.2.0→1.2.1。**工作区 status=0 清零** |
| **B2** | **退役 6 个 skill** | ✅ 完成 | commit `716ae69`；`cloudbase-webapp-deploy-debug`／`deep-research-pro`／`multi-search-engine`／`skill-install`／`fenjue-advisor-scoring`／`fenjue-cc-audit-cycle`。**副本已于 2026-09-14 按用户要求彻底删除**（`_trash/retired-2026-09-14/` 目录已移除，**不可回滚**）；源端+镜像端均已删除；镜像 `[GATE:mirror-pass]` |
| **_trash 清理** | 退役副本彻底删除 | ✅ 完成 | `retired-2026-09-14/`（6 副本 104.2 KB）已删；⚠️ `_trash` 内另有本会话拆卷前的 3 个原始备份（`A-project-handoff_.rule_backup` 55.8KB、`bigfile-split.SKILL.md.*.bak` 15KB、`cross-platform-agent-sync.SKILL.md.*.bak` 19.6KB）→ 待你确认拆卷结果无误后可清 |
| **审计修正** | `notion-research-documentation` | 🔍 新发现 | 该 skill **已在 `_trash`**（51.3 KB，先前会话退役）→ 审计报告中「4 个 Notion 件空转」实际在役仅 **3 个**（`knowledge-capture`／`meeting-intelligence`／`spec-to-implementation`） |
| **引用清理** | 退役留下的 6 处活跃引用 | ✅ **4/6 已清** | ① `A-get-memory/scripts/sync_skill_router.py` 删 `skill-install` 与 `deep-research-pro` 清单项（**脚本**，已 `py_compile` 验证）② `A-project-handoff:170` 表格行标注退役 ③ `skill-hitrate-improvement-pipeline:94` 标注退役。**剩余 2 处判定为历史案例记录**（`fenjue-routing-health-check:37` 的 2026-07-10 周维护复盘、`step2_4_missed_audit.md:5/26` 的漏用教训举例）→ 改之属篡改历史，**保留原文**；如需防误导可后续加退役标注 |
| **A1** | `A-get-memory` 死链修复 | ✅ 完成 | commit `5bcb550`；4 处（`trace_view.py`×3 + `wf_*.ps1`×1）标注实测缺失并给替代路径；版本历史行不动 |
| **A2** | `openclaw-task-supervision` Qoder 通道 | ✅ 完成 | commit `b6bf36e`；Qoder 段加失效警告（2026-08-01 已卸载），保留原文作设计参考 |
| **A3** | ~~14~~ **13 个 skill 补 `version:` 字段** | ✅ 完成 | commit `bc225b3`；**实做 9 个**（`ican-deploy`/`cross-platform-skill-sync`/`skills-security-check`/`shell-encoding-pitfalls`/`utf8-encoding-fix`/`wechat-voice-transcription`/`report-generator-skill`/`hook-analyzer-skill`/`agent-browser`）→ `version: 1.0.0`；**按新口径跳过 4 个**（`electron`/`shadcn`/`taskflow`/`taskflow-inbox-triage` 阶段2 已改判市场/上游件，补了会被上游覆盖）；`skill-install` 已退役。**核验：13 个正文全无 V 号** → 1.0.0 无倒退风险 |
| **A4** | ~~6~~ **7 个 local `meta.json` description 退化** | ✅ 完成 | commit `bc225b3`；**实做 7 个**（原清单**漏了 `local-vram`**）；**性质修正**：`meta.json` 是**腾讯 marvis 市场分包元数据**（`type=英特尔用户专区`+`download_url`），退化是**上游打包 bug**（YAML 多行块的 `|` 被直接塞进 JSON），**不参与路由**（路由读 SKILL.md frontmatter，7 个 SKILL.md description 实测全部正常且含丰富触发词）；改法 = **用同文件 `display_description` 回填**（零新增信息、零风险） |
| **A5** | `openclaw-dual-gate-quality-audit` description 收窄 | ✅ 完成 | commit `bc225b3`；description 重写（原为「…自评+Codex独立逐文件审计。openclaw双门禁审计」同短语重复）→ 补适用范围 + 4 个改投边界 + 7 个触发词；正文新增 `## 何时不用本 skill（负向边界）` 表格段（改投目标：`openclaw-task-supervision`/`openclaw-fenjue-weekly`/`skill-hitrate-full-audit`/`vp-perspective-audit`）；补丁留档 `05-exec/A5_patch.json` |

**执行顺序**：批3 → 批1 → 批2 → 批4 → 批5（批3 先做 = 先修治理规则自违，后续推 4KB 分卷才有说服力）

| 项 | 内容 | 状态 | 证据 |
|---|---|---|---|
| 3.5 | `A-project-handoff` frontmatter `3.22.0` → `3.35.0` | ✅ 完成 | commit `805465e`；读回 `version: 3.35.0` |
| 3.6 | `A-memory-start` frontmatter `10.27.0` → `10.28.0` | ✅ 完成 | 同上；源端与镜像端读回均为 `10.28.0` |
| — | 三门禁 | ✅ `[GATE:mirror-pass]`（missing=0 mismatch=0 extra=0） | `check-skill-mirror.ps1` |
| **1.1** | **全库 `Desktop\焚诀` → `Desktop\workspace\焚诀`** | ✅ **完成** | commit `1b6fe6d`；**11 文件 34 处**（实测命中 35 处，其中 1 处在 `_trash` 已跳过）；`[GATE:mirror-pass]`+`[GATE:noise-pass]`；改后残留命中=0 |
| **1.4a** | **平台口径统一（第1轮）**：`A-memory-start` G2 门禁模板 + 口径定义行 | ✅ 完成 | commit `5e89bb6`；模板 `<OC/WB/CC/TC/HM/CX>` → `<OC/WB/TR/CX>`；HM 改回在役 |
| **1.4b** | **平台口径统一（第2轮）**：`A-project-handoff`:124/142 + `A-get-memory`:422 | ✅ 完成 | commit `42760fc`；两文件单次收口 |
| 1.4c | 平台口径统一（余量） | ⬜ 待做 | **剩余活跃引用 90 处**（原 110，已扣 `pre-cc-check` 脚本名误匹配）。分类：路径映射表（`cross-platform-agent-sync` 4 处 `.claude\` 路径，CC 弃用后应删整条）／平台清单类（`cross-platform-skill-sync`:3/14/15、`skill-drift-surgery` 8 处、`data-layer-consistency-fix` 5 处、`discover-agent-cli` 5 处）／历史案例（`data-layer-consistency-fix:237`）。**口径基准：OC/WB/TR/CX（TR=TRAE=TC），CC 移除，HM 在役** |
| 3.1 | `A-project-handoff` 84,818B → 拆 references/ 分卷，主文件 ≤4KB | ⬜ 待做 | 需新建 references 文件，工程量大，单独一轮 |
| 3.2 | `bigfile-split` 15,360B 自拆为 6 卷 | ✅ 完成 | commit `98b974c`；主文件 **15362B → 3626B**，6 卷均 ≤4096B；镜像 `[GATE:mirror-pass]`；内容校验 14 章节 0 缺失 |
| **3.4** | `cross-platform-agent-sync` 19.59KB 自拆为 8 卷 | ✅ 完成 | commit（2026-09-14）；**20058B → 1764B**，8 卷均 ≤4096B；32 章节 0 缺失；`[GATE:mirror-pass]` |
| 3.3 | `fenjue-advisor-scoring` 退役 | ⬜ 待做 | 用户已确认不再使用；**退役前须确认无反向引用** |
| **2.x** | **死链修复 6 项**（本轮）| ✅ 完成 | ① `shell-encoding-pitfalls` name 与目录名对齐 ② `wechat-voice-transcription` local-asr 事实更正 ③ `first-principles-decomposer` 4 个不存在联动 skill 标为待建 ④ `c-cleanup` 两条不存在脚本 ⑤ `story-setup` 两个不存在生成脚本 ⑥ `wps-knowledgebase` 引用文件缺失声明（该 skill 仅剩 SKILL.md）。两个 commit，`[GATE:mirror-pass]` |
| 2.x | 死链剩余 | ⬜ 待做 | `A-get-memory`(trace_view.py + wf_*.ps1，5 处)、`openclaw-fenjue-weekly:73` 死门禁、`openclaw-task-supervision` Qoder 通道、`fenjue-routing-health-check` VERSION_LOCK.part2/3/4、`chaoshi-image-optimization` ffmpeg 版本路径、`hook-analyzer`/`report-generator` 共同上游 |

**本轮跑通的执行链路（可复用模板）**：
```
① rule_editor.py show --file <f> --lines N-M        # 改动前实测锚点
② rule_editor.py replace ... --dry-run              # 预览命中（须=1）
③ rule_editor.py replace ... --no-commit            # 落盘+自动备份+[verify] PASS
④ rule_editor.py commit --file A --file B --desc "" --fix-mirror   # 单次收口（镜像拦截自动修复）
⑤ check-skill-mirror.ps1 → [GATE:mirror-pass]       # 验证
```
