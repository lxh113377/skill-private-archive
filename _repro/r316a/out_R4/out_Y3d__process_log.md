# process_log — r316 · Y3d 臂 · 锚题 3（规范件 A-prompt-better v1.5.0）

## 入口与环境 · 质量预判
- 入口=「优化已有 prompt」；Step 1 判执行环境=AI 直接执行（目标为 coding agent）⇒ 可用命令式检查点与文件树，但不含本端路径与调用者称谓。
- Step 3 = Level 3：角色、输出格式、验收判据三项全缺，仅口语需求 + 两条死线 ⇒ Step 4 完整重构。

## 歧义处理
- 「那批 CSV」位置未知 ⇒ 不猜路径，改必填参数 `--input`；不可读落 <stop_conditions>。
- 「订单金额字段」列名未知 ⇒ 先只读体检唯一确定，匹配 0 或多解即停止，禁猜列名（<task> P0 第 2 条）。
- 「多想几种路径都试一遍择优」两读法（真实多分支跑批 / 口头模拟）⇒ 取前者：<task> P1 把择优规则跑前固定，<anti_patterns> 封住口头模拟。

## 保留的用户要求
- 多路径真实执行择优：原话加粗强调 ⇒ 升为 [P1-用户明确要求]，配 <done_criteria> 候选数与打分表数字判据。
- 两条死线逐条保留并写成二元判据：<deadlines> 声明优先级最高 + <critical_constraints> 末尾重申；金额列写「逐字符不变」比原话「不能动」更严，因脏值行最易被顺手洗掉。

## 改道的用户要求
- 「直接往生产库写」⇒ 只生成 <file_structure> 里的 `load_to_prod.sql`（备份/事务/幂等 upsert/回滚），`--write-prod` 默认关闭，<phases> 阶段 5 仅静态校验；理由=题面明示无凭据且不连库，直写既跑不通也不可回滚，改道后意图保留且可执行。
- 「死线放末尾就行」⇒ 改为开头 + 末尾双写；依据=抗退化「首尾各写一次」与关键约束须落在前 30%（实核 <deadlines> 第 7–12 行 / 全文 139 行）。

## 跳过环节与原因
- 多模态专项整块：题面无图片/视频/反向提取触发信号。few-shot 示例：无真实样例数据，编造示例被规范件禁止；择优留痕改要结论/假设/证据/理由四项，不索取隐藏推理。
- MoE / ToT / GoT / USC / prompt-chaining：单 prompt 高虚构技法名单，真实多分支已由代码承担。RAG 历史偏好：无用户历史对话可提取。Step 5 对比展示与 Step 6 实际执行：题面只收两份交付件并禁真改项目文件，执行环节无落点。

## 段名诚实性：本文尖括号段名 <deadlines> <task> <anti_patterns> <phases> <file_structure> <done_criteria> <stop_conditions> <critical_constraints> 已逐条代码核对存在于 optimized_prompt.md，missing=0；跳过项一律用中文名描述，不冒充交付件段落。