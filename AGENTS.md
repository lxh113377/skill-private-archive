# AGENTS.md — 自建skill优化

> 自动生成: 2026-09-14 21:48:14


## 最近对话摘要
- **2026-09-14（第 2 轮，本轮）** ——
  - ✅ **批3.1 完成**：`A-project-handoff/SKILL.md` 拆卷 **85,508B → 3,827B（≤4KB）**，18 条致命纪律+14 条重要规则 / 绑定表 / 记忆结构+加载指南 / 14 子命令 / 版本历史 → `references/` 5 卷，**内容零丢失**（逐段字节核对 87797 = 85508 + 2289）。commit `f8bc12f`
  - ✅ **拆卷回归修复**（`V3.37.1`）：拆卷把 `COLD_START_DECL` 锚点带入 `references/commands.md`，而 `handoff.py cmd_coldstart` 只读 SKILL.md → `coldstart --check` **exit 1**，会**误拒所有项目的 savepoint**。修法=锚点来源回退链（SKILL.md → `references/*.md`），并附来源文件名作证据；实测修复后 `✅ 6 行逐行 diff 全等`
  - ✅ **批4 元数据**：`ican-frontend-design-system` version 1.0.0→4.0.0（对齐版本表 V4）；`dogfood`/`testing` 补 `version: 1.0.0`。`fenjue-memory-audit` 实测已自洽（1.7.0=V1.7.0，审计结论过期）
  - ✅ 三门禁：`mirror=pass noise=pass evolution=pass`；扫描 `超4KB 69→68`
  - ⚠️ **记忆曾严重滞后**：磁盘已有 `716ae69`(退役6件)/`2e93585`/`5bcb550`(A1)/`b6bf36e`(A2)/`bc225b3`(A3-A5) 等提交，而旧 P0 仍写「待用户确认」→ 本轮已按 R-CURRENT 校正
- **2026-09-14（第 1 轮）** — 批1（路径 34 处）+ 批2（6 项死链）+ 批3 其余（版本号/bigfile-split/cross-platform-agent-sync 拆卷）+ 退役 6 件 + A3/A4/A5（`bc225b3`）+ `rule_editor` R234

---

# 01 - 项目目标

## 项目名称
自建skill优化

## 一句话描述
对 `D:\global_skills` 下用户自建的 skill 及其搭载的工作流做全量体检与优化设计，产出「审计报告 + 逐项实施计划」，分 6 阶段推进。

## 核心价值
- 解决「自建 skill 到底哪些算自建、哪些该修、哪些该合并」长期无清单、靠记忆拍脑袋的问题
- 四个维度同时体检：触发命中率与路由 / 体积注意力税 / 死链·过时引用·规则冲突 / 重复合并与工作流闭环
- 产出可直接执行的整改清单（目标文件 + 改动 + 验证命令 + 回滚手段），而不是一份看完就忘的评论

## 当前阶段目标
- [ ] 阶段0 范围裁定：三源交叉判定自建清单，产出高/中/低置信度名单与注册表失真条目
- [ ] 阶段1 四维机器扫描：复用 `焚诀\audit\` 现成脚本建基线与评分表
- [ ] 阶段2 全量精读：按族分批精读全部自建 skill，产出结构化审计卡
- [ ] 阶段3 审计报告：四维综合结论 + P0/P1/P2 分级清单（每级带实测证据）
- [ ] 阶段4 实施计划：逐项的目标文件 / 改动内容 / 验证命令 / 回滚手段，按 P0→P1→P2 分批
- [ ] 阶段5 工作流专项：七步闭环落地率、footer 协议、三道门禁、direct_map 误命中修正

## 已完成目标

---

# 02 - 仓库结构

## 模块说明
- `src/` — 
- `tests/` — 

---

# 03 - 技术栈

## 构建与部署
- 构建： 
- 部署： 

## 运行时要求

---

# 04 - 核心文件地图

## 核心逻辑文件
- `` — 

## 配置文件
- `` — 

---

# 05 - 功能状态

## ✅ 已完成

- 阶段0 范围裁定（2026-09-14）
  - 产出 `00-scope/自建skill清单.md`、`注册表失真条目.md`、`scope_result.json`
  - 结论：自建 102 / EXCLUDE 34 / 灰区 33 / 失真 42
- 项目记忆初始化（2026-09-14）：memory/ 8 文件 + archive/ + P-1 绑定表 + .aiexclude

- 阶段1 四维机器扫描（2026-09-14）
  - 产出 `01-scan/scan_report.md`、`scan_result.json`、`overlap_raw.txt`
  - 结论：超4KB 83/102、弱触发 9、真死链 4、弃用平台名 25、合并候选 4 簇

- 阶段2 第1批：A族 5 个精读（2026-09-14）→ `02-review/A族_精读.md`

- 阶段3 审计报告（2026-09-14）→ `03-audit/自建skill优化审计报告.md`：P0 共 25 项（分三梯队）、P1 按族、P2 合并决策、阶段4 分 5 批

- 阶段4 实施计划（2026-09-14）→ `04-plan/实施计划.md`：5 批共 40+ 项，每项含目标文件/改动/验证命令/回滚手段；建议顺序 批3→批1→批2→批4→批5

- 阶段4 A3/A4/A5（2026-09-14, commit `bc225b3`）：9 补 `version` + 1 收窄 description 并补负向边界 + 7 回填 `meta.json` description → 17 文件一次收口，`[GATE:mirror-pass]`、工作区 status=0
  - 实测修正 3 处清单偏差：A3 实存 13（`skill-install` 已退役）其中 4 个为市场件应跳过；A4 清单漏 `local-vram`；A4 性质 = 上游 marvis 打包 bug（不参与路由）

- 阶段4 批3.1 拆卷（2026-09-14, commit `f8bc12f` + `V3.37.1`）：`A-project-handoff/SKILL.md` **85,508B → 3,827B（≤4KB）**，分入 `references/` 5 卷（disciplines / skill-binding / memory-structure / commands / version-history），内容零丢失
  - **回归修复**：拆卷使 `COLD_START_DECL` 锚点迁出 SKILL.md → `coldstart --check` exit 1 → **所有项目 savepoint 被误拒**；修 `handoff.py cmd_coldstart` 锚点回退链（SKILL.md → `references/*.md`），实测 `✅ 6 行逐行 diff 全等`
  - 经验：**大型 skill 拆卷必须同步检查「按 SKILL.md 定位的机器锚点/门禁」**（coldstart 锚点、行号引用、脚本内硬编码路径）
- 阶段4 批4 元数据（2026-09-14）：`ican-frontend-design-system` version 1.0.0→4.0.0（对齐版本表 V4）；`dogfood`/`testing` 补 `version: 1.0.0`

## 🚧 进行中

- 阶段5 工作流专项（2026-09-14）→ `04-plan/工作流专项建议.md`：闭环落地率实测（七步 3.9% / footer 协议 2.0% / 门禁 24.5%）、footer 四处收敛方案、direct_map 误命中修正 5 步
- 阶段4 实际改动 skill — **等用户确认**（阶段0-4 全程只读，未碰 `D:\global_skills` 一个字节）（A族5 / fenjue5 / 审计15 / local10 / story11 / 其他族 4 批 57 = 103 个，7 批全部落盘）
  - 附带成果：最后一批推翻 11 个「自建」判定（市场/上游件），真自建量修正为约 91 个

## 📋 计划中

- 阶段2 全量精读（102 个，按族分批）
- 阶段3 审计报告 + P0/P1/P2 分级
- 阶段4 逐项实施计划
- 阶段5 工作流专项 + 注册表修正 + 合并评估

## ⛔ 阻塞

- LOW 灰区 33 个归属待用户裁定（阻塞阶段2 精读范围）

---

# 06 - 已知约束

## 已知 Bug

## 技术债

## 红线（不能改）
- 

## 性能/兼容性约束
- 

## 环境隔离（R196，init 必填）
- env_mode: development（枚举：development / staging / production）
- 红线：dev/staging 禁止连接 production 数据库与 API key
- production 操作前检查：近期备份存在（archive/ 或 DR 快照 ≤7 天）+ 密钥不复用
- 保护文件 .env.prod / .env.production 禁止入库（.gitignore 已含规则）

## 评测集隔离（R196）
- 测试专用文件清单：（如 eval/testset_provenance.json / blindset / frozen）
- 红线：训练/生产数据禁止写入测试专用文件；新增评测数据先登记来源（provenance）

---

# 07 - 下一步

## 最近对话摘要

- **2026-09-14（第 2 轮，本轮）** ——
  - ✅ **批3.1 完成**：`A-project-handoff/SKILL.md` 拆卷 **85,508B → 3,827B（≤4KB）**，18 条致命纪律+14 条重要规则 / 绑定表 / 记忆结构+加载指南 / 14 子命令 / 版本历史 → `references/` 5 卷，**内容零丢失**（逐段字节核对 87797 = 85508 + 2289）。commit `f8bc12f`
  - ✅ **拆卷回归修复**（`V3.37.1`）：拆卷把 `COLD_START_DECL` 锚点带入 `references/commands.md`，而 `handoff.py cmd_coldstart` 只读 SKILL.md → `coldstart --check` **exit 1**，会**误拒所有项目的 savepoint**。修法=锚点来源回退链（SKILL.md → `references/*.md`），并附来源文件名作证据；实测修复后 `✅ 6 行逐行 diff 全等`
  - ✅ **批4 元数据**：`ican-frontend-design-system` version 1.0.0→4.0.0（对齐版本表 V4）；`dogfood`/`testing` 补 `version: 1.0.0`。`fenjue-memory-audit` 实测已自洽（1.7.0=V1.7.0，审计结论过期）
  - ✅ 三门禁：`mirror=pass noise=pass evolution=pass`；扫描 `超4KB 69→68`
  - ⚠️ **记忆曾严重滞后**：磁盘已有 `716ae69`(退役6件)/`2e93585`/`5bcb550`(A1)/`b6bf36e`(A2)/`bc225b3`(A3-A5) 等提交，而旧 P0 仍写「待用户确认」→ 本轮已按 R-CURRENT 校正
- **2026-09-14（第 1 轮）** — 批1（路径 34 处）+ 批2（6 项死链）+ 批3 其余（版本号/bigfile-split/cross-platform-agent-sync 拆卷）+ 退役 6 件 + A3/A4/A5（`bc225b3`）+ `rule_editor` R234

## P0 — 必须做

- [ ] **批1 剩余：弃用平台名清理（需内容判断，非机械替换）** —— `windows-cli-utf8-wrapper`(:11/208/233 CC 主示例) / `discover-agent-cli`(:4/60/88/172 + reference.md:9 CLI 映射表) / `workflow-preflight-check`(:239) / `vp-perspective-audit`(:53-59 CC 段) / `skill-routing-regeneration` / `windows-native-ocr` / `prompt-consolidation` / `skill-defer-to-authority` → 改为 `OC/WB/TR/CX` 或删行；**历史案例类引用保留原文**
- [ ] **⚠️ 路由派生件脱节（live bug，致命纪律 #18）** —— `焚诀\skill\registry\unified-skills-index.json`(2026-09-10) 仍含 6 个已退役件（`skill-install` 等）→ `unified_router` 本轮实测 top1 = `skill-install`（死件）。修法 = 焚诀内 `eval/build_indexes.py --apply` 完整重建 + 注册表重生成 + `verify_truth_consistency.py` 复跑（属焚诀仓库，须走其门禁）
- [ ] **⚠️ 待你裁定：HM 平台口径冲突** —— 权威 `D:\global_memory\cross_platform_map.json V1.9`(2026-09-13) 写「HM 2026-08-08 已卸载」，而 `A-memory-start:134` 已写「HM 2026-09-14 恢复在役」→ 两源冲突，需一句话定案后统一（含 `A-memory-start:60` G2 模板是否枚举 HM）
- [ ] **⚠️ 待你裁定：灰区归属** —— `local-asr`/`computer-use`/`realtime-translator`/`tts`/`txt2img` 等 Intel 分发样例包是否计入自建（影响维护范围）
- [ ] **批5 合并/退役（需逐项确认）** —— 见 `04-plan/剩余待办分类清单.md` B3：审计族 15→8、story scan 合并、local `_shared` 抽取、4 个 Notion 件
- [ ] **B5 非本审计范围** —— 工作区约 40 个 `cloudbase__skillhub/*` 他人未提交改动（并行会话市场包升级）；`.rule_backup/` 248 个 `.bak` 待按 R198.7 轮转

## 分卷目录
- **卷1** `07-next-steps.part1.md` — 07-next-steps 分卷（R199 自动拆卷）


---

# 08 - AC-OBS 验收标准

## 验收标准列表

- AC-OBS-01: 用户登录功能 → 输入正确账密点击登录，跳转到首页 | 截图 + URL变化
- AC-OBS-02: API返回数据正确 → GET /api/users 返回200 + JSON数组 | API响应
- AC-OBS-03: 页面响应速度 → Lighthouse评分 > 90 | 测试输出
-->

