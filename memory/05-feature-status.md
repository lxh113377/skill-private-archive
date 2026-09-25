# 05 - 功能状态

> 本文件记录功能/任务的完成状态。
> 归档类型：增量（已完成项归档时移入 archive/）

## ✅ 已完成

- **r37 门禁假阳性治理轮（2026-09-25 第 37 轮）** — 新建第十三维并**用它解除自身阻塞**：`handoff.py noise` 连红 7 轮的 5 条 VIOL 经取证全部为假阳性（3 条 Git 已跟踪治理件 + 2 条 `.git` 内工具运行态日志）。按 R263 改判据不改数据，上游 **A-project-handoff V3.54.1**（`b98cdb5` 代码 + 文档同步）落三件：`git_tracked()` 三重收窄放行 / 二级深扫跳过 `.git` / auto-memory 根件放行面扩到 `reference-*` 且不外溢。验证 = 层a 新桩 `05-exec/r37_noise_tracked_stub.py` **修前红 8 → 修后 16/16**（5 条保牙反例）+ 层b 四根 `[GATE:noise-pass]`（violation 全 0）+ 层c **`savepoint` 首次转绿**（AC-OBS-05 结束 7 轮连红）。配套：证据件 `06-benchmark/noise_falsepositive_r37_2026-09-25.json`（before 取自改动前自动备份原件实跑，非记忆值）+ 契约入册（10 pattern）+ **第 8 道常驻门 `noise_tracked_stub`**（`[GATES:PASS] PASS=8`）+ 立 **X-9**（禁为凑绿迁走/删除/改名 Git 已跟踪根部件）。自纠：首版桩 2 条**假反例**（未跟踪件写在 `git add -A` 之前、误判 `_bak` 可在名中命中——`STRAY_NAME` 实为行尾锚定）由 R220 抽验抓回后重做；`run_gates.py` 去掉硬编码「10 份/8 pattern」陈旧值，改指取值命令（L-5）。

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
