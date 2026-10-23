# -*- coding: utf-8 -*-
"""r195_est_fixtures.py — 棘轮选件「估界法」的常驻夹具（W-47 双向 + 变异腿）。

存在理由（r195 一手）：棘轮报 overdue_debt_items=3 而 r38 真值 1。根因是同 glob 混两族
命名 —— 手工件 debt_aging_r195_fix.json（名无日期、mtime 最新）与自研件
debt_aging_r_autoregen_20261024_021326.json（紧凑时间戳），r190 版都取不到 YYYY-MM-DD，
于是同退到 mtime-day（同一天）再按名比字符：'_'(0x5F) > '1'(0x31) 选中旧件 => 假红。
r190 当时只用临时脚本自证，而临时件会被并行会话按扩展名清场（R189-2 / R191-1 两度在册
教训）=> 本轮固化为常驻夹具。

腿：A 真机态 / B CI 平 mtime 态 / B2 全平确定性 / C 反假绿（旧名 + checkout 刷新的 mtime）
    / D 变异（纯按名 => A 必须变红。靶选 A 不选 C：C 里变异与正解同解，是我第一版的错）
    / D2 两族正则各归其位。
"""
import glob
import importlib.util as _u
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TARGET = HERE / "ratchet_gate.py"
RESULTS = []

N_DASH = "debt_aging_r107_2026-10-15.json"
N_COMPACT = "debt_aging_r_autoregen_20261024_021326.json"
N_PLAIN = "debt_aging_r195_fix.json"


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-54s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load():
    s = _u.spec_from_file_location("rg_est", str(TARGET))
    m = _u.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def mk(td, spec):
    for nm, mt in spec:
        fp = os.path.join(td, nm)
        with open(fp, "w", encoding="utf-8") as f:
            f.write("{}")
        if mt is not None:
            os.utime(fp, (mt, mt))


def main():
    if not TARGET.is_file():
        ck("t0 被测件存在", False, "缺 " + TARGET.name)
        print("[GATE:fixture-fail]")
        return 1
    m = load()
    base_ts = 1700000000.0

    # A 真机态：mtime 有先后，估界 = min(名字上界, mtime) 应选中 mtime 最新的无日期件
    with tempfile.TemporaryDirectory(prefix="r195A_") as td:
        mk(td, [(N_PLAIN, base_ts + 5000), (N_COMPACT, base_ts + 4000),
                (N_DASH, base_ts + 1000)])
        got = os.path.basename(m._newest_artifact(Path(td) / "debt_aging_r*.json") or "")
        ck("A 真机态：mtime 最新的无日期件胜出", got == N_PLAIN, got)

    # B CI 态：mtime 全平，只能靠名字时间戳
    with tempfile.TemporaryDirectory(prefix="r195B_") as td:
        mk(td, [(N_DASH, base_ts), (N_COMPACT, base_ts), (N_PLAIN, base_ts)])
        got = os.path.basename(m._newest_artifact(Path(td) / "debt_aging_r*.json") or "")
        ck("B CI 平 mtime：紧凑时间戳赢过连字符旧日", got == N_COMPACT, got)

    # B2 全平且一方无名字时间：仍须确定（不得依赖 glob 顺序）
    with tempfile.TemporaryDirectory(prefix="r195B2_") as td:
        mk(td, [(N_PLAIN, base_ts), (N_DASH, base_ts)])
        got = os.path.basename(m._newest_artifact(Path(td) / "debt_aging_r*.json") or "")
        ck("B2 全平且一方无名字时间仍确定选出", got in (N_PLAIN, N_DASH) and bool(got), got)

    # C 反假绿：名字日期很旧，但 mtime 被 checkout 刷成今天
    with tempfile.TemporaryDirectory(prefix="r195C_") as td:
        now = datetime.now().timestamp()
        mk(td, [("debt_aging_r100_2026-09-01.json", now), (N_COMPACT, now - 60)])
        got = os.path.basename(m._newest_artifact(Path(td) / "debt_aging_r*.json") or "")
        ck("C 反假绿：旧名+刷新 mtime 不被选中", got == N_COMPACT, got)

    # D 变异：退回纯按名 => A 场景必须变红
    orig = m._newest_artifact

    def _name_only(glob_pat):
        fs = glob.glob(str(glob_pat))
        if not fs:
            return None
        return max(fs, key=os.path.basename)

    m._newest_artifact = _name_only
    try:
        with tempfile.TemporaryDirectory(prefix="r195D_") as td:
            mk(td, [(N_PLAIN, base_ts + 5000), (N_COMPACT, base_ts + 4000),
                    (N_DASH, base_ts + 1000)])
            got = os.path.basename(_name_only(Path(td) / "debt_aging_r*.json") or "")
            ck("D 变异：纯按名 => A 被错件夺走（估界非装饰）", got != N_PLAIN, got)
    finally:
        m._newest_artifact = orig

    # D2 两族正则各归其位
    mm = m._NAME_STAMP_RE.search(N_COMPACT)
    ck("D2 紧凑式可解析、连字符式取不到",
       bool(mm) and not m._NAME_DATE_RE.search(N_COMPACT)
       and mm.groups()[:3] == ("2026", "10", "24"),
       mm.groups() if mm else None)

    fails = [r for r in RESULTS if not r[0]]
    print("")
    print("夹具合计: %d 项，通过 %d，失败 %d"
          % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    if fails:
        for _ok, nm, det in fails:
            print("  FAIL %s | %s" % (nm, det))
        print("[GATE:fixture-fail]")
        return 1
    print("[GATE:fixture-pass]")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
