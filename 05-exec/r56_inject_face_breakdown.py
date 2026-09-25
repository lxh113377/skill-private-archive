# -*- coding: utf-8 -*-
"""W-32 取值面生成器：把「注入面超顶」拆到**可指派归属**的粒度，并与棘轮同源对账。

存在理由（r56）：r52 那份 `inject_face_breakdown_r52_*.json` 是当时**一次性内联脚本**产出的，
仓里没有可复跑的生成器 ⇒ 它自己就是一个解不出的死句柄（W-34/W-36 正在管这件事）。
本脚本补上生成器，并强制三条自证：
  ① 与 `ratchet_gate.inject_union_bytes()` **同源**（复用同一个枚举器，不许两份算法各算一遍）；
  ② 逐件求和必须等于该值，不等即 `[BREAKDOWN:DRIFT]` 退出 1（防"拆解口径"与"判定口径"漂移）；
  ③ 有文件读不到 ⇒ 整体记 unknown（沿用 r50 覆盖面口径），**禁**跳过它继续求和。
只报告不阻断（r25 用户否决拦任务的闸门）；本脚本自身退出码只表示"数据是否自洽"。
"""
import argparse
import datetime
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import ratchet_gate as rg  # noqa: E402

MANAGED = ("D:\\global_skills", "D:\\global_memory", "D:\\global_memory_archive",
           "C:\\Users\\37533\\Desktop\\workspace\\焚诀")


def owner_of(path):
    p = os.path.normcase(os.path.abspath(path))
    for m in MANAGED:
        if p.startswith(os.path.normcase(m) + os.sep) or p == os.path.normcase(m):
            return "受管根（本项目不可改）"
    if p.startswith(os.path.normcase(ROOT)):
        return "本项目可控"
    return "其它（端上注入壳，归属另议）"


def main():
    ap = argparse.ArgumentParser(prog="r56_inject_face_breakdown.py")
    ap.add_argument("--json")
    ap.add_argument("--round", type=int, default=56)
    args = ap.parse_args()

    paths = sorted(rg.inject_union_paths())
    if not paths:
        print("[BREAKDOWN:UNVERIFIED] 枚举器取不到任何路径 ⇒ 不判 0（R247）")
        return 2
    rows, total, unreadable = [], 0, []
    for p in paths:
        try:
            b = os.path.getsize(p)
        except OSError:
            unreadable.append(p)
            continue
        total += b
        rows.append({"path": p, "bytes": b, "owner": owner_of(p)})
    canonical = rg.inject_union_bytes()
    drift = (unreadable or total != canonical)
    cap = (rg.hard_caps() or {}).get("inject_union_bytes")
    by_owner = {}
    for r in rows:
        by_owner[r["owner"]] = by_owner.get(r["owner"], 0) + r["bytes"]

    doc = {
        "schema": "inject-face-breakdown-v1",
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "readonly": True, "round": args.round, "cap": cap,
        "measured_total": None if drift else total,
        "over_cap": None if (drift or cap is None) else total - cap,
        "enumerator": "05-exec/ratchet_gate.py:inject_union_paths()（与棘轮同源，单份算法）",
        "cross_check": "python 05-exec/ratchet_gate.py 的 inject_union_bytes 行须等于本件 measured_total",
        "by_owner": by_owner,
        "files": sorted(rows, key=lambda r: -r["bytes"]),
        "decision_needed": (
            [] if drift or cap is None or total <= cap else [
            {"id": "W-32-A", "选项": "真降", "需要减": total - cap,
             "说明": "本项目可控面仅 %d B，减不动 21k 量级 ⇒ 必须动受管根（须受管根侧授权）"
                     % by_owner.get("本项目可控", 0)},
            {"id": "W-32-B", "选项": "显式改硬顶 + 逐因归因", "需要改": cap,
             "新值下限": total,
             "说明": "硬顶在焚诀 truth_constants.inject_budget.hard_cap_bytes，改它=改共享预算，"
                     "属受管根归属会话；本项目只出数不代改"}]),
    }
    print("注入面拆解：合计 %s B ｜ 硬顶 %s ｜ 枚举 %d 件 ｜ 不可读 %d 件"
          % (total if not drift else "unknown", cap, len(paths), len(unreadable)))
    for k in sorted(by_owner, key=lambda x: -by_owner[x]):
        print("   %-22s %8d B  (%.1f%%)" % (k, by_owner[k], 100.0 * by_owner[k] / total))
    if drift:
        print("[BREAKDOWN:DRIFT] 逐件求和 %s vs 棘轮口径 %s，不可读 %s ⇒ 记 unknown"
              % (total, canonical, unreadable[:3]))
        return 1
    print("[BREAKDOWN:CONSISTENT] 与 inject_union_bytes 同值（%d）" % canonical)
    if args.json:
        io.open(args.json, "w", encoding="utf-8", newline="").write(
            json.dumps(doc, ensure_ascii=False, indent=1))
        print("JSON -> %s" % args.json)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
