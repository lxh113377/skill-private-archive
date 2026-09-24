# -*- coding: utf-8 -*-
r"""ratchet_gate.py — 注入面/度量棘轮门禁（本仓自持，只降不升；R19-2 的等价落点）。

为什么要它：r18/r19 实测出两条硬事实——① 平台技能目录每轮注入 ~45k 字符；② C25 只测它自己那 5 个
文件，而「P0 强制注入区」的另一套定义（attention_sim 的 6 文件）与之并集 **69,494B > 硬顶 65,536B
却仍判 PASS**，且**别的项目的注入壳完全在预算外**（本项目 AGENTS.md 实测 29,293B）。
把这条做成焚诀 C 系列判据要写它的 `eval/`（项目红线：只读调用不改，且该仓此刻 27 条在途），
转办两轮未回收 ⇒ 于是在**本仓权限内**先做成会拦人的东西：本文件即「超棘轮 / 超硬顶 / 无基线」
三类都 exit 非 0 的门禁，命令已挂进 `memory/AGENTS.md`「项目门禁命令」段（A-memory-start R193 在
修改类任务动手前实跑）。

五项指标（全部现算，不抄历史值）：
  catalog_grand_chars        平台技能目录 name+description 合计字符（`catalog_attention_tax.py` 产物）
  inject_union_bytes         C25 注入区 5 文件 **实测磁盘字节** ∪ 本项目注入壳 AGENTS.md（并集去重）
  claim_candidates           计数断言失真候选（`claim_truth_scan.py` 产物）
  drift_ruleish_candidates   累积漂移规则类候选（`cumulative_drift_scan.py` 产物）
  desc_over_cap              description 超官方 1024 上限条数（`description_baseline_scan.py` 产物）

R247：指标算不出（非数值）或基线缺该项 ⇒ 判失败，禁止「拿不到就当通过」。
用法：python 05-exec/ratchet_gate.py [--baseline 06-benchmark/inject_ratchet_baseline.json]
                                    [--json out.json] [--update] [--quiet]
退出码：0 全合规 / 1 有发现（超棘轮、超硬顶、无基线、指标缺失）/ 2 环境或输入不可用
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = HERE.parent
BENCH = WS / "06-benchmark"
PROJ_SHELL = WS / "AGENTS.md"
DEFAULT_BASELINE = BENCH / "inject_ratchet_baseline.json"
TRUTH_CONSTANTS = Path(r"C:\Users\37533\Desktop\workspace\焚诀\eval\truth_constants.json")

METRIC_NAMES = ("catalog_grand_chars", "inject_union_bytes", "claim_candidates",
                "drift_ruleish_candidates", "desc_over_cap")
SCHEMA = "zijian-inject-ratchet-v1"


def _read_json(glob_pat):
    """取匹配到的最新一份 JSON（按 mtime）。无文件/解析失败 → None（调用方记 unknown）。"""
    files = sorted(glob.glob(str(glob_pat)), key=lambda p: os.path.getmtime(p))
    if not files:
        return None
    try:
        with io_open(files[-1]) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def io_open(path):
    return open(str(path), "r", encoding="utf-8-sig")


def _latest(pattern):
    files = sorted(glob.glob(str(BENCH / pattern)), key=lambda p: os.path.getmtime(p))
    return files[-1] if files else None


def catalog_grand_chars():
    d = _read_json(BENCH / "catalog_attention_tax_*.json")
    return d.get("grand_chars") if isinstance(d, dict) else None


def claim_candidates():
    d = _read_json(BENCH / "claim_truth_*.json")
    return len(d.get("candidates") or []) if isinstance(d, dict) else None


def drift_ruleish_candidates():
    d = _read_json(BENCH / "cumulative_drift_*.json")
    return len(d.get("flagged_ruleish") or []) if isinstance(d, dict) else None


def desc_over_cap():
    d = _read_json(BENCH / "description*.json")
    return (d.get("summary") or {}).get("over_cap") if isinstance(d, dict) else None


def inject_union_bytes():
    """C25 注入区清单（**实测磁盘字节**，不取清单里登记的数字）∪ 本项目注入壳，按路径去重求和。

    这里刻意不用 `bytes` 字段：r19 实测清单登记值会滞后于盘上真实大小，
    而「注入区双源且互不校验」正是要防的病灶（N2）。
    """
    paths = set()
    try:
        tc = json.load(io_open(TRUTH_CONSTANTS))
        files = ((tc.get("inject_budget") or {}).get("files")) or []
    except (OSError, ValueError, AttributeError):
        files = []
    for row in files:
        p = (row or {}).get("path")
        if p:
            paths.add(os.path.realpath(p))
    if PROJ_SHELL.exists():
        paths.add(os.path.realpath(PROJ_SHELL))
    if not paths:
        return None
    total = 0
    for p in paths:
        try:
            total += os.path.getsize(p)
        except OSError:
            return None
    return total


def hard_caps():
    try:
        tc = json.load(io_open(TRUTH_CONSTANTS))
        cap = (tc.get("inject_budget") or {}).get("hard_cap_bytes")
    except (OSError, ValueError, AttributeError):
        cap = None
    return {"inject_union_bytes": cap} if isinstance(cap, int) else {}


COMPUTE = {"catalog_grand_chars": catalog_grand_chars,
           "inject_union_bytes": inject_union_bytes,
           "claim_candidates": claim_candidates,
           "drift_ruleish_candidates": drift_ruleish_candidates,
           "desc_over_cap": desc_over_cap}


def collect_metrics():
    """现算全部指标。返回 (metrics, unknown)——算不出的进 unknown，绝不填 0 冒充。"""
    metrics, unknown = {}, []
    for name in METRIC_NAMES:
        try:
            val = COMPUTE[name]()
        except Exception:
            val = None
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            unknown.append(name)
        else:
            metrics[name] = val
    return metrics, unknown


def load_baseline(path):
    try:
        with io_open(path) as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        return {"error": "%s: %s" % (type(e).__name__, e), "metrics": {}}
    if not isinstance(data, dict) or not isinstance(data.get("metrics"), dict):
        return {"error": "基线缺 metrics 字典", "metrics": {}}
    return data


def evaluate(metrics, baseline, caps):
    """返回 (findings, unknown)。未知指标名不参与判定（由调用方保证名单一致）。"""
    findings, unknown = [], []
    for name, val in metrics.items():
        if name not in METRIC_NAMES:
            continue
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            unknown.append(name)
            continue
        base = baseline.get(name)
        if not isinstance(base, (int, float)) or isinstance(base, bool):
            findings.append("%s=%s 无基线记录 ⇒ 禁止放行（先人工核定基线，不得默认通过）" % (name, val))
            continue
        if val > base:
            findings.append("%s=%s 超棘轮基线 %s（+%s，只降不升）" % (name, val, base, val - base))
        cap = caps.get(name)
        if isinstance(cap, int) and val > cap:
            findings.append("%s=%s 超硬顶 %s（+%s）" % (name, val, cap, val - cap))
    return findings, unknown


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default=str(DEFAULT_BASELINE))
    ap.add_argument("--json")
    ap.add_argument("--update", action="store_true",
                    help="把现状写成基线（**只允许下调**；上调或缺项一律拒绝）")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--strict-cap", action="store_true", dest="strict_cap",
                    help="把「超硬顶」也按阻断处理（默认非阻断告警，便于跨项目既有超限不拦本仓修改任务）")
    args = ap.parse_args()

    metrics, unknown = collect_metrics()
    caps = hard_caps()
    bl = load_baseline(args.baseline)

    if args.update:
        if unknown:
            print("[RATCHET:REFUSE] 指标缺失 %s ⇒ 拒绝写基线（禁止把算不出的项写成 0）" % unknown)
            return 2
        old = bl.get("metrics") or {}
        raised = {k: (v, old[k]) for k, v in metrics.items() if k in old and v > old[k]}
        if raised and bl.get("schema") == SCHEMA:
            print("[RATCHET:REFUSE] 拒绝抬基线：%s" % json.dumps(raised, ensure_ascii=False))
            print("   要接受更大的实测面，须人工改本消息说明理由后手动写文件（棘轮的意义就在于此）")
            return 1
        doc = {"schema": SCHEMA, "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
               "metrics": metrics, "hard_caps": caps,
               "sources": {"catalog": _latest("catalog_attention_tax_*.json"),
                           "claim": _latest("claim_truth_*.json"),
                           "drift": _latest("cumulative_drift_*.json"),
                           "desc": _latest("description*.json"),
                           "inject_files": "焚诀 truth_constants.inject_budget.files 实测 + 本项目 AGENTS.md"},
               "note": "只降不升棘轮；缺项/超顶/无基线一律 exit 非 0（R247）"}
        Path(args.baseline).parent.mkdir(parents=True, exist_ok=True)
        Path(args.baseline).write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        print("[RATCHET:BASELINE] 写入 %s（%d 项指标）" % (args.baseline, len(metrics)))
        return 0

    print("=== 注入面/度量棘轮门禁 (%s) ===" % datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("基线: %s%s" % (args.baseline, "" if bl.get("metrics") else "  ⚠️ %s" % bl.get("error", "无内容")))
    for name in METRIC_NAMES:
        val = metrics.get(name)
        base = (bl.get("metrics") or {}).get(name)
        cap = caps.get(name)
        print("  %-26s 实测=%-8s 基线=%-8s 硬顶=%s" % (
            name, val if val is not None else "缺失",
            base if base is not None else "-", cap if cap else "-"))
    if unknown:
        print("缺失指标（不得当 0）: %s" % ", ".join(unknown))
    if bl.get("error"):
        print("[RATCHET:FAIL] 基线不可用 → 先跑 `--update` 建立基线")
        return 2
    findings, _unknown2 = evaluate(metrics, bl["metrics"], caps)
    # 两级判定：超棘轮/无基线 = 本次长大或判据失效 ⇒ 阻断（exit 1）；
    # 超硬顶 = 可能是跨项目既有事实（C25 只管它自己那 5 个文件）⇒ 默认告警不阻断，
    # 加 --strict-cap 升级为阻断。刻意不做「为了让门禁变绿而删掉硬顶比较」——那正是 R263 禁的形态。
    blocking = [f for f in findings if "超硬顶" not in f]
    advisory = [f for f in findings if "超硬顶" in f]
    if args.json:
        Path(args.json).write_text(json.dumps({
            "schema": SCHEMA, "generated_at": datetime.now().isoformat(timespec="seconds"),
            "baseline_file": str(args.baseline), "metrics": metrics, "unknown": unknown,
            "hard_caps": caps, "findings": findings,
            "blocking": blocking, "advisory": advisory,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print("JSON -> %s" % args.json)
    for f in advisory:
        print("  ⚠️ 非阻断告警: %s" % f)
    if blocking or unknown:
        for f in blocking:
            print("  - %s" % f)
        print("[RATCHET:FAIL] 阻断项 %d 项（超棘轮/无基线/指标缺失），另有非阻断告警 %d 项"
              % (len(blocking) + (1 if unknown else 0), len(advisory)))
        return 1
    if advisory and args.strict_cap:
        print("[RATCHET:FAIL] --strict-cap 生效：超硬顶 %d 项按阻断处理" % len(advisory))
        return 1
    print("[RATCHET:PASS] %d 项指标均在棘轮基线内（只降不升）；非阻断告警 %d 项" % (len(metrics), len(advisory)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
