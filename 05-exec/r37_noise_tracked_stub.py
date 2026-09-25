# -*- coding: utf-8 -*-
r"""r37_noise_tracked_stub.py — noise_lint 两处**破坏性假阳性**的隔离桩（TDD：先看红，再改上游）。

根因（2026-09-25 实测，本项目 savepoint 连续 7 轮被同 5 条 VIOL 拒）：
① `焚诀/CONTRIBUTING.md`、`LICENSE.md`、`SECURITY.md` 是**归属方有意入库并已提交**的治理件
   （`114b5b0 docs(7-J): 根部社区件回正`），但不在 strict allowlist ⇒ 判 VIOL，
   且工具给出的处置是 **`迁往 _trash`** —— 对已跟踪治理文件而言这是破坏性建议（R263 禁「改数据凑判据」，
   此处是**判据本身错**）。
② `.git/push-failure.log` 是**仓内工具 `git_autopush.py` 的运行态产物**，写在 `.git` 里，
   无法被 `.gitignore` 豁免（`.git` 不受版本管理）⇒ 只要发生过一次推送失败，本门**永久红**。
   二级扫描把 `.git` 当普通子目录深扫，是把「git 运行态」误当「项目内容面」。

放行边界（牙齿必须保住，桩内含反例）：
- 只放行 **strict 模式 / 文件（非目录）/ 且命名不撞 STRAY·MIGRATION** 的已跟踪根部项；
- 目录仍按 allowlist 判；未跟踪文件仍判 VIOL；git 不可用 ⇒ 按未跟踪处理（fail-closed）。

被测对象：`D:\global_skills\A-project-handoff\scripts\noise_lint.py`
退出码：0 全过 / 1 有失败（含上游未改时的红阶段）
"""

import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

NL_PATH = Path(r"D:\global_skills\A-project-handoff\scripts\noise_lint.py")
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-52s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load_nl():
    spec = importlib.util.spec_from_file_location("noise_lint", str(NL_PATH))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(root, *args):
    return subprocess.run(["git", "-C", str(root)] + list(args),
                          capture_output=True, text=True,
                          env=dict(os.environ, GIT_AUTHOR_DATE="2020-01-01T00:00:00 +0800",
                                   GIT_COMMITTER_DATE="2020-01-01T00:00:00 +0800"))


def build_repo(tmp):
    """造一个 strict 根：含已跟踪治理件 / 未跟踪随手件 / 已跟踪但命名散落件 / 已跟踪目录 / .git 运行态。"""
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "CONTRIBUTING.md").write_text("# contributing\n", encoding="utf-8")
    # 命名即散落、且故意连它一起提交：验证「已跟踪」不得越过命名规则。实测 STRAY_NAME 锚在行尾，
    # `foo_bak.txt` 以 .txt 结尾不命中 —— 首版桩据此写出过一个**假反例**（R220 抽验抓回），换成命中的 notes_old
    (tmp / "notes_old").write_text("stray but tracked\n", encoding="utf-8")
    (tmp / "docs_dir").mkdir()
    (tmp / "docs_dir" / "a.md").write_text("x\n", encoding="utf-8")
    (tmp / "scripts").mkdir()
    (tmp / "scripts" / "handoff.py.bak_20260815").write_text("real scatter\n", encoding="utf-8")
    git(tmp, "init", "-q")
    git(tmp, "-c", "user.name=stub", "-c", "user.email=stub@local", "add", "-A")
    r = git(tmp, "-c", "user.name=stub", "-c", "user.email=stub@local", "commit", "-q", "-m", "stub")
    assert r.returncode == 0, r.stdout + r.stderr
    # 提交**之后**才落盘 = 真·未跟踪（首版把它写在 add -A 之前，于是"未跟踪"断言其实跟踪着，
    # t2/t6/t10 三条反例全成了假通过 —— 本次连带修桩）
    (tmp / "scratch.md").write_text("nobody tracked this\n", encoding="utf-8")
    # 提交后再落一个 .git 内的运行态日志（模拟 git_autopush.py 的失败留痕）
    (tmp / ".git" / "push-failure.log").write_text("fatal: could not read\n", encoding="utf-8")
    return tmp


def main():
    if not NL_PATH.exists():
        print("上游不存在：%s" % NL_PATH)
        return 2
    nl = load_nl()
    cfg = {"mode": "strict", "dirs": {".git", "scripts"}, "files": {".gitignore"}}

    tmp = Path(tempfile.mkdtemp(prefix="r37_noise_"))
    repo = build_repo(tmp / "repo")

    def cls(root, name):
        return nl.classify(str(root), os.path.join(str(root), name), cfg)

    def cls2(root, name, conf):
        return nl.classify(root, os.path.join(root, name), conf)

    # --- ① 已跟踪治理件：应放行（改前为 VIOL = 本次的红） ---
    s, why = cls(repo, "CONTRIBUTING.md")
    ck("t1 已跟踪根部治理件 → 非 violation", s != "violation", "%s %s" % (s, why))
    # --- 反例（牙齿）：未跟踪随手件必须照判 ---
    s2, why2 = cls(repo, "scratch.md")
    ck("t2 未跟踪根部随手件 → 仍 VIOL", s2 == "violation", "%s %s" % (s2, why2))
    # --- 反例：已跟踪但命名即散落（*_bak）—— 命名规则必须赢过跟踪放行 ---
    s3, why3 = cls(repo, "notes_old")
    ck("t3 已跟踪但命名散落（STRAY_NAME 命中）→ 仍 VIOL", s3 == "violation", "%s %s" % (s3, why3))
    # --- 反例：已跟踪**目录**不在 allowlist → 仍 VIOL（只放行文件） ---
    s4, why4 = cls(repo, "docs_dir")
    ck("t4 已跟踪目录不在清单 → 仍 VIOL", s4 == "violation", "%s %s" % (s4, why4))
    # --- 辅助函数存在性（实现须新增 git_tracked） ---
    ck("t5 暴露 git_tracked 且对已跟踪返回 True",
       hasattr(nl, "git_tracked") and nl.git_tracked(str(repo), "CONTRIBUTING.md") is True,
       str(getattr(nl, "git_tracked", None)))
    ck("t6 git_tracked 对未跟踪返回 False（fail-closed）",
       hasattr(nl, "git_tracked") and nl.git_tracked(str(repo), "scratch.md") is False, "")
    ck("t7 git_tracked 在非仓库根返回 False（不得当作已跟踪放行）",
       hasattr(nl, "git_tracked") and nl.git_tracked(str(tmp), "whatever.md") is False, "")

    # --- ② 二级扫描：.git 运行态不深扫，普通子目录散落照抓 ---
    res = nl.scan_root(str(repo), quiet=True)
    viol = {v["name"] for v in res["violation"]}
    ck("t8 .git 内运行态日志不再被深扫判 VIOL", ".git/push-failure.log" not in viol, str(sorted(viol)))
    ck("t9 反例保住：scripts/*.bak_ 仍被二级扫描抓到",
       "scripts/handoff.py.bak_20260815" in viol, str(sorted(viol)))
    ck("t10 反例保住：未跟踪 scratch.md 出现在一级 VIOL", "scratch.md" in viol, str(sorted(viol)))
    ck("t11 放行不含 allowlist 项：CONTRIBUTING.md 已不在 VIOL",
       "CONTRIBUTING.md" not in viol, str(sorted(viol)))

    # --- 真实受管根回归：焚诀三条治理件 + 两个 .git 日志必须不再是 VIOL ---
    for root in (r"C:\Users\37533\Desktop\workspace\焚诀", r"D:\global_memory"):
        if not os.path.isdir(root):
            ck("真实根存在 %s" % root, False, "目录不存在")
            continue
        rr = nl.scan_root(root, quiet=True)
        rv = {v["name"] for v in rr["violation"]}
        if "焚诀" in root:
            want_absent = {"CONTRIBUTING.md", "LICENSE.md", "SECURITY.md", ".git/push-failure.log"}
        else:
            want_absent = {".git/push-failure.log"}
        still = sorted(want_absent & rv)
        ck("真实根 %s 已知假阳性清零" % os.path.basename(root), not still, str(sorted(rv))[:220])

    # --- R283 续：harness auto-memory 根件放行面（feedback-* 已放行，reference-* 今日实测新挡一次）---
    GM = os.path.normpath(r"D:\global_memory")
    gcfg = nl.KNOWN_CORE[nl.os.path.normcase(GM)] if hasattr(nl, "os") else None
    gcfg = nl.KNOWN_CORE.get(__import__("os").path.normcase(GM))
    ck("t12 GM 根 reference-*.md → 非 violation（不再挡 savepoint）",
       gcfg is not None and cls2(GM, "reference-github-pages-blocked.md", gcfg)[0] != "violation",
       str(cls2(GM, "reference-github-pages-blocked.md", gcfg)) if gcfg else "GM 未登记")
    ck("t13 反例：大写不匹配命名约定 → 仍 VIOL",
       cls2(GM, "reference-Google.md", gcfg)[0] == "violation", str(cls2(GM, "reference-Google.md", gcfg)))
    ck("t14 反例：放行面不外溢 —— 焚诀根同名件仍按该根清单判 VIOL",
       cls2(r"C:\Users\37533\Desktop\workspace\焚诀", "reference-github-pages-blocked.md",
            nl.KNOWN_CORE[os.path.normcase(r"C:\Users\37533\Desktop\workspace\焚诀")])[0] == "violation",
       str(cls2(r"C:\Users\37533\Desktop\workspace\焚诀", "reference-github-pages-blocked.md",
                nl.KNOWN_CORE[os.path.normcase(r"C:\Users\37533\Desktop\workspace\焚诀")])))

    fails = [r for r in RESULTS if not r[0]]
    print("\n桩合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    if fails:
        print("[GATE:fixture-fail]")
        for ok_, name, detail in fails:
            print("  FAIL %s | %s" % (name, detail))
        return 1
    print("[GATE:fixture-pass]")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    raise SystemExit(main())
