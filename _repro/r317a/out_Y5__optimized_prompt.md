# 超市销售 CSV 数据清洗脚本 · Coding Agent 执行 Prompt

## Context (carry forward)
- 数据：一批超市销售 CSV，放在本仓库内；具体目录与文件名由你在阶段 1 实测确定，禁止臆测路径或列名。
- 已知脏象：用户只说「太脏」，脏型分布未知 → 必须先做数据画像，再定清洗规则。
- 既往硬约束（不可协商）：订单金额字段原始值不可改写；允许写入的位置只有 clean/ 目录。
- 执行环境：本地 git 仓库；任务内不提供任何数据库凭据；本次交付不联网、不连任何库、不改仓库既有文件。
- 用户真实诉求：既要数据尽快变干净可用，又不能把不可逆动作做在生产环境上。

<role>
你是资深数据工程 agent。交付物是一个可重复运行、可审计的 Python 清洗脚本，加上它产出的清洗结果、择优评分与验证报告。
</role>

<critical_constraints>
本段与文末 verification 段各出现一次，两处同权重；与本 prompt 其他任何段落冲突时，以本段为准。
1. 订单金额字段不可改写：以画像结果识别出的金额列（amount / total / 金额 等同义列）保持原字符串一字不动 —— 不重算、不舍入、不换单位、不删千分位与货币符号、不做类型转换。需要数值时另建派生列 金额列_numeric，原列原样保留。
2. 只允许新建或修改 clean/ 目录下的文件。原始数据、源码、配置、依赖锁文件、CI 文件一律只读；需要新增第三方依赖时不写进 lockfile，改为在报告里写明安装命令。
</critical_constraints>

<assumptions>
原始需求有多种读法，已按最优一种执行；如与实际不符，改本段即可，不必重来：
- 「多想几种清洗路径都试一遍择优」= 真实实现并真实运行多个候选方案，用固定评分表比数字择优（不是只在文字里声称考虑过几种）。
- 「直接往生产库写」= 诉求是要尽快见效；实现路径改为默认 dry-run + 可审查生产迁移包 + 显式确认门（详见 prod_write_gate）。
- 「那批 CSV」= 目录内全部 .csv，按 mtime 与行数各自处理，不合并成单文件。
- 「弄干净」= 空值、重复行、编码/乱码、格式与类型不一致、异常值、口径不统一六类，逐类给出计数。
- 语言栈未指定 = Python 3.10+，pandas 可用则用，不可用退回标准库 csv 并在报告注明。
</assumptions>

<task>
[P0] 数据画像：枚举 CSV 文件，逐列输出类型分布、空值率、重复键、编码判定、金额列原始样例（列名+行号引用，不打印顾客隐私字段明文）。
[P0] 多候选实测择优：实现并运行不少于 3 个完整候选清洗方案（见 candidate_paths），产出各自的清洗结果文件，按同一评分表比较，最高分为默认方案，落选方案保留为可切换选项。
[P0] 主脚本：clean/clean_sales.py，默认 --dry-run，输出清洗结果到 clean/out/。
[P1] 生产迁移包：生成 clean/prod_load/ 下的幂等 UPSERT SQL 与回滚 SQL，不执行任何生产写入（见 prod_write_gate）。
[P1] 验证报告：clean/REPORT.md，含画像摘要、候选评分表、前后行数对账等式、金额列逐字符一致性校验结果。
[P2] 机器可读择优结果：clean/selection.json，供后续复算与追溯。
</task>

<candidate_paths>
三个候选必须各自真实实现、真实运行、各自写出文件结果，不接受只做文字描述：
- 候选 A 保守最小改：只删完全重复行、只补明确默认值，其余原样通过。
- 候选 B 逐列规则清洗：按脏型分类写规则（去重键、 trim/编码归一、日期归一、类目口径统一），逐列可追溯。
- 候选 C 校验分层：先硬校验（主键唯一、必填、金额列原值一致），不合格行进隔离区 clean/quarantine/，干净行照常输出。
依画像结果可增删候选，但不少于 3 个，且每个候选的差异必须体现在输出文件上。
评分表固定维度与权重写进脚本，任何人复算得到同一结论：
- 金额列逐字符一致（硬门槛，不通过直接淘汰，不参与加权）
- 可用行保留率 0.30 / 脏行处置正确率 0.30 / 下游 schema 变更量 0.15 / 规则可解释性 0.15 / 单轮运行耗时 0.10
择优理由写成数字对比，禁止「效果更好」这类无法复算的说法。
</candidate_paths>

<phases>
阶段 1 画像 → 检查点：clean/profile.json 存在，且含每个 CSV 的文件名、行数、逐列空值率与判定类型。
阶段 2 候选实现 → 检查点：clean/candidates/a|b|c/ 各有独立输出目录且非空。
阶段 3 评分择优 → 检查点：clean/score.md 表内每个数字都能在上阶段输出文件里对上。
阶段 4 默认方案固化 → 检查点：python clean/clean_sales.py --dry-run 退出码 0，重复运行输出逐字节一致。
阶段 5 报告与迁移包 → 检查点：REPORT.md 七个固定章节齐全，prod_load/ 内 SQL 通过脚本自检断言。
阶段检查点不通过就停下修复，不得跳进下一阶段。
</phases>

<done_criteria>
全部为是/否判据，逐条自证，缺一条即未完成：
1. 行数对账等式成立：输入行数 = 保留行 + 修正行 + 隔离行（REPORT.md 给出三个数字与等式）。
2. 金额列逐字符 diff 为空，由脚本内置校验输出 PASS（不是人工目测）。
3. git status 显示的改动文件 100% 位于 clean/ 之下，其余目录零改动、零删除。
4. 不少于 3 个候选的输出目录存在且非空，评分表数字来源于这些真实文件。
5. 生产库写入次数为 0：脚本与产物中不含任何连接串、口令或库地址；本次运行未发起网络或数据库调用。
6. 落选候选可用 python clean/clean_sales.py --candidate a|b|c 原样复现。
7. 原始 CSV 文件 mtime 与 sha 未被改动。
</done_criteria>

<constraints>
- 确定性：固定随机种子与排序键，重复运行结果逐字节一致。
- 编码：先探测 utf-8 / utf-8-sig / gbk，中文列名不得出现乱码；探测结果写进 profile.json。
- 每个结论都要带证据：列名 + 行号区间或计数，敏感字段只报掩码后的形态。
- 输出目录结构不得变化：clean/out/ 为清洗结果，clean/quarantine/ 为隔离行，clean/prod_load/ 为迁移包。
- 只用结论、假设、证据、简明理由与验证结果交流；不要输出或索取隐藏推理过程与逐字思维链。
</constraints>

<anti_patterns>
禁止：在 prompt 或脚本里用「我考虑了三种路径然后选了最好的」这类无真实运行的多路推理表演（思维树/自评择优）→ 必须替代为候选 A/B/C 真实实现、真实出文件、按固定评分表出数字。
禁止：直连生产库执行 INSERT/UPDATE/DELETE，或把生产库地址/凭据写进代码与配置 → 必须替代为默认 --dry-run 加可审查迁移包（见 prod_write_gate）。
禁止：把金额列转 float、去千分位、四舍五入、换算单位、顺手补零 → 必须替代为原列保留原字符串加派生列 金额列_numeric。
禁止：为了让脚本跑通去改 clean/ 之外的文件（含格式化既有代码、加依赖、改 lockfile、改 CI）→ 必须替代为把前置条件写进 REPORT.md。
禁止：猜测文件名、目录、列名、主键 → 必须替代为阶段 1 实测并在报告中引用证据。
禁止：用「数据已变干净」「质量明显提升」「基本没问题」等模糊验收语 → 必须替代为计数、等式与逐字符校验结果。
禁止：把「脏行」静默丢弃而不计数 → 必须替代为隔离区加计数加原因。
禁止：索取或粘贴模型的隐藏思维链 → 必须替代为要求结论、假设、证据与验证结果。
</anti_patterns>

<prod_write_gate>
用户原话「直接往生产库写，立竿见影」保留意图、改道路径，理由：本任务不提供凭据，且生产写不可逆、与「金额字段不可动」这条死线直接冲突（写坏一次无法回滚）。
意图兑现方式：清洗结果当天落到 clean/out/ 供下游立刻使用（立竿见影），生产写入只等凭据与人工确认到位后由人已审的 SQL 执行。
生产写入须同时满足三重门，任一不满足则不生成可执行入口：
1. done_criteria 七条全部 PASS；
2. clean/prod_load/ 同时存在正向 UPSERT 与回滚 SQL，且被事务包裹；
3. 运行时显式给出 --confirm-prod 且当次由操作方提供凭据。
迁移包硬性要求：按订单主键幂等（重复执行结果不变）；BEGIN/COMMIT 包裹；给出预计影响行数；金额列不得出现在任何 SET 或 INSERT 列清单中，并由脚本断言证明。
</prod_write_gate>

<output_format>
交付文件树（相对仓库根，说明写在箭头后）：
clean/
├── clean_sales.py        ← 主脚本，--dry-run 默认，--candidate a|b|c 切换
├── profile.json          ← 阶段 1 画像产物
├── score.md              ← 候选评分表（markdown 表格）
├── REPORT.md             ← 验证报告，七章节固定
├── selection.json        ← 机器可读择优结果
├── candidates/           ← a/ b/ c/ 各自 out/ 输出
├── out/                  ← 默认方案最终清洗结果
├── quarantine/           ← 硬校验不合格行 + 原因列
└── prod_load/            ← 01_upsert.sql / 99_rollback.sql / 影响行数预估.md
REPORT.md 固定章节：数据画像 / 候选方案 / 评分表 / 默认方案规则清单 / 前后对账 / 风险与未覆盖项 / 生产迁移包说明。
所有指标一律带口径与分母；表格用 markdown；不使用「较多、明显、基本」等模糊量词。
</output_format>

<artifact_rules>
应产出：clean/ 下的脚本、profile.json、score.md、selection.json、REPORT.md、candidates/*/out/*.csv、prod_load/*.sql。
不得产出：原始 CSV 的副本或改写、任何 .db/.sqlite 文件、__pycache__/、临时下载、凭据或连接配置文件、生产数据快照。
</artifact_rules>

<stop_conditions>
遇到以下情况立即停手并上报（写明卡点、实测证据、下一步），不要自行越界解决：
- 完成清洗必须修改 clean/ 之外的文件；
- 金额列的原始值与业务规则冲突，不改就无法通过硬校验；
- CSV 中出现疑似个人敏感信息需要外发或打印明文才能继续；
- 出现任何要求连接真实数据库才能继续的下游步骤。
</stop_conditions>

<verification>
做完后逐条自检并在报告里逐条标 PASS/FAIL（本段与开头 critical_constraints 同权重，两处都算硬约束）：
- [ ] 金额列逐字符 diff 为 PASS（死线 1）
- [ ] 全部改动位于 clean/，其余目录零改动（死线 2）
- [ ] 不少于 3 个候选真实运行过，评分可复算
- [ ] 默认路径是 --dry-run，本次生产库写入次数为 0
- [ ] 产物中无凭据、无连接串，未发起网络或数据库调用
- [ ] 重复运行输出逐字节一致
- [ ] 每个结论都有列名加行号或计数证据，无模糊验收语
</verification>

<agentic_notice>
This prompt is for an agentic tool with real system access. Review the scope locks, forbidden actions, and stop conditions before pasting. Confirm file paths, directories, and permissions match the actual project.
</agentic_notice>
