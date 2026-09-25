# -*- coding: utf-8 -*-
"""r55 输入面自证夹具：R286 登记「不放宽判据」的双向实测。

存在理由（r55）：R286 把本工作区根登记进 `noise_lint.KNOWN_CORE`，复验顶层 VIOL 8→0。
「变绿」本身不构成交付证据 —— 必须同时证明**登记之后真散落仍然会被抓**，
否则这条登记就是拿判据换账面（X-9 的反面形态：放宽 allowlist 凑绿）。
本夹具双向取证件：
  正例 = 已登记根的顶层治理目录不再被 strict 全判 VIOL；
  反例 = 在该根内当场植入一个临时散落目录，noise 必须报它 VIOL（没报 ⇒ 本夹具红）；
  守恒 = 清理后违规计数必须回到植入前，防止我自己制造新散落。
按 X-28：一律走真实派发入口（`handoff.py noise <项目根>` 子进程），不偷调内部函数。
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HANDOFF = r"D:/global_skills/A-project-handoff/scripts/handoff.py"
NL = r"D:/global_skills/A-project-handoff/scripts/noise_lint.py"
PROBE = os.path.join(ROOT, "05-exec", "_r55probe_tmp")
GOVERNED = ["00-scope", "01-scan", "02-review", "03-audit", "04-plan",
            "05-exec", "06-benchmark", "archive", "memory"]

RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%-4s %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  ← " + str(detail)[:150]) if detail and not cond else ""))


def _run_noise_on(target):
    env = dict(os.environ, PYTHONPYCACHEPREFIX=r"C:/tmp/pyc_r55")
    p = subprocess.run([sys.executable, HANDOFF, "noise", target],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, cwd=ROOT)
    out = (p.stdout or "") + (p.stderr or "")
    m = re.search(r"汇总：\s*(\{.*\})", out)
    summary = json.loads(m.group(1)) if m else None
    items = []
    for l in out.splitlines():
        parts = l.split(None, 3)
        if parts and parts[0] == "VIOL" and len(parts) > 2 and parts[1] in ("dir", "file"):
            items.append((parts[1], parts[2].strip(), parts[3].strip() if len(parts) > 3 else ""))
    return p.returncode, out, summary, items


def run_noise():
    return _run_noise_on(ROOT)


def main():
    if not os.path.exists(HANDOFF):
        ck("前置：handoff.py 存在", False, HANDOFF)
        return finish()

    rc0, out0, sum0, viol0 = run_noise()
    base = (sum0 or {}).get("自建skill优化") or {}
    top0 = [n for k, n, r in viol0 if "/" not in n]
    ck("f1 真实派发形态：`handoff.py noise <项目根>` 子进程可解析出汇总 JSON（零输入不得记 PASS）",
       bool(sum0) and base.get("ok", 0) > 0, "rc=%s 汇总=%s" % (rc0, sum0))
    ck("f2 正例（R286 登记生效）：顶层治理目录无一被判 strict VIOL（按名精确比对，不算子串）",
       not [g for g in GOVERNED if g in top0], "顶层 VIOL=%s" % top0)
    ck("f3 覆盖面自证：ok 计数须 ≥ 受检顶层目录数（登记面没有截断）",
       base.get("ok", 0) >= len(GOVERNED), "ok=%d 面=%d" % (base.get("ok", 0), len(GOVERNED)))

    try:
        os.makedirs(PROBE)
        with io.open(os.path.join(PROBE, "seed.txt"), "w", encoding="utf-8") as f:
            f.write("r55 negative control\n")
        rc1, out1, sum1, viol1 = run_noise()
        after = (sum1 or {}).get("自建skill优化") or {}
        ck("f4 反例（牙齿）：登记之后植入的散落产物仍必须判 VIOL（判据没被顺手放宽）",
           any(n.endswith("_r55probe_tmp") for k, n, r in viol1), "植入后 VIOL=%s" % viol1)
        ck("f5 守恒：植入使 violation 严格 +1",
           after.get("violation", -1) == base.get("violation", -1) + 1,
           "before=%s after=%s rc=%s" % (base.get("violation"), after.get("violation"), rc1))
    finally:
        shutil.rmtree(PROBE, ignore_errors=True)

    ck("f6 清理自证：探针目录已不存在（禁我自己留下新散落）",
       not os.path.exists(PROBE), PROBE)
    rc2, out2, sum2, viol2 = run_noise()
    back = (sum2 or {}).get("自建skill优化") or {}
    ck("f7 计数复位：清理后违规计数回到植入前（无残留、无漂移）",
       back.get("violation") == base.get("violation")
       and not any("probe" in n for k, n, r in viol2),
       "before=%s after=%s VIOL=%s" % (base.get("violation"), back.get("violation"), viol2))
    ck("f8 残留项可逐条解释：当前 VIOL 只容 R269 登记项与 W-39 待裁定项",
       all(("手动维护" in n) or ("mark_backup" in n) for k, n, r in viol2), "VIOL=%s" % viol2)

    # f10/f11 = R287（查表键绝对化）双向锁：相对路径不得换面，未登记根仍须 strict。
    env = dict(os.environ, PYTHONPYCACHEPREFIX=r"C:/tmp/pyc_r55")
    p_rel = subprocess.run([sys.executable, NL, "."], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env, cwd=ROOT)
    m = re.search(r"汇总：\s*(\{.*\})", p_rel.stdout or "")
    same = bool(m) and json.loads(m.group(1)).get(".") == (sum0 or {}).get("自建skill优化")
    ck("f10 R287 正例：`noise .`（相对根）与绝对路径必须给出**同一个面**（修前 13 vs 2）",
       same, "dot=%s abs=%s" % (m.group(1) if m else None, sum0))

    tmp2 = os.path.join(r"C:/tmp", "r55_unreg_rel_root")
    try:
        shutil.rmtree(tmp2, ignore_errors=True)
        os.makedirs(os.path.join(tmp2, "memory"))
        os.makedirs(os.path.join(tmp2, "docs"))
        p_rel2 = subprocess.run([sys.executable, NL, "r55_unreg_rel_root"], capture_output=True,
                                text=True, encoding="utf-8", errors="replace",
                                env=env, cwd=r"C:/tmp")
        mm = re.search(r"汇总：\s*(\{.*\})", p_rel2.stdout or "")
        s2 = json.loads(mm.group(1)) if mm else {}
        got = list(s2.values())[0] if s2 else {}
        ck("f11 R287 反例（禁顺手放宽）：未登记的相对根仍须落 strict 判红",
           got.get("violation", 0) >= 2 and p_rel2.returncode != 0,
           "out=%s rc=%s" % (s2, p_rel2.returncode))
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    # f9 = f2 的反向对照：f2 判绿必须是"看得见违规的能力还在"，不是"这条断言根本抓不到东西"。
    # 造一个**未登记**的临时根（同名治理目录），同一条谓词必须判红。
    tmp = os.path.join(r"C:/tmp", "r55_unregistered_root")
    try:
        shutil.rmtree(tmp, ignore_errors=True)
        for g in GOVERNED:
            os.makedirs(os.path.join(tmp, g))
        rc9, out9, sum9, viol9 = _run_noise_on(tmp)
        top9 = [n for k, n, r in viol9 if "/" not in n]
        ck("f9 对照（防 f2 空断言）：未登记同形根上，同一谓词必须抓到顶层 strict VIOL",
           len([g for g in GOVERNED if g in top9]) >= 8,
           "顶层 VIOL=%s rc=%s" % (top9, rc9))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return finish()


def finish():
    fails = [r for r in RESULTS if not r[0]]
    print("\n夹具合计: %d 项，通过 %d，失败 %d"
          % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    print("[GATE:fixture-fail]" if fails else "[GATE:fixture-pass]")
    return 1 if fails else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
