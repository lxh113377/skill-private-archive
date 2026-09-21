# 03 - 技术栈

> 本文件记录项目使用的技术栈。sync 命令会自动更新此文件。
> 归档类型：快照（整体复制到归档）

<!-- SYNC_AUTO_GENERATED_START -->
（未检测到技术栈配置文件）
<!-- SYNC_AUTO_GENERATED_END -->

## 构建与部署
<!-- 手动补充（2026-09-22 实测回填） -->
- 构建：无构建流程。产物为 Markdown 报告 + JSON 数据 + patch JSON，直接落盘。
- 部署：无部署。唯一"发布"动作 = `git commit` + `git push` 到私有归档仓
  `https://github.com/lxh113377/skill-private-archive.git`（基线判据：`git rev-parse HEAD` == `git ls-remote origin main`）。

## 运行时要求
<!-- 手动补充（2026-09-22 实测回填） -->
- **执行环境**：Windows + PowerShell 7（core）。
- **Python**：本机实测可用 `C:\Program Files\Python312\python.exe`（首选）；焚诀门禁用 managed venv
  `C:\Users\37533\.workbuddy\binaries\python\envs\default\Scripts\python.exe`（依赖已对齐，含 onnxruntime BGE 后端）。
- **必设环境变量**：`PYTHONPYCACHEPREFIX`（防 `__pycache__` 重建在受管根内）。
- **外部依赖（脚本级，非包管理）**：
  - `D:\global_skills\A-project-handoff\scripts\handoff.py` —— 项目记忆管理（init/sync/review/savepoint/split/noise）
  - `D:\global_skills\A-memory-start\references\rule_editor.py` —— 受管根规则文件编辑 + 三门禁（mirror/noise/evolution）
  - `C:\Users\37533\Desktop\workspace\焚诀\eval\` —— `unified_router.py`（路由）/ `verify_truth_consistency.py`（真相源）
- **编码**：全部 UTF-8，无 BOM。
