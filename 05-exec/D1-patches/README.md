# D1-patches — D1 补丁证据（2026-09-22）

> 全部经 `rule_editor.py replace --patch <json>` 应用；先 `--dry-run` 预览命中（须逐处命中），后统一 `commit --fix-mirror` 收口。
> 收口提交：受管根 `7cc7d4d`（`A-project-handoff` V3.41.5 → **3.42.0**）。

| 补丁 | 目标文件 | 处数 | 内容 |
|---|---|---|---|
| `p1.json` | `A-project-handoff/scripts/handoff_lib/common.py` | 1 | 新增 3 个共用判定函数（`is_sync_placeholder` / `has_feature_entries` / `strip_html_comments`），下沉单一真相源 |
| `p2_savepoint.json` | `A-project-handoff/scripts/handoff_lib/savepoint.py` | 7 | ① import 补 3 函数 ②③④ 02/03/04 改用 `is_sync_placeholder()` ⑤ 05 改用 `has_feature_entries()` ⑥ 08 计数前 `strip_html_comments()` ⑦ 交叉检查 AC 计数同剔注释 |
| `p3_projcmds.json` | `A-project-handoff/scripts/handoff_lib/projcmds.py` | 2 | ① import 补 `is_sync_placeholder` ② `status` 结构类先判占位再计数（降级必须在 `filled_count` 累加之前） |
| `p4_version.json` | `A-project-handoff/SKILL.md` | 1 | frontmatter `version: 3.41.5` → `3.42.0` |
| `p5_vh.json` | `A-project-handoff/references/version-history.md` | 1 | 新增 V3.42.0 条目 |

素材说明：`p1_anchor.txt` / `p1_inserted.txt` 为 `p1.json` 的 `old_file` / `new_file`（该处替换涉及 47 行新增代码，用文件传参避免 shell 转义问题）。

验证：层 a 隔离桩 **11/11**；层 b 集成含对照（生效路径 PASS ＋ 注释-only 反例仍被拦）；`py_compile` 通过；`pyflakes` 无 `undefined name`（仅存量 unused import 噪声）；本项目 `handoff review` 56% → **100%**。
