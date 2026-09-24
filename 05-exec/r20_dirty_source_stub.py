# -*- coding: utf-8 -*-
r"""r20_dirty_source_stub.py — rule_editor「写前脏源检测」隔离桩（TDD：先跑红再实现）。

被测判据（本仓两次实测复现的根因）：
  `rule_editor commit` 按**整文件** `git add`，若该文件在本次编辑**之前**就已带着
  他人未提交改动，就会被一并写进我的 commit（归属失真）。
  · 复现①受管根 `f6f5b0c`（2026-09-23 r5）：我把并行会话在 `splitvol.py` 的在途 1 行带走；
  · 复现②受管根 `4b75d80`（2026-09-24 r19b）：并行会话把我 `contract.md` 的在途 hunks 带走。
  既有 R229 只回答「我写完以后有没有被人再改」，不回答「我动手以前它脏不脏」⇒ 本判据补后一半。

判据（纯函数 `_multi_author_findings(rel, head_blob_val, pre_sha, chain)`）：
  仅当「动手前磁盘指纹 != HEAD 指纹」且「该磁盘指纹不在本工具写入链上」时报多源共存；
  四态必须都测（干净基座 / 自有链上 / 他人在途 / HEAD 不可读）。

退出码：0 全过 / 1 有失败 / 2 环境不满足（受管根不可读）。
"""

import importlib.util
import os
import subprocess
import sys

RE = r"D:\global_skills\A-memory-start\references\rule_editor.py"
if not os.path.isfile(RE):
    print("SKIP: rule_editor.py 不可读")
    raise SystemExit(2)
spec = importlib.util.spec_from_file_location("rule_editor", RE)
re_mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(re_mod)
except Exception as e:
    print("SKIP: 导入 rule_editor 失败: %s" % e)
    raise SystemExit(2)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

R = []


def ck(name, cond, detail=""):
    R.append(bool(cond))
    print("%s %-58s %s" % ("PASS" if cond else "FAIL", name, "" if cond else str(detail)[:170]))


def main():
    f = getattr(re_mod, "_multi_author_findings", None)
    if f is None:
        ck("RED 前置：_multi_author_findings 已实现", False,
           "函数不存在 —— 本次运行即 TDD 红阶段（先看失败，再写实现）")
        print("\n合计 %d 项，通过 0，失败 %d" % (len(R), len(R)))
        print("[GATE:stub-fail]")
        return 1
    ck("_multi_author_findings 可调用", callable(f))

    # ① 干净基座：动手前磁盘 == HEAD ⇒ 不报
    ck("c1 干净基座（pre_sha == HEAD 指纹）不报",
       f("x/SKILL.md", "aaa111", "aaa111", []) == [], f("x/SKILL.md", "aaa111", "aaa111", []))
    # ② 自有链上：先前 --no-commit 写的，链里记着 post_sha ⇒ 不误报（r19b 双笔收口场景）
    chain = [{"rel": "x/SKILL.md", "post_sha": "bbb222"}]
    ck("c2 自有写入链上的中间态不误报",
       f("x/SKILL.md", "aaa111", "bbb222", chain) == [], f("x/SKILL.md", "aaa111", "bbb222", chain))
    # ③ 他人在途：脏但不在链上 ⇒ 必须报
    out = f("x/SKILL.md", "aaa111", "ccc333", chain)
    ck("c3 他人在途改动必须报（本次要防的形态）", len(out) == 1 and "x/SKILL.md" in out[0], out)
    ck("c4 告警文案含可执行处置（逃生门名 + 逐文件比对）",
       any("--allow-dirty-source" in m for m in out), out)
    # ⑤ HEAD 不可读（新文件 / 仓库异常）⇒ 不猜测，不报
    ck("c5 HEAD 不可读时不报（不误伤新文件）",
       f("new/File.md", None, "ddd444", []) == [])
    ck("c6 磁盘指纹读不到（空串）时不报（不误报为多源）",
       f("x/SKILL.md", "aaa111", "", []) == [])
    # ⑦ 链按 rel 隔离：别的文件的记录不得为本文件背书
    ck("c7 写入链按文件隔离（防跨文件背书）",
       len(f("y/SKILL.md", "aaa111", "ccc333", chain)) == 1)

    # ---- 层 b′ 真实数据正样本：受管根现有他人在途文件必须被点名（只读，不 stage 不 commit）----
    dirty = subprocess.run(["git", "-c", "core.quotepath=false", "-C", r"D:\global_skills",
                            "status", "--porcelain"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120).stdout.splitlines()
    mfiles = [l[3:].strip() for l in dirty if l.startswith(" M ")]
    if not mfiles:
        ck("层b′ 存在他人在途文件可测", False, "受管根当前 0 条 M，判据正样本待复测（不得当通过）")
    else:
        hits = 0
        for rel in mfiles[:12]:
            head = re_mod._head_blob(rel)
            pre = re_mod._file_sha256(os.path.join(re_mod.GIT_ROOT, rel))
            chain_b = re_mod.load_write_chain() if hasattr(re_mod, "load_write_chain") else []
            if f(rel, head, pre, chain_b):
                hits += 1
        ck("层b′ 真实他人在途文件被点名（≥1）", hits >= 1, "hits=%d/%d" % (hits, len(mfiles[:12])))
        # 生效路径对照：本工具刚写过的文件（链上有记录）不应被点名。
        # ⚠️ 链上有记录才构成有效对照；若该文件是被「升级前的旧版 rule_editor」写的（链空），
        #    必须显式标 SKIP，禁止把「无记录所以不报」当成通过（R220 假通过同族）。
        mine = "A-memory-start/references/rule_editor.py"
        head = re_mod._head_blob(mine)
        pre = re_mod._file_sha256(os.path.join(re_mod.GIT_ROOT, mine))
        chain_b = re_mod.load_write_chain() if hasattr(re_mod, "load_write_chain") else []
        on_chain = [r for r in chain_b if r.get("rel") == mine and r.get("post_sha") == pre]
        flagged = f(mine, head, pre, chain_b)
        if not on_chain and head != pre:
            print("SKIP %-56s 该文件由升级前的旧版 rule_editor 写入，链上无记录 ⇒ 本例不构成有效对照"
                  "（生效路径改由 commit 实跑验证并另行留证）" % "层b′ 对照组（链上自有记录不误报）")
        else:
            ck("层b′ 对照组：本工具写入链上的文件不误报", flagged == [],
               "head=%s pre=%s 链=%d 条 %s" % (head, pre, len(chain_b), flagged))
    ck("write_text 会留链（load_write_chain 可调用）", hasattr(re_mod, "load_write_chain"))

    bad = [i for i, ok in enumerate(R, 1) if not ok]
    print("\n合计 %d 项，通过 %d，失败 %d" % (len(R), len(R) - len(bad), len(bad)))
    print("[GATE:stub-pass]" if not bad else "[GATE:stub-fail] 用例 %s" % bad)
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
