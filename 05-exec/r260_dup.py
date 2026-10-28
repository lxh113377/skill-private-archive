import sys, io, json
sys.path.insert(0, "05-exec")
import r38_debt_aging as M
# 直接调件内 scan 取 dup_ids（自写正则会误报，R121 已一手实证：全文 findall 把正文引用算成副本）。
files = M.volume_files()
now = M.current_round()
items, face = M.scan(files, now, 2)
di = face.get("dup_ids") or []
bad = [x for x in di if not x["all_checked"]]
print("round", now, "groups_total", len(di), "BAD", len(bad))
for x in bad:
    print("-", x["id"], "n=", x["n"], "files=", [f.split("/")[-1] for f in x["files"]])
    for l in x["locs"]:
        print("     ", l["file"].split("/")[-1], l["line"], "checked=", l["checked"])