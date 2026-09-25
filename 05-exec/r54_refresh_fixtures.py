# -*- coding: utf-8 -*-
r"""r54_refresh_fixtures.py — W-36「指标须声明再生周期」的层a 夹具（先看红）。

动因（r54 双侧实测）：
  · 对手侧：五家只有 2 家在 workflow 里声明**节律**（cron/timeout/concurrency 行 pre-commit 12、spec-kit 7，
    其余 0）⇒ "多久必须跑一次"是被显式声明的对象，不是我凭感觉重跑；
  · 我方：r53 差点让 `catalog_grand_chars` 跟 33 轮前的快照比（实为命名假阳性，但揭开的是真缺口——
    **没有任何地方声明每个指标多久必须重算**，源件烂在柜里也照样出数）。

判据口径：
  · 纯函数 `face_metric_refresh(age_days, budget_days)` ⇒ 三态 OK / STALE / UNVERIFIED；
  · 取不到年龄（活体扫描无源件、文件缺失）⇒ **UNVERIFIED 而非 OK**（R-ENUM 边界条）；
  · 超期 ⇒ 该指标值作废转 unknown（宁可"算不出"，也不拿陈旧源件冒充现值），
    但**只影响该指标**，其余照常判定（不得因一项源件过期把整轮抹红成不可用）。
"""

import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
RESULTS = []


def ck(name, cond, got=""):
    RESULTS.append((bool(cond), name, str(got)))
    print("%s %-56s %s" % ("PASS" if cond else "FAIL", name, "" if cond else "  <-- " + str(got)[:190]))


rg = importlib.util.module_from_spec(
    importlib.util.spec_from_file_location("rg54", str(HERE / "ratchet_gate.py")))
importlib.util.spec_from_file_location("rg54", str(HERE / "ratchet_gate.py")).loader.exec_module(rg)

f = getattr(rg, "face_metric_refresh", None)
ck("g0 判据存在性：ratchet_gate 暴露 face_metric_refresh（缺则本轮即红阶段）", callable(f), type(f).__name__)
if not callable(f):
    print("\n红阶段确认：再生周期判据未实现。")
    print("[GATE:fixture-fail]")
    sys.exit(1)

ck("g1 正例：源件 1 天前、预算 3 天 ⇒ OK", f(1.0, 3) == "OK", f(1.0, 3))
ck("g2 反例：源件 12 天前、预算 3 天 ⇒ STALE（陈旧源件不得冒充现值）", f(12.0, 3) == "STALE", f(12.0, 3))
ck("g3 边界：年龄取不到（None）⇒ UNVERIFIED，绝不等于 OK", f(None, 3) == "UNVERIFIED", f(None, 3))
ck("g4 边界：预算未声明（None）⇒ UNVERIFIED（没声明周期本身就是缺口）", f(1.0, None) == "UNVERIFIED", f(1.0, None))
ck("g5 边界：预算为 0 ⇒ UNVERIFIED 而非「全部过期」（禁把配置写错变成全员判红）", f(1.0, 0) == "UNVERIFIED", f(1.0, 0))

b = getattr(rg, "METRIC_REFRESH_DAYS", None)
ck("g6 覆盖面：9 个指标必须**逐个**声明预算（缺任一即红，禁默认值兜底）",
   isinstance(b, dict) and set(b) == set(rg.METRIC_NAMES),
   sorted(set(rg.METRIC_NAMES) - set(b or {})))
ck("g7 形状：预算必须是 (1, 60] 天内的正数（防写成 0 或 9999 让判据失效）",
   bool(b) and all(isinstance(v, (int, float)) and 0 < v <= 60 for v in b.values()), b)

# ---- 真机：本轮全部指标源件必须未过期（过期即红，说明我该重跑探针而不是继续引用旧数）----
ages = {k: rg.source_age_days(k) for k in rg.METRIC_NAMES}
stale = [k for k, v in ages.items() if rg.face_metric_refresh(v, rg.METRIC_REFRESH_DAYS[k]) == "STALE"]
unver = [k for k, v in ages.items() if rg.face_metric_refresh(v, rg.METRIC_REFRESH_DAYS[k]) == "UNVERIFIED"]
ck("g8 真机：9 指标无一个源件超期（r54 接线时的误报率基线 = 0）", not stale, {"stale": stale})
ck("g9 真机：活体扫描类指标（无源件）必须显式记 UNVERIFIED 而非混进 OK",
   set(unver) == {"username_in_skill_files"} or not unver, unver)

rp = subprocess.run([sys.executable, str(HERE / "ratchet_gate.py")], capture_output=True,
                    text=True, encoding="utf-8", errors="replace")
out = (rp.stdout or "") + (rp.stderr or "")
ck("g10 真接线：CLI 输出必须打印再生周期行（否则声明只存在于代码里，没人看得见）",
   "再生周期" in out, out.strip().splitlines()[-1][:150] if out.strip() else "无输出")
ck("g11 真接线：加判据不得把本轮判红（只降不升的口径不变）",
   "[RATCHET:PASS]" in out, out.strip().splitlines()[-1][:150])

print("\n夹具合计: %d 项，通过 %d，失败 %d"
      % (len(RESULTS), sum(1 for r in RESULTS if r[0]), sum(1 for r in RESULTS if not r[0])))
print("[GATE:fixture-fail]" if any(not r[0] for r in RESULTS) else "[GATE:fixture-pass]")
sys.exit(1 if any(not r[0] for r in RESULTS) else 0)
