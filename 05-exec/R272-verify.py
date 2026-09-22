#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""R272 独立复验（层 a：隔离桩 / 合成场景）—— 不修改受管根任何文件。

对象：`D:\\global_skills\\A-project-handoff\\scripts\\handoff_lib\\savepoint.py`
      `_memory_volume_drift()`（由并行会话于 commit `b7ba255` 落地，R272 / v3.46.0）

判据：R238 两层含对照 —— 本脚本只做**层 a（合成场景隔离桩）**；
      层 b（集成：真实项目 review 零误伤）由外层命令单独跑并记录。
      两层都过才算「独立复验通过」；只过层 a = 未验证。

安全：全程在系统临时目录内造合成项目，**不触碰 D:\\global_skills / D:\\global_memory / 焚诀**。
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, r"D:\global_skills\A-project-handoff\scripts")
from handoff_lib import savepoint as sp  # noqa: E402

MAIN_HEAD = "# 07 - 下一步\n\n## P0 — 必须做\n\n"

# (场景名, 主卷正文, 分卷正文, 期望冲突数, 期望关键词或 None, 说明)
SCENARIOS = [
    (
        "A 主卷未勾选 / 分卷已勾选 → 声明失效",
        MAIN_HEAD + "- [ ] 阶段1 补跑三脚本\n",
        "- [x] 阶段1 补跑三脚本\n",
        1, "主卷声明失效", "生效路径①",
    ),
    (
        "B 双侧都勾选 → 重复登记",
        MAIN_HEAD + "- [x] 阶段1 补跑三脚本\n",
        "- [x] 阶段1 补跑三脚本\n",
        1, "重复登记", "生效路径②",
    ),
    (
        "C 主卷未完成、分卷是不同的已完成项 → 无冲突（对照·防误报）",
        MAIN_HEAD + "- [ ] 阶段1 补跑三脚本\n",
        "- [x] 另一件完全不同的事\n",
        0, None, "对照·正常",
    ),
    (
        "D 主卷无未完成项、分卷有 → P0 被整块迁走",
        MAIN_HEAD + "- [x] 已完成的老项\n",
        "- [ ] 阶段1 补跑三脚本\n",
        1, "P0 疑似被整块迁走", "生效路径③",
    ),
    (
        "E 条目写在 HTML 注释内 → 不计入（对照·防注释误报）",
        MAIN_HEAD + "- [ ] 阶段1 补跑三脚本\n",
        "<!-- - [x] 阶段1 补跑三脚本 -->\n",
        0, None, "对照·注释",
    ),
    (
        "F 主卷无任何条目、分卷有 → 不触发「整块迁走」（前置条件 main_e 为空）",
        "# 07 - 下一步\n\n（暂无 P0）\n",
        "- [ ] 阶段1 补跑三脚本\n",
        0, None, "对照·边界",
    ),
    (
        "G 主卷内嵌陈旧 commit 号（无勾选框漂移）→ 当前判据**不覆盖**（缺口证据，非缺陷断言）",
        MAIN_HEAD + "- [ ] 阶段1 补跑三脚本\n- 当前 HEAD = ca0b431（实测应为 4f2e050）\n",
        "- [x] 另一件已完成的事\n",
        0, None, "缺口证据·数字漂移",
    ),
]


def main():
    fails = []
    print("=" * 68)
    print("R272 独立复验 · 层 a（合成场景隔离桩）")
    print("=" * 68)
    for name, main_txt, vol_txt, exp_n, kw, kind in SCENARIOS:
        with tempfile.TemporaryDirectory(prefix="r272_") as td:
            d = Path(td)
            (d / "07-next-steps.md").write_text(main_txt, encoding="utf-8")
            (d / "07-next-steps.part1.md").write_text(vol_txt, encoding="utf-8")
            got = sp._memory_volume_drift(d)
        ok = (len(got) == exp_n) and (kw is None or any(kw in g for g in got))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         期望 {exp_n} 条{('/ 含「%s」' % kw) if kw else ''}；实测 {len(got)} 条 -> {got}")
        if not ok:
            fails.append(f"{kind}: {name}（期望 {exp_n} 条，实测 {len(got)} 条）")
    print("-" * 68)
    if fails:
        print(f"层 a 结果：FAIL {len(fails)}/{len(SCENARIOS)}")
        for f in fails:
            print("   " + f)
        return 1
    print(f"层 a 结果：{len(SCENARIOS)}/{len(SCENARIOS)} PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
