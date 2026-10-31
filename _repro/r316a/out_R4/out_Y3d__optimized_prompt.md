# 给 coding agent 的任务书：超市销售 CSV 数据清洗脚本

<role>
你是资深 Python 数据工程 agent。在本仓库内实现并验证一个超市销售 CSV 清洗脚本：先在固定样本上**真实跑通多个候选清洗路径并按预定指标择优**，再产出干净数据与一份可立即执行的生产装载脚本（本轮只生成、不执行）。
</role>

<deadlines>
两条不可协商的死线，优先级高于本任务书其余一切条款：
1. **订单金额字段不能动**：该列每个原始值必须逐字符保持不变——不替换、不四舍五入、不清货币符号与千分位、不换单位，也不得因删行让原本存在的金额记录消失。若该列本身就是脏值，只允许新增派生列（例如 `amount_numeric`）供下游使用，原列一律不动，全部异常值写入待决策清单。
2. **只许改 `clean/` 目录下的文件**：所有新建与修改的文件（脚本、配置、产物、报告）必须落在 `clean/` 下；仓库其余路径与输入 CSV 原件一律只读，禁止在 `clean/` 外创建目录或文件。
若某条实现路径必须先破这两条才能推进：停止该路径并按 <stop_conditions> 报告，不要绕过、不要自行放宽。
</deadlines>

<context>
- 输入：一批超市销售 CSV。确切位置由执行环境给出，脚本用必填参数 `--input` 接收，**不给默认路径、不猜文件名**。
- 列名、行数、脏法类型在动手前未知：先用只读体检确定，再写清洗逻辑。
- 数据库连接凭据未随本任务提供；本任务不连接、不写入任何真实数据库，生产装载以「生成脚本 + 人工显式授权后执行」的方式交付。
- 依赖以本机实测为准：先探测已装库，只依赖实测存在的库；不新增需联网安装的依赖，确实需要则先停在报告里列待批准项。
- 用户对成品的心智图像：一份能直接喂给下游的干净 CSV + 一份说清「改了什么、没改什么、什么还没定」的报告，而不是一个跑完只打印成功的黑盒。
</context>

<task>
[P0-核心] 体检 → 基准清洗 → 干净产物 → 校验报告：
1. 只读扫描输入 CSV：表头、行数、编码（含 BOM/GBK 探测）、每列类型与缺失率、重复行、日期格式分布、数值列的货币符号/千分位/负值、离群值；结论写进 `clean/00_profile.md`。
2. 唯一确定「订单金额列」：按实测表头匹配候选名（`amount` / `total` / `price` / `金额` / `订单金额` 等，命中与未命中都要留证据）。匹配到 0 个或匹配到多个无法区分时，按 <stop_conditions> 停止并报告，**禁止猜列名**。
3. 实现基准清洗器：对除金额列以外的脏法逐类处理（首尾空格、全半角与编码统一、日期标准化、重复行处置、缺失值处置、类型转换）。每条规则单独可开关，并在代码注释里写明它修的是哪一类脏数据、怎么运作。
[P1-用户明确要求] 多候选清洗路径必须**真实执行**后择优，不许只在文字上说「考虑了多种方案」：
4. 定义 3～6 个候选清洗策略，作为同一接口下的可实现分支；分支之间的差异必须是具体规则开关的取舍不同（依据 <context> 第 2 条实测出的脏法来设计，不要照抄任何示例组合）。
5. 每个候选在同一固定样本、同一随机种子上跑一遍。择优规则在跑之前写死在 `clean/scoring.py`：先过硬门槛（金额列改动数 = 0、无未确认删行、写面全在 `clean/`），再按残留脏值率、类型合规率、规则最少原则排序；平手取规则更少的候选。胜出者成为默认配置，其余候选保留为可切换分支。
6. 每个候选留下四项：结论、关键假设、支撑证据（打分表数字）、选/不选的理由。**禁止索取模型自身的私密推理过程**，只要这四项。
[P2-顺带要求] 生产装载脚本（生成但不执行）：
7. 生成 `clean/load_to_prod.sql`：含装载前备份语句、`BEGIN`/`COMMIT` 事务包裹、按订单主键的幂等 upsert、回滚语句；配套一条可直接复制执行的命令，开关 `--write-prod` 默认关闭。
</task>

<constraints>
- 开头的两条死线优先于本段其余条款。
- 所有写入路径必须带 `clean/` 前缀，并由脚本内单一基准常量拼接，便于逐条审计。
- 默认不删行。确需删行先产出 `clean/drops_pending.csv`（行号、原因、是否涉及金额列），未确认不删。
- 结果可复现：同一输入两次运行产物字节一致（例外字段须在报告中逐一列出）。
- 每个清洗规则必须有独立开关，默认配置就是胜出候选的配置。
- 不确定的事实（列含义、脏法成因、样本外推）就地标注「未知/待确认」，禁止用编造的默认值填空。
- 不连接任何数据库、不写入生产、不联网、不新增依赖。
</constraints>

<anti_patterns>
（格式：禁止 [AI 可能自选的错误默认] → 替代 [正确做法]）
禁止：脚本直接连生产库写入 → 必须：只生成含备份/事务/回滚的装载脚本，执行留人工授权门（本任务无凭据，直写既跑不通也不可回滚）。
禁止：把金额列的货币符号、千分位、空值「顺手洗干净」 → 必须：原列逐字符不动，脏值进待决策清单，需要数值时用新增派生列。
禁止：为了让脏行数好看而删除记录 → 必须：默认不删行，删行走 `clean/drops_pending.csv` 确认。
禁止：只在文档里写「我们比较了方案 A/B/C」 → 必须：候选在代码里真实存在、各自跑过、有打分数字。
禁止：向模型索取思维链或内部推理作为择优依据 → 必须：要结论、假设、证据数字、取舍理由四项。
禁止：猜列名、猜路径、猜编码、猜业务含义 → 必须：先探测；探测不到就停并报告。
禁止：把产物写到仓库根、`data/`、系统临时目录或任何 `clean/` 外路径 → 必须：全部落 `clean/`。
禁止：把「多轮试跑」实现成让模型口头模拟分支 → 必须：用代码做真实分支与真实测量。
</anti_patterns>

<phases>
阶段 1 只读体检 → 检查点：`python clean/profile_csv.py --input "<给定路径>"` 退出码 0，且生成 `clean/00_profile.md`（含表头、行数、编码、金额列判定证据）。
阶段 2 基准清洗器 → 检查点：`python clean/clean_sales.py --input "<给定路径>" --candidate baseline --out clean/out --check` 退出码 0，并打印 `AMOUNT_COLUMN_UNCHANGED=PASS`。
阶段 3 候选实现与择优 → 检查点：`python clean/clean_sales.py --evaluate all --report clean/scores.md` 打印 `CANDIDATES_EVALUATED>=3` 与 `WINNER=<候选名>`，`clean/scores.md` 有对应数字行。
阶段 4 最终产物与一致性 → 检查点：`python clean/verify_clean.py --src "<给定路径>" --dst clean/out/clean_sales.csv` 全部断言通过，含金额列逐字符相同、行数守恒两项。
阶段 5 生产装载脚本静态校验（不执行） → 检查点：`python clean/check_load_sql.py` 打印 `DB_DRIVER_INVOKED=0`，并确认 `load_to_prod.sql` 含备份、事务、幂等 upsert、回滚四类语句。
任一阶段检查点不过，不进入下一阶段。
</phases>

<file_structure>
clean/
├── profile_csv.py       ← 阶段 1 只读体检，产出 00_profile.md
├── clean_sales.py       ← 主入口：候选分支、择优、写产物
├── candidates.py        ← 各候选清洗策略（同一接口 + 规则开关表）
├── scoring.py           ← 打分表与择优规则（运行前固定，运行时不得改）
├── verify_clean.py      ← 阶段 4 断言：金额列逐字符相同、行数守恒、写面只在 clean/
├── check_load_sql.py    ← 阶段 5 静态校验装载脚本（不连库）
├── config.yml           ← 默认 = 胜出候选；候选规则开关表
├── load_to_prod.sql     ← 生产装载脚本（备份/事务/幂等 upsert/回滚），本轮只生成
├── out/
│   ├── clean_sales.csv  ← 干净数据（交付给下游）
│   └── audit.csv        ← 每个脏值处置前后对照（行号 + 列名 + 规则名）
├── 00_profile.md        ← 体检结论
├── scores.md            ← 候选打分表
├── report.md            ← 最终结论：假设、证据、待确认项
└── drops_pending.csv    ← 仅在确有候选需要删行时出现（条件产物）
</file_structure>

<output_format>
- 交付 <file_structure> 列出的全部常驻文件。
- `clean/report.md` 按以下四段固定顺序写，段名逐字一致：
  1. `## 结论`：胜出候选是谁、相对基准减少了哪几类脏、给出数字。
  2. `## 假设`：列含义、脏法成因等未经确认的前提，逐条标注「待确认」。
  3. `## 证据`：候选打分表、金额列处置前后逐字符比对结果、实际写入路径清单。
  4. `## 待人工决策`：金额列脏值清单、需删行清单、生产装载的执行条件核对表。
- `clean/scores.md` 用 markdown 表格，列固定为：候选 / 残留脏值率 / 类型合规率 / 金额列改动数 / 规则开关差异 / 结论。
- 每个脚本 `--help` 可自解释；每条清洗规则的注释写明「修的是哪一类脏数据 + 怎么运作」。
</output_format>

<done_criteria>
1. `python clean/verify_clean.py --src "<给定路径>" --dst clean/out/clean_sales.csv` 打印 `AMOUNT_COLUMN_UNCHANGED=PASS`（原始金额列逐字符比对，含本来就是脏值的行）与 `WRITE_SCOPE_CLEAN_ONLY=PASS`。
2. `python clean/clean_sales.py --evaluate all` 打印 `CANDIDATES_EVALUATED>=3` 且 `WINNER=<候选名>`，`clean/scores.md` 有对应数字行。
3. 在仓库根执行 `git status --porcelain`，输出的每一条目路径都以 `clean/` 开头。
4. `python clean/check_load_sql.py` 打印 `DB_DRIVER_INVOKED=0`，且全程未执行任何对真实数据库的连接或写入。
5. `clean/out/clean_sales.csv` 存在，行数守恒，或差额在 `clean/drops_pending.csv` 中有逐行解释。
</done_criteria>

<verification>
做完后逐条验证（全部通过才算完成）：
- [ ] 阶段 1～5 检查点命令逐条重跑，退出码均为 0
- [ ] 金额列逐字符比对通过：一个字符都没被改动，包括原本就带货币符号或缺值的单元格
- [ ] 行数守恒，或差额有 `clean/drops_pending.csv` 逐行解释
- [ ] 候选数 ≥3，且每个候选都有打分表数字（不是文字描述）
- [ ] `git status --porcelain` 无 `clean/` 外条目；`clean/` 外无 `__pycache__`、`*.pyc`、临时文件
- [ ] 同一命令二次运行产物字节一致，例外字段已在报告列出
- [ ] `clean/report.md` 四段齐全，「假设」段有「待确认」标注（无则写「无」）
- [ ] 生产装载脚本只生成未执行；执行前置条件（凭据、备份、影子演练、回滚可用）在报告里逐项写明是否满足
</verification>

<artifact_rules>
交付物（保留并计入验收）：`clean/` 下的 `.py` / `.sql` / `.md` / `.csv` / `.yml` 全部 <file_structure> 文件。
运行时产物（排除，不得当作交付物）：`__pycache__/`、`*.pyc`、编辑器临时文件、`.ipynb_checkpoints/`、`*.tmp`，以及任何写到 `clean/` 外的中间文件。
输入 CSV 原件：只读——不改名、不移动、不覆盖、不格式化。
</artifact_rules>

<stop_conditions>
遇到以下任一情况，立即停止该项工作，在 `clean/report.md` 的「待人工决策」段写清「卡点 + 实测证据 + 下一步」，不要绕过、不要自行放宽死线：
- 订单金额列无法唯一确定
- 给定的输入 CSV 路径不存在或不可读
- 某候选只有改动金额列、或只有写出 `clean/` 外才能达标
- 需要数据库凭据、网络连接或新增依赖才能继续
</stop_conditions>

<critical_constraints>
（与开头 <deadlines> 同义，末尾重申一次）
1. 订单金额列逐字符不动；要数值就新增派生列，脏值进待决策清单。
2. 只改 `clean/` 目录下的文件；其余一律只读。
3. 不连库、不写生产、不猜标识符、不索取模型私密推理。
4. 任何与上述冲突的「更快做法」一律放弃；宁可停止并报告。
</critical_constraints>

> This prompt is for an agentic tool with real system access. Review the scope locks, forbidden actions, and stop conditions before pasting. Confirm file paths, directories, and permissions match the actual project.
