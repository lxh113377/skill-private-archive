# -*- coding: utf-8 -*-
r"""r103_footer_fix.py — 生成本轮 footer [升级建议] 行的 old/new 两片（文法合规版）。

一手：首版把行写成 `对照=已取(证据=<路径> 与 <一句>) | 状态=待闭环(证据=…)`，被
`upgrade_footer_gate.py:RE_UPGRADE` 拒收两处 —— ①`对照` 的值用 `\(([^)]*)\)` 匹配，
**括号内不得再有括号**；②`状态` 只认 `已闭环|未闭环`，「待闭环」不是合法取值。
判据报错原文已把修法写全（缺行 + 非法行点名），先读红因再改形状，不动判据（R263）。

只改自己刚写的那一行 ⇒ 用整行做锚点，命中数必须==1。
退出码：0=两片就绪；1=锚点异常。
"""
import io
import json
import os
import sys

SHELL = r"D:/global_memory/memory/2026-10-03.md"
TMP = os.environ.get("TEMP", "/tmp")
OLD_P = os.path.join(TMP, "r103_footer_old.txt")
NEW_P = os.path.join(TMP, "r103_footer_new.txt")

OLD = ("[升级建议] skill=A-project-better | 五问=取数面失败必须与零值分形,档位谓词必须三态,"
       "夹具腿必须驱动被测本体,变异矩阵须出具具名红腿,挂账前提须可复算 | "
       "改法=把本轮假零一手写进 references/benchmark.md 并配四条反例腿 | "
       "对照=已取(证据=r103 报告 §0 与 r96_twelve_face selftest 53/53) | "
       "状态=未闭环(原因=A-project-better 本体归其 owner，本轮只修本仓判据未代改)")

# 第二形态（同轮再犯，红因由判据原文给出）：`五问` 只认固定词表
# {过期指令,缺失步骤,低效流程,模糊描述,错误信息}，`改法` 上限 40 字（实测 41 即红）。
NEW = ("[升级建议] skill=A-project-better | 五问=缺失步骤,模糊描述 | "
       "改法=benchmark.md 补「取数失败须显形」条并配反例腿 | "
       "对照=已取(证据=r103 报告 §0 与 r96_twelve_face selftest 53/53) | "
       "状态=未闭环(原因=A-project-better 本体归其 owner，本轮只修本仓判据未代改)")


def main():
    raw = io.open(SHELL, encoding="utf-8").read()
    n = raw.count(OLD)
    if n != 1:
        print("[FOOTER-FIX:FAIL] 锚点命中 %d 次（须==1）" % n)
        return 1
    io.open(OLD_P, "w", encoding="utf-8", newline="").write(OLD)
    io.open(NEW_P, "w", encoding="utf-8", newline="").write(NEW)
    print(json.dumps({"anchor_hits": n, "delta_chars": len(NEW) - len(OLD),
                      "old": OLD_P, "new": NEW_P}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
