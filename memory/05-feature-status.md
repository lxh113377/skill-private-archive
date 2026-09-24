# 05 - 功能状态

> 本文件记录功能/任务的完成状态。
> 归档类型：增量（已完成项归档时移入 archive/）

## ✅ 已完成

- **r19 对标实物层增量轮（2026-09-24，第 20 轮）** — 广度实测无收益（14 对象 35 分钟 +37 星）⇒ 转「读对手源码/Schema/模板」层：据 `drift-detection.py` 的 `SKIP_PREFIXES` 与 `--self-test` 实物，**修掉 r18 四工具的三处判据缺陷**（按设计累积项未排除致 6/16 噪声 37.5%、排除判据过宽误伤人工报告、四工具零夹具），并新建 `05-exec/r19_scan_fixtures.py`（**55/55** 两层夹具含 `--no-exclude` 对照组）。人工复核 P0-C 第 2 批（11 句六态判定：仍然成立 7 / 已失真 7 句 / uncertain 1）暴露**内容级门禁盲区** ⇒ 新建 `05-exec/claim_truth_scan.py`（正文端数/计数/版本断言 == 真相源，首跑 **10 条候选**，含每轮注入的 `A-memory-start` 「五端/V9.7.0」6 句）。P1-C 分母统一登记落地（`_lib.denominator()` 三口径 166/167/167，4 工具接入，注册表不可读 ⇒ `consistent=None` 禁静默）。新判据「流程入描述」（对标 skill-anatomy）实测 24/166。**上游真缺陷当场修**：`flow --add` 首次写 09 会吃掉「字段约定」图例与推进记录段首注释 ⇒ 受管根 `18294ba`（A-project-handoff **V3.52.2**，`_leading_comments()` 回填 + 幂等），隔离桩 **15/15 含修前/修后对照** + 真机端到端 `flow --check` PASS + 三文件白名单零夹带 + `-Fix` 后 mirror/noise/evolution 转绿。**flow 状态机本项目首次真用**（09 任务表此前恒空）：登记 R19-1/R19-2(blocked)/R19-3(todo) 并 `--sync` 回写 07。P2-A 交付 `06-benchmark/comparison.md` 常驻横向页。报告 = `06-benchmark/全量对标报告_r19_2026-09-24.md`。
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

