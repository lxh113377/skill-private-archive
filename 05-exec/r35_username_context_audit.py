# -*- coding: utf-8 -*-
"""r35_username_context_audit.py — 把「账号名出现在技能里」拆成**可执行的两类**（r35 H-2 修订版）。

为什么需要它（本轮实测推翻 r34 自家结论）：
    r34 我把 P3「账号名明文 25 个文件」判为"不承载机制、纯冗余"，并写下 H-3「清到 0」。
    本轮打开第一个目标 `openclaw-task-supervision`（14 处）逐条看：
        L19-21/L81-83  是 `--message-file "C:\\Users\\37533\\Desktop\\我的skill.txt"` 这类**要照抄执行的命令**
        L615/L622      是 `C:\\Users\\37533\\.openclaw\\agents\\main\\sessions\\...` **运行态真实路径**
        L22/L699       是焚诀工作目录，脚本要 cd 进去
    ⇒ 这些**全部承载机制**：清掉就把能跑的技能改成不能跑。r34 的"纯冗余"判定是**未逐条看就下的分类结论**。

判据（可机检、不靠语感）：对每处出现，取出它所在的**完整路径字面量**，判
    LOAD_BEARING  该路径 `os.path.exists()` 为真（含把 `{占位}` 段截断后其父目录存在的情形）
                  或该行含执行语境（`--message-file` / 反斜杠命令 / `cd ` / `python` / `powershell` / `.py` / `.ps1` / `Read →` / `path:`）
    ILLUSTRATIVE  路径在盘上不存在**且**行内无执行语境 ⇒ 纯示例，可安全相对化
    UNKNOWN       取不到路径边界 ⇒ 单列，禁并入任一类（不得"就近归类"制造可清量）

输出口径：三态计数 + 逐条定位；**只有 ILLUSTRATIVE 才允许进整改队列**。
用法：python 05-exec/r35_username_context_audit.py [--skill X] [--json 件.json]
退出码：0 正常出表 / 2 根不可读或账号名取不到（不得输出「0 处可清」，R247）
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime

GS = r"D:\global_skills"
# 路径字面量：盘符后**两种分隔符都要收**（本仓正文里 `C:/Users/...` 与 `C:\Users\...` 并存，
# 只认反斜杠会让正斜杠路径全落进 UNKNOWN —— r35 首跑实测 28 处 UNKNOWN 里绝大多数是这个形态）
PATH_RX = re.compile(r"[A-Za-z]:[\\/][^\s'\"`|,，。；;()]*")
EXEC_HINT = re.compile(r"(--message-file|^\s*[a-z]+\.py |python |powershell |pwsh |cd |bash |curl |\bRead →|path:\s|`run\.ps1|\.ps1|\.py\b|\.jsonl?\b)")
# 命中处若嵌在更长的字母数字串里（典型：邮箱前缀 3753318894@qq.com、端口、ID），
# 它**不是**路径泄漏，单列 NON_PATH —— 混进 UNKNOWN 会既夸大"可清量"又掩盖真实邮箱暴露
WORD_RX = re.compile(r"[0-9A-Za-z]")


def classify_line(line):
    """返回该行的分类列表。分类逐处判定，不按整行一刀切。"""
    user = USER
    out = []
    for m in re.finditer(re.escape(user), line, re.I):
        if WORD_RX.match(line, m.start() - 1) or WORD_RX.match(line, m.end()):
            out.append(("NON_PATH", None))       # 嵌在更长 token 里（邮箱/ID），非路径
            continue
        seg = None
        for pm in PATH_RX.finditer(line):
            if pm.start() <= m.start() < pm.end():
                seg = pm.group(0)
                break
        if seg is None:
            out.append(("UNKNOWN", None))
            continue
        probe = seg.split("{")[0].rstrip("\\/")
        cand = re.split(r"[{\\/]", seg)[0] if "{" in seg else probe
        exists = os.path.exists(probe) or os.path.exists(cand)
        if not exists:                       # 再退一级父目录（例：...\.openclaw\agents\{UUID}.jsonl）
            parent = os.path.dirname(probe)
            exists = bool(parent) and os.path.exists(parent)
        if exists or EXEC_HINT.search(line):
            out.append(("LOAD_BEARING", seg))
        else:
            out.append(("ILLUSTRATIVE", seg))
    return out


USER = (os.environ.get("USERNAME") or "").strip()


def audit(only_skill=None):
    root = GS
    if not os.path.isdir(root):
        return None, "技能根不可读: %s" % root
    if not USER or len(USER) < 3:
        return None, "取不到本机账号名 ⇒ 不得输出「0 处可清」（R247）"
    rows = []
    files = sorted(f for f in os.listdir(root) if os.path.isdir(os.path.join(root, f)))
    for name in files:
        if only_skill and name != only_skill:
            continue
        p = os.path.join(root, name, "SKILL.md")
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                lines = f.read().splitlines()
        except OSError:
            continue
        cls = []
        for ln, line in enumerate(lines, 1):
            if not re.search(re.escape(USER), line, re.I):
                continue
            for kind, seg in classify_line(line):
                cls.append({"line": ln, "class": kind, "path": seg, "text": line.strip()[:120]})
        if cls:
            rows.append({"skill": name, "occurrences": len(cls),
                         "by_class": dict(Counter(c["class"] for c in cls)), "detail": cls})
    return {"root": root, "user_len": len(USER), "files_with_hits": len(rows),
            "total": sum(r["occurrences"] for r in rows),
            # 聚合必须累加 n：写成 Counter(k for ...) 数的是「文件×类别」对数而非出现次数
            # （r35 首跑实测把 94 处误报成 33，正是本仓 audit-runner-safe-aggregate 点名的聚合误算）
            "totals_by_class": {k: sum(r["by_class"].get(k, 0) for r in rows)
                               for k in ("LOAD_BEARING", "ILLUSTRATIVE", "UNKNOWN", "NON_PATH")},
            "rows": rows}, None


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", help="只看单个技能（复核用）")
    ap.add_argument("--json")
    ap.add_argument("--list-fixable", action="store_true", help="只列 ILLUSTRATIVE（可安全整改）的定位")
    args = ap.parse_args()

    res, err = audit(args.skill)
    if res is None:
        print("[AUDIT:UNVERIFIED] %s" % err)
        return 2
    print("=== 账号名出现的承载性分类（r35；判据=路径盘上存在性 + 行内执行语境，不靠语感）===")
    print("技能根: %s｜命中文件 %d 个｜出现 %d 处｜分类: %s" % (
        res["root"], res["files_with_hits"], res["total"], res["totals_by_class"]))
    print("⚠️ 只有 ILLUSTRATIVE 可进整改队列；LOAD_BEARING 清掉即改坏技能（r34 的「清到 0」判据太粗，本轮推翻）")
    for r in sorted(res["rows"], key=lambda x: -x["occurrences"])[:12]:
        print("  %-36s %2d 处  %s" % (r["skill"], r["occurrences"], r["by_class"]))
    if args.list_fixable:
        fx = [(r["skill"], c) for r in res["rows"] for c in r["detail"] if c["class"] == "ILLUSTRATIVE"]
        print("\n--- ILLUSTRATIVE 定位（可整改）%d 处 ---" % len(fx))
        for skill, c in fx[:40]:
            print("  %s:%d  %s" % (skill, c["line"], c["text"]))
        unk = [(r["skill"], c) for r in res["rows"] for c in r["detail"] if c["class"] == "UNKNOWN"]
        print("--- UNKNOWN 定位（禁就近归类）%d 处 ---" % len(unk))
        for skill, c in unk[:15]:
            print("  %s:%d  %s" % (skill, c["line"], c["text"]))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(json.dumps({"schema": "username-context-audit-v1",
                                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "readonly": True, "benchmark": "r35 H-2 修订（推翻 r34 的『P3=纯冗余』判定）",
                                "rule": "路径 os.path.exists 或 行内含执行语境 ⇒ LOAD_BEARING；两者皆无 ⇒ ILLUSTRATIVE；取不到边界 ⇒ UNKNOWN（不并入任一类）",
                                "covers": [res["root"]], **res}, ensure_ascii=False, indent=1))
        print("JSON -> %s" % args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
