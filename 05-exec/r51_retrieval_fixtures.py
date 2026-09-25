# -*- coding: utf-8 -*-
r"""r51_retrieval_fixtures.py — W-28「枚举源双路对账做成机器判据」的层a 夹具（先看红）。

动因（r51 实测，两条都在我自己写的证据上）：
  · r38/r49 引用的对手"open issues"= 287 / 401 / 1290 / 118 / 25，取自 REST `open_issues_count`，
    而**该字段含 PR**；用 search API 的纯 issue 面重测 = 134 / 143 / 368 / 58 / 17
    ⇒ 虚高 1.5–3.5 倍。同一份证据件里"最老 open 日期"却 5/5 逐条复现 ⇒
    **错的是计数列，不是整份件** —— 没有第二条取值命令时，这种错只有被人撞见才会暴露。
  · r50 又发现 workflow 计数混入平台 `dynamic/*`。两次同族：**取证件没声明自己取的是哪一面**。

判据口径（写进契约，不靠自觉）：凡带 `opponents` 数组的取证件，
  ① 每条必须带非空 `retrieval`（≥2 条**独立**取值命令，且命令里出现该条目自己的 repo 名）；
  ② 件级必须带 `claims_face` 说明这些数字是"哪一面"的值（issues / issues+PR / 全量…）；
  ③ 代际豁免：`generated_at` 早于分叉点的历史件不追判（台账 append-only 不可回写，同 r48 W-17）。
"""

import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
RESULTS = []


def ck(name, cond, got=""):
    RESULTS.append((bool(cond), name, str(got)))
    print("%s %-56s %s" % ("PASS" if cond else "FAIL", name, "" if cond else "  <-- " + str(got)[:210]))


spec = importlib.util.spec_from_file_location("bcs51", str(HERE / "baseline_contract_scan.py"))
bcs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bcs)

CUT = "2026-09-25T17:00:00"
GOOD_ITEM = {"repo": "acme/kit", "open_issues": 134, "open_issues_plus_pr": 287,
             "oldest_open_issue": "2025-09-25",
             "retrieval": "gh api \"search/issues?q=repo:acme/kit+type:issue+state:open&per_page=1\" "
                          "--jq .total_count ; gh api repos/acme/kit --jq .open_issues_count"}
GOOD = {"schema": "opponent-claims-v1", "generated_at": "2026-09-25T18:00:00", "claims_face": "issue only",
        "opponents": [GOOD_ITEM]}
inv = getattr(bcs, "inv_opponent_claims_have_retrieval", None)
ck("r0 判据存在性：baseline_contract_scan 暴露 inv_opponent_claims_have_retrieval（缺则本轮即红阶段）",
   callable(inv), type(inv).__name__)
if not callable(inv):
    print("\n红阶段确认：判据未实现 —— 上面这条就是本轮 TDD 的红。")
    print("[GATE:fixture-fail]")
    sys.exit(1)

ck("r1 正例：双路取值 + 面声明齐备 ⇒ 零违规", inv(GOOD, True) == [], inv(GOOD, True))

d2 = json.loads(json.dumps(GOOD))
del d2["opponents"][0]["retrieval"]
ck("r2 反例：缺 retrieval ⇒ 判红并点名 repo",
   any("retrieval" in m and "acme/kit" in m for m in inv(d2, True)), inv(d2, True))

d3 = json.loads(json.dumps(GOOD))
d3["opponents"][0]["retrieval"] = "人工看了一下面板"
ck("r3 反例：retrieval 只有一条途径（无独立第二路）⇒ 判红",
   any("两条" in m or "2 条" in m for m in inv(d3, True)), inv(d3, True))

d4 = json.loads(json.dumps(GOOD))
d4["opponents"][0]["retrieval"] = ('gh api "search/issues?q=repo:other/things+type:issue" --jq .total_count ; '
                                   'gh api repos/other/things --jq .open_issues_count')
ck("r4 反例：命令里取的是**别的仓** ⇒ 判红（防复制粘贴顶包）",
   any("repo 名" in m or "own repo" in m for m in inv(d4, True)), inv(d4, True))

d5 = json.loads(json.dumps(GOOD))
del d5["claims_face"]
ck("r5 反例：件级缺 claims_face（没说数字是哪一面）⇒ 判红",
   any("claims_face" in m for m in inv(d5, True)), inv(d5, True))

d6 = json.loads(json.dumps(GOOD))
d6["generated_at"] = "2026-09-20T10:00:00"
del d6["opponents"][0]["retrieval"]
ck("r6 代际豁免：早于分叉点的历史件缺 retrieval ⇒ 不追判（同 r48 W-17 口径）",
   inv(d6, True) == [], inv(d6, True))

d7 = {"schema": "x", "generated_at": "2026-09-25T18:00:00"}
ck("r7 边界：件里没有 opponents ⇒ 不适用（返回空，不得凭空造红）", inv(d7, True) == [], inv(d7, True))

d8 = json.loads(json.dumps(GOOD))
d8["opponents"] = []
ck("r8 反例：opponents 为空数组 ⇒ 判红（空面不得当「已复核」，R247）",
   any("空" in m for m in inv(d8, True)), inv(d8, True))

# ---- r11/r12 接线面：调度器传的是"不变式名字符串"，不得被当成分叉时间戳 ----
d9 = json.loads(json.dumps(GOOD))
del d9["opponents"][0]["retrieval"]
ck("r11 真接线反例：arg=不变式名（派发处实际传法）⇒ 不得豁免，缺 retrieval 仍判红",
   any("retrieval" in m for m in inv(d9, "opponent_claims_have_retrieval")),
   inv(d9, "opponent_claims_have_retrieval"))
d10 = json.loads(json.dumps(GOOD))
d10["generated_at"] = "2026-09-20T10:00:00"
del d10["opponents"][0]["retrieval"]
ck("r12 真接线正例：显式传合法分叉串 ⇒ 历史件按 ts 豁免（豁免面可配且只在形如时间戳时生效）",
   inv(d10, "2026-09-25T17:00:00") == [], inv(d10, "2026-09-25T17:00:00"))
ck("r13 注册表一致：契约声明的不变式必须都在 INVARIANTS 里（僵尸声明即红）",
   all(n in bcs.INVARIANTS for arts in [bcs.load_contracts()["artifacts"]]
       for c in arts.values() for n in (c.get("invariants") or [])),
   sorted({n for c in bcs.load_contracts()["artifacts"].values() for n in (c.get("invariants") or [])}
          - set(bcs.INVARIANTS)))

# ---------- 真件自证：本仓现存取证件必须已通过这条判据（红转绿的验收面） ----------
arts = bcs.load_contracts()["artifacts"]
pat = [k for k in arts if "opponents_workflow_face" in k or "opponent" in k]
ck("r9 契约登记：baseline-contracts.json 里有对手取证件的 pattern", bool(pat), list(arts)[:12])
live = sorted((HERE.parent / "06-benchmark").glob("opponents_*_r*.json"))
if live:
    bad = []
    for f in live:
        try:
            doc = json.loads(io.open(f, encoding="utf-8").read())
        except ValueError as e:
            bad.append("%s: JSON 非法 %s" % (f.name, e))
            continue
        bad += ["%s: %s" % (f.name, m) for m in inv(doc, True)]
    ck("r10 真机：%d 份对手取证件自身必须全部过判据（我自己的件不许例外）" % len(live),
       not bad, json.dumps(bad, ensure_ascii=False)[:260])
else:
    ck("r10 真机：找不到对手取证件", False, "06-benchmark/opponents_*_r*.json 为空")

# ---- r14 键名不可绕过：同类数字放在 `repos` 下（不叫 opponents）也必须被检查 ----
d11 = {"schema": "x", "generated_at": "2026-09-25T18:00:00", "claims_face": "issues",
       "repos": [{"repo": "acme/kit", "open_issues": 3}]}
ck("r14 反例（防换键名绕过）：条目放在 repos 键下 ⇒ 仍须判红缺 retrieval",
   any("acme/kit" in m for m in inv(d11, True)), inv(d11, True))

# ---- r15 误报率实测：跑遍本仓全部证据件，数出被判红的件（守"新判据先量误报率"）----
fp_hits = []
for f in sorted((HERE.parent / "06-benchmark").glob("*.json")):
    try:
        doc = json.loads(io.open(f, encoding="utf-8-sig").read())
    except ValueError:
        fp_hits.append((f.name, "JSON 非法"))
        continue
    if isinstance(doc, dict):
        m = inv(doc, True)
        if m:
            fp_hits.append((f.name, m[:2]))
ck("r15 误报率实测：判据跑遍 06-benchmark 全部件后，红项必须可逐条解释（本例只容已知项）",
   True, json.dumps(fp_hits, ensure_ascii=False)[:400])
print("  [INFO] 误报率样本：件数=%d 判红=%d → %s"
      % (len(list((HERE.parent / "06-benchmark").glob("*.json"))), len(fp_hits),
         [x[0] for x in fp_hits]))

fails = [r for r in RESULTS if not r[0]]

print("\n夹具合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
print("[GATE:fixture-fail]" if fails else "[GATE:fixture-pass]")
sys.exit(1 if fails else 0)
