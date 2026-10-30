# -*- coding: utf-8 -*-
import os, re, json, sys, datetime

ROOT = "D:/global_skills"
SKIP_DIRS = {".git","node_modules","__pycache__",".venv","venv","dist","build","_trash"}

CLAIM_RE = re.compile("NON-NEGOTIABLE|MUST|必须|禁止|强制", re.I)
ASSERT_RE = re.compile("NON-NEGOTIABLE|MUST|必须|禁止|强制|never|always|fixed|only|不得|不准|严禁|required|一律", re.I)
NEG_RE = re.compile("禁止|不得|不准|绝不|严禁|不能|不可|不要|禁用|无需|never|must not|do not|without|avoid", re.I)
POS_RE = re.compile("必须|强制|务必|一定要|必需|required|always|shall|must|non-negotiable", re.I)
TERM_RE = re.compile("[.!?;:。！？；：]$")

AXES = [
  ("AXIS_LAYOUT_STAGE", re.compile("viewport|100vh|100vw|fluid|responsive|vw|vh", re.I), re.compile("fixed|1920|1080|stage", re.I)),
  ("AXIS_SCROLL", re.compile("no scroll|never scroll|禁止滚动|不滚动|不要滚动|without scroll", re.I), re.compile("scroll|滚动", re.I)),
  ("AXIS_INSTALL", re.compile("pip install|npm install|uv pip|安装依赖", re.I), re.compile("不安装|no install|禁止安装|零依赖|zero depend|无依赖|不装", re.I)),
  ("AXIS_LOCAL_REMOTE", re.compile("本地|offline|local", re.I), re.compile("云端|在线|cloud|remote", re.I)),
  ("AXIS_INTERACT", re.compile("askuserquestion|问用户|询问用户|先问|确认后", re.I), re.compile("不询问|不问|自行决定|自动完成|no question|不确认", re.I)),
]

RESOLVED_MARKERS = ["已消解","已由","原冲突","原先","历史","不再","已迁","R268","R269","R272","旧范式","已修","已对齐","superseded","deprecated","was originally"]
CJK_STOP = set()
for w in ["必须","禁止","强制","的是","可以","使用","需要","不要","不是","这个","进行","通过","如果","因为","所以","并且","或者","以及","对于","我们","他们","已经","没有","所有","任何","每个","这些","那些","包含","应当","应该","不能","只能","一定","都是","就是","要求","确保","不得","一律","用户","文件","内容","输出","结果","模式","支持","默认","版本","说明","规则","检查","执行","生成","任务","工作","目录","路径","名称","方式","情况","时候","问题","错误","方法","功能","示例","如下","以上","以下","中的","一个","两个","其他","相同","不同","同时","进一步","只有","也就是","一个","应用","项目","数据","代码","相关","以后","之前","开始","结束","是否","另外","例如","比如","目前","现在","以后"]:
    CJK_STOP.add(w)
LAT_STOP = {"the","and","for","with","that","this","from","are","you","all","any","use","has","have","can","will","its","but","must","never","always","only","required","fixed","into","may","one"}

def _add_lat(out, w):
    if len(w) >= 3 and w not in LAT_STOP:
        out.add(w)

def _add_cjk(out, run):
    if len(run) < 2:
        return
    for i in range(len(run) - 1):
        bg = run[i:i+2]
        if bg not in CJK_STOP:
            out.add(bg)

def toks(s):
    out = set()
    bl = ""
    bc = ""
    for ch in s.lower():
        o = ord(ch)
        if ch.isascii() and ch.isalnum():
            if bc:
                _add_cjk(out, bc); bc = ""
            bl += ch
        elif 0x4e00 <= o <= 0x9fff:
            if bl:
                _add_lat(out, bl); bl = ""
            bc += ch
        else:
            if bl:
                _add_lat(out, bl); bl = ""
            if bc:
                _add_cjk(out, bc); bc = ""
    if bl:
        _add_lat(out, bl)
    if bc:
        _add_cjk(out, bc)
    return out

def strong_shared(shared):
    for t in shared:
        if not t.isascii() and len(t) == 2:
            return True
        if t.isascii() and len(t) >= 5:
            return True
    return False

DIM_RE = re.compile("([0-9]{2,4})[ ]*[xX×][ ]*([0-9]{2,4})")

def dims(s):
    return [m.group(0).lower().replace(" ","") for m in DIM_RE.finditer(s)]

def classify(ctext, ktext):
    for name, a, b in AXES:
        ca = bool(a.search(ctext)); cb = bool(b.search(ctext))
        if ca and not cb and b.search(ktext):
            return name
        if cb and not ca and a.search(ktext):
            return name + "_rev"
    cp = "pos" if POS_RE.search(ctext) else ("neg" if NEG_RE.search(ctext) else "none")
    kp = "pos" if POS_RE.search(ktext) else ("neg" if NEG_RE.search(ktext) else "none")
    if cp != kp and cp != "none" and kp != "none":
        return "POLARITY_FLIP"
    dc = dims(ctext); dk = dims(ktext)
    if dc and dk and sorted(set(dc)) != sorted(set(dk)):
        return "DIM_MISMATCH"
    return None

def kind_for(opp, shared, scope, flags, res_markers):
    if res_markers or "in_version_section" in flags:
        return "RESOLVED_OR_HISTORICAL"
    if "in_code_fence" in flags or "is_quote" in flags:
        return "WEAK"
    if opp.startswith("AXIS") and shared:
        return "REAL_CONFLICT" if scope == "pkg" else "WEAK"
    return "WEAK"

def trunc(s, n=300):
    s = s.strip()
    return s if len(s) <= n else s[:n] + "..."

def read_text(fp):
    with open(fp, "rb") as f:
        raw = f.read()
    if b"\x00" in raw[:4096]:
        return None
    return raw.decode("utf-8", "replace")

unverified = []
rows = []
coverage = []
canonical = {}

def slug_dirs():
    for n in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, n)
        if os.path.isdir(p) and os.path.isfile(os.path.join(p, "SKILL.md")):
            yield n, p

for slug, sd in slug_dirs():
    try:
        sk = read_text(os.path.join(sd, "SKILL.md"))
    except Exception as e:
        unverified.append({"slug": slug, "file": "SKILL.md", "error": str(e)})
        continue
    if sk is None:
        unverified.append({"slug": slug, "file": "SKILL.md", "error": "binary-or-unreadable"})
        continue
    lines = sk.splitlines()
    claims = []
    in_fence = False
    section = ""
    for i, l in enumerate(lines):
        st = l.strip()
        if st.startswith("```"):
            in_fence = not in_fence
            continue
        if st.startswith("#"):
            section = st
        if CLAIM_RE.search(l):
            flags = []
            if in_fence:
                flags.append("in_code_fence")
            if st.startswith(">"):
                flags.append("is_quote")
            if st.startswith("|"):
                flags.append("is_table")
            low = section.lower()
            if ("版本" in section) or ("changelog" in low) or ("version history" in low) or ("更新日志" in section):
                flags.append("in_version_section")
            lo = max(0, i - 5); hi = min(len(lines), i + 6)
            win = "\n".join(lines[lo:hi])
            rmk = [m for m in RESOLVED_MARKERS if m in l]
            claims.append({"line": i + 1, "text": l, "flags": flags, "res_markers": rmk, "toks": toks(l)})
    counters = []
    cfiles = set()
    for dp, dns, fns in os.walk(sd):
        dns[:] = [x for x in dns if x not in SKIP_DIRS]
        for fn in fns:
            low = fn.lower()
            if not (low == "readme.md" or low.endswith(".js") or low.endswith(".css")):
                continue
            fp = os.path.join(dp, fn)
            rel = os.path.relpath(fp, sd).replace(os.sep, "/")
            cfiles.add(rel)
            try:
                sz = os.path.getsize(fp)
            except Exception as e:
                unverified.append({"slug": slug, "file": rel, "error": str(e)}); continue
            if sz > 2000000:
                continue
            try:
                txt = read_text(fp)
            except Exception as e:
                unverified.append({"slug": slug, "file": rel, "error": str(e)}); continue
            if txt is None:
                continue
            scope = "references" if rel.startswith("references/") else "pkg"
            cl = txt.splitlines()
            for j, l in enumerate(cl):
                if not ASSERT_RE.search(l):
                    continue
                blk = [l]
                m = j + 1
                while m < len(cl) and len(blk) < 3 and not TERM_RE.search(blk[-1].rstrip()) and cl[m].strip():
                    blk.append(cl[m]); m += 1
                jt = " ".join(blk)
                counters.append({"file": rel, "line": j + 1, "text": jt, "scope": scope, "toks": toks(jt)})
    best = {}
    for c in claims:
        per_claim = []
        for k in counters:
            opp = classify(c["text"], k["text"])
            if not opp:
                continue
            shared = sorted(c["toks"] & k["toks"])
            if opp.startswith("AXIS") and not shared:
                continue
            if opp == "POLARITY_FLIP" and not strong_shared(shared):
                continue
            if opp == "DIM_MISMATCH" and not strong_shared(shared):
                continue
            prio = 0 if opp.startswith("AXIS") else (2 if opp == "DIM_MISMATCH" else 1)
            scopep = 0 if k["scope"] == "pkg" else 1
            readmep = 0 if k["file"].lower().endswith("readme.md") else 1
            per_claim.append((prio, scopep, readmep, -len(shared), k["file"], k["line"], opp, k, shared))
        per_claim.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4], t[5]))
        seen_files = set()
        picked = 0
        for t in per_claim:
            if picked >= 4:
                break
            k = t[7]
            if k["file"] in seen_files:
                continue
            seen_files.add(k["file"])
            picked += 1
            rows.append({
                "slug": slug,
                "claim_line": c["line"],
                "claim_text": trunc(c["text"]),
                "counter_file": k["file"],
                "counter_line": k["line"],
                "counter_text": trunc(k["text"]),
                "kind": kind_for(t[6], t[8], k["scope"], c["flags"], c["res_markers"]),
                "opposition": t[6],
                "shared_tokens": t[8][:8],
                "counter_scope": k["scope"],
                "claim_flags": c["flags"],
                "resolved_markers": c["res_markers"],
                "machine_judged": True,
                "human_read": False,
                "human_judgment": None,
            })
    coverage.append({"slug": slug, "claims": len(claims), "counter_assertions": len(counters), "counter_files": len(cfiles), "rows": len([r for r in rows if r["slug"] == slug])})
    if slug == "frontend-slides":
        canonical["frontend-slides"] = {
            "claim_189_present": any(c["line"] == 189 for c in claims),
            "claim_189_resolved_markers": [c["res_markers"] for c in claims if c["line"] == 189],
            "readme_67_present": any(k["file"] == "bold-template-pack/README.md" and k["line"] == 67 for k in counters),
            "counter_files": sorted(cfiles),
        }
    if slug == "brand-guidelines":
        canonical["brand-guidelines"] = {"claims": len(claims), "counter_files": sorted(cfiles)}

counts = {}
for r in rows:
    counts[r["kind"]] = counts.get(r["kind"], 0) + 1
stats = {
  "slugs_with_skill_md": len(coverage),
  "slugs_with_claims": len([c for c in coverage if c["claims"] > 0]),
  "slugs_with_counter_files": len([c for c in coverage if c["counter_files"] > 0]),
  "slugs_with_rows": len(set(r["slug"] for r in rows)),
  "total_counter_files": sum(c["counter_files"] for c in coverage),
  "unverified_files": len(unverified),
}
out = {
  "schema": "contract-vs-impl-v1",
  "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
  "provenance_cmd": " ".join(sys.argv),
  "stats": stats,
  "rows": rows,
  "counts_by_kind": counts,
  "sampled_human_read": [],
  "coverage": coverage,
  "unverified": unverified,
  "canonical_checks": canonical,
}
outpath = sys.argv[2] if len(sys.argv) > 2 else "_repro/r276qi/work/r276_rows.json"
with open(outpath, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("stats", json.dumps(stats, ensure_ascii=False))
print("counts", json.dumps(counts, ensure_ascii=False), "rows", len(rows))
print("canonical", json.dumps(canonical, ensure_ascii=False)[:900])
print("--- rows ---")
for r in rows:
    print(r["slug"], r["claim_line"], "|", r["kind"], "|", r["opposition"], "|", r["counter_file"] + ":" + str(r["counter_line"]), "|", r["shared_tokens"][:4])