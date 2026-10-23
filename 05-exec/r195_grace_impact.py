# -*- coding: utf-8 -*-
"""r195_grace_impact.py — 只读测量「宽限表对主流标题写法失效」的影响面（不落盘、不改账）。

存在理由（r195 / R194-2）：RE_PRIORITY 旧式只认「【P0」方括号形态，而本仓主流条目写法是
圆括号（rNN 登记，P1）⇒ 大量条目读不到 P 级，GRACE_BY_PRIORITY 的 P1=4 / P2=8 从不生效，
一律走 GRACE_DEFAULT=2。§36.3 引用「339 条 / 209 条 / OVERDUE 76→74」三个数，必须可复算
（本仓 R189-2 / R191-1 两度教训：临时脚本会被并行会话清场 ⇒ 口径结论无人能复核）。

用法：python 05-exec/r195_grace_impact.py
输出：受检卷数、条目总数、旧式读不到 P 级的条数、改判据前后的分类位移（不落账本）。
退出：0（纯只读测量，恒 0；取不到面时打 UNVERIFIED 并 exit 2）
"""
import io
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import importlib  # noqa: E402

COLON = chr(65306)
RE_GRACE_HEAD = re.compile(r"(?:^|[^0-9A-Za-z])(P[0-2])(?:[^0-9]|$)")


def main():
    m = importlib.import_module("r38_debt_aging")
    now = m.current_round()
    now_round = now[0] if isinstance(now, tuple) else int(now or 0)
    files = m.volume_files()
    if not files:
        print("[GRACE-IMPACT:UNVERIFIED] 受检卷集为空，无面可测（R247）")
        return 2
    total = 0
    unreadable = 0
    flip = []
    dist_old = {}
    dist_new = {}
    for f in files:
        try:
            body = io.open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for line in body.splitlines():
            mm = m.RE_ITEM.match(line)
            if not mm:
                continue
            text = mm.group(2)
            total += 1
            # 旧式：全文 RE_PRIORITY.search
            mo = m.RE_PRIORITY.search(text)
            old_key = mo.group(1) if mo else "UNMARKED"
            # 新式：只看标题段（第一个全角冒号前）
            head = text.split(COLON)[0] if COLON in text else text
            mn = RE_GRACE_HEAD.search(head) or RE_GRACE_HEAD.search(text)
            new_key = mn.group(1) if mn else "UNMARKED"
            if old_key == "UNMARKED" and new_key != "UNMARKED":
                unreadable += 1
                flip.append((os.path.basename(f), new_key))
            go = m.GRACE_BY_PRIORITY.get(old_key, m.GRACE_DEFAULT)
            gn = m.GRACE_BY_PRIORITY.get(new_key, m.GRACE_DEFAULT)
            cls_old = _cls(m, text, now_round, go)
            cls_new = _cls(m, text, now_round, gn)
            dist_old[cls_old] = dist_old.get(cls_old, 0) + 1
            dist_new[cls_new] = dist_new.get(cls_new, 0) + 1
    print("受检卷数 = %d ｜ 条目总数 = %d ｜ 旧式读不到 P 级 = %d 条" % (len(files), total, unreadable))
    print("（旧式 RE_PRIORITY 只认「【P」方括号，圆括号（…，P1）读不到 ⇒ GRACE 表 P1=4/P2=8 从不生效）")
    print()
    print("%-10s %8s %8s %6s" % ("类", "旧式", "新式", "差"))
    for k in ("OVERDUE", "ACTIVE", "DECIDED", "DEFERRED", "REPEAT", "UNDATED"):
        o, n = dist_old.get(k, 0), dist_new.get(k, 0)
        print("%-10s %8d %8d %+6d" % (k, o, n, n - o))
    print()
    print("[GRACE-IMPACT:PASS] 只读测量，未写任何账本；复跑即得同值（round=%d）" % now_round)
    return 0


def _cls(m, text, now_round, grace):
    kind, arg = m.parse_last_verdict(text)
    if kind == "DEFER":
        return "DEFERRED" if arg > now_round else "OVERDUE"
    if kind == "FINAL":
        return "DECIDED"
    own = m.RE_TITLE_OWN.match(text)
    origin = int(own.group(1)) if own else None
    if origin is None:
        for x in m.RE_ROUND_DECL.finditer(text):
            if x.group(1) or x.group(2):
                origin = int(x.group(1) or x.group(2))
                break
    if origin is None:
        return "UNDATED"
    age = now_round - origin
    return "OVERDUE" if age > grace else "ACTIVE"


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
