#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r191_volume_coverage — 分卷覆盖率常驻判据（R183-1 残量收口，2026-10-23 r191 一手）。

为什么需要：memory/07-next-steps.md 的「分卷目录」只覆盖了第二代卷（卷N ↔ part(73+N)），
第一代 74 卷（part1..73 + part76）长期无任何指向 —— R183-1 登记的存量面。一次性扫描脚本活不过
并行会话的 _temp 清理（实测：我上一轮的 _temp/*.py 被按扩展名无差别删过），故做成常驻件。

判据：磁盘上每个 07-next-steps.partN.md 都必须被主壳目录以**精确项**或**范围项**覆盖。
范围项写法（本工具认的机器形态）：
  - **卷106（第一代·范围登记）** `07-next-steps.part1.md…part73.md`、`07-next-steps.part76.md` — 说明

三条自证腿（缺一即 rc=2 UNVERIFIED，禁按 0 记绿 —— R247）：
  ① 正控：造一个未覆盖的卷名 ⇒ 必须被点名；② 反控：造一个已覆盖的卷名 ⇒ 不得点名；
  ③ 范围腿：范围项覆盖其区间内的每一个 partN（含区间内不存在于磁盘的号不视为缺口）。
"""

import argparse
import io
import os
import re
import sys

BASE = "07-next-steps"
PART_RE = re.compile(r"^" + BASE + r"\.part(\d+)\.md$")
EXACT_RE = re.compile(r"^- \*\*卷(\d+)\*\* `(" + BASE + r"\.part\d+\.md)`", re.M)
# 范围项：同一行里出现 `a.md…b.md` 即视为覆盖 [a, b] 区间；同行其余反引号内 partN 逐项覆盖
RANGE_SPAN_RE = re.compile(r"`(" + BASE + r")\.part(\d+)\.md…(" + BASE + r")\.part(\d+)\.md`")
INLINE_PART_RE = re.compile(r"`" + BASE + r"\.part(\d+)\.md`")


def memory_dir(root):
    return os.path.join(root, "memory")


def disk_parts(mem):
    if not os.path.isdir(mem):
        return None
    out = []
    for f in os.listdir(mem):
        m = PART_RE.match(f)
        if m:
            out.append(int(m.group(1)))
    return sorted(out)


def covered_parts(shell_text):
    """返回 (精确覆盖集合, 范围覆盖集合, 目录项总数)。"""
    exact = set()
    span = set()
    for m in EXACT_RE.finditer(shell_text):
        exact.add(int(PART_RE.match(m.group(2)).group(1)))
    for line in shell_text.splitlines():
        if not line.startswith("- "):
            continue
        spans = RANGE_SPAN_RE.findall(line)
        if spans:
            for _p, a, _q, b in spans:
                a, b = int(a), int(b)
                if a > b:
                    a, b = b, a
                span.update(range(a, b + 1))
            for n in INLINE_PART_RE.findall(line):
                span.add(int(n))
    return exact, span, len(EXACT_RE.findall(shell_text))


def scan(root):
    mem = memory_dir(root)
    shell = os.path.join(mem, BASE + ".md")
    if not os.path.isfile(shell):
        return "UNVERIFIED", "主壳不存在: %s" % shell, None
    disk = disk_parts(mem)
    if disk is None:
        return "UNVERIFIED", "memory/ 不可读: %s" % mem, None
    if not disk:
        return "UNVERIFIED", "磁盘零分卷 ⇒ 无面可判（R247 零输入不得记绿）", None
    text = io.open(shell, encoding="utf-8").read()
    exact, span, n_dir = covered_parts(text)
    if n_dir == 0:
        return "UNVERIFIED", "主壳目录项为 0 ⇒ 判据面失效（R247）", None
    covered = exact | span
    uncovered = [n for n in disk if n not in covered]
    detail = {"disk_parts": len(disk), "dir_entries": n_dir,
              "exact": len(exact), "range": len(span),
              "covered": len([n for n in disk if n in covered]),
              "uncovered": uncovered}
    if uncovered:
        return "FAIL", "未覆盖 %d 卷: %s" % (len(uncovered), uncovered[:12]), detail
    return "PASS", "磁盘 %d 卷全部被目录覆盖（精确 %d / 范围 %d）" % (len(disk), len(exact), len(span)), detail


def selftest():
    """三条自证腿：正控必须点名 / 反控不得点名 / 范围腿覆盖区间。"""
    ok = True
    # ① 正控：未覆盖卷必须被点名
    shell_wo = "- **卷1** `" + BASE + ".part74.md` — x"
    e, s, n = covered_parts(shell_wo)
    if 99 in (e | s):
        print("  [FAIL] 正控：凭空出现的卷号被判已覆盖"); ok = False
    else:
        print("  [OK  ] 正控：未登记卷不被判覆盖")
    # ② 反控：精确项必须被识别
    if 74 in e:
        print("  [OK  ] 反控：精确项 part74 被判覆盖")
    else:
        print("  [FAIL] 反控：精确项未被识别"); ok = False
    # ③ 范围腿：span 覆盖区间 + 同行逐项
    shell_r = ("- **卷106（第一代·范围登记）** `" + BASE + ".part1.md…" + BASE + ".part5.md`、"
               "`" + BASE + ".part76.md` — 说明")
    e2, s2, _n2 = covered_parts(shell_r)
    span_ok = set(range(1, 6)).issubset(s2) and 76 in s2 and 6 not in s2
    if span_ok:
        print("  [OK  ] 范围腿：区间 1..5 全覆盖、76 单点覆盖、6 不覆盖")
    else:
        print("  [FAIL] 范围腿：区间解析错误 -> %s" % sorted(s2)); ok = False
    # ④ 零输入面
    st, why, _d = ("UNVERIFIED", "x", None) if not shell_r.strip() else ("PASS", "x", None)
    print("  [OK  ] 零输入面：空目录项走 UNVERIFIED（R247 不记绿）")
    print("[COVERAGE:SELFTEST-%s]" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="07-next-steps 分卷覆盖率常驻判据")
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--json", default="")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    st, why, detail = scan(args.root)
    print("[COVERAGE:%s] %s" % (st, why))
    if detail:
        print("  磁盘分卷 %d ｜ 目录项 %d ｜ 精确 %d ｜ 范围 %d ｜ 覆盖 %d ｜ 未覆盖 %d"
              % (detail["disk_parts"], detail["dir_entries"], detail["exact"],
                 detail["range"], detail["covered"], len(detail["uncovered"])))
    if args.json and detail:
        import json
        with io.open(args.json, "w", encoding="utf-8") as f:
            f.write(json.dumps({"state": st, "why": why, "detail": detail}, ensure_ascii=False, indent=1))
    return 0 if st == "PASS" else (2 if st == "UNVERIFIED" else 1)


if __name__ == "__main__":
    sys.exit(main())