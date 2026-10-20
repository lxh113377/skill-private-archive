# AGENTS.md — 自建skill优化（索引壳，R161 拆卷）

> 自动生成: 2026-10-16 17:20 | 由 r109 I-7「实减」把全量快照降级为索引壳（原 29,293B > 注入预算）。
> **本节只放路由与红线；正文权威源在 `memory/`，本壳不含第二真相源。**
> 备份与回滚：`05-exec/mark_backup/AGENTS.md.r109_before_index_shell`（git 亦可回滚，AGENTS.md 已跟踪）。

## 启动顺序（每次进来先做）

1. **`memory/07-next-steps.md`** = 跨会话唯一入口、P0 唯一真相源（handoff 致命纪律 #1）。超限部分在 `07-next-steps.partN.md`。
2. 需要状态 → `memory/05-feature-status.md`（含 partN）；需要约束/红线全文 → `memory/06-constraints.md`（含 partN）。
3. 需要目录结构 → `memory/02-structure.md`（`sync` 自动刷新，**本壳不再复制树**，防陈旧副本）。
4. 复杂任务先 `A-memory-start` → 按 `memory/AGENTS.md` P-1 绑定表加载技能，禁裸跑。
5. `TODO.md` / `README.md` 是**索引**，不是入口。

## 分卷目录

| 节 | 权威文件 | 说明 |
|---|---|---|
| 01 目标 | `memory/01-goal.md` | 六阶段目标 + 范围裁定口径 |
| 02 结构 | `memory/02-structure.md` | 目录树（sync 自动更新）+ 模块说明 |
| 03 技术栈 | `memory/03-tech-stack.md` | 运行环境 + 外部依赖 |
| 04 文件地图 | `memory/04-file-map.md` | 核心逻辑文件/配置表 |
| 05 功能状态 | `memory/05-feature-status.md`（+ part1…part29） | 已完成/进行中/阻塞 |
| 06 已知约束 | `memory/06-constraints.md`（+ part1…part5） | 已知 Bug / 技术债 / 红线全文 |
| 07 下一步 | `memory/07-next-steps.md`（+ part1…part57） | **P0 真相源** |
| 08 验收 | `memory/08-ac-obs.md` | AC-OBS 列表 |
| 09 工作流态 | `memory/09-workflow-state.md` | 批次与在途 |
| — | `memory/AGENTS.md` | P-1 项目级 Skill 绑定表（命中即加载） |
| — | `05-exec/README.md` | 执行证据索引（补丁 ↔ P0 ↔ commit） |

## 一句话项目定位

对 `D:\global_skills` 自建技能体系做全量体检与优化，产出「审计 + 逐项实施计划 + 执行证据」，六阶段推进；
**对标轮次报告**逐轮落 `06-benchmark/全量对标报告_rNN_*.md`。当前最新轮次取值：`Get-ChildItem 06-benchmark -Filter '全量对标报告_r*' | Sort-Object Name | Select-Object -Last 1 -ExpandProperty Name`（禁硬编码轮号，r110 立规——旧值 r108 系 2026-10-16 当时态）。

## 口径裁定（用户确认，禁换分母）

- 自建口径 = **HIGH 51 + MID 26 = 77 条**（阶段0 v2）；注册表基数按磁盘实测现值复算（`disk_registry_diff.py`，r108 实测 182⇄182 三类全 0）。
- LOW 灰区 30 条 = 排除维护范围（已在册仍参与路由）；EXCLUDE 43 条 = 市场/上游件。
- **已作废基数**「自建 ≈90 / 基数 169」禁止再引用。权威清单 = `00-scope/自建skill清单.md`。

## 红线（不能改 · 摘要；全文见 `06-constraints.md`）

1. 阶段 0-3 **只读取证**：不改 `D:\global_skills` 任何源文件，只在本工作区写报告。
2. 阶段 4 起改 skill 文件**唯一途径 = `rule_editor.py`**；禁 write 整体重写；镜像 `_my-skills`/`.agents\skills` **只读**。
3. **历史留痕不可改写（R241）**：旧报告旧数字只能加「校正注」，禁直接改成当前值。
4. 受管根散落项**只迁 `_trash`，禁止删除**；禁用 `_bak` 作落点。
5. 改 `D:\global_skills` 后必跑三门禁（mirror / noise / evolution）+ `disk_registry_diff` 三类全 0。
6. **焚诀 `eval/` 只读调用不改**；派生件（registry/skill_content/BGE）禁手改。
7. 破坏性动作双硬前提（备份已落 `_trash` + Git 可回滚）满足才可自动批准并留痕，缺任一回落待确认。

## 门禁与取值命令（常驻，禁凭记忆下结论）

```
python 05-exec/run_gates.py --json 06-benchmark/<新件>.json     # 本仓 29 门聚合
python 05-exec/ratchet_gate.py                                  # 注入面/度量六+三项只降不升
python 05-exec/r52_md_claim_face_scan.py --json <件>            # 报告数字须挂取值命令
python 05-exec/r38_debt_aging.py --json <件> --ledger 06-benchmark/debt_runs.jsonl
python D:/global_skills/A-memory-start/references/rule_editor.py gates
python D:/global_skills/A-skill-manager/assets/disk_registry_diff.py
python D:/global_skills/A-project-handoff/scripts/handoff.py volume <本项目>
```
Python 首选 managed venv `%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe`
（系统 Python 会假红：numpy/jinja2/networkx 缺）；跑任何 py 前设 `PYTHONPYCACHEPREFIX`。

## ⚠️ 提案处方必先实测（#31，2026-10-21 立规）

写进 `06-benchmark/transmit_proposals.json` 的 `fix_hint`，**必须是实测过的**，不是推理出来的。
机器判据：每条提案须能被某个 `05-exec/r1*_*.py` 的读数直接支撑——
即「跑一次那个脚本，能报出该处方能救几条」。若某处方没有对应读数面，
要么先建读数面（登记为常驻门），要么在提案里显式写「未验证，仅为候选方向」。

**反面实证（r132 本轮自查）**：r131 我把「direct_route 命中后放行到 tag/bge 层」写进转办提案第 10 条，
理由是「direct 抢答早于 BGE，放行就等于给 BGE 机会」——推理上无懈可击，但**从未实测**。
r132 建 `05-exec/r132_direct_fix_efficacy.py` 实测后发现：6 条闭包里该处方**只让 2 条一步到位**，
另 4 条会从「被 direct 抢答」退化为「被语义邻居压」。**推理正确的处方也可能只对 1/3 有效**。
若照字面执行并按原验收标准（只看 `direct_closed_n` 降到 0）判过，就是一次**假闭环**。

## ⚠️ 判据的「判据面」也须实测（#32，2026-10-21 立规）

判据写完后，**判据所读的面本身**也要实测三种形态，任一形态失效都会让判据**静默假绿**：

| 形态 | 症状 | 正解 | r133 实测 |
|---|---|---|---|
| ① 位置型面 | 用「列表尾部 N 个 = 新增件」判扩容 | 语料按字母排序，扩容件落中间 ⇒ 报出 xlsx / 天眼一下 等**老件**为新增 | 本轮踩中，改用显式前缀族 |
| ② 外部基线件面 | 读一份基线件名文件求差集 | 该件可能被他方删改 ⇒ 差集空 ⇒ **新增数恒 0** | 本轮踩中（文件消失） |
| ③ 旧件里的旧读数 | 拿历史产物里的 route_top1 / actually_hit 当现状 | 语料一变旧读数即陈旧；本轮 gsap 那条 actually_hit=True 但实测已变 | 本轮踩中，改为一律实测 route() |

**机器判据**：凡判据输出「某集合为空 / 某数为 0」，必须能回答「若真值非 0，它会长什么样」——
**先造一个已知非空的面复跑，确认判据能报出来**，再信它的 0。零输入面按 R247 记 UNVERIFIED，不记 0。

**反面实证（r133）**：新建的 r133_new_skill_ingress.py 连续自抓四次才收敛——
① 漏读 tag_closure 上游面（受检 32 题，真值需 311）；② 用了件里旧 route_top1（抢答报 0，真值 7）；
③ 按列表位置切新增件（报 8 件老件为新增）；④ 基线件名文件被他方删除（新增数恒 0）。
**四次都是「面错了」，不是「代码错了」。**

## ⚠️ 结论层的推理也须标注或实测（#33，2026-10-21 立规）

#31 管「处方」，#32 管「判据所读的面」——**两者都管不到结论层的推理**。本条补上。

报告里凡出现因果表述（「因为 / 所以 / 根因是 / 导致 / 因此 / 结论是」），必须二者择一：
- **A. 有实测支撑**：同报告 ±14 行内有**可复算的东西**（取值命令 / 逐条读数表 / 复算命令）；
- **B. 无实测支撑**：显式标注「⚠️未实测，仅推理」，不得写成「根因是」「实测发现」这类实测口吻。

**证据口径（关键）**：只有**可复算**的东西算证据。「实测」「已验证」这类**自我声明不算**——
声明可以撒谎，读数不会。`python 05-exec/r134_causal_evidence.py --report <报告>` 逐条判定并出读数，
是第 46 门。**INFERRED 不是红，是清单**：它的正确处理是补一次实测或加标注。

**反面实证（r133 一手）**：我推理「`gsap` 的 SKILL.md 有 7754 字符 ⇒ 会被压进固定长度 embedding 而稀释语义重心」，
理由听着无懈可击，差点作为「根因」写进 r133 报告。实测：全文 0.4983 vs 仅 frontmatter 0.4979，**差 0.0004**。
**这是第 5 次「我以为对，没量过」**（r126 假红判据 → r128 判据未入库 → r131 处方未验证 → r132 处方只对 1/3 → r133 长度假设）。

**规模实测（r134 全量普查）**：93 份对标报告、958 条因果行中 **182 条（19%）是仅推理**，无实测支撑。
⇒ 该纪律的历史欠账不小，**新写结论必须从严，历史面按 R241 只登记不返工**。

## ⚠️ 纪律须作用到自己身上（#34，2026-10-21 立规）

#31（处方必先实测）、#32（判据面必先实测）、#33（结论层推理须标注或实测）立了之后，
r135 收尾发现一个刺眼事实：**第 11 条提案自己的处方，没被这三条纪律覆盖**。
纪律立了不等于纪律作用到了自己身上。

**机器判据**：新增或修改转办提案后，必须跑
`python 05-exec/r136_proposal_evidence.py --json <件>`（第 48 门），
读 `face.unbacked_n` / `no_acceptance_n` / `no_evidence_n` —— **三个都必须是 0**。
「没有读数面支撑」的正确处置是**显式标注「未验证，仅为候选方向」**（该面把这种标注计为合规），
而不是让它静默混在提案堆里。

**反面实证（r136 实测）**：修之前 11 条提案里**只有 3 条**能追到读数面，8 条追不到
（其中 4 条连 evidence / acceptance 字段都没有）。r136 逐条处理后 11/11 完整。
⇒ 这不是别人的问题，是**我自己写提案时没走自己立的纪律**。

## ⚠️ 纪律须有阻断点（#35，2026-10-21 立规）

立了纪律却没有**阻断点**，等于没立。r136 盘点：本仓 5 条强制条目**全部没有流程强制点**
（门只跑不阻断、`.git/hooks` 三个 hook 全部 `exit 0`）。

**机器判据**：本次提交若落在纪律面（改 `05-exec/` / 转办提案 / 对标报告 / `AGENTS.md` /
`memory/07-next-steps.md` / `run_gates.py`），则**对应的门必须过**，否则**阻断提交**。
判定由 `python 05-exec/r137_commit_gate_map.py --json <件>`（第 49 门）给出
`required_gate_ids` / `in_scope_n`；`pre-commit` 依此逐门跑（`run_gates.py --gate <id> --no-ledger`）并按结果阻断。

**分级原则（R137 定）**：
- **不在纪律面**（`in_scope_n = 0`）⇒ **不阻断** —— 并行会话也在改同一个仓，
  无差别阻断 = 把我的判据变成「别人的活干不下去」（R269 反面）。这是 r130 老 hook 一直 exit 0 的正当理由，保留。
- **在纪律面** ⇒ 逐门跑，只阻断**这些门**的红；不连带阻断其他门（避免把无关的历史红算到本次头上）。
- **逃生阀**：`SKIP_COMMIT_GATES=1 git commit ...` 可放行，但**必须在提交说明里写明为何先落盘**。
- **台账不污染**：hook 用 `--no-ledger` 试跑，不写门禁台账（新鲜度门读的是完整跑的台账）。

**5 条强制条目的阻断点现状（r137 实测）**：

| 条目 | 触发条件 | 阻断的门 | 状态 |
|---|---|---|---|
| #30 落盘强制 | 改 `memory/07-next-steps.md` | `debt_aging`（账龄件重生） | 有阻断点 |
| #31 处方必先实测 | 改转办提案台账 | `proposal_evidence_face` | 有阻断点 |
| #32 判据面必先实测 | 改 `05-exec/` 下的判据 | `proposal_evidence_face` + 门表对账闸 | 有阻断点 |
| #33 结论层推理须标注 | 写/改对标报告 | `causal_evidence_face` | 有阻断点 |
| #34 纪律自用 | 改提案 / 改 `AGENTS.md` | `proposal_evidence_face` + `gate_table_reconcile` | 有阻断点 |

> 取值：`python 05-exec/r137_commit_gate_map.py --json <件>` 的 `required_gate_ids`；
> 阻断行为实测见 `_temp/v23_redprobe.py`（造一条无支撑提案 ⇒ 门面报「无读数支撑 1」⇒ 该门红 ⇒ hook 阻断）。

## ⚠️ 阻断机制须可恢复（#36，2026-10-21 立规）

#35（纪律须有阻断点）立了之后，r137 收尾发现一个更隐蔽的问题：**阻断机制本身不可恢复**。
`.git/hooks/` **不在 git 里**（`tracked hooks = 0`）⇒ 换机 / clone / 重装即全丢。
r130 与 r137 两次装 hook，装完都没再核过 ——
**「阻断机制不可恢复」比「没有阻断机制」更危险，因为它让人以为有。**

**机器判据**：
1. 阻断机制健在性由第 50 门（`r138_hook_health.py`）逐项断言 —— `pre-commit` 存在、含 `exit 1`、
   含分级判定入口、含逃生阀、用 `--no-ledger`；`post-commit` 存在；判定面脚本可跑。**任一不通判红**。
2. 恢复路径必须**脚本化且可自证**：`python 05-exec/r138_install_hooks.py`
   从 git 跟踪的模板（`05-exec/hook_templates/*.sh`）安装，**装完立刻跑自检**，不通则 rc≠0。

**反向验证（r138 实测，三态）**：

| 变体 | 读数 | 判定 |
|---|---|---|
| 空 hooks 目录（换机/clone 后真实态） | 2/8 通过，**6 项 FAIL** | 有牙 |
| `exit 1` 被抹掉（#35 要治的病） | **H2 精准 FAIL** | 有牙 |
| 真实 hooks | 8/8 通过 | 不冤枉 |

**恢复闭环实测（r138）**：删掉 `pre-commit` ⇒ 自检报 `3/8`（5 项 FAIL）⇒ 跑安装脚本 ⇒
`安装 2/2` + `自证 rc=0` ⇒ 再自检 `8/8`。**「不可恢复」变成「一条命令恢复且自证」。**

## ⚠️ 每轮收尾强制（#30，2026-10-20 老大立规）

本轮产生的**任何**建议/待办/改进项，必须在本轮内自动落盘到 `memory/07-next-steps.md`（或分卷），
**不等老大提醒**。落盘的机器判据 = 编号可 grep + 带判据/到期日 + 被 `r38_debt_aging.py --report <本轮报告>`
的建议面承认已承接（否则该门判 FAIL）。
没执行的建议也要落盘并标状态（⏳/✅/❌），禁只写在回复里。
反面实证：r122 主任务做完后 4 条新建议只在回复里，被建议面抓 FAIL 才补落。
## 已知坑（本壳级必读三条；其余见 `06-constraints.md`）

- 聚合 runner 的 stdout **禁落项目根**（noise 顶层 VIOL）**也禁落 tracked 件**（Out-File 截零 → `tracked_empty_check` 判红）；正解 = gitignore 命中的 `_temp/` 或只留 `--json` 快照。
- **写记忆卷之后必须重算账龄件**，否则「相对新鲜前置」把三门再次染红。⚠️ **本条已连踩 3 轮（r119/r121/r122）**：症状 = 棘轮报「overdue/deferred/repeat 指标缺失」+ `r55_note_fixtures` 的 n4 腿必现 FAIL（3/3 复现）。正确顺序 = **先改 07 台账 → 后跑 `r38_debt_aging.py`**；已踩后补救 = 原样重跑一次 `r38_debt_aging.py`（件 mtime 即新于卷集），ratchet / note fixtures / 同号多副本面三项随之转绿。
- 受管根提交落地 ≠ 交付：必复算 `git merge-base --is-ancestor <sha> HEAD`（并行 rebase 会把你的提交甩出主线，一手 `b9e5d90e`）。

