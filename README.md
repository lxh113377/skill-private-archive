# 自建 skill 体系优化审计 — 工作区入口

> 更新：2026-09-22 | **跨会话入口 = `memory/07-next-steps.md`（P0 唯一真相源）**
> 权威源：`D:\global_skills`（git）→ 镜像 `C:\Users\37533\.agents\skills`

## 从哪读起（新人 / 新会话，按序）

1. `memory/07-next-steps.md` — P0 未完成项（**唯一入口，先读这个**）
2. `memory/05-feature-status.md` — 已完成 / 进行中 / 阻塞
3. `05-exec/第3轮执行报告.md` — 最近一轮：四维诊断 + 建议清单 + 待确认破坏性项
4. `03-audit/自建skill优化审计报告.md` — 阶段3 全量审计结论（P0/P1/P2）
5. `04-plan/实施计划.md` — 阶段4 分批复核与回滚手段

## 六阶段产物地图

| 阶段 | 目录 | 产物 | 状态 |
|---|---|---|---|
| 0 范围裁定 | `00-scope/` | 自建skill清单.md / 注册表失真条目.md / scope_result.json | ✅ 完成 |
| 1 四维机器扫描 | `01-scan/` | scan_report.md / scan_result.json / overlap_raw.txt / scan_all.py | ✅ 完成（第10轮已补齐；2026-09-23 dry-run scope/scan均exit 0） |
| 2 全量精读 | `02-review/` | 6 份族审计卡（A族 / fenjue / 审计族 / local / story / 其他） | ✅ 完成 |
| 3 审计报告 | `03-audit/` | 自建skill优化审计报告.md | ✅ 完成 |
| 4 实施计划 | `04-plan/` | 实施计划.md / 剩余待办分类清单.md / 工作流专项建议.md | ✅ 完成 |
| 5 执行 | `05-exec/` | README.md（补丁索引）/ 第2轮·第3轮·第10轮执行报告 / 19 个 patch JSON + D1/D4/D5/R270/R271 补丁目录 | ✅ 完成 |
| 记忆 | `memory/` | handoff 8 文件 + 分卷 + P-1 绑定表（AGENTS.md） | ✅ 建档 |

## 边界与铁律

- 阶段 0-3 **只读取证**；阶段 4 起才改 `D:\global_skills`，且**唯一途径 = `rule_editor.py`**（禁 `write_file` 整体重写 skill 文件）。
- 改完必须：重建派生件 → 复跑三门禁（mirror / noise / evolution）。
- 结论一律标注 `✅已实测 / ⚠️部分实测 / ❌未实测`；禁用旧快照、旧记忆、历史报告当现状。
- 落盘编辑前必须输出 `【数据流假设】` 四要素。

## 收口门禁（改完必须复跑）

```powershell
$env:PYTHONPYCACHEPREFIX="$env:TEMP\pycache_verify"
& "C:\Program Files\Python312\python.exe" "D:\global_skills\A-memory-start\references\rule_editor.py" gates
Set-Location 'C:\Users\37533\Desktop\workspace\焚诀'; & "C:\Users\37533\.workbuddy\binaries\python\envs\default\Scripts\python.exe" eval/verify_truth_consistency.py
& "C:\Program Files\Python312\python.exe" "D:\global_skills\A-project-handoff\scripts\handoff.py" review "c:\Users\37533\Desktop\workspace\自建skill优化"
```

> 实测基线（2026-09-22）：`gates` = `mirror=pass noise=pass evolution=pass`；焚诀 `verify` = **15 PASS / 0 FAIL / 0 SKIP**；`handoff review` = 5/9（56%）→ 本轮整改后 **7/9（78%）**。
> ⚠️ **校正注（2026-09-22 第 10 轮，R241 只加注不改写）**：上行为当日**当时为真**的数值。当前实测已推进 —— `handoff review` = **9/9（100%）**（D1 修 3 处判据缺陷后）、`handoff status` = **8/8 sections filled**、焚诀 `verify` = **16 PASS / 0 FAIL / 0 SKIP**（新增 C15/C16）、本项目 HEAD = `632d183`。最新数值以本注为准。
> ⚠️ **追加说明（同日，R241 只加注不改历史）**：
> ① `handoff review` 剩余 2 条 warning **均为上游判据缺陷**所致（非内容缺失），见 `memory/06-constraints.md` [BUG]；
> ② `handoff savepoint` 中途曾 1 次被拒（`焚诀\.codebuddy` 未 gitignore 豁免），已由**并行会话**（焚诀 commit `1f354e9`）解除，最终 **exit 0 通过**——详见 `05-exec/第3轮执行报告.md` 第五-附节（含「活跃工具目录不能迁 `_trash`」与「时间戳盲区」两条教训）。

## 版本控制基线（A-project-handoff 致命纪律 #20）

- 远端：`https://github.com/lxh113377/skill-private-archive.git`（私有归档仓）
- 判据：`git rev-parse HEAD` == `git ls-remote origin main` 的 SHA
