# DECOMPOSE · r322（闭包口径第三层缺陷取证 + 首批补链真实落盘 + v2 普查判据 + 需求6 扩池候选）

> 本卡先于本轮任何产物写入落盘。起点 45620ea（tag r321e）｜goal 第 2 回合 ⇒ 轮号 r322（现取：git log 最大 rNN=321 + 1；`grep -rn R322- memory/ 04-plan/ 05-exec/ 06-benchmark/` 现值 NONE ⇒ 领号无撞）。

## 起点实测（现取 2026-10-31T22:4x）
- 本仓 dirty = 44 行（会话前既存 archive/trash-proof 备份族 + 我的 debt_end.json），非本轮造成。
- **受管根 D:/global_skills：`status --porcelain` = 79 行，其中索引暂存 0 行、worktree-only 76 行、未跟踪 3 行**；HEAD = e8f489ebcf78（与普查件 head_sha 一致）。
  ⇒ 上一轮 G-L1（要求 0 行）按字面永远等不到；但落盘的真实风险面是「**我这一笔会不会裹走他人在途改动**」，不是「全仓必须干净」。
  ⇒ rule_editor 用 `git add -A -- <file>` **带路径作用域**（:7137 注释具名：无作用域版曾把别人在途改动顺带带走），且索引现为空 ⇒ 前提满足。
- 逐件入口态（B1–B6 目标）：`gstack/SKILL.md` **CLEAN**（唯一可安全落盘的入口件）；ppt-master / story-setup / story-long-write / data-analysis / hyperframes-media / diagram-maker 的 SKILL.md 均 DIRTY（他人在途）⇒ 禁动。
- gstack 盘上 27944B vs HEAD blob 27307B，差 = 637 = CRLF 数（`core.autocrlf=true`）；CRLF→LF 归一后**逐字相等** ⇒ git 判 CLEAN 正确，非漂移（r260 回滚演练点名的同款）。

## 本轮核心怀疑（决定批次表要不要重算）
`gstack` 的 6 个孤儿全在 `gstack/qa/**` 与 `gstack/review/**`，而该子树里**存在嵌套入口件 `gstack/qa/SKILL.md`、`gstack/review/SKILL.md`**
⇒ 普查 `check_r319a.py` 的可达闭包只从顶层 `gstack/SKILL.md` 展开，把「由嵌套 SKILL.md 引用的文件」全判成孤儿。
若路由会加载嵌套 SKILL.md（skill 目录下再套 skill 是本受管根的既有形态），那这批"孤儿"是**假孤儿** ⇒ 真实工作量还要再降，
且批次表 B4（story 族 106 件）里大量项可能同因。这是继 P-1 噪声白名单、P-2 占位符死代码之后的**第三层口径缺陷**（闭包起点）。

## 臂全部失效后的处置记录（#44⑦，写在最前）

本轮 3 臂（A 闭包审计 / B v2 判据 / C 扩池候选）**两次派出、五次全灭，零产出无收尾消息**（provider 切换窗口）。
按 #44⑦「连续 2 次 ⇒ Lead 自干并登记根因」：三件全部由 Lead 自干完成，产出分别为 `_repro/r322a/`（3 件，判据 4 腿）、
`_repro/r322b/`（5 件，判据正例+4 负控）、`_repro/r322c/`（3 件，判据正例+1 负控）。
根因登记：模型路由切换窗口（qfmodel→trae→deepseek 三连切换）期间的 subagent 全部返回 failed 且 `left no closing message`；
`send_message` 对已注销成员返回 `active teammate not found` ⇒ 无法唤醒，只能自干。**这不是任务失败，是通道故障**，已在 `_repro/r322a/work/arm_failure_log.json` 留证。

## 本轮分解（W=3 并行就绪 ⇒ N=max(2,min(8,3,ceil(T/45)))=3）
| # | 件 | owner | 写面 | 判据命令 + 期望末行 |
|---|---|---|---|---|
| 1 | 嵌套 SKILL.md 闭包审计：全受管根有多少嵌套入口、顶层是否链它们、路由是否真会加载（一手读 router/注册表面） | 臂 A `_repro/r322a/` | 仅该目录 | `python -B _repro/r322a/check_r322a.py` ⇒ `[R322A:CLOSURE] nested=<n> top_linked=<n> fake_orphans=<n> teeth=pass` |
| 2 | v2 普查判据：三处口径一次修（噪声白名单 / 占位符展开对树 / 嵌套闭包），只读受管根，输出新旧对照 | 臂 B `_repro/r322b/` | 仅该目录 | `python -B _repro/r322b/check_r322b.py` ⇒ `[R322B:V2CENSUS] broken_real=<n> orphans_v2=<n> delta_vs_r320=<n> teeth=pass` |
| 3 | 需求6 数据缺口：从本仓 + D:/global_memory 会话面挖 ≥60 条**未命中直连表**的真实 query，产 PR-ready 扩池候选件（严禁写 焚诀/eval） | 臂 C `_repro/r322c/` | 仅该目录 | `python -B _repro/r322c/check_r322c.py` ⇒ `[R322C:POOL] candidates=<n≥60> dedup=ok leak_hits=0` |
| 4 | Lead：gstack 补链首批真实落盘（rule_editor 唯一途径）+ 复跑普查验效应 + 三门禁 | Lead | 受管根 gstack/SKILL.md（经 rule_editor）+ 本仓 04-plan/_repro | 复跑 `check_r319a.py`，gstack orphans 6→目标值；`[GATE:mirror-pass]` |
| 5 | Lead：批次表按新口径重算 + 台账/报告收口 + 显式清单提交 + tag + 复算 origin | Lead | 04-plan 批次表、memory/07、06-benchmark | 三读数一致（add 后 / commit 后 / 消息声明） |

## 30 秒卡 8 问
① 互不引用工作流 ≥2 ⇒ 是（A 读受管根结构面、B 读普查件+写判据、C 读会话日志面）→ 派 3 件。② 单件 ≥3 回合 ⇒ 是。③ ≥2 独立面取证 ⇒ 是。④ 四问（独立验收 ∧ 写面不相交 ∧ 输入可预固定 ∧ ≤45min）⇒ 三件全过。⑤ 本轮发 3 件（≠1）。⑥ brief 七项随正文写全。⑦ 每件判据命令+期望末行见上表。⑧ 收件后我复跑：A 我复跑其 check 并抽查 3 个嵌套件的 ls-tree 事实；B 我用它的 v2 读数与 r320 旧读数对账并验 delta 可解释；C 我抽查候选 query 的 leak_hits=0（拿直连表现核）。
skip_reason：件4/件5 = Lead 自留（写面为受管根入口件与共享台账/计划件，同文件先串后派 + 最终 diff 自留）。

## 并行写面纪律（D7.2）
- 臂 A/B/C 只准写各自 `_repro/r322[abc]/`；Lead 在交付前不写这三目录。
- Lead 落盘只动 `gstack/SKILL.md` 一个入口件（现 CLEAN），其余 DIRTY 目标件一律不碰。
- 本轮起严格执行 R321-7 验收靶：add 后 commit 前印 `--cached` 计数、commit 后印 `--name-only` 计数、消息声明数，三者一致才算交付。
