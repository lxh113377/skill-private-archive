# -*- coding: utf-8 -*-
r"""control_char_scan.py — 控制字符扫描器（每次动手前的机器护栏）。

存在理由（2026-09-24 实测）：同一天**四轮**踩同一个坑 —— 反斜杠在 shell 双引号 / Python 字面量 /
markdown 渲染三道解析关里少一级转义，就静默产出退格符（0x08）。后果不是"难看"而是**账面自证失效**：
`behavior_core.md` 里「用户命令绝对优先」这条铁律，它自己的权威源路径被写成
`core<0x08>ehavior_core.md`，于是引用它的那段文字**永远 grep 不到它**（要查依据时查不到依据）。
规则型解法已当场被证伪（写着这条教训的条目自身又中了同一个坑）⇒ 按 A-get-memory Step 2.7
「下一个会话不做任何事，这个强化还生效吗」，只有挂在执行路径上的扫描才算强化。

脏集定义：C0 控制符（0x00-0x1F）+ 0x7f DEL，减去制表/换行/回车。
判定面：默认扫整个仓（传文件=单扫，传目录=递归），扩展名 `.md .py .json .jsonl .txt .tmpl .yaml .yml`。
允许集 = 制表/换行/回车；其余 C0 控制符（含 0x00、0x08、0x1b）一律算脏。
二进制（首 4KB 含 NUL）不判脏，但**如实登记为 skipped**（判据面为空不得静默当通过，R247）。

退出码：0 干净 / 1 有脏项 / 2 无有效输入面（路径不存在或扩展名面为空）
"""

import argparse
import io
import json
import os
import sys

ALLOWED = frozenset((0x09, 0x0a, 0x0d))                      # 制表/换行/回车：合法空白
C0 = frozenset(range(0x00, 0x20))                           # 全部控制符
DIRTY = frozenset((C0 | {0x7f}) - ALLOWED)                  # 0x7f=DEL：实测曾真的出现在源码里
EXTS = (".md", ".py", ".json", ".jsonl", ".txt", ".tmpl", ".yaml", ".yml")
SKIP_DIRS = {".git", ".codebuddy", "__pycache__", "_trash", "node_modules", ".rule_backup"}
MARK_CLEAN, MARK_DIRTY, MARK_EMPTY, MARK_HIT = "[CTRL:CLEAN]", "[CTRL:DIRTY]", "[CTRL:EMPTY]", "[CTRL:HIT]"


def find_control(text):
    """返回 [(字符下标, 码位)]；偏移用**字符下标**，便于人直接在文件里定位。"""
    out = []
    for i, ch in enumerate(text):
        if ord(ch) in DIRTY:
            out.append((i, ord(ch)))
    return out


def is_binary(raw):
    return b"\x00" in raw[:4096]


def iter_targets(paths):
    for p in paths:
        p = os.path.abspath(p)
        if os.path.isfile(p):
            yield p
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for fn in files:
                    if fn.endswith(EXTS):
                        yield os.path.join(root, fn)


def scan_one(path):
    raw = open(path, "rb").read()
    if is_binary(raw):
        return {"path": path, "count": 0, "codes": [], "skipped": True, "skip_reason": "binary"}
    hits = find_control(raw.decode("utf-8", "replace"))
    if not hits:
        return None
    return {"path": path, "count": len(hits), "codes": sorted({c for _o, c in hits}),
            "offsets": [o for o, _c in hits][:12], "skipped": False}


def scan_paths(paths):
    """返回 finding 列表：脏项 + 被跳过的二进制项（不静默丢弃）。"""
    out = []
    for p in iter_targets(paths):
        r = scan_one(p)
        if r:
            out.append(r)
    return out


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="控制字符扫描（默认扫全仓，0 命中才放行）")
    ap.add_argument("paths", nargs="*", help="文件或目录；缺省 = 本仓根")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max", type=int, default=15, help="人读面最多列几条")
    a = ap.parse_args(argv)
    roots = a.paths or [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]
    existed = [p for p in roots if os.path.exists(p)]
    if not existed:
        print("%s 输入面不存在：%s（判据面为空，不得判过）" % (MARK_EMPTY, roots))
        return 2
    findings = scan_paths(existed)
    dirty = [f for f in findings if not f.get("skipped")]
    skipped = [f for f in findings if f.get("skipped")]

    print("=== 控制字符扫描：%d 个面 / 脏 %d / 跳过二进制 %d ==="
          % (len(list(iter_targets(existed))), len(dirty), len(skipped)))
    for f in dirty[:a.max]:
        print("  %s %s ×%d 码位=%s 首偏移=%s"
              % (MARK_HIT, f["path"], f["count"], f["codes"], f["offsets"][:3]))
    if len(dirty) > a.max:
        print("  …另有 %d 处（--max 调）" % (len(dirty) - a.max))
    if dirty:
        print("%s %d 个文件含非法控制符 ⇒ 用 chr(8)/chr(27) 显式构造或改 raw 串重写" % (MARK_DIRTY, len(dirty)))
    else:
        print("%s 无非法控制符" % MARK_CLEAN)
    if a.json:
        print(json.dumps({"schema": "zijian-ctrl-scan-v1", "dirty": dirty,
                          "skipped": [f["path"] for f in skipped]}, ensure_ascii=False))
    return 1 if dirty else 0


if __name__ == "__main__":
    raise SystemExit(main())
