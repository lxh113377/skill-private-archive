# 06-constraints.part3.md

<!-- 本卷为 06-constraints.part2.md 的延续 -->

## 已闭环条目归档（R279 活载卷自愈迁移）

- [DEBT→**已闭环**] `archive/` 为空目录 —— 归档机制从未执行（违反 handoff 致命纪律 #4「archive = 安全网」）— 还债方式：阶段切换前先 `handoff.py archive` | 状态：**已闭环**（实测 `archive/` 含 4 文件：`overlap_raw.txt` + `scope-v1-169-2026-09-14/` 3 件；`handoff.py status` 报 `Archived phases: scope-v1-169-2026-09-14`）

- [DEBT→**已闭环**] `01-scan/overlap_raw.txt`（282,977B）为阶段1 原始中间产物，滞留交付目录 — 还债方式：迁 `archive/`（待确认 D3） | 状态：**已闭环**（D3 已迁 `archive/overlap_raw.txt`）
