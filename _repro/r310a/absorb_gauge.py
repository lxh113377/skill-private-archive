#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""absorb_gauge.py —— 逐字吸收度尺（常驻判据，季度可复跑）

量什么
------
换装落地时，每条 insert 或 replace 编辑都在 new 里带了「上游逐字块正文」外加一行钉定注释，
注释内含 blob 定位器。本尺回答两件事：
  1) 上游逐字块今天在受管根里在不在 —— 按整块存在判，不是零散行在；
  2) 钉定注释里的 blob 定位器行在不在。
任务质量尺抓不到「上游原文是否真在本地件里」这层差异（前一轮锚题实验的结论），
所以独立成一把尺：一次写成、季度复跑，不是一次性探针。

口径（取舍全写在这里，避免读数歧义；三性标注见输出件的 sanxing 面）
------------------------------------------------------------------
对象 = 两件技能各自主件在受管根 HEAD 的现值。只读取，经 git show 取，不读工作区：
工作区可能被并行会话改动，按 HEAD 取才能保证任何时刻复跑读到同一对象。
分母 = 两件各自的 insert 或 replace 编辑，逐条各成一个「逐字块」。
op 为 hold 的编辑不算上游块：它们是本地独有守项（不动上游、不往件里写正文），
另记 held 数，不入吸收分母。
随落地一并铺开的附属载荷件（脚本、参考件、资产）不在本次分母里 ——
尺的对象只有两件主件的吸收块，混进来会把分母撑大、把率读低。
逐字块正文 = 该条编辑的 new 剔掉「钉定注释行」（以 HTML 注释起头的行）与「排版空行」后剩下的行。
逐字 = 整行 strip 后全等；不 strip 行内部空白 —— 行内空格或缩进漂移即判被改写。
整块存在 = 该块全部行按原顺序，在现值的非空行序列里连续命中一次。
块被拆开、行序被打乱、任一行被改写，都判 missing，并附逐行诊断（找到几行、第一条缺的是哪行）。
定位器 = 钉定注释行本身；一条编辑一行，按整行 strip 全等在现值里各验一次。
注释里解析出的 blob 与 commit 取值另存为证据面，不参与判定（判定只看整行，改一位即失配）。
剔完注释与空行后无正文的编辑（如守项条）不入分母。
定位器分两态：整行命中才算在；文本仍在但被并入他行记为内联（inline_only）仍算缺 ——
钉定注释的价值在能按行 grep 追溯，挤进他行等于证据链变细。
块内含本地自写行（清单 self_written_lines 所列）不因此把块拆成半上游：整块仍按一条验，
只在逐块明细里记该块含几条自写行，让季度复跑看得出这块并非百分之百上游。
"""

import argparse
import json
import os
import subprocess
import sys

NL = chr(10)
COMMENT_PREFIX = "<!--"
BLOB_MARK = "blob_sha"
COMMIT_MARK = "commit"
CONTENT_MARK = "content_sha256"

# 实际路径只出现在下面的常量里，散文与注释不复制路径形态串（防陈旧指针）
GIT_REPOSITORY = "D:/global_skills"        # 受管根，只读（允许 git show，禁任何 git 写）
ARMS = (
    # 件名, 受管根 HEAD 对象名, 落地编辑清单相对工作区根的片段
    ("A-prompt-better", "A-prompt-better/SKILL.md", ("_repro", "r306a", "edits.json")),
    ("frontend-skill", "frontend-skill/SKILL.md", ("_repro", "r307b", "edits.json")),
)


def utf8_stdout():
    # 中文 Windows 默认 GBK，打印 CJK 会当场炸；统一把 stdout 钉成 UTF-8
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def here():
    return os.path.dirname(os.path.abspath(__file__))


def workspace_root():
    # 本件常驻临时目录的末级，编辑清单在上跳两级的工作区分卷里
    return os.path.abspath(os.path.join(here(), os.pardir, os.pardir))


def git_show(object_name, rev="HEAD"):
    """只读受管根某版本下某对象的正文；bytes 显式按 UTF-8 解码，不吃 locale。

    实测坑（本机 git 2.56）：git show 只给工作树路径（不带版本前缀）会返回 rc=0 而正文 0 字节，
    看起来像「件里什么都没有」—— 那会把吸收率读成 0/12 的假红。
    正解 = cat-file blob 配「版本:路径」的显式对象名，取的一定是提交里的对象而非工作树。
    """
    proc = subprocess.run(
        ["git", "-C", GIT_REPOSITORY, "cat-file", "blob", rev + ":" + object_name],
        capture_output=True,
    )
    if proc.returncode != 0:
        raise SystemExit(
            "git cat-file 失败 rc=" + str(proc.returncode) + " obj=" + rev + ":" + object_name
            + " err=" + proc.stderr.decode("utf-8", "replace").strip()[:300]
        )
    return proc.stdout.decode("utf-8", "replace")


def git_head_commit(rev="HEAD"):
    proc = subprocess.run(["git", "-C", GIT_REPOSITORY, "rev-parse", rev], capture_output=True)
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("ascii", "replace").strip()


def load_edits(rel_parts, base=None):
    p = os.path.join(base or workspace_root(), *rel_parts)
    with open(p, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise SystemExit("编辑清单顶层不是数组: " + p)
    return p, data


def norm(line):
    # 逐字口径：整行 strip，不动行内部空白
    return line.strip()


def split_new(new_text):
    """把一条编辑的 new 拆成 正文行 与 钉定注释行 两组。"""
    body, comments = [], []
    for raw in (new_text or "").splitlines():
        s = norm(raw)
        if not s:
            continue            # 排版空行剔除
        if s.startswith(COMMENT_PREFIX):
            comments.append(s)  # 钉定注释行，定位器的载体
            continue
        body.append(s)          # 逐字块正文
    return body, comments


def head_lines(text):
    """现值 → (非空行序列, 非空行集合)。空行不参与连续判定，两侧同口径。"""
    seq = [norm(l) for l in text.splitlines() if norm(l)]
    return seq, set(seq)


def tokens_after(line, mark):
    """按空白切词取 mark 后面的取值，避免正则与转义。

    两臂的注释写法不同：一臂带前缀（upstream_ 接该词），一臂直接是该词，
    所以「整词相等」与「以该词收尾」两种形态都认，取其下一个词作为取值。
    """
    parts = line.split()
    for i, tok in enumerate(parts):
        if i + 1 >= len(parts):
            break
        if tok == mark or tok.endswith(mark):
            return parts[i + 1]
    return None

def parse_locators(comments):
    """从钉定注释行解析 blob / commit / 内容号，作为证据面（不参与判定）。"""
    out = []
    for c in comments:
        blob = tokens_after(c, BLOB_MARK)
        if not blob:
            continue
        out.append({
            "line": c,
            "blob_sha": blob,
            "commit": tokens_after(c, COMMIT_MARK),
            "content_sha256": tokens_after(c, CONTENT_MARK),
        })
    return out


def find_run(needle, hay):
    """连续整块命中：返回起始下标，未命中 -1；空块返回 -2 由调用方挡掉。"""
    n = len(needle)
    if n == 0:
        return -2
    if n > len(hay):
        return -1
    for i in range(len(hay) - n + 1):
        if hay[i:i + n] == needle:
            return i
    return -1


def diagnose(needle, hay_set):
    """missing 时的逐行诊断：命中几行、第一条不在现值里的行是哪行。"""
    found = sum(1 for x in needle if x in hay_set)
    first_absent = None
    for x in needle:
        if x not in hay_set:
            first_absent = x
            break
    return {"lines_total": len(needle), "lines_found": found, "first_absent_line": first_absent}


def evaluate_skill(edits, current_text):
    """单件判定：吸收读数加逐块明细。判定只看整块连续与定位器整行全等。

    参数 current_text 可由调用方替换 —— 负控腿就是在内存里换掉它，走的仍是同一判定路径，
    这样负控测的是尺本身，不是另一条捷径。
    """
    seq, seq_set = head_lines(current_text)
    blocks_total = blocks_present = 0
    locators_total = locators_present = 0
    held = 0
    missing = []
    detail = []
    locators_inline = []
    for e in edits:
        op = e.get("op")
        eid = e.get("id")
        if op == "hold":
            held += 1            # 本地独有守项：另记，不入吸收分母
            continue
        if op not in ("insert", "replace"):
            continue
        body, comments = split_new(e.get("new"))
        if not body:
            continue             # 无正文的编辑不入分母
        blocks_total += 1
        start = find_run(body, seq)
        present = start >= 0
        if present:
            blocks_present += 1
        else:
            missing.append(eid)
        locs = parse_locators(comments)
        loc_flags = [(l["line"] in seq_set) for l in locs]
        locators_total += len(locs)
        locators_present += sum(1 for f in loc_flags if f)
        # 定位器两态：整行命中算在；文本仍在但被并入他行（如落到版本历史行的行尾）记 inline_only 仍算缺 ——
        # 钉定注释的价值在能按行 grep 追溯，挤进他行等于证据链变细。
        for l, f in zip(locs, loc_flags):
            if f:
                continue
            holders = [i for i, x in enumerate(seq) if l["line"] in x and x != l["line"]]
            l["inline_only_in_line_index"] = holders[0] if holders else None
            if holders:
                locators_inline.append(eid)
        # 块内自写行：整块仍按一条验（不因此拆成半上游），只在 detail 记条数，让复跑看得出这块不全是上游
        self_written = [norm(x) for x in (e.get("self_written_lines") or []) if norm(x)]
        entry = {
            "id": eid,
            "op": op,
            "increment": e.get("increment"),
            "block_lines": len(body),
            "block_present": present,
            "block_start_line_index": start if present else None,
            "pinned_comment_lines": len(comments),
            "self_written_lines_in_block": sum(1 for s in self_written if s in body),
            "locators": [
                {"blob_sha": l["blob_sha"], "commit": l["commit"],
                 "content_sha256": l["content_sha256"], "line_present": f,
                 "inline_only_in_line_index": l.get("inline_only_in_line_index")}
                for l, f in zip(locs, loc_flags)
            ],
        }
        if not present:
            entry["diagnosis"] = diagnose(body, seq_set)
        detail.append(entry)
    rate = (100.0 * blocks_present / blocks_total) if blocks_total else 0.0
    return {
        "blocks_total": blocks_total,
        "blocks_present": blocks_present,
        "missing": missing,
        "locators_total": locators_total,
        "locators_present": locators_present,
        "locators_inline_only": locators_inline,
        "held": held,
        "rate": round(rate, 2),
        "detail": detail,
    }


def build_record(print_keys=True, base=None, texts=None, rev="HEAD"):
    """跑全部两件；现值文本可由调用方在内存注入（负控腿复用同一路径）。

    rev 默认 HEAD：季度复跑读的就是当时的主线现值；要把某季的读数钉死重算，传该季的提交号即可。
    """
    record = {"skills": {}, "overall_rate": 0.0}
    cache = dict(texts or {})
    bp = bt = lp = lt = 0
    for slug, object_name, rel in ARMS:
        p, edits = load_edits(rel, base=base)
        if print_keys:
            # 纪律：先 print 排序后的键面，逐条列出编辑的键，防止凭记忆猜字段
            for e in edits:
                print("KEYS[" + slug + "#" + str(e.get("id")) + "]=" + json.dumps(sorted(e.keys()), ensure_ascii=False))
            print("EDITS_SOURCE[" + slug + "] entries=" + str(len(edits)))
        if object_name not in cache:
            cache[object_name] = git_show(object_name, rev)
        text = cache[object_name]
        one = evaluate_skill(edits, text)
        one["head_object"] = object_name
        one["head_lines_nonblank"] = len(head_lines(text)[0])
        record["skills"][slug] = one
        bp += one["blocks_present"]
        bt += one["blocks_total"]
        lp += one["locators_present"]
        lt += one["locators_total"]
    record["overall_rate"] = round(100.0 * bp / bt, 2) if bt else 0.0
    record["totals"] = {"blocks_present": bp, "blocks_total": bt,
                        "locators_present": lp, "locators_total": lt}
    record["head_commit"] = git_head_commit(rev)
    record["head_rev"] = rev
    record["denominator_scope"] = {
        "in": "两件主件的 insert 或 replace 逐字块 + 钉定注释定位器行",
        "out": ["随落地铺开的附属载荷件（脚本、参考件、资产）—— 非本次分母",
                "op 为 hold 的本地独有守项（另记 held，不入吸收分母）",
                "工作区现值（只取 HEAD，保复跑同对象）"],
    }
    record["sanxing"] = {
        "实测": "逐块整块连续性与定位器整行全等，均在 HEAD 现值上实跑；两负控腿见判据件的 selftest",
        "部分": "present 仅代表整块在 HEAD 逐字存在，不回头校验上游侧内容号是否仍等（上游侧漂移需另尺）",
        "未证": "无：missing 的归因只到逐行诊断层，未逐条追是哪一轮改写所致",
    }
    return record


def dump_json(record, out_path):
    text = json.dumps(record, ensure_ascii=False, indent=2)
    json.loads(text)          # 落盘前自证：能 dumps 出来必须能 loads 回去
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text + NL)
    return out_path


def report(record):
    for slug, one in record["skills"].items():
        print("SKILL[" + slug + "] blocks=" + str(one["blocks_present"]) + "/" + str(one["blocks_total"])
              + " locators=" + str(one["locators_present"]) + "/" + str(one["locators_total"])
              + " inline_only_locators=" + json.dumps(one["locators_inline_only"], ensure_ascii=False)
              + " held=" + str(one["held"]) + " missing=" + json.dumps(one["missing"], ensure_ascii=False))
    print("OVERALL=" + str(record["overall_rate"]) + " head_commit=" + str(record["head_commit"]))


def main(argv=None):
    utf8_stdout()
    ap = argparse.ArgumentParser(
        description="逐字吸收度尺：验上游逐字块与 blob 定位器在受管根 HEAD 现值里在不在")
    ap.add_argument("--out", default=os.path.join(here(), "absorb_reading.json"))
    ap.add_argument("--no-write", action="store_true", help="只算不写盘")
    ap.add_argument("--quiet-keys", action="store_true", help="不打印逐条排序键面")
    ap.add_argument("--rev", default="HEAD", help="受管根版本（默认 HEAD；季度复跑可钉某提交号）")
    ap.add_argument("--ast-selfcheck", action="store_true", help="先把本件源码过一遍语法解析再跑")
    args = ap.parse_args(argv)
    if args.ast_selfcheck:
        import ast
        src = os.path.join(here(), os.path.basename(__file__))
        with open(src, "r", encoding="utf-8") as fh:
            ast.parse(fh.read(), filename=src)
        print("AST_SELFCHECK=OK")
    record = build_record(print_keys=not args.quiet_keys, rev=args.rev)
    report(record)
    if not args.no_write:
        dump_json(record, args.out)
        print("WROTE=" + args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
