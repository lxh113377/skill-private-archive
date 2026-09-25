# AGENTS.md — 自建skill优化 项目级 Skill 绑定表（P-1，A-project-handoff）

> 手动维护。agent 检测到本项目路径时第一动作 Read 本文件；命中触发条件 → 加载对应 skill，禁裸跑。

## Skill 强制绑定（命中即加载）

| 触发条件 | 必加载 skill |
|---------|-------------|
| 任何项目修改操作（代码/记忆/技能/文档/配置） | A-project-handoff |
| 每轮复杂任务开场 | A-memory-start |
| 任务结束/复盘/经验沉淀 | A-get-memory |
| 动手前需求澄清 | A-ask-questions |
| 审计视角：预判 agent 行为链/死链/规则冲突 | vp-perspective-audit |
| 注册表 user_created 标记失真 / 死链 / orphan | data-layer-consistency-fix |
| 同类 skill 合并评估（local-* / story-* / 审计族） | skill-merge |
| 路由健康度 / 领域计数 / 版本线自洽 | fenjue-routing-health-check |
| 提示词结构深度审计（V1-V7） | prompt-system-audit |
| 触发命中率全量审计 | skill-hitrate-full-audit |

## 项目门禁命令（A-memory-start V9.8 / R193 读取本行，修改类任务动手前必跑）

```
python 05-exec/run_gates.py
```

> **r31 起改为聚合 runner 单入口**（对标 mycelium-hq/ai-brain-starter `template-purity.yml` 的
> "the identical check runs locally pre-push, in the write-time hook, and here in CI — one source of truth"）。
> runner 内 `GATES` 表 = 单一真相源，逐门独立执行**不短路**（原 5 段 `&&` 串一段红即后四段不可知），
> 每门打印**覆盖根清单**（本仓 R20-2），并输出每门耗时（**单点值不可引用**，取值 `python 05-exec/run_gates.py --json <件>.json` 读 `total_ms`/`elapsed_ms`；r31-r32 观测区间 1.78～4.82 s，最慢门恒为 `r19_scan_fixtures`）。
> **r32 起门数 = 6**：新增 `gate_run_freshness`（`05-exec/r32_gate_freshness.py`），它评的是「本仓门禁最近是否还在被真跑」——
> 依据 `06-benchmark/gate_runs.jsonl` 执行台账（每次 runner 执行追加一行，`origin` 区分 `local`/`ci`）。
> 三条反假绿要点：① **空台账 ⇒ `UNVERIFIED`**（没跑过 ≠ 跑得干净）；② **只有 CI 记录 ⇒ FAIL**（CI 绿不能替人证明两台机专属门还在跑，这是本仓对 CI 的反向用法：用 CI 盯人）；
> ③ 该门自身标 `meta: True`，其红**不写回台账 `verdict`**（否则一次引导期红会自锁成永久红，r32 实测复现过；`overall` 仍如实记录）。
> 存在理由（对手实物）：anthropics/skills 的 run 分布 = 25% success / **75% failure**，且**已停摆 6 周无人报警**；
> superpowers 近 50 run **82% failure**。⇒ 「把判据放进 CI」本身不构成保障，必须另有有效性判据。
> 复现：`python 05-exec/r32_ci_health.py --json <件>.json`（近 ≤50 run 结论分布 + 心跳）；`python 05-exec/r32_freshness_fixtures.py`（18 例含变异 4/4）。
> ⛔ **X-1（r32 立）**：禁止为了把 CI 覆盖凑到 6/6 而把技能语料复制进本归档仓 —— 仓内 tracked `SKILL.md` 恒为 0 是有意的，
> 复制进来等于造第二真相源（违 C1），且快照陈旧会**假绿**（比红灯危险）。那 2 台机专属门是**设计边界**。
> 三态判据：`PASS`（rc=0 且含该门标记）/ `FAIL`（rc≠0）/ **`UNVERIFIED`（rc=0 但标记不见 —— 静默跳过一律不算绿，R247/R220）**；
> 门脚本缺失 ⇒ exit 2。聚合绿**不等于**受管根四门禁绿，runner 会显式打印「本 runner 不覆盖」清单。
> 展开等价的 6 条原命令（顺序与 runner 一致）：
> `python 05-exec/r19_scan_fixtures.py && python 05-exec/r19_baseline_contract_fixtures.py && python 05-exec/baseline_contract_scan.py --quiet && python 05-exec/ratchet_gate.py && python 05-exec/control_char_scan.py . && python 05-exec/r32_gate_freshness.py`
> 六条全 `[GATE:fixture-pass]` / `[CONTRACT:PASS]` / `[RATCHET:PASS]` / `[CTRL:CLEAN]` / `[FRESH:PASS]` 才允许落盘改动（`[RATCHET:FAIL]` 只在「指标比基线长大」或「指标算不出」时出现；既有的超硬顶项按非阻断告警显示，`--strict-cap` 可升级为阻断）；任一红 = 判据或基线契约已失效，先修判据再动手（R263）。
> runner 自身的夹具 = `python 05-exec/r31_run_gates_fixtures.py`（17 例含变异 4/4；刻意不入 `GATES` 表，因夹具会 subprocess 调 runner，入表即自递归）。
> 第五条 `[CTRL:CLEAN]` = 全仓无非法控制符（C0 ∪ {0x7f DEL} 减制表/换行/回车）。它拦的是「肉眼看不见、但会让引用检索不到」这一类：实测当天四轮复现，含被修文件自身与受管根两处死引用。
> 判据可信度本身由 `python 05-exec/r19_fixture_mutation_check.py` 变异测试担保（4 项变异必须全部被拦 + 未变异对照组通过）。
> **条件前置 · 写时冲突检查（r34 M-1，挂账四轮后本轮落地）**：往权威源同族文件（`behavior_core.md` / `BOOTSTRAP*` / `contract.md` / 各级 `AGENTS.md` / 技能 `SKILL.md`）**落规则前先跑**
> `python 05-exec/rule_conflict_scan.py --on-write <待写文件> [--against <权威源>]`（缺省权威面 = 脚本内 `DEFAULT_FILES` 十件）。
> 三态退出码：`0 CLEAN` / `1 CONFLICT`（先裁后写，**禁改权威源凑绿** R263）/ `2 UNVERIFIED`（候选不存在、为空、无极性词句，或权威侧规则数=0 ⇒ 覆盖为空即无鉴别力，**不得当作「无冲突」放行** R247）。
> 与批量模式的分工：批量 `rule_conflict_scan.py` 出跨文档候选清单供人工裁定；`--on-write` 只拿**待写的这一个文件**去撞权威源，把「写进去、入库后才发现互斥」提前到落盘前 —— 对标 mycelium 的双脚本形态（`check-rule-conflicts.py` + `check-rule-conflicts-on-write.py`）。
> 夹具 `python 05-exec/r34_onwrite_fixtures.py`（17 例含变异 4/4；变异 harness 自身缺陷见 r34 报告 §6 —— 「加载失败算拦住」已判为无效计数）。
> **条件前置（非每轮必跑）**：要把判据建议**外推给归属会话**时，先跑 `python 05-exec/transmit_obsolescence_check.py` —— 它拿 `06-benchmark/transmit_proposals.json` 与焚诀 verify 注册面（实测 33 条已注判据）做覆盖度比对；打印 `[TRANSMIT:STALE]` = 该件归属方**已自落**，禁止再外推；`[TRANSMIT:UNKNOWN]`/exit 2 = 真相源取不到，**不得当作「未过期」放行**。夹具 `05-exec/r21d_obsolete_fixtures.py` 26 例（含 4 项变异对照）。
> **r33 起轮次版本锚约定（对标第十维实测的结论，非抄形式）**：每完成一个实质轮次，push 后给该提交打 **annotated tag**
> （名式 `rNN`，如 `git tag -a r33 -m "r33 ..." && git push origin r33`）。
> 理由（实物）：12 个对标对象里 **11 个有 tag**（最少的同构参照系 mycelium 也有 4 个），唯一 0 tag 的 anthropics/skills 是因为它不做发布；
> 而本体系过去把版本全写在**文本**里（技能 `version:` / `Version: V1.0` / C13 的 `V10.70.0` 锚点行），
> **git 层 0 tag** ⇒ 无法 `git describe`、无法回答"r31 那轮落在哪个提交"、区间回滚 `git revert r33..HEAD` 根本写不出来。
> ⇒ 补的是**机器可查锚点**（回滚与归因能力），不是发布流水线。
> ⛔ 同时立 **X-2 禁做**：不得为"像一线"而补 `LICENSE`（= 对外授予权利，本仓为私有归档，非所愿）
> 或开 release/发布流水线（无外部消费者；r31 §1.2 与 r32 §1.1② 两轮的共同结论：**严格度由有无外部消费者决定，不由星标决定**）。
> 验收：`git tag -l` ≥1 且 `git describe --tags` 可解析；取值 `git -C . tag -l && git describe --tags`。
> 关联待裁定（本仓不代决）：受管根 `焚诀` 新增的 `CONTRIBUTING.md`/`LICENSE.md`/`SECURITY.md` 被 `noise` 判 VIOL 要求迁 `_trash`
> ⇒ allowlist 与业界治理件冲突，属 A-project-handoff 面，见报告 §1.1④ 与 §5 H-3（R269 不擅动他人在途文件）。
> ⛔ **边界（behavior_core #23「用户命令绝对优先」）**：上面这条只判定「**该不该把建议外推给别人**」，**不得**被引申为「本轮可以少干活/跳过执行」。本仓一切判据的合法作用域是**约束写法与落盘方式**（原子替换、先备份、只降不升棘轮），**永久禁止**用「自判重复 ⇒ 跳过执行」实现幂等。


## 铁律

- `memory/07-next-steps.md` P0 永不为空；`savepoint` 后才能结束对话
- 阶段 0-3 为只读取证阶段：不修改 `D:\global_skills` 下任何 skill 源文件，只在本工作区写报告
- 阶段 4 起改 skill 文件，唯一途径 = `rule_editor.py`，禁 `write_file` 整体重写；改完重建派生件 + 复跑三门禁（mirror / noise / evolution）
- 任何结论须标注 ✅已实测 / ⚠️部分实测 / ❌未实测；禁止用旧快照、旧记忆、历史报告当现状
- 落盘编辑前必须输出 `【数据流假设】` 四要素（来源/流向/结构/异常），缺一不得编辑
- **销账必须逐条对照分卷 `partN` 的已完成条目**（2026-09-22 用户裁定，替代「改上游 review 判据」方案）：`handoff.py status` 报 `8/8`、`review` 报 `9/9（100%）`**均只判「文件是否被填充」**，不做「主卷声明 vs 分卷已完成项」交叉校验 ⇒ **分数 100% ≠ 记忆与实况一致**。凡判定「项目记忆是否过期 / 某项是否已完成」，**必须同时读主卷 + 全部分卷，逐条比对 `## ✅ 已完成` 区块**；禁止仅凭 `status`/`review` 分数或主卷单方声明下结论（实证：2026-09-22 第 10 轮，主卷 3 条已修 [BUG] 与 8 条已闭环 [DEBT] 在 100% 分数下长期滞留）。
- **环境脏项从外部引入时只登记不擅动**（R269）：受管根出现的**非本项目**散落项（如并行会话在途快照）先查 mtime / 提交序 / 生产脚本溯源，确认归属后**登记为待观察**；禁止为让 `savepoint` 通过而擅自迁移他人在途文件（2026-09-22 实证：`D:\global_memory\_bak\07nextsteps_20260922_142621` = 并行会话改 GM 07-next-steps 前的手工快照）。
- **记忆里写「当前」类值必须附取值命令，禁硬编码**（2026-09-22 落地，替代被否的自动判据）：项目记忆出现「当前/实况 HEAD、版本、计数」等**当下值**时，**必须同时写出取值命令**（如 `git rev-parse --short HEAD`），**禁止硬编码具体值**。理由（实测）：值一旦硬编码即会陈旧，而**历史分卷里的旧值「当时为真」不该报警**，两者文本形态一致。
- **⛔ 本项目不再尝试为「记忆里的值是否陈旧」建自动判据**（2026-09-22 边界值测量定案，防重复造）：`05-exec/R272b-boundary.py` 已在 **8 个真实项目 / 104 行含 hash 上下文行**上测四个候选判据（值比对 / 硬编码形态 / 全仓 HEAD 命中 / 规范性），结果 **TP 恒 0（零拦截力）、FP 1~3（有误报）、真实世界正样本 = 0（连标定样本都没有）** ⇒ 按 R236 补注③「区间重叠即不可作判据，须改机制」**判为不可成立**。
- **⛔ 连「收窄到主卷 P0 的提示级」也已实测否决**（2026-09-22 第 14 批，`05-exec/R272c-narrow.py`）：用户要求「先重测、**0 误报才做**」，实测 **9 个真实项目主卷** ⇒ 命中 **2 处，2/2 全为误报、真漂移 TP = 0**——① `医/07:11` 的 `HEAD=645177f` 是**带日期的实测留痕**且同行已有复核命令；② `超市/07:13` 的 `5df544a` 是**备份分支**上的 commit（正当引用）。⇒ **提示级也不做**。后续会话**不要**再为该项造任何形态的判据（值比对 / 格式 / 提示级均已否决）；改用上面的「规范性约定 + 人工逐条销账」。
