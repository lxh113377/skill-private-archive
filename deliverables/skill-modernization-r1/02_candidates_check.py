#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""t2 候选覆盖判据：逐件 3-5 候选 + 元数据实测 + 维护筛选 + 负向对照。

判据不采信候选自带的 maintenance/activity 标签，一律从 metadata.pushed_at 与
metadata.archived 现场重算 365 天阈值；负控故意把停摆仓标签写成 active，判据
必须仍报红，证明筛选有牙而不是恒绿。
"""
import argparse, io, json, os, sys
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(HERE, "data", "candidates.json")
TEMP = os.path.join(ROOT, "_temp")
NEGCTRL = os.path.join(TEMP, "t2_candidates_negctrl.json")
REQUIRED_JQ = [".stargazers_count", ".pushed_at", ".license.spdx_id", ".archived"]

def load(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)

def maintenance_filter(cand, threshold):
    m = cand.get("metadata") or {}
    if m.get("archived"):
        return "archived"
    p = str(m.get("pushed_at") or "")[:10]
    if len(p) != 10:
        return "unknown_field"
    try:
        d = date.fromisoformat(p)
    except ValueError:
        return "unparsable_pushed_at"
    if d < threshold:
        return "stale_pushed_at"
    return "active"

def check(obj):
    reasons = []
    if obj.get("schema") != "t2-replacement-candidates-v1":
        reasons.append("schema 非 t2-replacement-candidates-v1")
    sc = obj.get("scope") or {}
    if sc.get("denominator") != 77:
        reasons.append("迁移范围分母 != 77")
    bc = sc.get("by_class") or {}
    if sum(int(bc.get(k, -1)) for k in ("HIGH", "MID", "LOW", "EXCLUDE")) != 150:
        reasons.append("清单分类之和 != 150")
    rows = obj.get("rows") or []
    if len(rows) != 77:
        reasons.append("rows != 77")
    slugs = [r.get("slug") for r in rows]
    if len(set(slugs)) != len(slugs):
        reasons.append("slug 重复")
    try:
        threshold = date.fromisoformat(obj.get("eval_date")) - timedelta(days=365)
    except Exception:
        threshold = date(2025, 11, 7)
        reasons.append("eval_date 不可解析，回退默认阈值")
    total = 0
    measured = 0
    cmd_ok = 0
    active_ok = 0
    pads_ok = True
    for r in rows:
        if r.get("class") not in ("HIGH", "MID"):
            reasons.append("类外行 " + str(r.get("slug")))
        cands = r.get("candidates") or []
        if not (3 <= len(cands) <= 5):
            reasons.append("候选数越界 " + str(r.get("slug")) + " n=" + str(len(cands)))
        if r.get("candidates_n") != len(cands):
            reasons.append("candidates_n 与实长不符 " + str(r.get("slug")))
        for c in cands:
            total += 1
            m = c.get("metadata") or {}
            cmds = c.get("metadata_commands") or []
            if m.get("state") == "OK" and m.get("stars") is not None and m.get("pushed_at") and m.get("license"):
                measured += 1
            else:
                reasons.append("元数据未实测 " + str(c.get("repo")))
            joined = " ".join(cmds)
            if len(cmds) >= 4 and all(("gh api repos/" in x) for x in cmds[:4]) and all(k in joined for k in REQUIRED_JQ):
                cmd_ok += 1
            else:
                reasons.append("取值命令不全 " + str(c.get("repo")))
            if "✅" not in str(c.get("evidence_status") or ""):
                reasons.append("未标 ✅已实测 " + str(c.get("repo")))
            if c.get("not_replacement"):
                reasons.append("族级补位件混入候选 " + str(c.get("repo")))
            res = maintenance_filter(c, threshold)
            if res == "active":
                active_ok += 1
            else:
                reasons.append("维护筛选剔除 " + str(c.get("repo")) + " -> " + res)
        for p in (r.get("family_pads") or []):
            if not p.get("not_replacement"):
                pads_ok = False
    if not pads_ok:
        reasons.append("family_pads 未标 not_replacement")
    nc = obj.get("negative_control") or {}
    if not (nc.get("injected_days_since_push", 0) > 365 and nc.get("expected_filter_result") == "stale_pushed_at"):
        reasons.append("负控配置缺失或阈值失配")
    cov = obj.get("coverage") or {}
    if cov.get("rows") != 77 or cov.get("all_candidates_measured") is not True:
        reasons.append("coverage 自证字段不自洽")
    if len(obj.get("self_verify") or []) < 3:
        reasons.append("自证命令不足 3 条")
    if not (obj.get("gate") or {}).get("verdict"):
        reasons.append("门禁 verdict 未如实登记")
    stats = {"rows": len(rows), "candidates": total, "measured": measured,
             "cmd_ok": cmd_ok, "active_ok": active_ok, "threshold": threshold.isoformat()}
    return (len(reasons) == 0), reasons, stats

def stale_fixture():
    r = "trimstray/test-your-sysadmin-skills"
    return {"repo": r, "url": "https://github.com/" + r,
            "candidate_class": "negative_control_fixture",
            "metadata": {"state": "OK", "stars": 11898,
                         "pushed_at": "2024-11-19T14:07:11Z", "license": "MIT",
                         "archived": False,
                         "measured_at": "2026-11-06T19:07:01.413113+00:00"},
            "metadata_commands": ["gh api repos/" + r + " --jq " + k for k in REQUIRED_JQ],
            "metadata_command": "gh api repos/" + r + " --jq '[.stargazers_count,.pushed_at,.license.spdx_id,.archived]'",
            "evidence_status": "✅已实测（GitHub 元数据）",
            "maintenance": "active", "activity": "活跃(718d)",
            "match_reason": "负控夹具：标签故意写 active，pushed_at 实为 2024-11-19"}

def negative_control(obj):
    fixture = stale_fixture()
    mutated = json.loads(json.dumps(obj))
    row = mutated["rows"][0]
    row["candidates"].append(fixture)
    row["candidates_n"] = len(row["candidates"])
    mutated["coverage"]["candidates_total"] = int(mutated["coverage"]["candidates_total"]) + 1
    ok, reasons, stats = check(mutated)
    thr = date.fromisoformat(mutated["eval_date"]) - timedelta(days=365)
    recomputed = maintenance_filter(fixture, thr)
    print("NEGCTRL_LABEL " + fixture["repo"] + " 标签=" + fixture["maintenance"] + " 实算=" + recomputed + "（判据不采信标签）")
    print("NEGCTRL_ACTIVE rlaope/oh-my-hermes -> " + maintenance_filter({"metadata": {"pushed_at": "2026-11-06T19:21:23Z", "archived": False}}, thr) + "（保留）")
    print("NEGCTRL_ARCHIVED PleasePrompto/notebooklm-skill -> " + maintenance_filter({"metadata": {"pushed_at": "2026-09-10T07:43:47Z", "archived": True}}, thr) + "（剔除）")
    hit = any(("trimstray/test-your-sysadmin-skills" in x and "stale_pushed_at" in x) for x in reasons)
    with io.open(NEGCTRL, "w", encoding="utf-8", newline=chr(10)) as f:
        f.write(json.dumps(mutated, ensure_ascii=False))
    try:
        if ok:
            print("[NEGCTRL:UNEXPECTED_GREEN] 塞入停摆仓后判据仍绿 = 判据无牙")
            return 1
        if not hit:
            print("[NEGCTRL:UNEXPECTED_REASON] 报红但不是停摆仓触发: " + " ; ".join(reasons[:4]))
            return 1
        print("[NEGCTRL:RED] 故意塞入停摆仓 " + fixture["repo"] + "（pushed_at=" + fixture["metadata"]["pushed_at"] + "，718d）后判据报红（符合预期）: " + " ; ".join(x for x in reasons if "trimstray" in x))
        return 0
    finally:
        if os.path.exists(NEGCTRL):
            os.remove(NEGCTRL)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--negative-control", action="store_true")
    args = ap.parse_args()
    obj = load(DATA)
    ok, reasons, stats = check(obj)
    if args.negative_control:
        return negative_control(obj)
    if not ok:
        print("[CANDIDATES:FAIL] " + " ; ".join(reasons[:10]))
        return 1
    print("[CANDIDATES:PASS] 分母=77 rows=%d 逐件候选 3-5=True 元数据实测=%d/%d 取值命令=%d/%d 维护筛选=active %d/%d 阈值=%s 族级补位未计入=True 负控配置=OK" %
          (stats["rows"], stats["measured"], stats["candidates"], stats["cmd_ok"],
           stats["candidates"], stats["active_ok"], stats["candidates"], stats["threshold"]))
    return 0

if __name__ == "__main__":
    sys.exit(main())
