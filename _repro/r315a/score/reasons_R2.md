# reasons_R2 — r313 轮次2 四交付件 · 第三方盲评（人判四项 1/2/3/7）

判据：`_repro/r309a/rubric2.md`（task2）与 `_repro/r312a/rubric3.md`（task3，同构同判法）；题面 `_temp/r309a/task2.md` / `_temp/r312a/task3.md`。机械项 4/5/6/8 不归本臂。

纪律：只读白名单（两份 rubric、两份题面、四份交付）；未读 skill_*.md / hidden_assignment.json / round2_mech.json / r307a / r309a、r312a 其它内容 / _repro 其余 / D 盘两源。四份 process_log 首行自报了技能版本号，本臂**未据此推断身份或版本、未按臂名猜叙事**，只看文本。未改任何既有文件，只新建本目录。

## 结果总览

| 臂 | 1 目标工具识别与格式适配 | 2 歧义处理 | 3 输出格式显式 | 7 忠实原意 | 合计 |
|---|---|---|---|---|---|
| X2b | 1 | 1 | 1 | 1 | 4/4 |
| Y2b | 1 | 1 | 1 | 1 | 4/4 |
| X3b | 1 | 1 | 1 | 1 | 4/4 |
| Y3b | 1 | 1 | 1 | 1 | 4/4 |

四臂 × 四项全部同分 ⇒ **本组人判项零区分力**。rubric2 末行已预置处置：两臂仍同分 ⇒ 记录「题面仍无区分力」，不硬解读。以下逐项同样标注。

## item1 目标工具识别与格式适配（判点：prompt 面向 coding agent 且按其形态组织）
- X2b = 1：out_X2b/optimized_prompt.md:3 「本文件整份交给有命令行权限的 coding agent 直接执行」；out_X2b/optimized_prompt.md:6 「你是这个纯静态 HTML 超市仓库的前端资产改造与部署执行 agent，拥有命令行权限」；按其形态组织 = out_X2b/optimized_prompt.md:70 「手段：git ls-files、列目录、grep 引用」。
- Y2b = 1：out_Y2b/optimized_prompt.md:3 「目标执行体：具备命令行权限的 coding agent」；out_Y2b/optimized_prompt.md:8 「你有命令行权限，可以在本仓库内读文件、跑脚本、执行部署命令」；按 agentic 形态附复核提醒 out_Y2b/optimized_prompt.md:123 「Review the scope locks, forbidden actions, and stop conditions before pasting.」。
- X3b = 1：out_X3b/optimized_prompt.md:1 「交给 coding agent 的任务书（优化版，可直接复制使用）」；out_X3b/optimized_prompt.md:4 「你是数据工程方向的 coding agent，在一个本地 Git 仓库内工作」；out_X3b/optimized_prompt.md:8 「可用能力 = 读写工作区文件、运行 shell 与 Python」。
- Y3b = 1：out_Y3b/optimized_prompt.md:4 「你是本仓库唯一执行体的 coding agent，负责编写并真实运行一个 CSV 数据清洗脚本」；out_Y3b/optimized_prompt.md:93 「本 prompt 面向拥有真实文件系统访问的 agentic 工具」；out_Y3b/optimized_prompt.md:22 「按 <phases> 逐阶段推进，检查点不过不得进入下一阶段」。
此项无区分力。

## item2 歧义处理（task2 判点：「想全面/多角度推敲」「最显眼」；task3 判点：「脏/弄干净/择优」被澄清或标注假设）
- X2b = 1：独立段显式裁定 out_X2b/optimized_prompt.md:26 「原始请求有歧义，以下按最优理解裁定并执行（不反问）」；直接命中题面歧义 out_X2b/optimized_prompt.md:31 「「想全面一点、多从几个角度反复推敲」是方法要求而非客套」；对「放结尾最显眼」的排版诉求给出裁定（前置复述 + 末尾保留）= out_X2b/optimized_prompt.md:15 「它们在任务书末尾」。
- Y2b = 1：prompt 本体无「歧义」二字（全文 grep 零命中），走 rubric 的第二形态「标注假设」：out_Y2b/optimized_prompt.md:21 「以下必须由你在阶段 0 实测得到，禁止假设」（未知事实逐类点名）；out_Y2b/optimized_prompt.md:22 「凡实测不到的事实，报告里一律写「未取证：原因」，不得编造路径、文件名、命令、平台或效果数据」；冲突摊开 out_Y2b/optimized_prompt.md:27 「达不成项逐条列出，交用户批准」；对排版诉求给理由 out_Y2b/optimized_prompt.md:112 「收尾再确认一次（放这里是因为长任务后半段最容易把红线忘掉）」。
- X3b = 1：「脏」拆七类 out_X3b/optimized_prompt.md:13 「一批超市销售 CSV 数据脏（编码/BOM、表头命名不统一、日期多态格式、数量存成文本、重复行、缺失值、门店编号格式混杂）」；「择优」裁定形态 out_X3b/optimized_prompt.md:14 「本任务书把它固定为「开发期跑候选对比 → 交付单一确定性脚本」的形态」；金额列名未给用候选标注 out_X3b/optimized_prompt.md:30 「探数时按实际列名锁定，同义候选：金额 / amount / total / 实付 / 应付」；out_X3b/optimized_prompt.md:9 「不得编造标识符：不猜表名、不猜列名、不猜连接串」。
- Y3b = 1：out_Y3b/optimized_prompt.md:18 「未知项：脏在哪些维度（空值、重复、类型、编码、异常值、单位、日期格式）尚未审计，必须先审计再定规则」；「关键假设」做成强制段落 out_Y3b/optimized_prompt.md:73 「把你不得不猜的地方（金额列名、脏因判断、去重键选择）写成显式假设加依据，禁止默默替用户选定」；out_Y3b/optimized_prompt.md:9 「先读真实表头确认列名，并把确认结果写进报告」。
此项无区分力（X2b/Y3b 走「显式澄清+独立段」，Y2b/X3b 走「标注假设+实测黑名单」，两形态都在判点内）。

## item3 输出格式显式（清单 / diff / 验收）
- X2b = 1：清单 out_X2b/optimized_prompt.md:107 「报告必须含以下 8 个段落（顺序可同此）」；交付物 out_X2b/optimized_prompt.md:125 「收尾只交两样」；验收 out_X2b/optimized_prompt.md:89 「做完后逐条自检，任一不过就回到对应阶段重修」，并要贴 git status 与价格基线 diff：out_X2b/optimized_prompt.md:81 「价格基线改前/改后 diff 输出为 0 行」。
- Y2b = 1：段名级刚性约束 out_Y2b/optimized_prompt.md:85 「Markdown，按以下顺序六段，段名逐字照用」；段内字段模板 out_Y2b/optimized_prompt.md:86 「现状审计（表格：路径 / 格式 / 尺寸 / 体积 / 引用数）」；验收形态 out_Y2b/optimized_prompt.md:92 「每段都要有可复核命令及其输出」。
- X3b = 1：交付清单 out_X3b/optimized_prompt.md:55 「交付文件（全部在 clean/ 下）」；决策表 out_X3b/optimized_prompt.md:59 「候选对比决策表」；收尾报告形态 out_X3b/optimized_prompt.md:62 「收尾报告（对话正文，不新建文件）」；验收为六条二元判据（sha256 一致、金额差异行数 = 0、git status 全在 clean/）。
- Y3b = 1：out_Y3b/optimized_prompt.md:71 「段落固定为」（八个二级标题逐字给出）；固定命名 out_Y3b/optimized_prompt.md:45 「产物命名固定」；收尾回复写死 out_Y3b/optimized_prompt.md:72 「收尾回复不超过 10 行」。
此项无区分力。

## item7 忠实原意（task2 四件：换图/变好看/多角度推敲/下游自跑上线；task3 四件：清洗/脚本/两条死线/快见效果；删要求不给替代 = 0）
- X2b = 1：换图 out_X2b/optimized_prompt.md:11 「把太难看的商品图换掉或重制」；变好看 out_X2b/optimized_prompt.md:12 「让页面看起来更好」；多角度推敲 out_X2b/optimized_prompt.md:35 「把「想全面一点」变成可验收动作」；上线 out_X2b/optimized_prompt.md:13 「全部做完后由你自己部署上线，并给出线上证据」。「直接让它上线」未删，仅在查不到通道时 fail-closed 并给替代处置 out_X2b/optimized_prompt.md:75 「停在「产物就绪」，在报告写清缺口、已试过什么、需要什么才能上线」；两条限制一字未削；log 可对应 out_X2b/process_log.md:13 「部署上线不做无条件承诺」。
- Y2b = 1：图整改 out_Y2b/optimized_prompt.md:31 「商品图资产整改（只写 assets 内图片）」；变好看改道但未删 out_Y2b/optimized_prompt.md:35 「页面观感提升提案：只写提案不改文件」；多角度 out_Y2b/optimized_prompt.md:27 「①首屏观感 ②商品图一致性 ③加载性能 ④可访问性 ⑤引用完整性风险」；上线 out_Y2b/optimized_prompt.md:36 「部署上线：按 phases 阶段 4 执行，必须过门」 加线上验证 out_Y2b/optimized_prompt.md:45 「部署命令返回成功，线上首页可访问且图片正常加载」；保留清单对位 out_Y2b/process_log.md:9 「直接让它自己跑完部署上线」。
- X3b = 1：清洗+脚本 out_X3b/optimized_prompt.md:4 「交付物是超市销售 CSV 的清洗脚本与配套产物」；择优保留 out_X3b/optimized_prompt.md:22 「针对脏值清单实现不少于 3 条不同的清洗路径并全部真实跑完所有输入 CSV」；两条死线原文级保留并置于末尾 out_X3b/optimized_prompt.md:116 「订单金额字段不能动：从输入到输出逐字符相同」 / out_X3b/optimized_prompt.md:117 「只许改 clean/ 目录下的文件（含新建）：clean/ 之外零写入」；写库/快见效诉求不删且给替代 out_X3b/optimized_prompt.md:87 「写库能力不删除，改以脚本 + 显式 --execute + 人工授权形式保留，功能等价、时机后移」；即时产物 out_X3b/optimized_prompt.md:24 「P0-4 清洗产出：清洗结果写 clean/out/」。
- Y3b = 1：清洗 out_Y3b/optimized_prompt.md:16 「一份干净数据集 + 可复算的清洗依据」；脚本且真跑 out_Y3b/optimized_prompt.md:4 「负责编写并真实运行一个 CSV 数据清洗脚本」；择优 out_Y3b/optimized_prompt.md:35 「实现 3 到 5 个策略变体」；两条死线原文 out_Y3b/optimized_prompt.md:9 「HC1 订单金额字段不能动」 / out_Y3b/optimized_prompt.md:10 「HC2 只许改 clean/ 目录下的文件」；写库诉求改道不删 out_Y3b/optimized_prompt.md:46 「真实写入需人在带外提供凭据并单独授权」，log 自辩 out_Y3b/process_log.md:9 「改的是手段不是目的」。
此项无区分力。

## 有区分度但不足以判 0 的观察（不进分数，供揭盲后合分参考）
1. **X2b 索取推理原文 vs Y2b 明令禁止**：out_X2b/optimized_prompt.md:44 「阶段 2 的方案先用 `<thinking>` 展开推理（各角度的取舍与冲突）」 与 out_Y2b/optimized_prompt.md:66 「禁止：索取或输出模型的隐藏思维链」 方向相反。这作用在 rubric item5（机械判），四项人判无处落分 ⇒ 不据此判 0。
2. **Y2b 本体无「歧义」裁定段**：裁定主要在 log（out_Y2b/process_log.md:5 「Step 2 歧义四点，按最优理解执行不反问」），本体靠「禁止假设/未取证」承接。若口径要求本体有显式澄清段，Y2b 弱于 X2b；判点含「或标注假设」⇒ 只记强弱。
3. **Y2b 压缩了「换掉丑图」的手段**：out_Y2b/optimized_prompt.md:61 「禁止：用生成图或网图替换真实商品图」 ⇒ 只剩整改；意图仍被承接（判点是「未砍」）。
4. **X2b「变好看」只能靠图片**：out_X2b/optimized_prompt.md:28 「不要越界改代码，把需要的代码改动写进报告的」（转 <gap> 段），比 Y2b 提案更保守；X2b 自己申报了不确定 out_X2b/process_log.md:25 「最不确定的一处」。
5. **上线/写库门槛收紧幅度不同**：X2b 仅无通道才 fail-closed；Y2b out_Y2b/optimized_prompt.md:54 「宁可不上线，不可越界」；X3b out_X3b/optimized_prompt.md:25 「真实写入需显式 --execute」；Y3b out_Y3b/optimized_prompt.md:51 「禁止：为了「立竿见影」跳过审计直接改数据」。四者都是「保留诉求 + 加门 + 给替代」，未触 item7 的 0 分线。
6. **Y3b 格式内部指代落空**：out_Y3b/optimized_prompt.md:70 「1. 上表列出的脚本与产物文件」 —— 该段之前并无表（清单在 op:45 与 <artifact_rules>）。可执行性瑕疵，格式仍显式 ⇒ 不判 0。
7. **择优候选的不重叠度**：X3b 三条异构路线（A 显式规则确定性 / B 规则+嗅探+审计日志 / C 最小改动集）比 Y3b 三档强度（保守/标准/严格）更分离；两者都禁「只在文字里设想」：out_Y3b/optimized_prompt.md:52 「禁止：只在文字里「设想」几种清洗路径然后挑一个」、out_X3b/optimized_prompt.md:100 「禁止：把「都试一遍择优」实现成运行时自动选路」。
8. **排版诉求的四种双写形态**（本臂不管 item4，仅登记）：X2b out_X2b/process_log.md:9 「选了双写，不牺牲用户排版」；Y2b 同名段首尾各一份；X3b 末尾 hard_constraints + task 内「关键约束」；Y3b out_Y3b/optimized_prompt.md:97 「开头 <hard_constraints> 已有同一份，此处是重复而不是新增」。

## 引用保真与负控

- 逐字引用共 **139 条**（score_R2.json 61 条 + reasons_R2.md 78 条，均 ≥35 门槛），逐条用 node 按「取所标 file:line 该行 → indexOf 引文」回验确有其句：**mismatch = 0**（终值，修复一处漏反引号的引文后复跑）。
- 伪造负控各臂一条（共 4 条：把并不存在的句子标到真实存在的行号），全部**未命中**（4/4 拒），且这 4 个字符串在八份文件全文中也**零出现** ⇒ 回验判据有牙，不是恒绿：
  - X2b op:3 「本文件整份交给语音合成引擎执行」
  - Y2b op:8 「你有命令行权限，可以任意修改仓库任何文件并自行注册云账号付款」
  - X3b op:116 「订单金额字段可以按需四舍五入并补默认值」
  - Y3b op:4 「你是本仓库唯一执行体的图像生成模型」

[R313C:BLIND-R2] per-arm 4/4 ×4 differing=[] mismatch=0
