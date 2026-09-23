#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""R272 独立复验（层 b'：端到端 CLI 接线验证）—— 证明「函数对」且「真的被 review 调用」。

R238 的核心教训：只过隔离桩 = 未验证（函数对、输入集合/接线可能错）。
本脚本走**真实 CLI**（`handoff.py review <合成项目>`），断言输出里真的出现 R272 告警行；
并跑一个「无漂移」合成项目作为**反例**，要求其不出现 R272 行（防线未被放松成「永不报警」）。

安全：合成项目建在系统临时目录，全程不触碰任何受管根。
"""
import os
import shutil
import subprocess
import sys
import tempfile

HANDOFF = r"D:\global_skills\A-project-handoff\scripts\handoff.py"
PY = sys.executable

BINDING = """# AGENTS.md — 测试项目绑定表

## Skill 强制绑定（命中即加载）

| 触发条件 | 必加载 skill |
|---------|-------------|
| 任何项目修改操作 | A-project-handoff |
"""

DRIFT_MAIN = """# 07 - 下一步

## P0 — 必须做

- [ ] 阶段1 补跑三脚本
"""
DRIFT_VOL = """# 07-next-steps.part1.md

- [x] 阶段1 补跑三脚本
"""

CLEAN_MAIN = """# 07 - 下一步

## P0 — 必须做

- [ ] 阶段1 补跑三脚本
"""
CLEAN_VOL = """# 07-next-steps.part1.md

- [x] 另一件已完成的事
"""


def make_project(root, main_txt, vol_txt):
    mem = root / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "07-next-steps.md").write_text(main_txt, encoding="utf-8")
    (mem / "07-next-steps.part1.md").write_text(vol_txt, encoding="utf-8")
    (mem / "AGENTS.md").write_text(BINDING, encoding="utf-8")
    (mem / "01-goal.md").write_text("# 01 - 目标\n\n测试目标\n", encoding="utf-8")
    (mem / "05-feature-status.md").write_text("# 05 - 功能状态\n\n## ✅ 已完成\n\n- 测试条目\n", encoding="utf-8")


def review(path):
    r = subprocess.run([PY, HANDOFF, "review", str(path)],
                       capture_output=True, text=True, encoding="utf-8", timeout=120)
    return (r.stdout or "") + (r.stderr or "")


def main():
    fails = []
    base = tempfile.mkdtemp(prefix="r272_e2e_")
    try:
        # 生效路径：有漂移 → 必须报 R272
        p1 = os.path.join(base, "drift")
        os.makedirs(p1, exist_ok=True)
        from pathlib import Path
        make_project(Path(p1), DRIFT_MAIN, DRIFT_VOL)
        out1 = review(p1)
        hit1 = "R272" in out1 and "主卷↔分卷漂移" in out1
        print("=" * 68)
        print("层 b' 端到端接线验证（真实 CLI: handoff.py review）")
        print("=" * 68)
        print(f"  [{'PASS' if hit1 else 'FAIL'}] 生效路径（合成漂移项目）→ 期望出现 R272 告警行")
        for ln in out1.splitlines():
            if "R272" in ln:
                print("         " + ln.strip())
        if not hit1:
            fails.append("生效路径未报 R272（接线断裂）")

        # 反例：无漂移 → 必须不报 R272
        p2 = os.path.join(base, "clean")
        os.makedirs(p2, exist_ok=True)
        make_project(Path(p2), CLEAN_MAIN, CLEAN_VOL)
        out2 = review(p2)
        hit2 = "R272" in out2
        print(f"  [{'PASS' if not hit2 else 'FAIL'}] 反例（合成无漂移项目）→ 期望**不**出现 R272 告警行")
        if hit2:
            for ln in out2.splitlines():
                if "R272" in ln:
                    print("         " + ln.strip())
            fails.append("反例误报 R272（判据过松/永不报警的反面）")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("-" * 68)
    if fails:
        print(f"层 b' 结果：FAIL（{len(fails)} 项）")
        for f in fails:
            print("   " + f)
        return 1
    print("层 b' 结果：2/2 PASS（生效路径报出 + 反例不报）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
