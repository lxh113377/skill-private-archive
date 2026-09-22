# 07 - 下一步

> 归档类型：增量（已完成项移入分卷）
> **⚠️ 这是新对话恢复上下文的入口文件；P0 永远不能空。**
> **真相源口径（2026-09-22 实测校准）**：P0 只放经实测确认**未完成**的项；已完成项一律迁入分卷 `- [x]`，不再滞留主卷。

## 最近对话摘要

- **2026-09-23（第 11 轮，本轮）** — A-project-better 全流程第二次实跑：Step 0 台账 10 条（取证 00:25，**6 条实为记忆滞后**）→ 用户按钮确认 → 四维诊断 + 3 条建议 → 用户选「全执行 1+2」：记忆层销账回写（06×4 条加注 / 05.part1 三条平台名 / 07 本卷 P0 收口 + 新待观察登记）→ 白名单提交 + savepoint 收口。**r2 补记**：`[推荐:R196-01]` 已收口——noise 处置提示补活跃工具运行态例外（A-project-handoff **V3.46.3**，受管根 `216be16`，dry-run 3/3 + py_compile + noise pass 路径复跑）
- **2026-09-22（第 6 批）** — 修 `rule_editor.py commit --fix-mirror`（`7d8a8e1`，R270）；v2 口径定格 **77 条**；31 件全量自包含入库（`29f9d868`）
- **2026-09-22（第 3 轮）** — A-project-better 四维体检 + 7 项非破坏性整改；见 `05-exec/第3轮执行报告.md`
- **2026-09-19（第 2 轮）** — 批2 剩余 P0 单点修复 + 注册表重建；见 `05-exec/第2轮执行报告.md`
- **2026-09-14（第 1 轮）** — 阶段0-4 主体；见 `07-next-steps.part3.md`

## P0 — 必须做

- [ ] **【待观察·他人在途】** 受管根未提交改动（2026-09-23 01:35 实测 `git -C D:\global_skills status --porcelain` = 6 条）：`gstack` / `local-computer-use` / `local-realtime-translator` / `local-screenshot-qa` / `chaoshi-image-optimization` / `chaoshi-web-deploy` 各自 `SKILL.md` 为 `M` —— 按 R269 与 P-1 铁律**只登记不擅动**，待对应会话自行收口
- [ ] **【待观察·焚诀在途债】** `gate_stub_runner` 实测 `[GATE:stub-fail]`（2026-09-23 01:35）：① 桩 `stub_c16_memory` 2/3——正例样本硬编码总分 `181.6` vs 活体评分卡 `183.9`（判据样本与活体口径漂移，R263 补注①形态，须由移动总分的会话裁决）；② 未登记桩判据 C17/C18/C19（registry 冻结于 09-22 后新增）。均非本轮引入（本轮仅改 A-project-handoff 文案，焚诀 eval 零触碰），按 R269 登记待其归属会话收口
## 分卷目录
- **卷1** `07-next-steps.part1.md` — 历史待办与已完成条目（2026-09-22 已按实测销账）
- **卷2** `07-next-steps.part2.md` — 已完成：批2 剩余 P0 与 q-2/q-3 收口
- **卷3** `07-next-steps.part3.md` — 最近对话摘要（历史）
- **卷4** `07-next-steps.part4.md` — 07-next-steps 分卷（R199 自动拆卷）
- **卷5** `07-next-steps.part5.md` — 07-next-steps 分卷（R199 自动拆卷）

