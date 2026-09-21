# 05 - 功能状态

> 本文件记录功能/任务的完成状态。
> 归档类型：增量（已完成项归档时移入 archive/）

## ✅ 已完成

- 阶段0 范围裁定（2026-09-14）
  - 产出 `00-scope/自建skill清单.md`、`注册表失真条目.md`、`scope_result.json`
  - 结论：自建 102 / EXCLUDE 34 / 灰区 33 / 失真 42
- 项目记忆初始化（2026-09-14）：memory/ 8 文件 + archive/ + P-1 绑定表 + .aiexclude

- 阶段1 四维机器扫描（2026-09-14）
  - 产出 `01-scan/scan_report.md`、`scan_result.json`、`overlap_raw.txt`
  - 结论：超4KB 83/102、弱触发 9、真死链 4、弃用平台名 25、合并候选 4 簇

- 阶段2 第1批：A族 5 个精读（2026-09-14）→ `02-review/A族_精读.md`

- 阶段3 审计报告（2026-09-14）→ `03-audit/自建skill优化审计报告.md`：P0 共 25 项（分三梯队）、P1 按族、P2 合并决策、阶段4 分 5 批

- 阶段4 实施计划（2026-09-14）→ `04-plan/实施计划.md`：5 批共 40+ 项，每项含目标文件/改动/验证命令/回滚手段；建议顺序 批3→批1→批2→批4→批5

- 阶段4 A3/A4/A5（2026-09-14, commit `bc225b3`）：9 补 `version` + 1 收窄 description 并补负向边界 + 7 回填 `meta.json` description → 17 文件一次收口，`[GATE:mirror-pass]`、工作区 status=0
  - 实测修正 3 处清单偏差：A3 实存 13（`skill-install` 已退役）其中 4 个为市场件应跳过；A4 清单漏 `local-vram`；A4 性质 = 上游 marvis 打包 bug（不参与路由）

- 阶段4 批3.1 拆卷（2026-09-14, commit `f8bc12f` + `V3.37.1`）：`A-project-handoff/SKILL.md` **85,508B → 3,827B（≤4KB）**，分入 `references/` 5 卷（disciplines / skill-binding / memory-structure / commands / version-history），内容零丢失
  - **回归修复**：拆卷使 `COLD_START_DECL` 锚点迁出 SKILL.md → `coldstart --check` exit 1 → **所有项目 savepoint 被误拒**；修 `handoff.py cmd_coldstart` 锚点回退链（SKILL.md → `references/*.md`），实测 `✅ 6 行逐行 diff 全等`
  - 经验：**大型 skill 拆卷必须同步检查「按 SKILL.md 定位的机器锚点/门禁」**（coldstart 锚点、行号引用、脚本内硬编码路径）
- 阶段4 批4 元数据（2026-09-14）：`ican-frontend-design-system` version 1.0.0→4.0.0（对齐版本表 V4）；`dogfood`/`testing` 补 `version: 1.0.0`

- 批5-b `story-scan` 合并（2026-09-14, commit `15449b0`，27 文件）：`story-long-scan`(17.3KB) + `story-short-scan`(9.2KB) → 统一入口 `story-scan`（`--length=long|short`）
  - 结构：`SKILL.md` 5,343B（第0步分流 + 采集质量门 + 分卷索引 + 流程衔接）+ `references/scan-long.md`(16.8KB 原文) / `scan-short.md`(8.8KB 原文) + 其余 6 references + 8 scripts（`cdp-utils.js` 去重）
  - 顺带**补齐审计指出的「短篇缺采集质量门」** → 提为两篇通用
  - 11 处引用方文本更新（`story/`、`story-long|short-analyze|write`）+ 4 个命令文档改名（`story-scan-long|short.md`）；旧件 → `_trash/retired-2026-09-14-story-scan-merge`
  - 风险控制：两篇正文**按原文搬运未改写**（git rename 识别 97%/95%），旧件入 `_trash` 可回滚
- 灰区裁定（用户 2026-09-14）：Intel 分发样例包（`local-asr`/`computer-use`/`realtime-translator`/`tts`/`txt2img`）+ 25 个边缘件 → **排除**，不纳入维护范围

## 分卷目录
- **卷1** `05-feature-status.part1.md` — 进行中 / 计划中 / 阻塞
- **卷2** `05-feature-status.part2.md` — 已完成：2026-09-19 第 3 轮（P0-2 收口 + 补建上游 + 注册表重建）

