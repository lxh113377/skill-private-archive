# -*- coding: utf-8 -*-
"""r299 采集器第 2 批：把 6 个「侧车声明了我却没采」的仓补齐并合并进 tree_paths.json。

为什么分批是我自己的错：第 1 批的输入是 declared_repos.txt，而那清单来自矩阵行的
declared_upstream_repo —— 每行只有**第一个**仓（r114 的 parse_sidecar 就这么设计）。所以
web-access 声明的 4 个仓里我只采了 1 个，其余 3 个被判 unmeasured。第 2 批改从盘上侧车
现读全部 owner/repo 行（allrepos.py），31 仓里补采 6 个 ⇒ 覆盖完整。
判据本体不动（仍离线读 tree_paths.json），只是喂给它的数据补全了。
"""
import importlib.util
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SP = os.path.join(ROOT, "05-exec", "r114_replacement_scan.py")
_s = importlib.util.spec_from_file_location("r114", SP)
r114 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(r114)
GH = os.environ.get("GH_BIN") or r"C:/Program Files/GitHub CLI/gh.exe"
JQ = ("{truncated:.truncated,paths:[.tree[]|select(.path|endswith(\"SKILL.md\"))"
      "|{path:.path,sha:.sha}]}")


def gh(args, timeout=200):
    try:
        r = subprocess.run([GH] + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except Exception as exc:
        return False, "", "EXC:" + repr(exc)[:120]
    err = (r.stderr or "").strip().replace("\n", " ")[:180]
    if r.returncode != 0:
        return False, (r.stdout or "").strip(), err or ("rc=%d" % r.returncode)
    return True, (r.stdout or "").strip(), err


import subprocess        # 放在函数后是刻意的：上面 gh() 只用它，不依赖导入顺序
def main():
    tp = os.path.join(HERE, "tree_paths.json")
    COL = json.load(io.open(tp, encoding="utf-8"))
    need = [x.strip() for x in io.open(os.path.join(HERE, "need_more.txt"), encoding="utf-8")
            if x.strip()]
    print("to collect =", len(need), need)
    added = 0
    for repo in need:
        ok, br, e1 = gh(["api", "repos/" + repo, "--jq", ".default_branch"], timeout=120)
        if not ok or not br:
            COL[repo] = {"state": "REPO_UNAVAILABLE", "error": e1 or "empty"}
            print("  MISS %-34s %s" % (repo, (e1 or "")[:70]))
            continue
        time.sleep(0.3)
        ok2, raw, e2 = gh(["api", "repos/%s/git/trees/%s?recursive=1" % (repo, br), "--jq", JQ])
        if not ok2 or not raw:
            COL[repo] = {"state": "TREE_FAILED", "branch": br, "error": e2 or "empty"}
            print("  MISS tree %-30s %s" % (repo, (e2 or "")[:70]))
            continue
        doc = json.loads(raw)
        paths = doc.get("paths") or []
        COL[repo] = {"state": "OK", "branch": br, "truncated": bool(doc.get("truncated")),
                     "skill_md_paths": paths, "skill_md_n": len(paths)}
        added += 1
        print("  ok  %-34s SKILL.md=%-5d truncated=%s" % (repo, len(paths), doc.get("truncated")))
        time.sleep(0.3)
    io.open(tp, "w", encoding="utf-8").write(json.dumps(COL, ensure_ascii=False, indent=1))
    ok_n = sum(1 for v in COL.values() if v.get("state") == "OK")
    print("[COLLECT2] added_ok=%d/%d total_repos=%d state_ok=%d" % (added, len(need), len(COL), ok_n))
    return 0 if added == len(need) else 1


if __name__ == "__main__":
    sys.exit(main())
