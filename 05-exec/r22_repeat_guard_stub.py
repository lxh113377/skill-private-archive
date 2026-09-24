# -*- coding: utf-8 -*-
"""r22_repeat_guard_stub.py - 层a 纯函数桩：_repeat_guard_row() 五场景 + 层b 接线对照说明。

判据 = A-project-handoff V3.53.0 新增的 savepoint「重复轮次闸门」行。
退出码 0=全过 / 1=有失败。产物建在受管根之外（本仓 _tmp 目录）。
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SP_DIR = Path(r"D:/global_skills/A-project-handoff/scripts")
sys.path.insert(0, str(SP_DIR))

results = []


def check(name, got, want):
    ok = got == want
    results.append(ok)
    print("  %-46s %s" % (name, "PASS" if ok else "FAIL got=%r want=%r" % (got, want)))


def mk(tmp, lines=None, raw=None):
    d = Path(tmp) / "memory"
    (d / "sessions").mkdir(parents=True, exist_ok=True)
    if raw is not None:
        (d / "sessions" / "repeat-guard.jsonl").write_text(raw, encoding="utf-8")
    elif lines is not None:
        (d / "sessions" / "repeat-guard.jsonl").write_text(
            "\n".join(json.dumps(x, ensure_ascii=False) for x in lines) + "\n", encoding="utf-8")
    return d


try:
    from handoff_lib.savepoint import _repeat_guard_row
except Exception as e:
    print("IMPORT_FAIL:", e)
    raise SystemExit(2)

tmp = tempfile.mkdtemp(prefix="r22stub_")
try:
    print("=== 层a 纯函数桩 ===")
    # 1 反例：无台账 → None（静默，不报错、不编造判定）
    d1 = Path(tmp) / "p1"
    (d1 / "sessions").mkdir(parents=True)
    check("1 无台账 -> None（防噪音反例）", _repeat_guard_row(d1), None)

    # 2 生效：DUPLICATE → warn，含轮次与行数
    d2 = mk(Path(tmp) / "p2", [{"verdict": "DUPLICATE",
                                "commits": {"rounds": 5, "insertions_by_rounds": 10466},
                                "same_day_sessions": ["a", "b"], "forked": True}])
    r2 = _repeat_guard_row(d2)
    check("2 DUPLICATE -> warn", r2[0], "warn")
    check("2a 文案含轮次=5", "轮次=5" in r2[1], True)
    check("2b 文案含分叉警示", "分叉" in r2[1], True)
    check("2c session 计数=2", "session=2" in r2[1], True)

    # 3 混合行格式：注释/空行/坏 JSON 夹在中间，末条可解析行生效（last-wins）
    d3 = mk(Path(tmp) / "p3", raw='not-json-line\n\n{"verdict": "FRESH", "commits": {"rounds": 0}}\n### 手工留痕行\n')
    r3 = _repeat_guard_row(d3)
    check("3 混合行末条可解析生效", (r3[0], "轮次=0" in r3[1]), ("ok", True))

    # 4 FRESH 且无分叉 → ok 而非 warn
    d4 = mk(Path(tmp) / "p4", [{"verdict": "FRESH", "commits": {"rounds": 1}, "forked": False}])
    check("4 FRESH -> ok", _repeat_guard_row(d4)[0], "ok")

    # 5 有文件但无 verdict 键 → None（不猜）
    d5 = mk(Path(tmp) / "p5", [{"ts": "2026-09-24", "note": "no verdict"}])
    check("5 缺 verdict -> None", _repeat_guard_row(d5), None)

    print("\n=== 层b 接线对照（生效侧：本仓真跑 review）===")
    print("  注：原判据文字写的是「savepoint 增加预检行」，实跑证明正确落点是 cmd_review——")
    print("      与既有两条台账行（AC 收敛 flow --verify-ac / 记忆评测 memory_eval_run）同处一个报告函数。")
    env = dict(**{"PYTHONPYCACHEPREFIX": "/tmp/pycache2"})
    p = subprocess.run([sys.executable, str(SP_DIR / "handoff.py"), "review",
                        str(Path.cwd())], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=420)
    out = (p.stdout or "") + (p.stderr or "")
    hit = [l.strip() for l in out.splitlines() if "重复轮次闸门" in l]
    print("  review rc=%s；闸门行数=%d" % (p.returncode, len(hit)))
    for h in hit:
        print("   ", h[:150])
    results.append(len(hit) >= 1)
    check("b 接线生效：review 输出含闸门行", len(hit) >= 1, True)
    print("  反例侧说明：不在他人项目真跑 savepoint（会重写对方 AGENTS.md 并可能自动提交，属 R269 禁面），"
          "「无台账→静默」由层a 第 1 例覆盖。")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

n, f = len(results), results.count(False)
print("\n合计 %d 项，失败 %d" % (n, f))
print("[GATE:stub-pass]" if f == 0 else "[GATE:stub-fail]")
raise SystemExit(0 if f == 0 else 1)
