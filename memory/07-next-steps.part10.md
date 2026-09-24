# 07-next-steps.part10.md

<!-- 本卷为 07-next-steps.part9.md 的延续 -->

## P0 条目历史复核（原样迁入，零改写）

- [x] **【r21b 止血进展（2026-09-24 21:2x，本轮已完成）】** 本轮 MCP 新增 `qoder_cron` 工具，`action=list` 实测 **7 个 enabled 本地自动化任务**（门店/医/陪聊/孝心/超市/自建skill `everyMs=3600000`，焚诀 `7200000`），**同一条 303 字符指令、全部 `bypassPermissions`、outputMode=merged**；按 `lastDurationMs` 折算 6 个整点任务合计 **79.2 分钟/小时 = 墙钟 1.32 倍**（必然重叠并发），含焚诀 ≈ **20.7 小时/天**无人值守全权限 agent 运行。三步止血：**① 全量定义先备份入库**（`06-benchmark/cron_tasks_backup_2026-09-24.json`：逐字段原文 + `restore_command`，独立 commit 先行满足「备份+Git」前提）**② 只改本项目那条任务的 instruction**（`36e379f3`，revision 7→8；schedule/模型/权限/outputMode 全保留原值；新文第 0 步 = 跑 `repeat_round_guard.py`，DUPLICATE→禁全量轮只补口径，原七维全量要求与收尾红线原样保留）**③ 其余 6 条未动**。**自我纠偏一件**：曾把该规则写入 A-memory-start ROUTER（V10.70.0），**被自家 C25 注入预算棘轮当场拦下**（净增 +1,085B ⇒ 65,557B > 硬顶 65,536，W3 FAIL），已撤回（受管根 `5819b47`，反向删除走 rule_editor），复跑 `gates = mirror/noise/evolution/stub 全 pass` + `verify 31 PASS/0 FAIL`、C25 回 64,252B（余量 1,284）；补丁原文暂存 `05-exec/r21b-patches/README.md`（含「何时该应用」两条前置判据）。**新教训（已入 lessons）**：撤回受管根改动也必须走 `rule_editor`——用 `git checkout` 绕过写入链会被 r20 脏源检测判为「他人在途」而 fail-closed 拦提交，**该拦截是真阳性，工具行为正确**。

- [x] **【P0 止血·r21→r22 重复触发源头｜已闭环（频率保留版）】** 用户 2026-09-24 裁定**每小时一次保持不变、拒绝降频建议** ⇒ 止血方式改为「频率不动 + 每轮自带幂等闸门」。
  - 已完成：`cron_tasks_backup_v2_full_2026-09-24.json` 先入库（commit `1a9fa35`，含 6 条未改任务的逐字原文 + restore_template）→ 再对 **7 条任务全部只发 `patch.prompt`**（`schedule/enabled/model/permissionMode/outputMode` 一个字段都没发 ⇒ 全部保留原值，逐条回执已核对 `everyMs` 6×3600000 + 1×7200000）。
  - 新文本第 0 步 = 跑规范闸门绝对路径 + `--repo <该仓>`，DUPLICATE(exit1)→禁全量轮、只补口径或空转；并显式写入「禁止修改 schedule/everyMs/启停」，防后续会话自作主张降频。
  - **两退出码复验（修正上一轮管道取 $? 的脚手架缺陷，本轮直连不接管道）**：医 / 超市web / 焚诀 三仓实测 `rc=1 判定 DUPLICATE`；同仓喂无关指令族 `rc=0 判定 FRESH`（不误伤）。
  - 残余风险：闸门脚本单点在 `自建skill优化/05-exec/`，若该仓移动需同步 7 条任务的路径；A-memory-start ROUTER 条款仍受 C25 注入预算硬顶挡在门外（见 `05-exec/r21b-patches/README.md` 两条前置判据）。 上一轮判「本机无可改配置」已**被本轮推翻**（见下条 r21b）；剩余待办 = 其余 6 个项目的同类任务降频/接闸门，属各自决策面。取值命令：`mcp qoder_cron action=list`。
