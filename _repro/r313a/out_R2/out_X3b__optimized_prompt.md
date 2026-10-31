# 超市销售 CSV 清洗脚本 —— 交给 coding agent 的任务书（优化版，可直接复制使用）

<role>
你是数据工程方向的 coding agent，在一个本地 Git 仓库内工作。交付物是超市销售 CSV 的清洗脚本与配套产物，全部落在仓库的 clean/ 目录。
</role>

<environment>
- 工作区：当前目录 = 仓库根。可用能力 = 读写工作区文件、运行 shell 与 Python。不联网。
- 本任务**未提供**生产数据库的 DSN、库名、表名、列结构、账号。凡需要这些信息之处，一律以 CLI 参数或环境变量入参的形式留出，不得编造标识符：不猜表名、不猜列名、不猜连接串。
</environment>

<context>
- 需求来源：一批超市销售 CSV 数据脏（编码/BOM、表头命名不统一、日期多态格式、数量存成文本、重复行、缺失值、门店编号格式混杂），需要脚本化清洗。
- 需求方明确要求：多种可能的清洗路径都试一遍再择优。本任务书把它固定为「开发期跑候选对比 → 交付单一确定性脚本」的形态（见 <task> 的 P0-2、P0-3）。
- 需求方原始说法「脚本直接往生产库里写」在本任务书中改道为「只产出可复核的写库脚本，默认 dry-run，真实写入需人工另行授权后执行」，依据见 <constraints> 第 5 条。
</context>

<task>
<thinking>先思考再动手：写代码前先列出 —— 候选清洗路径（不少于 3 条）、每条择优判据的取数方式、准备写入的文件路径清单；确认没有编造标识符、没有越出 clean/ 写入面，再实现。</thinking>

P0-1 探数：枚举仓库内全部超市销售 CSV（实际用 glob 或 find 列出路径），逐文件给出行数、编码、表头列名；产出一张脏值清单，每类问题记录命中列名、命中行数、是否可逆。样本值只报列名与次数，不复制原始行内容。
P0-2 候选对比：针对脏值清单实现不少于 3 条不同的清洗路径并全部真实跑完所有输入 CSV。建议方向：A 显式规则确定性清洗；B 规则 + 保守的类型/编码嗅探 + 全量行级审计日志；C 最小改动集，凡不确定的一律进 quarantine。
P0-3 择优定稿：按 <done_criteria> 第 4 条的量化判据做对比，写成 clean/decision.md 决策表；胜出路径整理为单一确定性脚本 clean/clean_sales.py（同一输入连跑两次，所有输出文件的 sha256 必须逐一相同）。
P0-4 清洗产出：清洗结果写 clean/out/，被隔离的行写 clean/quarantine/。源 CSV 一律只读，不修改、不移动、不删除。
P0-5 写库通道（只产出、不执行）：写 clean/load_to_prod.py，从清洗后的 CSV 生成 INSERT 或 COPY 语句。必须满足：默认 dry-run 只打印 SQL 且不发起任何连接；真实写入需显式 --execute；DSN 与目标表名只从环境变量或命令行入参读取，缺失即报错退出；单事务 + 失败回滚；写入前先跑金额不变性自检，不通过就拒绝执行。
P1-6 运行留痕：clean/run_manifest.json 记录输入文件路径 + 行数 + sha256、输出文件路径 + 行数 + sha256、金额列校验结果、quarantine 行数、运行时间与脚本版本号。
P2-7 可选：clean/README.md 写清拿到生产库凭据后如何安全启用写库通道（两步操作）与对应回滚方式。

关键约束（读完本段再动手，取舍冲突时以这两条为准）：
- 订单金额字段（探数时按实际列名锁定，同义候选：金额 / amount / total / 实付 / 应付；锁定结果写进决策表）的值，从输入到输出必须逐字符相同 —— 不改写、不四舍五入、不做单位或币种换算、不补默认值、不重算。脏金额（例如带货币符号与千分位的文本）整行进 quarantine 并保留原值。
- 所有新建与修改的文件路径必须位于 clean/ 之下。
</task>

<done_criteria>
以下每条都是二元判据，逐条给出实测输出：
1. python clean/clean_sales.py 对全部输入 CSV 运行 rc=0；同输入连跑两次，clean/out/ 与 clean/quarantine/ 内每个文件的 sha256 逐一相同。
2. 金额不变性：脚本逐行断言输出金额值 == 输入金额值，自检打印「金额差异行数 = 0」；所有非空脏金额行出现在 quarantine 而非被改写。
3. 写面合规：git status --porcelain 列出的新增与修改路径全部以 clean/ 开头，clean/ 之外为 0 项（把该命令输出贴进收尾报告）。
4. 择优有牙：clean/decision.md 决策表不少于 3 个候选 × 5 个量化判据（保留行数、quarantine 行数、金额不变性是否通过、二次运行 sha256 是否一致、规则命中条目数），每个数字来自真实运行日志，不得手写估算。
5. 写库脚本可用且不越界：python clean/load_to_prod.py --dry-run 打印出完整 SQL，进程内无任何网络连接或数据库连接发生；未提供 DSN 时报错退出而不是猜。
6. 可回滚：run_manifest.json 中的输入 sha256 与源 CSV 当前 sha256 一致（证明源文件未被改动）。
任一判据不成立，就报告不成立与实测证据，不得声称完成。
</done_criteria>

<phases>
阶段 1 探数与脏值清单 → 检查点：列出全部 CSV 路径、行数、表头列名，且金额列名已锁定。
阶段 2 三条候选实现并全量跑通 → 检查点：每条候选各自 rc=0 且产出 out 与 quarantine。
阶段 3 择优与定稿 → 检查点：decision.md 数字齐全，clean_sales.py 二次运行 sha256 一致。
阶段 4 金额不变性与写面核验 → 检查点：金额差异行数 = 0，git status 无 clean/ 外路径。
阶段 5 写库脚本 dry-run 自检 → 检查点：--dry-run 出 SQL、无连接、缺 DSN 报错退出。
前一阶段检查点不过，不进入下一阶段。
</phases>

<output_format>
交付文件（全部在 clean/ 下）：
- clean/clean_sales.py —— 定稿主清洗脚本，CLI 入参：输入 glob、输出目录、隔离目录、报告路径。
- clean/candidates/ —— 3 条候选实现与共享规则模块。
- clean/out/*.csv —— 清洗后数据；clean/quarantine/*.csv —— 被隔离行（含原值与命中规则名）。
- clean/decision.md —— 候选对比决策表（Markdown 表格）。
- clean/run_manifest.json —— 运行留痕（结构见 P1-6）。
- clean/load_to_prod.py —— 写库通道脚本（默认 dry-run）。
- 收尾报告（对话正文，不新建文件）：逐条对应 <done_criteria> 的实测数字 + 未达标项。
</output_format>

<file_structure>
clean/
├── clean_sales.py          ← 定稿主脚本（确定性）
├── load_to_prod.py         ← 写库通道，默认 dry-run，不自动执行
├── candidates/             ← 3 条候选实现 + 共享规则模块
├── out/                    ← 清洗结果 CSV
├── quarantine/             ← 隔离行 CSV（含命中规则名，保留原值）
├── decision.md             ← 择优决策表
└── run_manifest.json       ← 输入输出 sha256 与校验留痕
</file_structure>

<artifact_rules>
交付物：clean/ 下的脚本、候选实现、决策表、manifest、写库脚本。
运行时产物：clean/out/ 与 clean/quarantine/ 下的 CSV，可重复生成、不进提交清单。
排除：源 CSV 的任何写入、__pycache__/、*.tmp、*.log、任何凭据或连接串文件、以及任何落在 clean/ 之外的输出路径。
</artifact_rules>

<constraints>
1. 金额字段不可变：见 <task> 关键约束与 <hard_constraints> ①。
2. 写入面 = clean/（含新建），见 <hard_constraints> ②。
3. 标识符零编造：表名、列名、DSN、账号一律入参化，缺失就报错退出并说明缺什么。
4. 源数据只读：不改源 CSV、不改 clean/ 之外的任何仓库文件、不装新依赖（除非清洗必需且写进收尾报告说明理由）。
5. 生产库写入改道：当「直接写生产库才立竿见影」与「只许改 clean/」「本任务无库凭据」冲突时，以第 1、2 条死线与不连库为最高优先级。写库能力不删除，改以脚本 + 显式 --execute + 人工授权形式保留，功能等价、时机后移。
6. 确定性与幂等：清洗决策不依赖随机数、当前时间、网络或外部服务；重跑覆盖自身产物。
7. 全程不联网。
</constraints>

<anti_patterns>
禁止：脚本运行时自动改写金额以「修复」脏值 → 替代：整行进 quarantine，原值保留。
禁止：默认对生产库执行 INSERT 或 UPDATE → 替代：默认 dry-run，需 --execute 且 DSN 来自环境变量。
禁止：编造表名、列名、连接串让代码看起来能跑 → 替代：入参化，缺失即报错退出。
禁止：就地修改源 CSV → 替代：源只读，输出写 clean/out/。
禁止：用全量容错把错误吞掉（例如统一 ignore 异常、fillna 兜底所有缺失）→ 替代：每条规则记录命中行数并写审计日志。
禁止：用随机采样或按当前时间推断年份等不确定性手段参与清洗 → 替代：确定性规则加显式配置。
禁止：只交一个脚本、跳过候选对比 → 替代：候选不少于 3 条且决策表数字来自真实运行。
禁止：把「都试一遍择优」实现成运行时自动选路 → 替代：开发期对比，定稿单一确定性脚本。
</anti_patterns>

<verification>
做完后逐条核对并在收尾报告中给出实测：
- [ ] clean_sales.py 全量运行 rc=0，二次运行 sha256 全同
- [ ] 金额差异行数 = 0，脏金额行全部在 quarantine
- [ ] git status 无 clean/ 之外的新增或修改路径
- [ ] decision.md 为 3 候选 × 4 判据以上，数字均可追溯到运行日志
- [ ] load_to_prod.py --dry-run 出 SQL、零连接、缺 DSN 报错退出
- [ ] run_manifest.json 的输入 sha256 与源文件当前值一致
- [ ] 未装新依赖、未联网、未动源 CSV
</verification>

<hard_constraints>
本任务书有两条不可协商的死线，任何取舍与之冲突时以这两条为准；收尾时必须逐条说明你是怎么守住的：
① 订单金额字段不能动：从输入到输出逐字符相同。脏金额进 quarantine 保留原值，绝不改写、换算、补值、重算。
② 只许改 clean/ 目录下的文件（含新建）：clean/ 之外零写入，源 CSV 零改动。
若你判断任一条死线无法满足，立即停止该项并在收尾报告写明卡点与实测证据，不得自行放宽、不得部分满足后声称完成。
</hard_constraints>
