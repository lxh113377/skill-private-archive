# 07 - 下一步

> 归档类型：增量（已完成项移入分卷）
> **⚠️ 这是新对话恢复上下文的入口文件；P0 永远不能空。**
> **真相源口径（2026-09-22 实测校准）**：P0 只放经实测确认**未完成**的项；已完成项一律迁入分卷 `- [x]`，不再滞留主卷。

## 最近对话摘要

- **2026-09-22（第 10 轮，本轮）** — A-project-better **Step 0 首次实跑**（10 条遗留台账，用户按钮确认）+ 三方向并集执行：**非破坏性 2 项已做**（记忆层滞后回写 6 文件 / 阶段1 补齐含 **2 处判据缺陷修复**）；**破坏性 8 项列待确认**。详见 `05-exec/第10轮执行报告.md`
- **2026-09-22（第 6 批）** — 修 `rule_editor.py commit --fix-mirror`（`7d8a8e1`，R270）；v2 口径定格 **77 条**；31 件全量自包含入库（`29f9d868`）
- **2026-09-22（第 3 轮）** — A-project-better 四维体检 + 7 项非破坏性整改；见 `05-exec/第3轮执行报告.md`
- **2026-09-19（第 2 轮）** — 批2 剩余 P0 单点修复 + 注册表重建；见 `05-exec/第2轮执行报告.md`
- **2026-09-14（第 1 轮）** — 阶段0-4 主体；见 `07-next-steps.part3.md`

## P0 — 必须做

- [ ] **【待确认 B1】** 焚诀 `NEGATIVE_TAG_MAP` 清 **7 ghost 键 + 7 ghost 引用**（`negative_tag_audit` 健康率 72.5% → 100%）—— 破坏性（改焚诀源码 + 重建索引 + 回归）
- [ ] **【待确认 B2】** `openclaw-task-supervision:114` 六端口径改写（`OC/WB/CC/TC/HM/CX` → 在役端）＋ 裁定 `wps-knowledgebase:219`（注册表 `source=community`）**改 or 保留原文** —— 破坏性
- [ ] **【待确认 B3–B8】** 其余 5 项破坏性建议（`fenjue_measure.py` 路径 / `.rule_backup` 落点 / git 提交 / 注册表归一化 / `content_snr` M3·M4 / review 增交叉校验）—— 逐项详见 `05-exec/第10轮执行报告.md` §六
- [ ] **【待确认 B9｜环境脏项·外部引入】** `D:\global_memory\_bak`（并行会话 14:26:21 创建，18 文件）致 `rule_editor gates` → `noise=fail`（GM 根级被 `.gitignore:14` 豁免，但经 `焚诀\memory_content` junction 被 depth=2 `STRAY_NAME` 判 VIOL）⇒ 本项目 `savepoint` 被拒；按 R269 **未擅动**，需裁定是否为该会话在途备份（在途则等；非在途则迁 `_trash`）
- [ ] **[P2] 注册表归一化**（并入 B6）：`oc-dispatch-exec-guard` 的 `source='user'`（非标准值）→ `user-created`；`install_state.mv=''` → `None`


## 分卷目录
- **卷1** `07-next-steps.part1.md` — 历史待办与已完成条目（2026-09-22 已按实测销账）
- **卷2** `07-next-steps.part2.md` — 已完成：批2 剩余 P0 与 q-2/q-3 收口
- **卷3** `07-next-steps.part3.md` — 最近对话摘要（历史）
