#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""需求7覆盖矩阵自检：检查 7 项需求在四类文档+README 中均有章节落点，且四份汇总文档存在。
为什么：t7 完成判据要求覆盖 7/7 无遗漏；机器判据必须可复跑且有负控，避免人工宣称完整。
怎么运作：逐文档读取 UTF-8 文本，按 REQ_MARKERS 的锚点计数；任一需求 0 命中即差异。
--negative-control 在内存中删去一个必需锚点并断言判据报红，不写回源文件。
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ["问题分析报告.md", "对比评估表.md", "迁移执行计划.md", "后续维护规范文档.md", "README.md"]
REQ_MARKERS = {
    "REQ1": ["全量盘点", "150", "HIGH51"],
    "REQ2": ["3-5", "377", "77/77"],
    "REQ3": ["五维", "2365", "score5"],
    "REQ4": ["阶段门", "G0", "P0=5"],
    "REQ5": ["季度巡检", "cadence", "r113"],
    "REQ6": ["30%", "如实证否", "QUALITY:IMPOSSIBLE"],
    "REQ7": ["覆盖矩阵", "7/7", "README"],
}

def read_docs():
    texts = {}
    for name in DOCS:
        p = ROOT / name
        if not p.is_file():
            raise FileNotFoundError(str(p))
        texts[name] = p.read_text(encoding="utf-8")
    return texts

def evaluate(texts):
    all_text = "\n".join(texts.values())
    rows = []
    diffs = 0
    for req, markers in REQ_MARKERS.items():
        hits = [m for m in markers if m in all_text]
        ok = len(hits) == len(markers)
        if not ok:
            diffs += 1
        rows.append({"req": req, "markers": markers, "hits": hits, "status": "PASS" if ok else "FAIL"})
    for name in DOCS:
        if len(texts.get(name, "").strip()) < 200:
            diffs += 1
            rows.append({"req": "DOC:" + name, "status": "FAIL", "problem": "empty_or_too_short"})
    return diffs, rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--negative-control", action="store_true")
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    texts = read_docs()
    if a.negative_control:
        poisoned = dict(texts)
        # 负控：从所有汇总文档中抹除 REQ1 锚点，模拟删除源数据/章节后判据必须报红。
        for name in poisoned:
            for m in REQ_MARKERS["REQ1"]:
                poisoned[name] = poisoned[name].replace(m, "POISON")
        ndiff, _ = evaluate(poisoned)
        if ndiff == 0:
            print("[NEGCTRL:GREEN] 删除汇总源数据锚点后判据仍绿（不合格）")
            return 2
        print("[NEGCTRL:RED] 删除汇总源数据锚点后覆盖判据报红（符合预期） diffs=%d" % ndiff)
        return 0
    diffs, rows = evaluate(texts)
    payload = {"schema": "t7-coverage-v1", "negative_control": False, "diffs": diffs, "rows": rows}
    if a.json:
        Path(a.json).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    for r in rows:
        n = len(REQ_MARKERS.get(r["req"], []))
        print("[COVERAGE:ROW] %s %s hits=%d/%d" % (r["req"], r["status"], len(r.get("hits", [])), n))
    if diffs:
        print("[COVERAGE:FAIL] 需求覆盖=%d/7 差异=%d" % (7 - diffs, diffs))
        return 1
    print("[COVERAGE:PASS] 需求覆盖=7/7 差异=0")
    return 0

if __name__ == "__main__":
    sys.exit(main())
