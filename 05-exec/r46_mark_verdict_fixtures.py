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
    # r125（R123-4）：默认落点已从 05-exec/mark_backup 改为 _trash/mark_backup_rNN（该目录
    # 在 r57 清过 20 份后无声攒到 40 份，且被 root_face 的 f12 二级盲区腿判红）。
    # 本腿的本意自始至终是「**备份不落记忆卷**」（r35 落点教训），不是「必须落 mark_backup」；
    # 故改判「备份落在受管回收区、且不落记忆卷、也不散在 vault 根」。落点只放宽到 _trash，
    # 不放宽「备份必须存在」这一条 —— 备份本身仍是硬要求。
    bdir = uniq / "_trash" / "mark_backup_r46"
    _any_bak = list(uniq.rglob("*.bak"))
    ck("t5 写入自带备份且**不落记忆卷**（r125：默认落 _trash，受管回收区；记忆卷与 vault 根均无）",
       bool(list(bdir.glob("*.bak"))) and not list((uniq / "memory").rglob("*.bak"))
       and not list(uniq.glob("*.bak"))
       and all("_trash" in p.relative_to(uniq).parts for p in _any_bak),
       "bdir_bak=%d any_bak=%s" % (len(list(bdir.glob("*.bak"))),
                                 [str(p.relative_to(uniq)) for p in _any_bak][:6]))

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

    # ---- t11–t14（r51 W-19）：note 模式 —— 05/06/08 的状态回写走同一入口 ----
    ndir = Path(tempfile.mkdtemp(prefix="r51_nv_")) / "memory"
    ndir.mkdir(parents=True)
    nf = ndir / "06-constraints.md"
    nf.write_bytes("## 已知 Bug\r\n- [BUG] **甲项 状态：**未修复**（含 - [x] 之外的普通行）** 尾\r\n\r\n- [x] 乙项\r\n".encode("utf-8"))
    nb = nf.read_bytes()
    rn = run(["--mode", "note", "--vault", str(ndir.parent), "--file", str(nf), "--key", "甲项", "--round", "51",
              "--note", "归因校正注：原句未经核验"])
    nlines = nf.read_bytes().decode("utf-8").split(chr(10))
    hitn = [l for l in nlines if "r51 补记：" in l]
    ck("t11 note 模式可写非勾选项行（05/06/08 回写同一入口，禁再手写补丁脚本）",
       rn.returncode == 0 and len(hitn) == 1 and "甲项" in hitn[0], (rn.stdout + rn.stderr)[-170:])
    ck("t12 note 模式幂等靠拒绝：同轮二次补记 ⇒ 拒写且字节不变",
       run(["--mode", "note", "--vault", str(ndir.parent), "--file", str(nf), "--key", "甲项", "--round", "51", "--note", "再来一次"]).returncode != 0
       and nf.read_bytes().count("r51 补记：".encode("utf-8")) == 1, nf.read_bytes().count(b"r51") )
    ck("t13 note 模式歧义拒写：锚点命中 2 行 ⇒ 不写（禁挑第一行）",
       run(["--mode", "note", "--vault", str(ndir.parent), "--file", str(nf), "--key", "项", "--round", "52", "--note", "x"]).returncode != 0
       and nf.read_bytes().count(b"r52") == 0, (run(["--mode", "note", "--vault", str(ndir.parent), "--file", str(nf), "--key", "项",
                                                     "--round", "52", "--note", "x"]).stdout or "")[-140:])
    ck("t14 note 模式 0 命中不得退化成追加：锚点不存在 ⇒ 拒写且文件字节不动",
       run(["--mode", "note", "--vault", str(ndir.parent), "--file", str(nf), "--key", "根本不存在的锚点", "--round", "53",
            "--note", "x"]).returncode != 0 and nf.read_bytes() != b"" and nf.read_bytes().count(b"r53") == 0,
       nf.read_bytes().count(b"r53"))

    # ---- t15/t16（r163，R163-5）：verdict 模式给 --note，理由必须**真的落盘** ----
    # 一手事故：本轮四条裁决都用 `--verdict X --note 长理由` 调用，四条全打 [MARK:OK] 且读回
    # 验证通过 —— 但实现里 `body_text = args.verdict if mode==verdict else args.note` ⇒ verdict
    # 模式下 --note **根本不参与拼接**，长理由蒸发且零告警（X-8：return 了成功却没写盘的东西）。
    # 取证：写完后 grep 理由正文（70.8% / 命中 15 处 / autoregen 件名）在 07 卷 0 命中。
    sdir = Path(tempfile.mkdtemp(prefix="r163_note_")) / "memory"
    sdir.mkdir(parents=True)
    sf = sdir / "07-next-steps.md"
    sf.write_text("- [ ] **【P0·待办 庚（r163 登记）】** 唯一正文\n", encoding="utf-8", newline="")
    REASON = "误报率实测 70.8% 且 autoregen 件为证"
    r15 = run(["--vault", str(sdir.parent), "--key", "待办 庚", "--round", "163",
               "--verdict", "执行（终局）", "--note", REASON])
    body15 = sf.read_text(encoding="utf-8")
    ck("t15 verdict 模式带 --note：理由必须原样落盘（禁 [MARK:OK] 却把 note 丢掉）",
       r15.returncode == 0 and REASON in body15,
       "rc=%d ｜ 落盘含理由=%s ｜ %s" % (r15.returncode, REASON in body15, (r15.stdout or "")[-120:]))
    ck("t16 verdict 模式带 --note：裁决标记与理由必须在**同一物理行**（禁拆两行凑绿）",
       (lambda ls: any(("r163 裁决=" in l and REASON in l) for l in ls))(body15.splitlines()),
       " ｜ ".join(l[:60] for l in body15.splitlines() if "裁决=" in l) or "无标记")

    # ---- m1（#48 变异对照）：把旧行为注回（verdict 模式丢弃 --note）⇒ t15/t16 必须转红 ----
    #    恒绿的夹具等于没测：本条证明 t15/t16 的绿来自修复本身，不是断言写松了。
    src = (HERE / "r46_mark_verdict.py").read_text(encoding="utf-8")
    old_expr = "body_text = _one_line(args.verdict)"
    md = Path(tempfile.mkdtemp(prefix="r163_mut_"))
    (md / "memory").mkdir(parents=True)
    mut_tool = md / "r46_mark_verdict_mut.py"
    if old_expr in src:
        # 注入「丢弃 note」的旧语义
        mut_src = src.replace(
            "        _nt = _one_line(args.note)\n        if _nt:",
            "        _nt = ''  # MUTATED: 旧行为，丢弃 note\n        if _nt:")
        mut_tool.write_text(mut_src, encoding="utf-8", newline="")
        mf = md / "memory" / "07-next-steps.md"
        mf.write_text("- [ ] **【P0·待办 辛（r163 登记）】** 唯一正文\n", encoding="utf-8", newline="")
        mr = subprocess.run([sys.executable, str(mut_tool), "--vault", str(md), "--key", "待办 辛",
                             "--round", "163", "--verdict", "执行（终局）", "--note", REASON],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", cwd=str(HERE.parent))
        mbody = mf.read_text(encoding="utf-8")
        ck("m1 变异对照：注回「丢弃 note」旧行为 ⇒ 理由必须再次消失（证明 t15 的绿来自修复）",
           REASON not in mbody, "rc=%d ｜ 含理由=%s" % (mr.returncode, REASON in mbody))
    else:
        ck("m1 变异对照：找不到注入锚点（判据实现已变，须同步更新变异体）", False, "anchor missing")


    # ---- t17-t22 + m2（r214，对标改造 H-2 / R211-2）：备份簇 keep 收敛的双向证据 ----------
    # 一手规模（本轮实测，非估算）：_trash 内 .bak 431 件 / 49,135,862B；最大单簇
    # _trash/r163_mark_backup 100 份；近 3 小时新增 11 份 =>「越认真裁 => 越脏」，
    # L4 备份簇项与 21 天红线只涨不消（八维对标的量化落点）。
    # 锁五件事：超 keep 必收敛 / 只动旧份 / 未超 keep 一律不动 / 非法阈值不清空 /
    #   冷却期内一份都不动（防毁并行会话刚写的唯一旧态副本）。
    # 夹具置 HANDOFF_RECYCLE_NO_BIN=1 强制走 _trash：否则测试垃圾进用户真实回收站
    #   （recycle.py 的该开关正是为此而设 —— 治噪声的工具自己别造噪声）。
    os.environ["HANDOFF_RECYCLE_NO_BIN"] = "1"
    import time as _time

    def _seed(dirp, stem, n, age_day=30):
        dirp.mkdir(parents=True, exist_ok=True)
        names = []
        for k in range(n):
            q = dirp / (stem + ".r214_" + "%06d" % k + ".bak")
            q.write_text("old" + str(k), encoding="utf-8")
            old = _time.time() - age_day * 86400.0
            os.utime(str(q), (old, old))        # 过冷却期，才可被处置
            names.append(q.name)
        return sorted(names)

    def _mk_vault(label):
        d = Path(tempfile.mkdtemp(prefix="r214_"))
        (d / "memory").mkdir(parents=True, exist_ok=True)
        (d / "memory" / "07-next-steps.md").write_text(
            "- [ ] **【P0·待办 " + label + "（r214 登记）】** 唯一正文" + chr(10),
            encoding="utf-8", newline="")
        return d

    def _hms(name):
        return name.rsplit("_", 1)[1][:6]

    d17 = _mk_vault("甲")
    c17 = d17 / "_trash" / "mark_backup_r214"
    pre17 = _seed(c17, "07-next-steps.md", 6)          # 6 份 > keep=3 => 该收敛
    r17 = run(["--vault", str(d17), "--key", "待办 甲", "--round", "214",
               "--verdict", "执行（收敛验证）"])
    o17 = (r17.stdout or "") + (r17.stderr or "")
    post17 = sorted(p.name for p in c17.glob("*.bak"))
    ck("t17 超 keep => 同簇收敛到 keep 份以内，且 [BACKUP-TRIM] 行必须打印（禁静默）",
       r17.returncode == 0 and len(post17) <= 4 and "[BACKUP-TRIM]" in o17,
       "rc=%s 前=%d 后=%d ｜ %s" % (r17.returncode, len(pre17), len(post17), o17[-260:]))
    gone17 = [n for n in pre17 if n not in post17]
    surv17 = [n for n in post17 if n in pre17]
    # 注（r214 变异实测）：t18 是**必要但不充分**的 —— 受害者数 <= max_move 时全部被收，
    # 遍历顺序无从体现，变异态（去掉 reversed）下 t18 照样 PASS。真正鉴别顺序的是 t23
    # （受害者 > max_move）。别把 t18 当成「顺序已锁」，否则会重演「判据读不到该形态」。
    ck("t18 收敛只动旧份：被回收的最大时刻必须早于存活的最小时刻（留最新，非随机删）",
       bool(gone17) and bool(surv17) and max([_hms(x) for x in gone17]) < min([_hms(x) for x in surv17]),
       "gone=%s surv=%s" % (gone17[:4], surv17[:4]))
    ck("t21 本轮刚写的回滚副本不被回收（exclude 生效：seed 里最旧那份被收，新的留下）",
       "r214_000005" not in " ".join(gone17) and bool(gone17),
       "gone=%s" % (gone17[:6],))

    # 冷却期：全部在 age 内 => 一份都不许动（并行会话刚写的副本受保护）
    d22 = _mk_vault("乙")
    c22 = d22 / "_trash" / "mark_backup_r214"
    pre22 = _seed(c22, "07-next-steps.md", 6, age_day=0)     # 刚写的，冷却中
    r22 = run(["--vault", str(d22), "--key", "待办 乙", "--round", "214", "--verdict", "执行"])
    o22 = (r22.stdout or "") + (r22.stderr or "")
    post22 = sorted(p.name for p in c22.glob("*.bak"))
    ck("t22 冷却期内（bak_age_days）=> 一份都不动，且打印回收=0 与冷却中计数（禁静默隐身）",
       r22.returncode == 0 and all(b in post22 for b in pre22) and "回收=0" in o22
       and "冷却中=" in o22,
       "before=%d after=%d ｜ %s" % (len(pre22), len(post22), o22[-260:]))

    d19 = _mk_vault("丙")
    c19 = d19 / "_trash" / "mark_backup_r214"
    pre19 = _seed(c19, "07-next-steps.md", 2)               # 2 + 本次 1 <= keep => 不动
    r19 = run(["--vault", str(d19), "--key", "待办 丙", "--round", "214", "--verdict", "执行"])
    o19 = (r19.stdout or "") + (r19.stderr or "")
    post19 = sorted(p.name for p in c19.glob("*.bak"))
    ck("t19 未超 keep => 回收=0 且原有备份一个不少（禁顺手多删）",
       r19.returncode == 0 and all(b in post19 for b in pre19) and "回收=0" in o19,
       "before=%d after=%d ｜ %s" % (len(pre19), len(post19), o19[-260:]))

    d20 = _mk_vault("丁")
    c20 = d20 / "_trash" / "mark_backup_r214"
    pre20 = _seed(c20, "07-next-steps.md", 5)
    r20 = run(["--vault", str(d20), "--key", "待办 丁", "--round", "214",
               "--verdict", "执行", "--backup-keep", "0"])
    o20 = (r20.stdout or "") + (r20.stderr or "")
    post20 = sorted(p.name for p in c20.glob("*.bak"))
    ck("t20 非法阈值 keep=0 => 原有份数一个都不减（禁把配置写错变成全员清空）",
       all(b in post20 for b in pre20) and "非法 keep" in o20,
       "before=%d after=%d ｜ %s" % (len(pre20), len(post20), o20[-260:]))

    # t23 上限只吃最旧：9 份 seed + keep=3 => 受害者 6 份 > max_move=5 ⇒ 必须留下「最新的那位本应收走的」
    # 这条腿是顺序判据：修之前遍历从较新受害者开始收，最旧那份（_000000）反而活下来 => 本腿转红。
    d23 = _mk_vault("己")
    c23 = d23 / "_trash" / "mark_backup_r214"
    pre23 = _seed(c23, "07-next-steps.md", 9)          # 全部 30 天前，都过冷却
    r23 = run(["--vault", str(d23), "--key", "待办 己", "--round", "214", "--verdict", "执行"])
    o23 = (r23.stdout or "") + (r23.stderr or "")
    post23 = sorted(p.name for p in c23.glob("*.bak"))
    ck("t23 单轮上限只收最旧（最旧的已收走、最新那位受害者因上限留下，且打印超上限=1）",
       not any("r214_000000" in n for n in post23)
       and any("r214_000005" in n for n in post23)
       and "超上限=1" in o23,
       "before=%d after=%d ｜ %s" % (len(pre23), len(post23), o23[-260:]))

    src46 = (HERE / "r46_mark_verdict.py").read_text(encoding="utf-8")
    MUT = "            _ts = trim_backup_cluster("
    if MUT in src46:
        dm = _mk_vault("戊")
        mt = dm / "r46_mut.py"
        # 变异体：把收敛调用换成「返回全零统计」的 lambda —— 插进去的代码一个引号都不带，
        # 免得再踩「JS 模板串 / Python 字面量」双层转义（本仓 §9.18 已记三起）。
        stub = ('            _ts = (lambda *a, **k: dict(attempted=0, recycled=0, skipped_tracked=0, '
                'failed=0, kept=0, cooled=0, capped=0, cluster_before=0, stem_src="mut", disabled=True, '
                'errors=[]))(')
        mt.write_text(src46.replace(MUT, stub, 1), encoding="utf-8", newline="")
        cm = dm / "_trash" / "mark_backup_r214"
        _seed(cm, "07-next-steps.md", 6)
        mm = subprocess.run([sys.executable, str(mt), "--vault", str(dm), "--key", "待办 戊",
                             "--round", "214", "--verdict", "执行"],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", cwd=str(HERE.parent))
        om = (mm.stdout or "") + (mm.stderr or "")
        left = len(list(cm.glob("*.bak")))
        ck("m2 变异：摘掉收敛 => 6 份原样留着且打印回收=0（证 t17 的绿来自收敛本身）",
           left >= 6 and "回收=0" in om, "left=%d ｜ %s" % (left, om[-180:]))
    else:
        ck("m2 变异：找不到收敛调用锚点（实现已变，须同步更新变异体）", False, "anchor missing")


    # ---- t24~t26 + m3（r290 / R271-2）：⑧ 第 >=2 次到期禁再挂账的判别力 ----------
    def mk_defer_vault(tmpx, seed_marker):
        d = tmpx / "defer"
        (d / "memory").mkdir(parents=True, exist_ok=True)
        fx = d / "memory" / "07-next-steps.md"
        body = "- [ ] **待办 庚（r44 登记，P1）** 正文庚"
        fx.write_text((body + seed_marker + "\n") if seed_marker else (body + "\n"),
                      encoding="utf-8", newline="")
        return fx

    import shutil as _sh
    seed = "【r45 裁决=挂账至 r46｜首次越线】"
    fx24 = mk_defer_vault(tmp, seed)
    r24 = run(["--vault", str(tmp / "defer"), "--key", "待办 庚", "--round", "47",
               "--verdict", "挂账至 r48｜再延一轮"])
    o24 = (r24.stdout or "") + (r24.stderr or "")
    ck("t24 先前挂账目标轮已过 + 本轮仍挂账 → ⑧ 拒写且台账未被改",
       r24.returncode != 0 and "⑧" in o24 and seed in fx24.read_text(encoding="utf-8")
       and "r47 裁决=" not in fx24.read_text(encoding="utf-8"), o24[-170:])

    fx25 = mk_defer_vault(tmp, "")
    r25 = run(["--vault", str(tmp / "defer"), "--key", "待办 庚", "--round", "47",
               "--verdict", "挂账至 r48｜首次越线"])
    ck("t25 首轮挂账（无更早标记）→ 放行，⑧ 不误伤正常延期",
       r25.returncode == 0 and "r47 裁决=挂账" in fx25.read_text(encoding="utf-8"),
       ((r25.stdout or "") + (r25.stderr or ""))[-160:])

    fx26 = mk_defer_vault(tmp, "【r45 裁决=挂账至 r99｜目标轮尚远】")
    r26 = run(["--vault", str(tmp / "defer"), "--key", "待办 庚", "--round", "47",
               "--verdict", "挂账至 r48｜同条二次但目标轮未到"])
    ck("t26 先前挂账的目标轮未到（r99 > 本轮 47）→ 放行（判据只拦过期挂账）",
       r26.returncode == 0, ((r26.stdout or "") + (r26.stderr or ""))[-160:])

    fx27 = mk_defer_vault(tmp, seed)
    r27 = run(["--vault", str(tmp / "defer"), "--key", "待办 庚", "--round", "47",
               "--verdict", "挂账至 r48｜带逃生门", "--allow-repeat-deferral"])
    ck("t27 逃生门 --allow-repeat-deferral 可放行且留痕（⑧ 不是死闸）",
       r27.returncode == 0 and "r47 裁决=挂账" in fx27.read_text(encoding="utf-8"),
       ((r27.stdout or "") + (r27.stderr or ""))[-160:])

    MUT8 = "if RE_DEFERRAL_TEXT.search(args.verdict or \"\") and not args.allow_repeat_deferral:"
    src28 = TOOL.read_text(encoding="utf-8")
    if MUT8 in src28:
        md = tmp / "mut8"
        (md / "memory").mkdir(parents=True, exist_ok=True)
        mt = md / "memory" / "07-next-steps.md"
        mt.write_text("- [ ] **待办 庚（r44 登记，P1）** 正文庚【r45 裁决=挂账至 r46｜首次越线】\n",
                      encoding="utf-8", newline="")
        stub8 = "if False:"
        mut = md / "tool8.py"
        mut.write_text(src28.replace(MUT8, stub8, 1), encoding="utf-8", newline="")
        # 变异体必须**直接调用**：夹具里的 run() 会把正式 TOOL 路径前置，于是变异体文件名被
        # 当成多余位置参数 ⇒ argparse 报 unrecognized arguments（实测 rc=2，是假红不是判别力）。
        r28 = subprocess.run([sys.executable, str(mut), "--vault", str(md), "--key", "待办 庚",
                              "--round", "47", "--verdict", "挂账至 r48｜变异体"],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", cwd=str(HERE.parent))
        ck("m3 变异：摘掉 ⑧ → 同一输入被放行（证 t24 的绿来自 ⑧ 本身）",
           r28.returncode == 0 and "r47 裁决=挂账" in mt.read_text(encoding="utf-8"),
           ((r28.stdout or "") + (r28.stderr or ""))[-170:])
    else:
        ck("m3 变异：找不到 ⑧ 调用锚点（实现已变，须同步更新变异体）", False, "anchor missing")
    fails = [x for x in RESULTS if not x[0]]
    print("\n夹具合计: %d 项，通过 %d，失败 %d"
          % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    print("[GATE:fixture-fail]" if fails else "[GATE:fixture-pass]")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
