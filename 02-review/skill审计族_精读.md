# 审计族精读审计卡（阶段2 第 2 批，含合并决策）

> 生成：2026-09-14 | code-explorer 子代理只读精读 | 15 个 skill
> 本批核心交付：**合并决策建议**（把 15 个按相似度与职责差异分簇，给保留/合并/废弃）

---

## 审计卡（15 张）

### skill-hitrate-full-audit (8.48KB | refs=8 | 超4KB=Y | triggers=无)
**职责**: 五层 pipeline 做命中率全量诊断
**死链/过时**: QW 端章节 L93/94/98/130/145（QW 已下线）；skill_routing.md 已降为 402B 索引壳，L34 仍当"L2 路由表"读
**重叠**: improvement-pipeline（本 skill 仅诊断不出执行）、routing-test-driven-fix（本 skill 宏观抽样）
**闭环**: 门禁=N | 七步=N | footer=N | 版本一致=N（无版本历史节）
**问题**: [P1] QW 审计章节整段失效 L93/98/130 ｜ [P1] 输入源已降为索引 L34 ｜ [P2] 自身无 triggers 却是触发词质量审计者

### skill-hitrate-improvement-pipeline (10.97KB | refs=18 | 超4KB=Y | triggers=无)
**职责**: 命中率提升 7 阶段端到端编排
**死链/过时**: 无（引用的脚本均实测存在）
**重叠**: hitrate-full-audit（其 Phase1 上游）；routing-regeneration + test-driven-fix 被其 Phase5/6-7 编排
**闭环**: 门禁=Y | 七步=N | footer=N | 版本一致=N
**问题**: [P1] 纯编排层，单加载无法执行 L61/L66 ｜ [P1] 硬编码"137 个 skill" vs 实测 174 ｜ [P2] 无版本历史节

### skill-trigger-diagnosis (8.44KB | refs=10 | 超4KB=Y | triggers=有9)
**职责**: 单 skill 漏加载事后四层定位
**死链/过时**: `C:\Users\37533\Desktop\焚诀\prompts\总控台提示词.txt` 实测不存在 — L25/155/185/194
**重叠**: hitrate-full-audit（它宏观统计）、routing-regeneration
**闭环**: 门禁=N | 七步=N | footer=N | 版本一致=N
**问题**: **[P0] L4 安全网脚本指向不存在路径，Phase4 验证 1/4 全废** ｜ [P2] 无 frontmatter triggers

### skill-routing-test-driven-fix (8.32KB | refs=13 | 超4KB=Y | triggers=无)
**职责**: 测试集驱动修 L2 路由关键词
**死链/过时**: `scripts\templates\qw_agents.md` 实测 0 命中且 QW 已下线 — L37/152/160
**重叠**: improvement-pipeline（= 其 Phase6-7）、routing-regeneration
**闭环**: 门禁=Y | 七步=N | footer=N | 版本一致=N
**问题**: [P1] Step6 部署链路整条指向已消失的 qw_agents.md ｜ [P2] 门禁"扩展集 100%"(L142) 与 improvement-pipeline"95%"(L217) **口径冲突**

### skill-routing-regeneration (8.96KB | refs=12 | 超4KB=Y | triggers=有10)
**职责**: 修脚本后全量重生 skill_content JSON
**死链/过时**: `焚诀\audit\routing_health.py` 实测不存在 — L134；QW — L140
**重叠**: drift-surgery（L28 铁律互划边界）、improvement-pipeline（= 其 Phase5）
**闭环**: 门禁=Y | 七步=N | footer=N | 版本一致=N
**问题**: [P1] 收尾必跑的 routing_health.py 失踪，"不再可选"门禁悬空 ｜ [P1] 写盘限制章节针对已下线 QW

### skill-drift-surgery (7.9KB | refs=7 | 超4KB=Y | triggers=无)
**职责**: JSON 注册数 vs 磁盘外科对齐
**死链/过时**: 五端副本含 TD（已不存在）— L54
**重叠**: skill-merge（同改 JSON count + 同步路由）、routing-regeneration（L28 互划边界）
**闭环**: 门禁=Y | 七步=N | footer=N | 版本一致=Y
**问题**: [P1] Step3 要求同步 skill_routing.md 域计数，该档已拆为 402B 索引 ｜ [P1] 平台清单仍含 TD ｜ [P2] 收尾硬门禁段四份逐字重复 L68

### skill-merge (7.94KB | refs=10 | 超4KB=Y | triggers=有15)
**职责**: 两 skill 合并删除与资产迁移 SOP
**死链/过时**: 无
**重叠**: drift-surgery（骨架同构，本 skill 多边界分析 + 资产迁移）、skill-manager
**闭环**: 门禁=Y | 七步=N | footer=N | 版本一致=Y
**问题**: [P2] Step0 junction 验证与 skill-manager:34 重复定义未互引 ｜ [P2] 无"何时不用本 skill"负向边界

### skill-midtask-recheck (4.02KB | refs=1 | 超4KB=Y临界 | triggers=有6)
**职责**: 多阶段任务中途重探测更优 skill
**死链/过时**: 无
**重叠**: 与本批 14 个基本无重叠（唯一运行时重路由）
**闭环**: 门禁=N | 七步=N | footer=N | 版本一致=Y
**问题**: [P1] 全文无门禁与验收，命中即加载无证据留存 ｜ [P2] grep 模式硬编码 `audit|scoring|fenjue`，改名即漏检

### skill-defer-to-authority (15.97KB | refs=4 | 超4KB=Y | triggers=有13)
**职责**: skill 与权威源冲突 → 薄包装重写
**死链/过时**: 最高权威源 `Desktop\焚诀\prompts\总控台提示词.txt` 实测不存在 — L56/209
**重叠**: vp-perspective-audit（委托方）、prompt-system-audit
**闭环**: 门禁=Y | 七步=N | footer=N | 版本一致=Y
**问题**: [P1] 一级权威源路径为死链 ｜ **[P1] C6"禁止委托子任务"(L87) 与 openclaw-dual-gate 铁律#3"必须用 Agent 子代理"(L19/121) 直接冲突**

### skill-manager (28.19KB+20文件 | refs=25 | 超4KB=Y | triggers=有8)
**职责**: WB 技能安装/删除/兼容/批量管理
**死链/过时**: 分类表仍列 frontend-skill（2026-08-15 已并入 frontend-design 并移入 _trash）— L251/408
**重叠**: cross-platform-skill-sync(0.801)、skill-merge
**闭环**: 门禁=N | 七步=N | footer=N | 版本一致=**N（frontmatter 无 version）**
**问题**: [P1] 28.19KB 单文件超门槛 6 倍无 references ｜ [P1] 分类清单陈旧 ｜ [P2] 尾部"最后更新 2026-07-04"与经验记录 2026-08-24 矛盾

### prompt-system-audit (29.73KB | refs=11 | 超4KB=Y | triggers=无)
**职责**: 提示词 V1-V9 漏洞 + 数据层 D1-D6 审计
**死链/过时**: **单一真相源 `common_prompts.md` 全盘实测 0 命中** — L222/230/235/600；示例路径缺 workspace — L284/301
**重叠**: data-layer-consistency-fix（自称上下游但 D1-D6 与对方 Step1-6 内容重复）、vp-perspective-audit
**闭环**: 门禁=Y | 七步=N | footer=N | 版本一致=Y
**问题**: **[P0] V8/V9 全部围绕不存在的 common_prompts.md，该维度不可执行** ｜ [P1] 29.73KB 单文件双体系未拆

### audit-runner-safe-aggregate (5.24KB | refs=0 | 超4KB=Y | triggers=无)
**职责**: 聚合 runner 防 any() 掩盖单脚本失败
**死链/过时**: 自称"本 skill 的 Python 模块" `audit/safe_aggregate.py`，目录实测**仅 SKILL.md 一个文件** — L30
**重叠**: 与 14 个无实质重叠（唯一代码级反模式）
**闭环**: 门禁=Y | 七步=N | footer=N | 版本一致=N
**问题**: [P1] 自我引用的实现模块不存在，范式不可直接复用

### data-layer-consistency-fix (17.79KB | refs=46 | 超4KB=Y | triggers=有9)
**职责**: 提示词改后数据层六步同步
**死链/过时**: `C:\Users\37533\Desktop\焚诀\skill\registry\*.json` 实测不存在（实为 workspace\焚诀）— L88/155/279/404；CC 已弃用 — L219
**重叠**: prompt-system-audit（其 Phase4.5 已完整重复本 skill 的 D1-D6）、vp-perspective-audit
**闭环**: 门禁=Y | 七步=N | footer=N | 版本一致=Y
**问题**: **[P0] 4 处核心注册表路径死链（缺 workspace 段）** ｜ [P1] 平台清单含已弃用 CC

### vp-perspective-audit (14.15KB | refs=7 | 超4KB=Y | triggers=有10)
**职责**: 多 agent 心智模型预判式审计
**死链/过时**: 平台清单仍列 CC（已弃用）且缺 CX — L57；QW 作活跃对象陈述 — L230
**重叠**: openclaw-dual-gate（本 skill 定性预判，它定量评分）、prompt-system-audit + data-layer（本 skill 发现端）
**闭环**: 门禁=N | 七步=N | footer=N | 版本一致=N
**问题**: **[P0] 无"何时不用本 skill"负向边界（对比 hitrate-full-audit:19-23 有该列）— L241-249，这是本会话 direct_hit=1.0 误命中的结构根因** ｜ [P1] description 含"适用于任何多agent系统的质量检查"，触发面覆盖全族

### openclaw-dual-gate-quality-audit (19.75KB | refs=0 | 超4KB=Y | triggers=无)
**职责**: 自评 + Codex 独立审计双门禁评分
**死链/过时**: 无
**重叠**: vp-perspective-audit、prompt-system-audit
**闭环**: 门禁=Y | 七步=N | footer=N | 版本一致=N
**问题**: [P1] 铁律#3 强制 Agent 子代理 与 defer-to-authority C6 冲突 ｜ [P1] 维度数 5/10/14 三口径并存（L24/L34 vs L325）

---

## 🎯 合并决策建议（本批核心交付）

| 簇 | 现状 | 决策 | 理由 |
|---|---|---|---|
| **簇1 命中率/路由修复链** | 5 个 | `hitrate-full-audit` **保留**（诊断入口）；`trigger-diagnosis` **并入**（四层诊断是其 L0-L4 单点特例，且主安全网已死链，仅保留 Phase0 章节）；`improvement-pipeline` **保留**（执行编排）；`test-driven-fix` 与 `routing-regeneration` **并入**它（前者自述是其 Phase6-7、后者自述 Phase5，门禁口径 100% vs 95% 冲突必须收敛） | 0.82-0.88 相似度根源 = "诊断-执行"被切成四份共享同一批文件 |
| **簇2 注册表外科** | 3 个 | `skill-manager` **保留**（生命周期主档）；`skill-merge` 与 `drift-surgery` **降为其 references/** | 三者共享"备份→compact 写 JSON→同步计数→pre-cc-check→sync 收尾"同一骨架，收尾硬门禁逐字重复 |
| **簇3 指令层+数据层** | 2 个 | `prompt-system-audit` **保留**；`data-layer-consistency-fix` **合并**为其 Phase4.5 的 references | Step1-6 已在对方 L347-540 完整重复，且自身 4 处 P0 死链 |
| **簇4 质量审计** | 2 个 | `vp-perspective-audit` 与 `openclaw-dual-gate` **均保留，禁止合并** | 定性预判 vs 定量评分，视角与产物不同；但**必须各补"何时不用我"负向边界** |
| **簇5 单一职责** | 3 个 | `skill-defer-to-authority`、`audit-runner-safe-aggregate`、`skill-midtask-recheck` **保留** | 各为唯一职责，只需修自身 P0/P1 |

**净效果**：**15 → 8 个顶层 skill + 3 个 references**，消除 5 组真重复与 3 处门禁口径冲突。

---

## 审计族共性结论

1. **体积全数超标**：15/15 均 >4KB（4.02KB~29.73KB，均值约 13.2KB），无一个用 references 拆分。
2. **闭环三件套集体缺失**：15/15 无七步闭环、无 footer 协议声明；门禁仅 10/15 有（hitrate-full-audit / trigger-diagnosis / midtask-recheck / skill-manager / vp-perspective-audit 无）。
3. **元数据治理参差**：仅 6/15 版本与历史一致；9/15 无版本历史节，skill-manager 连 version 字段都没有；仅 2/15 有 frontmatter triggers —— **而其中 3 个专审触发词质量的 skill 自身无 triggers**。
4. **死链集中在一条路径漂移**：`C:\Users\37533\Desktop\焚诀\` 不存在（实际 `Desktop\workspace\焚诀`）造成 ≥10 处死链；另有 qw_agents.md、routing_health.py、common_prompts.md、safe_aggregate.py 四个空指针。
5. **审计族自身违反审计规则**：收尾硬门禁段被 4 份逐字复制（drift-surgery:68 / skill-merge:83 / prompt-system-audit:585 / data-layer:352），正是 skill-defer-to-authority 要治理的"重复定义权威源"反例；跨 skill 规则冲突 2 处。

---

## ✅ 路由误命中根因（本会话实测案例已定位）

现象：查询「为优化我的所有自建skill及其所搭载的工作流提出建议」被 direct_hit 到 `vp-perspective-audit`（score 1.0）。

**根因（实测）**：`vp-perspective-audit` 缺「何时不用本 skill」负向边界声明，而同族 `skill-hitrate-full-audit:19-23` **有**该列。其 description L3 含"适用于任何多 agent 系统的质量检查"——触发面覆盖整个审计族，任何审计类查询都会优先落它。

**修复**：给 vp-perspective-audit 补负向边界（如"仅当需预判 agent 行为链时使用；做命中率/路由/提示词审计时改投 X/Y"），并在 direct_map 中把审计类查询改投审计族具体 skill。
