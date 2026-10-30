# -*- coding: utf-8 -*-
"""r299_declared_inject.py — R296-4（把 .upstream 声明仓并入候选池）的改造取证，不改 r114 本体。

存在理由（一手实测）：需求 2 要「每件 3-5 个匹配度最高的替代」、需求 3 要「五维量化评分」，而 r114
的候选池只来自 15 条 POOL_QUERIES（L1037 实测）=> 我们声明在 .upstream 里的上游仓**从未进过打分面**
（r298 实测 declared_upstream_in_face 在 pad_only 13 件上 0/13、全矩阵 true 只有 10/55）。也就是
「已知上游是谁，却没评估过它」—— 需求 2 与需求 3 之间断掉的那条链。本件把「注入声明仓后能否被五维
打分、三种语义能否分开」跑成真读数。

版本史（两处都是我自己的错，留在件里以免下一轮重犯）：
  v1 用矩阵行的 declared_upstream_repo（只有第一个仓）+ 只看 slug 目录名。两个后果：
     · 侧车声明的是 **path: 子目录**（实测 data-analysis 指向
       K-Dense-AI/scientific-agent-skills 的 skills/exploratory-data-analysis）时，slug 目录名
       根本不相等 => 被误判 invalid（把真上游说成声明失效）。12 行 invalid 里 8 行是这一类。
     · 侧车可以有**多行 owner/repo**（实测 web-access 声明 4 个仓、browser-cdp/defuddle/dogfood
       各 2 个），只取第一个 => 其余声明仓完全不进判定。
     v1 结果留档为 r299_inject_result_v1_pathblind.json（不删，作为「判据先错后对」的证据）。
  v2 改为：从**盘上 .upstream 现读**（不信快照 —— 与 05-exec/r291_req2_compliance.py v2 同一姿势），
     取全部 owner/repo 行 + path: 子路径；命中判据 = 声明路径存在 或 树里有 slug 变体目录的 SKILL.md。

三种语义（r298 proposal 定，本件实测其可分性）：
  1 lineage      —— 声明确能在该仓树里落地（声明路径命中，或 slug 变体目录有 SKILL.md）=> 它是
                    **我们的上游**、不是「开源替代」：计入打分面（带五维），但**不得计入 skill_n**，
                    否则等于用上游把「无替代」洗成「有替代」（r299 派发件 owner 犯过一次、被它自己
                    的 LEG6 抓出）。
  2 other_source —— 与本件无声明关系的仓而 slug/路径命中 => 真替代候选、计入 skill_n。本件按设计
                    不产该态（判别边界见 report.md 第 3 节），只在腿里验方向。
  3 invalid      —— 声明仓可测、树完整未截断，且声明路径与 slug 目录**都**落不到 => 声明失效：
                    既不算替代，也不得判「开源侧无对应件」（实测 kepano/defuddle 全树 0 个 SKILL.md）。
  另 unmeasured  —— 仓/树取不到，或树被截断且未见命中 => 显式记 unmeasured：**取不到不等于不存在**
                    （R247 双向）。

口径纪律：五维一律 import r114 本体调 score5（复制口径 = 第二真相源，04-plan 5.4）；仓元数据用
r114.measure_repo 补测后落它自己的 gitignored 缓存（本轮补 12 仓、api_calls=24、errors=0）。
夹具注入点：技能根走 r114.UPSTREAM_ROOT（环境变量 ZIJIAN_SKILLS_ROOT，L554 现成），不需新开关。
退出码：0 = 三腿全 PASS；1 = 任一 FAIL；2 = 输入不可得。
末行：[R299:INJECT] rows=<n> lineage=<n> invalid=<n> unmeasured=<n> scored_with_dims=<n> legA=<> legB=<> legC=<>
"""
import importlib.util
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # _repro/r299a -> 项目根
SP = os.path.join(ROOT, "05-exec", "r114_replacement_scan.py")
_s = importlib.util.spec_from_file_location("r114", SP)
r114 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(r114)                            # 权威口径唯一来源
CACHE = r114.load_cache()
SKILLS_ROOT = r114.UPSTREAM_ROOT                       # 受管根（可被夹具覆盖）


def read_sidecar(slug):
    """盘上现读 .upstream -> (声明仓列表, 声明子路径)。缺文件返回 ([], None)。
    不用 r114.parse_sidecar 而自己扫全部行：它只返回**第一个** repo（实测 web-access 有 4 个），
    这里要的是全集。RE_REPO_LINE 与 path: 的识别仍复用本体常量，避免两处各写各的。"""
    p = os.path.join(SKILLS_ROOT, slug, ".upstream")
    if not os.path.isfile(p):
        return [], None
    txt = io.open(p, encoding="utf-8-sig", errors="replace").read()
    repos, sub = [], None
    for raw in txt.splitlines():
        ln = raw.strip()
        if not ln:
            continue
        if ln.lower().startswith("path:"):
            sub = ln.split(":", 1)[1].strip() or None
            continue
        if r114.RE_REPO_LINE.match(ln) and ln not in repos:
            repos.append(ln)
    return repos, sub


def slug_variants(slug):
    """slug 可匹配变体：连字符/下划线互换与粘连形。实测容器仓用 agent_skills/<slug> 原样目录名，
    另有仓写下划线形 => 三种都试；只试一种会假阴（把真上游判成失效）。"""
    base = str(slug).lower()
    return sorted({base, base.replace("-", "_"), base.replace("_", "-"), base.replace("-", "")})


def repo_is_skill(slug, repo, paths):
    """整仓即本件的情形（r299 自查发现的缺陷）。

    为什么必须有这条：实测 lewislulu/html-ppt-skill 全树只有 1 个 SKILL.md 且在**仓库根**，
    仓名又含本件 slug（html-ppt）—— 这是最典型的「我们的件就是从这个仓来的」。而 hits_for 要求
    「目录段等于 slug」⇒ 根级 SKILL.md 的 segs 只有一个元素、永远进不去 ⇒ 被我误判 invalid。
    判据收紧以免放宽成假绿：必须同时满足 ①根级确有 SKILL.md ②（仓名末段含 slug 变体 或 全树
    只有这一个 SKILL.md）。只满足其一不算 —— 否则 97 个 SKILL.md 的 trailofbits/skills 会因为
    「根级没有」以外的偶然命中被洗成 lineage。
    """
    names = [(x.get("path") if isinstance(x, dict) else str(x)).strip("/") for x in (paths or [])]
    if "SKILL.md" not in names:
        return None
    tail = str(repo).split("/")[-1].lower()
    vs = slug_variants(slug)
    name_ok = any(v and v in tail for v in vs)
    only_one = len(names) == 1
    # 只认 name_ok。曾打算把 only_one（全树唯一 SKILL.md）也算命中，自查时立刻否掉：
    # 实测 web-access 声明的 Panniantong/Agent-Reach 全树就 1 个 SKILL.md，但那是**别人的另一个技能**
    # （Agent-Reach，不是 web-access）⇒ 用 only_one 会把它洗成 lineage，正是我要防的假绿。
    # 三个根级案例（html-ppt/gstack/frontend-slides）本来就都 name_ok ⇒ 放宽没有收益只有风险。
    if name_ok:
        item = next(x for x in paths
                    if (x.get("path") if isinstance(x, dict) else str(x)).strip("/") == "SKILL.md")
        return {"path": "SKILL.md",
                "sha": (item.get("sha") if isinstance(item, dict) else "")[:12],
                "via": "repo_name", "name_ok": True, "sole_only": only_one}
    return None


def hits_for(slug, paths):
    """树里的 SKILL.md 路径中，目录段等于本件 slug 变体的那些（不含仓库根级，那走 repo_is_skill）。"""
    out = []
    for item in (paths or []):
        p = item.get("path") if isinstance(item, dict) else str(item)
        segs = [s.lower() for s in str(p).split("/") if s]
        if len(segs) < 2 or segs[-1] != "skill.md":
            continue                                   # 只看 SKILL.md 本体，README 不算入口
        if any(v in segs[:-1] for v in slug_variants(slug)):
            out.append({"path": p, "sha": (item.get("sha") if isinstance(item, dict) else "")[:12]})
    return sorted({x["path"]: x for x in out}.values(), key=lambda x: x["path"])


def path_hit(declared_path, paths):
    """声明的 path: 子目录是否在该仓树里落地。侧车写的是目录，故三种形态都算命中：
    该目录本身在树中 / 其下直接有 SKILL.md / 声明时已含 SKILL.md。"""
    if not declared_path:
        return None
    want = declared_path.strip("/").lower()
    dp = want + "/skill.md"
    for item in (paths or []):
        p = (item.get("path") if isinstance(item, dict) else str(item)).lower().strip("/")
        if p == declared_path.lower().strip("/") or p == dp or p.endswith("/" + dp):
            return {"path": (item.get("path") if isinstance(item, dict) else str(item)),
                    "sha": (item.get("sha") if isinstance(item, dict) else "")[:12],
                    "via": "declared_path"}
    return None


def dims_of(repo):
    """五维用 r114 本体 score5（同一函数 = 同一口径，落盘档与得分档不许互相打脸）。"""
    m = CACHE.get("repo__" + r114.key_of(repo))
    if not m or m.get("state") != "OK":
        return {"unmeasured": "仓元数据不在缓存（本轮已补测 12 仓；若仍缺说明取数失败）"}, None
    try:
        s, tot, fc = r114.score5(m, True, True)
        return {"score5": s, "score_total": tot, "fc_caliber": fc,
                "stars": m.get("stars"), "pushed_at": m.get("pushed_at"),
                "license": m.get("license")}, m
    except Exception as exc:
        return {"error": repr(exc)[:90]}, m


def classify(slug, repo, declared_path, col):
    """单个（本件 × 一个声明仓）的三态判定。"""
    if not repo or not re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", str(repo)):
        return {"kind": "invalid", "why": "声明不是 owner/repo 形态", "repo": repo,
                "counts_toward_skill_n": False}
    if col is None or col.get("state") != "OK":
        return {"kind": "unmeasured", "repo": repo, "counts_toward_skill_n": False,
                "why": "树不可得：%s" % ((col or {}).get("state") or "采集件里没有该仓")}
    paths = col.get("skill_md_paths") or []
    ph = path_hit(declared_path, paths)
    sh = hits_for(slug, paths)
    rs = repo_is_skill(slug, repo, paths)        # 根级单件仓（v2 前会漏）
    out = {"repo": repo, "declared_path": declared_path, "path_hit": ph, "slug_hits": sh[:6],
           "repo_is_skill_hit": rs,
           "tree_skill_md_n": col.get("skill_md_n"), "truncated": bool(col.get("truncated"))}
    out["dims"], _ = dims_of(repo)
    if ph or sh or rs:
        out["kind"] = "lineage"                        # 声明能落地：进打分面、不进 skill_n
    elif out["truncated"]:
        out["kind"] = "unmeasured"                     # 树截断 => 未见不等于不存在
        out["why"] = "tree truncated ⇒ 不得据缺失判声明失效"
    else:
        out["kind"] = "invalid"                        # 路径与 slug 都落不到 => 声明失效（实测非取不到）
        out["why"] = ("全树 %d 个 SKILL.md 里，声明路径 %s 与 slug 目录均未落地 ⇒ 声明失效"
                      % (col.get("skill_md_n"), declared_path or "（未声明）"))
    out["counts_toward_skill_n"] = False               # 三态共同点：声明仓永不充当「开源替代」
    return out


def main():
    mx = os.path.join(ROOT, "_repro", "r299a", "verdict_face.json")
    tpp = os.path.join(HERE, "tree_paths.json")
    # 树数据 1.39MB、可由 collect.py + collect2.py 从 gh 重建 ⇒ 不入库（与 r298 的 texts/ 同一处置）。
    # ⇒ 干净 clone 里本判据必须 REFUSED 而不是照样出态：在没树的时候还能报 lineage/invalid，
    #    那就是把「看不见」当「不存在」（R247），是假绿。REFUSED 是设计，不是缺陷。
    if not os.path.isfile(tpp):
        print("[R299:INJECT] REFUSED 采集件 tree_paths.json 不在盘上；先跑 "
              "python _repro/r299a/collect.py 再跑 collect2.py 重建 => 本轮不出任何态")
        return 2
    if not os.path.isfile(mx):
        print("[R299:INJECT] REFUSED 判定面 verdict_face.json 不可得")
        return 2
    mat = json.load(io.open(mx, encoding="utf-8"))
    COL = json.load(io.open(tpp, encoding="utf-8"))
    body = mat.get("rows") or mat.get("per_skill") or []
    if not body:
        print("[R299:INJECT] REFUSED 矩阵无 rows keys=%s" % sorted(mat.keys())[:8])
        return 2
    rows = []
    for r in body:
        slug = r.get("slug")
        repos, sub = read_sidecar(slug)                # 盘上现读，不信矩阵快照
        if not repos:
            continue
        for repo in repos:
            c = classify(slug, repo, sub, COL.get(repo))
            c["slug"] = slug
            c["row_verdict_before"] = r.get("verdict")
            c["matrix_declared"] = r.get("declared_upstream_repo")
            rows.append(c)

    def tally(k):
        return sum(1 for x in rows if x.get("kind") == k)

    def slug_kinds(k):
        return len({x["slug"] for x in rows if x.get("kind") == k})

    scored = sum(1 for x in rows if "score_total" in (x.get("dims") or {}))
    flip = sum(1 for x in rows if x.get("kind") == "invalid"
               and x.get("row_verdict_before") == "NO_OS_CANDIDATE")
    # 侧车声明多于一个仓的行数（这就是 v1 只取第一个所漏掉的量）
    multi = len({x["slug"] for x in rows}) and sum(
        1 for s in {x["slug"] for x in rows} if len(read_sidecar(s)[0]) > 1)

    # 腿 A（防乐观）：采集件里没有该仓 => 必须 unmeasured（不许丢弃、不许判 invalid 后被读成「无替代」）
    a1 = classify("no-such-xyz", "lxh113377/r299a-does-not-exist", None, None)["kind"] == "unmeasured"
    # 腿 B（防恒判失效，即证明有牙）：r298 gh api 实测 awesome-llm-apps 的
    # agent_skills/commit-archaeologist/SKILL.md 存在（sha a80214bea587）=> 必须 lineage + 五维 + 不计 skill_n
    b_obj = classify("commit-archaeologist", "Shubhamsaboo/awesome-llm-apps", None,
                     COL.get("Shubhamsaboo/awesome-llm-apps"))
    legB = ("PASS" if (b_obj["kind"] == "lineage" and b_obj["slug_hits"]
                       and b_obj["counts_toward_skill_n"] is False
                       and "score_total" in b_obj["dims"]) else "FAIL")
    # 腿 C（本轮新增，专治 v1 那个错）：**声明走 path: 子目录**的真例必须判 lineage。
    # data-analysis 声明 K-Dense-AI/scientific-agent-skills + path: skills/exploratory-data-analysis，
    # 目录名与本件 slug 完全不等 => v1 判 invalid；v2 必须靠声明路径命中判 lineage。此腿若 FAIL，
    # 就说明「不看 path」的缺陷还在。
    c_slug = "data-analysis"
    c_repo, c_sub = read_sidecar(c_slug)
    c_obj = classify(c_slug, c_repo[0] if c_repo else None, c_sub,
                     COL.get(c_repo[0]) if c_repo else None)
    legC = ("PASS" if (c_obj["kind"] == "lineage" and c_obj["path_hit"]
                       and not c_obj["slug_hits"]) else
            ("UNVERIFIED(no declared path)" if not c_sub else "FAIL"))
    legA = "PASS" if a1 else "FAIL"

    # 腿 D（本轮自查发现缺陷后补，双向断言 —— 单向只证明放宽不证明不假绿）：
    # D1 正向：html-ppt 声明 lewislulu/html-ppt-skill，全树仅根级 1 个 SKILL.md 且仓名含 slug
    #     ⇒ 必须 lineage（v2 前它被判 invalid，因为 hits_for 要求有父目录段）。
    # D2 反向：web-access 声明 Panniantong/Agent-Reach，全树 1 个 SKILL.md 但仓名不含 web-access
    #     ⇒ 必须**仍判 invalid**（若这里变 lineage，说明我把「唯一 SKILL.md」当成了命中 = 假绿）。
    d1_slug, d2_slug = "html-ppt", "web-access"
    d1r, d1p = read_sidecar(d1_slug)
    d1 = classify(d1_slug, d1r[0] if d1r else None, d1p, COL.get(d1r[0]) if d1r else None)
    d2r, d2p = read_sidecar(d2_slug)
    d2_repo = next((x for x in d2r if "Agent-Reach" in x), None)
    d2 = classify(d2_slug, d2_repo, d2p, COL.get(d2_repo)) if d2_repo else None
    legD1 = ("PASS" if (d1["kind"] == "lineage" and d1.get("repo_is_skill_hit")) else "FAIL")
    legD2 = ("PASS" if (d2 and d2["kind"] == "invalid" and not d2.get("repo_is_skill_hit"))
             else ("UNVERIFIED" if not d2 else "FAIL"))
    legD = "PASS" if (legD1 == "PASS" and legD2 == "PASS") else "FAIL"

    print("  pairs=%d（本件×声明仓）覆盖件数=%d kinds=%s"
          % (len(rows), len({x["slug"] for x in rows}),
             {k: tally(k) for k in ("lineage", "invalid", "unmeasured")}))
    print("  按件去重 lineage=%d invalid=%d；多仓侧车件数=%d；翻档面(invalid 且现行 NO_OS_CANDIDATE)=%d"
          % (slug_kinds("lineage"), slug_kinds("invalid"), multi, flip))
    print("  legA=%s legB=%s legC=%s legD1=%s legD2=%s"
          "（C 声明路径=%s / C slug命中=%s / D1 根级命中=%s）"
          % (legA, legB, legC, legD1, legD2, bool(c_obj.get("path_hit")),
             bool(c_obj.get("slug_hits")), bool(d1.get("repo_is_skill_hit"))))
    print("  legB detail: hits=%s dims=%s" % (b_obj["slug_hits"][:1], b_obj["dims"]))
    json.dump({"pairs_n": len(rows), "slugs_n": len({x["slug"] for x in rows}), "rows": rows,
               "tally": {k: tally(k) for k in ("lineage", "invalid", "unmeasured")},
               "tally_by_slug": {k: slug_kinds(k) for k in ("lineage", "invalid", "unmeasured")},
               "multi_repo_sidecars_n": multi, "flip_no_os_to_invalid": flip,
               "legs": {"A": legA, "B": legB, "C": legC, "D": legD, "D1": legD1, "D2": legD2,
                        "C_detail": {"slug": c_slug, "declared_path": c_sub,
                                     "path_hit": c_obj.get("path_hit"),
                                     "kind": c_obj["kind"]},
                        "B_detail": {"kind": b_obj["kind"], "slug_hits": b_obj["slug_hits"],
                                     "counts_toward_skill_n": b_obj["counts_toward_skill_n"],
                                     "dims": b_obj["dims"]}}},
              io.open(os.path.join(HERE, "r299_inject_result.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("[R299:INJECT] rows=%d lineage=%d invalid=%d unmeasured=%d scored_with_dims=%d legA=%s legB=%s legC=%s legD=%s"
          % (len(rows), tally("lineage"), tally("invalid"), tally("unmeasured"), scored, legA, legB, legC, legD))
    return 0 if all(x == "PASS" for x in (legA, legB, legC, legD)) else 1


if __name__ == "__main__":
    sys.exit(main())
