# 07-next-steps.part45.md

<!-- 本卷为 07-next-steps.part44.md 的延续 -->

## 最近对话摘要（历史）

- [x] **【P1·待办 W-13（r43 新立）】** 账龄尺改用**标题锚点**定位待办（现按行号）： 【r49 裁决=执行完毕｜标题锚点定位已落地于 05-exec/r38_debt_aging.py:88 find_item_line() 与 05-exec/r46_mark_verdict.py:37 find_item_lines()，全链零行号索引（r44 提交 017595e）】

- [x] **【P0·下轮首推 W-11（r42 Phase 4 已写测试未落地）】** 账龄尺补两态两档：① `REPEAT`（同一条被改期 >=2 次 ⇒ 单列，禁无限滚延期）；② 宽限期按优先级分档 `GRACE_BY_PRIORITY = P0:2 / P1:4 / P2:8`（现统一 2 轮，P2 长期项被误判 OVERDUE 制造噪音）。失败测试已入库：`python 05-exec/r39_debt_ledger_fixtures.py` → t30/t32/t33/t34 红，落地即转绿。 【r44 裁决=执行完毕｜已落地 `find_item_line()`（只认未勾选项、多命中由调用方拒写），t40/t41/t42/t46 四例覆盖；D55 那类行号漂移不再有写入错位风险】

- [x] **【P1·待办 W-6（r40 新立）】** 待办的「归属声明」必须可机检：条目若含 归属方/转办/待某会话，须能解析到一个真实存在的文件路径，否则账龄尺把它记为 UNOWNED（防 D37 那类自家债外部化，配 X-14）。 【r46 裁决=挂账至 r49｜归属声明可机检（UNOWNED 态）需先给 07 全卷补 owner 字段，本轮产能给了 W-16 工具化；到期即按 REPEAT 强制升级】 【r48 裁决=执行完毕（限定）｜判据已落地：classify_owner() + 全文 owner 字段 + 台账 unowned_claims，夹具 t6-pre/t63/t64/t65/t66 五例；首轮用截断标题判致 2 条假 UNOWNED 已改全文（见 05-exec/r38_debt_aging.py）】

- [x] **【P0·下轮首推 W-18（r46 新立）】** 此后所有「补标/回写」类一次性脚本一律改走 `python 05-exec/r46_mark_verdict.py --key <锚点> --round <NN> --verdict <裁决｜原因>`，禁再出现行号索引写入；违反即视为 W-9 同族缺陷复发（工具已不接收行号，绕开即手工写，手工写无读回验证）。 【r49 裁决=执行完毕（持续生效）｜r47 12/12、r48 3/3、r49 5/5 全部经写入器落标（备份件在 05-exec/mark_backup），零手工行号写入】

- [x] **【P0·下轮首推 W-16（r45 新立，优先级最高）】** 任何写记忆标记的临时脚本都必须复用 `r38_debt_aging.find_item_line()`（标题锚点，命中数 != 1 即拒写并报告），禁用行号索引写入。实证据：H-3″ 项三轮标记后裁决标记数仍为 0（W-9 真因）。复现：`python 05-exec/r38_debt_aging.py --json /tmp/x.json` 看 overdue 明细。 【r49 裁决=执行完毕｜唯一入口 05-exec/r46_mark_verdict.py 已注册为常驻门（run_gates id=mark_verdict_fixtures），本轮 5 条裁决全部经它写入；r49 追加第⑥重对账与混合行尾错位根因修（夹具 t9/t10）】

- [x] **【P0·下轮首推 W-14（r44 新立，优先级最高）】** 给 REPEAT 立棘轮第 9 指标 repeat_debt_items。存在理由（D59）：本轮 OVERDUE 从 16 压到 1 里有 11 条是靠「降级为长期看守」实现的；若降级项没有独立指标，「降级」就成了新的免检通道，等于把债务换个格子。取值面 by_class.REPEAT，须与 overdue/deferred 同等 fail-closed。 【r46 裁决=挂账至 r49｜契约分代必填需先设计，本轮产能给了 W-16 工具化】 【r49 裁决=执行完毕（并纠正 r46 误挂）｜第 9 指标 repeat_debt_items 已于 r45 落地（提交 8d7fb56，取值面 05-exec/ratchet_gate.py 的 _debt_class_state）；r46 却在本条头部写了延期、原因文本讲的是 W-17 —— 本轮到期追讨抓到，已立 W-22 做写时对账】
