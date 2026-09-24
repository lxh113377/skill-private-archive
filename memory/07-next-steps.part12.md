# 07-next-steps.part12.md

<!-- 本卷为 07-next-steps.part11.md 的延续 -->

## P0 条目历史复核（原样迁入，零改写）

- [x] **【r21c 还账（2026-09-24 21:4x，本轮完成）】** 焚诀 C31 归因台账记到本仓头上：r19b/r20 两笔把 `A-memory-start/SKILL.md` 推到 29,041B 致其注入区超硬顶 +21B。根因 = 我把整段执行记录写进 SKILL.md 的 `## 版本历史` 区（每轮注入面），而全文在 `references/version_history.md` 本就存在（纯重复计费）。修法 = 长条目换一行摘要 + 本版起「区一行、分卷全文」，实测 **29,041 → 26,593B**；其 C25 余量 220B → **1,583B**、C31 余量 4.0%（其 <5% 告警仍在，剩余面不属本仓可减项）。受管根 `928517a`，V10.70.0，未删规则本体/未改阈值/未碰 description。

- [x] **【r21c 转办状态更新：我那条「注入区合一」已由 owner 以更强形式收口】** 焚诀已自落 `C31 = L1 注入预算归因台账`（基线只能经 `inject_ledger --decision applied` 留痕移动、硬顶封死 65536、applied 须署名给因）⇒ 本仓建议的 C32′ 作废；仍开放两项 = **目录税棘轮**（其 C25/C31 只覆盖 5 文件，全库 name+description 每轮 ~45,250 字符仍无跨仓门禁；本仓已用 `ratchet_gate.py` 的 catalog_grand_chars/inject_union_bytes 两指标自持拦住本仓增长面）与 **C33′ 计数断言内容级门禁**。取值 `python 05-exec/ratchet_gate.py` + `cd 焚诀 && python eval/verify_truth_consistency.py | grep C31`。

- [x] **【r22 已闭环·A-project-handoff 台账行（R273）】** `review` 接入「重复轮次闸门」行（受管根 `aa32f7c`，版本 3.53.0，3 文件零夹带）：只读转述各仓 `memory/sessions/repeat-guard.jsonl`，无台账→静默；层a 8 例 + 层b 真跑 review 命中 1 行 = **10/10 [GATE:stub-pass]**；`mirror/noise/evolution/stub` 复跑见当日记录。**两处自我纠偏**：① 落点由建议原文的 savepoint **改判 cmd_review**（层a 全绿而层b 输出零行才暴露，属既有「验证须含接线层」族又一次实物）；② 共享 skill 不硬编码单仓脚本路径，改为转述各仓台账，避免 A-project-handoff 反向依赖本仓。取值命令：`python D:/global_skills/A-project-handoff/scripts/handoff.py review <项目> | grep 重复轮次闸门`；夹具 `05-exec/r22_repeat_guard_stub.py`。

- [x] **【H1/H3 已闭环（r29 同轮补做，用户标注驱动）**】 唯一未被 r29 推翻的大缺口 = `rationalizations` 13.9% vs addyosmani 96.0%（差 **82.1pt**，宽窄两口径差值 +0.0 ⇒ 无等价写法可兜底）。落点 = 新建技能模板（`A-skill-manager/SKILL.md` + `references/version-history.md`）**正被并行会话改写**（受管根实测 `M`），按 R269 不抢改；窗口一开即做「验证段 + 反理性化表 + H3 破坏性命令作用域守卫」三处，**只动正文不动 description**（C25 余量 0）。**闭环记录**：用户标注该行后复测发现「落点被占用」是误判 —— 模板真实落点 = `assets/creator/init_skill.py`（骨架生成器）+ `references/lifecycle-create.md`（硬规则卷），当时均干净，不必等壳文件；受管根 `afe0f13` 已落地三段（反理性化表 / 验证含反例 / 破坏性命令作用域守卫）+ `quick_validate.py` 缺段提醒（提醒级不阻断）+ 顺带修 `read_text()` 未指定编码在中文正文下抛 UnicodeDecodeError；冒烟 = py_compile PASS + 真跑生成骨架确含 3 段 + 校验器三侧（通过/提醒/退出码不变）；四门禁 mirror+noise+evolution+stub 全绿、verify 仍只差他人 C20。**教训**：把"某文件在途"当成"整件事被阻塞"前，先查清动作的真实落点文件，占用面往往只是壳。
