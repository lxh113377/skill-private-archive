# -*- coding: utf-8 -*-
"""
r339 提交面机械门（R338-3 兑现）：提交信息「声称的内容」与「该笔实际入库内容」对账。

为什么必须有（一手 6 次同族：r321 五次 + r338 一次写「见提交面 DECOMPOSE.md」而那笔没该文件）：
附二 §6 的「先数后写」是人肉纪律，被违反 6 次就说明它该机械化。

  C1 计数对账：信息含「本笔 N 个条目」⇒ N 必须 == 该笔 show --name-only 实际文件数，否则 RED。
  C2 声称路径对账：±30 字内出现声称动词的仓内路径必须在该笔清单内，缺 ⇒ RED（r338 形态）。
  C3 普通提及（无声称动词）⇒ advisory，不判红（引用没改动的件是常态；全判红=恒红门，r260 教训）。
外部路径（D:/、C:/、http、焚诀/）永不进 C2。信息无「本笔 N」声明 ⇒ C1 记 N/A（没声明不可对账，
不判绿也不判红）。零输入（无提交 / git 不可用）⇒ rc=2 UNVERIFIED（R247）。

正则刻意不用反斜杠转义（[0-9]/[ ] 形态 + 直接写 CJK 字面），避免中文 Windows 下的引号与转义双坑。
"""
import argparse, io, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = r"C:/Program Files/Git/bin/git.exe"

PATH_PAT = ("(?:0[0-9]-[a-z]+|_repro|_temp|memory|archive|docs)/"
            "[A-Za-z0-9_一-鿿./-]+"
            "|DECOMPOSE.md|README.md|AGENTS.md")
PATH_RE = re.compile(PATH_PAT)
EXT_PAT = "^(?:[A-Za-z]:/|https?://|焚诀/)"
EXT_RE = re.compile(EXT_PAT, re.IGNORECASE)
CLAIM_RE = re.compile("本笔 *[（(]* *([0-9]+)")
CLAIM_VERBS = ["卡先落", "见提交面", "入库", "落盘", "已落", "并入", "新增件", "常驻", "写进",
               "接进", "入门表", "已建", "补链落盘", "已写入", "落地", "登册", "迁"]
WINDOW = 30


def git(*args):
    r = subprocess.run([GIT, "-c", "core.quotepath=false", "-C", ROOT] + list(args),
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=60)
    if r.returncode != 0:
        return None
    return (r.stdout or "").strip()


def check_rev(rev):
    """对一笔提交做对账，返回结构体（取不到 ⇒ None ⇒ UNVERIFIED）。"""
    msg = git("show", "-s", "--format=%B", rev)
    files_s = git("show", "--name-only", "--format=", "-1", rev)
    if msg is None or files_s is None:
        return None
    files = set(x.strip().replace(chr(92), "/") for x in files_s.splitlines() if x.strip())
    res = {"rev": rev, "declared": None, "actual": len(files), "c1": None,
           "c2_red": [], "c3_advisory": [], "c4_red": []}
    m = CLAIM_RE.search(msg)
    if m:
        # 声明数 = 捕获组里的数字（括号形态可能带全角，用 findall 取首个纯数字）
        digits = "".join(ch for ch in m.group(1) if ch.isdigit()) or "0"
        res["declared"] = int(digits)
        res["c1"] = "ok" if res["declared"] == res["actual"] else "MISMATCH declared=%d actual=%d" % (res["declared"], res["actual"])
    for line in msg.splitlines():
        for mm in PATH_RE.finditer(line):
            p = mm.group(0).strip("`")
            norm = p[2:] if p.startswith("./") else p
            if norm in files:
                continue
            if EXT_RE.search(norm):
                res["c3_advisory"].append({"path": p, "why": "external"})
                continue
            lo = max(0, mm.start() - WINDOW)
            hi = min(len(line), mm.end() + WINDOW)
            near = line[lo:hi]
            verb = next((v for v in CLAIM_VERBS if v in near), None)
            if verb:
                res["c2_red"].append({"path": p, "verb": verb, "line": line.strip()[:120]})
            else:
                res["c3_advisory"].append({"path": p, "why": "mention_no_claim"})
    # C4（r339 补，一手：r338 那次不实句在**报告正文**而非提交信息，C2 抓不到）：
    #    该笔内每个 .md 的 blob 若声称「卡先落/先落卡」，则 DECOMPOSE.md 必须在同一笔里。
    #    已知 FP 形态（如实记）：同一轮把卡放在更早一笔、报告放本笔 ⇒ 本腿会误红；
    #    协议上卡与本笔同交（本轮即如此），FP 时报告须改写「卡先落于 <rev>」并具名，不许静默豁免。
    if "DECOMPOSE.md" not in files:
        for fp in sorted(files):
            if not fp.endswith(".md"):
                continue
            # 恒红防线（r260 教训，本轮实测抓到）：memory/ 与 archive/ 是**历史容器**，
            # 「卡先落」作为 R318-2 规则名以引文形态常驻其中 ⇒ 纳入 C4 会让每一笔碰台账的提交
            # 都红（新门自造恒红）。C4 只评「本轮自述文书」= 04-plan/ 与 06-benchmark/。
            if fp.startswith("memory/") or fp.startswith("archive/"):
                continue
            blob = git("show", "%s:%s" % (rev, fp))
            if blob is None:
                continue
            for claim in ("卡先落", "先落卡"):
                if claim in blob:
                    ln = next((i + 1 for i, x in enumerate(blob.splitlines()) if claim in x), 0)
                    res.setdefault("c4_red", []).append({"file": fp, "claim": claim, "line": ln})
                    break
    return res


def verdict_of(res):
    """RED = C1 明确不符 或 C2 非空；取不到 = UNVERIFIED；其余 GREEN。"""
    if res is None:
        return "UNVERIFIED"
    if res["c1"] not in (None, "ok"):
        return "RED"
    if res["c2_red"] or res.get("c4_red"):
        return "RED"
    return "GREEN"


def selftest():
    """夹具即负控：期望红的必须红、期望绿的必须绿、期望 N/A 的不得被当绿证据。"""
    mk = lambda d, a, c2=None: {"rev": "x", "declared": d, "actual": a,
                                "c1": (None if d is None else ("ok" if d == a else "MISMATCH",)),
                                "c2_red": c2 or [], "c3_advisory": [],
                                }
    cases = []
    def v(d, a, c2=None):
        r = mk(d, a, c2)
        r["c1"] = None if d is None else ("ok" if d == a else "MISMATCH")
        return verdict_of(r)
    cases.append(("t1 C1 声明5实际3 ⇒ RED", v(5, 3) == "RED"))
    cases.append(("t2 C1 声明5实际5 ⇒ GREEN", v(5, 5) == "GREEN"))
    cases.append(("t3 无声明 ⇒ 不判红(N/A)", v(None, 7) == "GREEN"))
    cases.append(("t4 C2 非空 ⇒ RED", v(1, 1, [{"path": "DECOMPOSE.md"}]) == "RED"))
    line = "本笔 1 个条目。卡先落（见提交面 DECOMPOSE.md）"
    hits = [x.group(0) for x in PATH_RE.finditer(line)]
    cases.append(("t5 r338 形态文本命中 DECOMPOSE.md", "DECOMPOSE.md" in hits))
    cases.append(("t6 该行含声称动词", any(x in line for x in CLAIM_VERBS)))
    cases.append(("t7 D:/ 判外部", bool(EXT_RE.search("D:/x/y.py"))))
    cases.append(("t8 焚诀/ 判外部", bool(EXT_RE.search("焚诀/eval/a.json"))))
    cases.append(("t9 零输入 ⇒ UNVERIFIED", verdict_of(None) == "UNVERIFIED"))
    m2 = CLAIM_RE.search("本笔 18 个条目（commit 前现数 = 18）")
    cases.append(("t10 声明数可提取且=18", bool(m2) and m2.group(1).strip() == "18"))
    r4 = mk(1, 1)
    r4["c4_red"] = [{"file": "06-benchmark/x.md", "claim": "卡先落", "line": 3}]
    cases.append(("t11 C4 非空 ⇒ RED", verdict_of(r4) == "RED"))
    n = 0
    for name, ok in cases:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
        n += 1 if ok else 0
    print("[R339:SELFTEST] %d/%d %s" % (n, len(cases), "teeth=pass" if n == len(cases) else "teeth=FAIL"))
    return 0 if n == len(cases) else 1


def main():
    ap = argparse.ArgumentParser(description="提交面机械门：信息声称 vs 该笔实际内容")
    ap.add_argument("--rev", default="", help="只查指定一笔")
    ap.add_argument("--replay", type=int, default=1, help="对最近 N 笔逐笔对账")
    ap.add_argument("--json", dest="out", default="", help="证据件输出路径")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.rev:
        revs = [a.rev]
    else:
        log_s = git("rev-list", "--max-count=%d" % max(1, a.replay), "HEAD")
        if not log_s:
            print("[R339:COMMITFACE] rc=2 UNVERIFIED rev-list 取不到（无提交或 git 不可用，R247）")
            return 2
        revs = log_s.splitlines()
    docs, any_red, unver = [], False, []
    for rv in revs:
        res = check_rev(rv)
        if res is None:
            unver.append(rv[:10])
            continue
        vd = verdict_of(res)
        docs.append(dict(res, verdict=vd))
        subj = git("show", "-s", "--format=%s", rv) or rv
        print("%-12s %-11s declared=%s actual=%d c2=%d c3=%d  %s" % (
            rv[:10], vd, res["declared"], res["actual"], len(res["c2_red"]),
            len(res["c3_advisory"]), subj[:60]))
        for x in res.get("c4_red", []):
            print("    C4-RED %s L%d 声称「%s」但本笔无 DECOMPOSE.md" % (x["file"], x["line"], x["claim"]))
        for x in res["c2_red"]:
            print("    C2-RED 声称 %s（动词:%s）不在该笔 :: %s" % (x["path"], x.get("verb", "?"), x.get("line", "")[:90]))
        if res["c1"] not in (None, "ok"):
            print("    C1-RED %s" % res["c1"])
        if vd == "RED":
            any_red = True
    if a.out:
        payload = {"schema": "r339-commit-face-1", "replay": a.replay, "revs": docs,
                   "unverified": unver}
        io.open(a.out, "w", encoding="utf-8", newline="\n").write(json.dumps(payload, ensure_ascii=False, indent=1))
    if unver and not docs:
        print("[R339:COMMITFACE] rc=2 UNVERIFIED 全部取不到")
        return 2
    print("[R339:COMMITFACE] revs=%d red=%s unver=%d" % (len(docs), any_red, len(unver)))
    return 1 if any_red else 0


if __name__ == "__main__":
    sys.exit(main())
