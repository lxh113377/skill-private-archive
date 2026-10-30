# -*- coding: utf-8 -*-
r"""r302_r260_input_pin_fixtures.py — r260 自检「输入指纹」三腿夹具（腿 a 保牙 / 腿 b 真数据 / 腿 c 反向）。

存在理由（r302 一手）：r260_local_baseline 的复现自检原先只比 score5，分不清「量尺漂移」与「输入刷新」。
本夹具不重写判据（复刻即双源，R241）——它 import 生产件的 reproduce_selfcheck() / input_pin() /
selfcheck_pass()，用合成数据与自有真数据各跑三腿，证明修完仍有牙、且两种证据不互相吞并：

  腿 a（保牙，最重要）：同一份 doc 两侧（矩阵记录侧与活件侧）指纹相同，但记录侧 score5 被人为改一档
    ⇒ mismatches 必须 >0 且 selfcheck_pass=False。这证明「量尺漂移」仍被抓得住。
  腿 b（自有真数据）：拿 r300 刷新过的 vercel-labs/agent-browser（r225 记录严格口径 SKILL.md 件数=10，
    现活件=11）⇒ 必须判 stale_input（两枚 pin 不同）而不是 mismatch，且其 score5 确实变了（fc 3 升 4）。
  腿 c（反向）：一次自检同时喂「pin 变 + score5 变」与「pin 同 + score5 变」两枚候选 ⇒ stale_input_n 与
    mismatches 必须同时 ≥1（两条腿不能互相吞掉），且 stale 样例里不出现漂移候选、漂移样例里不出现 stale 候选。

判据命令：python 05-exec/r302_r260_input_pin_fixtures.py  ⇒ 末行 [R302:PASS]。
退出码：0 三腿全过 / 1 任一腿失败（判据无牙或两腿互相吞掉）/ 2 生产件不可导入（禁复刻，硬断裂）。
用法：
  python 05-exec/r302_r260_input_pin_fixtures.py
  python 05-exec/r302_r260_input_pin_fixtures.py --json _temp/r302_input_pin_fixtures.json
"""
import argparse
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")
MATRIX = os.path.join(BENCH, "replacement_matrix_r225.json")
TOKEN = "[R302:%s]"


def import_production():
    """取生产件的判据函数（单源；取不到 rc=2，禁自写近似副本）。"""
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    try:
        import r260_local_baseline as base
        import r114_replacement_scan as scan
    except Exception as exc:  # noqa: BLE001 - 导入失败是硬断裂，必须显形成读数
        return None, None, "import_fail:%r" % (exc,)
    for name in ("reproduce_selfcheck", "input_pin", "pin_changed_fields", "selfcheck_pass",
                 "PIN_FIELDS", "INPUT_PIN_VERSION"):
        if not hasattr(base, name):
            return None, None, "symbol_missing:%s" % name
    for name in ("score5", "load_cache", "key_of"):
        if not callable(getattr(scan, name, None)):
            return None, None, "symbol_missing:r114.%s" % name
    return base, scan, None


def base_doc(repo):
    """合成一份缓存 doc（字段名与 r114 measure_repo 的落盘同名；取值中档，避开分档边界）。"""
    return {
        "state": "OK", "stars": 1000, "forks": 10, "pushed_at": "2026-10-01",
        "created_at": "2025-01-01", "archived": False, "license": "MIT",
        "open_issues": 1, "description": "r302 fixture repo", "topics": [],
        "default_branch": "main", "homepage": "",
        "tree_state": "OK", "tree_truncated": False, "blob_n": 120,
        "skill_md_n": 3, "skill_md_exact_n": 3, "skill_md_ghost_n": 0,
        "workflow_n": 1, "test_path_n": 5, "readme_n": 1, "docs_md_n": 2,
        "_repo": repo,
    }


def as_recorded(base, scan, doc, score5_override=None, score_total_override=None):
    """把一份 doc 折成矩阵记录的形态：只留 PIN_FIELDS 加 score5/score_total（矩阵就是这么落的）。"""
    cand = dict((k, doc[k]) for k in base.PIN_FIELDS if k in doc)
    cand["repo"] = doc.get("_repo") or "fixture/repo"
    s, t, _cal = scan.score5(doc, license_cap=True)
    cand["score5"] = s if score5_override is None else dict(score5_override)
    cand["score_total"] = t if score_total_override is None else score_total_override
    return cand


def as_live(doc):
    """记录侧 doc 折成活件侧缓存 doc（去掉夹具私有的 _repo 键）。"""
    live = dict(doc)
    live.pop("_repo", None)
    return live


def leg_a(base, scan):
    """保牙腿：同一 doc、指纹相同，记录侧 score5 人为改一档 ⇒ 必须判漂移。"""
    doc = base_doc("fixture/leg_a")
    live = as_live(doc)
    s, t, _cal = scan.score5(live, license_cap=True)
    fake = dict(s)
    fake["fc"] = max(0, s["fc"] - 1)          # 只动一档：模拟「输入没变、尺子行为变了」
    rec = as_recorded(base, scan, doc, score5_override=fake, score_total_override=sum(fake.values()))
    cache = {"repo__" + scan.key_of(rec["repo"]): live}
    mrows = [{"slug": "fixture-leg-a", "candidates": [rec]}]
    sc = base.reproduce_selfcheck(scan, cache, mrows)
    out = {
        "pins_equal": base.input_pin(rec) == base.input_pin(live),
        "recorded_score5": rec["score5"], "recomputed_score5": s,
        "mismatches": sc["mismatches"], "stale_input_n": sc["stale_input_n"],
        "unknown_n": sc["unknown_n"], "pinned_scored_n": sc["pinned_scored_n"],
        "mismatch_examples": sc["mismatch_examples"],
        "selfcheck_pass": base.selfcheck_pass(sc, True, True),
        "expect": "pins_equal=True 且 mismatches>0 且 selfcheck_pass=False",
    }
    out["pass"] = bool(out["pins_equal"] and sc["mismatches"] > 0 and out["selfcheck_pass"] is False)
    return out


def leg_b(base, scan):
    """真数据腿：r300 刷新过的 vercel-labs/agent-browser（r225 记录 加 现读缓存）⇒ 必须 stale。"""
    if not os.path.isfile(MATRIX):
        return {"pass": False, "reason": "matrix_missing"}
    matrix = json.load(io.open(MATRIX, encoding="utf-8"))
    cand = None
    for row in matrix.get("rows") or []:
        if row.get("slug") == "agent-browser":
            for c in row.get("candidates") or []:
                if c.get("repo") == "vercel-labs/agent-browser":
                    cand = c
    if cand is None:
        return {"pass": False, "reason": "r225_record_not_found"}
    cache = scan.load_cache()
    key = "repo__" + scan.key_of(cand["repo"])
    live = cache.get(key)
    if not live or live.get("state") != "OK":
        return {"pass": False, "reason": "live_cache_unavailable"}
    live = dict(live)
    sc = base.reproduce_selfcheck(scan, {key: live}, [{"slug": "agent-browser", "candidates": [cand]}])
    want, got = base.input_pin(cand), base.input_pin(live)
    s_now, _t_now, _cal = scan.score5(live, license_cap=True)
    out = {
        "repo": cand["repo"],
        "recorded_skill_md_exact_n": cand.get("skill_md_exact_n"),
        "live_skill_md_exact_n": live.get("skill_md_exact_n"),
        "recorded_pin": want, "live_pin": got, "pins_differ": want != got,
        "changed_fields": base.pin_changed_fields(cand, live),
        "recorded_score5": cand.get("score5"), "recomputed_score5": s_now,
        "stale_input_n": sc["stale_input_n"], "stale_input_rank0_n": sc["stale_input_rank0_n"],
        "stale_input_examples": sc["stale_input_examples"],
        "mismatches": sc["mismatches"], "unknown_n": sc["unknown_n"],
        "expect": "pins_differ=True 且 stale_input_n>=1 且 mismatches==0（不得读成漂移）",
    }
    out["pass"] = bool(want != got and sc["stale_input_n"] >= 1 and sc["mismatches"] == 0)
    return out


def leg_c(base, scan):
    """反向腿：同一轮里既有「pin 变」又有「pin 同 + score5 变」⇒ 两计数器必须同时非空。"""
    old_a = base_doc("fixture/leg_c_stale")
    doc_b = base_doc("fixture/leg_c_drift")
    live_a = as_live(old_a)
    live_b = as_live(doc_b)
    rec_a = as_recorded(base, scan, old_a)                 # 记录侧：严格口径件数 3
    live_a["skill_md_exact_n"] = 7                        # 活件侧：件数 3 升到 7 ⇒ pin 必不同
    live_a["skill_md_n"] = 7
    s_b, _t_b, _calb = scan.score5(live_b, license_cap=True)
    fake_b = dict(s_b)
    fake_b["docs"] = max(0, s_b["docs"] - 1)              # 记录侧只改一档 ⇒ pin 同、分不同
    rec_b = as_recorded(base, scan, doc_b, score5_override=fake_b,
                        score_total_override=sum(fake_b.values()))
    cache = {"repo__" + scan.key_of("fixture/leg_c_stale"): live_a,
             "repo__" + scan.key_of("fixture/leg_c_drift"): live_b}
    mrows = [{"slug": "fixture-leg-c-stale", "candidates": [rec_a]},
             {"slug": "fixture-leg-c-drift", "candidates": [rec_b]}]
    sc = base.reproduce_selfcheck(scan, cache, mrows)
    stale_repos = [e["repo"] for e in sc["stale_input_examples"]]
    mismatch_repos = [e["repo"] for e in sc["mismatch_examples"]]
    out = {
        "stale_input_n": sc["stale_input_n"], "mismatches": sc["mismatches"],
        "pinned_scored_n": sc["pinned_scored_n"],
        "stale_examples_repos": stale_repos, "mismatch_examples_repos": mismatch_repos,
        "stale_candidate_pins_differ": base.input_pin(rec_a) != base.input_pin(live_a),
        "drift_candidate_pins_equal": base.input_pin(rec_b) == base.input_pin(live_b),
        "expect": "stale_input_n>=1 且 mismatches>=1，两清单互不包含对方候选",
    }
    out["pass"] = bool(sc["stale_input_n"] >= 1 and sc["mismatches"] >= 1
                       and out["stale_candidate_pins_differ"] and out["drift_candidate_pins_equal"]
                       and "fixture/leg_c_drift" not in stale_repos
                       and "fixture/leg_c_stale" not in mismatch_repos)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="", help="可选：把三腿读数落盘")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001 - 老解释器无 reconfigure，不因此判死整轮
        pass
    base, scan, err = import_production()
    if base is None:
        print(TOKEN % "UNVERIFIED", "生产件导入失败 ⇒ 禁复刻，rc=2 ｜", err)
        return 2
    legs = {
        "a_scale_drift_keeps_teeth": leg_a(base, scan),
        "b_real_refreshed_repo_is_stale": leg_b(base, scan),
        "c_stale_and_drift_coexist": leg_c(base, scan),
    }
    order = ("a_scale_drift_keeps_teeth", "b_real_refreshed_repo_is_stale",
             "c_stale_and_drift_coexist")
    all_pass = True
    for name in order:
        lg = legs[name]
        ok = bool(lg.get("pass"))
        all_pass = all_pass and ok
        print("腿 {0}：{1} ｜ {2}".format(name, "PASS" if ok else "FAIL", lg.get("expect", "")))
        print("  逐字读数：" + json.dumps(lg, ensure_ascii=False, sort_keys=True))
    doc = {"schema": "r302-input-pin-fixtures-v1", "input_pin_version": base.INPUT_PIN_VERSION,
           "legs": legs, "status": "COMPLETE" if all_pass else "FAIL"}
    if args.out:
        tmp = args.out + ".tmp"
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, args.out)
    if not all_pass:
        print(TOKEN % "FAIL", "三腿未全过（判据无牙或两腿互相吞掉）")
        return 1
    print(TOKEN % "PASS", "腿 a 保牙 + 腿 b 真数据 stale + 腿 c 反向共存 ｜ input_pin_version={0}".format(
        base.INPUT_PIN_VERSION))
    return 0


if __name__ == "__main__":
    sys.exit(main())