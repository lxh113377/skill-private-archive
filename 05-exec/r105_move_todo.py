# -*- coding: utf-8 -*-
r"""r105_move_todo.py — 把本轮新落的 5 条 P1 待办从 07 主壳迁进独占新卷。

为什么做：append_guard 实测 07 主壳 143,340 B → 146,991 B，本就远超 shell_max 40,960 B
（W-48 在册超限面，处置口径=逐条人工裁决/摘要区归档，禁自动改 P0）。我这一条 append 又给
超限面加了 3,651 B ⇒ 正解不是「反正已经超了继续加」，而是**新落的量落到新卷**，并把主壳
回退到追加前的字节。

分区不变式（本仓 V3.48.0 立过的同一条）：迁出 ∪ 留守 == 原文，只搬不移除、不复制。
验收：主壳行数 -5、新卷行数 +5（含 1 行卷首说明）、迁出 5 行与原文逐字节相等。
退出码：0=成立；1=行数/字节不守恒（已回滚）；2=前置面不可达。
"""
import io
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "memory", "07-next-steps.md")
BAK = os.path.join(ROOT, "05-exec", "mark_backup")
KEYS = ["R105-6", "R105-7", "R105-8", "R105-9", "R105-10"]


def read_lines(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read().splitlines(True)


def write_lines(p, lines):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.writelines(lines)


def main():
    if not os.path.isfile(MAIN):
        print("[MOVE:UNVERIFIED] 07 主壳不存在")
        return 2
    orig = read_lines(MAIN)
    orig_bytes = "".join(orig).encode("utf-8")
    tail = orig[-len(KEYS):]
    hit = [k for k, l in zip(KEYS, tail) if k in l]
    if len(hit) != len(KEYS):
        print("[MOVE:UNVERIFIED] 末 %d 行不含全部 R105-x 锚点（命中=%s）⇒ 面与预期不符，停手"
              % (len(KEYS), hit))
        return 2
    moved = [l for l in tail if l.strip()]
    if len(moved) != len(KEYS):
        print("[MOVE:UNVERIFIED] 末行里有空行，取数面非恰好 5 条 ⇒ 停手")
        return 2

    os.makedirs(BAK, exist_ok=True)
    snap = os.path.join(BAK, "07-next-steps.md.r105_before_move")
    with io.open(snap, "wb") as f:
        f.write(orig_bytes)
    if os.path.getsize(snap) != len(orig_bytes):
        print("[MOVE:FAIL] 备份字节与原文不等（%s vs %s）⇒ 未动手"
              % (os.path.getsize(snap), len(orig_bytes)))
        return 1

    # ① 先取号建卷（建卷失败则主壳原样未动，不留半成品）
    batch = os.path.join(os.environ.get("TEMP", "/tmp"), "r105_part_batch.md")
    header = ("> 换卷理由（数字实测）：07 主壳追加本轮 5 条 P1 后实测 %d B，远超 append_guard "
              "②档 shell_max 40960 B；W-48 处置口径为「逐条人工裁决/摘要区归档、禁自动改 P0」，"
              "故本轮新落量落本独占卷，主壳回退至追加前 %d B。\n\n"
              % (len(orig_bytes), len(orig_bytes) - len("".join(moved).encode("utf-8"))))
    with io.open(batch, "w", encoding="utf-8", newline="") as f:
        f.write(header + "".join(moved))
    va = subprocess.run([sys.executable, r"D:\global_memory\scripts\volume_alloc.py",
                         "--dir", os.path.join(ROOT, "memory"),
                         "--template", "07-next-steps.part{N}.md",
                         "--from-file", batch, "--json"],
                        capture_output=True, text=True)
    if va.returncode != 0:
        print("[MOVE:FAIL] volume_alloc 取号失败 rc=%s\n%s\n%s" % (va.returncode, va.stdout, va.stderr))
        return 1
    import json
    try:
        info = json.loads(va.stdout.strip().splitlines()[-1])
    except Exception:
        print("[MOVE:FAIL] volume_alloc 输出不可解析：%s" % va.stdout[:200])
        return 1
    new_vol = info.get("path") or info.get("file") or ""
    if not new_vol or not os.path.isfile(new_vol):
        print("[MOVE:FAIL] 新卷未落盘：%s" % new_vol)
        return 1

    # ② 主壳回退（只删自己刚加的 5 行）
    rest = orig[:-len(KEYS)]
    write_lines(MAIN, rest)
    after = read_lines(MAIN)
    new_bytes = "".join(rest).encode("utf-8")

    # ③ 守恒断言：新卷正文逐字节 == 迁出 5 行；主壳行数 == 原-5
    nv = read_lines(new_vol)
    nv_body = "".join(nv).encode("utf-8")
    moved_b = "".join(moved).encode("utf-8")
    ok_lines = len(after) == len(orig) - len(KEYS)
    ok_bytes = len("".join(rest).encode("utf-8")) == len(orig_bytes) - len(moved_b)
    ok_part = moved_b in nv_body
    print("主壳 %d 行 → %d 行（期望 -5）｜字节 %d → %d（期望 -%d）｜新卷=%s 含迁出全文=%s"
          % (len(orig), len(after), len(orig_bytes), len(new_bytes), len(moved_b),
             os.path.basename(new_vol), ok_part))
    if not (ok_lines and ok_bytes and ok_part):
        write_lines(MAIN, orig)
        print("[MOVE:FAIL] 不守恒 ⇒ 已按备份回滚主壳（新卷留存待人工处置，未删）")
        return 1
    print("[MOVE:PASS] 迁出 5 条 → %s；主壳回退 %d B；分区不变式成立（迁出∪留守==原文）"
          % (os.path.basename(new_vol), len(orig_bytes) - len(new_bytes)))
    print("  备份=%s（原文字节 %d）" % (snap, len(orig_bytes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
