# -*- coding: utf-8 -*-
"""r103_note_patch.py — 生成 GM cross_platform_map.json 的 note 同步补丁（old/new 两片）。

为什么用本件而不是内联 -c：C6 判据要求 GM note 里登记的版本号集合含仓库版 version，
而 note 是**被 JSON 转义过的长串**；内联 python -c 在 Git Bash 下会吞反斜杠、把 `"` 与
`\\u` 转义写坏（本仓 shell-encoding-pitfalls 老坑），生成的 old 与盘上字节不等 ⇒
rule_editor 的「锚点须恰好命中一次」预检会红，或更糟：命中了错误的字节。

退出码：0=两片已生成且 old 在盘上恰好命中一次；1=命中数 != 1（不落片，禁止盲改）。
"""
import io
import json
import os
import sys

GM = r"D:/global_memory/cross_platform_map.json"
OUT_DIR = os.environ.get("TEMP", "/tmp")
OLD_P = os.path.join(OUT_DIR, "r103_old.txt")
NEW_P = os.path.join(OUT_DIR, "r103_new.txt")

ANCHOR = "install_state 同步至 V1.33"
ADD = ("install_state 同步至 V1.33; 2026-10-03 r103 换装轮装入 3 件 healthcare 模式件"
       "（healthcare-cdss-patterns / healthcare-emr-patterns / healthcare-eval-harness，"
       "源 affaan-m/ECC@main，MIT，逐件 sha256 读回全等），registry 173→176，"
       "install_state 同步至 V1.34")


def main():
    raw = io.open(GM, encoding="utf-8").read()
    doc = json.loads(raw)
    repo_ver = json.load(io.open(
        r"C:/Users/37533/Desktop/workspace/焚诀/skill/registry/cross_platform_map.json",
        encoding="utf-8"))["version"]
    if ANCHOR not in raw:
        print("[NOTE-PATCH:FAIL] 盘上找不到锚点 %r" % ANCHOR)
        return 1
    n = raw.count(ANCHOR)
    if n != 1:
        print("[NOTE-PATCH:FAIL] 锚点命中 %d 次（须==1），不落片" % n)
        return 1
    if ADD in raw:
        print("[NOTE-PATCH:ALREADY] note 已含 V1.34 补注，无需改动")
        return 0
    with io.open(OLD_P, "w", encoding="utf-8", newline="") as f:
        f.write(ANCHOR)
    with io.open(NEW_P, "w", encoding="utf-8", newline="") as f:
        f.write(ADD)
    print(json.dumps({"repo_version": repo_ver, "gm_version_before": doc.get("version"),
                      "anchor_hits": n, "old_file": OLD_P, "new_file": NEW_P,
                      "note_bytes_delta": len(ADD) - len(ANCHOR)},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
