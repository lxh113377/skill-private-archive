# -*- coding: utf-8 -*-
"""_fix_negctl.py — 把 check_r287m 的 anchor-multi 负控改成运行时挑选盘上真重复行。

根因（本轮实测）：首版硬编码 "## Overview" 当多命中串，但该串在 node_mcp_server.md 里
只出现 1 次 => 负控恒绿（判据没牙）。正解 = 用 Counter 现挑「非空且重复最多」的行。
"""
import os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_r287m.py")
src = open(p, encoding="utf-8", newline="").read()
start = src.index("    if neg == " + chr(34) + "anchor-multi" + chr(34) + ":")
end = src.index("    return out, vid", start) + len("    return out, vid" + chr(10))
NEW = chr(10).join([
    "    if neg == " + chr(34) + "anchor-multi" + chr(34) + ":",
    "        vid = " + chr(34) + "NODE-V1-BANNER" + chr(34),
    "        import collections",
    "        t = norm(os.path.join(SKILL_ROOT, " + chr(34) + "reference" + chr(34) + ", " + chr(34) + "node_mcp_server.md" + chr(34) + "))",
    "        cnt = collections.Counter(l + LF for l in read_text(t).splitlines())",
    "        # 运行时挑盘上重复最多的非空行，不硬编码字串（首版硬编码 " + chr(34) + "## Overview" + chr(34) + "
    "        # 实测只出现 1 次 => 负控恒绿、没有牙）。
    "        dup = max([(l, n) for l, n in cnt.items() if l.strip()], key=lambda x: x[1])",
    "        for it in out:",
    "            if it[" + chr(34) + "id" + chr(34) + "] == vid:",
    "                it[" + chr(34) + "old" + chr(34) + "] = dup[0]",
    "        return out, vid",
    "",
]) + chr(10)
open(p, "w", encoding="utf-8", newline="").write(src[:start] + NEW + src[end:])
print("patched, delta bytes", len(NEW) - (end - start))
