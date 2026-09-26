# -*- coding: utf-8 -*-
"""r58 VOL-D908D 落地：TODO.md 注入壳瘦身（历史节原样迁 memory/ 分卷 + 壳内留指针）。

为什么不能用 `handoff.py trim-shell`（r57 登记时写的处置方案）：
  trim-shell 的操作对象是 `memory/` 下的卷（TRIM_ENTRY_TARGETS = 07/05/06），
  而 TODO.md 是仓根手工索引，不在其目标表内 —— 照方抓药会「命令跑通但一件事也没做」。
  本轮实测（volume 体检）确认两条 L2 项里只有 TODO.md 可这样收；根 AGENTS.md 是**生成壳**，
  其体量是 memory/07 P0 面的函数，只能由「逐条人工裁决 P0」收敛，不在此件范围。

三条硬护栏（缺一即拒写）：
  ① 行守恒：原文每一行必须恰好出现在「新壳 + 历史卷」之一（missing==0 且 dup==0）；
  ② 原文零改写：迁出的行**逐字节**复制，不 trim、不重排、不改标点（R241）；
  ③ 默认 dry-run：必须显式 --apply 才动盘，且先把原文件备份到 _trash/<ts>/（可回滚）。
"""
import datetime
import io
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODO = os.path.join(ROOT, "TODO.md")
HIST = os.path.join(ROOT, "memory", "todo-history.part1.md")

# 迁出的历史节（按 H2/H3 标题精确定位；标题本身也一并迁走）
MOVE_TITLES = [
    "## 🔴 第 4 轮进度（2026-09-22）",
    "## 🔴 第 3 轮进度（2026-09-19）",
    "## 🔴 第 2 轮进度（2026-09-14）",
    "## 阶段0 范围裁定 ✅ 已完成（2026-09-14）",
    "## 阶段1 四维机器扫描 ✅ 已完成（2026-09-14）",
    "## 阶段2 全量精读 🚧 进行中（1/6 批，依赖阶段1）",
    "## 阶段3 审计报告 ⬜（依赖阶段2）",
    "## 阶段4 实施计划 ⬜（依赖阶段3）",
    "## 阶段5 工作流专项 ⬜（依赖阶段4）",
    "## 已记录但未闭环的升级建议",
    "## 阶段4 执行进度（实际改动 `D:\\global_skills`，2026-09-14 起）",
]
POINTER = [
    "",
    "## 📦 历史节已迁出（r58 体量治理 VOL-D908D）",
    "",
    "> 本文件原有 11 个历史/阶段详情节 **原样**（逐字节）迁至 `memory/todo-history.part1.md`，此处只留本指针。",
    "> 迁移动作与行守恒由 `05-exec/r58_todo_shell_slim.py` 机器把关（丢失原文行==0 且 无法归因新增行==0 才落盘）。",
    "> 触发迁出的判据：本文件每轮注入 31,685B > `root_doc_max` 16,384B（取值 `python <handoff.py> volume <项目根>`）。",
    "> 禁按「让 volume 变绿」反向操作：本件只搬不移除，任何一行在历史卷里找不到即为事故（R247）。",
    "",
    "> ⚠️ **校正注（r58，2026-09-26，R241 只加注不改写）**：上方「六阶段状态总表」与历史卷里的",
    "> 「阶段2 🚧 进行中 / 阶段3 ⬜ / 阶段4 ⬜」是 **2026-09-14~09-22 时点状态**，与当前实况不符。",
    "> 当前实况（取值 `python 05-exec/run_gates.py` + `python <handoff.py> status <项目根>`）：",
    "> 阶段 0-4 均已交付（见 `memory/05-feature-status.md`），阶段5 工作流专项进行中；",
    "> 本文件定位是**索引非入口**，跨会话唯一入口 = `memory/07-next-steps.md`。",
    "",
]


def split_sections(lines):
    """返回 [(title, [rows...])]，标题行为该节第一行；标题前的内容归入 ('', rows)。"""
    out, cur, title = [], [], ""
    for ln in lines:
        if ln.startswith("## ") or ln.startswith("### "):
            out.append((title, cur))
            title, cur = ln, [ln]
        else:
            cur.append(ln)
    out.append((title, cur))
    return out


def main():
    apply_ = "--apply" in sys.argv[1:]
    text = io.open(TODO, encoding="utf-8").read()
    lines = text.split("\n")
    orig_total = len(lines)
    sections = split_sections(lines)

    moved, kept = [], []
    hit_titles = set()
    for title, rows in sections:
        if title in MOVE_TITLES:
            moved.append((title, rows))
            hit_titles.add(title)
        else:
            kept.append((title, rows))
    missing_titles = [t for t in MOVE_TITLES if t not in hit_titles]
    if missing_titles:
        print("❌ 有 %d 个待迁标题在原文里找不到 ⇒ 版本漂移，拒绝动盘：" % len(missing_titles))
        for t in missing_titles:
            print("   - %s" % t)
        return 1

    HIST_HEADER = ["> 本卷由 `05-exec/r58_todo_shell_slim.py` 于 %s 从仓根 `TODO.md` **原样**迁入；"
                   "正文一字未改（R241）。回滚：`git checkout HEAD -- TODO.md memory/todo-history.part1.md`。"
                   % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                   "> 取当前状态请看 `memory/07-next-steps.md`（唯一入口）与 `memory/05-feature-status.md`。",
                   ""]
    hist_rows = list(HIST_HEADER)
    for _title, rows in moved:
        hist_rows.extend(rows)
    keep_rows = []
    for _title, rows in kept:
        keep_rows.extend(rows)
    n_dropped_blank = 0
    while keep_rows and keep_rows[-1] == "":
        keep_rows.pop()
        n_dropped_blank += 1
    new_shell = keep_rows + POINTER + [""]

    # ---- 护栏 ①：行守恒用**精确多重集对账**（首版按「输出独有行数 − 新增行数」粗算，
    #      被空行与重复短行污染，把一次干净迁移判成「意外重复 17」而拒写 —— 判据自己错比漏判更坏）----
    from collections import Counter
    additions = Counter(POINTER) + Counter(HIST_HEADER) + Counter([""])  # 末尾换行占位
    expected = Counter(lines)
    for _ in range(n_dropped_blank):
        expected[""] -= 1
    expected.update(additions)   # 首版漏了这一步：新增行没进「期望集」，于是干净迁移被判成 18 行「意外新增」
    actual = Counter(new_shell + hist_rows)
    lost = expected - actual          # 原文里本该保留却没落地的行
    unexplained = actual - expected   # 产物里出现、但不在保留集与新增集内的行
    shell_b = len("\n".join(new_shell).encode("utf-8"))
    hist_b = len("\n".join(hist_rows).encode("utf-8"))
    print("=== r58 TODO.md 注入壳瘦身（%s）===" % ("APPLY 落盘" if apply_ else "dry-run 预览"))
    print("  原文件 %d 行 / %d B ｜ 壳尾空行折叠 %d 行" % (orig_total, len(text.encode("utf-8")), n_dropped_blank))
    print("  迁出 %d 节 / %d B → memory/todo-history.part1.md" % (len(moved), hist_b))
    print("  新壳 %d 行 / %d B（阈值 root_doc_max=16384 ⇒ %s）" % (
        len(new_shell), shell_b, "达标" if shell_b <= 16384 else "仍超限"))
    print("  行守恒：丢失原文行=%d ｜ 无法归因的新增行=%d（本轮声明新增=%d 种）" % (
        sum(lost.values()), sum(unexplained.values()), len(additions)))
    if lost:
        print("  ❌ 有 %d 行原文未落地 ⇒ 拒绝落盘（R247 禁静默丢数据）" % sum(lost.values()))
        for k in list(lost)[:5]:
            print("     丢失: %r" % k[:90])
        return 1
    if unexplained:
        print("  ❌ 有 %d 行既非保留也非本轮新增 ⇒ 结构假设不成立，拒绝落盘" % sum(unexplained.values()))
        for k in list(unexplained)[:5]:
            print("     意外: %r" % k[:90])
        return 1
    if not apply_:
        print("[SLIM:DRYRUN] 未动盘。加 --apply 落盘（自动备份到 _trash/<ts>/）")
        return 0

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = os.path.join(ROOT, "_trash", "r58_todo_slim_" + ts)
    os.makedirs(bak, exist_ok=True)
    shutil.copy2(TODO, os.path.join(bak, "TODO.md.orig"))
    if os.path.isfile(HIST):
        shutil.copy2(HIST, os.path.join(bak, "todo-history.part1.md.prev"))
    io.open(HIST, "w", encoding="utf-8", newline="\n").write("\n".join(hist_rows) + "\n")
    io.open(TODO, "w", encoding="utf-8", newline="\n").write("\n".join(new_shell))
    print("[SLIM:APPLIED] 备份 %s ｜ 新壳 %dB ｜ 历史卷 %dB" % (bak, shell_b, hist_b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
