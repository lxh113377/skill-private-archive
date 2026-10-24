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

    _B78_UNVERIFIED = False
    # b7 真实派发：预算来源必须在 CLI 输出里看得见（声明看不见 = 等于没声明）
    # r208 修（接线腿与现状腿解耦，照 r202/r54 先例）：「预算来源」只印在 PASS 分支，
    # 而项目一有真实活债（overdue 3 > 基线 0）就走 FAIL 分支 ⇒ b7 恒红。
    # 那不是打印缺陷，是夹具把「本项目此刻绿不绿」焊进「声明行有没有被打印」。
    # 修法：临时基线 = 真基线骨架 + 现测指标值 ⇒ 无增长面 ⇒ 必走 PASS 分支，
    # 断言的是「PASS 分支上预算来源行确实被打印」这个接线事实。
    env = dict(os.environ, PYTHONPYCACHEPREFIX=r"C:/tmp/pyc_r56")
    _td7 = tempfile.mkdtemp(prefix="r56_b7_")
    try:
        _tb7 = os.path.join(_td7, "inject_ratchet_baseline.json")
        _d7 = base_doc()
        with io.open(_tb7, "w", encoding="utf-8", newline="") as f:
            json.dump(_d7, f, ensure_ascii=False, indent=1)
        subprocess.run([sys.executable, os.path.join(HERE, "ratchet_gate.py"),
                        "--baseline", _tb7, "--json", os.path.join(_td7, "live.json")],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, cwd=ROOT)
        try:
            with io.open(os.path.join(_td7, "live.json"), encoding="utf-8-sig") as f:
                _live7 = json.load(f)
            if isinstance(_live7.get("metrics"), dict) and _live7["metrics"]:
                _d7["metrics"] = dict(_live7["metrics"])
                with io.open(_tb7, "w", encoding="utf-8", newline="") as f:
                    json.dump(_d7, f, ensure_ascii=False, indent=1)
        except Exception:
            pass
        p7 = subprocess.run([sys.executable, os.path.join(HERE, "ratchet_gate.py"),
                             "--baseline", _tb7],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", env=env, cwd=ROOT)
    finally:
        shutil.rmtree(_td7, ignore_errors=True)
    o7 = (p7.stdout or "") + (p7.stderr or "")
    # r209 修 R113-5 第三种形态：r208 只解耦「增长面」，没解耦「指标缺失面」——
    # 本机 username_in_skill_files 恒算不出 ⇒ ratchet 走 unknown 分支 rc=1，
    # 而「预算来源」只印在 PASS 分支 ⇒ b7 恒红，且红因与打印代码无关。
    # 三态分流（第三态不得算通过，同 r208/r54 教训）：
    #   含「缺失指标」⇒ 本腿 UNVERIFIED（不判红也不判绿）
    #   否则必须看到「预算来源」（真打印缺陷仍红）
    if "缺失指标" in o7:
        print("SKIP %-56s %s" % ("b7 真实 CLI：指标缺失面未解除（UNVERIFIED，非打印缺陷）", "  <-- " + o7.strip().splitlines()[-1][:150] if o7.strip() else "无输出"))
        _B78_UNVERIFIED = True
    else:
        ck("b7 真实 CLI：PASS 分支必须打印「预算来源」（能看见来源才谈得上被谁看守）",
           "预算来源" in o7, o7[-300:])

    # b8/b9 --update 的两条口径：预算随基线存活 + 代码常量改了也不得覆盖基线（代码只读不写）
    # r190 修（CI 一手，clone 复现）：原写死 `C:/tmp/...` —— Linux runner 无 C:/tmp，
    #   --update 写不进临时件 ⇒ rc!=0 ⇒ b8/b9 恒红。用 tempfile 取当前平台临时目录，
    #   并在 finally 里清（跨平台；不假设任何盘符）。
    _tmpdir = tempfile.mkdtemp(prefix="r56_budget_")
    tmp = os.path.join(_tmpdir, "r56_update_baseline.json")
    d = base_doc()
    d["note"] = str(d.get("note", "")) + " ｜夹具哨兵留账"
    d["refresh_days"]["overdue_debt_items"] = 9
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    # r208 修（接线腿与现状腿解耦）：--update 在项目有真实活债时会**正确地**拒绝写入
    # （[RATCHET:REFUSE] 拒绝抬基线）⇒ rc=1 ⇒ b8 恒红。那不是写入缺陷，是夹具把
    # 「本项目此刻有没有超基线债」焊进「--update 会不会保留预算与留账」。
    # 修法：先把临时基线的指标对齐现测值（无增长面 ⇒ 拒写分支不触发），
    # 再断言预算与留账在写入路径上存活。拒绝写入本身由 ratchet_gate 与
    # r123 区间归因夹具（t1/t2/t7）专门看守，此处不重复断言。
    subprocess.run([sys.executable, os.path.join(HERE, "ratchet_gate.py"),
                    "--baseline", tmp, "--json", os.path.join(_tmpdir, "live8.json")],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", env=env, cwd=ROOT)
    try:
        with io.open(os.path.join(_tmpdir, "live8.json"), encoding="utf-8-sig") as f:
            _live8 = json.load(f)
        if isinstance(_live8.get("metrics"), dict) and _live8["metrics"]:
            d["metrics"] = dict(_live8["metrics"])
            with io.open(tmp, "w", encoding="utf-8", newline="") as f:
                json.dump(d, f, ensure_ascii=False, indent=1)
    except Exception:
        pass
    p8 = subprocess.run([sys.executable, os.path.join(HERE, "ratchet_gate.py"),
                         "--baseline", tmp, "--update"],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", env=env, cwd=ROOT)
    after = json.loads(io.open(tmp, encoding="utf-8-sig").read())
    _o8 = (p8.stdout or "") + (p8.stderr or "")
    # r209 修 R113-5 同族第三种形态：--update 在有算不出的指标时会**正确地**拒绝写基线
    # （[RATCHET:REFUSE] 禁止把算不出的项写成 0）⇒ rc=1 ⇒ b8 恒红，而红因与
    # 「预算与留账是否一起存活」无关。三态分流，第三态不算通过。
    if "缺失指标" in _o8 or "拒绝写基线" in _o8:
        print("SKIP %-56s %s" % ("b8 真实 --update：指标缺失面触发拒写（UNVERIFIED，非写入缺陷）",
                                 "  <-- " + (_o8.strip().splitlines()[-1][:150] if _o8.strip() else "无输出")))
        _B78_UNVERIFIED = True
    else:
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
    shutil.rmtree(_tmpdir, ignore_errors=True)

    fails = [r for r in RESULTS if not r[0]]
    print("\n夹具合计: %d 项，通过 %d，失败 %d"
          % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    if fails:
        print("[GATE:fixture-fail]")
        return 1
    if _B78_UNVERIFIED:
        print("[GATE:fixture-unverified] b7/b8 因本机指标缺失面未验证（非判据红，R247 不按绿记）")
        return 2
    print("[GATE:fixture-pass]")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
