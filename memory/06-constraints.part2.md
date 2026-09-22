# 06-constraints.part2.md

<!-- 本卷为 06-constraints.part1.md 的延续 -->

## 已闭环条目归档（R279 活载卷自愈迁移）

- [DEBT→**已闭环**] 记忆层与实况脱节（`01-goal` 六阶段目标 0 勾选 / `03`+`04` 空模板 / `06` 四节全空 / `08` 零条真实 AC）— 还债方式：本轮已回填（2026-09-22，见 `05-exec/第3轮执行报告.md`） | 状态：**已闭环**（`handoff.py status` 实测 **8/8 sections filled**）

- [DEBT→**已闭环**] 三重同义状态源（`TODO.md` / `memory/07-next-steps.md` / `memory/05-feature-status.md`）已实测漂移 — 还债方式：定 `memory/07` 为 P0 唯一真相源，`TODO.md` 降级为「阶段状态总表（索引）」（2026-09-22 已改） | 状态：**已闭环**（`TODO.md` 首行已写「非入口」并指向 `memory/07-next-steps.md`）

- [DEBT→**已闭环**] 工作区 git 仅 1 次提交（`49ff0d6` baseline）→ 无回滚粒度 — 还债方式：按主题逐步 commit（本轮改动待确认 D4） | 状态：**已闭环**（D4 起按主题拆分提交，实测 HEAD = `632d183`，累计 14 次提交）

- [DEBT→**已闭环**] `archive/` 为空目录 —— 归档机制从未执行（违反 handoff 致命纪律 #4「archive = 安全网」）— 还债方式：阶段切换前先 `handoff.py archive` | 状态：**已闭环**（实测 `archive/` 含 4 文件：`overlap_raw.txt` + `scope-v1-169-2026-09-14/` 3 件；`handoff.py status` 报 `Archived phases: scope-v1-169-2026-09-14`）

- [DEBT→**已闭环**] `01-scan/overlap_raw.txt`（282,977B）为阶段1 原始中间产物，滞留交付目录 — 还债方式：迁 `archive/`（待确认 D3） | 状态：**已闭环**（D3 已迁 `archive/overlap_raw.txt`）

- [DEBT→**已闭环**] `05-exec/` 19 个 patch JSON 无索引 — 还债方式：本轮已补 `05-exec/README.md`（2026-09-22） | 状态：**已闭环**（索引实测覆盖 19/19）

- [DEBT→**已闭环**] skill 数口径四数不一（记忆 169 / verify C1 实测 120 / 顶层目录 152 / 全盘 SKILL.md 205）→ 现行 P0 基数不可用 — 还债方式：先裁定口径再复核注册表（待确认 D2） | 状态：**已闭环**（口径裁定 = 注册表 **151**；焚诀 `verify` C1 实测「注册表 == 磁盘 (151 skills)」）


- [DEBT] **焚诀 `NEGATIVE_TAG_MAP` 残留 7 个 ghost 键 + 7 处 ghost 引用**（2026-09-22 第 10 轮实测，`negative_tag_audit.py` 报 `健康率 72.5%` / `RESULT: FAIL`）：`skill-install` / `skill-creator` / `skills-security-check` / `install-skill-dependency` / `deep-research-pro` / `cloudbase-webapp-deploy-debug` / `clawhub` —— **7 个全部实测 `disk=False` 且不在注册表**（非判据假阳性，R263 已先证）。根因：D2 只系统性复扫了**直连表**（`direct_map`），**未同步复扫负标签表**（`tag_layer.py:NEGATIVE_TAG_MAP`） | 还债方式：清理 7 个 ghost 键 + 7 处引用后复跑 `negative_tag_audit.py`（健康率应 → 100%）+ `test_router_regression.py` ALL PASS → 见第 10 轮建议 #5（破坏性）—— **✅ 校正注（2026-09-23 销账）：已闭环** —— B1 已执行；本轮实测 `negative_tag_audit.py` = 健康率 100% / `RESULT: PASS`

- [DEBT] **`fenjue_measure.py:168` 引用不存在的 `behavior_core.md` 路径**（真实位置为 `core/behavior_core.md`）→ 取 size=0，**D1 少算该 P0 文件**（2026-09-22 第 10 轮 `attention_sim.py` 实测告警，属上游口径差异） | 还债方式：改 `fenjue_measure.py` 路径并重跑评分 → 见第 10 轮建议 #8（破坏性）—— **✅ 校正注（2026-09-23 销账）：已闭环** —— B3 已执行；本轮实测 `fenjue_measure.py:182` 已为 `core/behavior_core.md`
