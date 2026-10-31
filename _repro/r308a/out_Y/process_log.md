# process_log — r308a Y 臂（A-prompt-better v1.5.0）

1. Step 1 环境探测：执行环境 = coding agent（agentic、可改文件）→ 走「技术/执行类」策略，保留内部工具中立表述、不引用本机私有技能名。
2. Step 1 入口判断：用户只给需求、未给现成 prompt → 判为「从需求生成」入口；仍做一次 Step 3 轻量预判（结果 Level 3：角色/输出格式/约束全缺）→ 走完整重构。文档两处表述在此处不冲突，取「照常分级」。
3. Step 2 歧义：「都换成好看的」有两种读法——A 全部重做 / B 只换不合格图并统一风格。按最优理解取 B 并写进 P0-2；「快点」与质量冲突译为 P0/P1/P2 取舍规则（prompt <task> 末行）；「上线」按题面属另一会话 → 落成 handoff，不做部署（硬边界 1）。
4. 双视角错位（元原则）：隐性期望「别太土」→ 客观化为 <visual_baseline> 7 条二元口径；AI 危险默认值（顺手扒网图、引入新框架、大改版、顺手部署）→ 全部落 <anti_patterns>；AI 信息缺口（页面数/尺寸/主色）→ 落 Context 的 UNKNOWN 条款，禁编造。
5. I2 Memory Block：原话「那个超市网页」引用既往项目 → 生成「## Context (carry forward)」并前置（位于全篇约前 12%）。
6. 执行类必选项齐：done 判据由 <phases> 5 个检查点 + <verification> 8 条 + <done_criteria> 语义承担；<anti_patterns>、<artifact_rules>、<context_budget> 均按技术/执行类写入。
7. 抗退化 C 项：三条硬边界写在 <task> 内（近因）、Context 内（前 30%）、结尾复读（首尾效应）各一次；指令冲突写了优先级（统一>好看、P0>快）。
8. I1 冲突处置：本地 B6「加 <thinking>」与 I1「禁索取隐藏思维链」相冲 → 取 I1，改为 <plan_and_assumptions> 只要结论/假设/证据/理由/验证。
9. 已移除的高虚构技法：未使用 MoE/ToT/GoT/Universal Self-Consistency/prompt-chaining 分层，并在 <anti_patterns> 末条明令禁止 → 对应 RECENCY 第 4 问。
10. I3 Agentic Output Warning：目标工具是 agentic → 原句附在文末。
11. RECENCY 六问逐条过（对应 prompt 内可见证据）：1 工具形态已写 agentic；2 硬边界在前 30% 且结尾复读；3 通篇 MUST/MUST NOT/NEVER；4 虚构技法零出现并显式禁；5 逐句承重、无空泛形容词、scope 已 bounded；6 判据全为二元可验。
12. 本例跳过项：多模态提示词专项（交付物不是文生图/图生图 prompt，平台语法 MJ/SD/FLUX 无适用对象）；<examples> 只给 1 行真实格式示例、不编造项目数据；教学模式、RAG 历史偏好（无既往偏好记录，编造即违规）。
13. 谨慎套用项：文件树跳过（项目文件数 UNKNOWN，画树＝编造），改由阶段 1 审计实测承担；子任务 <5 时不写 <phases>，本例恰为 5 阶段故写入；<context_budget> 规模未知，写成条件触发式。
14. 未声明 G6：文档明示该门禁项 2026-09-28 已废止，不需要写「跳过 G6」，故全文无 G6 字样（七步闭环 ② 衔接按 Step 1-3 → Level 3 → Step 4-6 走）。
15. Step 5/6：对比与核心改动随本文件与收尾消息呈报；因题面限定「只产出交付件、不改项目文件、不联网」，Step 6 的「直接执行」落到生成交付 prompt 本身，不再动仓库。
16. 写面与派发：任务明示只新建 out_Y/ 两文件，故未在项目根落 DECOMPOSE.md，分解内容并入本 log；未派子代理，skip_reason = 老大当轮点名单干。
17. 自评（元能力）：最不确定三项——(a)「都换」取 B 读法若裁判期望 A 则 P0-2 范围偏窄；(b)「不联网」写成硬边界+blocked 兜底可能过严；(c) <visual_baseline> 的 800px/4.5:1 等阈值是行业通用值、非项目实测，已标为口径而非现状。
18. 交付件：optimized_prompt.md（prompt 本体，可直接粘贴）；本 log（18 行内，逐条可对应 prompt 内标签）。
