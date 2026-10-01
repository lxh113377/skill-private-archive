#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r101 收口：跑 27 门 → 用实测结论回填报告里那条「未做复跑」的前置声明 → README/07 加索引行 → 逐个 pathspec 提交并推。"""
import io
import json
import os
import re
import subprocess
import sys

REPO = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
RPT = "06-benchmark/全量对标报告_r101_名册优质半边与同事实单尺_2026-10-02.md"
PY = "C:/Program Files/Python312/python.exe"


def sh(args, timeout=600):
    p = subprocess.run(args, cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def patch(path, old, new, must=True):
    s = io.open(path, encoding="utf-8", newline="").read()
    n = s.count(old)
    if n != 1:
        if must:
            sys.stderr.write("[ABORT] %s 锚点命中 %d（须==1）\n" % (path, n))
            return False
        return True
    io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    b = io.open(path, encoding="utf-8", newline="").read()
    if new not in b:
        sys.stderr.write("[ABORT] 读回缺失 %s\n" % path)
        return False
    return True


def main():
    env = dict(os.environ, PYTHONPYCACHEPREFIX=os.path.join(
        os.environ.get("TEMP", "."), "pycache_verify"))
    subprocess.run([PY, "05-exec/run_gates.py", "--json",
                    "06-benchmark/gate_run_r101.json"], cwd=REPO, env=env,
                   capture_output=True, text=True, timeout=900)
    doc = json.load(io.open(os.path.join(REPO, "06-benchmark/gate_run_r101.json"),
                            encoding="utf-8"))
    reds = [x["id"] for x in doc["gates"] if x["rc"] not in (0,)]
    line = ("③ 本轮 27 门实跑复算：%s（红门 id：%s）"
            % (doc["verdict_reason"], ", ".join(reds) if reds else "无"))
    ok = patch(os.path.join(REPO, RPT),
               "③ 本轮未做 27 门全量复跑（末次为 r100 的 FAIL=5，同因外部 +12）", line)
    print("[GATES]", doc["verdict"], doc["verdict_reason"], "| 报告边界行已按实测回填:", ok)

    if not patch(os.path.join(REPO, "README.md"), "- [全量对标报告_r100_",
                 "- [全量对标报告_r101_名册优质半边与同事实单尺_2026-10-02.md]"
                 "(06-benchmark/全量对标报告_r101_名册优质半边与同事实单尺_2026-10-02.md) — "
                 "同一指令第三次逐字重发⇒再整跑一轮。**名册只答了「高星」没答「优质」**："
                 "top-20 里 **7 席**被 SKILL.md<=3 的仓占掉（其一为 0 件），而 vercel-labs/skills、"
                 "mukul975/Anthropic-Cybersecurity-Skills(818 件) 等真技能仓被截在外面 ⇒ ROSTER_TOP_N 默认改 0（实测面全量入面）"
                 "+ 截断必须具名含星标（上轮只做到计数可见，dropped 语义还被我错定义成 pin 漏扫）；"
                 "新增 skill_bearing 分档，d1/d8/d9/d12 只在 23 个技能树上取分母。"
                 "**自抓同事实两把尺**（第一版档位谓词用「能否取到父目录 slug」而 non_skill_repos 用「有无 SKILL.md」⇒ "
                 "blader/humanizer 双档矛盾）改单尺后 skill 面 22→23，slug 缺失降格为另一件事实单列；"
                 "**再自抓 schema 号虚报**（r100 报告与提交说明写 v4，代码从未 bump，产物仍 r99-v3）本轮补到 r101-v5 并留痕。"
                 "夹具 38→**45 腿全过**；换装判定仍 0 件（新入面 818+50 件两仓逐族过 X-29 三门槛不成立）、卸载 0 件；"
                 "27 门复算与外部 +12 同因不动基线。报告=本行\n- [全量对标报告_r100_"):
        return 1
    # 注：此处刻意不做「若已存在则替换」的写法 —— 早期版本传了 old=新行前缀 + new=""，
    # 命中即会把 r101 摘要行整行删掉（删除语义被伪装成幂等检查）。改为只判存在再决定插入。
    s = io.open(os.path.join(REPO, "memory", "07-next-steps.md"),
                encoding="utf-8", newline="").read()
    if "- **2026-10-02（第 101 轮" not in s:
        summ = ("- **2026-10-02（第 101 轮 r101，同一指令第三次逐字重发⇒再整跑；名册补「优质」半边 + 同事实单尺返工）** — "
                "① 实测 20 席名册里 **7 席** 为 SKILL.md<=3 的仓（含 1 席为 0 件），真技能仓被 top-20 截在外面 "
                "⇒ 用户「高星且优质」只实现了前半句：ROSTER_TOP_N 默认 0 全量入面 + 截断必须具名含星标 + skill_bearing 分档"
                "（d1/d8/d9/d12 只在 23 个技能树取分母）。② **自抓同事实两把尺**：第一版档位谓词=「能否取到父目录 slug」，"
                "而 non_skill_repos=「有无 SKILL.md」⇒ blader/humanizer 双档矛盾；改单尺后 skill 面 22→23，"
                "slug 缺失降为另一件事实单列 slugless_skill_repos。③ **schema 号虚报补账**：r100 报告与提交说明写 v4 而代码从未 bump"
                "（产物仍 r99-v3）⇒ 声明先于证据，本轮 bump 到 twelve-face-r101-v5 并在 r101 报告 §0/§4 留痕（r100 原文按 R241 不改）。"
                "④ 夹具 38→**45 腿全过**（含根级 SKILL.md 不得降档、truncated 具名、[]≠None 三向）；同缓存离线复算 "
                "state=matched / skill_face_n=23 / humanizer=skill_tree。⑤ 换装判定 0 件、卸载 0 件（新入面 mukul975 818 件与 OpenViking 50 件"
                "逐族过 X-29 三门槛不成立）；r100 装的两件原状。⑥ 三闸复算：GS 脏 96、??=26（24 他人件）⇒ rebuild 前提仍未开窗；"
                "retired_face 保持绿（无第四次回流）；27 门红门全为外部 +12 棘轮同因，不动基线。"
                "报告=06-benchmark/全量对标报告_r101_名册优质半边与同事实单尺_2026-10-02.md\n")
        old = "- **2026-10-02（第 100 轮 r100"
        assert s.count(old) == 1
        io.open(os.path.join(REPO, "memory", "07-next-steps.md"), "w",
                encoding="utf-8", newline="").write(s.replace(old, summ + old, 1))
        print("[07] r101 摘要行已插并读回:",
              ("- **2026-10-02（第 101 轮" in io.open(
                  os.path.join(REPO, "memory", "07-next-steps.md"),
                  encoding="utf-8", newline="").read()))

    files = ["05-exec/r96_twelve_face.py", "05-exec/r101_patch.py", "05-exec/r101_patch2.py",
             "05-exec/r101_finalize.py",
             "05-exec/r96_gh_raw.json",
             "06-benchmark/twelve_face_r101_2026-10-02.json",
             "06-benchmark/gate_run_r101.json", RPT,
             "README.md", "memory/07-next-steps.md",
             "06-benchmark/gate_runs.jsonl", "06-benchmark/input_pins.jsonl"]
    missing = [f for f in files if not os.path.exists(os.path.join(REPO, f))]
    if missing:
        sys.stderr.write("[ABORT] 缺件 %s\n" % missing)
        return 1
    sh(["git", "add", "--"] + files)
    _, num = sh(["git", "diff", "--cached", "--numstat"])
    print("[STAGED]\n" + num.strip())
    rc, out = sh(["git", "commit", "-q", "-m",
                  "feat(r101): 名册补优质半边(全量入面+截断具名+skill_bearing分档)+同事实单尺返工;夹具38->45\n\n"
                  "- 一手实测: top-20 里 7 席被 SKILL.md<=3 的仓占用(1 席为 0 件),真技能仓被截在外面 => 用户「高星且优质」只做了前半句\n"
                  "- ROSTER_TOP_N 默认 0(全量入面);top_n>0 时 truncated 具名含星标,[]与None可区分(「没截」≠「没看」)\n"
                  "- 自抓两把尺: 档位谓词第一版用父目录slug可派生性而 non_skill_repos 用 SKILL.md 存在性 => humanizer 双档矛盾;"
                  "改单尺后 skill_face 22->23,slug 缺失另记 slugless_skill_repos 不改档\n"
                  "- 自抓 schema 号虚报: r100 报告与提交说明写 v4 而代码从未 bump(产物仍 r99-v3)=> 本轮 bump twelve-face-r101-v5 并留痕\n"
                  "- 换装 0 件/卸载 0 件: 新入面 mukul975(818 SKILL.md)与 OpenViking(50)逐族过 X-29 三门槛不成立\n"
                  "- 三闸复算 GS 脏96 ??=26(24 他人件)=>注册表 rebuild 前提未开窗;retired_face 保持绿;27 门红全为外部+12 不动基线"])
    print("[COMMIT rc=%d] %s" % (rc, out.strip()[:300]))
    sh(["git", "push", "origin", "HEAD:main"])
    _, ls = sh(["git", "ls-remote", "origin", "main"])
    _, hh = sh(["git", "rev-parse", "HEAD"])
    print("[PUSH] remote=%s local=%s" % (ls.split()[0][:10] if ls.strip() else "-", hh.strip()[:10]))
    return 0 if ls.strip() and ls.split()[0] == hh.strip() else 1


if __name__ == "__main__":
    sys.exit(main())
