# -*- coding: utf-8 -*-
"""r34_onwrite_fixtures.py — `rule_conflict_scan.py --on-write`（写时冲突检查）的夹具 + 变异对照。

对标实物（`06-benchmark/ci_evidence/mycelium_*.yml` 与 r19 报告 §②）：
  mycelium 有两支脚本 —— `check-rule-conflicts.py`（批量事后）与 **`check-rule-conflicts-on-write.py`（写时）**；
  本仓 r18 只落了前者，写时模式自 r19 起挂账，至 r34 共**四轮未做**。
  差别不是"快一点"，而是**发现时点**：批量模式在改动已入库后出候选清单等人工裁，
  写时模式在**落盘前**就把「新写的规则与权威源互斥」顶到脸上 —— 后者才挡得住"写进去才发现"。

三条硬判据（A-get-memory Step2.7 V4.30.0）：① 先看红 ② 变异/反例对照 ③ 挂执行路径。
被测对象：`05-exec/rule_conflict_scan.py`（`--on-write` 分支）+ `on_write_check()` 函数
退出码：0 全过 / 1 有失败
"""

import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "rule_conflict_scan.py"
sys.path.insert(0, str(HERE))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RESULTS = []
AUTH = """# 权威源（夹具用）
- 必须在提交前逐文件核对暂存区内容。
- 禁止对散落文件做删除操作。
"""
CAND_CONFLICT = """# 待写入的候选文件
- 必须直接删除散落文件以让门禁转绿。
"""
CAND_CLEAN = """# 待写入的候选文件
- 提交前应当逐文件核对暂存区内容，禁止使用 `git add -A`。
"""


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-64s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load():
    spec = importlib.util.spec_from_file_location("rcs_onwrite", str(TARGET))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def write(path, text):
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)
    return path


def main():
    if not TARGET.exists():
        ck("前置：rule_conflict_scan.py 存在", False, "缺实现 ⇒ 红阶段")
        print("[GATE:fixture-fail]")
        return 1
    m = load()
    if not hasattr(m, "on_write_check"):
        ck("a1 红阶段：on_write_check() 已实现（写时模式入口）", False,
           "函数不存在 ⇒ 本轮运行即为 TDD 红阶段（先看失败，再写实现）")
        print("\n夹具合计: %d 项，通过 0，失败 %d" % (len(RESULTS), len(RESULTS)))
        print("[GATE:fixture-fail]")
        return 1
    ck("a1 on_write_check() 存在且可调用", callable(m.on_write_check))

    tmp = Path(tempfile.mkdtemp(prefix="r34_onwrite_"))
    auth = write(tmp / "auth.md", AUTH)
    bad = write(tmp / "cand_bad.md", CAND_CONFLICT)
    good = write(tmp / "cand_good.md", CAND_CLEAN)
    empty = write(tmp / "cand_empty.md", "")
    nowords = write(tmp / "cand_nowords.md", "纯叙述文本，不含规范性动词。")
    missing = tmp / "nope.md"

    # ---- 层 a：已知答案 ----
    r_bad = m.on_write_check(bad, [auth])
    ck("a2 候选与权威源互斥（允许删除 vs 禁止删除）→ 判冲突且非零",
       r_bad["state"] == "CONFLICT" and len(r_bad["pairs"]) >= 1, json.dumps(r_bad, ensure_ascii=False)[:260])
    ck("a3 冲突项必须两侧定位（权威侧 + 候选侧的行位置都在）",
       all((":" in p["must"]["loc"] and ":" in p["forbid"]["loc"]) for p in r_bad["pairs"]),
       str(r_bad["pairs"][:1])[:260])
    ck("a4 冲突项必须标出候选文件自身（写时报错要指到「正在写的这个文件」）",
       any(os.path.basename(bad) in (p["must"]["loc"] + p["forbid"]["loc"]) for p in r_bad["pairs"]),
       str([p["must"]["loc"] for p in r_bad["pairs"]])[:200])

    r_good = m.on_write_check(good, [auth])
    ck("a5 合规候选（禁 add -A，与权威源同向）→ CLEAN",
       r_good["state"] == "CLEAN", json.dumps(r_good, ensure_ascii=False)[:240])

    r_empty = m.on_write_check(empty, [auth])
    ck("a6 候选为空 → UNVERIFIED 不得判 CLEAN（R247：空输入面不是「没有冲突」）",
       r_empty["state"] == "UNVERIFIED", json.dumps(r_empty, ensure_ascii=False)[:240])

    r_miss = m.on_write_check(str(missing), [auth])
    ck("a7 候选不存在 → UNVERIFIED（禁止把「读不到」当「没有冲突」）",
       r_miss["state"] == "UNVERIFIED", json.dumps(r_miss, ensure_ascii=False)[:240])

    r_noauth = m.on_write_check(bad, [tmp / "auth_missing.md"])
    ck("a8 权威源不可读 → UNVERIFIED 且**不得**输出 CLEAN（假绿最危险形态）",
       r_noauth["state"] == "UNVERIFIED", json.dumps(r_noauth, ensure_ascii=False)[:240])

    # ---- 层 a：自证覆盖面 ----
    ck("a9 结果必须自证覆盖根（候选 + 权威清单 + 规则条数）",
       r_bad["candidate"] == str(bad) and isinstance(r_bad["authority_files"], list)
       and r_bad["rules_candidate"] >= 1 and r_bad["rules_authority"] >= 1,
       json.dumps({k: r_bad[k] for k in ("authority_files", "rules_candidate", "rules_authority")
                   if k in r_bad}, ensure_ascii=False)[:240])
    ck("a10 权威侧规则数为 0 时不得判 CLEAN（覆盖为空即无鉴别力）",
       m.on_write_check(good, [write(tmp / "auth_empty.md", "纯叙述文本，不含规范性动词。")])["state"] == "UNVERIFIED")

    # ---- 层 b：真机接线（CLI 三态与退出码）----
    def run(args):
        p = subprocess.run([sys.executable, str(TARGET)] + args, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=300)
        return p.returncode, (p.stdout or "") + (p.stderr or "")

    rc, out = run(["--on-write", str(bad), "--against", str(auth)])
    ck("层b CLI 冲突侧 → rc=1 且打印 [ONWRITE:CONFLICT]", rc == 1 and "[ONWRITE:CONFLICT]" in out,
       "rc=%s %s" % (rc, out[-220:]))
    rc2, out2 = run(["--on-write", str(good), "--against", str(auth)])
    ck("层b CLI 合规侧 → rc=0 且打印 [ONWRITE:CLEAN]", rc2 == 0 and "[ONWRITE:CLEAN]" in out2,
       "rc=%s %s" % (rc2, out2[-220:]))
    rc3, out3 = run(["--on-write", str(empty), "--against", str(auth)])
    ck("层b CLI 空候选 → rc=2 且打印 [ONWRITE:UNVERIFIED]", rc3 == 2 and "[ONWRITE:UNVERIFIED]" in out3,
       "rc=%s %s" % (rc3, out3[-220:]))
    ck("层b 三态退出码互不相同（0/1/2）——防「任何非零都算冲突」的粗判",
       len({rc, rc2, rc3}) == 3, "%s/%s/%s" % (rc, rc2, rc3))
    ck("层b 输出自证覆盖根（候选/权威/规则数三行齐）",
       all(k in out for k in ("候选:", "权威:", "规则:")), out[-260:])

    # ---- 层 c：变异对照（判据必须有牙）----
    src = TARGET.read_text(encoding="utf-8")
    muts = [
        ("M1 权威面为空时静默判 CLEAN（假绿）",
         src.replace('if not auth_rules:', 'if False:')),
        ("M2 候选为空时静默判 CLEAN（R247 失守）",
         src.replace('if not cand_rules:', 'if False:')),
        ("M3 配对只查「权威 vs 权威」，候选不参与（等于永远查不到新写的冲突）",
         src.replace("pairs = [p for p in pairs if cand_name in", "pairs = [p for p in pairs if cand_name not in")),
        ("M4 冲突仍返回 0（拦不住落盘）",
         src.replace('return 1 if res["state"] == "CONFLICT"', 'return 0 if res["state"] == "CONFLICT"')),
    ]
    caught = 0
    for label, patched in muts:
        n_hit = 0
        for probe in ('if not auth_rules:', 'if not cand_rules:',
                      'pairs = [p for p in pairs if cand_name in', 'return 1 if res["state"] == "CONFLICT"'):
            n_hit = max(n_hit, src.count(probe))
        if patched == src:
            print("     %-52s 锚点未命中 ⇒ 夹具锚点需修（不得当作已拦住）<<<" % label)
            continue
        mp = tmp / ("mut_%d.py" % (abs(hash(label)) % 10**8))
        mp.write_text(patched, encoding="utf-8")
        try:
            spec2 = importlib.util.spec_from_file_location("mut_%d" % (abs(hash(label)) % 10**6), str(mp))
            mm = importlib.util.module_from_spec(spec2)
            spec2.loader.exec_module(mm)      # 注：不可用 except 把"加载失败"算作拦住——那是探针自身失效
        except Exception as e:
            print("     %-52s 变异体加载失败 ⇒ 该例不计功（修探针，别修结论）: %s" % (label, type(e).__name__))
            continue
        bad_reasons = []
        if not hasattr(mm, "on_write_check"):
            bad_reasons.append("函数被改坏")
        else:
            if mm.on_write_check(str(good), [str(tmp / "auth_none.md")])["state"] != "UNVERIFIED":
                bad_reasons.append("权威面缺失未判 UNVERIFIED")
            if mm.on_write_check(str(empty), [str(auth)])["state"] != "UNVERIFIED":
                bad_reasons.append("候选空未判 UNVERIFIED")
            rb = mm.on_write_check(str(bad), [str(auth)])
            if rb["state"] != "CONFLICT":
                bad_reasons.append("真冲突未判 CONFLICT")
            # M2 专属反例：文件有内容但**无极性词**（空文件走的是 c_empty 分支，测不到 cand_rules 那条）
            if mm.on_write_check(str(nowords), [str(auth)])["state"] != "UNVERIFIED":
                bad_reasons.append("候选无极性句未判 UNVERIFIED")
            # M4 专属反例：M4 只改 CLI 退出码，函数级断言永远测不到 ⇒ 必须真起进程
            r4 = subprocess.run([sys.executable, str(mp), "--on-write", str(bad), "--against", str(auth)],
                                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
            if r4.returncode != 1:
                bad_reasons.append("CLI 冲突侧 rc=%s（拦不住落盘）" % r4.returncode)
        if bad_reasons:
            caught += 1
            print("     %-52s 拦住：%s" % (label, "; ".join(bad_reasons)))
        else:
            print("     %-52s 未被拦住 <<<" % label)
    ck("层c 变异 4 项全部被**有效断言**拦住（加载失败不计功）", caught == 4, "caught=%d/4" % caught)

    # ---- 层 d：挂进执行路径 ----
    ag = (HERE.parent / "memory" / "AGENTS.md")
    txt = ag.read_text(encoding="utf-8") if ag.exists() else ""
    ck("层d --on-write 已写进项目门禁说明（否则又是一条只写不跑的判据）",
       "--on-write" in txt, "memory/AGENTS.md 未引用")

    fails = [r for r in RESULTS if not r[0]]
    print("\n夹具合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    if fails:
        print("[GATE:fixture-fail]")
        for _ok, name, detail in fails:
            print("  FAIL %s | %s" % (name, detail))
        return 1
    print("[GATE:fixture-pass]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
