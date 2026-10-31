# 判断记录（r317 轮次 5 · task2 · Y2e 臂 · 同题第 5 轮）
入口判定：用户已给具体请求文本 → 走「优化已有 prompt」→ Step 2 歧义 → Step 3 质量预判（Level 3：约束位置错、验收缺失、方法句空转）→ Step 4 技术/执行类策略（结构化 + 禁止项 + Done 判据 + 阶段检查点 + 交付物规则）。
环境探测：目标执行体是会改文件、跑命令、能部署的 coding agent（agentic）→ 必带作用域锁定与停止条件；交付形态 = 可直接使用的 prompt 本体。
歧义 1「想全面一点、多从几个角度反复推敲」：按文档高虚构风险清单，不套 Tree of Thought / Mixture of Experts / Universal Self-Consistency；改成 <review_angles>：三视角（视觉一致性 / 边界与数据完整性 / 交付与回滚）各跑两轮，每视角只交缺陷 + 修复 + 复验命令。
歧义 2「页面也要好看起来」与「只许改 assets 目录里的图片」互斥：不静默放宽边界。处置 = <scope_locks> 第 2 条 + <task> P0-2（同名覆盖把观感在资产层拉起）+ P2-7 需授权清单 + <stop_conditions>「需改 assets 之外文件即停」。
歧义 3「直接让它自己跑完部署上线」：保留原意不删，加门：<phases> 阶段 3 先记回滚点、阶段 4 线上复验；<anti_patterns> 禁止把未过检查点的版本推上线。
约束位置裁定：用户要求两条硬限制「写在任务书最后」→ 末尾 <critical_constraints_recall> 保留，同时前移一份到 <scope_locks>（落在前 30%）；依据 = 文档「长上下文遗漏 → 首尾各写一次」。
文件名与格式冲突补位：重命名 / 改扩展名会迫使 HTML 引用跟着改（越界），故 <anti_patterns> 明禁，并要求同名覆盖、备份不留 assets。
保留的用户要求：价格不动、只改 assets 图片、末尾位置（保留非删除）、下游 agent 自己部署、方法自定。
新增可对应交付物的项：sha256 前后 diff=0（<done_criteria> 1）、越界路径核对（<verification> 1-2）、引用零失效（<done_criteria> 3）、需授权清单四列表（<output_format> 4）、停止条件五条（<stop_conditions>）。
未添加用户没要求的内容：不引新框架、不改构建链、不做站点重构（见 <anti_patterns> 禁止装依赖 / 改 CI）。
形态声明：交付件段名全部为尖括号 XML 标签（<role> 起、</critical_constraints_recall> 收），首行是一级标题、不含路径或规范件名，正文未被代码栅栏整体包住。
段名诚实核对：本 log 点名 11 个段名（尖括号标签：<review_angles> <scope_locks> <task> <stop_conditions> <phases> <anti_patterns> <critical_constraints_recall> <done_criteria> <verification> <output_format> <role>），代码逐一 grep 交付件，missing = 0；交付件共 13 个闭合段。
零内部引用核对：交付件内 grep「优化前 | 核心改动 | 其他调整 | 任务书 | 派发 | 执行体 | 老大 | 原始请求 | 原文」= 0 命中；作用域复核写成执行 agent 的第 0 步自检动作，不直呼派发人。
自评：最强处是把「只改图片」与「页面变好看」的互斥显式化并给了不越界的出路；弱处是需授权清单会让「页面变好」看起来没做完——这是硬边界换来的代价。
