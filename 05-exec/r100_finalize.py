#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r100 收口：修 07 被 shell 命令替换掏空的摘要行 + 第三次回流处置 + 逐个 pathspec 提交。"""
import io
import os
import re
import subprocess
import sys

REPO = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
P07 = os.path.join(REPO, "memory", "07-next-steps.md")
MARK = "- **2026-10-02（第 100 轮 r100"


def sh(args, cwd=None):
    p = subprocess.run(args, cwd=cwd or REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    # ---- 1. 掏空探测：命令替换会把反引号片段整段吃掉，留「空格紧跟全角标点」状空洞
    s = io.open(P07, encoding="utf-8", newline="").read()
    lines = [l for l in s.splitlines() if l.startswith(MARK)]
    if len(lines) != 1:
        sys.stderr.write("[ABORT] r100 摘要行命中 %d 条（须==1）\n" % len(lines))
        return 1
    bad = re.findall(r"[ ：]\s*(?=[，。；、）｜])|``|\(\)", lines[0])
    holes = len(re.findall(r"[ \u4e00-\u9fff]（?）", lines[0]))
    print("现状：r100 行长度=%d 疑洞标记=%d 空括号=%d" % (len(lines[0]), len(bad), holes))
    # 掏空判据：整行不该短于同族 r99 行的 60%，且必须仍含三个关键结论词
    r99 = [l for l in s.splitlines() if l.startswith("- **2026-10-02（第 99 轮 r99")]
    need = ("ROSTER" not in lines[0], "换装" not in lines[0], "BLOCKED" not in lines[0])
    too_short = r99 and len(lines[0]) < 0.6 * len(r99[0])
    if any(need) or too_short or holes or bad:
        fixed = ("- **2026-10-02（第 100 轮 r100，同一指令逐字重发⇒完整再整跑；对手名册改测量派生 + 两件真换装）** — "
                 "① **本轮翻转 r99 结论**：ROSTER 原为源码手抄 10 仓，而同工具同轮 search_face 实测前 25 名里 **15 仓从未进面**"
                 "（140497★ awesome-llm-apps、108698★ caveman、63335★ last30days-skill 皆在外）⇒ X-26 禁把手抄清单当扫描分母在对手面复发，"
                 "「换装 0 件」实际只在约四成人口上成立。"
                 "② 名册改由 derive_roster 现算 top-20 + roster_face 四态（含 UNVERIFIED_stale_cache 防旧缓存冒充派生面），夹具 25 腿→**38 腿全过**"
                 "（取值：python 05-exec/r96_twelve_face.py --selftest）。"
                 "③ 扩面后本地缺失 123 个 slug 逐族过 X-29 三门槛 ⇒ **装入 commit-archaeologist 与 scope-creep-detector**"
                 "（各 4 文件齐装：SKILL.md、README、scripts、references；两脚本 ast.parse 过；无 shell=True；平台当轮即列出=可加载行为回执）；"
                 "**卸载 0 件**（属缺口补件，无更差的对应本地件，不做无对象删除）。"
                 "④ 两次自抓假干净：审计用 glob 大括号不展开⇒取到 0 文件却报 0 命中（改 os.walk 并印 scanned_face=8）；"
                 "补丁一漏清 ROSTER 使用点⇒fetch_remote NameError 而夹具 35/35 全绿（补 3 条主链接线腿，Step 2.7 第 11 条第三次现形）。"
                 "⑤ 注册表 rebuild 判 **BLOCKED（实测非推断）**：受管根 ?? 计 26 条含 24 个他人未入库件，全量重生必致注册表⇄BGE⇄skill_content 三方脱节；"
                 "前提=可复算命令 python C:/Users/37533/Desktop/workspace/焚诀/eval/build_registry.py --dry-run。"
                 "⑥ **回流节律实测**：executing-plans 与 slides 距上轮清零约 47 分钟第三次回到盘面 ⇒ 每小时重清不是自愈型收口，"
                 "本轮清一次并把它降级为看守项（复算 python 05-exec/r59_retired_face.py），下轮起以节律而非单次绿为准。"
                 "⑦ 27 门 FAIL=5 与 r99 同因（外部 +12 棘轮 + 元门延迟，不动基线）；焚诀 verify 42 PASS/1 FAIL=C25 同条。"
                 "报告=06-benchmark/全量对标报告_r100_名册派生与两件换装_2026-10-02.md")
        s = s.replace(lines[0] + "\n", fixed + "\n", 1)
        io.open(P07, "w", encoding="utf-8", newline="").write(s)
        b = io.open(P07, encoding="utf-8", newline="").read()
        assert fixed[:60] in b and b.count(MARK) == 1, "读回失败"
        print("[FIXED] r100 摘要行已重写并读回，长度=%d" % len(fixed))
    else:
        print("[OK] r100 摘要行未见掏空，保留原样")

    # ---- 2. 第三次回流：清一次 + 留节律证据
    rc, out = sh(["C:/Program Files/Python312/python.exe", "-B",
                  "05-exec/r97_retire_full_egress.py", "--apply"])
    print("[EGRESS rc=%d] %s" % (rc, out.strip().splitlines()[-1] if out.strip() else ""))
    rc2, out2 = sh(["C:/Program Files/Python312/python.exe", "-B", "05-exec/r59_retired_face.py"])
    print("[GATE rc=%d] %s" % (rc2, out2.strip().splitlines()[-1] if out2.strip() else ""))

    # ---- 3. 逐个 pathspec 提交（禁 -A，本仓与他人在途共存）
    files = ["05-exec/r96_twelve_face.py",
             "05-exec/r96_gh_raw.json",
             "06-benchmark/twelve_face_r100_2026-10-02.json",
             "06-benchmark/gate_run_r100.json",
             "06-benchmark/全量对标报告_r100_名册派生与两件换装_2026-10-02.md",
             "README.md", "memory/07-next-steps.md",
             "06-benchmark/gate_runs.jsonl", "06-benchmark/input_pins.jsonl"]
    present = [f for f in files if os.path.exists(os.path.join(REPO, f))]
    if len(present) != len(files):
        sys.stderr.write("[ABORT] 应提交件缺 %s\n" % set(files) - set(present))
        return 1
    rc3, _ = sh(["git", "add", "--"] + present)
    if rc3:
        sys.stderr.write("[ABORT] git add 失败\n")
        return 1
    rc4, num = sh(["git", "diff", "--cached", "--numstat"])
    print("[STAGED]\n" + num.strip())
    msg = ("feat(r100): 对手名册改由search_face测量派生(源码仓名清单归零)+两件真换装落地;结论翻转r99\n\n"
           "- 手抄 ROSTER 10 仓 vs 同工具实测前 25 名差 15 仓(140497/108698/63335 三仓在外) => X-26 在对手面复发\n"
           "- derive_roster top-20 + roster_face 四态(UNVERIFIED_stale_cache 防旧缓存冒充);夹具 25->38 腿全过\n"
           "- 装入 commit-archaeologist + scope-creep-detector(各4文件齐装/ast 过/无 shell=True/平台当轮已列出);卸载 0 件\n"
           "- 自抓两次假干净: glob brace 不展开致 0 文件报 0 命中(改 os.walk 印 scanned_face=8);"
           "补丁一漏清 ROSTER 使用点致 NameError 而夹具 35/35 全绿(补 3 条主链接线腿)\n"
           "- 注册表 rebuild 判 BLOCKED 实测(??=26 含 24 他人件);回流节律=47 分钟第三次 => 降级看守项\n"
           "- 棘轮 +12 不动基线;README 索引行与 07 摘要行同步(07 那行因 shell 命令替换掏空已按反查重写)")
    rc5, out5 = sh(["git", "commit", "-q", "-m", msg])
    print("[COMMIT rc=%d] %s" % (rc5, out5.strip()))
    rc6, st = sh(["git", "show", "--stat", "--name-only", "HEAD"])
    print("[HEAD FILES]\n" + "\n".join(st.strip().splitlines()[-12:]))
    rc7, pr = sh(["git", "push", "origin", "HEAD:main"])
    rc8, ls = sh(["git", "ls-remote", "origin", "main"])
    rc9, hh = sh(["git", "rev-parse", "HEAD"])
    print("[PUSH rc=%d] remote=%s local=%s" % (rc7, ls.split()[0][:10] if ls.strip() else "-", hh.strip()[:10]))
    return 0 if ls.strip() and ls.split()[0] == hh.strip() else 1


if __name__ == "__main__":
    sys.exit(main())
