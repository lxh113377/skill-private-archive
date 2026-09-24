# -*- coding: utf-8 -*-
r"""r21e_gate_probe.py — `upgrade_footer_gate.py` 证据可解析性的夹具（TDD：先看红，再实现，再复跑）。

用法：
    python 05-exec/r21e_gate_probe.py            # 跑全部层
    python 05-exec/r21e_gate_probe.py --red      # 只跑「期望被拦住但现状会放行」的两例（打补丁前必须先看到它们红）

判据分级（依据 = 同日边界测量 06-benchmark/evidence_resolvability_measure.json，近 3 日 97 条）：
  FAKE  = 路径不存在 / backup ID 在回滚目录与五仓 git 对象里都定位不到 ⇒ **阻断**（不可事后合理化，实测仅 4/97）
  STALE = 文件在、版本 token 已被后续提交推走 ⇒ **只告警**（声明当时可为真；追溯拦人 = 误伤 18/97，会把下一个人逼去放宽判据）
  SKIP  = 路径在本体系外 ⇒ 不判（防误伤第三方端点，如 .zcode）
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

GATE = r"D:\global_skills\A-memory-start\references\upgrade_footer_gate.py"
REAL = r"D:\global_skills\A-memory-start\SKILL.md"
R = []
BS = chr(92)

TPL = ("<!-- footer:begin session=t-evid ts=2026-09-24T23:30:00+08:00 -->" + chr(10)
       + "[skill清单] 本轮调用=1 个 (A-memory-start)" + chr(10)
       + "[升级建议] skill=A-memory-start | 五问=缺失步骤 | 改法=证据须可解析 | 对照=已取(证据=x)"
       + " | 状态=已闭环(证据={EV})" + chr(10)
       + "<!-- footer:end -->" + chr(10))


def ck(name, cond, detail=""):
    R.append(bool(cond))
    print("%s %-56s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def real_version():
    t = io.open(REAL, encoding="utf-8").read()
    m = re.search(r"(?m)^version:\s*([0-9][\w.\-]*)", t)
    return "V" + m.group(1)


def run_gate(ev):
    d = tempfile.mkdtemp(prefix="feg_")
    p = os.path.join(d, "blk.md")
    io.open(p, "w", encoding="utf-8").write(TPL.replace("{EV}", ev))
    r = subprocess.run([sys.executable, GATE, "--file", p, "--json"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "").strip().splitlines()
    js = None
    for l in out:
        if l.startswith("__JSON__"):
            js = json.loads(l[8:])
    return r.returncode, chr(10).join(out), js


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ver = real_version()
    cases = {
        "ok": REAL + "#版本行:" + ver,
        "fake_path": REAL.replace("SKILL.md", "nope_ZZ.md") + "#版本行:V9.9.9",  # 已知体系内不存在的文件
        "fake_backup": REAL + "#backup:zzz-not-a-real-handle",          # 形状合法但回滚件/git 对象都没有
        "stale_token": REAL + "#版本行:V99.99.99",            # 形状合法、文件在、token 不在 ⇒ STALE
        "skip_outside": "C:" + BS + "Users" + BS + "37533" + BS + ".zcode" + BS + "x.md#backup:abc",
    }
    print("真实锚点:", cases["ok"])
    only_red = "--red" in sys.argv
    names = ["fake_path", "fake_backup"] if only_red else list(cases)
    for nm in names:
        rc, line, js = run_gate(cases[nm])
        if nm == "ok":
            ck("① 可解析锚点必须放行", rc == 0, line)
        elif nm == "stale_token":
            ck("② 陈旧 token：不阻断但必须告警", rc == 0 and "陈旧" in line, line[:120])
        elif nm == "skip_outside":
            ck("③ 体系外路径：不判（防第三方端点误伤）", rc == 0, line)
        else:
            ck("④ %s：形状合法但必须被阻断" % nm, rc == 1 and "解析不到" in line,
             "rc=%s %s" % (rc, line[:110]))
    if only_red:
        print("-" * 66)
        print("[RED] 只看两例 FAKE：现在通过 = 判据缺位（补丁前应为 FAIL）")
    print("-" * 66)
    bad = R.count(False)
    print("%s 证据可解析性夹具 %d/%d" % ("[GATE:fixture-pass]" if not bad else "[GATE:fixture-fail]",
                                        R.count(True), len(R)))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
