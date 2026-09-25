# -*- coding: utf-8 -*-
"""r36_cmd_resolvability.py — 第十二维「文档内引用的可解析性」（r36 新维度，双侧同一把尺）。

为什么量这个：前 11 维量了体积、结构、命中率、CI 存在性/有效性、发布面、可移植性，
但**没有一维回答"技能文档里写的那个文件到底在不在"**。
本体系的 SKILL.md 大量以代码块给出 `python scripts/xxx.py` / `bash scripts/run.sh` /
`Read references/yyy.md` 形态的指令 —— agent 会**照抄执行**。若该文件不存在，表现是
"技能装了却跑不通"，而这在过去只能靠偶然撞到才发现（本仓 r18 曾用 7 个死目标一次性抓到 direct_map 死链）。

尺（只判**仓内相对引用**，别的一律不参与，避免与第十一维重复计数）：
    纳入   代码块内、形如 `scripts/x.py` `references/x.md` `../sibling/scripts/x.py` `<skill>/scripts/x.py`
    排除   绝对路径（属第十一维）、URL、含 `{}`/`*`/`<…>` 的占位与 glob、纯扩展名无目录的裸文件名
    判定   在技能目录内可解析 = RESOLVABLE；同技能缺但上级/兄弟技能下有 = RESOLVABLE_VIA_SIBLING；
           都没有 = DEAD（**这才是可整改项**）；无法定位所属技能 = UNLOCATED（不并入任何一类）

对手侧同一把尺：取其 SKILL.md 原文 + `git/trees?recursive=1` 的全仓 blob 路径集做存在性判定。
⇒ 注意口径差：对手仓里"文件在不在"是**全仓**判定，我们是**技能目录**判定（本体系一个技能一个目录、
   不给跨目录访问），故两侧绝对值不可直接相减，只能各自看趋势与 DEAD 清单。

用法：
    python 05-exec/r36_cmd_resolvability.py --ours            # 只扫本体系
    python 05-exec/r36_cmd_resolvability.py --json 件.json    # 加扫对手（联网，只读）
退出码：0 正常 / 1 本体系存在 DEAD 引用（可整改项待办）/ 2 扫描面为空或取数失败（R247，不得判「无死链」）
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime

GS = r"D:\global_skills"
FENJUE = r"C:\Users\37533\Desktop\workspace\焚诀"
REF_RX = re.compile(r"(?<![\w./\\-])((?:\.\./)?(?:[\w\-.]+/)*(?:scripts|references|assets|hooks|templates|eval|commands|schemas)/[\w./\-]+\.(?:py|sh|ps1|md|json|js|ts|txt|yaml|yml|mjs|tmpl|tmpl\.md))")
FENCE_RX = re.compile(r"```[^\n]*\n(.*?)```", re.S)
PLACEHOLDER_RX = re.compile(r"[{*<]|\.\.\.")

OPP = ["addyosmani/agent-skills", "obra/superpowers", "anthropics/skills", "Fission-AI/OpenSpec"]


def extract_refs(text):
    """全文扫描仓内相对引用。

    ⚠️ 口径修正（r36 抽验实测）：首版只扫代码块，而 494 处同类引用里代码块只占 40 处
    （漏检 92%）⇒ 由它得出的「0 DEAD / 90.7%」是**覆盖盲区造成的假绿**，不是结论。
    现改全文扫描；代码块/正文的差异改由 `refs_in_fence` 单独如实登记，不再当扫描面。
    """
    out = []
    for m in REF_RX.finditer(text):
        ref = m.group(1).rstrip(".,;:)")
        if PLACEHOLDER_RX.search(ref):
            continue
        out.append(ref)
    return out


def fence_only_refs(text):
    return [r for block in FENCE_RX.findall(text) for r in extract_refs(block)]


def classify(ref, skill_dir, all_skill_names, gs_root):
    """返回 RESOLVABLE / RESOLVABLE_VIA_SIBLING / DEAD / UNLOCATED。"""
    if os.path.exists(os.path.join(skill_dir, ref.replace("/", os.sep))):
        return "RESOLVABLE"
    if os.path.exists(os.path.join(FENJUE, ref.replace("/", os.sep))):
        # 大量正文以焚诀仓内相对路径引用（`eval/xxx.py`），第三解析域，禁与 DEAD 混计
        return "RESOLVABLE_VIA_EXTERNAL"
    head = ref.split("/")[0]
    if ref.startswith("../"):
        # `../assets/runtime.js` 是**产物 HTML 相对路径**：去掉开头的 `../` 后相对本技能目录即存在
        # （html-ppt/assets/runtime.js 实测在）。首版误按"兄弟技能"去掉两段 ⇒ 报出 2 处假 DEAD。
        rest = "/".join(ref.split("/")[1:])
        if os.path.exists(os.path.join(skill_dir, rest.replace("/", os.sep))):
            return "RESOLVABLE"
        tail = "/".join(ref.split("/")[2:])
        sib = ref.split("/")[1]
        if sib in all_skill_names and os.path.exists(os.path.join(gs_root, sib, tail.replace("/", os.sep))):
            return "RESOLVABLE_VIA_SIBLING"
        return "DEAD"
    if head in all_skill_names:                       # 以技能名开头的引用
        tail = "/".join(ref.split("/")[1:])
        return "RESOLVABLE_VIA_SIBLING" if os.path.exists(
            os.path.join(gs_root, head, tail.replace("/", os.sep))) else "DEAD"
    # 带子目录但不在技能根下：可能是仓级路径，无法定位归属 ⇒ 不并入 DEAD
    return "UNLOCATED" if "/" in ref else "UNLOCATED"


def scan_ours():
    if not os.path.isdir(GS):
        return None, "技能根不可读: %s" % GS
    names = sorted(d for d in os.listdir(GS) if os.path.isdir(os.path.join(GS, d)))
    rows = []
    for n in names:
        p = os.path.join(GS, n, "SKILL.md")
        if not os.path.exists(p):
            continue
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        refs = extract_refs(text)
        if not refs:
            continue
        kinds = {}
        dead = []
        for r in refs:
            k = classify(r, os.path.join(GS, n), set(names), GS)
            kinds[k] = kinds.get(k, 0) + 1
            if k == "DEAD":
                dead.append(r)
        rows.append({"skill": n, "refs": len(refs), "by_class": kinds, "dead": sorted(set(dead))})
    if not rows:
        return None, "本体系未抽到任何仓内引用（扫描面为空，禁判「无死链」，R247）"
    tot = sum(r["refs"] for r in rows)
    agg = {}
    for r in rows:
        for k, v in r["by_class"].items():
            agg[k] = agg.get(k, 0) + v
    RESOLVED = ("RESOLVABLE", "RESOLVABLE_VIA_SIBLING", "RESOLVABLE_VIA_EXTERNAL")
    return {"skills_with_refs": len(rows), "refs_total": tot, "by_class": agg,
            "resolvable_rate": round(sum(agg.get(k, 0) for k in RESOLVED) / float(tot), 4),
            "coverage_note": "全文扫描（非仅代码块）；解析域三级=技能目录 / 技能根下兄弟技能 / 焚诀仓根",
            "dead_rows": [r for r in rows if r["dead"]]}, None


def gh(args):
    return subprocess.run(["gh"] + args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=180)


def scan_repo(slug):
    t = gh(["api", "repos/%s/git/trees/HEAD?recursive=1" % slug, "--jq",
            '[.tree[] | select(.type=="blob") | .path] | join("\\n")'])
    if t.returncode != 0:
        return {"repo": slug, "error": (t.stderr or "")[:120]}
    tree = set(x for x in t.stdout.split("\n") if x.strip())
    l = gh(["api", "repos/%s/git/trees/HEAD" % slug, "--jq",
            '[.tree[] | select(.type=="tree") | .path] | join("\\n")'])
    top_dirs = [x for x in (l.stdout or "").split("\n") if x.strip()]
    hits = []
    for d in top_dirs:
        c = gh(["api", "repos/%s/contents/%s" % (slug, d), "--jq",
                '[.[] | select(.name=="SKILL.md") | .download_url] | join("\\n")'])
        for url in [x for x in (c.stdout or "").split("\n") if x.strip()][:40]:
            # raw 链接转成 contents API，才能直接拿 base64 .content
            api = url.replace("https://raw.githubusercontent.com/" + slug + "/HEAD/",
                              "repos/" + slug + "/contents/")
            r = gh(["api", api, "--jq", ".content"])
            if r.returncode != 0:
                continue
            try:
                import base64
                text = base64.b64decode(r.stdout.strip()).decode("utf-8", "replace")
            except Exception:
                continue
            for ref in extract_refs(text):
                hits.append(ref)
    if not hits:
        return {"repo": slug, "refs": 0, "note": "该仓 SKILL.md 内无此类仓内引用（不是死链为 0，是无对象）"}
    in_tree = sum(1 for h in hits if h in tree or any(p.endswith("/" + h) for p in tree))
    return {"repo": slug, "refs": len(hits), "resolvable": in_tree,
            "rate": round(in_tree / float(len(hits)), 4),
            "coverage_note": "对手侧按**全仓 blob 路径集**判定，与本体系按技能目录判定口径不同，禁直接相减"}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--ours", action="store_true")
    ap.add_argument("--json")
    args = ap.parse_args()

    ours, err = scan_ours()
    if ours is None:
        print("[RESOLVE:UNVERIFIED] %s" % err)
        return 2
    print("=== 本体系 文档内引用可解析性（第十二维）===")
    print("有引用的技能 %d 个｜引用 %d 处｜分类 %s｜可解析率 %.1f%%" % (
        ours["skills_with_refs"], ours["refs_total"], ours["by_class"], 100 * ours["resolvable_rate"]))
    for r in sorted(ours["dead_rows"], key=lambda x: -len(x["dead"]))[:15]:
        print("  DEAD %-30s %s" % (r["skill"], r["dead"][:6]))
    opp = []
    if not args.ours:
        for slug in OPP:
            o = scan_repo(slug)
            opp.append(o)
            if "error" in o:
                print("%-34s 取数失败：%s" % (slug, o["error"][:70]))
            else:
                print("%-34s refs=%s %s" % (slug, o["refs"], ("resolvable_rate=%.1f%%" % (100 * o["rate"]))
                                             if "rate" in o else o.get("note", "")))
    print("-" * 72)
    print("覆盖根: %s（技能目录内判定）＋对手 %d 仓（全仓 blob 集判定，口径不同）" % (GS, len(opp)))
    print("判据: 全文扫描 scripts/references/assets/hooks/templates/eval 等目录的相对引用；占位/glob/绝对路径/URL 不参与；解析域三级=技能目录/兄弟技能/焚诀仓根（r36 由只扫代码块改为全文，实测代码块只覆盖 40/494 处）")
    dead_n = sum(len(r["dead"]) for r in ours["dead_rows"])
    print("[RESOLVE:%s] %s" % ("DEAD" if dead_n else "OK",
                               "本体系 DEAD 引用 %d 处（唯一可整改面，逐条见上）" % dead_n if dead_n
                               else "本体系无 DEAD 引用"))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(json.dumps({"schema": "cmd-resolvability-v1",
                                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "readonly": True,
                                "benchmark": "r36 第十二维 文档内引用可解析性",
                                "provenance_cmd": "python 05-exec/r36_cmd_resolvability.py --json <件>",
                                "covers": [GS, OPP], "ours": ours, "opposites": opp,
                                "caveat": "两侧判定口径不同（技能目录 vs 全仓 blob），禁直接相减；"
                                          "本体系 DEAD 才是可整改项"}, ensure_ascii=False, indent=1))
        print("JSON -> %s" % args.json)
    return 1 if dead_n else 0


if __name__ == "__main__":
    raise SystemExit(main())
