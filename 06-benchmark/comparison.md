# comparison.md — 自建 skill 体系 vs 一线开源同类（常驻横向页）

> 一页看完「我们和谁同赛道、各自强在哪、我们差哪」。**本页是常驻页**：只写仍成立的结论，
> 每轮 r 轮增量报告（`全量对标报告_rNN_*.md`）负责过程，本页负责现状。
> 星标数**故意不进本页**（对标 addyosmani/agent-skills `docs/comparison.md` 的处理：星标周周变、
> 各家引用口径不一）——需要数字时跑：
> `gh api repos/<owner>/<repo> --jq '"\(.stargazers_count)|\(.pushed_at)"'`
> 本体系侧数字一律附取值命令，禁硬编码（项目铁律 2026-09-22）。

## At a glance

| | **本体系（global_skills + 焚诀 + 焚诀式门禁）** | superpowers (obra) | anthropics/skills | agent-skills (addyosmani) | spec-kit / OpenSpec | ruflo | AAS (sickn33) + vercel/skills | mem0 / letta / ai-brain-starter / cc-memory-setup |
|---|---|---|---|---|---|---|---|---|
| **一句话** | 个人多端 agent 的**规则+记忆+门禁**操作系统 | 把方法论编码成技能 | Agent Skills **规范本体** | 全 SDLC 生命周期技能库 | 规格驱动开发（重/轻两档） | swarm 编排 + RAG 记忆 | 技能**目录控制面与分发** | 记忆层 / 个人第二大脑 |
| **组织原理** | 七步闭环 + 八端单源 + C1~C33 棘轮 | 线性流水线（brainstorm→plan→subagent→review） | frontmatter 契约 + 渐进式披露 | 六段解剖 + phase 命令 + review personas | phase gate / 工件引导 | 任务图 + 编排 | 本地 MCP 控制面 + schema 清单 | 向量/图记忆 + hook 级联归档 |
| **技能规模** | 注册表 count（`verify_truth_consistency.py` C1 行） | ~14 | 官方示例若干 | 25 | 不是技能库 | 混合 | 目录 2,400+ | 不适用 |
| **Distinctive 机制** | **跨产物真值门禁（C1~C33）+ 棘轮只降不升 + 八端 junction 单源 + 派生件重建链** | subagent + task reviewer 双签 + worktree 隔离 | 规范权威、1024 字符 description 上限口径 | Rationalizations/Red Flags 每技能必备 + **三层 eval（结构/路由/行为）在 CI** | converge 循环（AC 机器 verdict） | 编排 + 记忆检索 | `--risk/--category` 裁剪安装 + selection-evidence sidecar + 12 份 JSON Schema | 召回评测集 / drift+conflict 自检脚本 |
| **记忆** | 8 节结构化 + 分卷自愈 + 归档 + 回滚 + 召回评测 | 会话内 spec/plan 文件 | 无（规范不含记忆） | 无 durable memory（其 comparison 页自己承认） | 工件即记忆 | RAG 记忆 | 清单即记忆 | **主打项** |
| **对「注意力税」的态度** | C25 字节棘轮（**只覆盖 5 文件**，r18 实测有盲区） | 未量化 | 描述即预算（≤1024 字符） | description 不写流程（防 agent 只读摘要） | 未量化 | 未量化 | 裁剪安装 = 结构侧解法 | N-F 把省 token 写成可验证标题 |
| **治理/维护** | 单人 + 多并行会话，四根合计提交数见 `cumulative_drift_scan.py` | 近乎 solo，社区 PR 积压 | 官方团队 | 主动收社区件，每技能带 eval | 一线团队，日推 | 日推 | AAS 日推 + 3 open issues（维护最健康的直接竞品） | E 活跃 / F 停滞 |
| **Best for** | 一个人管多端 agent，要「不重复踩坑 + 记忆不丢 + 规则自证」 | 长链自主编码任务 | 定契约、做兼容 | 把需求一路推到 ship 且有真人检查点 | 需要可追溯规格与收敛判据 | 多 agent 编排 | 目录规模化管理与分发 | 只做记忆层 |

## 我们领先的面（别被「对标」二字说服着丢掉）

1. **跨产物真值门禁**：C1~C33 机器校验「注册表 == 磁盘 == BGE == skill_content == 产物文案」，
   且基线棘轮只降不升 —— 14 个对象里**零家**有等价物（ruflo 有 RAG 无门禁；AAS 有 schema 无跨产物真值）。
2. **八端单源 + junction 传播**：改一处权威源多端生效，且有 C3/C4/C6/C22 校验传播链完整性。
3. **记忆可回滚**：阶段归档 + `restore` + savepoint 门禁；对照系里只有 mem0/letta 在「记忆」上有深度，但它们不回滚**项目记忆**。
4. **交接结构化**：9 节记忆 + P-1 绑定表 + 09 状态机（V3.48.0 flow）——superpowers/agent-skills 均无 durable cross-session memory。

## 我们落后的面（截至 r29，全部有实测证据）

| # | 落后项 | 对手做法 | 我们的状态 | 首次登记 |
|---|---|---|---|---|
| 1 | 目录注意力税无棘轮 | AAS 裁剪安装；N-A description ≤1024 | 每轮注入约 45,173 字符（`catalog_attention_tax.py`），C25 不覆盖 | r18 N1 |
| 2 | 注入区口径双源 | 单一真相源清单 | C25 五文件 ∪ attention_sim 六文件 = 10 文件 69,494B 已超顶仍判 PASS | r18 N2 |
| 3 | 六段解剖无规范 | 六段强制（含 Rationalizations/Red Flags/Verification） | **r29 双口径修正**：宽口径下 overview 100% / when_to_use 78.9% / process 54.2%（process 全场第一），真缺口只剩 **rationalizations 13.9%（对手 96%）与 verification**；且 verification 原判缺 68 条里 **22 条（32.4%）是没用了那组词**（如 story-scan 写「采集质量门」），自建维护面真缺 **3 条已于 r29 补齐** | r18 N3 → r28 建 A/B 尺 → r29 双口径+范围过滤 |
| 4 | description 质量门 | 「做什么+何时用」+**不写流程** | 双要素 120/166；**「流程入描述」24 条**（r19 新增判据首测） | r19 |
| 5 | 正文计数断言无内容级门禁 | C16 型产物对账（我们已有，但外推不到正文） | 「五端/四端/V9.7.0」类失真 10 句在注入面（`claim_truth_scan.py`） | r19 |
| 6 | 无 catalog 级三层 eval | N-A 结构/路由/行为三层 eval 在 CI | 焚诀有路由命中评测与召回评测（C26），**无「两技能描述撞车」静态判据** | r19 |
| 7 | 注册表无 JSON Schema 契约 | AAS `schemas/aas-v1/` 12 份 schema | 运行态污染件靠 noise 门禁事后 quarantine | r18 N5 |
| 8 | 对外文档为零 | N-A/N-B 有 docs home + comparison 页 | 对内极强、对外零；**本页即第 1 步** | r10 P2-1 / r19 落地本页 |
| 9 | **自动化验收面为零（判据全靠人记得跑）** | N-E mycelium 11 个 workflow 全守规则资产（AAS 9 / spec-kit 18 / ruflo 29 / mem0 34） | r31 前 `.github` 不存在 ⇒ 42 项判据（C1~C33 + 本仓 5 + 四门禁）无离人执行面；**r31 起步**：`run_gates.py` 单入口 + `gates.yml`（可移植 3/5 门，余 2 门显式 SKIPPED）；**r32 收口一半并改判剩余**：门数 5→6、可移植 3/5→**4/6**，剩余 2 门经实测改判为**设计边界**（仓内无语料，见 X-1）而非待修缺陷，防护转为「用 CI 盯人」的 `gate_run_freshness` | r31 N12 → r32 有效性面 |

### ⚠️ 落后项 #6 的 r31 校正注（R241：原文一字未改，只加注）

> 本表 #6 与上方 At-a-glance 里「N-A … **三层 eval（结构/路由/行为）在 CI**」这句**把对手的 README 宣称当成了实物**，
> 与 r28 已纠正过的「拿对手宣称当实物」同形态，在**新维度上第二次复现**。
> r31 实测（`gh api repos/addyosmani/agent-skills/contents/.github/workflows`）：该仓**只有 1 个 workflow**
> = `test-plugin-install.yml`（内容 = checkout + setup-node + 插件安装/skill 内容校验），
> **未见任何三层 eval 的执行件**。原文保留不改，引用时须改口为「addyosmani **宣称**三层 eval；其 CI 面实测仅 1 门」。
> ⇒ 新增引用铁律（本页通用）：**引用对手能力必须标注「README 宣称」或「实物已验（附文件/路径）」，二选一，不得混用。**

## 六段解剖 A/B（r28 建尺 · r29 双口径复测，同一把尺量双方真实文件）

复现：`python 05-exec/rubric_ab_compare.py --json 06-benchmark/rubric_ab_r29_2026-09-24.json`
（判据单一真相源 = `skill_structure_rubric_scan.RUBRIC_RX`；正文口径与 r28 归档 7 列全等，`--against` 机器对账）

**档一 · 正文口径（r18/r28 原尺，只认标题锚点）**

| 对象 | n | overview | when_to_use | process | rationalizations | red_flags | verification | 六段全含 |
|---|---|---|---|---|---|---|---|---|
| 本体系 | 166 | 18.1% | 24.1% | **42.2%** | 13.9% | 54.2% | 59.0% | 0.0% |
| obra/superpowers | 15 | 66.7% | 60.0% | 13.3% | 66.7% | 60.0% | 80.0% | 0.0% |
| addyosmani/agent-skills | 25 | 96.0% | 92.0% | 24.0% | **96.0%** | **96.0%** | **100.0%** | **20.0%** |
| anthropics/skills | 20 | 25.0% | 20.0% | 25.0% | 5.0% | 30.0% | 25.0% | 0.0% |
| mattpocock/skills | 30 | 23.3% | 3.3% | 40.0% | 3.3% | 6.7% | 16.7% | 0.0% |

**档二 · 宽口径（r29 M2：frontmatter description 亦可命中，复用 r17 description 判据）**

| 对象 | n | overview | when_to_use | process | rationalizations | red_flags | verification | 六段全含 |
|---|---|---|---|---|---|---|---|---|
| 本体系 | 166 | 100.0% | 78.9% | **54.2%** | 13.9% | 54.2% | 59.6% | 4.8% |
| obra/superpowers | 15 | 100.0% | 100.0% | 13.3% | 66.7% | 60.0% | 80.0% | 6.7% |
| addyosmani/agent-skills | 25 | 100.0% | 100.0% | 28.0% | **96.0%** | **96.0%** | **100.0%** | **28.0%** |
| anthropics/skills | 20 | 100.0% | 70.0% | 35.0% | 5.0% | 30.0% | 25.0% | 0.0% |
| mattpocock/skills | 30 | 100.0% | 46.7% | 40.0% | 3.3% | 6.7% | 16.7% | 0.0% |

两档差值（本体系）：overview +81.9 / when_to_use +54.8 / process +12.0 / **rationalizations +0.0** /
**red_flags +0.0** / verification +0.6 ⇒ **只有 rationalizations 一段是真·零兜底余地的大缺口（差 82pt）**。
`verification` 另经三档锚点稳健性检验：68 条原判缺里 22 条（32.4%）属措辞假阴性，
自建维护面真缺 3 条已于 r29 补齐（`video-breakdown-skill` / `local-vram` / `office-automation-pro`）。

## 判据稳健性四档（r30 起：任何对标数字必须指名档位）

复现：`python 05-exec/r30_section_robustness.py --section rationalizations`（`--section verification` 同器）
n=166 同一批文件，四档 = 现行尺 / 严格同义 / 功能等价宽写法 / 仅小节标题。

| 段 | 档1 现行尺 | 档2 严格同义 | 档2b 宽写法 | 档3 仅标题 | 读法 |
|---|---|---|---|---|---|
| rationalizations | **13.9%** | **13.9%**（差 0） | 71.1% | 33.1% | 缺口**不是措辞造成**的；但 57.2% 已有"反模式/误区/禁忌/坑"，缺的是**借口→反驳表这一形式** |
| verification | 60.8% | 72.3%（差 +19） | 74.1% | 33.1% | 原判缺口的 **29.2% 是没用了那组词**（如 `story-scan` 的「采集质量门」） |

⇒ 引用规则：**说"缺制度级反理性化表"成立；说"完全没有负面指引"不成立**；裸百分比（不指名档位）视为不可引用。
存量首批已按最保守口径（档2b 仍缺 ∩ 自建维护面）落 5 条（受管根 `359d0fc`），真队列 14 条、剩 9 条。

> **r31 复测注（原文不改）**：第二批已落 **8 条**（受管根 `93107ca`，98 行纯新增，逐条反驳句指向该技能正文
> 实测存在的 token，缺则拒写 —— 由 `05-exec/r31_landing_rationalizations.py::check_tokens` 机器把关）。
> 档1 **16.9%(28) → 21.7%(36)**、档2 **仍与档1 相等**（继续复证「缺口不是措辞」）、档2b 123→131、档3 60→68；
> 对 addyosmani 96.0% 的差距 **82.1pt → 74.3pt**。真队列 **9 → 1**（仅剩 `A-skill-manager`，他人在途 ` M`）。
> 取值：`python 05-exec/r30_section_robustness.py --section rationalizations --json 06-benchmark/r31_section_robustness_after_2026-09-25.json`

## 自动化验收面（r31 新增第八维；实物 = `.github/workflows/*.yml` 实数，非 README 宣称）

复现：`python 05-exec/r31_ci_surface.py --json 06-benchmark/ci_surface_r31_2026-09-25.json`
（15 对象 / 合计 112 个 workflow；原文留档 `06-benchmark/ci_evidence/`，8 份）

| 对象 | ★ | workflow 数 | 这一维度上它守的是什么 |
|---|---|---|---|
| obra/superpowers | 291,188 | **0** | 无 CI 面（方法论靠会话内自觉，与我们改造前同形） |
| anthropics/skills | 177,977 | **0** | 规范本体，无判据执行面 |
| mattpocock/skills | 269,095 | 1 | 仅 `release.yml`（发布件完整性） |
| github/spec-kit | 138,774 | 18 | `test/lint/codeql/security/extension-version-guard/catalog-assign` + 7 对 assess-fix-test |
| addyosmani/agent-skills | 98,879 | 1 | `test-plugin-install.yml` —— **不是三层 eval**（见落后项 #6 校正注） |
| ruvnet/ruflo | 73,218 | 29 | `verification-pipeline` `funnel-gates` `metaharness-pin-drift` `cve-audit` + 11 个 smoke |
| mem0ai/mem0 | 65,949 | **34** | `ci-gate` `pr-gate` + 9 对 `*-cd/*-checks`（9 个分发产物各一对） |
| **sickn33/AAS** | 46,875 | 9 | `ci.yml` 5 独立 job（`pr-policy`/`source-validation`/**`pr-evidence`**/`artifact-preview`/`main-validation-and-sync`）+ `skill-review` + `repo-hygiene` |
| vercel-labs/skills | 32,414 | 3 | `agents.yml` `ci.yml` `publish.yml` |
| **mycelium/ai-brain-starter** | **36** | **11** | `behavioral-install-eval`(周) `release-drift-heartbeat`(日) `template-purity` `personal-pii-scrub` `open-core-boundary` `install-canon-live-probe` —— **全数守规则/记忆资产本身** |
| **本体系** | 私有归档 | r31 起 1 | `gates.yml`：可移植 3/5 门 + 每日心跳 + 覆盖边界自证。**首跑已真机复验**：run `36064668657` = success，Linux 上 3 门 PASS / 234 ms，2 门 SKIPPED-BY-DESIGN 且原因进日志（取值 `gh run view --repo lxh113377/skill-private-archive --job 107851518725 --log`） |

⇒ **三条可执行结论**
1. **星标不是 CI 严格度的代理指标**：Spearman(stars, workflow_count) = **ρ = −0.114**（n=15）。星标前 4 名里 3 个 ≤1 workflow。
   这是 r28「结构纪律与星标无关」在**第二个独立维度**上的复现 ⇒ 本体系选对标对象一律**按机制同构度，不按星标**。
2. **同构参照系恰恰是 CI 最严者**：36★ 的 mycelium 11 个 workflow 无一构建发布物，全守规则资产；
   我们判据数量远多于它，执行面却只有「有人记得跑」⇒ 这是最刺眼的反向差，也是 r31 的落地起点。
3. **把门禁搬进 CI 的真实成本不是加 yml，而是先把扫描根参数化**：本仓 5 门实测 **3 门可离机复现、2 门绑死
   `D:\global_skills` ∪ 焚诀 ∪ `D:\global_memory`**（`ratchet_gate` + `r19_scan_fixtures` 层b）；
   已在 `run_gates.py` 的 `not_portable_reason` 写死原因，禁后来者再猜（待办 M-1）。

借到的机制与落点：B1 one-source-of-truth（一份逻辑 N 处调用）/ B2 跑不到≠过（`UNVERIFIED` 三态）/
B3 多 job 并列不短路 / B4 周期心跳档 / B5 `concurrency` 成本自觉 / B6 action 按 SHA 钉版本（本仓暂未做）。
原文逐行证据见 `06-benchmark/ci_evidence/`。

## CI 有效性（r32 增补：workflow 文件数只是必要条件，真值在 run 结论分布 + 心跳）

复现：`python 05-exec/r32_ci_health.py --json 06-benchmark/ci_health_r32_2026-09-25.json`（窗口 = 每仓近 ≤50 run，全 workflow 全分支）

| 对象 | workflow 数 | 近 50 run 结论分布 | success | 最近 run |
|---|---|---|---|---|
| obra/superpowers | 0（r31 实测） | `failure 41 / success 7 / startup_failure 2` | **14%** | 09-22 |
| anthropics/skills | 0（r31 实测） | `failure 24 / success 8` | 25% | **08-13 ⇒ 停摆 6 周无一人报警** |
| github/spec-kit | 18 | 半数卡在待批准 | 30% | 09-24 |
| vercel-labs/skills | 3 | — | 22% | 09-24 |
| mem0ai/mem0 | 34 | — | 54% | 09-24 |
| sickn33/AAS | 9 | — | 72%（failure 18%） | 09-24 |
| ruvnet/ruflo | 29 | — | 92%（中位 154 s） | 09-24 |
| **mycelium/ai-brain-starter** | 11 | `success 39 / skipped 6 / failure 3` | **78%（中位 19 s）** | 09-24 当日 |
| mattpocock/skills | 1 | `success 50` | 100% | **09-18 ⇒ 7 天未跑** |
| **本体系** | 1 | `success 3` | **100%（中位 12 s）** | 当日 0.4 h 前 |

⇒ **三条结论（含推翻上一轮自家建议）**
1. **「搬进 CI 就变强」被对手实物推翻**：两家最高星标的 CI 现状 = 曾经有、跑不绿、然后静默停摆。
   ⇒ 只把判据搬进 CI 而不配「有效性」监控，结局就是 anthropics 那种**没人报警的死亡**。
2. **⛔ 推翻 r31 的 M-1**（"扫描根参数化即可让 CI 覆盖 3/5→5/5"）：本仓 tracked `SKILL.md` 本体 = **0** ⇒
   CI 里没有语料，参数化只解决"从哪读"不解决"读什么"。要补语料就得把技能复制进归档仓
   = 造第二真相源（违 C1）+ 陈旧即假绿。⇒ **改判为设计边界**，防护方向改成"证明本机还在真跑"。
   新增禁止项 X-1：禁止为凑 CI 覆盖率把技能语料复制进归档仓。
3. **本体系在第九维首次反超全场**：`gate_run_freshness`（台账新鲜度 + 实质门 verdict，空台账/纯 CI 记录/超期/坏 ts 一律不判绿）
   + `r32_ci_health.py`（心跳与成功率自测）。**对手零家有等价物** —— 连最健康的 mycelium 也靠人盯，我们靠判据盯。

反向用法说明：对手用 CI 判代码，本仓额外用 CI **盯人**（`gate_runs.jsonl` 随仓提交，CI 读它判"本机是否还在跑门禁"）。
自锁教训见 `全量对标报告_r32_CI有效性_2026-09-25.md` §7.2（评台账的判据不得把自己的结论写回台账）。

## 发布与治理文件面（r33 第十维；实物探测，回答的是"有没有外部消费者"）

复现：`python 05-exec/r33_release_governance.py --json 06-benchmark/release_governance_r33_2026-09-25.json`
（tags/releases 用 `per_page=100` ⇒ **100+ 为触顶值，禁当精确数**；LICENSE 同时探 `LICENSE` 与 `LICENSE.md`）

| 对象 | ★ | license | tags | releases | 治理件 |
|---|---|---|---|---|---|
| github/spec-kit | 138,785 | MIT | 100+ | 100+ | **5/5** |
| sickn33/AAS | 46,874 | MIT | 100+ | 100+ | **5/5**（且 open issues 仅 3） |
| ruvnet/ruflo | 73,219 | MIT | 100+ | 100+ | 4/5（缺 COC） |
| mem0ai/mem0 | 65,951 | Apache-2.0 | 100+ | 100+ | 4/5（缺 CHANGELOG） |
| Fission-AI/OpenSpec | 70,222 | MIT | 54 | 50 | 4/5 |
| vercel-labs/skills | 32,413 | MIT | 47 | 47 | 1/5（只 LICENSE） |
| obra/superpowers | 291,213 | MIT | 35 | 13 | 2/5 |
| addyosmani/agent-skills | 98,889 | MIT | 12 | 12 | 2/5 |
| mattpocock/skills | 269,117 | MIT | 7 | 7 | 2/5 |
| **mycelium/ai-brain-starter** | **36** | MIT | **4** | 4 | **3/5** |
| anthropics/skills | 177,979 | **none** | **0** | **0** | **0/5** |
| **本体系** | 私有归档 | none | **0 → 1（r33 起打轮次 tag）** | 0 | 0/5 |

⇒ **三条结论**
1. **治理件密度与星标无关，与"是否有外部消费者"强相关**：269,117★ 的 mattpocock 只 2/5，46,874★ 的 AAS 满配 5/5；
   满配者全是有 npm/PyPI 分发物的产品仓。与 r31（CI 存在性 ρ=−0.114）、r32（CI 有效性）三连同向
   ⇒ **本体系选对标对象的唯一合格依据 = 机制同构度 + 有无外部消费者，不是星标。**
2. **真缺陷只有一个：版本锚机器不可查**。过去版本全写在文本里（技能 `version:` / `Version: V1.0` / C13 的 `V10.70.0` 锚点），
   git 层 0 tag ⇒ `git describe` 不可用、"r31 那轮落在哪个提交"答不出、`git revert r33..HEAD` 写不出来。
   ⇒ r33 起每轮打 annotated tag（补的是**回滚与归因能力**，不是发布流水线）。
3. **LICENSE / release 明确不学**（见下方不学清单 X-2）：补 LICENSE = 对外授予权利，本仓是私有归档；
   开发布线 = 服务不存在的消费者。唯一与我们同形的 anthropics 也不做发布，动机一致。

⚠️ **内部矛盾（r33 实测，比对手结论更值得修）**：受管根 `焚诀` 被并行会话加了 `CONTRIBUTING.md`/`LICENSE.md`/`SECURITY.md`，
`handoff.py noise` 逐条判 **VIOL 并要求迁 `_trash`** ⇒ 照建议执行就会把三家满配对手都有的标准治理件扔进回收站；
不执行则 noise 恒红、savepoint 过不去。**这是 allowlist 缺治理件口径，不是文件该删**（待归属会话裁定，本仓按 R269 不擅动）。

## 可移植性（r34 第十一维；对手 SKILL.md 原文逐文件实测，不看 README）

复现：`python 05-exec/r34_portability_surface.py --json 06-benchmark/portability_r34_2026-09-25.json`
尺：P1 家目录绝对路径 / P2 盘符根路径 / **P3 本机账号名明文** / P4 机器专属工具绝对路径

| 对象 | 取到 SKILL.md | 含机器专属路径 | 命中率 |
|---|---|---|---|
| addyosmani/agent-skills | 25/25 | **0** | 0% |
| obra/superpowers | 15/15 | **0** | 0% |
| anthropics/skills | 19/19 | **0** | 0% |
| sickn33/AAS | 29/997 | 1 | 3% |
| mycelium/ai-brain-starter | 29/38 | 2 | 7% |
| **本体系** | **167/167 全量** | **49** | **29.3%** |

⇒ **本体系第一处「可测地落后于全部对手」的维度，且是量级差**。前三维（CI 存在性/有效性/发布面）都能落到"定位差异、不必照抄"，这一维不行：三家对手抽样零命中，说明"技能文件不写死本机路径"在 Agent Skills 阵营是**普遍基线**而非某家特色。
⇒ **但改进面要精确**：P2 盘符（47 处）是 junction 单源架构的**承重件**（AGENTS 明文禁 `~` 展开、必须写完整路径）⇒ **不清**（见不学清单 X-4）；
真正该清的是 **P3 账号名明文（25 个文件）** —— 不承载任何机制、纯冗余、且是隐私面（当前靠"对外文档为零"侥幸未外泄）。
⇒ 对手已把这类事做成门禁（mycelium `personal-pii-scrub.yml`，原文在 `ci_evidence/`），而我们只有 C20 管"绝对路径条数"，**管不到账号名**。
⇒ r34 落地方式 = **复用既有棘轮**（`ratchet_gate.py` 第 6 指标 `username_in_skill_files`，基线 25 只降不升），不再新建第 7 道门。
现存门禁盲区一条（r34 dogfood 当场暴露）：`rule_conflict_scan.DEFAULT_FILES` 十件里 `D:\global_memory\AGENTS.md` 不可读 ⇒ 权威面实际只有九件，待修（L-4）。


> **r36 追加（第十二维，起步且未跨侧比较）**：新增只读尺 `05-exec/r36_cmd_resolvability.py`
> 量「技能文档里写的仓内引用到底解不解得开」——本体系实测 **1030 处 / 92.2% 可解析 / 真 DEAD 0 / UNLOCATED 80 待定性**；
> 对手侧 4 仓 blob 树已备好但**未跑同尺比较** ⇒ 禁据此声称领先。首版两处错（只扫代码块致假绿、`../assets/` 误判致假缺陷）
> 均由抽验抓回，教训固化成 **X-7**：新工具首跑再干净也要先证「扫描面完整 + 逐类自洽 + 抽样人工复验」。

> **r37 追加（第十三维「门禁可信度 / 假阳性治理」）**：本维度问的不是「有没有门禁」，而是
> **「门禁自己会不会报错，报错了谁来裁决」**。我方实测证据（`06-benchmark/noise_falsepositive_r37_2026-09-25.json`）：
> 噪声门连红 7 轮的 **5 条 VIOL 全部是假阳性** —— 3 条 `git ls-files` 实测**已跟踪**的治理件（工具建议「迁往 _trash」=
> 破坏性）+ 2 条 `.git/` 内**仓内工具自写**的运行态日志（`.gitignore` 管不到 ⇒ 结构性永久红）。
> 对手侧同类失效（前轮已实测，本轮据此定性同源）：`anthropics/skills` run 分布 25% success / **75% failure** 且停摆 6 周无人报警、
> `superpowers` 近 50 run **82% failure**、`spec-kit` 50% run 停在 `action_required`。
> **两种失效同源 = 判据失效无人裁决**；我方现在多出的能力是「取证 → 改判据（不改数据）→ 桩锁死边界 → 常驻门」。
> 落地：上游 A-project-handoff **V3.54.1**（`git_tracked()` 三重收窄 / 二级扫描跳过 `.git` / auto-memory 放行面含 `reference-*`），
> 四根复跑 `[GATE:noise-pass]`，`savepoint` 7 轮后首次转绿；本仓新增第 8 道常驻门 `noise_tracked_stub`（16 例含 5 反例）。
> ⚠️ **不得据此声称领先对手**：M-3（给对手 CI 的红灯逐条分类「真缺陷 vs 假阳性」）❌未实测。详见 `全量对标报告_r37_门禁假阳性治理_2026-09-25.md`。

> **r38 追加（第十四维「积压债务的可见性与到期治理」）**：对手 `gh api` 实测 —— 只有 `github/spec-kit`（27 workflow）
> 配 `Close stale issues and PRs` + 6 条 issue 流转自动化；`anthropics/skills`(1290 open，最老 2025-10-16)、
> `superpowers`(401，最老 2026-01-27)、`addyosmani/agent-skills`(118)、`pre-commit`(25，最老 2018 仍 open) **stale 自动化均为 0**。
> 我方首跑账龄尺即量出 **13 条超期无裁决（最老 30 轮）** ⇒ 「挂账 N 轮」长期只是散文。
> 现已做成判据：`05-exec/r38_debt_aging.py` 四分类 + `ratchet_gate` 第 7 指标 `overdue_debt_items`（只降不升，变异对照会红），
> 13 条逐条取证裁决至 **0**。取向差异记入不学清单 **X-10**（不引入自动关闭）/**X-11**（待办不外迁 tracker）：
> 对手消灭债务靠"关掉"，我靠"逼人裁决"，因为 07 是跨会话唯一真相源。**可宣称领先 4/5 对手，不可宣称领先 spec-kit。**

## 维护状态（r30 实测化，替换此前的形容词）

| 对象 | ★ | 最近推送 | open issues |
|---|---|---|---|
| obra/superpowers | 291,096 | 2026-09-22 | **401** |
| anthropics/skills | 177,935 | 2026-09-24 | **1,284** |
| addyosmani/agent-skills | 98,839 | 2026-09-23 | 116 |
| mattpocock/skills | 268,996 | 2026-09-24 | **527** |
| **本体系** | 私有归档仓，无公开面 | 每轮推 | 无 issue 面（靠 C1~C33 自证） |

取值命令：`gh api repos/<owner>/<repo> --jq '"\(.stargazers_count) \(.pushed_at) \(.open_issues_count)"'`
⇒ **issue 存量与星标同向增长**：高星标不等于高维护度。我们没有社区兜底，唯一可依赖的是自证门禁 ⇒ 该维度上"更强"= 门禁更硬，不是 issue 更少。

> **r31 复测注（原文不改，只加）**：同命令再跑一次，四家主对标为 superpowers 291,188★/401 issues、
> anthropics 177,977★/**1,286**、addyosmani 98,879★/116、mattpocock 269,095★/527 —— 与 r30 同向且量级稳定，
> 结论维持。新增两点：① **本体系侧首次有可比的「维护度」数字** = 四根 30 日提交合计 **487**
> （本仓 93 / `global_skills` 120 / `global_memory` 109 / 焚诀 165），四根最近一次提交均为当日；
> 取值 `git -C <root> log --since=30.days --oneline | wc -l`。② `letta-ai/letta` 推送停在 **09-10（15 天）**，
> `open_issues=0` 是**关闭 issue 面**而非零积压（该仓 `issue-guard.yml` 唯一 workflow 即为此而设），
> 引用它的 0 时须注明这不是健康度信号。

## 不学清单（独有优势，禁止为了「像一线」而丢）

| 独有项 | 若跟对手会怎样 |
|---|---|
| 七步闭环 + workflow_gate 状态机 | OpenSpec 明文「无 rigid phase gate 更轻」——我们踩过的漏加载/裸跑/假通过正是它靠人自觉兜的 |
| R241 历史留痕只加注不改写 | 多数对手直接 force-push 改写历史文案；我们的分母失真（151→167）能追溯全靠没改写 |
| 删除必经回收站 + 远端双前提 | 一次 robocopy /MIR 事故（R9）换来的铁律 |
| 判据带夹具 + 对照组（R238） | 对手 eval 多在 CI 跑 positive；我们要求「应报警的仍要报警」 |
| **不放 LICENSE / 不开 release 流水线**（r33 X-2） | 11/12 对手有 LICENSE、多数有 release —— 但那是**对外分发**的必需品。本仓是私有归档：补 LICENSE = 对外授予权利（非所愿），开发布线 = 服务不存在消费者。r31/r32/r33 三连同向结论：**严格度来自有无外部消费者，不来自星标** |
| **版本靠 tag 不靠流水线**（r33 H-2 起的取舍） | 对手用 tag/release 表达版本；我们只取 **tag**（回滚与归因锚点），不取 release（发布动作）。同一维度里"要一半不要一半"是刻意的，勿被"对标就要照抄"推着走 |

## 前序报告索引

- `全量对标报告_r18_2026-09-24.md` — 14 对象扩容 + N1~N8 差距 + 4 工具落地
- `全量对标报告_r19_2026-09-24.md` — 实物（代码）层核验 + 工具校准 + 分母统一 + 新判据两枚
- `全量对标报告_r20_插件面补口径_2026-09-24.md` — 插件技能面进入分母（47.5% / 自建视角低估 34.3%）
- `全量对标报告_r27_2026-09-24.md` — 57 个在册插件技能首次安全审计（HIGH 4 条逐行裁定，2 条在源码里裁定掉）
- `全量对标报告_r28_六段解剖AB_2026-09-24.md` — 同一把尺量对手真实文件，推翻三条旧推断
- `全量对标报告_r29_双口径与范围过滤_2026-09-24.md` — M2 双口径 + 判据稳健性 + H2 真队列 3→0
- `全量对标报告_r30_四档稳健性与反理性化首批_2026-09-25.md` — 四档参数化 + 首批 5 条 + 维护状态实测化
- **`全量对标报告_r31_自动化验收面_2026-09-25.md`** — 第八维（CI 执行面）15 对象实测 + ρ=−0.114 + 推翻「N-A 三层 eval 在 CI」+ 反理性化第二批 8 条 + `run_gates.py`/`gates.yml` 落地
- `ci_surface_r31_2026-09-25.json` + `ci_evidence/`（8 份对手 workflow 原文） — r31 第八维证据件
- `自建skill体系全量对标分析报告.md` — r10 首轮（七维矩阵 + 16 项映射，分母 151 已失效见 r18 校正注）
- `P0-C_累积漂移复核第1批_2026-09-24.md` / `第2批` — 高频改写文件的承重句语义复核
