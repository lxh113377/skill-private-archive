#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_r323b.py — 自证 r323b/feasibility.json 的三态取证是否真有牙。

判据分两段：
  A) 契约段：verdict 属枚举 / judge_branches>=2 且每条含 file_line+rule /
     BLOCKED 时 blockers 非空且带 evidence / REACHABLE 时 min_change.files>=1。
  B) 牙口段（这一段才让「填个字符串」通不过）：
     · file_line 的路径必须 os.path.isfile —— 写个不存在的路径当场红；
     · rule 必须是该文件该行**逐字**内容 —— 抄错/改写/编造一律红。

为什么 B 段必须存在：A 段任何一条只查「字段在不在」，把 rule 填成 "随便写点" 也能过。
多发的那一轮就是靠「有没有字段」自证，读数与文件无关 —— 那不是判据，是排版检查。

用法:
  python -B check_r323b.py            # 判现盘 feasibility.json，末行给三态
  python -B check_r323b.py --selftest # 四条负控：证明上面两段都会红
"""
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FEAS = os.path.join(HERE, "feasibility.json")
FENJUE = r"C:/Users/37533/Desktop/workspace/焚诀"
VERDICTS = ("REACHABLE", "PARTIAL", "BLOCKED")


def load(path):
    """读 feasibility.json；读不到返回 None（调用方判红，不假装过）。"""
    try:
        return json.loads(io.open(path, encoding="utf-8").read())
    except Exception:
        return None


def split_file_line(spec):
    """把 "eval/x.py:70" 拆成 (相对路径, 行号)；格式不合法返回 (None, None)。"""
    if not isinstance(spec, str) or spec.count(":") != 1:
        return None, None
    rel, _, num = spec.rpartition(":")
    try:
        return rel, int(num)
    except ValueError:
        return None, None


def check_rule_verbatim(entry):
    """牙口：file_line 真实存在 ∧ rule 与该行逐字相同。返回 (ok, 说明)。

    逐字口径 = 两侧 strip 后相等。刻意不留「包含即过」的缝 —— 包含语义下
    填一个该行任意子串就能过，等于把判据还给作者良心的自觉。
    """
    rel, num = split_file_line(entry.get("file_line"))
    if rel is None:
        return False, "file_line 非法（须为 <相对路径>:<行号>）: %r" % (entry.get("file_line"),)
    abs_p = os.path.join(FENJUE, rel)
    if not os.path.isfile(abs_p):
        return False, "file_line 指向不存在的文件: %s" % abs_p
    lines = io.open(abs_p, encoding="utf-8").read().splitlines()
    if num < 1 or num > len(lines):
        return False, "行号越界: %s 只有 %d 行" % (rel, len(lines))
    actual = lines[num - 1].strip()
    claimed = (entry.get("rule") or "").strip()
    if claimed != actual:
        return False, "rule 非逐字（%s:%d 实际 %r / 声称 %r）" % (rel, num, actual[:60], claimed[:60])
    return True, "verbatim %s:%d" % (rel, num)


def run(doc):
    """对一份 feasibility doc 跑 A+B 两段，返回 (是否全过, 失败清单, 统计)。"""
    fails = []
    if not isinstance(doc, dict):
        return False, ["不是 JSON 对象"], {}
    v = doc.get("verdict")
    if v not in VERDICTS:
        fails.append("verdict 不在枚举 %s: %r" % (list(VERDICTS), v))

    jb = doc.get("judge_branches")
    if not isinstance(jb, list):
        fails.append("judge_branches 不是数组")
        jb = []
    if len(jb) < 2:
        fails.append("judge_branches 少于 2 条: %d" % len(jb))
    teeth = 0
    for i, e in enumerate(jb):
        if not isinstance(e, dict):
            fails.append("judge_branches[%d] 不是对象" % i)
            continue
        if not e.get("name"):
            fails.append("judge_branches[%d] 缺 name" % i)
        if not e.get("file_line"):
            fails.append("judge_branches[%d] 缺 file_line" % i)
        if not e.get("rule"):
            fails.append("judge_branches[%d] 缺 rule" % i)
        ok, why = check_rule_verbatim(e)
        if not ok:
            fails.append("judge_branches[%d] %s" % (i, why))
        else:
            teeth += 1

    mc = doc.get("min_change") or {}
    if v == "REACHABLE":
        files = mc.get("files") if isinstance(mc, dict) else None
        if not isinstance(files, int) or files < 1:
            fails.append("REACHABLE 但 min_change.files < 1: %r" % (files,))

    bl = doc.get("blockers")
    if v == "BLOCKED":
        if not isinstance(bl, list) or not bl:
            fails.append("BLOCKED 但 blockers 为空")
        else:
            for i, b in enumerate(bl):
                if not isinstance(b, dict) or not b.get("evidence"):
                    fails.append("blockers[%d] 缺 evidence" % i)

    if not doc.get("testset_schema"):
        fails.append("缺 testset_schema")
    if not isinstance(doc.get("reusable_caps"), list):
        fails.append("reusable_caps 不是数组")
    if not doc.get("old_readings_impact"):
        fails.append("缺 old_readings_impact")

    stats = {"judges": len(jb), "teeth": teeth, "fails": len(fails)}
    return (not fails), fails, stats


def selftest():
    """四条负控 + 一条正控：证明判据红得起来（红不了的判据等于没判据）。"""
    res = []

    def leg(name, fn):
        try:
            got = fn()
        except Exception as e:  # noqa: BLE001
            got = "EXC %s" % e
        res.append((name, got is True))

    base = load(FEAS)
    if base is None:
        print("[R323B:SELFTEST-FAIL] feasibility.json 不可读，负控无从构造")
        return 1
    good, _, _ = run(base)

    # 负控1：verdict 写 "DONE"（枚举外）必须红
    d1 = json.loads(json.dumps(base)); d1["verdict"] = "DONE"
    leg("负控1 · verdict=DONE（枚举外）⇒ 红", lambda: run(d1)[0] is False)

    # 负控2：judge_branches 清空必须红
    d2 = json.loads(json.dumps(base)); d2["judge_branches"] = []
    leg("负控2 · judge_branches=[] ⇒ 红", lambda: run(d2)[0] is False)

    # 负控3：BLOCKED 但 blockers 空必须红
    d3 = json.loads(json.dumps(base)); d3["verdict"] = "BLOCKED"; d3["blockers"] = []
    leg("负控3 · BLOCKED 且 blockers=[] ⇒ 红", lambda: run(d3)[0] is False)

    # 负控4：file_line 指向不存在的路径必须红（os.path.isfile 核一遍）
    d4 = json.loads(json.dumps(base))
    d4["judge_branches"][0]["file_line"] = "eval/no_such_file_r323b_negative_control.py:1"
    leg("负控4 · file_line 指向不存在文件 ⇒ 红", lambda: run(d4)[0] is False)

    # 负控5：rule 被改写（非逐字）必须红 —— 这条挡「填个字符串凑字段」
    d5 = json.loads(json.dumps(base))
    d5["judge_branches"][0]["rule"] = "随便写点"
    leg("负控5 · rule 非逐字 ⇒ 红", lambda: run(d5)[0] is False)

    # 正控：现盘必须绿，否则说明判据本身坏了（比负控更先查）
    leg("正控 · 现盘 feasibility.json ⇒ 绿", lambda: good is True)

    # 负控副本用完即删（本例负控全在内存注入，只留一个磁盘副本做取证）
    fd, tmp = tempfile.mkstemp(prefix="r323b_neg_", suffix=".json")
    os.close(fd)
    try:
        io.open(tmp, "w", encoding="utf-8", newline="\n").write(json.dumps(d4, ensure_ascii=False))
        # 用同一套 run() 读副本，证明「改写 file_line 的落盘副本」同样判红
        copy_doc = load(tmp)
        leg("负控6 · 落盘副本(不存在 file_line) 复跑 ⇒ 红", lambda: run(copy_doc)[0] is False)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    npass = sum(1 for _, ok in res if ok)
    for name, ok in res:
        print("%s %s" % ("[R323B:LEG-PASS]" if ok else "[R323B:LEG-FAIL]", name))
    print("[R323B:SELFTEST] %d/%d 腿通过" % (npass, len(res)))
    return 0 if npass == len(res) else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    doc = load(FEAS)
    if doc is None:
        print("[R323B:MULTILABEL] verdict=UNREADABLE judges=0 teeth=fail")
        return 1
    ok, fails, st = run(doc)
    v = doc.get("verdict")
    for f in fails:
        print("  [FAIL] %s" % f)
    print("[R323B:MULTILABEL] verdict=%s judges=%d teeth=%s"
          % (v, st.get("judges", 0), "pass" if (ok and st.get("teeth", 0) >= 2) else "fail"))
    return 0 if (ok and st.get("teeth", 0) >= 2) else 1


if __name__ == "__main__":
    raise SystemExit(main())