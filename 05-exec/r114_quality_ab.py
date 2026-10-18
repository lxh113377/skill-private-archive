# -*- coding: utf-8 -*-
r"""r114_quality_ab.py — 需求6 的可复算落地：用**真实任务级基准**代替覆盖率代理量。

为什么换指标（r113 §10 需求6 行的自我限定）：
  r113 用 M1「身份可判定率 30.2%→69.2%」充当「质量提升 ≥30%」，并在同节写明它是
  **判定面覆盖率**、不是任务成功率，且「本仓无任务基准集」。本轮实测发现该断言**不成立**：
  焚诀 eval/skill_hitrate_eval_v2.py 就是一套可跑的任务级基准——
  99 条自然语言 query（easy 34 / medium 35 / hard 18 / extra_hard 5 / negative 7），
  每条带 expected_skill，跑 Top-1 / Top-3 / 命中率 / P / R / 误触发，且自带
  Wilson 区间与「区间重叠即不得判提升」的可比性判定（P1-23）。
  ⇒ 有真基准就不得再拿覆盖率代理量充当质量提升（R247 同族：代理量不得冒充观测量）。

本件做三件事：
  1) 跑基准并**结构化落盘**（原脚本只 print，无法跨轮比较、无法进契约校验）；
  2) 与基线件比对，输出 Δ 与 Wilson 可比性判定（禁只印 pp 不谈区间）；
  3) 把「替换动作」与「质量变化」**解耦度量**：替换动作由 r114_replacement_scan 的
     MATCHED 面与实装件决定；本件只回答「跑分变了没有、变的是不是抽样抖动」。

口径红线（写进产物，防后人读错）：
  · Top-1 是**路由命中**，不是「任务做完的好坏」；它测的是「用户一句话，系统有没有把
    正确的 skill 送到手上」。这是任务质量的**上游必要条件**，不是充分条件。
  · 区间重叠 ⇒ 一律不得写成「提升」，只能写「幅度落在抽样抖动内」（P1-23）。
  · contaminated（期望 skill 不在实时注册表）已由基准脚本从分母剔除，本件照抄该口径。

用法：
  python 05-exec/r114_quality_ab.py                      # 跑基准 + 与基线比对
  python 05-exec/r114_quality_ab.py --baseline <件> --json <件>
  python 05-exec/r114_quality_ab.py --record-baseline    # 把当前跑分登记为基线（慎用）
退出码：0 = 出件 / 2 = 基准不可跑（禁记绿）。
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")
FENJUE = r"C:\Users\37533\Desktop\workspace\焚诀"
EVAL = os.path.join(FENJUE, "eval", "skill_hitrate_eval_v2.py")
DEFAULT_BASELINE = os.path.join(BENCH, "quality_baseline_r114.json")
PY_CANDIDATES = [
    os.path.expanduser(r"~\.workbuddy\binaries\python\envs\default\Scripts\python.exe"),
    r"C:\Program Files\Python312\python.exe",
]

METHODS = ("keyword", "tfidf", "hybrid")
METHOD_CN = {"关键词": "keyword", "TF-IDF": "tfidf", "混合路由": "hybrid"}
LINE_RE = re.compile(
    r"^(关键词|TF-IDF|混合路由)\s+([0-9.]+)%\s+([0-9.]+)%\s+([0-9.]+)%\s+"
    r"([0-9.]+)%\s+([0-9.]+)%\s+([0-9.]+)%\s+([0-9.]+)%")
CI_RE = re.compile(
    r"^(关键词|TF-IDF|混合路由)\s+Top-1\s+([0-9.]+)%\s+\[([0-9.]+),\s*([0-9.]+)\]\s+n=(\d+)")
CONTAM_RE = re.compile(r"^\s+(关键词|TF-IDF|混合路由)\s+contaminated\s*=\s*(\d+)")


def pick_python():
    for p in PY_CANDIDATES:
        if os.path.exists(p):
            return p
    return sys.executable


def run_benchmark(py):
    """跑基准脚本并原样保存 stdout（失败不得静默）。"""
    env = dict(os.environ)
    env["PYTHONPYCACHEPREFIX"] = os.path.join(os.environ.get("TEMP", "."), "pycache_ab")
    try:
        p = subprocess.run([py, EVAL], cwd=FENJUE, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900, env=env)
    except Exception as exc:  # noqa: BLE001
        return None, "exc:%r" % (exc,)
    if p.returncode != 0:
        return None, "rc=%d:%s" % (p.returncode, (p.stderr or "").strip()[:400])
    return p.stdout, None


def parse(out):
    """从基准 stdout 解析结构化结果（逐行口径，可复算）。

    返回 {"methods": {m: {top1, top3, hit_rate, precision, recall, f1, fp_rate}},
                     "ci": {m: {"top1": [lo, hi, n]}}, "contaminated": {m: n}}
    解析不到的字段一律 **缺键**（不填 0）—— 填 0 会把「没解析到」伪装成「跑分为 0」。
    """
    res = {"methods": {}, "ci": {}, "contaminated": {}}
    for line in (out or "").splitlines():
        m = LINE_RE.match(line.strip())
        if m:
            key = METHOD_CN[m.group(1)]
            vals = [float(m.group(i)) for i in range(2, 9)]
            res["methods"][key] = {"top1": vals[0], "top3": vals[1],
                                   "hit_rate": vals[2], "precision": vals[3],
                                   "recall": vals[4], "f1": vals[5], "fp_rate": vals[6]}
            continue
        c = CI_RE.match(line.strip())
        if c:
            key = METHOD_CN[c.group(1)]
            res["ci"].setdefault(key, {})["top1"] = [float(c.group(3)),
                                                     float(c.group(4)), int(c.group(5))]
            continue
        k = CONTAM_RE.match(line)
        if k and "contaminated =" in line:
            res["contaminated"].setdefault(METHOD_CN[k.group(1)], int(k.group(2)))
    return res


def comparability(base_ci, other_ci):
    """两个 Wilson 区间的可比性（P1-23 同口径，禁自造）。"""
    if not base_ci or not other_ci:
        return "区间不可得(n=0/缺分母)"
    if other_ci[0] > base_ci[1]:
        return "区间分离(可判为提升)"
    if other_ci[1] < base_ci[0]:
        return "区间分离(可判为下降)"
    return "区间重叠(幅度落在抽样抖动内)"


def rel_delta(base, now):
    if not base:
        return None
    return round((now - base) / float(base) * 100.0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default=DEFAULT_BASELINE)
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--record-baseline", action="store_true")
    ap.add_argument("--method", default="hybrid", choices=list(METHODS))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    if not os.path.exists(EVAL):
        print("[QUALITY:UNVERIFIED] 基准脚本不存在: %s（禁按 0 分记）" % EVAL)
        return 2
    py = pick_python()
    raw, err = run_benchmark(py)
    if err:
        print("[QUALITY:UNVERIFIED] 基准跑不起来: %s（禁记绿；先查依赖）" % err)
        return 2
    now = parse(raw)
    if not now["methods"]:
        print("[QUALITY:UNVERIFIED] 基准输出解析不出任何方法行 ⇒ 判据/输出格式已漂移，"
              "禁按 0 分记（R247）")
        return 2

    doc = {"schema": "quality-ab-r114-v1",
           "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
           "cmd": "python 05-exec/r114_quality_ab.py",
           "benchmark": {"script": EVAL, "python": py,
                         "queries_n": None, "tiers": None},
           "metric_note": ("Top-1 是路由命中率，不是任务完成好坏；"
                           "它是任务质量的上游必要条件而非充分条件。"
                           "区间重叠一律不得写成「提升」（P1-23）。"),
           "now": now}

    # 补 queries/tiers 事实（从测试集现取，禁手抄）
    tq = os.path.join(FENJUE, "eval", "test_queries.json")
    if os.path.exists(tq):
        try:
            data = json.load(io.open(tq, encoding="utf-8"))
            doc["benchmark"]["tiers"] = {t.get("tier"): len(t.get("queries") or []) for t in data}
            doc["benchmark"]["queries_n"] = sum(doc["benchmark"]["tiers"].values())
        except Exception as exc:  # noqa: BLE001
            doc["benchmark"]["tiers_error"] = repr(exc)

    base = None
    if os.path.exists(args.baseline):
        try:
            base = json.load(io.open(args.baseline, encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            doc["baseline_error"] = repr(exc)

    m = args.method
    now_m = now["methods"].get(m)
    if base and base.get("now", {}).get("methods", {}).get(m):
        base_m = base["now"]["methods"][m]
        base_ci = (base["now"].get("ci", {}).get(m, {}) or {}).get("top1")
        now_ci = (now.get("ci", {}).get(m, {}) or {}).get("top1")
        doc["comparison"] = {
            "method": m,
            "base_top1": base_m["top1"], "now_top1": now_m["top1"] if now_m else None,
            "delta_pp": round((now_m["top1"] - base_m["top1"]), 1) if now_m else None,
            "delta_rel_pct": rel_delta(base_m["top1"], now_m["top1"]) if now_m else None,
            "base_top3": base_m["top3"], "now_top3": now_m["top3"] if now_m else None,
            "base_f1": base_m.get("f1"), "now_f1": now_m.get("f1") if now_m else None,
            "top1_ci_base": base_ci, "top1_ci_now": now_ci,
            "top1_comparability": comparability(base_ci, now_ci),
            "verdict_rule": ("区间分离(可判为提升) 且 delta_rel_pct >= 30 才可写「提升 ≥30%」；"
                             "区间重叠一律写「幅度落在抽样抖动内」"),
        }

    out = args.json_out or os.path.join(
        BENCH, "quality_ab_r114_%s.json" % datetime.now().strftime("%Y-%m-%d"))
    if args.record_baseline:
        out = args.baseline
    tmp = out + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out)

    if not args.quiet:
        for meth in METHODS:
            r = now["methods"].get(meth)
            if not r:
                continue
            ci = now.get("ci", {}).get(meth, {}).get("top1")
            ci_s = ("[%.1f, %.1f] n=%d" % (ci[0], ci[1], ci[2])) if ci else "区间不可得"
            print("  %-8s Top-1 %5.1f%% %s ｜ Top-3 %5.1f%% ｜ 命中 %5.1f%% ｜ "
                  "P %5.1f%% R %5.1f%% F1 %5.1f%% ｜ 误触发 %5.1f%%"
                  % (meth, r["top1"], ci_s, r["top3"], r["hit_rate"],
                     r["precision"], r["recall"], r["f1"], r["fp_rate"]))
        c = doc.get("comparison")
        if c:
            print("与基线（%s）比：Top-1 %.1f%% → %.1f%%（%+.1fpp / 相对 %+.1f%%）⇒ %s"
                  % (m, c["base_top1"], c["now_top1"], c["delta_pp"],
                     c["delta_rel_pct"], c["top1_comparability"]))
        else:
            print("无基线件可比（首次跑分即基线）：若确认要登记，加 --record-baseline")
        if now.get("contaminated"):
            print("评测集污染（已由基准脚本从分母剔除）：%s" % now["contaminated"])
    print("JSON -> %s" % out)
    key = now["methods"].get(m) or {}
    print("[QUALITY:MEASURED] method=%s top1=%.1f top3=%.1f hit=%.1f queries=%s"
          % (m, key.get("top1", -1), key.get("top3", -1), key.get("hit_rate", -1),
             doc["benchmark"].get("queries_n")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
