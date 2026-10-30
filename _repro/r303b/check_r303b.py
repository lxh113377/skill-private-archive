#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""R303b swap-pack checker.

Why: R303b must show that "a ref exists" is NOT the same as "the ref is valid".
How: (1) load swap_pack.json and re-resolve every increment upstream_ref against the
upstream SKILL.md fetched from the candidate repo, checking BOTH line bounds AND the
anchor token; (2) recompute the git blob sha of each fetched upstream file and compare
with the blob sha recorded from the GitHub API; (3) require local_only >= 1 (leg A,
anti one-way beautification); (4) inject two synthetic increments (a line past EOF and a
valid line with a wrong anchor) and assert the SAME validator returns UNVERIFIED (leg B,
anti fabricated increment).
"""
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(HERE, "swap_pack.json")
UPDIR = os.path.join(HERE, "upstream")

RE_REF = re.compile(r"^(?P<repo>[^:]+):(?P<path>\S+)\s+L(?P<a>\d+)(?:-(?P<b>\d+))?$")


def read_text(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def git_blob_sha(path):
    # git blob id = sha1 of b"blob <len>\x00<bytes>"; lets us cross-check the GitHub API sha.
    with open(path, "rb") as f:
        data = f.read()
    h = hashlib.sha1()
    h.update(("blob %d" % len(data)).encode("utf-8") + b"\x00" + data)
    return h.hexdigest()


def upstream_path(repo):
    # the two candidate artifacts were fetched by gh api into upstream/<name>.SKILL.md
    name = repo.split("/")[-1]
    cand = os.path.join(UPDIR, name + ".SKILL.md")
    return cand if os.path.isfile(cand) else None


def check_ref(ref, anchor):
    m = RE_REF.match(ref)
    if not m:
        return "UNVERIFIED", "ref not parseable: " + ref
    repo = m.group("repo")
    a = int(m.group("a"))
    b = int(m.group("b")) if m.group("b") else a
    if b < a:
        return "UNVERIFIED", "line range inverted"
    fp = upstream_path(repo)
    if fp is None:
        return "UNVERIFIED", "upstream artifact not on disk for " + repo
    lines = read_text(fp).splitlines()
    if b > len(lines):
        return "UNVERIFIED", "line " + str(b) + " beyond EOF " + str(len(lines))
    window = "\n".join(lines[a - 1:b])
    if anchor and anchor not in window:
        return "UNVERIFIED", "anchor absent from cited window"
    return "VERIFIED", "lines " + str(a) + "-" + str(b) + " of " + str(len(lines))


def main():
    # r303 提升边界（我提升到跟踪面后实测）：本判据要重放上游原文，而 _repro/*/upstream/ 被 .gitignore 命中
    # （既有 r291 规矩：部分上游快照的内部相对链会让死链门判红 ⇒ 不入库）。因此**克隆态**下这两份原文不在盘。
    # 三态纪律（本仓 PASS/FAIL/UNVERIFIED）：缺原文 ⇒ 必须报 UNVERIFIED 并 rc=2，禁用 rc=1 配一行像 PASS 的末行
    # —— 那会让读的人分不清「判据不通过」与「判据没材料可判」。
    _need = [os.path.join(UPDIR, n) for n in ("prompt-master.SKILL.md", "taste-skill.SKILL.md")]
    _miss = [p for p in _need if not os.path.isfile(p)]
    if _miss:
        print("[R303:SWAP] UNVERIFIED 上游原文副本不在盘（缺 %d 份；_repro/*/upstream/ 被 .gitignore 命中，"
              "属既有 r291 规矩）=> 本判据需先在写面用 gh api 重建副本，或改在写面目录内跑" % len(_miss))
        # 必须**直接退出**：本件的入口是 rc = <独立算出的判定> + sys.exit(rc)，main() 的返回值被忽略
        # （我第一版写 return 2 ⇒ 实测 rc 仍是 0，等于「报了 UNVERIFIED 却按通过退出」）。
        sys.exit(2)
    with io.open(PACK, encoding="utf-8") as f:
        pack = json.load(f)
    print("pack keys: " + str(sorted(pack.keys())))
    print("skill keys: " + str(sorted(pack["skills"][0].keys())))
    print("increment keys: " + str(sorted(pack["increments"][0].keys())))
    print("local_only keys: " + str(sorted(pack["local_only"][0].keys())))
    print("unknown keys: " + str(sorted(pack["unknown"][0].keys())))
    rc = 0
    # blob-sha cross-check: recorded GitHub blob sha vs locally recomputed git blob id
    sha_bad = 0
    for s in pack["skills"]:
        for c in s["candidates"]:
            fp = upstream_path(c["repo"])
            if fp is None:
                print("[SHA:UNVERIFIED] " + c["repo"] + " | upstream artifact not on disk")
                sha_bad += 1
                continue
            got = git_blob_sha(fp)
            if got == c["upstream_blob_sha"]:
                print("[SHA:VERIFIED] " + c["repo"] + " | blob " + got)
            else:
                print("[SHA:UNVERIFIED] " + c["repo"] + " | recorded=" + str(c["upstream_blob_sha"]) + " recomputed=" + got)
                sha_bad += 1
    if sha_bad:
        rc = 1
    # increment ref validity
    incs = pack["increments"]
    ok = 0
    bad = 0
    for it in incs:
        state, detail = check_ref(it["upstream_ref"], it.get("anchor", ""))
        if state == "VERIFIED":
            ok += 1
        else:
            bad += 1
        print("[INC:" + state + "] " + it["skill"] + " | " + it["upstream_ref"] + " | " + detail)
    if bad:
        rc = 1
    # leg A: anti one-way beautification -- local_only must not be empty
    lo = pack["local_only"]
    leg_a = "PASS" if len(lo) >= 1 else "FAIL"
    if leg_a == "FAIL":
        rc = 1
    print("[LEGA:" + leg_a + "] local_only=" + str(len(lo)))
    for it in lo:
        print("  local_only " + it["skill"] + " | " + it["local_ref"] + " | " + it["capability"][:60])
    # leg B: anti fabricated increment -- the same validator must reject bad refs
    probe1 = {"skill": "NEGCTRL", "upstream_ref": "nidhinjs/prompt-master:SKILL.md L99999", "anchor": "Mixture of Experts"}
    probe2 = {"skill": "NEGCTRL", "upstream_ref": "nidhinjs/prompt-master:SKILL.md L442", "anchor": "no-such-anchor-token-xyz"}
    st1, d1 = check_ref(probe1["upstream_ref"], probe1["anchor"])
    st2, d2 = check_ref(probe2["upstream_ref"], probe2["anchor"])
    leg_b = "PASS" if (st1 == "UNVERIFIED" and st2 == "UNVERIFIED") else "FAIL"
    if leg_b == "FAIL":
        rc = 1
    print("[LEGB:" + leg_b + "] ref-past-EOF -> " + st1 + " (" + d1 + ")")
    print("[LEGB:" + leg_b + "] valid-line-bad-anchor -> " + st2 + " (" + d2 + ")")
    ns = len(pack["skills"])
    nc = sum(len(s["candidates"]) for s in pack["skills"])
    ni = len(incs)
    nl = len(lo)
    nu = len(pack["unknown"])
    print("[R303:SWAP] skills=%d candidates=%d increments=%d local_only=%d unknown=%d" % (ns, nc, ni, nl, nu))
    sys.exit(rc)


if __name__ == "__main__":
    main()
