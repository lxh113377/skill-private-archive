#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r306a 判据：A 臂换装「落地编辑清单」自证（edits.json -> 内存演算 -> 三读数 + 两腿负控）。

判据逻辑（怎么运作）：本件只出局部编辑清单，不出整文件重写，所以判据自己
把清单在内存里按序字面拼接（不用正则替换、不动磁盘），再从演算文本上取三个读数：
  increments_present：四条上游增量的逐字探针是否全部命中（缺一即 RED）；
  local_only_kept：两条本地独有项的逐字整块与行探针是否全部还在（缺一即 RED）；
  anchors_unique：每条编辑的锚点在演算当下是否恰好命中一次（0 次或大于 1 次即 RED）。
另两条加固读数：基线 sha 必须等于建清单时冻结的快照（防基线漂移仍报绿）；
加法式核验：旧文每一行在新文里都要还在（replace 锚点自身覆盖的行除外）。
负控两腿（证明判据有牙，不是恒绿）：
  --drop-increment I2  演算时跳过承载该增量的编辑 => increments_present<4 => FAIL
  --drop-local LO1     演算后把该本地独有整块抠掉   => local_only_kept<2 => FAIL
退出码 0=PASS、1=FAIL；末行固定 [R306A:MERGE] 供上层 grep。
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(HERE, "local_snapshot.SKILL.md")
EDITS = os.path.join(HERE, "edits.json")
CRIT = os.path.join(HERE, "criteria_r306a.json")
PREVIEW = os.path.join(HERE, "merged_preview.md")
LIVE = "D:/global_skills/A-prompt-better/SKILL.md"


def read(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def apply_edits(base, edits, skip_increment=None, dry=False):
    """按 edits.json 顺序字面拼接。anchor 命中次数 != 1 的条目不执行，交给 anchors_unique 发红。"""
    text = base
    hits = []
    for e in edits:
        anchor = e["anchor"]
        n = text.count(anchor)
        hits.append((e["id"], n))
        if n != 1:
            continue
        if skip_increment and e.get("increment") == skip_increment:
            continue
        if dry:
            continue
        new = e["new"]
        if e["op"] == "replace":
            repl = new
        elif e.get("placement") == "before":
            repl = new + anchor
        else:
            repl = anchor + new
        i = text.index(anchor)
        text = text[:i] + repl + text[i + len(anchor):]
    return text, hits


def front_value(text, key):
    """frontmatter 取键值：只看前 40 行，key: 开头的最后一行。"""
    for ln in text.split("\n")[:40]:
        if ln.startswith(key + ":"):
            return ln.split(":", 1)[1].strip()
    return "NA"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drop-increment", default=None, help="负控腿 A：增量 id，例如 I2")
    ap.add_argument("--drop-local", default=None, help="负控腿 B：本地独有 id，例如 LO1")
    args = ap.parse_args()

    crit = json.loads(read(CRIT))
    edits = json.loads(read(EDITS))
    base = read(SNAP)
    exp = crit["expected"]
    reasons = []

    if sha256_text(base) != crit["base_sha256_at_build"]:
        reasons.append("BASE_SHA_MISMATCH(演算基线与被冻结的快照不一致)")

    merged, hits = apply_edits(base, edits, skip_increment=args.drop_increment)
    anchors_unique = all(n == 1 for _, n in hits)
    bad = ["%s:%d" % (i, n) for i, n in hits if n != 1]
    if not anchors_unique:
        reasons.append("ANCHORS_NOT_UNIQUE(" + ",".join(bad) + ")")

    inc_total = len(crit["increments"])
    inc_hits = []
    increments_present = 0
    for it in crit["increments"]:
        c = merged.count(it["anchor_probe"])
        inc_hits.append("%s=%d" % (it["id"], c))
        if c >= 1:
            increments_present += 1
        else:
            reasons.append("INCREMENT_MISSING(" + it["id"] + ")")

    if args.drop_local:
        for lo in crit["local_only"]:
            if lo["id"] != args.drop_local:
                continue
            for blk in lo["verbatim_blocks"]:
                merged = merged.replace(blk, "")

    lo_total = len(crit["local_only"])
    local_only_kept = 0
    lo_detail = []
    for lo in crit["local_only"]:
        ok_blk = all(merged.count(b) >= 1 for b in lo["verbatim_blocks"])
        ok_pr = all(merged.count(p) >= 1 for p in lo["probes"])
        if ok_blk and ok_pr:
            local_only_kept += 1
        else:
            reasons.append("LOCAL_ONLY_MISSING(" + lo["id"] + ")")
        lo_detail.append("%s(blk=%d/probe=%d)" % (lo["id"], int(ok_blk), int(ok_pr)))

    # 加法式核验：旧文每行都要还在（replace 锚点自己覆盖的行除外）
    excluded = set()
    for e in edits:
        if e["op"] == "replace":
            for ln in e["anchor"].split("\n"):
                excluded.add(ln)
    lost = []
    for ln in base.split("\n"):
        if not ln.strip() or ln in excluded:
            continue
        if merged.count(ln) < 1:
            lost.append(ln[:28])
    if lost:
        reasons.append("ADDITIVE_VIOLATION(丢失行数=%d)" % len(lost))
        print("NOTE lost_lines_sample=" + " || ".join(lost[:4]))

    v_old = front_value(base, "version")
    v_new = front_value(merged, "version")
    if v_old != exp["version_old"]:
        reasons.append("VERSION_OLD_UNEXPECTED(got %s want %s)" % (v_old, exp["version_old"]))
    if v_new != exp["version_new"]:
        reasons.append("VERSION_NOT_BUMPED(got %s want %s)" % (v_new, exp["version_new"]))
    if len(edits) != exp["edits"]:
        reasons.append("EDITS_COUNT(got %d want %d)" % (len(edits), exp["edits"]))

    control = not (args.drop_increment or args.drop_local)
    if control and os.path.exists(PREVIEW):
        if read(PREVIEW) != merged:
            reasons.append("PREVIEW_MISMATCH(演算文本与 merged_preview.md 不一致)")

    live_sha = "NA"
    try:
        live_sha = sha256_text(read(LIVE))
    except Exception as ex:
        live_sha = "ERR:" + type(ex).__name__
    if control:
        print("NOTE live_source_sha=" + live_sha[:12] + " snapshot_sha=" + sha256_text(base)[:12] + (" DIFFERENT(权威源已漂移，锚点以快照为准复核)" if live_sha[:12] != sha256_text(base)[:12] else " SAME"))
    print("NOTE inc_hits=" + " ".join(inc_hits))
    print("NOTE lo_kept_detail=" + " ".join(lo_detail))
    if reasons:
        print("NOTE fail_reasons=" + " | ".join(reasons))
    gate = "PASS" if not reasons else "FAIL"
    if control:
        print("GATE=" + gate)
    else:
        print("GATE=" + gate + " NEGCONTROL=" + str(args.drop_increment or args.drop_local))
    print("[R306A:MERGE] edits=%d increments_present=%d/%d local_only_kept=%d/%d anchors_unique=%s version=%s->%s" % (
        len(edits), increments_present, inc_total, local_only_kept, lo_total,
        "true" if anchors_unique else "false", v_old, v_new))
    return 0 if not reasons else 1


if __name__ == "__main__":
    sys.exit(main())
