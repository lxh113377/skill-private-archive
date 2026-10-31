# 超市销售 CSV 清洗脚本 — 交给 coding agent 的任务书

<role>
你是数据工程方向的 coding agent，在本仓库内交付一个可复跑的销售 CSV 清洗脚本及其验收产物。你写下的每一条判定，都必须能用一条命令复算。
</role>

<context>
- 输入：一批超市销售 CSV（本地文件）。实际路径、实际列名、实际脏法由你自己 profiling 得到，本任务书不预设。
- 执行环境：本地 git 仓库，单个 agent 会话；**无数据库凭据、不联网、不向任何外部系统写入**（本任务未提供 DSN）。
- 交付边界：只交付脚本与产物文件；生产数据加载不在本次范围内。
</context>

<hard_constraints>
两条死线（与本文件末尾的复述同权重；与其它任何段落冲突时，以本块为准）：
- **HC-1 订单金额字段不可改动**：金额列（按实际表头识别，识别结果写进报告）从输入到输出 MUST 满足 decimal 逐行等值。NEVER 对该列插值、填充、重算、单位或币种换算、四舍五入、格式化，或弱化为 float。做不到等值 ⇒ MUST fail-closed：中止并停止写出，同时把该行送入 quarantine。
- **HC-2 只允许改 clean/ 目录下的文件**：所有新建与修改的路径 MUST 以 `clean/` 开头；原始 CSV 一律只读；NEVER 写 clean/ 之外的任何路径。
</hard_constraints>

<task>
[P0-核心] 交付 `clean/clean_sales.py`：读输入 → profiling → 按选定候选清洗 → 写 `clean/out/`，并保证 HC-1 与 HC-2 可被机器校验。
[P0-核心] 交付 `clean/verify.py`：独立复核 HC-1（逐行金额等值）与 HC-2（写入路径范围），任一不过即非零退出。
[P1-增强] 多候选择优：实现 **≥3 个真实、确定性的候选清洗策略**（各自独立成函数、可单独跑），用客观指标打分后选优，候选/分数/淘汰理由写入 `clean/selection_report.md`。
[P1-增强] 交付 `clean/LOAD_PLAN.md`：把"立竿见影"落成一条待人工执行的加载方案（备份 → 导入 staging 库 → 行数与金额对账 → 回滚步骤）。本次 MUST NOT 执行其中任何一步。
[P2-锦上添花] CLI 开关（--dry-run / --candidate / --input-dir / --out-dir）、结构化日志、候选参数固定以保可复现。
</task>

<constraints>
- 本文件内的优先级：`<hard_constraints>` > `<done_criteria>` > `<phases>` > 其余段落；冲突时按此裁定。
- 脏数据形态（缺失、重复、表头/编码不一、金额含符号与千分位、日期混格式等）MUST 来自实际 profiling；未在数据中观察到的问题 NEVER 当作存在。
- 无法从数据确认的判断，MUST 在报告中以 `ASSUMPTION:` 前缀显式列出；没有假设就写「无」。
- 删除或改写任何行都 MUST 记录规则与被影响行数；MUST NOT 静默丢行。
- 默认 `--dry-run` 生效：不带显式开关不得写出 out/ 结果。
- "清洗质量"与 HC-1 冲突时，MUST 以 HC-1 为准：宁可少清洗、把该行隔离。
- 只用 Python 3 标准库或已存在的 pandas；NEVER 新增需联网安装的依赖；缺 pandas 时 MUST 退化为标准库 csv 实现。
</constraints>

<phases>
阶段 1 profiling → 检查点：`clean/profile.json` 存在，含实际列名、空值率、重复率、金额列样例形态。
阶段 2 候选实现 → 检查点：每个候选 `python clean/clean_sales.py --candidate=<id> --dry-run` 退出码 0。
阶段 3 打分与择优 → 检查点：`clean/selection_report.md` 出现 ≥3 行候选 × 分数 × 淘汰理由。
阶段 4 写出产物 → 检查点：`python clean/verify.py` 打印 `AMOUNT_UNCHANGED: PASS` 与 `SCOPE: PASS`，退出码 0。
阶段 5 交付自检 → 检查点：`git status --porcelain` 中除 `clean/` 外无条目。
前一阶段检查点不过 ⇒ MUST NOT 进入下一阶段。
</phases>

<anti_patterns>
禁止：脚本直连生产库或任何数据库写入 → 替代：只写 `clean/out/`，生产加载走 LOAD_PLAN.md 的人工闸（本次不执行）。
禁止：对金额列 fillna / 插值 / 重算 / 换算 / 四舍五入 / 改类型 → 替代：原样透传（decimal 等值），不满足等值的行进 quarantine。
禁止：in-place 覆盖原始 CSV → 替代：输入只读，输出仅写 `clean/out/`。
禁止：把"多想几种路径再挑"写成让脚本去"思考"（脚本无模型侧思考能力）→ 替代：≥3 个确定性候选函数 + 客观打分 + 择优选中者。
禁止：硬编码猜测的列名或表结构 → 替代：profiling 后建列名映射表并落盘。
禁止：靠删行来提高质量分 → 替代：任何删除写 audit 日志并计入报告。
禁止：`__pycache__/`、`*.bak`、中间临时文件混进交付 → 替代：临时件只落 `clean/tmp/`，交付前清空。
</anti_patterns>

<output_format>
产物（全部在 clean/ 下）：`clean_sales.py`、`verify.py`、`profile.json`、`selection_report.md`、`LOAD_PLAN.md`、`out/`（含 `out/quarantine/`）。
`selection_report.md` 固定段落：`## 结论` / `## 依据`（引用 profile.json 的具体数字）/ `## 候选对比`（表格）/ `## ASSUMPTION`。
最终回复固定三段：① 变更文件清单；② `<done_criteria>` 五条的**命令原文 + 实际输出末行**粘贴；③ 假设清单（或「无」）。
只写结论、依据与校验结果，不要输出内部推理过程。
</output_format>

<artifact_rules>
纳入交付：`*.py`、`*.json`、`*.md`、`out/*.csv`。
排除交付：`clean/tmp/`、`__pycache__/`、`*.bak`、被改动的原始输入、任何数据库文件。
</artifact_rules>

<done_criteria>
1. `python clean/verify.py` 退出码 0，且打印 `AMOUNT_UNCHANGED: PASS <N> rows` 与 `SCOPE: PASS`。
2. 输入↔输出逐行 join 后，金额列 decimal 等值率 = 100%（不一致行数 = 0）。
3. `git status --porcelain` 输出中不存在不以 `clean/` 开头的条目。
4. `clean/selection_report.md` 存在，含 ≥3 个候选的分数与逐条淘汰理由。
5. 代码与产物中无数据库连接串/凭据，运行期不发起网络请求（--dry-run 与写出两条路径都验）。
五条全绿才算完成；任一为红 ⇒ 视为未完成，不得声称已交付。
</done_criteria>

<verification>
交付前逐条自检：
- [ ] profile 里的列名与脏法确来自实测，而非本任务书的表述。
- [ ] 每个候选跑在同一份 profile 上，打分口径一致。
- [ ] 金额等值校验是逐行 join 比对，不是总量近似。
- [ ] quarantine 行数 + out 行数 == 输入行数（无静默丢失）。
- [ ] 未打开数据库、未联网、未写 clean/ 以外路径。
- 本任务书面向有真实文件系统访问的 agentic 工具：粘贴执行前请复核 scope lock（HC-2 的路径前缀）、forbidden actions（`<anti_patterns>`）与 stop conditions（`<done_criteria>` 任一为红即停），并确认文件路径、目录与权限与实际项目一致。
</verification>

<hard_constraints_repeat>
结尾复述（与开头 <hard_constraints> 同权重）：
**HC-1 订单金额字段不能动 —— decimal 逐行等值；做不到就隔离该行并 fail-closed，禁止任何重算/填充/换算/格式化。**
**HC-2 只许改 clean/ 目录下的文件 —— 其它路径一律不写，原始 CSV 只读，不连任何数据库。**
</hard_constraints_repeat>