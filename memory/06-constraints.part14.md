# 06-constraints.part14 -- 纪律条目正文归档（#30-#48，r154 从 AGENTS.md 迁入，原文零改写）

## ⚠️ 处方须声明适用边界（#46，2026-10-21 立规）

#31（处方必先实测）管「有没有实测」，管不到**实测了几个靶**。

**r148 一手实证**：r135 为第 11 类（语料语言不匹配）开的处方「frontmatter 补中文触发词」，
当时在 gsap 一个靶上实测有效（margin −0.0586→+0.0216）。r148 把同一处方套到面上
其余 2 对语言不一致（`r135_lang_boost_efficacy.py` 换 `--slug/--rival/--query` 逐对现算）：

| 靶对 | 基线 margin | 处方② | 处方③ |
|---|---|---|---|
| gsap vs libreoffice-draw | −0.0586 | **+0.0216 ✅** | +0.1827 ✅ |
| github vs code-review | −0.1476 | **−0.1725（更差）** | −0.2780（更差） |
| video-whisper-transcribe vs local-asr | −0.0965 | **−0.1084（更差）** | −0.2364（更差） |

⇒ **单靶实测有效 ≠ 适用面有效**（本轮 1/3）。且后两对的失败形态不同源：
`local-asr` 抢赢 `video-whisper-transcribe` 是**近邻语义竞争**（r135 自抓的 `B_NEIGHBOR_RANK` 类），
`github`/`code-review` 是**期望归属本身存疑**（query 真实职责更近 code-review）——
「语言不匹配」这个标签盖住了三种不同根因，一刀切补中文必然对 2/3 无效甚至有害。

**机器判据**：任何处方推广到第 2 个及以后的靶前，必须**逐靶跑效力面复测**，且提案须带
`适用边界` 字段写明「对哪种失败形态测过、在哪类形态上无效」；
无边界声明的处方**不得跨靶执行**（`r136_proposal_evidence.py` 读 `face.boundary_missing_n`，须为 0）。

**关联处置（r148）**：github/vwt 两对**未照搬执行**（#34 纪律自用），改立观察项
`06-benchmark/neighbor_rank_r148_2026-10-21.json`（由 `r133_new_skill_ingress.py` 的 lang_mismatch 明细承接）；
第 11 类提案 `corpus_lang_mismatch` 已补 `r148_execution` + 三段式 `acceptance_r148`（gsap 对源侧已达标，
生产翻绿待归属方重建 BGE 派生件——派生件 mtime 21:24 早于修复 23:19，本仓 eval 只读不代跑，R269）。
