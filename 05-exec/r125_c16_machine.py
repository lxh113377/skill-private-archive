# -*- coding: utf-8 -*-
r"""r125_c16_machine.py — R114-1 的 C1-C6 机器可判腿（C1/C3/C4 + 桶筛选）。

R114-1：152 件 MATCHED 桶 0 非空需逐件裁决。C2 需人读、C5/C6 是仓级门（常驻已绿），
本件把 C1（真 skill 仓）/ C3（license 合入）/ C4（12 个月内推送）跑全量，
把 168 件有候选者筛成「需人读 C2 的短名单」。

判据口径（迁移方案 §4，r118 补验证前提前置）：六条全满足才可写「更优」，
任一不满足 ⇒ KEEP 并写清是哪条挡住的。
"""
import argparse
import io, json, os, re
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# r211 修（本轮自犯，当场取证）：本件原把输入面与输出件**都写死成 r114/r125 那一对日期件**，
# 于是「拿新一轮的候选面复算机器腿」这件事做不到，而误跑一次就会把历史证据件的
# generated_at 原地改掉（本轮我实跑一次即撞上：diff 只剩时间戳、读数没变 ⇒ 历史留痕被刷）。
# 修法 = 输入面可指（缺省取 06-benchmark 下最新 replacement_matrix_r*.json），
# 输出件默认由输入名推导（新面 ⇒ 新件），且**已存在即拒写**（禁原地覆盖证据件，R241）。
OUT_DIR = os.path.join(ROOT, "06-benchmark")


def newest_matrix():
    cands = sorted(f for f in os.listdir(OUT_DIR)
                   if re.match(r"^replacement_matrix_r\d+.*\.json$", f))
    return os.path.join(OUT_DIR, cands[-1]) if cands else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", default=None,
                    help="候选面件（缺省 = 06-benchmark 下最新 replacement_matrix_r*.json）")
    ap.add_argument("--json", dest="out", default=None,
                    help="输出件（缺省 = 由输入名推导 c16_machine_<同后缀>.json）")
    ap.add_argument("--force", action="store_true",
                    help="显式允许覆盖已存在的输出件（默认拒写）")
    args = ap.parse_args(argv)
    matrix = args.matrix or newest_matrix()
    if not matrix or not os.path.isfile(matrix):
        print("[C16:UNVERIFIED] 取不到候选面 ⇒ 禁按无缺口记绿（R247）")
        return 2
    out_path = args.out
    if not out_path:
        stem = re.sub(r"^replacement_matrix_", "c16_machine_", os.path.basename(matrix))
        out_path = os.path.join(OUT_DIR, stem)
    if os.path.exists(out_path) and not args.force:
        print("[C16:REFUSE] 输出件已存在，拒绝原地覆盖历史证据：%s（要重算请另指 --json 或 --force）"
              % out_path)
        return 2
    m = json.load(io.open(matrix, encoding="utf-8"))
    out = []
    stats = {"total": 0, "no_candidate": 0, "c1_fail": 0, "c3_fail": 0, "c4_fail": 0,
             "need_c2_human": 0}
    now = datetime.utcnow()   # 统一 naive UTC，防 offset-naive/aware 混算
    for row in m["rows"]:
        stats["total"] += 1
        cands = row.get("candidates") or []
        if not cands:
            stats["no_candidate"] += 1
            out.append({"slug": row["slug"], "verdict": "KEEP", "blocked_by": "NO_CANDIDATE"})
            continue
        # 取分数最高的前 3 候选逐个判（迁移方案：逐件人读前 3 候选）
        ranked = sorted(cands, key=lambda c: -(c.get("score_total") or 0))
        top3 = ranked[:3]
        best_pass = None
        for c in top3:   # 判读范围 = top3（迁移方案 §R114-1 原文），出界不看
            c1 = (c.get("skill_md_n") or 0) > 0
            lic = (c.get("license") or "").lower()
            c3 = lic not in ("", "unlicensed", "unknown", "other", "none") and "agpl" not in lic
            pa = c.get("pushed_at") or ""
            try:
                pd = datetime.fromisoformat(pa.replace("Z", "+00:00")).replace(tzinfo=None)
                c4 = (now - pd).days <= 365
            except ValueError:
                c4 = False
            rec = {"slug": row["slug"], "repo": c.get("repo"),
                   "score_total": c.get("score_total"),
                   "c1_skill_md_n": c.get("skill_md_n"), "c3_license": c.get("license"),
                   "c4_pushed_at": pa,
                   "c1": c1, "c3": c3, "c4": c4}
            if c1 and c3 and c4:
                if best_pass is None:
                    best_pass = rec
        if best_pass:
            stats["need_c2_human"] += 1
            out.append(dict(best_pass, verdict="NEED_C2_HUMAN"))
        else:
            # 全被机器腿挡 ⇒ 挡路条按**分数最高候选**（ranked[0]）记，与 picked 同源
            c = ranked[0] if ranked else {}
            blocked = []
            if not (c.get("skill_md_n") or 0) > 0: blocked.append("C1")
            lic = (c.get("license") or "").lower()
            if lic in ("", "unlicensed", "unknown", "other", "none") or "agpl" in lic: blocked.append("C3")
            pa = c.get("pushed_at") or ""
            try:
                pd = datetime.fromisoformat(pa.replace("Z", "+00:00")).replace(tzinfo=None)
                if (now - pd).days > 365: blocked.append("C4")
            except ValueError:
                blocked.append("C4")
            if any((x.get("skill_md_n") or 0) > 0 for x in ranked[3:]):
                stats["blocked_top3_but_pool_has_skill"] = stats.get("blocked_top3_but_pool_has_skill", 0) + 1
            stats["c1_fail"] += blocked.count("C1")
            stats["c3_fail"] += blocked.count("C3")
            stats["c4_fail"] += blocked.count("C4")
            out.append({"slug": row["slug"], "verdict": "KEEP", "blocked_by": "+".join(blocked) or "MACHINE",
                        "top_repo": c.get("repo"), "top_score": c.get("score_total")})
    doc = {"schema": "c16-machine-r125-v2",
           "generated_at": datetime.now().isoformat(timespec="seconds"),
           "matrix": os.path.basename(matrix),
           "stats": stats, "rows": out}
    tmp = out_path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out_path)          # 原子写：禁把证据件写成半截
    print("matrix:", os.path.basename(matrix))
    print("stats:", json.dumps(stats, ensure_ascii=False))
    print("JSON -> %s" % os.path.relpath(out_path, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())