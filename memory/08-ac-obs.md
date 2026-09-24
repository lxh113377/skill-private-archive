# 08 - AC-OBS 验收标准

> 本文件定义每个核心功能的可观测验收标准。
> 归档类型：增量（已验证的标准移入归档）
> 
> 格式规范：
> AC-OBS-NN: [功能描述] → [验证方式] + [证据类型]
> 
> 证据类型：截图 | 日志 | 测试输出 | API响应 | 数据库查询 | 视频录制

## 验收标准列表

<!-- 示例：
- AC-OBS-01: 用户登录功能 → 输入正确账密点击登录，跳转到首页 | 截图 + URL变化
- AC-OBS-02: API返回数据正确 → GET /api/users 返回200 + JSON数组 | API响应
- AC-OBS-03: 页面响应速度 → Lighthouse评分 > 90 | 测试输出
-->

<!-- 以下为本项目**真实**验收标准（2026-09-22 回填；`- [x]` = 已实测通过，`- [ ]` = 尚未验证，禁写成通过） -->

- [ ] AC-OBS-01: 阶段0 自建清单裁定可复跑 → 跑 `01-scan/scan_all.py --stage scope` 退出码 0 且 `00-scope/` 下 3 个产物齐备（清单 / 失真条目 / scope_result.json） | 测试输出
- [ ] AC-OBS-02: 阶段1 四维扫描可复跑 → 跑 `01-scan/scan_all.py --stage scan` 退出码 0 且 `01-scan/scan_result.json` 可被 JSON 解析 | 测试输出
- [x] AC-OBS-03: 注册表与磁盘集合一致 → 焚诀 `verify_truth_consistency.py` 打印 `✅ C1 … 注册表 == 磁盘`（2026-09-22 实测 120 skills）—— ✅ 校正注（2026-09-23 r8）：120 为**重建前**口径；现行注册表口径 = **151**（磁盘实测全等，`28daf6e` 重建后持续成立），以 151 为准 | 测试输出
- [x] AC-OBS-04: 三门禁全绿 → `D:\global_skills\A-memory-start\references\rule_editor.py gates` 退出码 0 且打印 `mirror=pass noise=pass evolution=pass`（2026-09-22 实测；2026-09-24 r17 命令绝对路径化适配 --verify-ac 机器可跑） | 测试输出
- [x] AC-OBS-05: 记忆可交接 → `D:\global_skills\A-project-handoff\scripts\handoff.py savepoint C:\Users\37533\Desktop\workspace\自建skill优化` 退出码 0（07 P0 非空 + P-1 绑定表存在 + 门禁 PASS）—— 2026-09-22 实测 **exit 0「本次对话已安全落盘」**；P0 未完成 8 项、coldstart --check 6 行全等、`noise` = `[GATE:noise-pass]`；2026-09-24 r17 命令绝对路径化适配 --verify-ac 机器可跑 | 测试输出
- [ ] AC-OBS-06: 记忆完整性达标 → `D:\global_skills\A-project-handoff\scripts\handoff.py review C:\Users\37533\Desktop\workspace\自建skill优化` 输出 `Score: 9/9` 且 warnings = 0 —— 2026-09-22 实测 **7/9（78%）**，剩 2 条均为上游判据缺陷（假阴性 + 注释未剔）；2026-09-24 r17 命令绝对路径化适配 --verify-ac 机器可跑 | 测试输出
- [ ] AC-OBS-07: 改动可回滚且已离机 → `git log --oneline` 每个主题 ≥1 提交，且 `git rev-parse HEAD` == `git ls-remote origin main` 的 SHA（致命纪律 #20）—— 待 D4 授权 | 测试输出
- [ ] AC-OBS-08: 交付物入口可达 → 从 `README.md` 的「六阶段产物地图」出发，每行列出的路径 `Test-Path` 全为 `True` | 测试输出

<!-- ⚠️ 门禁缺陷留痕（2026-09-22 实测）：上方 `<!-- 示例： -->` 块里的 3 条**并非**本项目验收标准，但
     `handoff.py review` 会把它计入（`savepoint.py:632` 全文匹配不剔注释）→ 实测输出
     「8 个 AC-OBS，但只有 11 个格式正确」（11 > 8 自相矛盾），该子命令的 AC 计数不可信。
     处置遵循 R263：**不改数据去凑判据**，缺陷本身登记为 `06-constraints.md` 的 [BUG]，修复待确认 D1。 -->

<!-- 验证通过后标记 - [x]，归档时自动移入 archive -->
