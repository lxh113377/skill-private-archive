# 05-feature-status.part3.md

<!-- 本卷为 05-feature-status.md 的延续 -->

## ✅ 已完成（2026-09-22 第 4 轮：用户授权 D1–D5，全部执行）

- **D1 修 3 处门禁判据缺陷**（受管根 `7cc7d4d`，`A-project-handoff` **V3.42.0**）：AC 计数剔 HTML 注释（假通过）/ 新增 `has_feature_entries()` 兼容「`## ✅ 已完成` + 普通列表项」（假阴性）/ `status` 先判 sync 占位再计数（口径矛盾）；三函数**下沉 `common.py` 单一真相源**。验证：层a 隔离桩 **11/11**、层b 集成含对照（生效路径 PASS ＋ 注释-only 反例仍被拦）、本项目 `review` **56% → 100%**、三门禁全绿、焚诀 `verify` **15 PASS**
- **D2① 直连表修正**（焚诀 `bf5e284`，已推送 SHA 一致）：收窄 vp 过泛 pattern（去裸 `提出建议`）；**系统性复扫出 7 死目标 / 11 条死直连**并全数重指或删除；死目标复扫 **0**；回归套件 **ALL PASS**（T2 直连 **47/47**、T3 top1 死件 → `A-skill-manager`）；连带修 **6 处**过期测试期望
- **D2② 注册表 `user_created` 复核（口径已裁定）**：注册表口径 = **120 条**（verify C1/C2/C10 三方守）；A 类（死件）**0**、B 类（true+市场信号）**0** → 09-14 报的「42 条失真」在当前口径**不复现**；C 类 85 条**不可判为失真**（反证 `canvas-design`）；2 条真脏数据登记 P2。附带量化：磁盘含 `SKILL.md` **151** vs 注册表 **120**（仅磁盘有 31；**仅注册表有 0**）；阶段0 自建清单 90 → 仅 **60** 在册
- **D3 归档与轮转**：`.rule_backup` 仅 1 组超阈值（`A-memory-start.SKILL.md` @09-19 共 10 份）→ 保留 5、**迁移（非删除）** 5 至 `D:\global_memory_archive\_trash\backup-rotation\A-memory-start\2026-09-19\`；总数 **40 → 35**；`overlap_raw.txt`（283KB）→ `archive/`；随后 `sync` 刷新目录树
- **D5 GM 日志空档留痕**：`D:\global_memory\memory\2026-09-22.md` 追加「R9 事故 · 每日日志空档说明（事后补记）」（**不补造当日日志**）；`[GATE:evolution-pass]`

## ✅ 已完成（2026-09-22 第 5 批：用户追加授权 ①②④）

- **① 阶段0 清单按 151 重出**：先修 `01-scan/scan_all.py` 的**失效数据源**（`platform-oc.json` 随 OC 退役已被删 → 实跑 `FileNotFoundError`；口径回落为「在役端 `platform-*.json` 的 `user_created_skills` 并集」）；v1 三件**原样归档** `archive/scope-v1-169-2026-09-14/`（R241）；v2 结果 = **HIGH 51 / MID 26 / LOW 30 / EXCLUDE 43**（自建 **77**，失真 41）⇒ 记忆里「自建 ≈90 / 169 条」基数**全部作废**
- **② 31 件入册**：**认知修正** —— 不是"漏注册"，而是被 `RETIRED_SKILLS`（R198.6 fail-closed）有意排除（31/31 全命中）；摘除黑名单 **100 → 69** → `build_registry` 注册表 **120 → 151** → `build_indexes --apply`（BGE/TF-IDF `(151,512)/(151,5000)`、25 派生件、守恒 PASS）
  - 顺带修 **2 处派生件脱节（纪律 #18 族）**：C6（GM `cross_platform_map.json` note 引用 V1.21 → 同步 V1.22）；C16（`STATUS.md`/`STATUS.part1.md` 内容过期写 120 skills → **用生成器 `aggregate_status.py` 重出**，不手改数字）
  - 收口：焚诀 `verify` **16 PASS / 0 FAIL / 0 SKIP**；路由回归 **ALL PASS**；双仓提交 SHA 一致（焚诀 `28daf6e` / GM `575ca99`）
