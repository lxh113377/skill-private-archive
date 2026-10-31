# -*- coding: utf-8 -*-
"""r322c 自证：需求 6 的供给缺口读数。四条断言 + 一条负控；若真实语料将来出现短指令，本件必须转红逼重测。"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CEN = os.path.join(HERE, "corpus_census.json")


def main():
    d = json.load(open(CEN, encoding="utf-8"))
    errs = []
    if d.get("short_single_line") != 0:
        errs.append("short_single_line=%s 期望 0（若出现短指令须重测，不许沿用旧结论）" % d.get("short_single_line"))
    if d.get("user_msgs", 0) < 1900:
        errs.append("user_msgs=%s 面缩小" % d.get("user_msgs"))
    h = d.get("len_hist") or {}
    tot = sum(h.values()) or 1
    if h.get(">200", 0) / tot < 0.95:
        errs.append(">200 占比 %.3f < 0.95" % (h.get(">200", 0) / tot))
    if d.get("gm_user_utterance_hits", 0) < 5:
        errs.append("gm_user_utterance_hits=%s 期望 >=5" % d.get("gm_user_utterance_hits"))
    neg = os.environ.get("R322C_NEG")
    if neg == "short":
        ok = d.get("short_single_line") == 0
        print("[R322C:NEG] short teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    for e in errs:
        print("FAIL " + e)
    if errs:
        print("[R322C:POOL] short_single_line=%s verdict=SUPPLY_GAP teeth=FAIL" % d.get("short_single_line"))
        return 1
    print("[R322C:POOL] short_single_line=%d verdict=SUPPLY_GAP teeth=pass" % d.get("short_single_line"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
