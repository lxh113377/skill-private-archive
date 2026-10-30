# -*- coding: utf-8 -*-
"""_sync_meta.py — 给 numbers.json / newfile_manifest.json 补判据需要的字段（现取，不手填）。

存在理由：check_r287m 的 C 腿要拿 license_body_restricted_hits 做漂移比对、B 腿要拿
api_blob_sha 做三方相等（git blob == gh api .sha == 清单值）。这些值必须来自实时 gh api 与
实时 classify_body，不能由人抄写。
"""
import hashlib, json, os, subprocess, sys

D = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, os.path.join(ROOT, "05-exec"))
import r114_replacement_scan as R

body = open(os.path.join(D, "_upstream_LICENSE.txt"), encoding="utf-8", errors="replace").read()
spdx, cls, hits = R.classify_body(body.upper())
np = os.path.join(D, "numbers.json")
num = json.load(open(np, encoding="utf-8"))
num["license"]["license_body_restricted_hits"] = len(hits)
num["license"]["fetched_at"] = subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                                              capture_output=True, text=True).stdout.strip()
json.dump(num, open(np, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

raw = open(os.path.join(D, "upstream_node_mcp_server_v2.md"), "rb").read()
r = subprocess.run(["gh", "api",
                    "repos/anthropics/skills/contents/skills/mcp-builder/reference/node_mcp_server_v2.md?ref=main",
                    "--jq", ".sha + \" \" + (.size|tostring) + \" \" + (.name)"],
                    capture_output=True, text=True)
sha, size, name = (r.stdout or "").strip().split()
mp = os.path.join(D, "newfile_manifest.json")
man = json.load(open(mp, encoding="utf-8"))
man["api_blob_sha"] = sha
man["api_size"] = int(size)
man["api_name"] = name
man["local_target"] = "D:/global_skills/mcp-builder/reference/node_mcp_server_v2.md"
man["lines"] = raw.count(bytes([10]))
man["sha256_12"] = hashlib.sha256(raw).hexdigest()[:12]
man["bytes"] = len(raw)
json.dump(man, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("hits", len(hits), "api", sha[:12], size, name, "lines", man["lines"], "bytes", man["bytes"])
