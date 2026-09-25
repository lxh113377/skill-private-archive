# -*- coding: utf-8 -*-
"""r19_baseline_contract_fixtures.py — R19-3 基线契约校验器的夹具（TDD：先写测试并看它红）。

契约面（对标 sickn33/agentic-awesome-skills `schemas/aas-v1/` 的「事前拒收」思路，
缩小到本项目自持范围）：`06-benchmark/*.json` 是本仓唯一可复跑的机器证据，
r18/r19 已出现真实后果——`cumulative_drift` schema 由 v1 升 v2 后，沿用 v1 的下游读者
会**静默读不到** `excluded` 字段；`description基线` 三口径键是本轮新加。
散文式约定挡不住这类漂移，故落成可机检的契约 + 不变式。

被测对象：`05-exec/baseline_contract_scan.py`（本测试先写 → 期望 ImportError 红 → 再实现）
退出码：0 全过 / 1 有失败 / 2 环境不满足
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-56s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load_validator():
    if not (HERE / "baseline_contract_scan.py").exists():
        return None
    spec = importlib.util.spec_from_file_location("bcs", str(HERE / "baseline_contract_scan.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GOOD_DRIFT = {
    "schema": "cumulative-drift-scan-v2", "generated_at": "2026-09-24 18:00", "readonly": True,
    "window_days": 30, "threshold": 5, "exclusions_enabled": True,
    "verdict_taxonomy": ["drift_detected", "softened", "refinement", "additive",
                        "neutral_rephrase", "uncertain"], "evidence": {"total_commits": 318, "roots": {}},
    "flagged_ruleish": [], "flagged_all": [],
    "excluded": [{"root": "self", "path": "memory/x.part1.md", "edits": 6, "why": "by-design"}],
    "note": "candidates",
}
GOOD_DESC = {
    "generated_at": "2026-09-24T18:00:00",
    "denominator": {"scanned": 166, "junction_skipped": ["rag-eval"], "parse_errors": 0,
                    "glob_total": 167, "registry": {"available": True, "count": 167,
                                                    "skills_len": 167, "self_consistent": True},
                    "registry_cmd": "x", "consistent": True, "delta": 0},
    "desc_max_official": 1024,
    "summary": {"total": 166, "errors": 0, "no_desc": 0, "has_desc": 166, "with_trigger": 120,
                "double_element": 120, "over_cap": 0, "has_process": 24,
                "len_min": 23, "len_max": 1019, "len_median": 237},
    "skills": [],
}


GOOD_RUBRIC = {
    "schema": "skill-structure-rubric-v2", "generated_at": "2026-09-25 05:40", "readonly": True,
    "benchmark": "r31", "denominator": {"glob_total": 167, "scanned": 166,
                                        "junction_skipped": ["rag-eval"], "errors": []},
    "rubric": ["overview", "when_to_use", "process", "rationalizations", "red_flags", "verification"],
    "per_section": {"overview": {"count": 30, "pct": 18.1},
                    "rationalizations": {"count": 36, "pct": 21.7}},
    "all_six": {"count": 0, "pct": 0.0},
}


def main():
    bcs = load_validator()
    if bcs is None:
        ck("RED 前置：validator baseline_contract_scan.py 存在", False,
           "文件不存在 —— 本次运行即为 TDD 的红阶段（先看失败，再写实现）")
        print("\n夹具合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), 0, len(RESULTS)))
        print("[GATE:fixture-fail]")
        return 1
    ck("validator 可导入且暴露 validate_doc/load_contracts",
       hasattr(bcs, "validate_doc") and hasattr(bcs, "load_contracts"))

    contracts = bcs.load_contracts()
    ck("契约文件可读且含 artifacts", bool(contracts.get("artifacts")), json.dumps(contracts)[:120])

    # --- 正例：合法文档 0 违规 ---
    v = bcs.validate_doc(GOOD_DRIFT, contracts["artifacts"]["cumulative_drift_*.json"], "drift")
    ck("t1 合法 drift 文档 → 零违规", v == [], json.dumps(v, ensure_ascii=False)[:220])
    v2 = bcs.validate_doc(GOOD_DESC, contracts["artifacts"]["description*_.json"]
                          if "description*_.json" in contracts["artifacts"]
                          else contracts["artifacts"]["description*.json"], "desc")
    ck("t2 合法 description 文档 → 零违规", v2 == [], json.dumps(v2, ensure_ascii=False)[:220])

    # --- 违规样本：必须被拦住（判据有牙）---
    bad = json.loads(json.dumps(GOOD_DRIFT))
    del bad["verdict_taxonomy"]
    ck("t3 缺必填键 → 报该键", any("verdict_taxonomy" in x for x in
       bcs.validate_doc(bad, contracts["artifacts"]["cumulative_drift_*.json"], "drift")))
    bad2 = json.loads(json.dumps(GOOD_DRIFT))
    bad2["schema"] = "cumulative-drift-scan-v1"
    ck("t4 schema 串过期（v1 冒充 v2）→ 拦住", any("schema" in x.lower() for x in
       bcs.validate_doc(bad2, contracts["artifacts"]["cumulative_drift_*.json"], "drift")))
    bad3 = json.loads(json.dumps(GOOD_DRIFT))
    bad3["excluded"][0].pop("why")
    ck("t5 排除项缺 why（静默丢数据形态）→ 拦住", any("excluded" in x for x in
       bcs.validate_doc(bad3, contracts["artifacts"]["cumulative_drift_*.json"], "drift")))
    bad4 = json.loads(json.dumps(GOOD_DESC))
    bad4["denominator"]["glob_total"] = 166
    bad4["denominator"]["consistent"] = True
    ck("t6 分母不变式（glob==registry）被破坏 → 拦住", any("denominator" in x for x in
       bcs.validate_doc(bad4, contracts["artifacts"]["description*.json"], "desc")))
    bad5 = json.loads(json.dumps(GOOD_DESC))
    bad5["summary"]["has_process"] = 999
    ck("t7 计数越界（has_process > total）→ 拦住", any("has_process" in x for x in
       bcs.validate_doc(bad5, contracts["artifacts"]["description*.json"], "desc")))
    bad6 = json.loads(json.dumps(GOOD_DRIFT))
    bad6["readonly"] = False
    ck("t8 只读声明被改 False → 拦住", any("readonly" in x for x in
       bcs.validate_doc(bad6, contracts["artifacts"]["cumulative_drift_*.json"], "drift")))

    # --- r31：schema_id 授权代际列表（同一 glob 下两代产物并存的真实形态）---
    rub = contracts["artifacts"]["skill_structure_rubric_*.json"]
    ck("t11 契约侧 schema_id 已改为授权列表（非通配、非单值）",
       isinstance(rub.get("schema_id"), list) and len(rub["schema_id"]) == 2, str(rub.get("schema_id")))
    for gen in ("skill-structure-rubric-v1", "skill-structure-rubric-v2"):
        d = json.loads(json.dumps(GOOD_RUBRIC))
        d["schema"] = gen
        ck("t11.%s 已授权代际 → 零违规" % gen[-2:],
           bcs.validate_doc(d, rub, "rubric") == [],
           json.dumps(bcs.validate_doc(d, rub, "rubric"), ensure_ascii=False)[:200])
    d3 = json.loads(json.dumps(GOOD_RUBRIC))
    d3["schema"] = "skill-structure-rubric-v3"
    ck("t12 未登记代际 v3 → 必须仍拦住（列表=逐代枚举授权，不是放宽匹配）",
       any("schema" in x.lower() for x in bcs.validate_doc(d3, rub, "rubric")),
       json.dumps(bcs.validate_doc(d3, rub, "rubric"), ensure_ascii=False)[:200])

    # --- r33：JSONL 台账纳入契约面（M-1′，护住 r32 新落的 freshness 门不被写坏）---
    lj = contracts["artifacts"].get("gate_runs.jsonl")
    ck("t13 契约已登记 gate_runs.jsonl（未登记=台账在契约面外，freshness 门可被静默写坏）",
       isinstance(lj, dict) and bool(lj.get("row_required")), str(type(lj)))
    if isinstance(lj, dict):
        def bad_of(rows):
            return bcs.validate_jsonl(rows, lj, "ledger") if hasattr(bcs, "validate_jsonl") else ["NO validate_jsonl"]
        good = [{"ts": "2026-09-25T06:32:43", "origin": "local", "verdict": "PASS", "mode": "full"},
                {"ts": "2026-09-25T06:32:46", "origin": "ci", "verdict": "PASS", "mode": "portable-only"}]
        ck("t13.1 合规台账 → 零违规", bad_of(good) == [], json.dumps(bad_of(good), ensure_ascii=False)[:200])
        ck("t14 行缺必填键 origin → 拦住并点名行号", any("缺键" in x and "row 0" in x for x in
           bad_of([{"ts": "2026-09-25T06:32:43", "verdict": "PASS", "mode": "full"}])),
           str(bad_of([{"ts": "2026-09-25T06:32:43", "verdict": "PASS", "mode": "full"}]))[:200])
        ck("t15 origin 越出取值域 → 拦住（防第三态来源冒充本机记录）", any("origin 取值域" in x for x in
           bad_of([{"ts": "2026-09-25T06:32:43", "origin": "cron-bot", "verdict": "PASS", "mode": "full"}])),
           str(bad_of([{"ts": "2026-09-25T06:32:43", "origin": "cron-bot", "verdict": "PASS", "mode": "full"}]))[:200])
        ck("t16 ts 形态非法 → 拦住", any("ts 形态" in x for x in
           bad_of([{"ts": "2026/09/25 06:32", "origin": "local", "verdict": "PASS", "mode": "full"}])),
           str(bad_of([{"ts": "2026/09/25 06:32", "origin": "local", "verdict": "PASS", "mode": "full"}]))[:200])
        ck("t17 verdict 越出取值域 → 拦住", any("verdict 取值域" in x for x in
           bad_of([{"ts": "2026-09-25T06:32:43", "origin": "local", "verdict": "maybe", "mode": "full"}])),
           str(bad_of([{"ts": "2026-09-25T06:32:43", "origin": "local", "verdict": "maybe", "mode": "full"}]))[:200])
        ck("t18 空台账 → 不得判过（R247，无行不等于无违规）", any("0 行" in x for x in bad_of([])),
           str(bad_of([]))[:200])
        ck("t19 非对象行（裸文本行）→ 拦住", any("非对象" in x for x in bad_of(["just a string"])),
           str(bad_of(["just a string"]))[:200])

    # --- 契约面自身失效不得静默 PASS（R247）---
    ck("t9 空 artifacts → 报「契约面为空」", "CONTRACT-EMPTY" in
       json.dumps(bcs.validate_contracts({"artifacts": {}}, []), ensure_ascii=False))
    ck("t10 pattern 零命中文件 → 报空面而非通过", any("0 个" in x or "无文件" in x for x in
       bcs.validate_contracts(contracts, [("/nope/*.json", [])])[0]),
       str(bcs.validate_contracts(contracts, [("/nope/*.json", [])])[:2]))

    # --- 层 b 真机接线：本仓现有基线必须全部合规 ---
    tmp = Path(tempfile.mkdtemp(prefix="r19_contract_"))
    rep = tmp / "r.json"
    p = subprocess.run([sys.executable, str(HERE / "baseline_contract_scan.py"),
                        "--json", str(rep)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    ok_run = rep.exists()
    data = json.loads(rep.read_text(encoding="utf-8")) if ok_run else {}
    ck("层b 校验器可跑并出 JSON", ok_run, (p.stderr or p.stdout)[-200:])
    ck("层b 真实基线全部合规（violations 总数 == 0）",
       sum(v.get("violations", 0) for v in data.get("artifacts", [])) == 0,
       json.dumps([{a["glob"]: a["violations"]} for a in data.get("artifacts", [])])[:260])
    ck("层b 受检文件数 >= 7（契约面非空，R247）", data.get("files_checked", 0) >= 7,
       str(data.get("files_checked")))
    ck("层b 生效路径 exit 0", p.returncode == 0, "rc=%s" % p.returncode)

    # --- 层 b′ 对照组：污染一个真基线副本，判据必须变红 ---
    dirt = tmp / "06-dirty"
    dirt.mkdir()
    src = HERE.parent / "06-benchmark" / "cumulative_drift_2026-09-24.json"
    (dirt / "cumulative_drift_2026-09-24.json").write_text(
        src.read_text(encoding="utf-8").replace('"schema": "cumulative-drift-scan-v2"',
                                                '"schema": "cumulative-drift-scan-v1"'), encoding="utf-8")
    p2 = subprocess.run([sys.executable, str(HERE / "baseline_contract_scan.py"),
                         "--dir", str(dirt)], capture_output=True, text=True,
                        encoding="utf-8", errors="replace", timeout=300)
    out2 = (p2.stdout or "") + (p2.stderr or "")
    ck("层b′ 对照组：污染 schema 后 exit != 0", p2.returncode != 0, "rc=%s" % p2.returncode)
    ck("层b′ 对照组：报错点名该文件与 schema", "schema" in out2.lower() and "cumulative_drift" in out2,
       out2[-200:])

    # --- 层 b″：台账反例走**真实 subprocess 路径**（r33 M-1′；函数级 t14-t20 之外再证一次生效侧）---
    dirt2 = tmp / "06-dirty-ledger"
    dirt2.mkdir()
    src2 = HERE.parent / "06-benchmark" / "gate_runs.jsonl"
    if src2.exists():
        rows2 = [json.loads(l) for l in src2.read_text(encoding="utf-8").splitlines() if l.strip()]
        # 三种真实写坏形态各注一行：第三种 origin（CI 冒充本机）、非法 verdict、坏 ts
        rows2.append(dict(rows2[0], origin="cron-bot"))
        rows2.append(dict(rows2[0], verdict="maybe"))
        rows2.append(dict(rows2[0], ts="2026-09-25 07:00"))
        (dirt2 / "gate_runs.jsonl").write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in rows2) + "\n", encoding="utf-8")
        p3 = subprocess.run([sys.executable, str(HERE / "baseline_contract_scan.py"), "--dir", str(dirt2)],
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        out3 = (p3.stdout or "") + (p3.stderr or "")
        ck("层b″ 真跑对照组：污染台账后 exit != 0", p3.returncode != 0, "rc=%s" % p3.returncode)
        ck("层b″ 真跑对照组：三类违规逐条点名（origin/verdict/ts）",
           all(k in out3 for k in ("origin 取值域", "verdict 取值域", "ts 形态")), out3[-260:])
        # 空台账必须红（R247），不得因"没有行"而判过
        (dirt2 / "gate_runs.jsonl").write_text("", encoding="utf-8")
        p4 = subprocess.run([sys.executable, str(HERE / "baseline_contract_scan.py"), "--dir", str(dirt2)],
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        out4 = (p4.stdout or "") + (p4.stderr or "")
        ck("层b″ 真跑对照组：空台账判红而非绿（R247）",
           p4.returncode != 0 and ("0 行" in out4 or "命中 0 个文件" in out4), "rc=%s" % p4.returncode)
    else:
        ck("层b″ 前置：06-benchmark/gate_runs.jsonl 存在", False, "台账缺失，反例侧无从注入")

    # --- M-2（r38 清偿）：棘轮基线 ↔ METRIC_NAMES 集合全等，少一项必红 ---
    bl_path = HERE.parent / "06-benchmark" / "inject_ratchet_baseline.json"
    bl = json.loads(bl_path.read_text(encoding="utf-8"))
    art_bl = contracts["artifacts"]["inject_ratchet_baseline*.json"]
    v = bcs.validate_doc(bl, art_bl, "ratchet-baseline")
    ck("t21 棘轮基线原样 → 零违规（含集合全等）", v == [], json.dumps(v, ensure_ascii=False)[:200])
    cut = json.loads(bl_path.read_text(encoding="utf-8"))
    dropped = sorted(cut["metrics"].keys())[0]
    del cut["metrics"][dropped]
    v = bcs.validate_doc(cut, art_bl, "cut")
    ck("t22 基线少一项指标 → 必红并点名该指标（回归保护失效）",
       any("基线缺指标" in x and dropped in x for x in v), "%s | %s" % (dropped, str(v)[:160]))
    zombie = json.loads(bl_path.read_text(encoding="utf-8"))
    zombie["metrics"]["zz_not_a_real_metric"] = 1
    v = bcs.validate_doc(zombie, art_bl, "zombie")
    ck("t23 基线多出僵尸指标 → 必红", any("僵尸基线" in x for x in v), str(v)[:160])
    caporphan = json.loads(bl_path.read_text(encoding="utf-8"))
    caporphan["hard_caps"]["zz_unmetered"] = 10
    v = bcs.validate_doc(caporphan, art_bl, "cap-orphan")
    ck("t24 硬顶指向 metrics 之外的键 → 必红（硬顶无主永不触发）",
       any("HARD-CAP" in x for x in v), str(v)[:160])
    # --- r38 第十四维：账龄自洽不变式 ---
    debt = json.loads((HERE.parent / "06-benchmark" / "debt_aging_r38_2026-09-25.json")
                      .read_text(encoding="utf-8"))
    art_debt = contracts["artifacts"]["debt_aging_r38_*.json"]
    ck("t25 账龄件原样 → 零违规", bcs.validate_doc(debt, art_debt, "debt") == [],
       json.dumps(bcs.validate_doc(debt, art_debt, "debt"), ensure_ascii=False)[:200])
    leak = json.loads((HERE.parent / "06-benchmark" / "debt_aging_r38_2026-09-25.json")
                      .read_text(encoding="utf-8"))
    k0 = sorted(leak["by_class"].keys())[0]
    leak["by_class"][k0] = max(0, leak["by_class"][k0] - 1)
    v = bcs.validate_doc(leak, art_debt, "leak")
    ck("t26 分类之和 != 未闭环条目数 → 必红（判据漏桶 X-7）",
       any("DEBT-CLASS" in x for x in v), str(v)[:200])
    hid = json.loads((HERE.parent / "06-benchmark" / "debt_aging_r38_2026-09-25.json")
                     .read_text(encoding="utf-8"))
    hid["verdict_taxonomy"] = [x for x in hid["verdict_taxonomy"] if x != "UNDATED"]
    v = bcs.validate_doc(hid, art_debt, "hide-undated")
    ck("t27 隐掉 UNDATED 态 → 必红（防把无定年条目静默并入绿态）",
       any("verdict_taxonomy" in x and "UNDATED" in x for x in v), str(v)[:200])
    ck("t28 契约 pattern 数 >= 12（覆盖面不得缩水）", len(contracts["artifacts"]) >= 12,
       str(len(contracts["artifacts"])))

    fails = [r for r in RESULTS if not r[0]]
    print("\n夹具合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    if fails:
        print("[GATE:fixture-fail]")
        for ok, name, detail in fails:
            print("  FAIL %s | %s" % (name, detail))
        return 1
    print("[GATE:fixture-pass]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
