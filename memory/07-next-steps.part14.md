# 07-next-steps.part14.md

<!-- 本卷为 07-next-steps.part13.md 的延续 -->

## P0 条目历史复核（原样迁入，零改写）

- [x] **【r22 已闭环·A-project-handoff 台账行（R273）】** `review` 接入「重复轮次闸门」行（受管根 `aa32f7c`，版本 3.53.0，3 文件零夹带）：只读转述各仓 `memory/sessions/repeat-guard.jsonl`，无台账→静默；层a 8 例 + 层b 真跑 review 命中 1 行 = **10/10 [GATE:stub-pass]**；`mirror/noise/evolution/stub` 复跑见当日记录。**两处自我纠偏**：① 落点由建议原文的 savepoint **改判 cmd_review**（层a 全绿而层b 输出零行才暴露，属既有「验证须含接线层」族又一次实物）；② 共享 skill 不硬编码单仓脚本路径，改为转述各仓台账，避免 A-project-handoff 反向依赖本仓。取值命令：`python D:/global_skills/A-project-handoff/scripts/handoff.py review <项目> | grep 重复轮次闸门`；夹具 `05-exec/r22_repeat_guard_stub.py`。

- [x] **【H1/H3 已闭环（r29 同轮补做，用户标注驱动）**】 唯一未被 r29 推翻的大缺口 = `rationalizations` 13.9% vs addyosmani 96.0%（差 **82.1pt**，宽窄两口径差值 +0.0 ⇒ 无等价写法可兜底）。落点 = 新建技能模板（`A-skill-manager/SKILL.md` + `references/version-history.md`）**正被并行会话改写**（受管根实测 `M`），按 R269 不抢改；窗口一开即做「验证段 + 反理性化表 + H3 破坏性命令作用域守卫」三处，**只动正文不动 description**（C25 余量 0）。**闭环记录**：用户标注该行后复测发现「落点被占用」是误判 —— 模板真实落点 = `assets/creator/init_skill.py`（骨架生成器）+ `references/lifecycle-create.md`（硬规则卷），当时均干净，不必等壳文件；受管根 `afe0f13` 已落地三段（反理性化表 / 验证含反例 / 破坏性命令作用域守卫）+ `quick_validate.py` 缺段提醒（提醒级不阻断）+ 顺带修 `read_text()` 未指定编码在中文正文下抛 UnicodeDecodeError；冒烟 = py_compile PASS + 真跑生成骨架确含 3 段 + 校验器三侧（通过/提醒/退出码不变）；四门禁 mirror+noise+evolution+stub 全绿、verify 仍只差他人 C20。**教训**：把"某文件在途"当成"整件事被阻塞"前，先查清动作的真实落点文件，占用面往往只是壳。

- [x] **【P0·待办 M-2（挂账 3 轮）→ r38 已执行】** 契约不变式 `set(baseline.metrics) == set(ratchet_gate.METRIC_NAMES)` + 「基线少一项指标必红」夹具 —— 现六项指标靠 `ratchet_gate.py` 单源，`06-benchmark/inject_ratchet_baseline.json` 少键时只报缺文件不报缺项。【r38 执行完毕：契约新增 `inject_ratchet_baseline*.json` pattern + 不变式 `ratchet_metric_set_matches`（集合全等，双向报缺项/僵尸项）+ `ratchet_hardcap_subset`；夹具 t21–t24 实测「删一项必红并点名该指标」，`[GATE:fixture-pass]` 41/41】

- [x] **【P1·待办 H-5（r37 新立，结构性）】** `07-next-steps.md` **摘要与 P0 混排**：实测 `## 最近对话摘要` 只到 r20，而 **r28~r37 共 10 轮摘要全落在 `P0 节 — 必须做` 节内**（本轮插 r37 时按锚点命中才发现）。修法须与拆卷配合：摘要归位摘要节或专属分卷，P0 节只留 `- [ ]` 待办；动前先验 `savepoint` 的「P0 非空」判据（致命纪律 #1）不受影响，**禁止**为凑判据形状删待办。
