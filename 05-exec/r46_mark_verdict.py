# -*- coding: utf-8 -*-
r"""r46_mark_verdict.py — 给共享记忆卷写「裁决/状态标记」的唯一入口（X-19 工具化）。

为什么要有它（r45 D62 实测，不是猜测）：
`W-9` 挂了 5 轮，逐条取证后发现目标行的**裁决标记数 = 0** —— 我前三轮都是按**行号索引**
（`lines[n-1] += mark`）往 `07-next-steps.md` 补标记，而该卷会因 savepoint 拆卷与并行会话
整卷重写而**行号漂移** ⇒ 标记全写到别的行，看起来"裁过了"，账面下一轮照样红。
W-13 已经提供 `find_item_line()`，但**约定拦不住我写一次性脚本时图省事**（同一轮又犯一次），
所以本轮把它做成唯一入口：不接收行号，只接收标题锚点，且命中数 != 1 一律拒写。

五重拒写（每条都有夹具断言，见 r46_mark_verdict_fixtures.py）：
  ① 不提供行号入口（argparse 无 --line，传了就报错退出）；
  ② 锚点命中数 != 1（含 0 命中 = 条目不存在，**绝不退化成追加**）；
  ③ 命中的是 `- [x]` 已闭环条目 ⇒ 禁往别人做完的条目上标裁决；
  ④ 同一轮已有 `rNN 裁决=` ⇒ 拒写（幂等靠**拒绝**实现，不靠静默跳过，#23 同族）；
  ⑤ 目标卷不在 `<vault>/memory/` 下 ⇒ 拒写（受管根与仓外一律不许经此工具写）。
写入后必须 grep 读回验证，读不到就 restore 备份并返回失败（X-8：报 done 之前必须读回）。

退出码：0 = 已写入并读回验证；1 = 被拒写或读回失败；2 = 参数不合法
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MARK_RE_TPL = "r%s 裁决="


def find_item_lines(lines, key):
    """返回 (未勾选命中, 已勾选命中) 两组 1-based 行号 —— 只认 markdown 任务行。"""
    open_hits, closed_hits = [], []
    for i, l in enumerate(lines):
        if key not in l:
            continue
        st = l.lstrip()
        if st.startswith("- [ ]"):
            open_hits.append(i + 1)
        elif st.startswith("- [x]") or st.startswith("- [X]"):
            closed_hits.append(i + 1)
    return open_hits, closed_hits


def refuse(why, detail=""):
    print("[MARK:REFUSED] %s%s" % (why, (" ｜ " + detail) if detail else ""))
    return 1


def main():
    ap = argparse.ArgumentParser(
        prog="r46_mark_verdict.py",
        description="按标题锚点给记忆卷写裁决标记（唯一入口，禁行号）")
    ap.add_argument("--vault", default=str(ROOT), help="项目根（其下 memory/ 才允许写）")
    ap.add_argument("--file", help="指定卷路径（必须位于 <vault>/memory/ 下）")
    ap.add_argument("--key", required=True, help="条目标题锚点（子串，须在未勾选项中唯一命中）")
    ap.add_argument("--round", required=True, help="本轮轮号，如 46")
    ap.add_argument("--verdict", required=True, help="裁决文本，如「降级（转长期看守）｜原因」")
    ap.add_argument("--glob", default="07-next-steps*.md", help="在哪些卷里找锚点（默认 07 全卷）")
    ap.add_argument("--backup-dir", default=None,
                    help="备份目录（默认 <vault>/05-exec/mark_backup；刻意不放记忆卷，见 r35 落点教训）")
    args = ap.parse_args()

    vault = Path(args.vault).resolve()
    mem = vault / "memory"
    if not mem.is_dir():
        return refuse("目标根无 memory/ 目录", str(mem))

    cands = [Path(args.file).resolve()] if args.file else sorted(mem.glob(args.glob))
    if not args.file:
        cands = [p for p in cands if p.parent == mem]      # 只扫 memory/ 直属卷，不碰别人写的目录
    for p in cands:
        try:
            rp = p.resolve()
        except OSError:
            return refuse("路径不可解析", str(p))
        if rp.parent != mem:
            return refuse("⑤ 只允许写 <vault>/memory/ 下的卷（受管根与仓外一律拒写）", str(rp))
        raw = io.open(rp, encoding="utf-8", newline="").read()
        eol = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.split(eol)
        open_hits, closed_hits = find_item_lines(lines, args.key)
        if len(open_hits) + len(closed_hits) == 0:
            continue                                        # 本卷无此锚点，去下一卷找
        if closed_hits and not open_hits:
            return refuse("③ 锚点只命中已闭环条目，禁往 - [x] 上标裁决",
                          "行 %s in %s" % (closed_hits, rp.name))
        if len(open_hits) != 1:
            return refuse("② 锚点命中数 != 1（重复登记或跨卷歧义）",
                          "命中 %s 行 in %s" % (open_hits, rp.name))
        i = open_hits[0] - 1
        if MARK_RE_TPL % args.round in lines[i]:
            return refuse("④ 本轮已裁过，不重复写（幂等靠拒绝而非静默跳过）",
                          "%s:%d" % (rp.name, i + 1))
        marker = "【" + (MARK_RE_TPL % args.round) + args.verdict + "】"
        new_lines = list(lines)
        new_lines[i] = lines[i].rstrip() + " " + marker
        bdir = Path(args.backup_dir).resolve() if args.backup_dir else (vault / "05-exec" / "mark_backup")
        # r46：备份默认落 05-exec/mark_backup，不落记忆卷（同 r35 的 rule_backup 落点教训）
        bdir.mkdir(parents=True, exist_ok=True)
        bak = bdir / ("%s.r%s_%s.bak" % (rp.name, args.round, time.strftime("%H%M%S")))
        io.open(bak, "w", encoding="utf-8", newline="").write(raw)
        io.open(rp, "w", encoding="utf-8", newline="").write(eol.join(new_lines))
        back = io.open(rp, encoding="utf-8", newline="").read()
        if marker not in back:                              # X-8：读不到就不算写完
            io.open(rp, "w", encoding="utf-8", newline="").write(raw)
            return refuse("读回验证失败，已回滚（禁在只 return 不写盘的情况下报 done）",
                          "%s:%d" % (rp.name, i + 1))
        print("[MARK:OK] %s:%d ｜ 备份 %s ｜ 读回验证通过" % (rp.name, i + 1, bak.name))
        return 0
    return refuse("② 锚点在全部候选卷里 0 命中（不得退化成追加到文件末尾）", args.key)


if __name__ == "__main__":
    sys.exit(main())
