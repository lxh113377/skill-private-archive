#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""R272 第四类校验（主卷内嵌 commit 号漂移）—— **边界值测量 + 判据候选评估**（只读）。

R236 补注③：任何被当作判据的阈值/模式，标定前必须先实测两类样本的边界值：
  · 应通过样本 —— 「当时为真」的历史记录（如 `commit f8bc12f` 写在已完成条目里）
  · 应拒绝样本 —— 「声称当前」却已陈旧的自指值（门店实证：主卷写 HEAD=ca0b431 而实测 4f2e050）
若两者区间重叠 ⇒ 该参数不可作判据 ⇒ 改机制，禁调参。

本脚本评估三个候选判据，输出 2×2 混淆矩阵与边界数值：
  判据 A：token 是否 == 本项目 git HEAD           （直觉解）
  判据 B：P0（`- [ ]`）未完成项内出现 `HEAD = <hash>` 硬编码形态（时序/时态解，与值解耦）
  判据 C：token 是否命中「任一真实仓库 HEAD 全集」 （放宽解，测误报率）
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

PROJECTS = [
    r"c:\Users\37533\Desktop\workspace\自建skill优化",
    r"C:\Users\37533\Desktop\workspace\项目\门店 AI 管理智能体\iCAN大学生创新创业大赛",
    r"C:\Users\37533\Desktop\workspace\项目\陪聊",
    r"C:\Users\37533\Desktop\workspace\项目\医",
    r"C:\Users\37533\Desktop\workspace\超市web\超市",
    r"C:\Users\37533\Desktop\workspace\超市web\supermarket-web",
    r"C:\Users\37533\Desktop\workspace\ai漫剧\小说[六道]\ai改写",
    r"c:\Users\37533\Desktop\workspace\焚诀",
]

# 真实仓库（用于判据 C 的「任一仓库 HEAD 全集」；只读 git rev-parse）
KNOWN_REPOS = [
    r"D:\global_skills",
    r"D:\global_memory",
    r"C:\Users\37533\Desktop\workspace\焚诀",
    r"C:\Users\37533\.agents\skills",
]

HASH_RE = re.compile(r"(?<![0-9a-zA-Z])([0-9a-f]{7,40})(?![0-9a-zA-Z])")
# 「自指 + 声称当前」时序/时态词（判据 B 的核心）
CURRENT_MARK = ("HEAD", "当前提交", "当前版本", "实况", "当场")
# ⚠️ 2026-09-22 自纠：首版 PAST_MARK 含 "20"，会匹配一切 `2026`/`20 文件` ⇒ 过度过滤「声称当前」
#    样本（R263：判据自身会错，报不一致先证判据）。改为显式日期正则 + 精确历史词。
PAST_MARK = ("已完成", "✅", "校正注", "历史", "当时", "落盘 R", "→ ", "升级", "改为", "修复", "并入", "分批", "第 ", "轮）")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
# 判据 B：硬编码当前 HEAD 的形态（`HEAD = <hash>` / `HEAD 为 <hash>` / `HEAD：<hash>`）
HEADCODE_RE = re.compile(r"HEAD\s*[=：:为是]\s*`?[0-9a-f]{7,40}`?")
# 判据 D（改机制候选，**规范性检查，与「值是否陈旧」解耦**）：
#   P0（`- [ ]`）行内出现裸 hash 字面量，且同行**未附当场取值命令** ⇒ 提示补命令
LIVECMD_MARK = ("rev-parse", "当场实测", "实测为准", "git log", "git rev-parse")
P0_HASH_RE = re.compile(r"^\s*-\s*\[ \]")


def git_head(repo):
    try:
        r = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                           capture_output=True, text=True, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def mem_files(proj):
    mem = os.path.join(proj, "memory")
    if not os.path.isdir(mem):
        return []
    return [os.path.join(mem, fn) for fn in sorted(os.listdir(mem))
            if fn.endswith(".md") and fn.startswith(("07-next-steps", "05-feature-status"))]


def main():
    proj_heads = {p: git_head(p) for p in PROJECTS}
    known = {r: git_head(r) for r in KNOWN_REPOS}
    known_heads = {h for h in known.values() if h}
    known_shorts = {h[:7] for h in known_heads}

    # 混淆矩阵：判据 → [TP(应拒且报), FN(应拒未报), FP(应通过却报), TN(应通过未报)]
    M = {k: dict(TP=0, FN=0, FP=0, TN=0) for k in ("A", "B", "C", "D")}
    detail = {k: [] for k in ("A", "B", "C", "D")}
    total_lines_with_hash = 0
    REJ = []

    for proj in PROJECTS:
        head = proj_heads[proj]
        for f in mem_files(proj):
            try:
                lines = open(f, encoding="utf-8", errors="ignore").read().splitlines()
            except Exception:
                continue
            for i, ln in enumerate(lines, 1):
                toks = [m.group(1) for m in HASH_RE.finditer(ln)]
                if not toks:
                    continue
                total_lines_with_hash += 1
                is_p0 = bool(re.match(r"^\s*-\s*\[ \]", ln))
                # 真值标注（人工可复核的自动近似口径）：
                #   应拒绝 = 「P0 未完成项」且行内含自指时序词 且 无历史标记
                #   应通过 = 其余（历史记录 / 已完成条目 / 无自指时序词）
                claims_current = (any(k in ln for k in CURRENT_MARK)
                                  and not DATE_RE.search(ln)
                                  and not any(k in ln for k in PAST_MARK))
                should_reject = is_p0 and claims_current
                label = "应拒绝" if should_reject else "应通过"

                for tok in toks:
                    if should_reject:
                        REJ.append(f"{os.path.basename(proj)}/{os.path.basename(f)}:{i} `{tok}` :: {ln.strip()[:120]}")
                    # 判据 A：等于本项目 HEAD（短/全长）
                    hitA = bool(head) and (head.startswith(tok) or tok.startswith(head[:7]))
                    # 判据 B：P0 内出现 `HEAD = <hash>` 硬编码形态
                    hitB = bool(re.search(r"^\s*-\s*\[ \]", ln)) and bool(HEADCODE_RE.search(ln))
                    # 判据 C：命中任一真实仓库 HEAD（短号）
                    hitC = tok[:7] in known_shorts
                    # 判据 D：P0 内裸 hash 且未附当场取值命令（规范性，与值解耦）
                    hitD = bool(P0_HASH_RE.match(ln)) and not any(k in ln for k in LIVECMD_MARK)
                    for k, hit in (("A", hitA), ("B", hitB), ("C", hitC), ("D", hitD)):
                        key = ("TP" if hit else "FN") if should_reject else ("FP" if hit else "TN")
                        M[k][key] += 1
                        if hit:
                            detail[k].append(
                                f"[{label}] {os.path.basename(proj)}/{os.path.basename(f)}:{i} `{tok}` "
                                f":: {ln.strip()[:110]}")

    print("=" * 82)
    print("R272 第四类校验 · 边界值测量（8 真实项目，只读）")
    print("=" * 82)
    print(f"含 hash 的行总数: {total_lines_with_hash}")
    print(f"已知仓库 HEAD 短号集: {sorted(known_shorts)}")
    print()
    print(f"{'判据':<6}{'TP(应拒且报)':>14}{'FN(漏报)':>12}{'FP(误报)':>12}{'TN(应通过未报)':>16}")
    for k in ("A", "B", "C", "D"):
        m = M[k]
        print(f"{k:<6}{m['TP']:>14}{m['FN']:>12}{m['FP']:>12}{m['TN']:>16}")
    print()
    for k in ("A", "B", "C", "D"):
        if detail[k]:
            print(f"--- 判据 {k} 的命中明细（前 6 条）---")
            for d in detail[k][:6]:
                print("   " + d)
    print()
    print(f"--- 「应拒绝」样本全集（{len(REJ)} 条，人工可复核）---")
    for d in REJ:
        print("   " + d)
    print()
    print("=== 判定结论 ===")
    for k, name in (("A", "token == 本项目 HEAD"), ("B", "P0 内 HEAD 硬编码形态"),
                    ("C", "命中任一仓库 HEAD"), ("D", "P0 内裸 hash 且未附当场取值命令（规范性）")):
        m = M[k]
        ok = m["FP"] == 0 and m["TP"] > 0
        print(f"判据 {k}（{name}）: TP={m['TP']} FP={m['FP']} ⇒ "
              f"{'可作判据（零误报且有拦截力）' if ok else '不可作判据（区间重叠 / 无拦截力 / 有误报）'}")

    with open(os.path.join(ROOT, "R272b-boundary.json"), "w", encoding="utf-8") as f:
        json.dump({"matrix": M, "detail": detail, "heads": known}, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
