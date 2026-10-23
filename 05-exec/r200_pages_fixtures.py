# -*- coding: utf-8 -*-
# r200_pages_fixtures.py - Pages HTTP 量面的夹具（W-47 双向 + 变异腿）。
#
# 锁四件事，都是本轮实测撞到的：
#   P1 结构不符 ⇒ None（不得折算成 0）：缺 sum / requests 非数值 / 布尔 / 空账号列表
#   P2 任一行结构不符即整读数作废（不把部分当全量，R247）
#   P3 参数名口径：1d 用 date_geq/date_leq（Date 型，YYYY-MM-DD），与 adaptive 的
#      datetime_geq/datetime_leq 不同名；照抄官方 examples 会把 1d 打挂（实测 unknown arg）
#   P4 门契约：MEASURED 才出 [QUOTA:PASS]，取不到不得带 PASS 字样
import importlib.util as _u
import os
import sys

NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TARGET = os.path.join(HERE, "r200_pages_face.py")
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-56s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load():
    spec = _u.spec_from_file_location("pf", TARGET)
    m = _u.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def wrap(rows):
    return {"data": {"viewer": {"accounts": [{"httpRequests1dGroups": rows}]}}}


def main():
    if not os.path.isfile(TARGET):
        ck("t0 判据件存在", False, TARGET)
        print("[GATE:fixture-fail]")
        return 1
    m = load()

    good = wrap([{"sum": {"requests": 100}, "dimensions": {"date": "2026-10-01"}},
                 {"sum": {"requests": 250}, "dimensions": {"date": "2026-10-02"}}])
    rows = m.unwrap_payload(good)
    tot, days, per = m.sum_days(rows)
    ck("P1 正常两行求和=350、天数=2", tot == 350 and days == 2, (tot, days))

    # 结构不符一族必须全部 None（不得当作 0）
    shapes = [
        ("errors 存在", {"errors": [{"message": "boom"}]}),
        ("无 data", {"nope": 1}),
        ("accounts 非 list", {"data": {"viewer": {"accounts": {}}}}),
        ("accounts 空列表", {"data": {"viewer": {"accounts": []}}}),
        ("缺 dataset 键", {"data": {"viewer": {"accounts": [{"other": 1}]}}}),
    ]
    for label, doc in shapes:
        ck("P2 结构不符 ⇒ unwrap None（%s）" % label, m.unwrap_payload(doc) is None, label)

    # 行级坏形状：任一行不合 ⇒ 整读数作废，不得只加好的那行
    bad_rows = [
        ("缺 sum", [{"dimensions": {"date": "d"}}]),
        ("sum 非 dict", [{"sum": 5, "dimensions": {"date": "d"}}]),
        ("requests 字符串", [{"sum": {"requests": "NaN"}, "dimensions": {"date": "d"}}]),
        ("requests 布尔", [{"sum": {"requests": True}, "dimensions": {"date": "d"}}]),
        ("requests 缺失", [{"sum": {"errors": 1}, "dimensions": {"date": "d"}}]),
    ]
    for label, rows_bad in bad_rows:
        t, d, p = m.sum_days(rows_bad)
        ck("P3 行级坏形状 ⇒ total None（%s）" % label, t is None, (label, t, d))

    # P4 混合：一行好一行坏 ⇒ 整批作废（不把部分当全量）
    mixed = [{"sum": {"requests": 10}, "dimensions": {"date": "a"}},
             {"sum": {"requests": None}, "dimensions": {"date": "b"}}]
    t4, d4, p4 = m.sum_days(mixed)
    ck("P4 一行好一行坏 ⇒ 整批 None（不把部分当全量）", t4 is None, (t4, d4))

    # P5 空数据集是真值 0：rows=[] 应 total=0 days=0（区别于结构不符）
    t5, d5, p5 = m.sum_days([])
    ck("P5 空数据集 ⇒ 0 次（真值），非 None", t5 == 0 and d5 == 0, (t5, d5))

    # P6 参数名口径：件里必须用 date_geq/date_leq + Date 变量，绝不得出现 datetime_geq
    txt = open(TARGET, encoding="utf-8").read()
    ck("P6 用 date_geq/date_leq（1d 数据集口径）",
       "date_geq" in txt and "date_leq" in txt, "缺关键字")
    ck("P7 不照抄 adaptive 的 datetime_geq（抄了会 unknown arg）",
       "datetime_geq" not in txt.split("Q_1D")[1][:400], "1d 查询里混入了 datetime_geq")
    ck("P8 变量声明为 Date 型（不是 string）", "$a: Date" in txt and "$b: Date" in txt)

    # P9 门契约：token 只在 MEASURED 分支出
    tok_line = [l for l in txt.split(NL) if m.TOKEN_TEXT in l]
    ck("P9 PASS 标记只出现在 MEASURED 打印路径", len(tok_line) == 1, tok_line)
    ck("P10 TOKEN 常量存在且非空", bool(m.TOKEN_TEXT) and "PASS" in m.TOKEN_TEXT)

    # P11 post() 网络耗尽 ⇒ None（不可得），不得返回空 dict 让上层读成 0
    calls = {"n": 0}

    def boom(*a, **k):
        calls["n"] += 1
        raise OSError("URLError simulated")
    import urllib.request as UR
    real = UR.urlopen
    UR.urlopen = boom
    try:
        got = m.post(m.Q_1D, {"accountTag": "x", "a": "2026-10-01", "b": "2026-10-02"},
                     "tok", "https://example.invalid/graphql", tries=3, sleeper=lambda s: None)
    finally:
        UR.urlopen = real
    ck("P11 网络全失败 ⇒ post 返回 None（且真重试了 3 次）",
       got is None and calls["n"] == 3, (got, calls["n"]))

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
