# 07-next-steps.part181.md

<!-- 本卷为 07-next-steps.part180.md 的延续 -->

- [x] **R211-3（r211 登记，P1·到期 r217）对标改造 M-1** **CI 里「设计内红」与「真故障红」长得一模一样 —— 近 30 run 27 红全来自同一道本机专属门，读起来像 CI 挂了**： 【取值：`gh api repos/lxh113377/skill-private-archive/actions/runs?per_page=30` → 27 failure / 3 success；最新失败 run 40119157840 的 job 日志逐行只有一道门 FAIL = `gate_run_freshness`】 【r212 裁决=执行（R211-3 落地：runner 加 classify_reds + 第 91 门双向夹具 + CI 摘要分类行；rc 与地板判据一条未放宽）｜读数：夹具 9/9 含 m1 变异+ m1b 复原；单跑 gate_run_freshness 打印 REAL_RED=0 / DESIGN_INHERENT_RED=1 且整轮仍 [GATES:FAIL]（未消音）；CI 体内层 full/legacy/mixed 三侧 rc=0；r31 runner 契约夹具 31/31】
  该门语义 = 从 CI 反向盯「人还在不在本机完整跑门禁」（r32 立的反向用法），CI 环境无本机台账可读 ⇒ 设计内必红。**不放宽 SUCCESS_FLOOR、不为消红改判据**（X-9 反向 / R263）。
  修法：gates.yml 的结论步把 FAIL 门按 portable 属性分列具名分类（如 `DESIGN_INHERENT_RED=1 (gate_run_freshness)` 与 `REAL_RED=0`）；判据本身一字不动。
  验收（二元）：CI job 日志出现分类行且本地可复算（同一步骤读 --json 快照 per_gate + 门表 portable 字段）；地板与判据未改。
  归属：本仓自持（.github/workflows + 只读门表），不转办。
