# -*- coding: utf-8 -*-
r"""r21d_footer_append.py — r21d 反哺第二条目 + GM 日志段 + footer 锚点块（幂等，逐处守卫）。

来源: 本轮实测（`transmit_obsolescence_check` 真跑 rc=1 / 1 OBSOLETE；夹具 26/26 含变异 4/4；
      `r21d_fix_own_entry.py` 修 4 处退格符后读回 0x08=0；全工作区 md 文件 0x08 总数 = 0）。
流向: 本脚本 → ① `D:\global_memory\lessons\lessons.part49.md`（追加第 2 条）
      → ② `D:\global_memory\memory\2026-09-24.md`（append-only）→ `upgrade_footer_gate.py`。
结构: UTF-8 无 BOM；lessons 单卷硬上限 4096B，破限即停手不写（不换卷、不截断）。
异常: 任一锚点命中数 != 期望 → 该步停手；写后读回八项锚点（R213）缺失即 exit 1。
"""
import io
import os
import sys

P49 = r"D:\global_memory\lessons\lessons.part49.md"
LOG = r"D:\global_memory\memory\2026-09-24.md"
KEY = "session=qd-zijian-r21d-0924"
CAP = 4096

ENTRY2 = """
### [2026-09-24] 🔴 登记「退格符坑」的条目自己又中了同一个坑：含反斜杠的文本禁走 shell 内联
trigger: core<0x08>ehavior_core.md | 写记忆条目,shell内联python,反斜杠转义 | bash,python,markdown
- **问题：** 并行会话把权威源写成 `core\\behavior_core.md` 的退格版（markdown 里 `\b` 被当控制符），我写「登记这条缺陷」的条目时用 `python -c "..."` 传字符串，**同一个坑二次复现 3 次**，连我给的复测命令 `b'\\x08'` 也变成真退格符
- **原因：** shell 双引号 + Python 字符串字面量 = **两次**反斜杠解析，写 `'\\\\b'` 才得 `\b`；而 `-c` 里少一级转义就静默产出控制字符，肉眼在 markdown 里不可见
- **解法：** ① 含反斜杠/控制符的文本一律走**脚本文件**（源文件只经一次解析；`chr(8)` 显式构造更稳）；② 落盘后必做读回断言：`open(p,'rb').read().count(b'\\x08')==0`；③ 全仓扫面（不止被改文件）：`glob memory/**/*.md + 06-benchmark/**` 逐个计数
- **元：** 来源=自建skill优化 r21d 自纠 | 版本=05-exec/r21d_fix_own_entry.py @1257359f | 置信度=0.7（同坑两轮实证） | 日期=2026-09-24 | 适用范围=shell, python, markdown, 记忆系统
"""

BLOCK = """
## 22:5x 自建skill优化 r21d（第五次标注驱动·先推翻自己上一条「已闭环」）
- 复测自己：上一条 footer 把 `skill=fenjue-verify` 标成 `状态=已闭环`，实测只成立一半 —— 还账动作（净回吐 1,363B、棘轮 89,014→86,346）✅；但该条建议的**教训本体**当时只落在报告与当日日志，按本体系判据（「教训未升格为条目 = 未闭环」，同日另一会话在同一台账写下同型判据）= 自觉型、未闭环 ⇒ **已闭环声明过度**，本轮改正。
- 把教训做成机器型三件套：`05-exec/transmit_obsolescence_check.py`（转办登记表 vs 焚诀 verify 注册面 33 条已注判据；两下限 AND；取不到真相源 = UNVERIFIED + exit 2 不默认放行）+ `06-benchmark/transmit_proposals.json`（`zijian-transmit-proposal-v1`）+ `memory/AGENTS.md`「项目门禁命令」**条件前置**（只在要外推时跑，非每轮必跑）。夹具 `05-exec/r21d_obsolete_fixtures.py` 走 TDD：先实跑 `FAIL RED 前置：被测件不存在`，实现后 **26/26**，变异对照 **4/4 被拦**。
- 真跑与人工复测一致：1 件 OBSOLETE（注入区合一，被 C25、C31 覆盖 4/4 词）、2 件 VALID（目录税棘轮 / 计数断言内容级门禁，最强候选仅 1/3 词）。
- 一次「变异设计自身不可证伪」的自纠：两下限是 AND，首版只改单个旋钮翻不出结论 ⇒ 补灵敏度集 Z（单词高占比）/ Y5（双词低占比）后 4/4 才有拦截力；另按 R263 修一条**夹具期望值错**（`matched==["C31"]` 改为「含 C31 且不虚构」，因 C25 标题确有 2/4 词命中，属规则已知行为）。
- **作用域边界（防刚被否决的东西借壳复活）**：本判据只管「要不要把建议外推给别人」，不管「本轮要不要干活」；幂等闸门已于 r25/r26 被用户明令全删（权威 = `D:\\global_memory\\core\\behavior_core.md` #23 用户命令绝对优先，实测已落地 169 行 ⇒ 我 r19 登记的「跨根缺锚」空洞同步销账）。边界句已写进工具 docstring、AGENTS.md 条件前置、07 待观察三处。
- 反哺落盘：`lessons.part49.md` 新建卷（换卷理由 + 旧卷 3,944B + 本批字节数）两条 —— ①「对标来的机制必须先过用户价值函数这一关」（对手是 CI 省算力，这里是委托式研究，重发就是要再要一轮结果）；②「登记退格符坑的条目自己又中同一个坑」。并给 part46 那条把「重复识别闸门」当解法的条目**就地挂 `superseded_by` 反向锚**（+77B，3,961B 未破 4,096B）。
- 顺手抓到一个高优先低难度缺陷：07 的 P0 铁律把**自己权威源的路径**写成了含退格符的死路径（markdown `\\b` 被解释成 0x08），任何 grep 都跳不到 #23。`05-exec/r21d_fix_own_entry.py` 清零（修 4 处含我自己新引入的 3 处），全工作区 md 复扫 0x08 = **0**，提交 `1257359f`。

【数据流假设】
来源: `transmit_obsolescence_check.py` 真跑 stdout + 焚诀 `verify_truth_consistency.py` 注册面现解析（33 条）+ 夹具 26 例输出 + `git show --stat` 逐个核对归属 + `behavior_core.md:169` 行原文 + 07/报告/AGENTS 二进制级 0x08 计数
流向: 本脚本 → `D:\\global_memory\\lessons\\lessons.part49.md`（追加第 2 条，破 4096B 即停手）→ `D:\\global_memory\\memory\\2026-09-24.md`（append-only）→ `upgrade_footer_gate.py --file` 切片单验（门禁只看最后一个块，多会话共写时必须切片）→ 本仓 `git add <逐个路径>` + commit + push（add/commit 同串，防被排程轮窗口收下）
结构: 全 UTF-8 无 BOM；lessons 卷 ≤4096B；footer = begin + [skill清单] 1 行 + [升级建议] 2 行 + end；「改法」字段 15/18 字符均 ≤40；证据锚点仅用 `#版本行:V41` 与 `#backup:<SHA>` 两种合规形态
异常: 任一锚点命中数 != 期望即停手不写；写后读回缺失即 exit 1；07 主卷本轮仍现「修好又被活写入者弹回」（我改走脚本文件 + 提交前复测，最终 git 对象 0x08=0）；`--verify-src` 缺失 → exit 2 并拒绝给出过期结论；受管根本轮零写入（无 rule_editor 调用）

<!-- footer:begin session=qd-zijian-r21d-0924 ts=2026-09-24T22:58:00+08:00 -->
[skill清单] 本轮调用=2 个 (A-get-memory, A-project-handoff)
[升级建议] skill=A-get-memory | 五问=缺失步骤 | 改法=已闭环须同时改标动作与教训两半 | 对照=已取(证据=教训当时只在报告与日志属自觉型，现升格为 lessons.part49 两条 + part46 反向锚 + 机器型判据 26 例夹具) | 状态=已闭环(证据=D:\\global_memory\\lessons\\lessons.part49.md#版本行:V41)
[升级建议] skill=A-memory-start | 五问=错误信息 | 改法=含反斜杠文本禁走shell内联改走脚本文件 | 对照=已取(证据=同一退格符坑两轮复现，登记该坑的条目自身又引入3处；脚本清零后读回与全仓复扫均 0) | 状态=已闭环(证据=C:\\Users\\37533\\Desktop\\workspace\\自建skill优化\\05-exec\\r21d_fix_own_entry.py#backup:1257359f)
<!-- footer:end -->
"""

NEED = ["【数据流假设】", "来源:", "流向:", "结构:", "异常:", "[skill清单]", "[升级建议]", KEY]


def step1():
    if not os.path.exists(P49):
        print("[1/2 停手] part49 不存在（可能已被合并）")
        return False
    t = io.open(P49, encoding="utf-8-sig").read()
    if "shell 内联" in t:
        print("[1/2 跳过] 第 2 条已在位")
        return True
    new = t.rstrip("\n") + "\n" + ENTRY2
    if len(new.encode("utf-8")) > CAP:
        print("[1/2 停手] 追加后 %dB > %dB ⇒ 应换卷而非硬塞" % (len(new.encode("utf-8")), CAP))
        return False
    with open(P49, "wb") as f:
        f.write(new.encode("utf-8"))
    back = io.open(P49, encoding="utf-8-sig").read()
    ok = back.count("### [") == 2 and back.count(chr(8)) == 0
    print("[1/2] part49 追加=%s | 条目数=%d | %dB ≤%d | 0x08=%d"
          % (ok, back.count("### ["), os.path.getsize(P49), CAP, back.count(chr(8))))
    return ok


def step2():
    log = io.open(LOG, encoding="utf-8-sig").read()
    if KEY in log:
        print("[2/2 跳过] r21d footer 已存在（幂等）")
        return True
    with open(LOG, "wb") as f:
        f.write((log.rstrip("\n") + "\n" + BLOCK).encode("utf-8"))
    back = io.open(LOG, encoding="utf-8-sig").read()
    miss = [k for k in NEED if k not in back]
    print("[2/2] GM 日志读回=%s | 缺失=%s | %dB" % (not miss, miss or "-", os.path.getsize(LOG)))
    return not miss


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    return 0 if (step1() and step2()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
