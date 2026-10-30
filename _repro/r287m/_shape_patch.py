# -*- coding: utf-8 -*-
"""_shape_patch.py — 把 patch.json 整成 {hunks:[{id,old,new,...}], _verify:{...}} 并让判据兼容两种形态。

为什么要 object 形态：brief 要 patch.json 里「加一条 _verify，对每个 old 断言 text.count(old)==1」。
但 rule_editor.op_replace 的 --patch 只认**非空数组**，且一个 --file 只喂一个目标件
（读实现：resolve(args.file) -> _plan_patches(read_text(path), items)）⇒ 数组形态留给
per-file 拆分件（patch_SKILL.md.json / patch_node_mcp_server.md.json）供 Lead 直接喂，
patch.json 本体做「材料 + 断言」的自描述。
"""
import hashlib, json, os

D = os.path.dirname(os.path.abspath(__file__))
items = json.load(open(os.path.join(D, "patch.json"), encoding="utf-8"))
if isinstance(items, dict):
    items = items["hunks"]

ver = []
for it in items:
    t = it["target"]
    text = open(t, encoding="utf-8", newline="").read()
    n = text.count(it["old"])
    ver.append({"id": it["id"], "target": t, "count": n, "assert": "text.count(old) == 1",
                "pass": n == 1, "old_sha256_12": hashlib.sha256(it["old"].encode("utf-8")).hexdigest()[:12],
                "old_bytes": len(it["old"].encode("utf-8")), "new_bytes": len(it["new"].encode("utf-8"))})

out = {
    "schema": "r287m-replace-patch-v1",
    "note": "rule_editor 用 per-file 数组件（files 段）；本件是材料本体 + 断言自描述。",
    "coordinates": {
        "repo": "anthropics/skills", "ref": "main",
        "ref_sha": "ca45fc496a3436251f191354091d557da31c15b5",
        "commit_title": "Update mcp-builder skill: teach v2 of the MCP TypeScript SDK (#2087)",
        "commit_date": "2026-10-28T19:20:38Z",
        "upstream_path": "skills/mcp-builder",
        "reading_from": [
            "06-benchmark/r275_three_channel_intersection.json rows[28]",
            "06-benchmark/r264_sidecar_semantics.json rows[skill=mcp-builder] semantics=SAME_LINEAGE",
            "06-benchmark/r271_version_channel2.json rows[skill=mcp-builder] verdict=UPSTREAM_MOVED",
            "06-benchmark/r263_declared_upstream_face.json rows[skill=mcp-builder] rel=UNKNOWN_UPSTREAM_RELEASE"],
    },
    "new_file": {
        "upstream_path": "skills/mcp-builder/reference/node_mcp_server_v2.md",
        "local_target": "D:/global_skills/mcp-builder/reference/node_mcp_server_v2.md",
        "staged_copy": "_repro/r287m/upstream_node_mcp_server_v2.md",
        "bytes": 35171, "lines": 747, "sha256_12": "49b2fe48f339",
        "git_blob_sha": "5d61f896d9707c8797c33ac8ac03c5aebf9b163f",
        "api_blob_sha": "5d61f896d9707c8797c33ac8ac03c5aebf9b163f",
    },
    "files": {
        "D:/global_skills/mcp-builder/SKILL.md": "patch_SKILL.md.json",
        "D:/global_skills/mcp-builder/reference/node_mcp_server.md": "patch_node_mcp_server.md.json",
    },
    "_verify": {
        "rule": "对每个 hunk 断言 text.count(old) == 1（text = 目标件盘上原文，UTF-8 newline 逐字读）",
        "why": "本仓 R277-1 + 前 4 轮锚点靠记忆教训的机械化：old 必须是逐字切片，唯一命中，不多空行",
        "checked_by": "python -B _repro/r287m/check_r287m.py --only A",
        "negctl": [
            "check_r287m.py --only A --neg anchor-absent（old 改一个字符 => 点名 SKILL-STRUCTURE-PTR 判红）",
            "check_r287m.py --only A --neg anchor-multi（old 换成盘上重复 22 次的行 => 点名 NODE-V1-BANNER 判红）"],
        "all_pass": all(v["pass"] for v in ver),
        "rows": ver,
    },
    "hunks": items,
}
json.dump(out, open(os.path.join(D, "patch.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("all_pass", out["_verify"]["all_pass"], "hunks", len(items))

# 判据 loader 兼容两种形态
p = os.path.join(D, "check_r287m.py")
src = open(p, encoding="utf-8", newline="").read()
old = "    items = jload(\"patch.json\")"
new = ("    raw = jload(\"patch.json\")\n"
       "    items = raw[\"hunks\"] if isinstance(raw, dict) else raw")
assert src.count(old) == 1, ("loader anchor", src.count(old))
open(p, "w", encoding="utf-8", newline="").write(src.replace(old, new, 1))
print("loader patched")

# 拆分件同步（数组形态，可直接喂 rule_editor）
groups = {}
for it in items:
    groups.setdefault(it["target"], []).append({"id": it["id"], "old": it["old"], "new": it["new"]})
for tgt, grp in groups.items():
    name = "patch_" + os.path.basename(tgt) + ".json"
    json.dump(grp, open(os.path.join(D, name), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(name, len(grp))