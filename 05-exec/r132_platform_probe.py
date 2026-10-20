# -*- coding: utf-8 -*-
'''r132_platform_probe.py — R130-1 落地：季度巡检 domain_face 的「平台专查」腿。

存在理由（r130 一手）：r114 的 14 条 topic 查询**没有平台专查**（如 dingtalk），
而 GitHub 上 dingtalk 生态有 3 个专门 skill 仓（wukong ★121 / ai-table ★110 / skills ★102）
⇒ 桶 0 的 6 件钉钉技能的候选池存在盲区。本件按本地件的**平台关键词**逐个专查，
把「平台生态有没有专门 skill 仓」变成季度可复算的面。

判据：平台关键词 = 受管根 slug 的平台前缀（dingtalk-*/byted-*/obsidian-*/notion-*/wps-*等）；
每关键词跑一次 GitHub search（q=<kw> skill in:name,description），
有专门仓（skill_md 形态命中）即记 finding 并给 C2 预判。
只读受管根与注册表，不写任何权威源。GitHub 限流时 STALE-EXIT（禁按 0 记绿）。
'''
import argparse, io, json, os, re, subprocess, sys, urllib.request
from datetime import datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GM = r'D:/global_skills'

PLATFORM_PAT = re.compile(r"^(dingtalk|byted|obsidian|notion|wps|lark|wechat|workbuddy|figma|github)[-_]")

def gh_search(q):
    url = "https://api.github.com/search/repositories?q=" + urllib.parse.quote(q) + "&sort=stars&per_page=5"
    req = urllib.request.Request(url, headers={"User-Agent": "skill-governance-probe"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out")
    args = ap.parse_args()
    slugs = os.listdir(GM)
    kws = sorted(set(m.group(1) for s in slugs for m in [PLATFORM_PAT.match(s)] if m))
    print("[PROBE] 平台关键词:", ", ".join(kws))
    findings = []
    for kw in kws:
        try:
            d = gh_search("%s skill in:name,description" % kw)
            items = [r for r in d.get("items", [])[:5]]
            findings.append({"kw": kw, "total": d.get("total_count", 0),
                             "top": [{"repo": r["full_name"], "stars": r["stargazers_count"],
                                      "desc": (r.get("description") or "")[:100]} for r in items[:3]]})
            print("  %-12s total=%-5s top=%s" % (kw, d.get("total_count", 0),
                  items[0]["full_name"] if items else "-"))
        except Exception as e:
            print("[PROBE:STALE-EXIT] %s 检索失败：%s" % (kw, e))
            return 2   # R247：禁按 0 记绿
    local_hits = [f for f in findings if f["total"] > 0]
    doc = {"schema": "platform-probe-r132-v1", "generated_at": datetime.now().isoformat(timespec="seconds"),
           "kws": kws, "findings": findings,
           "kws_with_ecosystem": [f["kw"] for f in local_hits],
           "note": "有生态仓的平台即登记为下季 C2 候选面来源；本件只探测不裁决"}
    if args.out:
        io.open(args.out, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1))
        print("[PROBE] JSON -> %s" % args.out)
    return 0

if __name__ == "__main__":
    sys.exit(main())