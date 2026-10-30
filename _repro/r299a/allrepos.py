import io, os, re, json
MG = "D:/global_skills"
RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
repos, per = set(), {}
for name in sorted(os.listdir(MG)):
    p = os.path.join(MG, name, ".upstream")
    if not os.path.isfile(p):
        continue
    rs = []
    for raw in io.open(p, encoding="utf-8-sig", errors="replace").read().splitlines():
        ln = raw.strip()
        if not ln or ln.lower().startswith("path:"):
            continue
        if RE.match(ln):
            rs.append(ln)
    if rs:
        per[name] = rs
        repos.update(rs)
io.open("_temp/r299a/all_declared_repos.txt", "w", encoding="utf-8").write("\n".join(sorted(repos)) + "\n")
print("sidecars with declared repos =", len(per), "| distinct repos =", len(repos))
COL = json.load(io.open("_temp/r299a/tree_paths.json", encoding="utf-8"))
new = sorted(repos - set(COL.keys()))
io.open("_temp/r299a/need_more.txt", "w", encoding="utf-8").write("\n".join(new) + "\n")
print("尚未采集 =", len(new))
for x in new:
    print("   ", x)
multi = {k: v for k, v in per.items() if len(v) > 1}
print("多仓侧车件数 =", len(multi))
for k, v in list(multi.items())[:6]:
    print("   %-16s %s" % (k, v))

