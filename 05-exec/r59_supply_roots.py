# -*- coding: utf-8 -*-
r"""r59_supply_roots.py — 技能供给根计数与治理面守恒（R59-7 落地件，由 r60 补齐）.

存在理由（r59 一手实测）：同一个技能树由 **5 个根**供给会话，而 A-skill-manager 的治理面只覆盖
权威源 + 镜像两根；r59 报告 D9 把这件事第一次量化成「治理面只覆盖 170/438」，但那条台账里写的
`python 05-exec/r59_supply_roots.py` 是个**死句柄** —— r59 没有把这个生成器落进仓（W-46 通病第三次
复现：登记只落在一次性内联脚本里，仓里没有生成器，下一轮不带记忆的人无法复算）。本件即该句柄的实物。

判据面（一项事实只在一处判，见 run_gates 的 retired_face）：
  * 本件**不判**「权威根 ∩ 退役名单」（那是 retired_face 的活）；本件判的是
    **供给根守恒**：每根可数、名集可对齐、治理覆盖比例可复算。
  * 市场缓存根里重新出现的退役件 = **只报告不阻断**（守 r25：没量过误报率的闸门不得拦任务）。

取值：`python 05-exec/r59_supply_roots.py [--json <file>] [--selftest] [--quiet]`
退出码：0 = 守恒成立；1 = 守恒被破坏（名集漂移或分母自相矛盾）；
        2 = UNVERIFIED（任一根取不到 / 退役名单为空 / git 面为空 —— 一律不得静默当「无」，R247）。
"""

import argparse
import ctypes
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

AUTHORITY = r"D:\global_skills"
TRUTH = r"C:\Users\37533\Desktop\workspace\焚诀\eval\truth_constants.json"

# 声明式名册：判据对象、治理归属、是否进治理面 —— 全在一处，加一根只动这张表
ROOTS = [
    {"id": "authority", "path": AUTHORITY, "owner": "权威源（git + 私有归档远端）",
     "governed": True},
    {"id": "mirror_agents", "path": r"C:\Users\37533\.agents\skills",
     "owner": "镜像（check-skill-mirror 只读核）", "governed": True},
    {"id": "qd_junction", "path": r"C:\Users\37533\.qoder-cn\skills",
     "owner": "QD 端 junction → 权威源", "governed": True},
    {"id": "wb_junction", "path": r"C:\Users\37533\.workbuddy\skills",
     "owner": "WB 端 junction → 权威源", "governed": True},
    {"id": "marketplace", "path": r"C:\Users\37533\.workbuddy\skills-marketplace\skills",
     "owner": "第三方市场缓存根", "governed": False},
]
JUNCTION_SUSPECT = ("qd_junction", "wb_junction")
UNDERSCORE_NONSKILL = ("_trash", "_my-skills")  # 下划线前缀目录单独计数，不混进技能分母


def skill_names(root):
    """Top-level dirs carrying SKILL.md. The skill root is reached through a junction by
    several endpoints, so os.walk would miscount (A-skill-manager 铁律 1)."""
    if not os.path.isdir(root):
        return None, "root not a directory: %s" % root
    try:
        names = [d for d in sorted(os.listdir(root))
                 if os.path.isfile(os.path.join(root, d, "SKILL.md"))]
    except OSError as e:
        return None, "root unreadable: %s (%s)" % (root, e)
    if not names:
        return None, "root has 0 SKILL.md dirs: empty face, refuse to judge clean"
    return set(names), None


def is_reparse_dir(path):
    """实测 junction/symlink 判定：GetFileAttributesW 的 REPARSE_BIT，不是靠猜路径形态。"""
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
    except Exception:
        return None
    if attrs == -1:
        return None
    return bool(attrs & 0x400)


def load_retired(path):
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
    if not bl:
        return None, "retired_skills is EMPTY: a zero-entry blacklist cannot discriminate"
    return set(str(x) for x in bl), None


def git_tracked_top(root):
    """git 跟踪的顶层段集。空输出必须显形为 error —— r59 自抓 #3 记的就是把
    `git ls-files` 空输出读成「命令失败/没事」，真含义是「从来没人 add」。"""
    try:
        p = subprocess.run(["git", "-C", root, "ls-files"], capture_output=True,
                           encoding="utf-8", errors="replace", timeout=180)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, "git ls-files could not run: %s" % e
    if p.returncode != 0:
        return None, "git ls-files rc=%s: %s" % (p.returncode, (p.stderr or "").strip()[:200])
    lines = [ln.split("/")[0] for ln in (p.stdout or "").splitlines() if ln.strip()]
    if not lines:
        return None, "git ls-files returned 0 rows: empty git face, refuse to read as clean"
    return set(lines), None


def is_gitignored(root, rel):
    try:
        p = subprocess.run(["git", "-C", root, "check-ignore", "-q", rel],
                           capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return p.returncode == 0


def account(faces, enumerated_pairs, faces_counted):
    """守恒三查：分区和 == 扫描期累加、每根恰落一个分区、计数根数 == 可读根数。

    为什么不写成 `governed + (total - governed) == total`：那是自比恒等式，换错分母照样绿
    （本仓禁物）。这里 total 由**扫描期逐根累加**得到，分区和由 **faces 表**得到，两者走不同
    代码路径，对不上才叫判据。`account()` 单独成函数是为了能被夹具喂进 bogus 输入验证它有牙齿。
    """
    governed_units = sum(f["count"] or 0 for f in faces if f["governed"])
    ungoverned_units = sum(f["count"] or 0 for f in faces if not f["governed"])
    partition_sum = governed_units + ungoverned_units
    faces_partitioned = (sum(1 for f in faces if f["governed"])
                         + sum(1 for f in faces if not f["governed"]))
    readable = len([f for f in faces if f["count"] is not None])
    ok = (partition_sum == enumerated_pairs
          and faces_partitioned == len(faces)
          and faces_counted == readable)
    return {"governed_units": governed_units, "ungoverned_units": ungoverned_units,
            "partition_sum": partition_sum, "total_units": enumerated_pairs,
            "conservation_ok": ok}


def measure(roots, truth_path):
    """Return (doc, rc). rc 2 = UNVERIFIED, 1 = 守恒被破坏, 0 = OK."""
    notes, faces, unverified = [], [], []
    enumerated_pairs = 0   # 第三路取数：扫描时逐根累加，不由下面的分区求和反推
    faces_counted = 0
    for spec in roots:
        names, err = skill_names(spec["path"])
        row = {"id": spec["id"], "path": spec["path"], "owner": spec["owner"],
               "governed": spec["governed"], "count": None if names is None else len(names),
               "reparse": is_reparse_dir(spec["path"]), "realpath": None,
               "underscore_dirs": None, "retired_reproduced": []}
        if names is None:
            unverified.append("%s: %s" % (spec["id"], err))
            faces.append(row)
            continue
        try:
            row["realpath"] = os.path.realpath(spec["path"])
        except OSError:
            pass
        row["underscore_dirs"] = sorted(d for d in names if d.startswith("_"))
        row["skill_count"] = len(names - set(UNDERSCORE_NONSKILL))
        enumerated_pairs += len(names)
        faces_counted += 1
        retired, rerr = load_retired(truth_path)
        if retired is not None and not spec["governed"]:
            row["retired_reproduced"] = sorted(names & retired)
        faces.append(row)

    retired, rerr = load_retired(truth_path)
    if retired is None:
        unverified.append("retired: %s" % rerr)

    tracked, gerr = git_tracked_top(roots[0]["path"]) if roots else (None, "no roots")
    untracked_live, gitignored = [], []
    if tracked is None:
        unverified.append("git: %s" % gerr)
    else:
        auth, _ = skill_names(roots[0]["path"])
        if auth is not None:
            untracked_live = sorted(n for n in auth - tracked if not n.startswith("_"))
            gitignored = [n for n in untracked_live if is_gitignored(roots[0]["path"], n) is True]

    # 名集对齐：权威根 vs 镜像（r59 实测零差；漂移 = 镜像没跟上）
    by = {f["id"]: f for f in faces}
    drift = []
    if by.get("authority", {}).get("count") is not None and by.get("mirror_agents", {}).get("count") is not None:
        a, _ = skill_names(by["authority"]["path"])
        m, _ = skill_names(by["mirror_agents"]["path"])
        drift = sorted((a - m) | (m - a)) if a is not None and m is not None else ["<unreadable>"]
        notes.append("name_set_drift_authority_vs_mirror=%d" % len(drift))

    # 守恒按「两路独立取数对账」判，见 account() 的 docstring（禁自比恒等）
    acct = account(faces, enumerated_pairs, faces_counted)
    governed_units = acct["governed_units"]
    ungoverned_units = acct["ungoverned_units"]
    partition_sum = acct["partition_sum"]
    total_units = acct["total_units"]
    conservation_ok = acct["conservation_ok"]

    doc = {
        "schema": "supply-roots-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "faces": faces,
        "retired_blacklist_size": None if retired is None else len(retired),
        "untracked_live_skills": untracked_live,
        "untracked_but_gitignored": gitignored,
        "governed_roots": sum(1 for f in faces if f["governed"] and f["count"] is not None),
        "governed_units": governed_units,
        "ungoverned_units": ungoverned_units,
        "partition_sum": partition_sum,
        "total_units": total_units,
        "name_set_drift_authority_vs_mirror": drift,
        "conservation_ok": conservation_ok,
        "coverage_note": "治理覆盖 = governed_units/total_units（按根×技能计数，非唯一技能数）",
        "unverified": "; ".join(unverified),
    }
    if unverified:
        return doc, 2
    if not conservation_ok or drift:
        return doc, 1
    return doc, 0


def report(doc, quiet):
    for f in doc["faces"]:
        extra = ""
        if f["retired_reproduced"]:
            extra = " 退役件复现=%d: %s" % (len(f["retired_reproduced"]),
                                            ",".join(f["retired_reproduced"]))
        if not quiet:
            print("  %-15s %-6s count=%-5s skill=%-5s reparse=%-5s %s%s" % (
                f["id"], "GOV" if f["governed"] else "NOTGOV", f["count"],
                f.get("skill_count"), f["reparse"], f["owner"], extra))
    head = ("authority=%s governed_units=%s ungoverned_units=%s total_units=%s "
            "untracked_live=%s retired_reproduced_marketplace=%s" % (
                next((f["count"] for f in doc["faces"] if f["id"] == "authority"), "?"),
                doc["governed_units"], doc["ungoverned_units"], doc["total_units"],
                len(doc["untracked_live_skills"]),
                len(next((f["retired_reproduced"] for f in doc["faces"]
                          if f["id"] == "marketplace"), []))))
    if doc["unverified"]:
        print("[SUPPLY:UNVERIFIED] %s ｜ %s" % (head, doc["unverified"]))
    elif doc["conservation_ok"] and not doc.get("name_set_drift_authority_vs_mirror"):
        print("[SUPPLY:OK] %s ｜ partition_sum=%d vs enumerated_total=%d matched, faces=%d, drift=0" % (
            head, doc["partition_sum"], doc["total_units"], len(doc["faces"])))
    else:
        print("[SUPPLY:FAIL] %s ｜ conservation_ok=%s drift=%s" % (
            head, doc["conservation_ok"],
            doc.get("name_set_drift_authority_vs_mirror")))
    return 0


def build_roots_for(authority, mirror=None, market=None):
    """夹具用根表：把 authority 换成临时树，其余可指不存在面以测 UNVERIFIED 分支。"""
    out = []
    for spec in ROOTS:
        s = dict(spec)
        if s["id"] == "authority":
            s["path"] = authority
        if s["id"] == "mirror_agents":
            s["path"] = mirror if mirror is not None else spec["path"]
        if s["id"] == "marketplace":
            s["path"] = market if market is not None else spec["path"]
        if s["id"] in ("qd_junction", "wb_junction"):
            s["path"] = authority
        out.append(s)
    return out


def init_git_repo(path):
    """夹具用：把临时权威根变成真 git 仓。走真 `git ls-files` 代码路径，
    不开 `--skip-git` 旁路 —— 旁路即未被验证的分支（R238：单测通过≠接线正确）。"""
    cmds = [["init", "-q"], ["-c", "user.email=t@t", "-c", "user.name=t", "add", "-A"],
            ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "fixture"]]
    for c in cmds:
        try:
            p = subprocess.run(["git", "-C", path] + c, capture_output=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired):
            return False, "git %s could not run" % c[0]
        if p.returncode != 0:
            return False, "git %s rc=%s %s" % (c[0], p.returncode, (p.stderr or "")[:160])
    return True, ""


def selftest():
    checks = []
    tmp = tempfile.mkdtemp(prefix="r59_sr_")
    try:
        auth = os.path.join(tmp, "auth")
        mirror = os.path.join(tmp, "mirror")
        market = os.path.join(tmp, "market")
        for d, names in ((auth, ("alpha", "beta", "_my-skills")),
                         (mirror, ("alpha", "beta", "_my-skills")),
                         (market, ("alpha", "skill-creator"))):
            os.makedirs(d)
            for n in names:
                p = os.path.join(d, n)
                os.makedirs(p)
                with io.open(os.path.join(p, "SKILL.md"), "w", encoding="utf-8", newline="") as f:
                    f.write(u"# " + n)
        ok_git, gerr = init_git_repo(auth)
        if not ok_git:
            print("[GATE:supply-roots-selftest] 2/2 ENV-NOT-MET: %s" % gerr)
            return 2
        truth = os.path.join(tmp, "truth.json")
        with io.open(truth, "w", encoding="utf-8", newline="") as f:
            json.dump({"retired_skills": ["skill-creator", "notpresent"]}, f)

        def run_case(a, m, k, t):
            return measure(build_roots_for(a, m, k), t)

        d0, rc0 = run_case(auth, mirror, market, truth)
        checks.append((rc0 == 0, "s1 正例：三根可数且名集对齐 -> rc=0", "rc=%s" % rc0))
        checks.append((d0["governed_units"] + d0["ungoverned_units"] == d0["total_units"],
                       "s2 形状正例：真 doc 的 conservation_ok 应为 True（牙齿见 s10/s11 变异体）", "见 doc"))
        checks.append((len(d0["faces"][-1]["retired_reproduced"]) == 1,
                       "s3 市场根退役复现须被计数（只报告不阻断）",
                       str(d0["faces"][-1]["retired_reproduced"])))

        drift = os.path.join(tmp, "drift")
        shutil.copytree(auth, drift)
        os.makedirs(os.path.join(drift, "orphan"))
        with io.open(os.path.join(drift, "orphan", "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(u"# orphan")
        d1, rc1 = run_case(drift, mirror, market, truth)
        checks.append((rc1 == 1, "s4 变异体（应红）：镜像少一件 -> rc=1",
                       "rc=%s drift=%s" % (rc1, d1["name_set_drift_authority_vs_mirror"])))

        checks.append((d0["untracked_live_skills"] == [],
                       "s4b 正例：夹具权威根全部已跟踪 -> untracked_live=0",
                       str(d0["untracked_live_skills"])))
        stray = os.path.join(auth, "neveradded")
        os.makedirs(stray)
        with io.open(os.path.join(stray, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(u"# neveradded")
        d1b, _rc1b = run_case(auth, os.path.join(auth, "x"), market, truth)
        checks.append((d1b["untracked_live_skills"] == ["neveradded"],
                       "s4c 变异体（应显形）：新建未 add 的技能须进 untracked_live",
                       str(d1b["untracked_live_skills"])))
        shutil.rmtree(stray)

        # s9/s10 直接打 account()：证明守恒不是自比恒等 —— 累加值偏一格必须判 False
        good = [{"id": "x", "count": 3, "governed": True}, {"id": "y", "count": 2, "governed": False}]
        checks.append((account(good, 5, 2)["conservation_ok"] is True,
                       "s9 正例：分区和==扫描累加 且形状齐 -> True", "see account"))
        checks.append((account(good, 6, 2)["conservation_ok"] is False,
                       "s10 变异体（应红）：累加值多算一件 -> False",
                       str(account(good, 6, 2))))
        checks.append((account(good, 5, 1)["conservation_ok"] is False,
                       "s11 变异体（应红）：faces_counted 与实际可读根数不符 -> False",
                       str(account(good, 5, 1))))
        checks.append((account([{"id": "z", "count": None, "governed": True}], 0, 0)["conservation_ok"] is True,
                       "s12 边界：不可读根计 0 进 total（该态由 rc=2 拦，不由守恒拦）", "ok"))

        d2, rc2 = run_case(auth, os.path.join(tmp, "nope"), market, truth)
        checks.append((rc2 == 2, "s5 边界（不得判过）：镜像根不存在 -> rc=2 UNVERIFIED", "rc=%s" % rc2))
        empty_truth = os.path.join(tmp, "empty.json")
        with io.open(empty_truth, "w", encoding="utf-8") as f:
            json.dump({"retired_skills": []}, f)
        d3, rc3 = run_case(auth, mirror, market, empty_truth)
        checks.append((rc3 == 2, "s6 边界：空退役名单 -> rc=2（零输入不等于无残留）", "rc=%s" % rc3))
        d4, rc4 = run_case(os.path.join(tmp, "ghostauth"), mirror, market, truth)
        checks.append((rc4 == 2, "s7 边界：权威根为空面 -> rc=2，不得读成 0 件", "rc=%s" % rc4))
        # s8 方向断言：下划线目录单独计数，不混进技能分母
        checks.append((d0["faces"][0]["underscore_dirs"] == ["_my-skills"]
                       and d0["faces"][0]["skill_count"] == 2,
                       "s8 分母口径：_my-skills 不计入技能数",
                       "underscore=%s skill=%s" % (d0["faces"][0]["underscore_dirs"],
                                                   d0["faces"][0]["skill_count"])))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    ok = sum(1 for c in checks if c[0])
    for passed, name, detail in checks:
        print("%s %-56s %s" % ("PASS" if passed else "FAIL", name, "" if passed else detail))
    print("[GATE:supply-roots-selftest] %d/%d" % (ok, len(checks)))
    return 0 if ok == len(checks) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--json", dest="json_out", default="")
    ap.add_argument("--truth", default=TRUTH)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--help", action="store_true")
    a = ap.parse_args(argv)
    if a.help:
        print(__doc__)
        return 0
    if a.selftest:
        return selftest()
    doc, rc = measure(ROOTS, a.truth)
    if a.json_out:
        parent = os.path.dirname(os.path.abspath(a.json_out))
        if not os.path.isdir(parent):
            print("[SUPPLY:UNVERIFIED] json 落点目录不存在: %s" % parent)
            return 2
        with io.open(a.json_out, "w", encoding="utf-8", newline="") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    return report(doc, a.quiet) or rc


if __name__ == "__main__":
    sys.exit(main())
