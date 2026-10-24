# 06-constraints.part17 —— 从根壳 AGENTS.md 下沉的原文（r216 / 对标改造 M-2）

> 动因：注入面 `inject_union_bytes` 超 C25 硬顶，而本仓根 `AGENTS.md` 是该面里**唯一本仓可动的成员**
> （另四件属受管根 / 共享权威 / 他端在途，清单见 `truth_constants.inject_budget.files`，本仓不擅动）。
> 本卷只收**已在 memory 有正本的手抄值、已失效的死指针、已机械化的长说明** —— 即本壳自身违反
> R161「壳不含第二真相源」的那部分存量。红线摘要、启动顺序、口径裁定、已知坑另两条一律留壳内
> （它们是每轮决策输入，迁走 = 把判据挪出视野，比超顶更坏）。
> 迁出原文一字未改（R241）；字节守恒由 V2 还原校验证明；壳内对应位置已留指针。
> 取值（现读勿抄）：`python 05-exec/ratchet_gate.py` 的 inject_union_bytes 行；
> `git log --oneline -3 -- AGENTS.md`；`Get-ChildItem memory -Filter 06-constraints.part*.md`。
## 头部注（死指针 + 手抄降级史）

> 自动生成: 2026-10-16 17:20 | 由 r109 I-7「实减」把全量快照降级为索引壳（原 29,293B > 注入预算）。
> **本节只放路由与红线；正文权威源在 `memory/`，本壳不含第二真相源。**
> 备份与回滚：`05-exec/mark_backup/AGENTS.md.r109_before_index_shell`（git 亦可回滚，AGENTS.md 已跟踪）。
## 门禁与取值命令节（正本已在 memory/AGENTS.md）

## 门禁与取值命令（常驻，禁凭记忆下结论）

```
python 05-exec/run_gates.py --json 06-benchmark/<新件>.json     # 本仓 29 门聚合
python 05-exec/ratchet_gate.py                                  # 注入面/度量六+三项只降不升
python 05-exec/r52_md_claim_face_scan.py --json <件>            # 报告数字须挂取值命令
python 05-exec/r38_debt_aging.py --json <件> --ledger 06-benchmark/debt_runs.jsonl
python D:/global_skills/A-memory-start/references/rule_editor.py gates
python D:/global_skills/A-skill-manager/assets/disk_registry_diff.py
python D:/global_skills/A-project-handoff/scripts/handoff.py volume <本项目>
```
## 纪律条目归档节

## 纪律条目正文已归档至 memory 分卷（r154，R150-7）

> r154 归档（R150-7 落地）：下列纪律条目的**正文权威源**已迁 `memory/06-constraints.part6.md` .. `.part16.md`（原文零改写，R241）。
> 本壳仅留指针 —— 回到 R161 的原设计「本节只放路由与红线；本壳不含第二真相源」。
> 条目清单：#30..#48（含 #31 全自动完成 / #32 判据面 / #33 结论层 / #35 阻断点 / #45 写入顺序 / #47 转办复算面 / #48 want⇄got …）。
> ⛔ 新增纪律条目**先落 memory 分卷**，壳内只加指针（防本缺陷复发）。
## 已知坑第二条（长说明，正本在 part84）

- **写记忆卷之后必须重算账龄件**，否则「相对新鲜前置」把三门再次染红。⚠️ **本条已连踩 3 轮（r119/r121/r122）**：症状 = 棘轮报「overdue/deferred/repeat 指标缺失」+ `r55_note_fixtures` 的 n4 腿必现 FAIL（3/3 复现）。正确顺序 = **先改 07 台账 → 后跑 `r38_debt_aging.py`**；已踩后补救 = 原样重跑一次 `r38_debt_aging.py`（件 mtime 即新于卷集），ratchet / note fixtures / 同号多副本面三项随之转绿。
## 分卷目录 05 手抄 part 号

| 05 功能状态 | `memory/05-feature-status.md`（+ part1…part29） | 已完成/进行中/阻塞 |
## 分卷目录 06 手抄 part 号

| 06 已知约束 | `memory/06-constraints.md`（+ part1…part16；part6–16 = #30–#48 纪律正文，r154 从本壳归档） | 已知 Bug / 技术债 / 红线全文 |
## 分卷目录 07 手抄 part 号

| 07 下一步 | `memory/07-next-steps.md`（+ part1…part57） | **P0 真相源** |
