# -*- coding: utf-8 -*-
"""_drift_test.py — 第五腿负控：手改数组件一个字符 => load_patch 必须 FATAL 点名漂移。

先备份、finally 复原，不留脏件（纪律⑧：负控副本用完即删）。
"""
import io, os, subprocess, sys

D = os.path.dirname(os.path.abspath(__file__))
f = os.path.join(D, "patch_node_mcp_server.md.json")
orig = io.open(f, encoding="utf-8").read()
returned = 1
out = ""
try:
    tampered = orig.replace("Implementation Guide", "Implementation Guidx", 1)
    io.open(f, "w", encoding="utf-8").write(tampered)
    r = subprocess.run([sys.executable, "-B", os.path.join(D, "check_r287m.py"), "--only", "A"],
                       capture_output=True, text=True)
    returned = r.returncode
    out = (r.stdout or "") + (r.stderr or "")
finally:
    io.open(f, "w", encoding="utf-8").write(orig)
tail = out.strip().splitlines()[-1] if out.strip() else "(no output)"
print("rc=%d" % returned)
print("last=" + tail[:200])
print("restored_identical=%s" % (io.open(f, encoding="utf-8").read() == orig))
