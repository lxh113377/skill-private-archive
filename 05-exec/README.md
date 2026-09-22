# 05-exec — 执行证据索引

> 更新：2026-09-22 | 本目录 = 阶段4/5 的**执行证据**（补丁 JSON + 轮次报告），不含计划文档（计划在 `04-plan/`）。

## 轮次报告

| 报告 | 覆盖轮次 | 执行内容 | 收口 commit |
|---|---|---|---|
| `第2轮执行报告.md` | 2026-09-14 第 1~2 轮 | 批1 路径漂移 34 处 / 批3 拆卷 / 退役 6 件 / A3-A5 元数据 | `1b6fe6d` `f8bc12f` `716ae69` `bc225b3` 等 |
| `第3轮执行报告.md` | 2026-09-22 第 3 轮 | A-project-better 四维体检 + 7 项非破坏性整改 | 待确认（D4） |
| `第10轮执行报告.md` | 2026-09-22 第 10 轮 | A-project-better **Step 0 首次实跑**（10 条台账）+ 记忆层滞后回写 + 阶段1 补齐（三脚本实跑 + 通配符检测入编 + **2 处判据缺陷修复**）+ 10 条建议清单 | 待确认（B5） |

## 补丁索引（19 个 JSON，全部走 `rule_editor.py replace --patch`）

> **📁 位置变更（2026-09-23 第 12 轮）**：19 个补丁均已应用（见各行结果 commit），原件已整体迁至
> `../archive/applied-patches-2026-09/`（git mv 保历史）；本表文件名相对该目录。05-exec 根目录只保留脚本与未归档轮次产物。

| # | 补丁文件 | 对应 P0 | 目标 skill | 改动摘要 | 结果 commit |
|---|---|---|---|---|---|
| 1 | `patch_P0-2_cps-skillmd.json` | P0-2 | `cross-platform-agent-sync/SKILL.md` | description 口径修正 + 版本 1.2.1→1.3.0 | `4715713` |
| 2 | `patch_P0-2_cps-part1.json` | P0-2 | `.../cps.part1.md` | 平台口径对齐在役端 | `4715713` |
| 3 | `patch_P0-2_cps-part2.json` | P0-2 | `.../cps.part2.md` | 同上 | `4715713` |
| 4 | `patch_P0-2_cps-part3.json` | P0-2 | `.../cps.part3.md` | 同上 + QW 特例段改留痕 | `4715713` |
| 5 | `patch_P0-2_cps-part4.json` | P0-2 | `.../cps.part4.md` | 同上（含 QW 段） | `4715713` |
| 6 | `patch_P0-2_cps-part5.json` | P0-2 | `.../cps.part5.md` | 同上 | `4715713` |
| 7 | `patch_P0-2_cps-part6.json` | P0-2 | `.../cps.part6.md` | 同上 | `4715713` |
| 8 | `patch_P0-2_cps-part7.json` | P0-2 | `.../cps.part7.md` | 同上 | `4715713` |
| 9 | `patch_P0-2_cps-part8.json` | P0-2 | `.../cps.part8.md` | 同上（含 P0-14 死引用删除目标） | `4715713` |
| 10 | `patch_P0-5_chaoshi-image.json` | P0-5 | `chaoshi-image-optimization` | ffmpeg 硬编码 `8.1.1` → 动态探测（实测本机 9.0）；1.1.0→1.2.0 | `eb77870` |
| 11 | `patch_P0-6_fenjue-routing.json` | P0-6 | `fenjue-routing-health-check` | CHECK-3 写死 `part1..4` → 动态枚举（实测 16 卷）；2.5.1→2.5.2 | `eb77870` |
| 12 | `patch_P0-10_hook-analyzer.json` | P0-10 | `hook-analyzer-skill` | 上游 `video-breakdown-skill` 缺失 → 悬空标注；1.0.0→1.0.1 | `eb77870` |
| 13 | `patch_P0-10_report-generator.json` | P0-10 | `report-generator-skill` | 同上；1.0.0→1.0.1 | `eb77870` |
| 14 | `patch_P0-10b_hook-analyzer.json` | P0-10b | `hook-analyzer-skill` | 上游补建后回填真实命令；1.0.1→1.0.2 | `e145651` |
| 15 | `patch_P0-10b_report-generator.json` | P0-10b | `report-generator-skill` | 同上；1.0.1→1.0.2 | `e145651` |
| 16 | `patch_P0-12_openclaw-fenjue-weekly.json` | P0-12 | `openclaw-fenjue-weekly` | 收尾门禁平台枚举 → 在役端 `OC/WB/TR/CX/HM`；2.0.1→2.0.2 | `eb77870` |
| 17 | `patch_P0-14_cps-skillmd.json` | P0-14 | `cross-platform-agent-sync/SKILL.md` | 版本 1.2.0→1.2.1 | `eb77870` |
| 18 | `patch_P0-14_cps-part8.json` | P0-14 | `.../cps.part8.md` | 删 `A-memory-align` 死引用行（全库 0 命中） | `eb77870` |
| 19 | `A5_patch.json` | A5 | `openclaw-dual-gate-quality-audit` | description 收窄 + 新增「何时不用本 skill」负向边界段 | `bc225b3` |

> 覆盖核对：`patch_*.json` 实测 18 个 + `A5_patch.json` 1 个 = **19/19**（2026-09-23 迁移后实测 `archive/applied-patches-2026-09/` 计数 19，与目录一致）。
> 已知工具坑（历史记录，保留原文）：`rule_editor.py replace` 对**删除类补丁**曾恒报 `[verify] FAIL 未找到: <旧文本>`（回退搜旧文本的误报），写盘实际成功。

## 脚本与补丁素材（2026-09-22 第 4 轮新增）

| 路径 | 用途 | 关键产出 |
|---|---|---|
| `D1-patches/` | D1 门禁判据修复的 5 份补丁 + 索引 `README.md` | 受管根 commit `7cc7d4d`（`A-project-handoff` V3.42.0） |
| `D4-patches/` | ④ 回收站升级的 6 份补丁（facade / audit / SKILL / disciplines / commands / version-history） | 受管根 commit `49789bb`（`A-project-handoff` V3.43.0） |
| `recycle_selftest.py` | ④ 回收站两层自检（回落分支隔离桩 + 真机 CLI + 哈希级复原判据） | **18/18 通过**（真机 `method=recycle_bin`） |
| `unretire_31.py` | ② 从 `retired_skills` 摘除 31 项（dry-run / `--apply` + 写后守恒） | 焚诀 commit `28daf6e`（注册表 120→151） |
| `R270-patches/` | 修 `--fix-mirror` 的 3 份补丁（rule_editor 自身 / SKILL.md / version_history） | 受管根 commit `7d8a8e1`（`A-memory-start` V10.63.0） |
| `D5-patches/` | R269 落盘补丁 + 本轮 footer 素材 | 受管根 commit `f1e941a`（A-memory-start V10.62.0） |
| `user_created_audit.py` | 注册表 `user_created` 失真复核（含口径裁定与三类判据） | `user_created_audit.json` |
| `user_created_audit.json` | 120 条逐条明细 + 三类失真清单 + 阶段0 清单交叉 | A/B 类均为 **0**；C 类 85（判据不可靠） |
| `direct_map_dead_targets.py` | 直连表死目标扫描（双源判据：注册表 ∪ 磁盘） | `direct_map_dead_targets.json` |
| `direct_map_dead_targets.json` | 死目标清单（修复前 7 目标 / 11 条，修复后 **0**） | 焚诀 commit `bf5e284` |

> 中间产物已归档：`01-scan/overlap_raw.txt`（282,977B）→ `../archive/overlap_raw.txt`（2026-09-22，D3）。
