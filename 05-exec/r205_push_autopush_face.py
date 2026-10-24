# -*- coding: utf-8 -*-
"""r205_push_autopush_face.py - 自动推送钩子「跑没跑、成没成」结果面（第 87 门）。

存在理由（r205 一手，且先纠正我自己的两个错判）：
本会话我看到「提交后 origin/main 没动」，先后得出两个结论，两个都错：
  ①「post-commit 钩子没在跑」——错。reflog 显示 commit 后约 10 秒 origin/main 被更新。
  ②「钩子跑了但 push 失败」——方向对但根因说错。实测 --dry-run（不真推）：
      裸 git push → rc=128，21.3s，Failed to connect to github.com:443
      带代理 push → rc=0，2.5s
    即 push 因缺代理失败，而钩子里 git push --quiet ... || true 把它静默吞掉。

真正的缺口不是「钩子没跑」，而是：自动推送链失败无人知晓。危害具体——
我这几十轮一直以为「提交即自动推送」，实际每轮都是又手工带代理推一遍；
哪天忘了手工推，仓里会安静躺着一个「以为推上去了」的本地提交。
三条既有 hook 判据都回答不了：r138 查文件在/含 exit 1/含入口串（静态文本）、
r140 查模板与实装件漂移、r141 查归属。它们全绿而推送链实际是断的——
这就是「判据查存在、不查结果」的盲区。

判据设计（零网络，全部本地可复算）：
  P1 钩子存在且是自动推送形态（含 git push 与 --quiet）
  P2 钩子含 || true 或等价静默吞并 ⇒ 记 SILENT_SWALLOW（本门要补的盲区）
  P3 推送结果有留痕（.git/autopush.log，与模板 $GITDIR/autopush.log 对齐），末行可解析出 rc/ts；
     没留痕 = UNVERIFIED（不按绿记，R247）
  P4 留痕末次 rc 非 0 ⇒ FAIL（推送链真的断了）
  P5 留痕末行时间旧于最近一次 commit ⇒ FAIL（提交了却没留痕 = 没触发）
  P6 代理前提显式化：钩子未引用代理 ⇒ 记 PROXY_UNSET 警告（不判红，但必须可见）

退出码：0 全过 / 1 有 FAIL / 2 UNVERIFIED（留痕缺失或不可解析）
portable=False：读 .git/hooks 本机仓库状态；CI 侧由 workflow 推，语义不同。
"""
import argparse
import datetime
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOOKS = os.path.join(ROOT, ".git", "hooks")
PUSH_HOOK = os.path.join(HOOKS, "post-commit")
PUSH_LOG = os.path.join(ROOT, ".git", "autopush.log")   # 与模板 $GITDIR/autopush.log 对齐
TOKEN = "[AUTOPUSH:PASS]"
SILENT_RE = re.compile(r"\|\|\s*true")
# 钩子 printf 产出的是 shell 可读 key=value 行，不是 JSON ⇒ 消费方适配生产方
KV_RE = re.compile(r"ts=(\S+)\s+rc=(-?\d+)(?:\s+head=(\S+))?")


def _read(p):
    try:
        return io.open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def git(*a, tt=90):
    import subprocess
    try:
        r = subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=tt)
        return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()
    except Exception as e:
        return 90, "EXC %r" % (e,)


def last_commit_ts():
    rc, o = git("log", "-1", "--format=%ct")
    if rc != 0 or not o.strip().isdigit():
        return None
    return int(o.strip())


def parse_log():
    """留痕末行须能解析出 rc 与 ts；解析不出即不可用（不得当作绿）。"""
    """两种形态都吃（消费方适配生产方）：① 钩子 printf 的 ts=… rc=… head=… 行；
    ② JSON 行（仓内 .installed.log 风格）。都取不到 rc/ts 才返回 None ⇒ UNVERIFIED。"""
    txt = _read(PUSH_LOG)
    n = 0
    last = None
    for line in txt.splitlines():
        s = line.strip()
        if not s:
            continue
        mk = KV_RE.search(s)
        if mk:
            n += 1
            last = {"ts": mk.group(1), "rc": int(mk.group(2)),
                    "head": mk.group(3) or ""}
            continue
        if s.startswith("{"):
            try:
                d = json.loads(s)
            except ValueError:
                continue
            if "rc" in d and "ts" in d:
                n += 1
                last = {"ts": str(d.get("ts")), "rc": d.get("rc"),
                        "head": str(d.get("head", ""))}
    if last is None:
        return None
    return {"rows": n, "last": last}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args(argv)
    fails, notes = [], []

    hook = _read(PUSH_HOOK)
    if not hook.strip():
        print("[AUTOPUSH:UNVERIFIED] post-commit 钩子不存在 => 自动推送链未安装（不是绿）")
        return 2
    is_autopush = ("git push" in hook) and ("--quiet" in hook)
    print("  P1 钩子存在且为自动推送形态（git push + --quiet）= %s" % is_autopush)
    if not is_autopush:
        fails.append("P1 钩子不是自动推送形态")
    else:
        print("     PASS P1")

    # 只扫真执行行：钩子注释里写着「旧版 || true 全吞」是史料，不是现行为
    # （与 r31 防递归守卫同型错：把标签/注释当调用 ⇒ 假阳性）
    _code = [l for l in hook.splitlines() if not l.strip().startswith("#")]
    _c = chr(10).join(_code)
    silent = bool(SILENT_RE.search(_c))
    print("  P2 钩子是否静默吞掉 push 失败（|| true / 2>/dev/null）= %s" % silent)
    if silent:
        notes.append("SILENT_SWALLOW：push 失败被 || true 吞掉，本门 P3~P5 补这个盲区")
    else:
        print("     PASS P2（失败会暴露）")

    lg = parse_log()
    if lg is None:
        print("  [AUTOPUSH:UNVERIFIED] 无 push 结果留痕或末行不可解析 => 无法判断成没成（R247）")
        print("     期望留痕：%s（钩子 printf 的 ts= rc= head= 行）" % os.path.relpath(PUSH_LOG, ROOT))
        return 2
    last = lg["last"]
    print("  P3 留痕可解析（%d 行，末行 rc=%s ts=%s）" % (lg["rows"], last.get("rc"), last.get("ts")))
    print("     PASS P3")

    try:
        rc_last = int(last.get("rc"))
    except (TypeError, ValueError):
        print("  [AUTOPUSH:UNVERIFIED] 留痕 rc 非整数 %r" % (last.get("rc"),))
        return 2
    if rc_last != 0:
        fails.append("P4 末次推送 rc=%d（推送链真的断了）" % rc_last)
        print("     FAIL P4 末次推送 rc=%d" % rc_last)
    else:
        print("     PASS P4 末次推送 rc=0")

    cts = last_commit_ts()
    try:
        lts = int(datetime.datetime.strptime(str(last.get("ts")),
                                             "%Y-%m-%dT%H:%M:%S").timestamp())
    except (TypeError, ValueError):
        lts = None
    if cts is None or lts is None:
        notes.append("P5 时间不可比（commit ts=%s / log ts=%s）" % (cts, lts))
        print("     ? P5 时间不可比")
    elif lts < cts:
        fails.append("P5 留痕(%s)旧于最近一次提交 => 该次提交没触发推送或没留痕"
                     % (last.get("ts"),))
        print("     FAIL P5 留痕旧于最近提交")
    else:
        print("     PASS P5 留痕新于最近提交")

    has_proxy = bool(re.search(r"(?:http\.proxy|https\.proxy|7897)", hook))
    print("  P6 钩子是否显式带代理 = %s" % has_proxy)
    if not has_proxy:
        notes.append("PROXY_UNSET：钩子未显式配代理；全局 http.proxy 与钩子裸跑是两件事，P4 会抓真实失败")
    else:
        print("     PASS P6")

    if args.out:
        with io.open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"schema": "autopush-face-v1", "readonly": True,
                       "hook_autopush": is_autopush, "silent_swallow": silent,
                       "log_rows": lg["rows"], "last_rc": rc_last, "notes": notes,
                       "provenance_cmd": "python 05-exec/r205_push_autopush_face.py"},
                      fh, ensure_ascii=False, indent=1)
        print("JSON -> %s" % args.out)
    if fails:
        print("[AUTOPUSH:FAIL] %d 项：%s" % (len(fails), "；".join(fails)[:200]))
        return 1
    if notes:
        print("  %s（附注 %d 条）" % (TOKEN, len(notes)))
    else:
        print("  %s" % TOKEN)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())