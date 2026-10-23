# -*- coding: utf-8 -*-
# r201_r2_fixtures.py - R2 启用状态面的夹具（judge 是纯函数 ⇒ 零联网测全部形态）。
#
# 本件的命门只有一条：**活性对照不通过时，绝不允许输出 GAP_SERVICE**。
# 因为那等于把「凭据失效」记成「平台没开通」—— 而后者会被当成已定案，
# 这一项从此不再被重探（r163 时代就是这么把 R2 记死的：当时只试过 wrangler）。
# 变异腿 F7 专门证明：拿掉对照检查后，凭据全死的场景会被误判成 GAP_SERVICE。
import importlib.util as _u
import os
import sys

NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "r201_r2_enable_face.py")
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-58s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load():
    spec = _u.spec_from_file_location("r2f", TARGET)
    m = _u.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def ok_accounts():
    return (200, {"success": True, "result": {"id": "x"}}, "")


def buckets_10042():
    return (403, {"success": False, "errors": [{"code": 10042,
                                                "message": "enable R2"}]}, "")


def subs_10000():
    return (403, {"success": False, "errors": [{"code": 10000,
                                                "message": "Authentication error"}]}, "")


def main():
    if not os.path.isfile(TARGET):
        ck("t0 判据件存在", False, TARGET)
        print("[GATE:fixture-fail]")
        return 1
    m = load()

    st, why, det = m.judge(ok_accounts(), buckets_10042(), subs_10000(), 1, '"code":10042')
    ck("F1 对照活 + buckets10042 + 订阅不通 ⇒ GAP_SERVICE（带证据）",
       st == "GAP_SERVICE" and det.get("control") == "alive"
       and det.get("buckets_code") == 10042, (st, det))

    st2, why2, d2 = m.judge((403, {"success": False, "errors": [{"code": 10000}]}, ""),
                            buckets_10042(), subs_10000(), 1, "")
    ck("F2 命门：对照不活 ⇒ UNVERIFIED，绝不得记 GAP_SERVICE",
       st2 == "UNVERIFIED", (st2, why2[:70]))

    st3, why3, d3 = m.judge((0, {}, "网络异常"), buckets_10042(), subs_10000(), 1, "")
    ck("F3 对照取不到响应（status=0）⇒ UNVERIFIED（不猜）",
       st3 == "UNVERIFIED", (st3, why3[:60]))

    st4, why4, d4 = m.judge(ok_accounts(),
                            (200, {"success": True, "result": [{"name": "b1"}]}, ""),
                            subs_10000(), 0, "")
    ck("F4 buckets 200 有桶 ⇒ MEASURED（服务已启用）",
       st4 == "MEASURED" and "桶数 1" in why4, (st4, why4))

    st5, _w5, d5 = m.judge(ok_accounts(), (200, {"success": True, "result": []}, ""),
                           subs_10000(), 0, "")
    ck("F5 空桶列表是真值 0 桶（MEASURED，不得当取不到）",
       st5 == "MEASURED" and "桶数 0" in _w5, (st5, _w5))

    st6, why6, _d6 = m.judge(ok_accounts(), buckets_10042(),
                             (200, {"success": True, "result": []}, ""), 1, "")
    ck("F6 订阅通路未定（subs 200）⇒ UNVERIFIED 不硬判平台缺口",
       st6 == "UNVERIFIED", (st6, why6[:70]))

    st7, why7, _d7 = m.judge(ok_accounts(), (500, {}, "网络异常"), subs_10000(), 1, "")
    ck("F7 未知形态（buckets 500）⇒ UNVERIFIED，不套 10042 结论",
       st7 == "UNVERIFIED", (st7, why7[:60]))

    # 变异（W-47）：拿掉活性对照 ⇒ F2 那种凭据全死场景会被误判成 GAP_SERVICE
    real = m.judge
    try:
        def no_control(a, b, c, wr_rc, wr_out):
            return real(ok_accounts(), b, c, wr_rc, wr_out)
        m.judge = no_control
        st8, _w8, _d8 = m.judge((403, {"success": False}, ""), buckets_10042(),
                                subs_10000(), 1, "")
        ck("F8 变异：绕过对照后同输入被判成 GAP_SERVICE（证明对照是承重的）",
           st8 == "GAP_SERVICE", st8)
    finally:
        m.judge = real

    ck("F9 cf_code 缺 errors 时返回 None（不得当成 0 号错误）",
       m.cf_code({"success": True}) is None and m.cf_code(None) is None)
    ck("F10 CALLS_PER_RUN 声明在位（第 76 门对账要求）",
       "CALLS_PER_RUN" in open(TARGET, encoding="utf-8").read())

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
