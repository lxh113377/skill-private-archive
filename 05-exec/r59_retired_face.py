# -*- coding: utf-8 -*-
r"""r59_retired_face.py — 退役黑名单 vs 磁盘扫描树判据（第 24 道门）.

存在理由（r59 一手实测）：`executing-plans`、`slides` 早在 retired_skills 名单里，磁盘却仍带
SKILL.md 且能被会话加载。`disk_registry_diff.py` 把这个数**印了出来（「其中磁盘仍在: 2」）
却照打 [PASS]**——它的三类差集是 漏注册/回滚/幽灵，不含「退役未移出」。印数不判红 =
装饰性输出（本仓 R238「验证要覆盖接线」与「消不掉的告警等于没有判据」同族）。

取值：`python 05-exec/r59_retired_face.py [--truth <json>] [--tree <dir>] [--selftest] [--json <file>]`
退出码：0 = 干净；1 = 有退役残留；2 = UNVERIFIED（名单或磁盘面取不到，不得静默当「无」，R247）。
"""

import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

DEFAULT_TRUTH = r"C:\Users\37533\Desktop\workspace\焚诀\eval\truth_constants.json"
DEFAULT_TREE = r"D:\global_skills"
# 第二出口候选。r103 实测：该项是 Junction → DEFAULT_TREE（samefile=True / st_ino 相同），
# 故不再叫 MARKET_ROOT —— 名字本身曾把 r97 带进「两个独立出口」的错误前提。
DEFAULT_MARKET = r"C:\Users\37533\.workbuddy\skills"


def load_blacklist(path):
    if not os.path.isfile(path):
        return None, "truth_constants not found: %s" % path
    try:
        with io.open(path, encoding="utf-8-sig") as f:
            doc = json.load(f)
    except ValueError as e:
        return None, "truth_constants unparsable: %s" % e
    if "retired_skills" not in doc:
        return None, "retired_skills key absent in %s" % path
    bl = doc.get("retired_skills") or []
    if not isinstance(bl, list):
        return None, "retired_skills is %s, expected list" % type(bl).__name__
    if not bl:
        return None, "retired_skills is EMPTY: a zero-entry blacklist cannot discriminate anything"
    return set(str(x) for x in bl), None


def market_egress(tree, market_root, bl):
    """第二出口盘点 —— 只有当它真是另一棵树时才算持有。

    r103 一手：`C:\\Users\\37533\\.workbuddy\\skills` 实测是 Junction → `D:\\global_skills`
    （`os.path.samefile` 为 True、`st_ino` 相同、`realpath` 全等）。旧写法把它当独立出口，
    于是本门印出「只清权威源会被回流，用 r97_retire_full_egress.py 做全出口清理」这条
    **不可能照做**的处置：清权威源时 junction 那一侧同一步就没了，同一个对象被数了两次
    （r97 的面盘点因此报「4 处」、真实是 2 处；备份件数随之虚高一倍）。同事实只许一处判。
    返回 (hits, is_alias, tree_real, market_real)。
    """
    tree_real = os.path.realpath(tree)
    market_real = os.path.realpath(market_root)
    if not os.path.isdir(market_real):
        return [], False, tree_real, market_real
    if market_real == tree_real:
        return [], True, tree_real, market_real
    return (sorted(t for t in bl if os.path.isdir(os.path.join(market_real, t))),
            False, tree_real, market_real)


def scan_tree(root):
    """Top-level listing only — the skill root is reached through a junction by other
    endpoints, so os.walk would report a false zero (A-skill-manager 铁律 1)."""
    if not os.path.isdir(root):
        return None, "skill tree not a directory: %s" % root
    try:
        names = [d for d in sorted(os.listdir(root))
                 if os.path.isfile(os.path.join(root, d, "SKILL.md"))]
    except OSError as e:
        return None, "skill tree unreadable: %s" % e
    if not names:
        return None, "skill tree has 0 SKILL.md dirs: empty face, refuse to judge clean"
    return set(names), None


def emit(path, doc):
    if path:
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)


# r105 F-5：平台重下发的成批写入窗口（秒）。r100 实测 executing-plans 与 slides 落在同一秒
# 23:29:55；取 2s 覆盖同秒内的落盘抖动，**刻意不放宽到分钟级** —— 那会让「我方隔几分钟自己
# 复制回来一份」也被豁免，判据就失去鉴别力。
BATCH_WINDOW_S = 2


def _git_tracked_n(tree, name):
    """该退役件目录下被 git 跟踪的文件数。取不到（非仓/命令失败）返回 None ⇒ 调用方 fail-closed。

    用 `git -C <tree> ls-files -- <name>` 的**相对** pathspec：绝对路径带 Windows 反斜杠尾
    分隔符会被 git 当转义（本仓 windows-cli 同族坑），相对写法与 memory/AGENTS.md 排障表里
    既有取值命令同形。
    """
    try:
        p = subprocess.run(["git", "-C", tree, "ls-files", "--", name],
                           capture_output=True, text=True, timeout=60)
    except Exception:
        return None
    if p.returncode != 0:
        return None
    return len([x for x in (p.stdout or "").splitlines() if x.strip()])


def attribute_producer(tree, hits, batch_window_s=BATCH_WINDOW_S):
    """把「退役件仍在盘」按**写入方证据**分两堆，而不是按名字硬编码谁算豁免。

    判 platform_reflow 须两条同时成立（缺任一 → 归我方，照旧硬阻断）：
      ① 该件目录在 git 里零跟踪（tracked_n == 0）⇒ 不是我们提交回来的；
      ② 其 SKILL.md 的 mtime 与本批全部命中最大 mtime 相差 <= batch_window_s 秒
         ⇒ 成批写入特征（r100 实测平台重下发即此形态）。
    取不到 mtime / 取不到跟踪数 ⇒ 归我方（fail-closed，禁把「量不到」折算成「不是我的」）。
    """
    ev, mtimes = {}, []
    for n in hits:
        skill_md = os.path.join(tree, n, "SKILL.md")
        try:
            m = os.path.getmtime(skill_md)
        except OSError:
            m = None
        ev[n] = {"tracked_n": _git_tracked_n(tree, n), "skill_md": skill_md, "mtime": m,
                 "mtime_hms": time.strftime("%H:%M:%S", time.localtime(m)) if m else None}
        if m:
            mtimes.append(m)
    hi = max(mtimes) if mtimes else None
    ours, reflow = [], []
    for n in hits:
        tracked, m = ev[n]["tracked_n"], ev[n]["mtime"]
        spread = (hi - m) if (hi is not None and m is not None) else None
        ev[n]["spread_s"] = round(spread, 1) if spread is not None else None
        if tracked == 0 and spread is not None and spread <= batch_window_s:
            reflow.append(n)
        else:
            ours.append(n)
    return {"ours": ours, "reflow": reflow, "evidence": ev,
            "criteria": {"tracked_n_must_equal": 0, "mtime_spread_max_s": batch_window_s,
                         "fail_closed": "tracked 或 mtime 取不到 ⇒ 归 ours，不得折算成豁免"}}


def run(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--truth", default=DEFAULT_TRUTH)
    ap.add_argument("--tree", default=DEFAULT_TREE)
    ap.add_argument("--market-root", default=DEFAULT_MARKET,
                    help="第二出口候选（实测为 junction 时自动降格为同一对象，不重复计数）")
    ap.add_argument("--json", dest="json_out", default="")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--selftest-reflow", action="store_true",
                    help="r105 F-5 归属分堆的 W-47 双向证据（正例看守/两反例仍红/单件面/口径自证）")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest_reflow:
        return selftest_reflow_attribution()
    if a.selftest:
        return selftest()

    doc = {"schema": "retired-face-v1", "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "truth": a.truth, "tree": a.tree, "blacklist_size": 0, "disk_size": 0,
           "retired_still_on_disk": [], "unverified": ""}
    bl, e1 = load_blacklist(a.truth)
    disk, e2 = scan_tree(a.tree)
    doc["blacklist_size"] = len(bl) if bl else 0
    doc["disk_size"] = len(disk) if disk else 0
    if e1 or e2:
        doc["unverified"] = "; ".join(x for x in (e1, e2) if x)
        if not a.quiet:
            print("[GATE:retired-face-unverified] %s" % doc["unverified"])
        emit(a.json_out, doc)
        return 2
    hits = sorted(disk & bl)
    doc["retired_still_on_disk"] = hits
    # R97-7（r98 落地）：生产者可见性——权威源已清但市场缓存根仍持有退役件时，
    # 清了也会被回流（r97 实证：executing-plans/slides 由 .workbuddy/skills 于 15:24 写回）。
    # 警示不阻断（守 r25：没量过误报率的闸门不得拦任务）；本门判定面仍只看权威源磁盘 ∩ 名单。
    market_hits, alias, tree_real, market_real = market_egress(a.tree, a.market_root, bl)
    doc["market_root"] = a.market_root
    doc["market_root_realpath"] = market_real
    doc["market_root_is_alias_of_tree"] = alias
    doc["market_root_still_holding"] = market_hits
    if alias:
        doc["market_root_note"] = ("第二出口实测是本扫描树的 junction（realpath 全等）——"
                                   "同一对象，不计持有，也不得据此判「会被回流」")
    emit(a.json_out, doc)
    if hits:
        prov = attribute_producer(a.tree, hits)
        ours, reflow = prov["ours"], prov["reflow"]
        doc["retired_hits_split"] = {"ours": ours, "platform_reflow": reflow,
                                     "basis_evidence": prov["evidence"],
                                     "criteria": prov["criteria"]}
        if not a.quiet:
            print("[GATE:retired-face-%s] %d retired skill(s) still on disk: %s"
                  % ("fail" if ours else "watch", len(hits), ", ".join(hits)))
            for n in hits:
                ev = prov["evidence"].get(n, {})
                print("  %s %-18s 归属证据: 目录内 git 跟踪文件=%s ｜ SKILL.md mtime=%s ｜ 与同批最大差=%.0fs"
                      % ("⛔ 我方写入" if n in ours else "ℹ️ 平台回流", n,
                         ev.get("tracked_n"), ev.get("mtime_hms"), ev.get("spread_s")))
            if ours:
                print("  处置：按铁律 3 双备份移出扫描树（cp->copy/ + mv->moved/，落 "
                      "D:/global_memory/_trash/<tag>_<ts>/），再复跑本门。")
            else:
                print("  归属：全部命中项满足「整目录 git 零跟踪（我方从未提交）＋ mtime 同批"
                      "（差 ≤%ds，成批写入特征）」两项证据 ⇒ 生产者在我方写入链之外（平台重下发，"
                      "r100 实测节律 ~47min）。按 r25「没量过误报率的闸门不得拦任务」与本仓既有裁定"
                      "（W-39/X-9 不为凑绿动他人产出、r100 已把该形态降级为看守项），本门转"
                      "**具名看守**（rc=0）而非硬阻断：事实照印、名字照印，只是不再伪装成"
                      "「我欠的一次清理」。要终局消红只有两条合法路：撤销退役登记（改 "
                      "truth_constants.retired_skills，属用户裁定面）或在平台侧关下发（归属方非本仓）。"
                      % prov["criteria"]["mtime_spread_max_s"])
            if alias:
                print("  ℹ️ 第二出口 %s 经 realpath 判定与本树同一对象（st_ino 相同），"
                      "不存在「另一个根待清」；已移出却又回流 ⇒ 生产者在这棵树之外，"
                      "须先定位写入方（git ?? 未跟踪 + mtime 成批跳变即平台重下发），"
                      "再裁定「撤销退役登记」或「平台侧关下发」，不得再走全出口清理。"
                      % a.market_root)
            elif market_hits:
                print("  ⚠️ 生产者警示：市场缓存根 %s 仍持有 %d 件（%s）——只清权威源会被回流，"
                      "用 05-exec/r97_retire_full_egress.py --apply 做全出口清理。"
                      % (a.market_root, len(market_hits), ", ".join(market_hits)))
        emit(a.json_out, doc)
        return 1 if ours else 0
    if not a.quiet:
        print("[GATE:retired-face-pass] blacklist=%d disk=%d retired_still_on_disk=0"
              % (len(bl), len(disk)))
        if market_hits:
            print("  ⚠️ 生产者警示：独立第二出口 %s（realpath=%s，与扫描树不同对象）仍持有退役件 %d 件（%s）"
                  "——建议 r97_retire_full_egress.py --apply 全出口清理。"
                  % (a.market_root, market_real, len(market_hits), ", ".join(market_hits)))
        elif alias:
            print("  ℹ️ 第二出口 %s 与扫描树同一对象（junction），未计持有。" % a.market_root)
    return 0


def mk_skill(root, name):
    d = os.path.join(root, name)
    os.makedirs(d)
    with io.open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8", newline="") as f:
        f.write(u"# " + name)


def _git_init(root):
    """给临时树做 git 初始化（归属证据的 tracked_n 必须由真 git 回答，不能由桩伪造）。"""
    for args in (["init", "-q"], ["-c", "user.name=stub", "-c", "user.email=stub@local",
                                  "commit", "-q", "--allow-empty", "-m", "stub"]):
        subprocess.run(["git", "-C", root] + args, capture_output=True, text=True, timeout=120)


def selftest_reflow_attribution():
    """r105 F-5 的 W-47 双向证据：看守态只在**两条证据同时成立**时出现，任一不成立必须仍硬阻断。

    全部驱动 run() 本体（不在本件里重写归属谓词），临时树用真 git 起，
    这样 tracked_n 与 mtime 是「被测对象实际读到的量」，不是夹具自比的常量。
    """
    R = []

    def ck(name, got, want):
        R.append((got == want, name, "got=%r want=%r" % (got, want)))

    def write_truth(path, names):
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            json.dump({"retired_skills": list(names)}, f)

    def case(tag, tracked=False, gap_s=0.0, extra_batch=True):
        tmp = tempfile.mkdtemp(prefix="r105_rf_%s_" % tag)
        tree = os.path.join(tmp, "tree")
        os.makedirs(tree)
        names = ["alpha", "beta"] if extra_batch else ["alpha"]
        for i, n in enumerate(names):
            mk_skill(tree, n)
        _git_init(tree)
        if tracked:
            for n in names:
                subprocess.run(["git", "-C", tree, "add", "-f", "--", n],
                               capture_output=True, text=True, timeout=120)
                subprocess.run(["git", "-C", tree, "-c", "user.name=s", "-c", "user.email=s@l",
                                "commit", "-q", "-m", "track " + n],
                               capture_output=True, text=True, timeout=120)
        base = time.time()
        for i, n in enumerate(names):
            t = base + (gap_s if n == "beta" else 0.0)
            p = os.path.join(tree, n, "SKILL.md")
            os.utime(p, (t, t))
        truth = os.path.join(tmp, "truth.json")
        write_truth(truth, names)
        out = os.path.join(tmp, "o.json")
        rc = run(["--truth", truth, "--tree", tree, "--market-root", os.path.join(tmp, "none"),
                  "--json", out, "--quiet"])
        doc = json.load(io.open(out, encoding="utf-8")) if os.path.isfile(out) else {}
        return rc, doc

    rc1, doc1 = case("reflow")
    ck("r9 正例：退役件 git 零跟踪 + mtime 同批 ⇒ 转看守（rc=0，不是 rc=1）", rc1, 0)
    ck("r9b 看守态必须仍逐件具名（retired_still_on_disk 不得被清空）",
       sorted(doc1.get("retired_still_on_disk") or []), ["alpha", "beta"])
    ck("r9c 归属证据必须落件（platform_reflow 两条都在名册里）",
       sorted((doc1.get("retired_hits_split") or {}).get("platform_reflow") or []),
       ["alpha", "beta"])

    rc2, _ = case("ours_tracked", tracked=True)
    ck("r10 反例：同批 mtime 但**我方 git 跟踪过** ⇒ 仍硬阻断（豁免不得吞掉我方自己写回的件）", rc2, 1)

    rc3, _ = case("ours_spread", gap_s=90.0)
    ck("r11 反例：git 零跟踪但 mtime 相差 90s（>2s 成批窗口）⇒ 仍硬阻断（窗口不放宽到分钟级）", rc3, 1)

    rc4, doc4 = case("single", extra_batch=False)
    ck("r12 单件面不得因「无同批可比」静默放行（一件也算 spread=0，须走真判定而非跳过）",
       (rc4, sorted(doc4.get("retired_still_on_disk") or [])), (0, ["alpha"]))

    rc5, doc5 = case("reflow")
    crit = (doc5.get("retired_hits_split") or {}).get("criteria") or {}
    ck("r13 判据须自证口径（tracked_n_must_equal=0 与 mtime_spread_max_s 都写进产物，不留散文）",
       (crit.get("tracked_n_must_equal"), crit.get("mtime_spread_max_s")), (0, BATCH_WINDOW_S))

    bad = [r for r in R if not r[0]]
    for ok, name, det in R:
        print("%s %-72s %s" % ("PASS" if ok else "FAIL", name, "" if ok else det))
    print("\n归属分堆桩: %d 项，通过 %d，失败 %d" % (len(R), len(R) - len(bad), len(bad)))
    return 1 if bad else 0


def selftest():
    tmp = tempfile.mkdtemp(prefix="r59_rf_")
    tree = os.path.join(tmp, "tree")
    emptytree = os.path.join(tmp, "emptytree")
    os.makedirs(emptytree)
    checks = []

    def write_truth(path, names):
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            json.dump({"retired_skills": list(names)}, f)

    def ck(name, got, want):
        checks.append((got == want, name, "got=%s want=%s" % (got, want)))

    try:
        for n in ("alpha", "beta"):
            mk_skill(tree, n)
        os.makedirs(os.path.join(tree, "gamma"))          # no SKILL.md -> not a skill
        good = os.path.join(tmp, "truth_good.json")       # beta is retired and still on disk
        clean = os.path.join(tmp, "truth_clean.json")     # nothing retired on disk
        empty = os.path.join(tmp, "truth_empty.json")
        missing = os.path.join(tmp, "truth_missing.json")
        write_truth(good, ["beta", "zzz"])
        write_truth(clean, ["notpresent"])
        write_truth(empty, [])

        ck("r1 正例：黑名单全部已移出盘 -> rc=0",
           run(["--tree", tree, "--truth", clean, "--quiet"]), 0)
        ck("r2 反例：退役名仍带 SKILL.md -> rc=1 且点名",
           run(["--tree", tree, "--truth", good, "--quiet"]), 1)
        ck("r3 反例：空名单 -> rc=2（零输入不得判过，R247）",
           run(["--tree", tree, "--truth", empty, "--quiet"]), 2)
        ck("r4 反例：名单文件不存在 -> rc=2",
           run(["--tree", tree, "--truth", missing, "--quiet"]), 2)
        ck("r5 反例：磁盘面为空 -> rc=2（盘空也不配当「干净」）",
           run(["--tree", emptytree, "--truth", clean, "--quiet"]), 2)
        ck("r6 方向断言：无 SKILL.md 的 gamma 不计入分母",
           scan_tree(tree)[0], {"alpha", "beta"})
        # r7: reversible injection of a REAL blacklisted name into a copy of the tree
        real_bl, err = load_blacklist(DEFAULT_TRUTH)
        inj = sorted(real_bl)[0] if real_bl else None
        ck("r7 真件可逆注入：真名单首个名字建进临时树 -> 必须见红",
           (inj and _inject_and_run(tmp, tree, inj)) or 0, 1)
        ck("r8 真机对照：真名单 x 真树不得报 UNVERIFIED（rc 只能是 0/1）",
           run(["--quiet"]) in (0, 1), True)
        # r9/r10（r103 一手）：第二出口必须真是另一棵树才算持有。`C:\Users\37533\.workbuddy\skills`
        # 实测是 Junction → D:\global_skills（samefile=True、st_ino 相同），旧写法把它当独立根，
        # 面盘点因此翻倍（r97 印「4 处」而真实 2 处），并印出一条照做不到的处置。
        alias_root = _mk_junction(tmp, "alias_via_junction", tree)
        if alias_root:
            hits_a, is_alias_a, _, _ = market_egress(tree, alias_root, {"alpha", "beta"})
            ck("r9 反例 第二出口是本树 junction -> 判同一对象且持有清零",
               (hits_a, is_alias_a), ([], True))
            ck("r9b 接线 降格前提必须被 samefile 独立证实（不是只看路径字符串）",
               os.path.samefile(tree, alias_root), True)
        else:
            ck("r9 环境建不出 junction -> 显形未取证，不得静默当已验",
               "junction-unavailable", "junction-created")
        other = os.path.join(tmp, "other_root")
        mk_skill(other, "beta")
        hits_o, is_alias_o, _, _ = market_egress(tree, other, {"alpha", "beta"})
        ck("r10 正例 真独立的第二出口持有退役件 -> 点名且不降格",
           (hits_o, is_alias_o), (["beta"], False))
        hits_n, is_alias_n, _, _ = market_egress(tree, os.path.join(tmp, "nope"),
                                                 {"alpha", "beta"})
        ck("r10b 反例 第二出口不存在 -> 空持有且不是 alias（不得冒充已清）",
           (hits_n, is_alias_n), ([], False))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    ok = sum(1 for c in checks if c[0])
    for passed, name, detail in checks:
        print("%s %-58s %s" % ("PASS" if passed else "FAIL", name, detail if not passed else ""))
    print("[GATE:retired-face-selftest] %d/%d" % (ok, len(checks)))
    return 0 if ok == len(checks) else 1


def _mk_junction(base, name, target):
    """在 base 下建一个指向 target 的 NTFS junction（免管理员）。建不成返回 None。

    只允许指向临时树：夹具若把 junction 指向受管根，rmtree 清理失败会留下指向真根的链接。
    """
    link = os.path.join(base, name)
    try:
        rc = subprocess.call(["cmd", "/c", "mklink", "/J", link, target],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        return None
    return link if rc == 0 and os.path.isdir(link) else None


def _inject_and_run(tmp, tree, name):
    p = os.path.join(tmp, "truth_inj.json")
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        json.dump({"retired_skills": [name]}, f)
    mk_skill(tree, name)
    return run(["--tree", tree, "--truth", p, "--quiet"])


if __name__ == "__main__":
    sys.exit(run())
