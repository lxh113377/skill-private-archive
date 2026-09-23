#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""R272 第四类校验（收窄版）—— **只查主卷 07-next-steps.md 的 P0 段** 边界值重测（只读）。

用户口径（2026-09-22）：做提示级，但先重测；**0 误报才做，有误报就回报不做**。

收窄后判据定义：
  作用域 = `<project>/memory/07-next-steps.md`（**仅主卷**，不扫 partN 历史分卷）
  目标行 = P0 未完成项（`- [ ]`）
  命中条件 = 行内出现「像 commit 号的裸 hash」且**同行未附当场取值命令**

评估两个变体（为看清「加不加当前值语境」对误报的影响）：
  变体 1（宽）：P0 行 + 裸 hash + 无取值命令
  变体 2（窄）：变体 1 且同行含「当前值语境词」（HEAD / 当前 / commit / 提交 / 基线）

输出每一处命中**原文**，供人工逐条判 TP / FP（脚本不代替判断）。
"""
import os
import re
import sys

PROJECTS = [
    r"c:\Users\37533\Desktop\workspace\自建skill优化",
    r"C:\Users\37533\Desktop\workspace\项目\门店 AI 管理智能体\iCAN大学生创新创业大赛",
    r"C:\Users\37533\Desktop\workspace\项目\陪聊",
    r"C:\Users\37533\Desktop\workspace\项目\医",
    r"C:\Users\37533\Desktop\workspace\超市web\超市",
    r"C:\Users\37533\Desktop\workspace\超市web\supermarket-web",
    r"C:\Users\37533\Desktop\workspace\ai漫剧\小说[六道]\ai改写",
    r"c:\Users\37533\Desktop\workspace\焚诀",
    r"D:\global_memory",
]

HASH_RE = re.compile(r"(?<![0-9a-zA-Z])([0-9a-f]{7,40})(?![0-9a-zA-Z])")
P0_RE = re.compile(r"^\s*-\s*\[ \]")
# 当场取值命令标记（同行出现即放行）
LIVECMD = ("rev-parse", "当场实测", "实测为准", "git log", "git show", "git describe")
# 当前值语境词（变体 2 要求）
CURRENT_CTX = ("HEAD", "当前", "commit", "提交", "基线", "SHA")


def main():
    wide, narrow = [], []
    scanned = 0
    for proj in PROJECTS:
        f = os.path.join(proj, "memory", "07-next-steps.md")
        if not os.path.isfile(f):
            continue
        scanned += 1
        try:
            lines = open(f, encoding="utf-8", errors="ignore").read().splitlines()
        except Exception:
            continue
        for i, ln in enumerate(lines, 1):
            if not P0_RE.match(ln):
                continue
            toks = [m.group(1) for m in HASH_RE.finditer(ln)]
            if not toks:
                continue
            if any(k in ln for k in LIVECMD):
                continue
            rec = (proj, i, toks, ln.strip())
            wide.append(rec)
            if any(k in ln for k in CURRENT_CTX):
                narrow.append(rec)

    print("=" * 84)
    print("R272 第四类校验（收窄版）· 主卷 07-next-steps.md P0 段 · 边界值重测")
    print("=" * 84)
    print(f"扫描主卷数: {scanned} / {len(PROJECTS)} 个候选项目")
    print()
    for tag, hits in (("变体 1（宽：P0 + 裸 hash + 无取值命令）", wide),
                      ("变体 2（窄：变体1 且含当前值语境词）", narrow)):
        print(f"--- {tag}：命中 {len(hits)} 处 ---")
        for proj, i, toks, ln in hits:
            print(f"  [需人工判 TP/FP] {os.path.basename(proj)}/07-next-steps.md:{i} {toks}")
            print(f"        {ln[:150]}")
        if not hits:
            print("  （0 命中）")
        print()
    print("=== 说明 ===")
    print("· 上轮「3 例误报」里，门店 part17（CloudBase 环境 ID）与 医/超市 的样本，本脚本已按收窄口径重新取样")
    print("· 本脚本只摊证据，不做 TP/FP 判定 —— 判定由外层逐条人工核验后给出")
    return 0


if __name__ == "__main__":
    sys.exit(main())
