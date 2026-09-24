# 自建 skill 体系 × GitHub 优质开源项目全量对标分析报告

> **⚠️ 校正注（2026-09-24 r18，R241 只加注不改写正文）**：本报告正文（2026-09-23）**一字未改**，但以下三类内容现已失效，引用前必须重跑取值命令：
> ① **分母**：正文所有 `151`（顶层技能数）已陈旧——实测 `python 焚诀/eval/verify_truth_consistency.py` 看 C1 行 = **167**（注册表 == 磁盘，含 1 个 junction）；本仓扫描器口径 `python 05-exec/description_baseline_scan.py` = **166**（按设计跳过 junction）。
> ② **门禁与端数**：正文 `C1~C23` / 五端 现均扩为 **C1~C28 / 八端（cx/hm/oc/qd/qw/tr/wb/zc）**。
> ③ **差距账**：G1~G5 已全部在 r17/r17b 闭环或转入归属会话；**增量账（新差距 N1~N8、对标对象 7→14、4 个新工具与首跑实测）见同目录 `全量对标报告_r18_2026-09-24.md`**。

## Abstract

本报告以「整个自建 skill 体系」（`D:\global_skills` 全量技能库 + 注册表/路由 + 全局记忆系统 + 焚诀 eval 门禁基建 + 五端同步，151 个顶层技能）为被对标方，选取 **4 个主对标**（obra/superpowers 290,514★、anthropics/skills 177,786★、github/spec-kit 138,541★、ruvnet/ruflo 73,120★，均为 2026-09-23 经 GitHub API 实时核实）与 **3 个参照系**（mem0 65,887★、letta-ai/letta 24,858★、GreatScottyMac/roo-code-memory-bank 1,675★）做七维全量对标。

核心结论：**本体系与四个对标项目不是同一物种，但在「单人长期协作基础设施」标尺上已完成对 superpowers 的第一轮收敛（今日 17 项闭环，自评分 46→50.3）**。本轮多项目对标新增三角验证出 4 处此前未覆盖的差距：**①注入的机制层强制（hook）缺失（superpowers+ruflo 双重印证）；②AC 收敛校验缺失（spec-kit 的 converge/verdict 机制）；③技能 description 质量门缺失（anthropics 官方口径）；④交接记忆评测集缺失（mem0 LOCOMO 思路）**。同时确认 5 处本体系独有优势无对标者具备（真值门禁 / 判据隔离桩 / 语义路由 / 结构化记忆交接 / 五端单源）。改进建议按 P0×2、P1×3、P2×3 排序，全部非破坏性，且不与今日已闭环的 17 项重复。

## 1. 调研设计

### 1.1 对标对象选定

| 对标对象 | 选定理由 | 定位一句话 |
|---|---|---|
| obra/superpowers | 与本体系**同域**（技能库+工作流方法论），且有今日基线报告可直接衔接 | 可分发的无状态开发方法论 |
| anthropics/skills | **官方技能标准**制定者，对「技能资产该怎么写、怎么发」有定义权 | Agent Skills 官方示例库与规范 |
| github/spec-kit | 工作流治理标杆：规格驱动 + 门禁化生命周期，与七步闭环同构 | 规格驱动开发工具包 |
| ruvnet/ruflo（原 claude-flow） | 完整 agent harness：hooks/记忆/swarm，代表「机制层全自动化」路线 | Claude Code/Codex 的执行层元框架 |
| mem0 / letta（参照） | 记忆工程基建头部，用于校准「记忆层差距判断」 | 对话记忆基础设施 |
| roo-code-memory-bank（参照） | 文件式项目记忆的**模式先驱**，已停更，用于确认演化方向 | 文件式项目记忆（已转向 Context Portal MCP） |

### 1.2 方法与数据来源

- **对标仓库数据**：GitHub REST API 经认证通道（`gh api repos/<owner>/<repo>`）实时取数，star/fork/pushed_at/license 均为 2026-09-23 实测值；README 经 `gh api repos/<owner>/<repo>/readme` 解码直读。
- **本体系数据**：本机实测（`find`/`ls`/`grep` 计数、SKILL.md frontmatter 直读），并复用今日焚诀会话两份实测报告（`焚诀/reports/2026-09-23_Superpowers对标分析.md`、`2026-09-23_对标改进成效量化报告.md`），其中关键声明已按 R220 抽验 5 项（新判据脚本 mtime、C20/C22/C23 计数、151 顶层 SKILL.md、INDEX/移植指南在盘）全部证实。
- **可信度标注**：✅已实测（附命令/路径）｜⚠️部分实测或未实时查证。agentskills.io 官方规范全文本机网络不可达（超时），涉及该处的细节标注 ⚠️。

### 1.3 口径声明

- 对标主体按用户裁定 = **整个自建 skill 体系**（非仅记忆交接工作流）。
- 评分沿用今日基线报告的「同一标尺下的定位差」口径：分数反映标尺收敛度，不是价值判决。
- 本报告只分析不落地（零代码改动），改进项按「收益/成本/验收判据/破坏性」给出，供后续授权执行。

## 2. 被对标方画像：自建 skill 体系当前基线

### 2.1 分层架构（✅实测）

| 层 | 组件 | 当前状态（取值命令见附录） |
|---|---|---|
| 入口注入 | A-memory-start v10.67.0 + contract 分卷 + behavior_core V41 + 各端注入壳 | 主文件 25,456B（-64% 后）；复杂会话注入 ≈61–63KB |
| 语义路由 | 焚诀 `eval/unified_router.py` 五层（L0 域→L0.1 direct_map→L0.5 tag→L1 BGE onnx→L2 memory→L3 LLM） | 冷启动 1.30–1.37s（sklearn 急性导入税 0.91s 未修） |
| 技能资产 | 顶层 **151** 个 SKILL.md（`find D:/global_skills -maxdepth 2 -name SKILL.md` 实测） | 平均 10.1KB；超 4KB 107 个；含绝对路径 32 个（C20 棘轮门禁治理中） |
| 项目记忆 | A-project-handoff v3.51.0，**18 个子命令**，9 个记忆节 + 注入壳 + savepoint/review/split/trim-shell 自愈 + 三门禁 | 本项目注入壳 26,594B（V3.48.0 后，-6,435B/轮） |
| 质量门禁 | 焚诀 verify **23 条判据（C1~C23）** + 判据隔离桩 **13 个** + rule_editor 三门禁（mirror/noise/evolution） | 19→23 条为今日新增（C20/C22/C23） |
| 经验反哺 | A-get-memory + lessons 107+ 文件 + R 编号规则体系（至 R278+）+ 反理性化表 19 行 | decay_lessons 衰减 + 命中率采样 |
| 工作流 | 七步闭环 + A-ask-questions 四维澄清/③.5 方案探索 + task-card + `flow` 子命令 + 09-workflow-state 动态任务状态 | workflow_gate 机器校验任务卡 11 区字段 |
| 验收 | AC-OBS 写入项目记忆（本项目 8 条） | ⚠️ 半数未勾选，且**无机器收敛校验步骤**（本次对标新发现） |
| 平台 | 五端（wb/tr/cx/hm/zc）junction 一份权威源 | 每端启动注入模板 6 件 |
| 治理 | C7/C13/C6/C16 版本一致性门禁 + R 号防撞 + allow_collide 台账 + CI 10 jobs | 版本号↔版本历史机器校验 |

### 2.2 与既有对标工作的衔接

今日焚诀会话已完成 superpowers 单项目对标基线（46/70）并闭环 **17 项改进**（P0×4/P1×7/P2×6，现 50.3/70，+9.35%）。本报告的差距清单**逐条与该 17 项对账**，已闭环项（如 C20 棘轮、skill_trigger_acceptance、upstream_drift_check、R-ADMIT 准入 4 问、反理性化表、修复循环升级、模型分层、移植指南、INDEX 单入口）不再重复立项。

## 3. 对标对象画像

### 3.1 obra/superpowers（✅API + 今日源码级报告）

**290,514★ / 26,0k forks / MIT / pushed 2026-09-22 / v6.4.1（2026-09-18）**。15 个 SKILL.md + 4 个 hook 文件（共 4.5KB bash polyglot）+ 84 个测试文件 + 50 个 docs；零依赖；适配 **16 个 harness**（11 处平台清单）；方法论闭环 = brainstorming → writing-plans → executing-plans/subagent-driven-development → TDD → code-review → finishing-a-development-branch，4 条哲学铁律 + 贯穿全体的「防理性化对照表」；SessionStart hook（matcher=`startup|clear|compact`）强制注入 3.12KB bootstrap——**注入靠机制不靠自觉**；贡献治理 94% 拒收率；tests（插件代码）与 evals（真实 LLM 会话行为，外部仓库）二分；`test-skill-structure.sh` 硬测 frontmatter/被引文件存在/本地路径泄漏/word budget=1000。

### 3.2 anthropics/skills（✅API + README 直读）

**177,786★ / 21.1k forks / pushed 2026-09-22 / created 2025-09-22**。仓库 = `skills/`（19 个技能：docx/pdf/pptx/xlsx 四个生产级文档技能为 source-available，其余 Apache-2.0；含 skill-creator、mcp-builder、webapp-testing、frontend-design 等）+ `spec/`（Agent Skills 规范，已迁 agentskills.io）+ `template/`（技能模板）。格式：**一个文件夹 + 一个 SKILL.md，frontmatter 仅 `name` + `description` 两个必填字段**；description = 「做什么 + 何时用」的完整描述，是平台触发技能的**第一信号**；渐进披露（metadata → 正文 → 捆绑资源）为规范核心（⚠️ 体量上限具体数值未实时查证，agentskills.io 不可达）。分发走 Claude Code plugin marketplace（`/plugin marketplace add anthropics/skills`）、Claude.ai、Skills API 三通道，配 skills.sh 徽章与 partner skills 生态。

### 3.3 github/spec-kit（✅API + README 直读）

**138,541★ / 12.4k forks / MIT / pushed 2026-09-23 / v1.0.10（2026-09-22，发布节奏≈周更）**。三流程为**独立入口**：① Spec-Driven Development（核心）：`/speckit-constitution`（每项目一份宪法）→ `/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement` → **`/speckit-converge`，重复 implement→converge 直到报告 Converged**；clarify/checklists/analyze（跨产物一致性）为可选质量门。② Bug fixing（扩展）：`assess → fix → test` 三段分离，报告落 `.specify/bugs/<slug>/`，verdict = **verified / partial / failed**，明文「Missing verification is not a successful fix」。③ Idea assessment（扩展）：intake→research→define→shape→decide，终局 **go / needs-clarification / kill** 决策件。定制体系 = extensions/presets/workflows/bundles；docs 站（GitHub Pages）+ 中英双语 README；CLI = `uv tool install specify-cli`，多 agent 集成。

### 3.4 ruvnet/ruflo（原 claude-flow）（✅API + README 直读）

**73,120★ / 8.7k forks / MIT / pushed 2026-09-23 / created 2025-06-02**。定位「agent meta-harness」：**Agent = Model + Harness**，ruflo 是 Claude Code/Codex 的执行层。两条安装路径：轻量 plugin 轨（slash commands）与完整 CLI 轨（`npx ruflo init`）= **98 agents、60+ commands、30 skills、314 MCP tools、hooks、daemon**；**35 个插件**（ruflo-swarm/autopilot/loop-workers/workflows/**rag-memory**/federation/neural-trader…）；hooks 系统自动路由任务、从成功模式学习、后台协调 swarm；federation 跨机器 agent 协作（PII 自动剥离）；生态下载 8.1M+。⚠️ 注意其 CLI 明文「POSIX shells only — see Windows note」，Windows 支持弱。

### 3.5 参照系：mem0 / letta / roo-code-memory-bank

- **mem0（65,887★ / Apache-2.0 / pushed 2026-09-23）**：记忆抽取+更新管道（ADD/UPDATE/DELETE/NOOP 决策、冲突检测）、LOCOMO 评测、OpenMemory MCP 跨应用记忆服务器。
- **letta（24,858★ / Apache-2.0 / pushed 2026-09-10）**：有状态 agent 平台，memory blocks 自编辑 + 后台整理（sleep-time compute）。
- **roo-code-memory-bank（1,675★ / Apache-2.0 / **pushed 2025-05-15，已停更 16 个月**）**：文件式项目记忆模式先驱（core files + mode rules + VS Code 集成）；作者已转向 **Context Portal MCP**——文件式记忆正在向 MCP server 形态演化的信号。

## 4. 七维逐项对标

### 4.1 维度一：功能模块覆盖范围

| 能力域 | superpowers | anthropics/skills | spec-kit | ruflo | 本体系 |
|---|---|---|---|---|---|
| 技能创作/生命周期 | writing-skills 26KB 教学 | skill-creator + 官方模板 | 扩展/预设/捆绑定制 | 30 skills + 插件工厂 | A-skill-manager 全生命周期 + R-ADMIT 准入 |
| 需求澄清 | brainstorming 17.1KB | 无 | /speckit-clarify + assess 流程 | 无专用 | A-ask-questions 四维 + ③.5 方案探索 |
| 计划→执行 | writing-plans + executing-plans 19.9KB | 无 | specify→plan→tasks→implement | workflows 插件 | task-card 11 区机器校验 + flow 状态机 |
| 收敛/验收判定 | verification-before-completion（5 步 Gate） | 无 | **converge（Converged 判定）+ verdict 三态** | 无 | AC-OBS（**无机器收敛步**） |
| 调试/修复 | systematic-debugging + 防理性化 | webapp-testing 参考 | **assess→fix→test 分离** | 无专用 | G8 根因前置 + 修复循环升级 |
| 测试 | tests 84 文件 + evals 外部 | 无（示例级） | checklist 门禁 | daemon 内测 | eval/tests 58py/242 例 + **13 隔离桩** |
| 记忆持久化 | ❌ 无状态 | ❌ | ❌ | ✅ RAG memory 插件 | ✅ 9 节结构化 + savepoint/拆卷自愈 |
| 语义路由 | ❌ | ❌（平台内置） | ❌ | ✅ Router（swarm 内） | ✅ 五层 BGE+TF-IDF + 命中率度量 |
| 多平台分发 | ✅ 16 harness | ✅ marketplace/API | ✅ 多 agent 集成 | ✅ 35 插件 npm | ❌ 个人自用（五端 junction） |
| 垂直域技能 | ❌ 明确拒绝 | 示例级 | ❌ | ❌ | ✅ 151 个含大量垂直域 |

**判定：覆盖广度本体系最宽（151 技能含垂直域），但四处深度落后**：执行控制深度（superpowers executing-plans，已部分对账）、**收敛/验收机器判定（spec-kit 独有，本次新确认）**、端到端评测厚度（superpowers evals 生态，已建但薄）、分发面（非目标）。

### 4.2 维度二：技术架构与实现方式

| 架构要素 | superpowers | anthropics/skills | spec-kit | ruflo | 本体系 |
|---|---|---|---|---|---|
| 内容载体 | 15 SKILL.md（2 字段 frontmatter） | SKILL.md + scripts/references/assets | 模板 + `.specify/` 工件目录 | 插件化 skills/agents/commands | 151 SKILL.md（超集 frontmatter：+version/agent_created） |
| 运行时机制 | 4 hook 文件 4.5KB | **无运行时**（平台消费） | specify-cli（uv/Python） | Node daemon + MCP server + hooks | 145 个 Python 脚本 + BGE onnx |
| 注入机制 | **hook 强制**（含 compact 重注入） | 平台内置触发 | agent skill 调用（平台机制） | **hooks 自动路由** | AI 自觉 + 事后门禁（P0-3 已规程化，机制层未落） |
| 可靠性哲学 | 机制层强制 | 平台保证 | 流程分离 + verdict | 机制层全自动 | 校验层事后抓（门禁） |
| 真值源/一致性 | .version-bump 脚本 | 无 | 模板单一来源 | 无 | **truth_constants + C 门禁 23 条 + 隔离桩** |
| 依赖策略 | 零依赖洁癖 | 零运行时 | Python 3.11+ uv | Node 全家桶 | 11 钉版包（务实） |

**判定：本体系架构与四者都不同——机制在 Python、内容在 Markdown、可靠性做在校验层。** 四个对标项目共同印证了一个本体系尚未补齐的架构层：**「注入/触发」应做在机制层**（superpowers hook、ruflo hooks、anthropics 平台内置、spec-kit 平台 skill 调用），本体系仍靠纪律 + 事后门禁。这是四个项目里最一致、且今日 17 项只完成「规程化」未完成「机制化」的一处。

### 4.3 维度三：性能表现

| 指标 | superpowers | spec-kit | ruflo | 本体系 |
|---|---|---|---|---|
| 每会话注入 | ≈3.1KB | 按命令加载（轻） | hook 自动（内容可变） | 复杂会话 ≈61–63KB（已从 20 倍差距收敛中：A-memory-start -64%、contract -58%） |
| 冷启动开销 | 毫秒（bash cat） | uv 首次安装后秒级 | daemon 常驻 | 路由 1.30–1.37s（sklearn 税 0.91s 待修） |
| 无界增长 | 无 | 无 | daemon 托管 | ⚠️ `eval/_cache` 82→113MB 无淘汰；llm_decisions.jsonl 无轮转 |
| 可验证性能声明 | 无（方法论） | 无 | 下载量/clone 数（非性能） | verify 0.46s / pytest 242 例 35.4s |

**判定：注入税仍是最大性能差距，但已在正确方向收敛**（「20KB 以内可达」，今日已从 68.7KB 主文件降到 25.4KB）。计算性能主瓶颈（sklearn 急性导入、缓存无淘汰）属既有 PERF 遗留（PERF-P0-1/P0-2），本轮不重复立项，见 §8.5 联动。ruflo 证明「daemon 常驻 + hook 自动化」路线的运行时开销可被用户接受，本体系无需引入 daemon（单人规模收益为负）。

### 4.4 维度四：可扩展性

| 扩展要素 | superpowers | anthropics/skills | spec-kit | ruflo | 本体系 |
|---|---|---|---|---|---|
| 技能质量守门 | word budget + 路径泄漏测试 | 官方规范 + template | 模板校验 | 插件清单 | 4KB 拆卷纪律 + C20 棘轮（今日落）+ **description 质量无门禁（新差距）** |
| 上游/生态漂移 | bump-version --check | 官方自主 | release 周更 | npm 生态 | upstream_drift_check（今日落，覆盖 4 同源技能） |
| 行为评测 | evals 外部仓库（真实会话） | 无 | checklist + verdict | hooks 学习回路 | skill_trigger_acceptance（今日落，11/12）+ 路由层盲测/对抗 |
| 新端扩展 | porting 指南 50.7KB | 平台标准即规范 | integration key 机制 | 35 插件即生态 | 移植指南 7.5KB（今日落）+ 五端 junction |
| 准入门槛 | 94% 拒收 + 9 类不接受 | 无（示例库） | 无 | 无 | R-ADMIT 4 问（今日落） |

**判定：今日 17 项闭环后，可扩展性四项机制（守门/漂移/评测/移植）已全部「从无到有」，与基线报告结论一致（该维 +1.5 为最大提升）。本轮新确认的剩余差距只有一处：技能 `description` 字段无质量门禁**——anthropics 官方口径中 description 是触发技能的第一信号（frontmatter 两个必填字段之一），本体系 151 个技能的 description 从未被机器审计过，而它直接决定 L1/L2 路由命中率上限。

### 4.5 维度五：维护状态

| 指标 | superpowers | anthropics/skills | spec-kit | ruflo | 本体系 |
|---|---|---|---|---|---|
| Star | 290,514 | 177,786 | 138,541 | 73,120 | 不适用 |
| 最近推送 | 2026-09-22 | 2026-09-22 | 2026-09-23 | 2026-09-23 | 本地 git 每日 |
| 发布节奏 | 月度（v6.4.1，09-18） | 持续（无 tag） | **周级（v1.0.10，09-22）** | 持续（npm） | R 编号按需 + C13 版本门禁 |
| 维护者 | 团队 + 商业实体 | Anthropic 官方 | GitHub 官方 | 个人（ruvnet） | 1 人 + AI |
| 社区设施 | Discord/模板/遥测 | support 文章/工程博客 | docs 站/双语/Contributing | 14 章指南/UI | 无（个人项目） |
| 治理强度 | 94% 拒收 | 无公开治理 | 官方流程 | 松 | **机器门禁 + 防撞台账（单人下最严）** |

**判定：体量与生态不可比（个人 vs 现象级），但「发布纪律」可比且本体系不落下风**：spec-kit 的周级 release、superpowers 的 RELEASE-NOTES 97.6KB 对应本体系的 version-history 分卷 + C13 frontmatter↔版本历史机器校验——后者是四者都没有的机器化保证。唯一可内化的是其「贡献治理三条款」（披露 AI 环境 / 真实问题 / 不捆绑改动），本体系已通过 R236 `--file` 白名单实现最后一条。

### 4.6 维度六：文档完善程度

| 文档要素 | superpowers | anthropics/skills | spec-kit | ruflo | 本体系 |
|---|---|---|---|---|---|
| 单入口 | docs/ 50 文件 | README + support 文章 | **GitHub Pages 多页站** | docs 14 章指南 | deliverables/INDEX.md（今日落，4,775B） |
| 规范文档 | porting 50.7KB | agentskills.io 规范 ⚠️ | 概念/参考/指南三区 | ruflo-explained | 移植指南 7.5KB（今日落） |
| 变更史 | RELEASE-NOTES 97.6KB | 无 | release 页 | 无 | version-history 分卷（C13 校验） |
| 双语 | 英文 | 英文 | **中英双语** | 英文 | 中文单语 |
| 文档治理机制 | word budget 测试 | 无 | 无 | 无 | **C14 时效 + C5 口径扫描 + 4KB 拆卷 + C23 落点声明（今日落）** |

**判定：结构差距在缩小（INDEX + 移植指南补上了最痛的两块），剩余差距 = 多页文档站 + 双语（对外开源才有意义，非当前目标）**。反向优势保持：四者均无「文档不会烂」的机器治理层，本体系独有。

### 4.7 维度七：适用场景

| 场景 | superpowers | anthropics/skills | spec-kit | ruflo | 本体系 |
|---|---|---|---|---|---|
| 他人 clone 即用 | ✅ | ✅ | ✅ | ✅（Node） | ❌ 深耦合 Windows/junction/路径 |
| 通用方法论（TDD/调试/评审） | ✅✅ | 参考级 | ✅（规格侧） | ✅ | ⚠️ 同源但曾分叉（upstream_drift 已盯） |
| 长期个人协作（记得住） | ❌ | ❌ | ⚠️ 工件持久但无记忆 | ✅ | ✅✅ **核心优势** |
| 垂直域（作业/视频/微信等） | ❌ | ⚠️ | ❌ | ❌ | ✅ |
| 多 AI 平台一致行为 | ✅ 16 端 | ✅ Claude 系 | ✅ 多 agent | ✅ Claude/Codex | ✅ 五端 junction（单机最优解） |
| 跨机器协同 | ❌ | ❌ | ❌ | ✅ federation | ❌（单机五端） |
| Windows 原生 | ⚠️ polyglot 兼容 | 不适用 | ✅ | ❌ POSIX only | ✅✅ **Windows 深度适配** |

**判定：定位差非能力差。** 本体系甜蜜点 = 「单人 + Windows + 多端 + 长期记忆 + 垂直域」，四个对标项目没有任何一个同时覆盖这五点；反之本体系在「分发/跨机/团队」三格空白是设计选择。ruvnet 个人项目做到 73k★ 证明单人 harness 有社区价值，若未来想开源，路径见 §9。

## 5. 模块映射总表（本体系 ↔ 各项目对应部分）

| # | 本体系组件 | superpowers 对应 | anthropics/skills 对应 | spec-kit 对应 | ruflo 对应 | 强弱判定 |
|---|---|---|---|---|---|---|
| 1 | A-memory-start 入口门禁 | using-superpowers + hook 注入 | 平台内置触发 | agent skill 调用 | hooks 自动路由 | **落后（机制层）**，规程已补 |
| 2 | unified_router 五层路由 | ❌ | ❌（平台内置） | ❌ | Router（swarm 内部） | ✅ 本体系独有强度 |
| 3 | 技能 frontmatter/结构 | 2 字段 + word budget 测试 | **官方规范（name+description）** | 模板 | 插件清单 | 对位；description 质量门缺失 |
| 4 | A-project-handoff 9 节记忆 | ❌（无状态） | ❌ | ⚠️ `.specify/` 工件（非记忆） | RAG memory 插件 | ✅ 结构化+门禁最强（roo memory bank 为同构先驱已停更） |
| 5 | savepoint/拆卷/trim-shell 自愈 | ❌ | ❌ | ❌ | ❌ | ✅ ≈letta sleep-time compute 的文件版 |
| 6 | C1~C23 门禁 + 13 隔离桩 | tests 84 文件 | 无 | checklist + analyze（声明式） | 无 | ✅ **机器跨产物校验独有** |
| 7 | 七步闭环 + A-ask-questions | 7 步方法论 + brainstorming | 无 | 三流程（SDD/bug/assess） | workflows 插件 | 对位；缺 converge 与 verdict（#8） |
| 8 | AC-OBS 验收标准 | verification-before-completion | 无 | **/speckit-converge + bug verdict** | 无 | **落后：无机器收敛步** |
| 9 | G8 根因前置 + 修复循环升级 | systematic-debugging + fix loop | 无 | assess→fix→test 分离 | 无 | 对位；缺 verdict 三态字段 |
| 10 | 五端 junction 单源 | 11 处平台清单 | marketplace 分发 | integration key | **federation 跨机** | 单机最优；跨机空白 |
| 11 | 07-next-steps P0 唯一真相源 + flow/09 节 | executing-plans ledger | 无 | /speckit-tasks 工件 | loop-workers daemon | 对位 |
| 12 | lessons + R 规则 + 反理性化表 | 防理性化表（技能内） | 无 | constitution（项目级） | self-learning loop | ✅ 反哺闭环独有 |
| 13 | eval/tests 242 例 + acceptance | tests+evals 二分（更厚） | 无 | 无 | 内建测试 | 对位；e2e 厚度落后 |
| 14 | deliverables/INDEX + 移植指南 | docs/ 50 文件 | support 文章 | docs 站 | 14 章指南 | 对位偏弱（无站） |
| 15 | C7/C13/R 防撞版本治理 | bump-version 脚本 | 无 | release 节奏 | npm version | ✅ 机器化最强 |
| 16 | 分发（对外） | ✅ 16 harness 安装 | ✅ marketplace/skills.sh | ✅ uv tool | ✅ npm 8.1M | ❌ 无（非目标） |

**统计**：16 项映射中——本体系更强的 6 项（#2/4/5/6/12/15）、对位的 6 项、落后需补的 3 项（#1/8/13）、刻意空白的 1 项（#16）。

## 6. 差距清单（跨项目三角验证）

> 三角验证 = 至少一个对标项目有成熟实现、且本体系今日 17 项闭环未覆盖、且对「个人基础设施」标尺有实际收益。

| # | 差距 | 印证来源 | 现状证据 | 严重度 |
|---|---|---|---|---|
| G1 | **注入/触发的机制层强制缺失**：A-memory-start 仍靠 AI 自觉加载，压缩重注入只有规程（P0-3）无机制 | superpowers hook（`matcher: startup\|clear\|compact`）+ ruflo hooks 双印证；anthropics/spec-kit 由平台机制兜底 | 纪律 + C 门禁事后校验；hook 层为空 | **高**（体系可靠性的根） |
| G2 | **AC 收敛校验缺失**：AC-OBS 验收标准写在记忆里，无「实现后逐条实跑验证命令 → Converged/Not」的机器步骤 | spec-kit `/speckit-converge`（明文 repeat until Converged）+ bug verdict 三态 | 本项目 8 条 AC 中 4 条未勾选且无收敛机制；review 分数不校验 AC | **高**（验收闭环最后一公里） |
| G3 | **技能 description 质量门缺失**：description 是触发第一信号（官方两必填字段之一），151 个技能从未机器审计「做什么+何时用」双要素 | anthropics/skills 官方口径 + 规范 | frontmatter 有 version/agent_created 超集，但无 description 审计门禁 | 中（直接限制路由命中率上限） |
| G4 | **交接记忆评测集缺失**：记忆健康度只有「文件是否被填充」+ drift 校验，无固定场景集测「9 节记忆能否答对」 | mem0 LOCOMO 评测思路 + superpowers evals 二分 | R272 已做主卷/分卷 drift；已知盲区「分数 100% ≠ 记忆与实况一致」 | 中 |
| G5 | **修复无 verdict 字段**：修复类任务收尾无「verified/partial/failed」三态留痕，「缺失验证不算修复成功」未制度化 | spec-kit bug-fix verdict | P0.10 自修≤3 + 修复循环升级（已落）管过程；产物状态无强制 verdict | 中 |
| G6 | 性能遗留：`_cache` 113MB 无淘汰、sklearn 急性导入 0.91s | superpowers 报告 + 成效报告反向恶化记录 | PERF-P0-1/P0-2 在途 | 中（既有项，联动） |
| G7 | 跨机协同与对外分发空白 | ruflo federation / anthropics marketplace / skills.sh | 五端仅单机 junction | 低（非当前目标，登记） |
| G8 | 多页文档站 + 双语 | spec-kit docs 站 / ruflo 14 章 | INDEX.md 单页 | 低（开源前置） |

## 7. 可借鉴优势功能清单

**来自 superpowers**（今日已抄 5 件：hook 规程、结构测试→C20、反理性化表、执行控制、准入治理；剩余可借）：
- **抄-A1 hook 机制探底**：在 ZC/HM 端实测 SessionStart hook 能力（ZCode 存在 hook 机制），最小可行 = 注入 ≤1KB 强制声明 + compact 事件重注入；平台不支持则把「不支持结论」落盘为门禁豁免证据。
- **抄-A2 evals 二分纪律**：把「插件代码测试」（eval/tests）与「真实会话行为评测」（skill_trigger_acceptance）在文档与命名上明确二分，防止覆盖率假象。

**来自 anthropics/skills**：
- **抄-B1 description 双要素门禁**：机器扫描 151 个 description，校验「做什么 + 何时用」双要素与长度上限，输出基线报告并与路由命中率联动归因。
- **抄-B2 scripts/references/assets 目录惯例**：与官方渐进披露结构对齐命名（本体系 references 侧车方向一致，确认即可，防再发明）。
- **抄-B3 生产级技能配可执行脚本**：以官方 docx/pdf/pptx/xlsx 为范例，盘点本体系「纯文字说明型」重技能，补脚本化。

**来自 spec-kit**：
- **抄-C1 converge 收敛判定**：给 AC-OBS 建 `flow --verify-ac`（或 eval 脚本），逐条实跑 AC 验证命令 → 输出 Converged/Not 落盘；重复执行直到收敛。
- **抄-C2 bug verdict 三态**：修复类任务收尾强制 `verified/partial/failed` 字段（接 task_closing.md / 七步闭环⑦），明文「缺失验证不算修复成功」。
- **抄-C3 决策件形态**：方案探索（③.5）产物固化为 `<slug>/` 决策件（go / needs-clarification / kill），目前方案探索结论散在对话里。

**来自 ruflo**：
- **抄-D1 hooks 自动路由实证**：其「你不需要学 314 个工具，hooks 自动路由」与 superpowers 同向，加强 G1 的优先级论证。
- **抄-D2 loop-workers → 平台定时能力**：后台定时任务本体系已有平台级等价（Cron/闲时队列），确认不重复建设即可。

**来自 mem0/letta（参照校准）**：
- **抄-E1 交接记忆评测集**（=G4 落地形态）：固定 10–20 场景 × 9 节 recall 基准，接入 review 报告。
- **确认不抄**：mem0 的 LLM-judge 改写历史与 R241 留痕纪律冲突；letta 的 memory blocks 自编辑 ≈ trim-shell 已有文件版。

## 8. 改进建议与优先级排序

### 8.1 P0（建议本轮后立即排期，全部非破坏性）

| # | 建议 | 来源 | 收益（可量化） | 成本 | 验收判据 |
|---|---|---|---|---|---|
| **P0-1** | **hook 机制层探底与最小注入**：实测 ZC（及 HM）端 SessionStart/compact hook 支持面；可行则注入 ≤1KB 强制声明并实测 2 端；不可行则落盘「平台不支持」证据并保持规程 + 门禁兜底 | superpowers + ruflo 双印证（G1） | 从「可能漏」到「不可能漏」；长会话后半程不失忆 | 低–中（探底 1 轮 + 最小实现） | ① 探底结论（支持/不支持，附实测输出）落盘；② 若可行：2 端注入实测记录 + 回滚说明 |
| **P0-2** | **AC 收敛校验机器化**：新建 `flow --verify-ac`（或 eval 脚本），逐条实跑 AC-OBS 验证命令 → Converged/Not 落盘，纳入 review 报告 | spec-kit converge/verdict（G2） | 补上验收闭环最后一公里；本项目 4 条未闭环 AC 首次获得机器 verdict | 中（1 脚本 + 1 判据 + 隔离桩） | ① 本项目 8 条 AC 实跑一轮并留输出；② gate_stub_runner 覆盖该判据；③ review 报告含 AC 收敛行 |

### 8.2 P1（有明确收益，建议排期）

| # | 建议 | 来源 | 收益 | 成本 | 验收判据 |
|---|---|---|---|---|---|
| **P1-1** | **description 双要素质量门**：扫描 151 个 description（做什么+何时用、长度上限），先出基线报告再立门禁，与路由命中率联动归因 | anthropics 官方口径（G3） | 抬高路由命中率上限；触达「技能写了但路由不中」的隐藏损耗 | 低（扫描脚本）→ 中（门禁+桩） | ① 151 条基线报告落盘；② 门禁落盘并 bump 版本；③ 抽 3 条差 description 修复后路由命中可复现改善 |
| **P1-2** | **交接记忆评测集**：固定 10–20 场景 × 9 节 recall 基准（含「已完成条目销账」类陷阱题），接入 review | mem0 LOCOMO 思路（G4） | 把「分数 100% ≠ 记忆与实况一致」从已知盲区变为可测指标 | 中 | ① 场景集版本化落盘；② 基线分记录；③ review 报告含评测行 |
| **P1-3** | **修复 verdict 三态字段**：task_closing / 七步闭环⑦ 增补强制字段（verified/partial/failed + 验证证据） | spec-kit bug-fix（G5） | 「缺失验证不算修复成功」制度化；收尾审计可机检 | 低（模板 + 规则文本） | ① 模板落盘；② 下一次修复任务实跑一次并留痕 |

### 8.3 P2（登记，按触发条件启动）

| # | 建议 | 触发条件 |
|---|---|---|
| P2-1 | 多页文档站（INDEX → 静态站）+ 双语 | 决定开源/对外分发时 |
| P2-2 | 跨机协同（ruflo federation 思路）或记忆 MCP 化（mem0 OpenMemory / roo→context-portal 演化方向） | 出现第二台工作机或非五端 AI 工具接入需求时 |
| P2-3 | 生产级技能脚本化比例盘点（对齐官方 doc-skills 形态） | 技能库下一轮体量治理时顺带 |

### 8.4 防误学清单（勿在对标中丢掉）

| # | 独有优势 | 对标项目状态 | 为什么不能丢 |
|---|---|---|---|
| 1 | C1~C23 机器跨产物真值门禁 | 四者均无（最接近的 spec-kit analyze 是声明式清单） | 这是「口径全库一致」的唯一机器保证 |
| 2 | 判据隔离桩（13 个，防门禁假通过） | 均无 | 四者都把信任放在人或平台，本体系机器自证 |
| 3 | 结构化记忆 + savepoint/拆卷/trim 自愈 | superpowers/spec-kit 无状态；ruflo 黑盒 RAG | 单人五端长期协作的根基；ruflo 的记忆不可审计 |
| 4 | BGE+TF-IDF 五层语义路由 + 命中率度量 | 均无（anthropics 靠平台内置） | 151 技能规模化的前提 |
| 5 | 五端 junction 一份权威源 | superpowers 11 处清单；ruflo 靠 npm | 改一处五端生效的工程最优解（单机场景） |
| 6 | 留痕纪律（R241 只加注不改写） | mem0/letta 均做改写式更新 | 审计与回滚的基础，勿为「智能合并」牺牲 |

### 8.5 与既有遗留项联动（不重复立项）

- PERF-P0-1（sklearn 急性导入 0.91s）、PERF-P0-2（`_cache` 113MB 无淘汰）、`llm_decisions.jsonl` 无轮转：属性能维既有待办，本轮差距 G6 仅作登记，按原方案执行。
- 今日 17 项闭环中与本报告相邻的项：C20 棘轮（↔G3 前置）、skill_trigger_acceptance（↔P1-2 同层不同目标）、压缩重注入规程（↔P0-1 的规程层）——P0-1 是其「机制化」续篇，非重复。

## 9. 结论：通往「同等或更优」的路径

分两条标尺回答「如何提到同等或更优」：

**标尺 A（对标项目的通用可分发标尺）**：不建议整体迁移。四个项目 100k+ star 的来源是「零依赖 + 可分发 + 官方背书」，本体系为「单人 + 深度个性化 + Windows」设计，走标尺 A 需要牺牲记忆层与门禁层（§8.4 六项），净亏损。只取其中零冲突的一项——技能路径占位符化（今日已以 C20 棘轮落地）。

**标尺 B（个人长期协作基础设施的能力上限）**：本体系在 16 项模块映射中已有 6 项独有更强、6 项对位，落后仅 3 项（注入机制层、AC 收敛、e2e 评测厚度）。完成 **P0-1 + P0-2**（把 superpowers 的 hook 强制与 spec-kit 的 converge 闭环各取其一）与 **P1-1 ~ P1-3**（anthropics 的 description 门禁、mem0 思路的记忆评测、spec-kit 的 verdict 制度）后，本体系将同时具备：superpowers 的方法论闭环 + spec-kit 的验收收敛闭环 + anthropics 的资产规范意识 + 自有的记忆/门禁/路由/多端层——在「单人基础设施」标尺上**结构性优于任一单一对标项目**，达成「同等或更优」。

一句话：**别变成它们，把它们的机制拼到自己的骨架上。**

## 10. References

1. GitHub REST API（经认证通道取数，2026-09-23）：`gh api repos/obra/superpowers` / `repos/anthropics/skills` / `repos/github/spec-kit` / `repos/github/spec-kit/releases/latest` / `repos/ruvnet/ruflo` / `repos/mem0ai/mem0` / `repos/letta-ai/letta` / `repos/GreatScottyMac/roo-code-memory-bank`，及各仓 `/readme`（base64 解码直读）。
2. obra/superpowers: https://github.com/obra/superpowers （v6.4.1，源码级事实引自今日浅克隆报告）
3. anthropics/skills: https://github.com/anthropics/skills ；Agent Skills 规范： https://agentskills.io/specification （⚠️ 本机不可达，未实时查证）
4. github/spec-kit: https://github.com/github/spec-kit （v1.0.10，2026-09-22）；docs: https://github.github.io/spec-kit/
5. ruvnet/ruflo（原 claude-flow）: https://github.com/ruvnet/ruflo
6. mem0ai/mem0: https://github.com/mem0ai/mem0 ；letta-ai/letta: https://github.com/letta-ai/letta
7. GreatScottyMac/roo-code-memory-bank: https://github.com/GreatScottyMac/roo-code-memory-bank （已停更）；后继： https://github.com/GreatScottyMac/context-portal
8. 本机基线：`焚诀/reports/2026-09-23_Superpowers对标分析.md`、`焚诀/reports/2026-09-23_对标改进成效量化报告.md`（2026-09-23，含 17 项闭环实测证据；本轮抽验 5/5 通过）
9. 本体系实测命令：`find D:/global_skills -maxdepth 2 -name SKILL.md | wc -l` → 151；`grep -E '^version' A-memory-start/SKILL.md` → 10.67.0；`grep -E '^version' A-project-handoff/SKILL.md` → 3.51.0；焚诀 `ls eval/{upstream_drift_check,skill_trigger_acceptance,gate_stub_runner}.py` → 均在盘（mtime 2026-09-23）；`grep -c "C20\|C22\|C23" eval/verify_truth_consistency.py` → 30

## 附录：报告元信息

- 分析方法：API 实时取数 + README 直读 + 本机实测 + 既有源码级报告复用 + 跨项目三角验证
- 本轮改动：零代码改动，仅新增本报告（`06-benchmark/`）
- 数据快照：2026-09-23（star/pushed_at 以当日 API 返回为准；网络受限通道已标注）
- **2026-09-24 复核注（零实质漂移，结论维持）**：自动化重复触发复核——① 对标仓 API 复测：superpowers 290,672★（+158）/ anthropics/skills 177,823★（+37）/ spec-kit 138,592★（+51）/ ruflo 73,154★（+34），四仓 pushed_at 均无新推送（superpowers/anthropics 仍 09-22、spec-kit/ruflo 仍 09-23）；② 本体系复测：151 个 SKILL.md / A-memory-start 10.67.0 / A-project-handoff 3.51.0，与 §2.1 基线全等。§6 差距清单（G1–G8）与 §8 建议（P0×2/P1×3/P2×3）全部维持，无需改写。
