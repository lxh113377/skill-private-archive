# -*- coding: utf-8 -*-
r"""r105_debt_face_freshness_fixtures.py — 账龄三态「相对新鲜前置」的 W-47 双向证据。

被测对象（不在本件里重写谓词，全部驱动 ratchet_gate 本体）：
  · `ratchet_gate._debt_artifact_fresh(art, volume_globs)` —— 相对新鲜谓词
  · `ratchet_gate.overdue_debt_items()` —— 经该谓词把守的活体指标（接线腿）

一手动因（r105）：`debt_aging_r104_2026-10-03.json` 的 mtime 16:29:35 比它所测的
`memory/07-next-steps.md`（16:33:21，r104 在同一轮里先量账后写裁决）旧 226 秒。棘轮按 3 天
日历龄预算收下这份件 ⇒ 把「已经还掉的债」报成「比基线新长的债」（实测 25 vs 活体尺 1），
连带 4 道读棘轮文本的门一起染红。日历龄答不了「件比被量对象新不新」，故补相对新鲜前置。

三向覆盖（W-47：新判据首跑必须同时交「应绿的绿」与「应红的红」，且对照组自身被证伪过）：
  p1 件新于卷 ⇒ 放行且指标取到件内值
  p2 等界（件 mtime == 卷 mtime）⇒ 必须放行（`>` 写成 `>=` 是判据自造红）
  n1 件旧于卷 ⇒ None + FACE_NOTES 具名原因（不得沿用件内值）
  n2 所测卷集为空 ⇒ None + 「无基准可比」（R247 空面不得判绿）
  n3 件不存在 ⇒ None
  m1 变异：摘掉前置（回到 r104 行为）⇒ 陈旧值 25 必须能漏进指标（证明拦它的是本前置，不是运气）
  m2 变异：把谓词写成「件永远新」⇒ n1 必须仍红（否则该腿是装饰）

退出码：0=全过 / 1=有失败 / 2=被测对象不可达。
"""
import importlib.util
import io
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = []


def ck(name, cond, got=""):
    RESULTS.append((bool(cond), name, str(got)))
    print("%s %-62s %s" % ("PASS" if cond else "FAIL", name, "" if cond else "  <-- " + str(got)[:190]))


def load_rg():
    spec = importlib.util.spec_from_file_location("rg105", str(HERE / "ratchet_gate.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def seed_case(tmp, art_overdue, art_is_fresh, gap_s=60):
    """造一份「账龄件 + 所测卷集」，返回 (bench_dir, volume_globs)。

    art_is_fresh=False ⇒ 件比卷旧 gap_s 秒；True ⇒ 件比卷新 gap_s 秒。
    """
    bench = os.path.join(tmp, "bench")
    os.makedirs(bench, exist_ok=True)
    vol = os.path.join(tmp, "07-next-steps.md")
    with io.open(vol, "w", encoding="utf-8", newline="") as f:
        f.write("- [ ] 假待办（r105 夹具卷，不落真实记忆）\n")
    art = os.path.join(bench, "debt_aging_r105_0000-00-00.json")
    doc = {"by_class": {"OVERDUE": art_overdue, "ACTIVE": 0, "DECIDED": 0,
                        "UNDATED": 0, "DEFERRED": 0, "REPEAT": 0},
           "evidence": {"open_total": art_overdue}}
    with io.open(art, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False)
    vol_t = os.path.getmtime(vol)
    art_t = vol_t + (gap_s if art_is_fresh else -gap_s)
    os.utime(art, (art_t, art_t))
    os.utime(vol, (vol_t, vol_t))
    return bench, [vol], art


def main():
    rg = load_rg()
    for need in ("_debt_artifact_fresh", "_newest_artifact", "overdue_debt_items",
                 "_debt_class_state", "FACE_NOTES"):
        if not hasattr(rg, need):
            print("被测对象缺成员 %s ⇒ 判红（R247 缺件不得当通过）" % need)
            print("[GATE:debt-face-fresh-fail]")
            return 2

    tmp = tempfile.mkdtemp(prefix="r105_dff_")

    # ---- p1 件新于卷：谓词放行 + 指标真取到件内值（接线腿，驱动 overdue_debt_items 本体） ----
    bench, globs, art = seed_case(os.path.join(tmp, "p1"), 12, True)
    ok, why = rg._debt_artifact_fresh(art, globs)
    ck("p1 正例：件比卷新 60s ⇒ 谓词放行", ok is True, why)
    _BENCH_OLD, _GLOBS_OLD = rg.BENCH, rg.DEBT_VOLUME_GLOBS
    try:
        rg.BENCH, rg.DEBT_VOLUME_GLOBS = Path(bench), globs
        rg.FACE_NOTES.clear()
        got = rg.overdue_debt_items()
        ck("p1b 接线：同一件经 overdue_debt_items() 解出件内值 12（不是硬编码、不是 None）",
           got == 12, "got=%r" % (got,))

        # ---- p2 等界：件 mtime == 卷 mtime ⇒ 必须放行 ----
        os.utime(art, (os.path.getmtime(globs[0]),) * 2)
        ok2, why2 = rg._debt_artifact_fresh(art, globs)
        ck("p2 边界：等界必须放行（写成 > 即判据自造红）", ok2 is True, why2)

        # ---- n1 件旧于卷：None + 具名原因 ----
        os.utime(art, (os.path.getmtime(globs[0]) - 226,) * 2)
        rg.FACE_NOTES.clear()
        gotn = rg.overdue_debt_items()
        # r209 修（消费方适配生产者，非放宽阈值）：原实现按**字面键**
        # "overdue_debt_items·相对新鲜" 取 note。并行会话给棘轮加更细的红因分类时把后缀
        # 改成「·取值面」（键名属实现细节），本腿当场失配报红 —— 但我这腿真正要守的契约是
        # 「指标转 None 时，FACE_NOTES 里必须有一条属于本指标的具名 False 理由，且理由里带
        # mtime 差值」。键名换了不该让守卫瞎掉；反过来，若生产者**完全不再具名**（一条都
        # 没有），本腿照样红。故改为按键前缀筛，语义判据一字未放。
        note = None
        for _k, _v in rg.FACE_NOTES.items():
            if _k.startswith("overdue_debt_items·") and _v and _v[0] is False:
                note = _v
                break
        ck("n1 反例：件比卷旧 226s ⇒ 指标转 None（不得沿用件内 12）", gotn is None, "got=%r" % (gotn,))
        ck("n1b 反例：转 None 时读取面必须具名（含两个 mtime 与差值；键名后缀不锁死）",
           note is not None and "差 226" in note[1], str(note)[:150])

        # ---- n2 卷集为空：无基准可比 ----
        okz, whyz = rg._debt_artifact_fresh(art, [os.path.join(tmp, "nobody*.md")])
        ck("n2 反例：所测卷集为空 ⇒ 不得判新鲜（R247 空面不判绿）",
           okz is False and "为空" in whyz, whyz)

        # ---- n3 件不存在 ----
        ck("n3 反例：账龄件不存在 ⇒ _newest_artifact 返回 None 而不是「无债」",
           rg._newest_artifact(os.path.join(tmp, "empty_dir_none", "debt_aging_r*.json")) is None,
           "n/a")

        # ---- m1 变异：摘掉相对新鲜前置（复现 r104 的原行为）⇒ 陈旧值必须漏进来 ----
        def _naive(key):
            d = rg._read_json(Path(bench) / "debt_aging_r*.json")
            if not isinstance(d, dict):
                return None
            by, ev = d.get("by_class") or {}, d.get("evidence") or {}
            return by.get("OVERDUE") if sum(by.values()) == ev.get("open_total") else None
        os.utime(art, (os.path.getmtime(globs[0]) - 226,) * 2)
        leaked = _naive("OVERDUE")
        ck("m1 变异：摘前置后陈旧值 12 确实漏进指标（证明拦它的是本前置；同时证明 r104 的 25 是这么来的）",
           leaked == 12, "naive=%r real=%r" % (leaked, rg.overdue_debt_items()))

        # ---- m2 变异：谓词写成「永远新」⇒ n1 必须仍能被真值抓到 ----
        def _always_fresh(p, g=None):
            return True, "变异体：无鉴别力"
        _orig = rg._debt_artifact_fresh
        rg._debt_artifact_fresh = _always_fresh
        try:
            rg.FACE_NOTES.clear()
            through = rg.overdue_debt_items()
        finally:
            rg._debt_artifact_fresh = _orig
        ck("m2 变异：把前置改成恒真 ⇒ 旧件值直接进指标（说明本腿测的是前置本身，不是件形状）",
           through == 12, "got=%r" % (through,))
    finally:
        rg.BENCH, rg.DEBT_VOLUME_GLOBS = _BENCH_OLD, _GLOBS_OLD

    fails = [r for r in RESULTS if not r[0]]
    print("\n桩合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    if fails:
        print("[GATE:debt-face-fresh-fail]")
        return 1
    print("[GATE:debt-face-fresh-pass]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
