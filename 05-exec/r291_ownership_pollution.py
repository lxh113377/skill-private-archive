# -*- coding: utf-8 -*-
"""他人交付件的所有权污染面（r291 / R286-1 的机械化）。

一手（r286 我造成）：复跑 owner 的判据时没带 --out，而该脚本 DEFAULT_OUT 就指向 owner 的交付件
=> 复跑把 generated_at 与 129 条明细刷成我这遍的产物：**数值零漂移，但所有权与生成时刻已属我**。
r291 复跑 L 的 r285_validate.mjs 时我验过一次未污染（measured_at 未变、非时间字段与 HEAD 全等），
但那次没污染的原因是 **owner 的判据把写盘关在 --emit deliverable 后面**，不是我做到了「先 grep
默认输出路径」。靠别人的门槛保平安不叫纪律，所以要机器化。

可判的签名（这是本面的判别力来源）：
    跟踪的交付件，工作树版与 HEAD 版**只有时间字段不同**（内容等价）=> 判「污染」；
    内容也变了 => 那是一次真实修改，不判污染（避免把正常编辑当违规，那是恒红门）。
时间字段名按本仓实际写法列举（measured_at / generated_at / updated_at / timestamp / ts / ran_at
/ at / date / finished_at / started_at）；比较时**只剥掉这些键**，其余逐字段 sort_keys 序列化比对。

用法：python 05-exec/r291_ownership_pollution.py [--root .] [--json f] [--selftest]
末行：[POLLUTION:FACE] tracked_json=<n> polluted=<n> changed=<n> selftest=<ok|skip>
退出码：0 无污染 / 1 有污染 / 2 git 或输入不可用（UNVERIFIED，禁读成通过，R247）。
"""
import argparse
import io
import json
import os
import subprocess
import sys
import tempfile

TIME_KEYS = {"measured_at", "generated_at", "updated_at", "timestamp", "ts", "ran_at",
             "at", "date", "finished_at", "started_at", "registered_at", "created_at"}


def git(root, args):
    r = subprocess.run(["git", "-c", "core.quotepath=false", "-C", root] + args,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return (r.stdout or "") if r.returncode == 0 else None


def tracked_json(root):
    out = git(root, ["ls-files", "*.json"])
    if out is None:
        return None
    return [x.strip().replace("\\", "/") for x in out.splitlines() if x.strip()]


def strip_time(x):
    if isinstance(x, dict):
        return dict((k, strip_time(v)) for k, v in x.items() if k not in TIME_KEYS)
    if isinstance(x, list):
        return [strip_time(v) for v in x]
    return x


def classify(root, rel):
    """返回 (kind, detail)。kind ∈ ok / changed / polluted / unreadable。"""
    head_raw = git(root, ["show", "HEAD:" + rel])
    if head_raw is None:
        return "unreadable", "HEAD 版取不到"
    p = os.path.join(root, rel)
    if not os.path.isfile(p):
        return "changed", "工作树已删（真实修改，非污染）"
    try:
        a = json.loads(head_raw)
        b = json.loads(io.open(p, encoding="utf-8", errors="replace").read())
    except Exception as e:
        return "unreadable", "JSON 解析失败 %r" % e
    if head_raw == io.open(p, encoding="utf-8", errors="replace").read():
        return "ok", "逐字节相同"
    if json.dumps(strip_time(a), sort_keys=True) == json.dumps(strip_time(b), sort_keys=True):
        # 内容等价但字节不同 => 只有时间字段漂移 = 复跑覆盖了 owner 的交付件
        drift = [k for k, v in (a.items() if isinstance(a, dict) else []) if v != b.get(k)] if isinstance(b, dict) else []
        return "polluted", "仅时间字段漂移 %s" % (drift[:4])
    return "changed", "内容有实质变化（真实修改）"


def scan(root):
    files = tracked_json(root)
    if files is None:
        return None, None, None
    res = []
    for rel in files:
        if not rel.startswith("06-benchmark/"):
            continue
        # 范围规则（r291 实测加，缺它就会造出恒红门）：*_latest.json 是门禁每次跑都刷新的
        # **快照**，其所有权归运行门禁的会话（R285-4 已定：本会话跑过 run_gates 则由本会话提交）。
        # 所以「只有时间字段漂移」对它们是**设计行为**，不是污染。真正要防的是覆盖**具名交付件**
        # （owner 那一轮的产物，如 r285_guard_false_positive.json / r285_exec_commands_ab.json）。
        if rel.endswith("_latest.json") and not getattr(scan, "include_latest", False):
            continue
        kind, det = classify(root, rel)
        res.append((rel, kind, det))
    return res, len(res), None


def selftest():
    """造一个临时 git 仓：三种态都要判对（含两条负控性质）。"""
    d = tempfile.mkdtemp(prefix="r291_poll_")
    git(d, ["init", "-q"])
    git(d, ["config", "user.email", "t@t"])
    git(d, ["config", "user.name", "t"])
    os.makedirs(os.path.join(d, "06-benchmark"), exist_ok=True)
    w = lambda n, o: io.open(os.path.join(d, "06-benchmark", n), "w", encoding="utf-8").write(
        json.dumps(o, ensure_ascii=False, indent=1))
    w("a.json", {"schema": "x", "measured_at": "2026-01-01T00:00:00", "rows": [1, 2, 3]})
    w("b.json", {"schema": "y", "measured_at": "2026-01-01T00:00:00", "rows": [1, 2, 3]})
    w("c.json", {"schema": "z", "value": 7})
    git(d, ["add", "-A"])
    git(d, ["commit", "-qm", "seed"])
    # a：只改时间字段 => 必须判 polluted
    w("a.json", {"schema": "x", "measured_at": "2026-10-30T10:00:00", "rows": [1, 2, 3]})
    # b：改内容（时间不动）=> 必须判 changed，不得当污染（防恒红）
    w("b.json", {"schema": "y", "measured_at": "2026-01-01T00:00:00", "rows": [1, 2, 9]})
    # c：不动 => ok
    got = {}
    for n in ("a.json", "b.json", "c.json"):
        got[n] = classify(d, "06-benchmark/" + n)[0]
    # 范围腿：具名交付件必须被抓（复现 r286 真事故），_latest 默认必须不抓
    named = "06-benchmark/other_round_deliverable.json"
    io.open(os.path.join(d, named), "w", encoding="utf-8").write(
        json.dumps({"schema": "x", "generated_at": "2026-10-29T06:00:00", "hits_detail": [1, 2]}, ensure_ascii=False))
    git(d, ["add", "-A"])
    git(d, ["commit", "-qm", "owner deliverable"])
    io.open(os.path.join(d, named), "w", encoding="utf-8").write(
        json.dumps({"schema": "x", "generated_at": "2026-10-30T10:00:00", "hits_detail": [1, 2]}, ensure_ascii=False))
    kind_named = classify(d, named)[0]
    ok = (got["a.json"] == "polluted" and got["b.json"] == "changed" and got["c.json"] == "ok"
          and kind_named == "polluted")
    print("[SELFTEST] named-deliverable=%s(须polluted)" % kind_named)
    print("[SELFTEST] a=%s(须polluted) b=%s(须changed) c=%s(须ok) => %s"
          % (got["a.json"], got["b.json"], got["c.json"], "PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", dest="js")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--include-latest", action="store_true",
                    help="把 *_latest.json 也纳入（默认排除：那是门禁刷新快照，非他人交付件）")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    scan.include_latest = a.include_latest
    res, n, err = scan(a.root)
    if res is None:
        print("[POLLUTION:UNVERIFIED] git 不可用或 ls-files 失败（禁读成无漂移）")
        return 2
    pol = [x for x in res if x[1] == "polluted"]
    chg = [x for x in res if x[1] == "changed"]
    unr = [x for x in res if x[1] == "unreadable"]
    doc = {"schema": "ownership-pollution-v1", "tracked_json": n,
           "polluted": [x[0] for x in pol], "changed": [x[0] for x in chg],
           "unreadable": [x[0] for x in unr],
           "time_keys": sorted(TIME_KEYS),
           "reading_rule": "仅时间字段漂移=复跑覆盖他人交付件（所有权污染）；内容变化=真实修改，不判污染"}
    if a.js:
        dd = os.path.dirname(a.js)
        if dd:
            os.makedirs(dd, exist_ok=True)
        io.open(a.js, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1))
    for x in pol:
        print("   POLLUTED %s %s" % (x[0], x[2][:90]))
    for x in unr:
        print("   UNREADABLE %s %s" % (x[0], x[2][:70]))
    print("[POLLUTION:FACE] tracked_json=%d polluted=%d changed=%d unreadable=%d"
          % (n, len(pol), len(chg), len(unr)))
    return 1 if pol else 0


if __name__ == "__main__":
    sys.exit(main())
