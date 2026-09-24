# -*- coding: utf-8 -*-
"""r19_feedback_append.py — A-get-memory 收尾反哺落盘器（本会话一次性，幂等）。

写两处（均为工作区外受管根，Edit/Write 工具被限 ⇒ 走 python append + 写后读回验证 R213）：
  ① `D:\\global_memory\\lessons\\lessons.part44.md` ← 2 条经验（倒序：新条目插在首个 `### [` 之前）
  ② `D:\\global_memory\\memory\\2026-09-24.md`     ← 当日日志段 + 【数据流假设】四行 + footer 锚点块（append-only）

幂等判据：目标文件已含本会话标记串（LESSON_KEY / FOOTER_KEY）则跳过该处，不重复追加。
异常：目标不可写/不存在 → 打印 [WRITE:FAIL] + 原因并 exit 1（禁静默）；写后必须读回实证。
"""

import io
import os
import sys

LESSON_FILE = r"D:\global_memory\lessons\lessons.part44.md"
LOG_FILE = r"D:\global_memory\memory\2026-09-24.md"
LESSON_KEY = "[2026-09-24] 🔴 自研判据工具零夹具交付"
FOOTER_KEY = "session=qd-zijian-r19-0924"

LESSONS = """### [2026-09-24] 🔴 自研判据工具零夹具交付
trigger: 零夹具/判据不可信 | 交付扫描器或新判据 | python,gitbash,自建skill优化
- **问题：** r18 一次交付 4 个判据类只读工具（catalog_attention_tax / rule_conflict_scan / cumulative_drift_scan / skill_structure_rubric_scan），**一个夹具都没有**，且其中 3 个的判据后来被证实有误（drift 候选 16 条含 6 条噪声 37.5%：自动拆卷 `*.partN.md`、含「自动生成」标记的注入壳 AGENTS.md、因 "lessons" 子串被误判为规则类的 `eval/*.py`）。
- **原因：** 「新判据必须带桩」只写在 A-skill-manager `governance.md`（自觉型规则），批量交付时没人拦；且对标只看 README 不看实现，看不见对手的 `SKIP_PREFIXES` / `--self-test` 是判据可信度的一部分。
- **解法：** 立即可复跑的两步——① 判据类工具交付前必须 `python <项目>/05-exec/r19_scan_fixtures.py`（层 a 已知答案 + 层 b 真机接线**含对照组**，`[GATE:fixture-pass]` 才算交付）；② 排除/豁免类判据必须留 `--no-exclude` 形态的**对照开关**并把被排除项全量写进 JSON（排除可见，禁静默丢数据）。
- **元：** 来源=自建skill优化 r19 对标实物层 | 版本=A-project-handoff V3.52.2 同轮 | 置信度=0.5 | 日期=2026-09-24 | 适用范围=python, 数据层, 多agent

### [2026-09-24] 🔴 handoff flow 首次写 09 吃掉「字段约定」图例
trigger: 09-workflow-state 图例消失 | flow --add / --sync | A-project-handoff,handoff.py
- **问题：** `handoff.py flow <项目> --add` 第一次执行后，`memory/09-workflow-state.md` 模板自带的「字段约定（机器解析，**勿改列名与列序**）」HTML 注释块与「## 推进记录」段首注释**整块消失**（实测一次操作掉 18 行）。
- **原因：** `_write_task_table → _replace_section` 是**替换式**重写整段正文（旧正文一律不保留）；`_append_log` 另调 `strip_html_comments`，两处都不回填段首图例。
- **解法：** 上游已修（受管根 `18294ba`，V3.52.2）：新增 `_leading_comments()` 只回填**段首连续**注释块，无图例的存量文件不凭空造注释（幂等：重复重写只留一份）；调用方无需改动。存量项目若已丢图例，`git checkout HEAD -- memory/09-workflow-state.md` 后重跑 `flow --add/--block/--sync` 即可（r19 本项目实测）。
- **元：** 来源=自建skill优化 r19 | 版本=A-project-handoff V3.52.2 | 置信度=0.5 | 日期=2026-09-24 | 适用范围=python, handoff.py, 记忆系统

"""

LOG_BLOCK = """
## 18:2x 自建skill优化 r19「对标实物层」轮（QD 端）
- 广度实测无收益（14 个对手 35 分钟合计 +37 星 = +0.006%）⇒ 转「读对手源码/Schema/模板」层：据 `drift-detection.py`（SKIP_PREFIXES/--semantic 六态判据）、`check-rule-conflicts.py`（--self-test 6 例 + write-time hook）、`docs/skill-anatomy.md`（description ≤1024 + 禁写流程）、`schemas/aas-v1/`（12 份契约）反向修自有工具。
- **修 r18 三处判据缺陷**：按设计累积项未排除（6/16=37.5% 噪声）/ 排除判据过宽（误伤文件名中部带日期的人工报告）/ 四工具零夹具 ⇒ 新建 `05-exec/r19_scan_fixtures.py` **55/55 `[GATE:fixture-pass]`**（层 a 36 + 层 b 19 含 `--no-exclude` 对照组）。
- **打开内容级门禁盲区**：P0-C 第 2 批人工复核 11 句（仍然成立 7 / 已失真 7 句 / uncertain 1）暴露每轮注入的 `A-memory-start/SKILL.md` 仍写「五端 / V9.7.0 瘦身版」而真相源 = **8 端**、`version: 10.67.0`；C1~C28 无一条比对「正文计数断言 == 真相源」⇒ 新建 `05-exec/claim_truth_scan.py`，首跑 **10 条候选**。
- **上游真实缺陷当场修**：`flow --add` 首次写 09 吃掉「字段约定」图例注释 → 受管根 `18294ba`（A-project-handoff **V3.52.2**，`_leading_comments()` 回填 + 幂等），隔离桩 **15/15 含修前/修后对照** + 真机端到端 `flow --check` PASS + 三文件白名单零夹带 + `check-skill-mirror.ps1 -Fix`（单向源→镜像）后 **mirror/noise/evolution 三门转绿**（stub 仍一红 = 焚诀在途 C29，非本仓）。
- P1-C 分母统一登记落地（`_lib.denominator()` 三口径 166/167/167 接入 4 工具，注册表不可读 ⇒ `consistent=None` 禁静默）；新判据「流程入描述」实测 24/166；本项目 **flow 状态机首次真用**（R19-1/R19-2 blocked、R19-3 todo + `--sync` 回写 07）；P2-A 交付 `06-benchmark/comparison.md` 常驻横向页。
- 关键产出：`06-benchmark/全量对标报告_r19_2026-09-24.md` / `P0-C_累积漂移复核第2批_2026-09-24.md` / `05-exec/{claim_truth_scan,r19_scan_fixtures,r19_flow_legend_stub}.py`；本仓 `3328cb7` 已推送（`git rev-parse HEAD` == `git ls-remote origin main` 实测）。

【数据流假设】
来源: `05-exec/_lib.py` 现文（已 Read）+ `焚诀/skill/registry/disk_manifest.json`（schema=fenjue-disk-manifest-v1，count=167==len(skills) 实测）+ `焚诀/eval/truth_constants.json` `endpoints.active`=8 端实测 + `D:/global_skills/A-project-handoff/scripts/handoff_lib/flow.py:227/246`（Read 定位行号）+ 对手实物 gh api raw 直读（skill-anatomy.md / drift-detection.py / check-rule-conflicts.py / .driftignore / schemas/aas-v1）
流向: 新 helper `_lib.denominator()` → 4 个扫描器 stdout/JSON/MD → `06-benchmark/` 基线件 → r19 报告与 07 台账引用；`_leading_comments()` → `_replace_section`/`_append_log` → 各项目 `memory/09-workflow-state.md` 写入路径（下游消费者 = flow --check / savepoint / 跨会话读者）；lessons 两条 → GM 活跃检索位（A-memory-start Step 0.55 全文检索命中面）
结构: 全部 UTF-8 无 BOM；JSON 只增键不改名（新增 `denominator{}`/`excluded[]`/`verdict_taxonomy[]`/`has_process`/`over_cap`，schema 串升位 cumulative-drift-scan-v1→v2）；lessons 每条 = 标题 + trigger 三栏 + 问题/原因/解法/元 ≤6 行，目标卷 part44 写前 2543B 写后须 ≤4096B（字节判定，禁目测）；GM 日志 append-only，footer 块含 `<!-- footer:begin session= ts= -->` + [skill清单] 1 行 + [升级建议] ≤3 行 + end
异常: 注册表 manifest 不可读 → `registry.available=False` 且 `consistent=None`（打印「禁止引用为全库分母」，不以 0 冒充）；真相源不可读 → claim 工具 exit 2（禁判零失真，R247）；受管根补丁 old 未命中 → rule_editor dry-run 先验 + `git status --porcelain` 白名单逐文件核对（防夹带 28 条他人改动）；反哺写入前查标记串幂等防重复追加；写后 grep 读回验证（R213），失败即报 [WRITE:FAIL] 不静默

<!-- footer:begin session=qd-zijian-r19-0924 ts=2026-09-24T18:25:00+08:00 -->
[skill清单] 本轮调用=2 个 (A-memory-start, A-get-memory)
[升级建议] skill=A-project-handoff | 五问=错误信息 | 改法=flow重写回填段首图例注释 | 对照=已取(证据=修前桩 g1 图例两项 FAIL、修后 15/15，--no-exclude 对照组仍报警证明判据未放松) | 状态=已闭环(证据=D:\\global_skills\\A-project-handoff\\SKILL.md#版本行:V3.52.2)
[升级建议] skill=A-memory-start | 五问=过期指令 | 改法=正文五端与V9.7.0戳改口八端10.67.0 | 对照=已取(证据=claim_truth_scan 10 候选 vs truth_constants active=8 端；正当历史行已豁免) | 状态=未闭环(原因=description 属派生件镜像，改动需 build_indexes 全量重建窗口，且 global_skills 28 条他人 in-flight；已登记 flow R19-1=blocked)
[升级建议] skill=A-get-memory | 五问=缺失步骤 | 改法=交付判据类工具前强制跑夹具门禁 | 对照=未取(待证伪) | 状态=未闭环(原因=机器落点须登记焚诀 eval/stubs/registry.json，本项目对焚诀 eval/ 只读；转归属会话)
<!-- footer:end -->
"""


def read(path):
    with io.open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def write_bytes(path, text):
    with open(path, "wb") as f:
        f.write(text.encode("utf-8"))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    done, skipped = [], []

    # ① lessons：追加到最新 dated part；写前按字节硬判据决定是否换卷（≤4096B，禁目测）
    if not os.path.isfile(LESSON_FILE):
        print("[WRITE:FAIL] lessons 目标不存在: %s" % LESSON_FILE)
        return 1
    text = read(LESSON_FILE)
    if LESSON_KEY in text:
        skipped.append("lessons(已含本会话条目)")
    else:
        candidate_head = ("# lessons.part45\n\n"
                          "> 2026-09-24 r19 对标实物层轮新建（part44 现 %dB + 本批两条 %dB = %dB "
                          "超 4,096B 硬上限，按 bigfile-split/≤4KB 轻量规则换卷）\n\n"
                          "## 踩坑记录\n\n" % (len(text.encode("utf-8")),
                                               len(LESSONS.encode("utf-8")),
                                               len(text.encode("utf-8")) + len(LESSONS.encode("utf-8"))))
        idx = text.find("### [")
        appended = ((text[:idx] + LESSONS + text[idx:]) if idx >= 0
                    else (text.rstrip() + "\n\n" + LESSONS))
        if len(appended.encode("utf-8")) > 4096:
            target, new = LESSON_FILE.replace("part44", "part45"), candidate_head + LESSONS
            reason = "part44 追加后超限 ⇒ 换卷 part45"
        else:
            target, new, reason = LESSON_FILE, appended, "part44 原卷追加"
        write_bytes(target, new)
        back = read(target)
        size = os.path.getsize(target)
        ok = (LESSON_KEY in back) and back.count(LESSON_KEY) == 1 and ("handoff flow 首次写 09" in back)
        print("[lessons] %s | 落点=%s | 读回验证=%s | 字节=%d（≤4096 硬判据）" % (
            reason, os.path.basename(target), ok, size))
        if not ok or size > 4096:
            print("[WRITE:FAIL] lessons 验证未过（字节超限或重复）")
            return 1
        done.append(os.path.basename(target))

    # ② GM 当日日志：append-only
    log = read(LOG_FILE)
    if FOOTER_KEY in log:
        skipped.append("GM日志(本会话已落)")
    else:
        write_bytes(LOG_FILE, log.rstrip("\n") + "\n" + LOG_BLOCK)
        back = read(LOG_FILE)
        need = ["【数据流假设】", "来源:", "流向:", "结构:", "异常:", "[skill清单]", "[升级建议]", FOOTER_KEY]
        miss = [k for k in need if k not in back]
        print("[GM日志] 读回验证=%s | 缺失锚点=%s | 尾部字节=%d" % (not miss, miss or "-", os.path.getsize(LOG_FILE)))
        if miss:
            print("[WRITE:FAIL] GM 日志锚点不全（G8/footer 门禁会红）")
            return 1
        done.append("memory/2026-09-24.md")

    print("[WRITE:OK] 落盘=%s 跳过=%s" % (done, skipped or "无"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
