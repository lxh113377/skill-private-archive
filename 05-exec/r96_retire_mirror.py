# -*- coding: utf-8 -*-
r"""r96_retire_mirror.py — 把已退役两件的「移出扫描树」动作传播到镜像根.

存在理由（r96 一手）：`r60_retire_two.py` 的 AUTHORITY 只有 `D:\global_skills`；移出后复跑
`r59_retired_face.py` 得 `[GATE:retired-face-pass] blacklist=72 disk=169`，但本会话的可用技能清单
**仍列着 executing-plans 与 slides** —— 因为 `C:\Users\37533\.agents\skills` 是**独立 git 仓的真实目录副本**
（非 junction），它也在向会话供给这两件。只清权威源 = 退役只做了一半（呼应 [[feedback-fix-the-producer-covers-all-egress]]：
判据要说「已移出」，得覆盖该产物的全部写出出口）。

与权威源侧的两处差异，决定了本件不能照抄 r60：
  1. 镜像仓 **无远端**（实测 `git remote -v` 空）⇒ 按 R9 铁律「只有本地 .git 不算备份」，
     本件仍然先做 sha256 读回备份，再动 git；两者互不顶替。
  2. 镜像仓工作区有 **474 条他人在途脏项**（实测 `git status --porcelain | wc -l`）⇒ 一律用
     `git commit -- <显式路径>` 限定提交面，禁 `git add -A` / 禁裸 commit（R236 多会话并发铁律）。

取值：
    python 05-exec/r96_retire_mirror.py            # 预演：只备份 + sha256 读回，不动盘
    python 05-exec/r96_retire_mirror.py --apply    # 备份验证通过后 git rm + 限定路径提交
退出码：0 = 成功；1 = 备份/验证/提交任一步失败（未执行后续步）；
        2 = UNVERIFIED（目标不在镜像树 / 已提交过 / 取不到 dirty 计数 —— 零面不判完成，R247）。
"""

import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

MIRROR = r"C:\Users\37533\.agents\skills"
BACKUP_ROOT = r"D:\global_memory\_trash"
TARGETS = ("executing-plans", "slides")


def sha256_file(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def walk_files(root):
    out = []
    for dirpath, _dn, filenames in os.walk(root):
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            out.append((os.path.relpath(p, root).replace("\\", "/"), p))
    return sorted(out)


def git(args, cwd=MIRROR):
    p = subprocess.run(["git"] + args, cwd=cwd, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def backup_one(name, tag_dir):
    src = os.path.join(MIRROR, name)
    if not os.path.isdir(src):
        return None, "absent"
    files = walk_files(src)
    if not files:
        return None, "empty face"
    dst = os.path.join(tag_dir, "copy", name)
    shutil.copytree(src, dst)
    bad = []
    for rel, p in files:
        want = sha256_file(p)
        cp = os.path.join(dst, rel.replace("/", os.sep))
        got = sha256_file(cp) if os.path.isfile(cp) else None
        if got != want:
            bad.append(rel)
    return {"files": len(files), "mismatch": bad, "dst": dst}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()

    if not os.path.isdir(MIRROR):
        print("[GATE:r96mirror-unverified] 镜像根不存在: %s" % MIRROR)
        return 2

    # 他人在途脏项计数必须先取到，取不到就不声称「限定提交是安全的」
    rc, out, err = git(["status", "--porcelain"])
    if rc != 0:
        print("[GATE:r96mirror-unverified] git status 失败 rc=%s %s" % (rc, err))
        return 2
    dirty_total = len([x for x in out.splitlines() if x.strip()])

    tag = a.tag or ("r96_retire_mirror_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    tag_dir = os.path.join(BACKUP_ROOT, tag)
    os.makedirs(tag_dir, exist_ok=True)

    results, rows = [], []
    for name in TARGETS:
        r, err = backup_one(name, tag_dir)
        if err:
            print("[BACKUP:%s] %s -> %s" % ("SKIP" if err == "absent" else "FAIL", name, err))
            results.append((name, err))
            continue
        if r["mismatch"]:
            print("[BACKUP:FAIL] %-18s files=%d sha256 读回不一致: %s"
                  % (name, r["files"], ", ".join(r["mismatch"][:5])))
            return 1
        print("[BACKUP:OK] %-18s files=%-3d sha256 全部读回一致" % (name, r["files"]))
        results.append((name, "ok"))
    backed = [n for n, s in results if s == "ok"]
    if not backed:
        print("[GATE:r96mirror-unverified] 可备份面为空，禁止把「没什么可备份」读成「已退役」")
        return 2

    mf = os.path.join(tag_dir, "MANIFEST.txt")
    with io.open(mf, "w", encoding="utf-8", newline="") as f:
        for name in backed:
            for rel, p in walk_files(os.path.join(tag_dir, "copy", name)):
                f.write("%s\t%s\t%s\t%d\n" % (name, rel, sha256_file(p), os.path.getsize(p)))
    back = [x for x in io.open(mf, encoding="utf-8").read().splitlines() if x.strip()]
    print("[MANIFEST:OK] %d 行 -> %s" % (len(back), mf))

    if not a.apply:
        print("[DRYRUN] 备份+验证通过；加 --apply 才做 git rm 与限定路径提交。备份=%s" % tag_dir)
        print("  镜像仓现网脏项=%d 条（多属并行会话），提交将严格限定在 %s"
              % (dirty_total, ", ".join(backed)))
        return 0

    rc, out, err = git(["rm", "-r", "--cached", "--"] + backed)
    if rc != 0:
        print("[GITRM:FAIL] rc=%s %s" % (rc, err or out))
        return 1
    for name in backed:
        d = os.path.join(MIRROR, name)
        if os.path.isdir(d):
            shutil.rmtree(d)
        print("[MOVED] %s 已从镜像工作树移出" % name)

    rc, out, err = git(["commit", "-m",
                        "chore(retire): 移出已退役件 %s（权威源 r60_retire_two 已移出；本端镜像副本随退役，"
                        "备份+sha256 读回见 D:/global_memory/_trash/%s）"
                        % (", ".join(backed), tag), "--"] + backed)
    if rc != 0:
        print("[COMMIT:FAIL] rc=%s %s" % (rc, err or out))
        return 1
    rc, out, err = git(["show", "--name-only", "--format=%h %s", "HEAD"])
    print("[COMMIT:OK] 实际落入的文件清单（须只见本次路径）：")
    print(out[:1500])

    for name in backed:
        rc, o2, _e = git(["ls-files", "--", name])
        n = len([x for x in o2.splitlines() if x.strip()])
        print("[VERIFY] git ls-files %s -> %d 条（期望 0）" % (name, n))
        if n != 0:
            print("[GATE:r96mirror-fail] 镜像索引仍留该件")
            return 1
        if os.path.isdir(os.path.join(MIRROR, name)):
            print("[GATE:r96mirror-fail] 镜像工作树仍在")
            return 1
    print("[GATE:r96mirror-pass] 退役已传播到镜像根；备份=%s" % tag_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
