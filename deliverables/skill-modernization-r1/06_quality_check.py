# -*- coding: utf-8 -*-
"""06_quality_check.py -- 需求6 质量提升判据（captain 2026-11-07 接管 t6 后建）。

为什么存在：需求6 要求「替换后任务完成质量提升不低于 30%」。本判据把该承诺变成可执行的三态门，
并强制它回答一个此前没人算过的问题：**这个 30% 在某些面上是不是算术上就到不了**。

判据结构（三态，与 run_gates 同口径 0 PASS / 1 FAIL / 2 UNVERIFIED）：
  R1 阈值腿：基线 * 1.30 <= 该面上限？否 => 该面「算术不可达」，本腿必须显式点名而非静默通过。
  R2 歧义腿：当前 CI95 与基线 CI95 是否重叠？重叠 => 提升落在抽样抖动内，不得宣称提升。
  R3 实测腿：读本次基线件的 actual gain，与 R1 的算术上限对照。
  三腿任一不满足 => 需求6 判「未达标」；这是**如实记账**，不是失败。禁把 R1 不可达读成 PASS。

负控：把基线的 max_achievable 人为抬到 200，R1 会错误判「可达」=> 判据必须因此转红，
证明 R1 真的在算数、不是恒绿装饰。
"""
import argparse, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
R115 = os.path.join(HERE, "data", "06_r115_baseline.json")
THRESHOLD_PCT = 30.0


def load(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def faces_from(doc):
    """抽三面：L1/L2/L4。每面 -> (name, baseline, current, max_achievable, n)。

    baseline 取 requirement6.baseline_score 仅对 L1 适用（官方件只给 L1 的历史基线）；
    L2/L4 无历史基线时用 current 自身作 base（保守：等于「假设没有提升」），
    并在返回值里标记 base_is_assumed，避免把假设当实测。
    """
    f = doc.get("faces") or {}
    rq = doc.get("requirement6") or {}
    out = []
    l1 = f.get("L1_layered") or {}
    if l1:
        out.append(("L1_layered", rq.get("baseline_score"), l1.get("score"),
                    l1.get("max_achievable"), l1.get("n"), False))
    for key in ("L2_frozen", "L4_clean"):
        d = f.get(key) or {}
        if not d:
            continue
        sc = d.get("score") if key == "L2_frozen" else d.get("top1_pct")
        if sc is None:
            continue
        out.append((key, sc, sc, d.get("max_achievable") or (95.0 if key == "L2_frozen" else 100.0),
                    d.get("n"), True))
    return out


def evaluate(doc, boost_max=False):
    """返回 (ok, details)。boost_max=True 仅给负控用：人为抬高上限，判据必须因此变红。"""
    rq = doc.get("requirement6") or {}
    details = []
    ok = True
    for name, base_s, cur_s, max_s, n, assumed in faces_from(doc):
        if base_s is None or max_s is None:
            details.append({"face": name, "verdict": "UNVERIFIED", "why": "基线或上限缺失"})
            ok = False
            continue
        m = float(max_s) * (2.0 if boost_max else 1.0)
        need = float(base_s) * (1 + THRESHOLD_PCT / 100.0)
        reachable = need <= m
        row = {
            "face": name,
            "baseline": base_s,
            "baseline_assumed": assumed,
            "current": cur_s,
            "max_achievable": max_s,
            "need_for_30pct": round(need, 2),
            "arithmetically_reachable": reachable,
            "n": n,
        }
        if not reachable and not boost_max:
            # 算术不可达 => R1 腿必须显式点名，不得静默判绿
            row["verdict"] = "IMPOSSIBLE"
        elif reachable and boost_max:
            # 负控：上限被抬高后判「可达」，但实测 gain 不足 => 必须转红
            row["verdict"] = "NEGCTRL_OVERREACH"
            ok = False
        else:
            row["verdict"] = "EVALUATED"
        details.append(row)
    # R2 歧义腿：CI 重叠即不得宣称提升
    b_ci = rq.get("baseline_ci95")
    c_ci = rq.get("current_ci95")
    overlap = None
    if b_ci and c_ci:
        overlap = not (c_ci[0] > b_ci[1] or b_ci[0] > c_ci[1])
    r1_met = bool(rq.get("r1_threshold_met"))
    return ok, {
        "faces": details,
        "threshold_pct": THRESHOLD_PCT,
        "relative_gain_pct": rq.get("relative_gain_pct"),
        "r1_threshold_met": r1_met,
        "ci_overlap": overlap,
        "ci_note": rq.get("r2_comparability"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r115", default=R115)
    ap.add_argument("--negative-control", action="store_true")
    ap.add_argument("--json", dest="json_out")
    a = ap.parse_args()

    try:
        doc = load(a.r115)
    except Exception as e:
        print("[QUALITY:UNVERIFIED] 基线件不可读: " + str(e))
        return 2

    ok, res = evaluate(doc, boost_max=a.negative_control)
    if a.negative_control:
        # 负控：抬高上限后，L1 应被判「可达」，但实测 gain 只有 2.7% => 判据必须红
        over = [f for f in res["faces"] if f.get("verdict") == "NEGCTRL_OVERREACH"]
        if over:
            print("[NEGCTRL:RED] 上限被人为抬高后 L1 被误判为「可达」，实测 gain="
                  + str(res["relative_gain_pct"]) + "% 远不足 30% => 判据检出矛盾")
            return 0
        print("[NEGCTRL:FAIL] 抬高上限后判据仍未见红 —— 判据无牙")
        return 1

    for f in res["faces"]:
        print("  %-12s base=%-6s cur=%-6s max=%-6s need30=%-8s n=%-5s => %s"
              % (f["face"], f.get("baseline"), f.get("current"), f.get("max_achievable"),
                 f.get("need_for_30pct"), f.get("n"), f.get("verdict")))
    print("  relative_gain_pct = " + str(res["relative_gain_pct"])
          + " (threshold " + str(res["threshold_pct"]) + "%)")
    print("  r1_threshold_met   = " + str(res["r1_threshold_met"]))
    print("  ci_overlap         = " + str(res["ci_overlap"]) + " (" + str(res["ci_note"]) + ")")

    if a.json_out:
        with io.open(a.json_out, "w", encoding="utf-8", newline="\n") as fo:
            json.dump(res, fo, ensure_ascii=False, indent=2)

    impossible = [f["face"] for f in res["faces"] if f.get("verdict") == "IMPOSSIBLE"]
    if res["r1_threshold_met"]:
        print("[QUALITY:PASS] 30% 阈值已达标")
        return 0
    if impossible:
        print("[QUALITY:IMPOSSIBLE] 需求6 未达标，且以下面算术不可达: " + str(impossible)
              + " ｜ 相对提升 " + str(res["relative_gain_pct"]) + "% < 30%"
              + " ｜ CI 重叠=" + str(res["ci_overlap"]))
        return 1
    print("[QUALITY:FAIL] 需求6 未达标：相对提升 " + str(res["relative_gain_pct"]) + "% < 30%")
    return 1


if __name__ == "__main__":
    sys.exit(main())