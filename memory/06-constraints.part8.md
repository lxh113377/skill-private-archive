# 06-constraints.part8 -- 纪律条目正文归档（#30-#48，r154 从 AGENTS.md 迁入，原文零改写）

## ⚠️ 纪律须有阻断点（#35，2026-10-21 立规）

立了纪律却没有**阻断点**，等于没立。r136 盘点：本仓 5 条强制条目**全部没有流程强制点**
（门只跑不阻断、`.git/hooks` 三个 hook 全部 `exit 0`）。

**机器判据**：本次提交若落在纪律面（改 `05-exec/` / 转办提案 / 对标报告 / `AGENTS.md` /
`memory/07-next-steps.md` / `run_gates.py`），则**对应的门必须过**，否则**阻断提交**。
判定由 `python 05-exec/r137_commit_gate_map.py --json <件>`（第 49 门）给出
`required_gate_ids` / `in_scope_n`；`pre-commit` 依此逐门跑（`run_gates.py --gate <id> --no-ledger`）并按结果阻断。

**分级原则（R137 定）**：
- **不在纪律面**（`in_scope_n = 0`）⇒ **不阻断** —— 并行会话也在改同一个仓，
  无差别阻断 = 把我的判据变成「别人的活干不下去」（R269 反面）。这是 r130 老 hook 一直 exit 0 的正当理由，保留。
- **在纪律面** ⇒ 逐门跑，只阻断**这些门**的红；不连带阻断其他门（避免把无关的历史红算到本次头上）。
- **逃生阀**：`SKIP_COMMIT_GATES=1 git commit ...` 可放行，但**必须在提交说明里写明为何先落盘**。
- **台账不污染**：hook 用 `--no-ledger` 试跑，不写门禁台账（新鲜度门读的是完整跑的台账）。

**5 条强制条目的阻断点现状（r137 实测）**：

| 条目 | 触发条件 | 阻断的门 | 状态 |
|---|---|---|---|
| #30 落盘强制 | 改 `memory/07-next-steps.md` | `debt_aging`（账龄件重生） | 有阻断点 |
| #31 处方必先实测 | 改转办提案台账 | `proposal_evidence_face` | 有阻断点 |
| #32 判据面必先实测 | 改 `05-exec/` 下的判据 | `proposal_evidence_face` + 门表对账闸 | 有阻断点 |
| #33 结论层推理须标注 | 写/改对标报告 | `causal_evidence_face` | 有阻断点 |
| #34 纪律自用 | 改提案 / 改 `AGENTS.md` | `proposal_evidence_face` + `gate_table_reconcile` | 有阻断点 |

> 取值：`python 05-exec/r137_commit_gate_map.py --json <件>` 的 `required_gate_ids`；
> 阻断行为实测见 `_temp/v23_redprobe.py`（造一条无支撑提案 ⇒ 门面报「无读数支撑 1」⇒ 该门红 ⇒ hook 阻断）。

## ⚠️ 阻断机制须可恢复（#36，2026-10-21 立规）

#35（纪律须有阻断点）立了之后，r137 收尾发现一个更隐蔽的问题：**阻断机制本身不可恢复**。
`.git/hooks/` **不在 git 里**（`tracked hooks = 0`）⇒ 换机 / clone / 重装即全丢。
r130 与 r137 两次装 hook，装完都没再核过 ——
**「阻断机制不可恢复」比「没有阻断机制」更危险，因为它让人以为有。**

**机器判据**：
1. 阻断机制健在性由第 50 门（`r138_hook_health.py`）逐项断言 —— `pre-commit` 存在、含 `exit 1`、
   含分级判定入口、含逃生阀、用 `--no-ledger`；`post-commit` 存在；判定面脚本可跑。**任一不通判红**。
2. 恢复路径必须**脚本化且可自证**：`python 05-exec/r138_install_hooks.py`
   从 git 跟踪的模板（`05-exec/hook_templates/*.sh`）安装，**装完立刻跑自检**，不通则 rc≠0。

**反向验证（r138 实测，三态）**：

| 变体 | 读数 | 判定 |
|---|---|---|
| 空 hooks 目录（换机/clone 后真实态） | 2/8 通过，**6 项 FAIL** | 有牙 |
| `exit 1` 被抹掉（#35 要治的病） | **H2 精准 FAIL** | 有牙 |
| 真实 hooks | 8/8 通过 | 不冤枉 |

**恢复闭环实测（r138）**：删掉 `pre-commit` ⇒ 自检报 `3/8`（5 项 FAIL）⇒ 跑安装脚本 ⇒
`安装 2/2` + `自证 rc=0` ⇒ 再自检 `8/8`。**「不可恢复」变成「一条命令恢复且自证」。**
