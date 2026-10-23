# -*- coding: utf-8 -*-
r"""r112_provenance_face.py — 第 19 维常驻门（第 30 门）：身份面自洽性 + 覆盖自证（离线）。

为什么需要它：
  新开的「版本落后面」如果只在报告里说一次结论，下一轮没人知道它还在不在守着。
  本门把该维度的**结构性事实**钉成可复算判据（不联网、不依赖上游可达）：
    C1 来源扫描：三档置信度之和 == 扫到的技能总数（守恒）
    C2 pin 台账：① 每个 declared/inferred 件都在册 ② unknown 件不得被登记（不猜）
                  ③ **无空转**（同 slug 相邻两条记录的内容键必须不同 —— R306 内容寻址不变腿）
    C3 上游证据：OK + UNVERIFIED == 目标数；每条 UNVERIFIED 必须有非空 reason（禁静默跳过）
    C4 裁决面：裁决行数 == 证据面 OK 行数；各裁决之和 == 行数；UNVERIFIED 逐件具名
    C5 覆盖自证：打印总面 / 同源可判面 / 盲区（R20-2，且禁把盲区读成「无缺口」）

三态：缺件 ⇒ rc=2（UNVERIFIED，R247 不得算绿）；不一致 ⇒ rc=1（FAIL）；全过 ⇒ rc=0 且印 token。

用法：python 05-exec/r112_provenance_face.py [--bench 06-benchmark]
"""
import argparse
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOKEN = "[PROVENANCE:PASS]"
CONTENT_KEYS = ("slug", "source_state", "identity", "local_sha256", "local_bytes", "local_dir_sha256")


def ckey(rec):
    return json.dumps({k: rec.get(k) for k in CONTENT_KEYS}, ensure_ascii=False, sort_keys=True)


def check_ledger_churn(recs):
    """同 slug 相邻两条内容键相同 ⇒ 空转（跑一趟就写一次盘，违 R306）。返回违规 slug 列表。"""
    bad, last = [], {}
    for r in recs:
        s = r.get("slug")
        if not s:
            bad.append("<no-slug>")
            continue
        k = ckey(r)
        if s in last and last[s] == k:
            bad.append(s)
        last[s] = k
    return bad


_NAME_DATE = re.compile(r'(20\d\d-\d\d-\d\d)')


def latest(bench, pattern):
    # r113 修（一手实测）：原按文件名排序取尾，`provenance_r112b_2026-10-17` 会排在
    # `provenance_r112_2026-10-18` 之后（'b' > '_'），于是**新件被旧件压住**，门读的是
    # 上一代三档面却自报 PASS。当时改用 mtime 取新。
    #
    # r189 补（一手实测，CI 连续判红的根因之一）：**mtime 在全新 clone / CI 里全部相同**
    # （checkout 统一打时间戳）⇒ 平局又退化回按名排序，r113 那个 bug 在 CI 必然复发。
    # 实测：工作区 latest() 选 provenance_r112_2026-10-18（对），clone 选
    # provenance_r112b_2026-10-17（错，上一代）——同一门本地绿、CI 报 127 条 unknown 假红。
    # 名字里的日期是这份命名法自带的时间轴，且跨 checkout 稳定 ⇒ 作第一级；mtime 降为
    # 第二级（无日期的件仍要能排），名字最后兜底。保守方向不变：仍然取"新"，不放宽判据。
    hits = glob.glob(os.path.join(bench, pattern))
    if not hits:
        return None

    def _key(q):
        b = os.path.basename(q)
        m = _NAME_DATE.search(b)
        return (m.group(1) if m else "", os.path.getmtime(q), b)

    return max(hits, key=_key)


def load(p):
    if not p or not os.path.isfile(p):
        return None
    try:
        return json.load(io.open(p, encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        print("  读取失败 %s: %r" % (p, exc))
        return None


def load_jsonl(p):
    recs = []
    if not p or not os.path.isfile(p):
        return recs
    for ln in io.open(p, encoding="utf-8-sig"):
        ln = ln.strip()
        if ln:
            try:
                recs.append(json.loads(ln))
            except ValueError:
                recs.append({"slug": "<bad-json-line>"})
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", default=os.path.join(ROOT, "06-benchmark"))
    args = ap.parse_args()
    bench = args.bench

    # r113 修面（一手）：原 glob 只认 `_r112_`，任何后续轮次按 `_r1NN_` 命名的新证据件
    # 对本门**隐形**——门会抱着 r112 陈旧件判绿/判红而看不见盘上更新的那份（本轮实测：
    # pin 台账已含 self_built 74 行，门仍读三档旧件报 71 条「unknown 被登记」假红）。
    # 修法 = 扩到 provenance_r1* 全族（按名排序，日期后缀决定现值），不是豁免某轮。
    scan_p = latest(bench, "provenance_r1*.json")
    probe_p = latest(bench, "upstream_r1*.json")
    swap_p = latest(bench, "swap_gate_r1*.json")
    pins_p = os.path.join(bench, "upstream_pins.jsonl")
    missing = [n for n, p in (("scan", scan_p), ("probe", probe_p), ("swap", swap_p), ("pins", pins_p))
               if not p or not os.path.isfile(p)]
    if missing:
        print("[PROVENANCE:UNVERIFIED] 证据面缺件: %s（零输入不得判绿，R247）" % ",".join(missing))
        return 2

    scan, probe, swap = load(scan_p), load(probe_p), load(swap_p)
    pins = load_jsonl(pins_p)
    if scan is None or probe is None or swap is None:
        print("[PROVENANCE:UNVERIFIED] 证据面不可读")
        return 2

    fails = []
    # C1
    tiers = scan.get("tiers") or {}
    # r113 四档：v1 件无 self_built 键（get 缺省 0 即自洽），v2 件四键求和
    t_sum = sum(tiers.get(k, 0) for k in ("declared", "inferred", "self_built", "unknown"))
    total = (scan.get("face") or {}).get("authority_skill_n") or len(scan.get("rows") or [])
    if t_sum != total:
        fails.append("C1 三档之和 %d != 总数 %d" % (t_sum, total))
    # C2
    pinned = {}
    for r in pins:
        pinned.setdefault(r.get("slug"), []).append(r)
    need = {r["slug"]: r.get("confidence") for r in (scan.get("rows") or [])}
    for slug, conf in need.items():
        if conf in ("declared", "inferred", "self_built") and slug not in pinned:
            fails.append("C2 有身份但未入 pin 台账: %s" % slug)
        if conf == "unknown" and slug in pinned:
            fails.append("C2 unknown 件被登记（禁猜）: %s" % slug)
    churn = check_ledger_churn(pins)
    if churn:
        fails.append("C2 台账空转 %d 条（同 slug 相邻内容键相同，违 R306）: %s"
                     % (len(churn), ", ".join(sorted(set(churn))[:5])))
    # C3
    prows = probe.get("rows") or []
    tgt = (probe.get("face") or {}).get("targets_n")
    ok = [r for r in prows if r.get("status") == "OK"]
    unv = [r for r in prows if r.get("status") != "OK"]
    if tgt != len(prows):
        fails.append("C3 目标数 %s != 证据行数 %d" % (tgt, len(prows)))
    cons = probe.get("conservation") or {}
    if not cons.get("ok", False):
        fails.append("C3 上游证据守恒破坏: %s" % json.dumps(cons, ensure_ascii=False))
    for r in unv:
        if not (r.get("reason") or "").strip():
            fails.append("C3 UNVERIFIED 无理由（静默跳过）: %s" % r.get("slug"))
    # C4
    srows = swap.get("rows") or []
    if len(srows) != len(prows):
        fails.append("C4 裁决行数 %d != 证据行数 %d（每条证据都必须有裁决）" % (len(srows), len(prows)))
    judged_n = sum(1 for r in srows if r.get("verdict") != "UNVERIFIED")
    if judged_n != len(ok):
        fails.append("C4 非 UNVERIFIED 裁决 %d != 证据 OK 行数 %d（防把取不到的面判成通过）"
                     % (judged_n, len(ok)))
    counts = swap.get("counts") or {}
    if sum(counts.values()) != len(srows):
        fails.append("C4 裁决分布之和 != 行数")
    # C5 coverage self-证
    same_source = (swap.get("face") or {}).get("same_source_judged_n")
    roots = (scan.get("face") or {}).get("roots") or []

    print("覆盖根自证：%s" % json.dumps(roots, ensure_ascii=False))
    print("总面 %d ｜ 同源可判 %s ｜ 盲区 %s（盲区禁读成「无缺口」）"
          % (total, same_source, total - (same_source or 0)))
    print("四档：%s ｜ pin 台账 %d 行 / %d slug ｜ 上游证据 OK=%d UNVERIFIED=%d"
          % (json.dumps(tiers, ensure_ascii=False), len(pins), len(pinned), len(ok), len(unv)))
    print("裁决：%s" % json.dumps(counts, ensure_ascii=False))
    if unv:
        print("具名 UNVERIFIED（上游证据面）: %s" % ", ".join(sorted(r.get("slug", "?") for r in unv)))
    urows = [r.get("slug") for r in srows if r.get("verdict") == "UNVERIFIED"]
    if urows:
        print("具名 UNVERIFIED（裁决面）: %s" % ", ".join(sorted(urows)))

    if fails:
        for f in fails:
            print("  FAIL: %s" % f)
        print("[PROVENANCE:FAIL] %d 项" % len(fails))
        return 1
    print(TOKEN)
    return 0


if __name__ == "__main__":
    sys.exit(main())
