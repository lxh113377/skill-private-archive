# A族精读审计卡（阶段2 第 1 批）

> 生成：2026-09-14 | 方式：code-explorer 子代理只读精读（文件枚举 + 全文/关键章节读取 + 跨目录路径存在性核验）
> 范围：`A-project-handoff` / `A-memory-start` / `A-get-memory` / `A-prompt-better` / `A-ask-questions`
> 证据口径：行号来自 `D:\global_skills\<skill>\SKILL.md` 实测输出；体积为实测字节

---

### A-project-handoff

**体积与结构**: SKILL.md=84,818 B | references 文件数=0（实为 `scripts/`：handoff.py 169.16 KB / noise_lint.py 15.01 KB / templates/ 8 个 .tmpl） | 分卷=否（全库 `*.part*.md` 实测 0 命中） | 超 4KB 硬上限=**是（20.7 倍）** | 章节 35（716 行），最大章节「命令执行方式」261-601 行（340 行）

**触发与路由**: description≈68 字 | 触发词质量=优（`triggers:` 10 个中英双语，:4-14） | version/name=是（`version: 3.22.0`，:17）

**死链与过时引用**: 无死链（引用的 scripts/handoff.py、noise_lint.py、templates/*.tmpl、check-skill-mirror.ps1、eval/workflow_gate.py 均实测存在）。过时平台名：**CC**（:124、:142「OC/WB/CC/TC」），与 A-memory-start:134「CC 已弃用 2026-09-08」冲突。

**重复与冲突**: ①版本漂移 frontmatter `3.22.0`(:17) vs 历史最新 V3.35.0(:670)，**差 13 个版本**；②版本历史乱序 :698-706 且 :677==:678 整行重复；③自认 noise_lint 双副本需两处同步 allowlist(:143)；④与 A-get-memory 在项目续接、4KB 拆卷上重叠。

**工作流闭环**: 门禁命令=有(:713) | 七步闭环=**无**（「七步」0 命中） | footer 协议=**无**（0 命中） | 版本历史行=有(:669)

**问题清单**:
- [P0] 主文件 84,818 B 超 4KB 硬上限 20.7 倍，且无 references 分卷
- [P0] 双标：本 skill 用 `split` 强制他处 4KB 拆卷(:553)，自身主文件从未拆卷
- [P1] frontmatter version 3.22.0 与版本历史 V3.35.0 漂移 13 个版本（:17 vs :670）
- [P1] 版本历史顺序错乱且 V3.28.0 整行重复（:698-706；:677==:678）
- [P1] 已弃用平台名 CC 仍写在两条纪律里（:124、:142）
- [P2] 未声明七步闭环与 footer 协议
- [P2] scripts/handoff.py 169.16 KB 单文件巨石

**整改建议**:
1. 新建 `references/`，把 18 条致命纪律 + 14 子命令按 partN 拆出，主文件留指针（≤4KB）
2. :17 改 `version: 3.35.0`；删除 :678 重复行并按版本号重排 :698-706
3. :124/:142 的 `OC/WB/CC/TC` 改为 `OC/WB/TR/CX`

---

### A-memory-start

**体积与结构**: SKILL.md=36,065 B | references 文件数=9（contract.md 34.47 KB / detail_archive.md / multi_agent_collab.md / prompt_optimizer.md / reply_footer.md / rule_editor.py 56.61 KB / semantic_routing.md / upgrade_footer_gate.py / version_history.md）+ `references/.rule_backup/` 含 **248 个 .bak** + scripts/verify_current_state.py | 分卷=否 | 超 4KB=是（8.8 倍）；contract.md 34.47 KB 同样超限 | 13 章节（198 行），最大章节「版本历史」150-198

**触发与路由**: description≈700 字（YAML 折叠 12 行，:3-14） | 触发词质量=优（`triggers:` 10 个，:19-29） | version/name=是（`version: 10.27.0`，:17）

**死链与过时引用**: 无死链。过时平台名：①门禁模板 G2 仍写 `<OC/WB/CC/TC/HM/CX>`(:60)，与同文件 :134/:153/:157「CC 已弃用、HM 已卸载」**自相矛盾**；②:175 历史行仍写「Hermes 端」。

**重复与冲突**: ①内部平台口径矛盾（:60 vs :134）；②**备份轮转失守**：`.rule_backup/` 同日同文件 8 份 .bak（contract.md.20260911_*），共 248 份，违反 A-project-handoff:149 的 R198.7「同日 >5 份即轮转」；③footer 协议四处重复（本文件 :69/:93 + A-get-memory :166-170/:292）；④与 A-get-memory 互为出入口端。

**工作流闭环**: 门禁=有（G0-G8 九项 :58-65；三门禁 :157-161） | 七步闭环=有（①-⑦ :90） | footer=有（:69/:93） | 版本历史行=有(:150)

**问题清单**:
- [P0] SKILL.md 36,065 B + contract.md 34.47 KB 双双超限且无分卷
- [P1] frontmatter `10.27.0`(:17) vs 正文「V10.28.0」(:182) vs 历史行 V10.28.0(:151) 三处不一致
- [P1] 门禁模板 G2 仍列已弃用 CC/HM，与同文件弃用声明冲突（:60）
- [P1] `.rule_backup/` 248 个 .bak，同日同文件 8 份，违反 R198.7 轮转
- [P2] 版本历史 V9.7.6 重复两行（:190/:191 同号）
- [P2] :175 仍写「Hermes 端」
- [P2] description 12 行≈700 字，本身即启动注意力税

**整改建议**:
1. :60 枚举改 `<OC/WB/TR/CX>`；:175 删「Hermes 端」
2. :17 改 `version: 10.28.0`；删除 :190/:191 重复编号行
3. 按 R198.7 把 `.rule_backup/` 同日 >5 份迁 `D:\global_memory_archive\_trash\backup-rotation\A-memory-start\<日期>\`

---

### A-get-memory

**体积与结构**: SKILL.md=30,802 B | references 文件数=9（antipatterns / step2_4_missed_audit / step6_routing_manager / step7_project_handoff / step8_evolution / step9_forget / templates / user_profiler_init / version_history）+ 根级 ROUTER.md + `scripts/sync_skill_router.py` | 分卷=否 | 超 4KB=是（7.5 倍） | 34 章节（448 行），最大章节 Step 3「执行写入」230-311

**触发与路由**: description≈201 字 | 触发词质量=**中**（**无 `triggers:` 字段**，触发词在 description(:3) 与 :42「When This Triggers」双处维护，路由表无法结构化消费） | version/name=是（`4.24.0`，与历史行一致）

**死链与过时引用**: **2 条真死链**——①`scripts/trace_view.py`（:173/175/214/440，**scripts 目录存在但无此文件**）；②`scripts/wf_*.ps1`（:213/441，同目录无 wf_*.ps1；七步规范实际在 `D:\global_memory\prompts\workflow_seven_step.md`，实测存在）。过时平台名：Hermes（:255/:395/:398）、CC（:422「WB/CC/TRAE」）。

**重复与冲突**: ①**ROUTER 双源漂移**：ROUTER.md:13-25 的 11 分支表 vs SKILL.md:28-29 内容不一致，无同步机制；②footer 协议四处重复；③与 A-memory-start 出入口咬合、与 A-project-handoff 在项目续接/拆卷上重叠；④未声明七步闭环（「七步闭环」「⑦」0 命中），却正是闭环的⑦。

**工作流闭环**: 门禁=有（upgrade_footer_gate.py :170/:292） | 七步闭环=**无**（0 命中） | footer=有(:166/:292) | 版本历史行=有(:430)

**问题清单**:
- [P0] 死链 `scripts/trace_view.py`（4 处引用，实测无此文件）
- [P0] 死链 `scripts/wf_*.ps1`（:213/441，实测无此文件）
- [P0] 主文件 30,802 B 超限 7.5 倍；ROUTER.md 存在但主文件仍全量内联 ROUTER 表
- [P1] 平台名 Hermes(:255/395/398)、CC(:422) 已弃用
- [P1] ROUTER.md 与 SKILL.md 分支表漂移且无同步脚本
- [P1] frontmatter 缺 `triggers:`，触发词双处维护
- [P2] 未声明七步闭环定位（与 A-memory-start:90 的⑦定义单点耦合）
- [P2] 版本历史 V4.13.1 整行重复（:445==:446）

**整改建议**:
1. :213/214 改指向 `D:\global_memory\prompts\workflow_seven_step.md`，或补写 wf_*.ps1/trace_view.py
2. :395/:398 删 Hermes 分支，:422 改 `WB/TR/CX`；frontmatter 补 `triggers:` 10 个
3. 用 `sync_skill_router.py` 由 SKILL.md 生成 ROUTER.md 消除双源；删除 :446 重复行

---

### A-prompt-better

**体积与结构**: SKILL.md=28,672 B | references=**0**（目录内仅 SKILL.md） | 分卷=否 | 超 4KB=是（7 倍） | 33 章节（675 行），最大章节 Step 4「优化 Prompt」166-359（**193 行，占 28.6%**）

**触发与路由**: description≈290 字（折叠 8 行） | 触发词质量=优（`triggers:` 10 个，:12-22） | version/name=是（`1.3.0`，与历史行一致）

**死链与过时引用**: 无死链、无过时平台名（Hermes/QW/QClaw/CC 全文 0 命中）

**重复与冲突**: ①**版本历史表结构破损**：:672 多出一条 `|------|------|` 分隔行，致 V1.2/V1.1/V1.0(:673-675) 落入无表头区；②与 `A-memory-start/references/prompt_optimizer.md`(6.13 KB) 双套优化方法论并存；③:364/367/370/375 的样例标题被写成真实 H2，污染文档大纲。

**工作流闭环**: 门禁=**无**（0 命中） | 七步闭环=有（②环节 :33-35） | footer=**无**（0 命中） | 版本历史行=有(:667，表格破损)

**问题清单**:
- [P0] 主文件 28,672 B 超限 7 倍，无任何 references/分卷承接
- [P1] 版本历史表格 :672 多余分隔行导致渲染破损
- [P1] Step 4 单节 193 行占全文 28.6%，最大注意力税
- [P2] 无门禁命令声明、无 footer 协议，与 A 族其余 4 个收尾口径不一致
- [P2] 与 prompt_optimizer.md 双套优化规则并存
- [P2] 样例标题写成真实 H2 污染大纲

**整改建议**:
1. 新建 `references/`，Step 4(166-359) 与多模态专项(395-589) 拆为 partN，主文件留 ≤4KB 指针
2. 删除 :672 多余分隔行，合并 :673-675 入同一表格
3. :364/367/370/375 改为引用 `A-memory-start/references/prompt_optimizer.md`，消除双套规则

---

### A-ask-questions

**体积与结构**: SKILL.md=10,742 B | references=1（solution_exploration.md 1.72 KB） | 分卷=否 | 超 4KB=是（2.6 倍） | 18 章节（213 行），最大章节 2.5「方案探索」107-144

**触发与路由**: description=**29 字**（:3） | 触发词质量=**差**（`triggers:` 10 个全是同义泛词：需求澄清/澄清需求/需求分析/思路对齐…；description 无任务域/平台/产物/反例锚点，「思路对齐」「理解需求」在任意对话都可能误命中） | version/name=是（`2.5.0`；另有 `risk: unknown`(:5)、`source: community`(:6)）

**死链与过时引用**: 无死链、无过时平台名。但存在**孤儿文件**：`references/solution_exploration.md` 在 SKILL.md 全文 **0 处被引用**，而 A-memory-start:91/:171 称其为「死链已移除」——构成三源矛盾（A-memory-start 说不存在 / 文件实际存在 / SKILL.md §2.5 又内联一份同内容模板 :122-140）。

**重复与冲突**: ①方案探索模板三处并存且互相否认（SKILL.md:122-140 / references/solution_exploration.md / A-memory-start:91 的否认声明）；②与 A-memory-start Step 0.7 需求澄清重叠；③:52 用自我豁免方式解释与全局 P0.9 的冲突。

**工作流闭环**: 门禁=仅引用无声明（:44/:50） | 七步闭环=有（③+③.5 :30-32/:142） | footer=**无**（0 命中） | 版本历史行=有(:199)

**问题清单**:
- [P1] description 仅 29 字，无任务域/平台/产物锚点，触发依赖 10 个同义泛词
- [P1] `references/solution_exploration.md` 为孤儿文件（SKILL.md 0 处引用）
- [P1] 方案探索模板三源并存且互相否认
- [P2] 主文件 10,742 B 超限 2.6 倍
- [P2] 无 footer 协议；门禁仅被引用未声明
- [P2] `risk: unknown`(:5) 从未复核

**整改建议**:
1. 删除 `references/solution_exploration.md`，或由 §2.5 显式引用并同步修正 A-memory-start:91/171
2. description 扩到 80-120 字，补「动手前/复杂任务/≥2 文件改动」等判别锚点
3. 补 footer 协议声明；:5 `risk: unknown` 改 `risk: low`

---

## A族共性结论（跨 5 个 skill 通病）

1. **5/5 主文件全破 4KB 硬上限且 5/5 零分卷**：84,818 / 36,065 / 30,802 / 28,672 / 10,742 B；`D:\global_skills` 全库 `*.part*.md` 实测 **0 个**——R199 拆卷机制从未作用于 skill 自身。A-memory-start:151 自己记录过「4985B 超限 → 拆卷」，说明规则只治了 `behavior_core_rules_p8`，没治 A 族。
2. **版本元数据漂移**：A-project-handoff 差 13 个版本（3.22.0 vs V3.35.0）；A-memory-start 三处不一致（10.27.0 / V10.28.0 / V10.28.0）。3/5 存在版本历史重复行或乱序。
3. **平台口径已统一但正文未清理**：A-memory-start:134 三处声明四端=OC/WB/TR/CX，但正文弃用名仍命中 **7 处**（A-memory-start:60/:175、A-get-memory:255/395/398/422、A-project-handoff:124/142）。
4. **跨 skill 同模板/常量多源维护**：footer 协议 4 处；方案探索模板 3 处且互相否认；noise_lint 自认双副本；ROUTER 表双份且已漂移。
5. **工作流闭环声明不齐**：门禁 3/5、七步闭环 3/5（A-project-handoff 与 A-get-memory 恰是闭环的④与⑦却 0 命中）、footer 2/5。
6. **备份与噪声纪律在 A 族自身失守**：`.rule_backup/` 248 个 .bak、同日同文件 8 份，直接违反 A-project-handoff:149 自己立的 R198.7。

---

## 主进程修正（R-CURRENT 实证）

- ⚠️ 阶段1 扫描报告中「`A-get-memory` 无 scripts 目录」表述**有误**：`scripts/` 目录真实存在（含 `sync_skill_router.py` 19.07 KB），死链是目录内**缺 `trace_view.py` 文件**。已修正，结论（死链成立）不变。
- ➕ 新增阶段1 未捕获的死链：`scripts/wf_*.ps1`（通配符形式，正则未覆盖）。后续扫描需补通配符引用检测。
