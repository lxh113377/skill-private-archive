# 07-next-steps.part96.md

<!-- 本卷为 07-next-steps.part79.md 的延续 -->

## 逐段对应（供引用与回溯）

- [x] **R144-1（r144 登记，P0·已落地）** **git 跟踪的外部锚点台账已落地**：`06-benchmark/hook_install_ledger.json`（schema `hook-install-ledger-r144-v1`），`r138_install_hooks.py` 安装时同步写每个 hook 的 `lines` / `last_line_hash` / `invoker` / `reason`。台账在版本历史里，改它 = 留 git 痕迹。取值：`Get-Content 06-benchmark/hook_install_ledger.json -Raw`。 【r148 校正注：台账件已入库（git ls-files 可查）且 H7 历轮 PASS，本条闭环】

- [x] **R144-2（r144 登记，P0·已落地）** **第 54 门 H7（外部锚点对账）已生效**：台账须有该 hook 条目 / `lines` 与日志行数一致 / `last_line_hash` 与实际末行一致。**同一套伪造攻击前后对比**：r143（无 H7）rc=0 放行 → r144 **rc=1 被 H7 抓住**。取值：`python 05-exec/r142_install_history.py --json <件>` 的 `rows[].h7_anchor_match` / `h7_note`；伪造复现 `python ./_temp/v26_fullforge.py` + `python ./_temp/v26_probe.py`。 【r148 校正注：H7 外部锚点对账第 54 门历轮 PASS，本条闭环】

- [x] **R144-3（r144 登记，P1·已落地）** **AGENTS.md #42「防篡改须有外部锚点」**已立规，含量化坐实 + 前后对比表 + **信任根边界诚实声明**（H7 信任根 = git 历史；改写 git 历史属另一威胁模型）。取值：`Select-String -Path AGENTS.md -Pattern '^## '`。 【r148 校正注：#42 已立且为 #44/#45 前置，本条闭环】

- [x] **R144-4（r144 登记，P2）** **残留：台账与安装的原子性**。装了 hook 但台账还没提交的窗口期，H7 是绿的（台账同步写了）；真正的窗口是「装了但 `git add` 台账前就跑门」——此时台账是旧的 ⇒ H7 误红。**当前缓解**：安装后立刻提交（流程约定）。**建议**：H7 对「台账落后但落后量 = 1 次安装且工作区有未提交台账改动」给宽限态（WARNING 不判红），或安装脚本直接 `git add` 台账（需要协调并行会话，暂不做）。 【r149 校正注：台账/日志原子性窗口已由 r145 三条件宽限 + r146 pending + r147 写序重排三层治理，本条闭环】

- [x] **R143-1（r143 登记，P0·已落地）** **安装历史已加哈希链**：`r138_install_hooks.py` 每行写 `prev_hash`（上一行 `line_hash`，首行 GENESIS）+ `line_hash`（除自身外全部字段的规范化 JSON sha256，keys 排序）。**载荷约定**：`seq` 先定 ⇒ `prev_hash` 再定 ⇒ `line_hash` 最后算（载荷 = 除 line_hash 外全部字段，含 seq）。篡改/重排/删链任意行 ⇒ 链断。取值：`python ./_temp/v24_dbg.py`（逐行验 rehash_ok）。 【r147 校正注：哈希链第 54 门历轮终态 PASS，本轮 r147 重排后写序仍全绿，本条闭环】

- [x] **R143-2（r143 登记，P0·已落地）** **第 54 门 H6 防篡改断言已并入并三态验证**：链从首条带链行起完整连续 + **末行必须带链（无条件）**。三态：篡改第 1 行 ⇒ `L0 line_hash 复算不符`；自洽伪造（删光链字段洗成 legacy）⇒ `全部 N 行为 legacy 无链——历史可被整体伪造`（初版该分支不判红，被伪造绕过，已收紧）；真实状态 0 项。取值：`python 05-exec/r142_install_history.py --json <件>` 的 `rows[].h6_chain_intact` / `chain_note`。 【r147 校正注：H6 断言历轮三态验证 + 本轮门 55 旧序反向案再证有牙，本条闭环】

- [x] **R143-3（r143 登记，P1·已落地）** **AGENTS.md #41「历史须防篡改」**已立规，含量化坐实 + 三抓记录（载荷不一致 / 坐标系不一致 / 假绿分支）+ 三态反向验证表。取值：`Select-String -Path AGENTS.md -Pattern '^## '`。 【r148 校正注：#41 已立且第 54 门 H6 历轮终态 PASS（含 r147 写序穷举复核仍绿），本条闭环】
