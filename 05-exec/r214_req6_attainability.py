# -*- coding: utf-8 -*-
r"""r214_req6_attainability.py — 需求 6「提升 ≥30%」在现役质量指标面上是否算术可达（只读）。

存在理由（r214 一手，补需求 6 缺的那半句话）：
  需求 6 从 r114 起每轮都记「未达（2.0%）」，但没有任何一面把「差多少」算成「能不能到」。
  既有报告只给三重定性结构证明（r131 §1.2），没有定量。本轮把两头的数连起来：
    阈值 30%（相对提升，写在 r115_quality_truth.py 的 r1 判定行）
    基线 88.3 ⇒ 需要的分数 = 88.3 * 1.30 = 114.8
    而该指标的设计上限（全命中才有的分）由权威评估件自算 max_achievable = 95.2
    ⇒ 114.8 > 95.2 ⇒ 该阈值在本面上算术上不可能达成，与「本轮有没有进步」无关。
  这不是给未达找台阶，是把结论从「还没做到」改成「这条尺子上做不到」——
  两者的下一步动作完全不同（前者继续磨尺子，后者必须换尺子或走归属方动作）。

判据（三态，禁静默）：
  MATHEMATICALLY_IMPOSSIBLE  need_score > max_achievable（阈值在本面装不下）
  ACHIEVABLE                 need_score <= max_achievable（本面仍装得下）
  UNVERIFIED                 基线件 / 现值件 / 上限 / 阈值 任一取不到
                             ⇒ rc=2，禁读成「可达」也禁读成「不可达」（R247）

口径红线：
  · 不重实现评分：score / n / hits / max_achievable 全读权威件
    （06-benchmark/quality_truth_r115_*.json，其上游 = 焚诀 eval/frozen_blind_eval.py，
     该件 R165 U1 审计自算 max_achievable = 权重和/条数）；
  · 阈值不硬编：从 r115_quality_truth.py 的 r1 判定行现读，读不到 ⇒ UNVERIFIED；
  · 双口径同时给（相对提升 / 绝对百分点）——需求 6 原句「提升幅度不低于 30%」两读都可能，
    仅当两读方向一致时才允许下「算术不可达」的断言；不一致 ⇒ UNVERIFIED；
  · 本件只判「本面装不装得下」，不判「任务质量到底如何」——路由 Top-1 是任务质量的
    上游必要条件而非任务完成度本身（r114 口径红线原句），该差异随读数一起打印。

用法：
  python 05-exec/r214_req6_attainability.py [--json 件] [--quiet]
  python 05-exec/r214_req6_attainability.py --selftest    # 五条双向自证腿
退出码：0 本面可达 / 1 本面算术不可达（真结论，不是错误）/ 2 输入面不可用。
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
RULER = os.path.join(HERE, "r115_quality_truth.py")
BASELINE_NAME = "quality_truth_r115_2026-10-18.json"
TOK_OK = "[REQ6:ACHIEVABLE]"
TOK_IMPOSSIBLE = "[REQ6:IMPOSSIBLE]"
TOK_UNVER = "[REQ6:UNVERIFIED]"
# 阈值现读：r1 判定行形如「relative_gain_pct ... >= 30.0」。
# 刻意不用反斜杠 b（本仓 r211 一手：JS 模板写 Python 会把 \b 吃成退格符）。
RE_THRESH = re.compile(r"relative_gain_pct[^\n]*>=\s*([0-9]+(?:\.[0-9]+)?)")
RE_DATE = re.compile(r"quality_truth_r115_([0-9]{4}-[0-9]{2}-[0-9]{2})")


def read_text(path):
    try:
        return io.open(path, encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return ""


def read_json(path):
    txt = read_text(path)
    if not txt:
        return None
    try:
        return json.loads(txt)
    except ValueError:
        return None


def newest_current():
    """现值件 = 06-benchmark 下最新一份 quality_truth_r115_*.json（排除基线件本身）。

    按（文件名内日期, mtime）取新，与棘轮估界法同向：不靠手抄轮号（X-26 同族）。
    """
    cands = [p for p in glob.glob(os.path.join(BENCH, "quality_truth_r115_*.json"))
             if os.path.basename(p) != BASELINE_NAME]
    if not cands:
        return None
    return max(cands, key=_newest_key)


def _newest_key(p):
    m = RE_DATE.search(os.path.basename(p))
    try:
        mt = os.path.getmtime(p)
    except OSError:
        mt = 0.0
    return (m.group(1) if m else "", mt)


def face_of(doc, name):
    return ((doc or {}).get("faces") or {}).get(name) or {}


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def threshold_pct():
    """从尺子源文件现读阈值；取不到返回 None（不硬编 30 当真相）。"""
    src = read_text(RULER)
    if not src:
        return None, "ruler_unreadable"
    vals = sorted({float(x) for x in RE_THRESH.findall(src)})
    if not vals:
        return None, "threshold_not_found"
    if len(vals) > 1:
        return None, "threshold_ambiguous:%s" % ",".join(str(v) for v in vals)
    return vals[0], None


def analyze(baseline_doc, current_doc, thresh):
    """核心算术。返回 (dict, None) 或 (None, 原因)。任一必需量缺失 ⇒ 不判。"""
    b = face_of(baseline_doc, "L1_layered")
    c = face_of(current_doc, "L1_layered")
    b_s, c_s = b.get("score"), c.get("score")
    ceil, ceil_src = c.get("max_achievable"), "current"
    if not _num(ceil):
        ceil, ceil_src = b.get("max_achievable"), "baseline"
    if not _num(ceil):
        return None, "max_achievable 不可得（现值件与基线件都没有）⇒ 不判可达性"
    for tag, v in (("基线 score", b_s), ("现值 score", c_s), ("阈值", thresh)):
        if not _num(v):
            return None, "%s 不可得 ⇒ 不判可达性" % tag
    if b_s <= 0:
        return None, "基线 score <= 0 ⇒ 相对提升无定义，不判可达性"
    need_rel = round(b_s * (1.0 + thresh / 100.0), 1)
    need_abs = round(b_s + thresh, 1)
    rel_attain = need_rel <= ceil
    abs_attain = need_abs <= ceil
    if rel_attain == abs_attain:
        verdict = "ACHIEVABLE" if rel_attain else "MATHEMATICALLY_IMPOSSIBLE"
    else:
        verdict = "UNVERIFIED"
    n, hits = c.get("n"), c.get("hits")
    gap = round(need_rel - c_s, 1)
    need_hits = None
    if (not rel_attain) and _num(n) and _num(hits) and n > 0:
        need_hits = int(-(-(need_rel * n) // 100)) - hits
    headroom = round((ceil - b_s) / b_s * 100.0, 1)
    return {
        "threshold_relative_pct": thresh,
        "baseline_score": b_s,
        "current_score": c_s,
        "current_relative_gain_pct": round((c_s - b_s) / b_s * 100.0, 1),
        "ceiling_score": ceil,
        "ceiling_source": ceil_src,
        "max_possible_relative_gain_pct": headroom,
        "need_score_relative_reading": need_rel,
        "need_score_absolute_reading": need_abs,
        "attainable_under_relative_reading": rel_attain,
        "attainable_under_absolute_reading": abs_attain,
        "two_readings_agree": rel_attain == abs_attain,
        "exceeds_scale_100": need_rel > 100.0,   # 百分制满分都装不下 ⇒ 与上限无关
        "verdict": verdict,
        "gap_to_need_points": gap,
        "extra_hits_needed_for_threshold": need_hits,
    }, None


def _doc(score, ceil, n=291, hits=200):
    return {"faces": {"L1_layered": {"score": score, "max_achievable": ceil, "n": n, "hits": hits}}}


def selftest():
    """五条腿：正控可达 / 反控不可达 / 缺上限不判 / 缺阈值不判 / 算术自证一致。双向锁死防恒真。"""
    ok = True

    def chk(name, cond, got=""):
        if cond:
            print("  [OK  ] %s" % name)
        else:
            print("  [FAIL] %s  <-- got: %s" % (name, got))
        return bool(cond)

    # 正控必须真能达成：低基线才装得下相对 30%（50 → 需 65）。
    # r214 自抓：我首版把正控写成「基线 88.3 / 上限 99」期望 ACHIEVABLE，
    # 但 88.3*1.3 = 114.8 > 99 ⇒ 期望本身是错的（自测当场判 FAIL 才暴露）。
    r1, _ = analyze(_doc(50.0, 90.0), _doc(60.0, 90.0), 30.0)
    ok &= chk("正控：低基线 50（需 65）上限 90 ⇒ ACHIEVABLE",
              r1["verdict"] == "ACHIEVABLE", r1["verdict"])
    r2, _ = analyze(_doc(88.3, 95.2), _doc(90.1, 95.2), 30.0)
    ok &= chk("反控：上限 95.2 装不下 114.8 ⇒ IMPOSSIBLE",
              r2["verdict"] == "MATHEMATICALLY_IMPOSSIBLE", r2["verdict"])
    r2b, _ = analyze(_doc(88.3, 100.0), _doc(90.1, 100.0), 30.0)
    ok &= chk("更强一层：连满分 100 都装不下 114.8 ⇒ 与上限无关，量纲本身不可达",
              r2b["verdict"] == "MATHEMATICALLY_IMPOSSIBLE"
              and r2b["exceeds_scale_100"] is True, r2b)
    r5, _ = analyze(_doc(50.0, 70.0), _doc(55.0, 70.0), 30.0)
    ok &= chk("两读不一致（相对可达 / 绝对不可达）⇒ UNVERIFIED 不断言",
              r5["verdict"] == "UNVERIFIED" and r5["two_readings_agree"] is False, r5)
    r3, why3 = analyze(_doc(88.3, None), _doc(90.1, None), 30.0)
    ok &= chk("缺上限 ⇒ 不判（返 None，不猜）", r3 is None, why3)
    r4, why4 = analyze(_doc(88.3, 95.2), _doc(90.1, 95.2), None)
    ok &= chk("缺阈值 ⇒ 不判", r4 is None, why4)
    ok &= chk("算术自证：verdict 与 need<=ceil 同向",
              (r2["need_score_relative_reading"] <= r2["ceiling_score"])
              == r2["attainable_under_relative_reading"], r2)
    print("[REQ6:SELFTEST-%s]" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    ap.add_argument("--baseline", default=os.path.join(BENCH, BASELINE_NAME))
    ap.add_argument("--current", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    if args.selftest:
        return selftest()

    thresh, terr = threshold_pct()
    if thresh is None:
        print("%s 阈值不可得（%s）⇒ 不判可达性，禁硬编 30 当真相（R247）" % (TOK_UNVER, terr))
        return 2
    base_doc = read_json(args.baseline)
    cur_path = args.current or newest_current()
    cur_doc = read_json(cur_path) if cur_path else None
    if not base_doc or not cur_doc:
        print("%s 基线件或现值件不可得（baseline=%s / current=%s）⇒ 不判可达性"
              % (TOK_UNVER, bool(base_doc), bool(cur_doc)))
        return 2
    res, why = analyze(base_doc, cur_doc, thresh)
    if res is None:
        print("%s %s" % (TOK_UNVER, why))
        return 2
    doc = {
        "schema": "req6-attainability-r214-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "cmd": "python 05-exec/r214_req6_attainability.py",
        "inputs": {"baseline_file": os.path.basename(args.baseline),
                   "current_file": os.path.basename(cur_path) if cur_path else None,
                   "threshold_source": os.path.basename(RULER),
                   "ceiling_producer": "焚诀 eval/frozen_blind_eval.py（R165 U1 自算 max_achievable）"},
        "metric_caveat": "本面 = 生产路由 Top-1（L1 layered），是任务质量的上游必要条件而非任务完成度"
                         "本身（r114 口径红线）；「不可达」判定只对本面成立，不得外推成「需求 6 永远无法验证」。",
        "result": res,
    }
    if not args.quiet:
        print("需求6 阈值可达性（现役指标面 L1 layered，读数全取权威件）")
        print("  阈值 %s%%（%s 现读）｜基线 %s ｜现值 %s ｜本面上限 %s（源=%s）"
              % (thresh, os.path.basename(RULER), res["baseline_score"], res["current_score"],
                 res["ceiling_score"], res["ceiling_source"]))
        print("  需要分数：相对读法 %s ｜绝对百分点读法 %s"
              % (res["need_score_relative_reading"], res["need_score_absolute_reading"]))
        print("  两读方向一致=%s ⇒ 判定 %s" % (res["two_readings_agree"], res["verdict"]))
        print("  基线到上限的全部余量 = %s%%（本面最大可能相对提升）；距阈值还差 %s 分"
              % (res["max_possible_relative_gain_pct"], res["gap_to_need_points"]))
        if res["extra_hits_needed_for_threshold"] is not None:
            print("  要到阈值需净增命中 %s 条" % res["extra_hits_needed_for_threshold"])
        print("  ⚠️ %s" % doc["metric_caveat"])
    if args.out:
        tmp = args.out + ".tmp"
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, args.out)
        print("JSON -> %s" % os.path.relpath(args.out, ROOT))
    if res["verdict"] == "MATHEMATICALLY_IMPOSSIBLE":
        print("%s 阈值在本面算术不可达（需 %s > 上限 %s）"
              % (TOK_IMPOSSIBLE, res["need_score_relative_reading"], res["ceiling_score"]))
        return 1
    if res["verdict"] == "ACHIEVABLE":
        print("%s 本面仍装得下该阈值（需 %s <= 上限 %s）"
              % (TOK_OK, res["need_score_relative_reading"], res["ceiling_score"]))
        return 0
    print("%s 两读不一致 ⇒ 不足以断言可达性" % TOK_UNVER)
    return 2


if __name__ == "__main__":
    sys.exit(main())
