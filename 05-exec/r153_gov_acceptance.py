# -*- coding: utf-8 -*-
# r153_gov_acceptance.py -- 治理考核校验面（A1-A6 一键复跑，三态 + 归属分档）。
#
# 存在理由（r153）：r150 框架报告 §5.2 把「考核校验标准」写成了一张表（A1-A5），
#   但**没有任何一条命令能一键跑完它** —— 表在报告里，人在会话里记得才跑。
#   于是「可落地、可验证、可迭代」里的后两项没有机器承载：标准不可一键复算，也就不可迭代。
#   本件把 A1-A6 落成**常驻复跑面**，每轮一次即可给出逐条三态与总判。
#
# 三态（R247，禁假绿）：
#   PASS       rc==0 且 pass_token 命中（json 型 = 该组计数全为 0）
#   FAIL       rc!=0 / token 缺失 且 rc!=0 / json 型计数 > 0
#   UNVERIFIED **取不到数**（脚本缺失、json 缺字段、子进程不可跑）—— 不得读成 0，也不得读成绿
#
# 归属分档（#47 ③：他人漂移不连坐）：
#   owner="our"     计入总判
#   advisory=True   只显形（归属方侧闭环读数），不影响本面 rc
#
# 阈值来源（**不另立阈值**）：A2 的时效腿直接引用 `memory/06-constraints.md` 已声明的
#   `heartbeat_max_age_days=2`（契约册）与 `snapshot_max_age_days=3`（体量册）。
#
# 用法:
#   python 05-exec/r153_gov_acceptance.py                  # 人读
#   python 05-exec/r153_gov_acceptance.py --json <件>      # 机读留痕
#   python 05-exec/r153_gov_acceptance.py --stub-dir <目录># 夹具：把每条标准换成 <目录>/<Aid>.py
# 退出码: 0 全 PASS / 1 有 FAIL / 2 有 UNVERIFIED（且无 FAIL）
import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
CONTRACT_AGE_MAX_DAYS = 2.0    # = 06-constraints 声明的 heartbeat_max_age_days
VOLUME_AGE_MAX_DAYS = 3.0      # = 06-constraints 声明的 snapshot_max_age_days

CRITERIA = [
    {"id": "A1", "name": "契约登记册结构自洽（各态之和==契约数）",
     "script": "r150_contract_lifecycle.py", "token": "[GOVREG:PASS]", "owner": "our"},
    {"id": "A2", "name": "联动样本量>=3 且两侧读数未陈旧",
     "script": "r150_gov_link.py", "json": True, "owner": "our"},
    {"id": "A3", "name": "体量三层覆盖率 1.0 且未分类 0",
     "script": "r150_volume_tiers.py", "token": "[GOVTIER:PASS]", "owner": "our"},
    {"id": "A4", "name": "三面夹具全过且变异对照有牙",
     "script": "r150_gov_fixtures.py", "token": "[GATE:govfix-pass]", "owner": "our"},
    {"id": "A5", "name": "转办提案四计数为 0（含适用边界）",
     "script": "r136_proposal_evidence.py", "json": True, "owner": "our"},
    {"id": "A6", "name": "归属方侧联动缺陷（advisory，不计总判）",
     "script": "r150_gov_link.py", "json": True, "owner": "owner", "advisory": True},
]


def _run(cmd, cwd):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return None, "subprocess 不可跑：%s" % str(e)[:120]


def judge_json_a2(doc):
    gl = doc.get("gate_ledger") or {}
    vl = doc.get("vol_ledger") or {}
    ga, va = gl.get("age_days"), vl.get("age_days")
    common = doc.get("common_days")
    if common is None or ga is None or va is None:
        return None, "json 缺字段（common_days/age_days 取不到）=> UNVERIFIED 而非 0（R247）"
    legs = [("共同日>=3", common >= 3, "common_days=%s" % common),
            ("契约册龄期<=%.0f天" % CONTRACT_AGE_MAX_DAYS, ga <= CONTRACT_AGE_MAX_DAYS,
             "gate age=%s" % ga),
            ("体量册龄期<=%.0f天" % VOLUME_AGE_MAX_DAYS, va <= VOLUME_AGE_MAX_DAYS,
             "vol age=%s" % va)]
    bad = [n for n, ok, _ in legs if not ok]
    det = "; ".join(d for _, _, d in legs)
    return (not bad), ("%s ｜ 未达：%s" % (det, bad) if bad else det)


def judge_json_a5(doc):
    f = doc.get("face") or {}
    need = ("unbacked_n", "no_acceptance_n", "no_evidence_n")
    if any(k not in f for k in need):
        return None, "json 缺 face.%s 字段 => UNVERIFIED（R247）" % "/".join(need)
    vals = [int(f.get(k) or 0) for k in need]
    bm = f.get("boundary_missing_n")
    if bm is not None:
        vals.append(int(bm or 0))
    return (sum(vals) == 0), "unbacked=%s no_acceptance=%s no_evidence=%s boundary_missing=%s" % (
        f.get("unbacked_n"), f.get("no_acceptance_n"), f.get("no_evidence_n"), bm)


def judge_json_a6(doc):
    ds = doc.get("defects") or []
    kinds = sorted(set(d.get("kind") for d in ds))
    return True, "归属方侧缺陷 %d 条：%s（advisory，不计总判）" % (len(ds), kinds or "无")


JSON_JUDGE = {"A2": judge_json_a2, "A5": judge_json_a5, "A6": judge_json_a6}


def run_criterion(c, root, stub_dir="", tmp=""):
    if stub_dir:
        sp = os.path.join(stub_dir, c["id"] + ".py")
    else:
        sp = os.path.join(root, "05-exec", c["script"])
    if not os.path.isfile(sp):
        return {"status": "UNVERIFIED", "detail": "脚本不在盘：%s" % sp}
    out_json = os.path.join(tmp, "acc_%s.json" % c["id"]) if c.get("json") else ""
    argv = [sys.executable, sp]
    if out_json:
        argv += ["--json", out_json]
    rc, text = _run(argv, root)
    if rc is None:
        return {"status": "UNVERIFIED", "detail": text}
    if c.get("json"):
        if not os.path.isfile(out_json):
            return {"status": "UNVERIFIED", "detail": "子进程未落 json（rc=%s）=> 不得读成 0" % rc}
        try:
            doc = json.load(io.open(out_json, encoding="utf-8"))
        except Exception as e:
            return {"status": "UNVERIFIED", "detail": "json 不可解析：%s" % str(e)[:80]}
        ok, det = JSON_JUDGE[c["id"]](doc)
        if ok is None:
            return {"status": "UNVERIFIED", "detail": det}
        if not ok:
            return {"status": "FAIL", "detail": det}
        return {"status": "PASS", "detail": det}
    tok = c.get("token")
    tk_ok = bool(tok) and (tok in text)
    if rc == 0 and tk_ok:
        return {"status": "PASS", "detail": "rc=0 token=命中"}
    if rc == 0 and not tk_ok:
        # 与 run_gates 同口径：rc==0 但 pass_token 不见 = 静默跳过/标记改名 => UNVERIFIED，不得算绿（R247）
        return {"status": "UNVERIFIED", "detail": "rc=0 但 pass_token 缺失 => 静默跳过不得算绿（R247）"}
    return {"status": "FAIL", "detail": "rc=%s token=%s" % (rc, "命中" if tk_ok else "缺失")}


def build(root, stub_dir=""):
    tmp = tempfile.mkdtemp(prefix="govacc_")
    rows = []
    try:
        for c in CRITERIA:
            r = run_criterion(c, root, stub_dir, tmp)
            r.update({"id": c["id"], "name": c["name"], "owner": c["owner"],
                      "advisory": bool(c.get("advisory"))})
            rows.append(r)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    judged = [r for r in rows if not r["advisory"]]
    fails = [r["id"] for r in judged if r["status"] == "FAIL"]
    unv = [r["id"] for r in judged if r["status"] == "UNVERIFIED"]
    overall = "FAIL" if fails else ("UNVERIFIED" if unv else "PASS")
    return {"schema": "fj-gov-acceptance-v1",
            "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "root": root,
            "criteria": rows,
            "summary": {"n": len(rows), "judged_n": len(judged),
                        "pass_n": sum(1 for r in judged if r["status"] == "PASS"),
                        "fail_ids": fails, "unverified_ids": unv, "overall": overall}}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--json", dest="out", default="")
    ap.add_argument("--stub-dir", dest="stub", default="")
    args = ap.parse_args(argv)
    doc = build(os.path.abspath(args.root), args.stub)
    print("[GOVACC] 治理考核校验面：%d 条标准（计入总判 %d 条）"
          % (doc["summary"]["n"], doc["summary"]["judged_n"]))
    for r in doc["criteria"]:
        tag = "advisory" if r["advisory"] else r["owner"]
        print("  %-3s %-4s [%-8s] %-34s %s"
              % (r["id"], r["status"], tag, r["name"][:34], r["detail"][:96]))
    s = doc["summary"]
    if s["overall"] == "PASS":
        print("[GOVACC:PASS] %d/%d PASS｜FAIL 0｜UNVERIFIED 0" % (s["pass_n"], s["judged_n"]))
        rc = 0
    elif s["overall"] == "FAIL":
        print("[GOVACC:FAIL] 未达标：%s（PASS %d/%d）" % (s["fail_ids"], s["pass_n"], s["judged_n"]))
        rc = 1
    else:
        print("[GOVACC:UNVERIFIED] 取不到数：%s => 不得按绿记（R247）" % s["unverified_ids"])
        rc = 2
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print("[GOVACC] 留痕 %s" % args.out)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
