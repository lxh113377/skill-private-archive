# -*- coding: utf-8 -*-
# r315 配对体检（gstack UNK-02 泛化）：吸收基线 52 对的 path_rule 配对是不是「同一功能族」？
# 判据：local(SKILL.md 行集) vs 上游声明路径(行集) 的重合率 = |交集| / min(两侧非空行数)。
# 重合率 < 0.10 的列为疑配（可能配错路径，如 gstack 的 capy 开局件 vs 本地 browse QA 手册）。
# 每对现拉 gh（~52 次），落 json 供裁定；gstack 额外并比根 browse/SKILL.md 找更优配对。
import base64, io, json, subprocess, sys
A = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
PY = "C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
MG = "D:/global_skills"
NL2 = chr(10)
def gh_content(repo, path):
    r = subprocess.run(["gh", "api", "repos/%s/contents/%s" % (repo, path), "--jq", ".content"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
    if r.returncode != 0:
        return None
    try:
        return base64.b64decode("".join((r.stdout or "").split())).decode("utf-8", "replace")
    except Exception:
        return None
def loc(rel):
    r = subprocess.run(["git", "-C", MG, "show", "HEAD:" + rel], capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None
def lines(t):
    return set(l.strip() for l in (t or "").split(NL2) if l.strip())
d = json.loads(io.open(A + "/_repro/r303a/absorption_baseline.json", encoding="utf-8").read())
rows = []
for p in d["pairs"]:
    slug, repo, upath = p["slug"], p["repo"], p.get("upstream_path") or "SKILL.md"
    lt = loc(slug + "/SKILL.md")
    ut = gh_content(repo, upath)
    if lt is None or ut is None:
        rows.append({"slug": slug, "overlap": None, "note": "fetch-miss"}); continue
    L, U = lines(lt), lines(ut)
    ov = len(L & U) / float(min(len(L), len(U))) if L and U else 0.0
    rows.append({"slug": slug, "repo": repo, "path": upath, "local_lines": len(L),
                 "up_lines": len(U), "overlap": round(ov, 4)})
sus = [r for r in rows if r.get("overlap") is not None and r["overlap"] < 0.10]
print("[PAIRSANITY] pairs=%d fetched=%d suspects(<0.10)=%d" % (len(rows), len([r for r in rows if r.get("overlap") is not None]), len(sus)))
for r in sorted([x for x in rows if x.get("overlap") is not None], key=lambda x: x["overlap"])[:14]:
    print("   %-22s %-40s overlap=%.3f" % (r["slug"], (r.get("repo") or "") + ":" + (r.get("path") or ""), r["overlap"]))
# gstack 专项：与根 browse/SKILL.md 的重合率（找更优配对）
gt = loc("gstack/SKILL.md")
for cand in ("capy/skill/gstack/SKILL.md", "browse/SKILL.md"):
    ut = gh_content("garrytan/gstack", cand)
    if ut and gt:
        L, U = lines(gt), lines(ut)
        print("   gstack vs %-28s overlap=%.4f (up %d 行)" % (cand, len(L & U) / float(min(len(L), len(U))), len(U)))
json.dump(rows, io.open(A + "/_temp/r315_pairing.json", "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
print("[SAVED] _temp/r315_pairing.json")
