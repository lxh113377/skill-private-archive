# r21b 规则补丁暂存区（未应用）

本目录是 **A-memory-start V10.70.0 那次已落地又被撤回的改动原文**。撤回原因不是内容错，是**放不进去**：

| 事实 | 实测值 | 取值命令 |
|---|---|---|
| C25 注入区基线 | 64,472 B（5 文件） | `python 焚诀/eval/verify_truth_consistency.py` C25 行 |
| 应用补丁后 | **65,557 B > 硬顶 65,536（+21）** ⇒ `C25 ❌ FAIL(W3)` | 同上（已复跑证实） |
| 我的净增量 | +1,085 B（ROUTER 行 543 + SKILL.md 版本摘要行 542） | `stat -c%s` 前后差 |
| 撤回后 | 64,252 B，余量 1,284（2.0%）⇒ C25/C31 复绿 | 同上 |

## 为什么不能"只留一半"

- `W4 判据 = 总字节 > 基线即 FAIL` ⇒ **棘轮只降不升，任何净增长都不允许**，不存在"少写点就行"的空间（除非同时腾挪出等量字节）。
- `C13 判据 = frontmatter 版本 == SKILL.md 自身版本历史区最大版本` ⇒ 加了 ROUTER 行就必须 bump 版本，bump 就必须同时写 SKILL.md 摘要行 ⇒ **两处字节绑定，不能只改 references/**（version_history.md 不在预算内，但 SKILL.md 那行在）。

## 本条规则的执法改挂在执行路径（已生效，无需本补丁）

1. 本项目定时任务 `36e379f3-66e8-4ee9-b432-c97fd036cc4c` 的 instruction 已前置第 0 步闸门（详见 `06-benchmark/cron_tasks_backup_2026-09-24.json` 的备份与 restore_command）。
2. 闸门实物 = `../../repeat_round_guard.py`（0 放行 / 1 拒绝 / 2 取证失败）。

⇒ 符合 A-get-memory Step 2.7 的判据：「下一个会话不做任何事，这个强化还生效吗？」——排程侧自带闸门 = **机器型、生效**；而 ROUTER 行只是自觉型，且此刻要用掉 1,085B 硬预算。**用自觉型条款换机器型执法是亏的，所以撤回。**

## 何时应该应用本补丁

同时满足两条再应用（应用方式 = `rule_editor.py insert/replace`，禁直接改文件）：

- [ ] 注入区腾挪出 ≥ 本补丁净增字节（等量瘦身或 owner 依 C31 台账下调 `truth_constants.inject_budget.baseline_bytes`）；
- [ ] 其它 6 个项目的定时任务也已接入闸门（否则只有本仓受益，规则面与实面不符）。

文件：`a_row.txt`（ROUTER 行）·`c_sum.txt`（SKILL.md 版本摘要行）·`d_full.txt`（version_history.md 完整条目）。
