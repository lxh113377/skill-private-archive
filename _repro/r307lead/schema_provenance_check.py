import io, json
# 核 SOP 里那句「四件全是 r113 本体系真产物」的硬依据：schema 键一致性 + 与今日 r113 实跑件对键
today = json.load(io.open("_repro/r307lead/r113.json", encoding="utf-8"))
tk = set(today.keys())
ts = today.get("schema")
print("今日 r113 实跑件 schema =", ts, "| steps 自述 =", [k for k in tk if "step" in k.lower() or "face" in k.lower()][:6])
for p in ("06-benchmark/quarterly/2026Q4/audit.json", "06-benchmark/quarterly_r260c/2026Q4/audit.json"):
    d = json.load(io.open(p, encoding="utf-8"))
    print("%-48s schema=%s | 键数=%d | 与今日键集差=%s" % (p, d.get("schema"), len(d), sorted(set(d.keys()) ^ tk)[:6]))

