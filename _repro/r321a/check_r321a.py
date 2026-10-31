# -*- coding: utf-8 -*-
# r321a 自证脚本：读同目录 verdict.json，断言四条超期债务取证齐全、可复算、全程只读。
# 牙齿清单（每条都对应一个真实会漏的错误，不是装饰）：
#   T0 身份：head.repo / head.skills 必须是 40 位 sha —— 没有仓身份，证据在别人机器上复算不出。
#   T1 四条齐：items 的 key 序列恰为 R311-2/R317-2/R317-3/R317-4（少一条、换一条都红）。
#   T2 state 枚举：每条 ∈ {LANDED,NOT_LANDED,PARTIAL}；枚举外值（如 DONE）红并点名该条。
#   T3 证据三字段：evidence ≥1，cmd 非空且单行（逐字可复跑）、exit 是整数、reading 非空。
#   T4 只读面三道：(a) git 子命令 ∈ 只读白名单（比禁词表强：新出现的写动词不在禁词里也会红）；
#       (b) 任何 token 撞写命令禁词表即红（双保险，防写动词藏进引号段里）；
#       (c) 出现 -C 时目标必须是三条被检仓之一（项目仓 / 受管根 / 焚诀仓），别的仓一律红。
#   T5 limits 非空：未取证的面必须具名，防「全绿=全查过」的错觉。
# 负控纪律：本件只读 verdict.json、不写任何盘；红副本只在内存或系统 temp，仓内不留红件。
import io
import json
import os
import hashlib
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERDICT = os.path.join(HERE, "verdict.json")
EXPECTED_KEYS = ["R311-2", "R317-2", "R317-3", "R317-4"]
STATES = ("LANDED", "NOT_LANDED", "PARTIAL")
# 只读 git 子命令白名单：允许表外的任何 git 动词一律红（比禁词表覆盖面大）。
GIT_RO = set(["status", "log", "show", "diff", "ls-files", "rev-parse", "merge-base",
                  "grep", "ls-tree", "name-rev", "describe"])
# brief 给的禁用词表 + 同源扩展（写动作一律不许出现在取证命令里）。
GIT_WRITE = set(["add", "commit", "push", "checkout", "reset", "restore", "tag", "clean",
                   "stash", "merge", "rebase", "pull", "apply", "switch", "rm", "mv",
                   "branch", "cherry-pick", "am"])
ALLOWED_C = ("自建skill优化", "D:/global_skills", "workspace/焚诀")
SHA40 = re.compile("^[0-9a-f]{40}$")
DQ, SQ, BS = chr(34), chr(39), chr(92)
# token 化：双引号段/单引号段各算 1 个 token（引号内的词也进审查，禁词藏不住），其余按空白切。
TOK = re.compile("(" + DQ + "[^" + DQ + "]*" + DQ + ")|(" + SQ + "[^" + SQ + "]*" + SQ + ")|(\\S+)")


def tokens(cmd):
    out = []
    for m in TOK.finditer(cmd):
        g = m.group(1) or m.group(2) or m.group(3)
        if (m.group(1) or m.group(2)) and len(g) >= 2:
            g = g[1:-1]
        out.append(g)
    return out


def check(data):
    fails = []
    if data.get("schema") != "r321a-debt-verify-1":
        fails.append("schema != r321a-debt-verify-1")
    head = data.get("head") or {}
    for side in ("repo", "skills"):
        if not SHA40.match(head.get(side) or ""):
            fails.append("head.%s 非 40 位 sha（证据不可复算）" % side)
    if not (data.get("limits") or "").strip():
        fails.append("limits 缺失/为空：未取证的面必须具名")
    items = data.get("items") or []
    keys = [it.get("key") for it in items]
    if keys != EXPECTED_KEYS:
        fails.append("items.key 序列=%s 期望=%s" % (keys, EXPECTED_KEYS))
    for it in items:
        key = it.get("key", "?")
        if it.get("state") not in STATES:
            fails.append("%s: state=%r 不在枚举 %s" % (key, it.get("state"), list(STATES)))
        for field in ("claim", "recommend"):
            if not (it.get(field) or "").strip():
                fails.append("%s: %s 为空" % (key, field))
        ev = it.get("evidence") or []
        if not ev:
            fails.append("%s: evidence 为空（零可复算证据）" % key)
        for i, e in enumerate(ev):
            cmd = e.get("cmd")
            if not isinstance(cmd, str) or not cmd.strip() or chr(10) in cmd:
                fails.append("%s evidence[%d]: cmd 缺失/空/含换行（须逐字可复跑）" % (key, i))
                continue
            if not isinstance(e.get("exit"), int):
                fails.append("%s evidence[%d]: exit 非整数" % (key, i))
            if not (isinstance(e.get("reading"), str) and e.get("reading").strip()):
                fails.append("%s evidence[%d]: reading 缺失/为空" % (key, i))
            low = [t.lower() for t in tokens(cmd)]
            toks = tokens(cmd)
            for t in low:
                if t in GIT_WRITE:
                    fails.append("%s evidence[%d]: cmd 撞 git 写命令禁用词 %r" % (key, i, t))
            for j, t in enumerate(low):
                if not (t.endswith("git.exe") or t == "git"):
                    continue
                rest = toks[j + 1:]
                sub, k = None, 0
                while k < len(rest):
                    if rest[k] == "-C":
                        if k + 1 >= len(rest):
                            fails.append("%s evidence[%d]: -C 缺目标" % (key, i))
                            k += 1
                            continue
                        tgt = rest[k + 1].replace(BS, "/")
                        if not any(a in tgt for a in ALLOWED_C):
                            fails.append("%s evidence[%d]: git -C 目标 %r 不在被检仓白名单" % (key, i, rest[k + 1]))
                        k += 2
                        continue
                    if rest[k].startswith("-"):
                        k += 1
                        continue
                    sub = rest[k]
                    break
                if sub is not None and sub not in GIT_RO:
                    fails.append("%s evidence[%d]: git 子命令 %r 不在只读白名单" % (key, i, sub))
    return fails


def main():
    try:
        with io.open(VERDICT, encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:
        print("[R321A:DEBT] FAIL: verdict.json 读不到/非法 JSON: %r" % (exc,))
        print("[R321A:DEBT] ok=0/4 verdicts=uncited")
        return 1
    fails = check(data)
    if fails:
        for f in fails:
            print("[R321A:DEBT] FAIL: " + f)
        bad = set()
        for f in fails:
            for k in EXPECTED_KEYS:
                if f.startswith(k + ":"):
                    bad.add(k)
        print("[R321A:DEBT] ok=%d/4 verdicts=%s" % (4 - len(bad), "cited" if not bad else "uncited"))
        return 1
    print("[R321A:DEBT] items=4 states=%s evidence=%d cited=4/4" % (
        ",".join(it["state"] for it in data["items"]),
        sum(len(it["evidence"]) for it in data["items"])))
    # 收尾前打印两个被检产物的内容哈希（brief 要求读数里写明 verdict.json 与 report.md 的 sha256 前 12 位；
    # 放这里是因为 report.md 无法内嵌自身终态哈希，由判据现算现打）
    for nm in ("verdict.json", "report.md"):
        fp = os.path.join(HERE, nm)
        try:
            with open(fp, "rb") as fh:
                print("[R321A:DEBT] sha256-12 %s=%s" % (nm, hashlib.sha256(fh.read()).hexdigest()[:12]))
        except Exception as exc:
            print("[R321A:DEBT] sha256-12 %s=UNREADABLE(%r)" % (nm, exc))
    print("[R321A:DEBT] ok=4/4 verdicts=cited")
    return 0


if __name__ == "__main__":
    sys.exit(main())
