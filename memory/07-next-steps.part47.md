# 07-next-steps.part47.md

<!-- 本卷为 07-next-steps.part46.md 的延续 -->

## 最近对话摘要（历史）

- [x] **【P0·本轮落地 W-23（r49 新立）】** 写入器按**物理行保留行尾**（混合行尾卷不得并元素后追加到元素末尾），读回验证从「文件里有这个串」升级为「锚点与标记同一物理行」。 【r49 裁决=执行完毕｜split_keep_eol/join_keep_eol 逐行保留行尾，读回改为同行断言；混合行尾反例夹具 r46_mark_verdict_fixtures t9/t10 由红转绿（修前实测把标记写到「待办 戊」行）】

- [x] **【P0·本轮落地 W-24（r49 新立）】** 分类器只认**最后一个标记的头部**（第一个 ｜/】 之前）：原因体里引用的旧标记原文不得改变判定，也不得计入延期次数（防 REPEAT 第 9 指标虚增）。 【r49 裁决=执行完毕｜parse_last_verdict 只取最后一个标记的头部，count_deferrals 同口径；负控 q1-q5 五例锁死（引用旧标记不改判定、真延期仍 DEFERRED/到期仍 OVERDUE）】

- [x] **【P0·下轮首推 W-25（r49 新立）】** 把输入面自证推广到其余判据：05-exec/ratchet_gate.py、05-exec/baseline_contract_scan.py、05-exec/rule_conflict_scan.py 各自的 glob/取值窗口未自证；并评估把 face_status 写进 06-benchmark/debt_runs.jsonl 成为趋势列（先进台账观察，不进棘轮）。 【r50 裁决=执行完毕｜三面已推：05-exec/rule_conflict_scan.py 的 discover_authority_candidates/effective_files（扫描面 10→26 件，极性规则 116→188、互斥候选 6→21）+ 05-exec/ratchet_gate.py 的 face_counted_vs_observed；baseline_contract_scan 的 pattern 零命中判红 r33 既有，本轮只补防回退断言；face_status 已于 r49 进台账】

- [x] **【P1·待办 W-26（r49 新立）】** memory/07-next-steps.md 实测为**混合行尾**（178 个 CRLF + 4 个纯 LF）—— 根因在写入侧（并发工具按 text 模式写）。统一行尾前须先定位那 4 行由谁写；属 R241 敏感区，禁为让门变绿而整卷重写。 【r50 裁决=执行完毕（限定）｜根因已用证据定死而非推测：git show r43..r49:memory/07-next-steps.md 实测仓库内**全 190 行纯 LF**，而工作树 187 CRLF + 4 纯 LF ⇒ 混合行尾来自写卷脚本未传 newline=空串（Windows text 模式把 \n 转成 \r\n），不是并行会话乱写；判据侧已由 W-23 逐行保留行尾免疫，写入侧约定立为 X-25，不改写既有卷（R241）】

- [x] **【P0·下轮首推 W-28（r50 新立）】** 把「枚举源双路对账」做成机器判据：凡取证件引用外部/对手数字，必须带 `retrieval` 字段（≥2 条独立取值命令）+ 差额归因，缺一即由 `05-exec/baseline_contract_scan.py` 判红。存在理由（r50 实测）：r31/r32 的 workflow 计数取自 `/actions/workflows` 总计面，混入平台 `dynamic/*` ⇒ superpowers/anthropics 实为**仓库内 0 个 CI**，"82%/75% failure"是平台件而非测试；另 `steps=0` 的 failure 属 runner 配额而非测试失败。做法：先写夹具反例（无 retrieval 的取证件必须判红）看红，再加不变式。 【r51 裁决=执行完毕｜不变式 inv_opponent_claims_have_retrieval 已进 baseline_contract_scan 并注册到 debt_aging_r*.json 与新 pattern opponents_*_r*.json；按结构识别带 repo 的条目（不锁键名，防换 opponents/repos 绕过）；实跑接线另抓出 arg 传名字串会导致全量历史件被字典序豁免，已加 r11/r12 真接线反例】
