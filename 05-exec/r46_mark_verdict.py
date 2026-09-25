# -*- coding: utf-8 -*-
r"""r46_mark_verdict.py — 给共享记忆卷写「裁决/状态标记」的唯一入口（X-19 工具化）。

为什么要有它（r45 D62 实测，不是猜测）：
`W-9` 挂了 5 轮，逐条取证后发现目标行的**裁决标记数 = 0** —— 我前三轮都是按**行号索引**
（`lines[n-1] += mark`）往 `07-next-steps.md` 补标记，而该卷会因 savepoint 拆卷与并行会话
整卷重写而**行号漂移** ⇒ 标记全写到别的行，看起来"裁过了"，账面下一轮照样红。
W-13 已经提供 `find_item_line()`，但**约定拦不住我写一次性脚本时图省事**（同一轮又犯一次），
所以本轮把它做成唯一入口：不接收行号，只接收标题锚点，且命中数 != 1 一律拒写。

五重拒写 + 一重对账（每条都有夹具断言，见 r46_mark_verdict_fixtures.py / r49_face_fixtures.py）：
  ① 不提供行号入口（argparse 无 --line，传了就报错退出）；
  ② 锚点命中数 != 1（含 0 命中 = 条目不存在，**绝不退化成追加**）；
  ③ 命中的是 `- [x]` 已闭环条目 ⇒ 禁往别人做完的条目上标裁决；
  ④ 同一轮已有 `rNN 裁决=` ⇒ 拒写（幂等靠**拒绝**实现，不靠静默跳过，#23 同族）；
  ⑤ 目标卷不在 `<vault>/memory/` 下 ⇒ 拒写（受管根与仓外一律不许经此工具写）；
  ⑥ W-22（r49）延期型裁决与近期提交主题对账：条目**自身编号**已被宣布落地却还往后挂账 ⇒ 拒写
     （①~⑤ 只保证"写到唯一命中的那一行"，保证不了"那行是我要裁的那条"）。
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


# ---- W-22（r49）：锚点唯一命中 ≠ 裁决对象正确 ------------------------------------
# 动因（r46 真事故，r49 到期追讨时才发现）：我给 **W-14** 那一行写了「挂账至 r49」，
# 而原因文本讲的是「契约分代必填」（那是 W-17）；W-14 在 r45 的提交主题里已写明「落地」。
# 五重拒写拦住了"写到错行"，拦不住"把给 A 的裁决写到正确的 B 行上"——后者只能靠
# 「条目自己的编号」与「近期提交主题」对账。检测延迟 = 整个延期窗口（3 轮），必须前移到写时。
RE_ITEM_ID = re.compile(r"([A-Z]-\d+)（r\d{1,3}\s*新立")
RE_LANDED_WORD = re.compile(r"落地|已落地|执行完毕|已闭环")
RE_DEFERRAL_TEXT = re.compile(r"^\s*(?:【)?\s*挂账至\s*r\d{1,3}")   # 只看裁决文本**头部**：r49 实测「在原因里引用旧标记原文」会被全文 search 命中，把终局裁决误判成延期（同一劫持第 2 形态）


def item_own_id(line):
    """条目**自我声明**的编号 = 紧跟「（rNN 新立」的那个；正文里引用别条的编号不算自身编号。"""
    m = RE_ITEM_ID.search(line or "")
    return m.group(1) if m else None


def landed_contradiction(item_id, verdict, subjects):
    """True = 该延期与近期提交主题矛盾（条目自己已被宣布落地，却还在往后挂账）⇒ 调用方拒写。

    只在「延期型裁决」上生效：终局裁决（执行/作废/保留）指向已落地条目是**正确行为**，
    拒它就是把判据用反。取不到编号或取不到提交主题时一律不拒（禁凭空造拒写）。
    """
    if not item_id or not RE_DEFERRAL_TEXT.search(verdict or ""):
        return False
    pat = re.compile(r"\b%s\b" % re.escape(item_id))
    for subj in (subjects or "").splitlines():
        if pat.search(subj) and RE_LANDED_WORD.search(subj):
            return True
    return False


def git_subjects(vault, n=20):
    """独立取值：近期提交主题（供 landed_contradiction 对账）。取不到返回 ""（不拒写，只告警）。"""
    try:
        r = subprocess.run(["git", "-C", str(vault), "log", "--format=%s", "-%d" % n],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        return r.stdout if r.returncode == 0 else ""
    except OSError:
        return ""


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


def split_keep_eol(text):
    """按**物理行**切分并保留每行自己的行尾，返回 [(内容, 行尾)]。

    r49 根因修：原实现 `eol = "\r\n" if "\r\n" in raw else "\n"` 后整份按单一行尾切 ——
    而 `memory/07-next-steps.md` 实测是**混合行尾**（178 个 CRLF + 4 个纯 LF，并发写与
    拆卷产物），那 4 行被并进前一个元素，标记追加到"元素末尾"= 另一条目那一行。
    行号错位修好了，**元素错位**是同一缺陷的第二形态 ⇒ 必须逐行保留行尾，且只改目标行。
    """
    parts = re.split(r"(\r\n|\r|\n)", text)
    out = []
    for i in range(0, len(parts) - 1, 2):
        out.append((parts[i], parts[i + 1]))
    out.append((parts[-1], ""))
    return out


def join_keep_eol(rows):
    return "".join(c + e for c, e in rows)


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
        rows = split_keep_eol(raw)
        lines = [c for c, _ in rows]
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
        if RE_DEFERRAL_TEXT.search(args.verdict):                       # ⑥ 只对延期型裁决设卡
            subj = git_subjects(vault)
            own = item_own_id(lines[i])
            if not subj:
                print("[MARK:FACE-UNVERIFIED] 取不到近期提交主题 ⇒ 「已落地却仍挂账」对账未做，"
                      "放行但如实记录（r25：判据不得变成拦任务的闸门）")
            elif landed_contradiction(own, args.verdict, subj):
                return refuse("⑥ 条目自身编号 %s 已在近期提交主题里被宣布落地，却还往后挂账"
                              " —— 多半是把另一条的裁决写到了这条上（r46 W-14 事故同族）" % own,
                              "%s:%d ｜ 取值：git -C %s log --format=%%s -20"
                              % (rp.name, i + 1, vault))
        marker = "【" + (MARK_RE_TPL % args.round) + args.verdict + "】"
        new_rows = list(rows)
        body, tail = lines[i], rows[i][1]
        new_rows[i] = (body.rstrip() + " " + marker, tail)   # 只改目标这一行，行尾原样保留
        bdir = Path(args.backup_dir).resolve() if args.backup_dir else (vault / "05-exec" / "mark_backup")
        # r46：备份默认落 05-exec/mark_backup，不落记忆卷（同 r35 的 rule_backup 落点教训）
        bdir.mkdir(parents=True, exist_ok=True)
        bak = bdir / ("%s.r%s_%s.bak" % (rp.name, args.round, time.strftime("%H%M%S")))
        io.open(bak, "w", encoding="utf-8", newline="").write(raw)
        io.open(rp, "w", encoding="utf-8", newline="").write(join_keep_eol(new_rows))
        back_rows = [c for c, _ in split_keep_eol(io.open(rp, encoding="utf-8", newline="").read())]
        # X-8 的**实质**读回：不是"文件里有这个串"，而是"串与锚点在同一物理行"
        same_line = (i < len(back_rows) and marker in back_rows[i] and args.key in back_rows[i])
        others = [j for j, c in enumerate(back_rows) if marker in c and j != i]
        if not same_line or others:
            io.open(rp, "w", encoding="utf-8", newline="").write(raw)
            return refuse("读回验证失败，已回滚（禁在只 return 不写盘的情况下报 done）",
                          ("标记落到非锚点行 %s" % others if others else
                           "目标行未读到标记（行尾/并元素错位）"))
        print("[MARK:OK] %s:%d ｜ 备份 %s ｜ 读回验证通过（锚点与标记同行）" % (rp.name, i + 1, bak.name))
        return 0
    return refuse("② 锚点在全部候选卷里 0 命中（不得退化成追加到文件末尾）", args.key)


if __name__ == "__main__":
    sys.exit(main())
