# -*- coding: utf-8 -*-
r"""r103_install.py — 换装成立件的装入器（本轮首次出现非零判定，故新建本件）

判定来源：X-29 三门槛（原文 = memory/AGENTS.md:114）由子代理逐族过筛，
本报告 §换装 记录候选；本件只做**取证式安装**，不做判定。

设计约束（都是本仓踩过的坑）：
  1. 方向敏感：源只读、目标只写，落盘前先断言目标不存在（禁覆盖既有件 —— 覆盖 = 毁他人工作）。
  2. 凭据绑字节：验收按 sha256 与 API 声明 size 双向对账，不采信「写成功」回执。
  3. 危险形态扫描在落盘**之前**：装进去再扫等于把扫描当装饰。
  4. 零输入不判绿：取不到正文、目录为空一律 rc=1。
  5. 行尾锁 LF（newline=''），Windows 下 write_text 会把 \n 译成 \r\n 导致 sha 漂移。

退出码：0=全部装入并读回验证通过；1=任一件失败（已写件在回执里点名，可逐件回滚）；2=前提不满足。
"""
import hashlib
import io
import json
import os
import re
import subprocess
import sys

AUTH = r"D:\global_skills"
REPO = "affaan-m/ECC"
REF = "main"
SLUGS = ("healthcare-cdss-patterns", "healthcare-emr-patterns", "healthcare-eval-harness")
STAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_r103_stage")

# 危险形态：远程代码执行 / 破坏性删除 / 凭据外泄 / 反弹 shell / 提久
DANGER_RX = [
    (r"curl[^\n]*\|\s*(ba)?sh", "pipe-curl-to-shell"),
    (r"wget[^\n]*\|\s*(ba)?sh", "pipe-wget-to-shell"),
    (r"rm\s+-rf?\s+/", "rm-rf-root"),
    (r"(base64|b64decode)[^\n]*(exec|eval|system)", "encoded-payload-exec"),
    (r"\beval\s*\(", "eval-call"),
    (r"(nc|ncat)\s+-e", "reverse-shell"),
    (r"authorized_keys|id_rsa|/etc/passwd", "credential-file"),
    (r"(git|gh)\s+(push\s+--force|filter-branch|clean\s+-[fd])", "git-destructive"),
    (r"Set-MpPreference|Disable-Windows Defender", "av-disable"),
    (r"chmod\s+[0-7]*777", "perm-777"),
]
RE_FM = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def gh_raw(path):
    p = subprocess.run(["gh", "api", "-X", "GET", "repos/%s/contents/%s" % (REPO, path),
                        "-H", "Accept: application/vnd.github.raw", "-f", "ref=" + REF],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0 or not p.stdout.strip():
        return None, "rc=%d %s" % (p.returncode, (p.stderr or "").strip()[:200])
    return p.stdout.encode("utf-8"), ""


def fm_parse(text):
    m = RE_FM.match(text)
    if not m:
        return {"fence": False, "name": False, "description": False}
    block = m.group(1)
    return {"fence": True,
            "name": bool(re.search(r"^name:[ \t]+\S", block, re.M)),
            "description": bool(re.search(r"^description:[ \t]*\S", block, re.M))}


def main():
    apply = "--apply" in sys.argv
    receipt = {"repo": REPO, "ref": REF, "mode": "apply" if apply else "dry-run",
               "items": [], "installed": [], "refused": []}
    if apply and not os.path.isdir(AUTH):
        print("[INSTALL:UNVERIFIED] 权威根不存在 %s" % AUTH)
        return 2
    os.makedirs(STAGE, exist_ok=True)
    for slug in SLUGS:
        raw, err = gh_raw("skills/%s/SKILL.md" % slug)
        if raw is None:
            receipt["refused"].append({"slug": slug, "why": "fetch-failed " + err})
            continue
        text = raw.decode("utf-8")
        hits = [(tag, m.group(0)[:60]) for rx, tag in DANGER_RX
                for m in [re.search(rx, text, re.I)] if m]
        fm = fm_parse(text)
        decl = subprocess.run(["gh", "api", "-X", "GET",
                               "repos/%s/contents/skills/%s/SKILL.md" % (REPO, slug),
                               "-f", "ref=" + REF, "--jq", ".size"],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace").stdout.strip()
        row = {"slug": slug, "bytes": len(raw), "api_declared_size": decl,
               "sha256": sha256_bytes(raw), "frontmatter": fm, "danger_hits": hits,
               "origin": REPO + "/skills/" + slug}
        bad = []
        if not (fm["fence"] and fm["name"] and fm["description"]):
            bad.append("frontmatter 缺 name/description（不可入册不可路由）")
        if hits:
            bad.append("危险形态 %d 处: %s" % (len(hits), hits[0][1]))
        if str(len(raw)) != str(decl):
            bad.append("字节数与 API 声明不符 (%s vs %s)" % (len(raw), decl))
        dst_dir = os.path.join(AUTH, slug)
        dst = os.path.join(dst_dir, "SKILL.md")
        if os.path.exists(dst):
            bad.append("目标已存在，拒绝覆盖: %s" % dst)
        row["blockers"] = bad
        stage_p = os.path.join(STAGE, slug + ".SKILL.md")
        with io.open(stage_p, "wb") as f:
            f.write(raw)
        row["staged"] = stage_p
        row["staged_sha_match"] = sha256_bytes(open(stage_p, "rb").read()) == row["sha256"]
        if bad or not row["staged_sha_match"]:
            receipt["refused"].append({"slug": slug, "why": bad or ["stage-verify-fail"]})
            receipt["items"].append(row)
            continue
        if apply:
            os.makedirs(dst_dir, exist_ok=True)
            with io.open(dst, "wb") as f:
                f.write(raw)
            back = open(dst, "rb").read()
            row["written_sha_match"] = sha256_bytes(back) == row["sha256"]
            if not row["written_sha_match"]:
                receipt["refused"].append({"slug": slug, "why": ["writeback-verify-fail"]})
                receipt["items"].append(row)
                continue
            receipt["installed"].append(slug)
        receipt["items"].append(row)
    print(json.dumps(receipt, ensure_ascii=False, indent=1))
    with io.open(os.path.join(STAGE, "receipt_r103.json"), "w", encoding="utf-8",
                 newline="") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    if receipt["refused"]:
        print("[INSTALL:PARTIAL] installed=%d refused=%d" %
              (len(receipt["installed"]), len(receipt["refused"])))
        return 1
    if apply:
        print("[INSTALL:PASS] %d 件装入 %s 且读回 sha256 全等" % (len(SLUGS), AUTH))
    else:
        print("[INSTALL:DRY-RUN] 3 件全部通过预检，未落盘")
    return 0


if __name__ == "__main__":
    sys.exit(main())
