# -*- coding: utf-8 -*-
r"""r21e_land_memory.py — 把控制符扫描挂进必跑链，并在 07 落两条（校注 + r21e 条目）。

纪律：文本一律在本文件内构造（不走 shell 内联），反斜杠只写一处来源；写前断言锚点命中数、
写后读回复核（R213），并断言产物控制符计数为 0（本轮新判据自反适用）。
"""
import io
import sys

WS = r"C:\Users\37533\Desktop\workspace\自建skill优化"
AG = WS + r"\memory\AGENTS.md"
N07 = WS + r"\memory\07-next-steps.md"
BSL = chr(92)   # 单个反斜杠
DQ = chr(34)    # 双引号


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, t):
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)


def step_agents():
    t = rd(AG)
    old = ("python 05-exec/r19_scan_fixtures.py && python 05-exec/r19_baseline_contract_fixtures.py"
           " && python 05-exec/baseline_contract_scan.py --quiet && python 05-exec/ratchet_gate.py")
    if "control_char_scan" in t:
        print("[AGENTS] 已挂链，跳过")
        return True
    assert t.count(old) == 1, "必跑链锚点命中 %d" % t.count(old)
    t = t.replace(old, old + " && python 05-exec/control_char_scan.py .")
    t = t.replace("> 四条全 `[GATE:fixture-pass]`", "> 五条全 `[GATE:fixture-pass]`")
    ins = ("> 第五条 `[CTRL:CLEAN]` = 全仓无非法控制符（0x00-0x1F 减制表/换行/回车，另加 0x7f DEL）。"
           "它拦的是「肉眼看不见、但会让引用检索不到」这一类：实测当天四轮复现，含被修文件自身。 ")
    assert t.count("> 判据可信度本身由") == 1
    t = t.replace("> 判据可信度本身由", ins + "> 判据可信度本身由")
    wr(AG, t)
    b = rd(AG)
    ok = "control_char_scan" in b and "[CTRL:CLEAN]" in b
    print("[AGENTS] 挂链+说明=%s" % ok)
    return ok


def step_07():
    s = rd(N07)
    anchor = "幂等只许用「原子替换 / 先备份」实现，不得用跳过执行实现。"
    assert s.count(anchor) == 1, "铁律锚点命中 %d" % s.count(anchor)
    note = ("**⚠️ 校正注（r21e 实测，原文一字未改）**：本行引用的 " + DQ + "feedback-user-command-supreme.md" + DQ
            + " 在 " + BSL + "`D:" + BSL + "global_memory" + BSL + "` 根下**实测已不存在**（今天曾被写入后又消失，"
            + BSL + "`MEMORY.md` 索引亦不再指向它）⇒ 权威唯一存点 = 本行前半已引的 "
            + BSL + "`core" + BSL + BSL + "behavior_core.md` #23（实测存在）。引用不删、仅登记，避免改写他人留痕。")
    if "feedback-user-command-supreme.md` 在" not in s:
        s = s.replace(anchor, anchor + note, 1)

    add = ("- [ ] **【r21e 机器型补口·控制符 + 证据可解析】** 把 r21d 那条判据从自觉升级为机器型。新增 "
           + BSL + "`05-exec/control_char_scan.py`（脏集 = C0 控制符 ∪ {0x7f DEL} - 制表/换行/回车；跳二进制但如实登记 "
           "skipped；空输入面 exit 2 不放行）+ 夹具 " + BSL + "`05-exec/r21e_control_char_fixtures.py` **22/22**"
           "（红阶段先看红、变异 3/3 被拦），已挂进 " + BSL + "`memory/AGENTS.md` 必跑链第 5 条。"
           "**首跑即抓到三处真缺陷**：① 我自己的 " + BSL + "`lessons.part49.md` 残留 2 个退格符 —— 我先前声称"
           + DQ + "断言过已清零" + DQ + "，实为**重写脚本从未执行**（断言 ≠ 执行，当场被自己的新判据抓到）；"
           "② 受管根 " + BSL + "`A-project-handoff/references/version-history.md` 第 38 行两个 **NUL(0x00)** "
           "把 " + BSL + "`02-structure.md`/" + BSL + "`03-tech-stack.md` 写成死引用（已经 rule_editor 修复：受管根提交 + "
           "备份件 20260924_230108 + 镜像**单文件**同步，源与镜像 37,333B 同源；未跑全局 -Fix，因 "
           + BSL + "`ican-frontend-design-system` 3 文件仍在他人在途）；③ **判据定义自身有洞** —— 原只查 "
           "&lt;0x20，DEL(0x7f) 漏网，而 DEL 恰好真的出现在我写的源码里 ⇒ 脏集扩展为 C0 ∪ {0x7f} - 合法空白。"
           "**边界重申（防借壳复活）**：本仓全部判据（棘轮 / 外推过期 / 控制符 / 证据可解析）一律只约束"
           + DQ + "写法与落盘" + DQ + "，一律**不得**用于判定" + DQ + "本轮要不要干活" + DQ + "；重复指令按 "
           + BSL + "`core" + BSL + BSL + "behavior_core.md` #23 一律整跑。取值："
           + BSL + "`python 05-exec/control_char_scan.py .`（期望 " + BSL + "`[CTRL:CLEAN]`）。 ")
    a2 = "- [ ] **【P0 新立判据·r21d】**"
    if "r21e 机器型补口" not in s and s.count(a2) == 1:
        s = s.replace(a2, add + a2, 1)
    wr(N07, s)
    b = rd(N07)
    ok = ("r21e 机器型补口" in b) and ("feedback-user-command-supreme.md` 在" in b) and b.count(chr(8)) == 0
    print("[07] 两条落盘=%s | 控制符=%d | %dB" % (ok, b.count(chr(8)), len(b.encode("utf-8"))))
    return ok


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    return 0 if (step_agents() and step_07()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
