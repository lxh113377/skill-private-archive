# 07-next-steps.part140.md

<!-- 本卷为 07-next-steps.part99.md 的段落边界拆分（R241：原文字句零改写；超长行按句号边界切分，逐字节拼接等于原文） -->

- [x] **R147-3（r147 登记，P1·已落地）** **AGENTS.md #45「证据写入顺序：真相源先行」**已立规，含崩溃前缀穷举表 + 不变式 + 教训（登记残留别停在「下次自愈」，穷举超前/滞后两侧——滞后可宽限、超前是死窗）。**R146-4 已由本顺序治理（闭环）**。取值：`Select-String -Path AGENTS.md -Pattern '^## '`。 【r151 裁决=销账｜#45 在 AGENTS.md 在册且为 #46/#47/#48 前置（取值 Select-String -Path AGENTS.md -Pattern '^## '），本条为闭环确认】

- [x] **R147-4（r147 登记，P2）** **残留：崩溃落在「日志已写、pending 未写」+ 跨会话跑门 ⇒ 仍误红**（穷举 crash-after-1 读数 via=env：同会话靠 env-session 通道救；若换会话 B 跑门，env 不匹配且 pending 滞后 ⇒ 判红）。**性质已降级**：非永久——下次任意一次安装重写 pending 即自愈，且触发需「崩溃恰在两步之间 + 换会话跑门」双条件。**建议**：pending 改为记「日志末行 line_hash 的推导值」而非独立快照（或先算全内容再连写），代价是与日志结构耦合加深，按 07 优先级排。取值：`python 05-exec/r147_write_order_sweep.py --json <件>` 的 `face.new_prefixes[1].via`。 【r151 裁决=降级（转长期看守）｜本轮第 55 门读数显示死窗（missing<0）=0；本条触发需「崩溃恰在两步之间 + 换会话跑门」双条件且下次任意安装重写 pending 即自愈（非永久）。按 X-17 不再滚新到期日，数值由第 55 门看守】

- [x] **R146-1（r146 登记，P0·已落地）** **安装即写 git 内 pending 凭证件**：`r138_install_hooks.py` 每次安装同步写 `06-benchmark/hook_install_pending.json`（schema `hook-install-pending-r146-v1`），记录每个 hook 的「已装未提交」行 `line_hash` + `lines` + `invoker` + `reason`。取值：`Get-Content 06-benchmark/hook_install_pending.json -Raw`。 【r150 裁决=执行（终局）：该件所述机件已在盘并经门在册（第 54 门 install_history_face PASS），本期销账】 【r151 裁决=销账｜已落地且本轮复验：06-benchmark/hook_install_pending.json 在盘（schema hook-install-pending-r146-v1），第 54 门 H7 含 pending 通道历轮 PASS】

- [x] **R146-2（r146 登记，P0·已落地）** **H7 pending 通道（第四宽限路径）**：`r142_install_history.py` 在三条件 env-session 宽限失效时走 pending 凭证判别（pending.line_hash==实际末行 且 pending.lines==实际行数 且 台账 lines==实际-1 且 台账 last_line_hash==倒数第二行）。**四态反向验证全对**：跨人+有效凭证宽限 rc=0 / 跨人+过期凭证判红 / 真截断（missing<0）判红 / 真实状态 h7=True。取值：`python ./_temp/v30_verify2.py`。 【r150 裁决=执行（终局）：H7 pending 通道已在 r142_install_history.py 内实现且第 54 门 PASS，本期销账】 【r151 裁决=销账｜已落地且本轮复验：install_history_face PASS（四态反向验证含跨人+有效凭证宽限 / 过期凭证判红 / 真截断判红）】

- [x] **R146-3（r146 登记，P1·已落地）** **AGENTS.md #44「跨会话宽限须留安装凭证」**已立规，含四态表 + 信任强度声明（伪造 pending 与伪造台账同强度，都需改 git 跟踪件、都留 git 提交痕迹）。R145-4 已由本通道治理（闭环）。取值：`Select-String -Path AGENTS.md -Pattern '^## '`。 【r150 裁决=执行（终局）：AGENTS.md #44 已立规并留痕，本期销账】 【r151 裁决=销账｜#44 已在 AGENTS.md 立规（含四态表 + 信任强度声明），且为 #45/#46/#47 前置；取值 Select-String AGENTS.md】

