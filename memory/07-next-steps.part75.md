# 07-next-steps.part75.md

<!-- 本卷为 07-next-steps.part73.md 的延续 -->

## 新增待办（下轮承接）

- **常驻门**：第 31 门 `r112_provenance_fixtures`、第 32 门 `provenance_face`。
- **裁决分布**：UP_TO_DATE 10 / LOCAL_AHEAD_KEEP 2 / UPGRADE_REVIEW 12 / UNVERIFIED 15；盲区 143 件**禁读成已核对无缺口**。

### ③ 首件受控升级：writing-plans（改造 3，中优先级）

- 12 件 UPGRADE_REVIEW 里唯一 HIGH（上游增量 73 > 本地独有 31），上游 `obra/superpowers@8ca22dba`（2026-09-25「Release v6.4.2: leaner plans」）。
- 18 处逐段替换经 `rule_editor.py replace --patch`（dry-run 全命中 → --no-commit 写盘 → commit 收口），受管根提交 **7749bdf0**；本地独有 No Placeholders / Remember 段原样保留。
