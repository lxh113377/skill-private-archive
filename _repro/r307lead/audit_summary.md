# r307 · Lead 件 #3：季档巡检面来源审查 + r113 离线全链复跑（读数汇总）

## 一、来源审查：面里 4 件、green 是谁喂的
| 件 | schema | generated_at | git 提交（谁产的） |
|---|---|---|---|
| quarterly/2026Q4 | quarterly-skill-audit-v1 | 2026-10-25 | a366ed6（r230） |
| quarterly_r260/2026Q4 | 同上 | 2026-10-28 01:11 | 336c68a（r260） |
| quarterly_r260b/2026Q4 | 同上 | 2026-10-28 15:03 | 336c68a（r260） |
| quarterly_r260c/2026Q4 | 同上 | 2026-10-28 16:26 | 373a038（r260c） |

结论：**四件全是 r113 本体的真产物**（schema 同一；r260* 三件是 r260 系列轮用 --out-dir 落的预览跑，且都入库过）。
看门狗取最新=10-28 真跑 ⇒ [CADENCE:PASS]（龄期 3.0 天 ≤ 100）的 green 是**真的**，不是外来件喂的。
r305a 担心的冒充通道已被命名隔离：version_scan 不匹配 quarterly* 通配（fnmatch False/True 复证在 r305 台账 R305-1）。
残留口径模糊（登记、不判红）：预览件与正牌季档同 schema 同面 ⇒ 人读「面里最新」分不清正牌；新增季档请落正牌目录。

## 二、r113 离线全链今日复跑（链通证明）
命令：python 05-exec/r113_quarterly_audit.py --offline --no-side-write --out-dir _repro/r307lead/r113_preview
末行：[QUARTERLY:PASS] 产物=_repro\r307lead\r113.json ｜ 19 步全通过 ｜ 上游元数据 OK=11 UNVERIFIED=0
注：--no-side-write 的预览跑**不**生成 out-dir 下的 audit.json（实测 NO）⇒ 预览模式的三处写面改写行为与文档自述一致，
正牌季档未被本轮任何动作触碰（quarterly/2026Q4 仍 10-25、git 仍 a366ed6）。

## 三、SOP 接线（已落维护规范件 r307 附节）
三层动线：① r113 深审（新鲜度权威）② r303a 吸收基准比较器（UPSTREAM_CHANGED 进当季候选）③ r304a 版本扫描（刻意在面外）；
外加换装季义务：改受管根件跑覆盖它的 spec（现 4 件）/ 主动升级后重生成吸收基准 / 注册表 lag 由合规提交带走且 lag 读数带观测时刻。

## 四、F 臂 4 个卡点的当场复核（推翻 r304/r305 的两条「环境受阻」）

背景：r305b 计划把 frontend-skill 的 4 件判「卡住」（inspect.mjs 无 Chrome / assets.mjs 网络超时 / 2 条引用待补取）。
r307 我把可运行的两件放进**真目录结构**（scripts/ + scripts/lib/，从 B1 取回件复制）实测：

| 卡点 | r304/r305 的说法 | r307 实测 | 结论 |
|---|---|---|---|
| inspect.mjs | rc=1 本机无 Chrome | **能跑**：它 import lib/cdp.mjs，cdp 的候选清单含 msedge（本机 Program Files (x86) 有 Edge），
|  |  | 对极简页实测：三视口量测 + 7 张截图 + report.json 全出；rc=1 是设计语义 = process.exit(fails.length?1:0)（我的页有 1 FAIL） | **假卡点**：
|  |  | 当时要么缺 lib/ 结构要么误读了浏览器检测（报错原文是 No Chrome/Edge/Chromium found. …set CHROME_PATH） | 脚本可运行 |
| assets.mjs | rc=124 网络超时 | 无参 rc=2 = 用法提示（Give a search query）；带参才联网检索 | **半真**：脚本本体可跑，
|  |  |  | 网络只是取图时依赖（不是不可用性） |
| charts.js / base.js | 待补取 | B1 已取回（59,016B / 2,162B，blob 钉死） | **已解** |

⇒ F 臂 4 个 block 实测解了 3 个（2 取数 + inspect）；剩 assets.mjs 属「联网时才依赖网络」的正常语义。
⇒ **需求 4 的时间节点面更新**：F 臂（frontend-skill，T1 档）的换装**不再有硬环境卡点**，只等 B1 的合并编辑清单与我落地。
⇒ 教训一条（自记）：**脚本 rc!=0 别直接记「环境受阻」——先读它的退出语义与依赖结构**（r304 我把「缺 lib/ 目录的单文件跑法」
   和「有 FAIL findings 的正常 rc=1」都当成了不可用，差点让第二件换装多挂一季）。
