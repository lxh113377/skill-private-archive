# -*- coding: utf-8 -*-
"""_help_of.py <script.py> -- 拿到真实 argparse 用法，绕开缺依赖。

存在理由：受管 venv 里没有 anthropic / mcp 包，直接 python scripts/evaluation.py --help
会在 import 期 ModuleNotFoundError，拿不到 usage ⇒ 判据 2（引用的脚本参数必须被 --help
支持）就只能靠读源码猜。argparse 构造期不触碰第三方符号，故用桩模块顶掉缺失依赖，
让脚本跑到 parser.parse_args( --help ) 打印真实 usage 后 SystemExit(0)。
桩只做名字占位，不改脚本逻辑。
"""
import runpy
import sys
import types


def stub(name, attrs=()):
    m = types.ModuleType(name)
    for a in attrs:
        setattr(m, a, type(a, (), {}))
    sys.modules[name] = m


def main():
    if len(sys.argv) < 2:
        print("usage: _help_of.py <script.py> [flags...]")
        return 2
    script = sys.argv[1]
    extra = sys.argv[2:] or ["--help"]
    stub("anthropic", ("Anthropic",))
    stub("mcp", ("ClientSession", "StdioServerParameters"))
    stub("mcp.client")
    stub("mcp.client.sse", ("sse_client",))
    stub("mcp.client.stdio", ("stdio_client",))
    stub("mcp.client.streamable_http", ("streamablehttp_client",))
    sys.path.insert(0, os_dirname(script))
    sys.argv = [script] + list(extra)
    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as e:
        return int(e.code or 0)
    return 0


def os_dirname(p):
    import os
    return os.path.dirname(os.path.abspath(p)) or "."


if __name__ == "__main__":
    sys.exit(main())
