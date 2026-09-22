## P0 条目历史复核（原样迁入，零改写）

### 受管根在途改动 —— 历史复核（第 12 轮 / r4）
**第 12 轮复核（2026-09-23 01:30）**：仍为同 6 条 `M`，未收口，维持待观察。**第 13 轮 r4 复核（2026-09-23 05:43）**：实测降为 **5 条 `M`**（`chaoshi-web-deploy` 已由归属会话收口；`chaoshi-image-optimization` 仍 `M`），未清零，维持待观察

### 焚诀在途债 —— 历史复核（第 12 轮 / r4）
**第 12 轮复核（2026-09-23 01:30）**：stub 复跑仍 `[GATE:stub-fail]`（2/3 + 3 未登记，同态）；同刻焚诀 `verify_truth_consistency.py` **19 PASS / 0 FAIL**，C17/C18/C19 静态判据本身全绿——债仅在「桩未登记 + 样本漂移」层，维持待观察。**第 13 轮 r4 复核（2026-09-23 05:43）**：`rule_editor.py gates` 复跑仍 `mirror/noise/evolution=pass / stub=fail`（1 桩失败 + 3 未登记，同态）；同刻焚诀 `verify_truth_consistency.py` **19 PASS / 0 FAIL**（C16 总分 183.9=六线之和、C17~C19 全绿），维持待观察
