# 07-next-steps.part11.md

<!-- 本卷为 07-next-steps.part10.md 的延续 -->

## P0 条目历史复核（原样迁入，零改写）

- [x] **【P0 止血·r21→r22 重复触发源头｜已闭环（频率保留版）】** 用户 2026-09-24 裁定**每小时一次保持不变、拒绝降频建议** ⇒ 止血方式改为「频率不动 + 每轮自带幂等闸门」。
  - 已完成：`cron_tasks_backup_v2_full_2026-09-24.json` 先入库（commit `1a9fa35`，含 6 条未改任务的逐字原文 + restore_template）→ 再对 **7 条任务全部只发 `patch.prompt`**（`schedule/enabled/model/permissionMode/outputMode` 一个字段都没发 ⇒ 全部保留原值，逐条回执已核对 `everyMs` 6×3600000 + 1×7200000）。
  - 新文本第 0 步 = 跑规范闸门绝对路径 + `--repo <该仓>`，DUPLICATE(exit1)→禁全量轮、只补口径或空转；并显式写入「禁止修改 schedule/everyMs/启停」，防后续会话自作主张降频。
  - **两退出码复验（修正上一轮管道取 $? 的脚手架缺陷，本轮直连不接管道）**：医 / 超市web / 焚诀 三仓实测 `rc=1 判定 DUPLICATE`；同仓喂无关指令族 `rc=0 判定 FRESH`（不误伤）。
  - 残余风险：闸门脚本单点在 `自建skill优化/05-exec/`，若该仓移动需同步 7 条任务的路径；A-memory-start ROUTER 条款仍受 C25 注入预算硬顶挡在门外（见 `05-exec/r21b-patches/README.md` 两条前置判据）。 上一轮判「本机无可改配置」已**被本轮推翻**（见下条 r21b）；剩余待办 = 其余 6 个项目的同类任务降频/接闸门，属各自决策面。取值命令：`mcp qoder_cron action=list`。

- [x] **【r21c 还账（2026-09-24 21:4x，本轮完成）】** 焚诀 C31 归因台账记到本仓头上：r19b/r20 两笔把 `A-memory-start/SKILL.md` 推到 29,041B 致其注入区超硬顶 +21B。根因 = 我把整段执行记录写进 SKILL.md 的 `## 版本历史` 区（每轮注入面），而全文在 `references/version_history.md` 本就存在（纯重复计费）。修法 = 长条目换一行摘要 + 本版起「区一行、分卷全文」，实测 **29,041 → 26,593B**；其 C25 余量 220B → **1,583B**、C31 余量 4.0%（其 <5% 告警仍在，剩余面不属本仓可减项）。受管根 `928517a`，V10.70.0，未删规则本体/未改阈值/未碰 description。

- [x] **【r21c 转办状态更新：我那条「注入区合一」已由 owner 以更强形式收口】** 焚诀已自落 `C31 = L1 注入预算归因台账`（基线只能经 `inject_ledger --decision applied` 留痕移动、硬顶封死 65536、applied 须署名给因）⇒ 本仓建议的 C32′ 作废；仍开放两项 = **目录税棘轮**（其 C25/C31 只覆盖 5 文件，全库 name+description 每轮 ~45,250 字符仍无跨仓门禁；本仓已用 `ratchet_gate.py` 的 catalog_grand_chars/inject_union_bytes 两指标自持拦住本仓增长面）与 **C33′ 计数断言内容级门禁**。取值 `python 05-exec/ratchet_gate.py` + `cd 焚诀 && python eval/verify_truth_consistency.py | grep C31`。

- [x] **【r22 已闭环·A-project-handoff 台账行（R273）】** `review` 接入「重复轮次闸门」行（受管根 `aa32f7c`，版本 3.53.0，3 文件零夹带）：只读转述各仓 `memory/sessions/repeat-guard.jsonl`，无台账→静默；层a 8 例 + 层b 真跑 review 命中 1 行 = **10/10 [GATE:stub-pass]**；`mirror/noise/evolution/stub` 复跑见当日记录。**两处自我纠偏**：① 落点由建议原文的 savepoint **改判 cmd_review**（层a 全绿而层b 输出零行才暴露，属既有「验证须含接线层」族又一次实物）；② 共享 skill 不硬编码单仓脚本路径，改为转述各仓台账，避免 A-project-handoff 反向依赖本仓。取值命令：`python D:/global_skills/A-project-handoff/scripts/handoff.py review <项目> | grep 重复轮次闸门`；夹具 `05-exec/r22_repeat_guard_stub.py`。
