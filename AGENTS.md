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

