# -*- coding: utf-8 -*-
"""r35_tracked_empty.py — 第 7 道门：仓库里不得存在 0 字节的 tracked 文本文件（r35 H-1）。

存在理由（**本仓自伤实证，不是假想防御**）：
    r34 我用一条带 `if False else` 链的 python 表达式写 `memory/AGENTS.md`，
    表达式最终求值成空串 ⇒ `open(p, "w")` 立刻把文件清空到 **0 字节**。
    当轮靠 `git checkout HEAD --` 精确恢复（10,777B 全等）才没造成损失。
    事后我只在报告里立了"写文件禁内联复杂条件表达式"这条**规则** —— 按本仓 A-get-memory Step 2.7 的口径，
    那只算**自觉型落点**（下一个会话不做任何事就不生效），故本轮补成**机器型**：
    任何一次写崩、截断、编码事故留下的 0 字节件，都会在下次动手前的门禁里被点名。

判据（三态，沿用 run_gates 的 R247 语义）：
    PASS        扫描面非空，且 0 字节 tracked 文本件 = 0
    FAIL        存在 0 字节 tracked **文本**件（.md/.py/.json/.yml/.txt/.jsonl 等）
    UNVERIFIED  `git ls-files` 取不到、仓库无 tracked 件、或本脚本自身依赖缺失 ⇒ 一律不得算绿
二进制件（png/zip 等）不参与判定，但**如实登记 skipped 数**（防"跳过即通过"的读法）。

用法：
    python 05-exec/r35_tracked_empty.py [--json 件.json] [--root 仓库根]
退出码：0 PASS / 1 FAIL / 2 UNVERIFIED
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

TEXT_EXT = (".md", ".py", ".json", ".jsonl", ".yml", ".yaml", ".txt", ".cfg", ".ini", ".ps1", ".sh", ".toml")
BIN_HINT = (".png", ".jpg", ".jpeg", ".gif", ".ico", ".zip", ".gz", ".whl", ".pdf", ".docx", ".xlsx", ".pptx", ".mp4", ".mp3", ".onnx", ".npy")


def tracked_files(root):
    """`git ls-files -s` 取 tracked 清单。失败 ⇒ 返回 None（调用方必须判 UNVERIFIED，不得当"0 件"）。"""
    try:
        p = subprocess.run(["git", "-C", root, "ls-files", "-z"],
                           capture_output=True, timeout=60)
    except Exception as e:
        return None, "git 调用异常: %s" % e
    if p.returncode != 0:
        return None, "git ls-files 退出码 %s: %s" % (p.returncode, p.stderr.decode("utf-8", "replace")[:120])
    names = [n.decode("utf-8", "replace") for n in p.stdout.split(b"\0") if n]
    return names, None


def judge(root):
    """返回 (state, detail_dict)。

    单出口设计（r35 变异实测逼出来的）：状态只在唯一位置赋值、末尾唯一 return。
    多 return 写法会让"改状态却仍走旧 return"这类变异**行为不变**，
    从而出现"变异集看着齐全、其实没有鉴别力"的假验证（本轮 M2/M5 实测踩到）。
    """
    names, err = tracked_files(root)
    base = {"root": root, "tracked": 0 if names is None else len(names), "error": err,
            "zero_byte": [], "skipped_binary_or_unknown": 0}
    if names is None:
        state, why = "UNVERIFIED", "取数失败：%s ⇒ 不得当作「没有 0 字节文件」（R247）" % err
    elif not names:
        state, why = "UNVERIFIED", "tracked 清单为空（无文件不等于通过，R247）"
    else:
        zero, missing, skipped_bin, checked = [], [], 0, 0
        for n in names:
            fp = os.path.join(root, n.replace("/", os.sep))
            low = n.lower()
            if low.endswith(BIN_HINT) or not low.endswith(TEXT_EXT):
                skipped_bin += 1      # 二进制/未知扩展：跳过但**如实计数**，不静默
                continue
            if not os.path.exists(fp):
                missing.append(n)
                continue
            checked += 1
            try:
                if os.path.getsize(fp) == 0:
                    zero.append(n)
            except OSError:
                missing.append(n)
        base.update(checked_text=checked, zero_byte=zero, missing_on_disk=missing,
                    skipped_binary_or_unknown=skipped_bin)
        if not checked:
            state, why = "UNVERIFIED", "文本面为 0（扫描面为空不得判过，R247）"
        elif zero:
            state, why = "FAIL", "0 字节 tracked 文本件 %d 个" % len(zero)
        else:
            state, why = "PASS", "文本面 %d 件均非空；跳过二进制/未知扩展 %d 件（如实登记，非当作通过）" % (
                checked, skipped_bin)
    base.update(state=state, why=why)
    return state, base


MARK = {"PASS": "[EMPTY:PASS]", "FAIL": "[EMPTY:FAIL]", "UNVERIFIED": "[EMPTY:UNVERIFIED]"}
RC = {"PASS": 0, "FAIL": 1, "UNVERIFIED": 2}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--json")
    args = ap.parse_args()

    state, d = judge(args.root)
    print("=== 0 字节 tracked 文件门禁（r35 H-1；防 r34 我自己那次写崩事故复发）===")
    print("仓库: %s｜tracked %d 件｜受检文本 %s 件" % (d["root"], d["tracked"], d.get("checked_text", 0)))
    print("跳过: 二进制/未知扩展 %d 件（登记不静默）" % d.get("skipped_binary_or_unknown", 0))
    if d.get("missing_on_disk"):
        print("⚠️ tracked 但盘上缺失 %d 件: %s" % (len(d["missing_on_disk"]), d["missing_on_disk"][:5]))
    if d["zero_byte"]:
        print("0 字节件: %s" % ", ".join(d["zero_byte"][:20]))
    print("%s %s" % (MARK[state], d["why"]))
    if args.json:
        doc = {"schema": "tracked-empty-gate-v1", "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
               "readonly": True, "benchmark": "r35 H-1 写崩/截断事故的机器型回收",
               "state": state, "why": d["why"], "coverage": [d["root"]],
               "details": d}
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(json.dumps(doc, ensure_ascii=False, indent=1))
        print("JSON -> %s" % args.json)
    return RC[state]


if __name__ == "__main__":
    raise SystemExit(main())
