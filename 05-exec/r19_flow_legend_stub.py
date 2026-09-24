# -*- coding: utf-8 -*-
"""r19_flow_legend_stub.py — 隔离桩：flow 重写章节必须保留段首图例（层 a 已知答案）。

被测缺陷（2026-09-24 本项目 r19 实跑暴露，受管根 A-project-handoff V3.52.1）：
  `handoff.py flow <path> --add` 首次写 `memory/09-workflow-state.md` 时，
  `_write_task_table` → `_replace_section` 以**替换式**重写「## 任务表」整段正文，
  把模板自带的「字段约定（机器解析，**勿改列名与列序**）」HTML 注释图例整块删除；
  `_append_log` 另因 `strip_html_comments` 把「## 推进记录」段首注释一并抹掉。
  实测证据：修复前本项目 09 文件 `git diff` 显示 18 行注释块被删（两处 `<!--` 段落消失）。

层 b（真机接线）见 `r19_scan_fixtures.py` 之外的手工步骤：本项目 09 先 `git checkout HEAD --`
还原图例 → 重跑 `flow --add/--block/--sync` → 图例仍在（本脚本执行后由调用方核验）。

退出码：0 全过 / 1 有失败 / 2 依赖不满足（受管根不可读）。
"""

import sys
from pathlib import Path

GS = Path(r"D:\global_skills\A-project-handoff\scripts")
if not GS.exists():
    print("SKIP: 受管根 A-project-handoff/scripts 不可读")
    raise SystemExit(2)
sys.path.insert(0, str(GS))
try:
    from handoff_lib import flow  # noqa: E402
    from handoff_lib.common import strip_html_comments  # noqa: E402
except Exception as e:  # pragma: no cover
    print("SKIP: 导入 handoff_lib.flow 失败: %s" % e)
    raise SystemExit(2)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TPL = """# 09 - 动态工作流任务状态（状态唯一源）

> schema: fenjue-workflow-state-v1

## 任务表

<!--
字段约定（机器解析，**勿改列名与列序**）：
| id | 批次 | 标题 | 状态 | 依赖 | 阻塞 | 更新于 | 证据 |
- 状态    todo / doing / done / blocked；其他值 = 解析报错

示例行（在本注释内，不参与解析）：
| P0-1 | P0 | 示例任务 | todo | - | - | 2026-09-23 07:00 | - |
-->

| id | 批次 | 标题 | 状态 | 依赖 | 阻塞 | 更新于 | 证据 |
|----|------|------|------|------|------|--------|------|

## 推进记录

<!-- append-only，最新在下；由 flow --start / --done / --block 自动追加 -->
"""

TASK = {"id": "P0-9", "batch": "P0", "title": "示例任务", "state": "blocked",
        "deps": "-", "block": "原因说明", "updated": "2026-09-24 18:00", "evidence": "-"}

R = []


def ck(name, cond, detail=""):
    R.append(bool(cond))
    print("%s %-52s %s" % ("PASS" if cond else "FAIL", name, "" if cond else detail[:180]))


def main():
    # --- 组 1：任务表重写保留图例（生效路径）---
    out = flow._write_task_table(TPL, [TASK])
    ck("g1 图例仍在（字段约定）", "字段约定" in out and "-->" in out.split("## 推进记录")[0])
    ck("g1 示例行注释仍在", "示例行（在本注释内，不参与解析）" in out)
    ck("g1 新任务行已写入", "| P0-9 | P0 | 示例任务 | blocked | - | 原因说明 | 2026-09-24 18:00 | - |" in out)
    ck("g1 表头未被复制成两份（剔注释后按表头行计数）",
       strip_html_comments(out).count("| id | 批次 |") == 1,
       str(strip_html_comments(out).count("| id | 批次 |")))
    ck("g1 推进记录段未被破坏", "## 推进记录" in out and "append-only" in out)
    # --- 组 2：解析仍只见真任务行（注释里的示例不得混入）---
    tasks, perr = flow._parse_tasks(out)
    ck("g2 解析出 1 个任务（示例行在注释内不参与）", len(tasks) == 1 and not perr, str(tasks))
    ck("g2 状态/阻塞解析正确", tasks and tasks[0]["state"] == "blocked" and tasks[0]["block"] == "原因说明")
    # --- 组 3：推进记录追加保留段首注释 + 追加生效（对照组）---
    log1 = flow._append_log(out, "- [2026-09-24 18:00] P0-9 todo → blocked")
    ck("g3 推进记录段首注释仍在", "append-only，最新在下" in log1.split("## 推进记录")[1])
    ck("g3 新记录已追加", "P0-9 todo → blocked" in log1)
    ck("g3 任务表部分未被日志改写", "| P0-9 | P0 | 示例任务 | blocked |" in log1)
    # --- 组 4：无图例的存量项目（不得凭空造注释；幂等）---
    plain = TPL.split("<!--")[0] + TPL.split("-->", 1)[1]
    out2 = flow._write_task_table(plain, [TASK])
    ck("g4 无图例输入 → 输出不含 <!--", "<!--" not in out2.split("## 推进记录")[0], out2[:120])
    out3 = flow._write_task_table(out2, [TASK])
    ck("g4 幂等：二次重写不再新增图例块", out3.count("字段约定") == 0)
    out4 = flow._write_task_table(out, [TASK])
    ck("g4 幂等：重复重写图例只留一份", out4.count("字段约定") == 1, str(out4.count("字段约定")))
    # --- 组 5：判据未放松对照（章节缺失仍须返回 None）---
    ck("g5 缺「## 任务表」章节 → None（不得静默造章节）",
       flow._replace_section("# x\n\n## 别的\n\n内容\n", "任务表", "| a |\n") is None)
    ck("g5 缺推进记录章节时 _append_log 兜底建段", "## 推进记录" in flow._append_log("# x\n\n## 任务表\n\n- 空\n", "- 一行"))
    bad = [i for i, ok in enumerate(R, 1) if not ok]
    print("\n隔离桩合计: %d 项 / 通过 %d / 失败 %d" % (len(R), sum(R), len(bad)))
    print("[GATE:stub-pass]" if not bad else "[GATE:stub-fail] 用例 %s" % bad)
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
