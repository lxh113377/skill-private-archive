# 07-next-steps.part48.md

<!-- 本卷为 07-next-steps.part47.md 的延续 -->

## 最近对话摘要（历史）

- [x] **【P0·下轮首推 W-28（r50 新立）】** 把「枚举源双路对账」做成机器判据：凡取证件引用外部/对手数字，必须带 `retrieval` 字段（≥2 条独立取值命令）+ 差额归因，缺一即由 `05-exec/baseline_contract_scan.py` 判红。存在理由（r50 实测）：r31/r32 的 workflow 计数取自 `/actions/workflows` 总计面，混入平台 `dynamic/*` ⇒ superpowers/anthropics 实为**仓库内 0 个 CI**，"82%/75% failure"是平台件而非测试；另 `steps=0` 的 failure 属 runner 配额而非测试失败。做法：先写夹具反例（无 retrieval 的取证件必须判红）看红，再加不变式。 【r51 裁决=执行完毕｜不变式 inv_opponent_claims_have_retrieval 已进 baseline_contract_scan 并注册到 debt_aging_r*.json 与新 pattern opponents_*_r*.json；按结构识别带 repo 的条目（不锁键名，防换 opponents/repos 绕过）；实跑接线另抓出 arg 传名字串会导致全量历史件被字典序豁免，已加 r11/r12 真接线反例】

- [x] **【P1·待办 W-29（r50 新立）】** 复核其余历史对手数字是否同建立在错面：r38 的 open issues（287/1290/401/118/25）与最老 open 日期取自哪一路 API、是否含 PR 与已关闭项、有无 search-api 分页截断。取值须与 `search/issues` 的 `total_count` 交叉对账后方得引用。 【r51 裁决=执行完毕｜实测复核：r38 引用的 open issues 287/401/1290/118/25 取自 REST open_issues_count（含 PR），search 纯 issue 面 = 134/143/368/58/17 ⇒ 虚高 1.5-3.5 倍；最老 open 日期 5/5 逐条复现 ⇒ 错的是计数列不是整份件。证据与逐条取值命令见 06-benchmark/opponents_open_backlog_r51_2026-09-25.json】

- [x] **【P0·下轮首推 W-30（r51 新立）】** 把「外部数字须带独立第二路取值」从 JSON 证据件推广到**非 JSON 引用面**：`06-benchmark/*.md` 报告与 `comparison.md` 里的数字目前只靠人工带命令。做法 = 先跑只读统计（数字紧邻 60 字内无可复算命令者计数）量出误报率，再决定是否进阻断链（r25 用户否决拦任务的闸门 ⇒ 未量出低误报前只报告不阻断）。取值起点：`python 05-exec/baseline_contract_scan.py` 已管住 json 面，md 面另写 `r52_md_claim_face_scan.py`。 【r52 裁决=执行完毕｜新工具 05-exec/r52_md_claim_face_scan.py 已落地并注册为第 15 道门（md_claim_face，走 r52_mdclaim_fixtures 20 例）。窗口 ±12 行与单位集按抽样 14 条判读确定；全量敞口 60.4%→17.8%，可整改面 184 声明 / 0 敞口（历史面 755 处按 R241 只登记不回改）】

- [x] **【P1·待办 W-31（r51 新立）】** 契约 pattern 自身的陈旧面检查：r51 实测 `debt_aging_r3*.json` 让 r40 起的全部证据件落在受检面外（零命中判红抓不到，因为它仍命中十份旧件）。做法 = 在 `validate_contracts` 里对每个 pattern 计算「命中集内最大轮号」与当前轮号之差，超阈值即打印陈旧告警（先打印不阻断，量一轮误报再接线）。 【r52 裁决=执行完毕｜face_pattern_staleness 已进 baseline_contract_scan 且首跑抓到 3 个陈旧面（skill_structure_rubric 最新 r29 落后 22 轮等）；三态反例 t29–t32 入 r19 夹具；按 r25 否决只报告不判红，陈旧后果另立 W-33 清根因】
