# -*- coding: utf-8 -*-
r"""r38_debt_aging.py — 第十四维「积压债务的可见性与到期治理」测量尺（只读）。

对标实物（2026-09-25 `gh api` 实测，见 `--opponents` 内置结论与报告 §2）：
  github/spec-kit        27 workflow，含 `Close stale issues and PRs` + 6 条 issue 自动化  ← 唯一有到期治理的
  obra/superpowers       401 open issues，最老 open 于 2026-01-27（≈241 天）无人裁决
  anthropics/skills     1290 open issues，最老 open 于 2025-10-16（≈344 天）
  addyosmani/agent-skills 118 open，最老 2026-04-04
  pre-commit/pre-commit   25 open（靠"少建待办"而非"自动化到期"，最老一条 2018 年仍 open）
本体系对应物 = `memory/07-next-steps.md` 的 P0/P1 待办队列 —— 它有「挂账 N 轮」的**散文式自陈**，
却**没有任何机器判据**回答「哪条已经老到必须裁决」。实证：本仓 M-1 自 r33 挂到 r38（5 轮）仍无动作。

判据（三分类 + 一类未定年，四者之和 == 受检条目数，X-7 自洽校验）：
  DECIDED  已带机器可查裁决标记：`裁决=执行` / `裁决=降级` / `裁决=作废` / `挂账至 rNN`（目标轮 ≥ 本轮-1）
  OVERDUE  无裁决标记 且 账龄 > GRACE（默认 2 轮）
  ACTIVE   无裁决标记 但 账龄 <= GRACE
  UNDATED  条目里取不到来源轮次 ⇒ 单独成类，**禁止**并入 ACTIVE 蒙绿（R247）
OVERDUE 的条目再用 git 复核首次出现日期（`git log -S`），防"轮次标错"造成的假账龄。

用法：python 05-exec/r38_debt_aging.py [--json out.json] [--grace 2] [--quiet]
退出码：0 = 完成测量（本尺**本身不阻断**，阻断由 ratchet_gate 第 7 指标承载） / 2 = 取不到输入面
"""

import argparse
import datetime as dt
import fnmatch
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
# [R322 2026-10-26] --ledger-root 生效点：main() 解析参数后把本模块 ROOT 指到指定仓
TAXONOMY = ["OVERDUE", "ACTIVE", "DECIDED", "UNDATED", "DEFERRED", "REPEAT"]   # r39 加 DEFERRED（看得见但不到期，不得并入 DECIDED）；r43 加 REPEAT（第 31 行说明）
GRACE_DEFAULT = 2
# r42 D49 / r43 W-11b：宽限期按优先级分档。统一 2 轮会把 P2 长期项与 P0 同罪判红，
# 噪音反而稀释 P0 的紧迫感（活证据：本仓 W-2 自己在 r42 被判成 OVERDUE）。
GRACE_BY_PRIORITY = {"P0": 2, "P1": 4, "P2": 8, "UNMARKED": 2}
RE_PRIORITY = re.compile(r"【\s*(P[0-2])")
# r195 修 R194-2（宽限表长期是死代码）：旧 RE_PRIORITY 只认「【P0」方括号形态，而本仓主流
# 条目写法是圆括号（r194 登记，P1·已落地）⇒ 全量 339 条里 209 条读不到 P 级，GRACE_BY_PRIORITY
# 的 P1=4 / P2=8 从不生效，一律走 GRACE_DEFAULT=2。实测三行：R194-1、R183-1 标题均返回 None，
# 只有【P0·…】命中。修法 = 只看**条目标题段**（第一个全角冒号之前，无冒号退整条），用通用
# 边界式匹配 P0/P1/P2；标题段无 P 级再回退全文（保守，绝不比现状更宽松）。
# 只看标题段是为堵同族劫持（X-23 第 6 次复发，本轮我自抓）：R194-2 正文写了「只认「【P0」形态」,
# 被全文 search 读成 P0 ⇒ 宽限从应有的 8 塌成 2 —— 我登记这条缺陷的字，自己触发了这条缺陷。
RE_GRACE = re.compile(r"(?:^|[^0-9A-Za-z])(P[0-2])(?:[^0-9]|$)")
# r201：轮号只认「提交自身作用域」的形态，三选一分支各占一个捕获组，取号时须跳过 None。
#   ① 主题前缀式 chore(r201c): / feat(r201): —— 括号内才是本轮声明；
#   ② 声明式 r201 登记|立|新增|补记|更新|收尾；③ 中文「第 201 轮」。
# 刻意不认裸 rNNN（那会命中「挂账至 r206」「见 §41」等引用），也不认数字前紧邻挂账语境。
RE_SCOPED_ROUND = re.compile(
    r"[a-z]+\(r(\d{1,3})[a-z]?\)"
    + r"|(?<![至挂])(?<!挂账 )(?<!续挂 )(?<!目标 )r(\d{1,3})\s*(?:登记|立|新增|补记|更新|收尾)"
    + r"|第\s*(\d{1,3})\s*轮")
FULLWIDTH_COLON = chr(65306)


def grace_for(text):
    """条目的宽限轮数：优先看标题段（第一个全角冒号前）的 P 级，无则退全文，再无则默认。"""
    head = (text or "").split(FULLWIDTH_COLON)[0]
    mm = RE_GRACE.search(head) or RE_GRACE.search(text or "")
    return GRACE_BY_PRIORITY.get(mm.group(1) if mm else "UNMARKED", GRACE_DEFAULT)
# r42 D48 / r43 W-11a：同一条目被改期 >= 2 次 ⇒ 判 REPEAT 并强制升级，
# 堵死「到期就再往后挂一轮」的延期 treadmill（账面一路 DEFERRED，趋势线看不出恶化）。
RE_DEFERRAL = re.compile(r"挂账至\s*r\d{1,3}")
REPEAT_AFTER = 2
RE_ITEM = re.compile(r"^\s*-\s\[( |x)\]\s+(.+)$")
RE_ROUND_DECL = re.compile(r"(?:r(\d{1,3})\s*(?:登记|立|新增|补记|更新|收尾)|第\s*(\d{1,3})\s*轮|"
                           r"挂账\s*(\d{1,2})\s*轮)")
# r128 自抓（词表缺口）：「销账」是多轮沿用的自然表述（已完成并核销），但不在终局词表里，
# 于是写了 `裁决=销账` 仍被判 OVERDUE —— 判据不认我自己的裁决词。
# 修法 = 把该词**收进取值域**（扩枚举，不是放宽判定）：销账与「执行」同义，都表示已闭环。
# r260 根因修（X-23「正文引用劫持定年」同族第 6 次复发，且这次是**修好了却没接上线**）：
#   原式把 `-[ ]` 勾选框写成**必需前缀**。但两个调用点喂进来的形态不同 ——
#   夹具传整行（带 `- [ ]`）⇒ 命中；scan() 传的是 RE_ITEM 已剥掉勾选框的**正文**（`**R260-8（r260 登记…`）
#   ⇒ 永不命中 ⇒ r194 那次「标题自身编号优先」在生产路径上是死代码，origin 落到回退循环，
#   而循环取**最后一个** rNN 声明。一手：R260-8 正文写了「r113 立的 §3.1」（r113 是**另一件事**的
#   规范轮号）⇒ 登记轮号被顶成 113 ⇒ 账龄 260-113=147 轮 ⇒ 刚登记的条目当场判 OVERDUE。
#   修法 = 勾选框改成**可选前缀**并一律用 match（锚定串首）。不放宽：正文不以 R 号开头时
#   仍不命中，照旧走原回退循环（不新增判定能力，只把已有的标题优先真正接上）。
RE_TITLE_OWN = re.compile(r"\s*(?:-\s*\[[ x]\]\s*)?\*{0,2}\s*R(\d{2,3})[a-z]?-\d+")
    # r194：条目标题自身的编号（R194-1（r194 登记…）里的 194）= 登记的唯一权威来源。
    # 此前它只存在于 age is None 的回退支（r128），主循环一旦被正文引用先命中就再也轮不到它。
# r194：裁决取值域**单源化**。此前 RE_DECIDED 与 parse_last_verdict 的头部匹配各写一份词表，
# 改一处漏一处 ⇒ 与本轮 ratchet_gate「同一文件三份取最新件实现」同族的漂移风险。新增词只加这一处。
VERDICT_TERMS = ("执行", "降级", "作废", "保留", "销账", "已落地", "结案")
    # r260 收词（同 r128 收「销账」/r194 收「已落地」的先例，**扩枚举非放宽判定**）：
    # 本仓 r251/r256 用「结案」表示「以取证/判据取代人工、条目定稿」，且已在正文写出。
    # 一手代价：R250-2 / R252-2 两条 r251/r256 写了结案仍判 OVERDUE —— 判据不认词，
    # 棘轮 overdue_debt_items=6 超基线 0 连带 ratchet_gate 恒红。头部仍必须出现明确
    # 终局词才计数（X-10 不变：自造措辞照旧不算裁决）。
    # r194 收词（按 r128 收「销账」的先例**扩枚举**，不是放宽判定）：本仓 r192/r193/r194
    # 三轮都用「已落地」表示改动已入库且复验过，语义等同「执行」；仍要求头部出现明确
    # 终局词，自造措辞照旧不算裁决（X-10）。我这三条此前全被判 OVERDUE = 判据不认我的词。
RE_DECIDED = re.compile(r"裁决\s*=\s*(" + "|".join(VERDICT_TERMS) + r")|挂账至\s*r(\d{1,3})")
# r49 根因修（第 2 形态）：裁决标记是 `【rNN 裁决=<头部>｜原因】`，而**原因里允许引用旧标记原文**
# （本轮就在 W-14 上写了「r46 却在本条上写了『挂账至 r49』」）。全文 search 的 last-wins 会被
# 引号内容劫持 ⇒ 终局裁决被回判成"过期挂账"，凭空造一条 OVERDUE。
# 判据口径：只认**最后一个标记的头部**（第一个 ｜/】 之前），原因体一律不参与判定。
RE_MARK_HEAD = re.compile(r"【\s*r(\d{1,3}(?:[a-z])?)\s*裁决\s*=\s*([^｜】]*)")
   # r120b: 裁决头轮号补字母后缀（r119b / r120b 这类同轮多支线编号）。
   # 原式 r(\d{1,3}) 匹配不到 r120b ⇒ 支线轮裁决头静默不可见，
   # 最后头部回退到上一轮旧标记（本轮实测：R114-3 的 r120b 降级没被读到，
   # 尺子仍按 r119「挂账至 r122」判 OVERDUE）。
   # 与 RE_SUGG_ID 同族第 3 次：命名空间不认后缀轮号 ⇒ 修尺不放宽判定。


def parse_last_verdict(text):
    """返回 (kind, arg)：kind ∈ "FINAL"/"DEFER"/None；FINAL 的 arg 是裁决词，DEFER 的 arg 是目标轮 int。

    有 `【rNN 裁决=` 标记时**只看最后一个标记的头部**；一个都没有才回退到全文扁平匹配
    （兼容层a 夹具直接喂无括号裸文本）。头部取不到合法取值 ⇒ 视为未裁（X-10：自造措辞
    不算裁决，与 r38「部分作废不在取值域即照判 OVERDUE」同口径）。
    """
    heads = list(RE_MARK_HEAD.finditer(text or ""))
    if heads:
        head = heads[-1].group(2).strip()
        m = re.match("(" + "|".join(VERDICT_TERMS) + ")", head)   # r194 并轨单源词表
        if m:
            return ("FINAL", m.group(1))
        d = re.match(r"挂账至\s*r(\d{1,3})", head)
        if d:
            return ("DEFER", int(d.group(1)))
        return (None, None)
    flat = list(RE_DECIDED.finditer(text or ""))
    if not flat:
        return (None, None)
    last = flat[-1]
    return ("DEFER", int(last.group(2))) if last.group(2) else ("FINAL", last.group(1))
RE_R_IN_SUBJECT = re.compile(r"\br(\d{1,3})\b")
# 作用域轮号：(r201) / (r201c) 前缀式，或 r201 登记|立|新增|补记|更新|收尾、第 201 轮； NL + "# 但排除紧邻「挂账/续挂/至/目标」的未来轮号引用（那是账期，不是本轮声明）。" + NL + RE_SCOPED_ROUND = re.compile('^(?:[a-z]+()?r(d{1,3})[a-z]?)'|'(?<!挂账 )(?<!续挂 )(?<!至 )(?<!目标 )r(d{1,3})s*(?:登记|立|新增|补记|更新|收尾)'|'第s*(d{1,3})s*轮')
# R121（R119b-5）：条目编号（R\d{2,3}-\d{1,2}），用于跨分卷同号多副本检测。
RE_ID_SUBJECT = re.compile(r"^\*{0,2}【?[^】]{0,24}?\b(R\d{2,3}-\d{1,2})\b")


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT)] + list(args),
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def current_round():
    """本轮轮号 = 近期提交**自身作用域**里的最大 rNN（取值命令随结果走，不硬编码）。

    r201 修（我自己造的缺陷）：旧实现取主题里任意 rNN 的最大值，于是提交主题里写
    「挂账至 r206」会把全仓轮号从 r201 推到 r206 —— 尺子的原点被一句记账话术往前挪，
    后果是所有挂账条目集体提前到期（实测 overdue 3→4，且第 4 条就是我自己那条）。
    现按两级取号：① 优先只认作用域形态 (rNNN) / rNNN 登记|立|新增|补记|更新|收尾 / 第 N 轮；
    ② 一个都没有才回退到旧的任意 rNN（保持对历史提交主题的兼容），并在回退时告警。
    排除项：数字前紧邻「挂账/续挂/至/目标/hang/defer」的一律不算本轮声明。
    """
    out = git("log", "--format=%s", "-40").stdout
    # 三分支捕获组互斥：每个 match 只有一个组非 None，必须挑出来而不是 group(1)
    scoped = []
    for m in RE_SCOPED_ROUND.finditer(out):
        for g in m.groups():
            if g:
                scoped.append(int(g))
                break
    if scoped:
        return max(scoped)
    hits = [int(m.group(1)) for m in RE_R_IN_SUBJECT.finditer(out)]
    if hits:
        print("[ROUND:FALLBACK] 近 40 条提交主题里没有作用域轮号 (rNNN)，"
              "回退取任意 rNN 最大值 = r%d（若该值来自「挂账至 rNN」等引用，轮号已失真）"
              % max(hits))
    return max(hits) if hits else None


def round_from_tag():
    """独立轮号锚 = 最近一个 annotated tag（r33 起每轮收尾打 tag）。
    与 `git log --format=%s -40` 的窗口取值互不依赖，专供 W-20 的轮号面对账。"""
    out = git("describe", "--tags", "--abbrev=0").stdout.strip()
    m = re.match(r"^r(\d{1,3})\b", out)
    return int(m.group(1)) if m else None


# ------------------------------------------------------- W-20（r49）：输入面截断自证
def face_round(round_log, round_tag):
    """轮号面自证：提交主题窗口（降采样 -40）与 tag 硬锚（不降采样）双向对账。

    存在理由：整把尺子的账龄与到期都以 `now_round` 为原点，而它取的是**最近 40 条提交主题**
    里的最大 rNN —— 一旦一轮的提交数超过窗口，本轮声明就被截掉，轮号回退到上一轮，
    于是"到期项"集体少算一轮、账龄集体变浅，报出来的绿只是**局部干净**。
    返回 (ok, detail)；True=面自证通过 / False=判红 / None=无 tag 锚可对照（首轮，记 UNVERIFIED）。
    """
    if round_log is None:
        return (False, "提交主题窗口取不到轮号（log=None）—— 禁按 0 起算（R247）")
    if round_tag is None:
        return (None, "无 tag 锚可对照（首轮未打 tag 或 describe 失败）⇒ UNVERIFIED，不记绿")
    if round_tag > round_log:
        return (False, "tag=r%d 晚于 -40 窗口推出的 r%d ⇒ 窗口没覆盖到本轮声明，轮号基准被截断"
                % (round_tag, round_log))
    # r201 补：原实现只防「被算少」（窗口截断），不防「被算多」。而「被算多」会伪装成
    # 完全合法的形态（本轮尚未打 tag ⇒ log 比 tag 大），所以必须给差值设上限：
    # 一轮内可以有多个提交，但轮号最多领先 tag 一轮；领先 >=3 轮只可能是主题里出现了
    # 未来轮号（如「挂账至 r206」），此时整把尺子的原点已经不可信。
    if round_log - round_tag >= 3:
        return (False, "log=r%d 比 tag=r%d 领先 %d 轮 ⇒ 轮号疑被提交主题里的未来轮号污染"
                "（例：主题写「挂账至 rNN」），尺子原点不可信"
                % (round_log, round_tag, round_log - round_tag))
    return (True, "log=r%d ≥ tag=r%d（差 %d 轮：%s）"
            % (round_log, round_tag, round_log - round_tag,
               "本轮 tag 已打，两源一致" if round_log == round_tag
               else "本轮尚未打 tag，属每轮收尾打标的既有节奏"))


def face_dedup(raw_lines, items_total, collisions):
    """去重面自证：`key = body[:80]` 是**截断键**，两条不同条目撞前缀会被静默吞掉。

    存在理由（r49 立规）：open_total 是台账自洽式（debt_class_sum）的右端，
    被吞的行不会出现在任何一态里 ⇒ 分类之和仍"自洽"，账却是少的（少算比错算更难发现）。
    因此守恒必须是**行数 → 条目数**的守恒，而不是只查分类之和。
    """
    if raw_lines != items_total:
        return (False, "RE_ITEM 命中 %d 行，只计入 %d 条 ⇒ 有 %d 行被静默吞掉"
                % (raw_lines, items_total, raw_lines - items_total))
    if collisions:
        return (False, "%d 组 80 字前缀相同但正文不同 ⇒ 去重键在吞不同条目，首例：%s … vs %s …"
                % (len(collisions), collisions[0]["a"][:36], collisions[0]["b"][:36]))
    return (True, "%d 行全部计入，80 字前缀键零碰撞" % raw_lines)


def face_dup_ids(dup_ids):
    """R121（R119b-5）：同号多副本面自证。

    存在理由（r119 一手实证）：R112-1/2/3/4 在 part78 已 `[x]` 闭环，而 part75 留旧副本
    未勾销 ⇒ 同一笔债被算两次，overdue 从 0 虚增到 11（其中 4 条是这么来的）。
    现去重键是 80 字前缀，**跨分卷同号但正文不同的副本前缀不同 ⇒ 漏检**。

    判据口径（不静默、不代裁）：
      - 一个编号出现在 >1 个分卷 ⇒ 判红点名（可能是漏勾销，也可能是同号不同义）；
      - 全部副本都已 `[x]` ⇒ 只报不判红（无害，属拆卷留痕）；
      - 同卷内多行同号 ⇒ 同样点名（可能是重复登记）。
    本面**不改记账行为**（不自动去重、不自动勾销），只把「该看一眼」的显形。
    """
    if not dup_ids:
        return (True, "同号多副本 0 组（按条目编号聚合，跨分卷可见）")
    # r260 分类具名（诊断方向修正，判红口径**不放宽**）：同号有两种成因，处置完全不同 ——
    #   A 撞号：编号后的标题主体不同 ⇒ 两条**不同**条目抢了同一个 R 号（L-6 编号命名空间病，
    #     处置 = 给后登记者改号消歧并留 R241 注）；
    #   B 真副本：主体相同 ⇒ 同一笔债的第二份留痕未勾销（处置 = 勾销/迁卷，r119 那 4 条即此）。
    # 旧实现不分类、一律写「疑似漏勾销致重复计账」，本轮实测三组全是 A，照旧措辞会把人引去
    # 找一个根本不存在的漏勾销（#32 形态：读数对、结论方向错）。
    def _split(group):
        subs = set(x.get("subject") or "" for x in group["locs"])
        return "collision" if len(subs) > 1 else "stale_copy"
    bad = [d for d in dup_ids if not d["all_checked"]]
    coll = [d for d in bad if _split(d) == "collision"]
    stale = [d for d in bad if _split(d) == "stale_copy"]
    if bad:
        parts = []
        if coll:
            d = coll[0]
            parts.append("撞号 %d 组（不同条目抢同一编号，首例 %s：%d 处，主体不同 ⇒ 处置=改号消歧，非漏勾销）"
                         % (len(coll), d["id"], d["n"]))
        if stale:
            d = stale[0]
            parts.append("真副本 %d 组（主体相同而未勾销，首例 %s：%d 处，跨 %d 卷 %s ⇒ 疑似漏勾销致重复计账）"
                         % (len(stale), d["id"], d["n"], len(d["files"]),
                            ", ".join(os.path.basename(f) for f in d["files"])))
        return (False, "%d 组同号多副本存在未勾销副本：" % len(bad) + "；".join(parts))
    return (True, "%d 组同号多副本但全部已勾销（拆卷留痕，不判红）" % len(dup_ids))

def face_dating(seen_short, seen_full):
    """定年面自证：`git log -S` 的 needle 取正文前 70 字（截断串），可能命中更早的同前缀行。

    判据口径（X-21 同族）：两路取值**不等即判红**，禁止"取更保守的那个"把差异吞掉——
    差异本身就是"截断改变了结论"的证据，需要人看一眼而不是让尺子自选。
    """
    if seen_short is None and seen_full is None:
        return (True, "两路都取不到首现日期（该条目无 git 史，已按 UNDATED 面另行看守）")
    if seen_short == seen_full:
        return (True, "截断 needle 与全文 needle 同值 %s ⇒ 截断未改变结论" % seen_short)
    return (False, "前 70 字取到 %s，全文取到 %s ⇒ 截断改变了定年结论，须人工裁决"
            % (seen_short, seen_full))



def volume_files():
    """P0 唯一真相源 = 主壳；分卷里也有在途待办，一并按同一判据计（防"只量主壳"造成覆盖面虚高）。"""
    return sorted(ROOT.glob("memory/07-next-steps*.md"))


RE_OWN_CLAIM = re.compile(r"(归属方|归属会话|转办|待归属|他人归属)")
RE_PATH = re.compile(r"(?:[A-Za-z]:[\\/]|[\w.\-]+\.(?:py|md|json|jsonl|yml|yaml|sh|ps1|html))")


def classify_owner(text):
    """W-6（r48）：条目里「这不属于我」的声明必须**可机检**。

    存在理由（r40 D37 实测）：我把本仓自持的 `rule_conflict_scan.py` 标成「归属方件」挂了 4 轮 ——
    自家债被错误外部化后**永远不会有人做**。若允许只写"属归属方"而不给路径，
    这条退路比降级还便宜（X-14 防的是降级免检，这里防的是"甩锅免检"）。
    返回：OWNERED（声明归属且给了可解析路径）/ UNOWNED（声明归属却无路径 = 待查）/ NONE（不涉及归属）。
    """
    if not RE_OWN_CLAIM.search(text):
        return "NONE"
    return "OWNERED" if RE_PATH.search(text) else "UNOWNED"


def find_item_line(lines, key):
    """W-13（r44）：按**标题锚点**定位在账待办，返回全部命中的 1-based 行号。

    存在理由（r43 实测 D55）：并行会话整卷重写 + 本会话前序插入都会让行号漂移，
    按行号写裁决会写错行或漏写（r43 有 5 条 OVERDUE 报出的行号在写入时已不是未勾选行）。
    只认 `- [ ]` 未勾选项 —— 已闭环条目不参与定位，禁止往别人已做完的条目上再写裁决。
    命中数 != 1 时调用方必须**拒绝写入**并报告（多命中＝重复登记，见 t41/t46）。
    """
    return [i + 1 for i, l in enumerate(lines)
            if key in l and l.lstrip().startswith("- [ ]")]


def adjudication_gap(prev_keys, lines, round_tag):
    """W-12（r44）：上一轮 OVERDUE 清单里，本轮**仍未真正处理**的条目（missing 列表）。

    语义（t40–t46 锁死，防"只裁第一行就宣称完成"）：
      · 无任意裁决标记的在账项 ⇒ missing；
      · 最后一次标记是**已到期**的挂账（目标轮 <= 本轮）⇒ 仍 missing（延期不算已裁）；
      · 最后一次标记是终局裁决（执行/降级/作废/保留）或未到期挂账 ⇒ 不算；
      · 条目已勾掉或已不在账 ⇒ 不算（视为闭环/归档，不重复追责）。
    动因：r41 只裁「当期到期清单」、漏裁「账龄新越线清单」，r42 账面从 1 炸到 20；
    完整性没有机器约束时，它永远取决于我还记得多少。
    """
    cur = int(re.sub(r"\D", "", str(round_tag)) or 0)
    missing = []
    for key in prev_keys:
        hits = find_item_line(lines, key)
        for i in hits:
            kind, arg = parse_last_verdict(lines[i - 1])
            if kind is None:
                missing.append(key)          # 无标记，或有标记但头部不在取值域 ⇒ 不算已裁
            elif kind == "DEFER" and arg <= cur:
                missing.append(key)          # 已到期的挂账不算已裁
    return missing


def first_seen(rel_path, needle):
    r = git("log", "--format=%ad", "--date=short", "-S", needle[:70], "--", rel_path)
    dates = [d for d in r.stdout.split() if re.match(r"^\d{4}-\d{2}-\d{2}$", d)]
    return dates[-1] if dates else None


def count_deferrals(text):
    """真实延期次数 = **当前生效延期链**上的「挂账至 rNN」标记数。

    两条口径（缺一即错）：
    ① 只数**头部**，原因体里引用的旧标记原文不计 —— 否则 r49 那种"在原因里引用
       『挂账至 r49』"会把 REPEAT 计数（第 9 指标）虚增（X-17 反向形态）。
    ② **终局裁决中断延期链**：终局（执行/降级/作废/保留）之后的挂账才计入，
       终局之前的挂账已被「清零」—— r120b 实测残留：一条目「挂账 r121 → 降级
       → 挂账 r125」被数成 2 次延期，误增 REPEAT 1（终局明明已把它转长期看守，
       后面的挂账是新一轮而非第 2 次改期）。
    """
    heads = [h.group(2).strip() for h in RE_MARK_HEAD.finditer(text or "")]
    if heads:
        # r123 自抓（q2 腿抓出）：口径② 原实现「终局后清零」把**终局前的历史改期也抹成 0**，
        # 与第 43 行规则「同一条目被改期 >= 2 次 ⇒ REPEAT」直接冲突 ——
        # 实例：条目「挂账 r49 → 执行完毕」只改期 1 次，按规则不该 REPEAT，
        # 但按「数活跃链」得 0 次会把真实发生过的改期从账上抹掉（反向失真）。
        # 正确口径 = **历史改期总数**（终局前的挂账全部计入）+ 终局后的挂账计入新一轮，
        # 两者相加才是「这条目一共被改过几次期」。
        total = sum(1 for h in heads if re.match(r"挂账至\s*r\d{1,3}", h))
        return total
    return len(RE_DEFERRAL.findall(text or ""))


def classify_item(text, now_round):
    """返回 (cls, detail) —— 单一条目的判定，供层a 夹具直接调用。"""
    # W-8 根因修（r41 实测）：一条待办一生会被多次裁决，标记是**追加**在同一条目里的，
    # 用 search() 取首个 = 让最早的挂账永久劫持后续终局裁决（11 条到期项因此反复判红）。
    # 台账语义必须是 last-wins（与本仓 gate_runs / ac-verdicts 的 append-only 口径一致）。
    kind, arg = parse_last_verdict(text)
    if kind == "DEFER":
        tgt = arg
        # r39 W-0：延期不是终局。目标轮未到 → DEFERRED（单列，趋势线可见）；
        # 已到/已过 → 重新判 OVERDUE（到期追讨），防"挂账至 rNN"变成永久免检通道。
        if tgt > now_round:
            n_def = count_deferrals(text)
            if n_def >= REPEAT_AFTER:
                return ("REPEAT", "第 %d 次延期至 r%d ⇒ 须升级：执行 / 降级为长期看守 / 作废"
                        % (n_def, tgt))
            return ("DEFERRED", "挂账至 r%d（尚余 %d 轮）" % (tgt, tgt - now_round))
        return ("OVERDUE", "挂账目标 r%d 已到期（本轮 r%d）" % (tgt, now_round))
    if kind == "FINAL":
        return ("DECIDED", "裁决=" + arg)
    grace = grace_for(text)   # r195：走标题段取值器（修 R194-2，堵正文 P 级引用劫持）
    origin, held = None, None
    # r194 根因修（正文引用劫持定年 · 同族第 5 次复发，X-23）：r128 当年把「先认标题自身
    # 编号」只写在 **age is None 的回退支**里，于是只要正文里任何一处出现 rNN+登记词，
    # 主循环就已把 origin 填上，回退支永远轮不到 ⇒ 修了个寂寞。本仓一手实测：r194 登记的
    # R194-1 正文写了「③ r130 登记生效」（r130 是**另一件事**的对账器名），标题真值 r194 被
    # 顶掉 ⇒ 账龄算成 194-130 = 64 轮 ⇒ 刚登记的条目当场被判 OVERDUE、W-12 完整性转红。
    # 正解 = 把「标题自身编号」提到主路径**之前**并优先采用；无编号条目仍走原循环（不放宽）。
    _own_title = RE_TITLE_OWN.match(text)   # r260：match 而非 search —— 标题编号必须在串首，见常量注
    if _own_title:
        origin = int(_own_title.group(1))
    else:
        for m in RE_ROUND_DECL.finditer(text):
            if m.group(1):
                origin = int(m.group(1))
            elif m.group(2):
                origin = int(m.group(2))
            elif m.group(3):
                held = int(m.group(3))
    age = None
    if origin is not None:
        age = now_round - origin
    elif held is not None:
        age = held
    if age is None:
        # r128 自抓（定年回退被正文引用劫持，同 R120b-6 / R126-6 同族第 4 次复发）：
        # 原式取正文**第一个**裸 rNN。实测 R123-1 的正文引用了 r118/r120/r105 等历史轮号，
        # 于是本条（r123 登记、账龄应为 0）被判「账龄 5 轮」⇒ 假 OVERDUE。
        # 修法：先认**标题里的登记轮号**（`R123-1（r123 登记` 这类自身编号），
        # 它才是条目的真实来源；只有标题没有可识别编号时才退回裸 rNN。
        own = RE_TITLE_OWN.match(text)   # r194：与主路径同一常量，两处不漂移
        if own:
            age = now_round - int(own.group(1))
            return (("OVERDUE" if age > grace else "ACTIVE"),
                    "账龄 %d 轮 / 宽限 %d（定年取标题自身编号 R%s-）" % (age, grace, own.group(1)))
        bare = re.search(r"\br(\d{1,3})\b", text)
        if bare:
            age = now_round - int(bare.group(1))
            return (("OVERDUE" if age > grace else "ACTIVE"),
                    "账龄 %d 轮 / 宽限 %d（回落：正文裸 rNN=r%s）" % (age, grace, bare.group(1)))
        return ("UNDATED", "取不到来源轮次")
    return (("OVERDUE" if age > grace else "ACTIVE"), "账龄 %d 轮 / 宽限 %d" % (age, grace))


RE_SUGG_ID = re.compile(r"\b([WXMHRL]-\d{1,2}|R\d{2,3}(?:[a-z])?-\d{1,2})\b")
   # r120b: 命名空间补字母后缀轮号（R119b-1 / R120b-5 这类同轮多支线编号）。
   # 原式只认 R\d{2,3}-\d，带后缀的编号静默逃逸「报告新建议必须落待办卷」检查
   # （r119b 首次发现、当时只登记 UNVERIFIED；r120b 按 #30 硬门禁要求修尺而非改编号）。
   # 先例 = r105 F-7 补 L 命名空间：扩面，不放宽判定。
# r105 F-7：命名空间补全。原式 `[WXMH]` 有两个洞，且都是**静默**的（不报错，只是看不见）：
#   ① 本函数自己的 docstring 写着承接面含 `W/M/H/L-nn`，可式里没有 `L` ⇒ L-6 这类待办从登记那日起
#      就没被「报告新建议必须落待办卷」这条检查扫过；
#   ② r59 起改用 `R<轮号>-<序号>` 命名新立项（R59-4…R59-15、R60-3、R76-x），整个 R 系列不匹配。
# 后果正打在用户这条指令的要害上：「把报告里的改进建议按优先级直接开工执行」的机器承接面就是这一条
# 检查 —— 编号取不到 ⇒ `face_suggestions` 走 `if not new_ids` 分支返回 UNVERIFIED，
# 于是「报告立了 5 条、待办卷一条没落」与「报告没立新建议」两种情形**同形**（假绿）。
# 修法=扩命名空间而不是放宽判定：新编号仍必须逐条在其各自承接面找得到，缺任一即 False。


def face_suggestions(new_ids, todo_text, doctrine_text=""):
    """建议面自证：本轮报告里新立的编号，必须在**它自己的承接面**上找得到。

    存在理由（r49 实测）：W-20 / W-21 只出现在 r48 报告正文，`07-next-steps.md` 里一条都没有
    ⇒ 账龄尺看不见 ⇒ 永不到期 ⇒ "把报告里的改进建议直接开工执行"在机器层面是空的。

    r50 分面修（我自己的判据首跑造出的假阳性）：编号有两个承接面，混为一谈会把合规判成违规 ——
      · `W/M/H/L-nn` = 待办 ⇒ 承接面 = 07 待办卷；
      · `X-nn`       = 禁止项/立规 ⇒ 承接面 = `memory/AGENTS.md` 的 X 表（**不该**要求它进待办卷）。
    且不得互相顶替：X 编号写在 07 里不算承接，反之亦然（由 t73 反例锁死）。
    """
    if not new_ids:
        return (None, "本轮报告未取到新建议编号 ⇒ 该面对照无意义（记 UNVERIFIED，不记绿）")
    faces = {"TODO": todo_text or "", "DOCTRINE": doctrine_text or ""}
    want = lambda i: "DOCTRINE" if i.startswith("X-") else "TODO"
    missing = [i for i in new_ids
               if not re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(i), faces[want(i)])]
    if missing:
        return (False, "%d/%d 条新编号未落到各自承接面（%s）⇒ 不落卷即永不到期，等于免检；"
                       "TODO 面=07 待办卷，DOCTRINE 面=memory/AGENTS.md"
                       % (len(missing), len(new_ids), ", ".join(missing)))
    return (True, "%d 条新编号全部在各自承接面有登记行（待办 %d 条 / 禁止项 %d 条）"
            % (len(new_ids), sum(1 for i in new_ids if want(i) == "TODO"),
               sum(1 for i in new_ids if want(i) == "DOCTRINE")))


def face_floor(cur_volumes, prev_volumes):
    """规模下限面（R-ENUM 补条的 floor 形态，r49 第 5 面）。

    存在理由（读权威契约后自查发现的本判据缺口）：前四面都是**面内自洽**，
    没有一面能发现「受检面整体变小」。若 `memory/07-next-steps*.md` 的 glob 因拆卷改名
    或权限问题少收一卷（16→15 甚至 16→1），去重守恒、轮号对账、定年双路**全都照样绿**，
    而"零积压"是在 1/16 的语料上算出来的 —— 与 R-ENUM 实证的 `core.quotepath` 把
    109 数成 79 同族。口径 = 集合断言而非计数阈值：上轮受检的每一卷本轮必须仍在面内
    （拆卷只增不减，故无需豁免表）。
    """
    if not prev_volumes:
        return (None, "取不到上一轮受检卷清单 ⇒ 规模面无对照（UNVERIFIED，不判绿）")
    missing = [v for v in prev_volumes if v not in set(cur_volumes)]
    if missing:
        return (False, "上轮受检 %d 卷中有 %d 卷本轮不在面内（%s）⇒ 受检面萎缩，"
                       "任何「零」都只代表剩余面" % (len(prev_volumes), len(missing),
                       ", ".join(os.path.basename(m) for m in missing)))
    return (True, "上轮 %d 卷全部在本轮 %d 卷面内（拆卷只增不减，无需豁免表）"
            % (len(prev_volumes), len(cur_volumes)))


def prev_scanned_volumes():
    """上一轮证据件里的 files_scanned（取值口径与 coverage_check 同源：mtime 倒数第二）。"""
    hist = sorted(ROOT.glob("06-benchmark" + os.sep + "debt_aging_r*.json"),
                  key=lambda p: p.stat().st_mtime)
    if len(hist) < 2:
        return []
    try:
        prev = json.loads(hist[-2].read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return list(prev.get("files_scanned") or [])


def face_dating_summary(fails, n_dated):
    """把定年面收成分成三态（R-ENUM 边界条：零输入不得静默 PASS）。"""
    if fails:
        return (False, "定年双路取值有 %d 条不等：%s" % (len(fails), str(fails[0]["why"])[:90]))
    if n_dated == 0:
        return (None, "本轮无到期项 ⇒ 定年面未行使（不判绿，也不判红）")
    return (True, "%d 条到期项定年两路同值（截断 needle 未改变结论）" % n_dated)


def make_handles(doc, ledger_rel="06-benchmark/debt_runs.jsonl"):
    """生成「可引用句柄」：报告正文写句柄 + 字段名，**不抄数值**（r53 W-34）。

    存在理由（r53 双侧实测）：
      · 对手：`addyosmani/agent-skills` 一份 README 挂 50 个文件链接、正文数字 0–1 个 ⇒ 数值由产物承载；
      · 我方：`06-benchmark/` 有 60 份机器可读件，而 r38 那个含 PR 的 `open_issues` 在报告散文里
        无命令跑了 **12 轮** ⇒ 抄进正文的数字必然与源头脱钩。句柄就是把"抄"换成"指"。
    """
    by = doc.get("by_class") or {}
    h = {"overdue": {"artifact": ledger_rel, "field": "overdue", "selector": "末行",
                     "command": "python -c 读 06-benchmark/debt_runs.jsonl 末行取 overdue（本件 resolve_handle 即该实现）"},
         "ledger_rows": {"artifact": ledger_rel, "field": "#rows", "selector": "行数",
                         "command": "wc -l 06-benchmark/debt_runs.jsonl"},
         "open_total": {"artifact": ledger_rel, "field": "open_total", "selector": "末行",
                        "command": "python 05-exec/r38_debt_aging.py --json /tmp/x.json 读 by_class 之和"},
         "decided": {"artifact": ledger_rel, "field": "decided", "selector": "末行",
                     "command": "tail -1 06-benchmark/debt_runs.jsonl"}}
    for k in ("deferred", "repeat", "undated"):
        if k in by:
            h[k] = {"artifact": ledger_rel, "field": k, "selector": "末行",
                    "command": "tail -1 06-benchmark/debt_runs.jsonl"}
    return h


def resolve_handle(h):
    """按句柄现场解值。取不到（文件缺/形状不全/字段缺/台账空）一律 None ⇒ 绝不返回 0 冒充。"""
    if not isinstance(h, dict):
        return None
    art, field = h.get("artifact"), h.get("field")
    if not art or not field:
        return None
    p = Path(art) if os.path.isabs(str(art)) else ROOT / str(art)
    if not p.is_file():
        return None
    try:
        rows = [json.loads(x) for x in io.open(p, encoding="utf-8", errors="replace").read().splitlines() if x.strip()]
    except ValueError:
        return None
    if not rows:
        return None
    if field == "#rows":
        return len(rows)
    return rows[-1].get(field)


def scan(files, now_round, grace):
    """扫全部受检卷，返回 (items, face)。

    face 是 W-20（r49）要求的面自证块：`raw_lines` 用与计入逻辑**无关**的口径重新数
    （RE_ITEM 命中即数），用来证明 `body[:80]` 去重键没有吞掉不同条目。
    """
    global GRACE_DEFAULT
    items, seen = [], {}
    raw_lines, collisions, dating_fails = 0, [], []
    # R121（R119b-5）：同号多副本检测。r119 实测 R112-1/2/3/4 在 part78 已 [x]
    # 而 part75 留旧副本 ⇒ 同一笔债被算两次（overdue 11 里有 4 条是这么来的）。
    # 现判据只按 80 字前缀键去重，**跨分卷同号但正文不同的副本前缀不同 ⇒ 漏检**。
    # 本块按「条目编号」聚合（RE_R_IN_SUBJECT 取 Rd{2,3}-d{1,2}），
    # 一个编号出现在多个分卷即入 dup_ids，由面自证判红点名（不改记账行为）。
    by_id = {}
    for fp in files:
        rel = os.path.join("memory", fp.name)
        text = io.open(fp, encoding="utf-8", errors="replace").read()
        for ln, line in enumerate(text.splitlines(), 1):
            m = RE_ITEM.match(line)
            if not m:
                continue
            raw_lines += 1
            body = m.group(2).strip()
            key = re.sub(r"\s+", " ", body[:80])
            # R121（R119b-5）：编号登记必须**早于**去重 continue，且只取**标题首部**编号。
            # r121 两轮实测：① 登记点在 continue 之后 ⇒ 被 80 字前缀去重跳过的副本不登记（漏 5 组）；
            #   ② 用全文 findall 会把正文里**引用的**编号也算成副本（14 组里 9 组是这种误报）。
            # 故正则锚定标题首部（形态见 RE_ID_SUBJECT 定义），并改用 match 取第一个。
            _m_id = RE_ID_SUBJECT.match(body)
            if _m_id:
                # r260：除编号外再记「编号之后的标题主体」，供 face_dup_ids 区分两种同号形态 ——
                #   主体不同 ⇒ 撞号（两条不同条目抢同一个 R 号，L-6 编号命名空间病）；
                #   主体相同 ⇒ 真副本（拆卷留痕却漏勾销，同一笔债被计两次）。
                # 旧实现只比编号，于是把前者也报成「疑似漏勾销致重复计账」，诊断方向是错的
                # （本轮实测三组全是撞号：R249-1 自己写着「原编号 R245-1→R246-1 两度与并行
                # 会话撞号，本轮定为 R249-1」）。记账行为一字不改，只是把话说准。
                by_id.setdefault(_m_id.group(1), []).append(
                    {"file": rel, "line": ln, "checked": m.group(1) == "x",
                     "subject": body[_m_id.end():].strip()[:60]})
            if key in seen:
                # 主壳与分卷可能同条目（拆卷留索引），去重防重复计账；
                # 但**正文不同**就不是同一条目 —— 记账行为不变（防静默改数），面自证判红点名。
                if seen[key] != body:
                    collisions.append({"key": key, "a": seen[key], "b": body})
                continue
            seen[key] = body
            cls, detail = classify_item(body, now_round)
            row = {"file": rel, "line": ln, "priority": "P0" if "【P0" in body else
                   ("P1" if "【P1" in body else ("P2" if "【P2" in body else "未标")),
                   # r48 自抓：owner 必须按**整行全文**判，不能按截断后的 title[:110]——
                   # 路径常出现在 110 字之后，用截断文本判会造假 UNOWNED（首跑即误报 2 条）。
                   "owner": classify_owner(body),
                   "checked": m.group(1) == "x", "class": cls if m.group(1) == " " else "CLOSED",
                   "detail": detail, "title": body[:110]}
            if cls == "OVERDUE" and m.group(1) == " ":
                row["first_seen"] = first_seen(rel, key)
                # W-20 定年面：同一问题问两遍（截断 needle vs 全文 needle），不等即判红
                ok, why = face_dating(row["first_seen"], first_seen(rel, body))
                row["dating_face"] = "OK" if ok else "FAIL"
                if not ok:
                    dating_fails.append({"file": rel, "line": ln, "why": why,
                                         "title": body[:60]})
                    row["dating_face_detail"] = why
            items.append(row)
    dup_ids = []
    for _mid, _locs in sorted(by_id.items()):
        _files = sorted(set(x["file"] for x in _locs))
        if len(_locs) > 1:
            dup_ids.append({"id": _mid, "n": len(_locs), "files": _files,
                            "locs": _locs,
                            "all_checked": all(x["checked"] for x in _locs)})
    face = {"raw_lines": raw_lines, "items_total": len(items), "collisions": collisions,
            "dup_ids": dup_ids,
            "dating_fails": dating_fails,
            "method": "RE_ITEM 逐行计数（独立于去重计入）+ 截断键碰撞比对 + 定年双路取值"}
    return items, face



# ---------------------------------------------------------------- W-3：账龄趋势台账
LEDGER_CLASSES = ("OVERDUE", "ACTIVE", "DECIDED", "UNDATED")   # 必填四态（r39 前既有）
LEDGER_OPTIONAL = ("DEFERRED", "REPEAT")     # 缺省按 0 记；出现则计入自洽
LEDGER_ORIGINS = ("local", "ci")


def head_short():
    return git("rev-parse", "--short", "HEAD").stdout.strip() or "unknown"


def refresh_stale_count():
    """W-38（r56）：本轮有几个棘轮指标的源件已超期。取不到一律 None，**不写 0 冒充健康**。

    两种"取不到"都要显形：① 读不到 ratchet_gate/源件 mtime；② 基线根本没声明预算
    （W-37 之后预算在基线件里，缺位时所有指标都是 UNVERIFIED ⇒ 此时"0 个超期"是假绿）。
    """
    try:
        import ratchet_gate as rg
        rf = rg.refresh_summary()
    except Exception as e:
        print("[REFRESH:UNVERIFIED] 读不到再生面（%s: %s）⇒ 超期数记 None" % (type(e).__name__, e))
        return None
    if rf and all(v[2] is None for v in rf.values()):
        print("[REFRESH:UNVERIFIED] 基线未声明任何预算（W-37 面缺位）⇒ 超期数记 None，不记 0")
        return None
    return sum(1 for v in rf.values() if v[0] == "STALE")


def append_ledger(path, doc, origin="local", head=None):
    """把一次账龄测量**追加**成一行趋势记录；返回写入行数（0 = 被拒写）。

    拒写条件全部 fail-closed（R247：脏数据一旦进趋势线，斜率就成了伪造面）：
      · origin 不在取值域（防"本机记录冒充 CI"）
      · evidence.open_total 不是整数
      · by_class 缺任一态（**不按 0 补齐**：缺态即分类面不完整，正是 r38 首版把 27 条
        漏成 UNDATED 的那类盲区，写进台账会永久掩盖）
      · 四态之和 != open_total（判据漏桶）
    """
    by = doc.get("by_class") or {}
    ev = doc.get("evidence") or {}
    total = ev.get("open_total")
    if origin not in LEDGER_ORIGINS:
        return 0
    if not isinstance(total, int) or isinstance(total, bool):
        return 0
    if any(k not in by for k in LEDGER_CLASSES):
        return 0
    if any(k not in TAXONOMY for k in by):
        return 0                       # 出现未知态 ⇒ 分类面被改过，趋势线拒收
    if sum(by.values()) != total:
        return 0
    row = {"ts": dt.datetime.now().isoformat(timespec="seconds"), "origin": origin,
           "open_total": total, "overdue": by["OVERDUE"], "active": by["ACTIVE"],
           "decided": by["DECIDED"], "undated": by["UNDATED"],
           "deferred": by.get("DEFERRED", 0), "repeat": by.get("REPEAT", 0),
           "coverage_status": (doc.get("coverage") or {}).get("status", "UNVERIFIED"),
           "coverage_prev_overdue": (doc.get("coverage") or {}).get("prev_overdue"),
           "coverage_missing": len((doc.get("coverage") or {}).get("missing") or []),
           # r49 W-20：判据自身健康度也进趋势线 —— 只打印不落账的自证等于半成品（不阻断写入：
           # FAIL 行必须能进台账，趋势线才看得见"哪天判据自己变脏了"）
           "face_status": (doc.get("input_face") or {}).get("status", "UNVERIFIED"),
           "face_red_count": len((doc.get("input_face") or {}).get("red_faces") or []),
           # W-38（r56）：再生超期计数进趋势线 —— 一次性告警看不出斜率，"漏跑探针"必须可追。
           # 取不到就写 None（**不写 0**）：0 会被读成"今天没有一个超期"，那正是 R247 禁的假绿。
           "refresh_stale_count": doc.get("refresh_stale_count"),
           "grace_rounds": doc.get("grace_rounds"), "current_round": doc.get("current_round"),
           "head": head or head_short()}
    io.open(path, "a", encoding="utf-8", newline="").write(
        json.dumps(row, ensure_ascii=False) + chr(10))
    return 1


def coverage_check(cur_round):
    """W-12 接线：拿上一轮证据件的 OVERDUE 清单，逐条查本轮是否真被处理。

    只报告不阻断（r25 用户否决拦任务的闸门）：`[ADJUDICATION:INCOMPLETE n]` 会进 JSON 与终端，
    并把完整性变成趋势线上可追的一列，而不是等下一轮账面爆炸才发现。
    """
    hist = sorted(ROOT.glob("06-benchmark" + os.sep + "debt_aging_r*.json"),
                  key=lambda p: p.stat().st_mtime)
    if len(hist) < 2:
        return {"status": "UNVERIFIED", "prev": None, "prev_overdue": 0, "missing": [],
                "why": "历史证据件不足 2 份，无上一轮可比对（R247 不判绿）"}
    try:
        prev = json.loads(hist[-2].read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {"status": "UNVERIFIED", "prev": hist[-2].name, "prev_overdue": 0, "missing": [],
                "why": "上一轮证据件读不到：%s（不得当作已裁完）" % e}
    byfile = {}
    for row in prev.get("overdue") or []:
        byfile.setdefault(row["file"], []).append(re.sub(r"\s+", " ", row["title"][:40]))
    missing = []
    for f, keys in byfile.items():
        p = ROOT / f
        if not p.is_file():
            continue
        lines = p.read_text(encoding="utf-8", errors="replace").split(chr(10))
        for k in keys:
            if adjudication_gap([k], lines, "r%s" % (cur_round or 0)):
                missing.append({"file": f, "key": k})
    return {"status": "OK" if not missing else "INCOMPLETE", "prev": hist[-2].name,
            "prev_overdue": sum(len(v) for v in byfile.values()), "missing": missing,
            "method": "adjudication_gap(上一轮 overdue[].title 前 40 字, 当前卷文本, 本轮轮号)"}


def main():
    global GRACE_DEFAULT
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--grace", type=int, default=GRACE_DEFAULT)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--ledger", help="趋势台账 jsonl 路径（追加一行；自洽不过则一行都不写）")
    ap.add_argument("--origin", default="local", choices=list(LEDGER_ORIGINS))
    ap.add_argument("--report", help="本轮对标报告路径（W-20 第 4 面：报告新建议须落待办卷）")
    ap.add_argument("--ledger-root", help="待办卷/承接面根目录（默认=本脚本所在仓 ROOT；跨仓喂 report 时指被查仓）")
    args = ap.parse_args()
    if getattr(args, "ledger_root", None):
        global ROOT
        ROOT = Path(args.ledger_root).resolve()  # [R322]
    GRACE_DEFAULT = args.grace

    files = volume_files()
    if not files:
        print("[DEBT:N/A] 取不到 07 待办面（memory/07-next-steps*.md 不存在）—— 禁止判零积压（R247）")
        return 2
    now_round = current_round()
    if now_round is None:
        print("[DEBT:N/A] git log 取不到轮次序列 —— 无法定账龄，禁判绿（R247）")
        return 2

    items, face = scan(files, now_round, args.grace)
    # ---- W-20（r49）：三处截断/降采样的面自证。任一判红 ⇒ 本轮所有"零"都要打折读
    round_tag = round_from_tag()
    f_round = face_round(now_round, round_tag)
    f_dedup = face_dedup(face["raw_lines"], face["items_total"], face["collisions"])
    f_dup = face_dup_ids(face.get("dup_ids") or [])   # R121（R119b-5）
    f_dates = face["dating_fails"]
    f_dating = face_dating_summary(f_dates, sum(1 for r in items if r.get("dating_face")))
    # W-20 第 4 面：本轮报告新立的建议编号 → 待办卷承接对账
    sugg_ids, f_sugg = [], (None, "未传 --report ⇒ 建议面未对照（R247 不判绿）")
    if args.report:
        try:
            rpt = io.open(args.report, encoding="utf-8", errors="replace").read()
            prev = ""
            for hist in sorted(ROOT.glob("06-benchmark" + os.sep + "全量对标报告_r*.md")):
                if os.path.abspath(str(hist)) == os.path.abspath(args.report):
                    continue
                prev += io.open(hist, encoding="utf-8", errors="replace").read()
            prev_ids = set(RE_SUGG_ID.findall(prev))
            sugg_ids = sorted(set(RE_SUGG_ID.findall(rpt)) - prev_ids)
            todo_text = "".join(io.open(f, encoding="utf-8", errors="replace").read() for f in files)
            doc_path = ROOT / "memory" / "AGENTS.md"          # X 编号的承接面（r50 分面修）
            doctrine_text = (io.open(doc_path, encoding="utf-8", errors="replace").read()
                             if doc_path.is_file() else "")
            f_sugg = face_suggestions(sugg_ids, todo_text, doctrine_text)
        except OSError as e:
            f_sugg = (False, "--report 指向的文件读不到：%s（判红，不当作已通过）" % e)
    f_floor = face_floor([os.path.join("memory", f.name) for f in files], prev_scanned_volumes())
    input_face = {"round": {"log": now_round, "tag": round_tag, "ok": f_round[0], "detail": f_round[1]},
                  "floor": {"ok": f_floor[0], "detail": f_floor[1]},
                  "dedup": {"ok": f_dedup[0], "detail": f_dedup[1]},
                  "dup": {"ok": f_dup[0], "detail": f_dup[1]},  # R121（R119b-5）
                  "dating": {"ok": f_dating[0], "detail": f_dating[1], "checked": len(f_dates)},
                  "suggestions": {"ok": f_sugg[0], "detail": f_sugg[1]},
                  "raw_lines": face["raw_lines"], "collisions": face["collisions"]}
    FACE_KEYS = ("round", "floor", "dedup", "dup", "dating", "suggestions")
    face_red = [k for k in FACE_KEYS if input_face[k]["ok"] is False]
    face_unver = [k for k in FACE_KEYS if input_face[k]["ok"] is None]
    input_face["status"] = ("FAIL" if face_red else
                            ("UNVERIFIED" if face_unver else "OK"))
    input_face["red_faces"] = face_red
    input_face["unverified_faces"] = face_unver
    open_items = [r for r in items if r["class"] != "CLOSED"]
    closed = [r for r in items if r["class"] == "CLOSED"]
    by_cls = {c: sum(1 for r in open_items if r["class"] == c) for c in TAXONOMY}
    if sum(by_cls.values()) != len(open_items):
        print("[DEBT:SELF-FAIL] 分类之和 %d != 受检未闭环条目 %d（判据漏桶，X-7）"
              % (sum(by_cls.values()), len(open_items)))
        return 2

    overdue = sorted([r for r in open_items if r["class"] == "OVERDUE"],
                     key=lambda r: -int(re.sub(r"\D", "", r["detail"] or "0") or 0))
    if not args.quiet:
        print("轮号基准 = r%d（取值：git log --format=%%s -40 里**作用域**最大 rNN，"
              "不含「挂账至 rNN」等未来引用）｜tag 锚 = r%s｜受检面 %d 卷"
              % (now_round, round_tag if round_tag is not None else "?", len(files)))
        print("未闭环 %d 条：%s ｜ 已闭环 %d 条"
              % (len(open_items), " / ".join("%s %d" % (c, by_cls[c]) for c in TAXONOMY),
                 len(closed)))
        for r in overdue[:12]:
            print("  OVERDUE %-4s %-11s %s | %s" % (r["priority"], r["detail"],
                                                    r.get("first_seen", "?"), r["title"][:64]))
        print("[DEBT:MEASURED] 宽限 %d 轮｜本尺不阻断（阻断由 ratchet_gate 第 7 指标只降不升承载）" % args.grace)
        # W-20（r49）：判据读到的面必须先自证不是截断/降采样后的局部面
        for k, lbl in (("round", "轮号面(-40 窗口 vs tag 硬锚)"),
                       ("floor", "规模下限面(上轮受检卷须仍在面内)"),
                       ("dedup", "去重面(80 字前缀键)"),
                       ("dup", "同号多副本面(条目编号聚合)"),
                       ("dating", "定年面(70 字 needle)"),
                       ("suggestions", "建议面(报告新建议→待办卷承接)")):
            v = input_face[k]
            print("  %-26s %s ｜ %s" % (lbl, {True: "OK", False: "FAIL", None: "UNVERIFIED"}[v["ok"]],
                                         v["detail"]))
        print("[FACE:%s]%s" % (input_face["status"],
              "" if not face_red else " ← 判红的面上，任何「零」都只适用于被读到的那部分：%s"
              % ", ".join(face_red)))

    cov = coverage_check(now_round)
    print("裁决完整性（W-12）：状态 %s ｜ 上轮 OVERDUE %d 条 → 本轮仍未处理 %d 条%s"
          % (cov["status"], cov["prev_overdue"], len(cov["missing"]),
             "" if not cov["missing"] else " ← " + str([m["key"][:24] for m in cov["missing"][:4]])))
    if cov["status"] == "UNVERIFIED":
        print("[ADJUDICATION:UNVERIFIED] %s" % cov["why"])
    doc = {"schema": "debt-aging-v2",   # v2（r39）新增 DEFERRED 态；v1 历史件按自洽式不变式仍合格
           "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
           "readonly": True, "grace_rounds": args.grace, "current_round": now_round,
           "round_source": "git log --format=%s -40 中**作用域**最大 rNN（未硬编码；排除「挂账至 rNN」等未来轮号引用）",
           "verdict_taxonomy": TAXONOMY + ["CLOSED"],
           "files_scanned": [os.path.join("memory", f.name) for f in files],
           "evidence": {"volumes": len(files), "items_total": len(items),
                        "open_total": len(open_items), "closed_total": len(closed)},
           "by_class": by_cls,
           "overdue": overdue,
           "undated": [{"title": r["title"][:70], "file": r["file"], "line": r["line"]}
                       for r in open_items if r["class"] == "UNDATED"],
           "claims_face": "未闭环积压：REST open_issues_count（含 PR）与 search 纯 issue 面并列；"
                          "workflow 数并给 API 总计面/仓库内面/dynamic 面。r51 起每行带 retrieval",
           "opponents_measured_at": "2026-09-25",
           "opponents": [
               {"repo": "github/spec-kit", "open_issues_pure": 134, "open_issues_incl_pr": 287,
                "workflows": 18, "workflows_listed": 27, "stale_automation": True,
                "oldest_open_issue": "2025-09-25",
                "note": "唯一有到期自动化：Close stale issues and PRs + 6 条 issue 流转 workflow（stale.yml 系仓库自有件）",
                "retrieval": "gh api \"search/issues?q=repo:github/spec-kit+type:issue+state:open&per_page=1\" --jq .total_count ; "
                             "gh api repos/github/spec-kit --jq .open_issues_count ; "
                             "gh api repos/github/spec-kit/actions/workflows --jq '[.workflows[]|select(.path|startswith(\".github/workflows\"))]|length'"},
               {"repo": "obra/superpowers", "open_issues_pure": 143, "open_issues_incl_pr": 402,
                "workflows": 0, "workflows_listed": 2, "stale_automation": False,
                "oldest_open_issue": "2026-01-27",
                "note": "仓库内 0 个 workflow（.github/workflows 实测 404）；listed=2 全为平台 dynamic 件（r50 校正）",
                "retrieval": "gh api \"search/issues?q=repo:obra/superpowers+type:issue+state:open&per_page=1\" --jq .total_count ; "
                             "gh api repos/obra/superpowers --jq .open_issues_count ; "
                             "gh api repos/obra/superpowers/contents/.github/workflows  # 404"},
               {"repo": "anthropics/skills", "open_issues_pure": 368, "open_issues_incl_pr": 1292,
                "workflows": 0, "workflows_listed": 2, "stale_automation": False,
                "oldest_open_issue": "2025-10-16",
                "note": "同上：仓库内 0 个自有 workflow，积压规模最大但无到期治理",
                "retrieval": "gh api \"search/issues?q=repo:anthropics/skills+type:issue+state:open&per_page=1\" --jq .total_count ; "
                             "gh api repos/anthropics/skills --jq .open_issues_count ; "
                             "gh api repos/anthropics/skills/contents/.github/workflows  # 404"},
               {"repo": "addyosmani/agent-skills", "open_issues_pure": 58, "open_issues_incl_pr": 120,
                "workflows": 2, "workflows_listed": 5, "stale_automation": False,
                "oldest_open_issue": "2026-04-04",
                "note": "contents 目录实测 1 件（API 仍报已不存在的 markdownlint.yml）⇒ API 面 ≠ 磁盘面",
                "retrieval": "gh api \"search/issues?q=repo:addyosmani/agent-skills+type:issue+state:open&per_page=1\" --jq .total_count ; "
                             "gh api repos/addyosmani/agent-skills/contents/.github/workflows --jq '.[].name'"},
               {"repo": "pre-commit/pre-commit", "open_issues_pure": 17, "open_issues_incl_pr": 25,
                "workflows": 2, "workflows_listed": 3, "stale_automation": False,
                "oldest_open_issue": "2018-07-02",
                "note": "低积压靠少建待办，最老一条 8 年仍 open（日期已复现）；2 个自有 workflow 均为跨仓 uses: 复用件",
                "retrieval": "gh api \"search/issues?q=repo:pre-commit/pre-commit+type:issue+state:open&per_page=1\" --jq .total_count ; "
                             "gh api repos/pre-commit/pre-commit --jq .open_issues_count ; "
                             "gh api \"search/issues?q=repo:pre-commit/pre-commit+type:issue+state:open&sort=created&order=asc&per_page=1\" --jq '.items[0].created_at'"}],
           "note": "OVERDUE 数 = ratchet_gate 第 7 指标 overdue_debt_items 的唯一取值面"}
    unowned = [{"file": r["file"], "line": r["line"], "title": r["title"][:90]}
               for r in open_items if r.get("owner") == "UNOWNED"]
    print("归属可机检（W-6）：声明归属但**无可解析路径**的条目 %d 条 —— 逐条核实是不是又是我自己的债（r40 D37 同族）"
          % len(unowned))
    doc["coverage"] = cov
    doc["input_face"] = input_face
    doc["evidence"]["raw_item_lines"] = face["raw_lines"]
    doc["unowned_claims"] = unowned
    if args.ledger:
        doc["refresh_stale_count"] = refresh_stale_count()
        wrote = append_ledger(args.ledger, doc, origin=args.origin)
        print("台账 %s → 追加 %d 行（%s）" % (args.ledger, wrote,
              "自洽通过" if wrote else "分类面不完整或之和对不上，拒写"))
        if wrote == 0:
            print("[DEBT:LEDGER-REFUSED] 趋势线只接自洽的测量值（R247）")
    # W-34 顺序修正（r53 实测）：句柄必须在台账写入**之后**再建，否则同一次运行里
    # by_class 已经是新值、句柄却解出上一行（本轮实测 84 vs 82 的错位）。
    # r55 补齐另一半：句柄的 artifact 必须指向**本次真正写过的那本台账**。原先恒取默认
    # `06-benchmark/debt_runs.jsonl`，于是夹具那种「写临时台账」的运行会拿临时测量值去比
    # 真台账末行 ⇒ 同一轮里账面从 91 涨到 92 时，一致性自检反过来说我漂移（判据自己读错面）。
    doc["handles"] = make_handles(doc, ledger_rel=(args.ledger or "06-benchmark/debt_runs.jsonl"))
    if not args.quiet:
        got = {k: resolve_handle(v) for k, v in doc["handles"].items()}
        mismatch = [k for k in ("overdue", "open_total", "decided")
                    if k in got and got[k] is not None
                    and got[k] != (doc["by_class"].get(k.upper()) if k != "open_total"
                                   else doc["evidence"]["open_total"])]
        print("可引用句柄（报告写句柄别抄值；解不出即为 None）：%s%s"
              % (" ".join("%s=%s" % (k, got[k]) for k in
                           ("overdue", "open_total", "decided", "ledger_rows")),
                 "" if not mismatch else "  [HANDLE:DRIFT] 与本次测量不一致 %s" % mismatch))
        if mismatch:
            doc["handles_drift"] = mismatch
    if args.json:
        io.open(args.json, "w", encoding="utf-8", newline="").write(
            json.dumps(doc, ensure_ascii=False, indent=1))
        print("JSON -> %s" % args.json)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    raise SystemExit(main())
