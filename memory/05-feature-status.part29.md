# 05-feature-status.part29.md

<!-- 本卷为 05-feature-status.part28.md 的延续 -->

- **第 18 维「能力覆盖名册差集」落地**：两把尺（`05-exec/r60_capability_roster.py` slug 名面 / `r60_capability_roster_describe.py` 描述面）+ 契约入册两 pattern + 不变式 `roster_partition_sum` + 常驻门 `roster_partition_fixtures`（6/6）。

- **R59-4 退役真执行**：`executing-plans` + `slides` 先入库（受管根 `12916b7` / `af4be90`）再备份验证后移出扫描树；`r59_retired_face` 由自证升级为活体面，实测 `retired_still_on_disk=0`。

- **reactive 修正**：R59-5 与 R59-6 的 docx 半边经实测前提失效（均已就位）⇒ 销账；仅 xlsx 半边转 R60-3。

- 【r105 已完成｜2026-10-04】同一指令第五次逐字重发⇒完整重执行。**本轮成果全部落在"修我方自己的尺"上**：① F-1 账龄三态陈旧输入面根因修（件比所测卷旧 226s 仍照收⇒把已还的债报成新长的债 25 vs 活体 1，一域染红 5 门）；新增相对新鲜前置 + F-1b 修「读取面自证此前只在 PASS 分支打印」；常驻门 `debt_face_freshness`（9 腿含 2 变异）。② F-7 建议面命名空间洞补全：原式 `[WXMH]-\d{1,2}` 不含 r58 起 `R<轮号>-<序号>`、也不含其 docstring 自称覆盖的 `L-nn` ⇒ 这两族新立编号**静默逃逸**「报告新建议必须落待办卷」检查（正是用户这条指令的机器承接面）；修后当场判出本轮 12 条里 7 条未承接，补齐方转 OK 12/12（6 腿含变异）。③ F-5 `retired_face` 第八次回流：按**写入方证据**分两堆（git 零跟踪 ∧ mtime 成批差 ≤2s 同时成立才转具名看守；任一不成立照旧阻断，窗口不给分钟级），7 腿双向夹具含 2 条必须仍红的反例；终局消红仍待裁定，未闭环如实保留。④ F-2 夹具 h2 不再断言「项目当下无债」；F-3 r104 遗留 t15 改成现行裁定刻痕（不代用户裁 W-39②）；F-4 R76-4 终局裁决、W-48 降级看守 ⇒ 债务三态实测归 0。⑤ **F-6/F-7 换装判定自证伪**：`r105_swap_gate.py` 内置标定控制判出 G4 近邻尺无鉴别力（`copywriting↔xlsx` 重合 10；改 IDF 后应拒最高 28.543 > 应通过最低 15.447 区间仍重叠），根因=描述面语言不对称（本地 125/179 条含中文=69.8%）⇒ 10 件候选全 UNVERIFIED，**换装 0 件 / 卸载 0 件**，并明写 UNVERIFIED 不计入「已核对无缺口」；历轮 r60/r99/r100/r101/r103 换装结论同源降级待重测。⑥ F-6 `inject_union_bytes` +743 不动基线（磁盘字节 vs blob 字节两口径，R59-8「逐字节相等」不满足）。⑦ 体量一手：5 条 P1 落 07 主壳使 143,340→146,991 B（超 shell_max 40,960）⇒ `r105_move_todo.py` 迁独占卷并**逐字节回退主壳**，守恒断言通过；同轮 `volume_alloc` 报「该族 56 份 > 阈 30，名册许可未登记 ⇒ 只报禁自动动盘」。取值：`python 05-exec/run_gates.py`｜`python 05-exec/r105_debt_face_freshness_fixtures.py`｜`python 05-exec/r49_face_fixtures.py`（38 腿）｜`python 05-exec/r59_retired_face.py --selftest-reflow`｜`python 05-exec/r105_swap_gate.py`｜`python 05-exec/r38_debt_aging.py --report 06-benchmark/全量对标报告_r105_换装尺自我证伪与陈旧输入面返工_2026-10-04.md`
