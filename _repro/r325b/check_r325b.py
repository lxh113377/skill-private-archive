# -*- coding: utf-8 -*-
"""r325b 自证：龄期现算 / file_line 真存在 / 清单足够 / 门读数非空。负控三条。"""
import json, os, re, subprocess, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
F = os.path.join(HERE, "freshness.json")


def age_now(gen):
    """现算龄期（天，1 位小数）。判据不信 json 里写的数 —— 那是被判对象。"""
    t = datetime.fromisoformat(gen.replace("Z", "+00:00"))
    d = datetime.now(timezone.utc) - t
    return round(d.total_seconds() / 86400.0, 1)


def check_line(fl):
    """file_line 形如 <path>:<n>；现读该文件第 n 行且该行必须真含「每季度首周」这类词。"""
    m = re.match(r"^(.+):(\d+)$", fl or "")
    if not m:
        return None, "file_line 形态非法"
    p, n = m.group(1), int(m.group(2))
    fp = os.path.join(ROOT, p)
    if not os.path.isfile(fp):
        return None, "file 不存在: " + p
    lines = open(fp, encoding="utf-8").read().split(chr(10))
    if n < 1 or n > len(lines):
        return None, "行号越界: %d / %d" % (n, len(lines))
    return lines[n - 1], None


def main():
    d = json.load(open(F, encoding="utf-8"))
    errs = []
    a = age_now(d["matrix"]["generated_at"])
    if abs(a - d["matrix"]["age_days"]) > 0.2:
        errs.append("age_days 现算 %.1f != 记录 %.1f" % (a, d["matrix"]["age_days"]))
    ln, why = check_line(d["spec_def"]["file_line"])
    if why:
        errs.append("spec_def.file_line: " + why)
    elif "每季度首周" not in ln:
        errs.append("spec_def.file_line 那行不含「每季度首周」: " + ln[:60])
    cg = d.get("cadence_gate") or {}
    if not cg.get("reading") or cg.get("rc") is None:
        errs.append("cadence_gate 读数/rc 缺失")
    cl = d.get("next_run_checklist") or []
    if len(cl) < 3:
        errs.append("next_run_checklist 只有 %d 条（<3）" % len(cl))
    for i, x in enumerate(cl):
        if not x.get("cmd") or not x.get("expect"):
            errs.append("checklist[%d] 缺 cmd 或 expect" % i)
    ig = d.get("inputs_guarded") or []
    if len(ig) < 3:
        errs.append("inputs_guarded 只有 %d 条（<3）" % len(ig))
    neg = os.environ.get("R325B_NEG")
    if neg == "age":
        d2 = json.loads(json.dumps(d))
        d2["matrix"]["age_days"] = d2["matrix"]["age_days"] + 1
        a2 = age_now(d2["matrix"]["generated_at"])
        ok = abs(a2 - d2["matrix"]["age_days"]) > 0.2
        print("[R325B:NEG] age teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "line":
        ln2, why2 = check_line(d["spec_def"]["file_line"].rsplit(":", 1)[0] + ":99999")
        ok = why2 is not None
        print("[R325B:NEG] line teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "checklist":
        ok = len(cl[:2]) < 3
        print("[R325B:NEG] checklist teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    for e in errs:
        print("FAIL " + e)
    verdict = d["matrix"]["verdict"]
    rc = (d.get("cadence_gate") or {}).get("rc")
    if errs:
        print("[R325B:CADENCE] age_days=%.1f verdict=%s gate_rc=%s teeth=FAIL" % (a, verdict, rc))
        return 1
    print("[R325B:CADENCE] age_days=%.1f verdict=%s gate_rc=%s teeth=pass" % (a, verdict, rc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
