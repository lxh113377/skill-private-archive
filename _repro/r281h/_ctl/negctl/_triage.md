# _triage.md - SKILL.md 第 1 步「Triage」的书面裁定（臂 A，自行裁定，不回抛）

文档依据：本臂权威副本 `_temp/r281h/A/SKILL.md:16-23`（§1 Triage 列四问 + 「全部都要」条款）。
原文是「Ask only what you must」；本轮为受控实验、无提问对象，故四项全部自行裁定并写明理由。
任务文本（两臂一致）：为一个内部数据分析后台 dashboard 产出 UI/UX 设计系统，并保存成可跨会话取用的文件。

## 1. 平台（web / iOS / Android / desktop）

**裁定：web（桌面优先的内部浏览器应用），不是 iOS/Android/desktop 原生。**
理由：「内部数据分析后台」的交付形态是浏览器里的管理后台；本地数据也支持这一选择 ——
`ux-guidelines.csv:65`（Mobile First，Platform 列 = `Web`）与 `ux-guidelines.csv:51`（Font Loading，Platform = `Web`）`[CSV]`，
且 `web-interface.csv` 整表 Platform 列均为 `Web`（`web-interface.csv:4`、`web-interface.csv:16`）`[CSV]`。
推论：窄屏只做「不破版」级适配，主设计目标是 1440px / 1536px 大屏（见 TOKENS.md §5）。
触控底线（44px 目标、8px 间距）仍保留，用于平板与触屏会议室场景，依据 `ux-guidelines.csv:23` 与 `ux-guidelines.csv:24` `[CSV]`。

## 2. 栈（Stack, if code changes）

**裁定：React 18 + TypeScript + Tailwind CSS + CSS custom properties（`--token`）作令牌层；图表库 Recharts。**
理由（三条各自有本地出处）：
- 图表库：`styles.csv:29`（Data-Dense Dashboard 行）`Library Recommendation` 列 = `Recharts 9/10, Chart.js 9/10, D3.js 10/10` `[CSV]`，取工程上最省事的 Recharts。
- Tailwind：`scripts/core.py:86` 的 `STACK_CONFIG` 登记了 `html-tailwind`，其数据行直接给出本设计系统要用的类（`stacks/html-tailwind.csv:31` mobile-first `md: lg: xl:`；`stacks/html-tailwind.csv:32` 断点集）`[CSV]`，令牌可一比一映射进 `tailwind.config`。
- CSS 变量作令牌层：`styles.csv:29` 的 `Design System Variables` 列本身就是 `--grid-gap: 8px, --card-padding: 12px` 这种形态 `[CSV]`，与生成器写出的 `MASTER.md:19-25` 的 `--color-*` 表同构 `[GEN]`，无需另造格式。
- 不裁定为 shadcn：任务未给既有仓库，选它会把令牌绑到它的主题结构上，属无依据约束 `[J]` 设计判断（无本地出处）。

## 3. 目标与约束（Goal and constraints）

**裁定目标（优先级高→低）：读数准确 > 筛选与对比效率 > 长时可用性（夜班） > 转化率。**
理由：SKILL.md:20 把 conversion 列为默认目标之一，但内部分析后台没有转化漏斗可优化 ——
本地 BI 行 `styles.csv:29` 的 `Best For` = `Business intelligence dashboards, financial analytics, enterprise reporting, operational dashboards, data warehousing`，
同行 `Avoid`（Not Best For）列明确排除 `Marketing dashboards, consumer-facing analytics, simple reporting` `[CSV]`。
故把「转化率」降级，改测**首次读数时间**与**筛选成功率**两类指标 `[J]` 设计判断（无本地出处）。
约束：
- 高信息密度：`pages/dashboard.md:22` = `Content Density: High - optimize for information display` `[GEN]`；卡片内边距上限 12px（`styles.csv:29` `minimal padding (8-12px)`）`[CSV]`。
- 内部工具 ⇒ 允许暗色夜班主题，但暗色必须是同一套语义令牌的换值，不是第二套设计（TOKENS.md §1.4）。
- 令牌名 ASCII：SKILL.md:49 要求 default to ASCII-only tokens/variables。本设计系统令牌名全 ASCII；
  `MASTER.md` / `pages` 里的 emoji（⚡ ✓ ◐ ✗ ❌）是 CSV 原文与生成器自带输出，本臂未新增 `[GEN]`/`[CSV]`。
- 反模式沿用生成器判定：`MASTER.md:176-177`（Ornate design / No filtering）`[GEN]`。

## 4. WCAG 等级

**裁定：AA 为硬门槛（正文与标签 >=4.5:1，图形与控件边界 >=3:1），AAA 作「可达到即用」，不承诺全站 AAA。**
理由：本地 BI 行自身 `Accessibility` 列 = `✓ WCAG AA`（`styles.csv:29`、`styles.csv:31`、`styles.csv:34`）`[CSV]`；
文字底线出处 `ux-guidelines.csv:37` = `Minimum 4.5:1 ratio for normal text` `[CSV]`；
图形与控件 3:1 是 WCAG 2.1 SC 1.4.11（non-text contrast）既有要求，本仓 `data/data-provenance.json:938`
即指向 `https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast` `[CSV]`。
不做全站 AAA 的理由：AAA 只在 `styles.csv:37`（Financial，`✓ WCAG AAA`）与 `styles.csv:51`（Swiss）被个别行声明，
BI 分析行自述是 AA；把 AAA 当硬门会迫使暗色与图表色板整体降饱和，代价大于收益 `[J]` 设计判断（无本地出处）。
执行方式：所有对比度断言由臂内 `_evidence*.py` 实测（139 次比值计算，见 CONTRAST-AUDIT.md）。
生成器自带的三处不达标值（白字压 `#F59E0B` = 2.15、focus halo `#1E40AF20` 合成后 = 1.23、input 边框 `#E2E8F0` = 1.23）
已替换并留痕，不是「改完当作没问题」。

## 5. 已有素材（screenshot / Figma / repo / URL / user journey）

**裁定：无真实产品素材。只有 (a) 任务文本一句话、(b) 本地 CSV 知识库、(c) 生成器脚本、(d) 本臂文档副本。**
可用素材清单（全部只读，本臂已实测取数）：
- `D:/global_skills/ui-ux-pro-max/data/`：23 个活 CSV + `stacks/` 22 个栈 CSV（`scripts/core.py:22-83` CSV_CONFIG 12 域；`scripts/core.py:85-111` STACK_CONFIG 22 栈）
- 本臂实际取数并逐值引用过的行：`colors.csv`（:9 / :10 / :15 / :27 / :33 / :37 / :39 / :43 / :53 / :54 / :63 / :66 / :67 / :68 / :69 / :71）、
  `styles.csv`（:29 / :30 / :31 / :32 / :33 / :34 / :35 / :36 / :37 / :40 / :47 / :51）、`typography.csv`（:43 / :48 / :49 / :52）、
  `ux-guidelines.csv`（:4 / :10 / :11 / :23 / :24 / :29 / :32 / :33 / :37 / :62 / :65 / :66 / :68 / :73 / :75 / :77 / :79 / :80）、
  `web-interface.csv`（:4 / :16）、`charts.csv`（:2 / :5 / :14 / :25）、`motion.csv`（:3）、`stacks/html-tailwind.csv`（:5 / :29 / :31 / :32 / :39）、`data-provenance.json`（:938）
- 脚本：`scripts/search.py`（111 行）、`scripts/design_system.py`（1071 行）、`scripts/core.py`（280 行）
- **缺口（如实记录）**：没有真实 dashboard 截图、没有 Figma、没有代码仓、没有用户旅程数据。
  故实现计划（SKILL.md:31 的第 4 类）只能到「取用顺序 + 再生成命令 + 判据」，给不出逐文件 diff `[J]`。

## 6. 交付拆分（SKILL.md:23「全部都要」= 四类，按序出）

| SKILL.md 类别（:25-31） | 本臂载体 |
|------------------------|----------|
| UI concept + layout | `design-system/internal-data-dashboard/pages/dashboard.md`（12 栅 / 1400px / 高密度）+ `TOKENS.md` §2 组件几何、§5 断点栅格 |
| UX flow | `TOKENS.md` §4 状态矩阵（default/hover/focus/disabled/loading/error/empty 逐组件）+ 关键路径失败态规定 |
| Design system | `MASTER.md`（生成器产出）+ `TOKENS.md`（五类完整数值令牌）+ `CONTRAST-AUDIT.md`（实测判据） |
| Implementation plan | `README.md`（取用顺序、再生成命令、`--page` 上游 bug 的绕行包装器、验收判据与负向对照） |

回滚方式：本臂全部产物只在 `_temp/r281h/A/` 下新建，删该目录即完全回滚；`D:/global_skills` 未写入任何字节；未做 git 写。
