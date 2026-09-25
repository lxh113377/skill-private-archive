# -*- coding: utf-8 -*-
r"""r46_mark_verdict_fixtures.py — 裁决标记写入器的夹具（TDD：先看红）。

动因（r45 D62 实测）：W-9 挂了 5 轮，真因是我用**行号索引**给 07 写裁决标记，
而 07 在 savepoint 拆卷与并发整卷重写下行号会漂 ⇒ 三轮「补标」全写到别的行，目标行标记数 = 0。
W-13 已提供 find_item_line，但**约定拦不住我自己写临时脚本**（r45 又犯一次），
故本轮把它固化成唯一入口：`05-exec/r46_mark_verdict.py`。

工具契约（每条都有对应断言）：
  1) 只能按**标题锚点**定位（无 --line 参数；传 --line 必须直接拒绝）；
  2) 命中数 != 1 ⇒ 拒写（重复登记与找不到同样危险）；
  3) 只准写在 `- [ ]` 未勾选项上（禁往已闭环条目上标裁决）；
  4) 同一轮重复裁决 ⇒ 拒写（幂等靠拒绝实现，**不得靠静默跳过**，#23 同族）；
  5) 写入后必须 grep 读回验证，读不到 ⇒ 回滚并返回失败（X-8）；
  6) 只允许写本项目 memory/ 下的卷（受管根与仓外一律拒写）。
"""

import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "r46_mark_verdict.py"
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-54s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def run(args, cwd=None):
    return subprocess.run([sys.executable, str(TOOL)] + args, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", cwd=cwd or str(HERE.parent))


def make_vault(tmp):
    v = tmp / "memory"
    v.mkdir(parents=True, exist_ok=True)
    f = v / "07-next-steps.md"
    f.write_text("\n".join([
        "## P0 — 必须做",
        "- [ ] **【P0·待办 甲（r45 登记）】** 正文甲",
        "- [x] **【P0·待办 乙（r45 登记）】** 已闭环",
        "- [ ] **【P1·待办 甲（r45 登记）】** 正文甲重复登记",
        "",
    ]), encoding="utf-8", newline="")
    return f


def main():
    if not TOOL.exists():
        ck("RED 前置：写入器 r46_mark_verdict.py 存在", False,
           "文件不存在 —— 本次即 TDD 红阶段（先看失败再实现）")
        print("\n夹具合计: %d 项" % len(RESULTS))
        print("[GATE:fixture-fail]")
        return 1

    tmp = Path(tempfile.mkdtemp(prefix="r46_mv_"))
    f = make_vault(tmp)
    before = f.read_text(encoding="utf-8")

    r = run(["--vault", str(tmp), "--key", "待办 乙", "--round", "46",
             "--verdict", "作废｜实测已被上游取代"])
    ck("t1 已勾选项（- [x]）拒写：禁往别人已闭环的条目上标裁决",
       r.returncode != 0 and f.read_text(encoding="utf-8") == before, (r.stdout + r.stderr)[-200:])

    r = run(["--vault", str(tmp), "--key", "待办 甲", "--round", "46", "--verdict", "降级看守"])
    ck("t2 标题命中 2 行（主壳 + 分卷重复登记）→ 必须拒写而非挑第一行",
       r.returncode != 0 and f.read_text(encoding="utf-8") == before, (r.stdout + r.stderr)[-200:])

    r = run(["--vault", str(tmp), "--key", "待办 甲（r45 登记）】** 正文甲$", "--round", "46",
             "--verdict", "x"])
    ck("t3 锚点不存在 → 拒写（不得退化成追加到文件末尾）",
       r.returncode != 0 and f.read_text(encoding="utf-8") == before, (r.stdout + r.stderr)[-160:])

    uniq = tmp / "uniq"
    (uniq / "memory").mkdir(parents=True, exist_ok=True)
    uf = uniq / "memory" / "07-next-steps.md"
    uf.write_text("- [ ] **【P0·待办 丙（r44 登记）】】** 唯一正文\n", encoding="utf-8", newline="")
    r = run(["--vault", str(uniq), "--key", "待办 丙", "--round", "46",
             "--verdict", "降级（转长期看守）｜外部条件未解"])
    after = uf.read_text(encoding="utf-8")
    ck("t4 唯一命中 → 写入成功且带本轮轮号标记",
       r.returncode == 0 and "r46 裁决=降级" in after and after.lstrip().startswith("- [ ]"), after[:160])
    bdir = uniq / "05-exec" / "mark_backup"
    ck("t5 写入自带备份且**不落记忆卷**（同 r35 落点教训；默认落 05-exec/mark_backup）",
       bool(list(bdir.glob("*.bak"))) and not list((uniq / "memory").glob("*.bak"))
       and not list(uniq.glob("*.bak")), str([p.name for p in bdir.glob("*.bak")])[:160])

    r2 = run(["--vault", str(uniq), "--key", "待办 丙", "--round", "46", "--verdict", "作废｜重复裁"])
    ck("t6 同轮二次裁决 → 拒写（幂等靠拒绝实现，不靠静默跳过）",
       r2.returncode != 0 and "作废" not in uf.read_text(encoding="utf-8")
       and uf.read_text(encoding="utf-8").count("r46 裁决=") == 1,
       (r2.stdout + r2.stderr)[-200:])

    r3 = run(["--vault", str(uniq), "--line", "1", "--key", "待办 丙", "--round", "47", "--verdict", "x"])
    ck("t7 不提供行号入口：传 --line 直接拒绝（X-19 工具化，而非靠自觉）",
       r3.returncode != 0, (r3.stdout + r3.stderr)[-160:])

    outside = tmp / "outside.md"
    outside.write_text("- [ ] 受管根外条目\n", encoding="utf-8", newline="")
    r4 = run(["--file", str(outside), "--key", "受管根外", "--round", "46", "--verdict", "x"])
    ck("t8 只准写项目 memory/ 卷；指到仓外路径一律拒写",
       r4.returncode != 0 and outside.read_text(encoding="utf-8").strip() == "- [ ] 受管根外条目",
       (r4.stdout + r4.stderr)[-160:])

    # ---- t9/t10：混合行尾卷（r49 真事故复现）------------------------------------
    # 实测根因：memory/07-next-steps.md = 178 个 CRLF + 4 个纯 LF 的**混合行尾**文件。
    # 写入器原先按「文件里有 \r\n 就整份按 \r\n 切」，于是那 4 个 LF 行被并进前一个元素，
    # 追加标记落到**元素末尾 = 另一条目那一行**（我把 W-16 的裁决写到了 W-14 行上）。
    # 夹具样本卷若只用统一行尾，这一类错位**永远测不到** —— 与 W-20 同族：判据的输入面
    # 不覆盖真实形态时，全绿不代表真机正确。
    mixdir = Path(tempfile.mkdtemp(prefix="r49_mv_")) / "memory"
    mixdir.mkdir(parents=True)
    mf = mixdir / "07-next-steps.md"
    mf.write_bytes(
        "## P0 — 必须做\r\n".encode("utf-8") +
        "- [ ] **【P0·待办 丁（r49 登记）】** 锚点在这一行（本行行尾是纯 LF）\n".encode("utf-8") +
        "- [ ] **【P0·待办 戊（r49 登记）】** 同元素里的另一条目（行尾 CRLF）\r\n".encode("utf-8") +
        "- [ ] **【P0·待办 己（r49 登记）】** 尾条目\r\n".encode("utf-8"))
    mb = mf.read_bytes()
    rmix = run(["--vault", str(mf.parent.parent), "--key", "待办 丁", "--round", "49",
                "--verdict", "执行完毕｜混合行尾卷错位复现桩"])
    after = mf.read_bytes().decode("utf-8").split(chr(10))
    hit = [l for l in after if "r49 裁决=" in l]
    ck("t9 混合行尾卷：标记必须落在**锚点自己那一行**（不得并到同元素的另一条目）",
       rmix.returncode == 0 and len(hit) == 1 and "待办 丁" in hit[0],
       " ｜ ".join(x[:52] for x in hit) or "无标记")
    ck("t10 混合行尾卷：同元素内另一条目（待办 戊）必须零污染，且原文其余字节逐字不动",
       all("待办 戊" not in l or "裁决=" not in l for l in after)
       and mf.read_bytes().startswith(mb[:40])
       and mf.read_bytes().count(b"\r\n") == 3,
       "CRLF=%d" % mf.read_bytes().count(b"\r\n"))

    fails = [x for x in RESULTS if not x[0]]
    print("\n夹具合计: %d 项，通过 %d，失败 %d"
          % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    print("[GATE:fixture-fail]" if fails else "[GATE:fixture-pass]")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
