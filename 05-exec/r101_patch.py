#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r101 补丁：名册的「优质」半边补判据。

一手实测（本轮）：top-20 派生名册里 **7 席** 被 SKILL.md<=3 的仓占用
（tt-a1i/archify 2、last30days 1、awesome-claude-code **0**、humanizer 1、
i-have-adhd 2、CowAgent 3、LibreChat 3），而真技能仓 vercel-labs/skills、
VoltAgent/awesome-agent-skills、mukul975/Anthropic-Cybersecurity-Skills
被 top-20 截断挡在外面 —— 用户要的是「高星**且优质**」，此前只按星标排序。

三处改动（全部锚点命中==1 + 写后读回 + 行列字节不得下降）：
  1. ROSTER_TOP_N 默认 0 = 不截断（实测面 25 仓全入面）；设 >0 时 truncated 名单必须落盘
  2. derive_roster 输出 ranked 全集 + truncated 具名（含星标），截断从「计数可见」升到「名单可审计」
  3. score_dims 按 skill_bearing 分档：无 SKILL.md 的仓不进 d1/d8/d9/d12 分母（只进 d5/d6/d10），
     产物印 skill_face_n / non_skill_repos，禁止把平台仓当技能树参与「本地落后」结论
"""
import ast
import io
import os
import sys

TARGET = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/05-exec/r96_twelve_face.py"

PAIRS = [
    # ---- 1. 不再默认截断
    ("ROSTER_TOP_N = 20          # 取实测星标降序前 N 仓入面",
     "ROSTER_TOP_N = 0           # 0 = 不截断，实测面全量入面（r101：top-20 让 7 席被 SKILL.md<=3 的仓占掉，\n                               # 而 vercel-labs/skills 等真技能仓被截在外面；>0 时 truncated 名单必须落盘）"),

    # ---- 2. derive_roster：截断具名 + ranked 全集
    ("""    derived = [n for _s, n in ranked[:top_n]]
    for extra in pinned or ():
        if extra not in derived:
            derived.append(extra)
    return {"derived": derived,
            "face_rows": len(search_face or []),
            "unparsable_rows": unparsable,
            "top_n": top_n,
            "pinned": list(pinned or ())}""",
     """    ordered = [n for _s, n in ranked]
    derived = ordered if not top_n else ordered[:top_n]
    # 截断必须具名到仓（只报「差了几个」= 上轮形态：计数可见但名单不可审计）
    truncated = [{"repo": n, "stars": dict((m, s) for s, m in ranked)[n]}
                 for n in ordered[len(derived):]]
    for extra in pinned or ():
        if extra not in derived:
            derived.append(extra)
    return {"derived": derived,
            "ranked_all": ordered,
            "face_rows": len(search_face or []),
            "unparsable_rows": unparsable,
            "top_n": top_n,
            "truncated": truncated,
            "pinned": list(pinned or ())}"""),

    # ---- 3. score_dims：按技能面分档
    ("""    skill_face = [s for s in opp_slugs if opp_slugs[s]]
    universe = set().union(*opp_slugs.values()) if opp_slugs else set()""",
     """    # r101 分档：无 SKILL.md 的仓是平台/清单壳，不是技能树 —— 不得进 d1/d8/d9/d12 分母
    skill_bearing = {s: bool(opp_slugs.get(s)) for s in opp_slugs}
    skill_face = [s for s in opp_slugs if opp_slugs[s]]
    universe = set().union(*[v for k, v in opp_slugs.items() if skill_bearing.get(k)]) \\
        if skill_face else set()"""),

    # ---- 4. 每仓与门面输出带分档位
    ("""            "tree_truncated": rec.get("tree_truncated"),
        }""",
     """            "tree_truncated": rec.get("tree_truncated"),
            "skill_bearing": bool(skill_bearing.get(slug)),
            "face_role": ("skill_tree" if skill_bearing.get(slug) else "non_skill_repo"),
        }"""),

    # ---- 5. roster_face 增分档计数
    ("""                "non_skill_repos": sorted(s for s, r in raw.get("repos", {}).items()
                                          if r.get("available")
                                          and not r.get("skill_md_paths")),""",
     """                "non_skill_repos": sorted(s for s, r in raw.get("repos", {}).items()
                                          if r.get("available")
                                          and not r.get("skill_md_paths")),
                "probed_n": len([1 for r in raw.get("repos", {}).values() if r.get("available")]),
                "skill_face_n": len(skill_face),
                "truncated_named": (raw.get("roster_face") or {}).get("truncated"),
                "quality_note": "d1/d8/d9/d12 只在 skill_face 上取分母；non_skill_repos 仅进 d5/d6/d10（平台仓的维护/文档/CI 面仍可比）","""),

    # ---- 6. selftest 双向腿
    ("""    chk("接线 双单位并报且 toplevel<=alllayers",""",
     """    # r101 优质面双向证据
    mix = [["a/noskill", 900, "t", False], ["a/skill", 800, "t", False],
           ["a/small", 700, "t", False]]
    chk("正例 top_n=0 不截断（全量入面）",
        derive_roster(mix, top_n=0)["derived"], ["a/noskill", "a/skill", "a/small"])
    chk("反例 截断必须具名（含星标），不得只给计数",
        derive_roster(mix, top_n=1)["truncated"],
        [{"repo": "a/skill", "stars": 800}, {"repo": "a/small", "stars": 700}])
    chk("接线 截断计数与名单一致",
        len(derive_roster(mix, top_n=1)["truncated"]),
        derive_roster(mix, top_n=1)["face_rows"] - len(derive_roster(mix, top_n=1)["derived"]))
    chk("反例 全量入面时 truncated 必为空数组不是 None",
        derive_roster(mix, top_n=0)["truncated"], [])
    chk("接线 双单位并报且 toplevel<=alllayers","""),
    # ---- 7. schema 号补账（一手自抓：r100 报告与提交说明写的是 v4，但代码里 schema
    #      串从未 bump ⇒ 产物 schema 仍 r99-v3，属「声明先于证据」。本轮一次 bump 到 v5，
    #      并在 r101 报告里如实记这次错账；r100 报告原文按 R241 不改写，只加校正注。
    ('"schema": "twelve-face-r99-v3",',
     '"schema": "twelve-face-r101-v5",'),
]


def main():
    src = io.open(TARGET, encoding="utf-8").read()
    lb, bb = len(src.splitlines()), len(src.encode("utf-8"))
    for i, (old, new) in enumerate(PAIRS, 1):
        n = src.count(old)
        if n != 1:
            sys.stderr.write("[ABORT] 第 %d 处锚点命中 %d 次（须==1）\n" % (i, n))
            return 1
        src = src.replace(old, new, 1)
    tree = ast.parse(src, TARGET, "exec")
    names = {nd.name for nd in ast.walk(tree) if isinstance(nd, ast.FunctionDef)}
    if "derive_roster" not in names or "score_dims" not in names:
        sys.stderr.write("[ABORT] 函数丢失：%s\n" % sorted(names)[:6])
        return 1
    tmp = TARGET + ".r101tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    os.replace(tmp, TARGET)
    back = io.open(TARGET, encoding="utf-8").read()
    la, ba = len(back.splitlines()), len(back.encode("utf-8"))
    if la <= lb or ba <= bb:
        sys.stderr.write("[ABORT] 行数/字节未增长 %d/%d -> %d/%d\n" % (lb, bb, la, ba))
        return 1
    ast.parse(back, TARGET, "exec")
    print("[PATCH:r101:OK] %d 处锚点唯一命中；%d 行/%d B -> %d 行/%d B"
          % (len(PAIRS), lb, bb, la, ba))
    return 0


if __name__ == "__main__":
    sys.exit(main())
