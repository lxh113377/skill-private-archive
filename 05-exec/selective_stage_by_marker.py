# -*- coding: utf-8 -*-
"""selective_stage_by_marker.py - 按「归属标记」做 hunk 级选择性暂存（防跨会话夹带）。

背景：本仓 2026-09-24 已登记 6 种夹带形态，根因都是「整文件 add」。多会话同改一个
memory 文件时，`git add <file>` 会把他人在途行并入我的提交，双方工作区同时变"干净"，
归属判断失真。本工具把粒度降到 hunk：任一新增行命中 foreign marker 即整块不暂存。

只读工作区 + 写 index（--apply 才暂存）；默认 dry-run 打印决策，不改任何东西。
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@", re.M)


def sh(args):
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", shell=False)
    return p.stdout, (p.stderr or "").strip(), p.returncode


def split_hunks(diff_text):
    """Return (header_lines, [ (hunk_text, added_lines) ])."""
    lines = diff_text.split("\n")
    header, hunks, cur = [], [], None
    for ln in lines:
        if HUNK.match(ln):
            if cur:
                hunks.append(cur)
            cur = [ln]
        elif cur is not None:
            cur.append(ln)
        else:
            header.append(ln)
    if cur:
        hunks.append(cur)
    out = []
    for h in hunks:
        body = "\n".join(h)
        added = [l[1:] for l in h if l.startswith("+") and not l.startswith("+++")]
        out.append((body, added))
    return header, out


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--file", action="append", required=True, help="可重复")
    ap.add_argument("--foreign", action="append", required=True,
                    help="他人在途标记（命中该 hunk 的新增行则不暂存），可重复")
    ap.add_argument("--mine", action="append", default=[],
                    help="本次归属标记；给出后，未命中任一 mine 标记的 hunk 一律让路"
                         "（防「无他人标记」被误当成「属于我」）")
    ap.add_argument("--apply", action="store_true", help="真暂存（默认 dry-run）")
    ap.add_argument("--unified", type=int, default=3,
                    help="diff 上下文行数；多人改在同一段时降到 0 才能把归属拆开")
    args = ap.parse_args()

    tmp = Path(".git/_selective_stage.patch") if (Path(args.repo) / ".git").is_dir() else None
    total_kept = total_skipped = 0
    for f in args.file:
        diff, derr, rc = sh(["git", "-C", args.repo, "diff",
                             "--unified=%d" % args.unified, "--", f])
        if rc != 0 or not diff.strip():
            print("SKIP %s：无未暂存差异或 diff 失败(rc=%d %s)" % (f, rc, derr[:120]))
            continue
        header, hunks = split_hunks(diff)
        keep, drop = [], []
        for body, added in hunks:
            blob = "\n".join(added)
            hit = [m for m in args.foreign if m in blob]
            owned = (not args.mine) or any(m in blob for m in args.mine)
            why = ("命中标记 " + ", ".join(hit)) if hit else (
                "" if owned else "未命中本次归属标记：宁可让路，不可夹带")
            (drop if (hit or not owned) else keep).append((body, why))
        print("== %s: hunk 共 %d，本次暂存 %d，让路 %d" % (
            f, len(hunks), len(keep), len(drop)))
        for i, (body, why) in enumerate(drop, 1):
            print("   drop#%d %s" % (i, why))
        total_kept += len(keep)
        total_skipped += len(drop)
        if keep and args.apply:
            if tmp is None:
                print("FAIL: 找不到 .git 目录，无法写临时补丁")
                return 2
            # 每个文件单独成补丁：多文件共用一份 header 会让 git apply 直接拒收
            patch = "\n".join(header) + "\n" + "\n".join(b for b, _ in keep) + "\n"
            tmp.parent.mkdir(exist_ok=True)
            tmp.write_text(patch, encoding="utf-8", newline="\n")
            _, aerr, rc2 = sh(["git", "-C", args.repo, "apply", "--cached", "--recount",
                               "--allow-empty", str(tmp)])
            tmp.unlink(missing_ok=True)
            if rc2 != 0:
                print("FAIL: git apply --cached 退出码 %d：%s（不降级为整文件 add）"
                      % (rc2, aerr.splitlines()[0] if aerr else "无 stderr"))
                return 2
            print("   staged OK (%d hunks)" % len(keep))
    print("\n合计：暂存 %d hunk / 让路 %d hunk（让路者留在工作区，由归属会话自行收口）" % (
        total_kept, total_skipped))
    if not args.apply:
        print("（dry-run：未改动 index；加 --apply 生效）")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as exc:
        sys.stderr.write("UNEXPECTED_FAILURE: %r -> 退出码 2\n" % (exc,))
        raise SystemExit(2)
