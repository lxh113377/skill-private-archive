# 全量对标报告 r120 — 第 8 类失败层发现：L0 域过滤的 latent exposure（21.9% 题面域失配，仅 1 条真失败）

> 触发：自动化指令 goal round（同一目标继续执行，round 5/256）。上一轮 r119 于 2026-10-20 08:2x 收尾。
> 本轮定位：r119b §10 R119b-1 指名「prompt-consolidation 是唯一剩余 BGE_RECALL 层 miss，值得换更强前置形态再试」——本轮试了，**无效**，但顺着无效挖出了更根本的一层。
> 取值纪律：每个数字在 ±12 行内带可复算命令；历史结论按 R241 只加注不改写。

## 0. 本轮决定与排序依据

| 项 | 内容 |
|---|---|
| 起点 | R119b-1：对 prompt-consolidation 做「前置鉴别词」改造（r119b 已证「位置 > 存在」） |
| 转折 | 三组前置候选（含负向边界）沙箱**全部 0 翻转** ⇒ 说明该条 miss 的根因不在语料，遂转向归因 |
| 主结果 | 挖出 **r118 层归因未覆盖的第 8 类失败层：L0 域过滤**（domain filter latent exposure） |
| 附带 | 首次分析 `eval/route_trace.jsonl` 生产流量面（23,630 条 / 15 天）——证明生产题面本身健康，缺口全在合成题面 |

## 1. 起点：三组前置候选全部无效（先证后改，禁无证据改受管根）

对 `prompt-consolidation` 构造三组候选，用 `05-exec/r120_corpus_probe.py`（本轮新建，见 §5）逐一沙箱：

| 候选 | 形态 | 结果 |
|---|---|---|
| B_前置加负向边界 | 「提示词清理、清理提示词里堆积的补丁…」前置 + 「不适用：清理C盘（走 sq-cleanmgr-c）」 | flips=0 improved=0 |
| （另两组同族） | 前置动作词 / 极简前置 | 均 0 翻转 |

> 取值：`_temp/r120_probe_B.json`；诊断 `_temp/r120_diag.py`（BASE / ORACLE / CANDB 三种语料下**分数完全相同** 0.565 ⇒ 语料替换对该题根本不生效）

## 2. 主结果：根因是 L0 域过滤，不是语料

### 2.1 诊断链（每一步都有反事实）

| 步骤 | 实测 | 结论 |
|---|---|---|
| ① 该题是否被 direct_route 短路 | `direct=False`，`tag_hits=None` | 否 ⇒ 走 BGE 召回 |
| ② query 分类域 | `classify_domain('帮我清理提示词里堆积的补丁') = code` | — |
| ③ 期望件注册域 | `prompt-consolidation.domain = system` | 域不一致 |
| ④ 为何判 code | `DOMAIN_KEYWORDS.code` 含「清理」命中；`system` 表只有英文 `prompt`，**中文「提示词」不在 system 表**（它在 creative 表） | 中英混合盲区 |
| ⑤ 反事实：该件 domain 对齐 query 域 | top1 `sq-cleanmgr-c(0.565)` → `prompt-consolidation(0.694)` | **FLIP，且大幅反超** |

> 取值：`_temp/r120_diag.py` / `_temp/r120_domain_cf.py`；⑤ 的机制解释：`bge_recall` 在 `tag_hits` 为空且 `domain` 非 None 时，`indices = [i for i,s in enumerate(_bge_skills) if s['domain']==domain]` —— 只搜 code 域，`system` 域的 prompt-consolidation **结构上不在搜索范围**。

### 2.2 全局量化：这不是个例，是 21.9% 的题面

| 指标 | 实测 |
|---|---|
| layered 269 题（expected 非空）中域失配（query 域 != 期望件域） | **59 题（21.9%）** |
| 其中 qdomain=None（未触发域过滤） | 73 题不计入 |
| 域失配题中**有 tag/direct 掩护** | 55 题（期望件仍在候选且 top1 命中） |
| 域失配题中**真实暴露**于域过滤 | **4 题** |
| 暴露题中靠语料质量仍命中 | 3 题（pixelle-api-ensure / data-visualization / brainstorming） |
| 暴露题中真失败 | **1 题**（prompt-consolidation） |

> 取值：`06-benchmark/domain_mismatch_r120_2026-10-20.json`（59 题全量）；`06-benchmark/domain_exposure_r120_2026-10-20.json`（暴露/掩护二分 + 逐条）
> **4 道暴露题逐条**：`帮我检测并启动本地 Pixelle 视频服务`（exp=pixelle-api-ensure, qdom=local, **hit**）/ `帮我清理提示词里堆积的补丁`（exp=prompt-consolidation, qdom=code, **MISS**）/ `python 画 matplotlib 交互图`（exp=data-visualization, qdom=code, **hit**）/ `头脑风暴`（exp=brainstorming, qdom=general_utils, **hit**）

### 2.3 关键判别：域过滤是**有益的兜底**，不能关

| 反事实 | 结果 |
|---|---|
| 全局关掉域过滤（`classify_domain → None`） | 94.41% → **92.92%**（−1.49pp），WIN 1 / LOSE 5 |
| 只修 prompt-consolidation 的域归属 | +1 题翻转（0.565→0.694） |

> 取值：`_temp/r120_domain_global.py`（全 layered 跑两遍，269 题）
> ⇒ 域过滤的失效模式是**脆弱（fragile）而非有害（harmful）**：它偶尔排除正确件，但更多时候在挡住噪声件。**结论不是「关掉它」而是「修域归属」**。

## 3. 附带发现：生产流量面首次分析（证明缺口在合成题面，不在真实使用）

| 指标 | 实测 |
|---|---|
| `eval/route_trace.jsonl` 总行数 | 23,630（15 天，2026-10-05 → 10-20） |
| production 来源 | 11,032 条 |
| 去测试串后唯一真实 query | **332 个** |
| 其中 LOW 置信 | 3 个（提示词矛盾规则查一遍 / 内部公告模板 / 体量治理删模型权重） |
| 其中 MEDIUM 置信（真实歧义） | 7 个，且 4 个是合成验证串（`zzd+` / `健康态问句 r108` / `全新验证甲`） |
| 噪声串占比 | LOW 111 个里 108 个是 `^轮\d+` / `^另一个全新问句` / `唯一串` 形态 |

> 取值：本节全部由 `eval/route_trace.jsonl` 现算（解析 23,630 行 JSON，3 行坏行跳过）
> **结论**：生产题面很干净（332 个唯一 query，仅 3 个 LOW）⇒ **路由缺口集中在合成评测题面，不在真实使用**。这与 r118/r119 全链改进合成题面的方向一致，但也提示：真实用户体验已接近饱和，继续投入的边际收益在合成面。

## 4. 需求 6 判定（未达，且给出新的上界估计）

| 条件 | 状态 |
|---|---|
| R1 相对提升 ≥30% | ❌ 2.0%（r119 已产 +1.8pp） |
| R2 区间分离 | ⚠️ 仍未跑 Wilson（R119b-4 待办） |
| R3 反指标不退化 | ✅ 36 门 / 账实 / 镜像（见 §7） |

**新的上界估计**：本轮证明剩余 7 条 REAL_MISS 的可行修复面 = **1 条**（prompt-consolidation，且需改注册表域归属，属焚诀侧）。即使修成，L1 = 90.1% → 90.5%（+0.4pp，相对 +0.4%）。⇒ **需求 6 的 30% 在本仓可改面内已无可达成路径**，唯一剩余动作在归属方（eval/ + 注册表）。

## 5. 新建工具（R119b-2 落地）

| 件 | 作用 | 与既有件的关系 |
|---|---|---|
| `05-exec/r120_corpus_probe.py` | 语料改造「先证后改」**参数化**判定器：`--slug/--query/--body`，输出 improved/worsened/cross 三数 + **双向控制组**（负控 wins 必须 0 / 正控 flips≥1） | 取代 `r119_verify_landed.py`（硬编码 chaoshi-web-deploy，一次性）；与 `r119_corpus_gate.py`（多候选批量对比）分工 |

> 取值：`python 05-exec/r120_corpus_probe.py --slug prompt-consolidation --query "..." --body <文件>`
> ⚠️ **控制组不成立时禁引用结论**（本件显式判 `UNSAFE(控制组不成立，禁引用)`）：本轮首跑正控 0 flip（因目标题不在 `questions` 的 expected 集导致子集构造缺陷），已修——目标题强制进子集。

## 6. 逐项验证台账

| # | 结论 | 复算命令 | 本轮实测 |
|---|---|---|---|
| V1 | 三组前置候选无效 | `_temp/r120_probe_B.json` / `_temp/r120_diag.py` | BASE/ORACLE/CANDB 分数均 0.565，0 flip |
| V2 | 根因是域过滤 | `_temp/r120_diag.py` | `domain=code` `tag_hits=None` `direct=False`，期望件不在候选 |
| V3 | 域归属反事实可翻转 | `_temp/r120_domain_cf.py` | domain 对齐后 top1 0.565→0.694 FLIP |
| V4 | 域失配 59/269 | `06-benchmark/domain_mismatch_r120_2026-10-20.json` | 21.9% |
| V5 | 仅 4 题暴露 / 1 题真失败 | `06-benchmark/domain_exposure_r120_2026-10-20.json` | 55 掩护 / 4 暴露 / 1 MISS |
| V6 | 域过滤净有益（禁关） | `_temp/r120_domain_global.py` | 94.41%→92.92%，WIN 1 / LOSE 5 |
| V7 | 生产题面健康 | `eval/route_trace.jsonl` 现算 | 332 唯一 query / LOW 3 |
| V8 | 新工具可用 | `05-exec/r120_corpus_probe.py` | 三数组 + 双向控制组 |
| V9 | 转办提案第 8 条在册 | `python 05-exec/r119_transmit_shortcircuit.py` | 提案总数 8 |

## 7. 本轮自抓

1. **「语料无效」被误读成「候选不够强」**：三组候选 0 翻转后，第一反应是「再想更强的词」。实际用 oracle（query 自身编码）对照才发现**语料替换根本不参与该题打分**——同一个 0 flip，「语料不好」和「语料没被读」是两回事，只有对照实验能分。
2. **JS 模板字符串里的 PowerShell 转义**：`$env:TEMP\p...` 被当八进制转义、`` 触发 strict mode 报错，连败 3 次。正解 = 用 `String.fromCharCode(13)` 拼行 + PowerShell 单引号字符串。
3. **dag_precheck 落点竞争**：首轮写 `2026-10-20.part2.md` 后判据扫不到（并行会话正在重写该文件，race）。改投 `part3.md` 立即 `[GATE:dag-pass]`。教训：G8 块要写进**竞争较少**的分卷，写完立即复跑。

## 8. 需求 1-7 逐条达标度

| 需求 | 交付 | 达标度 |
|---|---|---|
| 1 全面盘点 | 182 件四列（r115）+ 本轮首次分析生产流量面（route_trace 23,630 条 / 332 唯一真实 query） | **达标（本轮补真实使用反馈面）** |
| 2 每件 3-5 替代 | 182/182（r114 矩阵） | 达标 |
| 3 五维评分 | 25 分制可复算（r114） | 达标（eff/community 为代理量） |
| 4 迁移方案 | r114 + r118 W-1 + r119 §9 + r119b 第 37 门 | 达标 |
| 5 季度巡检 | 9 步（r119b 扩） | 达标 |
| 6 质量提升 ≥30% | ❌ 2.0%；且本轮证明**可行修复面仅剩 1 条**，上界 ~90.5% | ⚠️ **未达（已证上界）** |
| 7 四类文档 | 本报告 + 3 个域分析 JSON + 1 个新工具 + 提案第 8 条 | 达标 |
> 取值（§8 全表 182 / 30% / 2.0% / 1 条 / 90.5% / 3 个 / 1 个 / 8 条）：182 = 注册表实读（同 r119b §8）；30% 是用户指令原文阈值（r114 §3 C1 固定）；2.0% = 1.8/88.3（分子分母取值 `python 05-exec/r115_quality_truth.py` 的 L1 与 r119 报告 §3.1）；「1 条」= 剩余 7 条 REAL_MISS 中域过滤可修的件数，取值 `06-benchmark/domain_exposure_r120_2026-10-20.json` 的 `exposed_n`(4) 与 `rows[].is_miss`(1)；90.5% = (276+1)/291 的推算上界（非实测，已注明「上界估计」）；「3 个域分析 JSON」= `ls 06-benchmark/domain_*_r120_2026-10-20.json`；「1 个新工具」= `ls 05-exec/r120_corpus_probe.py`；「8 条」= `python 05-exec/r119_transmit_shortcircuit.py` 的读回行。

### 8.1 本轮未达面（禁读成已闭环）

| 面 | 状态 | 追踪 |
|---|---|---|
| 需求 6「≥30%」 | 未达；本仓可改面上界已证 ~90.5% | R114-2 |
| prompt-consolidation 的域归属 | 已定位（注册表 domain=system 应为 creative，或 DOMAIN_KEYWORDS.system 补中文「提示词」），**未修**（焚诀侧红线） | 提案第 8 条 |
| Wilson 区间 | 仍未跑（R2 判定缺一半） | R119b-4 |
| 3 条暴露题（pixelle-api-ensure 等） | 已具名，靠语料命中，未加固 | 本轮新登记 |
> 取值（§8.1 全表 30% / 90.5% / 8 条 / 3 条）：30% 与 90.5% 同 §8 注；8 条同 §8 注；「3 条暴露题」= `06-benchmark/domain_exposure_r120_2026-10-20.json` 的 `exposed[]` 中 `is_miss=false` 的行（pixelle-api-ensure / data-visualization / brainstorming，共 3 行）。

## 9. 改进建议清单

| # | 建议 | 优先级 | 依据 | 状态 |
|---|---|---|---|---|
| R120-1 | 把「域失配面」纳入季度巡检常驻段（现为一次性脚本） | 中 | 21.9% 是结构性面，会随注册表增删漂移 | ⏳ 下轮 |
| R120-2 | `domain_exposure` 二分判据（掩护/暴露）常驻 | 中 | 区分「潜在脆弱」与「真实伤害」，防下轮又拿 21.9% 当缺口数 | ⏳ 下轮 |
| R120-3 | 3 条暴露题做语料加固（防域表一改就翻车） | 低 | 现靠语料命中，属运气非设计 | ⏳ 下轮 |
| R120-4 | route_trace 生产面纳入巡检（真实 query 分布 / LOW 置信集） | 中 | 本轮首次用它即证明「缺口在合成面不在真实面」 | ⏳ 下轮 |

## 10. 对比总览表（八维，本轮实测）

| 维度 | 我方 | anthropics/skills | obra/superpowers | addyosmani/agent-skills | github/spec-kit |
|---|---|---|---|---|---|
| ① 功能覆盖 | 182 在册 | 20 | 15 | 25 | 2 |
| ② 技术架构 | 三供给根 + 37 常驻门 + **8 类失败层归因**（r120 新增域过滤类） | 单树 | 单树 + tests | 单树 + 1 wf | 30 wf + CLI |
| ③ 可跑验证腿 | docx 17 / xlsx 3 / pdf 4 + provenance 23 + 沙箱 47 变体 + **域分析 3 件** + 生产 trace 23,630 条 | 1 | 87 tests | 2 | 390 tests |
| ④ 性能 | 37 门 PASS | 无门禁 | CI | CI | CI 30 wf |
| ⑤ 可扩展性 | references 分卷 + 准入三闸 + C20 棘轮 + 季度 9 步 | 目录约定 | 目录 + plugin | 目录约定 | 模板 + 文档 |
| ⑥ 维护状态 | 上游 11 件已分类；我方 0 issue（私有仓） | 181,836★ / 1,426 open | 301,336★ / 378 open | 107,938★ / 133 open | 141,709★ / 187 open |
| ⑦ 文档完善 | 根 1 件 CONTRIBUTING + 每轮报告 | 2 | 5 | 4 | 12 |
| ⑧ 适用场景 | AIPC/Win 深绑定 + 九端 | 平台中立 | 平台中立 | 平台中立 | 工具中立 |

> 取值（① 行 182 / ⑥ 行星标）：同 r119b §8（`gh api repos/<R>` + 注册表实读）；② 行「8 类失败层」= r118 四层（DIRECT_SHORT/DIRECT_NONE/TAG_SHORT/BGE_RECALL）+ 本轮新增 L0 域过滤 + STALE_EXPECT + UNREGISTERED + 语料位置敏感（r119b）。
