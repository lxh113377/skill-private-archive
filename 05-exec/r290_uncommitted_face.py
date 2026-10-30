# -*- coding: utf-8 -*-
"""本轮改过却未提交的跟踪件面（r290 / R290-4）。

为什么存在（一手，r290 我自己造成）：r289 我把「双轴合判」写进 04-plan 维护规范的 5.1 节，并在
r289b 报告里当已落地内容引用、还给了取值命令。那两批提交的 pathspec 没含这个文件，于是在干净
clone 里跑我给的取值命令得 0 命中 —— 报告声称的内容不在仓里，属「工作树绿但发布面缺件」。
更糟的是收尾自查当时报 mine-left: 0：因为自查用的是白名单正则（按文件名），04-plan 不在名单里
⇒ 白名单自查必然漏掉不在名单上的真实未交件。本面把自查换成按内容判：dirty 的跟踪件里，凡**新增
行**含本轮轮号标记者列入嫌疑（那正是「我这一轮动过手但没提交」的形态）。

边界（如实）：工作树是共享的，本面不证明作者，只给线索；处置权在 Lead —— 要么提交要么撤销，
禁止留着不管就收尾。因此它做成读数面 + 内建自证夹具，没有塞进全局门表（他人并发写会让它恒红 =
零判别力的门，见 r287 立的「不测规模不建门」）。
"""
import argparse, io, json, os, re, subprocess, sys, tempfile

MARK_CTX = ["登记", "实测", "校正注", "新增", "一手"]


def git(repo, args):
    r = subprocess.run(["git", "-c", "core.quotepath=false", "-C", repo] + args,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout or ""


def dirty_tracked(repo):
    files = []
    for ln in git(repo, ["status", "--porcelain"]).splitlines():
        if not ln.strip() or ln.startswith("??"):
            continue          # 未跟踪件不算「改过未提交」：多半是不入库素材
        p = ln[3:].strip().replace("\\", "/")
        if os.path.isfile(os.path.join(repo, p)):
            files.append(p)
    return files


def scan(repo, round_no):
    hits = []
    for p in dirty_tracked(repo):
        diff = git(repo, ["diff", "--unified=0", "--", p])
        added = [x[1:].strip() for x in diff.splitlines()
                 if x.startswith("+") and not x.startswith("+++")]
        marked = [x for x in added
                  if ("r%s" % round_no) in x and any(w in x for w in MARK_CTX)]
        if marked:
            hits.append({"file": p, "added_lines": len(added),
                         "marker_lines": len(marked), "sample": marked[0][:120]})
    return hits


def selftest():
    """三腿夹具：一腿必须命中（有牙），两腿必须不命中（不误伤他人、不误命中上下文）。"""
    d = tempfile.mkdtemp(prefix="r290_unc_")
    git(d, ["init", "-q"])
    git(d, ["config", "user.email", "t@t"])
    git(d, ["config", "user.name", "t"])
    for n in ("a.md", "b.md", "c.md"):
        io.open(os.path.join(d, n), "w", encoding="utf-8").write("base line" + chr(10))
    git(d, ["add", "-A"])
    git(d, ["commit", "-qm", "seed"])
    io.open(os.path.join(d, "a.md"), "a", encoding="utf-8").write(
        chr(10) + "新增 5.1 版本压力（r289 实测新增）" + chr(10))
    io.open(os.path.join(d, "b.md"), "a", encoding="utf-8").write(
        chr(10) + "别人这一轮写的东西没有轮号" + chr(10))
    io.open(os.path.join(d, "c.md"), "w", encoding="utf-8").write(
        "base r289 登记的老内容" + chr(10) + chr(10) + "本轮新写但没带轮号" + chr(10))
    git(d, ["add", "c.md"])
    res = scan(d, 289)
    got = set(x["file"] for x in res)
    ok_a = "a.md" in got
    ok_b = "b.md" not in got
    ok_c = "c.md" not in got
    print("[SELFTEST] hit(a must-hit)=%s miss(b must-miss)=%s miss(c must-miss)=%s"
          % (ok_a, ok_b, ok_c))
    print("[SELFTEST] suspects=%s" % sorted(got))
    return 0 if (ok_a and ok_b and ok_c) else 1


def main():
    ap = argparse.ArgumentParser(prog="r290_uncommitted_face.py")
    ap.add_argument("--round", help="本轮轮号，如 290（来自会话，不猜）")
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", dest="js")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.round:
        ap.error("必须给 --round")
    hits = scan(a.root, a.round)
    doc = {"schema": "uncommitted-this-round-v1", "round": a.round,
           "dirty_tracked": len(dirty_tracked(a.root)),
           "suspect_count": len(hits), "suspects": hits,
           "limit_note": "工作树共享：本面不证明作者，只给线索（新增行含本轮轮号 + 处置词）",
           "disposal": "Lead 收尾前逐个提交或撤销；留着就走 = 发布面缺件（r290 实测）"}
    if a.js:
        dd = os.path.dirname(a.js)
        if dd:
            os.makedirs(dd, exist_ok=True)
        io.open(a.js, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1))
    print("[UNCOMMITTED:FACE] round=%s dirty_tracked=%d suspect=%d files=%s"
          % (a.round, doc["dirty_tracked"], len(hits), [x["file"] for x in hits][:6]))
    return 0 if not hits else 2


if __name__ == "__main__":
    sys.exit(main())
