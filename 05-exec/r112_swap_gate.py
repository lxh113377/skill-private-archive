# -*- coding: utf-8 -*-
r"""r112_swap_gate.py — 第 19 维判定面：把「上游证据」翻成「我该不该动这一件」的裁决。

与 r105/r111 的关系（诚实交代，避免第三次造一把坏尺）：
  r105 词面尺（裸 token / IDF）与 r111 BGE 语义尺（六变体）先后被自己的标定控制判死——
  「相似度」在跨语言语料上没有鉴别力，无法回答「同源/不同源」，更无法回答「更好」。
  本件不造第三把相似度尺（R263 修机制不修数据），改判据：
      Q1 同源已证   —— 由内容寻址给出（r112_upstream_probe 的 relation），不靠相似度
      Q2 上游有本地没有的内容 —— upstream_only > 0（逐行可数）
      Q3 上游增量占优 —— upstream_only > local_only
      Q4 语义判重   —— 记录为 INVALID（r105 + r111 双向证伪），**对同源升级路径不构成阻断**：
                       同源即同一件事，判重问题在构造上不存在；判重只在「异名换装」时才需要，
                       而那条路径本轮明确不做（见报告「未闭环」节）。
  ⇒ 本尺的每一格都可逐行追溯，且不含任何模型。

裁决五态：
  UP_TO_DATE        本地 == 上游（逐字节或规范化行集合相同）
  UPGRADE_SAFE      本地行集合 ⊂ 上游 ⇒ 升级不丢本地任何一行，可直接走 rule_editor
  UPGRADE_REVIEW    两侧互有增量 ⇒ 上游有本地没有的内容，需人工合并（priority HIGH 当上游增量占优）
  LOCAL_AHEAD_KEEP  本地 ⊇ 上游 ⇒ 本地已增强，禁止自动覆盖（这正是「盲目换新会冲掉本地修复」的护栏）
  UNVERIFIED        取数面未证（同名但内容 unrelated / 取不到）—— 禁读成「已核对无缺口」

用法：
  python 05-exec/r112_swap_gate.py --scan 06-benchmark/provenance_r112_<date>.json \
         --probe 06-benchmark/upstream_r112_<date>.json --json 06-benchmark/swap_gate_r112_<date>.json
退出码：0 = 出件且守恒；2 = 输入面缺失（UNVERIFIED）。
"""
import argparse
import io
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

Q4_NOTE = "INVALID：r105 词面尺（裸 token/IDF）与 r111 BGE 语义尺六变体全部不可分（区间重叠）⇒ 语义判重不参与本裁决"


def decide(row):
    """纯函数：一条 probe 行 → 裁决。夹具直接驱动本函数（不在夹具里重写谓词）。"""
    if not isinstance(row, dict):
        return {"verdict": "UNVERIFIED", "reason": "not_a_dict"}
    if row.get("status") != "OK":
        return {"verdict": "UNVERIFIED",
                "reason": row.get("reason") or "probe_unverified",
                "q": {"Q1_same_source": None, "Q2_upstream_has_new": None,
                      "Q3_upstream_delta_dominant": None, "Q4_semantic_dup": Q4_NOTE}}
    rel = row.get("relation")
    st = row.get("stats") or {}
    uo = st.get("upstream_only") or 0
    lo = st.get("local_only") or 0
    q = {"Q1_same_source": rel in ("identical", "same_content", "upstream_ahead",
                                   "local_ahead", "diverged"),
         "Q2_upstream_has_new": uo > 0,
         "Q3_upstream_delta_dominant": uo > lo,
         "Q4_semantic_dup": Q4_NOTE}
    if rel in ("identical", "same_content"):
        return {"verdict": "UP_TO_DATE", "q": q,
                "evidence": {"upstream_sha256": row.get("upstream_sha256"),
                             "local_sha256": row.get("local_sha256"),
                             "upstream_last_commit_date": row.get("upstream_last_commit_date")}}
    if rel == "upstream_ahead":
        return {"verdict": "UPGRADE_SAFE", "q": q,
                "evidence": {"upstream_only": uo, "local_only": lo,
                             "upstream_repo": row.get("upstream_repo"),
                             "upstream_path": row.get("upstream_path")}}
    if rel == "local_ahead":
        return {"verdict": "LOCAL_AHEAD_KEEP", "q": q,
                "evidence": {"local_only": lo, "upstream_only": uo}}
    if rel == "diverged":
        if uo > 0:
            return {"verdict": "UPGRADE_REVIEW", "q": q,
                    "priority": "HIGH" if uo > lo else "NORMAL",
                    "evidence": {"upstream_only": uo, "local_only": lo,
                                 "upstream_repo": row.get("upstream_repo"),
                                 "upstream_path": row.get("upstream_path"),
                                 "upstream_last_commit_date": row.get("upstream_last_commit_date"),
                                 "upstream_last_commit_msg": row.get("upstream_last_commit_msg")}}
        return {"verdict": "LOCAL_AHEAD_KEEP", "q": q, "evidence": {"local_only": lo, "upstream_only": uo}}
    return {"verdict": "UNVERIFIED", "reason": "unknown_relation:%s" % rel, "q": q}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", required=True)
    ap.add_argument("--probe", required=True)
    ap.add_argument("--json", dest="json_out", default=None)
    args = ap.parse_args()

    def _p(p):
        return p if os.path.isabs(p) else os.path.join(ROOT, p)

    if not os.path.isfile(_p(args.scan)):
        print("[SWAP:UNVERIFIED] 来源扫描件缺失: %s" % args.scan)
        return 2
    if not os.path.isfile(_p(args.probe)):
        print("[SWAP:UNVERIFIED] 上游证据件缺失: %s" % args.probe)
        return 2
    scan = json.load(io.open(_p(args.scan), encoding="utf-8-sig"))
    probe = json.load(io.open(_p(args.probe), encoding="utf-8-sig"))

    total_face = (scan.get("face") or {}).get("authority_skill_n") or len(scan.get("rows") or [])
    tiers = scan.get("tiers") or {}
    seen = {r["slug"]: r for r in (scan.get("rows") or [])}

    rows = []
    for pr in (probe.get("rows") or []):
        d = decide(pr)
        rows.append({
            "slug": pr.get("slug"),
            "verdict": d["verdict"],
            "priority": d.get("priority"),
            "reason": d.get("reason"),
            "q": d.get("q"),
            "evidence": d.get("evidence"),
            "relation": pr.get("relation"),
            "stats": pr.get("stats"),
            "upstream_repo": pr.get("upstream_repo"),
            "upstream_path": pr.get("upstream_path"),
            "upstream_last_commit_date": pr.get("upstream_last_commit_date"),
            "upstream_last_commit_msg": pr.get("upstream_last_commit_msg"),
            "provenance_tier": (seen.get(pr.get("slug")) or {}).get("confidence"),
        })

    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1

    same_source_n = len(rows)
    behind = [r for r in rows if r["verdict"] in ("UPGRADE_SAFE", "UPGRADE_REVIEW")]
    behind.sort(key=lambda r: -((r.get("evidence") or {}).get("upstream_only") or 0))

    doc = {
        "schema": "swap-gate-r112-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ruler": {
            "kind": "content_addressed",
            "q1": "同源已证（内容寻址，非相似度）",
            "q2": "upstream_only > 0",
            "q3": "upstream_only > local_only",
            "q4": Q4_NOTE,
        },
        "face": {
            "total_skill_n": total_face,
            "provenance_tiers": tiers,
            "same_source_judged_n": same_source_n,
            "coverage_ratio": round(same_source_n / total_face, 4) if total_face else None,
            "probe_file": os.path.basename(args.probe),
            "scan_file": os.path.basename(args.scan),
            "blind_n": total_face - same_source_n,
        },
        "counts": counts,
        "behind_list": [{"slug": r["slug"], "verdict": r["verdict"], "priority": r["priority"],
                         "upstream_only": (r.get("evidence") or {}).get("upstream_only"),
                         "local_only": (r.get("evidence") or {}).get("local_only"),
                         "upstream": "%s/%s" % (r.get("upstream_repo"), r.get("upstream_path")),
                         "upstream_last_commit_date": r.get("upstream_last_commit_date")}
                        for r in behind],
        "rows": rows,
    }
    if args.json_out:
        outp = _p(args.json_out)
        os.makedirs(os.path.dirname(outp), exist_ok=True)
        io.open(outp, "w", encoding="utf-8", newline="\n").write(
            json.dumps(doc, ensure_ascii=False, indent=1))
        print("JSON -> %s" % outp)

    print("面：技能总数 %d ｜ 同源可判 %d（覆盖 %.1f%%）｜ 盲区 %d"
          % (total_face, same_source_n, 100.0 * same_source_n / total_face if total_face else 0,
             doc["face"]["blind_n"]))
    print("裁决分布：%s" % json.dumps(counts, ensure_ascii=False))
    print("上游有本地没有的内容（待比对/可升级）%d 件：" % len(behind))
    for b in doc["behind_list"]:
        print("  %-38s %-14s upstream_only=%-4s local_only=%-4s 上游提交 %s"
              % (b["slug"], b["verdict"], b["upstream_only"], b["local_only"],
                 (b["upstream_last_commit_date"] or "?")[:10]))
    unv = [r["slug"] for r in rows if r["verdict"] == "UNVERIFIED"]
    if unv:
        print("UNVERIFIED（同名但非同源/取不到，禁读成已核对）%d 件：%s" % (len(unv), ", ".join(unv)))
    print("[SWAP:GATE] counts=%s" % json.dumps(counts, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
