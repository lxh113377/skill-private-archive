# -*- coding: utf-8 -*-
"""r325b probe: 只读取证 —— 四件产物的 mtime / generated_at / sha256 / 行数 + 今日差。"""
import io, json, os, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT.endswith("_repro"):
    pass
ITEMS = [
    "06-benchmark/quarterly_r260/2026Q4/replacement_matrix.json",
    "06-benchmark/replacement_matrix_shadowstrict.json",
    "06-benchmark/quarterly/2026Q4/audit.json",
    "06-benchmark/quarterly_cadence_latest.json",
    "06-benchmark/local_frontmatter.json",
    "06-benchmark/r276_quarterly_inspection_dryrun.json",
]

def sha12(p):
    import hashlib
    h = hashlib.sha256(io.open(p, "rb").read()).hexdigest()
    return h[:12]

def shallow_ts(doc, depth=0):
    """在顶层与 face 子键里找 generated_at，找不到就返回 None（不猜）。"""
    ts = doc.get("generated_at")
    if ts:
        return ts
    face = doc.get("face")
    if isinstance(face, dict) and face.get("generated_at"):
        return face.get("generated_at")
    return None

def main():
    out = {"root": ROOT, "probed_at": datetime.now().isoformat(timespec="seconds")}
    rows = []
    for rel in ITEMS:
        p = os.path.join(ROOT, rel)
        row = {"path": rel, "exists": os.path.exists(p)}
        if os.path.exists(p):
            row["bytes"] = os.path.getsize(p)
            row["lines"] = io.open(p, encoding="utf-8-sig", errors="replace").read().count(chr(10))
            row["mtime"] = datetime.fromtimestamp(os.path.getmtime(p)).isoformat(timespec="seconds")
            row["sha256_12"] = sha12(p)
            try:
                doc = json.load(io.open(p, encoding="utf-8-sig"))
                row["generated_at"] = shallow_ts(doc)
                row["top_keys"] = sorted(doc.keys())[:20] if isinstance(doc, dict) else None
            except Exception as e:
                row["parse_error"] = type(e).__name__ + ": " + str(e)[:120]
        rows.append(row)
    out["items"] = rows
    out["dirs"] = sorted([d for d in os.listdir(os.path.join(ROOT, "06-benchmark")) if d.startswith("quarterly")])
    io.open(os.path.join(ROOT, "_repro", "r325b", "probe_raw.json"), "w", encoding="utf-8", newline=chr(10)).write(json.dumps(out, ensure_ascii=False, indent=1))
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    print("DIRS", out["dirs"])
    return 0

if __name__ == "__main__":
    sys.exit(main())