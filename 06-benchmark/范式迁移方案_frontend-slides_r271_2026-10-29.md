# 范式迁移方案 · frontend-slides R269-1（preparation / 只读分析）· 2026-10-29

> **本件性质**：R269-1 的**预备分析产物**（只读）。本件**不改** `D:/global_skills` 受管根，不跑 `run_gates.py`，不改 `05-exec/` 任何 `.py`，不做 git 写。
> **来源**：`06-benchmark/r271_frontend-slides_migration_plan.json`（schema=migration-plan-v1，本 md 由该 JSON 机器生成 + 人工定位段落）。
> **路径口径**：本仓根之下没有 `06-benchmark/`；本轮（r268/r269/r271）全部 `06-benchmark` 件都在 `自建skill优化/06-benchmark/`，本件同此。临时件：锚点三件套在 `skill焚诀/_temp/`，r268 面在 `自建skill优化/_temp/`（`r271_r268_recheck_before.json` 另留一份于 `skill焚诀/_temp/`）。
> **结论标记**：✅已实测 / ⚠️部分实测 / ❌未实测 —— 逐条标注，见 §7。

---

## 0. 总表（先看这张）

| # | 项 | 值 | 标记 |
|---|---|---|---|
| 1 | 权威选择 | **B = 改为包主张的 fixed 1920×1080 舞台**（正文侧迁移，包侧 0 改动） | ✅ |
| 2 | 关键证据 | 34/34 `design.md` 要求固定舞台；`deck-stage.js:53-54` = 1920/1080；`references/upstream-frontend-slides.md:9-14` 早已写死固定舞台+禁断点；`scripts/export-pdf.sh:38-39` = 1920/1080 | ✅ |
| 3 | 改法条数 | **32 条**（SKILL.md 17 + viewport-base.css 10 + html-template.md 4 + 上游增量卷 1） | ✅ |
| 4 | 涉及文件 | `SKILL.md` / `viewport-base.css` / `html-template.md` / `references/upstream-frontend-slides.md`（**包侧 4 件不改**） | ✅ |
| 5 | 锚点命中 | 32/32 逐条 `grep -nF` 唯一命中（行号见 §2） | ✅已实测 |
| 6 | 负向对照 | 注入不存在锚点后校验器报 **FAIL（33 条中 1 失败）** | ✅已实测 |
| 7 | 风险 | 6 条（2 条 HIGH：双翻页 K-04 / 导出链 K-05） | ✅ |
| 8 | 验证判据 | 7 条（V0-V6，含 r268 在盘件面复算与 render/导出判据） | ✅/⚠️/❌ |
| 9 | baseline | `SKILL.md` 21,260 B sha256 `39fdd120…d1cf`；r268 常规档未引用 = **1**（`meta.json`），strict = **69** | ✅ |

### 0.1 ⚠️ 口径校准（与任务书行号的两处偏差）

| 任务书说法 | 现文件实测 | 说明 |
|---|---|---|
| 「第 187-193 行是 r269 追加」 | 187-193（含 188、193 两个空行）= 7 行 | 与 r269 报告的 686 B / 7 行一致，**无偏差** |
| 「第 319 行要求内联 viewport-base.css」 | 现件 L319 = `---`；内联要求实际在 **L185**（Phase 3 清单）与 **L326**（Supporting Files 表行） | r269 插入 7 行后行号平移；本方案以 **L185/L326** 为准 |

---

## 1. 权威二选一

### 1.1 事实面（全部实测）

| 面 | 实测 | 命令 |
|---|---|---|
| 包主张 | `bold-template-pack/README.md:66-71`：内联 viewport-base.css **并且**「Generate every deck as a fixed 1920×1080 stage scaled uniformly… This applies even if the source template was originally viewport-fluid」 | `sed -n '63,72p' …/bold-template-pack/README.md` |
| 模板一致度 | `templates/` 34 个目录、**34 份 `design.md` 全部**含 `fixed 1920×1080 stage` | `grep -rl "fixed 1920×1080 stage" templates --include=design.md \| wc -l` → 34 |
| 运行时 | `deck-stage.js:53-54` `DESIGN_W_DEFAULT = 1920` / `DESIGN_H_DEFAULT = 1080`；`:538` `scale = Math.min(vw/W, vh/H)`；`:341` slides 经 `<slot>` 留在 light DOM | `grep -n "DESIGN_W_DEFAULT\|DESIGN_H_DEFAULT" …/deck-stage.js` |
| 本仓自证 | `references/upstream-frontend-slides.md:9-14`：每页写在**固定 1920×1080 舞台**、等比缩放不重排、**不要用响应式断点**、内联 viewport-base.css 全文 | `sed -n '6,14p' …/references/upstream-frontend-slides.md` |
| 导出链 | `scripts/export-pdf.sh:38-39` `VIEWPORT_W=1920` `VIEWPORT_H=1080` | `sed -n '36,39p' …/scripts/export-pdf.sh` |
| 正文旧范式 | `SKILL.md` L17（100vh NON-NEGOTIABLE）/ L43（100vh;100dvh）/ L44（clamp 强制）/ L47（断点）/ L83（1280x720 验收） | §2 逐条 |

### 1.2 方案 A（维持正文 viewport-fluid）

- **要改的行**：正文一侧基本不动；但要让全局自洽，必须改**包侧 3 件 + 34 套模板**：`bold-template-pack/README.md:66-71`（删掉固定舞台契约）、`deck-stage.js:53-54`（常量改 viewport 自适应）、**34 份 `design.md` 的固定舞台段**（每份 3-4 段，例如 `templates/8-bit-orbit/design.md:232-238`、`templates/block-frame/design.md:257-263`、`templates/block-frame/design.md:513`）。
- **影响下游**：`viewport-base.css` 保持 100vh/clamp/断点（不动）；`references/upstream-frontend-slides.md:9-14` 必须**回退/改反**；`scripts/export-pdf.sh` 仍按 1920×1080 截屏（但此时是「把 fluid 页面放到 1920×1080 窗口里截图」，行为尚可）；Phase 0/3 正文保持原样。
- **实际代价**：1 处正文 vs **37 处一致件**（1 README + 1 JS + 34 design.md + 1 增量卷）；且 34 套模板的固定舞台措辞是逐模板重复的硬约束（`even if the source template was originally viewport-fluid`）。

### 1.3 方案 B（正文改为固定 1920×1080 舞台）—— ✅ 推荐

- **要改的行**：**32 条全部落在正文侧可写文件**（`SKILL.md` 17、`viewport-base.css` 10、`html-template.md` 4、`references/upstream-frontend-slides.md` 1），见 §2；`bold-template-pack/*` **0 改动**。
- **影响下游与处置**：
  - `viewport-base.css`：**必须同批**改（`.slide` 100vw/100vh/100dvh → 1920×1080 固定画布；断点块 88-138 删除；scroll-snap 停用；vw/vh 容器上限 → 舞台像素）。理由：包 README:66 与正文 L51/L185/L198 都要求**内联该文件全文** ⇒ 该文件是生成物的一部分，其 `.slide` 规则不翻则舞台包裹形同虚设。
  - **Phase 0**：L83 的 Mode C 验收判据（1280x720 + clamp）改为 1920×1080 舞台坐标 + 无溢出/无压盖。
  - **Phase 3**：L198 生成契约补 stage wrapper；L185（清单）与 L326/L328（引用清单）保持内联 viewport-base.css 并补 `deck-stage.js` 行。
  - **引用清单**：Supporting Files 表新增 `bold-template-pack/deck-stage.js` 行（同时把 `deck-stage` 指针数从 1 提到 ≥2）。
  - **模板模板**：`html-template.md` 加 `<deck-stage width="1920" height="1080">` 包裹 + 控制器分工注释。

### 1.4 推荐 B —— 落证据的理由

1. 哪一侧更新：包与上游增量卷晚于正文（包件 mtime 2026-10-27、上游增量 2026-10-20 吸收；正文/ CSS 仍为 2026-07-05 上游导入文本）。
2. 哪一侧与实际模板一致：bold-template-pack/templates 34 个目录、34 份 design.md 全部含「fixed 1920×1080 stage」要求（grep -rl "fixed 1920×1080 stage" --include=design.md | wc -l = 34；目录数亦为 34），0 份模板要求 viewport-fluid。
3. 哪一侧与运行时一致：deck-stage.js:53-54 常量为 1920/1080，:538 缩放公式 = 整体 scale；bbox 与切页均由组件持有。
4. 本仓自己的旁证：references/upstream-frontend-slides.md:9-14 是本技能正文 L335 明确要求「一并读取」的分卷，它早于本轮就写下固定舞台 + 禁响应式断点 + 内联 viewport-base.css；正文是唯一未对齐的一方。
5. 导出链旁证：scripts/export-pdf.sh:38-39 以 1920×1080 截屏，与固定舞台同构（固定舞台在此视口下 scale=1）。
6. 不改包的理由（#39 不取折中）：包侧 3 件 + 34 模板全部一致指向固定舞台，改包等于用 1 处正文去改 37 处一致件；且包 README/design.md 的措辞（even if the source template was originally viewport-fluid）显式为旧范式预留了翻译路径。
7. 为何必须包含 viewport-base.css 的改动：包 README:66 与正文 L51/L185/L198 都要求内联 viewport-base.css 全文，所以「保留 viewport-base.css 不动」反而会违反包契约——必须把它 stage-scoped 化，否则每份生成物内联进来的 .slide 仍是 100vw/100vh。

> **残余注意**：权威翻转后，非包路径（STYLE_PRESETS 的 12 套）也一并变成固定舞台——这是本迁移的既定行为改变，不是副作用遗留；若日后要保留 fluid 通道，应以追加 .viewport-fluid 覆盖块实现，而非回退 baseline（回退会再次与 34 套模板/组件矛盾）。

---

## 2. 协调改法清单（32 条，逐条具名）

> 每条 `{file, 锚点文本(逐字), 命中行号, 现文, 建议文, 为什么必须同批}`。**锚点已由 `grep -nF` 逐条实测唯一命中**（见 §6 两条腿）。
> 分组：`edit_op` 取值 `replace_line`（整行替换）/ `replace_block_lines_88_138`（整块替换）/ `insert_after_line` / `insert_before_line`。

### 2.1 G1-body-core（7 条）

| id | rel | 锚点（逐字，grep -nF） | 行 | op |
|---|---|---|---|---|
| S-01 | `SKILL.md` | `4. **Viewport Fitting (NON-NEGOTIABLE)** — Every slide MUST fit exactly within 100vh` | 17 | replace_line |
| S-02 | `SKILL.md` | `## Viewport Fitting Rules` | 39 | replace_line |
| S-03 | `SKILL.md` | `- Every `.slide` must have `height: 100vh; height: 100dvh; overflow: hidden;`` | 43 | replace_line |
| S-04 | `SKILL.md` | `- ALL font sizes and spacing must use `clamp(min, preferred, max)`` | 44 | replace_line |
| S-05 | `SKILL.md` | `- Images: `max-height: min(50vh, 400px)`` | 46 | replace_line |
| S-06 | `SKILL.md` | `- Breakpoints required for heights: 700px, 600px, 500px` | 47 | replace_line |
| S-07 | `SKILL.md` | `**When generating, read `viewport-base.css` and include its full contents in every presentation.**` | 51 | replace_line |

#### S-01 · `SKILL.md` L17 · replace_line

- **锚点（逐字）**：`4. **Viewport Fitting (NON-NEGOTIABLE)** — Every slide MUST fit exactly within 100vh`
- **命中**：`grep -nF -e 4. **Viewport Fitting (NON-NEGOTIABLE)** — Every slide MUST fit exactly within 100vh D:/global_skills/fronte` ⇒ 行 [17] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：Core Principle #4 是代理读到的第一条硬契约；若它仍写 100vh，Phase 3 的固定舞台就被它压回旧范式（r269 报告 §1 实测的失败形态）。

#### S-02 · `SKILL.md` L39 · replace_line

- **锚点（逐字）**：`## Viewport Fitting Rules`
- **命中**：`grep -nF -e ## Viewport Fitting Rules D:/global_skills/frontend-slides/SKILL.md` ⇒ 行 [39] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：该标题是整块不变量的锚；不改则块内条款仍自称 viewport 规则，且与 references/upstream-frontend-slides.md:6 的「Fixed Stage Rules（固定舞台不变量）」同名断裂。

#### S-03 · `SKILL.md` L43 · replace_line

- **锚点（逐字）**：`- Every `.slide` must have `height: 100vh; height: 100dvh; overflow: hidden;``
- **命中**：`grep -nF -e - Every `.slide` must have `height: 100vh; height: 100dvh; overflow: hidden;` D:/global_skills/frontend-slid` ⇒ 行 [43] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：这一行是旧范式的可执行定义（100vh/100dvh）；它与 deck-stage.js 的 DESIGN_H_DEFAULT=1080 + scale() 直接互斥，必须与 S-01 同批，否则代理会照此写 fluid 滑页。

#### S-04 · `SKILL.md` L44 · replace_line

- **锚点（逐字）**：`- ALL font sizes and spacing must use `clamp(min, preferred, max)``
- **命中**：`grep -nF -e - ALL font sizes and spacing must use `clamp(min, preferred, max)` D:/global_skills/frontend-slides/SKILL.md` ⇒ 行 [44] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：包 README:70-71 明写「design.md 里的 vw/vh/clamp 要翻译成固定舞台坐标」；不改这行则 Phase 2/3 会继续产出 clamp 驱动的 fluid 版式。

#### S-05 · `SKILL.md` L46 · replace_line

- **锚点（逐字）**：`- Images: `max-height: min(50vh, 400px)``
- **命中**：`grep -nF -e - Images: `max-height: min(50vh, 400px)` D:/global_skills/frontend-slides/SKILL.md` ⇒ 行 [46] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：vh 参照系在固定舞台下失效（stage 内的 100vh 是视口而非画布）；同批换为舞台像素。

#### S-06 · `SKILL.md` L47 · replace_line

- **锚点（逐字）**：`- Breakpoints required for heights: 700px, 600px, 500px`
- **命中**：`grep -nF -e - Breakpoints required for heights: 700px, 600px, 500px D:/global_skills/frontend-slides/SKILL.md` ⇒ 行 [47] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：包与上游增量（references/upstream-frontend-slides.md:11「不要用响应式断点」）都禁重排；留断点等于留一条旧范式后门，且与 viewport-base.css 断点块的删除（V-05）必须同批。

#### S-07 · `SKILL.md` L51 · replace_line

- **锚点（逐字）**：`**When generating, read `viewport-base.css` and include its full contents in every presentation.**`
- **命中**：`grep -nF -e **When generating, read `viewport-base.css` and include its full contents in every presentation.** D:/global` ⇒ 行 [51] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：这是正文唯一把「读 CSS」与「生成形态」绑在一起的一句；不在此处引入包的 Implementation Contract，代理仍只照 viewport-base.css 走 fluid（r269 实测包不可达即源于此）。

### 2.2 G2-phase0（1 条）

| id | rel | 锚点（逐字，grep -nF） | 行 | op |
|---|---|---|---|---|
| S-08 | `SKILL.md` | `content fits at 1280x720` | 83 | replace_line |

#### S-08 · `SKILL.md` L83 · replace_line

- **锚点（逐字）**：`content fits at 1280x720`
- **命中**：`grep -nF -e content fits at 1280x720 D:/global_skills/frontend-slides/SKILL.md` ⇒ 行 [83] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：Phase 0 的 Mode C 验收判据；若仍写 1280x720 + clamp，则「改完不合规」会被判为合规，迁移等于没落地。

### 2.3 G3-phase3（4 条）

| id | rel | 锚点（逐字，grep -nF） | 行 | op |
|---|---|---|---|---|
| S-09 | `SKILL.md` | `- Include the FULL contents of viewport-base.css in the `<style>` block` | 198 | replace_line |
| S-10 | `SKILL.md` | `⚠️ **已知冲突（R268-1，待迁移）**` | 189 | replace_line |
| S-11 | `SKILL.md` | `**迁移完成前以正文的 NON-NEGOTIABLE 规则为准**` | 191 | replace_line |
| S-12 | `SKILL.md` | `该包的正式迁移（正文 Phase 0/3 与 CSS 引用须同批改）登记为 R268-1。` | 192 | replace_line |

#### S-09 · `SKILL.md` L198 · replace_line

- **锚点（逐字）**：`- Include the FULL contents of viewport-base.css in the `<style>` block`
- **命中**：`grep -nF -e - Include the FULL contents of viewport-base.css in the `<style>` block D:/global_skills/frontend-slides/SKI` ⇒ 行 [198] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：Phase 3 是真正写 HTML 的步骤；此处不给 stage 包裹 = 生成物仍是 fluid，与 S-03 的正文契约自相矛盾。

#### S-10 · `SKILL.md` L189 · replace_line

- **锚点（逐字）**：`⚠️ **已知冲突（R268-1，待迁移）**`
- **命中**：`grep -nF -e ⚠️ **已知冲突（R268-1，待迁移）** D:/global_skills/frontend-slides/SKILL.md` ⇒ 行 [189] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：r269 登记的冲突声明必须随权威翻转同步改写，否则文件内同时存在「冲突待迁移」与「已迁移」两套说法（自相矛盾的权威）。

#### S-11 · `SKILL.md` L191 · replace_line

- **锚点（逐字）**：`**迁移完成前以正文的 NON-NEGOTIABLE 规则为准**`
- **命中**：`grep -nF -e **迁移完成前以正文的 NON-NEGOTIABLE 规则为准** D:/global_skills/frontend-slides/SKILL.md` ⇒ 行 [191] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：这句是 r269 期间的权威指针；不翻它则代理按文件读到最后仍以 100vh 为准，S-01/S-03 会被该指针反压。

#### S-12 · `SKILL.md` L192 · replace_line

- **锚点（逐字）**：`该包的正式迁移（正文 Phase 0/3 与 CSS 引用须同批改）登记为 R268-1。`
- **命中**：`grep -nF -e 该包的正式迁移（正文 Phase 0/3 与 CSS 引用须同批改）登记为 R268-1。 D:/global_skills/frontend-slides/SKILL.md` ⇒ 行 [192] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：登记号与状态必须和 S-10/S-11 同步，否则待办台账（memory/07-next-steps 的 R269-1）与正文状态不一致。

### 2.4 G4-refs（5 条）

| id | rel | 锚点（逐字，grep -nF） | 行 | op |
|---|---|---|---|---|
| S-13 | `SKILL.md` | `Mandatory responsive CSS — copy into every presentation` | 326 | replace_line |
| S-14 | `SKILL.md` | `\| `animation-patterns.md`     \| CSS/JS animation snippets and effect-to-feeling guide` | 328 | insert_after_line |
| S-15 | `SKILL.md` | `- **1.3.0**（2026-10-27）— 修断链：补 上游 A 类（被本仓正文引用却缺件（真断链））1 件中的第 1/1 批` | 339 | insert_before_line |
| S-16 | `SKILL.md` | `version: 1.3.0` | 5 | replace_line |
| S-17 | `SKILL.md` | `last_updated: 2026-10-27` | 4 | replace_line |

#### S-13 · `SKILL.md` L326 · replace_line

- **锚点（逐字）**：`Mandatory responsive CSS — copy into every presentation`
- **命中**：`grep -nF -e Mandatory responsive CSS — copy into every presentation D:/global_skills/frontend-slides/SKILL.md` ⇒ 行 [326] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：Supporting Files 表是「引用清单」的权威行；留着 responsive 描述等于给代理第二个旧范式入口。

#### S-14 · `SKILL.md` L328 · insert_after_line

- **锚点（逐字）**：`| `animation-patterns.md`     | CSS/JS animation snippets and effect-to-feeling guide`
- **命中**：`grep -nF -e | `animation-patterns.md`     | CSS/JS animation snippets and effect-to-feeling guide` ⇒ 行 [328] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：该表要显式点名平台实现件；否则 deck-stage.js 只在正文散句里出现，引用清单查不到（r268 的未引用面同族）。

#### S-15 · `SKILL.md` L339 · insert_before_line

- **锚点（逐字）**：`- **1.3.0**（2026-10-27）— 修断链：补 上游 A 类（被本仓正文引用却缺件（真断链））1 件中的第 1/1 批`
- **命中**：`grep -nF -e - **1.3.0**（2026-10-27）— 修断链：补 上游 A 类（被本仓正文引用却缺件（真断链））1 件中的第 1/1 批 D:/global_skills/frontend-slides/SKILL.md` ⇒ 行 [339] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：版本史是本技能的自描述；不记这一笔则下次会话读不到范式已翻转。

#### S-16 · `SKILL.md` L5 · replace_line

- **锚点（逐字）**：`version: 1.3.0`
- **命中**：`grep -nF -e version: 1.3.0 D:/global_skills/frontend-slides/SKILL.md` ⇒ 行 [5] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：frontmatter 版本与 S-15 的版本史必须一致，否则 r269 复核已抓过的那类「版本行/历史行不齐」缺陷重现。

#### S-17 · `SKILL.md` L4 · replace_line

- **锚点（逐字）**：`last_updated: 2026-10-27`
- **命中**：`grep -nF -e last_updated: 2026-10-27 D:/global_skills/frontend-slides/SKILL.md` ⇒ 行 [4] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：同 S-16，frontmatter 时间戳须随改动前进。

### 2.5 G5-css（10 条）

| id | rel | 锚点（逐字，grep -nF） | 行 | op |
|---|---|---|---|---|
| V-01 | `viewport-base.css` | `    width: 100vw;` | 20 | replace_line |
| V-02 | `viewport-base.css` | `    height: 100vh;` | 21 | replace_line |
| V-03 | `viewport-base.css` | `    height: 100dvh; /* Dynamic viewport height for mobile browsers */` | 22 | replace_line |
| V-04 | `viewport-base.css` | `/* 2. Each slide = exact viewport height */` | 18 | replace_line |
| V-05 | `viewport-base.css` | `   RESPONSIVE BREAKPOINTS` | 89 | replace_block_lines_88_138 |
| V-06 | `viewport-base.css` | `/* 4. ALL typography uses clamp() for responsive scaling */` | 41 | replace_line |
| V-07 | `viewport-base.css` | `    max-width: min(90vw, 1000px);` | 60 | replace_line |
| V-08 | `viewport-base.css` | `    max-height: min(80vh, 700px);` | 61 | replace_line |
| V-09 | `viewport-base.css` | `    max-height: min(50vh, 400px);` | 84 | replace_line |
| V-10 | `viewport-base.css` | `    scroll-snap-type: y mandatory;` | 14 | replace_line |

#### V-01 · `viewport-base.css` L20 · replace_line

- **锚点（逐字）**：`    width: 100vw;`
- **命中**：`grep -nF -e     width: 100vw; D:/global_skills/frontend-slides/viewport-base.css` ⇒ 行 [20] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：viewport-base.css 被正文要求全文内联（S-07/S-09 保留此要求）；其 `.slide` 规则不改则每份生成物的 .slide 仍是 100vw，stage 包裹形同虚设。

#### V-02 · `viewport-base.css` L21 · replace_line

- **锚点（逐字）**：`    height: 100vh;`
- **命中**：`grep -nF -e     height: 100vh; D:/global_skills/frontend-slides/viewport-base.css` ⇒ 行 [21] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：同 V-01；这一行是「100vh 必守」在 CSS 层的落点，与 deck-stage.js 的 1080 常量互斥。

#### V-03 · `viewport-base.css` L22 · replace_line

- **锚点（逐字）**：`    height: 100dvh; /* Dynamic viewport height for mobile browsers */`
- **命中**：`grep -nF -e     height: 100dvh; /* Dynamic viewport height for mobile browsers */ D:/global_skills/frontend-slides/viewp` ⇒ 行 [22] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：dvh 是为了视口自适应；固定舞台恰恰相反，保留它会让手机地址栏伸缩时画布变形。

#### V-04 · `viewport-base.css` L18 · replace_line

- **锚点（逐字）**：`/* 2. Each slide = exact viewport height */`
- **命中**：`grep -nF -e /* 2. Each slide = exact viewport height */ D:/global_skills/frontend-slides/viewport-base.css` ⇒ 行 [18] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：注释是这份 CSS 被代理部分读时的语义入口；不改则同行代码改了、说明仍在讲 viewport。

#### V-05 · `viewport-base.css` L89 · replace_block_lines_88_138

- **锚点（逐字）**：`   RESPONSIVE BREAKPOINTS`
- **命中**：`grep -nF -e    RESPONSIVE BREAKPOINTS D:/global_skills/frontend-slides/viewport-base.css` ⇒ 行 [89] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：整块断点（88-138 行）就是 S-06 禁止的重排机制，且与 deck-stage 的整体缩放互斥；保留它则同一份 CSS 内自带两条互相打架的适配策略。

#### V-06 · `viewport-base.css` L41 · replace_line

- **锚点（逐字）**：`/* 4. ALL typography uses clamp() for responsive scaling */`
- **命中**：`grep -nF -e /* 4. ALL typography uses clamp() for responsive scaling */ D:/global_skills/frontend-slides/viewport-base.c` ⇒ 行 [41] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：否则 V-01/V-02 把画布改固定、第 4 段又把字号改回视口驱动，生成物在手机上仍会重排。

#### V-07 · `viewport-base.css` L60 · replace_line

- **锚点（逐字）**：`    max-width: min(90vw, 1000px);`
- **命中**：`grep -nF -e     max-width: min(90vw, 1000px); D:/global_skills/frontend-slides/viewport-base.css` ⇒ 行 [60] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：容器上限若继续用 vw，则固定舞台下卡片宽度随浏览器窗口变，与「绝不重排」互斥。

#### V-08 · `viewport-base.css` L61 · replace_line

- **锚点（逐字）**：`    max-height: min(80vh, 700px);`
- **命中**：`grep -nF -e     max-height: min(80vh, 700px); D:/global_skills/frontend-slides/viewport-base.css` ⇒ 行 [61] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：同 V-07；vh 在 stage 内指向浏览器视口而非画布，是旧范式残留。

#### V-09 · `viewport-base.css` L84 · replace_line

- **锚点（逐字）**：`    max-height: min(50vh, 400px);`
- **命中**：`grep -nF -e     max-height: min(50vh, 400px); D:/global_skills/frontend-slides/viewport-base.css` ⇒ 行 [84] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：与 S-05 是同一规则的两处落点，必须同批，否则正文说 540px、内联 CSS 说 50vh。

#### V-10 · `viewport-base.css` L14 · replace_line

- **锚点（逐字）**：`    scroll-snap-type: y mandatory;`
- **命中**：`grep -nF -e     scroll-snap-type: y mandatory; D:/global_skills/frontend-slides/viewport-base.css` ⇒ 行 [14] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：deck-stage 自持翻页；保留 scroll-snap 会出现「滚一次跳两页」并与 references/upstream-frontend-slides.md:13 的「禁用 display 切页、用 active/visible」策略叠加冲突。

### 2.6 G6-template（4 条）

| id | rel | 锚点（逐字，grep -nF） | 行 | op |
|---|---|---|---|---|
| H-01 | `html-template.md` | `/* --- PASTE viewport-base.css CONTENTS HERE --- */` | 57 | replace_line |
| H-02 | `html-template.md` | `    <section class="slide title-slide">` | 101 | replace_line |
| H-03 | `html-template.md` | `    <script>` | 115 | replace_line |
| H-04 | `html-template.md` | `          this.slides = document.querySelectorAll(".slide");` | 121 | replace_line |

#### H-01 · `html-template.md` L57 · replace_line

- **锚点（逐字）**：`/* --- PASTE viewport-base.css CONTENTS HERE --- */`
- **命中**：`grep -nF -e /* --- PASTE viewport-base.css CONTENTS HERE --- */ D:/global_skills/frontend-slides/html-template.md` ⇒ 行 [57] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：模板模板是 Phase 3 的复制源；注释不点出 stage 语义，生成者不会意识到粘贴进来的 .slide 已是固定画布。

#### H-02 · `html-template.md` L101 · replace_line

- **锚点（逐字）**：`    <section class="slide title-slide">`
- **命中**：`grep -nF -e     <section class="slide title-slide"> D:/global_skills/frontend-slides/html-template.md` ⇒ 行 [101] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：模板若不给 deck-stage 包裹，模板输出的 HTML 与 S-09 要求不一致，且 deck-stage.js 根本没有挂载点。

#### H-03 · `html-template.md` L115 · replace_line

- **锚点（逐字）**：`    <script>`
- **命中**：`grep -nF -e     <script> D:/global_skills/frontend-slides/html-template.md` ⇒ 行 [115] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：与 H-02 成对；不闭合则 deck-stage 把后续 script/UI 一并吃掉，页面结构错乱。

#### H-04 · `html-template.md` L121 · replace_line

- **锚点（逐字）**：`          this.slides = document.querySelectorAll(".slide");`
- **命中**：`grep -nF -e           this.slides = document.querySelectorAll(".slide"); D:/global_skills/frontend-slides/html-template.` ⇒ 行 [121] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：模板自带控制器与 deck-stage 自带翻页会同时响应键盘；注释必须在同批说明分工，否则「双翻页」成为迁移后的第一号行为缺陷。

### 2.7 G7-upstream（1 条）

| id | rel | 锚点（逐字，grep -nF） | 行 | op |
|---|---|---|---|---|
| U-01 | `references/upstream-frontend-slides.md` | `- **每个演示都要内联 `viewport-base.css` 全文**。` | 14 | replace_line |

#### U-01 · `references/upstream-frontend-slides.md` L14 · replace_line

- **锚点（逐字）**：`- **每个演示都要内联 `viewport-base.css` 全文**。`
- **命中**：`grep -nF -e - **每个演示都要内联 `viewport-base.css` 全文**。 D:/global_skills/frontend-slides/references/upstream-frontend-slides.` ⇒ 行 [14] / PASS
- **现文**：
- **建议文**：
- **为什么必须同批**：上游增量是本技能正文明确要「一并读取」的分卷（SKILL.md:335）；不在此同步舞台实现件，两卷对同一件事就有两套说法。

### 2.9 不改清单（明确「别动」）

| file | 行 | 文本 | 结论 | 理由 |
|---|---|---|---|---|
| `SKILL.md` | 185 | `- `viewport-base.css` — Mandatory CSS (include in full)` | **KEEP** | 包 README:66 同样要求内联 viewport-base.css 全文，B 侧不改这条要求，只改该 CSS 文件自身的内容（V-01..V-10）。 |
| `SKILL.md` | 49 | `- Never negate CSS functions directly (...) — use calc(-1 * clamp(...))` | **KEEP** | 是 CSS 语法陷阱，与舞台范式无关。 |
| `SKILL.md` | 48 | `- Include `prefers-reduced-motion` support` | **KEEP** | 无障碍要求，两范式都适用。 |
| `SKILL.md` | 293 | `- A headless browser opens the presentation at 1920×1080 (standard widescreen)` | **KEEP** | 导出链本已按 1920×1080 工作，与 B 一致（不再需要改）。 |
| `bold-template-pack/README.md` | 66 | `- Include the full contents of `viewport-base.css`.` | **KEEP** | 包是本轮权威侧，保持逐字不动是可回滚与可审计的前提（也避免把迁移混成「改包+改正文」双面改动）。 |
| `references/upstream-frontend-slides.md` | 11 | `- **不要用响应式断点**为手机重排幻灯片内容；` | **KEEP** | 已与 B 一致，无需改。 |

---

## 3. 风险与回滚

| id | 风险 | 生成出的 HTML 会变什么样 | 缓解 | 回滚 | sev |
|---|---|---|---|---|---|
| K-01 | 生成物形态变化：新生成 deck 在手机/小窗不再重排，改为整台等比缩小 + 留黑边（letterbox/pillarbox） | 手机端单行文字实际渲染尺寸可能小于旧版 fluid（旧版在小屏是重排而非缩小） | 这是包 Implementation Contract 的显式要求（README:67-69）；如某场 deck 必须重排，应在 Phase 1 与用户确认后追加 .viewport-fluid 覆盖块，而不是回退 baseline | 按 hunk 回退本批 32 处 edit，或 rule_editor undo 最近一次提交 | MEDIUM |
| K-02 | viewport-base.css 是共享底座：STYLE_PRESETS 的 12 套非包路径也改用固定舞台（V-01/V-02 直接改 .slide） | 老用户拿新模板生成的 deck 与既有已生成 HTML 外观不一致（既有 HTML 内联的是旧副本，不受影响） | 已在 authority_choice.residual_caveat 写清：这是既定行为改变；仅影响此后新生成物 | 同 K-01；也可只回退 V-01..V-10 而保留正文声明（但会造成正文与内联 CSS 再次自相矛盾，不建议） | MEDIUM |
| K-03 | V-05 删除 88-138 行的 3 组 max-height 断点 + max-width:600px 网格堆叠 | 极矮/极窄视口下不再隐藏 nav-dots/keyboard-hint、不再把 .grid 堆成单列；改由整体缩放覆盖可读性 | deck-stage 的整体缩放在这些视口下等价于「等比变小」，属于包既定策略；若要保留移动端向导隐藏，应改为按 stage 缩放因子触发而非视口断点 | 按 hunk 还原 88-138 行（现文已在 edits[V-05].current 里逐字留存） | LOW |
| K-04 | 双翻页：html-template.md 自带 SlidePresentation 控制器（模板 :121 查询 .slide）与 deck-stage.js 自带 paging/tapzones 同时响应 | 方向键/触摸可能一次跳两页；进度条与 deck-stage 内部页号不同步 | H-04 注释在同批写明分工；render 验证项 V5 明确要求用真实键盘事件跑一页→一页；Phase 3 应二选一（用 deck-stage 内部 paging 时不实例化模板控制器） | 只回退 H-02/H-03（去掉 wrapper）或 H-04（保留注释分流） | HIGH |
| K-05 | 导出链交互：export-pdf.sh:209/230/267 以 document.querySelectorAll('.slide') 取页；deck-stage 用 <slot>，slide 仍在 light DOM（实测 deck-stage.js:341 仅把 slot 放进 shadow canvas），选择器仍能命中；但导出脚本按文档滚动逐页截屏，而 deck-stage 是内部翻页 | PDF 可能只截到第一页或重复同一页 | verify V6 要求实跑一次 export-pdf，逐页比对页数；若失败，改导出脚本改用 deck-stage 的 API/事件（scripts/ 改动不在本批，另立） | 回退 HTML wrapper 即可恢复旧导出路径 | HIGH |
| K-06 | SKILL.md 只是文档，本批不改任何运行时逻辑；生成物质量取决于代理是否照新正文执行 | 本批自身不产生 HTML，无运行时回归；但若只落 md 不改 SKILL.md（本任务禁止），行为不变 | 交付判据 V1-V4 以 grep/复算为主，行为变化由 K-01/K-04 的 render 判据覆盖 | 不适用（本任务只读） | LOW |

**回滚方式（两条通道）**：

1. **rule_editor undo**（受管根唯一写通道，r269 已实测）：r269 用的 `python A-memory-start/references/rule_editor.py insert ...` 每次落一份备份到 `D:\global_memory_archive\_trash\rule_backup\`，回滚即 `rule_editor` 的 undo/restore 指针回到该 `.bak`（r269 的备份件：`frontend-slides.SKILL.md.20261029_180538_466624.bak`，20,574 B）。
2. **按 hunk revert**：本方案每条 `current` 都是**逐字现文**（机器从磁盘切片，非手抄），因此可直接反向替换 `proposed → current` 复原；块级改动（V-05，88-138 行）亦已整块留存在 `edits[V-05].current`，无需重建。
3. **git**：受管根已纳管（r270，31 个恢复提交），可按单文件 `git revert`/`git checkout` 回退；本任务禁 git 写，仅登记通道。

---

## 4. 验证标准（改后必跑，含期望末行）

| id | 判什么 | 命令 | 期望末行 | 现状 |
|---|---|---|---|---|
| V0 | 锚点校验脚本有牙（负向对照） | `python 05-exec/r271_anchor_check.py 05-exec/r271_edits_spec_negctrl.json _temp/r271_anchor_hits_negctrl.json FAIL` | TOTAL checked=33 fails=1 verdict=FAIL expect=FAIL | ✅已实测 exit=0（NEG-01 hits=[]） |
| V1 | 32 条锚点逐条 grep 命中且行号唯一 | `python 05-exec/r271_anchor_check.py 05-exec/r271_edits_spec.json _temp/r271_anchor_hits.json PASS` | TOTAL checked=32 fails=0 verdict=PASS expect=PASS | ✅已实测 exit=0 |
| V2 | 改后正文不再把 100vh 当规则、且在盘包被正文点名 | `grep -nF "100vh" D:/global_skills/frontend-slides/SKILL.md; grep -cF "bold-template-pack" D:/global_skills/frontend-slides/SKILL.md` | 100vh 仅剩 1 处（历史注释 Note 行）；bold-template-pack 计数 >=3（baseline 1） | ⚠️未实测（迁移前） |
| V3 | 改后 viewport-base.css 无 viewport 尺寸残留 | `grep -nF -e "100dvh" -e "min(50vh" -e "min(80vh" -e "min(90vw" -e "RESPONSIVE BREAKPOINTS" D:/global_skills/frontend-slides/viewport-base.css` | 无输出（exit=1） | ⚠️未实测（迁移前） |
| V4 | 本仓 r268 未引用在盘件面复算（同口径同命令） | `python 05-exec/r268_unreferenced_siblings.py --json _temp/r271_r268_after.json && python -c "import json;r=[x for x in json.load(open('_temp/r271_r268_after.json',encoding='utf-8'))['rows'] if x['slug']=='frontend-slides'][0];print(r['unreferenced_n'],r['unreferenced'],r['unreferenced_strict_n'])"` | 1 ['meta.json'] 69（常规档保持 1；strict 69 不变，本迁移不主张改善该面） | ✅迁移前 baseline 已实测：1 ['meta.json'] 69 |
| V5 | 模板 wrapper 成对 + 组件常量正确 | `grep -c "<deck-stage" D:/global_skills/frontend-slides/html-template.md; grep -c "</deck-stage>" D:/global_skills/frontend-slides/html-template.md; grep -n "DESIGN_W_DEFAULT\|DESIGN_H_DEFAULT" D:/global_skills/frontend-slides/bold-template-pack/deck-stage.js` | 1 / 1 / 53:const DESIGN_W_DEFAULT = 1920; 54:const DESIGN_H_DEFAULT = 1080; | ⚠️部分实测（组件常量 ✅；wrapper 未改前为 0/0） |
| V6 | 渲染/导出行为（可读性 + 单页翻页 + 导出页数） | `bash scripts/export-pdf.sh <fixture.html> /tmp/r271.pdf && grep -c "/Type /Page" /tmp/r271.pdf` | 页数 == fixture 的 .slide 数（并另跑一次键盘事件：一按一键只前进一页） | ❌未实测（需 Playwright；本任务禁跑生成式流程且无 fixture） |

### 4.1 `grep` 指针数（正文对在盘件的可达性）

| 读数 | 迁移前（实测） | 迁移后期望 |
|---|---|---|
| `grep -cF "bold-template-pack" SKILL.md` | **1** | **≥3**（L187 登记 + L51 生成契约 + L326/L328 引用清单） |
| `grep -cF "deck-stage" SKILL.md` | **1** | **≥2**（新增 Supporting Files 行） |
| `grep -cF "100vh" SKILL.md` | **3**（L17/L43/L191） | **1**（仅剩 S-10 的历史注释行） |
| `grep -cF "100dvh" SKILL.md` | **1**（L43） | **0** |
| `grep -cF "NON-NEGOTIABLE" SKILL.md` | **3** | **2**（L17 的 Fixed Stage + 历史注释里的 Viewport Fitting） |
| `grep -nF -e "100dvh" -e "min(50vh" -e "min(80vh" -e "min(90vw)" -e "RESPONSIVE BREAKPOINTS" viewport-base.css` | 5 类命中 | **无输出（exit=1）** |

### 4.2 本仓 r268 未引用在盘件面复算

```bash
cd 自建skill优化
python 05-exec/r268_unreferenced_siblings.py --json _temp/r271_r268_after.json
python -c "import json;r=[x for x in json.load(open('_temp/r271_r268_after.json',encoding='utf-8'))['rows'] if x['slug']=='frontend-slides'][0];print(r['unreferenced_n'],r['unreferenced'],r['unreferenced_strict_n'])"
```

- **迁移前实测末行**：`1 ['meta.json'] 69`（✅ 本轮已复算；baseline 落盘 `skill焚诀/_temp/r271_r268_recheck_before.json`，同件亦在 `自建skill优化/_temp/`）。
- **迁移后期望**：`1 ['meta.json'] 69`（常规档不劣化；`bold-template-pack` 三件已在 r269 离开常规清单）。
- **口径告诫（承接 r269 复核）**：常规档/strict 档对同一改动给出 **1–72 件**的不同改善量，读数必须带口径名；本件只主张「常规档 ≤1、包三件不在清单」。

### 4.3 render / 预览类判据

- **V5 静态**：`grep -c "<deck-stage" html-template.md` = 1、`grep -c "</deck-stage>"` = 1（成对）；`deck-stage.js` 常量 1920/1080。⚠️ 组件常量已实测，wrapper 未改前为 0/0。
- **V6 动态**：`bash scripts/export-pdf.sh <fixture.html> /tmp/r271.pdf` 后核对 PDF 页数 == fixture 的 `.slide` 数；另用真实键盘事件验收「一键只前进一页」（针对 K-04 双翻页，**改后第一优先**）。
- **V6 现状**：❌未实测 —— 需 Playwright 浏览器与一份 fixture HTML，本任务为只读分析且无 fixture，故只给判据不给结论。

---

## 5. 负向对照（证明校验有牙）· 两条腿实测

校验器：`05-exec/r271_anchor_check.py`（逐锚点调用 `grep -nF -e <anchor> <file>`，argv 传参，无 shell 引用面）。

**腿 1 —— 正向（真锚点）**：

```bash
cd 自建skill优化 && python 05-exec/r271_anchor_check.py 05-exec/r271_edits_spec.json _temp/r271_anchor_hits.json PASS
```

实测末行：`TOTAL checked=32 fails=0 verdict=PASS expect=PASS`，`EXIT1=0`（32/32 全部 `PASS line=[N]`）。

**腿 2 —— 负向（故意注入不存在的锚点）**：

```bash
cd 自建skill优化 && python 05-exec/r271_anchor_check.py 05-exec/r271_edits_spec_negctrl.json _temp/r271_anchor_hits_negctrl.json FAIL
```

实测逐字（关键两行）：

```text
FAIL line=[] NEG-01 :: ZZZ_NEGATIVE_CONTROL_ANCHOR_9f3a_NOT_IN_ANY_FILE
TOTAL checked=33 fails=1 verdict=FAIL expect=FAIL
```
`EXIT2=0` ⇒ 校验器在「锚点不存在」时确实报 FAIL（不是恒绿）。另：负控锚点在全部 5 个受检文件里的命中数 = 0（`NEGCTRL-ABSENT-OK hits=0`）。

> **诚实记录**：首次跑校验时 `U-01`（上游增量卷第 14 行）**真的 FAIL 过一次** —— 我漏了该行的 `**…**` 粗体标记；修正锚点为 `- **每个演示都要内联 \`viewport-base.css\` 全文**。` 后转 PASS。这条恰好是「锚点必须实读、不得凭记忆」的自证。

---

## 6. 实测证据命令汇（本件所有断言的复跑入口）

```bash
# ① 锚点两条腿（见 §5）
python 05-exec/r271_anchor_check.py 05-exec/r271_edits_spec.json _temp/r271_anchor_hits.json PASS
python 05-exec/r271_anchor_check.py 05-exec/r271_edits_spec_negctrl.json _temp/r271_anchor_hits_negctrl.json FAIL

# ② 权威证据
grep -rl "fixed 1920×1080 stage" 'D:/global_skills/frontend-slides/bold-template-pack/templates' --include=design.md | wc -l   # 34
grep -n "DESIGN_W_DEFAULT\|DESIGN_H_DEFAULT" D:/global_skills/frontend-slides/bold-template-pack/deck-stage.js
sed -n '36,39p' D:/global_skills/frontend-slides/scripts/export-pdf.sh
sed -n '6,14p' D:/global_skills/frontend-slides/references/upstream-frontend-slides.md

# ③ 指针数 baseline
for p in bold-template-pack deck-stage viewport-base.css 100vh 100dvh NON-NEGOTIABLE; do printf '%s: ' "$p"; grep -cF -- "$p" D:/global_skills/frontend-slides/SKILL.md; done

# ④ r268 在盘件面复算
cd 自建skill优化 && python 05-exec/r268_unreferenced_siblings.py --json _temp/r271_r268_recheck_before.json
```

---

## 7. 结论标记（逐条）

| 结论 | 标记 |
|---|---|
| 推荐权威 = B（固定 1920×1080 舞台），依据 34/34 模板 + 组件常量 + 本仓增量卷 + 导出链 | ✅已实测 |
| 32 条改法锚点逐条 `grep -nF` 唯一命中（行号 17/39/43/44/46/47/51/83/189/191/192/198/326/328/339/5/4；CSS 20/21/22/18/89/41/60/61/84/14；模板 57/101/115/121；增量卷 14） | ✅已实测 |
| 负向对照报 FAIL、正向量 PASS | ✅已实测 |
| baseline sha256 / 21,260 B / r268 常规档 1 / strict 69 | ✅已实测 |
| 包文件可读（`bold-template-pack/README.md` 3,308 B、77 行；34 套模板；`deck-stage.js` 22,748 B） | ✅已实测（无 UNVERIFIED） |
| 改后指针数、CSS 残留、wrapper 成对 | ⚠️部分实测（V5 组件常量已测；其余为迁移后判据，迁移前不可测） |
| render / 导出页数 / 单页翻页 | ❌未实测（需 Playwright + fixture；本任务只读，仅给判据） |
| `viewport-base.css` 属共享底座、12 套 STYLE_PRESETS 一并变固定舞台 | ⚠️已从文件事实推得（同文件 `.slide` 是全局选择器），未跑真实 deck 渲染 |

**退路执行情况**：本次**未触发** UNVERIFIED 退路 —— `D:/global_skills/frontend-slides/bold-template-pack/README.md`（3,308 B）、`deck-stage.js`（22,748 B）、34 套模板均可读，实测命令 `ls -la D:/global_skills/frontend-slides/bold-template-pack/` 见 §6 口径。

