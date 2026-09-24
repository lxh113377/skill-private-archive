# 05-feature-status 分卷 16 — 已完成：2026-09-24 第 20 轮 r19 全文

> 由 part15 就地续拆（R224：承接卷超限即续拆，条目正文零改写）。

## r19 主条目（自 05 主壳条目级归档迁入，正文零改写）

- **r19 对标实物层增量轮（2026-09-24，第 20 轮）** — 广度实测无收益（14 对象 35 分钟 +37 星）⇒ 转「读对手源码/Schema/模板」层：据 `drift-detection.py` 的 `SKIP_PREFIXES` 与 `--self-test` 实物，**修掉 r18 四工具的三处判据缺陷**（按设计累积项未排除致 6/16 噪声 37.5%、排除判据过宽误伤人工报告、四工具零夹具），并新建 `05-exec/r19_scan_fixtures.py`（**55/55** 两层夹具含 `--no-exclude` 对照组）。人工复核 P0-C 第 2 批（11 句六态判定：仍然成立 7 / 已失真 7 句 / uncertain 1）暴露**内容级门禁盲区** ⇒ 新建 `05-exec/claim_truth_scan.py`（正文端数/计数/版本断言 == 真相源，首跑 **10 条候选**，含每轮注入的 `A-memory-start` 「五端/V9.7.0」6 句）。P1-C 分母统一登记落地（`_lib.denominator()` 三口径 166/167/167，4 工具接入，注册表不可读 ⇒ `consistent=None` 禁静默）。新判据「流程入描述」（对标 skill-anatomy）实测 24/166。**上游真缺陷当场修**：`flow --add` 首次写 09 会吃掉「字段约定」图例与推进记录段首注释 ⇒ 受管根 `18294ba`（A-project-handoff **V3.52.2**，`_leading_comments()` 回填 + 幂等），隔离桩 **15/15 含修前/修后对照** + 真机端到端 `flow --check` PASS + 三文件白名单零夹带 + `-Fix` 后 mirror/noise/evolution 转绿。**flow 状态机本项目首次真用**（09 任务表此前恒空）：登记 R19-1/R19-2(blocked)/R19-3(todo) 并 `--sync` 回写 07。P2-A 交付 `06-benchmark/comparison.md` 常驻横向页。报告 = `06-benchmark/全量对标报告_r19_2026-09-24.md`。

