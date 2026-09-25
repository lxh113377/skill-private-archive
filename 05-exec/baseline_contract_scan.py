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
import importlib.util
import json
import re
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


def _ratchet_metric_names():
    """从 ratchet_gate 单源取 METRIC_NAMES；取不到一律抛，交调用方按 R247 判失败（禁当作一致）。"""
    p = HERE / "ratchet_gate.py"
    spec = importlib.util.spec_from_file_location("ratchet_gate_for_contract", str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return set(mod.METRIC_NAMES)


def inv_ratchet_metric_set(doc, arg):
    """M-2（挂账 3 轮，r38 清偿）：基线指标键集合必须与 ratchet_gate.METRIC_NAMES **全等**。

    根因：棘轮只遍历 `METRIC_NAMES`，而基线 JSON 是**另一份**键集合。两者一旦漂移：
    基线**多**出来的键 = 僵尸基线（没人再产出，白占审计面）；基线**少**出来的键 = 该指标
    **从此没有基线**，`ratchet_gate` 现场取不到基线时按新值放行 ⇒ **静默失去回归保护**
    （r34 加第 6 指标时就是靠手工同步两份文件，无机器护栏）。
    """
    try:
        want = _ratchet_metric_names()
    except Exception as e:
        return ["RATCHET-SET: 取不到 ratchet_gate.METRIC_NAMES（%s: %s）—— 不得判集合一致（R247）"
                % (type(e).__name__, e)]
    got = set((doc.get("metrics") or {}).keys())
    msgs = []
    if not got:
        return ["RATCHET-SET: metrics 为空面，禁判一致（R247）"]
    missing = sorted(want - got)
    extra = sorted(got - want)
    if missing:
        msgs.append("RATCHET-SET: 基线缺指标 %s（该指标无基线 = 棘轮静默放行，回归保护失效）" % missing)
    if extra:
        msgs.append("RATCHET-SET: 基线多指标 %s（ratchet_gate 已不再产出 = 僵尸基线）" % extra)
    return msgs


def inv_ratchet_hardcap_subset(doc, arg):
    caps = set((doc.get("hard_caps") or {}).keys())
    metrics = set((doc.get("metrics") or {}).keys())
    orphan = sorted(caps - metrics)
    return ["HARD-CAP: %s 设了硬顶却不在 metrics 里（硬顶无主，永不触发）" % orphan] if orphan else []


RETRIEVAL_CUTOFF = "2026-09-25T17:00:00"     # 代际分叉点：早于此的历史件不追判（台账/证据件不可回写，同 r48 W-17）


def inv_opponent_claims_have_retrieval(doc, arg):
    """外部取证件必须声明「取的是哪一面」并给两条独立取值命令（r51 W-28）。

    存在理由（r51 实测，两处都在我自己写的数上）：
      · r38 引用的对手 open issues 287/401/1290/118/25 取自 REST `open_issues_count`，
        **该字段含 PR**；search API 纯 issue 面 = 134/143/368/58/17 ⇒ 虚高 1.5–3.5 倍；
      · r50 又发现 `/actions/workflows` 总计面混有平台 `dynamic/*` ⇒ workflow 数同样错面。
    同族根因 = **取证件没声明自己读的是哪一面，也没留第二条路**。同一份 r38 件里
    "最老 open 日期"却 5/5 逐条复现 ⇒ 错的是计数列，不是整份件 —— 这正说明判据该锁列不锁件。
    入参 arg：调度器实际传的是**不变式名字符串**（见 INVARIANTS 派发处），不是配置值。
    ⇒ 只有形如 `2026-09-25T17:00:00` 的字符串才当分叉点用，其余（含名字本身）一律回落默认值。
    这个坑是本轮实跑接线的副产品：按名字比较时 `"2026-.." < "opponent_.."` 恒真，
    会让**全部**证据件被字典序豁免，判据当场静默失效而夹具（传 True）照样全绿。
    """
    cut = (arg if isinstance(arg, str) and re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", arg)
           else RETRIEVAL_CUTOFF)
    gen = str(doc.get("generated_at") or "")
    exempt = bool(gen) and gen < cut
    msgs = []
    # 按**结构**识别外部引用数字：任何顶层列表里带 `repo` 字段的 dict 都算，不锁死键名
    # （`opponents`/`repos`/`peers`/`benchmarks` 同视）—— 否则改个键名即可绕过本判据
    # （与「文档引用违禁词=规则本体」的豁免滥用同族）。
    items = []
    for val in (doc.values() if isinstance(doc, dict) else []):
        if isinstance(val, list):
            items += [x for x in val if isinstance(x, dict) and "repo" in x]
    if not items:
        if isinstance(doc, dict) and isinstance(doc.get("opponents"), list):
            return ([] if exempt else
                    ["opponents 为空数组：空面不得当「已复核」（R247 禁判零通过）"])
        return []                       # 不适用（没有外部引用数字）—— 不得凭空造红
    if exempt:
        return []
    if not str(doc.get("claims_face") or "").strip():
        msgs.append("件级缺 claims_face：未声明这些数字取的是哪一面（issues / issues+PR / 全量…）")
    for it in items:
        repo = str(it.get("repo") or "?")
        ret = str(it.get("retrieval") or "").strip()
        if not ret:
            msgs.append("opponents[%s] 缺 retrieval ⇒ 数字不可复算" % repo)
            continue
        paths = [s for s in re.split(r"[;；\n]", ret) if s.strip()]
        if len(paths) < 2:
            msgs.append("opponents[%s] retrieval 不足两条独立取值命令（须 ≥2 条，单路即错面风险）" % repo)
        elif repo != "?" and repo not in ret:
            msgs.append("opponents[%s] retrieval 里未出现该 repo 名 ⇒ 命令取的是别的对象，疑似顶包" % repo)
    return msgs


def inv_conflict_no_dead_inputs(doc, arg):
    """r40 L-4：冲突扫描器的输入面必须"声明 == 实存"。

    扫描器自身已把 `files_missing` 透明打印（9/10 存在），但**契约此前不看这一项** ⇒
    死条目可以长期存在而 [CONTRACT:PASS] 照绿。本不变式把"取不到的权威源"升格为违规：
    要么补回真实路径（不得靠删条目把覆盖面做小），要么显式承认少扫。
    """
    ev = doc.get("input_evidence") or {}
    declared = ev.get("files_declared", ev.get("files_listed"))
    present = ev.get("files_present")
    missing = ev.get("files_missing") or []
    if "files_declared" not in ev:
        # 代际豁免：files_declared 是 r40 才新增的自证字段，历史产物写不出它，
        # 按 R241 不得被回溯判红（判据只约束会写该字段的今后产物）。
        return []
    if declared is None or present is None:
        # 代际豁免：files_declared 是 r40 才落的自证字段，历史记录写不出它不能被回溯判红
        # （与 R241「历史只加注不改写」同理）。判据只约束**会写该字段的今后产物**。
        return []
    if missing:
        return ["CONFLICT-INPUT: 存在死输入条目 %s（声明 %s 实存 %s）" % (missing, declared, present)]
    return [] if declared == present else [
        "CONFLICT-INPUT: files_declared=%s != files_present=%s 却无 missing 名单（自相矛盾）"
        % (declared, present)]


def inv_debt_class_sum(doc, arg):
    """r38 第十四维：三分类之和必须 == open_total（判据漏桶即红，X-7 同族）。"""
    ev, by = doc.get("evidence") or {}, doc.get("by_class") or {}
    total = ev.get("open_total")
    if total is None or not by:
        return ["DEBT-CLASS: evidence.open_total 或 by_class 缺失，不得判自洽（R247）"]
    s = sum(by.values())
    return [] if s == total else ["DEBT-CLASS: 分类之和 %d != open_total %d（有未闭环条目没被任何一类接住）"
                                  % (s, total)]


def inv_debt_taxonomy_complete(doc, arg):
    """声明的分类态必须与实际计数态一一对应（跨代际通用：v1 四态 / v2 五态都须自洽）。写死集合会在下一次加分层时把历史证据件全判脏（r39 实测踩到：加 DEFERRED 后昨天的 v1 件全体 CONTRACT:FAIL）。自洽式既不豁免任何一代，又能抓住「把某态从 taxonomy 摘掉以并入绿态」的伪装（t27 反例仍红）。"""
    declared = set(doc.get('verdict_taxonomy') or [])
    counted = set((doc.get('by_class') or {}).keys())
    if not declared or not counted:
        return ['debt taxonomy/by_class 有一方为空，不得判自洽（R247）']
    msgs = []
    if counted - declared:
        msgs.append('debt by_class 出现未声明态 %s（分类面被改过）' % sorted(counted - declared))
    ghost = declared - counted - {'CLOSED'}
    if ghost:
        msgs.append('debt verdict_taxonomy 声明却无计数 %s（少一类即可能把该态静默并入绿态）' % sorted(ghost))
    return msgs


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
    "ratchet_metric_set_matches": inv_ratchet_metric_set,
    "ratchet_hardcap_subset": inv_ratchet_hardcap_subset,
    "debt_class_sum": inv_debt_class_sum,
    "debt_taxonomy_complete": inv_debt_taxonomy_complete,
    "conflict_no_dead_inputs": inv_conflict_no_dead_inputs,
    "opponent_claims_have_retrieval": inv_opponent_claims_have_retrieval,
}


def validate_jsonl(rows, contract, label="doc"):
    """r33：JSONL 台账类产物的逐行契约（M-1′）。

    为什么必须有：`06-benchmark/gate_runs.jsonl` 是 r32 第 6 门 `gate_run_freshness` 的**唯一证据面**。
    此前它不在任何契约面内 ⇒ 谁都能把它写坏（缺键 / 第三种 origin / 坏 ts），
    而 freshness 只会把坏数据读成 UNVERIFIED 或**更糟：把 cron 来源当本机记录放行**。
    判据形状缺陷教训（r31 D4）：**取值域必须逐字段枚举**，不得只查"键在不在"。
    """
    msgs = []
    if not rows:
        return ["%s: 0 行（台账为空，禁判「无行=无违规」，R247）" % label]
    req = contract.get("row_required", [])
    enum = contract.get("row_enum", {}) or {}
    fmt = contract.get("row_ts_format")
    # r48 W-17：代际分叉必填。台账是 append-only 不可回写，把新列直接加进 row_required 会把
    # r38–r45 的合法历史行全体判脏（同族 r42 D36）。故按 ts 划代：早于分叉点豁免，晚于分叉点强制。
    req_from = contract.get("row_required_from") or []
    if isinstance(req_from, dict):        # 单代写法仍合格；多代（台账列分批加入）用列表
        req_from = [req_from]
    gens = [(g.get("from"), g.get("fields") or []) for g in req_from]
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            msgs.append("%s row %d: 非对象行（JSONL 每行须为一个 JSON 对象）" % (label, i))
            continue
        for cut, extra_req in gens:
            if extra_req and (not cut or str(row.get("ts") or "") >= cut):
                xmiss = [k for k in extra_req if k not in row]
                if xmiss:
                    msgs.append("%s row %d: 缺分代必填列 %s（ts=%s 晚于分叉点 %s）"
                                % (label, i, xmiss, row.get("ts"), cut))
        miss = [k for k in req if k not in row]
        if miss:
            msgs.append("%s row %d: 缺键 %s" % (label, i, miss))
        for k, allowed in enum.items():
            if k in row and row[k] not in allowed:
                msgs.append("%s row %d: %s 取值域违规=%r（允许 %s）" % (label, i, k, row[k], allowed))
        if fmt and "ts" in row:
            try:
                datetime.strptime(str(row["ts"]), fmt)
            except ValueError:
                msgs.append("%s row %d: ts 形态非法=%r（须匹配 %s）" % (label, i, row["ts"], fmt))
    return msgs


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


def face_pattern_staleness(matched_files, cur_round, max_age_days=14, max_gap=2):
    """W-31（r52）+ r53 修正：契约 pattern 的新旧面。

    r53 自抓的假阳性：`catalog_attention_tax_2026-09-24.json` 是本轮**刚重跑**的产物，
    只因文件名不带轮号，被上一版按 `_rNN` 判成"落后 33 轮"。名字不等于新鲜度 ⇒
    优先级改为 ① 文件 mtime（真实再生时间）② 文件名轮号（仅对取不到 mtime 的构造样本兜底）。
    两者都取不到 ⇒ 不参与判定（记 note，不冒充已核验）。
    """
    import time as _t
    out = []
    for pattern, files in matched_files:
        ages, rounds = [], []
        for fp in files:
            name = Path(str(fp)).name
            m = re.search(r"_r(\d{1,3})", name)
            if m:
                rounds.append(int(m.group(1)))
            try:
                ages.append(_t.time() - Path(str(fp)).stat().st_mtime)
            except OSError:
                continue
        newest_age_days = min(int(a // 86400) for a in ages) if ages else None
        max_round = max(rounds) if rounds else None
        gap = (cur_round - max_round) if (cur_round and max_round is not None) else None
        if newest_age_days is not None:
            stale = newest_age_days > max_age_days
        elif gap is not None:
            stale = gap > max_gap
        else:
            stale = False
        out.append({"pattern": pattern, "files": len(files), "max_round": max_round, "gap": gap,
                    "newest_age_days": newest_age_days, "stale": stale,
                    "basis": ("mtime" if newest_age_days is not None
                              else ("round" if gap is not None else "无数据不参与"))})
    return out


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
            if fp.suffix == ".jsonl":   # r33：台账类产物走逐行契约
                lines = []
                for ln in fp.read_text(encoding="utf-8-sig").splitlines():
                    ln = ln.strip()
                    if not ln:
                        continue
                    try:
                        lines.append(json.loads(ln))
                    except ValueError:
                        lines.append(ln)      # 原样传给 validate_jsonl，由它报「非对象行」
                v = validate_jsonl(lines, contract, fp.name)
                bad_count += len(v)
                all_msgs += ["%s: %s" % (fp.name, m) for m in v]
                if not args.quiet:
                    print("%-46s %-24s 违规 %d（%d 行）" % (fp.name, pattern, len(v), len(lines)))
                continue
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
    # W-31（r52）：契约自身的新旧面 —— 光查"有没有命中"不够，还要查"命中的是不是最新一代"
    _rr = re.compile(r"_r(\d{1,3})")
    _all_rounds = [int(m.group(1)) for _, fs in matched for f in fs for m in [_rr.search(Path(str(f)).name)] if m]
    faces = face_pattern_staleness(matched, max(_all_rounds) if _all_rounds else None)
    for f in faces:
        if f.get("stale"):
            print("  ⚠️ 陈旧面 %s：最新件距今天数=%s ｜ 命中最大轮号=r%s（gap=%s）｜ 依据=%s"
                  % (f["pattern"], f["newest_age_days"], f["max_round"], f["gap"], f["basis"]))
    print("  陈旧自检（W-31，只报告不判红）：pattern %d 个 ｜ 陈旧 %d 个 ｜ 无轮号形态 %d 个"
          % (len(faces), sum(1 for f in faces if f.get("stale")),
             sum(1 for f in faces if f.get("max_round") is None)))
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
