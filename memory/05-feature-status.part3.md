# 05-feature-status.part3.md

<!-- 本卷为 05-feature-status.md 的延续 -->

## ✅ 已完成（2026-09-22 第 4 轮：用户授权 D1–D5，全部执行）

- **D1 修 3 处门禁判据缺陷**（受管根 `7cc7d4d`，`A-project-handoff` **V3.42.0**）：AC 计数剔 HTML 注释（假通过）/ 新增 `has_feature_entries()` 兼容「`## ✅ 已完成` + 普通列表项」（假阴性）/ `status` 先判 sync 占位再计数（口径矛盾）；三函数**下沉 `common.py` 单一真相源**。验证：层a 隔离桩 **11/11**、层b 集成含对照（生效路径 PASS ＋ 注释-only 反例仍被拦）、本项目 `review` **56% → 100%**、三门禁全绿、焚诀 `verify` **15 PASS**

## ✅ 已完成（2026-09-22 第 7 批：D7 残留处置）

- **D7 受管根残留处置**（受管根 `172eb88`，`local == remote`）：一次提交 **6 项迁移删除**（5 个 `.rule_backup/A-memory-start.SKILL.md.20260919_*.bak` 已按 D3 轮转至 `D:\global_memory_archive\_trash\backup-rotation\A-memory-start\2026-09-19\`；`_bm_skillid_migration.json` 已按 #17 迁 `global_skills\_trash\`）+ **跟进 33 个 `.rule_backup/*.bak`**；收口 `dirty=0`、三门禁全绿

## ✅ 已完成（2026-09-22 第 8 批：GM 行为核心口径调整）

- **GM「每轮以『老大。』开头」由 P0 降为 P1**（用户裁定：**保留要求、仅换榜位**）+ **P0 全表重排 #1–#17** + 焚诀评分器同步移除 d3 扣分 + 全生效端同步
  - 生效面 **19 文件 / 62 处**：GM 16 文件（`core/behavior_core_p1_map.md` 重排+降级表 / `core/behavior_core_rules_p8.md`(+part1·part2) 标题·正文重排·卷末新增 P1 段 / `core/MEMORY.md` 铁律·计数·列表 / `core/SOUL.md` / `core/BOOTSTRAP.part1.md` / `system/boot_template.md` / `p0_lean.md` / `conflict_resolution.md` / `core/behavior_core_appendix.md` / `memory_content/behavior_core.md` / `memory_content/user_habits.md` / `meta/memory_index_full.part1.md` / `meta/retire_policy.part1.md`（`P0#11→#10`）/ `core/behavior_core.md` 校正注）+ 焚诀 3 文件（`AGENTS.md` / `audit/fenjue_measure.py` / `eval/truth_constants.json`）
  - 传播结构：**OC/WB/TC/CC 为 junction → 改 GM 即四端生效**；CX 直读 GM；焚诀独立仓另改；`.agents` 镜像走 `--fix-mirror`
  - 留痕：GM `fdb86d0` + `a15325f`（修复）；焚诀 `29dfb22` + `03e0e31`（修复）
  - 验证（✅已实测）：焚诀 `verify` **16 PASS / 0 FAIL**（C13 对齐 **V10.64.0**）；全库 `18锚点/18有效` 残留 **0**；`truth_constants.json` `json.load` OK；`fenjue_measure.py` 编译 OK；`coldstart --check` 6 行全等；体量 **291 行 / 66,637 B / 速查区 6**
- **⚠️ 自曝 + 加固 + 落规 R271**（受管根 **V10.63.0 → V10.64.0**）：自写补丁器 `apply_patches.py` 的 `substr` 误实现为**整行覆盖** → **吃掉 6 行**打头内容（含 `truth_constants.json` 的 `"_changed": "…` 键名前缀）→ 焚诀 verify `JSONDecodeError`；**dry-run 与「new 首行存在」校验都拦不住「旧内容被顶掉」** ⇒ 新增 `repair_lines.py`（`git show <父提交>:<path>` 只读取原行 → 行内正确替换 → 回填）+ 补丁器改正语义 + **写前 JSON 模拟校验**（该拦截第二次写坏时实测生效）
- 新增工具（`05-exec/`）：`apply_patches.py`（跨仓多处补丁：全有或全无 + 命中数=1 + 写前 JSON 校验 + 写后双向校验）、`repair_lines.py`（定位式行修复）
- **未闭环（外部引入）**：`gates` 一度转红 = 平台/并行进程生成的 2 个 `*_migration.json`（mtime **02:28:48** > 本轮最后提交 02:21:24）→ 按 R269 **未擅动**，改用 `.gitignore` 豁免使 `noise` 恢复 pass；镜像差异由 `--fix-mirror` 补齐
