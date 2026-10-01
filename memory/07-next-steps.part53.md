# 07-next-steps.part53.md

<!-- 本卷为 07-next-steps.part52.md 的延续 -->

- [x] **【r21d 复测闭环·新机器型判据】** 「转办前先复测归属方是否已自落」升格为机器型：判据 （转办登记表 vs 焚诀 verify 注册面，两下限 AND；取不到真相源 = UNVERIFIED + exit 2，禁默认放行）+ 登记表 （schema ，3 件带 keywords/why）+ 夹具  **26/26**（红阶段实测 ；变异对照 4/4 被拦，含一次「变异设计自身不可证伪」的自纠）。真跑实测：1 件 OBSOLETE（注入区合一，被 C25/C31 覆盖 4/4 词）、2 件 VALID，与 r21c 人工复测一致。挂在 「项目门禁命令」**条件前置**（只在要外推时跑，非每轮必跑）。**取值**：=== 转办件过期检测 (33 条已注册判据 / 3 件待外推) === 【r47 裁决=作废｜定年：r? 登记（git log -S 实测首现 2026-09-24）→ 该判据已落地为常驻机制，条目本身已完成】 【r48 裁决=作废｜判据已落地为 05-exec/transmit_obsolescence_check.py 与 26 例夹具，转办面见 06-benchmark/transmit_proposals.json】
  VALID      catalog_tax_ratchet    平台技能目录注意力税棘轮 | 最强候选 C20 仅命中 1/3 词（占比 0.33），未达双下限 ⇒ 仍有效
  OBSOLETE   inject_union_merge     注入区口径合一（多项目注入壳并入统一预算） | 已被 C25、C31 覆盖：命中 4/4 词（如 注入、预算、台账、归因）
  VALID      claim_truth_gate       计数断言内容级门禁（注入文本里的数字断言与真相源对账） | 最强候选 C29 仅命中 1/3 词（占比 0.33），未达双下限 ⇒ 仍有效
