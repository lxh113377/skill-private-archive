import json, os, shutil, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import check_r287m as C
items = C.load_patch()
_o, work, errs = C.replay(items)
if errs:
    raise SystemExit("FATAL: replay errs " + errs[0])
dst = os.path.join(D, "_landed_preview")
if os.path.isdir(dst):
    shutil.rmtree(dst)
shutil.copytree(C.SKILL_ROOT, dst)
for p, t in work.items():
    q = os.path.join(dst, os.path.relpath(p, C.SKILL_ROOT).replace(chr(92), os.sep))
    open(q, "w", encoding="utf-8", newline="").write(t)
shutil.copyfile(C.NEW_STAGED, os.path.join(dst, "reference", "node_mcp_server_v2.md"))
man = json.load(open(os.path.join(D, "newfile_manifest.json"), encoding="utf-8"))
man2 = dict(man)
man2["local_target"] = os.path.join(dst, "reference", "node_mcp_server_v2.md")
json.dump(man2, open(os.path.join(dst, "_manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("preview bytes", sum(os.path.getsize(os.path.join(r, f)) for r, _d, fs in os.walk(dst) for f in fs))
