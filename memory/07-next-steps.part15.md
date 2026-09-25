# 07-next-steps.part15.md

<!-- 本卷为 07-next-steps.part14.md 的延续 -->

## P0 条目历史复核（原样迁入，零改写）

- [x] **【P0·待办 M-2（挂账 3 轮）→ r38 已执行】** 契约不变式 `set(baseline.metrics) == set(ratchet_gate.METRIC_NAMES)` + 「基线少一项指标必红」夹具 —— 现六项指标靠 `ratchet_gate.py` 单源，`06-benchmark/inject_ratchet_baseline.json` 少键时只报缺文件不报缺项。【r38 执行完毕：契约新增 `inject_ratchet_baseline*.json` pattern + 不变式 `ratchet_metric_set_matches`（集合全等，双向报缺项/僵尸项）+ `ratchet_hardcap_subset`；夹具 t21–t24 实测「删一项必红并点名该指标」，`[GATE:fixture-pass]` 41/41】

- [x] **【P1·待办 H-5（r37 新立，结构性）】** `07-next-steps.md` **摘要与 P0 混排**：实测 `## 最近对话摘要` 只到 r20，而 **r28~r37 共 10 轮摘要全落在 `P0 节 — 必须做` 节内**（本轮插 r37 时按锚点命中才发现）。修法须与拆卷配合：摘要归位摘要节或专属分卷，P0 节只留 `- [ ]` 待办；动前先验 `savepoint` 的「P0 非空」判据（致命纪律 #1）不受影响，**禁止**为凑判据形状删待办。

- [x] **【P0·下轮首推 W-12（r43 新立，优先级最高）】** 裁决清单完整性判据：本轮实际裁决条数必须 >= 上一轮 OVERDUE 条数（缺口即红）。存在理由：r41 只裁「当期到期清单」漏裁「账龄新越线清单」，r42 账面从 1 炸到 20；而 r43 写入阶段又有 5 条报出的行号已失效 —— 完整性没有机器约束，就只会靠我记得。复现取值：`python 05-exec/r38_debt_aging.py --json /tmp/a.json` 两轮对比 overdue[].title 集合差。

- [x] **【P0·下轮首推 W-4（r39 新立，优先级最高）】** 给 **DEFERRED** 立棘轮第 8 指标 `deferred_debt_items`（只降不升）：本轮 W-0 把 22 条超期压到 0，但同一动作让 DEFERRED 从 9 涨到 **23** —— 若延期堆没有独立回归保护，r38 的账龄判据就退化成"换个地方堆债"。取值面 `06-benchmark/debt_aging_r3*.json` 的 `by_class.DEFERRED`，须与 overdue 一样做「脏证据 ⇒ None」的 fail-closed。 【r44 裁决=执行完毕｜棘轮第 8 指标 deferred_debt_items 已于 r40 落地（与 overdue 共用 _debt_class_state、同等 fail-closed），本轮 ratchet 实跑输出该指标实测=1 基线=23；取值 python 05-exec/ratchet_gate.py】

- [x] **【P1·待办 W-3（r38）】** 账龄趋势落台账：仿 `gate_runs.jsonl` 建 `06-benchmark/debt_runs.jsonl`（ts/overdue/undated/open_total），使 CI 与棘轮能看到**斜率**而非只看到当期值；契约须带取值域（R247 空面判红）。 【r44 裁决=执行完毕｜趋势台账已建并稳定追加：06-benchmark/debt_runs.jsonl 现 21 行，契约带行级取值域（origin 仅 local/ci、五态之和自洽），注册为第 9 道常驻门；取值 wc -l 06-benchmark/debt_runs.jsonl】
