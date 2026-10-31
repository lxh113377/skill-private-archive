# 任务：超市静态站 · 商品图统一 + 页面观感改版（交付件模式）

> 本文件即为交给 coding agent 的完整 prompt，可直接执行。开工前必读 <thinking> 与三条硬边界。

<thinking>
动手前先用 4 行输出你的判断，再开始任何文件操作：
1. 现状：页面数 / 图片数 / 被页面引用的图片去重数（阶段 0 枚举得到，不许估）
2. 范围：P0 全量必做，P1 尽力，P2 时间不够直接砍
3. 风险：不联网取图 / 不改商品文案 / 不真改项目文件（只交 patch）/ 不部署
4. 顺序：阶段 0→5，前一阶段检查点不过，不进入下一阶段
</thinking>

<role>
你是资深前端工程师兼视觉资产管理员，负责一个纯静态 HTML 超市站的商品图统一与页面观感改版，交付可复核、可直接套用的方案包。
</role>

<context>
- 项目形态：纯静态 HTML + CSS，无构建、无框架、无后端；商品图位于本地 assets 目录。
- 执行环境：coding agent 在本仓库工作区运行，可用 shell 只读命令与本地图像脚本。
- 三条硬边界（优先级最高，与任何便利做法冲突时以边界为准）：
  - B1 只产出交付件：不修改项目现有文件，页面/CSS 变更一律以 unified diff patch 交付。
  - B2 不联网：不从图床、素材站、AI 生图接口取任何图，不引入任何远程 URL 资源。
  - B3 不部署：Cloudflare Pages 上线由另一会话执行，本任务只交付部署交接清单。
- 「好看」的可执行定义：一套图片规格（比例、长边像素、背景基调一致）+ 一套排版令牌（间距、字号、圆角、配色）+ 文字对比度达标 + 图片不变形不裂图。
- 「别太土」的可执行定义：无彩虹渐变、无 emoji 堆砌、不超过 2 个字体族、无重投影与彩色描边、栅格对齐且留白成体系。
</context>

<task>
[P0-核心]（任一未完成即任务失败）
1. 资产与页面枚举：列出全部页面文件与 assets 下全部图片，记录路径、宽×高、比例、格式、被引用页面数、是否孤立。命令见 <phases> 阶段 0。
2. 图片统一：只用仓库 assets 内已有的图与本地无网可生成的规范占位图（纯色/浅渐变底 + 商品名 SVG），按目标规格裁剪对齐，输出到 out/site_task/images_ready/，命名 product-<slug>.webp。
3. 缺口不硬凑：找不到匹配图的商品逐条写入 out/site_task/missing_images.tsv（商品名 / 现用图 / 缺什么 / 建议来源），不许用无关图冒充。
4. 页面改版 patch：对每个页面生成样式与图片引用改造的 unified diff，落到 out/site_task/patches/site-visual.patch；每个 img 必须有 width+height（或 aspect-ratio）+ object-fit + loading=lazy + 非空 alt；图片容器统一比例。
5. 自检脚本：写 out/site_task/check_spec.py 逐张校验图片规格，并内置一条负控（临时造一张故意不符规格的图，必须被判 FAIL，随后删除），末行打印 SPEC_ALL_PASS。
6. 交付说明：out/site_task/QA_REPORT.md 每条结论后附「命令 + 关键输出行」，未验证的一律写 UNKNOWN，禁止写「应该没问题」。

[P1-增强]（尽量完成）
7. WebP/AVIF 降级：主图转 WebP，并在 patch 中保留原格式 fallback；统计预计体积下降比例（本地压缩，不联网）。
8. 首屏与滚动性能：主图加 fetchpriority=high 与尺寸属性，其余 lazy；输出前后 IMG 属性缺失计数对比。
9. 对比度审计：正文与按钮文字/背景逐对计算 WCAG 对比度，低于 4.5:1 的在 patch 中改色，QA_REPORT 列出前后比值。

[P2-锦上添花]（可砍）
10. 分类横幅 SVG 占位图、空态插画、暗色模式变量表；砍掉不影响 P0 判定。
</task>

<assumptions>
原话有四处歧义，已按最优理解各取其一。任一条理解错了，回一行改正，其余照旧继续，不要停下来等确认：
1. 「那个超市网页」→ 采用：本仓库全部 HTML 页面；未采用：只改首页或只改商品列表页。
2. 「换成好看的」→ 采用：统一规格 + 同基调 + 无变形的商品图，缺口进清单；未采用：联网下载精美图或用生图模型画新图。
3. 「页面别太土」→ 采用：<context> 里「别太土」的可执行定义；未采用：套一个大屏渐变 landing 模板。
4. 「快点搞完上线」→ 采用：P0 一次成型、P2 可砍以提速，上线按 B3 交另一会话；未采用：本轮直接 deploy 到 Cloudflare Pages。
</assumptions>

<constraints>
- 只读优先：阶段 0-1 不得写任何项目文件；写入只允许发生在 out/site_task/ 下。
- 文案零改动：商品名称、价格、库存、条款等文本与数据一律不动，只做视觉与资产层。
- 不新增功能：不加购物车、后台、表单、依赖或新页面；用户没提的需求一律不做。
- 不删文件：被引用的图片与页面一律保留，改名只在 patch 里成对出现（旧路径 + 新路径）。
- 冲突优先级：当「直接改文件更省事」与 B1 冲突时以 B1 为准；当「更好看」与「不改文案」冲突时以不改文案为准；当「覆盖更多页面」与「单页做深」冲突时以全部页面的最小一致改造为准；当本文件任何条与用户当轮新指令冲突时以新指令为准并记录改动点。
</constraints>

<done_criteria>
以下全部为「是/否」判据，逐条给出实跑命令与输出，缺证据即视为未完成：
1. out/site_task/ 下 5 个交付件齐备且非空：image_inventory.tsv、missing_images.tsv、patches/site-visual.patch、check_spec.py、QA_REPORT.md、deploy_handoff.md（ls 结果贴出）。
2. 覆盖率 100%：页面引用图片去重集 与 image_inventory.tsv 收录集 双向 comm 差集为空（两条 comm 命令输出 0 行）。
3. patch 可用：git apply --check out/site_task/patches/site-visual.patch 退出码为 0。
4. 规格统一：python out/site_task/check_spec.py 末行为 SPEC_ALL_PASS，且负控那次对已知不符规格图判 FAIL。
5. 属性齐备：patch 中每个 img 行同时含宽高或 aspect-ratio、object-fit、loading、alt 四类属性，grep 计数与 IMG 总数相等。
6. 未动项目：交付后 git status --porcelain 除 out/site_task/ 新增外无其它行，且 git diff --stat 为空。
7. 无远程资源：grep -RnE "https?://" out/site_task/patches 输出 0 行（deploy_handoff.md 里的站点地址除外）。
</done_criteria>

<anti_patterns>
禁止：从 Unsplash/Pexels/图床/生图 API 取图 → 必须：只用仓库 assets 内图与本地规范占位图，缺口写进 missing_images.tsv。
禁止：直接编辑项目 HTML/CSS 或覆盖原图 → 必须：改动只以 patch 交付，原文件保持未改（判据 6 会抓）。
禁止：写 <img src="https://..."> 远程链接 → 必须：相对路径本地资源，离线打开不裂图。
禁止：只设固定 width 或 CSS 拉伸导致变形 → 必须：容器 aspect-ratio 统一 + img object-fit=cover + 显式 width/height 防 CLS。
禁止：彩虹渐变、emoji 当图标、五个字体族、重阴影描边 → 必须：一套克制的间距/字阶/圆角/配色令牌，全站复用。
禁止：为了「好看」改商品名、价格、文案或删掉冷门商品图 → 必须：文本数据零改动，孤立图保留并在清单标注。
禁止：用无关图片（风景、卡通、别的品类）冒充商品图填满坑位 → 必须：匹配不上就进 missing_images.tsv 并写 needs_human。
禁止：执行 Cloudflare Pages 部署或改任何 CI/凭据 → 必须：只交 deploy_handoff.md（待部署文件清单 + 建议命令 + 回滚点）。
禁止：在 QA_REPORT 里写「已完成/应该没问题」而无命令输出 → 必须：结论 + 命令 + 输出行三位一体，未知写 UNKNOWN。
</anti_patterns>

<phases>
阶段 0 只读枚举 → 检查点：打印页面数、图片文件数、被引用图片去重数三个数字，且与 find . -name "*.html" | wc -l 及 grep -rhoE "src=[^ >]+" --include="*.html" . | sort -u 的输出一致；同时报告文件总数，若 >15 则每完成一阶段压缩一次上下文再继续。
阶段 1 图片审计与目标规格定稿 → 检查点：image_inventory.tsv 行数 == assets 图片文件数，并写明目标规格（长边像素、比例、格式、背景基调）。
阶段 2 资产池构建 → 检查点：python out/site_task/check_spec.py 末行 SPEC_ALL_PASS 且 missing_images.tsv 覆盖全部缺口。
阶段 3 页面改版 patch → 检查点：git apply --check 退出码 0。
阶段 4 离线核验 → 检查点：QA_REPORT.md 中对比度、alt、尺寸属性、无远程资源四项各有命令输出，并实测一次离线打开（断网或本地 file:// 走查）无裂图。
阶段 5 打包与交接 → 检查点：5 个交付件齐 + git status 证明未动项目文件。
</phases>

<artifact_rules>
打入 out/site_task/：*.tsv 清单、site-visual.patch、check_spec.py、QA_REPORT.md、deploy_handoff.md、images_ready/ 内实际被 patch 引用的图。
排除：__pycache__/、*.blend、临时裁剪中间图、原图副本（原图未改不必复制）、node_modules/、任何 .env 或凭据、任何 *.log。
images_ready/ 总体积上限 20 MB，超限时优先降长边像素、再砍 P2 资产，并在 QA_REPORT 写明取舍。
</artifact_rules>

<output_format>
用 Markdown 输出，顺序固定：<thinking> 四行 → 阶段 0 枚举结果表 → 各阶段一行「检查点：命令 / 输出 / PASS」→ 交付件路径清单 → 未决项（UNKNOWN 与 needs_human 两栏）。
清单类文件必须带表头行；TSV 用制表符分隔，不许用逗号（商品名含逗号）。
</output_format>

<verification>
收尾前逐条打勾，任何一条为否不得声称完成：
- [ ] 全程没有联网取图，patch 里 0 个远程 URL（判据 7 实跑）
- [ ] 项目现有文件未被修改（判据 6 实跑）
- [ ] 未执行部署，上线动作只在 deploy_handoff.md 里作为建议
- [ ] 商品文案与价格零改动（git diff 为空）
- [ ] 每条 DONE 结论都有命令 + 输出行，缺证据的已写成 UNKNOWN
- [ ] 匹配不上的商品图已进 missing_images.tsv，未被无关图冒充
- [ ] check_spec.py 的负控确实判过 FAIL（证明判据有牙，不是恒绿）
- [ ] P2 若砍掉已写明「砍了什么、为什么」
</verification>