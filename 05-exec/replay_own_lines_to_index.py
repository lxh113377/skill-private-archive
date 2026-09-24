# -*- coding: utf-8 -*-
"""replay_own_lines_to_index.py - 只把「我新增的行」重放进 git index，工作区零改动。

为什么需要：多会话同改一个 memory 文件时，`git add <file>` 会把他人在途行并入我的提交
（本仓已登记 6 种夹带形态，根因都是整文件暂存）；`git apply --cached` 在本仓（工作副本 CRLF /
仓内 blob LF）反复 preimage 失配。本工具不做文本匹配猜测，只做一件保守的事：
  工作区里有、index 里没有的行 = 本次新增 ⇒ 按「其后第一条已存在于 index 的行」定位插入。
因此他人在途行若同样"index 里没有"，也会被我插进 index —— 所以必须配 --only 前缀白名单，
未列入白名单的新增行一律不插（宁可漏，不可夹带）。

用法：
  python 05-exec/replay_own_lines_to_index.py --file memory/07-next-steps.md \
      --only "- **2026-09-25（第 30 轮 r30" --only "- [ ] **【P0·待办 H4" --dry-run
"""

import argparse
import subprocess
import sys
from pathlib import Path


def sh(args, cwd, data=None):
    p = subprocess.run(args, cwd=cwd, capture_output=True, input=data, shell=False)
    return p.stdout, (p.stderr or b"").decode("utf-8", "replace").strip(), p.returncode


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--file", required=True)
    ap.add_argument("--only", action="append", required=True,
                    help="本次归属前缀白名单（可重复）；未命中的新增行一律不插")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划（默认行为）")
    args = ap.parse_args()

    repo = str(Path(args.repo).resolve())
    out, err, rc = sh(["git", "cat-file", "blob", ":" + args.file], repo)
    if rc != 0:
        print("FAIL: 读不到 index 版本（%s）" % err[:160])
        return 2
    wt = (Path(repo) / args.file).read_bytes()
    eol = b"\r\n" if b"\r\n" in out else b"\n"
    idx, work = out.split(eol), wt.split(eol if eol in wt else b"\n")
    if eol == b"\n" and b"\r\n" in wt:
        work = [l[:-1] if l.endswith(b"\r") else l for l in work]

    idx_lookup = {}
    for i, l in enumerate(idx):
        idx_lookup.setdefault(l, []).append(i)

    owned, unowned = [], []
    for i, l in enumerate(work):
        if l in idx_lookup:
            continue
        txt = l.decode("utf-8", "replace")
        (owned if any(txt.startswith(p) for p in args.only) else unowned).append((i, l))
    print("工作区新增行：归属我 %d 条 / 非白名单（不插）%d 条" % (len(owned), len(unowned)))
    for i, l in unowned[:8]:
        print("   跳过: %s" % l.decode("utf-8", "replace")[:60])

    new_idx = list(idx)
    plan = []
    cursor = 0
    for i, l in owned:
        anchor = None
        for j in range(i + 1, len(work)):
            if work[j] in idx_lookup:
                anchor = work[j]
                break
        if anchor is None:
            print("   无法定位（文件尾部新增）: %s" % l.decode("utf-8", "replace")[:60])
            pos = len(new_idx) - 1
        else:
            # 锚点可能是空行这类全文重复行：只能取"不早于上一条"的首次出现，否则会被插到文件头
            cands = [k for k in idx_lookup[anchor] if k >= cursor]
            if not cands:
                print("   锚点无可用位置，追加到尾部: %s" % l.decode("utf-8", "replace")[:50])
                pos = len(new_idx) - 1
            else:
                pos = cands[0]
        cursor = pos
        plan.append((pos, l))
    for pos, l in sorted(plan, key=lambda x: -x[0]):
        new_idx[pos:pos] = [l]
        print("   插入 @%d: %s" % (pos + 1, l.decode("utf-8", "replace")[:58]))

    if not owned:
        print("无我归属的新增行，index 不动")
        return 0
    if not args.apply:
        print("（dry-run：未改 index；加 --apply 生效）")
        return 0
    blob = eol.join(new_idx)
    sha, err2, rc2 = sh(["git", "hash-object", "-w", "--stdin"], repo, data=blob)
    if rc2 != 0:
        print("FAIL: hash-object %s" % err2[:160])
        return 2
    sha = sha.decode().strip().splitlines()[0]
    _, err3, rc3 = sh(["git", "update-index", "--add", "--cacheinfo", "100644", sha, args.file], repo)
    if rc3 != 0:
        print("FAIL: update-index %s" % err3[:160])
        return 2
    print("staged %s -> %s（新增 %d 行，删除 0 行）" % (args.file, sha[:7], len(owned)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as exc:
        sys.stderr.write("UNEXPECTED_FAILURE: %r -> 退出码 2\n" % (exc,))
        raise SystemExit(2)
