## r113 摘要 (四) · 收尾补记

⑭ **第三形态自抓：裁决文本自带前缀致解析失效** —— 给 r108 两条 OVERDUE 写终局裁决时，`r46_mark_verdict.py` 的 `--verdict` 我自带「（r113 裁决=」前缀 ⇒ 落成 `【r113 裁决=（r113 裁决=降级…】`；`parse_last_verdict` 只认最后一个标记的**头部**（第一个 ｜/】 之前，X-23），该头部以「（r113」开头、不以裁决词开头 ⇒ 判未裁 ⇒ 两条继续 OVERDUE。处置 = 按 canonical 形态重写（禁改判据凑绿）⇒ 复算 **OVERDUE 3→0 / DECIDED 44→46**。同族前身 = r112 §7-5「新条目正文含旧轮号字面量被裸 rNN 定年劫持」；共性与教训 = **「我写了裁决」≠「判据读到裁决」，只能靠读回复算发现**。取值：`python 05-exec/r38_debt_aging.py --json <件>`。

⑮ **收尾时的门禁终态（单一根因链，如实登记）** —— 最后一跑 `[GATES:FAIL] FAIL=5`（`ratchet_gate` / `refresh_budget_fixtures` / `budget_contract_fixtures` / `baseline_note_fixtures` / `gate_run_freshness`）：根因链 = 外部会话 11:37:11 改 `D:/global_skills/A-memory-start/references/contract.md`（19,107→19,204B，`git status` 实测仍 ` M` 在途）⇒ 注入面 66,762B 破棘轮基线 66,665B ⇒ `--update` 按设计 REFUSE ⇒ 三道依赖 `--update` 的夹具红 ⇒ 元门读上一行台账红。**红因是真缺陷（外部在途），非本仓判据坏**；另 `refresh_budget_fixtures` 的连带项与 `gate_run_freshness` 的延迟自愈将随外部件收口自动复原。登记 P0 **R113-4**（已由 flow 建行）。
   > 取值：`python 05-exec/run_gates.py --json 06-benchmark/gate_run_r113l_2026-10-18.json`（`verdict_reason=FAIL=5`）；外部件取证 `git -C D:/global_skills status --porcelain` + `Get-Item D:/global_skills/A-memory-start/references/contract.md | Select Length,LastWriteTime`

⑯ **本轮最终交付清单（需求 1–7 对应）**：①需求1 = 存量盘点（182 件四档身份 + 39 件同源可判 + 12 件裁决）；②需求2 = 132 仓检索面 + 8 族逐族结论（6 保留 / 2 已升级），3–5 候选 8/8 族达标；③需求3 = 五维锚定评分矩阵（本地基线 + 15 仓 + 20 扩面仓）；④需求4 = `04-plan/迁移替换方案_r113_2026-10-18.md`；⑤需求5 = `05-exec/r113_quarterly_audit.py` + `04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md` + 首份 `06-benchmark/quarterly/2026Q4/`；⑥需求6 = M1 30.2%→69.2%（+39.0pp）+ N1–N4 反指标；⑦需求7 = 本报告 + 上述四件，全部在册且已提交。

## 逐段对应（供引用与回溯）

| 段 | 覆盖标识 |
|---|---|
| (一) | ① 开工面 / ② 受管根复验 / ③ 身份面 / ④ 裁决面 / ⑤ 自抓三处陈旧 |
| (二) | ⑥ 升级复算 / ⑦ 需求 2/3 检索与矩阵 / ⑧ 需求 4 迁移方案 / ⑨ 需求 5 季度巡检 / ⑩ 需求 6 度量 |
| (三) | ⑪ 门禁（含 FAIL=2 如实登记）/ ⑫ 负面教训 / ⑬ 新建待办 |
