# 07-next-steps.part32.md

<!-- 本卷为 07-next-steps.part1.md 的延续 -->

## 已完成（索引；完整明细见 `05-feature-status.md` 与 `part2.md`）

- [x] **批量替换 `Desktop\焚诀` → `Desktop\workspace\焚诀`** —— `1b6fe6d`，11 文件 34 处
- [x] **修正权威平台口径行（HM 回归在役）** —— `5e89bb6` / `42760fc` + 焚诀 C4 代码 `f145f7f`
- [x] **确认两个 fenjue 件无反向引用** —— 已退役 `716ae69`；遗留 6 处活跃引用清 4/6，余 2 处判为**历史案例留痕**（保留原文）
- [x] **阶段1 补跑（上提主卷）** —— 2026-09-22 上提至主卷 P0 第 3 条，本卷不再记账
- [x] **阶段4 首批：A族 P0 整改** —— 拆卷 `f8bc12f`（85,508B→3,827B）+ 回归修复 `V3.37.1`；A-get-memory 死链 `5bcb550`；版本号/平台名清理

## P1 / P2（已全部销账）
- [ ] R57-3 推荐:注入壳 AGENTS.md 29,293B / TODO.md 31,909B 超 root_doc_max 16KB——走 trim-shell 迁历史条目（VOL-858E6/VOL-D908D 的落地）（由 flow 登记；状态: todo）
- [ ] R57-2 推荐:memory/08-ac-obs.md（4,102B 超 4KB）裁口径——入 SPLIT_TARGETS 还是加豁免册（flow --verify-ac 整卷解析 08，拆卷会打断 AC 判定）（由 flow 登记；状态: todo）
- [ ] R57-1 推荐:rule_editor gates 输出截断机器化——mirror 明细须逐条打印（本轮因只看 tail 误判「他人脏项」，跑 check-skill-mirror.ps1 原文才发现 13 项全是自己的）（由 flow 登记；状态: todo）
- [ ] VOL-D908D 体量治理[L2 根文档] TODO.md — 注入壳瘦身：历史条目迁 memory/ 分卷，壳内只留指针（handoff.py trim-shell）（由 flow 登记；状态: todo）
- [ ] VOL-858E6 体量治理[L2 根文档] AGENTS.md — 注入壳瘦身：历史条目迁 memory/ 分卷，壳内只留指针（handoff.py trim-shell）（由 flow 登记；状态: todo）
- [ ] VOL-1BFD2 体量治理[L1 记忆卷] memory/08-ac-obs.md — 非 4KB 拆卷目标：先裁口径（是否入 SPLIT_TARGETS / 加豁免册），禁自动拆（由 flow 登记；状态: todo）
- [x] R19-3 本仓9份基线JSON落 schemas/r19 契约族+校验器（由 flow 登记；状态: todo）

- [x] 阶段2 按族分批全量精读 102 个自建 skill —— 6 份族审计卡，7 批（2026-09-14）
- [x] 裁定 LOW 灰区 33 个归属 —— 用户裁定 **排除**（2026-09-14）
- [x] `A-memory-start` Step 0.6 补 PowerShell `&` 调用符与 venv 降级链 —— `c3dba47`
- [x] `direct_map` 误命中复核 —— ⚠️ 复核已完成、**修正未做**，已上提主卷 P0 第 1 条

## 最近对话摘要（历史）

- 2026-09-14 — 阶段0 完成：三源交叉裁定自建清单，判定逻辑两轮修正（① `user_created=false` -4 权重过重误杀本地目录 → 改硬排除市场信号；② 补 frontmatter homepage 第四源）。结论 自建 102 / EXCLUDE 34 / 灰区 33 / 注册表失真 42；同时 init 项目记忆（10 文件 + P-1 绑定表 11 行）。

## 已完成（索引；完整明细见 `05-feature-status.md` 与 `part2.md`）

- [x] 项目记忆 init（10 文件 + P-1 绑定表）— 2026-09-14
- [x] 权威源定位：三源（`unified-skills-index.json` / `platform-oc.json` / `disk_manifest.json`）与字段口径实测 — 2026-09-14
- [x] 阶段0 落盘 3 文件 / 阶段1 落盘 4 文件（含两轮判据修正）— 2026-09-14
- [x] 阶段2 第1批 A族精读（5 个）：新抓 `wf_*.ps1` 死链、版本漂移 13 个、248 个 `.bak` — 2026-09-14
- [x] 撤销错误升级建议「init 后生成 EXPERIENCE.md」（实测 Step 7 V4.6.0 已降级）— 2026-09-14
- [x] 阶段2 第2批：fenjue族 5 + 审计族 15 精读；审计族 15→8 合并决策；定位 `vp-perspective-audit` 误命中根因 — 2026-09-14
- [x] `TODO.md` 阶段待办总表建立（2026-09-22 已降级为「状态总表索引」）— 2026-09-14
- [x] 阶段4 A3/A4/A5（`bc225b3`，17 文件）— 2026-09-14
