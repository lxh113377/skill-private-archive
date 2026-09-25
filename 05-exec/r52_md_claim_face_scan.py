# -*- coding: utf-8 -*-
r"""r52_md_claim_face_scan.py — W-30：Markdown 引用面的数字是否自带取值途径（只读统计器）。

为什么要有它（r51 实测，不是假想）：
  `inv_opponent_claims_have_retrieval` 只管住 **JSON 取证件**；而对外真正被读的是
  `06-benchmark/*.md` 报告与 `comparison.md` —— 那里的数字一旦没有命令可追，
  就退化成"上一轮我说过"的回声（r38 的 open issues 就是这样虚高 1.5–3.5 倍跑了 12 轮）。

口径是抽样定下来的，不是拍脑袋（r52 实测）：
  · ±2 行窗口下敞口 60.4%（951 处声明 / 574 无命令）—— 随机 14 条判读显示大头是误伤：
    `82%`/`100%`/`22 条` 这类数字的取值命令写在**同节表头或段末**（距声明 3–12 行）；
  · 故窗口放宽到同节 ±12 行；
  · 且**历史报告（r < LIVE_FROM）只登记不回改**（R241），敞口分列成 `uncited`（全量）与
    `live_uncited`（可整改面）—— 只有后者才有资格决定是否接阻断。

不阻断（守 r25 用户否决"拦任务的闸门"）：默认 exit 0，只有 `--strict` 才让 EXPOSED 返回非零。
"""

import argparse
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

UNIT = r"(?:条|份|例|组|行|B|倍|%|个)"
CLAIM_RE = re.compile(r"(\d{1,4}(?:\.\d{1,2})?(?:,\d{3})*\s?" + UNIT + r")")
CMD_RE = re.compile(r"(python\s|gh\s+api\s|git\s|grep\s|curl\s|comm\s|ls\s|wc\s|取值|命令：)")
FENCE = re.compile(r"^\s*```")
EXCLUDE = re.compile(r"(\d{4}-\d{2}-\d{2}|\br\d{1,3}\b|[Vv]\d+(\.\d+){1,3}|P[0-2]\s|≤\s?\d+[KM]B)")
WINDOW = 12          # 同节窗口（抽样实测值）
LIVE_FROM = 51       # r51 起为可整改面；更早的报告属历史留痕（R241 只登记不回改）
LIVE_FROM_DATE = "2026-09-25"     # 无 rNN 的件按名字里的日期兜底（防"未知即当轮"的误判）
STATUS = ("PASS", "EXPOSED", "UNVERIFIED")


def _round_of(name):
    m = re.search(r"_r(\d{1,3})", name)
    return int(m.group(1)) if m else None


def is_live(name, path=None):
    """可整改面判定：轮次号 → 名字里的日期 → 文件 mtime 日期（三级兜底）。

    第三级是必需的而非可省：`comparison.md` 每轮被追加，却既无 rNN 也无日期；
    若一律归历史面，就等于**允许我用"文件名没日期"来躲开自己刚写下的数字**。
    未知仍取保守方向：连 mtime 都拿不到 ⇒ 归历史（不冒充可整改，也不冒充已核验）。
    """
    r = _round_of(name)
    if r is not None:
        return r >= LIVE_FROM
    d = re.search(r"(20\d{2}-\d{2}-\d{2})", name)
    if d:
        return d.group(1) >= LIVE_FROM_DATE
    try:
        if path is None:
            return False
        mt = datetime.fromtimestamp(Path(str(path)).stat().st_mtime)
        return mt.strftime("%Y-%m-%d") >= LIVE_FROM_DATE
    except (OSError, ValueError):
        return False


def find_claims(text):
    """返回 [{"line": n, "token": "13 条"}] —— 逐行找"像测量结果"的数字，围栏内与排除形态不算。"""
    out = []
    in_fence = False
    for n, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.lstrip().startswith("#"):
            continue                      # 标题行不是测量陈述（r52 实测：报告 H1 里的"3.5 倍"被误判成声明）
        body = re.sub(r"`[^`]*`", "", line)          # 反引号内是命令/字面量，不是声明
        for m in CLAIM_RE.finditer(body):
            tok = m.group(1).strip()
            seg = body[max(0, m.start() - 12):m.end() + 6]
            if EXCLUDE.search(seg) or EXCLUDE.search(tok):
                continue
            out.append({"line": n, "token": tok})
    return out


def has_command_nearby(line_text, idx, following, window=None):
    """本行 ±window 内出现取值途径 ⇒ 视为已自证（报告排版常态是命令写在表头/段末）。"""
    w = WINDOW if window is None else window
    allc = _CTX.get("lines") or []
    i = idx
    return any(CMD_RE.search(x or "") for x in allc[max(0, i - w):i] + [line_text] + list(following)[:w])


_CTX = {"lines": []}


def summarize(items):
    """三态汇总。零命中 ⇒ UNVERIFIED（R247：没抓到不等于没有）。"""
    claims = len(items)
    uncited = [x for x in items if not x.get("has_cmd")]
    if claims == 0:
        return {"claims": 0, "uncited": 0, "status": "UNVERIFIED", "uncited_list": [],
                "why": "引用面零命中 ⇒ 判据未行使（不判绿，也不判红）"}
    return {"claims": claims, "uncited": len(uncited),
            "status": "PASS" if not uncited else "EXPOSED",
            "uncited_list": uncited}


def scan_files(paths):
    items = []
    for p in paths:
        try:
            lines = io.open(p, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            continue
        _CTX["lines"] = lines
        hist = not is_live(p.name, p)
        for c in find_claims("\n".join(lines)):
            n = c["line"]
            c["file"] = p.name
            c["has_cmd"] = has_command_nearby(lines[n - 1], n - 1, lines[n:n + WINDOW])
            c["historical"] = hist
            items.append(c)
    s = summarize(items)
    live = [x for x in items if not x.get("historical")]
    s.update({"files": len(paths),
              "live_claims": len(live),
              "live_uncited": sum(1 for x in live if not x["has_cmd"]),
              "historical_claims": len(items) - len(live),
              "window_lines": WINDOW, "live_from_round": LIVE_FROM})
    return s


def main():
    ap = argparse.ArgumentParser(description="Markdown 引用面数字自证统计（只读，默认不阻断）")
    ap.add_argument("--glob", default="06-benchmark/*.md")
    ap.add_argument("--json", help="写统计证据件")
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--strict", action="store_true", help="EXPOSED 时返回非零（默认不阻断）")
    args = ap.parse_args()
    files = sorted(ROOT.glob(args.glob))
    if not files:
        print("[MDCLAIM:N/A] 引用面取不到文件（%s）—— 禁判零敞口（R247）" % args.glob)
        return 2
    res = scan_files(files)
    res.update({"schema": "md-claim-face-v1", "generated_at": datetime.now().isoformat(timespec="seconds"),
                "readonly": True, "scope": args.glob,
                "rule": "数字（条/份/例/组/行/B/倍/百分比/个）须在同节 ±" + str(WINDOW) + " 行内带取值途径",
                "note": "默认只报告不阻断（r25 否决）；接线判据只看 live_uncited（历史面按 R241 不回改）"})
    print("引用面 %d 份 md ｜ 数字声明 %d 处 ｜ 无取值途径 %d 处（占比 %.1f%%）"
          % (res["files"], res["claims"], res["uncited"],
             100.0 * res["uncited"] / res["claims"] if res["claims"] else 0))
    print("  分面：可整改面（r≥%d）声明 %d 处 / 敞口 %d 处 ｜ 历史面 %d 处（只登记，R241）"
          % (LIVE_FROM, res["live_claims"], res["live_uncited"], res["historical_claims"]))
    for x in res["uncited_list"][:args.top]:
        print("  %-52s L%-4d %s%s" % (x["file"][:52], x["line"], x["token"],
                                      "" if x.get("historical") else "  <== 可整改"))
    if res["uncited"] > args.top:
        print("  …另有 %d 处（--top 调大或读 --json 件）" % (res["uncited"] - args.top))
    live_status = ("UNVERIFIED" if not res["live_claims"]
                   else ("PASS" if not res["live_uncited"] else "EXPOSED"))
    print("[MDCLAIM:%s]（接线判据取可整改面口径，不取全量）" % live_status)
    if args.json:
        res["live_status"] = live_status
        io.open(args.json, "w", encoding="utf-8", newline="").write(
            json.dumps(res, ensure_ascii=False, indent=1))
        print("JSON -> %s" % args.json)
    return 1 if (args.strict and live_status == "EXPOSED") else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    raise SystemExit(main())
