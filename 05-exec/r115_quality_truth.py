# -*- coding: utf-8 -*-
r"""r115_quality_truth.py -- 更正 r114 的口径错误：质量主指标必须测**生产路由**，不是 eval 内的对照函数。

## r114 错在哪（本轮一手实证）

r114 用 05-exec/r114_quality_ab.py 解析 eval/skill_hitrate_eval_v2.py 的 print 输出，
取其中 hybrid 行的 Top-1 = 38.2% 当作「现役任务质量」，并据此写「本体系最硬的短板」。
**这是错的，且错了两层**：

1. hybrid_match() 只是该 eval 脚本里**用于三方法对照的其中一个近似实现**
   （keyword / tfidf / hybrid 三者并列，脚本用途是「对比哪种轻量匹配更好」，
   不是「给生产路由打分」）。它**不读** direct_map / tags / BGE / memory 任何一层。
2. 真正的生产路由是 eval/unified_router.py::route()（direct_map -> tags ->
   BGE 语义 -> memory -> LLM 多层）。仓内权威评估器是 eval/frozen_blind_eval.py，
   它**直接调 route()**，且 eval/blindset_gate_baseline.json 已记分面基线。

同一批题上下两把尺的实测差（本件 --selftest 可复算）：

| 面 | 生产 route() | eval hybrid_match | 差 |
|---|---|---|---|
| frozen_blind（10 条，永冻结） | 70.0%（净化 87.5%） | 30.0% | +40pp |
| test_queries（99 条，调参面） | 96.0%（净化 97.8%） | 37.0% | +59pp |
| layered_testset（291 条，仓内权威面） | 88.3% | （未在其上测） | -- |

=> 「38.2%」是**尺子的读数**，不是路由能力的读数。按 R263（修判据不改数据）本轮：
   **不删 r114 的历史结论**（R241 只加注），而是新建**正确口径**的度量件并给 r114 挂校正注。

## 本件判什么

四层，全部**调用仓内既有权威评估器**，不自己重实现判据（避免第三把坏尺）：

| 层 | 面 | 权威件 | 判什么 |
|---|---|---|---|
| L1 | layered 291 条 | frozen_blind_eval.py --json --set layered | 生产路由 Top-1（仓内基线面） |
| L2 | frozen 10 条 | frozen_blind_eval.py --json --set frozen | 生产路由 Top-1（永冻结面） |
| L3 | 污染 | hitrate_holdout.py --json | held-out 泄漏率（决定 L1 分数可信度） |
| L4 | 干净面 | 由 L1 + L3 派生 | 「不靠泄漏拿到的分」= 真实路由能力 |

## 口径红线（写进产物）

- L1 的 88.3% 含 63.6% 泄漏题加成（实测抬分 +7.7pp）=> 引用时必须同屏给 L4 干净面分。
- L2 只有 10 条，n 太小：只作「有没有崩」的哨兵，禁作趋势或幅度结论。
- 与 r114 的 38.2% **不可比**（不同函数），禁相减、禁写「提升了 N 倍」。

用法：
  python 05-exec/r115_quality_truth.py
  python 05-exec/r115_quality_truth.py --json <件>
  python 05-exec/r115_quality_truth.py --selftest
退出码：0 出件且权威面可用 / 2 任一权威评估器不可用（禁记绿）。
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
EVAL = os.path.join(FENJUE, "eval")
PY_CANDIDATES = [
    os.path.expanduser(r"~\.workbuddy\binaries\python\envs\default\Scripts\python.exe"),
    r"C:\Program Files\Python312\python.exe",
]


def pick_python():
    for p in PY_CANDIDATES:
        if os.path.exists(p):
            return p
    return sys.executable


def run_json(script, args, timeout=1800):
    """跑仓内权威评估器并取其 --json 输出（失败不得静默）。"""
    py = pick_python()
    argv = [py, os.path.join(EVAL, script)] + list(args)
    try:
        p = subprocess.run(argv, cwd=FENJUE, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except Exception as exc:  # noqa: BLE001
        return None, "exc:%r" % (exc,)
    raw = (p.stdout or "").strip()
    if not raw:
        return None, "empty_stdout rc=%s stderr=%s" % (p.returncode, (p.stderr or "")[:300])
    start = raw.find("{")
    if start < 0:
        return None, "no_json rc=%s head=%s" % (p.returncode, raw[:200])
    try:
        return json.loads(raw[start:]), None
    except ValueError as exc:
        return None, "json:%r tail=%s" % (exc, raw[-300:])


def face_layered():
    return run_json("frozen_blind_eval.py", ["--json", "--set", "layered"])


def face_frozen():
    return run_json("frozen_blind_eval.py", ["--json", "--set", "frozen"])


def face_holdout():
    return run_json("hitrate_holdout.py", ["--json"])


def clean_face(layered, holdout):
    """由 L1 逐条结果 + L3 泄漏面派生 L4 干净面。

    泄漏判定口径直接取 hitrate_holdout 的结论；取不到就返回 (None, 原因)。
    禁把「没算出来」当「零泄漏」（R247）。
    """
    if not layered:
        return None, "layered 面不可用"
    results = layered.get("results") or []
    if not results:
        return None, "layered.results 为空"
    if not holdout:
        return None, "holdout 面不可用（无泄漏面则无法派生干净面）"

    # 路径 A（首选）：holdout 的 testset 段给计数 + detail 串给官方双口径。
    # 这是权威件自己算出来的「干净面分」，优于我方按名单重算（避免第三把尺）。
    ts = holdout.get("testset") or {}
    n_all = ts.get("n")
    n_clean = ts.get("clean")
    n_leak = ts.get("leak")
    detail = holdout.get("detail") or ""
    mm = re.search(r"干净面\s*([0-9.]+)%", detail)
    clean_official = float(mm.group(1)) if mm else None
    if isinstance(n_clean, int) and n_clean > 0 and clean_official is not None:
        return {"source": "hitrate_holdout.testset + detail（官方件自算，非本件重算）",
                "n": n_clean, "n_all": n_all, "leak_n": n_leak,
                "leak_rate_pct": ts.get("rate"),
                "top1_pct": clean_official,
                "weighted_pct": None,
                "note": ("官方双口径 detail=%s ｜ 本值 = 剔除 %s 条泄漏题后的干净面 Top-1"
                         % (detail.strip(), n_leak))}, None

    # 路径 B（退路）：有逐条泄漏名单时按名单从 L1 结果派生
    leaked = None
    for k in ("leaked_queries", "leak_queries", "leaked", "leak_rows", "leaked_list"):
        v = holdout.get(k)
        if isinstance(v, list) and v:
            leaked = v
            break
    if leaked is None:
        return None, ("holdout 既无 testset.clean 也无逐条泄漏名单"
                      "（可用键=%s）" % ",".join(sorted(holdout.keys())[:12]))
    leak_set = set()
    for x in leaked:
        q = x.get("query") if isinstance(x, dict) else x
        if q:
            leak_set.add(q)
    cl = [r for r in results if r.get("query") not in leak_set]
    if not cl:
        return None, "干净面为空（全部题都在泄漏名单里）"
    hits = sum(1 for r in cl if r.get("hit"))
    return {"source": "由 L1 结果 + 泄漏名单逐条派生",
            "n": len(cl), "hits": hits,
            "top1_pct": round(100.0 * hits / len(cl), 1),
            "leak_n": len(leak_set),
            "note": "退路口径：与官方 testset.clean 计数可能不一致，须交叉核对"}, None


def selftest():
    """三腿：证明「生产 route()」与「eval hybrid_match」是两把不同的尺。

    这条腿是本件的存在理由 —— r114 的错就是没做这一步，
    直接把对照函数当生产路由，然后拿它的读数写「最硬短板」。
    """
    py = pick_python()
    code = "\n".join([
        "import os,sys,json",
        "FJ=r'" + FENJUE.replace("\\", "\\\\") + "'",
        "sys.path.insert(0, os.path.join(FJ,'eval'))",
        "os.chdir(FJ)",
        "import unified_router as U, skill_hitrate_eval_v2 as E",
        "sk=E.load_skills(); v,m,i=E.load_tfidf()",
        "qs=['把这个 PDF 合并一下','帮我装个 skill','生成一张图片']",
        "out=[]",
        "for q in qs:",
        "    pr=U.route(q, enable_llm=False).get('top1')",
        "    hy=(E.hybrid_match(q, sk, v, m, i) or [None])[0]",
        "    out.append({'q':q,'prod':pr,'hyb':hy})",
        "print('SELFTEST_JSON'+json.dumps(out,ensure_ascii=False))",
    ])
    try:
        p = subprocess.run([py, "-c", code], cwd=FENJUE, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
    except Exception as exc:  # noqa: BLE001
        print("[QUALITY:FAIL] selftest 跑不起来: %r" % (exc,))
        return 1
    line = [l for l in (p.stdout or "").splitlines() if l.startswith("SELFTEST_JSON")]
    if not line:
        print("[QUALITY:FAIL] selftest 无输出（stderr=%s）" % (p.stderr or "")[:300])
        return 1
    rows = json.loads(line[0][len("SELFTEST_JSON"):])
    print("  %-22s %-24s %-24s %s" % ("query", "生产 route()", "eval hybrid_match", "同否"))
    same = 0
    for r in rows:
        eq = r["prod"] == r["hyb"]
        same += 1 if eq else 0
        print("  %-22s %-24s %-24s %s" % (r["q"][:22], str(r["prod"])[:24],
                                          str(r["hyb"])[:24], "同" if eq else "**不同**"))
    print()
    if same == len(rows):
        print("[QUALITY:FAIL] 两把尺完全同结论 => 本件的立论不成立，须重查")
        return 1
    print("[QUALITY:PASS] selftest：两把尺在 %d/%d 条上结论不同 => 非同源，"
          "r114 用 hybrid_match 代表生产路由属口径错误" % (len(rows) - same, len(rows)))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    if args.selftest:
        return selftest()

    layered, e1 = face_layered()
    frozen, e2 = face_frozen()
    holdout, e3 = face_holdout()
    errs = {"layered": e1, "frozen": e2, "holdout": e3}
    if not layered or not frozen:
        print("[QUALITY:UNVERIFIED] 权威评估器不可用 => 禁记绿")
        for k, v in errs.items():
            if v:
                print("  %s: %s" % (k, v))
        return 2

    clean, clean_err = clean_face(layered, holdout)
    doc = {
        "schema": "quality-truth-r115-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "cmd": "python 05-exec/r115_quality_truth.py",
        "r114_correction": {
            "what_was_wrong": ("r114 取 eval/skill_hitrate_eval_v2.py 的 hybrid_match "
                               "Top-1=38.2% 当作「现役任务质量」；该函数只是三方法对照的"
                               "近似实现，不读 direct_map/tags/BGE/memory 任何一层"),
            "correct_measure": ("eval/unified_router.route()（生产路由），"
                                "由 eval/frozen_blind_eval.py 官方计分"),
            "r114_value_pct": 38.2,
            "comparable": False,
            "note": "两值不同源，禁相减、禁写「提升N倍」；按 R241 给 r114 挂校正注而非改写",
        },
        "metric_note": ("L1(layered) 含泄漏题加成，引用须同屏给 L4 干净面；"
                        "L2(frozen) 仅 10 条，只作哨兵不作趋势"),
        "faces": {
            "L1_layered": {k: layered.get(k) for k in
                           ("score", "max_achievable", "n", "hits",
                            "semantic_layer", "bge_status")},
            "L2_frozen": {k: frozen.get(k) for k in
                          ("score", "max_achievable", "n", "hits",
                           "semantic_layer", "bge_status")},
            "L3_holdout": holdout,
            "L4_clean": clean,
            "L4_error": clean_err,
        },
        "errors": {k: v for k, v in errs.items() if v},
    }
    out = args.json_out or os.path.join(
        BENCH, "quality_truth_r115_%s.json" % datetime.now().strftime("%Y-%m-%d"))
    tmp = out + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out)

    l1 = doc["faces"]["L1_layered"]
    l2 = doc["faces"]["L2_frozen"]
    if not args.quiet:
        print("覆盖根：production route() via eval/frozen_blind_eval.py（不重实现判据）")
        print("  L1 layered（%s 层）: %.1f%% （%s/%s 条，上限 %s）"
              % (l1.get("semantic_layer"), l1.get("score") or 0, l1.get("hits"),
                 l1.get("n"), l1.get("max_achievable")))
        print("  L2 frozen （%s 层）: %.1f%% （%s/%s 条）"
              % (l2.get("semantic_layer"), l2.get("score") or 0,
                 l2.get("hits"), l2.get("n")))
        if holdout:
            ts = holdout.get("testset") or {}
            pool = holdout.get("pool") or {}
            print("  L3 泄漏面          : 测试集 %s/%s = %s%% ｜ 干净面 %s 条 ｜ "
                  "轮换池 %s/%s = %s%%"
                  % (ts.get("leak"), ts.get("n"), ts.get("rate"), ts.get("clean"),
                     pool.get("leak"), pool.get("n"), pool.get("rate")))
            if holdout.get("detail"):
                print("     detail: %s" % holdout["detail"])
        if clean:
            print("  L4 干净面          : %.1f%% （%s/%s 条，剔除泄漏 %s 条，来源=%s）"
                  % (clean["top1_pct"], clean.get("hits", "?"), clean.get("n"),
                     clean.get("leak_n"), clean.get("source", "?")))
        else:
            print("  L4 干净面          : 不可得（%s）" % clean_err)
    print("JSON -> %s" % out)
    print("[QUALITY:PROD] L1=%.1f%% L2=%.1f%% L4=%s"
          % (l1.get("score") or 0, l2.get("score") or 0,
             ("%.1f%%" % clean["top1_pct"]) if clean else "N/A"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
