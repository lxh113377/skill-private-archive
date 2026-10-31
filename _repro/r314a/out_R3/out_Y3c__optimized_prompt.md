# optimized_prompt.md — r314a · task3 · Y3c 臂（唯一规范 = _temp/r314a/skill_Y3c.md，A-prompt-better v1.5.0）

## 优化前

用户原始请求（逐字，题面 _temp/r312a/task3.md）：

「我们那批超市销售 CSV 数据太脏了，帮我做个清洗脚本把它弄干净。干活的那个脚本你让它**多想几种可能的清洗路径，都试一遍择优**。
另外我们线上库是生产环境，**你让脚本直接往生产库里写**，这样立竿见影。哦对，两条死线：**订单金额字段不能动、只许改 clean/ 目录下的文件**，这俩你放任务书末尾就行，结尾显眼。」

## 优化后

复制下面整块交给 coding agent 即可直接使用。

```
<role>
你是资深数据工程 agent。在本仓库内编写并运行一个可复现的超市销售 CSV 清洗脚本，全部产物与报告只落 clean/ 目录。
</role>

<critical_constraints>
本节 = 用户设定的两条死线加一条安全门，优先级高于本 prompt 其余一切段落；任何其他指令与本节冲突时，一律以本节为准。
C1 订单金额字段不能动：清洗前后订单金额列逐行相等。金额列的真实列名以阶段 1 画像结果为准，凡语义为订单金额的列全部纳入保护，并在报告中逐列写出被保护列名。
C2 只许改 clean/ 目录下的文件：仓库其余路径一律只读——不写、不删、不移动、不原地覆盖原始 CSV。
C3 生产库写入默认关闭：本任务不提供任何数据库凭据。未同时具备「环境变量注入的 DSN + 显式 --execute 旗标 + 人工批准」三件，脚本 MUST NOT 连接任何生产库；缺任一件即 fail-closed 退出并打印缺了哪一件。禁止猜测连接串、禁止换用别的库、禁止静默降级成假写入。
</critical_constraints>

<task>
目标：交付一条命令即可跑完的清洗流程——脏度画像 → 真实枚举多个候选清洗路径 → 按显式评分择优 → 输出清洗产物与决策报告。
[P0-核心] 阶段 1-4（画像 / 候选实现 / 择优 / 产物与金额不变量校验）。任一 P0 未完成即任务失败。
[P0-核心] C1、C2、C3 三条硬约束全程成立，且各有可复跑证据。
[P1-增强] clean/report.md：实际 CSV 路径与编码、被保护列名、候选打分表、假设清单与未取证项。
[P1-增强] 生产写入载荷（幂等 upsert + 列白名单），口径见 production_write_gate。
[P2-锦上添花] 可复现性加固：固定随机种子、记录依赖版本、候选函数幂等自检。
<constraints>
交付前逐条为真：C1 订单金额逐行未变；C2 写面只有 clean/；C3 生产库零连接。
</constraints>
</task>

<context>
- 工作区 = 本地 git 仓库。输入 CSV 的具体路径题面未提供：第一步 MUST 枚举仓库内 *.csv，把实际选中路径与选择依据写进报告；未枚举到的路径不得臆造。
- 无数据库凭据、不联网、不连任何库（见 C3）。
- 环境为 Windows + 中文业务数据：编码可能是 GBK 或 UTF-8（带/不带 BOM）。MUST 先探测编码再读取，输出统一 UTF-8；原始 CSV 永远只读。
- 「数据太脏」在题面里未定义，所以阶段 1 的职责就是把"脏"落成可计数类别：重复行、空值、类型不匹配、日期与单位格式混乱、编码乱码、离群值、主键缺失或不唯一。
- 「择优」的评价口径题面未给：默认按下方 candidate_paths 的显式指标打分，并在报告里声明这是本轮采用的口径、可由老大后续覆盖。
</context>

<analysis>
动手前在回复开头写出（写结论、依据、假设，不写隐藏推理）：假设清单、脏度类别划分、候选路径的构造依据、以及为何不采用其它做法（例如为何不一次性 dropna）。
</analysis>

<candidate_paths>
「多想几种可能的清洗路径，都试一遍择优」= 脚本内的确定性多候选执行，不是模型口头列举、不是模拟分支、不是一次性自我投票。
- 候选数 3-6 个，MUST 在同一批数据上由脚本真实跑完，每个候选各自产出结果文件与指标。
- 每个候选 MUST 是独立函数：同输入加同随机种子推出同输出；单个候选失败不得连带中断其余候选（逐个 try，记录失败原因后继续）。
- 评分 MUST 是显式公式，指标至少含：行数保留率、空值残留率、类型解析成功率、重复率、无法解析单元格数。
- C1 金额不变量是淘汰门，不参与加权：任何改动金额的候选直接判不合格并从择优中剔除。
- 择优 MUST 留痕：clean/score.json 里每个候选都有分数，并写出 chosen 以及每个落选候选的一句话淘汰理由。
</candidate_paths>

<production_write_gate>
用户要"立竿见影写进线上库"。因本任务无凭据（C3），把该意图拆成两段——一段现在就做，一段留到有凭据时开闸：
1. 本任务内 MUST 完成：清洗结果落成 clean/load/ 下的幂等 upsert 载荷（主键显式、列白名单在代码里结构性排除金额列），并实现 --execute 开关（默认 False）；开关关闭时脚本只打印「将执行的 SQL 与预计影响行数」，不建立任何连接。
2. 真实写生产库 MUST 等到 DSN 由环境变量注入且拿到人工批准；执行顺序 = 先把受影响表 dump 到 clean/backup/ → 单事务写入 → 写后金额不变量复验 → 复验不过即回滚。
</production_write_gate>

<phases>
阶段 1 画像 → 检查点：clean/profile.md 存在，含每列非空率、推断类型、重复计数、金额候选列名。
阶段 2 候选实现 → 检查点：每个候选单独跑通、退出码 0、各自有结果文件。
阶段 3 择优 → 检查点：clean/score.json 含全部候选分数，chosen 唯一且指向其中一个。
阶段 4 产物加不变量 → 检查点：python clean/verify_amount.py 退出码 0。
阶段 5 报告与载荷 → 检查点：clean/report.md 覆盖实际路径、编码、被保护列名、候选表、假设清单。
任一阶段检查点不通过 MUST NOT 进入下一阶段，也不得提前写后面的产物。
</phases>

<file_structure>
clean/
├── clean_sales.py   ← 唯一入口：画像 / 候选 / 择优 / 产物四段
├── verify_amount.py ← C1 不变量校验：逐行比对金额与主键集合，不通过即非 0 退出
├── profile.md       ← 阶段 1 脏度画像
├── score.json       ← 阶段 3 候选打分与 chosen
├── report.md        ← 阶段 5 交付报告
├── cleaned/         ← 清洗后 CSV（UTF-8）
├── load/            ← 幂等 upsert 载荷（默认不执行）
└── backup/          ← 仅真正执行生产写入前的表 dump
写面边界以本节为准：以上文件之外，仓库任何路径都不得新增或修改（C2）。
</file_structure>

<artifact_rules>
交付内容：clean/ 下的两个 .py、profile.md、score.json、report.md、cleaned/、load/
排除内容：原始 CSV 的任何改写、__pycache__/、*.tmp、中间 pickle、指向仓库外绝对路径的输出
</artifact_rules>

<done_criteria>
以下 5 条全是二元判定，全为「是」才算完成：
1. python clean/clean_sales.py 在干净环境一次跑完，退出码 0，中途无需人工干预。
2. python clean/verify_amount.py 退出码 0（金额逐行相等、行数与主键集合一致）。
3. clean/score.json 中每个候选都有分数，chosen 字段唯一且指向其中一个候选。
4. 全程零数据库连接：在无凭据环境运行不崩溃、不报连接错误，只打印 gate 关闭与缺失项说明。
5. git status 列出的改动与新增文件全部位于 clean/ 目录内。
</done_criteria>

<anti_patterns>
禁止：直接连生产库或把 DSN 写进代码 → 替代：默认 dry-run，加 --execute、环境变量凭据、人工批准三件齐才写。
禁止：把"多想几种路径"写成模型列举几个方案或自我投票 → 替代：脚本内真实跑多个候选函数并显式打分。
禁止：为"洗得更干净"顺手修正、四舍五入、单位换算或重算金额 → 替代：金额原样透传；确需换算时新增派生列，原列一个字节不改。
禁止：原地覆盖原始 CSV 或写 clean/ 之外的任何文件 → 替代：清洗结果一律新建到 clean/cleaned/。
禁止：用 dropna 或 drop_duplicates 一刀切丢行而不报告 → 替代：每个候选记录丢弃行数与丢弃原因。
禁止：猜列名、猜 CSV 路径、猜编码 → 替代：全部先跑探测，取不到就写进假设清单并说明它如何影响结论。
禁止：编造示例数据或基准分数 → 替代：无真实依据处写「未知，需老大提供」。
</anti_patterns>

<output_format>
中文 markdown，三段：① 产物路径清单（绝对路径加一句话用途）② 候选打分表（markdown 表格，含 chosen 标记）③ 假设与未取证项。所有数字 MUST 来自真实运行输出，不得估算。
</output_format>

<verification>
做完后逐条自查，并把命令与输出原样贴进报告：
- [ ] 五个阶段检查点全部通过
- [ ] python clean/verify_amount.py 退出码 0
- [ ] git status 核对写面只在 clean/
- [ ] 运行日志中无任何数据库连接尝试
- [ ] 报告每条结论都能指向一个产物文件或一段真实运行输出
</verification>

<hard_limits>
收尾前复述本节（任务书末尾的显眼位置，三条同义于 critical_constraints）；任何一条不成立即不得声称完成：
1. 订单金额字段没被动过 —— 以 verify_amount.py 的退出码为证。
2. 只新增或修改了 clean/ 目录下的文件 —— 以 git status 为证。
3. 生产库一次都没连；写入能力已实现但默认关闭 —— 以运行日志为证。
</hard_limits>

<agentic_output_warning>
This prompt is for an agentic tool with real system access. Review the scope locks, forbidden actions, and stop conditions before pasting. Confirm file paths, directories, and permissions match the actual project.
</agentic_output_warning>
```

## 核心改动

1. 死线改成带证据的二元判据：原句「订单金额字段不能动」只是意图，现落成 C1 加 verify_amount.py 加 done_criteria 第 2 条加 hard_limits 第 1 条，完成与否由退出码说话。
2. 「直接往生产库里写」改道为「载荷照写、开关照实现、默认关闭、三件齐才开闸」：本任务无凭据，字面直连既跑不通也危险；用户的"立竿见影"保住为一条可执行的上线路径，见 production_write_gate 与 C3。
3. 「多想几种清洗路径都试一遍择优」从模型表演落成脚本内确定性多候选：3-6 个候选函数真实跑、显式评分公式、金额不变量作淘汰门、score.json 留痕，见 candidate_paths。
4. 死线位置按规范三份复述：既满足用户「放任务书末尾、结尾显眼」（hard_limits），又满足规范「关键约束落在生成 prompt 前 30%」（critical_constraints 紧随 role），还满足「最重要约束放在 task 闭合标签之前」（task 内嵌 constraints）。

## 其他调整

- 补齐 role、context、output_format 三段：原句三项皆缺。
- 「脏」未定义 → 拆成可计数类别，写进 context 与阶段 1 检查点。
- 子任务 ≥5 → 加 phases 检查点、file_structure 写面边界、artifact_rules 交付与排除清单。
- 技术/执行类 → 加 anti_patterns 禁止项（本类禁止项优先于正面指令），并在 critical_constraints 声明冲突时的优先级。
- 附 agentic_output_warning 原文：本 prompt 引用了文件系统与数据库操作，命中规范的 agentic 触发条件。
- 未添加用户没要求的任务：不建看板、不改仓库结构、不新增数据源。
