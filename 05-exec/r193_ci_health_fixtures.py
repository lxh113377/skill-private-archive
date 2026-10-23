# -*- coding: utf-8 -*-
"""r193_ci_health_fixtures.py - r32_ci_health 的「近期趋势」口径夹具。

存在理由（r193 一手）：r32 用「近 50 run」全窗口均线判 CI 有效性。本仓 2026-09-25 起
连红 338 个 run，四个根因修完后连续 5 个 push 全绿，但全窗口均线仍是 14% ⇒ 判据继续报
「判据在跑但长期不绿」。那不是新故障，是**历史把均线拖住**；不区分二者，下一轮会把
「已修好的事」继续读成坏的，甚至诱发放宽地板（把判据牙齿磨掉）。

本夹具锁三件事：
  t1 全窗口算得对（不因加趋势口径而变）；
  t2 近期趋势按 created_at 倒序取最近 N 个**已完成** run；
  t3 关键纪律：趋势只作**辅助读数**，不放宽 SUCCESS_FLOOR ——
     全窗口低于地板时仍判 FAIL（只是理由里点名「已修复待观察」）。
"""

import importlib.util as _u
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "r32_ci_health.py")
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-58s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load():
    s = _u.spec_from_file_location("ch", TARGET)
    m = _u.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def run(ts, conc, status="completed"):
    return {"created_at": ts, "status": status, "conclusion": conc}


def main():
    if not os.path.isfile(TARGET):
        ck("t0 判据文件存在", False, "r32_ci_health.py 不存在")
        print("\n[GATE:fixture-fail]")
        return 1
    m = load()
    ck("t0 判据可导入且暴露 SUCCESS_FLOOR", hasattr(m, "SUCCESS_FLOOR"))

    orig_gh = m.gh

    def fake_gh(args):
        class _R:
            pass
        r = _R()
        r.returncode = 0
        r.stdout = io.StringIO.__call__ if False else None
        return r

    # 直接调 sample()，用 monkeypatch 换掉 gh
    _runs = [
        # 旧的 45 个 failure（历史连红）+ 最近 5 个 success（修复后）
        run("2026-10-24T00:0%d:00Z" % i, "success") for i in range(1, 6)
    ] + [
        run("2026-10-20T00:00:00Z", "failure") for _ in range(45)
    ]
    m.gh = lambda args: type("R", (), {"returncode": 0,
                                  "stdout": __import__("json").dumps(_runs)})()
    s = m.sample("x/y", 50, 5)
    m.gh = orig_gh

    # t1 全窗口口径不变（50 个 run、5 success = 10%）
    ck("t1 全窗口 runs 计数与成功率不受趋势口径影响",
       s["runs"] == 50 and s["success_rate"] == 0.1,
       "runs=%s rate=%s" % (s["runs"], s["success_rate"]))

    # t2 近期趋势：最近 5 个已完成的 run，全 success
    _rc = s.get("recent") or {}
    ck("t2 近期趋势取最近 5 个已完成 run 且全计为 success",
       _rc.get("n") == 5 and _rc.get("success") == 5 and _rc.get("rate") == 1.0,
       json_dumps(_rc))

    # t2b 未完成的 run 不得计入趋势（in_progress 不是结论）
    _runs2 = [run("2026-10-24T00:01:00Z", None, "in_progress"),
              run("2026-10-24T00:02:00Z", "success"),
              run("2026-10-23T00:00:00Z", "failure")]
    m.gh = lambda args: type("R", (), {"returncode": 0,
                                  "stdout": __import__("json").dumps(_runs2)})()
    s2 = m.sample("x/y", 50, 5)
    m.gh = orig_gh
    _rc2 = s2.get("recent") or {}
    ck("t2b 未完成 run 不计入近期趋势",
       _rc2.get("n") == 2 and _rc2.get("success") == 1,
       json_dumps(_rc2))

    # t3 纪律：全窗口低于地板时仍须 FAIL（趋势只作辅助，不放宽）
    ck("t3 趋势口径不放宽地板：全窗口 10%% 仍低于 SUCCESS_FLOOR",
       s["success_rate"] < m.SUCCESS_FLOOR,
       "rate=%s floor=%s" % (s["success_rate"], m.SUCCESS_FLOOR))

    fails = [r for r in RESULTS if not r[0]]
    print("\n夹具合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    if fails:
        for _ok, name, detail in fails:
            print("  FAIL %s | %s" % (name, detail))
        print("[GATE:fixture-fail]")
        return 1
    print("[GATE:fixture-pass]")
    return 0


def json_dumps(o):
    import json
    return json.dumps(o, ensure_ascii=False)


if __name__ == "__main__":
    sys.exit(main())