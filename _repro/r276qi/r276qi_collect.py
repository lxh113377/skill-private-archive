# -*- coding: utf-8 -*-
"""r276 quarterly-inspection dryrun collector (read-only).

Why: the quarterly inspection must report a per-face coverage reading AND must never read a
missing input face as "no gap". This collector turns four on-disk faces plus the cadence file
into a machine-checkable reading; any face whose input file is absent or unreadable becomes
UNVERIFIED (R247) and the process exits 2 - a missing face is a finding, not a green.
"""
import argparse, io, json, os, sys, datetime

BENCH_DEFAULT = r"C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/06-benchmark"
SKILLS_DEFAULT = "D:/global_skills"

FACES = [
  ("F1", "版本通道一(tag)", "r263_declared_upstream_face.json"),
  ("F2", "版本通道二(提交级)", "r271_version_channel2.json"),
  ("F3", "替代面(候选池矩阵)", "r262_matrix_bodied.json"),
  ("F4", "替代面(侧车语义)", "r264_sidecar_semantics.json"),
  ("F5", "巡检节奏面", "quarterly_cadence_latest.json"),
]

def readj(p):
    try:
        return json.load(io.open(p, encoding="utf-8-sig"))
    except Exception:
        return None

def scan_registry(root):
    if not root or not os.path.isdir(root):
        return None
    out = []
    for n in sorted(os.listdir(root)):
        d = os.path.join(root, n)
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, "SKILL.md")):
            out.append(n)
    return out

def build(bench, skills_root):
    reg = scan_registry(skills_root)
    side = []
    if reg:
        side = [n for n in reg if os.path.isfile(os.path.join(skills_root, n, ".upstream"))]
    docs = {}
    faces = []
    for fid, fname, fn in FACES:
        p = os.path.join(bench, fn)
        if not os.path.isfile(p):
            st, doc = "ABSENT", None
        else:
            doc = readj(p)
            st = "OK" if doc is not None else "UNREADABLE"
        docs[fid] = doc if st == "OK" else None
        face = {"id": fid, "face": fname, "file": fn, "input_state": st}
        if st != "OK":
            face.update({"denom_kind": "不可定（输入件不可取）", "denom": None,
                         "covered": None, "uncovered": None, "uncovered_names": [],
                         "verdict": "UNVERIFIED", "never_green": True,
                         "note": "R247: 输入件 " + st + " => UNVERIFIED，禁止读成无缺口"})
            faces.append(face)
            continue
        rows = doc.get("rows") or []
        if fid == "F1":
            comp = [r for r in rows if r.get("rel") in ("BEHIND", "AHEAD", "SAME")]
            unc = [r for r in rows if r.get("rel") not in ("BEHIND", "AHEAD", "SAME")]
            face.update({"denom_kind": "版本通道入口(A)=在册且声明 .upstream 的 skill；登记库口径(B)=在册带 SKILL.md 的 skill",
                         "denom": len(rows),
                         "denom_registry": len(reg) if reg is not None else None,
                         "entry_uncovered_n": (len(reg) - len(rows)) if reg is not None else None,
                         "covered": len(comp), "uncovered": len(unc),
                         "uncovered_names": [r.get("skill") for r in unc][:10],
                         "by_rel": doc.get("by_rel"), "verdict": "OK"})
        elif fid == "F2":
            unc = [r for r in rows if r.get("verdict") == "UNAVAILABLE"]
            cov = [r for r in rows if r.get("verdict") != "UNAVAILABLE"]
            dsrc = {}
            for r in rows:
                k = r.get("date_source")
                dsrc[k] = dsrc.get(k, 0) + 1
            face.update({"denom_kind": "继承 F1 面入口（有 .upstream 的 55 件）；不含 136 件无侧车余量",
                         "denom": len(rows), "covered": len(cov), "uncovered": len(unc),
                         "uncovered_names": [r.get("skill") for r in unc][:10],
                         "by_verdict": doc.get("by_verdict"),
                         "unknown_release_n": doc.get("unknown_release_n"),
                         "unknown_release_covered_n": doc.get("unknown_release_covered_n"),
                         "date_source_mix": dsrc,
                         "capped_n": sum(1 for r in rows if r.get("capped")), "verdict": "OK"})
        elif fid == "F3":
            by = (doc.get("conservation") or {}).get("by_verdict") or {}
            unc_names = [r.get("slug") for r in rows if r.get("verdict") == "NO_OS_CANDIDATE"]
            fam_names = [r.get("slug") for r in rows if r.get("verdict") == "FAMILY_ONLY"]
            face.update({"denom_kind": "全登记库技能件（矩阵 face.local_n=191，与带 SKILL.md 扫描同分母）",
                         "denom": (doc.get("face") or {}).get("local_n") or len(rows),
                         "covered": by.get("MATCHED", 0), "partial": by.get("FAMILY_ONLY", 0),
                         "uncovered": by.get("NO_OS_CANDIDATE", 0) + by.get("UNVERIFIED", 0),
                         "uncovered_names": unc_names[:10], "partial_names": fam_names[:10],
                         "by_verdict": by,
                         "maintenance_trimmed_total": (doc.get("maintenance_face") or {}).get("trimmed_total"),
                         "maintenance_rows_affected": (doc.get("maintenance_face") or {}).get("rows_affected"),
                         "verdict": "OK"})
        elif fid == "F4":
            unc = [r for r in rows if r.get("semantics") == "UNKNOWN"]
            cov = [r for r in rows if r.get("semantics") != "UNKNOWN"]
            face.update({"denom_kind": "继承 F1 面入口（55 件有 .upstream 的 skill）",
                         "denom": len(rows), "covered": len(cov), "uncovered": len(unc),
                         "uncovered_names": [r.get("skill") for r in unc][:10],
                         "by_semantics": doc.get("by_semantics"),
                         "same_lineage_behind_n": len(doc.get("same_lineage_behind") or []),
                         "verdict": "OK"})
        elif fid == "F5":
            rc = doc.get("rc")
            face.update({"denom_kind": "受监控季产物面（quarterly*/audit.json 取最新一份）",
                         "denom": 1 if doc.get("newest_audit") else 0,
                         "covered": 1 if rc == 0 else 0, "uncovered": 0 if rc == 0 else 1,
                         "uncovered_names": [] if rc == 0 else [(doc.get("newest_audit") or "无季产物")],
                         "reading": doc.get("reading"), "newest_audit": doc.get("newest_audit"),
                         "watch_scope": ["quarterly*/audit.json"], "max_days": doc.get("max_days"),
                         "verdict": "OK" if rc == 0 else ("FAIL" if rc == 1 else "UNVERIFIED")})
        faces.append(face)
    joins = None
    if all(docs.get(f) is not None for f, _, _ in FACES) and reg is not None:
        behind = set(r.get("skill") for r in docs["F1"]["rows"] if r.get("rel") == "BEHIND")
        moved = set(r.get("skill") for r in docs["F2"]["rows"] if r.get("verdict") == "UPSTREAM_MOVED")
        same = set(r.get("skill") for r in docs["F4"]["rows"] if r.get("semantics") == "SAME_LINEAGE")
        notag = set(r.get("skill") for r in docs["F1"]["rows"] if r.get("rel") == "UNKNOWN_UPSTREAM_RELEASE")
        matched = set(r.get("slug") for r in docs["F3"]["rows"] if r.get("verdict") == "MATCHED")
        noos = set(r.get("slug") for r in docs["F3"]["rows"] if r.get("verdict") == "NO_OS_CANDIDATE")
        noside = set(reg) - set(side)
        joins = {
          "落后且同源(BEHIND x SAME_LINEAGE)": sorted(behind & same),
          "落后且上游动了(BEHIND x UPSTREAM_MOVED)": sorted(behind & moved),
          "无tag但上游动了(UNKNOWN_RELEASE x UPSTREAM_MOVED)": sorted(notag & moved),
          "无侧车且无替代候选(NOSIDE x NO_OS_CANDIDATE)": sorted(noside & noos),
          "无侧车但有件级替代(NOSIDE x MATCHED)": sorted(noside & matched),
          "无侧车件数": len(noside),
        }
    unv = [f["id"] for f in faces if f["verdict"] == "UNVERIFIED"]
    rc = 2 if unv else 0
    doc = {"schema": "r276-qi-stats-v1",
           "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           "bench_dir": bench, "skills_root": skills_root,
           "registry": {"with_skill_md": len(reg) if reg is not None else None,
                        "with_sidecar": len(side),
                        "without_sidecar": (len(reg) - len(side)) if reg is not None else None},
           "faces": faces, "joins": joins, "unverified_faces": unv, "rc": rc}
    return doc

def main():
    ap = argparse.ArgumentParser(prog="r276qi_collect.py")
    ap.add_argument("--bench-dir", default=BENCH_DEFAULT)
    ap.add_argument("--skills-root", default=SKILLS_DEFAULT)
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    doc = build(args.bench_dir, args.skills_root)
    for f in doc["faces"]:
        print("[FACE %s] %-22s %-10s denom=%s covered=%s uncovered=%s" % (
              f["id"], f["face"], f["input_state"], f["denom"], f["covered"], f["uncovered"]))
    if doc["joins"]:
        for k, v in doc["joins"].items():
            print("[JOIN] %-46s %s" % (k, (len(v) if isinstance(v, list) else v)))
    if args.out:
        io.open(args.out, "w", encoding="utf-8", newline=chr(10)).write(
            json.dumps(doc, ensure_ascii=False, indent=1))
        print("JSON ->", args.out)
    if doc["rc"] == 0:
        print("[QI:PASS] faces=%d unverified=0" % len(doc["faces"]))
    else:
        print("[QI:UNVERIFIED] faces=%d unverified=%s" % (len(doc["faces"]), doc["unverified_faces"]))
    return doc["rc"]

if __name__ == "__main__":
    sys.exit(main())