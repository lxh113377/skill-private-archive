# 05-feature-status.part4.md

<!-- 本卷为 05-feature-status.part3.md 的延续 -->

## ✅ 已完成（2026-09-22 第 5 批：用户追加授权 ①②④）

- **D5 GM 日志空档留痕**：`D:\global_memory\memory\2026-09-22.md` 追加「R9 事故 · 每日日志空档说明（事后补记）」（**不补造当日日志**）；`[GATE:evolution-pass]`

## ✅ 已完成（2026-09-22 第 5 批：用户追加授权 ①②④）

- **① 阶段0 清单按 151 重出**：先修 `01-scan/scan_all.py` 的**失效数据源**（`platform-oc.json` 随 OC 退役已被删 → 实跑 `FileNotFoundError`；口径回落为「在役端 `platform-*.json` 的 `user_created_skills` 并集」）；v1 三件**原样归档** `archive/scope-v1-169-2026-09-14/`（R241）；v2 结果 = **HIGH 51 / MID 26 / LOW 30 / EXCLUDE 43**（自建 **77**，失真 41）⇒ 记忆里「自建 ≈90 / 169 条」基数**全部作废**
- **② 31 件入册**：**认知修正** —— 不是"漏注册"，而是被 `RETIRED_SKILLS`（R198.6 fail-closed）有意排除（31/31 全命中）；摘除黑名单 **100 → 69** → `build_registry` 注册表 **120 → 151** → `build_indexes --apply`（BGE/TF-IDF `(151,512)/(151,5000)`、25 派生件、守恒 PASS）
  - 顺带修 **2 处派生件脱节（纪律 #18 族）**：C6（GM `cross_platform_map.json` note 引用 V1.21 → 同步 V1.22）；C16（`STATUS.md`/`STATUS.part1.md` 内容过期写 120 skills → **用生成器 `aggregate_status.py` 重出**，不手改数字）
  - 收口：焚诀 `verify` **16 PASS / 0 FAIL / 0 SKIP**；路由回归 **ALL PASS**；双仓提交 SHA 一致（焚诀 `28daf6e` / GM `575ca99`）
- **④ A-project-handoff 工作流升级「删除 → 回收站」**（受管根 commit `49789bb`，**V3.42.0 → V3.43.0**）
  - 用户口径：**两者结合**（系统回收站优先 + `_trash` 回落 + 两路都写 manifest）+ **升级为致命纪律**
  - 新增 `handoff_lib/recycle.py`（`recycle`/`restore`/`read_manifest`/`anchor_for`/`recycle_bin_available`）+ CLI `recycle <path>|--list|--restore` + **致命纪律 #21** + `commands.md` §18 + 决策树/分卷索引/facade 计数同步
  - **防静默永久删除**：`FOF_ALLOWUNDO` 在无回收站的卷上会被忽略而直接永久删 → 先探测「盘符根下 `$Recycle.Bin`」，不存在则显式走 `_trash`
  - 连带修 `audit forget` 的 `os.remove(src)` 硬删点 → 走回收站（失败即中止不静默）
  - 验证 **18/18**：层a 隔离桩（回落分支/反例/哈希级复原/二次复原拒绝）+ 层b 真机 CLI（**实测 `method=recycle_bin`**）
  - 收口：`gates` 三门禁全绿（镜像经手工 `-Fix` 补齐）、`coldstart --check` 6 行全等、焚诀 `verify` 16 PASS
  - ⚠️ **新发现**：`rule_editor.py commit --fix-mirror` **未生效**（commit 后镜像 missing=1/mismatch=6，须手工补）
- **R269 落盘（用户批准本轮 footer 未闭环项）**（受管根 `f1e941a`，`A-memory-start` **V10.61.8 → V10.62.0**）
  - 规则：「同项门禁/扫描**两入口结论不一致**时，先查**对象 mtime** 与**仓库提交序**、并**当下复跑**，三者齐了才允许写『判据缺陷』」
  - 伴生结论：**活跃工具目录**（`.codebuddy` 等 IDE 运行态目录）**不能按致命纪律 #17 字面迁 `_trash`**，正确出口 = 被 `.gitignore` 命中 → 降级 `quarantine`
  - 落点：`SKILL.md`「现状核验 / 历史留痕速查」区**区内追加**（R251 合规：落盘前实测 268 行 / 59,870B / 速查区 6 → 落盘后 **275 行 / 62,003B / 速查区仍 6**）+ `version_history.md` 前置条目 + C13 锚点行同步
  - 收口：`gates` 三门禁全绿（镜像经手工 `-Fix`）、`coldstart --check` 6 行全等、焚诀 `verify` **16 PASS / 0 FAIL**
