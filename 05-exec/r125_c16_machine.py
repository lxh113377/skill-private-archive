# -*- coding: utf-8 -*-
r"""r125_c16_machine.py — R114-1 的 C1-C6 机器可判腿（C1/C3/C4 + 桶筛选）。

R114-1：152 件 MATCHED 桶 0 非空需逐件裁决。C2 需人读、C5/C6 是仓级门（常驻已绿），
本件把 C1（真 skill 仓）/ C3（license 合入）/ C4（12 个月内推送）跑全量，
把 168 件有候选者筛成「需人读 C2 的短名单」。

判据口径（迁移方案 §4，r118 补验证前提前置）：六条全满足才可写「更优」，
任一不满足 ⇒ KEEP 并写清是哪条挡住的。
"""
import io, json, os, re
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATRIX = os.path.join(ROOT, '06-benchmark', 'replacement_matrix_r114_2026-10-18.json')

def main():
    m = json.load(io.open(MATRIX, encoding="utf-8"))
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
    json.dump({"schema": "c16-machine-r125-v1", "generated_at": datetime.now().isoformat(timespec="seconds"),
               "stats": stats, "rows": out},
              io.open(os.path.join(ROOT, "06-benchmark", "c16_machine_r125_2026-10-20.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("stats:", json.dumps(stats, ensure_ascii=False))
    print("JSON -> 06-benchmark/c16_machine_r125_2026-10-20.json")


if __name__ == "__main__":
    main()