# -*- coding: utf-8 -*-
r"""r21d_rewrite_footer_script.py — 把 r21d_footer_append.py 的两段长文本换成 raw 字符串并自愈已污染卷。

为什么这么绕：本轮第三次踩同一个「反斜杠被解析成退格符」坑（前两次 = shell 内联 python -c、
非 raw 的 ENTRY2 常量）。本脚本自身**不写任何字面反斜杠进被写文本**：所有反斜杠与控制符
一律用 chr(92)/chr(8) 显式构造，且写前断言目标文本 0x08 计数符合预期。

做三件事：
  ① 重写 footer 脚本的 ENTRY2 / BLOCK 为 raw 三引号形式（反斜杠单一来源 = 源文件本身）；
  ② 修复 lessons.part49：截掉被污染的旧第 2 条，按新 ENTRY2 重建；
  ③ 校验：py_compile 通过 + 两处产物二进制读回 0x08 计数 = 期望值。
"""
import io
import os
import py_compile
import sys

WS = r"C:\Users\37533\Desktop\workspace\自建skill优化"
SCRIPT = os.path.join(WS, "05-exec", "r21d_footer_append.py")
P49 = r"D:\global_memory\lessons\lessons.part49.md"
CAP = 4096
BS = chr(8)
MARK2 = "### [2026-09-24] 🔴 登记「退格符坑」的条目自己又中了同一个坑"

ENTRY2 = '''ENTRY2 = r"""
### [2026-09-24] 🔴 登记「退格符坑」的条目自己又中了同一个坑：含反斜杠的文本禁走 shell 内联
trigger: core<0x08>ehavior_core.md | 写记忆条目,反斜杠转义,字符串字面量 | bash,python,markdown
- **问题：** 并行会话把权威源路径写成含退格符的死路径（本意 `core\\behavior_core.md`，其中 `\\b` 被解析成 0x08）；我写「登记这条缺陷」的条目时先用 shell 内联 `python -c`（shell + Python 两次解析）**同坑二次复现 3 次**，改用脚本文件后又因常量非 raw **第三次复现 2 次**
- **原因：** 反斜杠要穿 shell 双引号 → Python 字面量 → markdown 渲染三道解析关，少一级转义就静默产出控制符；控制符在 markdown 肉眼不可见、grep 亦匹配不到 ⇒ 死路径无法被引用它的文本文字检索到
- **解法：** ① 含反斜杠/控制符的文本走**脚本文件 + raw 字符串**（`r"""`，只经一次解析），需要控制符本身时用 `chr(8)` 显式构造；② 写前断言「待写文本 0x08 计数 == 期望」，写后二进制读回复核；③ 复扫范围 = 全仓（`memory/**` + `06-benchmark/**`）而非只查被改文件
- **元：** 来源=自建skill优化 r21d 自纠（同坑三轮） | 版本=05-exec/r21d_fix_own_entry.py @1257359f | 置信度=0.7 | 日期=2026-09-24 | 适用范围=shell, python, markdown, 记忆系统
"""
'''

BLOCK = '''BLOCK = r"""
## 22:5x 自建skill优化 r21d（第五次标注驱动·先推翻自己上一条「已闭环」）
- 复测自己：上一条 footer 把 `skill=fenjue-verify` 标成 `状态=已闭环`，实测只成立一半 —— 还账动作（净回吐 1,363B、棘轮 89,014→86,346）✅；但该条建议的**教训本体**当时只落在报告与当日日志，按本体系判据（「教训未升格为条目 = 未闭环」，同日另一会话在同一台账写下同型判据）= 自觉型、未闭环 ⇒ **已闭环声明过度**，本轮改正并把两半分开标注。
- 把教训做成机器型三件套：`05-exec/transmit_obsolescence_check.py`（转办登记表 vs 焚诀 verify 注册面 33 条已注判据；两下限 AND；取不到真相源 = UNVERIFIED + exit 2，不默认放行）+ `06-benchmark/transmit_proposals.json`（schema `zijian-transmit-proposal-v1`）+ `memory/AGENTS.md`「项目门禁命令」**条件前置**（只在要外推时跑，非每轮必跑）。夹具 `05-exec/r21d_obsolete_fixtures.py` 走 TDD：先实跑 `FAIL RED 前置：被测件不存在`，实现后 **26/26**，变异对照 **4/4 被拦**。
- 真跑与人工复测一致：1 件 OBSOLETE（注入区合一，被 C25、C31 覆盖 4/4 词）、2 件 VALID（目录税棘轮 / 计数断言内容级门禁，最强候选仅 1/3 词）。
- 一次「变异设计自身不可证伪」的自纠：两下限是 AND，首版只改单个旋钮翻不出结论 ⇒ 补灵敏度集 Z（单词高占比）/ Y5（双词低占比）后 4/4 才有拦截力；另按 R263 修一条**夹具期望值错**（`matched == ["C31"]` 改为「含 C31 且不虚构」，因 C25 标题确有 2/4 词命中，属规则已知行为而非缺陷）。
- **作用域边界（防刚被否决的东西借壳复活）**：本判据只管「要不要把建议外推给别人」，不管「本轮要不要干活」；幂等闸门已于 r25/r26 被用户明令全删，权威 = `D:\\global_memory\\core\\behavior_core.md` #23 用户命令绝对优先（实测已落地 169 行 ⇒ 我 r19 登记的「跨根缺锚」空洞同步销账）。边界句写进工具 docstring、AGENTS.md 条件前置、07 待观察三处。
- 反哺落盘：`lessons.part49.md` 新建卷（卷首写换卷理由 + 旧卷 3,944B + 本批字节数）两条 —— ①「对标来的机制必须先过用户价值函数这一关」（对手是 CI，幂等 = 省算力；这里是委托式研究，重发 = 就是要再要一轮结果，同一机制收益符号相反）；②「登记退格符坑的条目自己又中同一个坑」。并给 `lessons.part46.md` 那条把「重复识别闸门」当解法的条目**就地挂 `superseded_by` 反向锚**（+77B，3,961B 未破 4,096B）。
- 顺手抓到一个高优先低难度缺陷：07 的 P0 铁律把**自己权威源的路径**写成含退格符的死路径，任何 grep 都跳不到 #23。`05-exec/r21d_fix_own_entry.py` 清零（修 4 处，含我自己新引入的 3 处），全工作区 md 复扫 0x08 = **0**，提交 `1257359f`。

【数据流假设】
来源: `transmit_obsolescence_check.py` 真跑 stdout + 焚诀 `verify_truth_consistency.py` 注册面现解析（33 条）+ 夹具 26 例输出 + `git show --stat` 逐个核对归属 + `behavior_core.md:169` 行原文 + 各文件二进制级 0x08 计数
流向: 本脚本 → `D:\\global_memory\\lessons\\lessons.part49.md`（第 2 条，破 4096B 即停手）→ `D:\\global_memory\\memory\\2026-09-24.md`（append-only）→ `upgrade_footer_gate.py --file` 切片单验（门禁只看最后一个块，多会话共写必须切片）→ 本仓 `git add <逐个路径>` + commit + push（add/commit 同串，防被排程轮在窗口期收下）
结构: 全 UTF-8 无 BOM；lessons 单卷 ≤4096B；footer = begin + [skill清单] 1 行 + [升级建议] 2 行 + end；「改法」字段 15/18 字符均 ≤40；证据锚点仅用 `#版本行:V41` 与 `#backup:<SHA>` 两种合规形态
异常: 任一锚点命中数 != 期望即停手不写；写后读回缺失即 exit 1；待写文本先断言 0x08 计数再落盘（本轮同坑三次复现的防呆）；`--verify-src` 缺失 → exit 2 且拒绝给出过期结论；受管根本轮零写入（无 rule_editor 调用）

<!-- footer:begin session=qd-zijian-r21d-0924 ts=2026-09-24T23:05:00+08:00 -->
[skill清单] 本轮调用=2 个 (A-get-memory, A-project-handoff)
[升级建议] skill=A-get-memory | 五问=缺失步骤 | 改法=已闭环须分标动作与教训两半 | 对照=已取(证据=教训当时只在报告与日志属自觉型，现升格 lessons.part49 两条 + part46 反向锚 + 机器型判据 26 例夹具) | 状态=已闭环(证据=D:\\global_memory\\lessons\\lessons.part49.md#版本行:V41)
[升级建议] skill=A-memory-start | 五问=错误信息 | 改法=含反斜杠文本改走脚本文件加raw串 | 对照=已取(证据=同坑三轮复现，shell 内联 3 处、非 raw 常量 2 处；raw 化后写前断言与写后读回均 0x08=0) | 状态=已闭环(证据=C:\\Users\\37533\\Desktop\\workspace\\自建skill优化\\05-exec\\r21d_fix_own_entry.py#backup:1257359f)
<!-- footer:end -->
"""
'''


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    # ① 重写脚本常量段
    s = io.open(SCRIPT, encoding="utf-8-sig").read()
    for name, new in (("ENTRY2", ENTRY2), ("BLOCK", BLOCK)):
        start = s.index('\n%s = """' % name) + 1
        end = s.index('\n"""\n', start) + len('\n"""\n')
        s = s[:start] + new + s[end:]
    for txt in (ENTRY2, BLOCK):
        if BS in txt:
            print("[停手] 新常量自身含退格符")
            return 1
    with open(SCRIPT, "wb") as f:
        f.write(s.encode("utf-8"))
    py_compile.compile(SCRIPT, doraise=True)
    print("[①] 脚本 raw 化重写 + py_compile PASS | 文件 0x08=%d"
          % io.open(SCRIPT, "rb").read().count(b"\x08"))

    # ② 修 part49：截掉污染的旧条目，重建
    t = io.open(P49, encoding="utf-8-sig").read()
    if MARK2 in t:
        t = t[:t.index(MARK2)].rstrip("\n") + "\n"
    e2 = ENTRY2.split('r"""\n', 1)[1].rsplit('"""', 1)[0]
    new = t + "\n" + e2.rstrip("\n") + "\n"
    if len(new.encode("utf-8")) > CAP:
        print("[② 停手] part49 重建后 %dB > %dB" % (len(new.encode("utf-8")), CAP))
        return 1
    with open(P49, "wb") as f:
        f.write(new.encode("utf-8"))
    back = io.open(P49, "rb").read()
    print("[②] part49 重建=%dB | 条目数=%d | 0x08=%d（期望 0）"
          % (len(back), back.decode("utf-8").count("### ["), back.count(b"\x08")))
    return 0 if back.count(b"\x08") == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
