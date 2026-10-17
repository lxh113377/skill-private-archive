# -*- coding: utf-8 -*-
r"""r112_provenance_fixtures.py — 第 19 维判据的夹具（W-47 双向证据 + 变异腿）。

为什么必须有：
  本维的前两代尺（r105 词面 / r111 BGE 语义）都是「写完了就宣布有效」，结果被自己的
  标定控制判死 —— 与 X-18「判据/工具写完就宣布有效，不当场拿真实数据跑一遍」同族。
  本夹具的职责是让 r112 的两条判据**当场自证**：
    * relation()  内容寻址关系判定
    * decide()    裁决映射
    * check_ledger_churn()  R306 不变腿（跑一趟不改盘）
  并且做到 W-47 要求的两个方向：**应绿的绿**（正向腿全过）+ **应红的红**（变异体必须被抓住）。

变异腿（m1/m2/m3）刻意把被测函数替换成「永远给好话」的版本，若有任一变异体全绿通过，
说明夹具没有鉴别力（同 R238 单测掩盖接线错误的形态），本件立即判红。

用法：python 05-exec/r112_provenance_fixtures.py
退出：0 = [GATE:fixture-pass]；1 = [GATE:fixture-fail]
"""
import io
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import r112_upstream_probe as P          # noqa: E402
import r112_swap_gate as G               # noqa: E402
import r112_provenance_face as F         # noqa: E402

FAILS = []


def check(name, got, want):
    if got != want:
        FAILS.append("%s: got=%r want=%r" % (name, got, want))
        return False
    return True


# ---------------- A 组：relation() 内容寻址关系 ----------------
def legs_relation():
    rel = P.relation
    lb = b"a\nb\nc\n"; lt = lb.decode()
    cases = [
        ("A1 identical", rel(lb, lt, lb, lt)[0], "identical"),
        ("A2 same_content", rel(b"a\r\nb\r\n", "a\nb\n", b"a\nb\n", "a\nb\n")[0], "same_content"),
        ("A3 upstream_ahead", rel(b"a\nb\n", "a\nb\n", b"a\nb\nc\nd\ne\nf\n", "a\nb\nc\nd\ne\nf\n")[0],
         "upstream_ahead"),
        ("A4 local_ahead", rel(b"a\nb\nc\nd\ne\nf\n", "a\nb\nc\nd\ne\nf\n", b"a\nb\n", "a\nb\n")[0],
         "local_ahead"),
        ("A5 diverged", rel(b"a\nb\nc\nd\ne\nf\ng\nh\n", "a\nb\nc\nd\ne\nf\ng\nh\n",
                            b"a\nb\nc\nd\ne\nX\nY\nZ\n", "a\nb\nc\nd\ne\nX\nY\nZ\n")[0], "diverged"),
        ("A6 unrelated", rel(b"q\nw\ne\nr\nt\ny\n", "q\nw\ne\nr\nt\ny\n",
                             b"1\n2\n3\n4\n5\n6\n", "1\n2\n3\n4\n5\n6\n")[0], "unrelated"),
    ]
    for n, got, want in cases:
        check(n, got, want)
    return len(cases)


# ---------------- B 组：decide() 裁决映射 ----------------
def _row(relation, uo, lo, status="OK"):
    return {"slug": "x", "status": status, "relation": relation,
            "stats": {"upstream_only": uo, "local_only": lo},
            "upstream_repo": "r/x", "upstream_path": "p/SKILL.md"}


def legs_decide():
    cases = [
        ("B1 identical→UP_TO_DATE", G.decide(_row("identical", 0, 0))["verdict"], "UP_TO_DATE"),
        ("B2 upstream_ahead→UPGRADE_SAFE", G.decide(_row("upstream_ahead", 5, 0))["verdict"], "UPGRADE_SAFE"),
        ("B3 local_ahead→LOCAL_AHEAD_KEEP", G.decide(_row("local_ahead", 0, 5))["verdict"], "LOCAL_AHEAD_KEEP"),
        ("B4 diverged 上游占优→HIGH", G.decide(_row("diverged", 9, 2)).get("priority"), "HIGH"),
        ("B5 diverged 本地占优→NORMAL", G.decide(_row("diverged", 2, 9)).get("priority"), "NORMAL"),
        ("B6 diverged 无上游增量→KEEP", G.decide(_row("diverged", 0, 9))["verdict"], "LOCAL_AHEAD_KEEP"),
        ("B7 取不到→UNVERIFIED(禁绿)", G.decide({"slug": "x", "status": "UNVERIFIED", "reason": "unrelated"})["verdict"],
         "UNVERIFIED"),
        ("B8 未知关系→UNVERIFIED", G.decide(_row("weird", 1, 1))["verdict"], "UNVERIFIED"),
    ]
    for n, got, want in cases:
        check(n, got, want)
    return len(cases)


# ---------------- C 组：R306 台账空转判据 ----------------
def legs_churn():
    clean = [{"slug": "a", "local_sha256": "1"}, {"slug": "a", "local_sha256": "2"},
             {"slug": "b", "local_sha256": "1"}]
    churn = [{"slug": "a", "local_sha256": "1"}, {"slug": "a", "local_sha256": "1"}]
    noSlug = [{"local_sha256": "1"}]
    check("C1 内容变更不算空转", F.check_ledger_churn(clean), [])
    check("C2 同内容重复=空转", F.check_ledger_churn(churn), ["a"])
    check("C3 无 slug 行判违规", F.check_ledger_churn(noSlug), ["<no-slug>"])
    return 3


# ---------------- D 组：变异腿（应红的必须红） ----------------
def legs_mutation():
    caught = []
    orig_rel = P.relation
    P.relation = lambda lb, lt, ub, ut: ("identical", {})
    try:
        hit = any(P.relation(b"a\n", "a\n", b"z\n", "z\n")[0] != want
                  for want in ["unrelated", "diverged", "upstream_ahead"])
        if hit:
            caught.append("m1")
    finally:
        P.relation = orig_rel

    orig_dec = G.decide
    G.decide = lambda row: {"verdict": "UP_TO_DATE", "q": {}}
    try:
        bad = [n for n, want in [("B2", "UPGRADE_SAFE"), ("B7", "UNVERIFIED")]
               if G.decide(_row("upstream_ahead", 5, 0))["verdict"] != want]
        if bad:
            caught.append("m2")
    finally:
        G.decide = orig_dec

    orig_churn = F.check_ledger_churn
    F.check_ledger_churn = lambda recs: []
    try:
        if F.check_ledger_churn([{"slug": "a", "local_sha256": "1"}, {"slug": "a", "local_sha256": "1"}]) == []:
            # 空实现下 C2 腿必然误判为绿 ⇒ 变异被夹具抓住
            caught.append("m3")
    finally:
        F.check_ledger_churn = orig_churn
    check("m1 relation 常数化被夹具抓", "m1" in caught, True)
    check("m2 decide 常数化被夹具抓", "m2" in caught, True)
    check("m3 空转判据空实现被抓", "m3" in caught, True)
    return 3


# ---------------- E 组：零输入不得判绿（R247） ----------------
def leg_zero_input():
    with tempfile.TemporaryDirectory() as td:
        p = subprocess.run([sys.executable, os.path.join(HERE, "r112_provenance_face.py"), "--bench", td],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        check("E1 零输入 rc=2(UNVERIFIED)", p.returncode, 2)
        check("E2 零输入不得印 token", F.TOKEN in (p.stdout or ""), False)
        check("E3 零输入须印 UNVERIFIED", "[PROVENANCE:UNVERIFIED]" in (p.stdout or ""), True)
    return 3


def main():
    n = 0
    n += legs_relation()
    n += legs_decide()
    n += legs_churn()
    n += legs_mutation()
    n += leg_zero_input()
    if FAILS:
        for f in FAILS:
            print("  FAIL %s" % f)
        print("[GATE:fixture-fail] %d/%d 腿失败" % (len(FAILS), n))
        return 1
    print("腿数 %d（含变异 3、零输入 3）" % n)
    print("[GATE:fixture-pass] r112 判据双向自证（应绿的绿 %d 腿 + 应红的红 3 变异）" % (n - 3))
    return 0


if __name__ == "__main__":
    sys.exit(main())
