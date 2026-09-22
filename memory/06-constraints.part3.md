# 06-constraints.part3.md

<!-- 本卷为 06-constraints.part2.md 的延续 -->

## 已闭环条目归档（R279 活载卷自愈迁移）

- [DEBT→**已闭环**] `archive/` 为空目录 —— 归档机制从未执行（违反 handoff 致命纪律 #4「archive = 安全网」）— 还债方式：阶段切换前先 `handoff.py archive` | 状态：**已闭环**（实测 `archive/` 含 4 文件：`overlap_raw.txt` + `scope-v1-169-2026-09-14/` 3 件；`handoff.py status` 报 `Archived phases: scope-v1-169-2026-09-14`）

- [DEBT→**已闭环**] `01-scan/overlap_raw.txt`（282,977B）为阶段1 原始中间产物，滞留交付目录 — 还债方式：迁 `archive/`（待确认 D3） | 状态：**已闭环**（D3 已迁 `archive/overlap_raw.txt`）

- [DEBT→**已闭环**] `05-exec/` 19 个 patch JSON 无索引 — 还债方式：本轮已补 `05-exec/README.md`（2026-09-22） | 状态：**已闭环**（索引实测覆盖 19/19）

- [DEBT→**已闭环**] skill 数口径四数不一（记忆 169 / verify C1 实测 120 / 顶层目录 152 / 全盘 SKILL.md 205）→ 现行 P0 基数不可用 — 还债方式：先裁定口径再复核注册表（待确认 D2） | 状态：**已闭环**（口径裁定 = 注册表 **151**；焚诀 `verify` C1 实测「注册表 == 磁盘 (151 skills)」）


- [DEBT] **焚诀 `NEGATIVE_TAG_MAP` 残留 7 个 ghost 键 + 7 处 ghost 引用**（2026-09-22 第 10 轮实测，`negative_tag_audit.py` 报 `健康率 72.5%` / `RESULT: FAIL`）：`skill-install` / `skill-creator` / `skills-security-check` / `install-skill-dependency` / `deep-research-pro` / `cloudbase-webapp-deploy-debug` / `clawhub` —— **7 个全部实测 `disk=False` 且不在注册表**（非判据假阳性，R263 已先证）。根因：D2 只系统性复扫了**直连表**（`direct_map`），**未同步复扫负标签表**（`tag_layer.py:NEGATIVE_TAG_MAP`） | 还债方式：清理 7 个 ghost 键 + 7 处引用后复跑 `negative_tag_audit.py`（健康率应 → 100%）+ `test_router_regression.py` ALL PASS → 见第 10 轮建议 #5（破坏性）—— **✅ 校正注（2026-09-23 销账）：已闭环** —— B1 已执行；本轮实测 `negative_tag_audit.py` = 健康率 100% / `RESULT: PASS`

- [DEBT] **`fenjue_measure.py:168` 引用不存在的 `behavior_core.md` 路径**（真实位置为 `core/behavior_core.md`）→ 取 size=0，**D1 少算该 P0 文件**（2026-09-22 第 10 轮 `attention_sim.py` 实测告警，属上游口径差异） | 还债方式：改 `fenjue_measure.py` 路径并重跑评分 → 见第 10 轮建议 #8（破坏性）—— **✅ 校正注（2026-09-23 销账）：已闭环** —— B3 已执行；本轮实测 `fenjue_measure.py:182` 已为 `core/behavior_core.md`

- [BUG→**已修复**] **`noise_lint` 二级扫描口径不一致 ⇒ 同一物理目录两套结论、假阳性阻断全部会话 savepoint** — 影响范围：**全局门禁假失败扩散**（四受管根任一违规即拒绝 savepoint）。2026-09-23 实测：`D:\global_memory\_bak`（并行会话在途备份现场）在 `D:\global_memory` 根判 `quarantine`，却经 `焚诀\memory_content`（junction → `D:\global_memory`）在焚诀根判 `VIOL`；同一会话的 savepoint 因此被拒 | 根因三处：① 二级扫描不继承一级 `quarantine` 豁免（一级用、二级漏用）；② 二级子项自身命中 `QUARANTINE_DIRS`（`_bak`）未判豁免；③ junction/符号链接顶层项被按宿主根口径重复判定 | 状态：**已修复（代码层）**（受管根 `d88b5ee`，仅 1 文件；`is_reparse_dir()` 三重回退 + `status_by_name` 留档复用；层a 隔离桩 14/14 含修前修后对照 + 层b `noise` 四根 `[GATE:noise-pass]`）—— ⚠️ **文档同步待补**：`SKILL.md` 版本行 / `version-history.md` / `commands.md §11`（并行会话占用 3.49.0 在途，避免二次夹带；见 `07-next-steps.md` 待办）
