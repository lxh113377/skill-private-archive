# -*- coding: utf-8 -*-
r"""r217_miss_migration.py — REAL_MISS 跨轮逐条状态迁移账（常驻判据，防「改善」由挪账/缩分母/删题面造出）。

存在理由（r217 一手，我自己踩点踩出来的）：
  需求 6 的口径 B 靠「REAL_MISS 12→7（−41.7%）」成立。本轮我用一次性脚本逐条比对了两份
  route_miss_attr 件，证明「零条 REAL_MISS→STALE_EXPECT（未挪账）、n 291→291（未缩分母）」。
  但那次自查本身不可复算：全仓没有任何件跨轮比较这两份产物（git grep STALE_EXPECT 05-exec 只命中
  r117 的单轮归因与 r113 的步名）。于是「−41.7%」与前几轮同类数字一样，是一句没人复跑就失效的结论
  （R183-1 同族：一次性脚本产出的结论不可复算）。本件把它钉成每轮/每季都能重跑的判据。

防的五件事（任一发生即「改善」是假的）：
  M1 挪账     baseline 的 REAL_MISS 在现轮被改判 STALE_EXPECT（真错重贴成「题面过期」而消失）；
  M1b 转不可判 被改判 UNDECIDABLE / UNREGISTERED（同样退出改进靶面，r117 口径里只有 REAL_MISS 可作靶子）；
  M2 缩分母   现轮题面数 n 变小（题被删了而不是被打对了）；
  M3 假消失   baseline 某条不再出现，且该 query 已不在题集里（靠删题面「修好」）；
  M4 分母     同一状态内 query|expected 重复 ⇒ 去重后键数 < 原始行数（枚举器分母静默缩小，X-24 型；
            首版此处写的是「分类相加 != 基线条数」，但五类互斥划分恒相等 ⇒ 装饰性判据，r217 改为可触发形态）；
  M5 自洽     face.real_n 与 rows 逐条计数不符（rows 被截断而 face 仍报旧数）。

三态（禁静默）：CLEAN（rc=0）/ RED（rc=1，真问题）/ UNVERIFIED（rc=2，输入面不可用，禁读成绿）。

口径红线：
  · 不重跑评分：两份件均由 r117_route_miss_attr.py 产出（上游 = 焚诀 eval 权威件，只读）；
  · 字段名一律现读（face.n / hits / real_n；rows[].query / expected / state），禁凭记忆写键名
    —— 本仓 r216 一手：我把 provenance 件字段写成 authority_n（实为 authority_skill_n）而 KeyError；
  · r117 的 rows 只含 miss 行（HIT 不入 rows）⇒ baseline 某行在现轮 rows 消失有两种含义
    （修好了 / 题面被删），必须用题集区分，禁直接当「修好」（这就是本件读 layered_testset.json 的原因）。

用法：
  python 05-exec/r217_miss_migration.py [--baseline 件] [--current 件] [--json 件] [--quiet]
  python 05-exec/r217_miss_migration.py --selftest
退出码：0 未见造假 / 1 红线破（真问题）/ 2 输入面不可用。
"""
import argparse
import glob
import io
import json
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")
EVAL = r"C:\Users\37533\Desktop\workspace\焚诀\eval"
TESTSET = os.path.join(EVAL, "layered_testset.json")
TOK_CLEAN = "[MIGRATION:CLEAN]"
TOK_RED = "[MIGRATION:RED]"
TOK_UNV = "[MIGRATION:UNVERIFIED]"
OTHER_STATES = ("UNDECIDABLE", "UNREGISTERED")


def read_json(path):
    try:
        return json.loads(io.open(path, encoding="utf-8-sig", errors="replace").read())
    except (OSError, ValueError):
        return None


def key_of(row):
    # 分隔符用 chr(1)：query 文本里可能出现竖线，字面分隔符会撞键；
    # 且本仓 r211 一手 —— 反斜杠转义会被外层模板吃掉，故不用转义写法。
    return (row.get("query") or "") + chr(1) + (row.get("expected") or "")


def rows_by_state(doc, state):
    out = {}
    for r in (doc or {}).get("rows") or []:
        if r.get("state") == state:
            out[key_of(r)] = r
    return out


def raw_state_counts(doc):
    """各状态的**原始行数**（不去重）。与 rows_by_state 的键数比对即 M4。"""
    c = {}
    for r in (doc or {}).get("rows") or []:
        st = r.get("state")
        c[st] = c.get(st, 0) + 1
    return c


def face_val(doc, name):
    v = ((doc or {}).get("face") or {}).get(name)
    return v if isinstance(v, int) and not isinstance(v, bool) else None


def testset_queries():
    """题集全部 query 集合（只读焚诀 eval）。取不到返 None ⇒ 上层判 UNVERIFIED，禁猜。"""
    d = read_json(TESTSET)
    if d is None:
        return None
    tiers = d if isinstance(d, list) else (d.get("tiers") or d.get("sets") or [])
    qs = set()
    for t in tiers:
        for q in (t or {}).get("queries") or []:
            if q.get("query"):
                qs.add(q["query"])
    if not qs and isinstance(d, dict):          # 扁平形态兜底（题集改版时不静默 UNVERIFIED）
        for q in d.get("questions") or []:
            if q.get("query"):
                qs.add(q["query"])
    return qs or None


def _num(v):
    return isinstance(v, int) and not isinstance(v, bool)


def compare(base_doc, cur_doc, queries):
    """返回 (读数 | None, 红线列表)。红线空 ⇒ CLEAN。必需量取不到一律 (None, []) 交上层判 UNVERIFIED。"""
    b_real = rows_by_state(base_doc, "REAL_MISS")
    c_real = rows_by_state(cur_doc, "REAL_MISS")
    c_stale = rows_by_state(cur_doc, "STALE_EXPECT")
    c_other = {}
    for st in OTHER_STATES:
        c_other.update(rows_by_state(cur_doc, st))
    bn, cn = face_val(base_doc, "n"), face_val(cur_doc, "n")
    if bn is None or cn is None:
        return None, []
    still, fixed, moved, to_other, vanished = [], [], [], [], []
    for k, r in b_real.items():
        q = r.get("query")
        if k in c_real:
            still.append(k)
        elif k in c_stale:
            moved.append((q, r.get("expected")))
        elif k in c_other:
            to_other.append((q, r.get("expected")))
        elif queries is None:
            return None, []                    # 无法区分「修好」与「删题面」⇒ 不判
        elif q in queries:
            fixed.append((q, r.get("expected")))
        else:
            vanished.append((q, r.get("expected")))
    new_miss = [(r.get("query"), r.get("expected")) for k, r in c_real.items() if k not in b_real]
    accounted = len(still) + len(fixed) + len(moved) + len(to_other) + len(vanished)
    red = []
    # M4 = X-24 型反向断言：枚举器分母不能静默变小。
    # 首版此处写的是 accounted != len(b_real)，但五类是对同一 dict 的**互斥划分** ⇒ 恒相等、
    # 永不触发（装饰性判据，比没有更坏：它让人以为有守恒检查）。
    # 真会缩小分母的通路是**同状态内 query|expected 重复**：rows_by_state 用 dict 装，
    # 重复键被静默合并 ⇒ 逐条比对的基线变小，而 face.real_n 仍报原值。
    # ⇒ M4 改判「原始行数 != 去重键数」，该条件可由重复行触发（selftest 变异 6 即造它）。
    for tag, doc_ in (("baseline", base_doc), ("current", cur_doc)):
        rawc = raw_state_counts(doc_)
        for st, raw_n in rawc.items():
            dedup_n = len(rows_by_state(doc_, st))
            if raw_n != dedup_n:
                red.append("M4 %s 状态 %s 原始 %d 行但去重后 %d 键（同 query|expected 重复 ⇒ 分母静默缩小）"
                           % (tag, st, raw_n, dedup_n))
    if moved:
        red.append("M1 挪账 %d 条 REAL_MISS->STALE_EXPECT：%s" % (len(moved), "; ".join("%s->%s" % m for m in moved[:6])))
    if to_other:
        red.append("M1b 转不可判 %d 条（真错被改贴成 %s）：%s" % (len(to_other), "/".join(OTHER_STATES), "; ".join("%s->%s" % m for m in to_other[:6])))
    if cn < bn:
        red.append("M2 分母缩小 n %s->%s（题面被删而非被打对）" % (bn, cn))
    if vanished:
        red.append("M3 假消失 %d 条（不再出现且 query 已不在题集）：%s" % (len(vanished), "; ".join("%s->%s" % m for m in vanished[:6])))
    for tag, fc, cnt in (("baseline", face_val(base_doc, "real_n"), len(b_real)),
                         ("current", face_val(cur_doc, "real_n"), len(c_real))):
        if _num(fc) and fc != cnt:
            red.append("M5 %s face.real_n=%s 与 rows 逐条计数 %s 不符（rows 可能被截断）" % (tag, fc, cnt))
    reading = {
        "baseline_real_rows": len(b_real), "current_real_rows": len(c_real),
        "face_real_n_baseline": face_val(base_doc, "real_n"), "face_real_n_current": face_val(cur_doc, "real_n"),
        "n_baseline": bn, "n_current": cn,
        "hits_baseline": face_val(base_doc, "hits"), "hits_current": face_val(cur_doc, "hits"),
        "still_real_n": len(still), "fixed_n": len(fixed), "moved_to_stale_n": len(moved),
        "to_undecidable_n": len(to_other), "vanished_not_in_testset_n": len(vanished),
        "new_real_miss_n": len(new_miss),
        "relative_change_pct": (round((len(b_real) - len(c_real)) / len(b_real) * 100.0, 1) if b_real else None),
        "partition_identity_ok": accounted == len(b_real),   # 恒等式读数（非红线，见 M4 注释）
        "fixed_list": [list(x) for x in fixed], "new_real_list": [list(x) for x in new_miss],
        "moved_list": [list(x) for x in moved], "to_undecidable_list": [list(x) for x in to_other],
    }
    return reading, red


def _doc(n, real, stale=0, hits=None, other=0, real_prefix="q"):
    rows = [{"query": real_prefix + str(i), "expected": "s" + str(i), "state": "REAL_MISS"} for i in range(real)]
    rows += [{"query": "st" + str(i), "expected": "x" + str(i), "state": "STALE_EXPECT"} for i in range(stale)]
    rows += [{"query": "od" + str(i), "expected": "y" + str(i), "state": "UNDECIDABLE"} for i in range(other)]
    return {"face": {"n": n, "hits": hits if hits is not None else n - real, "real_n": real, "stale_n": stale},
            "rows": rows}


def selftest():
    """七条腿：正控绿 + 五类造假各自判红 + 缺题集不判。缺任一方向即无鉴别力（R236）。"""
    ok = True

    def chk(name, cond, got=""):
        if cond:
            print("  [OK  ] %s" % name)
        else:
            print("  [FAIL] %s  <-- %s" % (name, got))
        return bool(cond)

    qs = set("q" + str(i) for i in range(20)) | set("st" + str(i) for i in range(20)) | set("od" + str(i) for i in range(20))
    b = _doc(20, 12)
    c = _doc(20, 7, stale=8, hits=5)
    r, red = compare(b, c, qs)
    ok &= chk("正控：12->7 且题面齐、无挪账 ⇒ 零红线", not red, red)
    ok &= chk("正控读数：fixed=5 still=7 相对 −41.7%",
              r["fixed_n"] == 5 and r["still_real_n"] == 7 and r["relative_change_pct"] == 41.7, r)
    # 变异 1 挪账：q7..q9 在现轮变 STALE（rows 里以 st 前缀存在，需真撞键）=> 用同 key 改态
    c1 = _doc(20, 7, stale=8, hits=5)
    c1["rows"].append({"query": "q9", "expected": "s9", "state": "STALE_EXPECT"})
    c1["rows"].append({"query": "q10", "expected": "s10", "state": "STALE_EXPECT"})
    c1["rows"] = [x for x in c1["rows"] if not (x["query"] in ("q7", "q8"))]
    c1["face"]["real_n"] = len([x for x in c1["rows"] if x["state"] == "REAL_MISS"])
    _, red1 = compare(b, c1, qs)
    ok &= chk("变异·挪账 ⇒ 必判红（M1）", any("M1 " in x for x in red1), red1)
    # 变异 2 缩分母
    _, red2 = compare(b, _doc(15, 7, stale=8, hits=1), qs)
    ok &= chk("变异·缩分母 ⇒ 必判红（M2）", any("M2" in x for x in red2), red2)
    # 变异 3 删题面：baseline 有真错 q30，现轮无该行且 q30 不在题集
    b3 = _doc(20, 12); b3["rows"].append({"query": "q30", "expected": "s30", "state": "REAL_MISS"}); b3["face"]["real_n"] = 13
    _, red3 = compare(b3, c, qs)
    ok &= chk("变异·题面被删 ⇒ 必判红（M3）", any("M3" in x for x in red3), red3)
    # 变异 4 转不可判
    c4 = _doc(20, 7, stale=8, hits=5, other=2)
    c4["rows"] = [x for x in c4["rows"] if x["state"] != "UNDECIDABLE"]
    c4["rows"].append({"query": "q11", "expected": "s11", "state": "UNDECIDABLE"})
    _, red4 = compare(b, c4, qs)
    ok &= chk("变异·转不可判 ⇒ 必判红（M1b）", any("M1b" in x for x in red4), red4)
    # 变异 5 face 与 rows 不自洽
    c5 = _doc(20, 7, stale=8, hits=5); c5["face"]["real_n"] = 99
    _, red5 = compare(b, c5, qs)
    ok &= chk("变异·face/rows 不符 ⇒ 必判红（M5）", any("M5" in x for x in red5), red5)
    r6, red6 = compare(b, c, None)
    ok &= chk("缺题集 ⇒ 不判（None 且不出 CLEAN 措辞）", r6 is None, (r6, red6))
    # 变异 6 = M4 本身的可触发证据（改语义后不补这条腿，M4 又变回装饰性判据）
    b6 = _doc(20, 12)
    b6["rows"].append({"query": "q1", "expected": "s1", "state": "REAL_MISS"})   # 重复键
    b6["face"]["real_n"] = 13
    _, red6b = compare(b6, c, qs)
    ok &= chk("变异·同状态重复键 ⇒ 必判红（M4 可触发，非装饰）", any("M4" in x for x in red6b), red6b)
    print("[MIGRATION:SELFTEST-%s]" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def _dated_key(p):
    """排序键 = (轮号, 文件名日期, mtime)。

    首版只按日期串排 ⇒ 实测把无日期的 `route_miss_attr_r216_live.json` 排到最前
    （"" < "2026-.."），默认取件于是拿到 r119b 当「现件」而判了个假的 CLEAN。
    本仓轮次轴是 rNN（与 r115_inventory 的 newest_* 同向），故轮号优先、日期次之、mtime 末之。
    """
    base = os.path.basename(p)
    mr = re.search(r"r(\d+)", base)
    md = re.search(r"(20\d\d-\d\d-\d\d)", base)
    try:
        mt = os.path.getmtime(p)
    except OSError:
        mt = 0.0
    return (int(mr.group(1)) if mr else -1, md.group(1) if md else "", mt)


def pick_paths(args):
    cands = sorted(glob.glob(os.path.join(BENCH, "route_miss_attr_*.json")), key=_dated_key)
    cur = args.current or (cands[-1] if cands else None)
    base = args.baseline
    if not base and len(cands) >= 2:
        prev = [p for p in cands if os.path.abspath(p) != os.path.abspath(cur)]
        base = max(prev, key=_dated_key) if prev else None
    return base, cur


def main(argv=None):
    ap = argparse.ArgumentParser(description="REAL_MISS 跨轮逐条状态迁移账（防挪账/缩分母/删题面）")
    ap.add_argument("--baseline", default=None, help="旧件（缺省 = 次新的 route_miss_attr_*.json）")
    ap.add_argument("--current", default=None, help="现件（缺省 = 最新的 route_miss_attr_*.json）")
    ap.add_argument("--json", dest="out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    if args.selftest:
        return selftest()
    base_path, cur_path = pick_paths(args)
    if not base_path or not cur_path:
        print("%s 两份 route_miss_attr 件不齐（baseline=%s current=%s）⇒ 不判" % (TOK_UNV, bool(base_path), bool(cur_path)))
        return 2
    b, c = read_json(base_path), read_json(cur_path)
    if not b or not c:
        print("%s 件不可读或解析失败 ⇒ 不判（R247）" % TOK_UNV)
        return 2
    qs = testset_queries()
    if qs is None:
        print("%s 题集不可读（%s）⇒ 无法区分「修好」与「删题面」，不判" % (TOK_UNV, TESTSET))
        return 2
    reading, red = compare(b, c, qs)
    if reading is None:
        print("%s face 必需字段取不到（n/hits）⇒ 不判" % TOK_UNV)
        return 2
    doc = {
        "schema": "miss-migration-r217-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "cmd": "python 05-exec/r217_miss_migration.py",
        "inputs": {"baseline": os.path.basename(base_path), "current": os.path.basename(cur_path),
                   "producer": "05-exec/r117_route_miss_attr.py",
                   "testset": os.path.relpath(TESTSET, ROOT).replace(os.sep, "/")},
        "testset_queries_n": len(qs),
        "state": "CLEAN" if not red else "RED", "red_lines": red, "reading": reading,
        "caveat": "本件只判改善是否造假，不判改善幅度本身；幅度口径与 30% 达标判据见 "
                  "04-plan/需求6口径对照与决策件_r216_2026-10-25.md §3。",
    }
    if not args.quiet:
        print("REAL_MISS 跨轮迁移账（%s -> %s）" % (os.path.basename(base_path), os.path.basename(cur_path)))
        print("  真错 %s -> %s 条（相对 %s%%）｜题面 n %s -> %s｜命中 %s -> %s"
              % (reading["face_real_n_baseline"], reading["face_real_n_current"],
                 reading["relative_change_pct"], reading["n_baseline"], reading["n_current"],
                 reading["hits_baseline"], reading["hits_current"]))
        # 「划分恒等」是恒真读数（五类互斥必等于基线），不是成就；M4 红线看的是「原始行数==去重键数」
        print("  逐条分类：仍错 %d｜真修好 %d｜挪账 %d｜转不可判 %d｜题面消失 %d｜新增真错 %d｜划分恒等 %s"
              % (reading["still_real_n"], reading["fixed_n"], reading["moved_to_stale_n"],
                 reading["to_undecidable_n"], reading["vanished_not_in_testset_n"],
                 reading["new_real_miss_n"], reading["partition_identity_ok"]))
        # 列表元素落 JSON 时是 list，% 格式化只认 tuple ⇒ 必须 tuple(t)
        # （r217 首跑实测 TypeError: not enough arguments for format string —— py_compile 全过也拦不住）
        if reading["fixed_list"]:
            print("  修好的题（逐条具名，供人工复验）：%s" % "; ".join("%s->%s" % tuple(t) for t in reading["fixed_list"]))
        if reading["new_real_list"]:
            print("  新增真错（必须具名，禁只报净值）：%s" % "; ".join("%s->%s" % tuple(t) for t in reading["new_real_list"]))
        for x in red:
            print("  ! %s" % x)
    if args.out:
        tmp = args.out + ".tmp"
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, args.out)
        print("JSON -> %s" % os.path.relpath(args.out, ROOT))
    if red:
        print("%s %d 条红线（改善不可信，先修取数面/题面）" % (TOK_RED, len(red)))
        return 1
    print("%s 未见造假：无挪账、无转不可判、n 未缩、题面未消失、无重复键缩分母、face 与 rows 自洽" % TOK_CLEAN)
    return 0


if __name__ == "__main__":
    sys.exit(main())
