# 07-next-steps.part9.md

<!-- 本卷为 07-next-steps.part8.md 的延续 -->

## P0 条目历史复核（原样迁入，零改写）

- [x] **【待观察·新节缺失】** `09-workflow-state.md`：并行会话在途功能（`handoff_lib/common.py` 已把该文件列为第 9 个记忆节 + `templates/09-workflow-state.md.tmpl` 模板已落盘但**未提交**）⇒ 本项目 `status` 现报 **8/9**（该节 `❌ missing`）。按 R269 **不擅动**（模板/口径仍在途，避免与归属会话冲突）；待其提交收口后按官方模板补建该节并复跑 status/review —— **✅ 收口注（2026-09-23 r7 已补建）**：3.49.0 已提交（模板入库）⇒ 阻塞解除；本轮 `flow --init` 补建 `memory/09-workflow-state.md`（schema `fenjue-workflow-state-v1`），`flow --check` PASS，`status` 9 节全 filled、`review` 9/9

- [x] **【待办·文档同步】** noise_lint 修补（受管根 `d88b5ee`，2026-09-23 r6）的**三处文档同步待补**：`SKILL.md` 版本行、`references/version-history.md` 条目、`commands.md §11` 豁免口径说明 —— 暂缓原因 = 并行会话已把 `version: 3.49.0` 与这三个文件纳入在途改动（其 `handoff_v3.50` 系功能），此刻补写必然二次夹带他人改动。**处置**：待其提交收口后，按 3.49.0 → 下一版补登记（若其条目已含本修补则只需核对）；登记证据 = 本轮 commit `d88b5ee` 的提交信息已完整记述修补内容与验证 —— **✅ 收口注（2026-09-23 r7 已收口）**：阻塞（并行会话在途）解除 ⇒ 受管根 `7ebd682`（rule_editor 三文件白名单收口）：版本行 3.50.0→**3.51.0** + `version-history.md` 补 V3.51.0 条目（d88b5ee 补登记，零代码变更）+ `commands.md §11` 补二级扫描豁免口径；gates 四门禁 pass

- [x] **【r21b 止血进展（2026-09-24 21:2x，本轮已完成）】** 本轮 MCP 新增 `qoder_cron` 工具，`action=list` 实测 **7 个 enabled 本地自动化任务**（门店/医/陪聊/孝心/超市/自建skill `everyMs=3600000`，焚诀 `7200000`），**同一条 303 字符指令、全部 `bypassPermissions`、outputMode=merged**；按 `lastDurationMs` 折算 6 个整点任务合计 **79.2 分钟/小时 = 墙钟 1.32 倍**（必然重叠并发），含焚诀 ≈ **20.7 小时/天**无人值守全权限 agent 运行。三步止血：**① 全量定义先备份入库**（`06-benchmark/cron_tasks_backup_2026-09-24.json`：逐字段原文 + `restore_command`，独立 commit 先行满足「备份+Git」前提）**② 只改本项目那条任务的 instruction**（`36e379f3`，revision 7→8；schedule/模型/权限/outputMode 全保留原值；新文第 0 步 = 跑 `repeat_round_guard.py`，DUPLICATE→禁全量轮只补口径，原七维全量要求与收尾红线原样保留）**③ 其余 6 条未动**。**自我纠偏一件**：曾把该规则写入 A-memory-start ROUTER（V10.70.0），**被自家 C25 注入预算棘轮当场拦下**（净增 +1,085B ⇒ 65,557B > 硬顶 65,536，W3 FAIL），已撤回（受管根 `5819b47`，反向删除走 rule_editor），复跑 `gates = mirror/noise/evolution/stub 全 pass` + `verify 31 PASS/0 FAIL`、C25 回 64,252B（余量 1,284）；补丁原文暂存 `05-exec/r21b-patches/README.md`（含「何时该应用」两条前置判据）。**新教训（已入 lessons）**：撤回受管根改动也必须走 `rule_editor`——用 `git checkout` 绕过写入链会被 r20 脏源检测判为「他人在途」而 fail-closed 拦提交，**该拦截是真阳性，工具行为正确**。
