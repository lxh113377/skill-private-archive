# -*- coding: utf-8 -*-
r"""r21c_footer_append.py — r21c 轮次 GM 日志段 + 数据流假设 + footer 锚点块（幂等）。

来源: 本轮实测（`wc -c D:\global_skills\A-memory-start\SKILL.md`=26,593B、受管根 `928517a`、
      焚诀 `verify_truth_consistency.py` 31PASS/0FAIL + C25 62,889B 余量 0 + C31 余量 2,647、
      `ratchet_gate.py` 86,346 [RATCHET:PASS]、`gates` mirror=fail、`check-skill-mirror.ps1` 三条 mismatch
      与 `git -C D:\global_skills status --porcelain` 28 条脏项逐条对照）。
流向: 本脚本 → `D:\global_memory\memory\2026-09-24.md`（append-only）→ `upgrade_footer_gate.py`。
结构: UTF-8 无 BOM；footer = begin + [skill清单] 1 行 + [升级建议] 2 行 + end；含 session 标记则跳过。
异常: 写后读回八项锚点（R213），缺任一 exit 1；「改法」字段实测均 ≤40 字（r20 曾因 41 字被拦）。
"""

import io
import os
import sys

LOG = r"D:\global_memory\memory\2026-09-24.md"
KEY = "session=qd-zijian-r21c-0924"

BLOCK = """
## 22:0x 自建skill优化 r21c（第四次标注驱动·先复测阻塞理由，再动自己能动的那半）
- 复测上一条「未闭环」的阻塞理由：归属方（焚诀）**已自落 C31 注入预算归因台账** —— 实测 `verify_truth_consistency.py` = **31 PASS / 0 FAIL / 0 SKIP**，`C31 台账 6 条（applied=3/pending=2）`。⇒ 我方 r20b 交付的「让号 C31′/C32′/C33′ + 接线指南」转办件**已过期**，本轮明确不再外推该方案（推过期件 = 让归属方做无用功），改做两件实事。
- 第一件：读台账发现**归属方把我方 r19b/r20 的注入面增量记在了我方账上**（C25 `余量 0` 是真拦路项，非「口径不合」）。按 R263 不改判据、只降实测值：用 `rule_editor replace` 把 `A-memory-start/SKILL.md` 主文件「版本历史」区两条长条目换成一行摘要（长记录唯一载体 = `references/version_history.md`），**未删规则本体、未改阈值、未碰 description（故不触派生件重建）** ⇒ 长条目换摘要一步实测 **27,956 → 26,315B（−1,641B）**，同轮补写版本行与版本历史条目 **+278B**，净回吐 **1,363B**（现值 **26,593B**，受管根 `928517a`，V10.69.0→**V10.70.0**；提交信息里的「回吐 1,641B」是换摘要那一步的单边值，非全轮净值的口径，本轮按 `git cat-file -s` 逐 rev 实测更正）；复跑 verify：**C25 注入区 62,889B / 基线 62,889B（余量 0）/ 硬顶 65,536**、**C31 余量 2,647（4.0%）⚠ 余量 <5%**、**C13 ✅**（区首条仍含最新版本号，防回滚判据未破）。
- 第二件：把我方自己的常驻告警收口成机器口径 —— `ratchet_gate.py --update` 允许下调 ⇒ `inject_union_bytes` 基线 **89,014 → 86,346**，`[RATCHET:PASS]` 五项全在棘轮内，仅剩 1 条非阻断告警（超 C25 硬顶 +20,810，属跨项目既有事实，消警路径留在 07 不销）。
- 门禁现状如实登记：`mirror=fail noise=pass evolution=pass stub=pass`。`check-skill-mirror.ps1` 三条 mismatch（`A-project-handoff/scripts/handoff_lib/savepoint.py`、`ican-frontend-design-system/SKILL.md`、`ican-frontend-design-system/references/delivery-chain.md`）**逐条对上了受管根 28 条脏项里的 `M` 在途文件** ⇒ 全属他人在途，按 R269 **只登记不 `-Fix`**（`-Fix` 会把别人未提交的源内容刷进镜像）。其中 `savepoint.py` 在途 diff 读作「r22 重复轮次闸门行 `_repeat_guard_row`」，与当日 r22 台账同族、归其归属会话收口。
- 记忆健康：`05-feature-status.md` 两次破 4KB（**4,334 → 4,230 → 3,775B**），改法 = 四条已完成项压成指针 + 全文迁 `part19`（零删除、原文照搬）。教训同族再现：登记句越写越长必然撞硬顶，**主卷只承载指针**才是可持续形态。

【数据流假设】
来源: `wc -c D:\\global_skills\\A-memory-start\\SKILL.md`（实测 26,593B，不抄提交信息）+ `焚诀/eval/verify_truth_consistency.py` 现跑输出（C13/C25/C29/C31 四行原文）+ `05-exec/ratchet_gate.py` 现算五指标 + `check-skill-mirror.ps1`（只读，无 `-Fix`）+ `git -C D:\\global_skills status --porcelain` 28 条逐条比对 + `rule_editor` 写入链台账 `write_chain.jsonl`
流向: 复测结论（转办件过期）→ 只改自己能改的 `A-memory-start/SKILL.md`（`rule_editor replace --dry-run` 命中数=2 才写，patch 由 `r21c_shrink_skillmd_patchgen.py` 从**文件自身行**生成并带 `[GUARD] 命中 != 2 ⇒ 停手`）→ 受管根单文件 commit `928517a` → 焚诀 verify 复跑（C25/C31 余量变化即本轮收益证据）→ 本仓 `ratchet_gate.py --update` 下调基线 → `06-benchmark/inject_ratchet_baseline.json` → 07/05/part19 登记 → 本日志块
结构: 全 UTF-8 无 BOM；记忆主卷硬上限 4096B（05 现值 3,775B 合规）；patch JSON 用 `old_file/new_file` 逐字段原文，长记录载体唯一化（SKILL.md 一行摘要 / version_history.md 全文）；footer [升级建议] 2 行（≤ N+1，N=1），「改法」字段 13/14 字符均 ≤40
异常: 写前脏源检测本轮 0 命中（受管根 A-memory-start 两文件 `git status` 干净）；编号预检 fail-closed 命中 1 次（提交信息含 R 号被拦，按无逃逸口径改写为散文而非加豁免）；`--update` 遇现状高于基线会拒绝写入（本轮方向为下调故放行）；指标算不出 → `unknown[]` + exit 1，禁填 0 冒充；mirror=fail 不代为消红（R269 优先于 R270，四门禁绿不是本仓单方义务）

<!-- footer:begin session=qd-zijian-r21c-0924 ts=2026-09-24T22:10:00+08:00 -->
[skill清单] 本轮调用=2 个 (A-memory-start, A-project-handoff)
[升级建议] skill=A-memory-start | 五问=低效流程 | 改法=主文件版本历史只留一行摘要 | 对照=已取(证据=逐 rev git cat-file 实测 27956→26593B 净回吐 1363B，C25 余量 0 与 C31 余量 2647 复跑通过，规则本体零删) | 状态=已闭环(证据=D:\\global_skills\\A-memory-start\\SKILL.md#版本行:V10.70.0)
[升级建议] skill=fenjue-verify | 五问=过期指令 | 改法=转办前先复测归属方是否已自落 | 对照=已取(证据=实测其已自落 C31 台账 6 条，我方 r20b 让号件过期，改为自己还注入面欠账) | 状态=已闭环(证据=C:\\Users\\37533\\Desktop\\workspace\\自建skill优化\\06-benchmark\\inject_ratchet_baseline.json#backup:A-memory-start.SKILL.md.20260924_214500_246348.bak)
<!-- footer:end -->
"""

NEED = ["【数据流假设】", "来源:", "流向:", "结构:", "异常:", "[skill清单]", "[升级建议]", KEY]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    log = io.open(LOG, encoding="utf-8-sig").read()
    if KEY in log:
        print("[SKIP] r21c footer 已存在（幂等）")
        return 0
    with open(LOG, "wb") as f:
        f.write((log.rstrip("\n") + "\n" + BLOCK).encode("utf-8"))
    back = io.open(LOG, encoding="utf-8-sig").read()
    miss = [k for k in NEED if k not in back]
    print("[GM日志] 读回验证=%s | 缺失=%s | 文件=%dB" % (not miss, miss or "-", os.path.getsize(LOG)))
    return 1 if miss else 0


if __name__ == "__main__":
    raise SystemExit(main())
