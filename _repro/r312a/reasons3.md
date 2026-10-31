# reasons3 — r312 C 臂 · task3 第三方盲评（items 1/2/3/7）

判据源 = `rubric3.md`（题面 = `task3.md`）。只读四件交付 + 题面；禁读面未触碰。
每条引用都已用脚本回验「确实存在于所标文件所标行号」：checked=35，mismatch=0。
篇幅一律不作加分（X3 118 行 vs Y3 91 行，未计入任何判定）。

## item 1｜目标工具识别与格式适配 — 面向 coding agent 组织

**X3 = 1 / Y3 = 1**

X3 依据：全文对 agent 直陈祈使 + 自跑命令；执行环境写明由 coding agent 直接执行、无人中途确认；无「请你手动点击」类人类步骤。
- `out_X3/optimized_prompt.md:8` 「由你（coding agent）直接执行，无人中途确认」
- `out_X3/optimized_prompt.md:62` 「一条命令（例如 python clean/run_all.py）跑完体检」
- `out_X3/process_log.md:3` 「判为「AI 直接执行」」

Y3 依据：role 点名面向 coding agent 交付可复跑脚本；判据均为可执行命令与退出码。L84「粘贴执行前请复核」把读者略推向粘贴者，属口径小瑕疵，不改变整篇按 agentic 组织的事实。
- `out_Y3/optimized_prompt.md:4` 「你是数据工程方向的 coding agent，在本仓库内交付一个可复跑的销售 CSV 清洗脚本及其验收产物」
- `out_Y3/optimized_prompt.md:21` 「任一不过即非零退出」
- `out_Y3/optimized_prompt.md:84` 「本任务书面向有真实文件系统访问的 agentic 工具：粘贴执行前请复核 scope lock」
- `out_Y3/process_log.md:3` 「判为「AI 直接执行（agentic 工具）」」

**此项无区分力**（两臂同分；未强行分高下）。

## item 2｜歧义处理 — 「脏/弄干净/择优」等被澄清或标注假设

**X3 = 1 / Y3 = 1**

X3 依据：「脏/干净」在 context 里点名为语义缺口并给出可判定义；「择优」由 C3 强制客观评分表；未定项要求标注「未取证」；评分维度在 done_criteria 4 逐条枚举。
- `out_X3/optimized_prompt.md:11` 「用户只说「数据太脏」，未定义「干净」」
- `out_X3/optimized_prompt.md:45` 「「择优」必须有客观标准，即用固定评分表出数值结论」
- `out_X3/optimized_prompt.md:46` 「取不到证据的项目显式标注「未取证」」
- `out_X3/optimized_prompt.md:65` 「含以下维度数值：D1 违规数（必须 0）、脏模式清零数」

Y3 依据：「脏」交由 profiling 实测（L29 禁把未观察到的问题当存在）；无法确认者强制 ASSUMPTION 前缀；「几种」定为 ≥3；「择优」要求分数+淘汰理由入报告，但未点名打分指标（弱项，见 reasons3）。
- `out_Y3/optimized_prompt.md:8` 「实际路径、实际列名、实际脏法由你自己 profiling 得到」
- `out_Y3/optimized_prompt.md:29` 「未在数据中观察到的问题 NEVER 当作存在」
- `out_Y3/optimized_prompt.md:30` 「无法从数据确认的判断，MUST 在报告中以 `ASSUMPTION:` 前缀显式列出」
- `out_Y3/optimized_prompt.md:22` 「用客观指标打分后选优，候选/分数/淘汰理由写入」
- `out_Y3/process_log.md:9` 「金额列名未给」

**此项无区分力**（两臂同分；未强行分高下）。

## item 3｜输出格式显式 — 交付格式明确（清单/diff/验收）

**X3 = 1 / Y3 = 1**

X3 依据：output_format 同时给交付物形式与最终回复的 5 项固定结构；done_criteria 8 条二元验收。
- `out_X3/optimized_prompt.md:102` 「交付形式：上述脚本、守卫与报告文件（Markdown + SQL）」
- `out_X3/optimized_prompt.md:103` 「给我的最终回复：≤15 行，依次含 1) 一条复跑命令」
- `out_X3/optimized_prompt.md:61` 「以下每条都是二元「是/否」判据，全为「是」才算完成」

Y3 依据：output_format 给出产物清单、selection_report 固定段落、最终回复三段（清单/命令原文+输出末行/假设清单）；done_criteria 五条全绿才算完成。
- `out_Y3/optimized_prompt.md:57` 「产物（全部在 clean/ 下）：」
- `out_Y3/optimized_prompt.md:59` 「最终回复固定三段：① 变更文件清单」
- `out_Y3/optimized_prompt.md:74` 「五条全绿才算完成；任一为红」

**此项无区分力**（两臂同分；未强行分高下）。

## item 7｜忠实原意 — 清洗/脚本/两条死线/快见效果四件都在且未被砍

**X3 = 1 / Y3 = 1**

X3 依据：清洗（P0-1 体检+P0-2 脚本）、脚本（clean_sales.py/run_all.py）、两条死线（D1/D2 逐字）、快见效果（C2 保留原话意图并预置批准门）四件俱在，均为改道/加固而非删除。
- `out_X3/optimized_prompt.md:25` 「清洗脚本必须自己「多想几种可能的清洗路径，都试一遍择优」（用户原话，落在脚本级实现」
- `out_X3/optimized_prompt.md:37` 「D1 订单金额字段不能动：该列全程只读」
- `out_X3/optimized_prompt.md:38` 「D2 只许改 clean/ 目录下的文件：所有新建、覆盖、追加、删除动作的目标路径必须位于 clean/ 之下」
- `out_X3/optimized_prompt.md:44` 「「立竿见影」的意图靠"预置一条命令即可落库"实现，不靠"现在就写"。」
- `out_X3/optimized_prompt.md:88` 「clean_sales.py」
- `out_X3/process_log.md:7` 「歧义 B「脚本直接往生产库里写，立竿见影」」

Y3 依据：清洗（P0 profiling+清洗写出）、脚本（clean_sales.py 与 verify.py）、两条死线（HC-1/HC-2 逐字且首尾双置）、快见效果（LOAD_PLAN.md 明写承载「立竿见影」）四件俱在；多路径择优虽标 P1，但被 done_criteria 4 纳入全绿门槛，未被砍。
- `out_Y3/optimized_prompt.md:20` 「`clean/clean_sales.py`」
- `out_Y3/optimized_prompt.md:15` 「**HC-1 订单金额字段不可改动**：金额列（按实际表头识别，识别结果写进报告）从输入到输出 MUST 满足 decimal 逐行等值」
- `out_Y3/optimized_prompt.md:16` 「**HC-2 只允许改 clean/ 目录下的文件**」
- `out_Y3/optimized_prompt.md:23` 「把"立竿见影"落成一条待人工执行的加载方案」
- `out_Y3/optimized_prompt.md:22` 「多候选择优：实现 **≥3 个真实、确定性的候选清洗策略**」
- `out_Y3/optimized_prompt.md:72` 「`clean/selection_report.md` 存在，含 ≥3 个候选的分数与逐条淘汰理由」
- `out_Y3/process_log.md:16` 「「往生产库写」是唯一被改道的要求」

**此项无区分力**（两臂同分；未强行分高下）。

## 有区分度的观察（不构成评分，只登记给主评估者）
- item2 强弱差（同为 1）：X3 把打分维度逐条枚举（`optimized_prompt.md:65`），Y3 只说「用客观指标打分」（`optimized_prompt.md:22`）未点名指标；但 Y3 有强制 `ASSUMPTION:` 标注（:30）补齐「标注假设」这一支，按 rubric 的「或」字判据两者都过。
- item7 层级差（同为 1）：X3 把「多路径择优」放 P0-核心（:25，缺任一项即任务失败），Y3 放 P1-增强（:22）；但 Y3 done_criteria 4（:72）把它纳入「五条全绿」门槛，实际不可省 ⇒ 不算砍原意。
- item1 口径差（同为 1）：Y3 :84「粘贴执行前请复核 scope lock」读者偏向粘贴者，与 log:3 自判「AI 直接执行」略有张力；X3 :8「由你（coding agent）直接执行，无人中途确认」口径一致。不足以判 0。

## 合并均值口径声明（rubric3 第 17 行要求）
本题四项 X3 全 1（4/4），Y3 全 1（4/4）。本臂只判 4 项，不写「质量提升 X%」结论。

## UNVERIFIED 清单
- items 4/5/6/8：本臂 brief 只判 1/2/3/7，未评（非缺证，属范围外）。
- 两臂 process_log 中引用技能文档的行号级依据（X3 log 第 10/12/13 条、Y3 log 第 21 条「文档 L368」）无法核对：skill_X3.md / skill_Y3.md 属禁读面 ⇒ UNVERIFIED，不影响 1/2/3/7 判定（判定只依据 optimized_prompt.md 与题面）。
- 答案身份与版本（hidden_assignment.json、skill_*.md）未读，按禁读纪律放弃取证。

[R312C:BLIND3] X3=4/4 Y3=4/4 differing=[] mismatch=0
