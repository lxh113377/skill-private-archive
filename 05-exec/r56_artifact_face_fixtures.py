# -*- coding: utf-8 -*-
"""r56 取证件自证夹具：W-27 / W-32 的两份"裁定依据"必须被契约守且可复跑。

存在理由：这两件过去都由**一次性内联脚本**产出（仓里没有生成器），所以它们是解不出的死句柄；
本轮补了生成器并纳入契约，本夹具再把"契约真的抓得住"钉成常驻断言（含 unknown 合法态，
免得判据反过来逼我造假数）。全部走真实派发：契约用 `baseline_contract_scan.py` 子进程。
"""
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")
CONTRACTS = os.path.join(HERE, "schemas", "r19", "baseline-contracts.json")
BD = "inject_face_breakdown_r56_2026-09-25.json"
TR = "w27_conflict_triage_r56_2026-09-25.json"
BD_PAT = "inject_face_breakdown_r*.json"
TR_PAT = "w27_conflict_triage_r*.json"
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%-4s %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  ← " + str(detail)[:200]) if detail and not cond else ""))


def scan_one(fname, doc, pattern=None):
    """只留**被测那一条** pattern：全量契约里其它 pattern 在临时目录必然零命中，
    而"pattern 命中 0 个文件 = 不判过"会让 rc 永远非 0，把断言淹成恒红（分不清被测缺陷与面截断）。
    """
    pattern = pattern or (BD_PAT if fname.startswith("inject_face_breakdown") else TR_PAT)
    tmp = tempfile.mkdtemp(prefix="r56_face_")
    try:
        io.open(os.path.join(tmp, fname), "w", encoding="utf-8", newline="").write(
            json.dumps(doc, ensure_ascii=False, indent=1))
        full = json.loads(io.open(CONTRACTS, encoding="utf-8-sig").read())
        assert pattern in full["artifacts"], "契约里没有 pattern %s" % pattern
        sub = json.loads(json.dumps(full))
        sub["artifacts"] = {pattern: full["artifacts"][pattern]}
        cp = os.path.join(tmp, "contracts-subset.json")
        io.open(cp, "w", encoding="utf-8", newline="").write(
            json.dumps(sub, ensure_ascii=False, indent=1))
        p = subprocess.run([sys.executable, os.path.join(HERE, "baseline_contract_scan.py"),
                            "--dir", tmp, "--contracts", cp],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=ROOT)
        return p.returncode, (p.stdout or "") + (p.stderr or ""), len(sub["artifacts"])
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def load(p):
    return json.loads(io.open(os.path.join(BENCH, p), encoding="utf-8-sig").read())


def main():
    arts = json.loads(io.open(CONTRACTS, encoding="utf-8-sig").read())["artifacts"]
    ck("e1 覆盖面前置：两份裁定依据件都必须在契约里有 pattern（防被静默脱管）",
       any(k.startswith("inject_face_breakdown") for k in arts)
       and any(k.startswith("w27_conflict_triage") for k in arts),
       sorted(arts))

    rc0, o0, _ = scan_one(BD, load(BD))
    ck("e2 正例：现盘 breakdown 过契约", rc0 == 0, o0[-260:])
    rc0t, o0t, _ = scan_one(TR, load(TR))
    ck("e2b 正例：现盘 triage 过契约", rc0t == 0, o0t[-260:])

    d = load(BD)
    d["measured_total"] = d["measured_total"] + 1
    rc1, o1, _ = scan_one(BD, d)
    ck("e3 反例：measured_total 与逐件求和不符 ⇒ 判红且点名 INJECT-BD",
       rc1 != 0 and "INJECT-BD" in o1, "rc=%s tail=%s" % (rc1, o1[-240:]))

    d2 = load(BD)
    d2["files"] = []
    rc2, o2, _ = scan_one(BD, d2)
    ck("e4 反例：files 空数组 ⇒ 红（空面不得当已拆解，R247）",
       rc2 != 0 and "INJECT-BD" in o2, "rc=%s tail=%s" % (rc2, o2[-240:]))

    d3 = load(BD)
    d3["measured_total"] = None
    d3["over_cap"] = None
    rc3, o3, _ = scan_one(BD, d3)
    ck("e5 方向反例：显式 unknown（measured_total=None）⇒ 不判红，禁逼我造一个数",
       rc3 == 0, "rc=%s tail=%s" % (rc3, o3[-240:]))

    t = load(TR)
    t["duplicated_pairs"] = t["duplicated_pairs"] + 5
    rc4, o4, _ = scan_one(TR, t)
    ck("e6 反例：triage 三数算术被改 ⇒ 红（total-distinct 必须等于 duplicated）",
       rc4 != 0 and "TRIAGE" in o4, "rc=%s tail=%s" % (rc4, o4[-240:]))

    t2 = load(TR)
    t2["total_candidates"] = 0
    rc5, o5, _ = scan_one(TR, t2)
    ck("e7 反例：候选数为 0 ⇒ 红（空面不得当「已复核无冲突」）",
       rc5 != 0 and "TRIAGE" in o5, "rc=%s tail=%s" % (rc5, o5[-240:]))

    t3 = load(TR)
    t3["decision_needed"] = []
    rc6, o6, _ = scan_one(TR, t3)
    ck("e8 反例：只数不呈裁定（decision_needed 空）⇒ 红（交回去的东西必须含裁定问句）",
       rc6 != 0 and "TRIAGE" in o6, "rc=%s tail=%s" % (rc6, o6[-240:]))

    # e9/e10 = 代际豁免自身的两条锁：豁免不是万能挡箭牌，且必须看得见
    d4 = load(BD)
    d4["generated_at"] = "2026-09-25T19:40:00"
    d4.pop("by_owner", None)
    rc7, o7, _ = scan_one(BD, d4)
    ck("e9 反例（豁免有牙齿）：分叉点**之后**的件缺 by_owner ⇒ 仍须判红（豁免只救历史件）",
       rc7 != 0 and "by_owner" in o7, "rc=%s tail=%s" % (rc7, o7[-240:]))
    rc8, o8, _ = scan_one(BD, load(BD))
    ck("e10 豁免可见性：扫描输出必须打印「代际豁免」计数行（看不见的豁免=豁免表，R247）",
       "代际豁免" in o8, o8[-200:])

    fails = [r for r in RESULTS if not r[0]]
    print("\n夹具合计: %d 项，通过 %d，失败 %d"
          % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    print("[GATE:fixture-fail]" if fails else "[GATE:fixture-pass]")
    return 1 if fails else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
