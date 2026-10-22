# -*- coding: utf-8 -*-
# r163_net_path_probe.py -- git 远端通路两态探针（直连 vs 走代理，各跑一次再定方向）。
#
# 存在理由（r163 一手）：R151-9 与 R161-2 都登记过「推送失败 ⇒ 清空代理绕行」，
#   本轮同一仓同一远端实测**方向相反**：清空代理三连失败（git 报 Failed to connect
#   github.com:443、Test-NetConnection 443=False），而显式设代理 rc=0 推成功。
#   ⇒ 网络通路不是固定解，任一方向当处方用都会在漂移时假红/假绿。
#   本探针把「先量两态」变成一条命令，替代凭记忆挑方向。
#
# 用法: python 05-exec/r163_net_path_probe.py [--repo <path>] [--remote origin]
# 退出码: 0 至少一态可用（打印推荐方向）/ 2 两态都不可用或取不到读数（UNVERIFIED）
import argparse
import os
import subprocess
import sys

PROXY = os.environ.get("FJ_PROBE_PROXY", "http://127.0.0.1:7897")


def _git(repo, argv, timeout=90):
    try:
        p = subprocess.run(["git", "-C", repo] + argv,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
        return p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()
    except (OSError, subprocess.SubprocessError) as e:
        return None, "EXC %r" % e


def probe(repo, remote):
    rows = []
    for label, cfg in (("direct", ["-c", "http.proxy=", "-c", "https.proxy="]),
                       ("proxy", ["-c", "http.proxy=%s" % PROXY,
                                 "-c", "https.proxy=%s" % PROXY])):
        env = dict(os.environ)
        for k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
            env.pop(k, None)
        try:
            p = subprocess.run(["git", "-C", repo] + cfg + ["ls-remote", remote, "refs/heads/main"],
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=90, env=env)
            rc, out = p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()
        except (OSError, subprocess.SubprocessError) as e:
            rc, out = None, "EXC %r" % e
        rows.append((label, rc, out.splitlines()[:1]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--remote", default="origin")
    args = ap.parse_args()
    rows = probe(args.repo, args.remote)
    for label, rc, head in rows:
        print("  %-7s rc=%-5s %s" % (label, rc, (head[0][:90] if head else "")))
    ok = [l for l, rc, _ in rows if rc == 0]
    if not ok:
        print("[NETPATH:UNVERIFIED] 两态均不可用（禁把任一方向当固定解，须先取证网络本体）")
        return 2
    print("[NETPATH:PROBED] 可用态=%s ｜ 结论：推送前跑本探针定方向，禁凭 R151-9/R161-2 任一固定处方"
          % ",".join(ok))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())