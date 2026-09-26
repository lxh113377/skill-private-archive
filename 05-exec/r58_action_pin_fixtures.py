# -*- coding: utf-8 -*-
"""r58 动作固定守卫的隔离桩（层 a 逻辑边界 + 层 b 真机变异体，R238 两层含对照）。

层 a 九例：正例 2 / 反例 7（P1 形态三形、P2 配对两形、P3 空面两形）。
层 b 变异体：拿**真实** `.github/workflows/` 副本，把已 pin 的 SHA 换回 `@v4`，
  守卫必须当场红 —— 只跑合成样本会漏掉「正则根本没匹配到真实写法」这类接线错误
  （r21 的 `%` 格式化 bug、r55 的两输入面反向，都是这么暴露的）。
退出码：0 全过 / 1 有失败 / 2 环境不满足（守卫脚本缺失）
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GUARD = os.path.join(HERE, "r58_action_pin_guard.py")
PIN = "11d5960a326750d5838078e36cf38b85af677262"

WF_TMPL = """name: demo
on: [push]
jobs:
  j:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@%s
%s
"""
DEP_OK = "version: 2\nupdates:\n  - package-ecosystem: \"github-actions\"\n    directory: \"/\"\n"
DEP_NO_ECO = "version: 2\nupdates:\n  - package-ecosystem: \"pip\"\n    directory: \"/\"\n"


def case(tmp, ref, extra="      - uses: actions/setup-python@" + PIN, dep=DEP_OK, write_wf=True):
    d = os.path.join(tmp, ".github", "workflows")
    os.makedirs(d, exist_ok=True)
    if write_wf:
        io.open(os.path.join(d, "g.yml"), "w", encoding="utf-8", newline="\n").write(
            WF_TMPL % (ref, extra))
    if dep is not None:
        io.open(os.path.join(tmp, ".github", "dependabot.yml"), "w",
                encoding="utf-8", newline="\n").write(dep)
    return d, os.path.join(tmp, ".github", "dependabot.yml")


def run(wf, dep):
    argv = [sys.executable, GUARD, "--workflows", wf, "--dependabot", dep]
    p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (p.stdout or "") + (p.stderr or "")
    token = "[GATE:actionpin-pass]" if p.returncode == 0 else ("[GATE:actionpin-fail]" if p.returncode == 1 else None)
    return p.returncode, out, token


def main():
    if not os.path.isfile(GUARD):
        print("守卫脚本不存在：%s" % GUARD)
        return 2
    results = []

    def check(name, tmp, wf, dep, want_rc, want_token):
        rc, out, got = run(wf, dep)
        ok = (rc == want_rc) and (want_token in out)
        results.append((name, ok, rc, want_rc, want_token if ok else ("缺 %s" % want_token)))
        print("  %-4s %-34s rc=%s(期望 %s) %s" % ("✅" if ok else "❌", name, rc, want_rc,
                                                 "" if ok else "← " + out.strip().splitlines()[-1][:78]))

    base = tempfile.mkdtemp(prefix="r58_pin_fixture_")
    try:
        # ---- 层 a：合成边界 ----
        wf, dep = case(os.path.join(base, "p1"), PIN)
        check("p1 全 pin + 有 dependabot", os.path.join(base, "p1"), wf, dep, 0, "[GATE:actionpin-pass]")
        wf, dep = case(os.path.join(base, "p2"), PIN, extra="      - uses: ./local-helper")
        check("p2 含仓内本地 action 不算浮动", os.path.join(base, "p2"), wf, dep, 0, "[GATE:actionpin-pass]")
        wf, dep = case(os.path.join(base, "n1"), "v4")
        check("n1 版本 tag 浮动", os.path.join(base, "n1"), wf, dep, 1, "[GATE:actionpin-fail]")
        wf, dep = case(os.path.join(base, "n2"), "main")
        check("n2 分支引用浮动", os.path.join(base, "n2"), wf, dep, 1, "[GATE:actionpin-fail]")
        wf, dep = case(os.path.join(base, "n3"), PIN[:39])
        check("n3 SHA 截断 39 位", os.path.join(base, "n3"), wf, dep, 1, "[GATE:actionpin-fail]")
        wf, dep = case(os.path.join(base, "n4"), PIN, dep=None)
        check("n4 无 dependabot（P2 配对）", os.path.join(base, "n4"), wf, dep, 1, "[GATE:actionpin-fail]")
        wf, dep = case(os.path.join(base, "n5"), PIN, dep=DEP_NO_ECO)
        check("n5 dependabot 缺 github-actions", os.path.join(base, "n5"), wf, dep, 1, "[GATE:actionpin-fail]")
        wf, dep = case(os.path.join(base, "n6"), PIN, write_wf=False)
        check("n6 空 workflow 目录（P3）", os.path.join(base, "n6"), wf, dep, 1, "[GATE:actionpin-fail]")
        check("n7 workflow 目录不存在", os.path.join(base, "nope"), os.path.join(base, "nope"), dep, 1,
              "[GATE:actionpin-fail]")

        # ---- 层 b：真机变异体（对照组 = 原样副本必须绿）----
        real_src = os.path.join(REPO, ".github")
        live = os.path.join(base, "live")
        shutil.copytree(real_src, os.path.join(live, ".github"))
        wf = os.path.join(live, ".github", "workflows")
        dep = os.path.join(live, ".github", "dependabot.yml")
        rc, out, _ = run(wf, dep)
        ok = rc == 0 and "[GATE:actionpin-pass]" in out
        results.append(("b1 真仓原样（对照组）", ok, rc, 0, ""))
        print("  %-4s %-34s rc=%s(期望 0)" % ("✅" if ok else "❌", "b1 真仓原样（对照组）", rc))

        mut = os.path.join(base, "mut")
        shutil.copytree(real_src, os.path.join(mut, ".github"))
        gp = os.path.join(mut, ".github", "workflows", "gates.yml")
        text = io.open(gp, encoding="utf-8").read()
        n = text.count("@" + PIN)
        mutated = text.replace("@" + PIN, "@v4")
        io.open(gp, "w", encoding="utf-8", newline="\n").write(mutated)
        rc2, out2, _ = run(os.path.join(mut, ".github", "workflows"),
                           os.path.join(mut, ".github", "dependabot.yml"))
        ok2 = rc2 == 1 and "[GATE:actionpin-fail]" in out2 and n >= 1
        results.append(("b2 真仓变异体(SHA→@v4)", ok2, rc2, 1, ""))
        print("  %-4s %-34s 命中替换 %d 处 rc=%s(期望 1)" % ("✅" if ok2 else "❌",
                                                       "b2 真仓变异体(SHA→@v4)", n, rc2))
        if n == 0:
            print("     ⚠️ 变异未命中任何 pin ⇒ 该对照是**空断言**，不得记通过（R247）")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    passed = sum(1 for r in results if r[1])
    print("-" * 62)
    print("action_pin_guard 桩: %d/%d %s" % (passed, len(results),
                                             "PASS" if passed == len(results) else "FAIL"))
    print("[GATE:stub-%s]" % ("pass" if passed == len(results) else "fail"))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
