import sys, os, json
BASE = r"C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
EXEC = os.path.join(BASE, "05-exec")
sys.path.insert(0, EXEC)
import r114_replacement_scan as m
print("PV_DOC:", (m.parse_version.__doc__ or "").replace("\n"," ")[:150])
print("LC_DOC:", (m.load_cache.__doc__ or "").replace("\n"," ")[:80])
cache = m.load_cache()
print("cache n =", len(cache))
rk = sorted([k for k in cache if k.startswith("repo__")])
print("repo__ keys n =", len(rk), "sample:", rk[:4])
e = cache[rk[0]]
print("entry type:", type(e).__name__)
print("entry keys:", sorted(e.keys()) if isinstance(e, dict) else repr(e)[:200])
print("pushed_at =", e.get("pushed_at"), "| stars =", e.get("stars"), "| license =", e.get("license"))
p = os.path.join(BASE, "_repro", "r299a", "results", "r299_inject_result.json")
d = json.load(open(p, encoding="utf-8"))
rows = [r for r in d["rows"] if r.get("kind") == "lineage"]
print("lineage n =", len(rows))
for r in rows[:3]:
    print(json.dumps({k: r.get(k) for k in ("slug","repo","declared_path","slug_hits","path_hit")}, ensure_ascii=False))
repos = sorted(set(r["repo"] for r in rows if r.get("repo")))
miss = [rp for rp in repos if "repo__" + m.key_of(rp) not in cache]
print("lineage repos n =", len(repos), "missing =", miss)
print("local skill dir exists n:", sum(1 for r in rows if os.path.isfile(os.path.join(r"D:\global_skills", r["slug"], "SKILL.md"))))