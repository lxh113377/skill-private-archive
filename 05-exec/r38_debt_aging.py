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
TAXONOMY = ["OVERDUE", "ACTIVE", "DECIDED", "UNDATED", "DEFERRED"]   # r39：DEFERRED = 挂账至未来轮，是"看得见但不到期"的第四种状态，不得并入 DECIDED
GRACE_DEFAULT = 2
RE_ITEM = re.compile(r"^\s*-\s\[( |x)\]\s+(.+)$")
RE_ROUND_DECL = re.compile(r"(?:r(\d{1,3})\s*(?:登记|立|新增|补记|更新|收尾)|第\s*(\d{1,3})\s*轮|"
                           r"挂账\s*(\d{1,2})\s*轮)")
RE_DECIDED = re.compile(r"裁决\s*=\s*(执行|降级|作废|保留)|挂账至\s*r(\d{1,3})")
RE_R_IN_SUBJECT = re.compile(r"\br(\d{1,3})\b")


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT)] + list(args),
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def current_round():
    """本轮轮号 = 近期提交主题里出现过的最大 rNN（取值命令随结果走，不硬编码）。"""
    out = git("log", "--format=%s", "-40").stdout
    hits = [int(m.group(1)) for m in RE_R_IN_SUBJECT.finditer(out)]
    return max(hits) if hits else None


def volume_files():
    """P0 唯一真相源 = 主壳；分卷里也有在途待办，一并按同一判据计（防"只量主壳"造成覆盖面虚高）。"""
    return sorted(ROOT.glob("memory/07-next-steps*.md"))


def first_seen(rel_path, needle):
    r = git("log", "--format=%ad", "--date=short", "-S", needle[:70], "--", rel_path)
    dates = [d for d in r.stdout.split() if re.match(r"^\d{4}-\d{2}-\d{2}$", d)]
    return dates[-1] if dates else None


def classify_item(text, now_round):
    """返回 (cls, detail) —— 单一条目的判定，供层a 夹具直接调用。"""
    dec = RE_DECIDED.search(text)
    if dec:
        if dec.group(2):
            tgt = int(dec.group(2))
            # r39 W-0：延期不是终局。目标轮未到 → DEFERRED（单列，趋势线可见）；
            # 已到/已过 → 重新判 OVERDUE（到期追讨），防"挂账至 rNN"变成永久免检通道。
            if tgt > now_round:
                return ("DEFERRED", "挂账至 r%d（尚余 %d 轮）" % (tgt, tgt - now_round))
            return ("OVERDUE", "挂账目标 r%d 已到期（本轮 r%d）" % (tgt, now_round))
        return ("DECIDED", "裁决=" + dec.group(1))
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
            return (("OVERDUE" if age > GRACE_DEFAULT else "ACTIVE"),
                    "账龄 %d 轮（回落：正文首个裸 rNN=r%s）" % (age, bare.group(1)))
        return ("UNDATED", "取不到来源轮次")
    return (("OVERDUE" if age > GRACE_DEFAULT else "ACTIVE"), "账龄 %d 轮" % age)


def scan(files, now_round, grace):
    global GRACE_DEFAULT
    items, seen_ids = [], set()
    for fp in files:
        rel = os.path.join("memory", fp.name)
        text = io.open(fp, encoding="utf-8", errors="replace").read()
        for ln, line in enumerate(text.splitlines(), 1):
            m = RE_ITEM.match(line)
            if not m:
                continue
            body = m.group(2).strip()
            key = re.sub(r"\s+", " ", body[:80])
            if key in seen_ids:
                continue          # 主壳与分卷可能同条目（拆卷留索引），去重防重复计账
            seen_ids.add(key)
            cls, detail = classify_item(body, now_round)
            row = {"file": rel, "line": ln, "priority": "P0" if "【P0" in body else
                   ("P1" if "【P1" in body else ("P2" if "【P2" in body else "未标")),
                   "checked": m.group(1) == "x", "class": cls if m.group(1) == " " else "CLOSED",
                   "detail": detail, "title": body[:110]}
            if cls == "OVERDUE" and m.group(1) == " ":
                row["first_seen"] = first_seen(rel, key)
            items.append(row)
    return items


# ---------------------------------------------------------------- W-3：账龄趋势台账
LEDGER_CLASSES = ("OVERDUE", "ACTIVE", "DECIDED", "UNDATED")   # 必填四态（r39 前既有）
LEDGER_OPTIONAL = ("DEFERRED",)              # 缺省按 0 记；出现则计入自洽
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
           "deferred": by.get("DEFERRED", 0),
           "grace_rounds": doc.get("grace_rounds"), "current_round": doc.get("current_round"),
           "head": head or head_short()}
    io.open(path, "a", encoding="utf-8", newline="").write(
        json.dumps(row, ensure_ascii=False) + chr(10))
    return 1


def main():
    global GRACE_DEFAULT
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--grace", type=int, default=GRACE_DEFAULT)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--ledger", help="趋势台账 jsonl 路径（追加一行；自洽不过则一行都不写）")
    ap.add_argument("--origin", default="local", choices=list(LEDGER_ORIGINS))
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

    items = scan(files, now_round, args.grace)
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
        print("轮号基准 = r%d（取值：git log --format=%%s -40 里的最大 rNN）｜受检面 %d 卷"
              % (now_round, len(files)))
        print("未闭环 %d 条：%s ｜ 已闭环 %d 条"
              % (len(open_items), " / ".join("%s %d" % (c, by_cls[c]) for c in TAXONOMY),
                 len(closed)))
        for r in overdue[:12]:
            print("  OVERDUE %-4s %-11s %s | %s" % (r["priority"], r["detail"],
                                                    r.get("first_seen", "?"), r["title"][:64]))
        print("[DEBT:MEASURED] 宽限 %d 轮｜本尺不阻断（阻断由 ratchet_gate 第 7 指标只降不升承载）" % args.grace)

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
           "opponents_measured_at": "2026-09-25",
           "opponents": [
               {"repo": "github/spec-kit", "open_issues": 287, "workflows": 27,
                "stale_automation": True, "oldest_open_issue": "2025-09-25",
                "note": "唯一有到期自动化：Close stale issues and PRs + 6 条 issue 流转 workflow"},
               {"repo": "obra/superpowers", "open_issues": 401, "workflows": 2,
                "stale_automation": False, "oldest_open_issue": "2026-01-27"},
               {"repo": "anthropics/skills", "open_issues": 1290, "workflows": 2,
                "stale_automation": False, "oldest_open_issue": "2025-10-16"},
               {"repo": "addyosmani/agent-skills", "open_issues": 118, "workflows": 5,
                "stale_automation": False, "oldest_open_issue": "2026-04-04"},
               {"repo": "pre-commit/pre-commit", "open_issues": 25, "workflows": 3,
                "stale_automation": False, "oldest_open_issue": "2018-07-02",
                "note": "低积压靠少建待办，最老一条 8 年仍 open —— 到期治理同样缺失"}],
           "note": "OVERDUE 数 = ratchet_gate 第 7 指标 overdue_debt_items 的唯一取值面"}
    if args.ledger:
        wrote = append_ledger(args.ledger, doc, origin=args.origin)
        print("台账 %s → 追加 %d 行（%s）" % (args.ledger, wrote,
              "自洽通过" if wrote else "分类面不完整或之和对不上，拒写"))
        if wrote == 0:
            print("[DEBT:LEDGER-REFUSED] 趋势线只接自洽的测量值（R247）")
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
