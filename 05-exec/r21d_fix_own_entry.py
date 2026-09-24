# -*- coding: utf-8 -*-
r"""r21d_fix_own_entry.py — 清掉 07 里的退格控制符（含我自己在登记条目里**又引入**的 3 处）。

实况：并行会话把权威源写成 `core<0x08>ehavior_core.md`（本意 `core\behavior_core.md`，
markdown 里的 `\b` 被当成退格）；我本轮写「登记这条缺陷」的条目时，同样用 shell 内联
python -c 传字符串，**同一个坑原样复现 3 次**（连给出的复测命令里 `b'\x08'` 也变成了真退格）。
⇒ 教训自证：这类文本必须走**脚本文件**（源文件里 "\\" 只经一次解析），不能走 shell 内联。

守卫：逐处替换前先计数，末尾断言 0x08 归零；写后读回实证（R213）。
"""
import io
import os
import sys

P = r"C:\Users\37533\Desktop\workspace\自建skill优化\memory\07-next-steps.md"
BS = chr(8)
GOOD = "core" + "\\" + "behavior_core.md"


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t = io.open(P, encoding="utf-8-sig").read()
    before = t.count(BS)
    subs = [
        ("core" + BS + "ehavior_core.md", GOOD),          # 权威源路径本体（P0 铁律行 + 我的条目）
        ("`" + BS + "`", "`" + "\\b" + "`"),              # 条目里「源码里的 \b」
        ("b'" + BS + "'", "b'" + "\\x08" + "'"),          # 复测命令里的字节串字面量
    ]
    for bad, good in subs:
        n = t.count(bad)
        t = t.replace(bad, good)
        print("  替换 %-34s 命中 %d 处" % (repr(bad)[:34], n))
    left = t.count(BS)
    print("[断言] 残留 0x08 = %d（期望 0）" % left)
    if left:
        i = t.index(BS)
        print("       上下文:", repr(t[i - 60:i + 40]))
        return 1
    with open(P, "wb") as f:
        f.write(t.encode("utf-8"))
    back = io.open(P, encoding="utf-8-sig").read()
    ok = back.count(BS) == 0 and back.count(GOOD) >= 2
    print("[FIX] 修前 %d 处 → 读回 0x08=%d | 正确路径 %d 处 | %dB | 在位=%s"
          % (before, back.count(BS), back.count(GOOD), os.path.getsize(P), ok))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
