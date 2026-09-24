# -*- coding: utf-8 -*-
r"""r20b_footer_append.py — r20b 轮次 GM 日志段 + 数据流假设 + footer 锚点块（幂等）。

来源: 本轮实测（受管根 `b8966da` A-get-memory V4.30.0、`git -C D:/global_skills status` 该文件 0 条在途、
      `05-exec/r20b_ratchet_fixtures.py` 21/21、`ratchet_gate.py` 真跑 87,878B 超硬顶、
      trim-shell 后 07 主卷 47,089→45,470B、四门禁首次全绿）。
流向: 本脚本 → `D:\global_memory\memory\2026-09-24.md`（append-only）→ `upgrade_footer_gate.py`。
结构: UTF-8 无 BOM；footer = begin + [skill清单] 1 行 + [升级建议] ≤ N+1 行 + end；含 session 标记则跳过。
异常: 写后读回八项锚点（R213），缺任一 exit 1；「改法」字段须 ≤40 字（本轮上一条即被门禁拦过，见 r20 段）。
"""

import io
import os
import sys

LOG = r"D:\global_memory\memory\2026-09-24.md"
KEY = "session=qd-zijian-r20b-0924"

BLOCK = """
## 21:4x 自建skill优化 r20b（第三次标注驱动·把「转办」变成自己能动 + 自己能动的那半）
- 复测两条未闭环项的阻塞理由是否仍成立：`A-get-memory/SKILL.md` **已归还**（该文件在受管根 0 条在途）⇒ 立刻用 `rule_editor` 落地「判据类工具交付三条硬判据」（① 夹具先写先看红 ② 变异/反例对照 ③ 挂执行路径），dry-run 3/3 命中 + 写后读回 + 版本线 4.29.0→**4.30.0**（受管根 `b8966da`）⇒ 镜像 `-Fix` 后 **mirror/noise/evolution/stub 四门禁首次全绿**。
- 焚诀 `eval/` 那条红线**维持不破**（且其 27 条在途，代改必被我刚落地的「写前脏源检测」拦下），但把「转办」做成两件实事：① **二次让号**——实测其 `205ed81` 已自落 `C30 = 路由静态表目标存活与空洞棘轮`（C29 亦已被占），故三项改号 **C31′/C32′/C33′**，转办件升级为可接线指南 `05-exec/r20b_fenjue_wiring/README.md`（给注册表锚点、`_check_fn` 显式关键字传参教训、stub 登记与对照组要求、验收三命令；不复制未经其运行时验证的代码）；② **能自己动的部分自己动**——新建 `05-exec/ratchet_gate.py`：五项指标只降不升棘轮（catalog_grand_chars / inject_union_bytes / claim_candidates / drift_ruleish_candidates / desc_over_cap）+ `--update` 拒绝抬基线，已并入 `memory/AGENTS.md` 项目门禁命令第 4 条。
- 棘轮首跑即抓到两条真信号：① 注入区并集实测 **87,878B > C25 硬顶 65,536B（+22,342）而 C25 判 PASS**——r18 报的 69,494B 偏低，根因是 `inject_budget.files.bytes` 为登记值、滞后于盘上真值，本判据刻意改为**实测磁盘字节 ∪ 本项目注入壳**去重求和；② `catalog_grand_chars` 45,250（较 r18 +77，来自今日他端新增技能）⇒ 无棘轮即线性恶化。判定分两级（超棘轮/无基线阻断，超硬顶默认非阻断、`--strict-cap` 升阻断），理由：拿跨项目既有事实拦本仓每条修改任务只会逼下一个人放宽判据；常驻告警与消警路径已留账 07 P0 不销。
- 台账卫生：4 条早已带「✅ 收口注（销账/已补建/已收口）」却仍写 `- [ ]` 的 r7 旧项翻 `- [x]` ⇒ `trim-shell` 立即迁出，07 主卷 **47,089B → 45,470B**。这正是 P-1 铁律点名的形态（`status`/`review` 分数不校验主卷与分卷交叉一致，100% 分仍挂着已闭环项）。同时实测 `handoff.py handoff .` **保护索引壳不覆盖**，故每轮注入的 AGENTS.md 体积不随 07 缩小（29,293B 原样），进一步减重须人工精简 07 分卷目录行——不为变绿删规则本体。
- 验证：`05-exec/r20b_ratchet_fixtures.py` **21/21**（层 a 7 + 层 b 14，含「+1 字符即拦 / 收紧允许 / 抬高拒绝 / --strict-cap 升级 / 算不出即失败 / 基线缺失不放行」）；回归 `r19_scan_fixtures` 55/55、`r19_baseline_contract_fixtures` 18/18、`r20_dirty_source_stub` 10/10、`baseline_contract_scan` 9 份全合规。两处自我纠正记档：夹具 m4/m17 两条断言我一开始写反（把「基线偏高」当成应拒绝、「以现状为基线」当成应 exit 0），按 R263 改判据表达而非改数据；`--update` 语义为「只降不升」，实现正确、测试错。

【数据流假设】
来源: `05-exec/claim_truth_scan.py`/`catalog_attention_tax.py`/`cumulative_drift_scan.py`/`description_baseline_scan.py` 的落盘 JSON（现算，不抄历史）+ `焚诀/eval/truth_constants.json` inject_budget（登记 baseline_bytes=64472 / hard_cap=65536 / files 清单，实测磁盘求和另算）+ 本项目 `AGENTS.md`(29293B 实测) + 受管根 `A-get-memory/SKILL.md` 行原文（锚点先 grep 取字节精确文本，命中数=1 才写）
流向: 三处上游 JSON → `ratchet_gate.py:collect_metrics()` 现算 → `06-benchmark/inject_ratchet_baseline.json`（棘轮基线，--update 只允许下调）→ stdout/`--json` → `memory/AGENTS.md` 项目门禁命令第 4 条（A-memory-start R193 在修改类任务动手前实跑）→ 阻断/告警两级退出码；另一支 `A-get-memory` 条款经 `rule_editor replace` 入受管根正文与版本历史（**未碰其 description ⇒ 不触派生件重建**）；07 翻 `- [x]` → `trim-shell` 条目级归档 → 主卷字节下降 → 注入壳体积不变（handoff 保护索引壳，已实测）
结构: 全部 UTF-8 无 BOM；棘轮基线 schema=`zijian-inject-ratchet-v1`，metrics 仅 5 个整型键、`hard_caps` 随实测注入；findings 分 `blocking`/`advisory` 两组，退出码 0/1/2 语义不变；footer [升级建议] 2 行（≤ N+1，N=1），「改法」字段全部 ≤40 字符（上一条 r20 因 41 字符被 `upgrade_footer_gate.py` 当场拦下并改短）
异常: 指标算不出 → `unknown[]` + exit 1（禁填 0 冒充）；基线文件缺失/损坏 → exit 2 并提示先跑 `--update`；`--update` 遇现状高于既有基线 → 拒绝写入并打印抬基线明细（须人工改文件说明理由，防静默放宽）；受管根 dry-run 未命中不写盘；`rule_editor commit` 全程单文件白名单（本轮 28+ 条他人在途零夹带，写前脏源检测未触发）；镜像漂移按「只读检查→ -Fix → 复核」三步处置

<!-- footer:begin session=qd-zijian-r20b-0924 ts=2026-09-24T21:45:00+08:00 -->
[skill清单] 本轮调用=1 个 (A-get-memory)
[升级建议] skill=A-get-memory | 五问=缺失步骤 | 改法=交付判据类工具前强制跑夹具门禁 | 对照=已取(证据=复测该文件 0 条在途后经 rule_editor 落地，dry-run 3/3、写后读回、四门禁全绿) | 状态=已闭环(证据=D:\\global_skills\\A-get-memory\\SKILL.md#版本行:V4.30.0)
[升级建议] skill=焚诀 verify | 五问=缺失步骤 | 改法=补 C31/C32/C33 三门禁并合一注入区口径 | 对照=已取(证据=本仓等价实现实测并集 87878B 超顶 65536 而 C25 判 PASS) | 状态=未闭环(原因=焚诀 eval/ 只读红线且其 27 条在途；已二次让号并交付接线指南 05-exec/r20b_fenjue_wiring/README.md，本仓侧棘轮已自持上线)
<!-- footer:end -->
"""

NEED = ["【数据流假设】", "来源:", "流向:", "结构:", "异常:", "[skill清单]", "[升级建议]", KEY]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    log = io.open(LOG, encoding="utf-8-sig").read()
    if KEY in log:
        print("[SKIP] r20b footer 已存在（幂等）")
        return 0
    with open(LOG, "wb") as f:
        f.write((log.rstrip("\n") + "\n" + BLOCK).encode("utf-8"))
    back = io.open(LOG, encoding="utf-8-sig").read()
    miss = [k for k in NEED if k not in back]
    print("[GM日志] 读回验证=%s | 缺失=%s | 文件=%dB" % (not miss, miss or "-", os.path.getsize(LOG)))
    return 1 if miss else 0


if __name__ == "__main__":
    raise SystemExit(main())
