# 07-next-steps.part53.md

<!-- 本卷为 07-next-steps.part52.md 的延续 -->

- [x] **【r21d 复测闭环·新机器型判据】** 「转办前先复测归属方是否已自落」升格为机器型：判据 （转办登记表 vs 焚诀 verify 注册面，两下限 AND；取不到真相源 = UNVERIFIED + exit 2，禁默认放行）+ 登记表 （schema ，3 件带 keywords/why）+ 夹具  **26/26**（红阶段实测 ；变异对照 4/4 被拦，含一次「变异设计自身不可证伪」的自纠）。真跑实测：1 件 OBSOLETE（注入区合一，被 C25/C31 覆盖 4/4 词）、2 件 VALID，与 r21c 人工复测一致。挂在 「项目门禁命令」**条件前置**（只在要外推时跑，非每轮必跑）。**取值**：=== 转办件过期检测 (33 条已注册判据 / 3 件待外推) === 【r47 裁决=作废｜定年：r? 登记（git log -S 实测首现 2026-09-24）→ 该判据已落地为常驻机制，条目本身已完成】 【r48 裁决=作废｜判据已落地为 05-exec/transmit_obsolescence_check.py 与 26 例夹具，转办面见 06-benchmark/transmit_proposals.json】
  VALID      catalog_tax_ratchet    平台技能目录注意力税棘轮 | 最强候选 C20 仅命中 1/3 词（占比 0.33），未达双下限 ⇒ 仍有效
  OBSOLETE   inject_union_merge     注入区口径合一（多项目注入壳并入统一预算） | 已被 C25、C31 覆盖：命中 4/4 词（如 注入、预算、台账、归因）
  VALID      claim_truth_gate       计数断言内容级门禁（注入文本里的数字断言与真相源对账） | 最强候选 C29 仅命中 1/3 词（占比 0.33），未达双下限 ⇒ 仍有效

- [x] **【r21e 证据可解析性 + 归因抬基线】** `upgrade_footer_gate.py` 的 `RE_EVID` 原只校形状，形状合格却指不到东西的假锚照样放行。边界测量（`evidence_resolvability_measure.py`，近 3 日 97 条已闭环声明）：可解析 52 / 形状合规但解析不到 37（38.1%）/ 形状不合规 8。据此分三级：`FAKE`（路径不存在、或 backup ID 在回滚目录与五仓 git 对象全无 ⇒ 阻断，仅 4/97 不可事后合理化）、`STALE`（文件在但版本 token 被后续提交推走 ⇒ 只告警，追溯拦人即误伤 18/97）、`SKIP`（体系外绝对路径 ⇒ 不判，防误伤第三方端点）；同时形状层 V 前缀改为可选（真实文件写的是裸值 `version: 10.70.0`，只收 V 前缀等于奖励美化而非真实）。夹具 `05-exec/r21e_gate_probe.py` 5/5（红阶段：伪造 backup 锚打补丁前 rc=0 放行、补丁后 rc=1）。配套 `ratchet_gate.py` 新增唯一合法上调通道 `--raise-baseline`（commit+path+delta+reason 四要素、delta 与实增逐字节相等、path 须在注入面成员内、commit 须能在该仓解析；无增长时拒绝抬，防刷账），并永久留账 `attributed_raises`；本轮实测用它接受 +447B（并行会话立 #23 所致，非本仓动作），基线 86,346→86,793。夹具 `05-exec/r21e_ratchet_attrib_fixtures.py` 16/16（含变异 4/4）。取值：`python 05-exec/ratchet_gate.py`（期望 `[RATCHET:PASS]` 且打印留账 1 条）。 【r47 裁决=作废｜定年：r30 登记（git log -S 实测首现 2026-09-25）→ 归因抬基线与证据解析已落地（ratchet --raise-baseline 需归因、多项同长即拒）】

- [x] **【P1·待办 W-21（r49 新立）】** 是否把 unowned_claims 升为棘轮第 10 指标：先量误报率再决定，未量出 0 误报前不得接线（r25 用户否决拦任务的闸门）。 【r49 裁决=作废（不接线）｜实测 27 条归属声明全部 OWNERED、UNOWNED=0：恒定 0 的指标是假绿面；且 OWNERED 判据精度低（正文含任意路径 token 即从 UNOWNED 翻成 OWNERED ⇒ 可刷），第 10 指标收益不抵噪声。牙齿已由 r39 夹具 t40-t46 变异桩持有，不重复建】
