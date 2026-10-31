# r322a · 嵌套 SKILL.md 闭包审计（Lead 自干，臂全灭后按 #44⑦ 接管闸门问题）

> 臂两次派出两次全灭（provider 切换窗口零产出），闸门问题 Lead 自答；判据脚本与读数全部可复算。

## 1. 规模事实（git ls-tree -r --name-only HEAD @ e8f489ebcf78）

- 全树 SKILL.md 共 **244** 个：顶层 **191**（与在册名册 191 一致 ⇒ 名册口径 = 顶层入口），嵌套 **53**。
- 有嵌套入口的件只有 **3 个**：`cloudbase`(32) / `gstack`(20) / `frontend-slides`(1)。

## 2. 分发面事实（回答「嵌套件会不会被拿到」）

- 镜像根 `C:/Users/37533/.agents/skills/gstack/` 下 **qa/SKILL.md、review/SKILL.md、browse/SKILL.md 等 19+ 个嵌套入口被同步分发**（readdir 递归现取）⇒ 嵌套件作为**子技能树**随件分发是既有形态。
- 本会话技能目录（DSH available_skills）只列 `gstack` 一个顶层条目 ⇒ 嵌套件**不是**独立注册的会话入口。

## 3. gstack 六个「孤儿」的嵌套可达性（逐件 grep -F basename）

| 孤儿 | 被谁引用 | 判定 |
|---|---|---|
| qa/references/issue-taxonomy.md | qa/SKILL.md | 嵌套可达 |
| qa/templates/qa-report-template.md | qa/SKILL.md | 嵌套可达 |
| review/checklist.md | review/SKILL.md + .tmpl | 嵌套可达 |
| review/design-checklist.md | review/SKILL.md | 嵌套可达 |
| review/greptile-triage.md | review/SKILL.md + .tmpl | 嵌套可达 |
| review/TODOS-format.md | 无 SKILL.md 引用 | **唯一真孤儿**（其目录 siblings 全被 review/SKILL.md 引用 ⇒ 结构上同目录可达，处置 = 给一句枚举规则，不是逐字挂链） |

⇒ **gstack 6 个孤儿里 5 个是嵌套闭包假象、1 个近假**。普查 `check_r319a.py` 的闭包只从顶层 SKILL.md 展开 = 第三层口径缺陷（P-4）。

## 4. 大件不受影响（批次表不用重算）

ppt-master / story-setup / story-long-write **均无嵌套 SKILL.md**（各件入口数 by=1），其 171/132/96 个孤儿全部保持「真孤儿」判定；顶层到嵌套入口的引用数 gstack=1、其余=0。
⇒ r321 批次表的 259 逐条下界**维持**（gstack 的 6 件从 B6 摘出后约 253）。

## 5. loader 结论

- **结构面**：嵌套入口被镜像分发（一手 readdir）；**注册面**：会话目录不单列嵌套件（一手 catalog）；**运行面**：路由是否在加载 gstack 后进一步吃嵌套 SKILL.md —— 本轮 UNVERIFIED（A-skill-manager / A-memory-start 引用面 grep 未找到钉死行为的注册表文件；**缺证据记缺口，不读成否定**）。
- 因此处置保守：普查 v2 加 `--closure nested` 口径给**结构可达**读数；运行面裁决留给带 router 源码的一轮。

## 6. 取证自身偏差

- grep 用 basename/stem 双形态，可能把「同名文件在别的目录」误判为可达（已用逐字路径 grep 复核 5 条全为路径级引用；TODOS-format 是 basename 级 ⇒ 已单列）。
- cloudbase 的 32 个嵌套件未做 fake-orphan 逐条审计（不在 52 件吸收名册、不在普查面）。
- 三臂两次全灭的教训：provider 切换窗口派发零产出且无收尾消息；按 #44⑦ Lead 自干闸门问题、缩范围重派 B/C 两臂。
