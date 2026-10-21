# -*- coding: utf-8 -*-
# r154_shell_archive.py -- 把注入壳 AGENTS.md 的纪律条目正文归档到 memory/ 分卷（R150-7 落地）。
#
# 起因（r154 实测，两条都量过）：
#   ① 声明面：#30-#48 共 19 条规则的**正文只存在于壳里**，memory/*.md 抽样比对**零命中**
#      => 壳成了「第二真相源」，**违它自己写的那句**「本节只放路由与红线；正文权威源在 memory/，本壳不含第二真相源」。
#      这是目标① 的**归档环节**在实践上失效（规则立了，没归档）。
#   ② 体量面：注入面 inject_union_bytes = 100,166B vs 硬顶 65,536B = **1.53 倍**；壳 38,766B 是其中唯一本仓可动的成员。
#
# 动作（原文零改写，R241）：把纪律条目正文整段迁至 `memory/06-constraints.partN.md`（每份 <= 4096B 的 memory 硬限），
#   壳内原位替换为**指针块**。两边都不删内容，只换落点。
#
# 自证（脚本内断言，不通即退出）：
#   V1 迁移总量 >= 20000B（防「一个都没迁」却报完成）
#   V2 每个分卷 <= 4096B（memory 硬限）
#   V3 分卷正文拼接**逐字节等于**壳中被移除的原文（原文零改写）
#   V4 迁移后壳内不再含任一纪律条目标题；且壳内仍有指针块与 P-1 路由结构
# 用法:
#   python 05-exec/r154_shell_archive.py            # 干跑（只打印计划）
#   python 05-exec/r154_shell_archive.py --apply    # 落盘
import argparse
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHELL = os.path.join(ROOT, "AGENTS.md")
MEMDIR = os.path.join(ROOT, "memory")
PART_LIMIT = 4096
RULE_RE = re.compile(r"^## \u26a0\ufe0f .*\uff08#\d+")
# 指针块标题**刻意不含**「⚠️ …（#NN」形态 —— 否则它会命中 RULE_RE，使 V4「壳内无残留纪律块」自否（r154 首跑自抓）。
POINTER_HEAD = "## 纪律条目正文已归档至 memory 分卷（r154，R150-7）"


def read_raw(path):
    return io.open(path, "rb").read().decode("utf-8")


def next_part_index():
    n = 0
    for fn in os.listdir(MEMDIR):
        m = re.match(r"06-constraints\.part(\d+)\.md$", fn)
        if m:
            n = max(n, int(m.group(1)))
    return n + 1, n


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args(argv)
    raw = read_raw(SHELL)
    lines = raw.split("\n")
    heads = [i for i, l in enumerate(lines) if RULE_RE.match(l)]
    if not heads:
        print("[ARCHIVE] UNVERIFIED 壳内找不到纪律条目标题 => 面不对，禁按完成记（R247）")
        return 2
    blocks = []
    for n, i in enumerate(heads):
        end = heads[n + 1] if n + 1 < len(heads) else None
        # 遇下一个非纪律条目标题（## 开头且不是纪律条目）即止
        if end is None:
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("## ") and not RULE_RE.match(lines[j]):
                    end = j
                    break
            if end is None:
                end = len(lines)
        blocks.append((i, end))
    moved = "\n".join("\n".join(lines[s:e]) for s, e in blocks)
    titles = [lines[s].strip() for s, _ in blocks]
    print("[ARCHIVE] 纪律条目 %d 条 / 待迁 %d B；壳现 %d B" % (len(blocks), len(moved.encode()), len(raw.encode())))
    first, _ = blocks[0]
    start_n, prev_n = next_part_index()
    chunks, cur, cur_len = [], [], 0
    chunk_limit = PART_LIMIT - 96   # 预留分卷头（约 76B）与连接换行
    for (s, e), t in zip(blocks, titles):
        seg = "\n".join(lines[s:e])
        seg_b = len(seg.encode()) + (1 if cur else 0)
        if cur and cur_len + seg_b > chunk_limit:
            chunks.append(cur)
            cur, cur_len = [], 0
        cur.append(seg)
        cur_len += seg_b
    if cur:
        chunks.append(cur)
    plan = []
    for k, ch in enumerate(chunks):
        idx = start_n + k
        head = "# 06-constraints.part%d -- 纪律条目正文归档（#30-#48，r154 从 AGENTS.md 迁入，原文零改写）\n\n" % idx
        body = head + "\n".join(ch)
        plan.append((os.path.join(MEMDIR, "06-constraints.part%d.md" % idx), body))
    # V1/V2/V3 前置断言
    v1 = len(moved.encode()) >= 20000
    v2 = all(len(b.encode()) <= PART_LIMIT for _, b in plan)
    joined = "\n".join("\n".join(ch) for ch in chunks)
    v3 = joined == moved
    print("[ARCHIVE] V1 迁移量>=20KB: %s（%d B）" % (v1, len(moved.encode())))
    print("[ARCHIVE] V2 每份<=4096B: %s（最大 %d B，共 %d 份）"
          % (v2, max(len(b.encode()) for _, b in plan) if plan else 0, len(plan)))
    print("[ARCHIVE] V3 拼接逐字节等于原文: %s" % v3)
    for p, b in plan:
        print("    -> %s (%d B)" % (os.path.relpath(p, ROOT), len(b.encode())))
    # 壳改造：删掉全部纪律块，在首块原位插指针块
    keep = []
    ptr = [POINTER_HEAD, "",
           "> r154 归档（R150-7 落地）：下列纪律条目的**正文权威源**已迁 `memory/06-constraints.part%d.md` .. `.part%d.md`（原文零改写，R241）。" % (start_n, start_n + len(plan) - 1),
           "> 本壳仅留指针 —— 回到 R161 的原设计「本节只放路由与红线；本壳不含第二真相源」。",
           "> 条目清单：#30..#48（含 #31 全自动完成 / #32 判据面 / #33 结论层 / #35 阻断点 / #45 写入顺序 / #47 转办复算面 / #48 want⇄got …）。",
           "> ⛔ 新增纪律条目**先落 memory 分卷**，壳内只加指针（防本缺陷复发）。",
           ""]
    idx_blocks = {s: e for s, e in blocks}
    i = 0
    while i < len(lines):
        if i in idx_blocks:
            if i == first:
                keep.extend(ptr)
            i = idx_blocks[i]
            continue
        keep.append(lines[i])
        i += 1
    new_raw = "\n".join(keep)
    v4a = not any(RULE_RE.match(l) for l in keep)
    v4b = (POINTER_HEAD in new_raw) and ("## 分卷目录" in new_raw) and ("## 启动顺序" in new_raw)
    print("[ARCHIVE] V4 壳内无残留纪律块且指针/路由结构俱在: %s" % (bool(v4a and v4b)))
    print("[ARCHIVE] 壳 %d B -> %d B（- %d B）" % (len(raw.encode()), len(new_raw.encode()),
                                                   len(raw.encode()) - len(new_raw.encode())))
    if not (v1 and v2 and v3 and v4a and v4b):
        print("[ARCHIVE:FAIL] 自证未过，拒绝落盘")
        return 1
    if not args.apply:
        print("[ARCHIVE] 干跑完成（未落盘；加 --apply 落盘）")
        return 0
    for p, b in plan:
        with io.open(p, "wb") as f:
            f.write(b.encode("utf-8"))
    with io.open(SHELL, "wb") as f:
        f.write(new_raw.encode("utf-8"))
    back = read_raw(SHELL)
    ok = back == new_raw
    print("[ARCHIVE] 落盘 + 读回验证: %s" % ("通过" if ok else "失败"))
    print("[ARCHIVE:PASS]" if ok else "[ARCHIVE:FAIL]")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
