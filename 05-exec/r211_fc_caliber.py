# -*- coding: utf-8 -*-
"""r211_fc_caliber.py — fc 维口径对账（生产口径 vs 正确口径），R211-9 的复算入口。r211 一手取证。

    产物落 06-benchmark/fc_caliber_r211.json（禁落 _temp：那正是本轮 R211-7 登记的「死句柄」形态 —— 一次性件活在会被清场的目录里）。：生产 skill_md_n 的 endswith("skill.md") 会把 create-skill.md/BOOTSTRAP_SKILL.md
算成技能。本件用两种口径同时数，量化被高估多少。GH 调用走 subprocess 列表传参（不经 shell）。"""
import json, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "06-benchmark", "fc_caliber_r211.json")
GH = r"C:\Program Files\GitHub CLI\gh.exe"
REPOS = ["yusufkaraaslan/Skill_Seekers","plugin87/ux-ui-agent-skills","arjun988/blender-skills",
         "affaan-m/ECC","genspark-ai/genoffice","scenario-labs/skills","wiltodelta/remove-ai-watermarks",
         "obra/superpowers","iOfficeAI/OfficeCLI","EL4CTEO/blender-skills","RobLe3/cc-blender-skill"]
def name_ok(p):  # 正确口径：文件名恰为 SKILL.md（大小写不敏感）
    return p.rsplit("/", 1)[-1].lower() == "skill.md"
rows = []
for r in REPOS:
    try:
        p = subprocess.run([GH, "api", "repos/%s/git/trees/HEAD?recursive=1" % r],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
        d = json.loads(p.stdout)
        blobs = [x["path"] for x in d.get("tree", []) if x.get("type") == "blob"]
        prod = [x for x in blobs if x.lower().endswith("skill.md")]          # 生产口径
        corr = [x for x in prod if name_ok(x)]                                 # 正确口径
        ghost = [x for x in prod if not name_ok(x)]
        rows.append({"repo": r, "prod_n": len(prod), "correct_n": len(corr), "ghost_n": len(ghost),
                     "ghost_sample": ghost[:3], "truncated": bool(d.get("truncated"))})
    except Exception as e:
        rows.append({"repo": r, "error": repr(e)[:80]})
json.dump(rows, open(OUT,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
infl = 0
for o in rows:
    if "error" in o: print("  ERR", o["repo"], o["error"]); continue
    if o["ghost_n"]:
        infl += 1
        print("  %-48s prod=%-5s correct=%-5s 高估=%-4s 例=%s" % (o["repo"], o["prod_n"], o["correct_n"], o["ghost_n"], o["ghost_sample"][:1]))
print("样本 %d 仓中 %d 仓被高估；truncated=%d" % (len(rows), infl, sum(1 for o in rows if o.get("truncated"))))
