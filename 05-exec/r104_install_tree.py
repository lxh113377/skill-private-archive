# -*- coding: utf-8 -*-
r"""r104_install_tree.py — 多文件 skill 整树装入器（react-best-practices 76 件）。

为什么另起一件而不复用 r103_install.py：那件按「一 slug 一 SKILL.md」写死，整树件是
76 个 blob，单件装法会把 rules/*.md 全漏掉 ⇒ 装进去的是残缺件。

硬约束（每条都对应本仓踩过的一个形态）：
  1. **先全量 stage 再落盘**：夹具/下载中断若在受管根留残件，同步工具会放大它
     （GM lessons「Mutation residue contaminates delivery faces」）。
  2. 凭据绑内容不绑回执：逐件用 GitHub contents API 的 **git blob sha1** 对账
     （本地重算 `sha1("blob N\0"+bytes)`），不是只看「下载没报错」。
  3. 方向敏感：源只读；写前断言目标不存在 ⇒ 绝不覆盖他人在途件。
  4. 危险形态扫描在落盘之前，扫的是**全部**待写文本件（不是抽样）。
  5. 零输入不判绿：tree 取空 / 下载零件 ⇒ rc=2。
  6. 部分写失败即整目录回滚（该目录本次新建、不存在他人工作，删它不伤别人）。
  7. Next/Vercel 绑定件如实登记为名单，**不改上游正文**（改 = 造一个无法同步的 fork）。

退出码：0=全部装入且逐件 blob sha 读回全等；1=任一件失败（已回滚并点名）；2=前置面不可达。
"""
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys

REPO = "vercel-labs/agent-skills"
REF = "main"
PREFIX = "skills/react-best-practices/"
SLUG = "react-best-practices"
AUTH = r"D:\global_skills"
STAGE = os.path.join(os.environ.get("TEMP", "/tmp"), "r104_stage_" + SLUG)

# Next/Vercel 绑定判据（与本轮实测 12/72 同一谓词；口径写在这里供报告引用，不留散文字面）
NEXT_RX = re.compile(
    r"next\.js|next/image|next/dynamic|from ['\"]next|app router|server component|"
    r"vercel|use server|route handler|app/", re.I)

DANGER_RX = [
    (r"curl[^\n]*\|\s*(ba)?sh", "pipe-curl-to-shell"),
    (r"wget[^\n]*\|\s*(ba)?sh", "pipe-wget-to-shell"),
    (r"rm\s+-rf?\s+/", "rm-rf-root"),
    (r"(base64|b64decode)[^\n]*(exec|eval|system)", "encoded-payload-exec"),
    (r"(nc|ncat)\s+-e", "reverse-shell"),
    (r"authorized_keys|id_rsa|/etc/passwd", "credential-file"),
    (r"(git|gh)\s+(push\s+--force|filter-branch|clean\s+-[fd])", "git-destructive"),
    (r"Set-MpPreference|Disable-Windows", "av-disable"),
]


def blob_sha(data):
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()



# r163：gh 解析（与第 64 门 gh_path_face / _lib.gh_cli 同源）。
#   本机 gh 命令名被三方争夺（官方 CLI / npm 第三方包 2.8.9 / 曾经的 0 字节空壳），
#   裸 subprocess.run(["gh", ...]) 在 PATH 序漂移时会静默跑到错实现上 => 取数面按绝对路径调。
def _gh_exe():
    try:
        import _lib
        g = _lib.gh_cli()
        if g:
            return g
    except Exception:
        pass
    import os as _os
    for c in (
        _os.path.join(_os.environ.get("ProgramFiles", r"C:\\Program Files"),
                      "GitHub CLI", "gh.exe"),
        _os.path.expanduser(r"~\\scoop\\shims\\gh.exe"),
    ):
        try:
            if _os.path.isfile(c) and _os.path.getsize(c) > 0:
                return c
        except OSError:
            pass
    return "gh"  # 兜底裸名（调用方若取到非零/异常须具名，不得折算 0）

def gh(*args):
    p = subprocess.run([_gh_exe(), "api"] + list(args), capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout, p.stderr


def main():
    apply = "--apply" in sys.argv
    rc, out, err = gh("-X", "GET", "repos/%s/git/trees/%s" % (REPO, REF),
                      "-f", "recursive=1")
    if rc != 0:
        print("[TREE:UNVERIFIED] tree 取不到 rc=%d %s" % (rc, err[:160]))
        return 2
    tree = json.loads(out).get("tree") or []
    if json.loads(out).get("truncated"):
        print("[TREE:UNVERIFIED] tree 被截断，分母不全，停手")
        return 2
    blobs = [t for t in tree
             if t.get("type") == "blob" and t["path"].startswith(PREFIX)]
    if not blobs:
        print("[TREE:UNVERIFIED] %s 下取到 0 个 blob（零输入不判绿）" % PREFIX)
        return 2

    dst_root = os.path.join(AUTH, SLUG)
    if os.path.exists(dst_root):
        print("[TREE:FAIL] 目标已存在，拒绝覆盖: %s" % dst_root)
        return 1

    shutil.rmtree(STAGE, ignore_errors=True)
    os.makedirs(STAGE)
    items, next_bound, danger = [], [], []
    for t in blobs:
        rel = t["path"][len(PREFIX):]
        rc2, body, err2 = gh("-X", "GET", "repos/%s/contents/%s" % (REPO, t["path"]),
                             "-f", "ref=" + REF)
        if rc2 != 0:
            print("[TREE:FAIL] 取 meta 失败 %s rc=%d %s" % (rel, rc2, err2[:120]))
            return 1
        meta = json.loads(body)
        rc3, raw, err3 = gh("-X", "GET", "repos/%s/contents/%s" % (REPO, t["path"]),
                            "-H", "Accept: application/vnd.github.raw")
        if rc3 != 0:
            print("[TREE:FAIL] 取正文失败 %s rc=%d %s" % (rel, rc3, err3[:120]))
            return 1
        data = raw.encode("utf-8")
        local_blob = blob_sha(data)
        stage_p = os.path.join(STAGE, rel.replace("/", "__"))
        with io.open(stage_p, "wb") as f:
            f.write(data)
        row = {"rel": rel, "bytes": len(data), "api_size": meta.get("size"),
               "api_blob_sha": meta.get("sha"), "local_blob_sha": local_blob,
               "match": meta.get("sha") == local_blob}
        items.append(row)
        if not row["match"]:
            print("[TREE:FAIL] blob sha 不等 %s api=%s local=%s"
                  % (rel, meta.get("sha"), local_blob))
            return 1
        hits = [tag for rx, tag in DANGER_RX if re.search(rx, data.decode("utf-8", "replace"), re.I)]
        if hits:
            danger.append({"rel": rel, "hits": hits})
        if rel.startswith("rules/") and rel.endswith(".md") and NEXT_RX.search(
                data.decode("utf-8", "replace")):
            next_bound.append(rel)

    if danger:
        print("[TREE:FAIL] 危险形态命中，不落盘: %s" % json.dumps(danger, ensure_ascii=False)[:300])
        return 1

    written = []
    if apply:
        try:
            for it in items:
                dst = os.path.join(dst_root, *it["rel"].split("/"))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                src = os.path.join(STAGE, it["rel"].replace("/", "__"))
                with io.open(src, "rb") as fin:
                    payload = fin.read()
                with io.open(dst, "wb") as fout:
                    fout.write(payload)
                written.append(dst)
                if blob_sha(open(dst, "rb").read()) != it["local_blob_sha"]:
                    raise IOError("读回 blob sha 不等: %s" % dst)
        except Exception as exc:
            print("[TREE:ROLLBACK] %s —— 删除本次新建目录（该目录本轮前不存在）" % exc)
            shutil.rmtree(dst_root, ignore_errors=True)
            print("[TREE:ROLLBACK-DONE] exists=%s" % os.path.exists(dst_root))
            return 1

    receipt = {"repo": REPO, "ref": REF, "prefix": PREFIX, "slug": SLUG,
               "mode": "apply" if apply else "dry-run",
               "files_n": len(items), "bytes_total": sum(i["bytes"] for i in items),
               "blob_sha_all_match": all(i["match"] for i in items),
               "danger_hits": danger, "next_bound_rules": sorted(next_bound),
               "next_bound_n": len(next_bound),
               "generic_rules_n": len([i for i in items if i["rel"].startswith("rules/")
                                       and i["rel"].endswith(".md")]) - len(next_bound),
               "installed_at": dst_root if apply else None}
    out_p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "06-benchmark", "install_receipt_r104.json")
    with io.open(os.path.abspath(out_p), "w", encoding="utf-8", newline="") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in receipt.items() if k != "next_bound_rules"},
                     ensure_ascii=False))
    print("[TREE:%s] %d 件 / %d B；Next 绑定规则 %d 条已具名登记、正文未改"
          % ("PASS" if apply else "DRY-RUN", receipt["files_n"],
             receipt["bytes_total"], receipt["next_bound_n"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
