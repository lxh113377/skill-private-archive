# -*- coding: utf-8 -*-
r"""r40_scan_inputs_fixtures.py — 冲突扫描器**输入面自证**夹具（TDD：先看红）。

发现（r40，L-4 反转）：`05-exec/rule_conflict_scan.py` 的 `DEFAULT_FILES` 里
`D:\global_memory\AGENTS.md` 实测不存在（该根无此文件），而扫描器对缺失输入的处理是
**静默跳过** ⇒ 受检文件数从 10 悄悄降到 9 却照常打印 PASS。这正是 R247 的形态：
「取不到的面」被当成「干净的面」。

更重的一层：这条债在 07 里被登记为「归属方件 L-4」挂账 4 轮 —— 但该文件**就在本仓 05-exec/**，
属本仓自持。⇒ 债务治理需要一个新判据：**待办里声称的归属必须可机检**（W-7）。

被测对象：`05-exec/rule_conflict_scan.py::check_inputs(files)`
期望：返回 (present, missing)；missing 非空时主流程必须**报出来并计入结果 JSON**，
      不得静默少扫；全缺时不得判 PASS。
"""

import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-54s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load_mod(name, fname):
    spec = importlib.util.spec_from_file_location(name, str(HERE / fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    rcs = load_mod("rcs40", "rule_conflict_scan.py")
    bcs = load_mod("bcs40", "baseline_contract_scan.py")
    contracts = bcs.load_contracts()
    art = contracts["artifacts"].get("rule_conflict_scan_*.json")
    ck("t0 契约里有 rule_conflict_scan 条目", bool(art), str(list(contracts.get("artifacts", {})))[:120])
    present = [str(f) for f in rcs.DEFAULT_FILES if os.path.isfile(str(f))]
    dead = [str(f) for f in rcs.DEFAULT_FILES if not os.path.isfile(str(f))]
    ck("t1 DEFAULT_FILES 零死条目（L-4 原案，实测而非推断）", not dead, "缺失 %s" % dead)
    ck("t2 受检面数量 = 声明数量（覆盖面不得靠删条目做干净）",
       len(present) == len(rcs.DEFAULT_FILES), "%d vs %d" % (len(present), len(rcs.DEFAULT_FILES)))
    # 真机件必须过新增不变式
    tmp = Path(tempfile.mkdtemp(prefix="r40_rcs_"))
    real = tmp / "rule_conflict_scan_probe.json"
    subprocess.run([sys.executable, str(HERE / "rule_conflict_scan.py"), "--json", str(real)],
                   capture_output=True, text=True, timeout=300)
    doc = json.loads(real.read_text(encoding="utf-8"))
    v = bcs.validate_doc(doc, art, "rcs")
    ck("t3 真机产物过契约（含新不变式 conflict_no_dead_inputs）", v == [], json.dumps(v, ensure_ascii=False)[:220])
    bad = json.loads(real.read_text(encoding="utf-8"))
    ev = bad.get("input_evidence") or {}
    if "files_present" in ev:
        ev["files_declared"] = ev["files_present"] + 1
    else:
        bad.setdefault("input_evidence", {})["files_declared"] = 10
        bad["input_evidence"]["files_present"] = 9
    v2 = bcs.validate_doc(bad, art, "rcs-bad")
    ck("t4 反例：声明 10 实存 9（有死条目）→ 契约必红并点名", any("CONFLICT-INPUT" in x for x in v2),
       json.dumps(v2, ensure_ascii=False)[:220])
    print(chr(10) + "夹具合计: %d 项，通过 %d，失败 %d"
          % (len(RESULTS), sum(1 for r in RESULTS if r[0]), sum(1 for r in RESULTS if not r[0])))
    print("[GATE:fixture-fail]" if any(not r[0] for r in RESULTS) else "[GATE:fixture-pass]")
    return 1 if any(not r[0] for r in RESULTS) else 0


if __name__ == "__main__":
    raise SystemExit(main())
