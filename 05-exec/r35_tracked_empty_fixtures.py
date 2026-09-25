# -*- coding: utf-8 -*-
"""r35_tracked_empty_fixtures.py — 第 7 道门（0 字节 tracked 件）的夹具 + 变异对照。

有效性口径沿用 r32/r34 立的规矩：**每条变异必须绑定"只有它能变红"的专属输入面**，
且"加载失败/取数失败"一律**不计功**（不得把探针自身失效记成判据生效）。
临时仓用真 `git init` + `git commit` 造 tracked 面，不用假数据骗自己。
"""

import importlib.util
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "r35_tracked_empty.py"
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-62s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load(path=None):
    src = Path(path or TARGET)
    spec = importlib.util.spec_from_file_location("te_%s" % abs(hash(str(src))), str(src))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def git(repo, *args):
    return subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "-C", repo] + list(args),
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def make_repo(files):
    """files: {相对路径: 内容str 或 b'' }；返回 repo path。"""
    repo = tempfile.mkdtemp(prefix="r35_repo_")
    git(repo, "init", "-q", ".")
    for rel, content in files.items():
        fp = Path(repo) / rel
        fp.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            fp.write_bytes(content)
        else:
            fp.write_text(content, encoding="utf-8")
    if files:
        git(repo, "add", "-A")
        r = git(repo, "commit", "-q", "-m", "t")
        assert r.returncode == 0, r.stdout[-300:] + r.stderr[-300:]
    # 空仓不 commit：git 对无文件仓库必然 rc=1，那是 git 的行为，不是判据的失败
    return repo


def main():
    if not TARGET.exists():
        ck("a1 红阶段前置：r35_tracked_empty.py 存在", False, "缺实现 ⇒ TDD 红阶段")
        print("[GATE:fixture-fail]")
        return 1
    m = load()
    ck("a1 judge() 与三态标记齐备", hasattr(m, "judge") and set(m.RC) == {"PASS", "FAIL", "UNVERIFIED"})

    # ---- 层 a：已知答案（真 git 仓，两侧对照）----
    ok_repo = make_repo({"a.md": "# 有内容\n", "b.py": "print(1)\n"})
    st, d = m.judge(ok_repo)
    ck("a2 正常仓 → PASS 且受检文本数==2", st == "PASS" and d["checked_text"] == 2, str(d)[:220])

    zero_repo = make_repo({"a.md": "# 有内容\n", "memory/AGENTS.md": "", "c.json": "{}\n"})
    st, d = m.judge(zero_repo)
    ck("a3 含 0 字节 tracked md → FAIL（**违规侧**，即 r34 事故形态）",
       st == "FAIL" and "memory/AGENTS.md" in d["zero_byte"], str(d["zero_byte"])[:200])

    # M4 的专属面必须是 **0 字节** 二进制：非空二进制在"跳过/不跳过"两种实现下结果相同，探针就没有鉴别力
    bin_repo = make_repo({"a.md": "x\n", "img.png": b"", "pkg.zip": b""})
    st, d = m.judge(bin_repo)
    ck("a4 0 字节**二进制**不误伤 → 仍 PASS 且计入 skipped（登记而非当作通过）",
       st == "PASS" and d["skipped_binary_or_unknown"] >= 1, str(d)[:220])

    empty_repo = make_repo({})
    st, d = m.judge(empty_repo)
    ck("a5 tracked 清单为空 → UNVERIFIED（无文件不等于通过，R247）",
       st == "UNVERIFIED" and "为空" in d["why"], str(d["why"])[:160])

    st, d = m.judge(tempfile.mkdtemp(prefix="r35_nogit_"))
    ck("a6 非 git 仓（取数失败）→ UNVERIFIED，不得当作「没有 0 字节文件」",
       st == "UNVERIFIED" and d.get("error"), str(d.get("why", ""))[:160])

    # tracked 但盘上缺失（模拟他人 rm 未提交）：不得崩，必须点名
    miss_repo = make_repo({"a.md": "x\n", "gone.md": "y\n"})
    os.remove(os.path.join(miss_repo, "gone.md"))
    st, d = m.judge(miss_repo)
    ck("a7 tracked 但盘上缺失 → 不崩且如实点名（不静默当不存在）",
       "gone.md" in d["missing_on_disk"], str(d["missing_on_disk"])[:160])

    # ---- 层 b：真机接线（本仓必须绿）----
    root = str(HERE.parent)
    p = subprocess.run([sys.executable, str(TARGET), "--root", root, "--json",
                        os.path.join(tempfile.gettempdir(), "r35_te.json")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    out = (p.stdout or "") + (p.stderr or "")
    ck("层b 本仓真跑 → rc=0 且 [EMPTY:PASS]", p.returncode == 0 and "[EMPTY:PASS]" in out, out[-200:])
    ck("层b 自证覆盖面（tracked 数 / 受检文本数 / 跳过数三行齐）",
       "tracked" in out and "受检文本" in out and "跳过" in out, out[-200:])

    # ---- 层 c：变异对照（每条绑专属输入面）----
    src = TARGET.read_text(encoding="utf-8")
    muts = [
        ("M1 0 字节判定反了（>0 才算空）→ 专属面=a3 含空 md 的仓",
         'if os.path.getsize(fp) == 0:', 'if os.path.getsize(fp) > 999999:'),
        ("M2 tracked 空清单当过 → 专属面=a5 空仓",
         'state, why = "UNVERIFIED", "tracked 清单为空', 'state, why = "PASS", "tracked 清单为空'),
        ("M3 文本面为 0 仍判过 → 专属面=无文本件的仓",
         'if not checked:', 'if False:'),
        # 注：M4 曾设为「把二进制当文本检」的误伤方向变异，但实现里二进制是**两级跳过**
        # （先 BIN_HINT、再未知扩展），单改一处行为不变 ⇒ 该变异**天然无鉴别力**，撤出变异集。
        # 误伤方向改由 a4 直接断言覆盖（0 字节二进制不误伤 + 计入 skipped 不静默），如实分工不硬凑 5/5。
        ("M5 git 取数失败当作「无违规」→ 专属面=a6 非 git 目录",
         'state, why = "UNVERIFIED", "取数失败', 'state, why = "PASS", "取数失败'),
    ]
    caught = 0
    for label, old, new in muts:
        if src.count(old) != 1:
            print("     %-56s 锚点命中 %d 次 ⇒ 夹具锚点需修（不计功）<<<" % (label, src.count(old)))
            continue
        mp = Path(tempfile.mkdtemp(prefix="r35_mut_")) / "mut.py"
        mp.write_text(src.replace(old, new, 1), encoding="utf-8")
        try:
            mm = load(mp)
        except Exception as e:
            print("     %-56s 变异体加载失败 ⇒ 不计功（修探针别修结论）: %s" % (label, type(e).__name__))
            continue
        reasons = []
        if label.startswith("M1") or label.startswith("M2") or label.startswith("M5"):
            # 违规侧/取数失败侧：变异后必须**不再**给出应有的红/UNVERIFIED
            if label.startswith("M1") and mm.judge(zero_repo)[0] == "FAIL":
                reasons.append("仍拦住空 md（变异未改变行为=探针无鉴别力）")
            if label.startswith("M2") and mm.judge(empty_repo)[0] == "UNVERIFIED":
                reasons.append("空仓仍判 UNVERIFIED（未改变）")
            if label.startswith("M5") and mm.judge(tempfile.mkdtemp(prefix="x_"))[0] == "UNVERIFIED":
                reasons.append("非 git 仍判 UNVERIFIED（未改变）")
        if label.startswith("M3"):
            r_repo = make_repo({"i.png": b"\x00"})
            if mm.judge(r_repo)[0] == "UNVERIFIED":
                reasons.append("文本面为 0 仍判 UNVERIFIED（未改变）")
        if label.startswith("M4"):
            if mm.judge(bin_repo)[0] == "PASS":
                reasons.append("0 字节图片仍判 PASS（未改变=此变异不影响 a4）")
        if reasons:
            print("     %-56s 未被有效拦住 <<< %s" % (label, "; ".join(reasons)))
        else:
            caught += 1
            print("     %-56s 拦住：变异后判据行为确有改变（专属面生效）" % label)
    ck("层c 变异 4 项全部被专属面拦住（M4 因需同时改两处、单点变异无鉴别力而撤出；误伤方向由 a4 覆盖）",
       caught == 4, "caught=%d/4" % caught)

    fails = [r for r in RESULTS if not r[0]]
    print("\n夹具合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    print("[GATE:fixture-pass]" if not fails else "[GATE:fixture-fail]")
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
