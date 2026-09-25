# -*- coding: utf-8 -*-
"""r56 取值面生成器：对手 CI 的「声明面 vs 自有文件面」双路对账 + 校验步计数。

存在理由（两条，都是本轮自己踩出来的）：
  ① W-46：任何进 06-benchmark 的证据件都必须有**仓内可复跑的生成器**，否则它是解不出的死句柄；
     本件最初就是 /tmp 里的一次性脚本，故收编为正式脚本。
  ② r50 老坑复现：`/actions/workflows.total_count` 含平台侧条目，与仓库自有文件数不等
     （r56 实测 superpowers / anthropics 的 api 总计面各报 2，而 `.github/workflows/` 下
     自有 yaml 数 = **0**，contents 目录直接 404）。⇒ 只取任一面的数字都不可写进报告。
本脚本因此**同时取两面**，并输出差值；差值不为 0 不算错，但必须显式记在件里。
"""
import datetime
import json
import os
import re
import subprocess
import sys

REPOS = [("github/spec-kit", 287, 134), ("obra/superpowers", 401, 143),
         ("anthropics/skills", 1290, 368), ("addyosmani/agent-skills", 118, 58),
         ("pre-commit/pre-commit", 25, 17)]     # (repo, 含PR面, 纯issue面) 供检索留痕，不参与本件计算
WF_DIR = ".github/workflows/"
YAML = re.compile(r"\.ya?ml$")
VALIDATE = re.compile(r"pre-commit run|--check\b|validate|schema|\blint\b", re.I)


def gh(args):
    p = subprocess.run(["gh"] + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, p.stdout, p.stderr


def main():
    out_json = None
    if len(sys.argv) > 2 and sys.argv[1] == "--json":
        out_json = sys.argv[2]
    rows = []
    for repo, _i1, _i2 in REPOS:
        rc, out, err = gh(["api", "repos/%s/git/trees/HEAD?recursive=1" % repo])
        if rc != 0:
            rows.append({"repo": repo, "error": (err or "").strip()[:120]})
            print("  %-28s 取不到 tree：%s" % (repo, (err or "").strip()[:60]))
            continue
        tree = json.loads(out)
        own = sorted(p["path"] for p in tree.get("tree", [])
                     if p.get("path", "").startswith(WF_DIR) and YAML.search(p["path"]))
        hits, unread = [], []
        for f in own:
            rc2, body, _ = gh(["api", "-H", "Accept: application/vnd.github.raw+json",
                              "repos/%s/contents/%s" % (repo, f)])
            if rc2 != 0 or not body:
                unread.append(f)
                continue
            if VALIDATE.search(body):
                hits.append(os.path.basename(f))
        rc3, out3, _ = gh(["api", "repos/%s/actions/workflows" % repo])
        api_face = json.loads(out3).get("total_count") if rc3 == 0 else None
        rows.append({"repo": repo, "tree_truncated": bool(tree.get("truncated")),
                     "own_workflow_files": len(own), "read_ok": len(own) - len(unread),
                     "unreadable": unread, "api_total_face": api_face,
                     "face_delta": (None if api_face is None else api_face - len(own)),
                     "with_validation_step": len(hits), "validation_names": hits})
        print("  %-28s 自有=%-3d 实读=%-3d api总计面=%-4s 差=%-4s 含校验步=%d %s"
              % (repo, len(own), len(own) - len(unread), api_face,
                 None if api_face is None else api_face - len(own), len(hits),
                 "⚠️ tree 被截断" if tree.get("truncated") else ""))
    if any(r.get("tree_truncated") for r in rows):
        print("[WFFACE:UNVERIFIED] 有仓库的递归 tree 被截断 ⇒ 该仓自有文件数不完整，不得当分母（R247）")
    doc = {"schema": "wf-validation-face-v1",
           "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "readonly": True,
           "method": "git/trees/HEAD?recursive=1 取自有 .github/workflows/*.y(a)ml 为分母；"
                     "逐个 contents raw 正文匹配校验 token；同时取 /actions/workflows.total_count 作对照面",
           "validate_tokens": ["pre-commit run", "--check", "validate", "schema", "lint"],
           "face_caveat": "api 总计面含平台侧/历史条目，与自有文件面不等是常态（r56 实测两家差 2）；"
                          "任何一侧单独引用都不算已核验",
           "repos": rows}
    print("合计：自有 workflow 文件 %d 个 ｜ 含校验步 %d 个 ｜ 不可读 %d 个"
          % (sum(r.get("own_workflow_files", 0) for r in rows),
             sum(r.get("with_validation_step", 0) for r in rows),
             sum(len(r.get("unreadable") or []) for r in rows)))
    if out_json:
        with open(out_json, "w", encoding="utf-8", newline="") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print("JSON -> %s" % out_json)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
