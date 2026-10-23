# -*- coding: utf-8 -*-
"""r174: part97/part99 人工拆卷（R166-2 收口）。

语义对标 handoff_lib/splitvol.py 的 _split_once，但补上它拒做的 single_block：
  - 段落边界优先：整块（空行分隔）迁移，与工具同口径；
  - 单行超长：按中文句号边界递归切分，续行加 "- " 前缀；
  - 多行超长：按整行边界递归切分（不加前缀）；
  - 字节守恒判据（不通即拒落盘）：按原段把 parts 还原，必须逐字节等于原文；
  - 不解剖：不删字、不改字、不调序，只加前缀与卷头。
"""
import io
import os
import re
import sys

MEM = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory")
NL = chr(10)
CAP = 4096
MAXLINE = 3000
FULL_STOP = chr(0x3002)


def _blen(s):
    return len(s.encode("utf-8"))


def parse_segments(text):
    lines_ = text.split(NL)
    segs = []
    cur = []
    blank = 0
    for l in lines_:
        if l == "":
            if cur:
                blank += 1
            continue
        if cur:
            segs.append({"text": NL.join(cur), "sep": NL * (blank + 1)})
            cur = []
        cur = [l]
        blank = 0
    if cur:
        segs.append({"text": NL.join(cur), "sep": None})
    return segs


def split_long_line(line, maxlen=MAXLINE):
    """单行按句号边界递归切分；续段加 "- " 前缀。

    还原规则：parts[0] + "".join(p[2:] for p in parts[1:]) == line
    """
    if _blen(line) <= maxlen:
        return [line]
    mids = [i for i, ch in enumerate(line) if ch == FULL_STOP]
    mids = [i for i in mids if 0 < i < len(line) - 1]
    if not mids:
        return [line]
    target = len(line) // 2
    cut = min(mids, key=lambda p: abs(p - target))
    head = line[: cut + 1]
    tail = "- " + line[cut + 1:]
    if _blen(head) >= _blen(line) or _blen(tail) >= _blen(line):
        return [line]
    return split_long_line(head, maxlen) + split_long_line(tail, maxlen)


def split_segment(seg_text, maxlen=MAXLINE):
    """段内切分：单行超长走句号边界；多行超长走整行边界。

    多行切分的还原规则：NL.join(parts) == seg_text
    """
    if _blen(seg_text) <= maxlen:
        return [seg_text]
    if NL in seg_text:
        lines_ = seg_text.split(NL)
        if len(lines_) >= 2:
            mid = len(lines_) // 2
            head = NL.join(lines_[:mid])
            tail = NL.join(lines_[mid:])
            if head and tail and _blen(head) < _blen(seg_text) and _blen(tail) < _blen(seg_text):
                return split_segment(head, maxlen) + split_segment(tail, maxlen)
    return split_long_line(seg_text, maxlen)


def vol_header(name, src):
    return ("# %s" + NL + NL + "<!-- 本卷为 %s 的段落边界拆分（R241：原文字句零改写；"
            "超长行按句号边界切分，逐字节拼接等于原文） -->" + NL) % (name, src)


def _part_name(base, n):
    """base = '07-next-steps' 或 '05-feature-status' 等。"""
    return "%s.part%d.md" % (base, n)


def register_in_shell(new_part_names, base_name="07-next-steps.md", desc=None):
    """把新卷登记进主卷「## 分卷目录」节（对齐归属方 splitvol._register_in_shell 语义）。

    r183 一手：本工具此前只写卷不登记 ⇒ 拆出的卷成**孤儿卷**（主卷无任何指向）。
    去重只认「已作为目录行存在」——旧式判「卷名出现在全文」会把正文里一句普通引用误判成
    已登记 ⇒ 漏登记、卷号错位（归属方 2026-09-12 iCAN 同坑）。卷号 = 现有最大 +1；
    无目录节则建节；只追加，绝不改他人既有行。
    """
    path = os.path.join(MEM, base_name)
    if not os.path.isfile(path):
        return "REFUSED 主卷不存在: %s" % base_name
    with io.open(path, encoding="utf-8") as f:
        lines = f.read().split(NL)
    dir_re = re.compile(r"^- \*\*卷(\d+)\*\* `(.+?)`")
    idxs = [i for i, ln in enumerate(lines) if dir_re.match(ln)]
    named = {}
    for i in idxs:
        mm = dir_re.match(lines[i])
        named[mm.group(2)] = int(mm.group(1))
    todo = [n for n in new_part_names if n not in named]
    if not todo:
        return "SKIP 已登记（幂等）%d 卷" % len(new_part_names)
    nxt = (max(named.values()) if named else 0) + 1
    d = desc or "r174 段落边界拆分（R241 原文零改写）"
    add = ["- **卷%d** `%s` — %s" % (nxt + k, nm, d) for k, nm in enumerate(todo)]
    if idxs:
        lines[idxs[-1] + 1:idxs[-1] + 1] = add
    else:
        block = ["## 分卷目录", ""] + add
        pos = max([i for i, ln in enumerate(lines) if ln.startswith("## ")], default=len(lines) - 1)
        lines[pos:pos] = block + [""]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(NL.join(lines))
    return "REGISTERED %d 卷（卷%d..卷%d）" % (len(todo), nxt, nxt + len(todo) - 1)


def rewrite_source_shell(src, header_seg_count, new_names, result=None):
    """源卷改成指针壳（r183 一手：只写新卷不改源卷 ⇒ 源卷与新卷**内容重复**，
    被账龄尺去重面判红 `RE_ITEM 命中 333 行、只计入 331 ⇒ 2 行被静默吞掉`）。
    迁出的每段必须能在新卷里逐字找到首行，否则拒写（防「壳写了、内容丢了」）。
    """
    path = os.path.join(MEM, src)
    if not os.path.isfile(path):
        return False, "REFUSED 源卷不存在: %s" % src
    with io.open(path, encoding="utf-8") as f:
        orig = f.read()
    if not result:
        return False, "REFUSED 缺 do_split 结果（无法核对迁出内容）"
    segs = parse_segments(orig)
    moved = group_moved_parts(result)
    bad = []
    for seg, parts in moved:
        cov, note = cover_ok(seg, parts)
        if not cov:
            bad.append("%s | %s" % (seg[:28], note))
    if bad:
        return False, "REFUSED 迁出内容与原段不守恒: %s" % bad[:2]
    # 覆盖数须等于源卷正文段数（漏迁就不许改壳）
    if len(moved) != len(segs) - header_seg_count:
        return False, "REFUSED 迁出段数 %d != 源卷正文段数 %d" % (
            len(moved), len(segs) - header_seg_count)
    head_txt = NL.join(s["text"] for s in segs[:header_seg_count])
    listed = "、".join("`" + n + "`" for n in new_names)
    note = ("> **拆卷说明**：本卷正文已按段落边界拆至 " + listed +"；源卷只留标题与注记，"
            "正文不与新卷重复（重复会被账龄尺去重面判红）。")
    out_txt = head_txt + NL + NL + note + NL
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(out_txt)
    return True, "SHELL %s -> %dB（迁出 %d 段，全部在新卷中命中）" % (src, _blen(out_txt), len(moved))

def do_split(src, header_seg_count, start_num, base=None):
    with io.open(os.path.join(MEM, src), encoding="utf-8") as f:
        orig = f.read()
    segs = parse_segments(orig)
    header_segs = segs[:header_seg_count]
    content = segs[header_seg_count:]
    expanded = []
    prov = []          # 与 expanded 对齐：(原段文本, 该原段第几次出现)
    occ = {}
    for s in content:
        k = (s["text"], occ.get(s["text"], 0))
        occ[s["text"]] = occ.get(s["text"], 0) + 1
        if _blen(s["text"]) > MAXLINE:
            for part in split_segment(s["text"]):
                expanded.append({"text": part, "sep": NL + NL})
                prov.append(k)
        else:
            expanded.append(s)
            prov.append(k)
    if expanded:
        expanded[-1] = {"text": expanded[-1]["text"], "sep": None}
    volumes = []
    n = start_num
    buf = []
    buf_bytes = 0
    placement = []   # 与 buf 对齐：原段 text

    def flush():
        nonlocal n, buf, buf_bytes, placement
        if not buf:
            return
        name = _part_name(base or "07-next-steps", n)
        body = "".join(s["text"] + (s["sep"] or "") for s in buf)
        volumes.append({"name": name, "content": vol_header(name, src) + NL + body,
                        "placement": list(placement)})
        n += 1
        buf = []
        buf_bytes = 0
        placement = []

    for idx, s in enumerate(expanded):
        seg_bytes = _blen(s["text"] + (s["sep"] or ""))
        head_bytes = _blen(vol_header(_part_name(base or "07-next-steps", n), src) + NL)
        if buf and head_bytes + buf_bytes + seg_bytes > CAP:
            flush()
        buf.append(s)
        placement.append(prov[idx])
        buf_bytes += seg_bytes
    flush()
    return {"orig": orig, "header_segs": header_segs, "volumes": volumes,
            "expanded": expanded, "prov": prov, "next": n}


def group_moved_parts(result):
    """从已写出的新卷里，按 do_split 记好的 placement 归组每个原段的 parts。

    返回 [(原段文本, [片...])]，顺序稳定。verify 与 rewrite_source_shell 共用同一份归组，
    避免两处各写一套判据（漂移源）。
    """
    groups = {}
    order = []
    for v in result["volumes"]:
        body = v["content"].split(NL, 3)[3] if v["content"].count(NL) >= 3 else ""
        for s, k in zip(parse_segments(body), v["placement"]):
            if k not in groups:
                groups[k] = []
                order.append(k)
            groups[k].append(s["text"])
    return [(k[0], groups[k]) for k in order]

def _reconstruct(orig_seg_text, parts):
    """把一个原段的全部 parts 还原成原文；规则见 split_long_line/split_segment docstring。"""
    if NL in orig_seg_text:
        return NL.join(parts)
    return parts[0] + "".join(p[2:] if p.startswith("- ") else p for p in parts[1:])

def cover_ok(orig_seg_text, parts):
    """不猜还原规则的守恒判据（r183 一手，替代旧 verify 的猜规则实现）。

    要求：每片都是原段的**有序不重叠子串**，且「片长合计 − 切分时写入的前缀」== 原段长度
    ⇒ 既没丢字也没多字。与切分动作的实现细节无关，所以不受「猜错规则」影响。

    旧实现缺陷（实测）：按「段里有没有换行」猜规则，混合形态（多行 + 首行超长）猜错 ——
    3 片 [814, 817, 25] 对原段 1655 字，按文档规则还原得 1658 != 1655，而 verify 仍报
    ok_bytes=True ⇒ 这条腿自己会假绿（#32 / R247 同族）。
    """
    if not parts:
        return False, "零片（不得当已守恒）"
    pos = 0
    stripped = 0
    for i, part in enumerate(parts):
        body = part[2:] if (i > 0 and part.startswith("- ")) else part
        stripped += len(part) - len(body)
        j = orig_seg_text.find(body, pos)
        if j < 0:
            return False, "第 %d 片不在原段中（自 %d 起找）" % (i, pos)
        pos = j + len(body)
    if pos != len(orig_seg_text):
        return False, "有序覆盖到 %d，原段 %d ⇒ 有缺口" % (pos, len(orig_seg_text))
    total = sum(len(x) for x in parts) - stripped
    if total != len(orig_seg_text):
        return False, "片长合计 %d != 原段 %d" % (total, len(orig_seg_text))
    return True, "有序覆盖 %d/%d 字｜写入前缀 %d 字" % (pos, len(orig_seg_text), stripped)


def verify(result):
    """三重判据：① 每原段字节级可还原 ② 卷体合规 ③ 无空卷。不通即拒落盘。"""
    orig_segs = [s["text"] for s in parse_segments(result["orig"])]
    kept = [s["text"] for s in result["header_segs"]]
    # 按「原段文本 + 第几次出现」归组（键在 do_split 已定好，直接用它）
    moved = group_moved_parts(result)
    ok_bytes = True
    bad = []
    for seg, parts in moved:
        # 主判据：有序覆盖 + 长度守恒（不猜还原规则）；旧 _reconstruct 仅留作对照参考
        cov, note = cover_ok(seg, parts)
        if not cov:
            ok_bytes = False
            bad.append("%s | %s" % (seg[:28], note))
    moved_all = [seg for seg, _ in moved]
    ok_sets = sorted(kept + moved_all) == sorted(orig_segs)
    sizes_ok = all(_blen(v["content"]) <= CAP for v in result["volumes"])
    nonempty = all(v["content"].strip() for v in result["volumes"])
    return ok_bytes, sizes_ok, nonempty, bad[:3]


if __name__ == "__main__":
    src = sys.argv[1]
    hdr = int(sys.argv[2])
    start = int(sys.argv[3])
    apply_flag = "--apply" in sys.argv
    # base 缺省从 src 推：'07-next-steps.part99.md' -> '07-next-steps'
    base = None
    for a in sys.argv[4:]:
        if a.startswith("--base="):
            base = a.split("=", 1)[1]
    if base is None:
        base = src.split(".part")[0] if ".part" in src else src.rsplit(".", 1)[0]
    r = do_split(src, hdr, start, base)
    ok_bytes, sizes_ok, nonempty, bad = verify(r)
    print("[SPLIT:PLAN] %s -> %d 卷 | 字节守恒=%s 体积合规=%s 非空=%s" % (
        src, len(r["volumes"]), ok_bytes, sizes_ok, nonempty))
    if bad:
        print("  还原失败样例:", bad)
    if not (ok_bytes and sizes_ok and nonempty):
        print("[SPLIT:REFUSE] 守恒或体积判据不成立，拒绝落盘")
        raise SystemExit(1)
    if not apply_flag:
        for v in r["volumes"]:
            print("  %s %dB" % (v["name"], _blen(v["content"])))
        print("[SPLIT:DRYRUN] 加 --apply 才动盘")
        raise SystemExit(0)
    for v in r["volumes"]:
        with io.open(os.path.join(MEM, v["name"]), "w", encoding="utf-8", newline="") as f:
            f.write(v["content"])
    print("[SPLIT:APPLIED] 写入 %d 卷" % len(r["volumes"]))
    base_name = (src.split(".part")[0] + ".md") if ".part" in src else src
    print("[SPLIT:REGISTER] %s" % register_in_shell(
        [v["name"] for v in r["volumes"]], base_name))
    ok_sh, msg_sh = rewrite_source_shell(src, hdr, [v["name"] for v in r["volumes"]], r)
    print("[SPLIT:SHELL] %s" % msg_sh)
    if not ok_sh:
        raise SystemExit(1)
