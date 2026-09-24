# -*- coding: utf-8 -*-
"""baseline_contract_scan.py — 本仓机器证据（06-benchmark/*.json）契约校验器（R19-3 / 报告 N13）。

对标 `sickn33/agentic-awesome-skills` 的 `schemas/aas-v1/`：把「产物结构」从散文约定升级为
**可机检的版本化契约**，从「事后发现下游读不到字段」改成「事前拒收」。
契约定义：`05-exec/schemas/r19/baseline-contracts.json`（单一真相源，本脚本不内联结构）。

根因（实测）：r19 把 `cumulative-drift-scan` 的 schema 由 v1 升到 v2 并新增 `excluded` 字段，
下游若仍按 v1 读会**静默拿不到排除面**——这类漂移在 r18/r19 已出现两次（description 三口径键、
excluded 字段），而本仓此前无任何契约校验面。

判据三族：`schema_id` 字面量 / `required` 必填点路径 / `types` 类型 / `invariants` 具名不变式。
R247 硬门：契约面为空、或某 pattern 命中 0 个文件 ⇒ 判 FAIL（禁「无文件 = 无违规」）。

用法：
    python 05-exec/baseline_contract_scan.py [--dir 06-benchmark] [--json out.json] [--quiet]
退出码：0 = 全部合规 / 1 = 有违规或契约面空 / 2 = 契约文件不可读
"""

import argparse
import fnmatch
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTRACT_FILE = HERE / "schemas" / "r19" / "baseline-contracts.json"
DEFAULT_DIR = HERE.parent / "06-benchmark"

TYPE_MAP = {"str": str, "int": int, "bool": bool, "list": list, "dict": dict, "num": (int, float)}


def load_contracts(path=None):
    """读契约；失败时返回带 error 的空 artifacts（调用方必须判空，不得当通过）。"""
    p = Path(path or CONTRACT_FILE)
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        return {"schema": "unavailable", "artifacts": {}, "error": "%s: %s" % (type(e).__name__, e)}
    if not isinstance(data.get("artifacts"), dict):
        return {"schema": data.get("schema"), "artifacts": {}, "error": "契约缺 artifacts 字典"}
    data["path"] = str(p)
    return data


def dig(doc, dotted):
    cur = doc
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False, None
        cur = cur[part]
    return True, cur


# ---------------------------------------------------------------- 不变式注册表
def inv_readonly_true(doc, arg):
    ok, val = dig(doc, "readonly")
    return [] if not ok or val is True else ["readonly: 只读件 readonly 被改为 %r" % (val,)]


def inv_excluded_have_why(doc, arg):
    bad = []
    for i, row in enumerate(doc.get("excluded", []) or []):
        miss = [k for k in ("root", "path", "edits", "why") if not row.get(k) and row.get(k) != 0]
        if miss:
            bad.append("excluded[%d]: 缺字段 %s（排除必须可见）" % (i, miss))
    return bad


def inv_flagged_row_shape(doc, arg):
    bad = []
    for key in ("flagged_ruleish", "flagged_all"):
        for i, row in enumerate(doc.get(key, []) or []):
            if key == "flagged_all" and not isinstance(row, dict):
                continue
            miss = [k for k in ("path", "edits") if k not in row]
            if miss:
                bad.append("%s[%d]: 缺字段 %s" % (key, i, miss))
    return bad


def inv_verdict_taxonomy_complete(doc, arg):
    want = {"drift_detected", "softened", "refinement", "additive", "neutral_rephrase", "uncertain"}
    got = set(doc.get("verdict_taxonomy") or [])
    return [] if want <= got else ["verdict_taxonomy: 缺态 %s" % sorted(want - got)]


def inv_denominator_glob_eq_registry(doc, arg):
    d = doc.get("denominator") or {}
    reg = d.get("registry") or {}
    if not reg.get("available"):
        return []
    msgs = []
    if d.get("glob_total") != reg.get("count"):
        msgs.append("denominator: glob_total=%s != registry.count=%s（分母漂移）"
                    % (d.get("glob_total"), reg.get("count")))
    elif d.get("consistent") is False:
        msgs.append("denominator: consistent=False 但两口径相等（判据自相矛盾）")
    if reg.get("count") != reg.get("skills_len"):
        msgs.append("denominator: 注册表内部 count=%s != skills=%s"
                    % (reg.get("count"), reg.get("skills_len")))
    return msgs


def inv_counts_le_total(doc, arg):
    s = doc.get("summary") or {}
    total = s.get("total", 0)
    return ["summary.%s=%s 超过 total=%s（统计口径 bug）" % (k, s[k], total)
            for k in ("has_desc", "with_trigger", "double_element", "over_cap", "has_process",
                      "no_desc", "errors")
            if isinstance(s.get(k), int) and s[k] > total]


def inv_desc_max_is_official_cap(doc, arg):
    ok, val = dig(doc, "desc_max_official")
    if not ok:
        return []
    return [] if val == 1024 else ["desc_max_official=%s 与官方上限 1024 不符" % val]


def inv_catalog_chars_sum(doc, arg):
    a, b, c = doc.get("desc_chars_total"), doc.get("name_chars_total"), doc.get("grand_chars")
    if None in (a, b, c):
        return []
    return [] if a + b == c else ["grand_chars=%s != desc %s + name %s" % (c, a, b)]


def inv_truth_active_shape(doc, arg):
    t = doc.get("truth") or {}
    active = t.get("active") or []
    msgs = []
    if not active:
        msgs.append("truth.active 为空（真相源读取失败，禁判零失真）")
    elif t.get("n") != len(active):
        msgs.append("truth.n=%s != len(active)=%s" % (t.get("n"), len(active)))
    return msgs


def inv_claim_candidates_shape(doc, arg):
    return ["candidates[%d]: 缺字段 %s" % (i, [k for k in ("family", "file", "line") if k not in row])
            for i, row in enumerate(doc.get("candidates") or [])
            if any(k not in row for k in ("family", "file", "line"))]


def inv_conflict_input_evidence_nonzero(doc, arg):
    ev = doc.get("input_evidence") or {}
    msgs = []
    if not ev.get("files_present"):
        msgs.append("input_evidence.files_present=0（扫描面为空，禁判零冲突 R247）")
    if not ev.get("polarity_rules"):
        msgs.append("input_evidence.polarity_rules=0（规则面为空，禁判零冲突 R247）")
    return msgs


def inv_rubric_pct_within_total(doc, arg):
    n = (doc.get("denominator") or {}).get("scanned", 0)
    return ["per_section.%s 命中数 > scanned=%s" % (k, n)
            for k, v in (doc.get("per_section") or {}).items()
            if isinstance(v, dict) and isinstance(v.get("count"), int) and v["count"] > n]


def inv_scenarios_nonempty(doc, arg):
    sc = doc.get("scenarios")
    return [] if isinstance(sc, list) and sc else ["scenarios 为空（评测集失效）"]


INVARIANTS = {
    "readonly_true": inv_readonly_true,
    "excluded_have_why": inv_excluded_have_why,
    "flagged_row_shape": inv_flagged_row_shape,
    "verdict_taxonomy_complete": inv_verdict_taxonomy_complete,
    "denominator_glob_eq_registry": inv_denominator_glob_eq_registry,
    "counts_le_total": inv_counts_le_total,
    "desc_max_is_official_cap": inv_desc_max_is_official_cap,
    "catalog_chars_sum": inv_catalog_chars_sum,
    "truth_active_shape": inv_truth_active_shape,
    "claim_candidates_shape": inv_claim_candidates_shape,
    "conflict_input_evidence_nonzero": inv_conflict_input_evidence_nonzero,
    "rubric_pct_within_total": inv_rubric_pct_within_total,
    "scenarios_nonempty": inv_scenarios_nonempty,
}


def validate_doc(doc, contract, label="doc"):
    """按契约校验单个文档，返回违规描述列表（空 = 合规）。"""
    msgs = []
    want = contract.get("schema_id")
    if want and doc.get("schema") != want:
        # r31：schema_id 允许「已授权代际清单」（列表）。同一技能的产物在 06-benchmark 里跨轮共存，
        # 一个 glob 只挂一个字面量的假设会让「上游升代」必然表现为一条红 —— 而历史件不该被改写。
        # 列表是**逐代枚举授权**而非放宽匹配：未登记的代际（如 v3）照样拦（夹具 t12 反例实测）。
        allowed = want if isinstance(want, list) else [want]
        if doc.get("schema") not in allowed:
            msgs.append("schema: 期望 %r 实得 %r（契约过期或产物未重建）" % (want, doc.get("schema")))
    for key in contract.get("required", []):
        found, _ = dig(doc, key)
        if not found:
            msgs.append("required: 缺字段 %s" % key)
    for key, tname in (contract.get("types") or {}).items():
        found, val = dig(doc, key)
        if found and not isinstance(val, TYPE_MAP.get(tname, object)):
            msgs.append("types: %s 期望 %s 实得 %s" % (key, tname, type(val).__name__))
    for name in contract.get("invariants", []):
        fn = INVARIANTS.get(name)
        if fn is None:
            msgs.append("invariants: 未知不变式 %s（契约与实现脱节）" % name)
            continue
        msgs += fn(doc, name)
    return msgs


def validate_contracts(contracts, matched_files):
    """契约面自检：空 artifacts / pattern 零命中 ⇒ 必须报，不得静默通过（R247）。
    matched_files: [(pattern, [路径...])]。返回 (messages, rows)。"""
    msgs = []
    artifacts = contracts.get("artifacts") or {}
    if not artifacts:
        return (["CONTRACT-EMPTY: 契约 artifacts 为空%s" % (("（%s）" % contracts.get("error"))
                if contracts.get("error") else "")], [])
    for pattern, files in matched_files:
        if not files:
            msgs.append("pattern %s 命中 0 个文件（无文件不等于通过）" % pattern)
    unknown = [p for p, _ in matched_files if p not in artifacts]
    for p in unknown:
        msgs.append("未知 pattern %s（契约缺定义）" % p)
    return (msgs, [])


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(DEFAULT_DIR))
    ap.add_argument("--contracts", default=str(CONTRACT_FILE))
    ap.add_argument("--json")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    contracts = load_contracts(args.contracts)
    if contracts.get("error"):
        print("[CONTRACT:FAIL] %s" % contracts["error"])
        return 2
    root = Path(args.dir)
    if not root.is_dir():
        print("[CONTRACT:FAIL] 目录不存在: %s" % root)
        return 2

    rows, all_msgs = [], []
    files_checked = 0
    matched = []
    for pattern, contract in contracts["artifacts"].items():
        found = sorted(root.glob(pattern))
        matched.append((pattern, found))
        bad_count = 0
        for fp in found:
            files_checked += 1
            try:
                doc = json.loads(fp.read_text(encoding="utf-8-sig"))
            except ValueError as e:
                all_msgs.append("%s: JSON 解析失败 %s" % (fp.name, e))
                bad_count += 1
                continue
            if not isinstance(doc, dict):
                all_msgs.append("%s: 顶层非对象" % fp.name)
                bad_count += 1
                continue
            v = validate_doc(doc, contract, fp.name)
            bad_count += len(v)
            all_msgs += ["%s: %s" % (fp.name, m) for m in v]
            if not args.quiet:
                print("%-46s %-24s 违规 %d" % (fp.name, pattern, len(v)))
        rows.append({"glob": pattern, "files": len(found), "violations": bad_count})

    cmsgs, _ = validate_contracts(contracts, matched)
    all_msgs += cmsgs
    if not files_checked:
        all_msgs.append("R247: 受检基线为 0 个文件，禁止判「全部合规」")
    print("\n契约: %s（%d 个 pattern / 受检文件 %d 个）" % (
        Path(contracts.get("path", args.contracts)).name, len(contracts["artifacts"]), files_checked))
    if all_msgs:
        print("[CONTRACT:FAIL] 违规 %d 条" % len(all_msgs))
        for m in all_msgs:
            print("  - %s" % m)
    else:
        print("[CONTRACT:PASS] %d 份基线全部合规（结构 + 不变式）" % files_checked)

    if args.json:
        Path(args.json).write_text(json.dumps({
            "schema": contracts.get("schema"), "generated_at": datetime.now().isoformat(timespec="seconds"),
            "contract_file": contracts.get("path"), "dir": str(root),
            "files_checked": files_checked, "artifacts": rows,
            "violations_total": len(all_msgs), "violations_detail": all_msgs,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print("JSON -> %s" % args.json)
    return 1 if all_msgs else 0


if __name__ == "__main__":
    raise SystemExit(main())
