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


# ---- r214（对标改造 H-2 / R211-2）：备份簇 keep 收敛 --------------------------------
# 一手规模（r214 本轮实测，非估算）：_trash 内 .bak 431 件 / 49,135,862B；最大单簇
# _trash/r163_mark_backup 100 份；近 3 小时新增 11 份 .bak =>「越认真裁 => 越脏」：每次
# 裁决都往回收区追加一份**全量** 07 副本（约 250KB/份），而没有任何一侧做 keep 收敛，
# 于是体量治理 L4 备份簇项与 21 天红线只涨不消（八维对标量化出来的改造点）。
# 三条设计约束（都是本仓反复判红的同族，写在这里防下轮又走捷径）：
#   ① 阈值不另立：读体量治理单一真相源 volumegov.DEFAULT_BUDGET 的 bak_keep/bak_age_days，
#      两个值必须**同源一次读齐** —— 只对齐 keep 不对齐冷却期，会出现「本件收了、体量门
#      说还在冷却」两套账（同一事实两处判）。
#   ② 通道不自写：复用归属方 handoff_lib.recycle()，两条出口（系统回收站 / _trash）都可逆
#      且自带 manifest（可 handoff.py recycle --restore 复原）；本件永不永久删除。
#   ③ 跟踪件不处置：git 跟踪件由 disposition_guard 默认拒绝（X-9：禁为让门禁变绿而迁走
#      已跟踪件），本件不放宽、不传 allow_tracked，只把它们计入 skipped_tracked 并点名。
# 注：正则刻意写成 [.] / [0-9] 形态（不用反斜杠）—— 本仓 §9.18 已记三起「多层转义把
#     正则吃掉」的事故（JS 模板串 / PowerShell 双引号 / Python 字面量各吃一层）。
DEFAULT_BAK_KEEP_FALLBACK = 3      # 仅当体量治理真相源取不到时的兜底（与 bak_keep 现值同源）
DEFAULT_BAK_AGE_FALLBACK = 7.0     # 同上，冷却期兜底（与 bak_age_days 现值同源）
RE_BAK_NAME = re.compile("^(?P<stem>.+)[.]r(?P<round>[0-9]{1,4})_(?P<hms>[0-9]{6})[.]bak$")
_BAK_STEM_MODE = ""


def _hg_scripts():
    """归属方脚本根（受管根入口；取不到环境变量时用实测默认值）。"""
    ap = os.environ.get("A_PROJECT_HANDOFF_SCRIPTS")
    if not ap or not os.path.isdir(ap):
        ap = "D:/global_skills/A-project-handoff/scripts"
    return ap


def bak_keep_source():
    """读体量治理的 bak_keep / bak_age_days（同一真相源，一次读齐）。

    返回 (keep, age_days, 来源说明)；取不到 ⇒ (None, None, 原因)，由调用方走兜底。
    """
    try:
        ap = _hg_scripts()
        if not os.path.isfile(os.path.join(ap, "handoff_lib", "volumegov.py")):
            return None, None, "取不到 volumegov（受管根不在位）"
        if ap not in sys.path:
            sys.path.insert(0, ap)
        from handoff_lib import volumegov as _V          # noqa: E402
        _b = getattr(_V, "DEFAULT_BUDGET", {}) or {}
        v = _b.get("bak_keep")
        a = _b.get("bak_age_days")
        if not (isinstance(v, int) and not isinstance(v, bool) and v >= 1):
            return None, None, "volumegov 无合法 bak_keep（%r）" % (v,)
        ok_a = isinstance(a, (int, float)) and not isinstance(a, bool) and a >= 0
        return v, (a if ok_a else None), "volumegov.bak_keep/bak_age_days"
    except Exception as e:
        return None, None, "import volumegov 异常：%r" % (e,)


def _recycle_mod():
    ap = _hg_scripts()
    if ap not in sys.path:
        sys.path.insert(0, ap)
    from handoff_lib import recycle as _R                # noqa: E402
    return _R


def _bak_stem(name):
    """归一化备份基名 —— 优先用体量治理的**同一个**函数（同一事实只在一处判）。

    一手（volumegov._scan_backups 的原注）：轮次标签夹在中间时只削尾缀，会让 24 份备份
    各成一组、L4 全漏 => 我再另写一套分组，必然与体量门算出两个簇。取不到真相源时
    才回落本件正则，并把分组来源标进统计（stem_src=fallback 即显式可见，不冒充同源）。
    """
    global _BAK_STEM_MODE
    low = str(name).lower()
    try:
        ap = _hg_scripts()
        if ap not in sys.path:
            sys.path.insert(0, ap)
        from handoff_lib import volumegov as _V          # noqa: E402
        out = _V._stem_of_backup(low)
        _BAK_STEM_MODE = "volumegov"
        return out
    except Exception:
        _BAK_STEM_MODE = "fallback"
        m = RE_BAK_NAME.match(low)
        if m:
            return m.group("stem")
        return low[:-4] if low.endswith(".bak") else low


def trim_backup_cluster(scan_dir, stem, keep, max_move=5, age_days=7.0, exclude="", reason=""):
    """把同一备份簇收敛到最新 keep 份；超出**且已过冷却期**者走可逆回收通道。

    簇口径与体量治理 L4 对齐（volumegov._scan_backups）：分组 = 归一化基名（跨目录，
    因为默认落点是每轮一个新目录 _trash/mark_backup_rNN，只在目录内分组会「每簇恒 1 份」，
    跨轮累积这个真正的大头永远管不住）；排序 = mtime 倒序留最新。
    冷却期不是保守，是防毁他人安全副本：并行会话刚写的 .bak 若被我当垃圾收走，它那一笔
    改动的唯一旧态副本就没了。exclude = 本轮刚写的那份，任何情况下不回收。
    keep / max_move / age_days 非法 ⇒ 一律不动（禁把配置写错变成全员清空）。
    单次上限 max_move：存量簇达 100 份时禁止一把清空，存量清理须人工核后走 volume --apply。
    """
    stat = {"attempted": 0, "recycled": 0, "skipped_tracked": 0, "failed": 0,
            "kept": 0, "cluster_before": 0, "cooled": 0, "capped": 0,
            "stem_src": "", "disabled": False, "errors": []}
    if not isinstance(keep, int) or isinstance(keep, bool) or keep < 1:
        stat["disabled"] = True
        stat["errors"].append("非法 keep=%r => 一个都不动（禁把配置写错变成全员清空）" % (keep,))
        return stat
    if not isinstance(max_move, int) or isinstance(max_move, bool) or max_move < 1:
        max_move = 1
    try:
        age_days = float(age_days)
    except (TypeError, ValueError):
        age_days = 7.0
    if age_days < 0:
        age_days = 0.0
    try:
        want = _bak_stem(stem)
        stat["stem_src"] = _BAK_STEM_MODE
        excl = os.path.normcase(str(Path(exclude).resolve())) if exclude else ""
        cands = []
        for p in sorted(Path(scan_dir).rglob("*.bak")):
            if _bak_stem(p.name) != want:
                continue
            if excl and os.path.normcase(str(p.resolve())) == excl:
                continue                      # 本轮刚写的回滚副本，永不回收
            try:
                cands.append((p.stat().st_mtime, p))
            except OSError:
                continue
        cands.sort(key=lambda kv: kv[0], reverse=True)
        files = [p for _m, p in cands]
        stat["cluster_before"] = len(files) + (1 if excl else 0)
        stat["kept"] = min(len(files), keep) + (1 if excl else 0)
        if len(files) <= keep:
            return stat
        now = time.time()
        moved = 0
        # 遍历顺序必须是**最旧先动**：files 是新->旧，直接 for p in files[keep:] 会从
        # 「较新的那份受害者」开始收，配 max_move 上限时等于优先毁掉最新备份 —— 与收敛目的相反。
        for p in reversed(files[keep:]):
            try:
                age = (now - p.stat().st_mtime) / 86400.0
            except OSError:
                continue
            if age < age_days:
                stat["cooled"] += 1
                continue
            if moved >= max_move:
                stat["capped"] += 1
                continue
            stat["attempted"] += 1
            try:
                rr = _recycle_mod().recycle(
                    p, reason=reason or "r46 备份簇 keep 收敛（对标改造 H-2 / R211-2）")
            except Exception as e:
                stat["failed"] += 1
                stat["errors"].append("%s: %r" % (p.name, e))
                continue
            if rr.get("ok"):
                stat["recycled"] += 1
                moved += 1
            else:
                err = str(rr.get("error") or "")
                if "跟踪" in err:
                    stat["skipped_tracked"] += 1     # X-9：不由本件处置
                else:
                    stat["failed"] += 1
                    stat["errors"].append("%s: %s" % (p.name, err[:120]))
        return stat
    except Exception as e:
        stat["errors"].append("收敛整体异常：%r" % (e,))
        stat["disabled"] = True
        return stat


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
    ap.add_argument("--mode", choices=("verdict", "note"), default="verdict",
                    help="verdict=在账龄尺可见的「【rNN 裁决=…】」标记（仅 - [ ] 条目）；"
                         "note=任意行的「【rNN 补记：…】」校正注（W-19：05/06/08 的状态回写走同一入口）")
    ap.add_argument("--vault", default=str(ROOT), help="项目根（其下 memory/ 才允许写）")
    ap.add_argument("--allow-renumbered", action="store_true",
                    help="⑦ 显式放行「编号疑被改写」的条目（默认拒写，见 r128 事故）")
    ap.add_argument("--file", help="指定卷路径（必须位于 <vault>/memory/ 下）")
    ap.add_argument("--key", required=True, help="锚点子串（须在目标卷内唯一命中）")
    ap.add_argument("--round", required=True, help="本轮轮号，如 46")
    ap.add_argument("--verdict", help="裁决文本，如「降级（转长期看守）｜原因」（verdict 模式必填）")
    ap.add_argument("--note", help="校正注文本（note 模式必填，落为「【rNN 补记：…】」）；"
                    "verdict 模式下可选，会并入同一裁决标记内（r163 起，禁静默丢弃）")
    ap.add_argument("--glob", default="07-next-steps*.md", help="在哪些卷里找锚点（默认 07 全卷）")
    ap.add_argument("--backup-dir", default=None,
                    help="备份目录（默认 <vault>/05-exec/mark_backup；刻意不放记忆卷，见 r35 落点教训）")
    # r214（对标改造 H-2 / R211-2）：阈值读体量治理的单一真相源（volumegov），
    # 本件不另立常量 —— 两处各写一份必漂移（本仓 R263/R280 反复判红的同族）。
    ap.add_argument("--backup-keep", type=int, default=None,
                    help="同簇保留最新 N 份（缺省读 volumegov bak_keep，取不到则 3）")
    ap.add_argument("--backup-age-days", type=float, default=None,
                    help="冷却期：新于 N 天的备份一律不动（缺省读 volumegov bak_age_days）")
    ap.add_argument("--backup-trim-max", type=int, default=5,
                    help="单次最多回收几份（存量簇上百份时禁一把清空）")
    ap.add_argument("--no-backup-trim", action="store_true", help="关闭收敛（取证用）")

    args = ap.parse_args()
    if args.mode == "verdict" and not args.verdict:
        return refuse("verdict 模式必须给 --verdict")
    if args.mode == "note" and not args.note:
        return refuse("note 模式必须给 --note")
    # r163 修（R163-5，X-8 同族：return 了成功却没写盘的东西）：
    #   旧式 verdict 模式下 --note **完全不参与拼接** ⇒ 长理由蒸发、零告警，而
    #   读回验证只验「裁决标记与锚点同行」⇒ 照样打 [MARK:OK]（假交付面）。
    #   一手取证：本轮四条裁决带长 --note 调用全 OK，事后 grep 理由正文在 07 卷 0 命中。
    #   修法 = verdict 模式**也**接受 --note，并入同一 marker（同物理行，禁拆两行凑绿）；
    #   换行/连续空白压成单空格 —— 标记是行内追加物，带换行会把后续内容顶到下一行。
    def _one_line(s):
        return " ".join((s or "").split())

    if args.mode == "verdict":
        body_text = _one_line(args.verdict)
        _nt = _one_line(args.note)
        if _nt:
            # 已有内联「｜原因」形态（老调用方）则不重复分隔
            body_text = body_text + ("" if ("｜" in body_text) else "｜") + _nt
    else:
        body_text = args.note
    mark_head = ("r%s 裁决=" % args.round) if args.mode == "verdict" else ("r%s 补记：" % args.round)

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
        if args.mode == "note":
            hits = [n for n, c in enumerate(lines, 1) if args.key in c]
            if not hits:
                continue                                        # 本卷无此锚点，去下一卷找
            if len(hits) != 1:
                return refuse("② note 模式锚点命中数 != 1（歧义即拒写，禁挑第一行）",
                              "命中 %s 行 in %s" % (hits, rp.name))
            i = hits[0] - 1
            if mark_head in lines[i]:
                return refuse("④ 本轮已在此行写过补记，不重复写（幂等靠拒绝）", "%s:%d" % (rp.name, i + 1))
        else:
            open_hits, closed_hits = find_item_lines(lines, args.key)
            if len(open_hits) + len(closed_hits) == 0:
                continue
            if closed_hits and not open_hits:
                return refuse("③ 锚点只命中已闭环条目，禁往 - [x] 上标裁决",
                              "行 %s in %s" % (closed_hits, rp.name))
            if len(open_hits) != 1:
                return refuse("② 锚点命中数 != 1（重复登记或跨卷歧义）",
                              "命中 %s 行 in %s" % (open_hits, rp.name))
            i = open_hits[0] - 1
            if mark_head in lines[i]:
                return refuse("④ 本轮已裁过，不重复写（幂等靠拒绝而非静默跳过）",
                              "%s:%d" % (rp.name, i + 1))
            if RE_DEFERRAL_TEXT.search(args.verdict or ""):                 # ⑥ 只对延期型裁决设卡
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
        # r129（R128-8）：写入前查条目编号是否被改写 —— 命中不一致即**响亮告警**，
        # 因为 r128 实测：按旧编号下达的裁决会落在同名但不同条目上，读回验证照样通过，
        # 账面仍红而人以为已处理完（静默失真是最难查的一类）。
        _renum = id_renumbered_note(args, lines[i])
        if _renum and not args.allow_renumbered:
            return refuse("⑦ 条目编号疑被改写（标题声明轮次与编号不一致，%s）⇒ 拒写，"
                          "请核对条目身份后用 --allow-renumbered 明示放行" % _renum, args.key)
        marker = "【" + mark_head + body_text + "】"
        new_rows = list(rows)
        body, tail = lines[i], rows[i][1]
        new_rows[i] = (body.rstrip() + " " + marker, tail)   # 只改目标这一行，行尾原样保留
        # r125（R123-4 收口·堵产生源）：原默认落 05-exec/mark_backup —— r57 清过 20 份后，
        # 该目录又无声攒到 40 份（35 未跟踪 + 5 被 git 跟踪），root_face 的 f12 二级盲区腿
        # 一度把它抓红。项目红线 #25④ 本就写明「散落项只迁 _trash，禁 .bak 作落点」，
        # 而 _trash 已被 noise 判据登记为「设计内指定回收区」⇒ 落 _trash 既合规又不产生敞口。
        # 同时保留 --backup-dir 覆盖能力（旧流程与夹具仍可用显式路径）。
        _trash = vault / "_trash" / ("mark_backup_r%s" % args.round)
        bdir = Path(args.backup_dir).resolve() if args.backup_dir else _trash
        bdir.mkdir(parents=True, exist_ok=True)
        bak = bdir / ("%s.r%s_%s.bak" % (rp.name, args.round, time.strftime("%H%M%S")))
        io.open(bak, "w", encoding="utf-8", newline="").write(raw)
        # r125：目标文件改原子写（先截零再逐字节写的窗口会让并行读方拿到空串/半写，
        # 已导致连续三轮假红）。与 ratchet_gate 的 _atomic_write_json 同理。
        _tmp = rp.with_suffix(rp.suffix + ".r125tmp")
        io.open(_tmp, "w", encoding="utf-8", newline="").write(join_keep_eol(new_rows))
        os.replace(str(_tmp), str(rp))
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
        # r214（对标改造 H-2 / R211-2）：备份簇 keep 收敛。刻意放在读回验证成功之后 ——
        # 任何 refuse / 回滚路径都不动既有备份（读回失败时那份 raw 还是唯一的旧态副本）。
        # 收敛结果不参与主判据成败：标记已写成功，回收只是附带卫生动作；异常打 WARN，
        # 既不把「没清干净」报成「裁决失败」，也不静默吞掉 WARN（R247）。
        if args.backup_keep is not None:
            _keep_v = args.backup_keep
            _age_v = args.backup_age_days if args.backup_age_days is not None else DEFAULT_BAK_AGE_FALLBACK
            _keep_src = "--backup-keep/--backup-age-days"
        else:
            _keep_v, _age_v, _keep_src = bak_keep_source()
            if _keep_v is None:
                _keep_v = DEFAULT_BAK_KEEP_FALLBACK
            if _age_v is None:
                _age_v = DEFAULT_BAK_AGE_FALLBACK
        if args.no_backup_trim:
            print("  [BACKUP-TRIM] --no-backup-trim => 本轮不收敛")
        else:
            # 扫描根 = 整个回收区，不是本次那个单轮目录：默认落点每轮一个新目录，
            # 只在目录内分组会「每簇恒 1 份」，跨轮累积（真正的大头）永远管不住。
            _ts = trim_backup_cluster(
                vault / "_trash", rp.name, _keep_v, max_move=args.backup_trim_max,
                age_days=_age_v, exclude=str(bak),
                reason="r46 备份簇 keep 收敛（round %s，阈值源=%s）" % (args.round, _keep_src))
            _warn = " ; ".join(_ts["errors"]) if _ts["errors"] else ""
            print("  [BACKUP-TRIM] 阈值=%s 冷却=%s天(源:%s 分组:%s) 簇内=%d 留=%d 回收=%d 冷却中=%d 超上限=%d 跳过跟踪件=%d 失败=%d%s"
                  % (_keep_v, _age_v, _keep_src, _ts["stem_src"], _ts["cluster_before"],
                     _ts["kept"], _ts["recycled"], _ts["cooled"], _ts["capped"],
                     _ts["skipped_tracked"], _ts["failed"],
                     (" WARN: " + _warn) if _warn else ""))
        return 0
    return refuse("② 锚点在全部候选卷里 0 命中（不得退化成追加到文件末尾）", args.key)


def id_renumbered_note(args, line):
    # ⑦（r129，R128-8 落地）：条目编号被改写时给出响亮提示。
    # 一手事故（r128）：并行会话把 R123-4 / R125-5 改号避撞，我按旧编号写的裁决落在
    # 「同名但不同条目」上，读回验证照样通过（标记确实写进了那一行），但裁决对象错了 ——
    # 账面因此仍红，而我以为已处理完。
    # 检测：标题里声明的登记轮次（R123-1（r123 登记 => r123）与该编号在 git 里的首现轮号
    # 应当一致；不一致即提示「按旧编号的裁决无效」。
    # 取不到首现（未跟踪 / 历史被压平）⇒ 只打印不拒写（不因取不到真相源而误拒，R247 反向）。
    import re as _re
    m = _re.search(r'R(\d{2,3})([a-z]?)-(\d{1,2})', line)
    d = _re.search(r'（\s*r(\d{2,3})([a-z]?)\s*登记', line)
    if not m or not d:
        return None
    rid = 'R%s%s-%s' % (m.group(1), m.group(2), m.group(3))
    declared = 'r%s%s' % (d.group(1), d.group(2))
    if declared == 'r%s%s' % (m.group(1), m.group(2)):
        return None
    print('[MARK:WARN] ⑦ 条目 %s 标题声明登记轮次为 %s，与编号自带的 r%s 不一致 ⇒ 该编号疑被改写，'
          % (rid, declared, m.group(1) + m.group(2)))
    print('[MARK:WARN]   本次裁决若按旧编号下达将落在同名但不同条目上（r128 实测），请先核对条目身份')
    return rid

if __name__ == "__main__":
    sys.exit(main())
