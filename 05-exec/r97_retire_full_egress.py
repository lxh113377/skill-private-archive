# -*- coding: utf-8 -*-
"""r97_retire_full_egress.py — 退役件全出口清理（铁律：判据要覆盖产物的全部写出出口）。

背景（r97 一手实测）：r60 退役 executing-plans/slides（权威源）→ r96 传播到镜像根
`C:/Users/37533/.agents/skills`（--apply 已完成，镜像已无）→ 2026-10-01 15:24 两件**又回到
权威源**（git ?? 未跟踪、mtime 15:24）。生产者定位 = 市场缓存根 `C:/Users/37533/.workbuddy/skills`
两件仍在（r59 已有先例「原件保留（删了会自动恢复）」）⇒ 只清权威源/镜像 = 退役永远做不完。

本件动作：①备份（cp 全量 + sha256 清单读回验证）②移出权威源 D:/global_skills 两目录
③移出市场缓存根 C:/Users/37533/.workbuddy/skills 两目录（恢复源）④复跑 retired_face。
退出码：0=成功；1=备份/验证失败（不动盘）；2=UNVERIFIED（零面/目标缺失）。
已知边界：平台升级可能重新下发两件 → 若回流，登记为已知边界并升级判据（marketplace 源入 retired_face 输出面）。
"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

AUTH = r"D:\global_skills"
MARKET = r"C:\Users\37533\.workbuddy\skills"
BACKUP_ROOT = r"D:\global_memory\_trash"
TARGETS = ("executing-plans", "slides")
TAG = "r97_retire_full_egress_" + datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = os.path.join(BACKUP_ROOT, TAG)


def sha256_file(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(root):
    """备份 root 下 TARGETS 各目录，返回 {skill: {relpath: sha256}}。"""
    out = {}
    for t in TARGETS:
        src = os.path.join(root, t)
        if not os.path.isdir(src):
            out[t] = None
            continue
        dst = os.path.join(BACKUP_DIR, os.path.basename(root.rstrip("\\/")), t)
        shutil.copytree(src, dst)
        manifest = {}
        for dp, _dn, fns in os.walk(dst):
            for fn in fns:
                p = os.path.join(dp, fn)
                manifest[os.path.relpath(p, dst)] = sha256_file(p)
        out[t] = manifest
    return out


def verify_backup(root, snap):
    """读回验证：备份里逐文件 sha256 与原目录现值比对（必须在删除前做）。"""
    bad = []
    for t, manifest in snap.items():
        if manifest is None:
            continue
        src = os.path.join(root, t)
        for rel, sha in manifest.items():
            p = os.path.join(src, rel)
            if not os.path.isfile(p) or sha256_file(p) != sha:
                bad.append("%s/%s" % (t, rel))
    return bad


def main():
    apply = "--apply" in sys.argv
    faces = {}
    for root in (AUTH, MARKET):
        faces[root] = {t: os.path.isdir(os.path.join(root, t)) for t in TARGETS}
    on_disk = sum(1 for root in faces.values() for present in root.values() if present)
    print("面盘点: " + json.dumps({os.path.basename(k.rstrip('\\/')): v for k, v in faces.items()}, ensure_ascii=False))
    if on_disk == 0:
        print("[RETIRE:UNVERIFIED] 两根均无目标 —— 零面不判完成（R247）")
        return 2
    if not apply:
        print("[RETIRE:DRY-RUN] 待清理 %d 处；备份将落 %s" % (on_disk, BACKUP_DIR))
        return 0
    os.makedirs(BACKUP_DIR, exist_ok=True)
    snaps = {}
    for root, present in faces.items():
        if not any(present.values()):
            continue
        snaps[root] = snapshot(root)
        bad = verify_backup(root, snaps[root])
        if bad:
            print("[RETIRE:FAIL] 备份读回不一致: %s（不动盘）" % bad[:5])
            return 1
        n = sum(len(m) for m in snaps[root].values() if m)
        print("[RETIRE:BACKUP-OK] %s -> %s（%d 文件 sha256 读回全等）" % (root, BACKUP_DIR, n))
    for root in snaps:
        for t in TARGETS:
            p = os.path.join(root, t)
            if os.path.isdir(p):
                shutil.rmtree(p)
                print("[RETIRE:REMOVED] %s" % p)
    # 终态读回
    left = [os.path.join(r, t) for r in snaps for t in TARGETS if os.path.isdir(os.path.join(r, t))]
    with io.open(os.path.join(BACKUP_DIR, "MANIFEST.txt"), "w", encoding="utf-8", newline="") as f:
        f.write("tag=%s\ntargets=%s\nleft_on_disk=%s\n回滚: 把 %s 下对应目录 cp 回原位\n"
                % (TAG, ",".join(TARGETS), left, BACKUP_DIR))
    if left:
        print("[RETIRE:FAIL] 删除后仍在盘: %s" % left)
        return 1
    print("[RETIRE:PASS] 全出口清零（权威源+市场缓存）；回滚锚=%s" % BACKUP_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
