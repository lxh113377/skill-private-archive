# r316b G2 — gstack 配对血缘证据包（已知答案堂先行）

> 轮次：r316 派发 · 现取时刻 2026-10-31T19:3x+08（gh api 实时）· 写面仅 `自建skill优化/_temp/r316b/`
> 受管根 / 焚诀 / `_repro` 全程只读，本件**未写 .upstream**。

## 0. 本件建议是否够格进裁定 —— 声明（先答这个）

**够格。** r315 立的纪律是「过不了已知正确答案就不配当证据」。本件的已知答案堂两极**都过**，且两条负控**都绿**：

| 堂 | 样本 | 必须判 | 实判 | 过 |
|---|---|---|---|---|
| 正例 | `D:/global_skills/docx/SKILL.md` ↔ `anthropics/skills:skills/docx/SKILL.md` | 同族=配对成立 | **same-family**（三门全过，语义均值 0.7857，弃权 0 维） | ✅ |
| 反例 | `D:/global_skills/gstack/SKILL.md` ↔ 声明件 `garrytan/gstack:capy/skill/gstack/SKILL.md` | 异族 | **diff-family**（异族信号 5 亮 4） | ✅ |

负控（内嵌 `--selftest`，逐字见 §5）：腿A 转判异族 ✅ / 腿B 转判 unclear ✅ ⇒ 指标不是恒绿。
⇒ `lineage.json.verdict_suggestion_allowed = true`，本件**可以**产出裁定建议（建议正文 = §4）。

## 1. 指标设计（签名级；整行重合率禁用）

**为什么禁用整行重合率**（r315 实测已证不可分）：正例 docx 本地 862 行是上游 92 行的超集 fork，行重合率只给 **0.0678** ——
一个公认配对正确的样本被行重合率读成错配；而样板话（preamble / 围栏注释）能把真正错配的两件抬上去。
一个数分不开「增扩超集」与「异族错配」，所以本件不再用任何形式的行/文本重合比。

本件只比**签名**，且所有集合比对一律用**最小集包含率** `containment = |A∩B| / min(|A|,|B|)`：
直系上游在下游被改写放大 ⇒ 小签名必须被大文件复现；反过来扩写不会稀释它。这是唯一对「超集」免疫的方向。

维（`lineage.json.metric_design`）：
- `D1 fm_name` frontmatter `name` **逐字**等（同一性，不是相似度）
- `D2 family` 功能族分布（dominant 族 + 余弦）：word_document / pdf_documents / data_tables / browser_qa / host_protocol / cohort_runtime / engineering_workflow / media_visual，**计数**而非集合（1 个杂词不许与 owning 族打平）
- `D3 h1_topic` 首个真 H1 的词集包含率（围栏内 `#` 是 shell 注释，先滤 —— 与 r314b 同纪律）
- `D4 purpose_verbs` 用途动词（描述 + 章节标题，51 词域无关表）
- `D5 trigger_face` 触发词面（frontmatter triggers / allowed-tools / 描述；12 条触发短语）
- `D6 tool_command_face` 工具命令面（inline-code 与 CLI 里的 31 个工具名）
- `S1 gen_parity` **生成标记同侧**：本地 gstack 与 `browse/SKILL.md`、根 `SKILL.md` 都带 `AUTO-GENERATED from SKILL.md.tmpl` + `do not edit directly` + `regenerate:`，capy 件三件全不带
- `S2 heading` 章节标题集包含率（佐证，≥0.40 记一票）
- `S3 code` inline-code / CLI token 集包含率（佐证，≥0.40 记一票；floor 5/3）
- `S4 length_ratio` 只报告、**永不参与门禁**（r315 教训：长度差是超集的必然，不是异族的证据）

硬门（**先声明后跑数，跑完没回调过任何阈值**）：
- `G1 同一性` = (D1 逐字等 ∨ 本地件自述「上游同步」点名该候选的特征目录段) ∧ D2 dominant 族同 ∧ (D3∨D4∨D6 至少一个 ≥0.50)
- `G2 语义` = 可用语义维 [D4,D5,D6] 均值 ≥ 0.50（多数复现）
- `G3 结构` = S1 ∨ S2≥0.40 ∨ S3≥0.40 ∨ D2 余弦 ≥0.70
- 弃权：`min(|A|,|B|) < 3` 才弃权（D3 用 2、S3 用 5）
- **不对称律**（本件的关键设计，写死在 docstring 里）：弃权只能**挡正面主张**（缺证据不是证据），
  判 `diff-family` 必须靠**异族信号** ≥3/5：P1 同一性缺席 / P2 dominant 族不同 / P3 章节包含 ≤0.15 且两侧各 ≥5 节 / P4 命令面包含 ≤0.15 且两侧各 ≥10 token / P5 生成标记只在一侧。
  裁决：异族信号≥3 ⇒ diff-family；否则（弃权≤1 ∧ 三门全过）⇒ same-family；否则 ⇒ unclear。

设计期修掉的三个自身缺陷（都记在 `lineage.json.metric_design.design_iterations`，都不是调阈值）：
1. run-1 `containment` 把「交集<2」也当弃权 ⇒ 厚对厚零重合被吞成「无证据」，diff-family **永远读不出来**（地板恒 unclear）。
2. run-1/3 `identity_tokens` 把 `kind:repo:path` 整个标签按 `/` 切 ⇒ 仓主 `anthropics` 成了特征段，docx↔pdf 靠同仓主拿到同一性，**腿A 被悄悄削弱**；改为只取 path 段并排除仓主/`SKILL.md`/泛目录/本地自身 slug。
3. run-2 `TRIG_ONLY` 混进 `session start` / `run first` / `before any`（宿主生命周期语，不是技能触发语）⇒ 准入协议与文档技能因错原因「触发面相符」；删词只会**降**分，不可能靠它重新过堂，且删词是在堂判已记录之后做的。

## 2. 已知答案堂读数（可指认）

```
COURT+ docx<->anthropic/docx  verdict=same-family sem=0.7857  abstain=0 gates=3/3 | h1=0.25 dom=True pur=0.8571 trg=1.0 tool=0.5 head=0.1667 code=0.3673 cos=0.9867
COURT- gstack<->capy          verdict=diff-family sem=0.6     abstain=2 gates=2/3 | h1=0.0 dom=False pur=0.6 trg=None tool=None head=0.0 code=0.0719 cos=0.7361
```

正例之所以过（关键在它对超集免疫）：D1 `docx==docx`；D2 双侧 dominant 同族 word_document（18 / 16 命中，余弦 0.9867）；
D4 0.8571、D5 **1.0**、D6 0.5 ⇒ 语义均值 0.7857；长度比只有 **0.1067**（862 行 vs 92 行）却完全不影响裁决 —— 这正是行重合率会判死的那一型。

反例之所以过（异族信号 4/5，逐条可指认）：
- P2 族不同：本地 `browser_qa`(19) vs capy `engineering_workflow`(10)，余弦 0.7361；
- P3 章节零共享：37 节 vs 10 节标题集包含 **0.0**；
- P4 命令面近乎零：160 vs 153 个 inline-code/CLI token，包含 **0.0719**（交集 11 个，全是 `bash`/`gstack` 一类杂词）；
- P5 生成标记劈开：本地三条 AUTO-GENERATED 标记齐，capy 件**一条都没有**；
- P1 未亮（唯一一条不亮的）：D1 `name: gstack` 与 `name: gstack` 逐字等 ⇒ **同名不同族**，正是 path_rule 配错的典型形态。

## 3. gstack 三方案对照（各 ≥2 支持 / ≥2 反对）

指标对三个候选靶的裁语（同一套门与阈值，未逐件调）：
```
维持 capy   : verdict=diff-family   disproof 4/5  gates 2/3  sem=0.6    cos=0.7361  gen_parity=False
改配 browse : verdict=unclear       disproof 1/5  gates 3/3  sem=0.8    cos=0.9449  gen_parity=True  （D5/D6 两维弃权）
对照 根 SKILL.md: verdict=unclear   disproof 0/5  gates 1/3  sem=None   cos=0.9164  abstain=3
```

### 方案 A 维持 `path: capy/skill/gstack`
- 支持：A1 仓面没错 —— `garrytan/gstack` 确是本地件的来源仓，受管侧 §上游同步状态（SKILL.md:63-67）自己也写「上游 browse 已重构 v2.0.0（garrytan/gstack）」，动第一行没意义；A2 frontmatter `name` 与路径末段都与本地同名（D1 逐字等，P1 不亮）；A3 改动要写**受管根**并作废 r303a 该对的 `upstream_file_sha=11bd23cc` 与 `upstream_commit_sha=b6174451`，成本非零、要走 landing 五腿。
- 反对：A1′ 指标判 **diff-family**（5 项异族信号亮 4）；A2′ 本地 644 行里 `capy` 出现 **0** 次、`browse` 出现 **27** 次，受管侧的自述与吸收卷都指向 browse 族（`gstack/references/browse-v2-upstream.md` 标题逐字「受控吸收 garrytan/gstack/browse」）；A3′ capy 件在动 —— 2026-10-31 一天内 5 个 commit 改它（6748d54f 00:42 → 71af16c6 11:01，v1.91.343→362），维持即意味着每季都收一条**功能族错位**的 UPSTREAM_CHANGED（本季 r314b 那条唯一候选就是这么来的）；A4′ 与 r314b 结论一致：两侧功能异质，「吸收」等于把整件换成功能族。

### 方案 B 改配 `path: browse`
- 支持：B1 双侧 dominant 族同为 `browser_qa`，余弦 **0.9449**；B2 生成标记**同侧全等**（三条 AUTO-GENERATED/`do not edit directly`/`regenerate:` 都在，且上游树里确有 `browse/SKILL.md.tmpl` blob `0655b388`、本地件自述就是从这个生成器出来的）；B3 语义维 **0.8 全案最高**（D4 purpose 0.8），长度比 0.93（470 行 vs 644 行）与「本地为超集改写」形态吻合；B4 受管侧自述点名 browse v2.0.0，而 `browse/SKILL.md` frontmatter 正是 `version: 2.0.0`；B5 browse 侧节奏稳定（最近 415e343b 2026-10-28，此前 10-26 / 10-19），钉得住；B6 52 对里 browse 字样 0 撞靶（唯一含 browser 的是 `agent-browser`→vercel-labs，不同仓）。
- 反对：B1′ **指标只给 unclear，不给 same-family** —— 五个被检维里 D5 触发面（browse 侧命中 0：它的 `triggers:` 是 `browse a page` 这类短语，不在触发短语表内）与 D6 工具面（browse 侧 0）双双弃权；按本件自己的纪律，弃权≥2 时**不许**判同族，所以「改配 browse」不是指标直接背书的结论；B2′ D1 会断（`gstack` vs `browse`），改完 .upstream 的同一性只剩「受管侧自述点名」一条通道；B3′ `.upstream` 是**目录级**声明：把受管目录 `gstack/` 指向上游 `browse/SKILL.md`，等于把「族错位」换成「名错位」，r264 的 SAME_LINEAGE 分类仍错；B4′ 本地件实为套件混合体（development workflow 建议 + 上游同步状态节 + browse QA 手册），**没有任何单一上游件等于它**，根 `SKILL.md`（router，278 行）也只读到 unclear（abstain=3、gates 1/3）。

### 方案 C 保持冻结，待上游稳定
- 支持：C1 上游确在高频动 —— 同一件 24h 内 5 commit、版本每几小时一跳，现在重钉 pin 当季即过期（r314b UNK-01 已记三 commit 并存漂移）；C2 冻结零写入、零回滚成本，且漂移链已当场复算钉死：capy 件 `11bd23cc`(17898B，季档 pin，本次按 ref=b6174451 现拉复算 sha1 对上) → `8ef728bd`(21608B，r314b) → `6bbb4e0c`(21622B，本次现拉)——同一个被声明靶 24h 内两度换 blob；C3 三案里**唯一被指标确定**的结论只有「按 capy 吸收不成立」，冻结不越过指标能背书的那一步。
- 反对：C1′ 冻结不停产噪声 —— 每季仍交一条异族 UPSTREAM_CHANGED 候选（本季就是它）；C2′ 与 r264 的机器闸语义冲突：明知异族仍留 declared 靶，把它从「未知错配」变成**已知错配**，比留白更糟；C3′ 受管侧已经自己做过 browse 族吸收（带 SHA 锚点的侧卷），说明真正缺的是**靶的归类**，冻结不解决吸收面。

## 4. 裁定建议（够格进裁定的那一版）

1. **配错成立**：`D:/global_skills/gstack/.upstream` 第 2 行 `path: capy/skill/gstack` 与本地受管根件**异族**（diff-family，4/5 异族信号，含「章节零共享 + 命令面 0.07 + 生成标记劈开」三条硬证据）。
2. **先落归类，后落 path**：本季在季档/台账把 gstack 记 `declared_state=NOT_SAME_LINEAGE`（禁按 BEHIND 读版本面，r264 R263-3 口径），并把 capy 侧漂**从吸收候选面摘出**——这一步不改受管根、不作废任何 pin。
3. **不建议本轮就把 path 写成 browse**：指标对 browse 只到 unclear（两维弃权）。补证办法（下一步取证，不需调阈值）： browse 侧触发面/工具面之所以 0 命中是**词表覆盖**问题，可用两侧 `triggers:`/`allowed-tools:` 全文交叉与 `$B` 命令面逐条对账补成可计维；补强后若升 same-family ⇒ 改 `path: browse`；若仍 unclear ⇒ 把 gstack 声明改为**合成件**（多源派生、无单一上游件），这恰好是数据支持的第三种答案（本地=套件混合体）。
4. 任何 path 改写**必须**同一次重建该对 pin（`11bd23cc→新靶 blob`），否则 `compare_baseline` 会把改写本身读成 UPSTREAM_CHANGED。

## 5. 判据与负控（逐字）

```
C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe -B 自建skill优化/_temp/r316b/check_r316b.py --selftest
```
期望末行（逐字）：
```
[R316G2:LINEAGE] known-pass=true gstack_pairing=diff-family browse-alternative=unclear
```
负控两腿（同一次 `--selftest` 内嵌，逐字抄自任务书）：
- 腿A：把 docx 对照件换成 anthropics 仓里另一个不同功能件（如 pdf）⇒ 指标必须转判异族（证明它真在量语义不是恒绿）
  实测：`NEG-A docx-vs-pdf  : verdict=diff-family expect=diff-family PASS`（异族信号 P1+P2+P3 亮，族 `word_document` vs `pdf_documents`）
- 腿B：签名词表清空 ⇒ 必须判 unclear 而非 same-family
  实测：`NEG-B cleared-vocab: verdict=unclear     expect=unclear       PASS`（5 维全弃权，D2 余弦 0、dominant 两侧皆 null）

## 6. 影响面（改 .upstream 谁受影响）

声明件本体：`D:/global_skills/gstack/.upstream`（2 行 40B，sha256 `d728928e5eb8…`）= `garrytan/gstack` + `path: capy/skill/gstack`。
52 对基线（`_repro/r303a/absorption_baseline.json`，schema `r303a.absorption_baseline.v1`）里**只有 1 对**用该 path：`gstack / garrytan/gstack / capy/skill/gstack/SKILL.md / pin 11bd23cc / commit b6174451 / local_version 1.3.0`；其余 51 对不受影响。
引用该 path_rule 的面（6 个活面 + 2 个只引历史）：`r303a/compare_baseline.py`、`r304a/r304_quarterly_version_scan.py`（默认基线就是那个 JSON）、`05-exec/r114_replacement_scan.py:569-668`（解析 .upstream 三形态）、`05-exec/r263_declared_upstream_face.py`、`05-exec/r264_sidecar_semantics.py`（SAME_LINEAGE 分类，本件结论直接喂它）、`05-exec/check_r291_landed.py:31`（落地面比对）。
不受影响：`05-exec/r291_req2_compliance.py:45` 只读 `.upstream` **首行 repo** ⇒ 改 path 行不会把这条合规面弄红。
历史快照（只读，不改行为）：`06-benchmark/r263/r264/r271/r275/r277/replacement_matrix_shadowstrict.json`、`memory/07-next-steps.md`、`_repro/r301c/r302b/r314b/r315a`。

## 7. 三件路径与写面自证

- `自建skill优化/_temp/r316b/lineage.json`（known_answers / metric_design / gstack_options / impact / negative_controls / signatures 七签名 sha256）
- `自建skill优化/_temp/r316b/report.md`（本件）
- `自建skill优化/_temp/r316b/check_r316b.py`（判据 + 内嵌两腿负控）
- 佐证：`_temp/r316b/evidence/`（gh api 现拉 5 件 + 2 个 .tmpl + impact.json + gstack 树 SKILL/browse 路径清单）、`_temp/r316b/scripts/fetch_upstream.py`（可复现取件，联网只用 gh api）
受管根未写：`git -C D:/global_skills rev-parse HEAD` = `c5d8391dbea1ff16c666c2278d277a4bf09b37fb`，`HEAD:gstack/SKILL.md` = blob `3d9592a92789f36cbbeb567676c715fa6f2533a0`（27307B），`gstack/SKILL.md` 与 `gstack/.upstream` porcelain 皆空。`_repro` 与焚诀侧只读。

### 7.1 行数口径对账（任务书给的两个数与实测不符，按实测记，不改判据）

| 件 | 字节 | LF 换行数 | 非空行 | 任务书/r315a 口径 |
|---|---|---|---|---|
| 本地 `HEAD:gstack/SKILL.md`（blob 3d9592a9） | 27307 | 643 | 502 | 437 |
| 本地工作树 `gstack/SKILL.md`（CRLF 形态） | 27944 | 644 | — | — |
| capy 件 @pin `b6174451`（blob 11bd23cc，本次按 ref 现拉并当场复算 sha1 对上） | 17898 | 83 | 51 | 52 |
| capy 件 @main 现值（blob 6bbb4e0c） | 21622 | 87 | 53 | r314b 记 21608B / blob 8ef728bd |

⇒ 本件判据**不依赖行数**（S4 长度比只报告、永不过门，就是为避开这个口径泥潭而设计的），437/52 与 643/83 之差不影响任何裁决。
  差因未取证，登记为 UNK：**任务书那两个数无法由 git blob 换行数 / 非空行数 / 工作树行数任一口径复现**，疑为更早一次吸收前快照口径。

## 8. 本件局限（不装作已验）
- browse 方案的 same-family **未成立**：D5/D6 弃权源于触发短语表与工具表覆盖不足，指标无法区分「无触发面」与「词表没这条」——已在 §4.3 记为下一步取证，不据此下改配结论。
- 本地件的 `capy` 0 次出现是**受管侧文本**证据，不是上游证据；上游是否存在一个与本地等价的 gstack 套件件未取证（根 `SKILL.md` 是 router，278 行，判 unclear）。
- 未与 r314b 的 `8ef728bd` 做逐字节 delta（本件只需签名，不需增量清单）；季档 pin 未动。