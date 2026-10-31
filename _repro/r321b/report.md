# R321B — 入口普查「断链」10 条逐条取证复核

> 只读取证件。判据本体 `_repro/r320a/entry_census/check_r319a.py` **逐字未改**（sha256 前 12 位 `a0ab6a9d40cc`，31777 B）。
> 结论件 `_repro/r321b/broken_verify.json`；自证件 `_repro/r321b/check_r321b.py`。

## 0. 受管根可达性与前置

| 项 | 命令 | 读数 |
|---|---|---|
| HEAD | `git -C D:/global_skills rev-parse HEAD` | `e8f489ebcf788f9b4f258ab96bb6c3cf465c5b25`（与 brief 一致，面可达，未触发退路） |
| 工作树脏 | `git -C D:/global_skills status --porcelain` | rc=0，79 行脏件 ⇒ 全程只用 HEAD 树与 HEAD blob 下结论，未取工作树内容作依据 |
| 树规模 | `git -C D:/global_skills ls-tree -r -l HEAD` | 16509 条（与 `entry_scan.r320.json` 的 `tree_rows=16509` 一致） |
| 普查报告 | `report.r320.md` L105-L114 | 末节「断链清单（全量）」逐字列 10 条；sha256 前 12 位 `4dc0d49161ee`（10157 B） |
| 普查读数 | `entry_scan.r320.json` | sha256 前 12 位 `464161791dc1`；`broken_total=10`、`orphan_total=624`、`court.verdict=pass`、`schema=_r319a-entry-scan-1` |

**复现对齐（前置门）**：本臂用 `importlib` 直接加载判据本体，逐 slug 调其 `judge()`（`_r321b_driver.py`，rc=0），得 `broken_total=10` 且断链集合与 `entry_scan.r320.json` 的 `per_skill[].broken` 逐条相同（`html-ppt` 1 条 + 9 个 `story-*` 各 1 条 `references/split-NN.md`）。复现不齐则无权复核口径，这一步先过了。

---

## 1. 逐条取证（原话 → 命令 → 读数 → 判定）

### 1.1 九个 `story-*/references/split-NN.md` ⇒ 全部 **PLACEHOLDER_FALSE**

**普查原话**（`report.r320.md` L106，逐字；其余 8 条同形态）：

```
- `story-cover/references/split-NN.md`：入口写着它，HEAD 树里没有（断链）
```

**入口原文那一条（HEAD blob，含行号）** — 9 件形态一致，都在版本变更表行里：

```
story-cover/SKILL.md:47:| V1.0.1 | 2026-10-06 | **体量治理分卷**：主文件 1439 B 超过 12 KB soft limit，按章节将细节迁至 `references/split-NN.md`，主文件只留章节路由与指针（渐进式披露）。正文语义未改，仅迁移位置。 |
```

9 件行号（同一句话在各件位置）：story-cover:47 / story-deslop:181 / story-import:234 / story-long-analyze:98 / story-long-write:53 / story-review:186 / story-setup:99 / story-short-analyze:179 / story-short-write:169。

句子语义：「按章节将细节**迁至** `references/split-NN.md`」= 在描述**命名规约**（NN 是序号占位），不是指向某个叫 `split-NN.md` 的文件。

**该件树内实际存在的 `references/split-*.md`**（命令形态 `git -C D:/global_skills ls-tree -r --name-only HEAD -- <slug>/references/` 过滤 split-* ，全部 rc=0）：

| slug | 树里真实的 split-* | 条数 | 树里有字面 split-NN.md 吗 |
|---|---|---|---|
| story-cover | split-01..05 | 5 | 无 |
| story-deslop | split-01 | 1 | 无 |
| story-import | split-01..10 | 10 | 无 |
| story-long-analyze | split-01, split-02 | 2 | 无 |
| story-long-write | split-01..03 | 3 | 无 |
| story-review | split-01..05 | 5 | 无 |
| story-setup | split-01, split-02 | 2 | 无 |
| story-short-analyze | split-01..03 | 3 | 无 |
| story-short-write | split-01, split-02 | 2 | 无 |

**决定性一条**：这些真实件在入口里都被逐字点名过（路由行形态为 `> **细节见** ` 加反引号包 `references/split-01.md`）。实测每件的「树里有但入口没提」与「入口提了但树里没有」两个清单都是空集（`_link_cover.json`）：story-cover 5/5、story-import 10/10、story-review 5/5 …… 全部 tree_but_unmentioned=0、mentioned_but_absent=0 ⇒ 入口真实链接面完整，`split-NN.md` 只是那行 changelog 里的模式串。

**判定：PLACEHOLDER_FALSE（假阳性 9 条）**。老大的怀疑成立，且本臂给出更强证据（§2）：扫描器根本没有能力识别任何占位符 —— 那条分支是死代码。

### 1.2 `html-ppt/examples/my-talk/index.html` ⇒ **REAL_BROKEN**（真断链，附另有解释）

**普查原话**（`report.r320.md` L105）：

```
- `html-ppt/examples/my-talk/index.html`：入口写着它，HEAD 树里没有（断链）
```

**命令与读数**：

```
$ git -C D:/global_skills cat-file -e HEAD:html-ppt/examples/my-talk/index.html
fatal: path 'html-ppt/examples/my-talk/index.html' does not exist in 'HEAD'
rc=128   （预期失败，实测即失败）

$ git -C D:/global_skills ls-tree -r --name-only HEAD -- html-ppt/examples/
html-ppt/examples/demo-deck/index.html
rc=0     （examples/ 下 HEAD 树只有这一个文件）

$ git -C D:/global_skills ls-tree -r --name-only HEAD（全树 16509 条）中含 my-talk 的路径
（空）    0 条
```

**入口原文写到它的行（HEAD blob，逐字）**：

```
html-ppt/SKILL.md:101:   ./scripts/new-deck.sh my-talk
html-ppt/SKILL.md:102:   open examples/my-talk/index.html
html-ppt/SKILL.md:118:    `examples/my-talk/` as a starting point. Each folder is self-contained with
html-ppt/SKILL.md:124:    ./scripts/render.sh examples/my-talk/index.html 12      # 12 slides
```

**另一条实测**：上游 `lewislulu/html-ppt-skill` 的 main 分支 `examples/` 也只有 `demo-deck`（GitHub contents API，status=200）⇒ 不是本仓迁移丢件，本仓与上游同形态。

**判定：REAL_BROKEN（真断链 1 条）**。这不是占位符形态：`my-talk` 是具体小写词，无 `NN`/`*`/`{}`/`<>`/`$` 任何占位标记，路径字面解析成功、落在本 slug 已存在的 `examples/` 子目录内、树里确无此件 —— 属扫描器口径该抓的那一类。

**「另有解释」必须写清（影响修法，不影响判红）**：L101-L102 是一个 bash 代码块的两步 —— 先跑 `./scripts/new-deck.sh my-talk` 生成该文件，再 `open` 它。`scripts/new-deck.sh` 本身在 HEAD 树里存在（`git -C D:/global_skills cat-file -e HEAD:html-ppt/scripts/new-deck.sh` rc=0），其 L18 为 `PARENT="${2:-examples}"`、L27 为 `OUT_DIR="$HERE/$PARENT/$NAME"`、L37 把模板重定向写入 `"$OUT_DIR/index.html"`，证实 `examples/my-talk/index.html` 是**命令产物**，文档不是在声称仓里已随附一份 deck。所以严格说它是「引用运行后才存在的路径」，不是「链接指向丢了的文件」。但这条**不能因此放过**（理由见 §4）：静态入口可达性口径下它就是不可解析的字面路径；一旦为它开「命令产物」豁免口子，任何把文件名写进反引号的 typo 都能宣称「这是运行后才有的」而逃逸。正确修法只能是新增第三计数桶（如 GENERATED_OUTPUT_REF）并显影，而不是判它「不是断链」。

### 1.3 `counts.other = 0` 的依据

10 条里没有第三条路：9 条占位符误判（树里真实件齐全且已被逐字点名），1 条字面真缺件。不存在需要单列的「工作树有但 HEAD 没有」「权限不可达」「中文名八进制转义没还原」形态 —— 后者已排除：`check_r319a.py:214-221` 的 `unquote()` 负责还原 109 条八进制引号路径，本批 10 条路径全为 ASCII，不涉及。

---

## 2. 断链口径实现（`check_r319a.py` file:line）与缺陷定位

判链链路在 `judge()`（`check_r319a.py:249-334`）：

| 步 | file:line | 做什么 |
|---|---|---|
| 1 | `check_r319a.py:276` | `for tok in path_tokens(text)`：按字符白名单把正文切成像路径的串 |
| 2 | `check_r319a.py:277` | `cand, why = norm(tok)`：规整 + 剔除不合格 token |
| 3 | `check_r319a.py:301` | `local_of()` 归位本 slug |
| 4 | `check_r319a.py:308` | 一级目录段必须在本 slug 已存在的子目录集合 `sdirs` 内，否则落 `outside_slug` 剔除 |
| 5 | **`check_r319a.py:316-317`** | `if full not in own:` → `broken.append(rel)` —— **定论点：只看 HEAD 树里有没有这个字面路径，完全不看名字形态** |

### 缺陷一（直接致本批 9 条误报）：占位符过滤只按字符集，漏「字母占位符」

`check_r319a.py:122` 逐字：

```python
    if any(c in t for c in "<>{}*$^|%") or t[0] in "~!":
        return None, "placeholder"
```

作者本意确实要剔占位符（`check_r319a.py:14` 文档话术、`report.r320.md` L137「剔 URL、占位符 <x>/$VAR、..、绝对路径…」同话术），但实现是**字符集合命中**。`split-NN.md` 的 `NN` 是字母，不在 `<>{}*$^|%` 内 ⇒ 不触发剔除 ⇒ `norm()` 原样返回 ⇒ 走到 `:316` 判缺 ⇒ broken +1。

用判据本体自有函数实测（`_driver_out.ndjson`，stage=norm_probe）：

```json
{"input": "references/split-NN.md", "tokens": ["references/split-NN.md"],
 "norm": [[{"tok": "references/split-NN.md", "cand": "references/split-NN.md", "why": null}]]}
```

`why: null` = 没被任何剔除规则拦住 ⇒ 直接进入存在性判定 ⇒ 必然判缺。**具体缺陷：占位符识别按字符集枚举，未覆盖「纯大写字母/数字位占位后缀」形态（-NN、-XX、-00、-N）。**

### 缺陷二（更根本，本臂新发现）：`:122` 那一支永远打不到 = 死代码

`check_r319a.py:51` 逐字：

```python
PATH_OK = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-/:") | set([BS])
```

`path_tokens()`（`check_r319a.py:91-103`）只把白名单内的字符拼进 token，而 `< > { } * $ ^ | %` 全都不在 `PATH_OK` 内 ⇒ 任何 token 都不可能含这些字符 ⇒ `norm()` 里那句 `any(...)` **恒为 False**。

两条独立实测互证（`_driver_out.ndjson`，stage=deadcode）：

```json
{"tokens_scanned": 52060, "tokens_with_ph_chars": 0, "placeholder_bucket_count": 0,
 "drop_keys": ["absolute","empty","ext_not_routable","no_dir","no_ext","outside_repo",
             "outside_slug","parent_jump","repo_root_ref","upstream_mirror","url_scheme"]}
```

对 52 件入口全文切出 52060 个 token，**没有一个**含占位符字符；剔除桶里根本没有 `placeholder` 这个键 —— 与 `entry_scan.r320.json` 的 `skip_histogram` 不含 `placeholder` 一致。

⇒ 报告 L137 写的「剔 … 占位符 <x>/$VAR …」在实现层面是**空头承诺**：占位符从来就没被 `norm()` 剔过。那为什么过去没大规模误报？因为真尖括号/花括号/星号形态被 `path_tokens` 当场切开，落到 `no_dir`/`no_ext` 桶里去了（顺带剔掉）。反证实测（stage=norm_probe）：

```json
{"input": "references/split-<name>.md", "tokens": ["references/split-", "name", ".md"],
 "norm": [[{"tok":"references/split-","cand":null,"why":"no_ext"},
          {"tok":"name","cand":null,"why":"no_dir"},
          {"tok":".md","cand":null,"why":"no_dir"}]]}
```

`references/split-*.md` 同形态（切 2 段，全落 `no_dir`/`no_ext`）。**所以真实缺陷不是「漏了 NN 这一种字符」，而是「占位符过滤整体失效，靠切分副作用兜底」——`NN` 恰好是唯一一种能穿过切分、又不被字符集拦住的占位形态。**

### 缺陷三（连带登记，免下轮误以为改一处就好）

凡是依赖「token 里还剩什么字符」的判断都被 `path_tokens` 的白名单改写：`:122` 的字符剔除、`:131-136` 的 `no_ext`/`ext_not_routable` 都建立在切分结果上。报告 L138 自称「拿漏判换假阳性归零」的 `sdirs` 收紧（`:308`）也属同一族 —— 它把整段目录名 typo 落到 `outside_slug`（本批 77 条）而**不计断链**，即漏判侧。本臂不改这些行为，只登记它们与 `:122` 同源。

---

## 3. 修正口径两条候选（各配「必须仍判红」反例，均已在内存实装复算）

> 均为**建议**，判据本体一行未改。实装见：`_r321b_resolve.py`（候选一展开对树）、`_r321b_teeth.py`（牙齿）、`_r1_vs_r3.py`（形状豁免 vs 展开对树对比）、`_r321b_driver.py` 内的 R1/R2n/R2b 三形。

### 候选一（推荐）：占位符**展开对树**，命中才算占位符

规则一句话：断链候选若具占位形态（末段主干以纯大写后缀 -NN / -XX / -00 收尾，或含 `*` `?` `{x}` `<x>` `$VAR`），**不直接豁免**，而是把它当 glob 在 HEAD 本 slug 子树里展开：命中 >=1 个真实文件 ⇒ 记 PLACEHOLDER_PATTERN、从 broken 分母剔除并单独计数；命中 0 ⇒ **仍判红**。存在性检查本身不放宽。

实测 kills=9（`_resolve_out.ndjson` 首行 `killed` 字段），且 `red` 字段只剩一条：`html-ppt/examples/my-talk/index.html`。逐件展开命中数：

| slug | 占位符展开命中 | 判定 |
|---|---|---|
| story-cover | 5（split-01..05） | PLACEHOLDER_PATTERN |
| story-deslop | 1（split-01） | PLACEHOLDER_PATTERN |
| story-import | 10（split-01..10） | PLACEHOLDER_PATTERN |
| story-long-analyze | 2 | PLACEHOLDER_PATTERN |
| story-long-write | 3 | PLACEHOLDER_PATTERN |
| story-review | 5 | PLACEHOLDER_PATTERN |
| story-setup | 2 | PLACEHOLDER_PATTERN |
| story-short-analyze | 3 | PLACEHOLDER_PATTERN |
| story-short-write | 2 | PLACEHOLDER_PATTERN |
| html-ppt | 0（非占位形态，不展开） | **RED** |

为什么比「按形状豁免」强（`_r1_vs_r3.py` 实测：形状豁免单用会漏真断链）：

| 探针 | 树里存在吗 | 形状豁免 R1 | 展开对树 R3 |
|---|---|---|---|
| `data-analysis/assets/STYLE_PRESETS.md` | 否（typo 型真断链） | **放过（错）** | 判红 hits=0 |
| `story-review/references/dispatch-NN.md` | 否（占位形态但树里无对应件） | **放过（错）** | 判红 hits=0 |
| `canvas-design/canvas-fonts/Nope-OFL.txt` | 否 | **放过（错）** | 判红 hits=0 |
| `story-import/references/split-11.md` | 否 | 判红 | 判红 hits=0 |
| `story-cover/references/split-NN.md` | 否（本应豁免） | 放过 | 豁免 hits=5 |

配套量级证据：HEAD 全树 16509 条路径里有 **39 条真实文件的 basename 命中「纯大写后缀」形状**（`canvas-design/canvas-fonts/*-OFL.txt` 27 条、`cloudbase/**/RULES_INDEX.md`、`frontend-slides/STYLE_PRESETS.md` 等）⇒ 形状豁免会把这一类真缺件一并放过，**不能单独用**。

**keeps_red（三条，实测全部仍红）**：

1. `story-review/references/dispatch-NN.md` —— 占位形态但本件树内展开 0 命中 ⇒ 判红。**防 Goodhart 关键条**：不因「像占位符」免检。
2. `html-ppt/examples/my-talk/index.html` —— 无占位形态、树内不存在 ⇒ 判红。
3. `story-import/references/split-11.md` —— 真实命名形态但树里没有 ⇒ 判红。

反向验（存在性优先，`_teeth_out.ndjson` 的 r3_reverse 段）：把 `story-cover/references/split-NN.md` 假造进内存树 ⇒ 现行口径该条消失（`now_red_after_fake=false`）、R3 命中从 5 变 6 ⇒ 证明加的是「展开」这一步，判据仍看树、没改成看名字。

### 候选二（后备，口径最窄）：同行规约上下文词

规则一句话：该断链候选在入口原文出现的那一行同时含「分卷」或「迁至」⇒ 该行在讲分卷命名规约而非指向具体文件，记 PLACEHOLDER_PATTERN 从 broken 分母剔除、单独计数；否则维持判红。

实测 kills=9（`_driver_out.ndjson` 的 variants 段 R2n：9 件各 before=1 → after=0，html-ppt 那条不动）。

**必须写进建议的失败形态**：把词表放宽到含 模板 / template / 命名 / 占位 / pattern（实测形 R2b）会漏放真断链 —— `data-analysis/assets/report_templateX.md` 的文件名自带 template 子串，注入行即命中宽表 ⇒ 判非红（teeth_B 段实测 red_R2b=false）。故本候选只能用窄表，且窄表本身脆：绑定中文 changelog 措辞，换件不适用（html-ppt 的 my-talk 行就不含这两个词，反而因此仍判红）。

**keeps_red（四条，窄表实测全部仍红）**：

1. `html-ppt/examples/my-talk/index.html` —— L102/L118/L124 均不含「分卷/迁至」⇒ 判红
2. `story-import/references/split-11.md` —— 注入行无规约词 ⇒ 判红
3. `story-review/references/dispatch-NN.md` —— 占位形态但同行无规约词 ⇒ 判红
4. `data-analysis/assets/report_templateX.md` —— typo 型真断链，窄表仍判红（宽表已实测漏判）

### 落地顺序建议

候选一为主（不放宽存在性、可复算、对全仓 39 条全大写真实名零误伤）；候选二只作「该行在讲规约」的可解释性辅助字段，不要当豁免依据。两条都必须新增 PLACEHOLDER_PATTERN 独立计数并在报告显影，否则会像现在这样「看不见但不认错」。同时建议把 `check_r319a.py:122` 的死分支改成「切分前判形态」，或从报告话术里删掉「剔占位符」这句空头承诺 —— 注意 `report.r320.md` L137 属历史留痕，按 R241 只能加校正注、不得改写。

---

## 4. 为什么 html-ppt 那条不能跟着一起放（口径边界）

静态入口可达性回答的是「路由面照着这个路径能不能取到东西」。`my-talk` 是运行 `new-deck.sh` 才产出的路径，仓里永远不会有。若为它开「命令产物」豁免口子，任何把文件名写进反引号的 typo 都能宣称「这是运行后才有的」而逃逸。实测：现行口径与两条修正候选下它都判红（teeth_B 段：now_red=true、red_R1=true、red_R2n=true、red_R2b=true），这正是两条候选的 keeps_red 都收它的原因。若要给它另立类别，正确做法是**新增第三计数桶**（如 GENERATED_OUTPUT_REF），把该条从 broken 移到该桶并显影，而不是判它「不是断链」。

---

## 5. 本次取证自身偏差

1. **复现依赖判据本体，不依赖我自写的口径**。这是刻意的（`importlib` 加载 `check_r319a.py` 后调其 `judge()`）。残余风险：我实装的 R1/R2n/R2b/R3 四条规则是本臂近似实现，与将来真落地的实现可能有差异 ⇒ 候选的 kills=9 只能当「量级 + 牙齿方向」证据，**不能当落地后的回归基线**（落地件必须自带负控）。
2. **只读 HEAD，未读工作树**（工作树有 79 行脏件）。若真实意图是审「磁盘当前态」，本批判定不覆盖该口径。同口径依据：`report.r320.md` L137 自称「未读工作树任何入口外内容」。
3. **上游 GitHub 一条是外部证据**（contents API，status=200，只回 `demo-deck`），是 2026-10-31 的实时值，未 pin 到 `upstream_commit_sha=fd16290679...` 对应的历史树（本臂未做）。它只支撑「非迁移丢件」这一句，不支撑任何判红/判绿结论。
4. **`split-NN.md` 语义为「命名规约」是文本推断**，一手证据三点：句子措辞「按章节将细节迁至」（分卷=多份）＋ 树里 split-01..NN 连续编号真实存在 ＋ 每个真实件都已被逐字点名。未取证当轮拆分执行件与 r161 分卷规则原文对 NN 的正式定义。
5. **counts.other=0 是分桶选择，不是数据缺失**。若父级认为「命令产物引用」应单列，`html-ppt` 那条应从 real 移到 other（real→0、other→1）。本臂按「静态存在性」口径选 real，并把另一种分法写在 §1.2/§4，未擅自隐藏。
6. **负控未落红副本进仓**：进程级负控在 `%LOCALAPPDATA%/Temp/r321b_negctl_<ts>` 跑完即删（实测 `scratch removed exists=false`）；`--negctl` 走 `copy.deepcopy` 内存注入，不写 `broken_verify.json`。
7. **判据本体只读性自证**：收尾复算 `check_r319a.py` sha256 前 12 位 = `a0ab6a9d40cc`、31777 B，与 r320a 落盘时一致（本臂从未打开写句柄）。
8. **写面自证（含并发写者申报）**：本臂写入只落 `_repro/r321b/`（git status 里我的行只有 `?? _repro/r321b/` 一条；中途一张临时转储 `_repro/r321b_tmp_tree_truth.json` 已删除）。`memory/`、`06-benchmark/`、`04-plan/`、`05-exec/`、`_repro/r320a/`、`_repro/r319b/`、`README.md`、`DECOMPOSE.md`、`D:/global_skills`、`D:/global_memory` 均未写；git 全程只读（rev-parse / ls-tree / show / cat-file / status / log / check-ignore），无 add/commit/checkout/reset/restore/stash/push/tag/clean。**并发写者实测**：收尾扫描发现 `06-benchmark/` 等禁写面有 50 个文件 mtime 晚于我开工时刻（最晚 2026-10-31T14:08:42Z，即本机 22:08），文件名为 `r321_gate_run.json` / `gate_runs.jsonl` / `teeth_proof_latest.json` 一类的门禁运行产物 ⇒ 属**另一写者**（同项目并行的 r321 门禁跑批），非本臂所为。按 D7.2 多写者纪律在此显影，并声明：本臂三件产出的哈希取自 22:10 之后的一次性快照，若父级复算时值不同，先比对是否被该跑批波及，不要回改本臂结论件。

---

## 6. 结论与判据

**10 条里真断链 1 条（`html-ppt/examples/my-talk/index.html`），模板占位符误判 9 条（9 个 `story-*/references/split-NN.md`），other 0 条。**

老大的怀疑成立，且根因比怀疑更严重：判据的占位符过滤分支是**死代码**（`check_r319a.py:51` 的 `PATH_OK` 白名单不含 `<>{}*$^|%`，致 `:122` 恒 False；52060 个 token 里 0 个含占位符字符、剔除桶里根本没有 placeholder 键）。`NN` 恰好是唯一能穿过切分又不被字符集拦住的占位形态，所以它成了本批 9 条假阳性的入口。

### 判据命令

```bash
export PYTHONPYCACHEPREFIX=/tmp/r321b_pyc     # Windows: set PYTHONPYCACHEPREFIX=%TEMP%\r321b_pyc
cd C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化
python -B _repro/r321b/check_r321b.py
```

期望末行：`[R321B:BROKEN] real=1 placeholder=9 teeth=pass`

### 负向对照（证明判据有牙，两条形态都跑过）

| 形态 | 命令 | 实测 |
|---|---|---|
| 内存注入 8 类缺陷 | `python -B _repro/r321b/check_r321b.py --negctl` | rc=0，8 行全部 `caught`（含 brief 点名的「kind 改空串」「keeps_red 清空」两类），原样文档仍 `teeth=pass` |
| 进程级篡改副本（scratch 目录，跑完即删） | 逐类改写后跑同一脚本 | kind 空串 rc=1、keeps_red 清空 rc=1、cmd 清空 rc=1、exit 改字符串 rc=1、counts 改数 rc=1；未篡改副本 rc=0 |

### 读数（sha256 前 12 位）

| 件 | sha256 前 12 位 | 字节 |
|---|---|---|
| `_repro/r321b/broken_verify.json` | `a1abcee01fab` | 7944 |
| `_repro/r321b/report.md` | 见收尾消息（本件不能自指自身哈希） | 21841 |
| `_repro/r321b/check_r321b.py` | `692d1670ddc5` | 6512 |
| 上游 `_repro/r320a/entry_census/report.r320.md` | `4dc0d49161ee` | 10157 |
| 上游 `_repro/r320a/entry_census/entry_scan.r320.json` | `464161791dc1` | 81341 |
| 判据本体 `_repro/r320a/entry_census/check_r319a.py`（只读未改） | `a0ab6a9d40cc` | 31777 |


