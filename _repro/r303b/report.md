# R303b · R261-7 剩余两件的换装证据包（增量 / 本地独有 / 验证标准 / 回滚预案）

> 轮次：r303b ｜ 生成时刻：2026-10-30T14:52:30.167Z
> 范围：台账 R261-7 具名的剩余两件 —— A 臂 slug = A-prompt-better；F 臂 slug = frontend-skill。
> 结论标注：✅已实测 / ⚠️部分实测 / ❌未实测，逐条标注。本件不执行换装、不改受管根任何既有文件、不跑 run_gates.py。

## 0. 本件不做裁定（显式声明）

本件只产出「换装前必须看清的事实」：① 上游相对本地有哪些可指行/块的**具体增量**；② 本地有而上游**没有**的（证明换装不是单向的赢面）；③ 若要换，**验证标准**应是什么（可量、可复跑）；④ **回滚预案**（改前状态记在哪）。

**本件不判定值不值得换** —— 该裁定属 Lead。本件也不给出「换/不换」的建议，不代改任何文件，不代跑仓门禁。
凡拿不到证据的面一律记为 UNVERIFIED：**不编造增量，也不把「搜不到」写成「本地更好」**。

## 1. 上游声明核验（先核台账，再谈增量）

台账 R261-7 原句（✅已实测，逐字取回）：A 具名 `A-prompt-better←prompt-master`，括注写「L22-23/442/469/482 四块增量可指行」；F 具名 `frontend-skill←taste-skill`，括注写「把本地散文规则变 1440/768/390 实测门禁」。

**先确认「那是对哪份件的行号」**（✅已实测）：433/469/482 等行号**不是本地件的行号**，而是候选件 `nidhinjs/prompt-master` 的 `SKILL.md`（499 行）行号 —— 已用 GitHub raw 取回后逐行比对命中（L22 起黑名单、L442 first 30%、L469 Agentic Output Warning、L482 六问自检）；候选件明确后，本地 A 臂只有 675 行且上述锚点词在本地命中为 0，二者不可能同指。

**候选仓存在性核验（✅已实测，rc=0）**：

```bash
gh api repos/nidhinjs/prompt-master --jq "{full_name,license:.license.spdx_id,default_branch,pushed_at,archived}"
  -> {"archived":false,"default_branch":"main","full_name":"nidhinjs/prompt-master","license":"MIT","pushed_at":"2026-10-22T13:26:18Z"}
gh api repos/nidhinjs/prompt-master/contents/SKILL.md --jq "{name,path,sha,size}"
  -> {"name":"SKILL.md","path":"SKILL.md","sha":"742deafaf4222f9f0e9d9410e72483dad64fe716","size":33508}
gh api repos/Leonxlnx/taste-skill --jq "{full_name,license:.license.spdx_id,default_branch,pushed_at,archived}"
  -> {"archived":false,"default_branch":"main","full_name":"Leonxlnx/taste-skill","license":"MIT","pushed_at":"2026-10-30T09:24:57Z"}
gh api repos/Leonxlnx/taste-skill/contents/skills/taste-skill/SKILL.md --jq "{name,path,sha,size}"
  -> {"name":"SKILL.md","path":"skills/taste-skill/SKILL.md","sha":"d8444f13b76be100b3b088dfdae738e85288d6b6","size":39537}
```

⇒ 两个候选仓均**存在**、均有**可指认的 SKILL.md**（A 臂 rel 为根 `SKILL.md`；F 臂 rel 为 `skills/taste-skill/SKILL.md`），故 candidates 的 state 均为 VERIFIED，**不触发 CANDIDATE_UNVERIFIED**。

**两个上游声明文件均缺失（⚠️部分实测，缺面如实记）**：两件目录下都不存在声明文件（实测 `ls` 报 No such file），而同族技能确以「仓库 + path:」两行式声明。⇒ 本包 skills[].declared_upstream 记 `present=false`，候选取值改由台账 R261-7 与 r261 判定件给出，并把「上游声明的权威来源」列入 unknown（U1）。

## 2. A 臂：A-prompt-better ← nidhinjs 的 prompt-master

本地件：slug A-prompt-better ｜ 版本 1.3.0 ｜ 675 行 ｜ SKILL.md sha256 `01884cd11aed608ba09d3911e96f0d4143a034ce75980719a0c04cf54f3d0aa3` ｜ git blob `ce4652490b755f20c39f1a9756006e0243785f6b`。
候选件：仓库 nidhinjs/prompt-master ｜ SKILL.md 499 行 ｜ 版本 1.8.2 ｜ MIT ｜ git blob `742deafaf4222f9f0e9d9410e72483dad64fe716`（GitHub API 值与本机重算一致，✅已实测）。

### 2.1 增量（4 块，每块均可指行；✅已实测）

| # | upstream_ref（文件 + 行/块） | 增量是什么 | 为什么本地缺 | 状态 |
|---|---|---|---|---|
| A1 | prompt-master SKILL.md L22-27 | 单 prompt 高虚构风险技法黑名单（Mixture of Experts / Tree of Thought / Graph of Thought / Universal Self-Consistency / prompt-chaining 只在用户显式点名且目标工具支持时可用），同段含 L27「Never request hidden chain-of-thought, private reasoning, or a verbatim reasoning trace」 | 本地无该黑名单，也无「不得索取隐藏思维链」硬规则（缺席探针命中 0） | ✅已实测 |
| A2 | 同件 L442 | Memory Block 位置约束：「Place it in the first 30% of the prompt so it survives attention decay in the target model」 | 本地只有近因效应这一半（同一约束放在闭合标签之前），无位置比例量化、无 attention decay 机理 | ✅已实测 |
| A3 | 同件 L469-470 | Agentic Output Warning：对会执行命令/改文件的 agentic 工具附 scope lock 复核告示（scope locks / forbidden actions / stop conditions / 路径权限） | 本地无 agentic 输出警示段，不区分「粘贴给可执行工具」这一风险面 | ✅已实测 |
| A4 | 同件 L482 | 交付前六问自检（RECENCY ZONE）之一：最关键约束是否落在生成 prompt 的前 30%，另含 token efficiency audit | 本地无交付前自检清单（六问形态缺席），只有写作期规则 | ✅已实测 |

### 2.2 本地独有（上游没有；腿 A 证据，✅已实测）

| # | local_ref（本地件行） | 能力 | 上游反证 |
|---|---|---|---|
| A-L1 | A-prompt-better SKILL.md L34-39 | 七步闭环的第 ② 环节衔接（R195）：声明本件是七步闭环 ② 环节、引用记忆侧共享规范、并写明门禁项 G6 已废止 | 候选对 workflow_seven_step / 七步 命中 0 |
| A-L2 | 同件 L146-165 与 L205 | Level 1/2/3 达标分流 + 闭合标签级近因规则（最重要约束放在闭合标签之前） | 候选对 Level 1 / Level 2 / 闭合标签 命中均为 0 |

### 2.3 验证标准建议（可量 / 可复跑）

- **增量可达性（换装后必须仍可指）**：换装后的本地件文本对 A1~A4 的四个锚点词（Mixture of Experts / first 30% / Agentic Output Warning / most critical constraints）逐一 grep，要求每个命中 ≥1。可复跑判据：四词命中数之和 = 4 且逐词 ≥1。
- **本地独有未被覆盖（腿 A 的换装期守护）**：换装后对 A-L1/A-L2 的锚点（workflow_seven_step、Level 1、闭合标签近因句）grep，要求仍各 ≥1 —— 防止「纯替换即降级」把本地独有面洗掉。
- **落地态重放**：按仓内工序模板给该单建一份 spec（replays / patches / version），跑谷仓内的落地态重放检查器，要求 rc=0 且末行 gate=PASS；判据必须换装后仍能从仓内复算。
- **回归面**：对同一输入提示词，优化输出仍走 Level 1/2/3 分流（Level 1 直跳、Level 2/3 进流程），且成文顺序仍满足闭合标签近因规则。

### 2.4 回滚预案建议

- **改前状态记在哪（✅已实测，三值落账面）**：① 受管根 git 短头 `a9a98ba6`（取值命令见 §4）；② 两件 SKILL.md 的 sha256 与 git blob sha（本包 skills[] 内 `local_sha256` / `local_blob_sha` 即改前账）；③ 受管根 `git rev-parse HEAD` 全值时值。
- **回滚手序**：改前先 `git -C <受管根> rev-parse HEAD` 存全值并留 `_trash/rule_backup` 一份 .bak；回滚 = `git -C <受管根> checkout <改前全值 sha> -- <该件相对路径>`，回滚前双前提 = .bak 在盘 + `git cat-file -e <sha>^{commit}` 通过。
- **落地走唯一通道**：受管根改动唯一途径为仓内 rule_editor（禁整体重写），并复核提交范围只含本单文件。
- **回滚可验证**：回滚后对 §2.3 的本地独有锚点重跑 grep，要求命中数回到改前值（≥改前），且件 sha256 回到 §2 首段记录值。

## 3. F 臂：frontend-skill ← Leonxlnx 的 taste-skill

本地件：slug frontend-skill ｜ 版本 1.0.0 ｜ 186 行 ｜ 附带 Apache-2.0 许可件与一个 agents 子面 ｜ SKILL.md sha256 `4a87c81063d4cb66954b379012091d3dad0cc53c6f88b428eac2f78d0b3085f8` ｜ git blob `c94f6d03d7a799a213e755d65388f40bd8bf2d09`。
候选件：仓库 Leonxlnx/taste-skill ｜ rel 文件 542 行 ｜ MIT ｜ 版本 UNVERIFIED（候选 frontmatter 无 version 字段）｜ git blob `d8444f13b76be100b3b088dfdae738e85288d6b6`（API 值与本机重算一致，✅已实测）。

### 3.1 增量（4 块，每块均可指行；✅已实测）

| # | upstream_ref（文件 + 行/块） | 增量是什么 | 为什么本地缺 | 状态 |
|---|---|---|---|---|
| F1 | taste-skill rel SKILL.md L307-322 | 第 7 步 Gate 的执行器：lint.mjs 扫禁用模式与套话；inspect.mjs 在真实浏览器按 1440 / 768 / 390 三档实测 headline line counts、type sizes、fonts actually loaded、contrast、overflow 与版面帧；scenes.mjs 覆盖滚动场景 | 本地纯散文规则、目录内无脚本，没有任何可执行审美门禁 | ✅已实测 |
| F2 | 同件 L367 | 交付判据：inspect.mjs 在 1440/768/390 三档对最终版本显示 0 FAIL 才允许报告，并列「每次改动后打开它列出的全部截图」等前置 | 本地交付标准停留在文字要求，无可复算判据 | ✅已实测 |
| F3 | 同件 L25（配合 library 面 9 文件） | draw.mjs 从 20 个已研究研究方向发牌（方向/构图/字体/配色/摄影/分区蓝图），数据成库 | 本地只有 Working Model 三件套叙述性方法，无成库方向数据与执行器 | ✅已实测 |
| F4 | 同件 L52-54 | app 屏专线：独立数据文件、独立 draw 调用（--app）、独立 house rules 与 inspect 验收 | 本地 Apps 一节是散文约束，无独立数据文件与独立验收命令 | ✅已实测 |

附：候选仓该 rel 面下共 31 个资产文件（scripts 11 / library 9 / references 11，✅已实测），是上述可执行门禁的载体。

### 3.2 本地独有（上游没有；腿 A 证据，✅已实测）

| # | local_ref（本地件行） | 能力 | 上游反证 |
|---|---|---|---|
| F-L1 | frontend-skill SKILL.md L48 | Canonical full-bleed rule：品牌落地页 hero 必须 edge-to-edge，不得继承页面 gutters / framed container / shared max-width | 候选对 full-bleed 命中 0 |
| F-L2 | 同件 L57-60 | Viewport budget：100vh / 100svh hero 须扣掉常驻 UI chrome（calc(100svh - header-height)）或让 header 覆盖而非顺排 | 候选对 Viewport budget 与 100svh 命中均为 0 |
| F-L3 | 同件 agents 子面的平台配置件（326 B） | 本地带平台 agent 配置文件 | 候选仓该 rel 面下只有 scripts / library / references 三个子面，无 agents 子面 |

### 3.3 验证标准建议（可量 / 可复跑）

- **门禁可跑（换装的核心新面）**：换装后该件目录须出现 lint.mjs 与 inspect.mjs；对一份样本页面跑两脚本，要求 lint 可执行且 inspect 在 1440/768/390 三档输出结论行含 `0 FAIL`。可复跑判据：三档全部 `0 FAIL`（任一档 非 0 ⇒ FAIL）。
- **本地独有未被覆盖**：换装后对 F-L1/F-L2 锚点（full-bleed、Viewport budget）grep，要求仍各 ≥1；agents 子面文件仍在盘（换装不得删本地独有资产）。
- **许可混合不许丢单边**：候选 MIT 与本地 Apache-2.0 混用时须两份 notice 并存；判据 = 两份许可文本均在盘且 sha 与改前一致（或用候选侧 LICENSE 的 blob sha 核验）。
- **落地态重放**：同 §2.3，为本单建 spec 后跑仓内落地态重放检查器，rc=0 且 gate=PASS。

### 3.4 回滚预案建议

- **改前状态记在哪**：同 §2.4（受管根 git 头 `a9a98ba6` + 本包 skills[] 内的本地 sha256/blob + 改前全值 HEAD + `_trash/rule_backup` 的 .bak）。
- **回滚手序**：`git -C <受管根> checkout <改前全值 sha> -- <该件相对路径>`（该件在受管根已跟踪，✅已实测）；若换装新增了脚本/数据文件，回滚时须一并移除新增件（新增件清单以本单 spec 的 new_files 为准，禁删他人文件）。
- **回滚可验证**：回滚后该件目录不残留新增脚本；对 F-L1/F-L2 锚点重跑 grep 回到改前命中数；SKILL.md sha256 回到 §3 首段记录值。

## 4. 数据来源与每条取值的命令

受管根短头与跟踪状态（✅已实测）：
```bash
git -C D:/global_skills rev-parse --short HEAD        -> a9a98ba6
git -C D:/global_skills rev-parse --is-inside-work-tree -> true
git -C D:/global_skills ls-files A-prompt-better/SKILL.md frontend-skill/SKILL.md  -> 两件均跟踪
```

本地两件 sha / blob / 行数（✅已实测）：
```bash
sha256sum D:/global_skills/A-prompt-better/SKILL.md D:/global_skills/frontend-skill/SKILL.md
git -C D:/global_skills hash-object A-prompt-better/SKILL.md frontend-skill/SKILL.md
wc -l D:/global_skills/A-prompt-better/SKILL.md D:/global_skills/frontend-skill/SKILL.md  -> 675 / 186
ls D:/global_skills/A-prompt-better/.upstream D:/global_skills/frontend-skill/.upstream  -> 均 No such file
```

候选件取回与逐条增量取值（✅已实测，rc=0）：
```bash
gh api repos/nidhinjs/prompt-master/contents/SKILL.md -H "Accept: application/vnd.github.raw"
grep -n -e "Mixture of Experts" -e "first 30%" -e "Agentic Output Warning" prompt-master.SKILL.md
  -> 22 / 442 / 469；（482 行命中 most critical constraints）
gh api repos/Leonxlnx/taste-skill/contents/skills/taste-skill/SKILL.md -H "Accept: application/vnd.github.raw"
grep -n -e "lint.mjs" -e "inspect.mjs" -e "1440" -e "0 FAIL" -e "app-screens.md" taste-skill.SKILL.md
  -> 307/310/311/319/320/367/52/54
gh api "repos/Leonxlnx/taste-skill/git/trees/HEAD?recursive=1" --jq ".tree[]|select(.path|test("^skills/taste-skill/(scripts|library|references)/"))|.path"
  -> 31 行（scripts 11 / library 9 / references 11）
```

本地独有缺席探针（✅已实测，全部命中 0）：
```bash
grep -Fic "workflow_seven_step" prompt-master.SKILL.md   -> 0
grep -Fic "Level 1" prompt-master.SKILL.md                -> 0
grep -Fic "full-bleed" taste-skill.SKILL.md               -> 0
grep -Fic "Viewport budget" taste-skill.SKILL.md          -> 0
grep -Fic "100svh" taste-skill.SKILL.md                   -> 0
```

本包校验器（含两腿负控，✅已实测 rc=0）：
```bash
C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe -B check_r303b.py
```

**本机本次全部取值均为一手现取**；唯一未取到的面是「上游声明的权威文件」（两件的声明文件缺失），已记 U1；候选版本号（F 臂）缺失已记 U2。

## 5. 负向对照两腿（逐字输出）

**腿 A（防单向美化）**：local_only 必须 ≥1，指到本地件行。校验器输出逐字：

```text
[LEGA:PASS] local_only=5
  local_only A-prompt-better | D:/global_skills/A-prompt-better/SKILL.md L34-39
  local_only A-prompt-better | D:/global_skills/A-prompt-better/SKILL.md L146-165 与 L205
  local_only frontend-skill | D:/global_skills/frontend-skill/SKILL.md L48
  local_only frontend-skill | D:/global_skills/frontend-skill/SKILL.md L57-60
  local_only frontend-skill | D:/global_skills/frontend-skill/agents/openai.yaml（326 B）
```

**腿 B（防编造增量）**：造一条故意指向不存在行的条目喂给同一校验函数，必须被标 UNVERIFIED。校验器输出逐字：

```text
[LEGB:PASS] ref-past-EOF -> UNVERIFIED (line 99999 beyond EOF 499)
[LEGB:PASS] valid-line-bad-anchor -> UNVERIFIED (anchor absent from cited window)
```

判据末行（期望值 = 实得值）：
```text
[R303:SWAP] skills=2 candidates=2 increments=8 local_only=5 unknown=5
```

## 6. 结论三态标注汇总

- ✅已实测：候选仓存在与 SKILL.md 可指认；两候选 blob sha（API 值与本机重算一致）；8 条增量的行号窗口与锚点；5 条本地独有项及其缺席探针命中 0；两腿负控；受管根 git 状态与本地两件 sha/blob。
- ⚠️部分实测：两件的上游声明文件缺失 —— 「上游声明」这一面只有台账与判定件来源，无权威声明文件；本件按候选存在性独立取证，故不影响增量成立。
- ❌未实测：候选脚本在本机的可运行性（Node / Chrome / CDP 依赖）；本地 agents 子面文件的引用方；上游行号随 HEAD 推进的漂移。三项已逐条记入 unknown（U3/U4/U5）。

