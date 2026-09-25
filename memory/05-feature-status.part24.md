# 05-feature-status.part24.md

<!-- 本卷为 05-feature-status.part23.md 的延续 -->

- **r31 第八维 + 队列清零轮（2026-09-25 第 31 轮）** — 新增对标维度「**自动化验收面**」并把它变成落地动作：① 15 对象 × `.github/workflows/*.yml` 实数采集（112 个，ρ(stars,wf)=**−0.114**；superpowers/anthropics 各 **0**），推翻常驻页落后项 #6「N-A 三层 eval 在 CI」（实物 = 1 个安装测试件）；② **H-1** 反理性化第二批 8 条（受管根 `93107ca`，98 行纯新增零夹带；档1 16.9%→**21.7%**、真队列 **9→1**）；③ **H-2** `05-exec/run_gates.py` 门禁单一真相源 + 不短路 + `UNVERIFIED` 三态 + 覆盖根自证 + 自家首个耗时基线（**5 门 1,781 ms / 3 门 561 ms**），夹具 17 例含变异 4/4；④ **H-3** 解除 `CONTRACT:FAIL`，根因改判为「一个 glob 挂一个 schema 字面量」的形状缺陷 ⇒ 契约改**逐代枚举授权** `[v1,v2]`（未登记 v3 仍拦），夹具 18→**22**；⑤ **H-4** `.github/workflows/gates.yml`（日 cron 心跳 + PR-only 取消并发）。实测敞口 **D3**：本仓门禁可离机复现性仅 **3/5**，2 门绑死本机绝对根（原因写死在 runner `not_portable_reason`）。全文见 `06-benchmark/全量对标报告_r31_自动化验收面_2026-09-25.md`；证据 `06-benchmark/{ci_surface_r31_2026-09-25.json,ci_evidence/,gate_run_r31_2026-09-25.json,r31_section_robustness_after_2026-09-25.json}`。
