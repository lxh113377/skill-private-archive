# 05-feature-status.part23.md

<!-- 本卷为 05-feature-status.part22.md 的延续 -->

- **r30 反理性化首批轮（2026-09-25 第 30 轮）** — 四档稳健性工具段参数化（`05-exec/r30_section_robustness.py`）→ **rationalizations 严格同义零假阴性（档1=档2=13.9%，与 verification 的 29.2% 相反）但档2b=71.1%** ⇒ 定性为"缺的是借口→反驳这一形式，不是负面指引本身"；真队列取最保守口径 14 条，首批 5 条逐技能写特有失败形态落表（`story-scan`/`video-breakdown-skill`/`local-vram`/`code-review`/`utf8-encoding-fix`，受管根 `359d0fc` 50 行纯新增零夹带），复测档1 23→28、档3 55→60。维护状态维度首次实测化（4 仓 stars/pushed/issues，**issue 存量与星标同向**⇒高星标≠高维护度）并入常驻页。全文见 `06-benchmark/全量对标报告_r30_四档稳健性与反理性化首批_2026-09-25.md`。
