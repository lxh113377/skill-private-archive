# -*- coding: utf-8 -*-
"""r29b_stage_07_line.py — 一次性：只把「我改的那一行」写进 index，工作区零改动。

为什么不用 git apply / git add：
  * `git add memory/07-next-steps.md` 会把并行会话在同一文件里的 4 行在途内容一起吞进
    我的提交 —— 本仓已登记 6 种夹带形态，根因都是整文件暂存。
  * hunk 级 `git apply --cached` 在本仓（CRLF 工作副本 + LF 仓内 blob）反复 preimage 失配。
做法：取 index 原始字节 → 按原行尾只替换我那一行 → hash-object → update-index。
行尾必须逐字节保持：第一版用文本模式读，行尾被规范化成 LF，结果整文件 100+ 行"变更"。
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(r"C:\Users\37533\Desktop\workspace\自建skill优化")
PATH = "memory/07-next-steps.md"
OLD_PREFIX = "- [ ] **【P0·待窗口 H1/H3】**"
NEW_PREFIX = "- [x] **【H1/H3 已闭环"


def sh(args, data=None):
    p = subprocess.run(args, cwd=str(REPO), capture_output=True, input=data, shell=False)
    if p.returncode != 0:
        sys.stderr.write("FAIL %s -> rc=%d %s\n" % (" ".join(args[:3]), p.returncode,
                                                    (p.stderr or b"").decode("utf-8", "replace")[:200]))
        raise SystemExit(2)
    return p.stdout


idx_bytes = sh(["git", "cat-file", "blob", ":" + PATH])
work_bytes = (REPO / PATH).read_bytes()
eol = b"\r\n" if b"\r\n" in idx_bytes else b"\n"
idx = idx_bytes.split(eol)
work = work_bytes.split(eol if eol in work_bytes else b"\n")

mine = [l for l in work if l.startswith(NEW_PREFIX.encode())]
assert len(mine) == 1, "工作区里我的目标行应恰好 1 条，实得 %d" % len(mine)
tgt = [i for i, l in enumerate(idx) if l.startswith(OLD_PREFIX.encode())]
assert len(tgt) == 1, "index 里旧行应恰好 1 条，实得 %d" % len(tgt)

out = list(idx)
out[tgt[0]] = mine[0]
assert sum(1 for a, b in zip(idx, out) if a != b) == 1, "只允许一行不同"
assert b"\r\n" not in mine[0] and b"\n" not in mine[0], "替换行不得内嵌换行"
new_blob = eol.join(out)

sha = sh(["git", "hash-object", "-w", "--stdin"], data=new_blob).decode().strip().splitlines()[0]
sh(["git", "update-index", "--add", "--cacheinfo", "100644", sha, PATH])
others = sum(1 for a, b in zip(work, idx) if a != b) - 1
print("staged %s -> %s（仅第 %d 行；行尾 %s 保持；他人 %d 行留在工作区未暂存）" % (
    PATH, sha[:7], tgt[0] + 1, "CRLF" if eol == b"\r\n" else "LF", others))
