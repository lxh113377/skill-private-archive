#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""check_r310a.py —— 逐字吸收度尺的判据腿（尺件 absorb_gauge.py 的判定面 + 负控自测）

判据末行（固定形态，季度复跑就对这一行）
----------------------------------------
[R310A:ABSORB] skills=2 blocks=<p>/<t> locators=<lp>/<lt> overall=<x.xx%> verdict=<full|partial|broken>

verdict 口径
------------
full    = 逐字块全存在，且定位器行全存在
partial = 有缺但存在数大于 0（只吸收了一部分，或有块被改写过）
broken  = 逐字块全缺（⇒ 读错对象，或件被整体重写）
判定用「且」：块全在但定位器有缺也判 partial —— 定位器断线意味钉定证据链断了，
块即便在也不可追溯，不算 full。分母口径（剔守项、剔附属载荷件、只取 HEAD）
写在尺件的模块注释里，此处不复述，避免两处漂移。

三性标注（同时打进 stdout 与读数件）
----------------------------------
实测 = 两件的逐块连续命中与定位器整行全等，都在受管根 HEAD 现值上实跑；两负控腿内存实测。
部分 = 只判「在不在、整块还是散行」，不回头校验上游侧内容号是否仍等（上游漂移需另尺）。
未证 = 无：missing 只给逐行诊断，不归因到具体哪一轮改写所致。

负控腿（--selftest，必实测）
--------------------------
腿一 抹行：在内存里对某件现值抹掉一个逐字块的中间一行 ⇒ 该件 blocks_present 必减 1，且该条进 missing。
腿二 改位：把某条 blob 定位器行改一位（取值首字符换掉）⇒ locators_present 必减 1，blocks_present 不动。
两腿都调尺件的同一条判定函数，只换传入文本 —— 测的是尺本身，不是另一条捷径。
"""

import argparse
import ast
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import absorb_gauge as gauge   # noqa: E402  判据与尺必须同一实现，否则判的就不是尺

MARK = "[R310A:ABSORB]"
HEX = set("0123456789abcdefABCDEF")


def selfcheck_sources():
    # 落盘前纪律：两件源码都先过一遍语法解析；解析不过直接红，不留「跑到一半才炸」
    for name in ("absorb_gauge.py", "check_r310a.py"):
        p = os.path.join(gauge.here(), name)
        with open(p, "r", encoding="utf-8") as fh:
            ast.parse(fh.read(), filename=p)
        print("AST_PARSE_OK=" + name)


def raw_index_of_nth_nonblank(text, want):
    """现值里第 want 个非空行对应的原始行号 —— 抹行要按原始行抹，不能按序列抹。"""
    n = 0
    for i, l in enumerate(text.splitlines()):
        if gauge.norm(l):
            if n == want:
                return i
            n += 1
    return None


def erase_line(text, idx):
    lines = text.splitlines()
    if idx is None or idx < 0 or idx >= len(lines):
        raise SystemExit("负控抹行失败：原始行号越界 idx=" + str(idx))
    return "\n".join(lines[:idx] + lines[idx + 1:])


def flip_one_char(line):
    """把定位器行里的 blob 取值首字符改一位（其余字节一律不动）。

    只改一位是最小破坏：改两位以上可能把整行改成另一条合法 sha，
    判据要测的是「整行全等」有没有牙，不是 sha 语义。
    """
    parts = line.split()
    for i, tok in enumerate(parts):
        if i + 1 >= len(parts):
            break
        if tok == gauge.BLOB_MARK or tok.endswith(gauge.BLOB_MARK):
            sha = parts[i + 1]
            if len(sha) < 7 or any(c not in HEX for c in sha):
                return None
            head = "b" if sha[0] != "b" else "c"   # 换首位，长度不变，只动这一位
            mutated_sha = head + sha[1:]
            # 只替换首个出现的该取值，保证除这一位以外与原文完全相同
            return line.replace(sha, mutated_sha, 1)
    return None


def pick_block_sample(edits, text):
    """挑一条可抹行的样本：正文 >=3 行且当前整块存在的编辑条。"""
    seq, _ = gauge.head_lines(text)
    for e in edits:
        if e.get("op") not in ("insert", "replace"):
            continue
        body, _ = gauge.split_new(e.get("new"))
        if len(body) < 3:
            continue
        start = gauge.find_run(body, seq)
        if start >= 0:
            return e.get("id"), start, len(body)
    return None, None, None


def pick_locator_sample(edits, text):
    """挑一条可改位的样本：定位器行当前整行命中于现值的编辑条。"""
    _, seq_set = gauge.head_lines(text)
    for e in edits:
        if e.get("op") not in ("insert", "replace"):
            continue
        _body, comments = gauge.split_new(e.get("new"))
        for c in comments:
            if gauge.parse_locators([c]) and c in seq_set:
                return e.get("id"), c
    return None, None


def selftest(rev="HEAD"):
    # 判据自证：两负控腿必须实测成立，否则这把尺没牙（申报绿而实红＝假交付）
    ok_block = ok_loc = False
    for slug, object_name, rel in gauge.ARMS:
        _p, edits = gauge.load_edits(rel)
        text = gauge.git_show(object_name, rev)
        base = gauge.evaluate_skill(edits, text)

        if not ok_block:
            bid, start, blen = pick_block_sample(edits, text)
            if bid is None:
                print("SELFTEST[BLOCK-ERASE] skill=" + slug + " verdict=SKIP reason=无整块存在样本")
            else:
                mid = start + max(1, blen // 2)          # 取块中间一行，避开首尾（首尾被外部改动也会红，噪声大）
                raw = raw_index_of_nth_nonblank(text, mid)
                neg = gauge.evaluate_skill(edits, erase_line(text, raw))
                a = neg["blocks_present"] == base["blocks_present"] - 1
                b = bid in neg["missing"]
                c = bid not in base["missing"]
                ok_block = a and b and c
                print("SELFTEST[BLOCK-ERASE] skill=" + slug + " entry=" + bid + " erased_nonblank_line=" + str(mid)
                      + " blocks=" + str(base["blocks_present"]) + "/" + str(base["blocks_total"])
                      + " -> " + str(neg["blocks_present"]) + "/" + str(neg["blocks_total"])
                      + " missing_after=" + json.dumps(neg["missing"], ensure_ascii=False)
                      + " minus1=" + str(a) + " in_missing=" + str(b) + " baseline_clean=" + str(c)
                      + " verdict=" + ("PASS" if ok_block else "FAIL"))

        if not ok_loc:
            lid, loc_line = pick_locator_sample(edits, text)
            if loc_line is None:
                print("SELFTEST[LOCATOR-MUTATE] skill=" + slug + " verdict=SKIP reason=无定位器命中样本")
            else:
                mutated = flip_one_char(loc_line)
                if mutated is None:
                    print("SELFTEST[LOCATOR-MUTATE] skill=" + slug + " verdict=FAIL reason=定位器行解析不出 sha")
                else:
                    neg = gauge.evaluate_skill(edits, text.replace(loc_line, mutated, 1))
                    a = neg["locators_present"] == base["locators_present"] - 1
                    stable = neg["blocks_present"] == base["blocks_present"]
                    flagged = any((not x["line_present"]) for d in neg["detail"] for x in d["locators"])
                    ok_loc = a and stable and flagged
                    print("SELFTEST[LOCATOR-MUTATE] skill=" + slug + " entry=" + lid
                          + " locators=" + str(base["locators_present"]) + "/" + str(base["locators_total"])
                          + " -> " + str(neg["locators_present"]) + "/" + str(neg["locators_total"])
                          + " minus1=" + str(a) + " blocks_stable=" + str(stable) + " flagged=" + str(flagged)
                          + " verdict=" + ("PASS" if ok_loc else "FAIL"))
        if ok_block and ok_loc:
            break
    if not (ok_block and ok_loc):
        print("SELFTEST=FAIL legs=" + json.dumps({"block_erase": ok_block, "locator_mutate": ok_loc}, ensure_ascii=False))
        return 1
    print("SELFTEST=PASS legs=2")
    return 0


def main(argv=None):
    gauge.utf8_stdout()
    ap = argparse.ArgumentParser(description="逐字吸收度尺判据腿：出末行判定；负控走 --selftest")
    ap.add_argument("--rev", default="HEAD", help="受管根版本（默认 HEAD）")
    ap.add_argument("--selftest", action="store_true", help="两负控腿实测（判据自证，必测）")
    ap.add_argument("--no-write", action="store_true", help="不落读数件")
    ap.add_argument("--out", default=os.path.join(gauge.here(), "absorb_reading.json"))
    args = ap.parse_args(argv)
    selfcheck_sources()
    if args.selftest:
        return selftest(args.rev)
    record = gauge.build_record(print_keys=True, rev=args.rev)
    if not args.no_write:
        gauge.dump_json(record, args.out)
        print("READING_DUMPED=" + args.out)
    t = record["totals"]
    bp, bt = t["blocks_present"], t["blocks_total"]
    lp, lt = t["locators_present"], t["locators_total"]
    if bt == 0 or bp == 0:
        verdict = "broken"      # 全缺：读错对象，或件被整体重写
    elif bp == bt and lp == lt:
        verdict = "full"
    else:
        verdict = "partial"
    print("SANXING 实测=" + record["sanxing"]["实测"])
    print("SANXING 部分=" + record["sanxing"]["部分"])
    print("SANXING 未证=" + record["sanxing"]["未证"])
    print(MARK + " skills=" + str(len(record["skills"]))
          + " blocks=" + str(bp) + "/" + str(bt)
          + " locators=" + str(lp) + "/" + str(lt)
          + " overall=" + format(record["overall_rate"], ".2f") + "%"
          + " verdict=" + verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
