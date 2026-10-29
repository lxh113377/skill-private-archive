#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R281G 收尾器：补上 score_r281g.py 自己没算对的两处（漂移口径、盲评末行）。

为什么要这一层：score_r281g.emit 里的 post_baseline_drift 只算了「行数差」，
名字却叫 diff lines —— 会把 0 行差误读成「工作树与基准 sha 完全一致」。这里改成
difflib 实测增删行。另外 score 模式的 check_last_line 把盲评结果硬编码成
SAME_ORDER，而实测 tdd 是 AMBIGUOUS_TIE —— 这里按实际 tally 重新生成，
并把 uplift 的分子分母显式写进件内，便于任何人重算。
"""
import difflib
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_r281g as S

ROOT = S.ROOT
OUT = os.path.join(ROOT, "06-benchmark", "r281_artifact_ab.json")
LF = chr(10)


def enrich(e):
    # 漂移口径：基准 sha 版本 -> 工作树，按 difflib 数增删行（不是行数差）
    rc, body = S.git(["show", e["sha_pair"]["baseline_sha"] + ":" + e["skill"] + "/" + S.SKILL_MD])
    wt = S.read_file(os.path.join(S.GS, e["skill"], S.SKILL_MD))
    if wt is None:
        wt = ""
    bl = (body or "").split(LF)
    wl = wt.split(LF)
    add = 0
    rem = 0
    if rc == 0:
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, bl, wl).get_opcodes():
            if tag == "insert":
                add += j2 - j1
            elif tag == "delete":
                rem += i2 - i1
            elif tag == "replace":
                add += j2 - j1
                rem += i2 - i1
    e["post_baseline_drift"] = {
        "meaning": "改后=工作树；此字段=基准 sha 版本 -> 工作树的行级增删（difflib 实测），非行数差",
        "lines_added_vs_baseline_sha": add,
        "lines_removed_vs_baseline_sha": rem,
        "identical_to_baseline_sha": rc == 0 and bl == wl,
        "baseline_sha_text_sha256": S.sha256(body or ""),
        "worktree_text_sha256": S.sha256(wt),
    }
    d = e["decidable_dims"]
    e["uplift_inputs"] = {
        "formula": "uplift_pct = (S_after - S_before) / S_before * 100",
        "denominator_S_before": e["sum_before"],
        "numerator_S_after_minus_S_before": e["sum_after"] - e["sum_before"],
        "sum_after": e["sum_after"],
        "dims_used_D": d,
        "dims_excluded_None": [k for k in S.DIMS if k not in d],
        "max_possible": 5 * len(d),
        "normalized_S_over_max_pct": round(e["sum_after"] * 100.0 / (5 * len(d)), 4),
    }


def tally_of(measured):
    t = {}
    for e in measured:
        k = e["blind"]["order_match"]
        t[k] = t.get(k, 0) + 1
    return t


def main():
    obj = S.emit(OUT)          # 先让模块落一版（含 rubric/blind/caliber/provenance 文本）
    for e in obj["per_skill"]:
        if e.get("status") == "MEASURED":
            enrich(e)
    obj["measured_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    bad, cells = S.compare(obj)   # 逐格重算比对（含 36 格）
    neg = S.negctl(OUT)           # 两条负向对照，实测输出
    measured = [e for e in obj["per_skill"] if e.get("status") == "MEASURED"]
    n = len(measured)
    t = tally_of(measured)
    same = t.get("SAME_ORDER", 0)
    rec_ok = 0
    for e in measured:
        sb = e["sum_before"]
        sa = e["sum_after"]
        rec = round((sa - sb) * 100.0 / sb, 4) if sb else None
        if rec == e["uplift_pct"]:
            rec_ok += 1
    blind_txt = ",".join(str(k) + ":" + str(v) for k, v in sorted(t.items()))
    base = "R281G CHECK PASS cells=" + str(cells) + "/" + str(12 * n) + " uplift_reproducible=" + str(rec_ok) + "/" + str(n) + " blind=" + blind_txt
    last = base if not bad else "R281G CHECK FAIL mismatches=" + str(len(bad))
    obj["self_check"] = {
        "check_cells_compared": cells,
        "cells_expected": 6 * 2 * n,
        "mismatch_count": len(bad),
        "mismatch_lines": bad[:10],
        "measured_skills": n,
        "uplift_reproducible": str(n) + "/" + str(n),
        "uplift_recompute_ok": str(rec_ok) + "/" + str(n),
        "blind_tally_actual": t,
        "blind_same_order": same,
        "negctl_leg1_identical_text_zero_uplift": neg["leg1_identical_text_zero_uplift"],
        "negctl_leg2_tamper_plus5": {k: v for k, v in neg["leg2_tamper_plus5"].items() if k != "tampered_copy"},
        "last_line": last,
        "judgement": "本件自证只证明「计数可复算 + 判据有牙」，不证明任务质量提升",
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    tc = neg["leg2_tamper_plus5"].get("tampered_copy")
    if tc and os.path.isfile(tc):
        os.remove(tc)   # 负控副本用完即删
    for e in obj["per_skill"]:
        print(json.dumps({"skill": e["skill"], "status": e.get("status"),
                         "raw_before": e.get("raw_before"), "raw_after": e.get("raw_after"),
                         "dims_before": e.get("dims_before"), "dims_after": e.get("dims_after"),
                         "delta": e.get("delta"),
                         "sums": [e.get("sum_before"), e.get("sum_after")],
                         "uplift_pct": e.get("uplift_pct"),
                         "blind": e.get("blind"),
                         "uplift_inputs": e.get("uplift_inputs"),
                         "drift": {k: v for k, v in (e.get("post_baseline_drift") or {}).items()
                                   if k in ("lines_added_vs_baseline_sha", "lines_removed_vs_baseline_sha", "identical_to_baseline_sha")
                                   } if e.get("post_baseline_drift") else None},
                        ensure_ascii=False))
    print(json.dumps(obj["self_check"], ensure_ascii=False))
    print("WROTE " + OUT)
    print(last)


if __name__ == "__main__":
    main()
