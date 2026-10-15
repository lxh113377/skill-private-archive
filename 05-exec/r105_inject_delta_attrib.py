# -*- coding: utf-8 -*-
r"""r105_inject_delta_attrib.py — inject_union_bytes +743 的**逐字节**归因（磁盘口径）。

为什么量得到而 r103 量不到：棘轮这个指标取的是 `os.path.getsize` **磁盘字节**，
而受管根 `core.autocrlf=true` 且无 `.gitattributes` ⇒ blob 存 LF、检出是 CRLF。
r103 用 `cat-file -s`（blob 字节）做归因，两笔相加 697+450=1,147 ≠ 棘轮实增 743，
于是「delta 与指标实增逐字节相等」（R59-8）这条硬前提当时**确实**不成立。
本件把 blob 换算成检出字节再做差：`disk_len(blob) = len(blob) + blob.count(b"\\n")`
（autocrlf 只把行尾 LF 换成 CRLF，每行 +1 字节），并在动手前**先用现网一件自证该式成立**
（对 HEAD 的 blob 换算出的磁盘字节必须与盘上 `getsize` 逐字节相等；不等即判该式不适用并退出）。

退出码：0=每一枚可归因路径的实增之和 == 棘轮实增（可进归因抬账）；
1=对不上（差值非零 ⇒ 不得抬基线，如实登记）；2=前置面不可达 / 自证失败。
"""
import io
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASELINE_COMMIT = "84db1c07"          # r102 归因抬基线落账的那次提交（87604→87610）
BASELINE_FILE = ROOT / "06-benchmark" / "inject_ratchet_baseline.json"
OUT = ROOT / "06-benchmark" / "inject_delta_attrib_r105_2026-10-04.json"


def sh(args, cwd=None):
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=cwd, timeout=120)
    return p.returncode, p.stdout, p.stderr


def disk_len_from_blob(blob_bytes):
    """检出字节 == blob 字节（r105 实测否证了「autocrlf 一律 +1 字节/行」这条假设）。

    一手：首版写 `len(blob) + blob.count(b"\\n")`，自证腿当场判红 3 件 —— GS 的
    `A-memory-start/SKILL.md` est=25289 而盘上 25115（多算的 174 == 该件行数），
    `contract.md` 多算 202、GM 的 `behavior_core.md` 多算 183，同形 ⇒ 那些 blob 里
    本来就存 CRLF，检出不转换。改成恒等后自证又在**本仓** `AGENTS.md` 判红
    （est=28985 vs 盘上 29293，差 308 == 行数）⇒ 该仓 blob 存 LF、检出转 CRLF。
    结论：**换算式不是全仓常数，是逐路径性质**，故本函数不再"选一个口径"，
    而由 `derive_eol_identity()` 从现网观测反推，推不出即拒绝归因。
    """
    return len(blob_bytes)


def derive_eol_identity(blob_bytes, disk_bytes):
    """由「HEAD blob 与盘上字节」这一对观测，反推该路径的检出换算；两种候选都不等 ⇒ 返回 None。

    候选只两个，且都必须**逐字节相等**才算命中（不做「差不多」的近似）：
      raw     —— blob 已含 CRLF 或该路径不转换 ⇒ 长度直接可比
      lf2crlf —— blob 存 LF，检出补 CR ⇒ 长度 = len(blob) + blob.count(b"\\n")
    命中哪一个，就只对**基线 blob** 施加同一个换算 ⇒ 增量口径与现网同源，不是我拍的。
    """
    if len(blob_bytes) == disk_bytes:
        return "raw"
    if len(blob_bytes) + blob_bytes.count(b"\n") == disk_bytes:
        return "lf2crlf"
    return None


def apply_identity(blob_bytes, identity):
    if identity == "raw":
        return len(blob_bytes)
    if identity == "lf2crlf":
        return len(blob_bytes) + blob_bytes.count(b"\n")
    return None


def main():
    sys.path.insert(0, str(HERE))
    import importlib.util
    spec = importlib.util.spec_from_file_location("rgat", str(HERE / "ratchet_gate.py"))
    rg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rg)

    paths = rg.inject_union_paths()
    if not paths:
        print("[ATTRIB:UNVERIFIED] 注入面路径取不到 ⇒ 不归因")
        return 2
    base = json.load(io.open(str(BASELINE_FILE), encoding="utf-8-sig"))
    floor = (base.get("metrics") or {}).get("inject_union_bytes")
    if not isinstance(floor, int):
        print("[ATTRIB:UNVERIFIED] 基线 metrics.inject_union_bytes 取不到（现值=%r）" % (floor,))
        return 2

    rows, selfcheck_fail, unattrib = [], [], []
    total_now = 0
    # 基线时刻：每个路径用它**自己那个仓**在基线时点的提交，不能拿一个仓的 SHA 去问另一个仓
    # （r105 一手：首版把 GS 的 `84db1c07` 同时用于 GM 的 behavior_core.md，判成「基线无此 blob」，
    #  于是 1,147 vs 应增 743 的差被误记成「有面无法归因」——实际是取数面认错仓库。）
    BASE_AT = (base.get("generated_at") or "")[:19]
    if not BASE_AT:
        print("[ATTRIB:UNVERIFIED] 基线 generated_at 取不到 ⇒ 无法按仓库定位基线提交")
        return 2
    repo_cache = {}

    def baseline_ref(repo):
        if repo not in repo_cache:
            rc, out, _ = sh(["git", "-C", repo, "rev-list", "-1", "--before=%s" % BASE_AT, "HEAD"])
            repo_cache[repo] = (out or "").strip() if rc == 0 and out.strip() else None
        return repo_cache[repo]

    REPOS = (r"D:\global_skills", r"D:\global_memory", str(ROOT))
    for p in paths:
        p = str(p)
        try:
            now = os.path.getsize(p)
        except OSError:
            unattrib.append({"path": p, "why": "盘上取不到（junction 断/件被移走）"})
            continue
        total_now += now
        repo = None
        for cand in REPOS:
            try:
                if os.path.commonpath([os.path.realpath(p), os.path.realpath(cand)]) == os.path.realpath(cand):
                    repo = cand
                    break
            except ValueError:
                continue
        if repo is None:
            unattrib.append({"path": p, "bytes": now, "why": "不在三个有历史的根内（仓外件，git 无旧值可比）"})
            continue
        bref = baseline_ref(repo)
        if not bref:
            unattrib.append({"path": p, "bytes": now, "why": "该仓在基线时刻 %s 前无提交" % BASE_AT})
            continue
        rel = os.path.relpath(os.path.realpath(p), os.path.realpath(repo)).replace("\\", "/")
        rc, _, _ = sh(["git", "-C", repo, "cat-file", "-e", "HEAD:%s" % rel])
        if rc != 0:
            unattrib.append({"path": p, "why": "HEAD 无此 blob（件是新增/被移走）rel=%s repo=%s" % (rel, repo)})
            continue
        p_blob = subprocess.run(["git", "-C", repo, "cat-file", "blob", "HEAD:%s" % rel],
                                capture_output=True, timeout=120)
        head_disk_est = disk_len_from_blob(p_blob.stdout)
        identity = derive_eol_identity(p_blob.stdout, now)
        if identity is None:
            selfcheck_fail.append({"path": p, "est_raw": head_disk_est,
                                   "est_lf2crlf": head_disk_est + p_blob.stdout.count(b"\n"),
                                   "disk": now,
                                   "why": "两种换算口径都不逐字节相等 ⇒ 该路径不可归因（不猜）"})
            continue
        rc2, _, _ = sh(["git", "-C", repo, "cat-file", "-e", "%s:%s" % (bref, rel)])
        if rc2 != 0:
            unattrib.append({"path": p, "why": "基线提交 %s 无此 blob（该时点后新增件）repo=%s" % (bref, repo)})
            rows.append({"path": p, "head_disk": now, "baseline_disk": None, "delta": None,
                         "note": "基线无件 ⇒ 该件全量是新增，增量口径另行说明"})
            continue
        p_old = subprocess.run(["git", "-C", repo, "cat-file", "blob", "%s:%s" % (bref, rel)],
                               capture_output=True, timeout=120)
        old_disk = apply_identity(p_old.stdout, identity)
        rows.append({"path": p, "head_disk": now, "baseline_disk": old_disk,
                     "delta": now - old_disk, "repo": repo,
                     "baseline_commit": bref, "eol_identity": identity})

    attrib_sum = sum(r["delta"] for r in rows if isinstance(r.get("delta"), int))
    # 基线本身是「上一轮实测值」，与 HEAD 换算之和可能差在 unattrib 面上 ⇒ 报告两路都要印
    known_sum = sum(r["head_disk"] for r in rows)
    doc = {"schema": "inject-delta-attrib-r105-v2", "baseline_moment": BASE_AT,
           "baseline_commits_by_repo": dict(repo_cache),
           "floor": floor, "paths_n": len(paths), "attributable_n": len(rows),
           "unattributable": unattrib, "selfcheck_fail": selfcheck_fail,
           "rows": [r for r in rows if isinstance(r.get("delta"), int)],
           "attributable_delta_sum": attrib_sum,
           "current_total": total_now, "current_total_over_known_paths": known_sum,
           "ratchet_measured_now": rg.inject_union_bytes()}
    io.open(str(OUT), "w", encoding="utf-8", newline="").write(
        json.dumps(doc, ensure_ascii=False, indent=1))

    print("自证（HEAD blob 换算检出字节 == 盘上 getsize）：失败 %d 件" % len(selfcheck_fail))
    for s in selfcheck_fail[:5]:
        print("   %s est=%s disk=%s" % (s["path"], s["est"], s["disk"]))
    if selfcheck_fail:
        print("[ATTRIB:UNVERIFIED] LF→CRLF 换算式在本机不成立 ⇒ 不得用它做归因（改机制，不凑数）")
        print("JSON -> %s" % OUT)
        return 2
    print("可归因增量之和=%s ｜ 基线 floor=%s ｜ 棘轮现值=%s ｜ 应增=%s"
          % (attrib_sum, floor, doc["ratchet_measured_now"],
             (doc["ratchet_measured_now"] - floor) if doc["ratchet_measured_now"] else None))
    for r in doc["rows"]:
        print("   %+6d  %s" % (r["delta"], r["path"]))
    for u in unattrib:
        print("   不归因: %s （%s）" % (u["path"], u["why"]))
    target = (doc["ratchet_measured_now"] or 0) - floor
    if attrib_sum == target:
        print("[ATTRIB:EXACT] 逐字节相等 ⇒ 满足 R59-8 抬账前提（抬与不抬仍由人决定，本件只回答「能不能」）")
        print("JSON -> %s" % OUT)
        return 0
    print("[ATTRIB:MISMATCH] 差 %d ⇒ 不满足逐字节相等，禁抬基线；如实登记" % (target - attrib_sum))
    print("JSON -> %s" % OUT)
    return 1


if __name__ == "__main__":
    sys.exit(main())
