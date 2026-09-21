# 07 - 下一步

> 本文件记录下一步行动项，按优先级排序。
> 归档类型：增量（已完成的行动项移入归档）
>
> **⚠️ 这是新对话恢复上下文的入口文件。P0 必须永远有一条可执行指令。**

## 最近对话摘要

- **2026-09-19（第 3 轮，本轮）** —— 详见 `05-exec/第2轮执行报告.md` §十四~§二十
  - ✅ **批2 剩余 P0 单点修复**（commit `eb77870`，7 文件）：P0-5 ffmpeg 硬编码 `8.1.1` 失效（实测 9.0）→ 动态探测；P0-6 `VERSION_LOCK` 写死 `part1..4` → 动态枚举（实测 16 卷，旧文漏 12 卷致假阴性）；P0-10 上游缺失标注；P0-12 收尾门禁枚举 → 在役端 `OC/WB/TR/CX/HM`；P0-14 删 `A-memory-align` 死引用行
  - ✅ **P0-2 残留收口**（`4715713`，9 文件）：`cross-platform-agent-sync` 删 CC 平台表行/端口字典/启动文件段 + QW 特例段改留痕 + `5端/四端`→在役端；v1.3.0
  - ✅ **P0-10 补建上游 `video-breakdown-skill`**（`e145651`）：分镜拆解（scene 检测+关键帧+音频电平），**端到端实测 3 分镜/9 帧，两个下游 exit 0**
  - ✅ **注册表重建**（焚诀 `284cd75` / GM `6c0fc70`）：磁盘 169 == 注册表 169；`session-logs` 补退役黑名单解 fail-closed；**路由器 top1 命中新 skill**；`verify` 12 PASS / 2 FAIL（C13/C14 非本轮引入）
  - ✅ 三门禁全绿；⚠️ **工具坑**：`replace` 删除类补丁恒报 `[verify] FAIL 未找到`（误报，写盘成功）
- **2026-09-14（第 2 轮 / 第 1 轮）** — 详见 `07-next-steps.part3.md` 的「最近对话摘要（历史）」节

## P0 — 必须做

- [ ] **阶段5 工作流专项剩余（下一轮首选）** —— ① `direct_map` 误命中修正（实测「优化自建skill」误直连 `vp-perspective-audit`；方案见 `04-plan/工作流专项建议.md`）② 注册表 `user_created` 失真复核（阶段0 报 42 条，**须按当前 169 条注册表重新实测**，勿用旧数）
- [ ] **遗留：10 个文件复核（2026-09-19 实测重扫）** —— `prompt-system-audit` / `chaoshi-image-optimization` / `skill-hitrate-full-audit` **已归零**；`story-setup`(5) / `story-review`(4) / `story-short-write`(1) / `story-long-write`(1) 的命中是**上游结构性引用**（story 族 frontmatter `metadata.openclaw.source=github.com/worldwonderer/oh-story-claudecode`，其 hook/agent 模板本身就是 CC 体系）→ **建议保留原文**（改动即篡改上游）；`openclaw-task-supervision`(1) / `wps-knowledgebase`(1) / `data-layer-consistency-fix`(1) 待逐条判断
- [ ] **批5 余项（你已裁定：只做 b）** —— a 审计族 15→8 / c local `_shared` 抽取 / d 4 个 Notion 件 = **本阶段不做**；如需再议
- [ ] **B5 非本审计范围** —— `cloudbase__skillhub/*` 他人未提交改动；`.rule_backup/` 248 个 `.bak` 待按 R198.7 轮转
## 分卷目录
- **卷1** `07-next-steps.part1.md` — 历史待办与已完成条目（R199 自动拆卷）
- **卷2** `07-next-steps.part2.md` — 已完成：批2 剩余 P0 与 q-2/q-3 收口
- **卷3** `07-next-steps.part3.md` — 最近对话摘要（历史）
