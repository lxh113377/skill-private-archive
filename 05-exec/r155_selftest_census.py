# -*- coding: utf-8 -*-
# r155_selftest_census.py -- #48 反向验证普查（静态候选面）。
#
# 存在理由（r155）：#48 立规「反向验证的每一腿必须 ① 写出 want ② 取到 got ③ **机器比对** ④ 不符即非零退出；
#   打印了 want 不算验证」，但当时只治了第 56 门 —— R151-5 明确登记「历轮大量夹具是『打印 want 不看 got』同族形态」。
#   本件把该形态做成**常驻候选面**：静态扫 05-exec/ 下全部自测/夹具件，按三条机器可判的线索出候选清单。
#
# ⚠️ 诚实边界（#32）：本件是**静态启发式**，出的叫**候选**不叫**缺陷证明** ——
#   「没比对」也可能是把期望编码进了断言文本或数据文件。候选的正确处置 = 逐个看一次，或补一次真实比对。
#   凡本件输出候选数 = 0，必须先造一个已知有缺陷的面复跑，确认它报得出来才可信（--selftest 即此腿）。
#
# 三条线索：
#   C1 SUSPECT_NO_TEETH  打印里出现 want/期望，但全文件**零 Compare/Assert 涉及它**（典型的「只打印」）
#   C2 SUSPECT_DEAD_FLAG 定义了 ok/allok/all_ok 一类判定旗，但**除赋值外零引用**（r149 原 bug 形态）
#   C3 SUSPECT_UNWIRED   有判定旗且被引用，但退出路径（sys.exit/SystemExit/return）**不带它**
#
# 用法:
#   python 05-exec/r155_selftest_census.py            # 人读候选表
#   python 05-exec/r155_selftest_census.py --json <件>
#   python 05-exec/r155_selftest_census.py --selftest  # 自证：造已知缺陷面，必须报得出来
# 退出码: 0 面可算 / 1 自证失败 / 2 零输入面（R247）
import argparse
import ast
import io
import json
import os
import re
import shutil
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# 判定旗是**家族**：`ok = fail = 0` 这种同句赋值很常见，退出只要被家族任一成员把守即算接线（r155 二次自抓）。
FLAG_RE = re.compile(r"\b(allok|all_ok|ok|passed|isok|verdict_ok|fail|fails|failed|bad|err|errors|nfail|n_fail)\b")
EXIT_RE = re.compile(r"(sys\.exit|SystemExit|raise SystemExit|^\s*return\b)", re.M)
WANT_RE = re.compile(r"(want|期望|expect)", re.I)


def has_exit(stmts):
    """分支体内是否有退出（return / raise / sys.exit）。"""
    for s in stmts or []:
        for n in ast.walk(s):
            if isinstance(n, (ast.Return, ast.Raise)):
                return True
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "exit":
                return True
    return False


def targets():
    out = []
    for fn in sorted(os.listdir(HERE)):
        if not fn.endswith(".py"):
            continue
        p = os.path.join(HERE, fn)
        try:
            src = io.open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if "_fixtures.py" in fn or "--selftest" in src or "def selftest" in src or "--mutation" in src:
            out.append((fn, src))
    return out


def scan(fn, src):
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return {"file": fn, "verdict": "UNPARSABLE"}
    compares = [ast.unparse(n) for n in ast.walk(tree) if isinstance(n, ast.Compare)]
    asserts = [n for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    lines = src.split("\n")
    want_prints = [l.strip()[:80] for l in lines if "print(" in l and WANT_RE.search(l)]
    want_compare = sum(1 for c in compares if WANT_RE.search(c)) + len(asserts)
    assigned = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    assigned.add(t.id)
    # r155 三次自抓（#32）：判定旗必须是**计数器**（赋 int 常量 或 +=1），不能只是名字撞族。
    #   实测三件假阳：`bad = re.findall(...)`（标记表）/ `bad = [n for ...]`（失败清单）/ `bad = json.loads(...)`（违规样本文档）
    #   —— 它们撞上 ok/bad 家族名却根本不是计数旗。
    counters = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and isinstance(n.value, ast.Constant) \
                        and isinstance(n.value.value, (int, float)) and not isinstance(n.value.value, bool):
                    counters.add(t.id)
        if isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name):
            # r156 第 4 次自抓：`bad += [...]`（列表拼接）曾被当计数器 —— 只有**数值 +=** 才是计数。
            #   实证：r51_retrieval_fixtures.py 的 bad 是失败清单（经 check(not bad) 汇入 RESULTS），
            #   退出实际由 fails 把守 => 候选判错。真缺陷面由 --selftest 死旗腿继续担保。
            if isinstance(n.value, ast.Constant) and isinstance(n.value.value, (int, float)) \
                    and not isinstance(n.value.value, bool):
                counters.add(n.target.id)
    flags = sorted(x for x in counters if FLAG_RE.fullmatch(x))
    dead, wired = [], []
    for f in flags:
        uses = len(re.findall(r"\b%s\b" % re.escape(f), src))
        if uses <= 1:
            dead.append(f)
            continue
        # r155 自抓（#32）：初版按「退出那一行是否含判定旗」判接线 => 把 `if ok == n: return 0`
        #   这种形态（判定在 If 测试里、旗不在 return 行）全判死旗，实测 6 件误报（含 r150_gov_fixtures.py）。
        #   正解 = AST：If 测试含该旗 且 分支体内有退出 => 视为已接线。
        in_line = any(f in l for l in lines if EXIT_RE.search(l))
        guarded = False
        for n in ast.walk(tree):
            if isinstance(n, ast.If):
                names = set(x.id for x in ast.walk(n.test) if isinstance(x, ast.Name))
                if f in names and (has_exit(n.body) or has_exit(n.orelse)):
                    guarded = True
                    break
        if in_line or guarded:
            wired.append(f)
        else:
            dead.append(f)
    # r155 二次自抓（#32）：家族任一成员把守退出 => 整体算接线；其余成员降级为 redundant（冗余计数），不算缺陷。
    #   反例实测：r29_rubric_calibre_fixtures.py 的 `return 0 if fail == 0 else 1` 由 fail 把守，
    #   ok 只是冗余计数 => 初版报「死旗 ok」是假阳。
    redundant = []
    if wired:
        redundant = list(dead)
        dead = []
    # 弱信号（advisory）：族名变量出现在 If 测试里、分支无退出，但它**不是计数器** => 名字撞车高发，只当线索。
    weak = []
    for n in ast.walk(tree):
        if isinstance(n, ast.If):
            nm = set(x.id for x in ast.walk(n.test) if isinstance(x, ast.Name))
            fam = sorted(x for x in nm if FLAG_RE.fullmatch(x) and x not in counters)
            if fam and not has_exit(n.body):
                weak.extend(fam)
    weak = sorted(set(weak))
    verdict = "OK"
    why = []
    if want_prints and want_compare == 0:
        verdict = "SUSPECT_NO_TEETH"
        why.append("打印 want %d 处但零比对" % len(want_prints))
    elif dead:
        verdict = "SUSPECT_DEAD_FLAG"
        why.append("判定旗仅赋值未引用：%s" % ",".join(dead))
    elif flags and not wired:
        verdict = "SUSPECT_UNWIRED"
        why.append("退出路径不带判定旗：%s" % ",".join(flags))
    return {"file": fn, "verdict": verdict, "why": why, "asserts": len(asserts),
            "want_prints_n": len(want_prints), "want_compare_n": want_compare,
            "flags": flags, "dead_flags": dead, "wired_flags": wired, "redundant_flags": redundant,
            "weak_signals": weak,
            "sample": want_prints[0] if want_prints else ""}


def build():
    rows = [scan(fn, src) for fn, src in targets()]
    cand = [r for r in rows if r["verdict"].startswith("SUSPECT")]
    return {"schema": "fj-selftest-census-v1", "files_n": len(rows), "rows": rows,
            "candidates": cand,
            "summary": {"files_n": len(rows),
                        "ok_n": sum(1 for r in rows if r["verdict"] == "OK"),
                        "cand_n": len(cand),
                        "no_teeth_n": sum(1 for r in rows if r["verdict"] == "SUSPECT_NO_TEETH"),
                        "dead_flag_n": sum(1 for r in rows if r["verdict"] == "SUSPECT_DEAD_FLAG"),
                        "unwired_n": sum(1 for r in rows if r["verdict"] == "SUSPECT_UNWIRED"),
                        "weak_total": sum(len(r.get("weak_signals") or []) for r in rows),
                        "unparsable_n": sum(1 for r in rows if r["verdict"] == "UNPARSABLE")}}


def selftest():
    tmp = tempfile.mkdtemp(prefix="census_")
    try:
        bad = os.path.join(tmp, "bad_fixtures.py")
        io.open(bad, "w", encoding="utf-8", newline="\n").write(
            "import sys\nwant = 3\nprint(\"want=3\")\nsys.exit(0)\n")
        good = os.path.join(tmp, "good_fixtures.py")
        io.open(good, "w", encoding="utf-8", newline="\n").write(
            "import sys\nwant = 3\ngot = 3\nprint(\"want=3 got=3\")\n"
            "assert want == got\nsys.exit(0 if want == got else 1)\n")
        dead = os.path.join(tmp, "dead_fixtures.py")
        io.open(dead, "w", encoding="utf-8", newline="\n").write(
            "import sys\nok = 1\nprint(\"total=%d\" % ok)\nsys.exit(0)\n")
        b = scan("bad_fixtures.py", io.open(bad, encoding="utf-8").read())
        d = scan("dead_fixtures.py", io.open(dead, encoding="utf-8").read())
        g = scan("good_fixtures.py", io.open(good, encoding="utf-8").read())
        print("[CENSUS] 自证 无齿面=%s（应 SUSPECT_NO_TEETH）｜死旗面=%s（应 SUSPECT_DEAD_FLAG）｜对照=%s（应 OK）"
              % (b["verdict"], d["verdict"], g["verdict"]))
        ok = (b["verdict"] == "SUSPECT_NO_TEETH" and d["verdict"] == "SUSPECT_DEAD_FLAG"
              and g["verdict"] == "OK")
        print("[CENSUS:SELFTEST-PASS]" if ok else "[CENSUS:SELFTEST-FAIL]")
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    doc = build()
    s = doc["summary"]
    if s["files_n"] == 0:
        print("[CENSUS:UNVERIFIED] 零自测件入面 => 面不对，禁按干净记（R247）")
        return 2
    print("[CENSUS] 自测/夹具件 %d 件｜OK %d｜候选 %d（无齿 %d / 死旗 %d / 未接线 %d）｜不可解析 %d"
          % (s["files_n"], s["ok_n"], s["cand_n"], s["no_teeth_n"], s["dead_flag_n"],
             s["unwired_n"], s["unparsable_n"]))
    for r in doc["candidates"]:
        print("  %-18s %-38s %s" % (r["verdict"], r["file"][:38], "; ".join(r["why"])[:60]))
    print("[CENSUS] 弱信号（族名撞车、非计数器，advisory）%d 处" % s.get("weak_total", 0))
    for r in doc["rows"]:
        if r.get("weak_signals"):
            print("  %-18s %-38s weak=%s" % ("(advisory)", r["file"][:38], ",".join(r["weak_signals"])))
    print("[CENSUS:PASS] 静态候选面可算（候选是线索不是判决 —— 处置=逐个复核或补比对，#32）")
    if args.out:
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print("[CENSUS] 留痕 %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
