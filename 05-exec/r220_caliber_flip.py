# -*- coding: utf-8 -*-
r"""r220_caliber_flip.py — 严格口径 vs 生产口径的「分桶翻转面」量化（只读，判据切换的前置定量）。

存在理由（r220 一手）：R211-9 把 skill_md_exact_n 建成双列读数后，「是否切换判据」被我记成
「须另行单独裁」——这句长期会变成无人接的待办，因为没人算过两件事：
  ① 切换会不会改变任何结论（翻转数）；
  ② 现有双读数覆盖多少行（够不够支撑切换）。
本轮实测答案：翻转 0，但覆盖 17/937 = 1.8% ⇒ 卡点是**测量覆盖**，不是等谁签字。
裁据因此写死在本件：覆盖 = 全部候选行 且 翻转 = 0 ⇒ 本仓自行切换并留 R241 校正注。

四态（禁静默）：
  FLIP:READY      翻转 0 且覆盖满 ⇒ 可切换（仍须独立提交）
  FLIP:CLEAN      翻转 0 但覆盖不足 ⇒ 不切换（等数据），具名缺覆盖行数
  FLIP:DETECTED   翻转 > 0 ⇒ 两口径结论不同，切换会改分桶 ⇒ 先逐条读翻转行
  FLIP:UNVERIFIED 矩阵件缺失/无 rows/无任何双读数行（rc=2，禁读成「无翻转」）

口径红线：
  · 只读 r114 产物 replacement_matrix.json，不重跑评分、不联网、不碰焚诀 eval；
  · 比较的是**布尔**（prod>0 与 exact>0），因为下游 r116 / r125 的 C1 判据就是
    skill_md_n > 0 这种「是否 skill 仓」标志；比数值大小会误报（同 3 仓各差 1 个 ghost 却都仍是 skill 仓）；
  · 无 exact 读数的行不计入翻转分母，但必须报覆盖率 —— 把「没测到」当「没翻转」就是假绿（R247）。

用法：python 05-exec/r220_caliber_flip.py [--matrix 件] [--json 件] [--selftest] [--quiet]
退出码：0 READY/CLEAN / 1 DETECTED / 2 UNVERIFIED。
"""
import argparse
import glob
import io
import json
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")


def read_json(path):
    try:
        return json.loads(io.open(path, encoding="utf-8-sig", errors="replace").read())
    except (OSError, ValueError):
        return None


def default_matrix():
    cands = []
    cands += glob.glob(os.path.join(BENCH, "quarterly", "*", "replacement_matrix.json"))
    cands += glob.glob(os.path.join(BENCH, "replacement_matrix_*.json"))
    if not cands:
        return None

    def key(p):
        m = re.search(r"(20\d\d-\d\d-\d\d)", os.path.basename(p))
        try:
            mt = os.path.getmtime(p)
        except OSError:
            mt = 0.0
        # 排序键 = (是否季度产物, 文件名内日期, mtime)。季度件的文件名固定是
        # replacement_matrix.json（无日期）⇒ 若只按日期串排，它会被排到最底，
        # 于是默认取到 06-benchmark 根的旧历史件（r217_miss_migration 修过同型 bug，
        # 本件首版又犯 ⇒ 由 selftest 之外的真实跑暴露，不是靠看代码）。季度件本身是
        # 每轮再生产物，优先级最高；同级再比日期、再比 mtime。
        return (1 if os.path.basename(p) == "replacement_matrix.json" else 0,
                m.group(1) if m else "", mt)
    return max(cands, key=key)


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def measure(doc):
    rows = (doc or {}).get("rows")
    if not isinstance(rows, list) or not rows:
        return None
    cands = []
    for r in rows:
        for c in (r.get("candidates") or []):
            cands.append((r.get("slug"), c))
    if not cands:
        return None
    both = [(s, c) for (s, c) in cands
            if is_int(c.get("skill_md_n")) and is_int(c.get("skill_md_exact_n"))]
    flips = [(s, c) for (s, c) in both
             if (c["skill_md_n"] > 0) != (c["skill_md_exact_n"] > 0)]
    ghosts = [(s, c) for (s, c) in both
              if c["skill_md_n"] - c["skill_md_exact_n"] > 0]
    cover = round(100.0 * len(both) / len(cands), 1)
    if not both:
        state = "UNVERIFIED"
    elif flips:
        state = "DETECTED"
    elif len(both) == len(cands):
        state = "READY"
    else:
        state = "CLEAN"
    examples = []
    for s, c in flips[:10]:
        examples.append({"slug": s,
                         "repo": c.get("repo") or c.get("full_name"),
                         "prod": c["skill_md_n"],
                         "exact": c["skill_md_exact_n"]})
    return {"candidates_total": len(cands),
            "rows_with_both_calibers": len(both),
            "rows_missing_exact": len(cands) - len(both),
            "coverage_pct": cover,
            "bucket_flag_flips": len(flips),
            "ghost_positive_rows": len(ghosts),
            "max_ghost_per_row": (max([c["skill_md_n"] - c["skill_md_exact_n"]
                                       for _, c in both]) if both else 0),
            "flip_examples": examples,
            "state": state}


def _doc(pairs):
    return {"rows": [{"slug": "s" + str(i),
                      "candidates": [{"repo": "r" + str(i),
                                      "skill_md_n": p,
                                      "skill_md_exact_n": e}]}
                     for i, (p, e) in enumerate(pairs)]}


def selftest():
    ok = True

    def chk(name, cond, got=""):
        if cond:
            print("  [OK  ] " + name)
        else:
            print("  [FAIL] " + name + "  <-- " + str(got))
        return bool(cond)

    m = measure(_doc([(5, 5), (3, 3)]))
    ok &= chk("正控：双读数全覆盖 + 零翻转 ⇒ READY", m["state"] == "READY", m["state"])
    m2 = measure(_doc([(5, 5), (0, 3)]))
    ok &= chk("变异：exact 使「是否 skill 仓」翻转 ⇒ DETECTED",
              m2["state"] == "DETECTED" and m2["bucket_flag_flips"] == 1, m2["state"])
    # 注意夹具必须是**两侧都 >0** 才对：首版我写成 (9, 0)，那是真翻转（exact=0 使
    # 「是否 skill 仓」变否），判据没错、夹具错 —— 自测腿自己也要可伪证（r215 立的规矩）。
    m3 = measure(_doc([(9, 2), (3, 3)]))
    ok &= chk("变异：数值差 9 但两侧都 >0 ⇒ 不得判翻转（布尔口径）",
              m3["bucket_flag_flips"] == 0, m3["flip_examples"])
    m4 = measure({"rows": [{"slug": "x", "candidates": [{"repo": "q", "skill_md_n": 9}]}]})
    ok &= chk("变异：全无 exact 读数 ⇒ UNVERIFIED（禁读成零翻转）",
              m4["state"] == "UNVERIFIED", m4["state"])
    m5 = measure(_doc([(5, 5), (3, 3), (2, 2), (7, 7)]))
    m5rows = _doc([(5, 5), (3, 3), (2, None), (7, None)])
    m6 = measure(m5rows)
    ok &= chk("变异：部分缺 exact ⇒ CLEAN 且覆盖 < 100（不得判 READY）",
              m6["state"] == "CLEAN" and m6["coverage_pct"] == 50.0
              and m6["rows_missing_exact"] == 2, m6)
    ok &= chk("正控读数不被污染（同件全覆盖版仍 READY）", m5["state"] == "READY", m5["state"])
    ok &= chk("空 rows ⇒ 不判（None）", measure({"rows": []}) is None, "")
    print("[FLIP:SELFTEST-" + ("PASS" if ok else "FAIL") + "]")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="严格口径 vs 生产口径的分桶翻转面量化（只读）")
    ap.add_argument("--matrix", default=None)
    ap.add_argument("--json", dest="out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if args.selftest:
        return selftest()
    path = args.matrix or default_matrix()
    if not path or not os.path.isfile(path):
        print("[FLIP:UNVERIFIED] 矩阵件不可得（" + str(path) + "）⇒ 不判，禁读成无翻转")
        return 2
    doc = read_json(path)
    if not isinstance(doc, dict):
        print("[FLIP:UNVERIFIED] 矩阵件不可读或解析失败 ⇒ 不判（R247）")
        return 2
    m = measure(doc)
    if m is None:
        print("[FLIP:UNVERIFIED] 矩阵件无 rows/candidates ⇒ 零输入不判")
        return 2
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    out = {"schema": "caliber-flip-r220-v1",
           "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
           "cmd": "python 05-exec/r220_caliber_flip.py",
           "inputs": {"matrix": rel, "producer": "05-exec/r114_replacement_scan.py"},
           "decision_rule": "覆盖=全部候选行 且 翻转=0 ⇒ 本仓自行把 C1 前置切到 skill_md_exact_n "
                            "并留 R241 校正注；否则保持旧口径不动（等数据，不等签字）",
           "reading": m}
    if not args.quiet:
        print("严格口径 vs 生产口径 分桶翻转面（矩阵件 = " + rel + "）")
        print("  候选行 " + str(m["candidates_total"])
              + " ｜有双读数 " + str(m["rows_with_both_calibers"])
              + "（覆盖 " + str(m["coverage_pct"]) + "%）"
              + " ｜缺 exact 读数 " + str(m["rows_missing_exact"])
              + " ｜分桶标志翻转 " + str(m["bucket_flag_flips"])
              + " ｜ghost>0 行 " + str(m["ghost_positive_rows"])
              + " ｜单行最大 ghost " + str(m["max_ghost_per_row"]))
        for x in m["flip_examples"]:
            print("  翻转：" + str(x["slug"]) + " " + str(x["repo"])
                  + " prod=" + str(x["prod"]) + " exact=" + str(x["exact"]))
    if args.out:
        tmp = args.out + ".tmp"
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, args.out)
        print("JSON -> " + os.path.relpath(args.out, ROOT))
    st = m["state"]
    if st == "DETECTED":
        print("[FLIP:DETECTED] 切换会改变分桶 ⇒ 先逐条读翻转行（禁止直接换判据凑整洁）")
        return 1
    if st == "READY":
        print("[FLIP:READY] 零翻转 + 全覆盖 ⇒ 可切换（仍须独立提交，不与本件混做）")
        return 0
    if st == "CLEAN":
        print("[FLIP:CLEAN] 零翻转，但覆盖仅 " + str(m["coverage_pct"])
              + "% ⇒ 保持旧口径；卡点是测量覆盖（需一次联网 --remeasure），不是等人")
        return 0
    print("[FLIP:UNVERIFIED] 无任何双口径读数行 ⇒ 不得据此说「严格口径不影响结论」")
    return 2


if __name__ == "__main__":
    sys.exit(main())
