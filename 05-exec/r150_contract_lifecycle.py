# -*- coding: utf-8 -*-
# r150_contract_lifecycle.py -- 契约全生命周期登记册与履约读数面（第 57 门候选）。
#
# 存在理由（r150 现状核验实测）：本体系有五处契约权威 ——
#   A 判据契约  56 门（05-exec/run_gates.py 的 GATES 表）
#   B 规则契约  9 条（D:/global_skills/A-skill-manager/references/governance.md 的「新判据交付契约」R272 及 8 条补条）
#   C 基线契约  24 条不变式（05-exec/baseline_contract_scan.py 的 INVARIANTS）
#   D CI 契约   四态（D:/global_skills/A-project-handoff/scripts/greencheck.py + references/ci-green-contract.md）
#   E 执行契约  （D:/global_skills/A-memory-start/references/contract.md）
# 五处各自成篇，**没有任何一张表把它们放进同一条生命周期**：谁起草 / 谁审核 / 谁签署 /
# 履约率多少 / 何时归档，全部只存在于报告叙事里，机器问不出来。
#
# 本件把「起草 - 审核 - 签署 - 履约 - 归档」五环节落成**逐契约可复算的三态判据**：
#   PASS       该环节有机器面且本次读数为真
#   FAIL       该环节有机器面且读数为假（缺件 / 无记录）
#   UNVERIFIED 该环节**本体系根本没有读数面**（R247：零输入面不得记绿，也不得记 0）
# 三态口径为的是把「缺口」与「失败」分开 —— 这是本体系反复踩过的那条线（r133 五抓）：
# 面不对时读出来的 0 不是「没问题」，是「问不出来」。
#
# 另出**风险预警清单**（advisory，不阻断）：缺环节 / 从未履约 / 末次非 PASS / 履约陈旧 / 无履约读数面。
#
# 用法:
#   python 05-exec/r150_contract_lifecycle.py                 # 人读表
#   python 05-exec/r150_contract_lifecycle.py --json <件>     # 机读留痕
#   python 05-exec/r150_contract_lifecycle.py --root <仓根>   # 夹具用（换面）
# 退出码: 0 登记册可算且结构自洽 / 1 结构自洽性被破 / 2 零输入面（UNVERIFIED，R247）
import argparse
import io
import importlib.util
import json
import os
import re
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)

# r152 夹具可测性钩子：外部权威源允许用 R150_<NAME> 环境变量改面（夹具据此喂 stub，
#   从而能在不依赖受管根的前提下复现「P0 预警 => 阻断」这条路）。缺省仍走真实绝对路径。
GOV_MD = os.environ.get("R150_GOV_MD") or r"D:\global_skills\A-skill-manager\references\governance.md"
GREENCHECK = os.environ.get("R150_GREENCHECK") or r"D:\global_skills\A-project-handoff\scripts\greencheck.py"
CI_CONTRACT_MD = os.environ.get("R150_CI_CONTRACT_MD") or r"D:\global_skills\A-project-handoff\references\ci-green-contract.md"
EXEC_CONTRACT_MD = os.environ.get("R150_EXEC_CONTRACT_MD") or r"D:\global_skills\A-memory-start\references\contract.md"
STALE_DAYS = 30   # 履约陈旧阈值：末次履约超过此天数即预警

# 权责划分（机读表，目标①「明确各节点权责」的机器载体；正文权威=框架报告 §2.1）
STAGE_ROLES = {
    "draft": "契约作者（本仓会话 / 归属方会话）",
    "review": "对账闸 r130_gate_table_reconcile（机判）+ 作者（交夹具证据）",
    "sign": "门表维护者（run_gates.py#GATES 单一真相源入口）",
    "perform": "聚合 runner run_gates.py（每轮真跑）+ pre-commit 分级阻断（r137 判定面）",
    "archive": "台账（gate_runs.jsonl / memory 分卷，append-only 不可回写）",
}
# 非门禁族（规则/基线/CI/执行）的审核与履约责任位不同 —— 具名单列，防把门禁权责错扣到它们头上
NON_GATE_REVIEW_OWNER = "受管根归属方会话（A-skill-manager / A-project-handoff 侧；本仓只有转诊面）"


def read_text(path):
    if not path or not os.path.isfile(path):
        return None
    try:
        return io.open(path, encoding="utf-8", errors="ignore").read()
    except Exception:
        return None


def load_gates(runner_path):
    """从 run_gates.py 取 GATES 表（不执行 main）。"""
    if not os.path.isfile(runner_path):
        return None
    spec = importlib.util.spec_from_file_location("r150_run_gates_probe", runner_path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass
    except Exception:
        return None
    return getattr(mod, "GATES", None)


def load_ledger(path):
    rows = []
    if not os.path.isfile(path):
        return rows
    for line in io.open(path, encoding="utf-8", errors="ignore"):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def reconcile_registry(root):
    p = os.path.join(root, "06-benchmark", "gate_reconcile_registry.json")
    t = read_text(p)
    if t is None:
        return None
    try:
        doc = json.loads(t)
    except Exception:
        return None
    gates = doc.get("gates") or {}
    reg = {k: v for k, v in gates.items() if not k.startswith("_")}
    snap = list(gates.get("_snapshot_gate_ids") or [])
    return {"registered": reg, "snapshot_ids": snap}


def parse_ts(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:len(fmt) + 4 if len(fmt) > 10 else len(fmt)], fmt)
        except Exception:
            continue
    return None


def stage(ok, evidence):
    if ok is None:
        return {"status": "UNVERIFIED", "evidence": evidence}
    return {"status": "PASS" if ok else "FAIL", "evidence": evidence}


def perform_face(gate_id, rows):
    """履约读数：某门在 gate_runs.jsonl 的逐门历史。"""
    seen = passn = failn = uvn = 0
    last_ts = None
    last_verdict = None
    for r in rows:
        pg = r.get("per_gate") or {}
        if gate_id not in pg:
            continue
        seen += 1
        v = pg[gate_id]
        if v == "PASS":
            passn += 1
        elif v == "FAIL":
            failn += 1
        else:
            uvn += 1
        last_ts = r.get("ts") or last_ts
        last_verdict = v
    if seen == 0:
        return None
    return {"runs_seen": seen, "pass": passn, "fail": failn, "unverified": uvn,
            "rate": round(passn / float(seen), 4), "last_ts": last_ts, "last_verdict": last_verdict}


def build(root):
    runner = os.path.join(root, "05-exec", "run_gates.py")
    gates = load_gates(runner)
    rows = load_ledger(os.path.join(root, "06-benchmark", "gate_runs.jsonl"))
    recon = reconcile_registry(root)
    contracts = []
    alerts = []

    # ---- A 判据契约：逐门五环节 ----
    if gates:
        for g in gates:
            gid = g.get("id") or ""
            script = g.get("script") or ""
            spath = os.path.join(root, "05-exec", script) if script else ""
            exists = bool(spath) and os.path.isfile(spath)
            size = os.path.getsize(spath) if exists else 0
            tok_raw = g.get("pass_token")
            if isinstance(tok_raw, (list, tuple)):
                token = " | ".join(str(x) for x in tok_raw).strip()
            else:
                token = (tok_raw or "").strip()
                token = token if isinstance(token, str) else str(token)
            pf = perform_face(gid, rows)
            # r250 自抓：原实现对 why 直接 .strip()，而我给新门写成了**元组**（相邻字面量漏去逗号）
            #   ⇒ AttributeError 把 pre-commit 整体拦下。改为与上面 pass_token 同样的归一化处理。
            _why = g.get("why")
            if isinstance(_why, (list, tuple)):
                _why = " ".join(str(x) for x in _why)
            drafted = bool(exists and size > 0 and (_why or "").strip())
            if recon is None:
                reviewed = None
            else:
                reviewed = (gid in recon["registered"]) or (gid in recon["snapshot_ids"])
            signed = bool(gid and (g.get("covers") or []))
            archived = bool(token) and (pf is not None and pf["runs_seen"] > 0)
            c = {
                "cid": "GATE:" + gid,
                "family": "判据契约",
                "authority": "05-exec/run_gates.py#GATES",
                "portable": bool(g.get("portable")),
                "stages": {
                    "draft": stage(drafted, "脚本 %s (%dB) + why 字段非空" % (script or "-", size)),
                    "review": stage(reviewed, "gate_reconcile_registry.json 有无 %s 的对账行" % gid
                                     if recon is not None else "对账台账不可读"),
                    "sign": stage(signed, "covers 声明 %d 条" % len(g.get("covers") or [])),
                    "perform": stage(pf is not None,
                                     "gate_runs.jsonl 逐门历史：%d 轮" % pf["runs_seen"] if pf else "台账无该门记录"),
                    "archive": stage(archived, "pass_token=%s；留痕轮次=%s"
                                     % (token or "(空)", pf["runs_seen"] if pf else 0)),
                },
                "perform": pf,
            }
            contracts.append(c)

    # ---- B 规则契约：governance.md 的「新判据交付契约」条目 ----
    gov = read_text(GOV_MD)
    if gov is not None:
        lines = gov.split("\n")
        idx = [i for i, l in enumerate(lines) if l.startswith("## ") and "契约" in l]
        for n, i in enumerate(idx):
            head = lines[i].strip()
            end = idx[n + 1] if n + 1 < len(idx) else len(lines)
            body = "\n".join(lines[i + 1:end]).strip()
            rid = head.split("（")[0].replace("## ", "").strip()
            has_date = bool(re.search(r"20\d\d-\d\d-\d\d", head))
            has_case = bool(re.search(r"夹具|桩|正例|反例|变异", body))
            contracts.append({
                "cid": "RULE:" + rid,
                "family": "规则契约",
                "authority": "A-skill-manager/references/governance.md",
                "portable": True,
                "stages": {
                    "draft": stage(bool(body), "正文 %d 字符" % len(body)),
                    # r152 自抓（#32 又一例）：原把「正文含夹具/正例/反例/变异关键词」当 review 面 =>
                    #   散文里有没有这几个词被当成「有没有审核」，在 R-ENUM / R-ATTR 上误报 NO_REVIEW FAIL。
                    #   实测该族**本来就没有独立对账面** => 正解是记 UNVERIFIED（R247），不是 FAIL。
                    #   关键词降级为 evidence 文案，供人读；不再参与判定。
                    "review": stage(None, "规则契约无独立对账面（本体系只见正文；%s）"
                                     % ("正文含夹具/正例/反例/变异关键词" if has_case else "正文亦无上述关键词")),
                    "sign": stage(has_date, "标题含立规日期" if has_date else "标题无日期"),
                    "perform": stage(None, "规则契约无逐条履约读数面（本体系缺该环节机器面）"),
                    "archive": stage(bool(read_text(os.path.join(os.path.dirname(GOV_MD), "version-history.md"))
                                         and rid.split(" ")[0] in (read_text(os.path.join(os.path.dirname(GOV_MD), "version-history.md")) or "")),
                                     "version-history.md 是否提及该条"),
                },
                "perform": None,
            })

    # ---- C 基线契约：INVARIANTS ----
    bc = read_text(os.path.join(root, "05-exec", "baseline_contract_scan.py"))
    inv_n = None
    if bc is not None:
        m = re.search(r"INVARIANTS\s*=\s*\{", bc)
        if m:
            tail = bc[m.end():]
            inv_n = len(re.findall(r"^\s{4}[\'\"][A-Za-z0-9_\-\.]+[\'\"]\s*:", tail, re.M))
    contracts.append({
        "cid": "BASELINE:invariants",
        "family": "基线契约",
        "authority": "05-exec/baseline_contract_scan.py#INVARIANTS",
        "portable": True,
        "stages": {
            "draft": stage(inv_n is not None and inv_n > 0, "不变式 %s 条" % inv_n),
            "review": stage(None, "无独立于本体的对账面（与 C 族同源）"),
            "sign": stage(bc is not None, "扫描器在盘"),
            "perform": stage(None, "整族单列读数，无逐条不变式履约面"),
            "archive": stage(bool(read_text(os.path.join(root, "06-benchmark", "input_pins.jsonl"))),
                             "input_pins.jsonl 留痕"),
        },
        "perform": None,
    })

    # ---- D CI 契约（四态） ----
    gc = read_text(GREENCHECK)
    ci_md = read_text(CI_CONTRACT_MD)
    states = [s for s in ("GREEN", "RED", "BLOCKED", "UNKNOWN") if gc and s in gc]
    contracts.append({
        "cid": "CI:greencheck",
        "family": "CI 全绿契约",
        "authority": "A-project-handoff/scripts/greencheck.py",
        "portable": True,
        "stages": {
            "draft": stage(len(states) == 4, "四态齐备 %s" % states),
            "review": stage(bool(ci_md), "references/ci-green-contract.md %s"
                            % (str(len(ci_md)) + "B" if ci_md else "缺失")),
            "sign": stage(bool(ci_md and ".ci/contract.json" in ci_md), "契约文件形态已在文档中定义"),
            "perform": stage(None, "本仓未接 CI 契约（tracked SKILL.md 恒 0 的有意设计，X-1）"),
            "archive": stage(bool(ci_md and len(ci_md) > 0), "文档在盘即留痕"),
        },
        "perform": None,
    })

    # ---- E 执行契约 ----
    ec = read_text(EXEC_CONTRACT_MD)
    contracts.append({
        "cid": "EXEC:memory-start-contract",
        "family": "执行契约",
        "authority": "A-memory-start/references/contract.md",
        "portable": True,
        "stages": {
            "draft": stage(bool(ec), "正文 %s" % (str(len(ec)) + "B" if ec else "缺失")),
            "review": stage(None, "无独立对账面"),
            "sign": stage(bool(ec), "权威源在盘"),
            "perform": stage(None, "履约由会话自述承担，无机器面"),
            "archive": stage(bool(ec), "权威源在盘即留痕"),
        },
        "perform": None,
    })

    # ---- 风险预警（advisory） ----
    for c in contracts:
        st = c["stages"]
        missing = [k for k, v in st.items() if v["status"] == "FAIL"]
        unver = [k for k, v in st.items() if v["status"] == "UNVERIFIED"]
        pf = c.get("perform")
        if st["perform"]["status"] == "UNVERIFIED":
            alerts.append({"cid": c["cid"], "level": "P1", "kind": "NO_PERFORM_FACE",
                           "detail": "无履约读数面 ⇒ 履约监控在本体系不可算（item1 缺口）"})
        if "draft" in missing:
            alerts.append({"cid": c["cid"], "level": "P0", "kind": "MISSING_DRAFT", "detail": "起草环节无件"})
        if st["review"]["status"] == "FAIL":
            alerts.append({"cid": c["cid"], "level": "P0", "kind": "NO_REVIEW",
                           "detail": "审核环节无对账/夹具痕"})
        if pf and pf["last_verdict"] and pf["last_verdict"] != "PASS":
            alerts.append({"cid": c["cid"], "level": "P1", "kind": "LAST_NOT_PASS",
                           "detail": "末次履约 %s @ %s" % (pf["last_verdict"], pf["last_ts"])})
        if pf and pf["rate"] == 0.0:
            alerts.append({"cid": c["cid"], "level": "P1", "kind": "NEVER_PASSED",
                           "detail": "%d 轮全非 PASS" % pf["runs_seen"]})
        if pf and pf["runs_seen"] and pf["rate"] is not None and pf["rate"] < 0.5:
            alerts.append({"cid": c["cid"], "level": "P2", "kind": "LOW_RATE",
                           "detail": "履约率 %.2f（%d/%d）" % (pf["rate"], pf["pass"], pf["runs_seen"])})
        if len(missing) + len(unver) >= 3:
            alerts.append({"cid": c["cid"], "level": "P2", "kind": "THIN_LIFECYCLE",
                           "detail": "五环节里 %d FAIL + %d UNVERIFIED" % (len(missing), len(unver))})

    # 履约陈旧腿（用上 STALE_DAYS；此前是死常量——常量存在但无腿=判据半截，r156b 补）
    for c in contracts:
        pf = c.get("perform")
        if pf and pf.get("last_ts"):
            try:
                age = (datetime.now() - datetime.strptime(pf["last_ts"][:19], "%Y-%m-%dT%H:%M:%S")).days
                if age > STALE_DAYS:
                    alerts.append({"cid": c["cid"], "level": "P1", "kind": "STALE_PERFORM",
                                   "detail": "末次履约 %s（%d 天前 > %d）" % (pf["last_ts"], age, STALE_DAYS)})
            except ValueError:
                pass
    family_cnt = {}
    for c in contracts:
        family_cnt[c["family"]] = family_cnt.get(c["family"], 0) + 1
    stage_cnt = {}
    for k in ("draft", "review", "sign", "perform", "archive"):
        st = {"PASS": 0, "FAIL": 0, "UNVERIFIED": 0}
        for c in contracts:
            st[c["stages"][k]["status"]] += 1
        stage_cnt[k] = st
    missing_sources = [p for p in (GOV_MD, GREENCHECK, CI_CONTRACT_MD, EXEC_CONTRACT_MD) if not os.path.isfile(p)]
    return {
        "schema": "fj-gov-contract-lifecycle-v1",
        "missing_sources": missing_sources,
        "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "root": root,
        "contracts": contracts,
        "alerts": alerts,
        "summary": {
            "contracts_n": len(contracts),
            "families": family_cnt,
            "stages": stage_cnt,
            "gate_runs_n": len(rows),
            "reconcile_registry_n": None if recon is None else len(recon["registered"]),
            "reconcile_snapshot_n": None if recon is None else len(recon["snapshot_ids"]),
            "alerts_n": len(alerts),
            "alerts_by_level": {lv: sum(1 for a in alerts if a["level"] == lv) for lv in ("P0", "P1", "P2")},
            "roles": {"stage_roles": STAGE_ROLES,
                      "non_gate_review_owner": NON_GATE_REVIEW_OWNER,
                      "authority": "本面为权责的机器载体；正文权威=06-benchmark/契约治理与体量治理联动框架_r150_2026-10-21.md §2.1"},
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args(argv)
    doc = build(os.path.abspath(args.root))
    s = doc["summary"]
    # X-24 分母自证：外部件缺失会让登记册在**缩小的分母**上照样自洽（68 降到 57 仍全绿）。
    #   ⇒ 任一外部件缺失即 UNVERIFIED(rc=2)，禁在缩小的面上判绿。
    if doc.get("missing_sources"):
        print("[GOVREG:UNVERIFIED] 外部件缺失 %d 件 => 登记册分母不完整（R247/X-24 禁按绿记）：%s"
              % (len(doc["missing_sources"]), "; ".join(doc["missing_sources"])))
        if args.out:
            os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
            with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
                json.dump(doc, f, ensure_ascii=False, indent=1)
        return 2
    if s["contracts_n"] == 0:
        print("[GOVREG:UNVERIFIED] 零契约入面（面不对或权威源取不到）——R247 禁按绿记")
        return 2
    # 结构自洽：五环节计数之和必须等于契约数（各态之和 == 分母，X-24 口径）
    bad = []
    for k, st in s["stages"].items():
        if st["PASS"] + st["FAIL"] + st["UNVERIFIED"] != s["contracts_n"]:
            bad.append(k)
    print("[GOVREG] 契约登记册 %d 条｜族 %s" % (s["contracts_n"], json.dumps(s["families"], ensure_ascii=False)))
    for k in ("draft", "review", "sign", "perform", "archive"):
        st = s["stages"][k]
        print("  %-8s PASS=%-4d FAIL=%-4d UNVERIFIED=%-4d" % (k, st["PASS"], st["FAIL"], st["UNVERIFIED"]))
    print("[GOVREG] 履约台账 %d 轮｜对账登记 %s 条" % (s["gate_runs_n"], s["reconcile_registry_n"]))
    lv = s["alerts_by_level"]
    print("[GOVREG] 风险预警 P0=%d P1=%d P2=%d" % (lv["P0"], lv["P1"], lv["P2"]))
    for a in doc["alerts"][:12]:
        print("    %-4s %-18s %-28s %s" % (a["level"], a["kind"], a["cid"], a["detail"]))
    if len(doc["alerts"]) > 12:
        print("    ... 另有 %d 条" % (len(doc["alerts"]) - 12))
    # r152（#35 纪律须有阻断点 / R150-6）：P0 预警 = 契约未成立（缺件或缺审核痕）=> 本门判红。
    #   分级：P0 阻断；P1/P2 只显形（advisory）。阻断的**适用范围**由 r137 的 commit-gate-map 决定，
    #   即只在「契约纪律面」变更时被要求通过 —— 不做无差别阻断（R269 反面）。
    if bad:
        print("[GOVREG:FAIL] 环节计数不自洽：%s（各态之和 != 契约数）" % bad)
        rc = 1
    elif lv["P0"] > 0:
        print("[GOVREG:FAIL] P0 契约风险预警 %d 条 => 契约未成立，本门阻断（P1/P2 只显形）" % lv["P0"])
        rc = 1
    else:
        print("[GOVREG:PASS] 五环节计数自洽（各态之和 == 契约数）｜P0 预警 0")
        rc = 0
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print("[GOVREG] 留痕 %s" % args.out)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
