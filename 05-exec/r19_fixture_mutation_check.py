# -*- coding: utf-8 -*-
"""r19_fixture_mutation_check.py — 变异测试：证明 `r19_scan_fixtures.py` 判据**有牙**（对照实验）。

为什么需要它：footer 协议要求每条升级建议在提出阶段就取「对照」（A-get-memory Step 2.3.1 第 7 条，
2026-09-19 实证：一条未取对照的建议落盘会把错误归因写进全局规则）。r19 给出的建议是
「交付判据类工具前强制跑夹具门禁」，但若夹具本身**放松成永真**，这条落点等于零。
本脚本用变异测试给出两侧证据：
  正例（对照组）= 原样复制 → 夹具必须 PASS；
  违规样本（变异组）= 把判据逐条改坏 → 夹具必须 FAIL 且 exit 1。
任一变异未被抓到 ⇒ 该判据不可信，本脚本 exit 1。

用法：python 05-exec/r19_fixture_mutation_check.py
退出码：0 = 全部变异被拦住 / 1 = 有变异漏网 / 2 = 环境不满足
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = "r19_scan_fixtures.py"

MUTATIONS = [
    ("BY_DESIGN 永不生效（按设计累积项不再被排除）",
     "cumulative_drift_scan.py",
     "    if BY_DESIGN.search(path):",
     "    if BY_DESIGN.search(path) and False:"),
    ("is_ruleish 放开 .md 限制（代码文件重新混入规则类）",
     "cumulative_drift_scan.py",
     'return path.lower().endswith(".md") and bool(RULEISH.search(path))',
     "return bool(RULEISH.search(path))"),
    ("PROCESS_RE 永不命中（description 流程入描述判据失效）",
     "description_baseline_scan.py",
     '    r"\\s→\\s.*\\s→\\s|步骤[:：]|流程[:：]|先.+(再|然后).+(最后|再)|pipeline|Phase\\s*\\d)",',
     '    r"(?!x)x_never)",'),
    ("denominator 恒判一致（分母漂移不再报警）",
     "_lib.py",
     'd["consistent"] = (glob_total == reg["count"])',
     'd["consistent"] = True'),
]


def run_suite(root):
    p = subprocess.run([sys.executable, str(root / FIXTURE)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=900)
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, ("[GATE:fixture-pass]" in out, "[GATE:fixture-fail]" in out,
                          out.strip().splitlines()[-1] if out.strip() else "")


def clone(dst):
    for f in HERE.glob("*.py"):
        shutil.copy2(f, dst / f.name)
    shutil.copytree(HERE / "schemas", dst / "schemas", dirs_exist_ok=True)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if not (HERE / FIXTURE).exists() or not (HERE / "cumulative_drift_scan.py").exists():
        print("SKIP: 夹具或被变异工具不在位")
        return 2

    base = Path(tempfile.mkdtemp(prefix="r19_mut_ctrl_"))
    clone(base)
    rc, (passed, failed, last) = run_suite(base)
    print("对照组（未变异）: rc=%s pass=%s | %s" % (rc, passed, last))
    if not passed or rc != 0:
        print("[GATE:MUTATION-INCONCLUSIVE] 对照组未通过，环境本身有问题，变异结论无效")
        return 2

    missed = []
    for title, target, old, new in MUTATIONS:
        d = Path(tempfile.mkdtemp(prefix="r19_mut_"))
        clone(d)
        fp = d / target
        text = fp.read_text(encoding="utf-8")
        if old not in text:
            print("FAIL %-52s 变异锚点未命中（测试失效，不得算通过）" % title)
            missed.append(title)
            continue
        fp.write_text(text.replace(old, new, 1), encoding="utf-8")
        rc2, (ok2, bad2, last2) = run_suite(d)
        caught = bad2 and rc2 == 1
        print("%s %-52s rc=%s %s" % ("PASS" if caught else "FAIL", title, rc2,
                                     "" if caught else "变异后夹具仍判通过 ⇒ 该判据不可信: " + last2))
        if not caught:
            missed.append(title)

    print("\n变异组共 %d 项，被拦住 %d 项" % (len(MUTATIONS), len(MUTATIONS) - len(missed)))
    print("[GATE:MUTATION-PASS] 夹具对四条关键判据均有拦截力（对照=已取）" if not missed
          else "[GATE:MUTATION-FAIL] 漏网: %s" % missed)
    return 0 if not missed else 1


if __name__ == "__main__":
    raise SystemExit(main())
