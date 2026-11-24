# -*- coding: utf-8 -*-
import io, json, os, glob
out = []
for p in sorted(glob.glob("06-benchmark/**/replacement_matrix*.json", recursive=True)):
    row = {"path": p.replace(os.sep, "/"), "bytes": os.path.getsize(p)}
    try:
        d = json.load(io.open(p, encoding="utf-8-sig"))
        row["generated_at"] = d.get("generated_at")
        row["schema"] = d.get("schema")
        row["cmd"] = str(d.get("cmd"))[:120]
        row["rows_n"] = len(d.get("rows", [])) if isinstance(d.get("rows"), list) else None
        row["face"] = d.get("face") if isinstance(d.get("face"), dict) else None
        row["extra_keys"] = sorted(d.keys())
    except Exception as e:
        row["error"] = type(e).__name__ + ":" + str(e)[:80]
    out.append(row)
print(json.dumps(out, ensure_ascii=False, indent=1))