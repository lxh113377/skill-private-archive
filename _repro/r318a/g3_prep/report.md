# coding-agent 落地备料证据包 · r316c

> 任务性质：**只出证据 + 方案，不落地不代裁**（r307b 同款备料，供下一件 T1 换装/吸收用）。
> 受管根 `D:/global_skills/coding-agent/` 本轮**未写一个字节**（只 `git show` / 只读）。产物全落 `自建skill优化/_temp/r316c/`。
> 联网仅 `gh api`。Python = managed venv，`PYTHONPYCACHEPREFIX` 已设。

## 0. 结论一行

| 项 | 值 |
|---|---|
| 已知答案堂 known-pass | **true**（两极双双命中） |
| 配对裁定 pairing | **same-family-gaps**（同族，但本地缺 4 块） |
| 增量条数 | **4**（全部 reverified=true） |
| 换装候选 | **3**（三值 gh api 现取） |
| 上游漂移 | **no-drift**（自算 git 对象号 == 在册基线 == gh 现取，三方一致） |

## 1. 问题①：配对同族核验（gstack 教训前置）

### 1.1 判据（先过已知答案堂，才配裁本件）

禁整行重合率（r315 已证伪：吸收后本地把上游改写为中文，行级必然不重合 ⇒ 会把同族误判成异族）。
改用四条签名轴 + 一条块级轴，全部是集合包含/Jaccard，不含任何逐行相等判定：

| 轴 | 定义 | 方向 |
|---|---|---|
| A1 标题域 | 本地面 vs 上游的标题词元 Jaccard | 对称 |
| A2 用途动词 | 动词集 Jaccard（read/edit/delegate/commit…） | 对称 |
| A3 工具命令面 | 长选项旗标 + CLI 名集合 Jaccard | 对称 |
| A4 判别词包含 | 上游「带信息词元」（代码块/反引号/旗标/文件名/标题词）在本地面的命中率 | 有向 |
| **A5 块级包含**（主判据） | 上游按 `##`/`###` 切块，逐块算 A4 取均值 | 有向 |

**轴必须过堂**：有牙 = 正例分 − 反例分 ≥ `siglib.MIN_TEETH`；无牙轴进 `discarded_axes`，禁止参与裁定。
切割点 = 两极中点（堂内数据导出，不手调）。

| 极 | 件 | 期望 | 实测判词 | 命中 | A1 | A2 | A3 | A4 | A5 |
|---|---|---|---|---|---|---|---|---|---|
| 正例 | docx（`anthropics/skills:skills/docx`） | same-family | same-family | ✅ | 0.0863 | 0.5484 | 0.1818 | 0.6994 | 0.7738 |
| 反例 | gstack（`garrytan/gstack:capy/skill/gstack`） | diff-family | diff-family | ✅ | 0.0181 | 0.5769 | 0.0430 | 0.5061 | 0.5361 |

两极 **双双命中** ⇒ 指标有效，堂过 ⇒ `known-pass=true`。

堂同时抓出一条**无牙轴**（这就是过堂的价值）：A2 用途动词牙距 = 0.5484 − 0.5769 = **−0.0285**（反例反而更高），
read/edit/run 这类动词任何技能都有 ⇒ A2 **作废**，不参与本件裁定。

### 1.2 本件对（本地 coding-agent × 声明上游 codex-delegate）实测

| 轴 | 切割点（两极中点） | 本件实测 | 位置 |
|---|---|---|---|
| A1 标题域 | 0.0522 | **0.2033** | 正例侧 |
| A2 用途动词 | 0.5626 | 0.5106 | 无牙轴，作废不参与 |
| A3 工具命令面 | 0.1124 | **0.2761** | 正例侧（且高于正例 0.1818） |
| A4 判别词包含（确认据） | 0.6028 | **0.8639** | 高于正例 0.6994 |
| A5 块级包含（主判据） | 0.6550 | **0.8648** | 高于正例 0.7738 |

本地面 = `SKILL.md` + `references/*.md` 共 6 件、42653 B（分卷是包的一部分，只比正文必然假报缺块）。

**裁定 = `same-family-gaps`**，三个候选里排掉两个：

- **不是异族错配**（gstack 教训未复现）：gstack 的 A5 只有 0.5361（低于切割点 0.655），本件 A5=0.8648；
  且有硬旁证——本地 4 个 `references/` 分卷与上游同名件 **git 对象号逐字等值**（下表）。
- **不是「零缺口纯超集」**：上游 `SKILL.md` 仍有成块内容在本地面无判别词踪迹（第 2 节 INC-01/02/03）+ 一块入口断链（INC-04）。
- **路径名疑云核清**：上游叫 `codex-delegate` 是因为它是**单后端切片**（Codex CLI）。实测源仓
  `amElnagdy/delegate-skills` 树里有 20 个同族变体（`agy/aider/claude/cline/codex-background/codex/commandcode/copilot/cursor/grok/kimi/muse/omp/opencode/pi/qoder/vibe/warp/zcode-delegate` + `delegate-setup`），
  本地是把这一族的 Codex 切片**扩成四后端**（Codex/Claude Code/OpenCode/WorkBuddy）的超集 ⇒ 与 gstack「面映射错位」不同性质。

### 1.3 逐字收录硬证（references 双对拍，本地 vs 上游）

| 分卷 | 本地 B | 上游 B | 本地 git 对象号 | 上游 git 对象号 | 等值 |
|---|---|---|---|---|---|
| dispatch-and-poll.md | 11738 | 11738 | `b124b940…` | `b124b940…` | ✅ |
| multi-task-queues.md | 3741 | 3741 | `ab8cb011…` | `ab8cb011…` | ✅ |
| review-and-land.md | 7877 | 7877 | `bf64373d…` | `bf64373d…` | ✅ |
| writing-the-brief.md | 6172 | 6172 | `71f256ec…` | `71f256ec…` | ✅ |

上游 `SKILL.md` 本体（10285 B / 175 行）里被中文重写的六块（When NOT / Prerequisites / 五步环 / Review / Authorization / Land）
落在本地 `references/delegation-contract.md`（5716 B / 100 行），其小节标题**保留英文原名**供对账 ⇒ 属「已吸收（改写形态）」，不算缺块。

### 1.4 上游漂移钉（三方对拍）

- 自算 git 对象号 `821111317265648bdaa42643d82a5cfc393592ba`
- 在册吸收基线 `821111317265648bdaa42643d82a5cfc393592ba`
- gh api `contents/...?ref=main` 现取 `.sha` `821111317265648bdaa42643d82a5cfc393592ba`

⇒ **no-drift**，该路径自 r303 起无漂移（本轮 gh 现取复核，非引用旧读数）。
注：聚合仓 `sickn33/agentic-awesome-skills` 本身仍在活跃推送（`pushed_at=2026-10-31T11:16:41Z`），但被声明路径的 blob 号未变。

### 1.5 本地身份实测（与任务所给「已核事实」的出入 —— 如实登记，不改判据）

| 面 | git blob | 字节 | version |
|---|---|---|---|
| 任务所给（已核事实） | `f70875d142…` | 7254 | 1.2.0 |
| 实测 HEAD | `6831af60…` | **7254** | **1.2.0** |
| 实测工作树 | `dde69cdc…` | 7404 | 1.3.0 |

- 字节数与版本号与 HEAD 面**完全相符**（7254 B / v1.2.0），但任务给的 blob 前缀 `f70875d142` 在受管根仓库内
  `git cat-file -t` **解析不出对象** ⇒ 疑为抄录的号前缀有误；本轮以实测号为准。
- 工作树相对 HEAD 有**未提交改动**（`M coding-agent/SKILL.md`，4 insert / 2 delete）：`version 1.2.0→1.3.0`、
  `last_updated 2026-10-26→2026-10-27`、版本史新增 1.3.0 一行（内容 = 「修断链：补上游 A 类被引用却缺件 4 件，29528 B」，
  正是本轮实测到的那 4 个分卷 ⇒ 该改动是 r310 前后修断链留下的，与受管根 git log `d070eee2` 同源）。
  ⇒ **r317 落地前须先确认这批改动归属并决定是否提交**，防并发写者（#44 D7.2）。

## 2. 问题②：增量清单（4 条，各带上游行区间 + 逐字 verbatim + 落点建议）

全部 verbatim 由脚本从 `raw/upstream_SKILL.md`（本轮 gh api 实取留档）**按行区间机械切片**，不手抄；
`reverified` = 该串在上游全文原样命中（4/4 = true）；负控腿 A 证明「改一字 ⇒ false」。
行号基准 = `raw/upstream_SKILL.md`（10285 B / 175 行，git 对象号 `8211113…`）。

### INC-01 — `## Read-only second opinions`（上游 **L122–L131**，700 B，sha256 `2fb5181eccbc…`）

- 类：`content-gap`（真内容缺口）｜强度：strong（6 个判别词在本地面 **0 命中**：`readOnlyViolation` / `best-effort` / `concede` / `defend` / `adversarial` / `contested`）
- 落点：`D:/global_skills/coding-agent/references/delegation-contract.md`，本地 `## Read-only second opinions` 段（实测第 72–75 行）**之后追加两块**。
- 为什么是真缺口：本地只写了「把只读写进 brief、别靠对方自觉」这一句原则；上游同段还多两样**可执行**内容：
  (a) 对抗式取意见的流程——先列已同意点，再逐个争议点给出双方立场，要求对方 `defend` 或 `concede`，结论写在最终消息；
  (b) **只读强度分档**——Codex 沙箱是硬强制，其它实现是 best-effort 且只在事后标 `readOnlyViolation`，故对后者必须改验 `touchedFiles` 是否为空。
  本地是**四后端**（codex/claude/opencode/workbuddy），(b) 比上游单后端原版**更适用**，属本地最该有而没有的一块。

verbatim：
```text
## Read-only second opinions

The relay doubles as a clean way to get an adversarial second opinion with a verified read-only filesystem profile: dispatch
`--read-only` with a brief that lists the agreed points, then each contested point with both
positions, and ask Codex to defend or concede each — deliverable in its final message, touching no
files. Any delegation skill whose implementer offers a read-only mode supports the same use, but
check how hard that mode's guarantee is first: Codex's sandbox enforces it, while Grok's is
best-effort and only flagged after the fact (`readOnlyViolation`) — for those implementers,
verify `touchedFiles` came back empty instead of assuming no edits.
```

### INC-02 — `## If you have the openai-codex plugin`（上游 **L141–L157**，1134 B，sha256 `3d34db0031bb…`）

- 类：`deliberately-skipped-recheck`（**既往主动跳过，须重裁**，不当无争议缺口）｜强度：strong（`codex-rescue` / `forwarder` / `complementary` / `inverse` / `stop-review` / `deliberately` 本地 0 命中）
- 落点：同卷 `Authorization model` 之前新增小节「与 openai-codex 插件的方向图」；若 r317 仍判插件专属，则至少在该卷留一行方向图指针。
- 内容价值：三向区分——插件 `codex-rescue` 是**转发器**（不 poll / 不 review / 不 commit）；插件评审与 stop-review 门是**反方向**（Codex 审你的活）；
  本件是**正向编排环**（你派、你审、你落地）。本地 v1.2.0 版本史明写「属插件专属，未吸收」= 当时的主动取舍。
- 重裁理由（新事实）：本地自 v1.1.0 起已含 **claude 启动形态**，用户若同时装该插件，容易把活整包交给插件，
  从而**丢掉 review + land 责任面**——这正是本件的核心纪律。故本轮把它从「已裁掉」改登记为「须重裁」。

verbatim（脚本切片，逐字）：
```text
## If you have the openai-codex plugin

The official openai-codex Claude Code plugin is excellent and **complementary** — `codex-delegate`
builds on the same `codex` CLI, it doesn't replace the plugin. They point in different directions:

- The plugin's `codex:codex-rescue` agent is a **forwarder**: it hands one task to Codex and returns
  the output. It deliberately does not poll, review, or commit.
- The plugin's review command and stop-review gate run the **inverse** direction: **Codex reviews your work**.
- `codex-delegate` is the **orchestration loop in the other direction**: *you* drive Codex to
  implement across one task or a queue, and *you* review and land each result. That loop — brief →
  dispatch → poll → review → commit, with the orchestrator owning the commit — is what the plugin
  leaves to you, and what this skill encodes.

If you have the plugin installed, its companion CLI is an optional alternative dispatch backend; the
upstream `relay.mjs` is a separate runtime dependency beyond the `codex` binary
(Node and `git`, which the relay also needs, are prerequisites for every skill here).
```

### INC-03 — `## When to Use` 段内「designed-for vs proven」（上游 **L30–L33**，335 B，sha256 `85dfddc1c76b…`）

- 类：`honesty-gap`（证据状态诚实性缺口，非命令缺口）｜强度：strong（`orchestrating` / `comparable` / `designed-for` 本地 0 命中）
- 落点：`SKILL.md` 正文 `# Coding Agent` 与 `## Hard rules` 之间，补**一行**后端证据分档声明。
- 上游原话：环不依赖具体编排 agent（只要能跑 shell + 读文件），但**只在 Claude Code 上设计并实测**，其它编排器算 `designed-for`、不算已证。
- 本地宣称可派四后端（含 WorkBuddy），却**没有任何已实测/未证的分档声明** ⇒ 一句话可补，落正文需同步 `version` 与版本史。

verbatim（脚本切片，逐字）：
```text
Nothing here is specific to one orchestrating agent. The loop needs only the ability to run a shell
command and read a file, so it works the same whether you are Claude Code, OpenCode with a selected
model, or any comparable agent. (It is designed for and run on Claude Code; treat other orchestrators
as designed-for, not yet proven.)
```

### INC-04 — `## References` 四条分卷链接（上游 **L158–L169**，743 B，sha256 `73d02b3cab8c…`）【本轮新抓，非历史结论】

- 类：`navigation-gap-orphan-volumes`（入口断链 / 孤儿卷）｜强度：strong（四条路径 `references/writing-the-brief.md` / `dispatch-and-poll.md` / `review-and-land.md` / `multi-task-queues.md` 在本地面 **0 命中**）
- 实测证据（两条命令，可复跑）：
  - `grep -rlF "references/writing-the-brief.md" /d/global_skills/coding-agent/` ⇒ 无输出；
  - 链接图实测：`dispatch-and-poll.md` 只被 `review-and-land.md`、`writing-the-brief.md` 链到；`multi-task-queues.md` 只被 `review-and-land.md` 链到；
    `writing-the-brief.md` **无人链**；`SKILL.md` 只链 `delegation-contract.md` ⇒ 四卷从入口**不可达**（互相引用的孤岛）。
- 后果：路由/检索面看不见这四卷 ⇒ **生产上等于没有吸收**（尽管字节逐字等值、r310 还专门提交过「修断链」29528 B）。
- 落点：`SKILL.md` 在 `## Delegation contract (read before delegating)` 之后新增 `## References` 小节，四条链接各带一行用途（可中文，**路径须逐字保留**）。
- 这是本包里**性价比最高的一条**：4 行改动、零内容改写风险、直接让已付 29528 B 的吸收成本生效。

## 3. 换装候选（本件非换装路径；三值 gh api 现取，未抄历史数）

| 仓 | stars | 最近 push | license | archived |
|---|---|---|---|---|
| `amElnagdy/delegate-skills` | 2538 | 2026-10-29T23:13:49Z | MIT | false |
| `Yeachan-Heo/oh-my-claudecode` | 40440 | 2026-10-31T11:32:19Z | MIT | false |
| `OrchestratorInc/agent-orchestrator` | 13945 | 2026-10-31T11:49:21Z | Apache-2.0 | false |

取数面：`gh api repos/<r>`（本轮直连）。因判定是 `same-family-gaps`（可增量吸收），**换装不是主路径**；上表仅供 r317 若要换装时参考。

### 3.1 更大的鱼（实测，须 Lead 裁，本件不擅自推进）

- 声明路径在聚合仓是 **docs-only**：`gh api contents/…/codex-delegate` 实测只回 `SKILL.md` + `references/`，**无 `scripts/`**；
  上游自己的 `Limitations` 也写着「executable `scripts/relay.mjs` not included」。
- 源仓 `amElnagdy/delegate-skills` 每个变体**各带运行时**：实测树读数 `skills/agy-delegate/scripts/relay.mjs` 41187 B、
  `skills/aider-delegate/scripts/relay.mjs` 35091 B。
- ⇒ **真正没到手的不是文档，是 relay.mjs 运行时**（本地 5 步环里 dispatch/poll 全靠它）。
  引入运行时 = 新增执行面 + 供应链审查 + 范围变更 ⇒ 按本地自身纪律（「取得、钉版本、审阅后再用」）与 #44，**须老大/Lead 裁**，不在备料包推进。

## 4. 负控两腿（内嵌 `--selftest`）

| 腿 | 规则 | 实测 | pass |
|---|---|---|---|
| A | 把 INC-01 的 verbatim 末字符改一个字 ⇒ `reverified` 必须 false | 原串命中=true，改后命中=false | ✅ |
| B | 把堂内正例 docx 的判词强制改成 `diff-family` ⇒ 整体 `known-pass` 必须 false | 常规 known-pass=true；翻转后=false（pairing 退成 `unproven-metric-hall-failed`，不许裁定） | ✅ |

两腿都**不是**恒绿判据：腿 A 证明逐字复验有牙；腿 B 证明 known-pass 由堂内命中真决定（判词被篡改即塌）。

## 5. 判据命令与期望末行

```bash
export PYTHONPYCACHEPREFIX=/d/app-cache/pyc_r316c
cd 自建skill优化/_temp/r316c
"C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -B check_r316c.py
```

期望末行：

```text
[R316C:PREP] known-pass=true pairing=same-family-gaps increments=4 swap-cands=3
```

两腿逐字（实测输出行）：

```text
# 1) 自检（两腿都跑，走 gh 缓存不重复联网）
"C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -B check_r316c.py --selftest
#   末两行 =
#   [R316C:SELFTEST] legA-pass=true legB-pass=true overall=true
#   [R316C:PREP] known-pass=true pairing=same-family-gaps increments=4 swap-cands=3

# 2) 腿 B 的「真执行」形态（把正例判词强制改异族，整体必须塌）
"C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe" -B check_r316c.py --selftest --force-leg=B
#   末两行 =
#   [R316C:SELFTEST] legA-pass=true legB-pass=false overall=false
#   [R316C:PREP] known-pass=false pairing=unproven-metric-hall-failed increments=4 swap-cands=3
```

> 腿 B 在同一进程内**既跑常规通路也跑翻转通路**（`negative_controls.legB`），故 `--selftest` 不带 flag 时也能自证；
> `--force-leg=B` 是把翻转**注入主判定链**的第二种形态（会让本次 known-pass 变 false），两者互为对照。

## 6. 给 r317 的交接（三道闸 + 建议顺序，不代裁）

- 门：`rule_editor.py` 三道闸（`自建skill优化/AGENTS.md` 红线 2：改 skill 文件唯一途径；**禁 write 整体重写**；镜像 `_my-skills`/`.agents\skills` 只读）。
- 建议顺序：
  1. **INC-04**（4 行、零风险、让已吸收的 29528 B 真正可达）；
  2. **INC-01**（真内容缺口，且本地四后端比上游单后端更需要）；
  3. **INC-03**（一句话诚实性声明；落 SKILL.md 正文须同步 `version` 与版本史）；
  4. **INC-02**（既往主动跳过项 = 重裁，须 Lead 面，不与前三条同闸）；
  5. **relay.mjs 运行时是否引入** = 范围变更，先裁再做（§3.1）。
- 前置脏面：工作树有未提交的 1.2.0→1.3.0 改动，**先确认归属/是否提交**，否则闸会撞并发写者。
- 本件未做的事（按 brief 有意为之）：未写受管根、未改 `.upstream`、未代裁落点、未引入运行时。

## 7. 诚实偏差（三条，不藏）

1. **步数超限**：brief 声明上限 14 步，本件实际工具回合超出。成因 = 两次 `run_code` 的 TS 引号闭合语法失败（正是 AGENTS.md ⑬ 记录的病根）+ 判据脚本分块重写。产物完整、判据可复跑；超限如实登记，不用它当降级理由。
2. **任务所给 blob 前缀对不上**：`f70875d142…` 在受管根解析不出对象（§1.5）。字节/版本与 HEAD 相符 ⇒ 判为抄录号误，未据此改判任何结论。
3. **A2 轴在我的首次尝试里差点被当判据用**：第一版把 A4 当主判据、并用「标题骨架相似度 A4′」做负向轴，docx 正例算出 −4.6、gstack 算出 −82.6（本地分卷越多越像异族）——**方向是反的**。现版把骨架计数只作读数不作判据，主判据改成有向块级包含 A5，并把 A2 用牙距门槛当场作废。这段弯路留在 `raw/` 与本文，供后续复用者不重踩。

## 8. 产物清单

| 件 | 作用 |
|---|---|
| `coding_agent_evidence.json` | 证据包本体（known_answers / pairing_verdict / local_vs_upstream / increments / swap_candidates / negative_controls / handoff） |
| `report.md` | 本文 |
| `check_r316c.py` | 判据（含 `--selftest` 两腿与 `--force-leg=B`） |
| `siglib.py` | 签名轴共享库（轴定义 + MIN_TEETH + 主/确认判据选择） |
| `gap_specs_extra.json` | INC-04 的数据驱动追加项（避免源码手术） |
| `raw/upstream_SKILL.md` | 声明上游全文留档（10285 B，对象号 `8211113…`） |
| `raw/upstream_ref_*.md` | 上游 4 分卷留档（逐字等值对拍用） |
| `raw/known_docx_upstream.md` / `raw/known_gstack_upstream.md` | 已知答案堂两极的上游侧 |
| `raw/upstream_codexdelegate_listing.txt` / `upstream_refs_listing.tsv` | gh contents 树读数（证 docs-only、无 scripts/） |
| `raw/inc_*.txt` / `raw/swap_cache.json` / `coding_agent_evidence.selftest.json` | 切片中间件与自检产物（判据不依赖） |

verbatim（脚本切片，逐字）：
```text
## References

- [references/writing-the-brief.md](references/writing-the-brief.md) — how to write a brief Codex can
  execute blind: structure, XML blocks, the report contract, embedding the real gate commands.
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) — `relay.mjs` flags, the
  `result.json` contract, backgrounding per orchestrator, and recovery when a run misbehaves.
- [references/review-and-land.md](references/review-and-land.md) — the review checklist, the commit
  boundary, and the exact-session rework cycle.
- [references/multi-task-queues.md](references/multi-task-queues.md) — running a sequential queue:
  carrying constraints forward, progress tracking, and the end-of-run coherence check.
```
