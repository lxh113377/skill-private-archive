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
TAXONOMY = ["OVERDUE", "ACTIVE", "DECIDED", "UNDATED", "DEFERRED", "REPEAT"]   # r39 加 DEFERRED（看得见但不到期，不得并入 DECIDED）；r43 加 REPEAT（第 31 行说明）
GRACE_DEFAULT = 2
# r42 D49 / r43 W-11b：宽限期按优先级分档。统一 2 轮会把 P2 长期项与 P0 同罪判红，
# 噪音反而稀释 P0 的紧迫感（活证据：本仓 W-2 自己在 r42 被判成 OVERDUE）。
GRACE_BY_PRIORITY = {"P0": 2, "P1": 4, "P2": 8, "UNMARKED": 2}
RE_PRIORITY = re.compile(r"【\s*(P[0-2])")
# r42 D48 / r43 W-11a：同一条目被改期 >= 2 次 ⇒ 判 REPEAT 并强制升级，
# 堵死「到期就再往后挂一轮」的延期 treadmill（账面一路 DEFERRED，趋势线看不出恶化）。
RE_DEFERRAL = re.compile(r"挂账至\s*r\d{1,3}")
REPEAT_AFTER = 2
RE_ITEM = re.compile(r"^\s*-\s\[( |x)\]\s+(.+)$")
RE_ROUND_DECL = re.compile(r"(?:r(\d{1,3})\s*(?:登记|立|新增|补记|更新|收尾)|第\s*(\d{1,3})\s*轮|"
                           r"挂账\s*(\d{1,2})\s*轮)")
RE_DECIDED = re.compile(r"裁决\s*=\s*(执行|降级|作废|保留)|挂账至\s*r(\d{1,3})")
# r49 根因修（第 2 形态）：裁决标记是 `【rNN 裁决=<头部>｜原因】`，而**原因里允许引用旧标记原文**
# （本轮就在 W-14 上写了「r46 却在本条上写了『挂账至 r49』」）。全文 search 的 last-wins 会被
# 引号内容劫持 ⇒ 终局裁决被回判成"过期挂账"，凭空造一条 OVERDUE。
# 判据口径：只认**最后一个标记的头部**（第一个 ｜/】 之前），原因体一律不参与判定。
RE_MARK_HEAD = re.compile(r"【\s*r(\d{1,3})\s*裁决\s*=\s*([^｜】]*)")


def parse_last_verdict(text):
    """返回 (kind, arg)：kind ∈ "FINAL"/"DEFER"/None；FINAL 的 arg 是裁决词，DEFER 的 arg 是目标轮 int。

    有 `【rNN 裁决=` 标记时**只看最后一个标记的头部**；一个都没有才回退到全文扁平匹配
    （兼容层a 夹具直接喂无括号裸文本）。头部取不到合法取值 ⇒ 视为未裁（X-10：自造措辞
    不算裁决，与 r38「部分作废不在取值域即照判 OVERDUE」同口径）。
    """
    heads = list(RE_MARK_HEAD.finditer(text or ""))
    if heads:
        head = heads[-1].group(2).strip()
        m = re.match(r"(执行|降级|作废|保留)", head)
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


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT)] + list(args),
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def current_round():
    """本轮轮号 = 近期提交主题里出现过的最大 rNN（取值命令随结果走，不硬编码）。"""
    out = git("log", "--format=%s", "-40").stdout
    hits = [int(m.group(1)) for m in RE_R_IN_SUBJECT.finditer(out)]
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
    """真实延期次数 = 头部为「挂账至 rNN」的标记数（原因体里引用的旧标记原文不计）。

    与 parse_last_verdict 同一口径，否则 r49 这种"在原因里引用『挂账至 r49』"会把
    REPEAT 计数（第 9 指标）虚增 —— 那正是 X-17 禁止的"把延期次数当成绩"的反向形态。
    """
    heads = [h.group(2).strip() for h in RE_MARK_HEAD.finditer(text or "")]
    if heads:
        return sum(1 for h in heads if re.match(r"挂账至\s*r\d{1,3}", h))
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
    grace = GRACE_BY_PRIORITY.get((RE_PRIORITY.search(text) or ["", "UNMARKED"])[1], GRACE_DEFAULT)
    origin, held = None, None
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
        bare = re.search(r"\br(\d{1,3})\b", text)
        if bare:
            age = now_round - int(bare.group(1))
            return (("OVERDUE" if age > grace else "ACTIVE"),
                    "账龄 %d 轮 / 宽限 %d（回落：正文裸 rNN=r%s）" % (age, grace, bare.group(1)))
        return ("UNDATED", "取不到来源轮次")
    return (("OVERDUE" if age > grace else "ACTIVE"), "账龄 %d 轮 / 宽限 %d" % (age, grace))


RE_SUGG_ID = re.compile(r"\b([WXMH]-\d{1,2})\b")


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
    face = {"raw_lines": raw_lines, "items_total": len(items), "collisions": collisions,
            "dating_fails": dating_fails,
            "method": "RE_ITEM 逐行计数（独立于去重计入）+ 截断键碰撞比对 + 定年双路取值"}
    return items, face



# ---------------------------------------------------------------- W-3：账龄趋势台账
LEDGER_CLASSES = ("OVERDUE", "ACTIVE", "DECIDED", "UNDATED")   # 必填四态（r39 前既有）
LEDGER_OPTIONAL = ("DEFERRED", "REPEAT")     # 缺省按 0 记；出现则计入自洽
LEDGER_ORIGINS = ("local", "ci")


def head_short():
    return git("rev-parse", "--short", "HEAD").stdout.strip() or "unknown"


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
    args = ap.parse_args()
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
                  "dating": {"ok": f_dating[0], "detail": f_dating[1], "checked": len(f_dates)},
                  "suggestions": {"ok": f_sugg[0], "detail": f_sugg[1]},
                  "raw_lines": face["raw_lines"], "collisions": face["collisions"]}
    FACE_KEYS = ("round", "floor", "dedup", "dating", "suggestions")
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
        print("轮号基准 = r%d（取值：git log --format=%%s -40 里的最大 rNN）｜tag 锚 = r%s｜受检面 %d 卷"
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
           "round_source": "git log --format=%s -40 中最大 rNN（未硬编码）",
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
        wrote = append_ledger(args.ledger, doc, origin=args.origin)
        print("台账 %s → 追加 %d 行（%s）" % (args.ledger, wrote,
              "自洽通过" if wrote else "分类面不完整或之和对不上，拒写"))
        if wrote == 0:
            print("[DEBT:LEDGER-REFUSED] 趋势线只接自洽的测量值（R247）")
    # W-34 顺序修正（r53 实测）：句柄必须在台账写入**之后**再建，否则同一次运行里
    # by_class 已经是新值、句柄却解出上一行（本轮实测 84 vs 82 的错位）。
    doc["handles"] = make_handles(doc)
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
