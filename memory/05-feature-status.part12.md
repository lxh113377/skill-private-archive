# 05-feature-status.part12.md

<!-- 本卷为 05-feature-status.part10.md 的延续 -->

## ✅ 已完成（2026-09-23 第 13 轮）

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

- 代码质量五维审查 + A/B/C 批执行（2026-09-23 r8，3 只读子代理并行审查 → 用户按钮选 A+B/C 批）：**A 批** = `apply_patches.py` 4 修（①CRLF 双重换行 P0：读取归一化+按原行尾复原 ②临时文件+os.replace 原子写 ③写盘事务化+失败自动回滚 ④行区间重叠预检+相对路径按补丁目录解析）——正反夹具 **12/12**（CRLF/LF/BOM 保持、重叠拒绝、只读写失败自动回滚、跨目录相对路径）；`scan_all.py` 8 修（frontmatter CRLF ×2、死链分支不可达+切片错 P0×2、quotepath、QW/CC 正则、meta.json fail-open 留痕、references isdir、walk 剪枝）+ 清单打分文案对齐——py_compile ×3 + 双阶段 dry-run exit 0。**B 批** = 120/151 双口径注记（user_created_audit.json / direct_map_dead_targets.json 加 `_registry_epoch`）+ AC-OBS-03 校正注 + 清单 L7 打分说明校正注 + 根 README overlap_raw 陈旧引用清理 + 01-scan README 裸数组标注与 r8 漂移登记 + 05-exec README 补丁双格式 runner 标注。**C 批** = user_created_audit.py `generated` 动态化；truth_constants 失真按焚诀红线只登记（07 r8 条）。**重要发现**：scope 复跑 = 56/21 vs 冻结 51/26（切分漂移非笔误，冻结件不动，待裁定）
