## P0 条目历史复核（原样迁入，零改写）

### 受管根在途改动 —— 历史复核（第 12 轮 / r4）
**第 12 轮复核（2026-09-23 01:30）**：仍为同 6 条 `M`，未收口，维持待观察。**第 13 轮 r4 复核（2026-09-23 05:43）**：实测降为 **5 条 `M`**（`chaoshi-web-deploy` 已由归属会话收口；`chaoshi-image-optimization` 仍 `M`），未清零，维持待观察

### 焚诀在途债 —— 历史复核（第 12 轮 / r4）
**第 12 轮复核（2026-09-23 01:30）**：stub 复跑仍 `[GATE:stub-fail]`（2/3 + 3 未登记，同态）；同刻焚诀 `verify_truth_consistency.py` **19 PASS / 0 FAIL**，C17/C18/C19 静态判据本身全绿——债仅在「桩未登记 + 样本漂移」层，维持待观察。**第 13 轮 r4 复核（2026-09-23 05:43）**：`rule_editor.py gates` 复跑仍 `mirror/noise/evolution=pass / stub=fail`（1 桩失败 + 3 未登记，同态）；同刻焚诀 `verify_truth_consistency.py` **19 PASS / 0 FAIL**（C16 总分 183.9=六线之和、C17~C19 全绿），维持待观察

- [x] **【待观察·新节缺失】** `09-workflow-state.md`：并行会话在途功能（`handoff_lib/common.py` 已把该文件列为第 9 个记忆节 + `templates/09-workflow-state.md.tmpl` 模板已落盘但**未提交**）⇒ 本项目 `status` 现报 **8/9**（该节 `❌ missing`）。按 R269 **不擅动**（模板/口径仍在途，避免与归属会话冲突）；待其提交收口后按官方模板补建该节并复跑 status/review —— **✅ 收口注（2026-09-23 r7 已补建）**：3.49.0 已提交（模板入库）⇒ 阻塞解除；本轮 `flow --init` 补建 `memory/09-workflow-state.md`（schema `fenjue-workflow-state-v1`），`flow --check` PASS，`status` 9 节全 filled、`review` 9/9

- [x] **【待办·文档同步】** noise_lint 修补（受管根 `d88b5ee`，2026-09-23 r6）的**三处文档同步待补**：`SKILL.md` 版本行、`references/version-history.md` 条目、`commands.md §11` 豁免口径说明 —— 暂缓原因 = 并行会话已把 `version: 3.49.0` 与这三个文件纳入在途改动（其 `handoff_v3.50` 系功能），此刻补写必然二次夹带他人改动。**处置**：待其提交收口后，按 3.49.0 → 下一版补登记（若其条目已含本修补则只需核对）；登记证据 = 本轮 commit `d88b5ee` 的提交信息已完整记述修补内容与验证 —— **✅ 收口注（2026-09-23 r7 已收口）**：阻塞（并行会话在途）解除 ⇒ 受管根 `7ebd682`（rule_editor 三文件白名单收口）：版本行 3.50.0→**3.51.0** + `version-history.md` 补 V3.51.0 条目（d88b5ee 补登记，零代码变更）+ `commands.md §11` 补二级扫描豁免口径；gates 四门禁 pass
