# -*- coding: utf-8 -*-
"""r305_wiring_headroom.py — 「换装要不要动注入面、动得起吗」的可复算判据（r305 立，替掉空过的 C5）。

为什么立它（一手，r304）：方案 §4 的 C5 是「合入后 inject_union_bytes 不越硬顶」，判据是 ratchet_gate.py。
实测那条门禁的**成员面 5 条里不含被换装的两件**（A-prompt-better / frontend-skill）⇒ 它对我这两件**零约束**；
派发件把它标成「空过 vacuous pass」。⇒ 需要一条**真的对这两件有约束**的判据。

本件的约束口径（怎么运作）：
  换装本身（两件 SKILL.md 及其 scripts/references 侧车）**不进**注入面 ⇒ 不计字节；
  真正会动注入面的是**接线**：仓库落地时常要往注入面某个成员件里加/改一行路由或绑定（r261 起的做法）。
  于是判据 = Σ(接线编辑的字节增量，且**仅当**被编辑的路径在注入面成员清单内时才计入)  ≤  hard_cap − 实测并集。
  成员清单与硬顶**不写字面量**，现读常量件的 inject_budget（files / hard_cap_bytes）；并集去重照该门禁语义。

三态与边界：
  · 成员清单读不到 ⇒ rc=2 UNVERIFIED（禁按「余量充足」记）；
  · 编辑落在**非成员**文件 ⇒ 该条 delta 记为 0，但必须计入 ignored_files 具名显形（防「把面外改动算进面内」或反向漏算）；
  · 被换装两件自身是否在注入面内，本件**显式打印**（vacuous_face 检查），免得有人再拿 C5 的 ok 当「无风险」。

末行：[R305:HEADROOM] members=<n> live=<n> cap=<n> headroom=<n> wiring_needed=<n> verdict=<fits|exceeds|unverified> counted=<n> ignored=<n> swapped_in_face=<true|false>
退出码：0 判定成功 / 1 自证腿失败 / 2 输入不可得（常量件或清单读不到）。
"""
import argparse
import io
import json
import os
import sys

NL = chr(10)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # 自建skill优化/
TRUTH = "C:/Users/37533/Desktop/workspace/焚诀/eval/truth_constants.json"  # 现读：注入面清单与硬顶的唯一来源
SWAPPED = ("A-prompt-better", "frontend-skill")                            # r304 实测「空过」涉及的两件


def load_members():
    """读常量件的 inject_budget -> (成员路径列表, 硬顶, 基线)；读不到返回 (None, None, None)（调用方判 UNVERIFIED）。"""
    if not os.path.isfile(TRUTH):
        return None, None, None
    try:
        d = json.load(io.open(TRUTH, encoding="utf-8"))
    except (OSError, ValueError):
        return None, None, None
    ib = d.get("inject_budget") or {}
    files = ib.get("files") or []
    paths = []
    for f in files:
        p = f.get("path") if isinstance(f, dict) else str(f)
        if not p:
            continue
        # 相对路径（如 AGENTS.md）按本仓根解析；绝对路径原样
        paths.append(p if os.path.isabs(p) else os.path.join(ROOT, p))
    return paths, ib.get("hard_cap_bytes"), ib.get("baseline_bytes")


def norm(p):
    return os.path.normcase(os.path.abspath(p))


def measure(paths):
    """并集去重后的实测字节（去重的理由：同一件被两个 id 指到只应计一次，否则会虚增分母）。"""
    seen, tot, rows = set(), 0, []
    for p in paths:
        k = norm(p)
        if k in seen:
            continue
        seen.add(k)
        if os.path.isfile(p):
            n = os.path.getsize(p)
            tot += n
            rows.append((f.get_id() if False else "", p, n))
        else:
            rows.append(("", p, None))
    return tot, rows


def wire_delta(spec, paths):
    """接线编辑的字节增量：仅对落在成员清单内的路径计入；面外编辑计 0 但具名。
    spec 元素 = {"path": 被编辑件, "old": 原文, "new": 新文}（old 可为空串=纯新增）。"""
    members = {norm(p) for p in paths}
    need, counted, ignored = 0, [], []
    for e in spec or []:
        p = e.get("path") or ""
        o, n = e.get("old") or "", e.get("new") or ""
        d = len(n.encode("utf-8")) - len(o.encode("utf-8"))
        (counted if norm(p) in members else ignored).append({"path": p, "delta": d})
        if norm(p) in members:
            need += d
    return need, counted, ignored


def swapped_in_face(paths):
    """被换装的两件自身是否出现在注入面清单里 —— r304 的空过就是「成员面不含它们」。"""
    ns = " ".join(norm(p) for p in paths)
    return any(("global_skills/" + s).lower() in ns.lower() for s in SWAPPED)


def selftest():
    """两腿：① 超余量必判 exceeds（有牙）；② 面外编辑必须被忽略且具名（membership 真在起作用）。"""
    paths, cap, _b = load_members()
    if not paths or not cap:
        print("[R305:NC] 常量件读不到 ⇒ 自证不成立（rc=2）")
        return 2
    live, _rows = measure(paths)
    head = cap - live
    ok = True
    # 腿 1：把一个**成员**件的增量拉到远超余量 ⇒ 必判 exceeds
    d1, c1, i1 = wire_delta([{"path": paths[0], "old": "", "new": "x" * (head + 1)}], paths)
    v1 = "exceeds" if live + d1 > cap else "fits"
    print("[R305:NC-A] member edit delta=%d -> verdict=%s (expect exceeds)" % (d1, v1))
    ok &= (v1 == "exceeds")
    # 腿 2：把同一增量放到**面外**路径 ⇒ 必计 0 且具名 ignored
    d2, c2, i2 = wire_delta([{"path": os.path.join(ROOT, "_temp", "outside.md"), "old": "", "new": "x" * (head + 1)}], paths)
    v2 = "exceeds" if live + d2 > cap else "fits"
    print("[R305:NC-B] nonmember edit delta=%d ignored=%d -> verdict=%s (expect fits, ignored=1)" % (d2, len(i2), v2))
    ok &= (d2 == 0 and len(i2) == 1 and v2 == "fits")
    print("[R305:NC] legs=%s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="换装接线对注入面的字节约束（替代空过的 C5）")
    ap.add_argument("--spec", help="接线编辑清单 JSON：[{path, old, new}]（省略则只量现状与余量）")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    paths, cap, base = load_members()
    if not paths or not cap:
        print("[R305:HEADROOM] UNVERIFIED 常量件的 inject_budget 读不到 ⇒ 禁按余量充足记 rc=2")
        return 2
    live, rows = measure(paths)
    head = cap - live
    spec = []
    if a.spec:
        if not os.path.isfile(a.spec):
            print("[R305:HEADROOM] UNVERIFIED 接线清单不可得 rc=2")
            return 2
        spec = json.load(io.open(a.spec, encoding="utf-8"))
    need, counted, ignored = wire_delta(spec, paths)
    verdict = "fits" if live + need <= cap else "exceeds"
    sif = swapped_in_face(paths)
    for p, n in [(r[1], r[2]) for r in rows]:
        print("   %-58s %s" % (p[-58:], ("%d B" % n) if n is not None else "NOT-FOUND"))
    if spec:
        for c in counted:
            print("   [counted] %-52s %+d B" % (str(c["path"])[-52:], c["delta"]))
        for g in ignored:
            print("   [ignored] %-52s %+d B（非成员 ⇒ 不计入，但具名显形）" % (str(g["path"])[-52:], g["delta"]))
    print("   [VACUOUS-FACE] 被换装两件在注入面内 = %s（r304 实测为 false ⇒ C5 对它们零约束）" % sif)
    print("[R305:HEADROOM] members=%d live=%d cap=%d headroom=%d wiring_needed=%d verdict=%s counted=%d ignored=%d swapped_in_face=%s"
          % (len(paths), live, cap, head, need, verdict, len(counted), len(ignored), str(sif).lower()))
    if a.json:
        io.open(a.json, "w", encoding="utf-8", newline="").write(json.dumps(
            {"schema": "r305-wiring-headroom-v1", "members": paths, "live": live, "cap": cap,
             "baseline_bytes": base, "headroom": head, "wiring_needed": need, "verdict": verdict,
             "counted": counted, "ignored": ignored, "swapped_in_face": sif}, ensure_ascii=False, indent=1) + NL)
    return 0


if __name__ == "__main__":
    sys.exit(main())
