import json, os
D = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(D, "patch.json")
items = json.load(open(p, encoding="utf-8"))
for it in items:
    it["_verify"]["assert"] = "text.count(old) == 1"
    it["_verify"]["file"] = os.path.basename(it["target"])
json.dump(items, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("asserted", len(items), "hunks")
print("ids:", [i["id"] for i in items])
