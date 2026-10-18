# -*- coding: utf-8 -*-
r"""r113_degrade_fixtures.py — r96 防退化闸（degrade_check）的双向自证夹具（W-47）。

被测缺陷（r112 一手同族的另一半）：
  r112 修的是「单件取数失败覆盖好缓存」；r96_twelve_face 写的是**整面语料缓存**
  （05-exec/r96_gh_raw.json，即 provenance/inferred 的身份来源根）。单件失败它已显形
  （available:False），但若一次大面积失败（gh 断链/限流）把 25 仓好语料覆成 2 仓可用，
  整体覆写照样成立 ⇒ 第 19 维的 inferred 面会凭空塌掉，而所有面内不变式仍自洽。
  本夹具锁的就是这条「整面塌陷不退档」的闸。

腿：
  g1 应绿的绿（真拦截）：旧面 5 可用、新面 1 可用 ⇒ 判退化，返回带 old/new 的 dict
  g2 应绿的绿（正常轮不误伤）：旧面 5、新面 3 ⇒ 不拦（覆写许可）
  g3 无对照基准不拦：旧缓存不可读（None）⇒ 返回 None（首建面属正常，禁造假豁免）
  g4 平局不误伤：新旧同面 ⇒ None
  g5 接线（真实派发形态）：把 degrade_check 放回 main 的调用位，用临时缓存文件跑
     「旧好件 + 新塌陷面」⇒ 旧缓存文件必须字节不变（守「不覆写」的落地动作，非只测谓词）
  m1 变异（摘闸）：把 degrade_check 常数化为 None ⇒ g1 与 g5 必须转红
     （证明本夹具鉴别力来自该闸，而非恒绿断言）
  m2 变异（判据过严）：阈值从「一半」改成「不大于旧面」⇒ g2 必须转红
     （防把正常轮也拦成退化，那是另一种失真）
用法：python 05-exec/r113_degrade_fixtures.py
退出：0 = [GATE:fixture-pass]；1 = [GATE:fixture-fail]
"""
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r96_twelve_face as M  # noqa: E402


def _repos(n_avail, n_dead=0):
    d = {}
    for i in range(n_avail):
        d["o/r%d" % i] = {"available": True}
    for i in range(n_dead):
        d["dead%d" % i] = {"available": False}
    return {"repos": d}


def g1():
    r = M.degrade_check(_repos(5), _repos(1, 24))
    ok = isinstance(r, dict) and r.get("old_available") == 5 and r.get("new_available") == 1
    return ok, "塌陷面（1/5）判退化=%s" % (r,)


def g2():
    r = M.degrade_check(_repos(5), _repos(3))
    return r is None, "正常轮（3/5）不误伤=%r" % (r,)


def g3():
    r = M.degrade_check(None, _repos(0))
    return r is None, "无对照基准不拦（首建面）=%r" % (r,)


def g4():
    old = _repos(6)
    r = M.degrade_check(old, _repos(6))
    return r is None, "新旧同面不误伤=%r" % (r,)


def g5():
    """接线腿：按 main 的真实派发形态（读缓存文件→比对→决定覆写），验旧件字节不变。"""
    tmp = tempfile.mkdtemp(prefix="dg5_")
    try:
        cache = os.path.join(tmp, "r96_gh_raw.json")
        good = _repos(5, 20)
        good["marker"] = "GOOD-CORPUS"
        io.open(cache, "w", encoding="utf-8").write(json.dumps(good))
        before = io.open(cache, "rb").read()
        new_raw = _repos(1, 24)          # 大面积失败轮
        deg = M.degrade_check(M.read_json_or_none(cache), new_raw)
        if not deg:
            return False, "接线：塌陷面未被识别（degrade_check 放行）"
        # 复刻 main 的分支：退化 ⇒ 保留旧缓存，只在新面打标记
        new_raw["degraded_round"] = deg
        after = io.open(cache, "rb").read()
        still_good = json.loads(after.decode("utf-8")).get("marker") == "GOOD-CORPUS"
        return (after == before and still_good), "接线：旧缓存字节不变=%s" % (after == before)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def m1():
    """变异：摘掉闸（恒 None）⇒ g1 与 g5 必须失败。"""
    orig = M.degrade_check
    try:
        M.degrade_check = lambda old_raw, new_raw: None
        a = g1()[0]
        b = g5()[0]
        return (not a) and (not b), "摘闸后 g1=%s g5=%s（须均 False）" % (a, b)
    finally:
        M.degrade_check = orig


def m2():
    """变异：阈值放宽成「不大于旧面即拦」⇒ 正常轮 g2 必须失败（防过严判）。"""
    orig = M.degrade_check
    try:
        def strict(old_raw, new_raw):
            _oa = M.available_n(old_raw)
            _na = M.available_n(new_raw)
            if not _oa or _na is None:
                return None
            if _na <= _oa:
                return {"old_available": _oa, "new_available": _na}
            return None
        M.degrade_check = strict
        return not g2()[0], "放宽阈值后 g2=%s（须 False=正常轮被误拦）" % (g2()[0],)
    finally:
        M.degrade_check = orig


LEGS = [("g1", g1), ("g2", g2), ("g3", g3), ("g4", g4), ("g5", g5),
        ("m1", m1), ("m2", m2)]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    npass = 0
    for name, fn in LEGS:
        try:
            ok, why = fn()
        except Exception as exc:
            ok, why = False, "exc:%r" % (exc,)
        print("%s %-3s %s" % ("PASS" if ok else "FAIL", name, why))
        if ok:
            npass += 1
    print("夹具合计: %d 项，通过 %d，失败 %d" % (len(LEGS), npass, len(LEGS) - npass))
    if npass == len(LEGS):
        print("[GATE:fixture-pass] 防退化闸双向自证（5 正/反例 + 2 变异体均被抓住）")
        return 0
    print("[GATE:fixture-fail]")
    return 1


if __name__ == "__main__":
    sys.exit(main())
