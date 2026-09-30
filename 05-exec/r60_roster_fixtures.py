# -*- coding: utf-8 -*-
r"""r60_roster_fixtures.py — 第 18 维新不变式 `roster_partition_sum` 的双向夹具（W-47）.

存在理由（r60 一手）：名册生成器首版把「路径条数」当分母，并让单仓 864 条生成式清单占掉
对手面 79.8% —— 域内自洽、整体失真。把这层防护钉进契约只算前半步；按 W-47，新判据首跑
必须同时交出「应绿的绿」与「应红的红」，且对照组自身要被证伪过一轮。本件即那两向证据：
  A 真件面：直接拿盘上两份 r60 证据件喂 `inv_roster_partition_sum` ⇒ 必须 0 违规；
  B 变异面（应红）：① 抽掉一行 domain（和 ≠ 总数）② 抽掉一条 item 的 retrieval
    ③ 件里既无 domains 也无 items（零面）④ items 长度与 totals.gap_items 不符。
每一例都断言**具体报错文本**，不只断言「非空」——否则换个不相关的红也算过。

取值：`python 05-exec/r60_roster_fixtures.py`
退出码：0 = 全过；1 = 有例失败；2 = 证据件缺失（零面不判过，R247）。
"""

import copy
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ROSTER = os.path.join(ROOT, "06-benchmark", "capability_roster_r60_2026-09-30.json")
GAP = os.path.join(ROOT, "06-benchmark", "capability_gap_r60_2026-09-30.json")


def load_scanner():
    spec = importlib.util.spec_from_file_location(
        "baseline_contract_scan", os.path.join(HERE, "baseline_contract_scan.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    missing = [p for p in (ROSTER, GAP) if not os.path.isfile(p)]
    if missing:
        sys.stderr.write("[GATE:roster-fixture-fail] 证据件缺失，零面不判过：%s\n" % missing)
        return 2
    mod = load_scanner()
    fn = mod.INVARIANTS.get("roster_partition_sum")
    if fn is None:
        sys.stderr.write("[GATE:roster-fixture-fail] 契约声明了 roster_partition_sum 但实现缺失\n")
        return 1
    roster = json.loads(io.open(ROSTER, encoding="utf-8-sig").read())
    gap = json.loads(io.open(GAP, encoding="utf-8-sig").read())

    cases = []

    def case(name, doc, want_substr):
        msgs = fn(doc, "roster_partition_sum")
        hit = any(want_substr in m for m in msgs)
        cases.append((name, hit, "want=%r got=%r" % (want_substr, msgs[:2])))

    # A 真件面：应绿
    cases.append(("a1 真件 roster 0 违规", fn(roster, "roster_partition_sum") == [],
                  "got=%r" % fn(roster, "roster_partition_sum")[:2]))
    cases.append(("a2 真件 gap 0 违规", fn(gap, "roster_partition_sum") == [],
                  "got=%r" % fn(gap, "roster_partition_sum")[:2]))

    # B 变异面：应红（逐条断言报错文本）
    m = copy.deepcopy(roster)
    m["domains"] = m["domains"][:-1]
    case("b1 抽掉一行 domain 应报和≠总数", m, "之和")
    m = copy.deepcopy(gap)
    m["items"][0].pop("retrieval", None)
    case("b2 抽掉 item 的 retrieval 应点名", m, "缺 retrieval")
    case("b3 零面（既无 domains 也无 items）应判红", {"totals": {}}, "零面")
    m = copy.deepcopy(gap)
    m["items"] = m["items"][:5]
    case("b4 items 长度与 totals 不符应报", m, "items 长度")

    # C 第三把尺（语义面）：真件应绿、四类破坏应红
    sem_path = os.path.join(ROOT, "06-benchmark", "semantic_coverage_r61_2026-09-30.json")
    if not os.path.isfile(sem_path):
        sys.stderr.write("[GATE:roster-fixture-fail] 语义面证据件缺失，零面不判过：%s\n" % sem_path)
        return 2
    sem = json.loads(io.open(sem_path, encoding="utf-8-sig").read())
    sfn = mod.INVARIANTS.get("semantic_face_sum")
    if sfn is None:
        sys.stderr.write("[GATE:roster-fixture-fail] 契约声明了 semantic_face_sum 但实现缺失\n")
        return 1
    cases.append(("c1 真件语义面 0 违规", sfn(sem, "semantic_face_sum") == [],
                  "got=%r" % sfn(sem, "semantic_face_sum")[:2]))
    def scase(name, doc, want_substr):
        msgs = sfn(doc, "semantic_face_sum")
        hit = any(want_substr in m for m in msgs)
        cases.append((name, hit, "want=%r got=%r" % (want_substr, msgs[:2])))

    m = copy.deepcopy(sem)
    m["tiers"] = {"face_A_router_index": m["tiers"]["face_A_router_index"]}
    scase("c2 只剩一个语料面应点名", m, "只有 1 个语料面")
    m = copy.deepcopy(sem)
    m["totals"]["gap_double_refuted"] = 0
    scase("c3 三桶不守恒应报", m, "三桶不守恒")
    m = copy.deepcopy(sem)
    m["tiers"]["face_B_loadable"]["no_neighbour"] += 3
    scase("c4 档分布之和偏离 items 应报", m, "之和")

    # D 契约自身层级守卫（r60 D-124 与 r61 同形态复发的机器面）
    contract = json.loads(io.open(mod.CONTRACT_FILE, encoding="utf-8-sig").read())
    cases.append(("c5 真契约 层级守卫通过", mod.check_contract_nesting(contract) is None,
                  "got=%r" % mod.check_contract_nesting(contract)))
    leaked = copy.deepcopy(contract)
    leaked["capability_gap_r*.json"] = leaked["artifacts"]["capability_gap_r*.json"]
    cases.append(("c6 条目漏到顶层应被点名", "顶层出现未知键" in (
        mod.check_contract_nesting(leaked) or ""),
        "got=%r" % mod.check_contract_nesting(leaked)))

    passed = sum(1 for _, ok, _ in cases if ok)
    for name, ok, detail in cases:
        print("  %-40s %s   %s" % (name, "PASS" if ok else "FAIL", "" if ok else detail))
    if passed == len(cases):
        print("[GATE:roster-fixture-pass] %d/%d" % (passed, len(cases)))
        return 0
    print("[GATE:roster-fixture-fail] %d/%d" % (passed, len(cases)))
    return 1


if __name__ == "__main__":
    sys.exit(main())
