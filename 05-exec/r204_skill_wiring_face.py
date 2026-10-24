# -*- coding: utf-8 -*-
"""r204_skill_wiring_face.py — 自建 skill 的「分卷是否真被收录」面（第 86 门）。

存在理由（r204 一手）：本仓第 78 门（fixture_wiring_face）守的是「05-exec 夹具写了没人跑」，
但 SKILL 侧同型失效没有常驻看守。本会话给 win-toolchain-pitfalls 加了 R804 分卷
powershell-cli-silent-failures.md，它此刻就是「无指针孤儿卷」（= 挂在台账 R201-2 的欠账）——
我是手工扫才发现的。知识写进 skill 但没有任何 SKILL.md/A-memory-start 指针指向 = Agent
永远不会加载到 = 等于没写。把这条手工扫描固化成每轮可复算的判据。

关键精度（两次自抓，写进实现）：
  ① 朴素「文件名在不在 SKILL.md 里」判据 → 83 个「孤儿」。错：分卷可被父分卷间接引用
    （part7.md 里写 part7.part1.md），必须 BFS 链式可达 ⇒ 真孤儿降到 35（全表）/ 10（自建口径）。
  ② 自建名正则 ^[A-Za-z0-9] 漏掉中文名 skill（如「天眼一下」）⇒ 分母 76 而非权威 77。
    改：以「磁盘目录真实存在」为准（os.path.isdir），不靠字符集白名单。

权威边界：只读 00-scope 自建清单（HIGH+MID 口径，AGENTS.md 禁换分母）与 D:/global_skills
的 SKILL.md/references，不改任何受管根。

为什么判红用「基线只拦增量」（同第 78 门）：现存 10 个孤儿里只有 1 个是我本轮的，其余 9 个
属并行会话/既有，按 R269 不代裁；把 9 条历史债判成永久红会淹没「新加了个没人收的卷」这个信号。

portable=False：判据读 D:/global_skills（本机绝对路径），CI 的 Linux runner 上没有这棵树
⇒ 必须标本机专属并写明原因，否则 CI 假红。

三态：[SKILLWIRING:PASS]（无新增孤儿）/ rc=1（有新增孤儿）/ rc=2 UNVERIFIED（基线件缺失或
自建清单读不到，不得按全绿记，R247）。
"""
import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SK = "D:/global_skills"
BTL = chr(96)
TOKEN = "[SKILLWIRING:PASS]"
REF_RE = re.compile(r"([\w.\-\u4e00-\u9fff]+\.md)")
ROSTER = os.path.join(ROOT, "00-scope", "自建skill清单.md")
BASELINE = os.path.join(ROOT, "06-benchmark", "skill_wiring_baseline.json")


def own_skills():
    """从自建清单 HIGH+MID 分节解析名，且必须在磁盘真实存在（不靠字符集白名单）。"""
    if not os.path.isfile(ROSTER):
        return None
    tier, out = None, set()
    for l in io.open(ROSTER, encoding="utf-8", errors="replace"):
        s = l.strip()
        m = re.match(r"^##+\s*(HIGH|MID|LOW|EXCLUDE)[（(]\d+[）)]", s)
        if m:
            tier = m.group(1)
            continue
        if s.startswith("##"):
            tier = None
            continue
        if tier in ("HIGH", "MID") and s.startswith("|") and "---" not in s \
                and s.count(BTL) >= 2:
            nm = s.split(BTL)[1].strip()
            if nm and os.path.isdir(os.path.join(SK, nm)):
                out.add(nm)
    return out


def global_pool():
    """A-memory-start 全量文本：跨 skill 引用也算可达（cli-invocation 就靠它非孤儿）。"""
    buf = []
    for sub in ("references", "."):
        dd = os.path.join(SK, "A-memory-start", sub)
        if os.path.isdir(dd):
            for f in os.listdir(dd):
                if f.endswith(".md"):
                    try:
                        buf.append(io.open(os.path.join(dd, f), encoding="utf-8",
                                           errors="replace").read())
                    except OSError:
                        pass
    return "\n".join(buf)


def reachable(skill):
    """从该 skill 的 SKILL.md 出发，沿 references 内文件名引用做 BFS，返回可达文件名集合。"""
    rp = os.path.join(SK, skill, "references")
    skmd = os.path.join(SK, skill, "SKILL.md")
    if not os.path.isdir(rp) or not os.path.isfile(skmd):
        return set()
    files = {f for f in os.listdir(rp) if f.endswith(".md")}
    reached = set()
    frontier = [io.open(skmd, encoding="utf-8", errors="replace").read()]
    guard = 0
    while frontier and guard < 4000:
        guard += 1
        txt = frontier.pop()
        for m in REF_RE.finditer(txt):
            fn = m.group(1)
            if fn in files and fn not in reached:
                reached.add(fn)
                try:
                    frontier.append(io.open(os.path.join(rp, fn), encoding="utf-8",
                                            errors="replace").read())
                except OSError:
                    pass
    return reached


def build():
    own = own_skills()
    if own is None:
        return None
    pool = global_pool()
    orphans, total = [], 0
    for skill in sorted(own):
        rp = os.path.join(SK, skill, "references")
        if not os.path.isdir(rp):
            continue
        files = sorted(f for f in os.listdir(rp) if f.endswith(".md"))
        if not files:
            continue
        reach = reachable(skill)
        for fn in files:
            total += 1
            stem = fn[:-3]
            if fn in reach:
                continue
            if fn in pool or stem in pool:
                continue
            orphans.append("%s/%s" % (skill, fn))
    return {"own_count": len(own), "refs_total": total, "orphans": orphans}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args(argv)
    r = build()
    if r is None:
        print("[SKILLWIRING:UNVERIFIED] 自建清单读不到 ⇒ 分母不明，不得按全绿记（R247）")
        return 2
    print("=== 自建 skill 分卷收录面（r204·本机专属）===")
    print("  自建口径(HIGH+MID)=%d 名，其中有 references 的分卷共 %d 个，孤儿 %d 个"
          % (r["own_count"], r["refs_total"], len(r["orphans"])))
    if not os.path.isfile(BASELINE):
        print("  [SKILLWIRING:UNVERIFIED] 基线件缺失 ⇒ 无法判增量（不得按全绿记，R247）")
        return 2
    base = set(json.load(io.open(BASELINE, encoding="utf-8")).get("known_orphans") or [])
    cur = set(r["orphans"])
    new_ones = sorted(cur - base)
    known = sorted(cur & base)
    healed = sorted(base - cur)
    for h in healed:
        print("  [SKILLWIRING:HEALED] %s 已补指针（基线应同步收缩）" % h)
    for k in known:
        print("  [SKILLWIRING:KNOWN] %s 历史孤儿（在基线内，待补指针）" % k)
    for n in new_ones:
        print("  [SKILLWIRING:ORPHAN] %s 新增无指针分卷：SKILL.md 与 A-memory-start 池都提不到"
              % n)
    if args.out:
        with io.open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"schema": "skill-wiring-v1", "readonly": True,
                       "own_count": r["own_count"], "refs_total": r["refs_total"],
                       "orphans": r["orphans"], "baseline": sorted(base),
                       "new_orphans": new_ones,
                       "note": ("分卷可达=BFS 链式引用(父引子)+跨skill全局池; 只拦增量。"
                                "孤儿分卷=写了没人读=等于没写。"),
                       "provenance_cmd":
                       "python 05-exec/r204_skill_wiring_face.py --json <件>"},
                      fh, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.out)
    if new_ones:
        return 1
    print("  %s 无新增无指针分卷（历史 %d 条在基线内，只准减不准增）" % (TOKEN, len(known)))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
