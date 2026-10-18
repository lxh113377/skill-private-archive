# -*- coding: utf-8 -*-
r'''r113_cache_guard_face_fixtures.py -- 第 33 门（cache_guard_face）自身的双向夹具（W-47）。

职责：证明这道门「应绿的绿 + 应红的红」两侧都成立，且两条豁免规则真有鉴别力。
  门自身首跑两次失真（按 basename 判定致夹具文件名误判 / 写标记零捕获信息），
  与 X-18「判据写完就宣布有效」、R238「单测掩盖接线错误」同族 => 本夹具把这两型钉住。

腿：
  f1 应红的红：取数 + 裸写可复用证据缓存（无守卫 token）=> classify 必须点名 1 件
  f2 应绿的绿：同上加守卫 token => 0 违规且计入在面 1 件
  f3 豁免成立：写目标是每轮新产物（args.json_out / 日期）=> 不判违规也不计在面
  f4 豁免成立：写目标在临时目录（tmp_*）=> 不判违规
  f5 真机接线：用真实 CLI 形态对 05-exec 跑门本体 => rc=0 且印 token（不只测函数）
  f6 零输入面：空目录 => rc=2 且不印 token（R247）
  m1 变异（摘守卫识别）：GUARD_TOKENS 置空 => f2 必须转红（f2 的绿确由守卫判定产生）
  m2 变异（摘豁免识别）：EVIDENCE_RE 改恒真 => f3 与 f4 必须转红（豁免腿非空断言）
用法：python 05-exec/r113_cache_guard_face_fixtures.py
退出：0 = [GATE:fixture-pass]；1 = [GATE:fixture-fail]
'''
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r113_cache_guard_face as M  # noqa: E402

NL = chr(10)
Q = chr(34)


def _synthetic(target_expr, guard=False):
    """造一个「远端取数 + 写盘」的假脚本源码（源码内引号用 Q 现拼，免转义）。"""
    lines = [
        "import io, json, subprocess",
        "rc = subprocess.run([" + Q + "gh" + Q + ", " + Q + "api" + Q + ", " + Q + "rate_limit" + Q + "])",
        "raw = json.loads(rc.stdout)",
        "io.open(" + target_expr + ", " + Q + "w" + Q + ", encoding=" + Q + "utf-8" + Q + ")"
        ".write(json.dumps(raw))",
    ]
    if guard:
        lines.append("cache_error = None")
    return NL.join(lines) + NL


def _dir_with(body, name="sample.py"):
    tmp = tempfile.mkdtemp(prefix="cgf_")
    io.open(os.path.join(tmp, name), "w", encoding="utf-8", newline=NL).write(body)
    return tmp


def _paths(d):
    return [os.path.join(d, x) for x in sorted(os.listdir(d))]


def f1():
    # 写目标用 args.cache —— 门认得的「持久路径标记」之一（r96_twelve_face 真实形态），
    # 而不是裸词 cache_p：后者会被正向鉴别放行，那测的就不是本腿要测的东西。
    d = _dir_with(_synthetic("args.cache"))
    try:
        viol, ok_n, fetch_n, scanned = M.classify(_paths(d))
        return (len(viol) == 1 and viol[0][0] == "sample.py"), \
            "裸写点名=%d 在面=%d 取数面=%d" % (len(viol), ok_n, fetch_n)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def f2():
    d = _dir_with(_synthetic("args.cache", guard=True))
    try:
        viol, ok_n, fetch_n, scanned = M.classify(_paths(d))
        return (len(viol) == 0 and ok_n == 1), "带守卫=违规%d 在面%d" % (len(viol), ok_n)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def f3():
    # r113 一手（m2 首版无效的原因）：豁免腿必须让「持久标记」与「每轮标记」**同一行共存**，
    # 否则摘掉 PERROUND 也不会改变结果（= 改了不影响断言的变异体，等于没测）。
    # cache_path_r113_2026：cache_p 命中 EVIDENCE（持久），r113 命中 PERROUND（轮号产物）。
    d = _dir_with(_synthetic("cache_path_r113_2026"))
    try:
        viol, ok_n, fetch_n, scanned = M.classify(_paths(d))
        return (len(viol) == 0 and ok_n == 0), "每轮新产物豁免=违规%d 在面%d" % (len(viol), ok_n)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def f4():
    d = _dir_with(_synthetic("tmp_cache_path"))
    try:
        viol, ok_n, fetch_n, scanned = M.classify(_paths(d))
        return (len(viol) == 0), "临时目录豁免=违规%d" % len(viol)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def f5():
    p = subprocess.run([sys.executable, os.path.join(HERE, "r113_cache_guard_face.py"),
                        "--exec-dir", HERE],
                       capture_output=True, text=True, timeout=180,
                       encoding="utf-8", errors="replace")
    out = (p.stdout or "") + (p.stderr or "")
    return (p.returncode == 0 and M.TOKEN in out), \
        "真机 rc=%s token可见=%s" % (p.returncode, M.TOKEN in out)


def f6():
    d = tempfile.mkdtemp(prefix="cgf_empty_")
    try:
        p = subprocess.run([sys.executable, os.path.join(HERE, "r113_cache_guard_face.py"),
                            "--exec-dir", d],
                           capture_output=True, text=True, timeout=120,
                           encoding="utf-8", errors="replace")
        out = (p.stdout or "") + (p.stderr or "")
        return (p.returncode == 2 and M.TOKEN not in out), \
            "零输入 rc=%s（须 2 且不印 token）" % p.returncode
    finally:
        shutil.rmtree(d, ignore_errors=True)


def m1():
    orig = M.GUARD_TOKENS
    try:
        M.GUARD_TOKENS = ()
        caught = not f2()[0]
        return caught, "摘守卫识别后 f2 转红=%s（须 True）" % caught
    finally:
        M.GUARD_TOKENS = orig


def m2():
    """变异：摘掉两条**豁免**识别（TMP/PERROUND 恒不匹配）=> f3、f4 必须转红。

    r113 一手：首版这腿改的是 EVIDENCE_RE 恒真，但 evidence_write_lines 的判定顺序是
    先 TMP/PERROUND 跳过、后才看 EVIDENCE，于是摘 EVIDENCE 根本不触及豁免路径 ——
    那是「改了不影响结果的变异体」，等于没测（R238 同族）。
    """
    orig_pr, orig_tmp = M.PERROUND_RE, M.TMP_RE
    NEVER = re.compile(chr(36) + chr(39))  # 永不匹配的模式（$ 后无内容）
    try:
        M.PERROUND_RE = NEVER
        M.TMP_RE = NEVER
        bad3 = not f3()[0]
        bad4 = not f4()[0]
        return (bad3 and bad4), "摘豁免识别后 f3转红=%s f4转红=%s（须均 True）" % (bad3, bad4)
    finally:
        M.PERROUND_RE, M.TMP_RE = orig_pr, orig_tmp


LEGS = [("f1", f1), ("f2", f2), ("f3", f3), ("f4", f4), ("f5", f5), ("f6", f6),
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
        print("[GATE:fixture-pass] 第 33 门双向自证（6 腿 + 2 变异体均被抓住）")
        return 0
    print("[GATE:fixture-fail]")
    return 1


if __name__ == "__main__":
    sys.exit(main())
