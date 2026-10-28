# -*- coding: utf-8 -*-
"""r260_quarterly_cadence.py — 需求5「季度巡检」的**节律看门狗**（CI 可跑，纯 stdlib）。

为什么存在：巡检器 r113_quarterly_audit.py 本身能跑（19 步已实测），但「季度」二字此前
不成立 —— CI 里 `grep quarterly` 命中 0，节律全靠人记得跑（独立复核实测）。把整支深度巡检
搬进 CI 也不对：它要现扫受管根（D 盘 global_skills）、要 managed venv 的 numpy/jinja2/networkx，
换机必假红（本仓 X-1 与「两台机专属门是设计边界」同口径）。CI 该干的是**盯人**：季产物
超龄就叫，叫到有人跑为止 —— 这正是 gate_run_freshness 用「CI 绿不能替人证明本机门在跑」的反向用法。

怎么运作：
  1) 找面：扫 06-benchmark/quarterly*/<季>/audit.json，取 generated_at 最新的一份（**不靠目录名排序**，
     目录名会漂；r259 一手教训 = 读数必须随件走，不随名字走）；
  2) 算龄：age_days = 今日 - generated_at；age > max_days 即判红并点名该件；
  3) 三态退出码与 run_gates 同口径：0 PASS / 1 超龄（真故障）/ 2 UNVERIFIED（无件、无 generated_at、
     时间戳不可析 —— R247 禁把「取不到」读成「没超期」）；
  4) --selftest：进程内三腿（新鲜⇒绿 / 陈旧⇒**必须红** / 缺件⇒UNVERIFIED）+ 变异对照
     （把「超龄判红」摘掉后，陈旧腿必转绿 ⇒ 证该腿承重），全部走 tempfile，绝不碰真件（X-20）。
"""

import argparse
import glob
import io
import json
import os
import sys
import tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATE_FMT = "%Y-%m-%dT%H:%M:%S"


def newest_audit(root=ROOT):
    """返回 (path, generated_at_datetime) 或 (None, None)；面为空 ⇒ 交调用方判 UNVERIFIED。"""
    best = None
    for pat in ("06-benchmark/quarterly*" + os.sep + "*" + os.sep + "audit.json",
                "06-benchmark/quarterly*" + os.sep + "audit.json"):
        for p in glob.glob(os.path.join(root, pat)):
            try:
                doc = json.load(io.open(p, encoding="utf-8-sig"))
            except Exception:
                continue                       # 不可析的件不进面（但面为空仍会被判 UNVERIFIED）
            ts = doc.get("generated_at") or doc.get("face", {}).get("generated_at")
            if not ts:
                continue
            try:
                d = datetime.strptime(str(ts)[:19], DATE_FMT)
            except ValueError:
                continue
            if best is None or d > best[1]:
                best = (p, d)
    return best if best else (None, None)


def judge(ts, now, max_days):
    """核心判据：单一纯函数，便于夹具与变异对照复用。返回 (rc, 说明)。"""
    if ts is None:
        return 2, "无季产物或 generated_at 不可析 ⇒ UNVERIFIED（禁按未超期记绿）"
    age = (now - ts).total_seconds() / 86400.0
    if age > max_days:
        return 1, "季产物超龄 %.1f 天 > 上限 %s 天 ⇒ 季度巡检该跑了" % (age, max_days)
    return 0, "季产物龄期 %.1f 天 ≤ 上限 %s 天" % (age, max_days)


def selftest():
    """三腿 + 变异。夹具全在 tempfile 里造，绝不读改真件（X-20 禁拿真实记忆卷做冒烟）。"""
    now = datetime(2026, 10, 28, 12, 0, 0)
    rows = []

    def ck(name, cond, detail=""):
        rows.append((bool(cond), name, str(detail)[:200]))
        print("%-4s %s%s" % ("PASS" if cond else "FAIL", name, "" if cond else "  <-- " + str(detail)[:180]))

    rc0, w0 = judge(datetime(2026, 10, 20, 12, 0, 0), now, 100)
    ck("t1 新鲜（8 天）⇒ rc=0", rc0 == 0, (rc0, w0))
    rc1, w1 = judge(datetime(2026, 1, 1, 12, 0, 0), now, 100)
    ck("t2 反例（必须仍红）：超龄 300 天 ⇒ rc=1", rc1 == 1, (rc1, w1))
    rc2, w2 = judge(None, now, 100)
    ck("t3 空面 ⇒ rc=2 UNVERIFIED（非 0）", rc2 == 2, (rc2, w2))
    # 变异：摘掉超龄判定（恒 0）⇒ t2 的应红前提失效，证 t2 不是恒红也不是摆设
    def judge_mutated(ts, now_, max_days):
        return (0, "mutated") if ts else (2, "empty")
    ck("t4 变异对照：恒 0 版会把超龄判成绿（证 t2 有牙）",
       judge_mutated(datetime(2026, 1, 1), now, 100)[0] == 0)
    # 真实面自证：临时目录里放一份新鲜 audit.json，走 newest_audit 取回，证明取数路径接得上
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "06-benchmark", "quarterlyX", "2026Q4"))
        doc = {"generated_at": now.strftime(DATE_FMT)}
        io.open(os.path.join(td, "06-benchmark", "quarterlyX", "2026Q4", "audit.json"),
                "w", encoding="utf-8").write(json.dumps(doc))
        p, ts = newest_audit(td)
        ck("t5 真接线：newest_audit 能从目录树取回 generated_at", p is not None and ts == now,
           (p, str(ts)))
    fails = [n for ok, n, _ in rows if not ok]
    print("夹具合计: %d 项，通过 %d，失败 %d" % (len(rows), len(rows) - len(fails), len(fails)))
    if fails:
        print("[CADENCE:SELFTEST-FAIL] %s" % fails)
        return 1
    print("[CADENCE:SELFTEST-PASS] 5 腿含 t2 必须仍红 + t4 变异 + t5 真接线")
    return 0


def main():
    ap = argparse.ArgumentParser(prog="r260_quarterly_cadence.py")
    ap.add_argument("--max-days", type=int, default=100,
                    help="季产物龄期上限（季度 91~92 天 + 缓冲 ⇒ 默认 100）")
    ap.add_argument("--json", dest="out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    path, ts = newest_audit()
    rc, why = judge(ts, datetime.now(), args.max_days)
    doc = {"schema": "r260-quarterly-cadence-v1", "readonly": True,
           "provenance_cmd": "python 05-exec/r260_quarterly_cadence.py --json <件>",
           "newest_audit": os.path.relpath(path, ROOT) if path else None,
           "generated_at": ts.strftime(DATE_FMT) if ts else None,
           "max_days": args.max_days, "rc": rc, "reading": why}
    if args.out:
        d = os.path.dirname(os.path.abspath(args.out))
        if d:
            os.makedirs(d, exist_ok=True)
        # newline=chr(10)：本仓第八形态铁律 —— 反斜杠字面量经工具 JSON 解码会被吃掉，
        # 用 chr(10) 构造换行常量，避免写成 "\n" 时被剥成裸换行把语句切断。
        io.open(args.out, "w", encoding="utf-8", newline=chr(10)).write(json.dumps(doc, ensure_ascii=False, indent=1))
    print("[CADENCE] 最新季产物 = %s（%s）" % (doc["newest_audit"], doc["generated_at"]))
    print("[CADENCE] %s" % why)
    if rc == 0:
        print("[CADENCE:PASS] 季度节律在限内")
    elif rc == 1:
        print("[CADENCE:FAIL] 季度巡检超龄 ⇒ 跑 python 05-exec/r113_quarterly_audit.py --offline")
    else:
        print("[CADENCE:UNVERIFIED] 季产物面取不到（R247 不记绿）")
    if args.out:
        print("JSON -> %s" % args.out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
