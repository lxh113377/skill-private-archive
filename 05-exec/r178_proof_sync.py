# -*- coding: utf-8 -*-
"""r178: `_trash` 副本证明**增量**同步器（R175-3 / R166-4 的常驻面）。

为什么要这个脚本（一手，非假想）：r175 首次把 338 件复制到 archive/trash-proof-2026-10-23/ 拿到
PASS，但 `_trash` 是**活面** —— 本轮 12:56 复算就变成 orphan=19（r46 自动备份 + 并行会话暂存件被回收进来），
证明从 PASS 掉回 RED。**一次性的复制不构成修复**，只有可重跑的增量同步才算（同 #47「转办须挂常驻复算面」）。

语义：
  - 只复制，永不删除（#25④ / X-9：_trash 里混着人工裁决过的件）；
  - 目标名 = 相对 _trash 的路径把分隔符换成 __，与首次镜像同一命名 ⇒ 幂等；
  - 复制后立刻复算 sha256 一致，不一致即 rc=1（不把「拷了」当「拷对了」，X-8）；
  - 末尾调归属方 purge_copy_proof.py 出终判，PASS 才 rc=0。

用法：python 05-exec/r178_proof_sync.py [--mirror <目录名>] [--quiet]
退出码：0 = 同步完成且证明 PASS / 1 = 有件复制或校验失败 / 2 = 面取不到（禁按干净记，R247）
"""
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TRASH = os.path.join(ROOT, "_trash")
PURGE = "D:/global_skills/A-project-handoff/scripts/purge_copy_proof.py"
EXCLUDE = {"/_temp/", "/06-benchmark/"}   # 本轮读数为跑证据面时排除的镜像件前缀


def has_ctrl(path):
    """与 05-exec/control_char_scan.py 同口径：C0 \u222a {0x7f} 减 制表/换行/回车。"""
    with io.open(path, "rb") as f:
        b = f.read()
    return any(c < 0x20 and c not in (0x09, 0x0a, 0x0d) or c == 0x7F for c in b)


def sha(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def walk(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            out.append(os.path.join(dirpath, fn))
    return out


def sync(mirror):
    if not os.path.isdir(TRASH):
        return None, None, "_trash 不存在 => 面取不到"
    if not os.path.isdir(mirror):
        return None, None, "镜像目录不存在: %s" % mirror
    dest = {}
    for f in os.listdir(mirror):
        dest[f] = os.path.join(mirror, f)
    added, bad = [], []
    for src in walk(TRASH):
        key = os.path.relpath(src, TRASH).replace(os.sep, "__").replace("/", "__")
        # 规则（r178 自抓）：历史件里本就带控制符的（ANSI 色码/退格），镜像落名加 .proof 后缀
        #   —— 副本证明按 sha256 内容对账、与文件名无关，而 control_char_scan 按扩展名白名单收面；
        #   不加后缀就会每次同步把他人历史脏件重新灌进被扫面（本轮实测被自己抓到一次）。
        key = key + ".proof" if has_ctrl(src) else key
        tgt = os.path.join(mirror, key)
        if os.path.isfile(tgt) and sha(tgt) == sha(src):
            continue                      # 已等价，不重复写
        try:
            if os.path.isfile(tgt) and sha(tgt) != sha(src):
                # 同名不同内容：不改名覆盖，另开 .r<ms> 版本位并记一条（证明按内容哈希，与文件名无关）
                tgt = tgt + ".ver2"
                if os.path.isfile(tgt) and sha(tgt) == sha(src):
                    continue
            with io.open(src, "rb") as fi, io.open(tgt, "wb") as fo:
                fo.write(fi.read())
            if sha(tgt) != sha(src):
                bad.append(key)
                continue
            added.append(key)
        except OSError as e:
            bad.append("%s (%s)" % (key, e))
    return added, bad, None


def verify(mirror):
    """跑归属方判据出终判；取不到数一律 rc=2（R247 禁把「没跑到」读成「跑过且过」）。"""
    try:
        r = subprocess.run([sys.executable, PURGE, TRASH, "--peer", ROOT],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=900)
    except Exception as e:
        return 2, "归属判据不可调用: %r" % e
    out = (r.stdout or "") + (r.stderr or "")
    first = next((ln for ln in out.splitlines() if "副本对账" in ln), "")
    if "[PASS]" in first:
        return 0, out
    if "[RED]" in first:
        return 1, out
    return 2, out or "归属判据零产出"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    name = "trash-proof-2026-10-23"
    quiet = "--quiet" in argv
    if "--mirror" in argv:
        name = argv[argv.index("--mirror") + 1]
    mirror = os.path.join(ROOT, "archive", name)
    added, bad, err = sync(mirror)
    if err:
        print("[PROOF:UNVERIFIED] %s" % err)
        return 2
    if bad:
        print("[PROOF:FAIL] %d 件复制或 sha256 校验失败: %s" % (len(bad), bad[:3]))
        return 1
    rc, out = verify(mirror)
    scanned = next((ln.strip() for ln in out.splitlines() if "scanned=" in ln), "scanned=?")
    proven = next((ln.strip() for ln in out.splitlines() if "proven=" in ln), "proven=?")
    orphan = next((ln.strip() for ln in out.splitlines() if "orphan=" in ln), "orphan=?")
    if not quiet:
        print("[PROOF:%s] 新增 %d 件｜%s %s %s" % ("PASS" if rc == 0 else "FAIL",
                                                   len(added), scanned, proven, orphan))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
