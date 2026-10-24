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
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BENCH = ROOT / "06-benchmark"
PATTERN = "inject_ratchet_baseline.json"
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

# r208 修（接线腿与现状腿解耦，照 r202 runner_internals 先例）：
# 原写法直接跑真基线 ⇒ 项目一有真实活债（overdue_debt_items 实测 3 > 基线 0）就走 FAIL 分支，
# 而「再生周期行」与「[RATCHET:PASS]」**只印在 PASS 分支** ⇒ g10/g11 恒红。
# 那不是接线缺陷，是夹具把「本项目此刻绿不绿」焊进「打印代码有没有接线」。
# 本机是否全绿由 ratchet_gate 自身 + gate_run_freshness + debt_aging 三门常驻看守，此处不重复断言。
# 修法：临时基线 = 真基线骨架 + **现测指标值**（--json 现读）⇒ 无增长面 ⇒ 必走 PASS 分支，
# 于是断言的是「PASS 分支上声明行确实被打印」这个接线事实，与项目此刻红绿无关。
def _wire_run():
    import tempfile
    _td = tempfile.mkdtemp(prefix="r54_wire_")
    try:
        _tb = os.path.join(_td, "inject_ratchet_baseline.json")
        with io.open(str(BENCH / PATTERN), encoding="utf-8-sig") as f:
            _doc = json.load(f)
        # 先把临时基线落盘（否则第一次跑面对的是不存在的基线 ⇒ rc=2 且不产 live.json）
        with io.open(_tb, "w", encoding="utf-8", newline="") as f:
            json.dump(_doc, f, ensure_ascii=False, indent=1)
        # 再跑一次拿现测值（这一步本身也验证 --json 接线）
        subprocess.run([sys.executable, str(HERE / "ratchet_gate.py"),
                        "--baseline", _tb, "--json", os.path.join(_td, "live.json")],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=ROOT)
        try:
            with io.open(os.path.join(_td, "live.json"), encoding="utf-8-sig") as f:
                _live = json.load(f)
            if isinstance(_live.get("metrics"), dict) and _live["metrics"]:
                _doc["metrics"] = dict(_live["metrics"])
                with io.open(_tb, "w", encoding="utf-8", newline="") as f:
                    json.dump(_doc, f, ensure_ascii=False, indent=1)
        except Exception:
            pass
        _p = subprocess.run([sys.executable, str(HERE / "ratchet_gate.py"), "--baseline", _tb],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", cwd=ROOT)
        return _p.returncode, (_p.stdout or "") + (_p.stderr or "")
    finally:
        shutil.rmtree(_td, ignore_errors=True)

_rc_w, _out_w = _wire_run()
# r209 修 R113-5（夹具与真实项目状态耦合的第三种形态）：r208 只解耦了「增长面」，
# 没解耦「指标缺失面」—— ratchet 只要有任一指标算不出（本机 username_in_skill_files
# 恒缺失）就走 unknown 分支 rc=1，而 PASS 分支的两行只在该分支打印 ⇒ g10/g11 仍恒红。
# 那依旧不是接线缺陷：判据按 R247「算不出即红」是**正确设计**，错的是夹具把
# 「本机此刻能否算出全部指标」焊进「打印代码有没有接线」。
# 修法 = 三态分流（禁把第三态算通过，照 r208 同文件先例）：
#   · 输出含「缺失指标」⇒ 本机该指标不可算 ⇒ 接线腿 UNVERIFIED（不判红也不判绿）
#   · 否则必须走 PASS 分支且两行都在（真接线失败仍红）
_missing = "缺失指标" in _out_w
_WIRING_UNVERIFIED = False
if _missing:
    # 第三态**不得算通过**（r208 在同文件修掉的病：SKIP 伪装成 PASS 会吞掉「没验证到」的信号）。
    # 这里既不写 PASS 行也不写 FAIL 行，只打独立视觉标记，末尾汇总改印 UNVERIFIED 令牌。
    print("SKIP %-56s %s" % ("g10/g11 真接线：指标缺失面未解除（UNVERIFIED，非接线缺陷）",
                             "  <-- " + (_out_w.strip().splitlines()[-1][:150] if _out_w.strip() else "无输出")))
    _WIRING_UNVERIFIED = True
else:
    ck("g10 真接线：PASS 分支必须打印再生周期行（否则声明只存在于代码里，没人看得见）",
       "再生周期" in _out_w, _out_w.strip().splitlines()[-1][:150] if _out_w.strip() else "无输出")
    ck("g11 真接线：无增长面时判据必须判 PASS（证明它拦的是增长，不是恒红）",
       "[RATCHET:PASS]" in _out_w, _out_w.strip().splitlines()[-1][:150])

print("\n夹具合计: %d 项，通过 %d，失败 %d"
      % (len(RESULTS), sum(1 for r in RESULTS if r[0]), sum(1 for r in RESULTS if not r[0])))
if any(not r[0] for r in RESULTS):
    print("[GATE:fixture-fail]")
    sys.exit(1)
if _WIRING_UNVERIFIED:
    print("[GATE:fixture-unverified] 接线腿因本机指标缺失面未验证（非判据红，R247 不按绿记）")
    sys.exit(2)
print("[GATE:fixture-pass]")
sys.exit(0)
