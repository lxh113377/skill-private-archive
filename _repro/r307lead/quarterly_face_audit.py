import glob, io, json, subprocess
NL2 = chr(10)
# 1) 面里全部 audit 件：来源（git 最近提交）+ schema + 时标
for p in sorted(glob.glob("06-benchmark/quarterly*/2026Q4/audit.json")) + sorted(glob.glob("06-benchmark/quarterly*/audit.json")):
    try:
        d = json.load(io.open(p, encoding="utf-8"))
    except Exception as e:
        print("   %-52s 读不出 %s" % (p, repr(e)[:50])); continue
    g = subprocess.run(["git", "log", "--oneline", "-1", "--", p], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()
    print("   %-52s schema=%-34s gen=%s" % (p, str(d.get("schema"))[:34], str(d.get("generated_at"))[:19]))
    print("        git: %s" % (g[:100] or "(未跟踪)"))
# 2) 看门狗自己报的 newest 与口径
print()
r = subprocess.run([__import__("sys").executable, "05-exec/r260_quarterly_cadence.py", "--json", "_repro/r307lead/r307_cad3.json"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
for l in (r.stdout or "").splitlines()[-3:]:
    print("   [CADENCE] " + l[:130])
d = json.load(io.open("_repro/r307lead/r307_cad3.json", encoding="utf-8"))
print("   newest_audit =", d.get("newest_audit"))
print("   rc =", d.get("rc"), "| reading =", json.dumps(d.get("reading"), ensure_ascii=False)[:150])

