# -*- coding: utf-8 -*-
r"""r117_route_miss_attr.py -- 生产路由 miss 归因引擎（只读；需求 6「提升幅度」的第一块地基）。

存在理由（r117 一手，接 r115 §5 Q1-Q3 与 r114 的口径错误）：
  r115 修好尺之后，生产路由在仓内权威面 layered 291 条上是 88.3%（271/291），
  剩 20 条 miss 一直只被写成「长尾个案」，**没有人逐条判过它们到底是谁的问题**。
  这是「提升 ≥30%」最前置的一步：分不清 STALE_EXPECT（题面过期）与 REAL_MISS
  （路由真错），任何改进都只能靠猜，改进幅度也不可归因。

判据（三态 + 一类单列，四者之和 == miss 总数，X-7 自洽校验）：
  STALE_EXPECT  期望 skill 既不在注册表也不在盘上 ⇒ 题面写的是一门已退役/不存在的技能
                （典型：deep-research-pro / multi-search-engine / weather 等已在 r 早轮退役）
  UNREGISTERED  期望 skill 在盘上但不在注册表 ⇒ 漏注册态，单列并具名，禁并入 STALE
  REAL_MISS     期望 skill 在册且在盘 ⇒ 路由真错（本类才可作为改进靶子）
  UNDECIDABLE   注册表或盘面取不到 ⇒ 单独成类，禁并入 REAL_MISS 蒙绿（R247）

分母守恒（本件核心断言）：
  stale + unregistered + real + undecidable == miss_n
  hits + miss_n == n

口径红线（写进产物）：
  · 只读 焚诀 eval/ 与注册表，**不代改**题面期望（eval 只读红线）；
  · 过期期望的处置 = 登记转办（transmit proposal），不是本仓自己改题再宣称提升；
  · 本件只做归因，不做任何「提升」主张；提升判定仍走 r114 §3.3 / r115 §3 的 C1-C3。

用法：
  python 05-exec/r117_route_miss_attr.py                       # 现跑权威评估器
  python 05-exec/r117_route_miss_attr.py --reuse <eval.json>   # 复用已落盘评估结果
  python 05-exec/r117_route_miss_attr.py --json <件> --quiet
退出码：0 出件且分母守恒 / 2 输入面不可用（R247 零输入不得记绿）
"""
import argparse
import io
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")
FENJUE = r"C:\Users\37533\Desktop\workspace\焚诀"
EVAL = os.path.join(FENJUE, "eval")
REGISTRY = os.path.join(FENJUE, "skill", "registry", "unified-skills-index.json")
GS = r"D:\global_skills"
PY_CANDIDATES = [
    os.path.expanduser(r"~\.workbuddy\binaries\python\envs\default\Scripts\python.exe"),
    r"C:\Program Files\Python312\python.exe",
]

STATE_ORDER = ["STALE_EXPECT", "UNREGISTERED", "REAL_MISS", "UNDECIDABLE"]


def pick_python():
    for p in PY_CANDIDATES:
        if os.path.exists(p):
            return p
    return sys.executable


def load_json(path):
    raw = io.open(path, "rb").read()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return json.loads(raw.decode("utf-16"))
    return json.loads(raw.decode("utf-8-sig"))


def run_layered_eval():
    """现跑仓内权威评估器；失败返回 (None, 原因)，禁静默。"""
    py = pick_python()
    argv = [py, os.path.join(EVAL, "frozen_blind_eval.py"), "--json", "--set", "layered"]
    try:
        p = subprocess.run(argv, cwd=FENJUE, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=1800)
    except Exception as exc:  # noqa: BLE001
        return None, "exc:%r" % (exc,)
    raw = (p.stdout or "").strip()
    if not raw:
        return None, "empty_stdout rc=%s stderr=%s" % (p.returncode, (p.stderr or "")[:300])
    start = raw.find("{")
    if start < 0:
        return None, "no_json rc=%s head=%s" % (p.returncode, raw[:200])
    try:
        return json.loads(raw[start:]), None
    except ValueError as exc:
        return None, "json:%r tail=%s" % (exc, raw[-300:])


def load_registry_names():
    if not os.path.isfile(REGISTRY):
        return None, "registry_missing:%s" % REGISTRY
    try:
        doc = load_json(REGISTRY)
    except (OSError, ValueError) as exc:
        return None, "registry_unreadable:%r" % (exc,)
    skills = doc.get("skills")
    if isinstance(skills, dict):
        names = sorted(skills.keys())
    elif isinstance(skills, list):
        names = sorted([s.get("name") or s.get("slug") for s in skills if isinstance(s, dict)])
    else:
        return None, "registry_schema_unknown:keys=%s" % ",".join(sorted(doc.keys())[:8])
    if not names:
        return None, "registry_empty"
    return set(names), None


def classify(expected, registry, disk_cache):
    """返回 (state, reason)。expected 为 None（盲区题）时由调用方先行处理。"""
    if expected is None:
        return None, None
    if registry is None:
        return "UNDECIDABLE", "registry_unavailable"
    if expected in registry:
        return "REAL_MISS", "in_registry"
    on_disk = disk_cache.get(expected)
    if on_disk is None:
        on_disk = os.path.isdir(os.path.join(GS, expected))
        disk_cache[expected] = on_disk
    if on_disk:
        return "UNREGISTERED", "on_disk_not_in_registry"
    return "STALE_EXPECT", "absent_from_disk_and_registry"


def pair_of(row):
    """混淆对：期望 -> 实路由（用于『谁顶替了谁』的聚类，不做因果推断）。"""
    return "%s->%s" % (row.get("expected"), row.get("router_top1"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reuse", default=None, help="复用已落盘的 frozen_blind_eval --json 结果")
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    if args.reuse:
        if not os.path.isfile(args.reuse):
            print("[ROUTEMISS:UNVERIFIED] --reuse 件不存在: %s" % args.reuse)
            return 2
        ev, ev_err = load_json(args.reuse), None
    else:
        ev, ev_err = run_layered_eval()
    if not ev:
        print("[ROUTEMISS:UNVERIFIED] 权威评估器不可用 => 禁记绿（%s）" % ev_err)
        return 2

    registry, reg_err = load_registry_names()
    if registry is None:
        print("[ROUTEMISS:UNVERIFIED] 注册表不可用 => 禁记绿（%s）" % reg_err)

    results = ev.get("results") or []
    if not results:
        print("[ROUTEMISS:UNVERIFIED] 评估结果为空 => 不得读成无 miss（R247）")
        return 2

    disk_cache = {}
    rows = []
    states = {k: 0 for k in STATE_ORDER}
    blind_n = 0
    for r in results:
        expected = r.get("expected")
        if expected is None:
            # 盲区题：期望就是"不该路由到任何 skill"，命中判据是 top1 为 NONE
            blind_n += 1
            if not r.get("hit"):
                st, reason = "REAL_MISS", "blind_query_should_be_none"
            else:
                continue
        elif r.get("hit"):
            continue
        else:
            st, reason = classify(expected, registry, disk_cache)
        states[st] += 1
        rows.append({
            "query": r.get("query"),
            "expected": expected,
            "router_top1": r.get("router_top1"),
            "judge": r.get("judge"),
            "state": st,
            "reason": reason,
            "pair": pair_of(r),
        })

    miss_n = len(rows)
    conservation = (sum(states.values()) == miss_n
                    and (int(ev.get("hits") or 0) + miss_n == int(ev.get("n") or 0)))
    face = {
        "n": ev.get("n"),
        "hits": ev.get("hits"),
        "score_pct": ev.get("score"),
        "semantic_layer": ev.get("semantic_layer"),
        "bge_status": ev.get("bge_status"),
        "miss_n": miss_n,
        "blind_n": blind_n,
        "registry_n": len(registry) if registry else None,
        "stale_n": states["STALE_EXPECT"],
        "unregistered_n": states["UNREGISTERED"],
        "real_n": states["REAL_MISS"],
        "undecidable_n": states["UNDECIDABLE"],
        "conservation_ok": conservation,
    }
    # 去重聚合：同一期望被多次 miss、同一混淆对重复出现
    by_expected = {}
    for r in rows:
        by_expected.setdefault(str(r["expected"]), []).append(r["state"])
    by_pair = {}
    for r in rows:
        by_pair[r["pair"]] = by_pair.get(r["pair"], 0) + 1

    doc = {
        "schema": "route-miss-attr-r117-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "cmd": "python 05-exec/r117_route_miss_attr.py",
        "ruler": {
            "STALE_EXPECT": "期望 skill 既不在注册表也不在盘上（题面过期）",
            "UNREGISTERED": "期望 skill 在盘上但不在注册表（漏注册，单列）",
            "REAL_MISS": "期望 skill 在册且在盘（路由真错，唯一可作改进靶子）",
            "UNDECIDABLE": "注册表/盘面取不到（禁并入 REAL_MISS 蒙绿，R247）",
            "conservation": "stale + unregistered + real + undecidable == miss_n 且 hits + miss_n == n",
        },
        "inputs": {
            "eval": ("reuse:%s" % args.reuse) if args.reuse else "eval/frozen_blind_eval.py --json --set layered",
            "registry": REGISTRY.replace("\\", "/"),
            "registry_error": reg_err,
        },
        "face": face,
        "states_by_expected": by_expected,
        "pairs": by_pair,
        "rows": rows,
    }
    out = args.json_out or os.path.join(
        BENCH, "route_miss_attr_r117_%s.json" % datetime.now().strftime("%Y-%m-%d"))
    tmp = out + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out)

    if not args.quiet:
        print("覆盖根：生产路由评分 = eval/frozen_blind_eval.py（权威件）｜注册表 = skill/registry/unified-skills-index.json")
        print("  L1 layered: %s%%（%s/%s，%s 层）｜miss=%d｜盲区题=%d"
              % (face["score_pct"], face["hits"], face["n"],
                 face["semantic_layer"], miss_n, blind_n))
        print("  归因：STALE_EXPECT=%d  UNREGISTERED=%d  REAL_MISS=%d  UNDECIDABLE=%d"
              % (face["stale_n"], face["unregistered_n"], face["real_n"], face["undecidable_n"]))
        for r in rows:
            print("    %-13s %-28s -> %-24s | %s"
                  % (r["state"], str(r["expected"])[:28], str(r["router_top1"])[:24], r["query"][:26]))
    print("JSON -> %s" % out)
    if not conservation:
        print("[ROUTEMISS:FAIL] 分母不守恒：sum(states)=%d miss_n=%d hits+miss=%d n=%s"
              % (sum(states.values()), miss_n, int(ev.get("hits") or 0) + miss_n, ev.get("n")))
        return 1
    print("[ROUTEMISS:PASS] miss=%d 归因守恒（stale=%d unregistered=%d real=%d undecidable=%d）"
          % (miss_n, face["stale_n"], face["unregistered_n"], face["real_n"], face["undecidable_n"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
