# 05-feature-status.part2.md

<!-- 本卷为 05-feature-status.md 的延续 -->

## ✅ 已完成（2026-09-19 第 3 轮）

- 批2 剩余 P0 单点修复（commit `eb77870`，7 文件）：P0-5 ffmpeg 硬编码失效→动态探测（实测 9.0）/ P0-6 VERSION_LOCK 写死 part1..4→动态枚举（实测 16 卷）/ P0-10 上游缺失标注 / P0-12 收尾门禁平台枚举→在役端 / P0-14 删 A-memory-align 死引用行

- 批1 残留 P0-2 收口（commit `4715713`，9 文件）：`cross-platform-agent-sync` 平台口径对齐在役端 `OC/WB/TR/CX/HM` —— 删 CC 平台表行/端口字典/启动文件段（part1/2/4/5/6/7），QW 特例段改留痕（part3/4/8），`5端/四端`→在役端，description 口径修正；v1.2.1→1.3.0；残留 2 处为刻意弃用说明

- P0-10 补建上游 `video-breakdown-skill`（commit `e145651`，4 文件）：`SKILL.md` + `scripts/process_video.py`（ffprobe + scene 检测 + 3 关键帧/分镜 + volumedetect；**机械层产 breakdown.json，语义层留 agent**）
  - **端到端实测**：合成 3 镜头视频 → 3 分镜 / 9 关键帧 → `hook-analyzer-skill` 与 `report-generator-skill` 双双 exit 0
  - 下游示例回填真实上游命令；两件 v1.0.1→1.0.2

- 注册表重建（焚诀 `284cd75` / GM `6c0fc70`）：`video-breakdown-skill` + OC 包新增 `control-ui` 入库 → **磁盘 169 == 注册表 169**；`session-logs`（市场件，磁盘随 OC 包更新移除）补退役黑名单 + `retire_reconcile --repair` 剔除，解 `build_indexes` fail-closed；守恒 PASS 169 条
  - **路由器实测**：`拆解视频分镜` → top1 `video-breakdown-skill`(0.6465)；`分镜拆解出关键帧` → top1 同上(0.7363)
  - `verify_truth_consistency`：12 PASS / 2 FAIL（C13 A-memory-start 版本漂移、C14 时效产物，**均非本轮引入**）
  - 三门禁 `mirror=pass noise=pass evolution=pass`

## ✅ 已完成（2026-09-22 第 3 轮）

- **A-project-better 四维体检**（用户按钮选定口径）→ `05-exec/第3轮执行报告.md`：四源感知 + 5 项门禁实跑取证 + 四维诊断 + 10 条建议清单
  - 门禁实测基线：`handoff status` 6/8 filled；`handoff review` 5/9（56%，4 warnings）；`rule_editor.py gates` 三门禁全绿；焚诀 `verify` **15 PASS / 0 FAIL / 0 SKIP**；版本控制基线（#20）远端 SHA == 本地 HEAD ✅
- **7 项非破坏性整改落盘**：
  1. `07-next-steps.md` 主卷 P0 按实测重写 + `part1` 过期待办逐条销账（原「已完成」标题下藏 7 条 `- [ ]`，其中 5 条实测早已完成）
  2. `05-feature-status.part1.md` 清失效阻塞：LOW 灰区 / HM 方案 / q-2 / q-3 四项均移入「已解除（历史留痕）」
  3. `01-goal.md` 六阶段目标按实测勾选 + 补「已完成目标」3 条
  4. `handoff.py sync` 填充 `02-structure.md` 目录树 + 手工回填模块说明 / `03-tech-stack.md` / `04-file-map.md`
  5. `06-constraints.md` 补 4 条 [BUG] + 7 条 [DEBT] + 5 条红线
  6. `08-ac-obs.md` 补 **8 条真实可复跑 AC**（AC-OBS-01~08，全部带命令判据）
  7. 新增 `README.md`（工作区入口）/ `05-exec/README.md`（19 patch 索引）/ `05-exec/第3轮执行报告.md`
- **本轮新发现（实测，已登记为待办）**：
  - 上游门禁 **3 处判据缺陷**：AC 未剔注释致假通过 / 05 判「无功能状态」假阴性 / `status`≠`review` 对 02 口径矛盾
  - GM 每日日志 **09-09~09-20 空档 12 天**（R9 事故清空未回填）→ 项目 09-14/09-19 的 footer 落盘证据不可核验
  - skill 数口径 **四数不一**（169 / 120 / 152 / 205）
  - `.rule_backup` 实测 32 个 `.bak`；`01-scan/overlap_raw.txt`（283KB）中间产物滞留
- **收尾（2026-09-22）**：`savepoint` **exit 0**（中途 1 次被拒 = `焚诀\.codebuddy` 未 gitignore 豁免 → 并行会话 `1f354e9` 解除）；焚诀 `verify` 15 PASS / 0 FAIL；`gates` 三门禁全绿
