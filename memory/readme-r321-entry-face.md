# readme-r321-entry-face — README「r321 增补」节正文（自 README 零改写迁出）

> 迁出动因 = `root_doc_max` 16,384B（R161 体量治理）；本卷为原节全文，README 只留指针。
> 迁出前 README = 23004B（我已把原 README 的 20568B 又加了 2436B ⇒ 当场自抓，按 r175 先例整段外迁，非删除）。

### r321 增补 · 入口可达性维 + 解释器路径校正（读数 2026-10-31T22:1x+08:00）

> 动因：r320 普查量到此前 15 维全未覆盖的缺陷类「**落盘未入口**」，而本入口件当时也没挂上那批新交付件
> —— 本仓自己就是该缺陷的样本。按 R241 不改写上方 10-28 表行，只增补。

| 需求 | r321 句柄 | 取值（末行即验收） |
|---|---|---|
| 1 盘点（新增入口可达维） | [`_repro/r320a/entry_census/`](_repro/r320a/entry_census/) 三件（判据/读数/报告） | `python -B _repro/r320a/entry_census/check_r319a.py` ⇒ `[R319A:ENTRY] court=pass … orphans=624 orphan_kb=4781` |
| 3 矩阵（断链轴真伪二分） | [`_repro/r321b/broken_verify.json`](_repro/r321b/broken_verify.json) | `python -B _repro/r321b/check_r321b.py` ⇒ `[R321B:BROKEN] real=1 placeholder=9 teeth=pass` ⇒ 普查报的 10 条断链**只有 1 条是真的** |
| 4 迁移方案（入口补链分批） | [`04-plan/入口补链批次表_r321_2026-10-31.md`](04-plan/入口补链批次表_r321_2026-10-31.md) | `python -B _repro/r321_lead_triage/check_r321.py` ⇒ `[R321:BATCH] batches=6 files=552 kb=4447 coverage=ok`（判据从普查 JSON 现算再比对表内抄录值，抄错即红） |
| 5 季度巡检 | [`04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md`](04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md) 的「附二 · r321 巡检面补记」 | 孤儿噪声白名单 72 件不该补链；293/552 已被目录名覆盖 ⇒ 处方是取用规则不是逐条挂链 |
| 6 质量 ≥30% | [`_repro/r320a/PROBE_WEAK_LEDGER.md`](_repro/r320a/PROBE_WEAK_LEDGER.md) | 终态三件套之「不可达证据」：路①弱执行体运行时坏、路②盲测集 63.6% 泄漏债 |

**解释器校正**（r321 实测）：上方「收口门禁」代码块两处写的 `C:\Program Files\Python312\python.exe` 本机已不存在（`spawn ENOENT`）。现用 `C:\Users\37533\.workbuddy\binaries\python\envs\default\Scripts\python.exe`（3.13.14），备用 `D:\LibreOffice\program\python.exe`（3.13.15）。本轮用前者实跑 `rule_editor.py gates` = `mirror=pass noise=fail evolution=fail stub=fail`，三红均在归属方侧既存面（`D:\global_memory` 23 项散落 + C29 评分产物与 STATUS 脱节），非本会话写面；留证 [`_repro/r321_lead_triage/rule_editor_gates.txt`](_repro/r321_lead_triage/rule_editor_gates.txt)。

