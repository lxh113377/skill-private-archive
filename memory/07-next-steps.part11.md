# 07-next-steps.part11.md

<!-- 本卷为 07-next-steps.part10.md 的延续 -->

## P0 条目历史复核（原样迁入，零改写）

- [x] **【P0 止血·r21→r22 重复触发源头｜已闭环（频率保留版）】** 用户 2026-09-24 裁定**每小时一次保持不变、拒绝降频建议** ⇒ 止血方式改为「频率不动 + 每轮自带幂等闸门」。
  - 已完成：`cron_tasks_backup_v2_full_2026-09-24.json` 先入库（commit `1a9fa35`，含 6 条未改任务的逐字原文 + restore_template）→ 再对 **7 条任务全部只发 `patch.prompt`**（`schedule/enabled/model/permissionMode/outputMode` 一个字段都没发 ⇒ 全部保留原值，逐条回执已核对 `everyMs` 6×3600000 + 1×7200000）。
  - 新文本第 0 步 = 跑规范闸门绝对路径 + `--repo <该仓>`，DUPLICATE(exit1)→禁全量轮、只补口径或空转；并显式写入「禁止修改 schedule/everyMs/启停」，防后续会话自作主张降频。
  - **两退出码复验（修正上一轮管道取 $? 的脚手架缺陷，本轮直连不接管道）**：医 / 超市web / 焚诀 三仓实测 `rc=1 判定 DUPLICATE`；同仓喂无关指令族 `rc=0 判定 FRESH`（不误伤）。
  - 残余风险：闸门脚本单点在 `自建skill优化/05-exec/`，若该仓移动需同步 7 条任务的路径；A-memory-start ROUTER 条款仍受 C25 注入预算硬顶挡在门外（见 `05-exec/r21b-patches/README.md` 两条前置判据）。 上一轮判「本机无可改配置」已**被本轮推翻**（见下条 r21b）；剩余待办 = 其余 6 个项目的同类任务降频/接闸门，属各自决策面。取值命令：`mcp qoder_cron action=list`。
