# -*- coding: utf-8 -*-
"""r299 采集器（联网一次，落盘后判据本体可离线复算）。

为什么需要它（一手，r299）：实测 r114 的仓缓存**只存计数**（skill_md_n=10 这类），没有树路径
=> 我第一版判据把「路径看不见」当成「路径不存在」，给 33 行判了 invalid —— 那正是本仓反复
登记的「把取不到写成结论」（R247）。所以要么真取树、要么显式记 unmeasured，二者不能混。

为什么用 Python 不用 bash（也是一手）：前两次 bash 版采集器全军覆没，一次是清单 CRLF 让
gh 拿到带回车的 URL，一次是 heredoc 残骸拉起交互式解释器；同一轮里我已第 110 次栽在引号/
展开家族上。把取数写成 Python subprocess 调用，参数走 argv 列表 = 不经过 shell，从结构上
消灭这一类错（本仓 AGENTS 的 windows-cli-utf8-wrapper 也是同一结论）。

输出 tree_paths.json：{repo: {"state": ..., "branch": ..., "truncated": ...,
"skill_md_paths": [{"path":..., "sha":...}]}}。取数失败**照实记状态并留 stderr 摘要**，
不补空表、不记 0。
"""
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GH = os.environ.get("GH_BIN") or r"C:/Program Files/GitHub CLI/gh.exe"
JQ_TREE = "{truncated:.truncated,paths:[.tree[]|select(.path|endswith(\"SKILL.md\"))|{path:.path,sha:.sha}]}"


def gh(args, timeout=150):
    """直连 gh.exe（无 shell），返回 (ok, stdout, err摘要)。"""
    try:
        r = subprocess.run([GH] + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except Exception as exc:
        return False, "", "EXC:" + repr(exc)[:120]
    err = (r.stderr or "").strip().replace("\n", " ")[:200]
    if r.returncode != 0:
        return False, (r.stdout or "").strip(), err or ("rc=%d" % r.returncode)
    return True, (r.stdout or "").strip(), err


def main():
    lst = io.open(os.path.join(HERE, "declared_repos.txt"), encoding="utf-8").read()
    repos = sorted({x.strip() for x in lst.splitlines() if x.strip()})
    print("repos to collect =", len(repos))
    out = {}
    for repo in repos:
        ok, br, e1 = gh(["api", "repos/" + repo, "--jq", ".default_branch"])
        if not ok or not br:
            out[repo] = {"state": "REPO_UNAVAILABLE", "error": e1 or "empty branch"}
            print("  MISS repo  %-42s %s" % (repo, (e1 or "")[:70]))
            continue
        time.sleep(0.3)
        ok2, raw, e2 = gh(["api", "repos/%s/git/trees/%s?recursive=1" % (repo, br),
                           "--jq", JQ_TREE], timeout=200)
        if not ok2 or not raw:
            out[repo] = {"state": "TREE_FAILED", "branch": br, "error": e2 or "empty"}
            print("  MISS tree  %-40s %s" % (repo, (e2 or "")[:70]))
            continue
        try:
            doc = json.loads(raw)
        except ValueError as exc:
            out[repo] = {"state": "TREE_JSON_BAD", "branch": br, "error": repr(exc)[:120]}
            print("  BAD json %-44s %s" % (repo, repr(exc)[:60]))
            continue
        paths = doc.get("paths") or []
        out[repo] = {"state": "OK", "branch": br, "truncated": bool(doc.get("truncated")),
                     "skill_md_paths": paths, "skill_md_n": len(paths)}
        print("  ok  %-44s SKILL.md=%-4d truncated=%s"
              % (repo, len(paths), bool(doc.get("truncated"))))
        time.sleep(0.3)
    io.open(os.path.join(HERE, "tree_paths.json"), "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    good = sum(1 for v in out.values() if v["state"] == "OK")
    print("[COLLECT] ok=%d failed=%d total=%d" % (good, len(out) - good, len(out)))
    return 0 if good > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
