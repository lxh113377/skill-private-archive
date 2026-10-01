# 07-next-steps.part45.md

<!-- 本卷为 07-next-steps.part44.md 的延续 -->

## 最近对话摘要（历史）

- [x] **【P1·待办 W-13（r43 新立）】** 账龄尺改用**标题锚点**定位待办（现按行号）： 【r49 裁决=执行完毕｜标题锚点定位已落地于 05-exec/r38_debt_aging.py:88 find_item_line() 与 05-exec/r46_mark_verdict.py:37 find_item_lines()，全链零行号索引（r44 提交 017595e）】

- [x] **【P0·下轮首推 W-11（r42 Phase 4 已写测试未落地）】** 账龄尺补两态两档：① `REPEAT`（同一条被改期 >=2 次 ⇒ 单列，禁无限滚延期）；② 宽限期按优先级分档 `GRACE_BY_PRIORITY = P0:2 / P1:4 / P2:8`（现统一 2 轮，P2 长期项被误判 OVERDUE 制造噪音）。失败测试已入库：`python 05-exec/r39_debt_ledger_fixtures.py` → t30/t32/t33/t34 红，落地即转绿。 【r44 裁决=执行完毕｜已落地 `find_item_line()`（只认未勾选项、多命中由调用方拒写），t40/t41/t42/t46 四例覆盖；D55 那类行号漂移不再有写入错位风险】

- [x] **【P1·待办 W-6（r40 新立）】** 待办的「归属声明」必须可机检：条目若含 归属方/转办/待某会话，须能解析到一个真实存在的文件路径，否则账龄尺把它记为 UNOWNED（防 D37 那类自家债外部化，配 X-14）。 【r46 裁决=挂账至 r49｜归属声明可机检（UNOWNED 态）需先给 07 全卷补 owner 字段，本轮产能给了 W-16 工具化；到期即按 REPEAT 强制升级】 【r48 裁决=执行完毕（限定）｜判据已落地：classify_owner() + 全文 owner 字段 + 台账 unowned_claims，夹具 t6-pre/t63/t64/t65/t66 五例；首轮用截断标题判致 2 条假 UNOWNED 已改全文（见 05-exec/r38_debt_aging.py）】
