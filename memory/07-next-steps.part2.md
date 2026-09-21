# 07-next-steps.part2.md

<!-- 本卷为 07-next-steps.md 的延续 -->

## 已完成（批2 剩余 P0 与 q-2/q-3 收口，2026-09-19）

- [x] **批2 剩余 P0 单点修复完成（2026-09-19，commit `eb77870`）** —— P0-5/P0-6/P0-10/P0-12/P0-14 五项一次收口（7 文件），三门禁全绿

- [x] **q-2 焚诀重建完成（2026-09-14）** —— 实测 `retire_skill.py` 因「目录存在性校验」拒跑（副本已删）→ 改走它的**设计语义**：补黑名单 8 项 → `retire_reconcile --repair` 清注册表 → `build_registry`（**登记表 168 == 磁盘 168**）→ `build_indexes --apply`（守恒 PASS 168 条）→ 双仓提交（焚诀 `6a06d74` / GM `244937e`）。门禁 **13 PASS / 1 FAIL**（C1+C6 已修；仅剩**与我无关**的 C14 时效）；**路由器 top1 从死件 `skill-install` → `skill-manager`，候选中再无退役件**

- [x] **q-3 HM 口径统一完成（2026-09-14，三仓提交）** —— 焚诀 `f145f7f`：`endpoints.active` += hm、`junction_paths` += hm、`retired` -= hm；`platform_tiers` tiers+=hm / retired-=hm；新增 `skill/registry/platform-hm.json` + `scripts/wf_hm.ps1`；`build_registry.platform_files` += hm；**`verify` C4 标题改为「cx/hm 存在」**且 `_ep_to_file` += hm。GM `c0a582b`：`core/SOUL.md:36/44`、`meta/six_sync_checklist.md`（**V5**：CC 标弃用 + HM 活跃行 + junction 维护章节）、`memory/06-constraints.md:20`、`cross_platform_map.json` `platform_facts.hm`+note。global_skills：`A-memory-start` **V10.29.0**（G2 枚举 `<OC/WB/TR/CX/HM>`）、`A-project-handoff` **V3.38.0**（新增致命纪律 #19）
  - 验收：焚诀 `verify` **13 PASS / 1 FAIL**（C3/C4/C11 全绿，仅剩无关的 C14）；`global_skills` `mirror=pass noise=pass evolution=pass`

- [x] **q-3 HM 记忆接入完成** —— `AppData\Local\hermes\memories` junction → `D:\global_memory`（照 WB/TC 惯例），实测 63 项可见

- [x] **q-3 junction 农场维护步骤已写入** —— `meta/six_sync_checklist.md` 新增「HM junction 农场维护」章节（新增/清理命令 + 两种禁做做法及实测依据）

- [x] **批1 弃用平台名清理完成（2026-09-14，8 skill / 10 文件一次提交）** —— 活跃示例与指令改用在役端（`OC/WB/TR/CX/HM`）；CC 专属路径/调用示例段**删除并留注**（不以未经实测的路径替换）；QW 条目保留可操作结论并标注已下线；「已卸载平台」举例（QClaw / `[已下线]`QoderWork / 旧版TRAE）**按纪律保留原文**。三门禁 `mirror=pass noise=pass evolution=pass`

- [x] **批1 剩余：弃用平台名清理（2026-09-14 完成，commit `c319e86`，8 skill / 10 文件）** —— `windows-cli-utf8-wrapper` / `discover-agent-cli`(含 `reference.md`) / `workflow-preflight-check`(含 `reference/manifest-schema.md`) / `vp-perspective-audit` / `skill-routing-regeneration` / `windows-native-ocr` / `prompt-consolidation` / `skill-defer-to-authority`；活跃示例改在役端，CC 专属路径段删除留注，「已卸载平台」举例保留原文

- [x] **灰区归属（你已裁定）** —— Intel 分发样例包（`local-asr`/`computer-use`/`realtime-translator`/`tts`/`txt2img`）+ 25 个边缘件 = **按来源判「排除」**，不纳入维护范围

- [x] **HM 恢复在役的口径统一（已完成，2026-09-14 三仓提交）** —— 焚诀 `f145f7f` + GM `c0a582b` + global_skills `cd5d733`（`A-memory-start` V10.29.0 G2 枚举 `<OC/WB/TR/CX/HM>`、`A-project-handoff` V3.38.0）；2026-09-19 复核 `cross_platform_map.json` `platform_facts` 已是 cc retired / qw removed / hm active
