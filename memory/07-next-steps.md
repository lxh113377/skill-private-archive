# 07 - 下一步

> 归档类型：增量（已完成项移入分卷）
> **⚠️ 这是新对话恢复上下文的入口文件；P0 永远不能空。**
> **真相源口径（2026-09-22 实测校准）**：P0 只放经实测确认**未完成**的项；已完成项一律迁入分卷 `- [x]`，不再滞留主卷。

## 最近对话摘要

- **2026-09-22（第 3 轮，本轮）** — A-project-better 四维体检 + 7 项非破坏性整改；详见 `05-exec/第3轮执行报告.md`（含新发现：门禁判据 3 处缺陷、GM 日志 09-09~09-20 空档 12 天、skill 数口径四数不一）。收尾三条：`handoff savepoint` **exit 0**（中途一度被拒，根因 = `焚诀\.codebuddy` 未 gitignore 豁免，已由并行会话 commit `1f354e9` 解除）、焚诀 `verify` **15 PASS / 0 FAIL**、`rule_editor gates` 三门禁全绿
- **2026-09-19（第 2 轮）** — 批2 剩余 P0 单点修复 + 注册表重建；见 `05-exec/第2轮执行报告.md` §十四~§二十
- **2026-09-14（第 1 轮）** — 阶段0-4 主体；见 `07-next-steps.part3.md`

## P0 — 必须做

- [ ] **阶段1 补跑**：`attention_sim.py` / `content_snr.py` / `negative_tag_audit.py`；扫描脚本补「通配符引用」死链检测（`scan_all.py --stage scan` 已修好可用，见 `05-exec/第3轮执行报告.md` 第十节）
- [ ] **遗留 3 条待逐条判定**：`openclaw-task-supervision` / `wps-knowledgebase` / `data-layer-consistency-fix` 各 1 处弃用平台名
- [ ] **v2 清单的 LOW 30 / EXCLUDE 43 待裁定**：v2 按 151 基数重出后灰区 30 条 + 排除 43 条是否维持（v1 曾裁定灰区「排除」）
- [ ] **[P2] 新入册 31 件在 `D:\global_skills` 仍是未跟踪（`??`）** → 是否纳入版本化（否则 `git clean` 即丢）
- [ ] **[P2] 注册表 2 条真脏数据**：`testing` 的 `source` 为空串、`oc-dispatch-exec-guard` 的 `source=user`（非标准值 `user-created`）

## 分卷目录
- **卷1** `07-next-steps.part1.md` — 历史待办与已完成条目（2026-09-22 已按实测销账）
- **卷2** `07-next-steps.part2.md` — 已完成：批2 剩余 P0 与 q-2/q-3 收口
- **卷3** `07-next-steps.part3.md` — 最近对话摘要（历史）
