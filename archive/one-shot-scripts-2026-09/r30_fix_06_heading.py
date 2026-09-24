# -*- coding: utf-8 -*-
"""r30_fix_06_heading.py — 一次性修复：上一次 Edit 以「## 技术债」为 old_string 覆盖了该标题，
导致本轮 [DEBT] 条目落进了「已知 Bug」节。修法：在该条目行前补回空行 + 节标题，其余一字不动。"""
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "memory" / "06-constraints.md"
DEBT_MARK = "- [DEBT] **反理性化表覆盖率仅 13.9%"

raw = P.read_bytes()
eol = b"\r\n" if b"\r\n" in raw else b"\n"
lines = raw.split(eol)
assert "## 技术债".encode() not in raw, "标题已存在，勿重复插入"
tgt = [i for i, l in enumerate(lines) if l.startswith(DEBT_MARK.encode())]
assert len(tgt) == 1, "本轮 [DEBT] 行应恰好 1 条，实得 %d" % len(tgt)
i = tgt[0]
lines[i:i] = [b"", "## 技术债".encode()]
P.write_bytes(eol.join(lines))
print("补回标题于第 %d 行（%s 行尾保持），其后 [DEBT] 条目序号顺延" % (i + 1, "CRLF" if eol == b"\r\n" else "LF"))
