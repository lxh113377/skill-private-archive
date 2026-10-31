# r323b · 需求 6 判据口径改多标签的可行性取证（只读）

**结论三态：`PARTIAL`** —— 机制上可达（一行判分改动 + 全仓已有 8 处 list 约定），但**数据面零样本**：现役 291 条题面最长 30 字符、`expected_skill` 全部单值（list=0），拿它测「任务书 → 多标签」等于用一张量程 30 字符的尺去量 200+ 字符的任务书。

| 项 | 值 |
|---|---|
| 取证时间 | 2026-11-01（Asia/Shanghai） |
| 焚诀 eval 只读面 | 可读（红线未越：焚诀仓零写入、零 git 写） |
| 写面 | 仅 `自建skill优化/_repro/r323b/`（全部产出与探针脚本都在此目录内） |
| 判据命令 | `python -B _repro/r323b/check_r323b.py` |
| 实际末行 | `[R323B:MULTILABEL] verdict=PARTIAL judges=7 teeth=pass` |
| 负控 | `python -B check_r323b.py --selftest` → `[R323B:SELFTEST] 7/7 腿通过` |

> 判据有牙的关键：不止查「字段在不在」，还**逐条回源核验** `file_line` 指向的文件存在（`os.path.isfile`）且 `rule` 与磁盘该行**逐字相同**。只查字段的判据，把 rule 填成「随便写点」也能过。

---

## 问 1 · judge 分支有哪些取值？逐条贴规则

**命令**：`read eval/frozen_blind_eval.py`（132 行全文）+ `grep -rn judge --include=*.py eval/`

**读数**：judge 标签**共 4 档**（`exact` / `usable-suboptimal` / `wrong` / `blindspot`），但**分支点有 7 处**，各自「吃什么」不同：

| # | 分支 | file:line | 逐字规则 | 吃 expected? | 多值可用 |
|---|---|---|---|---|---|
| 1 | exact | `eval/frozen_blind_eval.py:15` | `exact=1.0, usable-suboptimal=0.75, wrong=0.5, blindspot=0.4` | 否 | 否 |
| 2 | usable-suboptimal | `eval/frozen_blind_eval.py:28` | `JUDGE_WEIGHT = {'exact': 1.0, 'usable-suboptimal': 0.75, 'wrong': 0.5, 'blindspot': 0.4}` | 否 | 否 |
| 3 | default_exact | `eval/frozen_blind_eval.py:64` | `judge = q.get('judge', 'exact')` | 否 | 否 |
| 4 | wrong | `eval/frozen_blind_eval.py:66` | `w = JUDGE_WEIGHT.get(judge, 0.5)` | 否 | 否 |
| 5 | **top1_equality** | `eval/frozen_blind_eval.py:70` | `hit = (top1 in (None, 'NONE')) if expected is None else (top1 == expected)` | **是** | **否** |
| 6 | aggregate_score | `eval/frozen_blind_eval.py:82` | `score = round(hit_w / n * 100, 1) if n else 0.0` | 否 | 是（中性） |
| 7 | max_achievable | `eval/frozen_blind_eval.py:85` | `max_achievable = round(total_w / n * 100, 1) if n else 0.0` | 否 | 是（中性） |

**结论**：真正决定「命中」的只有第 5 处（`:70`），它是**标量相等**（盲区走 `expected is None` 分支）。第 6/7 处对多标签**完全中性** —— 分数与上限只由 judge 标签加权，与 expected 取值形态无关。这就是「多标签不会动上限」的代码依据。

补充：`:66` 是**不拒收**的查表 —— 未知 judge 静默回落 0.5（不是报错），所以「新增一个 judge 档位」不会当场炸，会静默按 0.5 计。这点在做多标签时要留意：新增档位必须先进 `:28` 的表。

## 问 2 · layered_testset.json 的 schema：有没有多值字段？

**命令**：`python -B _probe_schema.py`（逐条遍历 291 条统计字段与类型）

**读数**：
```
N_QUERIES 291
GROUP_FIELDS {tier: 5, queries: 5}            # 顶层 5 个 {tier, queries}
QUERY_FIELDS {query: 291, expected_skill: 291, judge: 291, source: 291, skill: 291, note: 12}
EXPECTED_TYPE_DIST {str: 269, NoneType: 22}
LIST_VALUED_EXPECTED 0
```

**一条真实条目原文**（`tier=skills`，逐字来自文件）：
```json
{"query": "需求有点模糊，帮我先问清楚再动手", "expected_skill": "A-ask-questions",
 "judge": "exact", "source": "auto-draft", "skill": "A-ask-questions"}
```

**结论**：schema 里**没有任何多值字段**（无 `acceptable` / `aliases` / `also_ok` / `labels`）。`expected_skill` 实测严格单值：str=269 / None=22 / **list=0**。

但——**判分面之外的其余 8 处代码早已按「可传 list」写死**，同一行逐字重复：
```
exp_set = {exp} if isinstance(exp, str) else set(exp)
```
落点：`eval/unified_router.py:356,366` · `eval/eval_dual_tree.py:125` · `eval/functional_dim_checks.py:168` · `eval/llm_layer.py:271` · `eval/run_dual_regression.py:30` · `eval/scorecard.py:128` · `eval/skill_hitrate_eval_v2.py:129` · `eval/tune_threshold.py:45`。

⇒ **全仓的「多标签词汇」已经存在，只有 frozen_blind_eval 这一把尺没接上**。这不是要新建体系，是要补齐最后一处。

## 问 3 · 现成的多标签 / 加权能力能复用哪些？

**命令**：`grep -rn 'def annotate|annotate(' --include=*.py eval/`、`read eval/blindset_leak_manifest.py`、`read eval/scorecard.py`、`read eval/unified_router.py:340-414`

| 件 | 能复用？ | 证据 |
|---|---|---|
| `blindset_leak_manifest.py::annotate()` `:69-90` | **不能**当多标签标注器 | 它只做**泄漏标注**（`status` = LEAKED/CLEAN + 命中规则 idx），**不判对错**。名字像标注器，职责是审计器 |
| `blindset_leak_manifest.py::score()` `:93-107` | **能** | 独立于盲测的 judge 加权计分器，按 judge 过滤，未知 judge 返回 `pct=None`（`:204-206` 有自测腿「不假装量到」） |
| `unified_router.route()` 的 `candidates` | **能**（关键） | 已返回**完整排序表**（`:229-230` 组装，`:121-122` 文档）。多标签判定可直接吃 top-k，**无需改路由器** |
| `unified_router` 的 top1/top3 双指标 | **能** | `:377/:380/:385/:388` 已是 set 成员判定（`top1 in expected_set` / `any(n in expected_set for n in top3)`）⇒ **set-recall 骨架已在，只是没接进 frozen_blind_eval** |
| `scorecard.py:128` | **能** | 已 `exp_set = {exp} if isinstance(exp, str) else set(exp)` ⇒ 上层消费方已能接 list，不用改 |
| `JUDGE_WEIGHT` `:28` | **能**（唯一权重旋钮） | 模块级常量，改档位权重的入口只有这一行 |

**weight 字段怎么用**：`w` 不是数据里给的，是 `:66` 由 judge 查表算出来的（exact=1.0 / usable-suboptimal=0.75 / wrong=0.5 / blindspot=0.4）。所以「加权」这件事**已经实现**，但权重维度是「judge 档位」，**不是「多个 acceptable 的置信度」**。要做后者得在 `:28` 之外新开一张表。

**`judge: exact` 之外的分支有没有被用到**：有，且是实跑数据 —— 291 条实测 `{exact: 266, blindspot: 22, usable-suboptimal: 3, wrong: 0}`。注意 `wrong: 0` ⇒ **`wrong`（0.5）这一档从未在真数据上生效过**，只活在权重表里。

## 问 4 · 最小改法是什么？动几个文件？旧读数会不会失效？

**命令**：`python -B _probe_break.py`（复刻 `:70` 表达式喂 list）、`grep -n testset_sha256 scripts/ci_blind_eval.py`、`python -B _probe_schema.py`（`HAS_ARGPARSE`）

**读数 1 —— 不改会怎样**：
```
LIST_BREAKS   False   # top1=A-ask-questions, expected=[A-ask-questions, brainstorming] -> 判 False
LIST_BREAKS2  False   # top1=brainstorming,      expected=[A-ask-questions, brainstorming] -> 判 False
SET_MEMBERSHIP_WOULD_BE True
```
⇒ `:70` 吃 list 会**静默全 miss**（不报错、不告警）。这是多标签方案的唯一硬堵点。

**最小改法**：
```
改前 :70  hit = (top1 in (None,'NONE')) if expected is None else (top1 == expected)
改后 :70  hit = (top1 in (None,'NONE')) if expected is None else (top1 in ({expected} if isinstance(expected,str) else set(expected)))
```
- **判分口径 1 个文件、1 行**（`eval/frozen_blind_eval.py:70`）。权重表、分母 `n`、上限算法**零改动**。
- **有没有现成旋钮**：**没有**。`HAS_ARGPARSE=False`（该文件连 `import argparse` 都没有），只有 `--json` 与 `--set {frozen|layered}` 两个 argv 分支（`:113-114`）。`JUDGE_WEIGHT` 是模块常量。⇒ **任何口径变更都必然落在代码上，没有 env / CLI 逃生舱**。这也是为什么它属于「改尺」，必须按 R263 先评审。
- **全路径 3 个文件**：① `eval/frozen_blind_eval.py:70` 判分（1 行）② `eval/layered_testset.json` 加标签字段（数据面，纯增量，不动旧字段）③ `eval/blindset_gate_baseline.json` 重签 `testset_sha256`。
  - ③ 容易被漏：`scripts/ci_blind_eval.py:114-120` 对题集指纹走 **fail-closed**，题集字节一变就判「本门不可信」且**不回落 `hard_floor=50`**。不重签 ⇒ CI 这道门从「绿」变「不可信」，不是变「红」。

**旧读数会不会失效** —— 分两层，别混：

| 面 | 会失效？ | 依据 |
|---|---|---|
| **291 条基准的分数** | **不失效** | 权重和 `sum_w=277.05`、分母 `n=291` 都与标签无关（见问 5 的不变性实测）⇒ 旧读数(88.3 / 95.2)与新读数**同尺可比** |
| **混引口径** | 失效 | 命中判据变宽 ⇒ 同一查询在多标签下更易命中，**跨口径相减/相比即失真**，禁混引 |
| **基线指纹** | 失效（必须重签） | `blindset_gate_baseline.json` 的 `testset_sha256`；实测现读 = `e1d700258d2b55ad2515df98bd35dd051154b9870222266b0e4852b33c4a0856`，与基线**逐字相同**（说明守卫此刻是在位的，改题集就会踩） |

⇒ **291 条能重算**，但重算出来的数「更绿」且不能与旧数混引；同时必须重签 1 个基线文件，否则门禁翻「不可信」。

## 问 5 · 多标签上线后 max_achievable 会变成多少？

**命令**：`python -B _probe_ceiling.py`（按 judge 权重逐条复算上限，并做干净面复算）

**读数**：
```
FULL_N 291   FULL_CEILING 95.2          # = blindset_gate_baseline.json:20 max_achievable_pct 95.2
CLEAN_N 106  CLEAN_CEILING_RECOMPUTED 87.5   vs_recorded 87.5   # = blindset_leak_manifest.json:49
MULTILABEL_CEILING_INVARIANT 95.2   # 权重只来自 judge，加多少个 acceptable 都不动分子分母
TIER skills 151 -> 100.0 | cli 59 -> 100.0 | short 51 -> 100.0
TIER fault_finding 19 -> 61.3 | negative 11 -> 40.0
```

**结论**：**`max_achievable` 仍是 95.2，不变**（干净面同为 87.5）。理由是结构性的：上限 = `权重和/n`（`frozen_blind_eval.py:85`），权重只由 judge 档位决定，**多标签只放宽「命中」，不动「分数」的天花板**。

所以「多标签上线会把上限变成多少」这个问法本身就是个不能达成的问法 —— 它**不会变**。真正会变的是**实测分**。

**实测分会落到哪**：区间 `[88.3, 95.2]`。下界 = `blindset_gate_baseline.json` 记录的 bge 面 2026-10-01 实测 88.3；上界 = 上限 95.2。

**确切值算不出，具名缺什么**：
1. **291 条每条的 acceptable 标签集** —— 现在 0 条，需要新标注（这是真缺口，不是口径缺口）；
2. **一次真跑 `route()` 的实测** —— 本轮是只读取证，未跑 291 条全量，所以任何 `[88.3, 95.2]` 内的具体数都是估的，不予给点值。

---

## 三态判定依据（为什么是 PARTIAL 不是 REACHABLE / BLOCKED）

**机制侧 REACHABLE**：改 1 行判分 + 全仓 8 处已有 list 约定 + `candidates` 排序表现成 + `scorecard.py:128` 上层已能接 list ⇒ **不需要新建体系**。

**数据侧 BLOCKED**：这张尺上**没有一条任务书形态的题**。实测 291 条：`MEAN 11.5 / MEDIAN 11 / MIN 3 / MAX 30`，`LEN_GT 30 = 0`、`LEN_GT 200 = 0`。要测「任务书 → 多标签」，现有语料**零样本可测**。

⇒ 合起来是 **PARTIAL**：改法可落地，但落到这把尺上没有东西可量 —— 必须先补「任务书形态 + 多标签」的新题面，那属于**新建题集**，不是改判据。

**旁证（上一轮前提，本轮回读复算）**：`_repro/r322c/corpus_census.json` 实测 `user_msgs=1974`、`len_hist {>200: 1925, <=200: 49}` ⇒ 1925/1974 = **97.5%**，`short_single_line=0`。即真实语料是任务书形态、短单句 0 条，而这张尺最长 30 字符 ⇒ **拿任务书当 query 喂 exact judge，读数确实无意义**。前提成立。

---

## 自身偏差（本轮哪里可能不准）

1. **`87.5` 的口径被上一轮标错了对象**。任务书把 87.5 当「max_achievable」。实测：87.5 是 `blindset_leak_manifest.json:49` 的 `score_clean_only.pct`（干净面 106 条的**上限**），而全量面的 `max_achievable` 是 **95.2**（`blindset_gate_baseline.json:20`）。两者都是「上限」但**分母不同**（106 vs 291）。本报告把两者**分开写**，没有合并成一个数。
2. **`glob` 工具在中文路径上给了假阴性**：`glob(eval/**/*)` 返回 `n_paths=0`，但 `ls` 实测该目录存在、324 个条目。若我信 glob 就会误判「不可读」并触发退路。已改用 shell 列举，并把它记在这里 —— 这类假阴性足以让一次取证直接判错。
3. **任务书给的消费者路径不存在**：`焚诀/05-exec/r115_quality_truth.py` 实测 No such file；真身在同工作区另一项目 `自建skill优化/05-exec/r115_quality_truth.py`（已只读引用，未改）。**没有拿本项目侧来替代焚诀 eval 面** —— eval 面本身可读，退路未触发。
4. **未跑全量 291 条 `route()`**：判分口径取证不需要真跑（问 1-4 都是静态可证的），代价是问 5 只能给区间不能给点值。已具名缺什么，没有拿估算当实测。
5. **`scripts/ci_blind_eval.py` 在 eval/ 之外**（`焚诀/scripts/`）。我把它的 sha 守卫算进「全路径 3 文件」的依据，但**它本身不在改动清单里**（守卫不用改，只需要重签基线）。这点在 `min_change.full_path_detail` 里已写明。
6. **探针脚本留在写面内**（`_probe_schema.py` / `_probe_shape.py` / `_probe_ceiling.py` / `_probe_break.py` / `_gen_feasibility.py`）：blockers 的 evidence 逐条引它们的读数，删了就没法复跑。全部在 `_repro/r323b/` 白名单内，未越界。

## 一句话给下游

**多标签改法最小只动 1 个文件 1 行**（`eval/frozen_blind_eval.py:70`），但**上限不会变（仍是 95.2）**，变的是实测分；而**这把尺上没有任务书题面（最长 30 字符）**，所以「短句 → exact」换成「任务书 → 多标签」的真正成本不在判分器，在**新标注 291 条 acceptable 集 + 补任务书形态题面**。

