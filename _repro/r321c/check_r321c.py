# -*- coding: utf-8 -*-
r"""check_r321c.py -- r321c 盲测可跑性取证的自证判据（结构完整性机器闸）。

为什么要有这件：r321c 的结论（verdict + 四个读数）是一份人写的 JSON，人写的东西会虚报。
本件把「这份取证有没有自相矛盾、有没有空壳」变成一条可复跑的判据。
它不复核读数本身（读数复核靠 steps 里逐字命令，每条都能在副本上重跑），
只复核结构：verdict 合法、步骤有命令有 rc 有读数、BLOCKED 必带证据、
非 BLOCKED 必至少有一个真实读数。

用法：
  python -B _repro/r321c/check_r321c.py
  python -B _repro/r321c/check_r321c.py --file 路径   # 负控：指向 OS 临时目录的副本，不落红副本进仓

退出码：0 结构自证通过 / 1 不通过（打印 [R321C:BLIND:FAIL] 与原因）。
末行（通过时）：[R321C:BLIND] verdict=<REACHABLE|PARTIAL|BLOCKED> steps=<n>
"""
import argparse
import hashlib
import io
import json
import os
import sys

SCHEMA = "r321c-blind-feasibility-1"
# 三态是任务书硬规定；DONE/PASS/OK 这类口语态一律判红（负控之一）。
VERDICTS = ("REACHABLE", "PARTIAL", "BLOCKED")
BLOCKER_KINDS = ("needs_eval_write", "needs_external_credential", "hardcoded_face",
                 "runtime_broken", "other")
EMPTY = (None, "", "null")
HERE = os.path.dirname(os.path.abspath(__file__))


def sha12(p):
    """取文件最终字节的 sha256 前 12 位：读数必须绑定被检字节，否则引用会漂。"""
    with io.open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:12]


def fail(why):
    """统一失败出口：打印原因并返回 1，禁「报错却返回 0」的假绿。"""
    print("[R321C:BLIND:FAIL] %s" % why)
    return 1


def check(doc):
    """逐条硬断言；返回 (rc, 已过项)。任一条不过立即 rc=1。"""
    passed = []

    if not isinstance(doc, dict):
        return fail("feasibility 顶层不是对象"), passed
    if doc.get("schema") != SCHEMA:
        return fail("schema 应为 %s，实为 %r" % (SCHEMA, doc.get("schema"))), passed
    passed.append("schema")

    verdict = doc.get("verdict")
    if verdict not in VERDICTS:
        return fail("verdict 必须属三态枚举 %s，实为 %r" % (list(VERDICTS), verdict)), passed
    passed.append("verdict-enum")

    steps = doc.get("steps")
    # 任务书要求：steps 至少 3 条，且每条含非空 cmd 与 rc 与 reading。
    # 非空按 strip 后判（空格不算）；rc 必须是真 int（排除字符串 0 与 null 蒙混）。
    if not isinstance(steps, list) or len(steps) < 3:
        got = "None" if steps is None else (len(steps) if isinstance(steps, list) else type(steps).__name__)
        return fail("steps 需为 >=3 条数组，实为 %s" % got), passed
    for i, s in enumerate(steps):
        if not isinstance(s, dict):
            return fail("steps[%d] 不是对象" % i), passed
        for k in ("n", "cmd", "rc", "reading", "conclusion"):
            if k not in s:
                return fail("steps[%d] 缺字段 %s" % (i, k)), passed
        if not isinstance(s["cmd"], str) or not s["cmd"].strip():
            return fail("steps[%d].cmd 为空或非串（每条步骤必须有逐字命令）" % i), passed
        if not isinstance(s["rc"], int) or isinstance(s["rc"], bool):
            return fail("steps[%d].rc 必须是 int，实为 %r" % (i, s["rc"])), passed
        if not isinstance(s["reading"], str) or not s["reading"].strip():
            return fail("steps[%d].reading 为空：有命令无读数等于没跑成或没记" % i), passed
        if not isinstance(s["conclusion"], str) or not s["conclusion"].strip():
            return fail("steps[%d].conclusion 为空" % i), passed
    passed.append("steps=%d" % len(steps))

    blockers = doc.get("blockers") or []
    if not isinstance(blockers, list):
        return fail("blockers 需为数组"), passed
    for i, b in enumerate(blockers):
        if not isinstance(b, dict) or "step" not in b or "kind" not in b or "evidence" not in b:
            return fail("blockers[%d] 需含 step/kind/evidence 三字段" % i), passed
        if b["kind"] not in BLOCKER_KINDS:
            return fail("blockers[%d].kind 不在枚举 %s，实为 %r" % (i, list(BLOCKER_KINDS), b["kind"])), passed
        if not isinstance(b["evidence"], str) or not b["evidence"].strip():
            return fail("blockers[%d].evidence 为空：卡点必须带命令+rc+stderr摘要" % i), passed

    if verdict == "BLOCKED":
        # 无证据的 BLOCKED 就是放弃：任务书要求 blockers 非空且逐条有 evidence。
        if not blockers:
            return fail("verdict=BLOCKED 但 blockers 为空，必须具名卡点与证据"), passed
        passed.append("blocked-has-evidence")
    else:
        # REACHABLE/PARTIAL 必须至少落地一个真实读数，否则跑通是空话。
        leak_after = doc.get("leak_after")
        quality_now = doc.get("quality_now")
        if leak_after in EMPTY and quality_now in EMPTY:
            return fail("verdict=%s 但 leak_after 与 quality_now 全空：没读数不得判非 BLOCKED" % verdict), passed
        passed.append("has-reading")
        if verdict == "PARTIAL" and not blockers:
            return fail("PARTIAL 必须写明把链路截在哪里的 blockers"), passed
        # 矛盾态：既说运行时坏又报出了读数，二者不可同真。
        if any(b["kind"] == "runtime_broken" for b in blockers) and quality_now not in EMPTY:
            return fail("自相矛盾：kind=runtime_broken 却有 quality_now 读数"), passed
    return 0, passed


def main():
    ap = argparse.ArgumentParser(description="r321c 盲测可跑性取证自证判据")
    ap.add_argument("--file", dest="json_in", default=os.path.join(HERE, "feasibility.json"),
                    help="被检 feasibility.json（负控时指向 OS 临时目录副本，不落红副本进仓）")
    ap.add_argument("--report", dest="report", default=os.path.join(HERE, "report.md"))
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    if not os.path.exists(args.json_in):
        print("[R321C:BLIND:FAIL] 被检件不存在: %s" % args.json_in)
        return 1
    with io.open(args.json_in, encoding="utf-8") as fh:
        doc = json.load(fh)
    rc, passed = check(doc)
    if rc:
        return rc
    print("结构自证通过: %s" % ", ".join(passed))
    # 读数绑定被检字节：打印最终 sha256 前 12 位（report.md 末尾引用同样两值）。
    print("sha256[0:12] feasibility=%s" % sha12(args.json_in))
    if os.path.exists(args.report):
        print("sha256[0:12] report=%s" % sha12(args.report))
    print("leak_before=%s" % doc.get("leak_before"))
    print("leak_after=%s" % doc.get("leak_after"))
    print("quality_now=%s" % doc.get("quality_now"))
    d = doc.get("delta")
    print("delta=%s" % ("(null)" if d in EMPTY else str(d)[:220]))
    nb = doc.get("next_action")
    if doc["verdict"] == "BLOCKED" and (not nb or not str(nb).strip()):
        return fail("BLOCKED 必须写 next_action（下一步要什么权限/动作）")
    print("[R321C:BLIND] verdict=%s steps=%d" % (doc["verdict"], len(doc["steps"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
