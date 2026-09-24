# 待落地补丁：A-get-memory「判据类工具交付三条硬判据」

- **为什么本仓不代改**：`D:\global_skills\A-get-memory\SKILL.md` 与
  `references/step2_4_missed_audit.md` 当前为并行会话**在途**（`git status --porcelain` 首列 `M` = 已 staged，
  frontmatter 已到 `version: 4.29.0` > 本会话所见的 4.27.0）。按 R269 只登记不擅动；
  且本会话刚落地的「写前脏源检测」（受管根 `9a15f4e`）对此类提交本就 fail-closed。
- **一条命令落地**（归属会话，A-get-memory 干净后执行）：

```bash
python D:/global_skills/A-memory-start/references/rule_editor.py replace   --file A-get-memory/SKILL.md   --patch 05-exec/r20-patches/patch_agetmemory_jig_clause.json --dry-run
# 六处全命中后去掉 --dry-run，并把 frontmatter 4.29.0 → 4.30.0 与版本历史条目一并 commit
```

- **验收**：`grep -c "判据类工具交付三条硬判据" A-get-memory/SKILL.md` = 1；
  `rule_editor.py gates` 三门 pass；`check-skill-mirror.ps1 -Fix` 后 `mirror=pass`。
- **根因证据**：r18 一次交付 4 个判据工具**零夹具**（违反本 skill Step 2.7 与「新判据交付契约」）；
  r19 补夹具 55 例、r20 补变异对照 4/4 —— 若无这三条硬判据，下一个交付仍会重犯。
