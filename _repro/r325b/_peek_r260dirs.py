import io,json
for p in ["06-benchmark/quarterly_r260c/2026Q4/audit.json","06-benchmark/quarterly_r260b/2026Q4/audit.json","06-benchmark/quarterly_r260/2026Q4/audit.json"]:
    d=json.load(io.open(p,encoding="utf-8-sig"))
    print(p, "| schema=",d.get("schema"),"| quarter=",d.get("quarter"),"| generated_at=",d.get("generated_at"))
    print("   keys=",sorted(d.keys()))
    print("   cmd=",str(d.get("cmd"))[:160])
    print("   steps_n=",len(d.get("steps",[])) if isinstance(d.get("steps"),list) else "n/a")