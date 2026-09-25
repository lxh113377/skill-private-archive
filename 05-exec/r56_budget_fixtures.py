# -*- coding: utf-8 -*-
"""r56 W-37 夹具：把「指标再生预算」从代码常量升级为被契约看守的声明面。

存在理由（r54 W-36 的续款，r54 报告 D-97 登记）：预算 `METRIC_REFRESH_DAYS` 只存在于
`05-exec/ratchet_gate.py` 里，**契约看不见它** —— 任何人删掉某一项，`collect_metrics`
只会静默少一项而不报错，"多久必须重算"这条声明于是退化成没人看守的注释。对手对照：
pre-commit/spec-kit 把节律写进被 CI 解析的 workflow 文件里（声明即被校验）。
本套件双向取证件：缺键/多键/越界必须红（b1-b3、b9），现件必须绿（b4），
且**禁止代码值冒充基线值**（b6：静默回落就是新的豁免表，X-9 的反面）。
按 X-28：契约与 CLI 断言一律走真实派发（子进程 + 真参数），不偷调内部函数。
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")
CONTRACTS = os.path.join(HERE, "schemas", "r19", "baseline-contracts.json")
PATTERN = "inject_ratchet_baseline.json"
sys.path.insert(0, HERE)
import ratchet_gate as rg  # noqa: E402

RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%-4s %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  ← " + str(detail)[:220]) if detail and not cond else ""))


def base_doc():
    with io.open(os.path.join(BENCH, PATTERN), encoding="utf-8-sig") as f:
        return json.load(f)


def run_scan(doc, mutate=None):
    """把（可选改写后的）基线件放进临时目录跑真实契约扫描器，返回 (rc, 输出)。

    契约文件同样只留**本件那一条 spec**：全量契约里有 `debt_runs.jsonl` 等 pattern，
    临时目录里没有它们 ⇒ 「pattern 命中 0 个文件 = 不判过」会把断言淹成恒红，
    分不清是被测缺陷还是面被截断（R-ENUM 覆盖面口径）。
    """
    tmp = tempfile.mkdtemp(prefix="r56_budget_")
    try:
        d = json.loads(json.dumps(doc))
        if mutate:
            mutate(d)
        with io.open(os.path.join(tmp, PATTERN), "w", encoding="utf-8", newline="") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        full = json.loads(io.open(CONTRACTS, encoding="utf-8-sig").read())
        sub = json.loads(json.dumps(full))
        sub["artifacts"] = {k: v for k, v in full["artifacts"].items()
                           if k == "inject_ratchet_baseline*.json"}
        cpath = os.path.join(tmp, "contracts-subset.json")
        with io.open(cpath, "w", encoding="utf-8", newline="") as f:
            json.dump(sub, f, ensure_ascii=False, indent=1)
        env = dict(os.environ, PYTHONPYCACHEPREFIX=r"C:/tmp/pyc_r56")
        p = subprocess.run([sys.executable, os.path.join(HERE, "baseline_contract_scan.py"),
                            "--dir", tmp, "--contracts", cpath],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=ROOT)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    doc = base_doc()
    names = set(rg.METRIC_NAMES)

    ck("b0 声明面存在：基线件必须承载 refresh_days（缺即整轮红，不许回落代码值）",
       isinstance(doc.get("refresh_days"), dict), "keys=%s" % sorted(doc.keys()))

    rd = doc.get("refresh_days") or {}

    def drop_one(d):
        d.setdefault("refresh_days", dict(rd)).pop("overdue_debt_items", None)

    rc1, o1 = run_scan(doc, drop_one)
    ck("b1 反例：基线少一个指标预算 ⇒ 契约判红且点名该指标",
       rc1 != 0 and "overdue_debt_items" in o1, "rc=%s tail=%s" % (rc1, o1[-260:]))

    rc2, o2 = run_scan(doc, lambda d: d.setdefault("refresh_days", dict(rd)).update(
        {"zombie_metric_days": 7}))
    ck("b2 反例：预算里多一个未知指标 ⇒ 契约判红（僵尸声明同样不许存在）",
       rc2 != 0 and "zombie_metric_days" in o2, "rc=%s tail=%s" % (rc2, o2[-260:]))

    bad_cases = []
    for v in (0, -3, "30", 1.5, 999):
        rcx, ox = run_scan(doc, lambda d, v=v: d.setdefault("refresh_days", dict(rd)).update(
            {"desc_over_cap": v}))
        bad_cases.append((repr(v), rcx != 0))
    ck("b3 反例：预算值越界/形态不对（0、负、字符串、小数、超上限）⇒ 全部判红",
       all(ok for _, ok in bad_cases), bad_cases)

    rc4, o4 = run_scan(doc)
    ck("b4 正例：现件（9/9 预算齐、值在 (1,60]）⇒ 契约绿",
       rc4 == 0, "rc=%s tail=%s" % (rc4, o4[-260:]))

    ck("b5 覆盖面自证：预算键集合必须与 METRIC_NAMES 全等（分母不靠手抄）",
       set(rd) == names and len(rd) == len(names),
       "基线=%d 代码=%d 差=%s" % (len(rd), len(names), sorted(set(rd) ^ names)))

    # b6 禁止静默回落：基线没有预算时，refresh_status 不得拿代码常量冒充"已声明"
    saved = rg.BASELINE_REFRESH_DAYS
    try:
        rg.BASELINE_REFRESH_DAYS = {}
        st = rg.refresh_status()
        unv = {k: v for k, v in st.items() if v[0] == "UNVERIFIED"}
        ck("b6 反例（禁豁免表）：基线缺预算 ⇒ 全部 UNVERIFIED 且理由指认基线，不得回落代码值",
           len(unv) == len(names) and all(v[2] is None and ("基线" in str(v[3]) or "未声明" in str(v[3]))
                                         for v in unv.values()),
           "unv=%d/%d 例=%s" % (len(unv), len(names), list(unv.items())[:2]))
    finally:
        rg.BASELINE_REFRESH_DAYS = saved

    # b7 真实派发：预算来源必须在 CLI 输出里看得见（声明看不见 = 等于没声明）
    env = dict(os.environ, PYTHONPYCACHEPREFIX=r"C:/tmp/pyc_r56")
    p7 = subprocess.run([sys.executable, os.path.join(HERE, "ratchet_gate.py")],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", env=env, cwd=ROOT)
    o7 = (p7.stdout or "") + (p7.stderr or "")
    ck("b7 真实 CLI：必须打印「预算来源」（能看见来源才谈得上被谁看守）",
       "预算来源" in o7, o7[-300:])

    # b8/b9 --update 的两条口径：预算随基线存活 + 代码常量改了也不得覆盖基线（代码只读不写）
    tmp = os.path.join(r"C:/tmp", "r56_update_baseline.json")
    d = base_doc()
    d["note"] = str(d.get("note", "")) + " ｜夹具哨兵留账"
    d["refresh_days"]["overdue_debt_items"] = 9
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    p8 = subprocess.run([sys.executable, os.path.join(HERE, "ratchet_gate.py"),
                         "--baseline", tmp, "--update"],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", env=env, cwd=ROOT)
    after = json.loads(io.open(tmp, encoding="utf-8-sig").read())
    ck("b8 真实 --update：预算与 note 留账必须一起存活（D-104 同族再犯防护）",
       p8.returncode == 0 and (after.get("refresh_days") or {}).get("overdue_debt_items") == 9
       and "夹具哨兵留账" in str(after.get("note")),
       "rc=%s rd=%s note=%s" % (p8.returncode, (after.get("refresh_days") or {}).get(
           "overdue_debt_items"), str(after.get("note"))[-60:]))
    ck("b9 代码只读不写：基线预算与代码常量不同（9 vs 3）时 --update 必须保留基线值",
       (after.get("refresh_days") or {}).get("overdue_debt_items") == 9
       and rg.METRIC_REFRESH_DAYS.get("overdue_debt_items") != 9,
       "基线=%s 代码=%s" % ((after.get("refresh_days") or {}).get("overdue_debt_items"),
                            rg.METRIC_REFRESH_DAYS.get("overdue_debt_items")))
    os.remove(tmp)

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
