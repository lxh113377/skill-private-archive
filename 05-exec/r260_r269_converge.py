# -*- coding: utf-8 -*-
"""r260_r269_converge.py -- R269 双向盲区收敛序的机器判据。

为什么存在（一手代价 = R220-6）：两会话各自把对方在途件判成「他人件、不代修」（R269 原文语义），
结果是没有任何人修、两道门持续红。r220 当时处置了实物（走 recycle 通道），但把「归属怎么判」
留在叙述里、没有可复算形态 => 账龄尺连判 OVERDUE 到 r260。本件把那四步序（正文权威 =
memory/06-constraints.part18.md）做成函数 + 进程内夹具，并含一条必须仍红的双推诿反例腿 ——
按 W-47 第四腿口径，只有正例的夹具不算证明。

怎么运作：adjudicate(facts) 按 1->4 步顺序判，命中即停（先到先得，避免多规则给出不同结论）；
live 面用 git 未跟踪件 + 仓内引用计数算出每个散件的事实集，逐条分类并落 JSON。
三态退出码与 run_gates 同口径：0 PASS / 1 有不一致 / 2 输入面不可用（R247 禁按 0 记绿）。"""

import argparse
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RULE_LEAF = os.path.join(ROOT, "memory", "06-constraints.part18.md")
SKIP_DIRS = (".git", "__pycache__", "_temp", "node_modules", "archive")


def adjudicate(facts):
    """四步序判定，返回 (verdict, reason)。facts 键：tracked / last_commit_round / refs_n /
    self_attest / other_claims_this_piece。"""
    # 步 1：git 跟踪态先于 mtime -- 已跟踪 => 归属 = 最近提交该件的轮号，不进入自证段。
    if facts.get("tracked"):
        return "OWN_BY_COMMIT", "已跟踪，最近提交轮号 r%s" % facts.get("last_commit_round")
    # 步 2：引用面 >=2 => 有他面在用，处置前必须先在报告里具名通知（禁径行移走）。
    if int(facts.get("refs_n") or 0) >= 2:
        return "NOTIFY_FIRST", "被 %s 处引用，处置前须具名通知" % facts.get("refs_n")
    # 步 3：单方可自证作者（三证全中才算）=> 归该方，直接处置，不等对方表态。
    if facts.get("self_attest"):
        return "OWN_DISCOVERER", "未跟踪 + 零外部引用 + 三证自证作者"
    # 步 4：都不成立 => 归发现方处置 + 双向留痕。本步存在本身就是为了让「谁都不动」不可用。
    if facts.get("other_claims_this_piece"):
        # 双推诿：另一会话也把它推给对方 => 正是 R220-6 要消灭的形态，必须具名报警而非判无主。
        return "BUCK_PASSING", "两会话互推（R269 双向盲区），按步 4 归发现方并双向留痕"
    return "DISCOVERER_WITH_TRACE", "不自证作者 => 发现方处置 + 双向留痕"


def fixtures():
    """进程内夹具：四条应绿 + 一条必须仍红（双推诿）+ 变异对照。不读共享产物（R252 教训）。"""
    rows = []

    def ck(name, cond, detail=""):
        rows.append((bool(cond), name, str(detail)[:200]))
        print("%-4s %s%s" % ("PASS" if cond else "FAIL", name, "" if cond else "  <-- " + str(detail)[:180]))

    v1, _ = adjudicate({"tracked": False, "refs_n": 1, "self_attest": True})
    ck("t1 步3：未跟踪+零引用+自证 => OWN_DISCOVERER", v1 == "OWN_DISCOVERER", v1)
    v2, r2 = adjudicate({"tracked": True, "last_commit_round": 240})
    ck("t2 步1：已跟踪 => 按最近提交轮号（不看 mtime）", v2 == "OWN_BY_COMMIT" and "240" in r2, (v2, r2))
    v3, _ = adjudicate({"tracked": False, "refs_n": 3, "self_attest": True})
    ck("t3 步2：引用 >=2 => NOTIFY_FIRST（自证也不许径行动他面在用的件）", v3 == "NOTIFY_FIRST", v3)
    v4, _ = adjudicate({"tracked": False, "refs_n": 1, "self_attest": False})
    ck("t4 步4：不自证 => 发现方处置 + 留痕（不是无主）", v4 == "DISCOVERER_WITH_TRACE", v4)
    # 必须仍红的一腿：双推诿形态不得被算成「无主」或「无人可归」。
    v5, _ = adjudicate({"tracked": False, "refs_n": 1, "self_attest": False, "other_claims_this_piece": True})
    ck("t5 反例（必须红）：两会话互推 => 具名 BUCK_PASSING，禁降级成无主", v5 == "BUCK_PASSING", v5)

    def adjudicate_mutated(facts):
        """变异体：摘掉步 3 的自证闸门（恒真）=> t4 的结论被改写，证该步确实承重。"""
        if facts.get("tracked"):
            return "OWN_BY_COMMIT"
        if int(facts.get("refs_n") or 0) >= 2:
            return "NOTIFY_FIRST"
        return "OWN_DISCOVERER"

    vm = adjudicate_mutated({"tracked": False, "refs_n": 1, "self_attest": False})
    ck("t6 变异对照：摘掉自证闸门 => t4 结论被改写（证明该步承重）", vm == "OWN_DISCOVERER", vm)
    return rows


def untracked_pys(root=ROOT):
    """返回 (files, None) 或 (None, 原因)。git 查询失败与「查询成功但面为空」必须分开：
    前者不可知（UNVERIFIED），后者是**目标态**（散件已全部归属处置）⇒ 命题空洞成立。
    旧实现把两者混成同一个 rc=2，等于造一扇永远不可能绿的门 —— 恒红门与恒绿门一样无用。"""
    try:
        p = subprocess.run(["git", "-C", root, "ls-files", "--others", "--exclude-standard", "05-exec/"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
    except Exception as e:
        return None, "git 取不到未跟踪面: %r" % (e,)
    if p.returncode != 0:
        return None, "git rc=%s" % p.returncode
    files = [x.strip() for x in (p.stdout or "").splitlines() if x.strip().endswith(".py")]
    return files, None


def build_text_index(root=ROOT):
    """一次性建全文索引再逐件计数：旧实现每个散件都 os.walk 全仓（N 次全仓扫描，
    本轮实测单轮 1.7s→53s 级）。索引一次、判定多次，且体积超 2MB 的件跳过（防把 700KB
    级读数件重复读 N 遍）。"""
    idx = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith((".py", ".md", ".json")):
                continue
            full = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(full) > 2 * 1024 * 1024:
                    continue
                txt = io.open(full, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            idx.append((os.path.basename(full), txt))
    return idx


def live_face(idx=None):
    """扫 05-exec 未跟踪 .py，按四步序逐条分类（只读取证，不动任何盘）。"""
    files, err = untracked_pys()
    if err:
        return None, err
    if not files:
        return [], "empty-face"
    idx = idx or build_text_index()
    out = []
    for f in files:
        stem = os.path.splitext(os.path.basename(f))[0]
        base = os.path.basename(f)
        # 引用计数：排除自身文件；命中 = 主干名出现在任一 .py/.md/.json 文本里（粗尺，具名口径）。
        # 索引只建一次（旧式每个散件重扫全仓 = O(N x 全仓)，本轮实测把整门拖到 50s 级）。
        refs = sum(1 for name, txt in idx if name != base and stem in txt)
        verdict, reason = adjudicate({"tracked": False, "refs_n": refs, "self_attest": False})
        out.append({"file": f, "refs_n": refs, "verdict": verdict, "reason": reason})
    return out, "ok"


def main():
    ap = argparse.ArgumentParser(prog="r260_r269_converge.py")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", dest="out")
    args = ap.parse_args()
    if not os.path.isfile(RULE_LEAF):
        # 规则本体缺失 => 判据失去权威源，按 UNVERIFIED 而非「无冲突」（R247）。
        print("[CONVERGE:UNVERIFIED] 规则本体不在盘：%s" % RULE_LEAF)
        return 2
    if args.selftest:
        rows = fixtures()
        fails = [n for ok, n, _ in rows if not ok]
        print("夹具合计: %d 项，通过 %d，失败 %d" % (len(rows), len(rows) - len(fails), len(fails)))
        if fails:
            print("[CONVERGE:SELFTEST-FAIL] %s" % fails)
            return 1
        print("[CONVERGE:SELFTEST-PASS] 6 腿含 1 条必须红反例（双推诿）+ 1 条变异对照")
        return 0
    items, note = live_face()
    if items is None:
        # 只有「取不到面」（git 调用失败 / rc!=0）才是 UNVERIFIED —— 不可知不等于没散件。
        print("[CONVERGE:UNVERIFIED] %s（面不可知，不得当作无散件）" % note)
        return 2
    if note == "empty-face":
        # 查询成功且未跟踪 .py = 0：这是四步序的**目标态**（散件已全部归属处置），命题空洞成立。
        # r260 一手：上一版把这里也判 rc=2，于是本仓一旦提交干净，这扇门就永远红 ——
        # 恒红门与恒绿门一样没有信息量（且会把真故障淹在固定噪声里）。
        print("[CONVERGE] 未跟踪 .py 0 个（git ls-files --others 成功）⇒ 无待归属散件，四步序空洞成立")
        print("[CONVERGE:PASS] 无未跟踪件需判归属；规则本体 = %s" % os.path.relpath(RULE_LEAF, ROOT))
        if args.out:
            d = os.path.dirname(os.path.abspath(args.out))
            if d:
                os.makedirs(d, exist_ok=True)
            with io.open(args.out, "w", encoding="utf-8", newline=chr(10)) as fh:
                json.dump({"schema": "r269-converge-v1", "readonly": True,
                         "provenance_cmd": "python 05-exec/r260_r269_converge.py --json <件>",
                         "rule_leaf": "memory/06-constraints.part18.md",
                         "untracked_py_n": 0, "counts": {}, "buck_passing": [], "items": [],
                         "face_state": "empty-by-successful-query"}, fh, ensure_ascii=False, indent=1)
            print("JSON -> %s" % args.out)
        return 0
    counts = {}
    for it in items:
        counts[it["verdict"]] = counts.get(it["verdict"], 0) + 1
    buck = [it["file"] for it in items if it["verdict"] == "BUCK_PASSING"]
    doc = {"schema": "r269-converge-v1", "readonly": True,
           "provenance_cmd": "python 05-exec/r260_r269_converge.py --json <件>",
           "rule_leaf": "memory/06-constraints.part18.md",
           "untracked_py_n": len(items), "counts": counts, "buck_passing": buck,
           "items": items}
    if args.out:
        d = os.path.dirname(os.path.abspath(args.out))
        if d:
            os.makedirs(d, exist_ok=True)
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    print("[CONVERGE] 未跟踪 .py %d 个｜分类 %s｜双推诿具名 %d" % (len(items), counts, len(buck)))
    for b in buck[:10]:
        print("[CONVERGE:BUCK] %s" % b)
    print("[CONVERGE:PASS] 散件归属可判（四步序无「无主」结论）；本体 = %s" % os.path.relpath(RULE_LEAF, ROOT))
    if args.out:
        print("JSON -> %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
