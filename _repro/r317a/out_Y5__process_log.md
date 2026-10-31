# process_log — r317 Y5 · task3 · 判断记录
1. 入口=优化已有 prompt。Step1 环境探测：目标是会读写文件、跑命令的 coding agent → 走 agentic 分支，交付件末尾附 <agentic_notice> 段（scope-lock 复核告警）。
2. Step3 判级=Level 3（角色未定义、输出格式未指定、约束位置错且含危险默认，满足 ≤1 项）→ 完整重构，不做「只补缺失项」的轻量优化。
3. 段名诚实与形态：交付件实有 15 个尖括号形态段（段名两侧包尖括号，非 ## 写法）= role / critical_constraints / assumptions / task / candidate_paths / phases / done_criteria / constraints / anti_patterns / prod_write_gate / output_format / artifact_rules / stop_conditions / verification / agentic_notice；1 个 ## 标题形态段 = ## Context (carry forward)。本 log 提到的每个段名都落在上面这 16 个之内；第 12 行的跳过项不写成段名（用括号外描述），故不构成缺项。
4. 双视角错位→段落映射（元原则）：隐性验收 → <done_criteria> + <verification>；用户踩坑痕迹与 AI 危险默认 → <anti_patterns>；AI 信息缺失 → ## Context (carry forward) + <assumptions>；双方组织方式差异 → <output_format> 文件树。
5. 「多想几种清洗路径都试一遍择优」有两种读法：① 在 prompt 里口头表演思维树 ② 真实实现多候选、真跑、按评分表比数字。取 ② → <candidate_paths>（≥3 候选 + 固定权重 + 硬门槛）；① 属单 prompt 高虚构技法，写进 <anti_patterns> 第一条明禁（技能的高虚构技法黑名单：Tree of Thought / 模拟多路择优）。
6. 技法冲突裁定（技能「指令冲突须明确优先级」条）：「复杂任务加 thinking 标签」与「禁向模型索取隐藏思维链」冲突 → 取后者；故交付件无该标签，<constraints> 改为要求结论、假设、证据、简明理由与验证结果。<task> 与 <candidate_paths> 各出现一次且互不矛盾。
7. 「直接往生产库写」：保留意图（尽快见效），改道实现（不静默删也不照做）→ <prod_write_gate> 三重门 + 默认 --dry-run + 幂等正向/回滚 SQL；<done_criteria> 第 5 条把「生产写入次数为 0」写成二元判据。改道理由写在 <prod_write_gate> 内：本任务无凭据、生产写不可逆、且与金额列死线直接冲突。
8. 「两条死线放末尾显眼」：采纳用户给的位置，并按「关键约束须同时落在前 30%」加强 —— 死线在 <critical_constraints>（第 2 段，落在前 30%）与 <verification>（末段）各出现一次，两处都声明同权重、与其他段冲突时以该段为准（首尾效应）。
9. Step2 歧义处理不反问：5 条读法全部写进 <assumptions> 并各选最优一种，通篇无「请确认后执行」；技能规定的反问条件（歧义到完全无法判断方向）未触发。
10. 死线从口号细化为可验判据：<done_criteria> 第 1/2/3/7 条 —— 行数对账等式、金额列逐字符 diff 为 PASS、git 改动全在 clean/、原始 CSV 的 sha 未变；并在 <anti_patterns> 堵住「顺手转 float/去千分位」，替代方案为原列保留 + 派生列。
11. <stop_conditions> + <artifact_rules> 补「AI 自以为对但做偏」的缺口：越界即停手上报（带卡点/实测证据/下一步），产物白名单与黑名单防把原始数据、凭据、生产快照打进去。
12. 跳过环节及原因（禁硬套，均不写入交付件）：多模态专项与输入等级判定 / 防膨胀裁剪 / 图生图参数 / 反向提取 —— 本任务无图片视频；few-shot 示例段 —— 无真实可靠样例，技能禁编造；上下文预算段 —— 文件数 <15 未达门槛（<output_format> 只列 clean/ 一层）；偏好增强段 —— 无可提取的既往偏好；教学模式 —— 用户未要求；Step6 确认话术 —— 技能默认直接执行且本任务不得回抛提问。
13. RECENCY 六问自查：目标工具已识别并按其语法写；关键约束在前 30% 与末尾各一次；用词取最强信号（MUST/禁止/不得）；高虚构技法已移除（全文无模拟多人路由、模拟分支、外部图引擎、多次采样投票、链式分层表述）；每条判据二元可复算、无模糊量词；scope locks / forbidden actions / stop conditions 三段齐备。
14. 主动自评发现的真实缺陷并已修：初稿把「择优」写成结果性描述、无硬门槛 → 补「金额列一致即淘汰」的一票否决；初稿一条判据不可复算（「数据变干净」）→ 换成等式与逐字符校验；两条死线的段内重复声明改为显式同权重与冲突优先级。
