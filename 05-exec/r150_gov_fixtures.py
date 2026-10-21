# -*- coding: utf-8 -*-
# r150_gov_fixtures.py -- r150 两面（契约生命周期 / 契约x体量联动）的隔离桩 + 变异对照。
#
# 纪律来源（A-skill-manager/references/governance.md 的「新判据交付契约」R272）：
#   新增判据必须同时交付 ①正例 ②违规样本（证明判据非恒真）③边界（零输入按 R247 记 UNVERIFIED
#   而不是静默 PASS）。桩不过 = 判据未完成，禁止落盘。
# 另加变异对照（对标 r19_fixture_mutation_check 的形态）：把判据本体改坏，夹具必须有牙抓住。
#
# 用法: python 05-exec/r150_gov_fixtures.py [--keep]
# 退出码: 0 全过 / 1 有失败
import argparse
import io
import json
import os
import contextlib
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIFE_SRC = os.path.join(HERE, "r150_contract_lifecycle.py")
LINK_SRC = os.path.join(HERE, "r150_gov_link.py")
TIER_SRC = os.path.join(HERE, "r150_volume_tiers.py")
ACC_SRC = os.path.join(HERE, "r153_gov_acceptance.py")

MINI_GATES = "\n".join([
    "# mini runner for fixtures",
    "GATES = [",
    "    {",
    '        "id": "gate_a",',
    '        "script": "a.py",',
    '        "argv": [],',
    '        "pass_token": "[GATE:a-pass]",',
    '        "portable": True,',
    '        "covers": ["c1"],',
    '        "why": "fixture gate A",',
    "    },",
    "    {",
    '        "id": "gate_b",',
    '        "script": "missing_b.py",',
    '        "argv": [],',
    '        "pass_token": "[GATE:b-pass]",',
    '        "portable": True,',
    '        "covers": ["c2"],',
    '        "why": "fixture gate B (script deliberately absent)",',
    "    },",
    "]",
    "",
    'if __name__ == "__main__":',
    "    raise SystemExit(0)",
    "",
])


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def make_root(tmp, gate_rows=2, vol_rows=2, vol_files=None, vol_growth=None,
              reconcile=None, gate_ledger=True, vol_ledger=True, bad_lines=0):
    w(os.path.join(tmp, "05-exec", "run_gates.py"), MINI_GATES)
    w(os.path.join(tmp, "05-exec", "a.py"), "# fixture gate A body\n")
    w(os.path.join(tmp, "05-exec", "baseline_contract_scan.py"),
      "# fixture\nINVARIANTS = {\n    \"inv_one\": 1,\n    \"inv_two\": 2,\n}\n")
    if reconcile is not None:
        w(os.path.join(tmp, "06-benchmark", "gate_reconcile_registry.json"),
          json.dumps({"schema": "x", "gates": reconcile}, ensure_ascii=False))
    if gate_ledger:
        lines = []
        for i in range(gate_rows):
            lines.append(json.dumps({"ts": "2026-10-2%dT10:00:00" % (i % 10), "origin": "local",
                                     "verdict": "PASS" if i == 0 else "FAIL",
                                     "overall": "PASS" if i == 0 else "FAIL", "gates_run": 2,
                                     "total_ms": 100, "head": "abc1234",
                                     "per_gate": {"gate_a": "PASS", "gate_b": "FAIL"}},
                                    ensure_ascii=False))
        for _ in range(bad_lines):
            lines.append("{not json")
        w(os.path.join(tmp, "06-benchmark", "gate_runs.jsonl"), "\n".join(lines) + "\n")
    if vol_ledger:
        lines = []
        for i in range(vol_rows):
            row = {"schema": "fenjue-volume-snapshot-v2", "ts": "2026-10-2%dT22:00:00" % (i % 10),
                   "proj": tmp, "total_bytes": 1000 + i * 100, "auto_moved": 0, "auto_freed": 0}
            row["files"] = vol_files
            row["growth_ratio"] = vol_growth
            lines.append(json.dumps(row, ensure_ascii=False))
        w(os.path.join(tmp, "memory", "sessions", "volume-snapshots.jsonl"), "\n".join(lines) + "\n")
    return tmp


def load_module(src_path, ns_name):
    src = io.open(src_path, encoding="utf-8").read()
    return exec_module(src, ns_name)


def exec_module(src, ns_name):
    ns = {"__name__": ns_name, "__file__": os.path.join(HERE, ns_name + ".py")}
    code = compile(src, ns["__file__"], "exec")
    exec(code, ns)
    return ns


def isolate(ns, keys=("GOV_MD", "GREENCHECK", "CI_CONTRACT_MD", "EXEC_CONTRACT_MD")):
    for k in keys:
        if k in ns:
            ns[k] = ""
    return ns


RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append({"name": name, "ok": bool(cond), "detail": detail})
    print("  %-52s %s %s" % (name, "PASS" if cond else "FAIL", detail[:96]))


def part1_lifecycle(tmp):
    print("[FIX] A 契约生命周期面")
    ns = isolate(load_module(LIFE_SRC, "life_mod"))
    build = ns["build"]

    # 正例：两门齐、台账有记录、对账快照含两门
    r = make_root(os.path.join(tmp, "case_ok"), reconcile={"_snapshot_gate_ids": ["gate_a", "gate_b"],
                                                           "_snapshot_at": "2026-10-21 19:58"})
    doc = build(r)
    c = {x["cid"]: x for x in doc["contracts"]}
    check("f1 正例：登记册出 2 门判据契约", doc["summary"]["contracts_n"] - 2 >= 0,
          "contracts_n=%d" % doc["summary"]["contracts_n"])
    check("f2 正例：gate_a 五环节 draft/sign PASS",
          c["GATE:gate_a"]["stages"]["draft"]["status"] == "PASS"
          and c["GATE:gate_a"]["stages"]["sign"]["status"] == "PASS")
    check("f3 正例：gate_a perform PASS（台账 2 轮）",
          c["GATE:gate_a"]["stages"]["perform"]["status"] == "PASS",
          "runs_seen=%s" % (c["GATE:gate_a"]["perform"] or {}).get("runs_seen"))
    check("f4 正例：五环节计数自洽（各态之和 == 契约数）",
          all(v["PASS"] + v["FAIL"] + v["UNVERIFIED"] == doc["summary"]["contracts_n"]
              for v in doc["summary"]["stages"].values()))

    # 违规样本 1：脚本缺失的门 ⇒ draft FAIL（证明判据非恒真）
    check("f5 违规样本：脚本缺失的门 draft FAIL",
          c["GATE:gate_b"]["stages"]["draft"]["status"] == "FAIL")
    warns = [a for a in doc["alerts"] if a["cid"] == "GATE:gate_b" and a["kind"] == "MISSING_DRAFT"]
    check("f6 违规样本：出 MISSING_DRAFT 预警", len(warns) == 1)

    # 违规样本 2：无对账行且不在快照 ⇒ review FAIL
    r2 = make_root(os.path.join(tmp, "case_norecon"),
                   reconcile={"gate_table_reconcile": {"evidence": "x", "at": "2026-10-21"}})
    doc2 = build(r2)
    c2 = {x["cid"]: x for x in doc2["contracts"]}
    check("f7 违规样本：无对账行且不在快照 ⇒ review FAIL",
          c2["GATE:gate_a"]["stages"]["review"]["status"] == "FAIL")

    # 边界：零契约 ⇒ 零输入面 UNVERIFIED rc=2（R247 禁静默 PASS）
    r3 = os.path.join(tmp, "case_empty")
    w(os.path.join(r3, "05-exec", "run_gates.py"), "GATES = []\n")
    doc3 = build(r3)
    check("f8 边界：零契约 ⇒ contracts_n==0（供 rc=2 判定）",
          len([x for x in doc3["contracts"] if x["family"] == "判据契约"]) == 0)
    return ns, build


def part2_link(tmp):
    print("[FIX] B 契约x体量联动面")
    ns = isolate(load_module(LINK_SRC, "link_mod"), keys=())
    build = ns["build"]

    r = make_root(os.path.join(tmp, "link_ok"), gate_rows=3, vol_rows=3)
    doc = build(r)
    check("g1 正例：共同日 >= 1", doc["common_days"] >= 1, "common=%d" % doc["common_days"])
    check("g2 正例：联动表含线上两侧读数",
          any(x["gate_runs"] > 0 and x["vol_bytes"] for x in doc["joined"]))
    check("g3 正例：无共享主键被点名（契约册无项目键 / 体量册无提交键）",
          any(d["kind"] == "NO_SHARED_KEY" for d in doc["defects"]))

    # 违规样本：体量册字段空缺 ⇒ VOL_FIELD_EMPTY，且分母写实（不是 0%）
    check("g4 违规样本：files 覆盖 0/3 被点名",
          any(d["kind"] == "VOL_FIELD_EMPTY" and "files" in d["detail"] for d in doc["defects"]),
          "denom=%d" % doc["vol_ledger"]["field_denominator"])
    r2 = make_root(os.path.join(tmp, "link_filled"), gate_rows=3, vol_rows=3,
                   vol_files=10, vol_growth=0.1)
    doc2 = build(r2)
    check("g5 反面照：字段填上后同名缺陷消失（证明 g4 非恒真）",
          not any(d["kind"] == "VOL_FIELD_EMPTY" for d in doc2["defects"]))

    # 违规样本：只契约侧有台账 ⇒ 共同日 0（供 rc=2 判定）
    r3 = make_root(os.path.join(tmp, "link_gateonly"), gate_rows=2, vol_ledger=False)
    doc3 = build(r3)
    check("g6 违规样本：体量册零行 ⇒ 共同日 0", doc3["common_days"] == 0,
          "vol_rows=%d" % doc3["vol_ledger"]["rows"])

    # 边界：坏行计数（不得静默吞）
    r4 = make_root(os.path.join(tmp, "link_badrows"), gate_rows=2, bad_lines=2)
    doc4 = build(r4)
    check("g7 边界：坏行被计数而非静默吞", doc4["gate_ledger"]["bad_rows"] == 2,
          "bad=%d" % doc4["gate_ledger"]["bad_rows"])
    return ns, build


def part4_tiers(tmp):
    print("[FIX] D 体量三层归口面")
    ns = load_module(TIER_SRC, "tier_mod")
    build = ns["build"]
    allkeys = {}
    for tier in ns["TIER_KEYS"]:
        for k in ns["TIER_KEYS"][tier]:
            allkeys[k] = 1
    bf = os.path.join(tmp, "budget_full.json")
    w(bf, json.dumps({"budget": allkeys, "sources": ["fixture"]}, ensure_ascii=False))
    doc = build(tmp, bf)
    check("t1 正例：60 key 全分层、覆盖率 1.0", doc["coverage"] == 1.0 and not doc["unclassified"],
          "n=%d cov=%s" % (doc["total_n"], doc["coverage"]))
    check("t2 正例：三层计数之和 == 总数",
          sum(doc["tiers"][t]["n"] for t in doc["tiers"]) == doc["total_n"])
    bf2 = os.path.join(tmp, "budget_extra.json")
    extra = dict(allkeys)
    extra["brand_new_upstream_key"] = 7
    w(bf2, json.dumps({"budget": extra}, ensure_ascii=False))
    doc2 = build(tmp, bf2)
    check("t3 违规样本：上游新 key 被具名（未分类 = 1）",
          doc2["unclassified"] == ["brand_new_upstream_key"], "unclassified=%s" % doc2["unclassified"])
    bf3 = os.path.join(tmp, "budget_empty.json")
    w(bf3, json.dumps({"budget": {}}, ensure_ascii=False))
    doc3 = build(tmp, bf3)
    check("t4 边界：零 key ⇒ budget_n==0（供 rc=2 判定）", doc3["budget_n"] == 0)
    return ns, build


def part5_blocking(tmp):
    print("[FIX] E P0 阻断路（R150-6 / r152 常驻反向验证）")
    stubs = {
        "R150_GOV_MD": "stub_gov.md",
        "R150_GREENCHECK": "stub_greencheck.py",
        "R150_CI_CONTRACT_MD": "stub_ci.md",
        "R150_EXEC_CONTRACT_MD": "stub_exec.md",
    }
    bodies = {
        "stub_gov.md": "## 新判据交付契约（R272，2026-01-01）\n\n夹具/正例/反例三要素。\n",
        "stub_greencheck.py": "GREEN = 1\nRED = 1\nBLOCKED = 1\nUNKNOWN = 1\n",
        "stub_ci.md": "## 契约文件 `.ci/contract.json`\n",
        "stub_exec.md": "## 执行契约\n",
    }
    for fn, body in bodies.items():
        w(os.path.join(tmp, fn), body)
        for env_k, v in stubs.items():
            if v == fn:
                os.environ[env_k] = os.path.join(tmp, fn)
    src = io.open(LIFE_SRC, encoding="utf-8").read()
    ns = exec_module(src, "life_block")
    recon = {"_snapshot_gate_ids": ["gate_a", "gate_b"], "_snapshot_at": ""}
    r_missing = make_root(os.path.join(tmp, "blk_missing"), reconcile=recon)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = ns["main"](["--root", r_missing])
    out = buf.getvalue()
    check("p5a P0 阻断：门脚本缺失 => rc=1 且打 [GOVREG:FAIL]",
          rc == 1 and "[GOVREG:FAIL]" in out, "rc=%s" % rc)
    check("p5b 同跑：P0 阻断时不得打 [GOVREG:PASS] 冒充绿", "[GOVREG:PASS]" not in out)
    r_ok = make_root(os.path.join(tmp, "blk_ok"), reconcile=recon)
    w(os.path.join(r_ok, "05-exec", "missing_b.py"), "# present\n")
    buf2 = io.StringIO()
    with contextlib.redirect_stdout(buf2):
        rc2 = ns["main"](["--root", r_ok])
    _diag = [x.strip()[:70] for x in buf2.getvalue().split("\n") if x.strip().startswith("P0")][:2] + ["exists=%s" % os.path.isfile(os.path.join(r_ok, "05-exec", "missing_b.py"))]
    check("p5c 对照：补齐脚本后 rc=0 且打 [GOVREG:PASS]",
          rc2 == 0 and "[GOVREG:PASS]" in buf2.getvalue(), "rc=%s diag=%s" % (rc2, _diag))
    mut = src.replace("elif lv[" + chr(34) + "P0" + chr(34) + "] > 0:", "elif False:")
    ns2 = exec_module(mut, "life_block_mut")
    r_missing2 = make_root(os.path.join(tmp, "blk_missing2"), reconcile=recon)
    buf3 = io.StringIO()
    with contextlib.redirect_stdout(buf3):
        rc3 = ns2["main"](["--root", r_missing2])
    check("m6 P0 分支摘掉 => 阻断消失（夹具对 P0 分支有牙）", rc3 == 0, "rc=%s" % rc3)
    staged = os.path.join(tmp, "staged_probe.txt")
    w(staged, "05-exec/r150_probe.py\n")
    gm_path = os.path.join(tmp, "gm.json")
    subprocess.run([sys.executable, os.path.join(HERE, "r137_commit_gate_map.py"),
                    "--staged", staged, "--json", gm_path],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
    gm = json.load(io.open(gm_path, encoding="utf-8"))
    ids = gm.get("required_gate_ids") or []
    check("p5d 接线：改 05-exec/ => required_gate_ids 含 contract_lifecycle_face",
          "contract_lifecycle_face" in ids, "ids=%s" % ids[:4])
    for k in stubs:
        os.environ.pop(k, None)
    return ns


def part6_acceptance(tmp):
    print("[FIX] F 考核校验面 A1-A6（r153 常驻反向验证）")
    Q = chr(34)
    sd = os.path.join(tmp, "accstub")
    os.makedirs(sd, exist_ok=True)
    def mk(name, lines):
        w(os.path.join(sd, name + ".py"), "\n".join(lines) + "\n")
    mk("A1", ["import sys", "print(" + Q + "[GOVREG:PASS]" + Q + ")"])
    mk("A3", ["import sys", "print(" + Q + "[GOVTIER:PASS]" + Q + ")"])
    mk("A4", ["import sys", "print(" + Q + "[GATE:govfix-pass]" + Q + ")"])
    mk("A2", ["import sys,json", "p=[a for a in sys.argv if a.endswith('.json')][0]", "d={'common_days':9,'gate_ledger':{'age_days':0.0},'vol_ledger':{'age_days':0.0}}", "f=open(p,'w')", "json.dump(d,f)", "f.close()"])
    mk("A5", ["import sys,json", "p=[a for a in sys.argv if a.endswith('.json')][0]", "d={'face':{'unbacked_n':0,'no_acceptance_n':0,'no_evidence_n':0,'boundary_missing_n':0}}", "f=open(p,'w')", "json.dump(d,f)", "f.close()"])
    mk("A6", ["import sys,json", "p=[a for a in sys.argv if a.endswith('.json')][0]", "d={'defects':[]}", "f=open(p,'w')", "json.dump(d,f)", "f.close()"])
    src = io.open(ACC_SRC, encoding="utf-8").read()
    ns = exec_module(src, "acc_mod")
    doc = ns["build"](tmp, sd)
    st = dict((r["id"], r["status"]) for r in doc["criteria"])
    check("a6a 正例：六标准全绿 => overall PASS", st.get("A1") == "PASS" and doc["summary"]["overall"] == "PASS", "overall=%s" % doc["summary"]["overall"])
    check("a6b 正例：A6 为 advisory 不计入总判", doc["summary"]["judged_n"] == 5)
    mk("A4", ["import sys", "sys.exit(1)"])
    d2 = ns["build"](tmp, sd)
    check("a6c 违规样本：A4 rc=1 => overall FAIL 且 fail_ids=['A4']",
          d2["summary"]["overall"] == "FAIL" and d2["summary"]["fail_ids"] == ["A4"],
          "fail=%s" % d2["summary"]["fail_ids"])
    mk("A4", ["import sys", "print(" + Q + "[GATE:govfix-pass]" + Q + ")"])
    mk("A3", ["import sys", "print('done')"])
    d3 = ns["build"](tmp, sd)
    st3 = dict((r["id"], r["status"]) for r in d3["criteria"])
    check("a6d 边界：rc=0 但 token 缺 => UNVERIFIED（不得算绿，R247）",
          st3.get("A3") == "UNVERIFIED" and d3["summary"]["overall"] == "UNVERIFIED",
          "A3=%s overall=%s" % (st3.get("A3"), d3["summary"]["overall"]))
    os.remove(os.path.join(sd, "A1.py"))
    d4 = ns["build"](tmp, sd)
    st4 = dict((r["id"], r["status"]) for r in d4["criteria"])
    check("a6e 边界：标准脚本缺失 => UNVERIFIED 而非 FAIL", st4.get("A1") == "UNVERIFIED",
          "A1=%s" % st4.get("A1"))
    mut = src.replace("if rc == 0 and tk_ok:", "if rc == 0:")
    ns2 = exec_module(mut, "acc_mod_mut")
    d5 = ns2["build"](tmp, sd)
    st5 = dict((r["id"], r["status"]) for r in d5["criteria"])
    check("m7 UNVERIFIED 分支摘掉 => 静默跳过被算绿（夹具对三分支有牙）",
          st5.get("A3") == "PASS", "A3=%s" % st5.get("A3"))
    return ns


MUTATIONS = [
    ("m1_life_draft_always_true", LIFE_SRC,
     "drafted = bool(exists and size > 0 and (g.get(\"why\") or \"\").strip())",
     "drafted = True"),
    ("m2_life_review_always_true", LIFE_SRC,
     "reviewed = (gid in recon[\"registered\"]) or (gid in recon[\"snapshot_ids\"])",
     "reviewed = True"),
    ("m3_link_no_shared_key_dropped", LINK_SRC,
     'if not g_proj or not v_commit:',
     "if False:"),
    ("m4_link_bad_rows_dropped", LINK_SRC,
     "bad += 1",
     "bad += 0"),
    ("m5_tier_unclassified_dropped", TIER_SRC,
     "unclassified = sorted(k for k in budget if k not in owner)",
     "unclassified = []"),
]


def part3_mutations(tmp):
    print("[FIX] C 变异对照（判据本体改坏，夹具必须有牙）")
    base = os.path.join(tmp, "mut_base")
    make_root(base, gate_rows=3, vol_rows=3, bad_lines=2,
              reconcile={"_snapshot_gate_ids": [], "_snapshot_at": ""})
    mut_budget = os.path.join(tmp, "mut_budget.json")
    _mk = {}
    for _t in ("T1", "T2", "T3"):
        for _k in json.loads("{}") or []:
            pass
    # 变异体的输入只需含一个上游新 key，以逼出未分类面
    w(mut_budget, json.dumps({"budget": {"unknown_key_z": 1}}, ensure_ascii=False))
    for mid, src_path, old, new in MUTATIONS:
        src = io.open(src_path, encoding="utf-8").read()
        if old not in src:
            check("%s 变异点可命中" % mid, False, "锚点未命中：%s" % old[:48])
            continue
        mutant = src.replace(old, new, 1)
        ns = isolate(exec_module(mutant, mid),
                     keys=("GOV_MD", "GREENCHECK", "CI_CONTRACT_MD", "EXEC_CONTRACT_MD"))
        try:
            if mid.startswith("m5"):
                doc = ns["build"](base, mut_budget)
            else:
                doc = ns["build"](base)
        except Exception as e:
            check(mid + " 变异被检出", True, "变异体崩溃：%s" % str(e)[:60])
            continue
        caught = False
        note = ""
        if mid.startswith("m1"):
            c = {x["cid"]: x for x in doc["contracts"]}
            caught = c.get("GATE:gate_b", {}).get("stages", {}).get("draft", {}).get("status") != "FAIL"
            note = "gate_b draft=%s" % c.get("GATE:gate_b", {}).get("stages", {}).get("draft", {}).get("status")
        elif mid.startswith("m2"):
            c = {x["cid"]: x for x in doc["contracts"]}
            caught = c.get("GATE:gate_a", {}).get("stages", {}).get("review", {}).get("status") == "PASS"
            note = "gate_a review=%s" % c.get("GATE:gate_a", {}).get("stages", {}).get("review", {}).get("status")
        elif mid.startswith("m3"):
            caught = not any(d["kind"] == "NO_SHARED_KEY" for d in doc["defects"])
            note = "defects=%d" % len(doc["defects"])
        elif mid.startswith("m4"):
            caught = doc["gate_ledger"]["bad_rows"] == 0
            note = "bad_rows=%d" % doc["gate_ledger"]["bad_rows"]
        elif mid.startswith("m5"):
            caught = doc["unclassified"] == []
            note = "unclassified=%s" % doc["unclassified"]
        check(mid + " 变异被检出", caught, note)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args(argv)
    tmp = tempfile.mkdtemp(prefix="r150fix_", dir=os.path.join(ROOT, "_temp") if os.path.isdir(os.path.join(ROOT, "_temp")) else None)
    try:
        part1_lifecycle(tmp)
        part2_link(tmp)
        part4_tiers(tmp)
        part5_blocking(tmp)
        part6_acceptance(tmp)
        part3_mutations(tmp)
    finally:
        if not args.keep:
            shutil.rmtree(tmp, ignore_errors=True)
    n = len(RESULTS)
    ok = sum(1 for r in RESULTS if r["ok"])
    print("[GOVFIX] %d/%d 通过（含变异对照 %d 项 = MUTATIONS %d + 内联 m6/m7）" % (ok, n, len(MUTATIONS) + 2, len(MUTATIONS)))
    if ok == n:
        print("[GATE:govfix-pass]")
        return 0
    for r in RESULTS:
        if not r["ok"]:
            print("  FAILED %s :: %s" % (r["name"], r["detail"]))
    print("[GATE:govfix-fail]")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
