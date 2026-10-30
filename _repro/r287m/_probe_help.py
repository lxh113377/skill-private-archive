# -*- coding: utf-8 -*-
"""_probe_help.py — 用桩模块替掉 anthropic/mcp 依赖，真跑 scripts/evaluation.py --help。

存在理由：直接 --help 会 ModuleNotFoundError: anthropic（受管 venv 无该包）⇒
「脚本参数是否被 --help 支持」这条判据不能靠猜 argparse 源码，必须拿到真实 usage。
桩只做名字占位，不改脚本逻辑（argparse 在 import 期不触碰这些符号）。
"""
import runpy
import sys
import types


def stub(name, attrs=()):
    m = types.ModuleType(name)
    for a in attrs:
        setattr(m, a, type(a, (), {}))
    sys.modules[name] = m
    return m


stub("anthropic", ("Anthropic",))
sys.path.insert(0, r"D:\global_skills\mcp-builder\scripts")
stub("mcp", ("ClientSession", "StdioServerParameters"))
stub("mcp.client")
stub("mcp.client.sse", ("sse_client",))
stub("mcp.client.stdio", ("stdio_client",))
stub("mcp.client.streamable_http", ("streamablehttp_client",))
sys.argv = ["evaluation.py", "--help"]
try:
    runpy.run_path(sys.argv[0] if False else r"D:\global_skills\mcp-builder\scripts\evaluation.py",
                   run_name="__main__")
except SystemExit as e:
    print("[STUB-RC] %s" % e.code)