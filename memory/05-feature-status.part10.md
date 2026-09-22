# 05-feature-status.part10.md

<!-- 本卷为 05-feature-status.part9.md 的延续 -->

## ✅ 已完成（2026-09-23 第 13 轮）

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

- trim-shell 双重盲区修复 + 本项目记忆自愈（2026-09-23 第 13 轮 r3，上游 A-project-handoff **V3.47.0**）：① 调用面与条目识别双修复（cmd_trim_shell/savepoint 遍历 SPLIT_TARGETS + 认 ✅/已完成章节普通列表）；② 验证 = 隔离桩 15/15 + py_compile + gates 三项 pass + 本项目实跑 05 主壳 5,130B→1,036B 迁 11 条零误伤；③ split 拆出 part9、07 摘要历史 6 条迁 part6、AGENTS.md 重生成（05 节 -3,887B）；④ P1-3a 裁定不做（无上游机制支撑，登记上游建议）
