# -*- coding: utf-8 -*-
"""r29_fix_07_merge.py — 一次性修复：上一处编辑误把 r29 摘要插进 r28 行内，两条被并成一条。
拆回两行并还原 r28 原句开头（原文其余部分逐字保留）。跑完即可删。"""
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "memory" / "07-next-steps.md"
MARK = "（此前全是「我们源码 vs 对手 README 宣称」）"
R28_HEAD = ("- **2026-09-24（第 28 轮 r28，方法论修正轮）** — 首次把同一把尺架到对手"
            "**真实 SKILL.md**")

lines = P.read_text(encoding="utf-8").split("\n")
idx = [i for i, ln in enumerate(lines) if ln.startswith("- **2026-09-24（第 29 轮 r29")]
assert len(idx) == 1, "定位 r29 行失败: %r" % idx
i = idx[0]
cur = lines[i]
assert MARK in cur, "r28 尾巴不在该行，可能已修好"
head, tail = cur.split(MARK, 1)
assert head.endswith("在途 `M`）。"), "r29 行结尾非预期: %r" % head[-30:]
lines[i] = head.rstrip()
lines[i + 1:i + 1] = ["", R28_HEAD + MARK + tail]
P.write_text("\n".join(lines), encoding="utf-8")
print("已拆分：r29 行 %dB / r28 行 %dB" % (len(lines[i].encode()), len((R28_HEAD + MARK + tail).encode())))
