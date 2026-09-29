# -*- coding: utf-8 -*-
r"""r60_retire_two.py — 已登记退役件的「备份 -> 验证 -> 移出扫描树」执行器（R59-4 / r60）.

存在理由（r59 一手）：`executing-plans` 与 `slides` 早已在 `焚诀/eval/truth_constants.json`
的 `retired_skills` 里，磁盘上却仍带 SKILL.md 且能被会话加载；r59 的 `r59_retire.py` 只落在
`$TEMP` 里（生成器不在仓 = 死句柄，W-46 通病），且当时被三重护栏拦下未执行。本件是该动作的
**仓内实物**，并把「未验证的备份只是希望」做成判据：先备份、再逐文件 sha256 读回比对、
**比对通过才允许 mv**，mv 后再核原件已离树。

铁律 3：备份落 `D:\global_memory\_trash\<标签>_<ts>\`（`_bak` 禁用），且必须整体移出
`D:\global_skills` 树 —— 留树内会被扫描面看见。

取值：
    python 05-exec/r60_retire_two.py                 # 预演：只备份 + 验证，不动树
    python 05-exec/r60_retire_two.py --apply-mv      # 备份验证通过后把原件移出扫描树
退出码：0 = 备份与验证通过（--apply-mv 时含离树校验）；1 = 备份或验证失败（未执行 mv）；
        2 = UNVERIFIED（目标不在盘 / 备份根不可写 / 目标已不在扫描树 —— 零面不判完成，R247）。
"""

import argparse
import hashlib
import io
import json
import os
import shutil
import sys
from datetime import datetime

AUTHORITY = r"D:\global_skills"
BACKUP_ROOT = r"D:\global_memory\_trash"
TRUTH = r"C:\Users\37533\Desktop\workspace\焚诀\eval\truth_constants.json"
TARGETS = ("executing-plans", "slides")


def sha256_file(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def walk_files(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            full = os.path.join(dirpath, name)
            out.append((os.path.relpath(full, root).replace("\\", "/"), full))
    return out


def registered_retired():
    doc = json.loads(io.open(TRUTH, encoding="utf-8-sig").read())
    return set(doc.get("retired_skills") or [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply-mv", action="store_true")
    ap.add_argument("--tag", default="r60_retire_" + datetime.now().strftime("%Y-%m-%d"))
    args = ap.parse_args()

    retired = registered_retired()
    if not retired:
        sys.stderr.write("[RETIRE:UNVERIFIED] retired_skills 为空，零面不得判「无残留」（R247）\n")
        return 2

    present = [t for t in TARGETS if os.path.isdir(os.path.join(AUTHORITY, t))]
    if not present:
        sys.stderr.write("[RETIRE:UNVERIFIED] 两件均不在盘：可能已被移出。核 probe：%s\n"
                         % os.path.join(AUTHORITY, TARGETS[0]))
        return 2

    missing_reg = [t for t in present if t not in retired]
    if missing_reg:
        sys.stderr.write("[RETIRE:FAIL] 在盘但不在退役名单，拒绝处置（防误伤在用件）：%s\n" % missing_reg)
        return 1

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_ROOT, args.tag + "_" + stamp)
    os.makedirs(dest, exist_ok=False)
    manifest = []

    for name in present:
        src = os.path.join(AUTHORITY, name)
        dst = os.path.join(dest, name)
        files = walk_files(src)
        if not files:
            sys.stderr.write("[RETIRE:FAIL] %s 下 0 个文件，空面不判完成\n" % name)
            return 1
        shutil.copytree(src, dst)
        for rel, full in files:
            src_sha = sha256_file(full)
            back_sha = sha256_file(os.path.join(dst, rel))
            if src_sha != back_sha:
                sys.stderr.write("[RETIRE:FAIL] 备份 sha 不一致 %s/%s\n" % (name, rel))
                return 1
            manifest.append("%s  %s/%s" % (src_sha, name, rel))
        print("[BACKUP:OK] %-18s files=%-3d sha256 全部读回一致" % (name, len(files)))

    mpath = os.path.join(dest, "MANIFEST.txt")
    with io.open(mpath, "w", encoding="utf-8", newline="\n") as f:
        f.write("r60 retire backup  %s\n" % datetime.now().isoformat(timespec="seconds"))
        f.write("source = %s\n" % AUTHORITY)
        f.write("restore = copy <dir>/<name> back to %s\\<name>, then rerun verify\n\n" % AUTHORITY)
        f.write("sha256                                                            path\n")
        f.write("\n".join(manifest) + "\n")
    # 清单自身读回：断言每一行都能在备份树里再算一遍
    lines = [l for l in io.open(mpath, encoding="utf-8").read().split("\n") if "  " in l and len(l) > 70]
    for line in lines:
        sh, rel = line.split("  ", 1)
        if sha256_file(os.path.join(dest, rel)) != sh:
            sys.stderr.write("[RETIRE:FAIL] 清单行读回不一致: %s\n" % rel)
            return 1
    print("[MANIFEST:OK] %d 行，逐行读回复算一致 -> %s" % (len(lines), mpath))

    if not args.apply_mv:
        print("[RETIRE:DRYRUN] 备份与验证通过；加 --apply-mv 才移出扫描树。备份=%s" % dest)
        return 0

    for name in present:
        shutil.move(os.path.join(AUTHORITY, name), os.path.join(dest, name + "__moved"))
    left = [t for t in TARGETS if os.path.isdir(os.path.join(AUTHORITY, t))]
    if left:
        sys.stderr.write("[RETIRE:FAIL] 移出后仍在扫描树：%s（回滚：从 %s 拷回）\n" % (left, dest))
        return 1
    print("[RETIRE:OK] 两件已移出 %s；回滚锚 = %s" % (AUTHORITY, dest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
