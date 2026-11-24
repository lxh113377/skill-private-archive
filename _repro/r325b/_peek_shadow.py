# -*- coding: utf-8 -*-
import io, json
p = "06-benchmark/replacement_matrix_shadowstrict.json"
d = json.load(io.open(p, encoding="utf-8-sig"))
print("schema=", d.get("schema"))
print("cmd=", d.get("cmd"))
print("generated_at=", d.get("generated_at"))
print("rows_n=", len(d.get("rows", [])))
print("conservation=", json.dumps(d.get("conservation"), ensure_ascii=False)[:300])
print("face=", json.dumps(d.get("face"), ensure_ascii=False, indent=1)[:1500])
print("license_face=", json.dumps(d.get("license_face"), ensure_ascii=False)[:600])
print("maintenance_face=", json.dumps(d.get("maintenance_face"), ensure_ascii=False)[:600])
r0 = d.get("rows", [{}])[0]
print("row0_keys=", sorted(r0.keys()))
print("row0_sample=", json.dumps(r0, ensure_ascii=False)[:1200])