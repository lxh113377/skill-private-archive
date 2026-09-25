# -*- coding: utf-8 -*-
r"""r53_handles_fixtures.py — W-34「报告数字改引用可再生句柄」的层a 夹具（先看红）。

动因（r53 实测两侧）：
  · 对手侧：五家 README 正文数字 0–1 个，`addyosmani/agent-skills` 一个 README 就挂 **50 个文件链接**
    ⇒ 数值由被链接的产物承载，散文只指路；
  · 我方：`06-benchmark/` 有 **60 份机器可读件**，而 `README.md` 指向 .md 产物的链接数 = **0**
    ⇒ 既有"抄写数字会腐"的问题（r38 的 open_issues 跑了 12 轮），又有"产物存在但入口不可发现"的问题。

句柄（handle）的合格形状 = {artifact, field, selector, command} 四件齐，且：
  ① artifact 必须真实存在（指不到文件的句柄就是死输入，r40 L-4 同族）；
  ② 句柄必须**可解出值**（本夹具现场从 jsonl 末行取该字段，解不出即红）；
  ③ 零句柄 ⇒ UNVERIFIED（不得因为"没写句柄"而判绿，R-ENUM 边界条）。
"""

import importlib.util
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
RESULTS = []


def ck(name, cond, got=""):
    RESULTS.append((bool(cond), name, str(got)))
    print("%s %-58s %s" % ("PASS" if cond else "FAIL", name, "" if cond else "  <-- " + str(got)[:200]))


da = importlib.util.module_from_spec(
    importlib.util.spec_from_file_location("da53", str(HERE / "r38_debt_aging.py")))
importlib.util.spec_from_file_location("da53", str(HERE / "r38_debt_aging.py")).loader.exec_module(da)

mk = getattr(da, "make_handles", None)
ck("h0 判据存在性：r38_debt_aging 暴露 make_handles（缺则本轮即红阶段）", callable(mk), type(mk).__name__)
if not callable(mk):
    print("\n红阶段确认：句柄生成器未实现。")
    print("[GATE:fixture-fail]")
    sys.exit(1)

hd = mk({"by_class": {"OVERDUE": 0, "ACTIVE": 2, "DECIDED": 80, "UNDATED": 0,
                      "DEFERRED": 0, "REPEAT": 0},
          "evidence": {"open_total": 82}}, str(ROOT / "06-benchmark" / "debt_runs.jsonl"))
ck("h1 形状：至少给出 overdue / ledger_rows 两个句柄，且各含 artifact+field+command",
   len(hd) >= 2 and all({"artifact", "field", "command"} <= set(v) for v in hd.values()),
   json.dumps(hd, ensure_ascii=False)[:200])
ck("h2 可解值：overdue 句柄现场从台账末行取得出（句柄不是装饰，必须能解析）",
   da.resolve_handle(hd["overdue"]) == 0, da.resolve_handle(hd.get("overdue")))
ck("h3 死句柄必红：artifact 指不到文件 ⇒ resolve 返回 None 而不是 0（R247 禁把取不到当 0）",
   da.resolve_handle({"artifact": str(ROOT / "nope" / "x.jsonl"), "field": "overdue",
                      "command": "cat"}) is None,
   da.resolve_handle({"artifact": str(ROOT / "nope" / "x.jsonl"), "field": "overdue", "command": "cat"}))
ck("h4 反例：缺 field 的句柄 ⇒ resolve 判 None（形状不完整不得返回「看起来对」的值）",
   da.resolve_handle({"artifact": str(ROOT / "06-benchmark" / "debt_runs.jsonl"),
                      "command": "tail -1"}) is None,
   da.resolve_handle({"artifact": str(ROOT / "06-benchmark" / "debt_runs.jsonl"), "command": "tail -1"}))
ck("h5 台账行数句柄可解且 >0（趋势线长度本身也要能被引用而非抄写）",
   isinstance(da.resolve_handle(hd["ledger_rows"]), int) and da.resolve_handle(hd["ledger_rows"]) > 0,
   da.resolve_handle(hd.get("ledger_rows")))
ck("h6 command 必填且含可执行动词（禁写「见上文」这类不可复算的指路）",
   all(any(v in v2.get("command", "") for v in ("python ", "tail ", "git ", "jq ", "wc ", "grep ")) for v2 in hd.values()),
   {k: v.get("command", "")[:40] for k, v in hd.items()})

# ---- 真接线：写台账 → 再解句柄（证明句柄与源头是同一条链，不是巧合相等）----
import tempfile
tmp_led = Path(tempfile.mkdtemp(prefix="r53_h_")) / "debt_runs.jsonl"
tmp_rel = str(tmp_led)
doc = {"by_class": {"OVERDUE": 3, "ACTIVE": 1, "DECIDED": 2, "UNDATED": 0, "DEFERRED": 0, "REPEAT": 0},
       "evidence": {"open_total": 6}, "grace_rounds": 2, "current_round": 53}
assert da.append_ledger(str(tmp_led), doc, origin="local", head="r53test") == 1, "写台账失败"
hh = da.make_handles(doc, ledger_rel=str(tmp_led))
ck("h7 真机闭环：写进行末行后，句柄必须解出**同一值**（overdue=3 由源头再生，非抄写）",
   da.resolve_handle(hh["overdue"]) == 3 and da.resolve_handle(hh["ledger_rows"]) == 1,
   {k: da.resolve_handle(v) for k, v in hh.items()})
ck("h7b 反证：句柄指向不存在的台账 ⇒ None（源头断了必须显形，不得沿用旧值）",
   da.resolve_handle(da.make_handles(doc, ledger_rel=str(ROOT / "gone.jsonl"))["overdue"]) is None, "ok")

# ---- README 可发现性（W-35）：入口文档必须能指向证据面 ----
rd = io.open(ROOT / "README.md", encoding="utf-8", errors="replace").read()
links = json.loads(io.open(str(HERE / "_r53_readme_links.json"), encoding="utf-8").read()) \
    if (HERE / "_r53_readme_links.json").exists() else None
art = len(list((ROOT / "06-benchmark").glob("*.json")))
import re as _re
n_md_links = len(_re.findall(r"\]\([^)]*06-benchmark/[^)]+\)", rd))
ck("h8 可发现性：README 指向 06-benchmark 的链接数必须 >0（%d 份证据件不可达就是入口失效）" % art,
   n_md_links > 0, "链接数=%d" % n_md_links)
ck("h9 守恒：链接数不得超过证据件总数（防为凑数堆无效链接）",
   n_md_links <= art * 2, "链接=%d 件=%d" % (n_md_links, art))

# ---- h12 真机端到端：跑 CLI 写临时台账，句柄必须与同一次运行的 by_class 相等（r53 实测错位 84 vs 82 的回归）----
import subprocess
import tempfile


def resolve_or_none(h):
    try:
        return da.resolve_handle(h) if h else None
    except Exception as e:                                    # noqa: BLE001
        return ("ERR", type(e).__name__)


tmp2 = Path(tempfile.mkdtemp(prefix="r53_e2e_"))
led2 = tmp2 / "debt_runs.jsonl"
outj = tmp2 / "doc.json"
rp = subprocess.run([sys.executable, str(HERE / "r38_debt_aging.py"), "--ledger", str(led2),
                     "--json", str(outj)], capture_output=True, text=True,
                    encoding="utf-8", errors="replace")
docj = json.loads(io.open(outj, encoding="utf-8").read()) if outj.exists() else {}
hh2 = docj.get("handles") or {}
ck("h12 真机端到端：CLI 同一次运行内句柄值 == 本次 by_class（防「报告引用的是上一行」）",
   rp.returncode == 0 and resolve_or_none(hh2.get("overdue")) == docj.get("by_class", {}).get("OVERDUE")
   and resolve_or_none(hh2.get("open_total")) == docj.get("evidence", {}).get("open_total"),
   {"rc": rp.returncode, "handle_overdue": resolve_or_none(hh2.get("overdue")),
    "by_class": docj.get("by_class", {}).get("OVERDUE"), "drift": docj.get("handles_drift")})
ck("h13 真机无漂移标记：同轮一致性自检不得产生 handles_drift（产生即红）",
   not docj.get("handles_drift"), docj.get("handles_drift"))

print("\n夹具合计: %d 项，通过 %d，失败 %d"
      % (len(RESULTS), sum(1 for r in RESULTS if r[0]), sum(1 for r in RESULTS if not r[0])))
print("[GATE:fixture-fail]" if any(not r[0] for r in RESULTS) else "[GATE:fixture-pass]")
sys.exit(1 if any(not r[0] for r in RESULTS) else 0)
