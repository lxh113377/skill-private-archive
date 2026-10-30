"""_split_patch.py — 按 target 拆出 rule_editor 可用的补丁文件（一件一次调用）。

存在理由（读实现所得，非猜测）：rule_editor.op_replace 先 resolve(args.file) 再
_plan_patches(read_text(path), items) —— 一个 --file 只喂一个目标件，故跨件补丁必须拆。
拆出的文件只留 old/new（rule_editor 只认这两键 + old_file/new_file/delete），
id/target/_verify 留在 patch.json 里给判据用。
"""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
items = json.load(open(os.path.join(D, "patch.json"), encoding="utf-8"))
groups = {}
for it in items:
    groups.setdefault(it["target"], []).append({"id": it["id"], "old": it["old"], "new": it["new"]})
for tgt, grp in groups.items():
    name = "patch_" + os.path.basename(tgt) + ".json"
    json.dump(grp, open(os.path.join(D, name), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(name, len(grp), "items ->", tgt)
