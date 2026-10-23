# -*- coding: utf-8 -*-
# r200_probe_cost_fixtures.py - 第 76 门对账逻辑的夹具（W-47 双向 + 变异腿）。
#
# 关键要证明的牙齿：本面的价值全在「声明 ⇄ 实测不一致即判红」。若这条不测，
# 就等于回到本轮之前的状态 —— 成本无人看守，而且更坏：多了一个假称在看守的面。
# 变异腿还锁我自己踩过的那处：DECL_RE 漏 re.I 会让 10 件全读成未声明（成本面自己少算）。
import importlib.util as _u
import os
import re
import sys

NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "r200_probe_cost_face.py")
RESULTS = []
DECL = "# CALLS_PER_RUN: cloudflare=1 github=0"


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-58s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load():
    spec = _u.spec_from_file_location("pcf", TARGET)
    m = _u.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def mk(cf, gh):
    # 最小件文本。夹具第一版只写 import subprocess，没有 MECH 认的 subprocess.run 字面量，
    # 于是 5 个件全被 has_machinery 滤掉、F1-F6 集体空返回 —— 那是**夹具的错**不是判据的错，
    # 而空返回让断言全线 FAIL（不是静默通过），这条也要记：夹具失效要响，不能哑。
    s = "import subprocess" + NL + "subprocess.run(argv)" + NL
    if cf:
        s += "wrangler d1 list" + NL
    if gh:
        s += "gh api repos" + NL
    return s


def main():
    if not os.path.isfile(TARGET):
        ck("t0 判据件存在", False, TARGET)
        print("[GATE:fixture-fail]")
        return 1
    m = load()
    gates = [
        {"id": "g1", "script": "a.py", "portable": False},
        {"id": "g2", "script": "b.py", "portable": True},
        {"id": "g3", "script": "c.py", "portable": False},
        {"id": "g4", "script": "d.py", "portable": False},
        {"id": "g5", "script": "e.py", "portable": False},
    ]
    texts = {
        "a.py": mk(1, 0) + "# CALLS_PER_RUN: cloudflare=1 github=0",
        "b.py": mk(0, 1) + "# CALLS_PER_RUN: cloudflare=0 github=2",
        "c.py": mk(1, 1),
        "d.py": mk(0, 1) + "# CALLS_PER_RUN: cloudflare=0 github=9",
        "e.py": mk(1, 0),
    }
    measured = {
        "a.py": {"calls": {"cloudflare": 1, "github": 0}},
        "b.py": {"calls": {"cloudflare": 0, "github": 2}},
        "c.py": {"calls": {"cloudflare": 1, "github": 1}},
        "d.py": {"calls": {"cloudflare": 0, "github": 1}},
        "e.py": {"calls": {"cloudflare": 0, "github": 0}},
    }
    rows, problems, totals, ci = m.build(gates, texts, measured)
    st = {r["gate"]: r["state"] for r in rows}
    ck("F1 声明=实测 ⇒ OK 且计入成本",
       st.get("g1") == "OK" and totals.get("cloudflare") == 1, (st, totals))
    ck("F2 portable 门同时计入 CI 足迹",
       st.get("g2") == "OK" and ci.get("github") == 2, (st.get("g2"), ci))
    ck("F3 有实测但无声明 ⇒ UNDECLARED 进 problems",
       st.get("g3") == "UNDECLARED" and any("c.py" in p for p in problems),
       (st.get("g3"), problems))
    ck("F4 声明≠实测 ⇒ MISMATCH 判红（本面的牙齿）",
       st.get("g4") == "MISMATCH" and any("d.py" in p for p in problems),
       (st.get("g4"), problems))
    ck("F5 静态候选但实测 0 次 ⇒ NO_EXTERNAL_CALLS，不计成本也不要求声明",
       st.get("g5") == "NO_EXTERNAL_CALLS"
       and not any("e.py" in p for p in problems), st.get("g5"))
    ck("F6 totals 只含对账一致的件（其余一律不计）",
       totals == {"cloudflare": 1, "github": 2}, totals)

    ck("F7 裸 gh 子串不判厂商（weight/through/although 里的 gh 不算）",
       m.apis_of("a weight throughput although") == [],
       m.apis_of("a weight throughput although"))
    ck("F8 wrangler 判 cloudflare（不走 GraphQL 主机也算 CF 足迹）",
       "cloudflare" in m.apis_of(mk(1, 0)), m.apis_of(mk(1, 0)))
    ck("F9 git push 判 github（推送吃 GitHub 侧配额）",
       "github" in m.apis_of("git push origin main"))
    ck("F10 无外部机械的纯注释件不算候选",
       not m.has_machinery("# only comments here"))

    lower_decl = (mk(1, 0) + DECL).lower()
    ck("F11 真实路径：件文本按 lower 比对，re.I 下仍读到大写声明",
       m.parse_decl(lower_decl) == {"cloudflare": 1, "github": 0},
       m.parse_decl(lower_decl))
    _real = m.DECL_RE
    try:
        m.DECL_RE = re.compile("CALLS_PER_RUN" + chr(92) + "s*:" + chr(92) + "s*(.+)")
        ck("F12 变异：去掉 re.I ⇒ 小写文本里读不到声明（证明 re.I 承重，r200 真错过）",
           m.parse_decl(lower_decl) is None, "去掉 re.I 竟仍读到，变异不成立")
    finally:
        m.DECL_RE = _real

    bak = m.MANIFEST
    try:
        m.MANIFEST = os.path.join(HERE, "__no_such_manifest__.json")
        got, why = m.load_manifest()
        ck("F13 manifest 缺失 ⇒ (None, 原因)，上层出 rc=2 UNVERIFIED（不记绿不判红）",
           got is None and bool(why), why)
    finally:
        m.MANIFEST = bak
    got2, _w2 = m.load_manifest()
    ck("F14 真实 manifest 含本面自身（自我测量 ⇒ 不需排除名单）",
       got2 is not None and "r200_probe_cost_face.py" in got2,
       sorted((got2 or {}).keys())[:3])

    fails = [x for x in RESULTS if not x[0]]
    print("")
    print("夹具合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    print("[GATE:fixture-fail]" if fails else "[GATE:fixture-pass]")
    return 1 if fails else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
