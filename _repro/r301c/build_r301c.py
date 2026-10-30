"""R301C 新鲜度面正式取数：只读既有缓存与本地正文，产出 fresh_scan.json。
写面：仅 _repro/r301c/。D:/global_skills 只读，D:/global_memory 不碰，禁 git 写。
版本解析用本体 r114_replacement_scan.parse_version；last_updated 用已有 r112_provenance_scan.fm_field（不另写解析器）。
"""
import base64
import io
import json
import os
import subprocess
import sys

BASE = r"C:\Users\37533\Desktop\workspace\skill焚诀\自建skill优化"
EXEC = os.path.join(BASE, "05-exec")
OUT = os.path.join(BASE, "_temp", "r301c")
ROOTS = r"D:\global_skills"
R299 = os.path.join(BASE, "_repro", "r299a", "results", "r299_inject_result.json")
GH_BIN = os.environ.get("GH_BIN") or r"C:\Program Files\GitHub CLI\gh.exe"

sys.path.insert(0, EXEC)
sys.path.insert(0, OUT)
import r114_replacement_scan as m
import fresh_judge as J

print("parse_version docstring:", (m.parse_version.__doc__ or "").replace(chr(10), " ")[:160])
print("parse_version 入参形态 = (text)，返回 version 串或 None")

FM_SRC = ""
try:
    import r112_provenance_scan as P
    fm_field = P.fm_field
    FM_SRC = "r112_provenance_scan.fm_field"
except Exception as exc:
    fm_field = None
    FM_SRC = "IMPORT_FAILED:" + repr(exc)
print("last_updated 解析器来源:", FM_SRC)


def read_text(path):
    try:
        return io.open(path, encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return None


def local_fields(slug):
    p = os.path.join(ROOTS, slug, "SKILL.md")
    text = read_text(p)
    if text is None:
        return None, None, p
    ver = m.parse_version(text)
    lu = fm_field(text, "last_updated") if fm_field else None
    return ver, J.norm_day(lu), p


def gh_contents(repo, path):
    """gh api repos/<repo>/contents/<path> 取正文（base64 解码）；返回 (text, sha, err)。"""
    url = "repos/%s/contents/%s" % (repo, path)
    try:
        r = subprocess.run([GH_BIN, "api", url], capture_output=True)
    except OSError as exc:
        return None, None, "SPAWN:" + repr(exc)
    err = r.stderr.decode("utf-8", "replace").strip()
    if r.returncode != 0:
        return None, None, "rc=%d stderr=%s" % (r.returncode, err[:400])
    try:
        doc = json.loads(r.stdout.decode("utf-8", "replace"))
    except Exception as exc:
        return None, None, "JSON:" + repr(exc)
    sha = doc.get("sha")
    content = doc.get("content")
    if content:
        raw = base64.b64decode(content).decode("utf-8", "replace")
        return raw, sha, ""
    sh = subprocess.run([GH_BIN, "api", url, "-H", "Accept: application/vnd.github.raw"], capture_output=True)
    if sh.returncode == 0 and sh.stdout:
        return sh.stdout.decode("utf-8", "replace"), sha, ""
    return None, sha, "no_content rc=%d stderr=%s" % (sh.returncode, sh.stderr.decode("utf-8", "replace")[:300])


def main():
    prov = {}
    cache = m.load_cache(prov=prov)
    data = json.load(io.open(R299, encoding="utf-8-sig", errors="replace"))
    rows = [r for r in data["rows"] if r.get("kind") == "lineage"]
    print("lineage rows =", len(rows))
    print("row keys =", sorted(rows[0].keys()))
    recs = []
    for r in rows:
        slug = r.get("slug")
        repo = r.get("repo") or ""
        ph = r.get("path_hit") or {}
        dp = (r.get("declared_path") or "").strip("/")
        path = ph.get("path") or ((dp + "/SKILL.md") if dp else "SKILL.md")
        ver, lu, lp = local_fields(slug)
        ent = cache.get("repo__" + m.key_of(repo)) if repo else None
        pushed = J.norm_day((ent or {}).get("pushed_at"))
        state = J.classify(lu, pushed)
        ev = "LOCAL parse_version(read(%s)) -> %s ; fm_field(text,last_updated) -> %s ; UPSTREAM load_cache()[repo__%s].pushed_at -> %s" % (lp, ver, lu, m.key_of(repo), pushed)
        recs.append({
            "slug": slug,
            "repo": repo,
            "path": path,
            "local_version": ver,
            "local_last_updated": lu,
            "upstream_pushed_at": pushed,
            "state": state,
            "evidence_cmd": ev,
        })
    fields = ["slug", "repo", "local_version", "local_last_updated", "upstream_pushed_at", "state", "evidence_cmd"]
    pairs = [{k: rec[k] for k in fields} for rec in recs]
    ranked = sorted([rec for rec in recs if rec["upstream_pushed_at"]], key=lambda x: x["upstream_pushed_at"], reverse=True)
    samples = []
    for rec in ranked[:12]:
        up, sha, err = gh_contents(rec["repo"], rec["path"])
        evc = "gh api repos/%s/contents/%s -> base64 decode -> parse_version" % (rec["repo"], rec["path"])
        if up is None:
            samples.append({"slug": rec["slug"], "repo": rec["repo"], "path": rec["path"], "upstream_version": None, "sha": sha, "sampled_state": "UNVERIFIED", "evidence_cmd": evc, "stderr": err})
        else:
            samples.append({"slug": rec["slug"], "repo": rec["repo"], "path": rec["path"], "upstream_version": m.parse_version(up), "sha": sha, "sampled_state": "VERIFIED", "evidence_cmd": evc, "stderr": ""})
    meta = {
        "tool": "r301c freshness face",
        "rules": "upstream_pushed_at > local_last_updated => BEHIND; == => CURRENT; < => LOCAL_AHEAD; either None => UNKNOWN; version 不参与判定",
        "fm_src": FM_SRC,
        "cache_prov": prov,
        "load_cache_doc": (m.load_cache.__doc__ or "").replace(chr(10), " ")[:100],
    }
    out = {"meta": meta, "pairs": pairs, "samples": samples}
    io.open(os.path.join(OUT, "fresh_scan.json"), "w", encoding="utf-8", newline=chr(10)).write(json.dumps(out, ensure_ascii=False, indent=1))
    from collections import Counter
    c = Counter(p["state"] for p in pairs)
    print("PAIRS", len(pairs), dict(c))
    print("SAMPLES attempted=%d verified=%d" % (len(samples), sum(1 for s in samples if s["sampled_state"] == "VERIFIED")))
    for s in samples:
        print("SAMPLE %s %s %s ver=%s sha=%s %s" % (s["slug"], s["repo"], s["sampled_state"], s["upstream_version"], s["sha"], (s["stderr"] or "")[:200]))
    return 0


if __name__ == "__main__":
    sys.exit(main())