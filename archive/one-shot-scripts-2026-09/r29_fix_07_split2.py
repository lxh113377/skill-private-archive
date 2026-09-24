# -*- coding: utf-8 -*-
"""r29_fix_07_split2.py — 一次性修复：上一条插入又把「P0·待裁定」项与原 r27 自纠项并成一行。
拆回两行并还原 r27 项标签（其余文字逐字保留）。"""
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "memory" / "07-next-steps.md"
SPLIT_AT = "本仓不擅动冻结件。"
R27_LABEL = "- [ ] **【P0 自纠·r27 我犯了自己登记过的夹带缺陷】**"

lines = P.read_text(encoding="utf-8").split("\n")
idx = [i for i, ln in enumerate(lines)
       if SPLIT_AT in ln and R27_LABEL.lstrip("- [ ").split("】")[0] not in ln and "提交 `b973917`" in ln]
assert len(idx) == 1, "定位待拆行失败: %r" % idx
i = idx[0]
ln = lines[i]
assert ln.count(SPLIT_AT) == 1
head, tail = ln.split(SPLIT_AT, 1)
lines[i] = head + SPLIT_AT
lines[i + 1:i + 1] = ["", R27_LABEL + tail.lstrip()]
P.write_text("\n".join(lines), encoding="utf-8")
print("已拆分 -> 行%d(%dB) / 行%d(%dB)" % (i + 1, len(lines[i].encode()), i + 3, len((R27_LABEL + tail).encode())))
