# -*- coding: utf-8 -*-
"""r327 自证：M1 两条承重断言 + 回滚锚解引用口径 + L1 通道在位。三条负控。"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GIT = r"C:/Program Files/Git/bin/git.exe"
PY = sys.executable
OUT = os.path.join(HERE, "m1_gate_recheck.json")
ANCHOR_TAG = "r259"
ANCHOR_COMMIT = "9e33cce4cf111ab6c296b7fdbbb79707993e32a0"
WANT_COUNTS = {"LOCAL_AHEAD_KEEP": 13, "UNVERIFIED": 17, "UPGRADE_REVIEW": 10}
TARGETS = ["test-driven-development", "obsidian-bases", "hyperframes-registry"]


def git(*args):
    r = subprocess.run([GIT, "-C", ROOT] + list(args), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120)
    return (r.stdout or "").strip(), r.returncode


def main():
    d = json.load(open(OUT, encoding="utf-8"))
    errs = []
    if d.get("counts") != WANT_COUNTS:
        errs.append("counts 不匹配: %s" % d.get("counts"))
    rows = d.get("rows") or []
    if sum(d["counts"].values()) != len(rows):
        errs.append("守恒破: sum=%d len(rows)=%d" % (sum(d["counts"].values()), len(rows)))
    verdicts = {}
    for x in rows:
        s = x.get("slug") or x.get("skill")
        if s in TARGETS:
            verdicts[s] = x.get("verdict") or x.get("state")
    ob = verdicts.get("obsidian-bases")
    if not ob:
        errs.append("obsidian-bases 不在 rows 里")
    elif ob.startswith("UPGRADE"):
        errs.append("obsidian-bases 回退成 %s" % ob)
    commit, rc1 = git("rev-list", "-n", "1", ANCHOR_TAG)
    if rc1 != 0 or commit != ANCHOR_COMMIT:
        errs.append("锚解引用不符: %s（期望 %s）" % (commit[:12], ANCHOR_COMMIT[:12]))
    l1 = os.path.join(ROOT, "05-exec", "r260_drill", "l1b.sh")
    if not os.path.isfile(l1):
        errs.append("L1 通道 l1b.sh 缺失")
    neg = os.environ.get("R327_NEG")
    if neg == "anchor":
        raw, _ = git("rev-parse", ANCHOR_TAG)
        ok = (raw != ANCHOR_COMMIT)
        print("[R327:NEG] anchor teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "counts":
        ok = ({"LOCAL_AHEAD_KEEP": 13, "UNVERIFIED": 17, "UPGRADE_REVIEW": 11} != WANT_COUNTS)
        print("[R327:NEG] counts teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "obsidian":
        ok = bool(ob) and not ob.startswith("UPGRADE")
        print("[R327:NEG] obsidian teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    for e in errs:
        print("FAIL " + e)
    if errs:
        print("[R327:M1] counts=RED anchor=RED teeth=FAIL")
        return 1
    print("[R327:M1] counts=13/17/10 sum=40 anchor=" + commit[:12] + " obsidian=" + ob + " teeth=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
