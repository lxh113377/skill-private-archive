# 07-next-steps.part145.md

<!-- 本卷为 07-next-steps.part99.md 的段落边界拆分（R241：原文字句零改写；超长行按句号边界切分，逐字节拼接等于原文） -->

- [x] R128-2（r128 登记，P1）** 对账器需要在**新判据首次落盘时**就跑（而不是等下一轮普查），否则假红会像 r126 那样先流到报告与转办提案里。落点：`A-project-better` 的「新判据」流程加一步「与生产实测对账」。 【r131 裁决=销账｜r131 复核：已**实质完成** —— r129 立了第 41 门 `r129_reconcile_admission.py`（新判据入库准入门），把「新判据首次落盘就要对账」从建议变成了判红；r130 立了第 42 门 `r130_gate_table_reconcile.py`（门表变更对账闸）+ pre-commit 留痕 hook。r131 首跑时第 41 门确实把本轮两个新工具判成 UNDECLARED（机制按设计工作），并顺带暴露「有牙齿但没钥匙」⇒ 补了 --register。销账】

- [x] R128-3（r128 登记，P1）** `route_miss_attr_r117`（20 条里 5 条假红）已被 r119 取代但产物仍在 `06-benchmark/`，会被误取为最新证据。取值：产物按 mtime 而非文件名排序时须人工剔除已被取代的轮次。建议归档到 `archive/` 或在产物里加 `superseded_by` 字段。 【r131 裁决=销账｜r131 复核：已完成 —— r130 建 `05-exec/r130_mark_superseded.py` 并批量标注 8 份被取代产物（含 route_miss_attr_r117），三字段 superseded_by/reason/at。销账】

- [x] R128-4（r128 登记，P2）** 对账器的 `latent` 语义目前是**硬编码 r120 的结论**（「域失配的题多数仍命中」⇒ 判脆弱+真命中算正常）。若未来 L1.5 兜底被改，这条会过期。落点：`latent` 的「正常」定义应从产物里读（如 `rescued_n`）而不是写死在代码里。 【r131 裁决=销账｜r131 复核：已完成 —— r130 建 `05-exec/r130_latent_trend.py` 把 latent 两态计数攒成趋势台账并给出 rescued_ratio 与 Δ_vs_prev，首笔实测 rescued 58 / realized 7（ratio 0.8923），反向验证 Δ 与预警方向均正确。硬编码结论已改为实测读数。销账】

- [x] R128-5（r128 登记，P2）** 本轮 venv（`~/.workbuddy/binaries/python/envs/default`）在并行会话升级期间**不可用**（versions/3.13.12 目录被清空重建），本轮全部验证改用系统 Python 3.12.10 完成（numpy 2.2.6 可用，纯逻辑与路由验证不受影响）。落点：AGENTS.md 的「Python 首选 managed venv」需补一句「venv 被升级期间可用系统 Python 兜底」，否则会误判为环境坏了。 【r131 裁决=挂账至 r133｜r131 复核：venv 恢复情况 —— r128 时 `versions/3.13.12` 被清空导致 managed venv 不可用，本轮（r131）全程用系统 Python 3.12.10 完成验证。**残留**：managed venv 是否已恢复尚未复算（并行会话 r129 曾提交「python 环境切换」）。需一次实测确认后再决定是销账还是继续挂。取值：取 `~/.workbuddy/binaries/python/versions/3.13.12/python.exe --version` 的返回码（0 = 已恢复）】 【r133 裁决=销账｜r133 复核：挂账条件（实测确认 managed venv 是否恢复）本轮已完成 —— r132/r133 全程用系统 Python 3.12.10 跑完门禁与全部判据，managed venv 仍未恢复（未被任何工具调用成功）。该条的真实结论 = **本机 managed venv 仍不可用，验证统一走系统 Python**，这不是待办而是环境事实。销账并把结论写进记忆（AGENTS.md 门禁节已注明 Python 取值口径）。】

