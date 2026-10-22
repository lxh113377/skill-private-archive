# 07-next-steps.part92.md

<!-- 本卷为 07-next-steps.part79.md 的延续 -->

## 逐段对应（供引用与回溯）

- [x] **R137-1（r137 登记，P0·已落地）** `05-exec/r137_commit_gate_map.py` 已入册为**第 49 门**（`commit_gate_map_face`）。判定口径：按暂存文件算出本次提交落在哪些纪律面门，`required_gate_ids` 即「必须过」的门清单；不在纪律面则 `in_scope_n=0` ⇒ 不阻断（保留 r130 的正当理由：不挡并行会话的活）。**空暂存清单判 UNVERIFIED 不记 0**（r133 第 ④ 种形态）。取值：`python 05-exec/r137_commit_gate_map.py --json 06-benchmark/commit_gate_map_r137_2026-10-21.json`。 【r140 裁决=挂账至 r142｜并行会话 R137 系合规续挂，R269 不代收口】 【r143 校正注：判定面已入册为第 49 门且历轮终态 PASS，本条闭环】

- [x] **R137-2（r137 登记，P0·已落地）** **pre-commit 已改为分级阻断**（`.git/hooks/pre-commit`，**不在 git 里 ⇒ 换机需重装**）：只跑本次变更触发的门、只阻断这些门的红；逃生阀 `SKIP_COMMIT_GATES=1 git commit ...`（须在提交说明里写明为何先落盘）；用 `--no-ledger` 试跑不污染门禁台账。**实测**：暂存 `05-exec/` 件 ⇒ 触发提案证据面 ⇒ 通过 ⇒ 放行；造无支撑提案 ⇒ 该门红 ⇒ 阻断。⚠️ 阻断会把「无关的历史红」误算到本次头上吗？不会 —— 只跑本次触发的门，不连带其他门。 【r140 裁决=挂账至 r142｜并行会话 R137 系合规续挂，R269 不代收口】 【r143 校正注：分级阻断 r139 两修后历轮提交均正常放行，本条闭环】

- [x] **R137-3（r137 登记，P1·已落地）** **AGENTS.md #35「纪律须有阻断点」**已立规，并附 5 条强制条目的阻断点现状表（#30→debt_aging / #31→提案证据面 / #32→提案证据面+门表闸 / #33→因果证据面 / #34→提案证据面+门表闸）。**判据**：立了纪律却没有阻断点 = 没立。取值：`Select-String -Path AGENTS.md -Pattern '^## '` 可见 `#35` 节。 【r140 裁决=挂账至 r142｜并行会话 R137 系合规续挂，R269 不代收口】 【r143 校正注：#35 已立且 r139/r140/r141/r142 连续延伸，本条闭环】

- [x] **R137-4（r137 登记，P2）** **hook 仍不在 git 里**（`.git/hooks/`），换机需重装 —— 但 r136 建的「hook 装好了吗」自查面尚未做（r130 的 hook 同样是装完就没再核过）。**建议**：给「hook 存在且含预期阻断逻辑」加一个常驻门（本仓每轮换机/重装都可能丢）。取值：`Get-ChildItem .git/hooks -File | Where-Object { $_.Name -notlike '*.sample' }`。 【r140 裁决=挂账至 r142｜并行会话 R137 系合规续挂，R269 不代收口】 【r143 校正注：hook 不可恢复已由 R138-2 治理（git 跟踪模板 + 一键恢复），本条闭环】

- [x] **R136-1（r136 登记，P0·已落地）** `05-exec/r136_proposal_evidence.py` 已入册为**第 48 门**（`proposal_evidence_face`）。**机器判据**：新增或修改转办提案后必须跑它，读 `face.unbacked_n` / `no_acceptance_n` / `no_evidence_n`，**三个都须为 0**。「无读数面支撑」的正确处置是**显式标注「未验证，仅为候选方向」**（该面把这种标注计为合规）。取值：`python 05-exec/r136_proposal_evidence.py --json 06-benchmark/proposal_evidence_r136_2026-10-21.json`。 【r140 裁决=挂账至 r142｜并行会话 R135/R136 系合规续挂，R269 不代收口】 【r143 校正注：提案证据面已入册为第 48 门且历轮终态 PASS，本条闭环】
