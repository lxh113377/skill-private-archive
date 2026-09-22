# 06-constraints.part1.md

<!-- 本卷为 06-constraints.md 的延续（R199.5） -->

## 已闭环条目归档（R279 活载卷自愈迁移）

- [BUG→**已修复**] `handoff.py review` 判 `08-ac-obs.md: 3 个验收标准，格式正确`，实际这 3 条全在 `<!-- 示例： ... -->` 注释内 — 影响范围：**假通过**，交付就绪度被高估；根因 `handoff_lib/savepoint.py:632` 用 `re.findall(r"AC-OBS-\d+", content)` 全文匹配、不剔注释 | 状态：**已修复**（受管根 `7cc7d4d`，`A-project-handoff` **V3.42.0**；`common.py` 新增 `strip_html_comments()` 作单一真相源；层a 隔离桩 11/11 + 层b 含对照；本项目 `review` 56% → **100%**）

- [BUG→**已修复**] `handoff.py review` 判 `05-feature-status.md: 没有记录任何功能状态`，实际该文件有 10 条已完成条目 — 影响范围：**假阴性**，误导为「记忆未填」；根因同文件 `:594` 正则 `^-\s*(\[x\]|\[ \]|[✅🚧📋])` 只认 `- ✅` 形态，不认「`## ✅ 已完成` + 普通 `- 描述`」写法 | 状态：**已修复**（同上；新增 `has_feature_entries()` 兼容章节式；层b 反例 = 注释-only 合成项目仍报「没有定义 AC-OBS」，防线未放松）

- [BUG→**已修复**] `handoff.py status` 判 `02-structure.md ✅ filled (auto-synced)`，同日 `review` 判 `尚未运行 sync，目录树为空` — 影响范围：同一文件两子命令结论相反，门禁口径自相矛盾（`status` 只数非空行） | 状态：**已修复**（同上；`status` 结构类先判 `is_sync_placeholder()` 再累加计数，两子命令现同结论）

- [BUG→已解除] `handoff.py savepoint` 于 2026-09-22 01:17 **曾被拒**：`[GATE:noise-fail]` VIOL `焚诀\.codebuddy\` —— 该目录是**运行中 IDE 的会话数据**（当日日志 mtime 分钟级），**不是 agent 交付物**。⚠️ 关键教训：**#17 字面处置「迁 `_trash`」在此是错的**（会破坏活动工具状态）；正确出口 = `noise_lint` 既有机制「被 `.gitignore` 命中 → 降级 `quarantine`」 — 状态：**已解除**（并行会话 2026-09-22 01:20:13 补 `焚诀\.gitignore:9` 的 `.codebuddy/`，commit `1f354e9`）→ `noise` 复跑 `[GATE:noise-pass]`（四根 violation=0），本项目 `savepoint` 复跑 **exit 0「本次对话已安全落盘」**
  - 归属说明（⚠️不能确证）：本会话确实执行过 `Set-Location …\焚诀`（cwd 曾为焚诀），故**可能是写入方之一**；但该目录性质为「活跃 IDE 会话数据」，同一时段另有并行会话在焚诀作业，无法单方归因。教训已吸收：跨受管根跑脚本改用 `Push-Location` + `Pop-Location`（本会话后段已改）
