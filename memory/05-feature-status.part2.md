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
