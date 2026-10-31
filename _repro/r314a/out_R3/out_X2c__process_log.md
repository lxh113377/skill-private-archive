# process_log · r314 轮次3 task2 X2c 臂（同题第 3 轮）
规范源：skill_X2c.md（A-prompt-better V1.3.0）。逐条对应 optimized_prompt.md，无一条编造。
1 环境探测：判定「AI 直接执行」（下游 agent 有命令行权限）⇒ 判据全写成可跑命令，不写手动运行说明。
2 入口判断：优化已有 prompt（用户给了完整原始请求）⇒ 走 Step 2-6，不是从零生成。
3 质量预判：角色未定义、输出格式未指定、表达口语冗余，仅「关键约束明确」达标 = 满足 1 项 ⇒ 判为不及格、按 Step 4 完整重构（不是只补缺失项的轻量优化）。
4 歧义处理（Step 2：列理解 + 按最优执行，不反问）：context 内 4 条裁定 = 上线含义 / 只改 assets 图片=就地同名替换 / 价格含图内价签 / 「反复推敲」= 有界 3 视角。
5 策略选择（代码生成/技术任务 + 复杂多步 + 打包导出）：结构化框架、六法则、抗退化（幻觉+约束+输出不稳定）、Done 判据、禁止项、交付物规则全开。
6 保留用户原意：商品图丑→P0 第 1-4 步逐张定病因；页面好看→P1 第 7-9 步；「方法你自己定」→我定 3 视角有界推敲；「自己跑完部署上线」→P0 第 5-6 步 + 阶段 3/4；「想全面」→<thinking> 强制先出表再动手。
7 红线位置：用户明说「写在任务书最后」⇒ hard_constraints 置于文件末且承载两条红线全文；同时在 task 末、constraints、anti_patterns、done_criteria、verification 各留一处，属技能「末尾重复核心要求 + 首尾效应」，非改用户意图。
8 主要改动（改了才有的段落）：done_criteria 5 条二元判据；anti_patterns 10 条禁止→替代；phases 5 阶段带检查点；output_format 报告 6 字段；artifact_rules 打入/排除；context_budget；verification 8 项自检；task 用 [P0]/[P1] 分层。
9 冲突写死（抗退化「指令冲突」）：constraints 内 3 条优先级 = 红线覆盖美化、如实报告覆盖冒充上线、价格不变覆盖图美观。
10 跳过的技能环节（原因均为硬套会编造）：
  · <examples> 与文件树：题面未给文件清单/示例，禁编造 ⇒ 改令 agent 阶段 0 自行勘察产出图片清单。
  · 多模态提示词专项（字段拆解/输入等级 Lv1-4/平台语法 MJ-SD-FLUX/图生图参数/反编译七六维度）：本任务不产出文生图或图生视频的平台 prompt，图片加工在 agent 侧执行 ⇒ 整章跳过；仅把「安全校验-侵权」落成 anti_patterns 的「禁来源不明素材」。
  · RAG 历史偏好增强、教学模式：无历史对话可提取、用户未要求「教我写」⇒ 跳过。
  · Step 6 确认：属默认直接执行（未列大方向歧义需用户挑）⇒ 不生成确认话术；Step 2 的理解直接写进 context。
  · 七步闭环 ③ A-ask-questions：本任务只交两件、不反问 ⇒ 不适用；G6 已废止，按规范不声明也不写「跳过 G6」。
11 交付物 vs 运行时产物：因「打包/导出」命中，artifact_rules 排除加工中间产物与基线快照，并要求辅助文件落仓库外，避免污染改动面核验。
12 自评最不确定的一处：把「页面好看」的可执行范围压到只剩图片替换（要动 HTML/CSS/JS 的一律进「超范围改进清单」），是对红线 B 的窄读；若用户本意允许改样式，本 prompt 会明显欠交付。
13 诚实核对：上述引用的每个段名（role/context/thinking/task/done_criteria/constraints/anti_patterns/phases/context_budget/artifact_rules/output_format/verification/hard_constraints）与「超范围改进清单」「未替换清单」「3 视角取舍表」「部署就绪」均已在交付件中逐字验证存在（见收尾 missing 数）。
