# -*- coding: utf-8 -*-
"""_probe_newfile.py — 纯只读探测：rule_editor 能否在安全区内创建**新文件**。

做法：import 该模块后只调 resolve()（无写动作）。resolve 在安全区分支里
`if os.path.isfile(ap): return ap` 否则 sys.exit(安全区内文件不存在)。
目的：判「新增独立文件」这条腿能不能用 rule_editor 落，还是必须走别的受管途径。
"""
import importlib.util, os, sys
spec = importlib.util.spec_from_file_location("rule_editor", r"D:\global_skills\A-memory-start\references\rule_editor.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print("GIT_ROOT =", m.GIT_ROOT)
target = "mcp-builder/reference/node_mcp_server_v2.md"
try:
    p = m.resolve(target)
    print("RESOLVED", p)
except SystemExit as e:
    print("SYSEXIT:", e)
existing = "mcp-builder/SKILL.md"
try:
    print("EXISTING RESOLVED", m.resolve(existing))
except SystemExit as e:
    print("SYSEXIT existing:", e)