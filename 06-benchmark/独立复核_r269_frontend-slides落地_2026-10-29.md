# 独立复核：r269 · frontend-slides 受管根改动（包登记 + 冲突声明）

- 被审件：`D:/global_skills/frontend-slides/SKILL.md`（21260 B，mtime 2026-10-29 18:05:38.705236 +0800，sha256 `39fdd120…d1cf`）
- 受管根：`D:/global_skills`（只读复核，本次未写入一个字节）
- 提交：`6394cbae1e5d00f8a60e383f761613664cca2b41`（[rule_editor] insert (frontend-slides/SKILL.md)，2026-10-29 18:05:39 +0800）
- 复核时间：2026-10-29T18:15:23+08:00（本机 `date -Iseconds`）
- 形态：只读取证；未写 `D:/global_skills` / `D:/global_memory`；未跑 run_gates.py；未改 05-exec 任何 .py；未动 Lead 的 06-benchmark 件；零 git 写。

## 总判：**PARTLY**（5 条实测成立 + 1 条部分成立）

| # | 检查项 | 判读 | 状态 |
|---|---|---|---|
| ① | 插入内容实读 / 只追加 | 7 行 686 B 纯追加，既有 100vh 条款原样在位 | CONFIRMED ✅已实测 |
| ② | 备份是改前快照（两条腿） | 备份 0 命中、当前 1 命中；20574 + 686 = 21260 精确闭合 | CONFIRMED ✅已实测 |
| ③ | 受管根 git 单文件 / 祖先 | 1 file changed；merge-base 祖先 exit 0 | CONFIRMED ✅已实测（附 commit 粒度校正） |
| ④ | 效果复算 | grep 0→1 成立；「常规档 14→1 / 严格 69」30 组口径全复现不出 | PARTLY ⚠️部分实测 |
| ⑤ | 冲突断言 | 三方取证（SKILL.md / 包 README / deck-stage.js）⇒ 互斥成立 | CONFIRMED ✅已实测 |
| ⑥ | 越界检查 | 递归 find 只回 SKILL.md 一行 | CONFIRMED ✅已实测 |

总判推导（landing-independent-check-v1）：任一条 REFUTED 即不得给 CONFIRMED；本件无 REFUTED，但 ④ 的数字复现不出 ⇒ 总判 `PARTLY`，不给 `CONFIRMED`。

## ① 插入内容实读：只是追加，未删改既有条款

**命令**

    awk 'NR>=183 && NR<=196 {printf "%d|%s\n", NR, $0}' 'D:/global_skills/frontend-slides/SKILL.md'
    diff '<备份.bak>' 'D:/global_skills/frontend-slides/SKILL.md'
    diff '<备份.bak>' 'D:/global_skills/frontend-slides/SKILL.md' | grep -c '^<'
    sed -n '187,193p' 'D:/global_skills/frontend-slides/SKILL.md' | wc -c

**实测输出（绝对行号）**

    183|（空行）
    184|- `html-template.md` — HTML architecture and JS features
    185|- `viewport-base.css` — Mandatory CSS (include in full)
    186|- `animation-patterns.md` — Animation reference for the chosen feeling
    187|- `bold-template-pack/` — 固定舞台包（`deck-stage.js` fixed 1920×1080 + `selection-index.json` 34 模板索引 + `README.md`）
    188|（空行）
    189|  ⚠️ **已知冲突（R268-1，待迁移）**：本件正文规定 slides 必须落在 `100vh` 内（Viewport Fitting，NON-NEGOTIABLE），
    190|  而该包要求「每个 deck 都按固定 1920×1080 舞台等比缩放」，且其 README 明写「即使源模板原本是 viewport-fluid 也照此办」
    191|  ⇒ **两者对舞台尺寸的指令互斥**。**迁移完成前以正文的 NON-NEGOTIABLE 规则为准**（不改行为）；
    192|  该包的正式迁移（正文 Phase 0/3 与 CSS 引用须同批改）登记为 R268-1。
    193|（空行）
    194|（空行）
    195|**Key requirements:**

插入块 = 187-193 共 7 行，字节实测 `686`（与宣称 686 B 精确一致）。

> 取值（本节两个数字）：`diff '<备份.bak>' D:/global_skills/frontend-slides/SKILL.md | wc -l` 与 `sed -n '187,193p' D:/global_skills/frontend-slides/SKILL.md | wc -c`；
> 期望末行分别给出该唯一 hunk 的行数与插入块的字节数（本件实测 7 行 / 686 B，与宣称一致）。

    $ diff '<备份.bak>' 'D:/global_skills/frontend-slides/SKILL.md'
    （唯一 hunk）
    @@ -184,6 +184,13 @@
     - `html-template.md` — HTML architecture and JS features
     - `viewport-base.css` — Mandatory CSS (include in full)
     - `animation-patterns.md` — Animation reference for the chosen feeling
    +- [`D:/global_skills/frontend-slides/bold-template-pack/` — 固定舞台包（…）
    +
    +  ⚠️ **已知冲突（R268-1，待迁移）**：…
    +  而该包要求「每个 deck 都按固定 1920×1080 舞台等比缩放」…
    +  ⇒ **两者对舞台尺寸的指令互斥**。…
    +  该包的正式迁移（正文 Phase 0/3 与 CSS 引用须同批改）登记为 R268-1。
    +
    DIFF_EXIT=1（有差异，符合预期）

    $ diff '<备份.bak>' '…/SKILL.md' | grep -c '^<'
    0                     ← 零删除行

**既有条款原样核验**

    $ grep -n '100vh\|NON-NEGOTIABLE' 'D:/global_skills/frontend-slides/SKILL.md'
    17:4. **Viewport Fitting (NON-NEGOTIABLE)** — Every slide MUST fit exactly within 100vh. No scrolling within slides, ever. Content overflows? Split into multiple slides.
    43:- Every `.slide` must have `height: 100vh; height: 100dvh; overflow: hidden;`
    189:（本次插入自述，非条款本体）
    191:（本次插入自述，非条款本体）
    另 44 行 clamp 条款、185 行 viewport-base.css 引用行均原样在位。

**判读**：唯一 hunk 的 7 行全部为 `+`，删除行数 = 0 ⇒ 对既有正文（100vh / clamp / viewport-base.css）零改写零删除。边界：这只在「相对备份」意义上成立；**commit 粒度上不是纯追加**（见 ③ 校正）。

**结论：CONFIRMED ✅已实测**

## ② 备份核验：真是改前快照（两条腿都跑）

**命令**

    ls -la 'D:/global_memory_archive/_trash/rule_backup/' | grep -i frontend-slides
    grep -c 'bold-template-pack' '<备份.bak>'; echo EXIT=$?     # 腿 A：改前件必须不命中
    grep -c 'bold-template-pack' 'D:/global_skills/frontend-slides/SKILL.md'  # 腿 B：改后件必须命中
    wc -c '<备份.bak>' 'D:/global_skills/frontend-slides/SKILL.md'
    wc -l '<备份.bak>' 'D:/global_skills/frontend-slides/SKILL.md'
    sha256sum '<备份.bak>' 'D:/global_skills/frontend-slides/SKILL.md'

**实测输出**

    $ ls -la …/rule_backup/ | grep -i frontend-slides
    -rw-r--r-- 1 37533 197609 20574 Oct 27 17:59 frontend-slides.SKILL.md.20261029_180538_466624.bak

    $ grep -c 'bold-template-pack' '<备份.bak>'; echo EXIT=$?
    0
    EXIT=1                     ← 腿 A：改前件不命中 ✓

    $ grep -c 'bold-template-pack' '…/SKILL.md'
    1                          ← 腿 B：改后件命中 ✓（grep -n 指向 187 行）

    $ wc -c '<备份.bak>' '…/SKILL.md'
      20574 <备份.bak>
      21260 D:/global_skills/frontend-slides/SKILL.md
      ⇒ 20574 + 686 = 21260，精确闭合，无其它增删

    $ wc -l '<备份.bak>' '…/SKILL.md'
      336 <备份.bak>
      343 …/SKILL.md            （+7 = 插入块行数）

    $ sha256sum '<备份.bak>' '…/SKILL.md'
    411bc5291705b35b17b51f6fafe4247fff2ff211668bc8ba402f856d821c2405 *<备份.bak>
    39fdd1203aacb16648ccc88944bf46dc6cb2ed4dafae52f3f6ac11bd1134d1cf *D:/global_skills/frontend-slides/SKILL.md

**负向对照（证明判据有牙）**

| 腿 | 对象 | 命令 | 实测 | 期望 | 判定 |
|---|---|---|---|---|---|
| A | 备份（改前） | `grep -c bold-template-pack <备份>` | `0` / EXIT=1 | 不命中 | ✅ |
| B | 当前 SKILL.md（改后） | 同一 grep | `1`（187 行） | 必须命中 | ✅ |

两腿齐备 ⇒ 该判据能区分改前/改后，不是恒绿。若只有腿 A，连「文件被删空」也会假绿。

**附加硬证据**：`diff 备份 → 当前` 只有唯一 hunk 且删除行 0（见 ①）⇒ 备份内容 = 当前内容 − 这 7 行，非字节数巧合。

**结论：CONFIRMED ✅已实测**
## ③ 受管根 git：单文件 + 祖先关系

**命令**

    git -C D:/global_skills log --oneline -3 -- frontend-slides/SKILL.md
    git -C D:/global_skills show --stat HEAD
    git -C D:/global_skills show --stat --name-only HEAD | tail -4
    git -C D:/global_skills merge-base --is-ancestor 6394cbae1e5d00f8a60e383f761613664cca2b41 HEAD; echo IS_ANCESTOR_EXIT=$?
    git -C D:/global_skills status --porcelain -- frontend-slides/SKILL.md

**实测输出**

    $ git -C D:/global_skills log --oneline -3 -- frontend-slides/SKILL.md
    6394cbae [rule_editor] insert (frontend-slides/SKILL.md)
    079b91f3 [rule_editor] insert (test-driven-development/SKILL.md)
    9c38d9b2 跟版补齐：frontend-slides 补上游 A 类缺件 1 件（3308 B）第 1/1 批

    $ git -C D:/global_skills show --stat HEAD
    commit 6394cbae1e5d00f8a60e383f761613664cca2b41
    Author: lxh113377 <3753318894@qq.com>
    Date:   Thu Oct 29 18:05:39 2026 +0800
        [rule_editor] insert (frontend-slides/SKILL.md)
     frontend-slides/SKILL.md | 19 +++++++++++++++++--
     1 file changed, 17 insertions(+), 2 deletions(-)

    $ … show --stat --name-only HEAD | tail -4
    frontend-slides/SKILL.md            ← 唯一文件 ✓

    $ git -C D:/global_skills merge-base --is-ancestor 6394cbae… HEAD; echo IS_ANCESTOR_EXIT=$?
    IS_ANCESTOR_EXIT=0                  ← 祖先关系为真 ✓

    $ git -C D:/global_skills status --porcelain -- frontend-slides/SKILL.md
    （空输出）⇒ 在盘件 == HEAD blob，无未提交尾巴

**⚠️ 必须登记的校正：那 2 处删除行不是插入块造成的**

    $ git -C D:/global_skills show HEAD^:frontend-slides/SKILL.md | wc -c
    20073
    $ git -C D:/global_skills show HEAD^:frontend-slides/SKILL.md > /tmp/headprev_sk.md
    $ diff /tmp/headprev_sk.md '<备份.bak>'
    4,5c4,5
    < last_updated: 2026-09-21
    < version: 1.0.0
    ---
    > last_updated: 2026-10-27
    > version: 1.3.0
    328a329,336
    > ## Version history
    > - **1.3.0**（2026-10-27）— 修断链：…（本批 1 件，3308 B）
    > - **1.2.0**（2026-10-27）— 修断链：…（本批 1 件，3308 B）
    > - **1.1.0**（2026-10-27）— 修断链：…（69 件中的第 1/4 批，18 件）

即备份（20574 B）= HEAD^ 版（20073 B）**再加**「frontmatter 版本行改写 + Version history 追加」，然后才被插入这 7 行（+686）。同一个 commit 把三件事捆成一个提交：HEAD^→HEAD 实际 **+1187 B**，不是 +686 B。

| 说法 | 判定 |
|---|---|
| 提交只动这一个文件 | ✅ 成立（--name-only 仅 1 行） |
| 插入是纯追加 | ✅ 成立（对备份删除行 0） |
| 本次提交只追加了 686 B | ❌ commit 粒度不成立（另含 2 行 frontmatter + 8 行 Version history —— 但经 ③-bis 二次取证，那是**恢复被误覆盖的内容**，不是新增篡改） |

### ③-bis 二次取证：这 2 处删除其实是「恢复」，不是 r269 的改写

    $ git -C D:/global_skills show 079b91f3 -- frontend-slides/SKILL.md | head -45
    commit 079b91f3（HEAD^，2026-10-29 16:10:10，[rule_editor] insert (test-driven-development/SKILL.md)）
    -last_updated: 2026-10-27
    -version: 1.3.0
    +last_updated: 2026-09-21
    +version: 1.0.0
    @@ -326,11 +326,3 @@
    -## Version history
    -- **1.3.0**（2026-10-27）— 修断链：…
    -- **1.2.0**（2026-10-27）— 修断链：…
    -- **1.1.0**（2026-10-27）— 修断链：…

即 **HEAD^ 那个提交把本件误覆盖了**（降版 + 整段删掉 Version history，同提交还删掉 bold-template-pack 三个件，见 ⑦）。所以 r269 提交里的 2 处删除 = 把被覆盖的版本元数据与版本史**改回来**，属修复而非夹带；HEAD^→HEAD 净增 1187 B = 恢复的约 501 B + 插入 686 B。

风险换成这一条：**用 `git revert 6394cbae` 回滚本次插入，会连带把版本元数据与版本史再次打回 1.0.0 / 无史状态** ⇒ 回滚必须按 hunk 做，不能整提交 revert。

**结论：CONFIRMED ✅已实测（附上述粒度校正）**

## ④ 效果复算：grep 成立，但 14→1 我复现不出（自建口径）

**命令**

    grep -c bold-template-pack D:/global_skills/frontend-slides/SKILL.md
    find 'D:/global_skills/frontend-slides' -type f -not -path '*/.git/*' -printf '%P\n' | sort
    # 自写复算（不走 Lead 脚本）：94 个在盘件 × 6 种引用口径 × 5 种范围 = 30 组，改前(备份)/改后(当前) 各算一次

**实测输出**

    $ grep -c bold-template-pack …/SKILL.md
    1                              ← 宣称 0→1 成立 ✓

    在盘件 94 个（递归、排除 .git）；除 SKILL.md 外 93 件参与计数，其中
    bold-template-pack/templates/** 占 68 件（34 模板 × design.md/preview.md）。

    我的口径（未引用件数，改前 → 改后）：
      1) 首段目录名或文件名命中，全 94 件       79 → 7
      2) 父目录或文件名命中，全 94 件           79 → 75
      3) 仅相对路径命中，全 94 件               86 → 85
      4) depth≤2 范围（17 件）文件名命中         9 → 5
      5) 排除 templates（26 件）文件名命中       11 → 7
      6) 仅 top-level（9 件）文件名命中           5 → 4

    30 组里命中「常规档 14→1」的：0 组；
    我最近的严格档读数 = 85（改后）/ 86（改前），与宣称「69」不符。

**判读**

- 实质效果 **成立**：改前该包 3 个根件 + 68 个模板件全部「未被 SKILL.md 指向」；改后 187 行以目录链接指向该包，并在括号里点名 `deck-stage.js` / `selection-index.json` / `README.md` 三件。
- 但「常规档 14→1」「严格档 69」这两个数字，用我 6×5=30 组自定口径**一组都复现不出** ⇒ 记为不可复算，不能给 CONFIRMED；也不给 REFUTED（方向与 grep 读数都对，可能只是口径未公开）。
- 复算所需：Lead 的计数脚本原文 + 「在盘件」集合定义（是否排除 templates/、plugins/ 镜像、是否按目录聚合为单元）。

**结论：PARTLY ⚠️部分实测**（`grep -c` 0→1 = ✅已实测；14→1 / 69 = 实测不成立，非未实测）

## ⑤ 冲突断言是否成立：**成立**

**命令**

    grep -n '100vh\|NON-NEGOTIABLE' 'D:/global_skills/frontend-slides/SKILL.md'
    grep -n '1920\|fixed' 'D:/global_skills/frontend-slides/bold-template-pack/README.md'
    sed -n '55,80p' 'D:/global_skills/frontend-slides/bold-template-pack/README.md'
    grep -n '1920\|1080\|scale' 'D:/global_skills/frontend-slides/bold-template-pack/deck-stage.js' | head -12
    grep -n 'vh\|100%\|height' 'D:/global_skills/frontend-slides/viewport-base.css' | head -30

**实测输出**

    $ grep -n '100vh\|NON-NEGOTIABLE' SKILL.md
    17:4. **Viewport Fitting (NON-NEGOTIABLE)** — Every slide MUST fit exactly within 100vh. No scrolling within slides, ever.
    43:- Every `.slide` must have `height: 100vh; height: 100dvh; overflow: hidden;`
    189/191:（本次插入自述，非条款本体）
    另 44:- ALL font sizes and spacing must use `clamp(min, preferred, max)` — never fixed px/rem

    $ grep -n '1920\|fixed' bold-template-pack/README.md
    50:context-specific visual idea, fixed 16:9 stage behavior, and no visible process
    67:- Generate every deck as a fixed 1920×1080 stage scaled uniformly to the
    71:  proportions to translate into fixed 1920×1080 stage coordinates.

    $ sed -n '65,72p' bold-template-pack/README.md
    - Keep `frontend-slides` output as one self-contained HTML file.
    - Include the full contents of `viewport-base.css`.
    - Generate every deck as a fixed 1920×1080 stage scaled uniformly to the
      viewport. This applies even if the source template was originally
      viewport-fluid.
    - Treat `vw`, `vh`, and `clamp()` values in a source `design.md` as design
      proportions to translate into fixed 1920×1080 stage coordinates.

    $ grep -n '1920\|1080\|scale' bold-template-pack/deck-stage.js
    10: *  (e) auto-scaling — inner canvas is a fixed design size (default 1920×1080)
    11: *      scaled with `transform: scale()` to fit the viewport, letterboxed.
    53:  const DESIGN_W_DEFAULT = 1920;
    54:  const DESIGN_H_DEFAULT = 1080;

    $ grep -n 'vh\|100%\|height' viewport-base.css
    21:    height: 100vh;
    22:    height: 100dvh; /* Dynamic viewport height for mobile browsers */
    94:@media (max-height: 700px)   104:@media (max-height: 600px)   119:@media (max-height: 500px)

**判读：成立（在「舞台尺寸 / 单位基准」层面）**

| 维度 | 正文（SKILL.md） | 包（README + deck-stage.js） |
|---|---|---|
| 舞台尺寸 | 每张 slide 恰好落在 100vh / 100dvh | 固定 1920×1080 设计画布 |
| 尺寸单位 | clamp 流体，禁固定 px/rem | 固定 px 坐标；vw/vh/clamp 只当比例翻译 |
| 断点策略 | 700 / 600 / 500px 高度断点 | 等比 scale 缩放，无断点 |
| 源模板是流体时 | 必须流体 | 「即使源模板原本是 viewport-fluid 也照此办」 |

三点精确化（不把断言抬得过高）：

1. **不是运行时不可共存**：fixed stage 用 `transform: scale()` 铺满视口时同样不出滚动条，正文「不滚动」子条款可被满足；真正互斥的是**度量基准与配套写法**（流体 100vh + clamp vs 固定 1920×1080 px 舞台）。
2. **包 README 第 66 行自身又要求 `Include the full contents of viewport-base.css`**，与第 67 行固定舞台要求内部打架 ⇒ 冲突由文档自身证实，不是审读误判。
3. 插入文本对 README 的转述（「即使源模板原本是 viewport-fluid 也照此办」）**与原文逐字对应**，非编造。

**结论：CONFIRMED ✅已实测 · 断言「互斥」= 成立**

## ⑥ 越界检查：只有 SKILL.md 被写

**命令**

    ls -la --time-style=full-iso 'D:/global_skills/frontend-slides/'
    find 'D:/global_skills/frontend-slides' -type f -newermt '2026-10-29 17:50' -printf '%TY-%Tm-%Td %TH:%TM:%TS %p\n' | sort
    ls -la --time-style=full-iso 'D:/global_skills/frontend-slides/bold-template-pack/'

**实测输出**

    $ find … -type f -newermt '2026-10-29 17:50' | sort
    2026-10-29 18:05:38.7052360000 D:/global_skills/frontend-slides/SKILL.md
    （全场仅 1 行 ⇒ 递归范围内零其它触碰）

    $ ls -la --time-style=full-iso …/frontend-slides/
    drwxr-xr-x .                       2026-10-27 17:22:41.305128500
    drwxr-xr-x ..                      2026-10-29 14:42:35.398127700
    drwxr-xr-x .claude-plugin          2026-08-03 11:36:07.447424500
    -rw-r--r-- .upstream          82   2026-10-26 16:50:47.341625700
    -rw-r--r-- LICENSE          1067   2026-07-05 04:04:08.454236300
    -rw-r--r-- NOTICE           1937   2026-10-26 16:50:47.342625200
    -rw-r--r-- README.md        6686   2026-07-05 04:04:08.454236300
    -rw-r--r-- SKILL.md        21260   2026-10-29 18:05:38.705236000   ← 唯一 18:0x
    -rw-r--r-- STYLE_PRESETS.md 8202   2026-07-05 04:04:08.458814300
    -rw-r--r-- animation-patterns.md 4030 2026-07-05 04:04:08.458814300
    drwxr-xr-x bold-template-pack      2026-10-27 17:56:43.764111300
    -rw-r--r-- html-template.md 12535  2026-07-05 04:04:08.458814300
    -rw-r--r-- meta.json        1581   2026-07-05 04:04:08.496502000
    drwxr-xr-x plugins                 2026-08-03 11:36:07.449417500
    drwxr-xr-x references              2026-10-20 12:35:01.986576200
    drwxr-xr-x scripts                 2026-08-03 11:36:07.465417100
    -rw-r--r-- viewport-base.css 4037  2026-07-05 04:04:08.468401500

    $ ls -la --time-style=full-iso …/bold-template-pack/
    -rw-r--r-- README.md             3308  2026-10-27 17:59:18.646740400
    -rw-r--r-- deck-stage.js        22748  2026-10-27 17:22:41.305128500
    -rw-r--r-- selection-index.json 39202  2026-10-27 17:22:43.433500000
    drwxr-xr-x templates                   2026-10-27 17:24:37.658935900

**判读**：18:0x 时间窗内唯一被写的件是 SKILL.md；包内三件与 templates/ 全为 2026-10-27（早于本次改动 2 天）。仓库全局 `git status` 有 brainstorming / cloudbase 等其它技能的历史 dirty，但与 `frontend-slides/` 无关（该路径下 status 为空）。

**结论：CONFIRMED ✅已实测**

## ⑦ 附加发现（超出 6 条判据，但必须上呈）

### B1 · 被登记的 bold-template-pack 不在 git 里（盘上有、索引里没有）

    $ git -C D:/global_skills status --porcelain -- frontend-slides
    ?? frontend-slides/bold-template-pack/

    $ git -C D:/global_skills ls-files frontend-slides/bold-template-pack
    （空输出 = 索引零条目）

    $ git -C D:/global_skills ls-tree -r --name-only HEAD -- frontend-slides/ | grep bold-template-pack
    （无输出：HEAD 树里没有任何该包文件）

    $ git -C D:/global_skills show --name-status 079b91f3 -- frontend-slides
    M	frontend-slides/SKILL.md
    D	frontend-slides/bold-template-pack/README.md
    D	frontend-slides/bold-template-pack/deck-stage.js
    D	frontend-slides/bold-template-pack/selection-index.json

**判读（高危）**：r269 新登记的包指向的是**未纳入版本控制的在盘文件**。任何 clone / 换端 / `git clean -fdx` 都会把 187 行的登记变成死链（指向不存在的目录）；反过来，后续任一次 `git add -A` 会把这 68+3 个未跟踪件以「新增」身份混进某个不知名提交。

建议（不由本件执行，只上呈）：单独一笔提交把该包（3 根件 + templates 68 件）纳入索引；或显式记录「有意不入库」+ 理由，并在登记行标注「仅本机在盘」。

### B2 · HEAD^ 的误覆盖未被单独登记

    2026-10-29 16:10:10  079b91f3  588 个 D 条目（含 frontend-slides/SKILL.md 的降版 + 删版本史 + 删包三件）

**判读（中危）**：该损伤早于 r269（不是本次改动引入），r269 顺手恢复了元数据部分但**没恢复包的三件进 git**，也没在提交信息里记录这次恢复 —— 于是同一个提交里既有「插入」又有「未声明的恢复」。建议在下一条提交信息或 06-benchmark 台账里把这次恢复写明，避免后人把它当篡改。

## 差异与局限（不隐藏）

1. **④ 「14→1 / 69」不可复算**：30 组自定口径全部落空，我最近的严格档读数是 85/86。需要 Lead 的脚本原文与集合定义才能对齐；在此之前「已降到 1」不满足「面 · 分子/分母 · 切点 · 数值稳定时刻」的可引用标准。
2. **备份 ≠ HEAD^**：20574 vs 20073 B。备份是「插入前一刻的盘上状态」，比 HEAD^ 多出 frontmatter 版本行改写与 Version history ⇒ 对「插入」它是合格改前快照，但不能当 HEAD^ 的等价物（拿它去对 `6394cbae^` 会得到 3 处并不存在于该提交语义的差异）。
3. **commit 粒度夹带**：该提交同时改 frontmatter（`version: 1.0.0 → 1.3.0`、`last_updated` 2026-09-21 → 2026-10-27）并追加 Version history；只回滚插入须按 hunk 做，不能 `git revert`。
4. 附带观察（不影响判读）：Version history 三条正文措辞重复（1.1.0/1.2.0 都写「本批 1 件（3308 B）」），属既有内容瑕疵，非本次插入引入。
5. 备份 mtime = 2026-10-27 17:59:18.646740，与 `bold-template-pack/README.md` 同刻（同批拷贝），早于 commit 时间 2026-10-29 18:05:39 ⇒ 备份时间戳自洽。
6. ⑦/B1、⑦/B2 两条**不计入 6 条判据的 verdict**（它们不反驳任何一条宣称），但属落地完整性缺陷：登记落点不在版本控制内 + 未声明的恢复。总判仍为 PARTLY（唯一拉低判据的是 ④ 的数字）。

## 收尾自证

- 产出（本件自行新建，未动任何既有 06-benchmark 件）：
  - `06-benchmark/r269_landing_independent_check.json`（schema=landing-independent-check-v1，checks=6，verdict=PARTLY）
  - `06-benchmark/独立复核_r269_frontend-slides落地_2026-10-29.md`（本文件）
- 判据命令（可独立复跑）：

    grep -c bold-template-pack D:/global_skills/frontend-slides/SKILL.md

- 期望末行：`1`
- 负向对照（改前件，同一命令）：期望末行 `0`、退出码 1
- 纪律声明：边取证边落盘，先 JSON 后 MD；全程只读受管根；未跑 run_gates.py；零 git 写；写入只落在 06-benchmark 两个白名单件。
