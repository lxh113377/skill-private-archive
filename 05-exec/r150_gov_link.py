# -*- coding: utf-8 -*-
# r150_gov_link.py -- 契约履约数据 x 体量变化数据 联动读数面（第 58 门候选）。
#
# 存在理由（r150 现状核验实测）：两类治理各自都有 append-only 台账 ——
#   契约侧 06-benchmark/gate_runs.jsonl             478 轮 / 15 个活动日（2026-09-25..10-21）
#   体量侧 memory/sessions/volume-snapshots.jsonl    41 快照 / 11 个活动日（..2026-10-17）
# 但没有任何一处把它们放在同一条时间轴上：问「哪一轮体量涨了、那轮契约履约是不是也红了」，
# 机器答不出来。归属方的 volume_effect_report.py 只对账「心跳 x 快照」两把尺，实测共同日 0 个。
#
# 本件做三件事：
#   1) 按日联结（day-level join）：每契约履约日 x 每体量快照日，出 runs / 非 PASS 门 / 字节 / 环比；
#   2) 联结诊断（key alignment）：两册有无共享主键、各册字段覆盖度、各册末尾新鲜度；
#   3) 结构缺陷清单（advisory）：缺共享主键 / 体量册字段空缺 / 快照陈旧 / 共同日过少。
#
# 纪律（本项目 #33）：本件只出联合读数，不作因果断言。因果须另有实测面。
#
# 用法:
#   python 05-exec/r150_gov_link.py                 # 人读联动表
#   python 05-exec/r150_gov_link.py --json <件>     # 机读留痕
# 退出码: 0 可算且有共同日 / 2 任一侧零分母或零共同日（UNVERIFIED，R247 禁按绿记）
import argparse
import collections
import io
import json
import os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
STALE_WARN_DAYS = 2.0      # 体量册末条超过此天数即预警（与 volumegov 的 heartbeat_max_age_days 同向）
VOL_FIELDS_OF_INTEREST = ["files", "growth_ratio", "auto_moved", "auto_freed", "total_bytes"]
GATE_PROJ_KEYS = ("proj", "root", "repo", "project")
VOL_COMMIT_KEYS = ("head", "commit", "sha", "rev")


def load_jsonl(path):
    rows = []
    bad = 0
    if not os.path.isfile(path):
        return rows, bad
    for line in io.open(path, encoding="utf-8", errors="ignore"):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            bad += 1
    return rows, bad


def day_of(ts):
    return (ts or "")[:10]


def age_days(ts, now):
    if not ts:
        return None
    t = None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            t = datetime.strptime(ts[:19], fmt)
            break
        except Exception:
            continue
    if t is None:
        return None
    return round((now - t).total_seconds() / 86400.0, 2)


def build(root, now=None):
    now = now or datetime.now()
    gp = os.path.join(root, "06-benchmark", "gate_runs.jsonl")
    vp = os.path.join(root, "memory", "sessions", "volume-snapshots.jsonl")
    grows, gbad = load_jsonl(gp)
    vrows, vbad = load_jsonl(vp)

    gday = {}
    for r in grows:
        d = day_of(r.get("ts"))
        if not d:
            continue
        cur = gday.setdefault(d, {"runs": 0, "overall": collections.Counter(),
                                  "nongreen": collections.Counter(), "gates_run": 0, "total_ms": 0})
        cur["runs"] += 1
        cur["overall"][r.get("overall") or "?"] += 1
        cur["gates_run"] = max(cur["gates_run"], int(r.get("gates_run") or 0))
        cur["total_ms"] += int(r.get("total_ms") or 0)
        for gid, v in (r.get("per_gate") or {}).items():
            if v != "PASS":
                cur["nongreen"][gid] += 1

    vday = {}
    for r in vrows:
        d = day_of(r.get("ts"))
        if not d:
            continue
        vday[d] = r   # 同日多条取末条：快照为追加式，末条反映当日终态

    all_days = sorted(set(gday) | set(vday))
    joined = []
    for d in all_days:
        g = gday.get(d)
        v = vday.get(d)
        joined.append({
            "day": d,
            "gate_runs": g["runs"] if g else 0,
            "gate_overall": dict(g["overall"]) if g else None,
            "gate_nongreen_top": [x[0] for x in g["nongreen"].most_common(3)] if g else [],
            "vol_bytes": v.get("total_bytes") if v else None,
            "vol_moved": v.get("auto_moved") if v else None,
            "vol_freed": v.get("auto_freed") if v else None,
            "linked": bool(g and v),
        })
    prev_b = None
    for row in joined:
        b = row["vol_bytes"]
        if b is not None and prev_b:
            row["vol_delta_pct"] = round((b - prev_b) / float(prev_b) * 100.0, 2)
        else:
            row["vol_delta_pct"] = None
        if b is not None:
            prev_b = b
    common = [r for r in joined if r["linked"]]

    gkeys = set()
    for r in grows[:50]:
        gkeys |= set(r.keys())
    vkeys = set()
    for r in vrows[:50]:
        vkeys |= set(r.keys())
    g_proj = [k for k in gkeys if k in GATE_PROJ_KEYS]
    v_commit = [k for k in vkeys if k in VOL_COMMIT_KEYS]
    cov = {}
    for f in VOL_FIELDS_OF_INTEREST:
        cov[f] = sum(1 for r in vrows if r.get(f) not in (None, ""))
    last_g = grows[-1].get("ts") if grows else None
    last_v = vrows[-1].get("ts") if vrows else None
    ga = age_days(last_g, now)
    va = age_days(last_v, now)

    defects = []
    if not g_proj or not v_commit:
        defects.append({"kind": "NO_SHARED_KEY", "level": "P1", "detail":
                        "契约册项目键=%s / 体量册提交键=%s => 只能按日窗口粗联结，无法唯一定位哪一轮契约读数配哪一份体量快照"
                        % (g_proj or "无", v_commit or "无")})
    for f, n in cov.items():
        if n == 0 and vrows:
            defects.append({"kind": "VOL_FIELD_EMPTY", "level": "P1", "detail":
                            "体量册字段 %s 覆盖 0/%d => 联动分析缺该维度" % (f, len(vrows))})
    if va is not None and va > STALE_WARN_DAYS:
        defects.append({"kind": "VOL_LEDGER_STALE", "level": "P1", "detail":
                        "体量册末条 %s（%.2f 天前 > %.1f 天）=> 联动表右列停更、左列每天在动"
                        % (last_v, va, STALE_WARN_DAYS)})
    if len(common) < 3 and vrows and grows:
        defects.append({"kind": "FEW_COMMON_DAYS", "level": "P1", "detail":
                        "共同日仅 %d 个（契约日 %d / 体量日 %d）=> 样本量不足，联合读数不具判别力"
                        % (len(common), len(gday), len(vday))})

    return {
        "schema": "fj-gov-contract-volume-link-v1",
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "root": root,
        "gate_ledger": {"path": "06-benchmark/gate_runs.jsonl", "rows": len(grows), "bad_rows": gbad,
                        "days": len(gday), "last_ts": last_g, "age_days": ga, "keys": sorted(gkeys)},
        "vol_ledger": {"path": "memory/sessions/volume-snapshots.jsonl", "rows": len(vrows), "bad_rows": vbad,
                       "days": len(vday), "last_ts": last_v, "age_days": va, "keys": sorted(vkeys),
                       "field_coverage": cov, "field_denominator": len(vrows)},
        "joined": joined,
        "common_days": len(common),
        "defects": defects,
        "summary": {"common_days": len(common), "gate_days": len(gday), "vol_days": len(vday),
                    "defects_n": len(defects),
                    "defects_by_level": {lv: sum(1 for d in defects if d["level"] == lv)
                                         for lv in ("P0", "P1", "P2")}},
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args(argv)
    doc = build(os.path.abspath(args.root))
    gl = doc["gate_ledger"]
    vl = doc["vol_ledger"]
    print("[GOVLINK] 契约册 %d 行 / %d 日 / 末条 %s（%s 天前）"
          % (gl["rows"], gl["days"], gl["last_ts"], gl["age_days"]))
    print("[GOVLINK] 体量册 %d 行 / %d 日 / 末条 %s（%s 天前）"
          % (vl["rows"], vl["days"], vl["last_ts"], vl["age_days"]))
    print("[GOVLINK] 共享主键：契约册项目键 %s ｜ 体量册提交键 %s"
          % ([k for k in gl["keys"] if k in GATE_PROJ_KEYS] or "无",
             [k for k in vl["keys"] if k in VOL_COMMIT_KEYS] or "无"))
    print("[GOVLINK] 体量册字段覆盖（分母 %d）：%s"
          % (vl["field_denominator"], " ".join("%s=%d" % (k, v) for k, v in vl["field_coverage"].items())))
    print("[GOVLINK] 联动表（末 14 行：日 / 契约轮次 / 非绿门 / 体量字节 / 环比%）：")
    for r in doc["joined"][-14:]:
        ng = ("|".join(r["gate_nongreen_top"]) or "-") if r["gate_runs"] else "-"
        print("   %s  runs=%-3d nonGreen=%-26s bytes=%-12s dPct=%s"
              % (r["day"], r["gate_runs"], ng[:26], r["vol_bytes"], r["vol_delta_pct"]))
    for d in doc["defects"]:
        print("   %-4s %-16s %s" % (d["level"], d["kind"], d["detail"]))
    common = doc["common_days"]
    if gl["rows"] == 0 or vl["rows"] == 0 or common == 0:
        print("[GOVLINK:UNVERIFIED] 分母不足（契约册 %d 行 / 体量册 %d 行 / 共同日 %d）=> 不得按绿记（R247）"
              % (gl["rows"], vl["rows"], common))
        rc = 2
    else:
        s = doc["summary"]["defects_by_level"]
        print("[GOVLINK:PASS] 共同日 %d 个｜缺陷 %d 条（P0=%d P1=%d P2=%d）"
              % (common, doc["summary"]["defects_n"], s["P0"], s["P1"], s["P2"]))
        rc = 0
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print("[GOVLINK] 留痕 %s" % args.out)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
