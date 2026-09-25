# -*- coding: utf-8 -*-
"""r35_landing_username.py — 只清 ILLUSTRATIVE 那 8 处账号名（r35 H-2，队列由分类器给）。

与 r34 的差别（重要）：r34 写的是「P3 = 纯冗余，清到 0」。r35 用 `r35_username_context_audit.py`
按「路径在盘上是否存在 + 行内是否有执行语境」逐处分类，实测 94 处里
**77 处承载机制（清掉即把能跑的技能改成不能跑）**，可清的只有 8 处。⇒ 本脚本只处理这 8 处。

改法（唯一形态）：`<账号名>` → `<用户名>` 占位。
    ⛔ 禁止换成另一个绝对路径（只是给泄漏改名字）；
    ⛔ 禁止对 LOAD_BEARING / UNKNOWN / NON_PATH 任何一处动手 —— 前者会破坏执行，后者是分类未完成。
落盘：全程走 rule_editor（受管根唯一途径），先 --dry-run 校锚点命中数，再 --no-commit 逐文件写，
      最后一次 commit --file 白名单收口（禁 -A，见 r27 夹带纪律）。
"""

import io
import json
import os
import subprocess
import sys

GS = r"D:\global_skills"
PY = r"C:\Program Files\Python312\python.exe"
RULE_EDITOR = os.path.join(GS, "A-memory-start", "references", "rule_editor.py")
AUDIT_JSON = os.path.join(os.path.dirname(GS), "Desktop", "workspace", "自建skill优化",
                          "06-benchmark", "username_context_r35_2026-09-25.json")
AUDIT_JSON = r"C:\Users\37533\Desktop\workspace\自建skill优化\06-benchmark\username_context_r35_2026-09-25.json"
TMP = r"C:\Users\37533\AppData\Local\Temp\r35_patches"


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def fixable_targets():
    d = json.load(io.open(AUDIT_JSON, encoding="utf-8"))
    out = []
    for r in d["rows"]:
        for c in r["detail"]:
            if c["class"] == "ILLUSTRATIVE":
                out.append((r["skill"], c["line"], c["text"]))
    return out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--dry-run"
    if not os.path.isdir(TMP):
        os.makedirs(TMP)
    user = os.environ["USERNAME"]
    tg = fixable_targets()
    print("分类器给的 ILLUSTRATIVE 队列 = %d 处" % len(tg))
    byfile = {}
    for skill, ln, text in tg:
        byfile.setdefault(skill, []).append((ln, text))

    plans = []
    for skill, items in sorted(byfile.items()):
        p = os.path.join(GS, skill, "SKILL.md")
        lines = io.open(p, encoding="utf-8").read().split("\n")
        for ln, text in items:
            old = lines[ln - 1]
            if user not in old:
                print("  !! %s:%d 复核失败：该行已不含账号名（可能已被改）⇒ 跳过，不猜" % (skill, ln))
                continue
            new = old.replace(user, "<用户名>")
            plans.append((skill, ln, old, new))
            print("  %-34s L%-4d %s" % (skill, ln, old.strip()[:78]))
    print("待改 %d 处 / %d 个文件" % (len(plans), len({x[0] for x in plans})))

    if mode == "--dry-run":
        print("[dry-run] 未写盘")
        return 0

    touched = set()
    for i, (skill, ln, old, new) in enumerate(plans):
        of, nf = os.path.join(TMP, "old_%d.txt" % i), os.path.join(TMP, "new_%d.txt" % i)
        io.open(of, "w", encoding="utf-8", newline="\n").write(old)
        io.open(nf, "w", encoding="utf-8", newline="\n").write(new)
        args = [PY, RULE_EDITOR, "replace", "--file", "%s/SKILL.md" % skill,
                "--old-file", of, "--new-file", nf]
        if mode == "--apply":
            args += ["--no-commit"]
        else:
            args += ["--dry-run"]
        rc, out = run(args)
        ok = rc == 0
        print("  %-34s L%-4d rc=%d %s" % (skill, ln, rc, out.strip().replace("\n", " | ")[:130]))
        if not ok:
            print("  !! 中断：任一处锚点失败即停，不做半改")
            return 1
        touched.add("%s/SKILL.md" % skill)

    if mode != "--apply":
        print("[dry-run 完成] 去掉 --dry-run 即执行")
        return 0
    args = [PY, RULE_EDITOR, "commit"]
    for f in sorted(touched):
        args += ["--file", f]
    args += ["--desc",
             "feat(skills): r35 精确整改账号名明文 8 处（ILLUSTRATIVE 类）→ <用户名> 占位 —— "
             "分类器 r35_username_context_audit.py 实测 94 处里 77 处承载执行（清掉即改坏技能），"
             "推翻 r34 自家『P3=纯冗余、清到 0』判定，本轮只动可安全相对化的 8 处（6 文件，正文行，"
             "frontmatter/description 零改动⇒派生件无需重建）。UNKNOWN 8 处与 NON_PATH 1 处（邮箱）不并类、不动。"]
    rc, out = run(args)
    print(out.strip()[:700])
    return rc


if __name__ == "__main__":
    sys.exit(main())
