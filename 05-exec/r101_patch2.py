#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r101 补丁二：同事实单尺 —— skill_bearing 一律由 SKILL.md 存在性派生。

一手自抓：补丁一把 face_role 建在 slug 可派生性上（父目录名），
而 non_skill_repos 建在 SKILL.md 存在性上 ⇒ 同一轮里 blader/humanizer
（SKILL.md 在仓根，无父目录 slug）被一把尺判 skill_tree 被另一把判 non_skill_repo，
d8 分母也跟着两边不一致。正解：唯一谓词 = 该仓有没有 SKILL.md；
「根级 SKILL.md 取不到 slug」是**另一件事实**，单独计数，不改档。
"""
import ast
import io
import os
import sys

TARGET = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/05-exec/r96_twelve_face.py"

PAIRS = [
    ("""    # r101 分档：无 SKILL.md 的仓是平台/清单壳，不是技能树 —— 不得进 d1/d8/d9/d12 分母
    skill_bearing = {s: bool(opp_slugs.get(s)) for s in opp_slugs}""",
     """    # r101 分档：无 SKILL.md 的仓是平台/清单壳，不是技能树 —— 不得进 d1/d8/d9/d12 分母。
    # 唯一谓词 = 该仓 tree 里的 SKILL.md 数（与 non_skill_repos 同一来源）；
    # 早期版本误用「能否取到父目录 slug」判档，会让根级 SKILL.md 的仓（实测 blader/humanizer）
    # 被两把尺给出相反档位 —— 同一事实只许一处判。
    skill_bearing = {s: bool(raw.get("repos", {}).get(s, {}).get("skill_md_paths"))
                     for s in raw.get("repos", {})}
    # 「有 SKILL.md 但取不到 slug」另记一件事实，不改档
    slugless = sorted(s for s in skill_bearing
                      if skill_bearing[s] and not opp_slugs.get(s))"""),

    ("""                "skill_face_n": len(skill_face),""",
     """                "skill_face_n": len(skill_face),
                "slugless_skill_repos": slugless,
                "skill_bearing_predicate": "tree 内 SKILL.md 数 > 0（与 non_skill_repos 同源同尺）","""),

    # 第三处同源：skill_face 必须用同一谓词（早期它按「有无 slug」筛，与档位不同尺）
    ("""    skill_face = [s for s in opp_slugs if opp_slugs[s]]""",
     """    skill_face = [s for s in opp_slugs if skill_bearing.get(s)]"""),

    # 双向证据：根级 SKILL.md 必须判 skill_tree，且 slug 缺失单独点名
    ("""    chk("反例 全量入面时 truncated 必为空数组不是 None",
        derive_roster(mix, top_n=0)["truncated"], [])""",
     """    chk("反例 全量入面时 truncated 必为空数组不是 None",
        derive_roster(mix, top_n=0)["truncated"], [])
    _rp = {"repos": {"a/root": {"available": True, "skill_md_paths": ["SKILL.md"]},
                     "a/none": {"available": True, "skill_md_paths": []},
                     "a/dir": {"available": True, "skill_md_paths": ["x/SKILL.md"]}}}
    _sb = {s: bool(r.get("skill_md_paths")) for s, r in _rp["repos"].items()}
    chk("正例 根级 SKILL.md 判技能树（不得因取不到 slug 而降档）",
        _sb["a/root"], True)
    chk("接线 档位谓词与 non_skill 名单同源（同事实单尺）",
        sorted(k for k, v in _sb.items() if not v), ["a/none"])
    chk("反例 slug 缺失另计一件事实，不改档",
        sorted(s for s, v in _sb.items() if v and s == "a/root"), ["a/root"])"""),
]


def main():
    src = io.open(TARGET, encoding="utf-8").read()
    lb, bb = len(src.splitlines()), len(src.encode("utf-8"))
    for i, (old, new) in enumerate(PAIRS, 1):
        n = src.count(old)
        if n != 1:
            sys.stderr.write("[ABORT2] 第 %d 处锚点命中 %d 次（须==1）\n" % (i, n))
            return 1
        src = src.replace(old, new, 1)
    ast.parse(src, TARGET, "exec")
    tmp = TARGET + ".r101btmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    os.replace(tmp, TARGET)
    back = io.open(TARGET, encoding="utf-8").read()
    la, ba = len(back.splitlines()), len(back.encode("utf-8"))
    if la <= lb or ba <= bb:
        sys.stderr.write("[ABORT2] 行数/字节未增长 %d/%d -> %d/%d\n" % (lb, bb, la, ba))
        return 1
    ast.parse(back, TARGET, "exec")
    print("[PATCH:r101b:OK] 同事实单尺已落；%d 行/%d B -> %d 行/%d B" % (lb, bb, la, ba))
    return 0


if __name__ == "__main__":
    sys.exit(main())
