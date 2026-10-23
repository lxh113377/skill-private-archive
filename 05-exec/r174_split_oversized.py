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


def _reconstruct(orig_seg_text, parts):
    """把一个原段的全部 parts 还原成原文；规则见 split_long_line/split_segment docstring。"""
    if NL in orig_seg_text:
        return NL.join(parts)
    return parts[0] + "".join(p[2:] if p.startswith("- ") else p for p in parts[1:])


def verify(result):
    """三重判据：① 每原段字节级可还原 ② 卷体合规 ③ 无空卷。不通即拒落盘。"""
    orig_segs = [s["text"] for s in parse_segments(result["orig"])]
    kept = [s["text"] for s in result["header_segs"]]
    # 按「原段文本 + 第几次出现」归组（键在 do_split 已定好，直接用它）
    groups = {}
    order = []
    for v in result["volumes"]:
        body = v["content"].split(NL, 3)[3] if v["content"].count(NL) >= 3 else ""
        for s, k in zip(parse_segments(body), v["placement"]):
            if k not in groups:
                groups[k] = []
                order.append(k)
            groups[k].append(s["text"])
    ok_bytes = True
    bad = []
    for key in order:
        seg = key[0]
        rebuilt = _reconstruct(seg, groups[key])
        if rebuilt != seg:
            ok_bytes = False
            bad.append(seg[:40])
    moved_all = [k[0] for k in order]
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
