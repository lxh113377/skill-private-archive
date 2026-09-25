# 05 - 功能状态

> 本文件记录功能/任务的完成状态。
> 归档类型：增量（已完成项归档时移入 archive/）

## ✅ 已完成

- **r38 债务到期治理轮（2026-09-25 第 38 轮）** — 第十四维「积压债务的可见性与到期治理」：账龄尺 `05-exec/r38_debt_aging.py`（13 卷全扫 / 正文去重 / 四分类之和自校验 / OVERDUE 用 `git log -S` 复核首现）首跑量出 13 条超期无裁决（最老 30 轮）⇒ 逐条取证裁决至 **OVERDUE 0**（12 DECIDED + 1 执行闭环），并把账龄做成 `ratchet_gate` **第 7 指标** `overdue_debt_items`（只降不升、变异对照 OVERDUE=3 必红、不进 `run_gates` 阻断位）；同时清偿挂账 3 轮的 **M-2**（契约 `inject_ratchet_baseline*.json` + 集合全等不变式双向报缺项/僵尸项 + 硬顶无主检查，夹具 t21–t28 → 41/41），契约 12 pattern / 15 受检件，`[RATCHET:PASS] 7 项`、`[GATES:PASS] PASS=8`。立 X-10（不引入到期自动关闭）/ X-11（待办不外迁 tracker）。被自家判据抓两处：自造裁决措辞不在取值域照判红、M-1/M-2 编号与 r31 撞车（改 W- 前缀）。残余 36 条 UNDATED = 判据盲区（W-1）。**✅ 校正注（同日 r38 二刷）：给账龄尺补上「正文裸 rNN 回落」后盲区 36→13，但真实超期敞口随之从 13 跳到 22（原判 UNDATED 的条目里 9 条其实早已超期只是没定年）⇒ 棘轮基线按实况核定 22 而非 0；本轮「OVERDUE 归 0」的说法只对**首版判据**成立，不成立於修正后判据。教训：尺子变准会让债务变多，这时唯一诚实的做法是把基线钉在真值上（R263 禁改数据凑判据的反向形态：禁改判据凑好看）。**

- **r21c 还账轮（2026-09-24 第 21 轮 c 段）** — 本仓欠焚诀 C25/C31 的注入超顶已清偿：`A-memory-start/SKILL.md` 29,041→26,593B（长条目换一行摘要，全文归分卷），其余量 220→1,583B；实测 owner 已自落 C31 归因台账 ⇒ 我「注入区合一」建议作废。受管根 `928517a`/V10.70.0。全文见 `05-feature-status.part19.md`。
- **r20b 棘轮落地轮（第 21 轮 b 段）** — A-get-memory 三条硬判据落地（受管根 `b8966da` V4.30.0，四门禁首次全绿）+ 本仓注入面棘轮 `ratchet_gate.py`（21/21 夹具，两级判定）挂进项目门禁命令。全文见 `05-feature-status.part18.md`。
- **r20 机制化轮（第 21 轮）** — rule_editor 写前脏源检测落地（受管根 `9a15f4e` V10.69.0，桩 10/10）+ 09 状态机首次真用 + comparison 常驻页。全文见 `05-feature-status.part17.md`。
- **r19b 标注驱动续做轮（第 20 轮 b 段）** — 契约族 + 变异对照 + 注入面端数 6 句改口八端（V10.68.0）。全文见 `05-feature-status.part15.md`。
- **r19 对标实物层增量轮（第 20 轮）** — 实物层校准 + 55 例夹具 + claim 对账新工具 + 分母三口径 + 上游 flow 图例缺陷修（V3.52.2）。全文见 `05-feature-status.part16.md`。
- **r18 全量对标增量轮（2026-09-24，第 19 轮）** — 对象 7→14 + 差距 N1~N8 + 4 只读工具落地；全文见 `05-feature-status.part14.md`（本轮条目级归档迁出，正文零改写）。⚠️ **r19 校正注**：该轮四工具当时**零夹具**、drift 扫描含 37.5% 噪声，已由 r19 修正。

## 分卷目录
- **卷1** `05-feature-status.part1.md` — 进行中 / 计划中 / 阻塞
- **卷2** `05-feature-status.part2.md` — 已完成：2026-09-19 第 3 轮（P0-2 收口 + 补建上游 + 注册表重建）
- **卷3** `05-feature-status.part3.md` — 已完成：2026-09-22 第 4 轮（D1–D5 授权项执行结果）
- **卷4** `05-feature-status.part4.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷5** `05-feature-status.part5.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷6** `05-feature-status.part6.md` — 已完成：2026-09-22 第 10 轮（Step 0 首次实跑 + 记忆层回写 + 阶段1 补齐 + B1–B7 授权执行）
- **卷7** `05-feature-status.part7.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷8** `05-feature-status.part8.md` — 已完成：2026-09-23 第 13 轮（性能瓶颈三维实测分析）
- **卷9** `05-feature-status.part9.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷10** `05-feature-status.part10.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷11** `05-feature-status.part11.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷12** `05-feature-status.part12.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷13** `05-feature-status.part13.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷14** `05-feature-status.part14.md` — 已完成：2026-09-24 第 19 轮 r18 全文（条目级归档迁出，防主壳超 4KB）
- **卷15** `05-feature-status.part15.md` — 已完成：2026-09-24 r19b 全文（契约族+变异对照+端数改口）
- **卷16** `05-feature-status.part16.md` — 已完成：2026-09-24 第 20 轮 r19 全文（自 part15 就地续拆）
- **卷17** `05-feature-status.part17.md` — 已完成：2026-09-24 第 21 轮 r20 全文
- **卷18** `05-feature-status.part18.md` — 已完成：2026-09-24 第 21 轮 r20b 全文
- **卷19** `05-feature-status.part19.md` — 已完成：2026-09-24 第 21 轮 r21c 全文
- **卷20** `05-feature-status.part20.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷21** `05-feature-status.part21.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷22** `05-feature-status.part22.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷23** `05-feature-status.part23.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷24** `05-feature-status.part24.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷25** `05-feature-status.part25.md` — 05-feature-status 分卷（R199 自动拆卷）
- **卷26** `05-feature-status.part26.md` — 05-feature-status 分卷（R199 自动拆卷）

