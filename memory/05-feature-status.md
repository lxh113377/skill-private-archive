# 05 - 功能状态

> 本文件记录功能/任务的完成状态。
> 归档类型：增量（已完成项归档时移入 archive/）

## ✅ 已完成

r44 裁决完整性落地轮（2026-09-25 第 44 轮） — 落地连续两轮点名的 W-12/W-13：find_item_line（标题锚点、只认未勾选项、多命中拒写）+ adjudication_gap/coverage_check（四条语义由夹具 t40–t46 锁死），夹具 39/39。判据首跑即报 INCOMPLETE（上轮 15 条一条没裁），据此真裁决 15 条（11 降级看守 + 2 执行完毕 + 1 延期 r47）并补勾 r40 已交付漏勾的 W-4 ⇒ OVERDUE 16→2→1、DECIDED 43、REPEAT 0。余 1 条真实未做 ⇒ 棘轮如实留红，未上调基线。过程自抓：先发现自写测试互相矛盾（t44/t45 vs t43）再定语义实现，未改断言凑过。立 X-18（判据不当场跑真实数据不得宣布有效）、W-14（REPEAT 第 9 指标）、W-15（完整性进契约）。

r43 反延期落地轮（2026-09-25 第 43 轮） — 把 r42 的 4 条红测试落地：第 6 态 REPEAT（同行改期 >=2 次显形，RE_DEFERRAL 计数 + REPEAT_AFTER=2）与按优先级分档宽限 P0:2/P1:4/P2:8（值入 GRACE_BY_PRIORITY 常量表），台账行新增 repeat 字段；夹具 32/32。首跑显形 6 条滚延期项、分档使 OVERDUE 20→15；按 X-16 逐条升级：11 条判「降级为长期看守」（终局但数值仍被棘轮看守）、4 条首次延期至 r46，复测 OVERDUE 15 / DECIDED 24 / DEFERRED 4 / REPEAT 2。**棘轮如实留红 +15，未上调基线**。新发现 D55 行号漂移（5 条写入时已非未勾选行，守卫跳过未强改）→ 立 W-13 标题锚点定位、W-12 裁决完整性。

r42 根因轮（2026-09-25 第 42 轮） — 查清 OVERDUE 反弹真因：轮号推进致 15 条如期到期（14 计入）+ 上轮漏裁 r38 自立项（账龄新越线 6 条），**非判据缺陷、非正文替换扰动**；据此定性流程缺陷并写失败测试 t30–t34（REPEAT 反延期 treadmill + 分档宽限）。实现未落地（补丁中途断言失败未写盘），如实挂红 28/32，立 W-11 为下轮 P0。

r41 结构归位与 last-wins 轮（2026-09-25 第 41 轮） — 纠正 r40 误诊（到期洪峰是机制正常，非判据缺陷，D41）；抓到 W-8 真根因：多裁决标记同行时 `search()` 取最早 ⇒ 新终局被旧挂账劫持，改 `finditer()[-1]`，夹具 t26/t27 双向锁死 → 27/27；H-5 结构债清掉：P0 节内 15 条轮次摘要整段归位，守恒三校验全过（行数守恒、残留摘要 0、60 条待办未删）；再裁 9 条到期债（3 作废 + 6 挂账至 r44 各带取值），账面 OVERDUE 10→1 / DECIDED 12→15 / DEFERRED 25→22。如实留红：[RATCHET:FAIL] overdue=1，不使用归因通道掩盖，立 W-9 与 X-15。

r40 还债轮（2026-09-25 第 40 轮） — 不开新维度、专修判据放水：W-4 第 8 指标 deferred_debt_items（共用单源读取器、同等 fail-closed，24/24）、到期追讨首次真响 3 条、L-4 归属反转（扫描器原在本仓；契约新增 conflict_no_dead_inputs + 死条目改指真实在役件 + 第 10 道门 5/5）、M-1 判为历史不可测（git 不记脏树）改前瞻影子计数。自错三处留证并加代际豁免。立 X-14。如实留红：RATCHET overdue+1/deferred+2，W-8 列下轮 P0。

- **r21c 还账轮（2026-09-24 第 21 轮 c 段）** — 本仓欠焚诀 C25/C31 的注入超顶已清偿：`A-memory-start/SKILL.md` 29,041→26,593B（长条目换一行摘要，全文归分卷），其余量 220→1,583B；实测 owner 已自落 C31 归因台账 ⇒ 我「注入区合一」建议作废。受管根 `928517a`/V10.70.0。全文见 `05-feature-status.part19.md`。
- **r20b 棘轮落地轮（第 21 轮 b 段）** — A-get-memory 三条硬判据落地（受管根 `b8966da` V4.30.0，四门禁首次全绿）+ 本仓注入面棘轮 `ratchet_gate.py`（21/21 夹具，两级判定）挂进项目门禁命令。全文见 `05-feature-status.part18.md`。
- **r20 机制化轮（第 21 轮）** — rule_editor 写前脏源检测落地（受管根 `9a15f4e` V10.69.0，桩 10/10）+ 09 状态机首次真用 + comparison 常驻页。全文见 `05-feature-status.part17.md`。
- **r19b 标注驱动续做轮（第 20 轮 b 段）** — 契约族 + 变异对照 + 注入面端数 6 句改口八端（V10.68.0）。全文见 `05-feature-status.part15.md`。
- **r19 对标实物层增量轮（第 20 轮）** — 实物层校准 + 55 例夹具 + claim 对账新工具 + 分母三口径 + 上游 flow 图例缺陷修（V3.52.2）。全文见 `05-feature-status.part16.md`。
- **r18 全量对标增量轮（2026-09-24，第 19 轮）** — 对象 7→14 + 差距 N1~N8 + 4 只读工具落地；全文见 `05-feature-status.part14.md`（本轮条目级归档迁出，正文零改写）。⚠️ **r19 校正注**：该轮四工具当时**零夹具**、drift 扫描含 37.5% 噪声，已由 r19 修正。

## 分卷目录
- **卷1** `05-feature-status.part1.md` — 进行中 / 计划中 / 阻塞
- **卷2** `05-feature-status.part2.md` — 已完成：2026-09-19 第 3 轮（P0-2 收口 + 补建上游 + 注册表重建）
- **卷3** `05-feature-status.part3.md` — 已完成：2026-09-22 第 4 轮（D1–D5 授权项执行结果）
- **卷4** `05-feature-status.part4.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷5** `05-feature-status.part5.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷6** `05-feature-status.part6.md` — 已完成：2026-09-22 第 10 轮（Step 0 首次实跑 + 记忆层回写 + 阶段1 补齐 + B1–B7 授权执行）
- **卷7** `05-feature-status.part7.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷8** `05-feature-status.part8.md` — 已完成：2026-09-23 第 13 轮（性能瓶颈三维实测分析）
- **卷9** `05-feature-status.part9.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷10** `05-feature-status.part10.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷11** `05-feature-status.part11.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷12** `05-feature-status.part12.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷13** `05-feature-status.part13.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷14** `05-feature-status.part14.md` — 已完成：2026-09-24 第 19 轮 r18 全文（条目级归档迁出，防主壳超 4KB）
- **卷15** `05-feature-status.part15.md` — 已完成：2026-09-24 r19b 全文（契约族+变异对照+端数改口）
- **卷16** `05-feature-status.part16.md` — 已完成：2026-09-24 第 20 轮 r19 全文（自 part15 就地续拆）
- **卷17** `05-feature-status.part17.md` — 已完成：2026-09-24 第 21 轮 r20 全文
- **卷18** `05-feature-status.part18.md` — 已完成：2026-09-24 第 21 轮 r20b 全文
- **卷19** `05-feature-status.part19.md` — 已完成：2026-09-24 第 21 轮 r21c 全文
- **卷20** `05-feature-status.part20.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷21** `05-feature-status.part21.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷22** `05-feature-status.part22.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷23** `05-feature-status.part23.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷24** `05-feature-status.part24.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷25** `05-feature-status.part25.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷26** `05-feature-status.part26.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷27** `05-feature-status.part27.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷28** `05-feature-status.part28.md` — 05-feature-status 分卷（R199 自动拆卷）

