# 06 · 需求6 质量提升验证（≥30%）

> 任务 `t6`｜captain 接管（attempt=3，接手于 2026-11-07 09:22）｜原成员 `quality-verifier` 完成全部基线采集但未落主报告，连续两次重派未产出后由 captain 接管收口。
> 机器可读同源件：[data/06_r115_baseline.json](data/06_r115_baseline.json)、[data/06_gate_baseline.json](data/06_gate_baseline.json)；判据件：[06_quality_check.py](06_quality_check.py)。
> 结论标注：✅已实测 / ⚠️部分实测 / ❌未实测。

---

## 0. 结论摘要（先说结论）

**需求⑥「替换后任务完成质量提升不低于 30%」在本仓当前质量面上不可达标。**

这不是执行不力，是**算术边界**：以 r115 生产质量口径的 L1 面为例，基线 88.3 → 当前 90.7，实测相对提升 **2.7%**；而 30% 相对提升需要达到 **114.79 分**，可该面上限只有 **95.2 分**。缺口 19.59 分，任何改造都无法跨越。

裁决取 **(c) 如实证否**：逐面给出算术证明与最大可达值，需求⑥标 ⚠️不可达标。

| 面 | 基线 | 当前 | 上限 | 30% 所需 | 判定 |
|---|---|---|---|---|---|
| L1 layered（n=291） | 88.3 | 90.7 | **95.2** | **114.79** | ❌ 算术不可达（缺口 19.59） |
| L4 干净面（n=106） | 87.5 | 87.5 | **100.0** | **113.75** | ❌ 算术不可达（缺口 13.75） |
| L2 frozen（n=10） | 65.0 | 65.0 | 95.0 | 84.5 | ⚠️ 理论可达，但 n=10 功效不足不可证 |

- ✅已实测：`relative_gain_pct = 2.7`、`r1_threshold_met = false`、`baseline_ci95=[89.6,95.5]` 与 `current_ci95=[92.5,97.4]` **区间重叠** ⇒ 即便有提升也落在抽样抖动内（`r2_comparability = 区间重叠`）。
- ✅已实测：`ceiling_score = 95.2` / `need_score_relative_reading = 114.8`，存入 `_temp/t5_qi/2026Q4/req6_attainability.json`；巡检侧同报 `[REQ6:IMPOSSIBLE]`（`_temp/t5_qi/2026Q4/audit.error.json:156`）。两条独立取证互证。

---

## 1. 两条前置证据的显式回应（不可绕过）

### 1.1 T 差约 90% 是结构性假象，不得当作质量提升

t3 矩阵给出 T 总分：现有件 **31.87** / 候选 **76.11** / 差 **44.24**。若直接换算即「提升 139%」—— **这是量尺假象，本报告拒绝该结论**。

按维拆解（captain 复算 `data/matrix.csv` 2365 行）：

| 维度 | 现有件 | 候选 | 差距×权重 | 占 T 差 |
|---|---|---|---|---|
| eff 运行效率 | 0.09 | 3.56 | 13.87 | 31.3% |
| docs 文档完善 | 1.03 | 4.08 | 9.15 | 20.7% |
| fc 功能完整性 | 1.96 | 3.38 | 8.52 | 19.3% |
| community 社区 | 0.97 | 3.73 | 8.26 | 18.7% |
| compat 兼容性 | 3.43 | 4.54 | 4.43 | 10.0% |

根因（captain 现扫 146 个现有 skill 目录实测）：有根 `README.md` 仅 **4/146 = 2.7%**、有 `docs/` 仅 **2/146 = 1.4%**、有 `tests/` 仅 **10/146 = 6.8%**、有 `.github/workflows` 仅 **1/146 = 0.7%**、`SKILL.md` 件数 **144/146 只有 1 个**、本地目录无 GitHub stars 故 `community` 恒 1.0（方差 0）。

`score5` 的锚点是按 **GitHub 整仓**设计的（README/docs/tests/workflows/stars），现有件却是 **本地单件 skill 目录**。故前四维被结构性锁死 —— **这是形态差异，不是质量落后**。t3 §9 的 B1（bundle-scale 不对称）与 B6（community 通道不可比）已披露同一事实。

### 1.2 需求⑥的 30% 在 r115 质量面上算术不可达

见 §0 表格与 §2 逐面证明。

---

## 2. 逐面算术证明

### 2.1 L1 layered —— 主力面，不可达

```
baseline      = 88.3
need(+30%)    = 88.3 × 1.30 = 114.79
max_achievable= 95.2
114.79 > 95.2  =>  缺口 19.59 分，不可达
measured gain = 90.7 - 88.3 = 2.4pp = 2.72%
max possible gain from baseline = 95.2 - 88.3 = 6.9pp = 7.81%  < 30%
```

**关键**：即使把 L1 面做到**理论上限 95.2**，相对基线也只能得到 **7.81%** 提升，仍不到 30% 的 1/3。

### 2.2 L4 干净面 —— 不可达

```
baseline = 87.5，need(+30%) = 113.75，max = 100.0（百分比上限）
113.75 > 100  =>  缺口 13.75 分，不可达
```

### 2.3 L2 frozen —— 理论可达但不可证

```
baseline = 65.0，need(+30%) = 84.5，max = 95.0  =>  理论可达
但 n = 10，CI95 = [39.7, 89.2]，区间宽 49.5pp
目标提升 19.5pp < 噪声区间 49.5pp  =>  即便真提升也测不出（信噪比 < 1）
```

⚠️部分实测：L2 仅 10 条样本，`metric_note` 明写「仅作哨兵不作趋势」。**不得**用它宣称「某面可达 30%」。

### 2.4 反向检验（防口径作弊）

有人可能改用「剩余空间」当提升幅度：`95.2 / 90.7 - 1 = 4.96%`。**这仍是 4.96%，不是 30%**，且该算法本身错误（剩余空间占比 ≠ 相对基线提升）。两种算法都到不了 30%。

---

## 3. 兼容性验证（三面，均为「不劣化 / 不新增红」口径）

> 口径说明：本轮**未真实执行替换**（迁移方案列入 t4 阶段门 G0–G5，本轮不执行），故兼容性验证的是「**改造与取证过程未引入劣化**」，不是「替换后不劣化」。这个区别必须写明，否则读者会误以为替换已完成。

### 3.1 路由面：r115 三口径同口径对照

| 口径 | 值 | 说明 |
|---|---|---|
| L1 layered | 90.7%（278/291，CI95 [92.5, 97.4]，max 95.2） | 含泄漏题加成，引用须同屏给 L4 |
| L2 frozen | 65.0%（7/10，CI95 [39.7, 89.2]） | n=10 仅哨兵 |
| L4 干净面 | 87.5%（106 条，剔除泄漏 185 条） | 官方件自算 |
| L3 泄漏面 | 185/291 = 63.6%；轮换池 14/20 = 70.0% | 泄漏抬分 7.7pp |

⚠️ **禁混用**：r114 的 `hybrid_match` Top-1 38.2% 与 r115 的 `unified_router.route()` **不同源，禁相减、禁写「提升 N 倍」**（`data/06_r115_baseline.json` 的 `r114_correction.comparable = false`，按 R241 挂校正注）。

### 3.2 门禁面：起点 FAIL=8 / UNVERIFIED=3，未新增红

本次现跑（`data/06_gate_baseline.json`，`gates_run=118`，`generated_at=2026-11-07 08:19`）：`verdict=FAIL`，`real_red=10`，`design_inherent=1`，**FAIL=8 / UNVERIFIED=3**。

| 门 | 归因 |
|---|---|
| `gov_acceptance_face` | 既有：体量册末条超 3 天 + A6 VOL_LEDGER_STALE |
| `ratchet_gate` | 既有：注入面/度量棘轮 |
| `control_char_scan` | 既有：`_temp/r295a/meta_raw.json` 6 个 DEL 码位 |
| `refresh_budget_fixtures` | 既有：周期声明预算 |
| **`gate_run_freshness`** | **自循环设计红**：本轮跑出 verdict=FAIL ⇒ 台账记 FAIL ⇒ 本门读台账判红（`[FRESH:FAIL] 0.0 天前`）。`memory/AGENTS.md` 排障速查 row 7 已载明此形态，再跑一次自愈 |
| `fixture_wiring_face` | 既有：孤儿夹具增量 |
| `skill_wiring_face` | 既有：SKILL 侧无指针孤儿 |
| `turnstile_usage_face` | 既有：建面未进表 |

✅ **captain 独立归因结论：8 红无一条可归因于 t1–t7 任何一件。本轮未新增任何红门。**

> 历史差说明：t1/t2/t3/t5 早轮读到 FAIL=7 / UNVERIFIED=2，本轮为 8/3。差值是 `gate_run_freshness` 自循环 + `control_char_scan` 脏件在不同时点的读数漂移，**如实并列，不抹平**（R241）。

### 3.3 业务逻辑面：`dispatch_regress` 12 面，11 通过

来自 `_temp/t6_qv/dispatch_baseline.txt`：**11 通过 / 1 失败**。

| 判据面 | 结果 |
|---|---|
| gate-fixtures / gate-negative / plan-formula / doc-audit / doc-claims | 44/44、7/7、34/34、18/18、19/19 ✅ |
| inject-budget / doc-faces / wt-reconcile / goal-coverage / probe-pin / checklist-state | OK、8/8、W=4 T=180、20/20、6/6、36/36 ✅ |
| **`gate-main`** | ❌ rc=1 `GATE_FAIL C12_REGISTRY` |

**captain 归属实测**：`C12_REGISTRY` 是**焚诀仓** `eval/verify_truth_consistency.py:778` 的「workflow 任务卡字段 == gate TASK_CARD_HEADERS（R196）」判据，该文件 mtime = **2026-11-06 09:19**，早于本会话开工（2026-11-07 01:10）；本团队从未写入 `焚诀/eval/`。⇒ **既有状态，不归因 t1–t7、不否定兼容性结论。**

旁证：`_temp/t6_qv/dispatch_selftest_baseline.txt` = `REGRESS_GATE_OK 4/4` rc=0，判据机制本身健康。

### 3.4 保护件面

`04_protected_guard.py` → `[PROTGUARD:CLEAN]`（替换面 57 件无注册表保护件），负控 `[NEGCTRL:RED]`。✅

### 3.5 adversarial 分面的正确读法

`_temp/t6_qv/adversarial_baseline.txt` 的 `EXITCODE=1`，但分面结果不同：

| 分面 | 结果 | 读数 |
|---|---|---|
| `router_negative_labels` | ✅ pass | entries=20，min_required=15 |
| `edge_robustness` | ✅ pass | cases=10 |
| **`write_boundary`** | ❌ **fail** | scanned=254，baseline=29，matched=50，**new=11**，unmatched=1，hits_total=61 |

⚠️ **不得把「两个分面 fails=[]」外推成整体通过，也不得把 rc=1 外推成整体失败。** `all_pass=false` 的真因是 `write_boundary`。

**captain 归属实测**：`write_boundary` 点名的 11 个新增写点位于 `焚诀/eval/` 与 `焚诀/scripts/`，mtime 全部早于本会话开工：

| 文件 | mtime |
|---|---|
| `焚诀/eval/chain_red_days.py` | 2026-11-02 10:13 |
| `焚诀/eval/gov_archive_audit.py` | 2026-11-02 06:23 |
| `焚诀/eval/pre_commit_hooks.py` | 2026-11-06 17:15 |
| `焚诀/scripts/endpoint_deleg_cron.py` | 2026-11-02 20:58 |

⇒ 属焚诀仓库既有状态（R269 登记不擅动），**不归因 t1–t7、不否定兼容性**。

---

## 4. 裁决：三选一取 (c)

| 选项 | 内容 | 本报告裁决 |
|---|---|---|
| (a) 换面 | 另找基线离饱和足够远的同尺可测面 | ❌ 已穷尽 L1/L2/L4 三面，无一满足（见 §2） |
| (b) 分面加权 | 多面加权凑出可达 30% | ❌ 三面中两面算术不可达、一面不可证，加权无法造出可达性 |
| **(c) 如实证否** | 输出各面最大可达值 + 算术证明，标 ⚠️不可达标 | ✅ **本报告裁决** |

**最大可达提升（相对基线）**：L1 面 **7.81%**（做到上限 95.2 时）；L4 面 **14.29%**（做到 100 时）；L2 面理论 46.15% 但 n=10 不可证。
**结论：需求⑥ 在本仓当前质量口径下最大可达约 7.81%（L1 主力面），达不到 30%。**

---

## 5. 可复跑判据

### 5.1 判据件：`06_quality_check.py`

三态退出码：`0` PASS / `1` FAIL 或 IMPOSSIBLE / `2` UNVERIFIED。

三腿设计：
- **R1 阈值腿**：`baseline × 1.30 <= max_achievable`？否 ⇒ 判 `IMPOSSIBLE` 并显式点名该面，**禁静默通过**；
- **R2 歧义腿**：`baseline_ci95` 与 `current_ci95` 是否重叠？重叠 ⇒ 提升落在抖动内，不得宣称提升；
- **R3 实测腿**：读 `relative_gain_pct` 与 `r1_threshold_met` 佐证。

### 5.2 正常态（期望末行）

```
python -B deliverables/skill-modernization-r1/06_quality_check.py   (workdir=自建skill优化)
```
✅已实测输出：
```
  L1_layered   base=88.3   cur=90.7   max=95.2   need30=114.79   n=291   => IMPOSSIBLE
  L2_frozen    base=65.0   cur=65.0   max=95.0   need30=84.5     n=10    => EVALUATED
  L4_clean     base=87.5   cur=87.5   max=100.0  need30=113.75   n=106   => IMPOSSIBLE
  relative_gain_pct = 2.7 (threshold 30.0%)
  r1_threshold_met   = False
  ci_overlap         = True (区间重叠(幅度落在抽样抖动内))
[QUALITY:IMPOSSIBLE] 需求6 未达标，且以下面算术不可达: ['L1_layered', 'L4_clean'] ｜ 相对提升 2.7% < 30% ｜ CI 重叠=True
```
**退出码 1 是正确结果**（需求未达标如实报），不是判据故障。

### 5.3 负控（证明判据有牙）

```
python -B deliverables/skill-modernization-r1/06_quality_check.py --negative-control
```
✅已实测输出：`[NEGCTRL:RED] 上限被人为抬高后 L1 被误判为「可达」，实测 gain=2.7% 远不足 30% => 判据检出矛盾`

负控机理：把 `max_achievable` 人为放大 2 倍，R1 腿会误判「可达」，此时判据**必须**因实测 gain 不足而转红；若仍绿则判据无牙。

---

## 6. 盲区与不可外推面

| 盲区 | 状态 | 影响 |
|---|---|---|
| 本轮**未真实执行替换** | ✅已实测（t4 定稿为阶段门计划，G0–G5 未进） | 兼容性结论 = 「未引入劣化」，≠「替换后不劣化」 |
| L2 面 n=10 | ⚠️部分实测 | 信噪比 < 1，不得据此宣称任何提升 |
| r114 38.2% 与 r115 不同源 | ✅已实测（`comparable=false`） | 禁相减、禁写「提升 N 倍」 |
| 三项不被 run_gates 覆盖 | ✅已实测（`not_covered`） | 受管根四门禁 / 焚诀 C1~C33 / 变异测试，需另行取值 |
| 替换后真实 A/B | ❌未实测 | 需在 t4 阶段门 G2 试点后重跑本判据 |

---

## 7. 后续（替换真实执行后的复验路径）

当 t4 阶段门 G2 试点（P0 五件）真实执行后，按下列命令复验需求⑥：

```
# 1) 重新采集 r115 基线（替换后）
python 05-exec/r115_quality_truth.py --json deliverables/skill-modernization-r1/data/06_r115_post.json
# 2) 与本次基线比对（把 --r115 指向新件）
python -B deliverables/skill-modernization-r1/06_quality_check.py --r115 deliverables/skill-modernization-r1/data/06_r115_post.json
# 3) 复跑门禁，确认未新增红
python 05-exec/run_gates.py --json deliverables/skill-modernization-r1/data/06_gate_post.json
```

**判据不变**：仍要求 30% 相对提升；若届时仍不可达，本报告的算术证明即为长期依据。

---

## 8. 纪律声明

- 只读取证：未改 `D:/global_skills` 下任何 `SKILL.md`/源文件；未改焚诀 `eval/`。
- R241：历史报告旧数字只加校正注，未改写。
- 门禁如实记红（FAIL=8 / UNVERIFIED=3），未删 tracked 件凑绿（R263 / X-9）。
- 需求⑥**未达标**，本报告如实标注 ⚠️不可达标，**未写「已提升 30%」**（#36 禁假完成）。
