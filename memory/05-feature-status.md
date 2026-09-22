# 05 - 功能状态

> 本文件记录功能/任务的完成状态。
> 归档类型：增量（已完成项归档时移入 archive/）

## ✅ 已完成

- 上游口径落地：**06-约束卷纳入「条目归档自愈」**（2026-09-23 第 13 轮 r5，A-project-handoff **V3.48.0**）：① 设计 = `TRIM_ENTRY_TARGETS`（07+05+06）与 `SPLIT_TARGETS` **解耦**——06 含红线等必须始终可见章节，通用拆卷会搬走它们，故只走条目归档；② 判据 = `closed_marker`（已修复/已闭环/已解除/已销账 且 不含 未修复/未闭环/部分解决/待观察…）+ **留痕章节白名单**（只迁「已知 Bug」「技术债」）+ **分区不变式**（归档∪留守 = 原文，只搬不移除/不复制）；③ 配套：承接卷就地续拆、CLI 迁后复跑拆卷、`volume_health` 活载卷只读可见；④ 验证 = 层a 隔离桩 **34/34** + 既有 V3.47.0 桩 15/15 复跑全绿（07/05 零回归）+ 层b 真机（焚诀 06 零变更；本项目 06 13,075B→7,097B 迁 13 条、行守恒 missing=0/dup=0、红线留主卷）；⑤ 收益 = 本项目注入壳 **33,029B → 26,594B（-6,435B/轮）**，其中 06 节 12,148B→6,182B

## 分卷目录
- **卷1** `05-feature-status.part1.md` — 进行中 / 计划中 / 阻塞
- **卷2** `05-feature-status.part2.md` — 已完成：2026-09-19 第 3 轮（P0-2 收口 + 补建上游 + 注册表重建）
- **卷3** `05-feature-status.part3.md` — 已完成：2026-09-22 第 4 轮（D1–D5 授权项执行结果）
- **卷4** `05-feature-status.part4.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷5** `05-feature-status.part5.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷6** `05-feature-status.part6.md` — 已完成：2026-09-22 第 10 轮（Step 0 首次实跑 + 记忆层回写 + 阶段1 补齐 + B1–B7 授权执行）
- **卷7** `05-feature-status.part7.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷8** `05-feature-status.part8.md` — 已完成：2026-09-23 第 13 轮（性能瓶颈三维实测分析）
- **卷9** `05-feature-status.part9.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷10** `05-feature-status.part10.md` — 05-feature-status 分卷（R199 自动拆卷）

