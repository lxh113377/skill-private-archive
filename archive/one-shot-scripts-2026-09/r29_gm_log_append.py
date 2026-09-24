# -*- coding: utf-8 -*-
"""r29_gm_log_append.py — 一次性：把 r29 轮次条目 + 收尾 footer 锚点块追加到当日 GM 日志。
跑完即可删（追加语义，不读不改既有内容，避免与并行会话抢写）。"""
import sys
from datetime import datetime
from pathlib import Path

LOG = Path(r"D:\global_memory\memory\2026-09-24.md")
sid = "r29-dualcalibre-" + datetime.now().strftime("%H%M%S")
ts = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

body = """

## 第 29 轮 r29（自建skill优化 · 端 QD · 定时对标指令第 N 次重发，按原文完整再跑）

- **先量尺子再动手**：M2 双口径落 `skill_structure_rubric_scan.rubric_hits(calibre)`，宽口径**复用** r17 description 判据（`TRIGGER_RE`/`PROCESS_RE`/`MIN_DO_LEN`）不另造尺；四层自证 = 层a 夹具 9/9（含 3 条反例）/ 层b 真跑双表 / 层b′ `--against` 与 r28 归档**正文口径 7 列全等**（改尺不动历史）/ 层c 不可达仓库 RC=2 拒出表。
- **推翻④（判据稳健性）**：三档锚点实测本体系 verification 59.0% → 72.3%（档3 仅标题 31.3%），**22 条 = 原判缺口 32.4% 属措辞假阴性**（实物 `story-scan` 有「采集质量门」却被判缺）。⇒ r28「差 41pt」更正为 **27.7pt**。
- **推翻⑤（范围过滤）**：r28 的 H2 队列按体积排 top14 **全是市场/上游件**，越过 2026-09-22 自建裁定（维护面 77）⇒ 新护栏 `r29_scope_filtered_queue.py`；双过滤后真队列 **3 条 → 已全部补「验证」段清零**（受管根 `6a4f97b`，26 行纯新增零夹带，frontmatter/description 未动 ⇒ 派生件零重建、C25 未受影响）。
- **削掉虚高后唯一站得住的缺口** = `rationalizations` 13.9% vs addyosmani 96.0%（差 **82.1pt**，宽窄两口径差值 +0.0）；其落点模板被并行会话占用（`A-skill-manager/SKILL.md` 在途 `M`），按 R269 未抢改。
- **门禁事实**：`mirror` fail(mismatch=6) → **pass**（`check-skill-mirror.ps1 -Fix` 源→镜像单向补齐）；`noise` fail 与焚诀 `C20` fail **均为开工前既存**且归属并行会话（GM 根 feedback 文件 + `ican-frontend-design-system` inline 1→4），只登记未动。
- **自纠（同坑本轮二次复现，值得记住的写法坑）**：用 Edit 在某行**前缀**处插入整行时，若 new_string 不含该前缀，会把原行吞掉并与新行粘连 —— 本轮连犯 2 次（07 摘要、07 P0），两次都用行号定位脚本拆回并逐字校验。**规程**：插入整行时 old_string 必须取完整行，或 new_string 以原前缀结尾；写完必须 `git diff` 看删除行数是否等于预期。
- 工作区提交 `b8f7f96`（18 文件，逐路径 add，他人件 `ratchet_gate.py` / `inject_ratchet_baseline.json` / `r21e_*` / `evidence_resolvability_*` 未卷入），HEAD == origin/main。

<!-- footer:begin session=__SID__ ts=__TS__ -->
[skill清单] 本轮调用=2 个 (A-project-handoff, A-memory-start)
[升级建议] skill=A-skill-manager | 五问=缺失步骤 | 改法=新建技能模板强制加验证段与反理性化表 | 对照=已取(证据=同类改动受管根 6a4f97b 落地后复测真队列 3→0，且宽窄口径差值 +0.0 说明该段无等价写法) | 状态=未闭环(原因=目标模板文件 `A-skill-manager/SKILL.md` 与其 version-history 正被并行会话改写，按 R269 不抢改，待窗口)
<!-- footer:end -->
""".replace("__SID__", sid).replace("__TS__", ts)

with LOG.open("a", encoding="utf-8", newline="\n") as fh:
    fh.write(body)
print("APPENDED %dB -> %s" % (len(body.encode("utf-8")), LOG))
