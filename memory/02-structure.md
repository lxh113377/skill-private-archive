# 02 - 仓库结构

> 本文件记录项目目录结构。sync 命令会自动更新此文件。
> 归档类型：快照（整体复制到归档）

<!-- SYNC_AUTO_GENERATED_START -->
```
├── .codebuddy/
│   ├── plans/
│   │   └── 自建skill体系优化审计_33834ceb.md
│   └── settings.local.json
├── 00-scope/
│   ├── scope_result.json
│   ├── 注册表失真条目.md
│   └── 自建skill清单.md
├── 01-scan/
│   ├── scan_all.py
│   ├── scan_report.md
│   └── scan_result.json
├── 02-review/
│   ├── A族_精读.md
│   ├── fenjue族_精读.md
│   ├── local族_精读.md
│   ├── skill审计族_精读.md
│   ├── story族_精读.md
│   └── 其他族_精读.md
├── 03-audit/
│   └── 自建skill优化审计报告.md
├── 04-plan/
│   ├── 剩余待办分类清单.md
│   ├── 实施计划.md
│   └── 工作流专项建议.md
├── 05-exec/
│   ├── D1-patches/
│   │   ├── d5_gap_note.txt
│   │   ├── p1.json
│   │   ├── p1_anchor.txt
│   │   ├── p1_inserted.txt
│   │   ├── p2_savepoint.json
│   │   ├── p3_projcmds.json
│   │   ├── p4_version.json
│   │   ├── p5_vh.json
│   │   └── README.md
│   ├── A5_patch.json
│   ├── direct_map_dead_targets.json
│   ├── direct_map_dead_targets.py
│   ├── patch_P0-10_hook-analyzer.json
│   ├── patch_P0-10_report-generator.json
│   ├── patch_P0-10b_hook-analyzer.json
│   ├── patch_P0-10b_report-generator.json
│   ├── patch_P0-12_openclaw-fenjue-weekly.json
│   ├── patch_P0-14_cps-part8.json
│   ├── patch_P0-14_cps-skillmd.json
│   ├── patch_P0-2_cps-part1.json
│   ├── patch_P0-2_cps-part2.json
│   ├── patch_P0-2_cps-part3.json
│   ├── patch_P0-2_cps-part4.json
│   ├── patch_P0-2_cps-part5.json
│   ├── patch_P0-2_cps-part6.json
│   ├── patch_P0-2_cps-part7.json
│   ├── patch_P0-2_cps-part8.json
│   ├── patch_P0-2_cps-skillmd.json
│   ├── patch_P0-5_chaoshi-image.json
│   ├── patch_P0-6_fenjue-routing.json
│   ├── README.md
│   ├── user_created_audit.json
│   ├── user_created_audit.py
│   ├── 第2轮执行报告.md
│   └── 第3轮执行报告.md
├── .aiexclude
├── AGENTS.md
├── README.md
└── TODO.md
```
<!-- SYNC_AUTO_GENERATED_END -->

## 模块说明
<!-- 手动补充（2026-09-22 实测回填；本工作区无 src/ 与 tests/，目录按六阶段对齐） -->
- `00-scope/` — 阶段0 范围裁定：自建清单 + 注册表失真条目 + 原始打分数（`scope_result.json`）
- `01-scan/` — 阶段1 四维机器扫描：报告 + 结果 JSON + 重叠原始件 + **唯一可复跑脚本 `scan_all.py`**
- `02-review/` — 阶段2 全量精读：6 份族审计卡（A族 / fenjue / 审计族 / local / story / 其他）
- `03-audit/` — 阶段3 审计报告：四维结论 + P0/P1/P2 分级
- `04-plan/` — 阶段4 实施计划与阶段5 专项建议（含验证命令 + 回滚手段）
- `05-exec/` — 阶段4/5 **执行证据**：`README.md`（补丁索引）+ 2 份轮次报告 + 19 个 patch JSON
- `memory/` — handoff 8 文件 + 分卷 + `AGENTS.md`（P-1 绑定表）+ `archive/`（安全网，**当前为空**）
- `.codebuddy/` — 平台元数据（plans / 记忆），已在 `.gitignore` 内，不入库
