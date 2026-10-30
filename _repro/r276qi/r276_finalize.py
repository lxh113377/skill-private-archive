# -*- coding: utf-8 -*-
import json, sys, datetime

d = json.load(open("_repro/r276qi/work/r276_rows.json", encoding="utf-8"))
rows = d["rows"]

HUMAN_PAIRS = set([
 ("browser-cdp",14),("cloudbase",50),("cloudbase",134),
 ("frontend-slides",17),("frontend-slides",81),("frontend-slides",189),("frontend-slides",311),
 ("ppt-master",103),("ppt-master",110),("ppt-master",161),
 ("story-deslop",16),("story-deslop",30),("story-import",17),
 ("story-review",86),("story-short-write",30),
])

OVERRIDE = {}
OVERRIDE[("frontend-slides",81,"viewport-base.css",20)] = ("REAL_CONFLICT", "人读：Mode C 第 81 行仍要求图片 max-height:min(50vh,400px)（视口相对），而 viewport-base.css:19-22 把 .slide 钉死为 1920px/1080px 固定舞台（行内注释 not by the viewport / dvh sizing removed）—— vh 单位在固定舞台范式下失去参照。更强旁证 = 同件 SKILL.md:83 残留旧句 images have viewport-relative max-height。判 REAL_CONFLICT。")
OVERRIDE[("frontend-slides",189,"bold-template-pack/README.md",67)] = ("RESOLVED_OR_HISTORICAL", "人读：正文 189 行自述原冲突 R268-1 已由 R269-1 消解；包 README:67-69 明写 fixed 1920×1080（即使源模板原本 viewport-fluid）。该断言与正文当前 Fixed Stage 条款一致，仅与正文历史句（100vh Viewport Fitting）互斥 ⇒ 历史命中。")
OVERRIDE[("frontend-slides",189,"viewport-base.css",20)] = ("RESOLVED_OR_HISTORICAL", "人读：counter 行带 R269-1 注释，是消解后的固定舞台实现；仅与正文历史句互斥 ⇒ 历史命中。")
OVERRIDE[("frontend-slides",189,"bold-template-pack/deck-stage.js",10)] = ("RESOLVED_OR_HISTORICAL", "人读：deck-stage.js 头注释 fixed design size 1920×1080 scaled to fit viewport；与正文当前条款一致，仅与历史句互斥 ⇒ 历史命中。")

for r in rows:
    k3 = (r["slug"], r["claim_line"], r["counter_file"], r["counter_line"])
    k2 = (r["slug"], r["claim_line"])
    if k3 in OVERRIDE:
        r["kind"], note = OVERRIDE[k3]
    elif k2 in HUMAN_PAIRS:
        if r["kind"] == "RESOLVED_OR_HISTORICAL":
            r["kind"] = "WEAK"
        if r["slug"] == "browser-cdp":
            note = "人读：正文禁造命令（负）对 js 注释 agent:false 是必须的（正），仅 agent 一词巧合 ⇒ WEAK 假阳性（机判曾误标 RESOLVED，因相邻行含不再二字，已按同行口径纠正）。"
        elif r["slug"] == "cloudbase":
            note = "人读：正文讲 MCP/stdio 站点选择，counter 讲 app.storage 上传用法，共享词为巧合 ⇒ WEAK 假阳性。"
        elif r["slug"] == "ppt-master":
            note = "人读：正文术语表条目 vs 导出脚本 README 的 structure mode 描述，二者不互斥 ⇒ WEAK 假阳性。"
        elif r["slug"] == "story-deslop":
            note = "人读：正文删除保护条款 vs 检查脚本的套词/连接词 advisory 文案，主题巧合 ⇒ WEAK 假阳性。"
        elif r["slug"] == "story-import":
            note = "人读：正文 Agent 兼容性 blockquote vs 大纲契约脚本字段常量，顺序一词巧合 ⇒ WEAK 假阳性。"
        elif r["slug"] == "story-review":
            note = "人读：正文 prompt 自包含要求 vs 脚本 report-only 说明，主题巧合 ⇒ WEAK 假阳性。"
        elif r["slug"] == "story-short-write":
            note = "人读：正文正文格式规范 vs 小节编号检查器文案，同一主题无互斥 ⇒ WEAK 假阳性。"
        elif r["slug"] == "frontend-slides" and r["claim_line"] == 17:
            note = "人读：counter 为正固定舞台实现（deck-stage 生命周期注释 / STAGE SCALE 注释），与正文当前 Fixed Stage 条款同向、非互斥 ⇒ WEAK（同向，不构成冲突）。"
        elif r["slug"] == "frontend-slides" and r["claim_line"] == 311:
            note = "人读：正文要求 .slide 类名，counter 为 deck-stage 生命周期注释，同向无互斥 ⇒ WEAK。"
        else:
            note = "人读：无实质互斥 ⇒ WEAK。"
    else:
        note = None
    if k2 in HUMAN_PAIRS:
        r["human_read"] = True
        r["machine_judged"] = False
        r["human_judgment"] = note
    else:
        r["human_read"] = False
        r["machine_judged"] = True
        r["human_judgment"] = None
        r["unread_flag"] = "⚠️未人读"

counts = {}
for r in rows:
    counts[r["kind"]] = counts.get(r["kind"], 0) + 1
assert sum(counts.values()) == len(rows), "counts mismatch"

req = ["slug","claim_line","claim_text","counter_file","counter_line","counter_text","kind"]
for r in rows:
    for f in req:
        assert f in r and r[f] is not None, "missing field " + f

ind = {}
for r in rows:
    if r["slug"] == "frontend-slides" and r["claim_line"] == 189 and r["counter_file"] == "bold-template-pack/README.md":
        ind["frontend_slides_canonical"] = {"row": r, "kind": r["kind"]}
brand = [r for r in rows if r["slug"] == "brand-guidelines"]
ind["brand_guidelines"] = {"rows": len(brand), "verdict": ("PASS 无候选" if len(brand) == 0 else "FAIL")}

sampled = []
seen = set()
for r in rows:
    if r["human_read"] and r["slug"] not in seen:
        seen.add(r["slug"])
        rs = [x for x in rows if x["slug"] == r["slug"] and x["human_read"]]
        sampled.append({"slug": r["slug"], "human_read_rows": len(rs), "claim_lines": sorted(set(x["claim_line"] for x in rs)), "kinds": sorted(set(x["kind"] for x in rs))})

cov = d["coverage"]
stats = d["stats"]
stats["slugs_with_rows"] = len(set(r["slug"] for r in rows))
stats["human_read_rows"] = len([r for r in rows if r["human_read"]])
stats["machine_only_rows"] = len([r for r in rows if not r["human_read"]])

out = {
 "schema": "contract-vs-impl-v1",
 "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
 "provenance_cmd": "cd 自建skill优化 && PYTHONPYCACHEPREFIX=/tmp/pycache_r276 python -B _repro/r276qi/r276_scan.py _repro/r276qi/work/r276_rows.json ; python -B _repro/r276qi/r276_finalize.py",
 "disclaimer": "候选面（candidate surface），非缺陷结论：每行须人读后才可入缺陷台账；未人读行标 ⚠️未人读。",
 "corpus": {"root": "D:/global_skills", "skill_md_slugs": stats["slugs_with_skill_md"], "claim_slugs": stats["slugs_with_claims"], "counter_source_slugs": stats["slugs_with_counter_files"], "counter_files": stats["total_counter_files"], "counter_file_glob": "README.md / *.js / *.css（含 references/ 下同名 README）"},
 "detector": {"axes": ["AXIS_LAYOUT_STAGE","AXIS_SCROLL","AXIS_INSTALL","AXIS_LOCAL_REMOTE","AXIS_INTERACT"], "other_rules": ["POLARITY_FLIP（正/负极性词 + 强共享词）","DIM_MISMATCH（尺寸字面量不一致 + 强共享词）"], "claim_regex": "NON-NEGOTIABLE|MUST|必须|禁止|强制 (re.I)", "counter_assert_regex": "NON-NEGOTIABLE|MUST|必须|禁止|强制|never|always|fixed|only|不得|不准|严禁|required|一律 (re.I)", "axis_purity": "正文侧必须只站轴的一侧，两侧都站则跳过轴规则"},
 "stats": stats,
 "counts_by_kind": counts,
 "rows": rows,
 "sampled_human_read": sampled,
 "negative_controls": ind,
 "side_observations": [{"slug": "frontend-slides", "file": "SKILL.md", "line": 17, "note": "第 17 行行尾出现整句重复：No scrolling within slides, ever. Content overflows? Split into multiple slides. 出现两次 —— 疑为升级写入未去重，属文本残留，建议人读后入台账。"}, {"slug": "frontend-slides", "file": "SKILL.md", "line": 83, "note": "Mode C 第 4 条在同一行出现陈旧句与新句拼接：...images have viewport-relative max-height, 4. **After ANY modification, verify:** ...1920×1080 stage coordinates... —— 疑为 r272 迁移的行内残留；它是正文自相矛盾的文本残留（非 contract-vs-impl 行），建议人读后入台账。"}],
 "coverage": cov,
 "unverified": d["unverified"],
}
with open("06-benchmark/r276_contract_vs_impl_conflicts.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("ROWS", len(rows), "COUNTS", json.dumps(counts, ensure_ascii=False))
print("SUM_OK", sum(counts.values()) == len(rows))
print("HUMAN_SLUGS", len(sampled), "HUMAN_ROWS", stats["human_read_rows"])
print("FRONTEND_CANONICAL", json.dumps(ind["frontend_slides_canonical"]["kind"]))
print("BRAND", json.dumps(ind["brand_guidelines"]))
print("FIELDS_OK", True)
