# 07-next-steps.part95.md

<!-- 本卷为 07-next-steps.part79.md 的延续 -->

## 逐段对应（供引用与回溯）

- [x] **R143-4（r143 登记，P2）** **残留：尾部截断仍难防**——攻击者把历史删到只剩首行（带链）即可通过 H6（末行=首行，链完整）。单机判据的边界：无外部参照就无法区分「真的只装过一次」与「删到只剩一次」。**建议**：把 `.installed.log` 的**快照**（或行数+末行 line_hash）同步进一个 **git 跟踪的台账件**（如 `06-benchmark/hook_install_ledger.json`），门里对账 git 内台账 vs git 外日志——不一致即篡改。代价：并行会话同时装 hook 时台账合并需排队（用 git 提交串行化天然解决）。 【r149 校正注：尾部截断已由 r144 H7 外部锚点 + r146 pending 凭证治理（单机边界声明保留在 #47 适用面），本条闭环】

- [x] **R142-1（r142 登记，P0·已落地）** `05-exec/r142_install_history.py` 已入册为**第 54 门**（`install_history_face`）。五项断言：H1 历史存在非空 / H2 每行 `seq`+`installed_at`+`invoker`+`reason` 四要素齐 / H3 seq 严格单调增 / H4 末行与快照一致 / H5 至少 2 条（证明追加真的在发生）。反向验证四态：删历史 5 项全红 / 只剩 1 条 H5 精准 / seq 乱序 H3+H4 / 坏 JSON 行 H2+H4。取值：`python 05-exec/r142_install_history.py --json <件>`。 【r143 校正注：第 54 门 install_history_face 本轮含 H6 全 PASS，本条闭环】

- [x] **R142-2（r142 登记，P0·已落地）** **安装历史已追加式**：`r138_install_hooks.py` 每次安装写两处 —— `.installed` 快照（schema 不变，兼容第 52/53 门）+ `.installed.log` 追加 JSONL（`seq` 单调序号，永不覆盖）。实测装 2 次 ⇒ log 2 行，两次 reason 都可回溯（r141 量化坐实过快照模式下第 1 次的记录彻底丢失）。 【r143 校正注：追加式历史 + r143 哈希链持续扩展，本条闭环】

- [x] **R142-3（r142 登记，P1·已落地）** **AGENTS.md #40「归因须可回溯」**已立规，含量化坐实 + 五项断言 + 四态反向验证表 + 归因链五层全景。取值：`Select-String -Path AGENTS.md -Pattern '^## '`。 【r143 校正注：#40 已立，本条闭环】

- [x] **R142-4（r142 登记，P2）** **残留：历史无防篡改**。`.installed.log` 是普通文本，可被改写/重排（H3 能发现乱序，但发现不了「整体重写成一份假历史」—— 改写者可以连 seq 一起重排并保持单调）。**建议**：每行加前一行内容的哈希链（`prev_hash`），篡改任意一行会导致后续行哈希不连；代价是删除末行后重算成本极低（尾部篡改仍难防），完整方案需外部锚点（如把日志快照进 git 跟踪的台账）。 【r143 校正注：防篡改已由 r143 哈希链 + H6 治理，本条闭环】

- [x] **R141-1（r141 登记，P0·已落地）** `05-exec/r141_hook_attribution.py` 已入册为**第 53 门**（`hook_attribution_face`）。四项断言：A1 印记存在 / A2 有 `git_user` / A3 有 `session`（**多会话归因的关键**）/ A4 有 `reason`。任一不通判红。反向验证：旧印记 ⇒ `a2`/`a3`/`a4` 精准 FAIL；无印记 ⇒ 四项全 FAIL；真实状态 0 项。取值：`python 05-exec/r141_hook_attribution.py --json <件>`。 【r143 校正注：第 53 门 hook_attribution_face 历轮终态 PASS，本条闭环】

- [x] **R141-2（r141 登记，P0·已落地）** **印记已含 invoker + reason**：`r138_install_hooks.py` 安装时写 `invoker`（`git_user` / `git_email` / `session` / `pid`）与 `reason`（`HOOK_INSTALL_REASON`，缺省「(未说明)」）。**原则**：全部自动取，取不到留空并显式说明，禁猜、禁硬编码。`r140_hook_trace.py` 已同步读出（`invoker=lxh113377@3753318894 reason=...`），旧印记无该字段时显式说明而非崩溃。 【r143 校正注：invoker+reason 已实测写入历轮印记，本条闭环】
