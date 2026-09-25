# -*- coding: utf-8 -*-
r"""r52_mdclaim_fixtures.py — W-30「非 JSON 引用面的数字须带取值命令」的层a 夹具（先看红）。

口径（刻意保守，宁漏不误）：只把"像被测量结果"的数字当声明 —— 数字紧邻 条/份/例/组/行/B/倍/%/个，
且不在代码围栏内、不是 rNN/Vx.y/P0/日期/阈值上下文；命中后看**同行或下一行**有没有取值途径
（`python ` / `gh api ` / `git ` / `grep ` / 反引号命令 / 「取值」字样）。

判据函数刻意纯函数化（不读盘），真实文件面另跑一条集成断言，避免夹具与真机两回事。
"""

import importlib.util
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
RESULTS = []


def ck(name, cond, got=""):
    RESULTS.append((bool(cond), name, str(got)))
    print("%s %-58s %s" % ("PASS" if cond else "FAIL", name, "" if cond else "  <-- " + str(got)[:200]))


spec = importlib.util.spec_from_file_location("mc52", str(HERE / "r52_md_claim_face_scan.py"))
if spec is None or not (HERE / "r52_md_claim_face_scan.py").exists():
    ck("m0 判据存在性：05-exec/r52_md_claim_face_scan.py 存在（缺则本轮即红阶段）", False, "文件不存在")
    print("\n夹具合计: 1 项，通过 0，失败 1")
    print("[GATE:fixture-fail]")
    sys.exit(1)
mc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc)

# ---- 声明识别：该抓的必须抓到 ----
hit = mc.find_claims("实测 OVERDUE 13 条 / 最老 30 轮，详见台账。\n")
ck("m1 正例：数字+量词（13 条）被判为引用声明", any(x["token"] == "13 条" for x in hit), hit)
ck("m2 形状：命中项必须带 line/token 两个字段（供报告回指）",
   bool(hit) and all({"line", "token"} <= set(x) for x in hit), hit[:1])

# ---- 不该抓的绝不抓（误报面）----
neg = [
    ("代码围栏内数字", "```bash\npython x.py  # 12 例\n```\n"),
    ("轮次号 rNN", "- **2026-09-25（第 52 轮 r52）** — 本轮 8 例通过\n"),
    ("版本号 Vx.y", "上游 V3.48.0（2026-09-23）落地\n"),
    ("优先级标签", "P0 25 项分级与 P1 待定 3 个\n" if False else "见 P1 优先级 2 项\n"),
]
for name, text in neg:
    if name == "轮次号 rNN":          # 这条本身含「8 例」，须被抓；只要求 rNN/日期不被抓
        toks = [x["token"] for x in mc.find_claims(text)]
        ck("m3 不误报：轮次/日期形态不得成为声明（%s）" % name,
           not any(t.startswith("52") or t.startswith("2026") for t in toks), toks)
        continue
    ck("m3 不误报（%s）⇒ 零命中" % name, mc.find_claims(text) == [], mc.find_claims(text))

# ---- 命令紧邻性：同行 / 下一行 都算已自证 ----
a = mc.has_command_nearby("实测 13 条（取值 python 05-exec/r38_debt_aging.py --json /tmp/x.json）\n", 0, [])
ck("m4 正例：同行带 python 取值命令 ⇒ 判为已自证", a is True, a)
b = mc.has_command_nearby("台账 31 行\n", 0, ["  取值：gh api repos/x --jq .total_count\n"])
ck("m5 正例：下一行给取值命令 ⇒ 同样判为已自证（报告排版常态）", b is True, b)
c = mc.has_command_nearby("台账 31 行，数字很硬但没有命令\n", 0, ["\n"])
ck("m6 反例：无命令 ⇒ 判为未自证（这才是本判据要抓的形态）", c is False, c)

# ---- 分级：只有"裸数字 + 结论句"才计入敞口，避免把叙述当违规 ----
scored = mc.summarize([
    {"line": 1, "token": "13 条", "has_cmd": True},
    {"line": 2, "token": "31 行", "has_cmd": False},
    {"line": 3, "token": "3.5 倍", "has_cmd": False},
])
ck("m7 汇总口径：分母=全部声明、敞口=无命令数，二者不得混为一谈",
   scored["claims"] == 3 and scored["uncited"] == 2, scored)
ck("m8 边界：空面 ⇒ UNVERIFIED 而非 0 敞口（R247 零输入不得记绿）",
   mc.summarize([])["status"] == "UNVERIFIED", mc.summarize([]))
ck("m9 反例：全 0 敞口但分母为 0 时不得判 PASS",
   mc.summarize([])["status"] != "PASS", mc.summarize([]))

# ---- 真机集成：跑本仓 06-benchmark/*.md，量出误报率所需原始数 ----
res = mc.scan_files(sorted((HERE.parent / "06-benchmark").glob("*.md")))
ck("m10 真机：能取到非空统计（声明数>0 且逐条带文件与行号）",
   res["claims"] > 0 and all({"file", "line", "token"} <= set(x) for x in res["uncited_list"]),
   {k: res[k] for k in ("files", "claims", "uncited")})
ck("m11 真机：状态只可能是 PASS/EXPOSED/UNVERIFIED 三态之一（禁自造取值）",
   res["status"] in ("PASS", "EXPOSED", "UNVERIFIED"), res["status"])

# ---- 可整改面判定的默认方向（r52 实测修：未知形态不得默认当轮）----
ck("m12 默认方向：无 rNN 且无日期的件 ⇒ 归历史面，不得冒充可整改（否则会去回改历史，违 R241）",
   mc.is_live("某张没有编号的旧基线.md") is False, mc.is_live("某张没有编号的旧基线.md"))
ck("m13 分面正确：老日期件归历史、rNN≥51 归可整改、rNN<51 归历史",
   (mc.is_live("memory_eval基线_2026-09-24.md") is False
    and mc.is_live("全量对标报告_r51_x_2026-09-25.md") is True
    and mc.is_live("全量对标报告_r44_x_2026-09-25.md") is False),
   [mc.is_live("memory_eval基线_2026-09-24.md"), mc.is_live("全量对标报告_r51_x_2026-09-25.md"),
    mc.is_live("全量对标报告_r44_x_2026-09-25.md")])
ck("m14 真机分面守恒：可整改 + 历史 == 全部声明（两列不得重叠或漏计）",
   res["live_claims"] + res["historical_claims"] == res["claims"], 
   (res["live_claims"], res["historical_claims"], res["claims"]))

ck("m15 不误报：标题行（H1/H2）里的数字不算声明 —— r52 实测报告标题的「3.5 倍」曾被误判",
   mc.find_claims("# 全量对标报告 r52 — 敞口 3.5 倍与 175 处\n## 2. 差距 21 组\n") == [],
   mc.find_claims("# 全量对标报告 r52 — 敞口 3.5 倍与 175 处\n## 2. 差距 21 组\n"))
ck("m16 不误伤正文：同样数字出现在正文里必须仍被抓（排除标题不得顺手放过正文）",
   [x["token"] for x in mc.find_claims("正文实测敞口 3.5 倍与 175 条\n")] == ["3.5 倍", "175 条"],
   mc.find_claims("正文实测敞口 3.5 倍与 175 条\n"))

live_status = ("UNVERIFIED" if not res["live_claims"] else
               ("PASS" if not res["live_uncited"] else "EXPOSED"))
ck("m17 真机接线：可整改面（r≥51 或当日 mtime）必须零敞口 ⇒ 新增无命令数字会红",
   live_status == "PASS", "live=%d uncited=%d 历史面=%d（不参与判定）" % (
       res["live_claims"], res["live_uncited"], res["historical_claims"]))

print("\n夹具合计: %d 项，通过 %d，失败 %d"
      % (len(RESULTS), sum(1 for r in RESULTS if r[0]), sum(1 for r in RESULTS if not r[0])))
print("[GATE:fixture-fail]" if any(not r[0] for r in RESULTS) else "[GATE:fixture-pass]")
sys.exit(1 if any(not r[0] for r in RESULTS) else 0)
