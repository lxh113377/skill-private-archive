#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r307a 执行级 A/B 判定器（件：A-prompt-better 1.3.0 -> 1.5.0）。

口径不自创：五项定义逐字沿用 r285 执行级命令 A/B 件的 caliber_note；
uplift 公式沿用 r281 执行级 A/B 件（分母 = 改前臂；分母 0 时百分比无定义，只能报 not_applicable）。
两模式：five_items（真跑两臂字面命令算五项）/ r281_transfer（腿 B：判 r281 那道题能否外推到本件）。
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys

# r285 caliber_note.commands_found 的 trigger 家族（沿用其列举，不扩不缩）
TRIGGERS = [r"\bpython3?\s", r"\bpy\s+-", r"\bbash\s+scripts", r"\bnpm\s+test",
            r"\bpytest\b", r"\bcargo\s+test", r"\bpip3?\s+install", r"\bnpx\s+", r"\bopen\s+\["]
# r285：查询型（--help / --version / whoami / login）不进分母
QUERY_ONLY = r"(--help|--version|\bwhoami\b|\blogin\b)"


def extract(text):
    """该臂字面命令集：去 inline-code 反引号后逐行匹配 trigger，去重，剔查询型。"""
    clean = text.replace(chr(96), "")
    found = []
    for line in clean.splitlines():
        for pat in TRIGGERS:
            m = re.search(pat + r"[^\n$]*", line)
            if m:
                s = m.group(0).strip()
                if s not in found:
                    found.append(s)
                break
    return [s for s in found if not re.search(QUERY_ONLY, s)]


def snapshot(d):
    """工作区相对路径 -> 字节数，用于 r285 口径 persisted_artifacts。"""
    got = {}
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x != "__pycache__"]
        for f in files:
            p = os.path.join(root, f)
            got[os.path.relpath(p, d).replace(os.sep, "/")] = os.path.getsize(p)
    return got


def run_arm(name, cmds, workdir, pyexe):
    """真跑一臂：跑前清空该臂自己的目录（两臂绝不共享，防 r283 污染）。"""
    d = os.path.join(workdir, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    base = snapshot(d)
    runnable = 0
    rc_zero = 0
    blocked = 0
    rows = []
    for c in cmds:
        # operative_rc：文中的 python 前缀解析成受管解释器（r285 operative_rc 口径）
        # 受管解释器路径含空格，shell=True 下必须加引号，否则被拆成两个 token
        argv = ('"'.join([pyexe]) + c[6:]) if c.startswith("python ") else c
        try:
            p = subprocess.run(argv, shell=True, cwd=d, capture_output=True, text=True, timeout=120)
            rc = p.returncode
        except Exception as e:
            # 工具链缺失：计入 commands_found，永不计入 runnable / rc_zero / artifacts
            rows.append({"cmd": c, "rc": "BLOCKED:" + type(e).__name__})
            blocked += 1
            continue
        runnable += 1
        if rc == 0:
            rc_zero += 1
        rows.append({"cmd": c, "rc": rc, "stdout_bytes": len(p.stdout or "")})
    now = snapshot(d)
    arts = sorted(k for k in now if k not in base)
    return {"commands_found": len(cmds), "runnable": runnable, "blocked_not_runnable": blocked,
            "rc_zero": rc_zero, "persisted_artifacts": len(arts), "artifact_files": arts, "rows": rows}


def doc_claim_count(text):
    """第 5 项前置：文内是否声明了可机械判定的落盘产物（无声明 => 该项 not_computable，不冒充 Y）。"""
    return len(re.findall(r"(写入|产出|落盘|输出到|生成)[^\n]{0,80}?\.(json|md|txt|pdf|png)", text))


def arm_items(r, claim_declared):
    """五项：字面命令集 / 实跑数 / rc=0 / 落盘件数 / 声明兑现。"""
    if not claim_declared:
        claim = "not_computable"
    else:
        claim = "Y" if r["rc_zero"] >= 1 and r["persisted_artifacts"] >= 1 else "N"
    return [r["commands_found"], r["runnable"], r["rc_zero"], r["persisted_artifacts"], claim]


def five_items_mode(a):
    btxt = open(a.before, encoding="utf-8").read()
    atxt = open(a.after, encoding="utf-8").read()
    cb, ca = extract(btxt), extract(atxt)
    rb = run_arm("arm_before", cb, a.workdir, a.py)
    ra = run_arm("arm_after", ca, a.workdir, a.py)
    ib, ia = arm_items(rb, doc_claim_count(btxt) > 0), arm_items(ra, doc_claim_count(atxt) > 0)
    # 五项里可计数的整数项（声明兑现项非整数则不计入 <n>/5）
    # 五项里给出读数的项数：前四项为整数项，第 5 项（声明兑现）非 not_computable 即算给出读数
    numeric = sum(1 for k in range(4) if isinstance(ib[k], int) and isinstance(ia[k], int))
    numeric += 1 if (ib[4] != "not_computable" and ia[4] != "not_computable") else 0
    q_a, q_b = rb["rc_zero"], ra["rc_zero"]
    # r281 公式 uplift=(q_b-q_a)/q_a*100；分母=改前臂=0 时百分比无定义 => not_applicable
    if q_a == 0:
        delta = "not_applicable"
        verdict = "na"
    else:
        delta = "%+.2f%%" % ((q_b - q_a) * 100.0 / q_a)
        verdict = "reported"
    print("BEFORE " + json.dumps(dict(zip(["commands_found", "runnable", "rc_zero",
          "persisted_artifacts", "doc_claim_met"], ib)), sort_keys=True, ensure_ascii=False))
    print("AFTER  " + json.dumps(dict(zip(["commands_found", "runnable", "rc_zero",
          "persisted_artifacts", "doc_claim_met"], ia)), sort_keys=True, ensure_ascii=False))
    print("CMDS_BEFORE " + json.dumps(cb, ensure_ascii=False))
    print("CMDS_AFTER  " + json.dumps(ca, ensure_ascii=False))
    print("SHA12 before=" + hashlib.sha256(btxt.encode("utf-8")).hexdigest()[:12] +
          " after=" + hashlib.sha256(atxt.encode("utf-8")).hexdigest()[:12])
    print("[R307A:AB] method=r281 five_items=%d/5 q_a=%d q_b=%d delta=%s verdict=%s" % (
        numeric, q_a, q_b, delta, verdict))
    return 0


def r281_transfer_mode(a):
    """腿 B：r281 的六维尺锚在那道 dashboard 设计系统题上；题面不同则不外推，报 not_applicable。"""
    ours = open(a.task_file, encoding="utf-8").read().strip()
    theirs = a.rubric_task.strip()
    same = ours == theirs
    print("RUBRIC_TASK_MATCH " + str(same))
    print("OUR_TASK  " + json.dumps(ours, ensure_ascii=False)[:200])
    print("R281_TASK " + json.dumps(theirs, ensure_ascii=False)[:200])
    if not same:
        print("REFUSE reason=rubric_is_task_anchored_and_task_text_differs")
    print("[R307A:AB] method=r281 five_items=0/5 q_a=na q_b=na delta=not_applicable verdict=na")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["five_items", "r281_transfer"])
    ap.add_argument("--before"); ap.add_argument("--after"); ap.add_argument("--workdir")
    ap.add_argument("--py", default=sys.executable)
    ap.add_argument("--task-file"); ap.add_argument("--rubric-task", default="")
    a = ap.parse_args()
    if a.mode == "five_items":
        if not (a.before and a.after and a.workdir):
            print("MISSING_ARG five_items needs before/after/workdir")
            return 2
        return five_items_mode(a)
    if not (a.task_file and a.rubric_task):
        print("MISSING_ARG r281_transfer needs task-file/rubric-task")
        return 2
    return r281_transfer_mode(a)


if __name__ == "__main__":
    sys.exit(main())
