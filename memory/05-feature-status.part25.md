# 05-feature-status.part25.md

<!-- 本卷为 05-feature-status.part24.md 的延续 -->

- **r32 CI 有效性轮（2026-09-25 第 32 轮）** — 把 r31 第八维往深量一层（run 结论分布 + 心跳，非文件数）：13 仓实测发现 **superpowers 82% failure / anthropics 75% failure 且停摆 6 周无人报警 / spec-kit 50% 卡在 action_required** ⇒ 「搬进 CI 就变强」被对手实物推翻；**推翻并改写 r31 自家 M-1**（仓内 tracked `SKILL.md`=0 ⇒ 参数化造不出语料，复制语料=第二真相源+陈旧假绿 ⇒ 改判设计边界，新立禁止项 X-1）；落地**第 6 门 `gate_run_freshness`**（执行台账 `gate_runs.jsonl` + `origin` 分本机/CI + 空台账/纯CI记录/超期/坏ts 四类不判绿）与 `r32_ci_health.py`（只测不拦），门数 5→**6**、可移植 3/5→**4/6**，用法反转为「**用 CI 盯人**」；夹具 18 例含变异 4/4（**自纠两条**：M1 探针样本形态错致"假拦住"、元判据写回台账致自锁，均真机复现后修）。全文见 `06-benchmark/全量对标报告_r32_CI有效性_2026-09-25.md`；证据 `06-benchmark/{ci_health_r32,gate_run_r32,gate_run_r32_portable,freshness_r32}_2026-09-25.json`。
