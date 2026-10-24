# -*- coding: utf-8 -*-
# r202_fixture_wiring_face.py - 夹具挂接面（第 78 门）：每个夹具是否真在执行路径上。
#
# 存在理由（r202 一手）：本轮我把重试分流的取证从 TEMP 升级为常驻夹具 r31，写完后顺手核了一句
# 「谁调用 r31」——结果是**没有任何东西调用它**：不在门表、不被任何门件引用、pre-commit 也不跑。
# 也就是说「常驻文件」≠「会被执行」，我上一轮刚批评过 r32「写下靶子却六年没挂门」，这轮发现自己
# 手上就有 7 个同型的孤儿夹具（含我上轮刚写的 19 腿 pages 夹具）。
#
# 判据（纯本地扫描，零网络 ⇒ portable=True，CI 同轮跑）：
#   孤儿 = 文件名含 fixture 的 .py，且 ① 不在门表 script/argv 里 ② 不被任何其它 05-exec 件引用
#   ③ 不在季度巡检登记面里。三条全不满足才算孤儿（宁可漏报不误伤）。
#
# 为什么判红而不是告警：夹具的价值 100% 来自「会被跑」。一条没人执行的夹具比没有更坏 ——
# 它让人以为某个行为被锁住了（本轮的 M3 空锁就是同一机理的变异版）。
#
# 已知设计限制（不是缺陷，件内注明以免后人误挂）：r31 层 b 会 subprocess 跑 run_gates.py 全量，
# 若把 r31 直接挂进门表就是无限递归 ⇒ 它必须先拆出「零成本层 a/c」再挂，或改由 pre-commit 调。
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOKEN = "[WIRING:PASS]"
FIX_RE = re.compile(r"fixture", re.I)
# 既有孤儿夹具的基线（棘轮式：只准减不准增）。理由：直接把 7 条历史债判成永久红，
# 会淹没「新写了个没人跑的夹具」这个真正要拦的信号 —— 本门的价值是防**增量**。
# 基线只减不增：挂接一个就从基线里删一个，删完转全绿。


def load_gate_scripts(run_gates_path):
    import importlib.util as _u
    spec = _u.spec_from_file_location("rg_wiring", run_gates_path)
    m = _u.module_from_spec(spec)
    bak = sys.argv[:]
    sys.argv = ["run_gates.py"]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = bak
    names = set()
    for g in (getattr(m, "GATES", []) or []):
        names.add(g.get("script"))
        for a in (g.get("argv") or []):
            if isinstance(a, str):
                names.add(a)
    return {n for n in names if n}


def registry_blob(path):
    if not os.path.isfile(path):
        return ""
    try:
        return json.dumps(json.load(io.open(path, encoding="utf-8")), ensure_ascii=False)
    except (ValueError, OSError):
        return ""


def find_orphans(exec_dir, gate_scripts, blob):
    fix = [f for f in sorted(os.listdir(exec_dir))
           if f.endswith(".py") and FIX_RE.search(f)]
    texts = {}
    for f in fix + [x for x in sorted(os.listdir(exec_dir)) if x.endswith(".py")]:
        if f not in texts:
            try:
                texts[f] = io.open(os.path.join(exec_dir, f), encoding="utf-8",
                                   errors="replace").read()
            except OSError:
                texts[f] = ""
    orphans, referenced = [], []
    for f in fix:
        if f in gate_scripts:
            continue
        called = any(f in t for k, t in texts.items() if k != f)
        if called:
            referenced.append(f)
            continue
        if f in blob:
            continue
        orphans.append(f)
    return fix, orphans, referenced


def load_baseline(path):
    if not os.path.isfile(path):
        return None
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except (ValueError, OSError):
        return None
    return set(d.get("known_orphans") or [])


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args(argv)
    gate_scripts = load_gate_scripts(os.path.join(HERE, "run_gates.py"))
    blob = registry_blob(os.path.join(ROOT, "06-benchmark",
                                      "gate_reconcile_registry.json"))
    fix, orphans, referenced = find_orphans(HERE, gate_scripts, blob)
    print("=== 夹具挂接面（r202·零网络）===")
    print("  夹具类件 %d ｜门表或引用面覆盖 %d ｜孤儿 %d" % (
        len(fix), len(fix) - len(orphans), len(orphans)))
    bl_path = os.path.join(ROOT, "06-benchmark", "fixture_wiring_baseline.json")
    base = load_baseline(bl_path)
    if base is None:
        print("  [WIRING:UNVERIFIED] 基线件缺失 ⇒ 无法判增量（不得按全绿记，R247）")
        new_ones = []
        known = list(orphans)
    else:
        new_ones = sorted(set(orphans) - base)
        known = sorted(set(orphans) & base)
        healed = sorted(base - set(orphans))
        for f in healed:
            print("  [WIRING:HEALED] %s 已挂上执行路径（基线应同步收缩）" % f)
    for f in known:
        print("  [WIRING:KNOWN] %s 历史孤儿（在基线内，待挂接）" % f)
    for f in new_ones:
        print("  [WIRING:ORPHAN] %s 新增孤儿夹具：不在门表、不被任何门件引用、不在巡检登记面" % f)
    if args.out:
        with io.open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"schema": "fixture-wiring-v1", "readonly": True,
                       "fixtures_total": len(fix), "orphans": orphans,
                       "baseline": sorted(base or []),
                       "new_orphans": new_ones,
                       "referenced_by_peers": referenced,
                       "note": ("常驻文件 != 会被执行。孤儿夹具比没有夹具更坏：它让人以为某行为"
                                "被锁住（本轮 M3 空锁是同一机理的变异版）。"),
                       "provenance_cmd":
                       "python 05-exec/r202_fixture_wiring_face.py --json <件>"},
                      fh, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.out)
    if base is None:
        return 2
    if new_ones:
        return 1
    print("  %s 无新增孤儿夹具（已知历史孤儿 %d 条在基线内，只准减不准增）" % (
        TOKEN, len(known)))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
