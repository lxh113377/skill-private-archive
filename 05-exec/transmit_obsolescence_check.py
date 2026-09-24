# -*- coding: utf-8 -*-
r"""transmit_obsolescence_check.py — 转办件过期检测：外推前先查归属方是否已自落。

存在理由（2026-09-24 实测）：r20b 我按「让号 C31′/C32′/C33′」把三项判据转办给焚诀归属会话，
r21c 复测才发现对方**已自落 C31/C32** ⇒ 转办件两项早已过期。当时靠人工逐条复测抓到，属自觉型；
本件把同等判定变成机器型：把「我方打算外推的东西」与「对方已注册的判据面」做覆盖度比对，
命中即判 OBSOLETE 并 exit 1（拦外推），取不到真相源一律 UNVERIFIED + exit 2（禁止把「没看到」当结论）。

只读：不写任何仓；判据来源 = 焚诀 `eval/verify_truth_consistency.py` 的注册面（C 号 + 标题）。
结论口径 = 单条已落判据标题对转办项关键词的命中数与占比（两下限 AND，防单词巧合与低占比误判）。

⛔ 作用域边界（`D:\\global_memory\\core\\behavior_core.md` #23 用户命令绝对优先）：本件判的是
「**要不要把建议外推给归属会话**」，不是「本轮要不要干活」。禁止把它挂成每轮前置拦截、或用它
把重复指令降格为核验轮——那是 2026-09-24 被用户明令全删的「重复轮次闸门」的复活动机。

用法：
    python 05-exec/transmit_obsolescence_check.py [--json]
        [--proposals 06-benchmark/transmit_proposals.json] [--verify-src <path>]
退出码：0 无过期项（可外推）/ 1 有过期项（停止外推该件）/ 2 真相源或输入不可用
"""

import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PROPOSALS = os.path.join(HERE, "..", "06-benchmark", "transmit_proposals.json")
DEFAULT_VERIFY = r"C:\Users\37533\Desktop\workspace\焚诀\eval\verify_truth_consistency.py"

RE_LANDED = re.compile(r"\(\s*['\"](C\d+)['\"]\s*,\s*['\"]([^'\"]*)['\"]")


def read_text(path):
    try:
        return io.open(path, encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return ""


def parse_landed(verify_text):
    """从 verify 注册面提取 {C号: 判据标题}；非注册面输入返回 {}（不抛）。"""
    landed = {}
    for cid, title in RE_LANDED.findall(verify_text or ""):
        landed.setdefault(cid, title)
    return landed


def _verdict(landed, keywords, threshold, min_hits):
    """三态判定。landed/keywords 取不到 → UNVERIFIED（不得当作「没过期」或「已过期」）。

    下限参数**不设默认值**：默认值唯一在 `evaluate()` 签名上，变异测试改的就是那一处。
    """
    if not landed or not keywords:
        return "UNVERIFIED"
    matched, best = [], (0, "", 0.0)
    for cid in sorted(landed):
        hits = sum(1 for k in keywords if k in landed[cid])
        ratio = hits / float(len(keywords))
        if hits > best[0]:
            best = (hits, cid, ratio)
        if hits >= min_hits and ratio >= threshold:
            matched.append(cid)
    if matched:
        return "OBSOLETE", matched, best
    return "VALID", matched, best


def evaluate(proposals, landed, threshold: float = 0.5, min_hits: int = 2):
    """逐条独立判定（同 pid 不互相覆盖）。返回 [{pid,title,verdict,matched,why}]。"""
    rows = []
    for p in proposals:
        kws = [k for k in (p.get("keywords") or []) if k]
        got = _verdict(landed, kws, threshold, min_hits)
        if got == "UNVERIFIED":
            rows.append({"pid": p.get("pid", "?"), "title": p.get("title", ""),
                         "verdict": got, "matched": [],
                         "why": "真相源注册面为空或该件无关键词，无法判定（禁默认放行）"})
            continue
        verdict, matched, best = got
        hits, bcid, ratio = best
        why = ("已被 %s 覆盖：命中 %d/%d 词（如 %s）" % ("、".join(matched) or bcid, hits,
                                                       len(kws), "、".join(kws[:4]))) \
            if matched else ("最强候选 %s 仅命中 %d/%d 词（占比 %.2f），未达双下限 ⇒ 仍有效"
                             % (bcid or "-", hits, len(kws), ratio))
        rows.append({"pid": p.get("pid", "?"), "title": p.get("title", ""),
                     "verdict": verdict, "matched": matched, "why": why})
    return rows


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="转办件过期检测（只读，取不到真相源不放行）")
    ap.add_argument("--proposals", default=DEFAULT_PROPOSALS)
    ap.add_argument("--verify-src", default=DEFAULT_VERIFY)
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--min-hits", type=int, default=2)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    ptxt = read_text(a.proposals)
    if not ptxt:
        print("[TRANSMIT:UNKNOWN] 转办登记表不可读：%s" % a.proposals)
        return 2
    vtxt = read_text(a.verify_src)
    if not vtxt:
        print("[TRANSMIT:UNKNOWN] 真相源不可读：%s" % a.verify_src)
        return 2
    try:
        data = json.loads(ptxt)
    except ValueError as e:
        print("[TRANSMIT:UNKNOWN] 登记表 JSON 失效：%r" % e)
        return 2
    landed = parse_landed(vtxt)
    if not landed:
        print("[TRANSMIT:UNKNOWN] 未从真相源解析出任何已注册判据（判据面为空，不得判过）")
        return 2
    rows = evaluate(data.get("proposals") or [], landed, a.threshold, a.min_hits)

    stale = [r for r in rows if r["verdict"] == "OBSOLETE"]
    unver = [r for r in rows if r["verdict"] == "UNVERIFIED"]
    print("=== 转办件过期检测 (%d 条已注册判据 / %d 件待外推) ===" % (len(landed), len(rows)))
    for r in rows:
        print("  %-10s %-22s %s | %s" % (r["verdict"], r["pid"], r["title"], r["why"]))
    if stale:
        print("[TRANSMIT:STALE] %d 件已过期 ⇒ 停止外推，改为只还自己那半" % len(stale))
    else:
        print("[TRANSMIT:OK] 无过期件（可外推）")

    if a.json:
        print(json.dumps({"schema": "zijian-transmit-verdict-v1",
                          "landed_count": len(landed), "results": rows}, ensure_ascii=False))
    if unver:
        return 2
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
