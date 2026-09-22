#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""R272 第四类校验（主卷内嵌数字/版本漂移）—— **边界值取样**（只读，不改任何文件）。

方法（R236 补注③）：参数标定前先测两侧边界值 ——
  1) 在 ≥3 个真实项目的 07/05 主卷+分卷里抽「数字/版本类」候选行；
  2) 按**上下文**分类：自指本项目 / 外部仓库或 skill / 噪音（日期、编号、路径、尺寸）；
  3) 对「自指」类实测 token 与实况是否一致 → 得出应拒绝样本与应通过样本的分布；
  4) 若两侧区间重叠 ⇒ 该判据不可用，须改机制（不得调参硬凑）。
"""
import json
import os
import re
import subprocess
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
]

SHA_RE = re.compile(r"(?<![0-9a-zA-Z])[0-9a-f]{7,40}(?![0-9a-zA-Z])")
VER_RE = re.compile(r"\bV?\d+\.\d+(?:\.\d+)?\b")
KEY_SHA = ("commit", "HEAD", "SHA", "落盘", "提交", "基线", "推送")
KEY_VER = ("版本", "version", "frontmatter", "V10.", "V9.", "V4.", "V3.", "V2.", "V1.")

# 外部仓库 / 外部体系的限定词（出现 ⇒ 不是「本项目自指」）
EXT_MARK = ("受管根", "焚诀", "global_skills", "global_memory", "工作区", "supermarket-web",
            "github", "origin", "远端", "镜像", "GM ", "A-memory-start", "A-project-handoff",
            "A-skill-manager", "A-get-memory", "A-project-better", "A-ask-questions")
# 噪音：日期 / AC 编号 / 尺寸 / 路径段
NOISE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$|^AC-OBS|^\d+$|^\d+(\.\d+)?(KB|MB|B)$|^part\d+$")


def find_vol_files(proj):
    mem = os.path.join(proj, "memory")
    if not os.path.isdir(mem):
        return []
    out = []
    for fn in sorted(os.listdir(mem)):
        if not fn.endswith(".md"):
            continue
        if fn.startswith(("07-next-steps", "05-feature-status")):
            out.append(os.path.join(mem, fn))
    return out


def git_head(proj):
    try:
        r = subprocess.run(["git", "-C", proj, "rev-parse", "HEAD"],
                           capture_output=True, text=True, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def main():
    report = []
    for proj in PROJECTS:
        files = find_vol_files(proj)
        head = git_head(proj)
        n_sha = n_ver = 0
        samples = []
        for f in files:
            try:
                with open(f, encoding="utf-8", errors="ignore") as fh:
                    lines = fh.read().splitlines()
            except Exception:
                continue
            for i, ln in enumerate(lines, 1):
                has_kw_sha = any(k in ln for k in KEY_SHA)
                if has_kw_sha:
                    for m in SHA_RE.finditer(ln):
                        tok = m.group(0)
                        if NOISE_RE.match(tok):
                            continue
                        n_sha += 1
                        if len(samples) < 12:
                            samples.append(("SHA", os.path.basename(f), i, tok, ln.strip()[:110]))
                has_kw_ver = any(k in ln for k in KEY_VER)
                if has_kw_ver:
                    for m in VER_RE.finditer(ln):
                        tok = m.group(0)
                        if NOISE_RE.match(tok):
                            continue
                        n_ver += 1
                        if len(samples) < 12:
                            samples.append(("VER", os.path.basename(f), i, tok, ln.strip()[:110]))
        ext = sum(1 for _, _, _, _, ctx in samples if any(e in ctx for e in EXT_MARK))
        report.append({
            "project": proj,
            "files": [os.path.basename(f) for f in files],
            "head": head,
            "sha_candidates": n_sha,
            "ver_candidates": n_ver,
            "sample_ext_hits": ext,
            "samples": samples,
        })

    print("=" * 78)
    print("R272 第四类校验 · 边界值取样（只读）")
    print("=" * 78)
    for r in report:
        print(f"\n### {r['project']}")
        print(f"    文件: {', '.join(r['files']) or '（无 07/05）'}")
        print(f"    git HEAD: {r['head'] or '（非 git 仓或无提交）'}")
        print(f"    候选数: SHA 上下文行 {r['sha_candidates']} / VER 上下文行 {r['ver_candidates']}")
        for kind, fn, i, tok, ctx in r["samples"]:
            tag = "外部" if any(e in ctx for e in EXT_MARK) else "自指?"
            print(f"      [{kind}|{tag}] {fn}:{i} `{tok}`")
            print(f"            …{ctx}")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "R272b-survey.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(f"\n[saved] {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
