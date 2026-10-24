# -*- coding: utf-8 -*-
"""r210_autopush_fixtures.py — 第 87 门 push_autopush_face 的双向取证件（W-47）。

存在理由：r205 建门时只交了真仓证据，没有隔离夹具；r210 修订 P4（判当前提交而非留痕末行）
时补上。三条腿 + 一条变异腿：
  f1 正例：留痕末行 rc=0 ⇒ PASS
  f2 反例：留痕末行 head==HEAD 且 rc!=0 ⇒ FAIL（真失败，牙齿必须保留）
  f3 反例（r210 新增的假阳性面）：留痕末行 head!=HEAD 且 rc!=0，
     但 HEAD 已是 origin/main 祖先 ⇒ 必须 PASS 并带 TRACE_STALE 注
     （旧实现在这里假红：并行会话的 head 失败一次、手工推成功不留痕）
  f4 反例：留痕末行 head!=HEAD、rc!=0、且 HEAD 不在 origin/main ⇒ FAIL
     （真有一个提交没推上去 —— 本门存在的理由）
  m1 变异：把「head 不同 ⇒ 查 remote-tracking」这段摘掉（回到只看末行 rc）
     ⇒ f3 必须转红（证明该腿承重）
全部在临时仓里跑，不碰真仓（DSH_AUTOPUSH_ROOT 指向临时仓）。
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "r205_push_autopush_face.py")
RESULTS = []

HOOK_BODY = (
    "#!/bin/sh\n"
    "# post-commit 自动推送（夹具桩，非真推送）\n"
    "printf 'ts=%s rc=0 head=%s\\n' \"$(date +%Y-%m-%dT%H:%M:%S)\" \"$(git rev-parse HEAD)\" "
    ">> \"$GIT_DIR/autopush.log\"\n"
    "git push --quiet origin HEAD || true\n"
)


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, str(detail)))
    print("%-4s %s%s" % ("PASS" if cond else "FAIL", name,
                          "" if cond else "  <-- " + str(detail)[:220]))


def sh(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", shell=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def build_repo(tmp, last_line, head_pushed):
    """造一个最小 git 仓：钩子 + autopush.log 末行 + origin/main tracking ref。"""
    sh("git init -q .", tmp)
    sh("git config user.email t@t", tmp)
    sh("git config user.name t", tmp)
    sh("git checkout -q -b main", tmp)
    with io.open(os.path.join(tmp, "a.txt"), "w", encoding="utf-8") as f:
        f.write("x")
    sh("git add a.txt", tmp)
    sh("git commit -q -m init", tmp)
    head = sh("git rev-parse HEAD", tmp)[1].strip()
    # 钩子（自动推送形态）—— git init 在部分形态下不预建 hooks 目录，先确保存在
    os.makedirs(os.path.join(tmp, ".git", "hooks"), exist_ok=True)
    hp = os.path.join(tmp, ".git", "hooks", "post-commit")
    with io.open(hp, "w", encoding="utf-8", newline="") as f:
        f.write(HOOK_BODY)
    # 留痕
    with io.open(os.path.join(tmp, ".git", "autopush.log"), "w",
                 encoding="utf-8", newline="") as f:
        # 留痕时间必须**新于**最近一次提交，否则 P5（留痕旧于提交 ⇒ 没触发）会盖过
        # 本夹具要测的 P4 分支。用固定未来时间戳，与提交时刻无关、可复算。
        f.write("ts=2099-01-01T00:00:00 rc=0 head=oldbeef\n")
        f.write(last_line.replace("__HEAD__", head).replace("2026-10-25T01:00:00",
                                                             "2099-01-01T00:01:00") + "\n")
    # origin/main tracking ref
    if head_pushed:
        sh("git update-ref refs/remotes/origin/main " + head, tmp)
    else:
        sh("git update-ref refs/remotes/origin/main deadbeef" + "0" * 32, tmp)
    return head


def run_gate(tmp):
    env = dict(os.environ, DSH_AUTOPUSH_ROOT=tmp)
    p = subprocess.run([sys.executable, GATE], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env, cwd=HERE)
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, out


def case(name, last_line, head_pushed, expect_rc0, expect_note=None):
    tmp = tempfile.mkdtemp(prefix="r210_ap_")
    try:
        build_repo(tmp, last_line, head_pushed)
        rc, out = run_gate(tmp)
        ok = (rc == 0) if expect_rc0 else (rc != 0)
        if expect_note:
            ok = ok and (expect_note in out)
        ck(name, ok, "rc=%s out=%s" % (rc, out.strip().splitlines()[-1][:120] if out.strip() else ""))
        return rc, out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if not os.path.isfile(GATE):
        ck("前置：门脚本存在", False, GATE)
        return 1

    # f1 正例：末行 rc=0
    case("f1 正例：留痕末行 rc=0 ⇒ PASS",
         "ts=2026-10-25T01:00:00 rc=0 head=__HEAD__", True, True)

    # f2 反例：末行就是当前 HEAD 且失败 ⇒ 真失败必须红
    case("f2 反例：末行 head==HEAD 且 rc!=0 ⇒ FAIL（真失败）",
         "ts=2026-10-25T01:00:00 rc=128 head=__HEAD__", False, False)

    # f3 r210 假阳性面：末行是别的 head 的失败，但当前 HEAD 已推 ⇒ PASS + TRACE_STALE
    case("f3 反例（r210 假阳性）：末行 head!=HEAD 且 rc!=0，但 HEAD 已推 ⇒ PASS+TRACE_STALE",
         "ts=2026-10-25T01:00:00 rc=128 head=other01", True, True, "TRACE_STALE")

    # f4 反例：末行是别的 head 的失败，且当前 HEAD 没推 ⇒ FAIL
    case("f4 反例：末行 head!=HEAD 且 rc!=0，HEAD 也不在 origin/main ⇒ FAIL",
         "ts=2026-10-25T01:00:00 rc=128 head=other01", False, False)

    # m1 变异：回到「只看末行 rc」的旧实现 ⇒ f3 必须转红
    src = io.open(GATE, encoding="utf-8").read()
    anchor = '    _head = str(last.get("head") or "")'
    if anchor not in src:
        ck("m1 变异锚点存在", False, "anchor missing")
    else:
        # 变异必须复现**旧实现**（只看末行 rc、不看 head）：把三态分支换成旧的一行判定。
        mutated = src.replace(
            '    if rc_last == 0:\n        print("     PASS P4 末次推送 rc=0")',
            '    if rc_last == 0:\n        print("     PASS P4 末次推送 rc=0")\n'
            '    if rc_last != 0:\n'
            '        fails.append("P4 末次推送 rc=%d（旧实现：只看末行 rc）" % rc_last)\n'
            '        print("     FAIL P4 末次推送 rc=%d（旧实现）" % rc_last)')
        backup = src
        try:
            with io.open(GATE, "w", encoding="utf-8", newline="") as f:
                f.write(mutated)
            rc, out = run_gate_case_f3()
            ck("m1 变异：摘掉 head 判别后 f3 假阳性必须复现（证明该腿承重）", rc != 0,
               "rc=%s out=%s" % (rc, out.strip().splitlines()[-1][:120] if out.strip() else ""))
        finally:
            with io.open(GATE, "w", encoding="utf-8", newline="") as f:
                f.write(backup)

    ok = sum(1 for r in RESULTS if r[0])
    total = len(RESULTS)
    print("\n夹具合计: %d 项，通过 %d，失败 %d" % (total, ok, total - ok))
    print("[GATE:fixture-fail]" if total != ok else "[GATE:fixture-pass]")
    return 0 if total == ok else 1


def run_gate_case_f3():
    tmp = tempfile.mkdtemp(prefix="r210_ap_m1_")
    try:
        build_repo(tmp, "ts=2026-10-25T01:00:00 rc=128 head=other01", True)
        return run_gate(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
