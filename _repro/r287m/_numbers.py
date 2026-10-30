# -*- coding: utf-8 -*-
"""_numbers.py — 许可门/提交坐标现取（一次跑完，落 _repro/r287m/numbers.json 供引用）。

为什么走脚本而不是手抄：本仓 4 次「锚点靠记忆」教训 ⇒ 所有数字必须可由命令复算。
"""
import hashlib, json, os, subprocess, sys

D = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, os.path.join(ROOT, "05-exec"))
import r114_replacement_scan as R  # 单源判定：classify_body / license_class / LICENSE_CAPS


def gh(*args):
    r = subprocess.run(["gh"] + list(args), capture_output=True, text=True)
    return (r.stdout or "").strip(), (r.stderr or "").strip(), r.returncode


def sha12(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]


def blob(p):
    return subprocess.run(["git", "hash-object", p], capture_output=True, text=True).stdout.strip()


out = {}
lic_p = os.path.join(D, "_upstream_LICENSE.txt")
body = open(lic_p, encoding="utf-8", errors="replace").read()
spdx, cls, hits = R.classify_body(body.upper())
out["license"] = {
    "upstream_body_file": "skills/mcp-builder/LICENSE.txt",
    "bytes": os.path.getsize(lic_p),
    "sha256_12": sha12(lic_p),
    "git_blob_sha40": blob(lic_p),
    "classify_body_spdx": spdx,
    "classify_body_class": cls,
    "restricted_phrase_hits": hits,
    "license_class_spdx_only": R.license_class(spdx),
    "license_class_body_first": R.license_class(spdx, body_class=cls),
    "cap": R.LICENSE_CAPS.get(cls),
    "caps_table": R.LICENSE_CAPS,
    "local_license_txt_sha256_12": sha12("D:/global_skills/mcp-builder/LICENSE.txt"),
    "local_license_txt_blob40": blob("D:/global_skills/mcp-builder/LICENSE.txt"),
}
so, se, rc = gh("api", "repos/anthropics/skills", "--jq", ".license")
out["api_repo_license_field"] = {"stdout": so, "stderr": se, "rc": rc}
so, se, rc = gh("api", "repos/anthropics/skills/license", "--jq", ".license.spdx_id")
out["api_license_endpoint"] = {"stdout": so, "stderr": se, "rc": rc}
so, se, rc = gh("api", "repos/anthropics/skills/commits/ca45fc496a3436251f191354091d557da31c15b5",
                "--jq", '[.sha, .commit.author.date, .commit.message, (.files | length)] | join(" ~ ")')
out["commit"] = {"stdout": so, "stderr": se, "rc": rc}
v2 = os.path.join(D, "upstream_node_mcp_server_v2.md")
b = open(v2, "rb").read()
out["v2"] = {"bytes": len(b), "lines_text_mode": sum(1 for _ in open(v2, encoding="utf-8")),
             "lines_newline_count": b.count(10), "sha256_12": sha12(v2), "git_blob_sha40": blob(v2)}
so, se, rc = gh("api", "repos/anthropics/skills/contents/skills/mcp-builder/reference/node_mcp_server_v2.md?ref=main", "--jq", ".sha")
out["v2_api_blob_sha"] = {"stdout": so, "stderr": se, "rc": rc}
json.dump(out, open(os.path.join(D, "numbers.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=1))
