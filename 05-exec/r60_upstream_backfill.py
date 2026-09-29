# -*- coding: utf-8 -*-
r"""r60_upstream_backfill.py — 把上游 anthropics/skills 的 OOXML 校验层补进本地 docx / xlsx.

R59-5 登记（r59 对标 D1 实测缺口）：本地 docx/xlsx 是上游的**超集**（本地独占 doctor.py /
fill_template.py / md_to_docx* / styles/ 等），但**校验面为空** —— 上游 ships
`scripts/office/{soffice,validate}.py` + `scripts/office/validators/{__init__,base,docx,pptx,
redlining}.py`（另有 `office/helpers/pptx_*.py` 与 `scripts/templates/*.xml`），本地一件没有。

纪律：
  * **只增不删**：目标路径已存在即 skip（要么内容相同，要么本地是更新代；本件不覆盖、不裁决）。
  * 改动前先算出「将新增 / 将跳过」两张清单并按目录打印（先看清单再落盘）。
  * 上游全名一律 `gh api` 实测（本页铁律：禁从表头抄名字）。
  * 落盘用 raw media type 逐件取，写 `.part` 再 os.replace（原子替换，禁半成品上盘）。
  * 落盘后逐件：`ast.parse` 语法自证（.py）+ sha256 回读断言。

取值：
    python 05-exec/r60_upstream_backfill.py                 # 预演（默认）
    python 05-exec/r60_upstream_backfill.py --apply         # 落盘
退出码：0 = 有面可比且（预演或落盘后自证）全过；1 = 自证失败；2 = UNVERIFIED（取不到上游 / 空面）。
"""

import argparse
import ast
import hashlib
import io
import json
import os
import subprocess
import sys

AUTHORITY = r"D:\global_skills"
REPO = "anthropics/skills"
SKILLS = ("docx", "xlsx")
ALLOW_TARGET_SUFFIXES = (".py", ".xml", ".md", ".mjs", ".txt")


def gh(*args):
    proc = subprocess.run(["gh", "api"] + list(args), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError("gh api %s rc=%s err=%s" % (list(args), proc.returncode,
                                                       (proc.stderr or "").strip()[:200]))
    return proc.stdout


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    full = gh("repos/" + REPO, "--jq", ".full_name").strip()
    if full != REPO:
        sys.stderr.write("[BACKFILL:UNVERIFIED] repo 全名对不上：gh api 回 %r != %r\n" % (full, REPO))
        return 2

    tree = json.loads(gh("repos/%s/git/trees/HEAD" % REPO, "-X", "GET", "-f", "recursive=1"))
    blobs = [n["path"] for n in tree.get("tree") or []
             if n.get("type") == "blob" and (n["path"].startswith("skills/docx/")
                                             or n["path"].startswith("skills/xlsx/"))]
    if not blobs:
        sys.stderr.write("[BACKFILL:UNVERIFIED] 上游面为空，零面不得读成「已补齐」（R247）\n")
        return 2
    if tree.get("truncated"):
        sys.stderr.write("[BACKFILL:UNVERIFIED] 上游树被截断，不做差异结论\n")
        return 2

    to_add, to_skip, refused = [], [], []
    for path in blobs:
        rel = path[len("skills/"):]                      # docx/scripts/...  xlsx/scripts/...
        local = os.path.join(AUTHORITY, rel.replace("/", os.sep))
        if os.path.splitext(local)[1].lower() not in ALLOW_TARGET_SUFFIXES:
            refused.append(rel)
            continue
        (to_skip if os.path.exists(local) else to_add).append(rel)

    print("上游 %s ｜ blob %d ｜ 将新增 %d ｜ 已存在跳过 %d ｜ 后缀不收 %d"
          % (REPO, len(blobs), len(to_add), len(to_skip), len(refused)))
    for rel in to_add:
        print("   + %s" % rel)
    if not to_add:
        print("[BACKFILL:PASS] 无新增面（本地已是超集）")
        return 0
    if not args.apply:
        print("[BACKFILL:DRYRUN] 加 --apply 落盘")
        return 0

    added, evidence = [], []
    for rel in to_add:
        raw = gh("repos/%s/contents/skills/%s" % (REPO, rel), "-H",
                 "Accept: application/vnd.github.raw")
        data = raw.encode("utf-8")
        dst = os.path.join(AUTHORITY, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        tmp = dst + ".part"
        with io.open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, dst)
        back = io.open(dst, "rb").read()
        if sha256_bytes(back) != sha256_bytes(data):
            sys.stderr.write("[BACKFILL:FAIL] sha 回读不一致 %s\n" % rel)
            return 1
        if dst.endswith(".py"):
            try:
                ast.parse(back.decode("utf-8"))
            except SyntaxError as e:
                sys.stderr.write("[BACKFILL:FAIL] 语法自证失败 %s: %s\n" % (rel, e))
                return 1
        added.append(rel)
        evidence.append({"path": rel, "bytes": len(back), "sha256": sha256_bytes(back)})
        print("[ADD:OK] %-58s %6d B" % (rel, len(back)))

    print("[BACKFILL:OK] 新增 %d 件，逐件 sha256 回读 + ast 自证全过" % len(added))
    ev = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "06-benchmark", "upstream_backfill_r60_2026-09-30.json")
    with io.open(ev, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"schema": "upstream-backfill-r60-v1", "readonly": True,
                            "repo": REPO, "added": evidence,
                            "skipped_existing": to_skip, "refused_suffix": refused,
                            "retrieval": 'gh api "repos/%s/git/trees/HEAD?recursive=1" ; '
                                         'gh api "repos/%s/contents/skills/<rel>" -H '
                                         '"Accept: application/vnd.github.raw"' % (REPO, REPO)},
                           ensure_ascii=False, indent=1))
    print("证据件: %s" % ev)
    return 0


if __name__ == "__main__":
    sys.exit(main())
