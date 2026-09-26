# -*- coding: utf-8 -*-
"""r58 W-46 取值件生成器：契约 pattern 的「有没有生成器」覆盖率实测。

存在理由：r56 连踩两份死句柄（裁定依据件在仓里没有生成器），W-46 要求把它做成机器判据。
按「新判据先量误报率」，本件先只**测量并交清单**，不接线判红。

三路取数（单路必误判，与 r51/r52 两路对账同族）：
  路 A 字面量路：脚本源码的 ast 字符串常量能被 glob 直接匹配该 pattern；
  路 B 词干路：pattern 首个 `*` 前的最长字面词干出现在任一字符串常量里
     —— 捕捉 `"debt_aging_r%d_%s.json" % (...)` 这类**拼接出的**文件名（只走路 A 会把真生成器误判成死句柄）；
  路 C 同名工具路：脚本名以 pattern 词干开头（`rule_conflict_scan.py` → `rule_conflict_scan_*.json`）
     —— 捕捉「输出文件名由 `--json <path>` 传入、源码里根本没有该字面量」的工具（r58 实测 A/B 口径的
        3 条死句柄指控里有 2 条是这种假阴性，故必须补这一路）。
分档（三档互斥，求和必须 == pattern 总数，否则 [GENCOV:BREAKDOWN-DRIFT] 退出 1）：
  COVERED      有非夹具脚本命中且含写盘痕迹
  DEAD_HANDLE  06-benchmark 里有该 pattern 的件，却没有任何非夹具生成器
  NO_ARTIFACT  一件都不存在（契约在册但产物未落，另案，不算死句柄）
夹具（文件名含 fixture/stub）单独记 `fixture_refs`：它们引用件名是为了自证，不是生产者；
把它们算进生成器 = 本判据最主要的误报形态，故显式剔除而不是靠人眼挑。
"""
import ast
import datetime
import fnmatch
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRACT = os.path.join(ROOT, "05-exec", "schemas", "r19", "baseline-contracts.json")
BENCH = os.path.join(ROOT, "06-benchmark")
SCRIPTS = os.path.join(ROOT, "05-exec")
SELF = os.path.basename(__file__)

WRITE_RX = re.compile(r"json\.dump|\bopen\([^)]{0,80}[\"'][wa][+b]?\b|--json|newline\s*=")
FIXTURE_RX = re.compile(r"fixture|stub|_check\b", re.I)
# 外部只读依赖根（项目红线：焚诀 eval/ 与 audit/ 只读调用不改）。
# 不探这一层就会把「生成器在受管根外」误判成本仓死句柄 —— r58 实测 attention_sim_raw_*.json 即此形态。
EXTERNAL_ROOTS = [("C:/Users/37533/Desktop/workspace/焚诀/audit", "焚诀/audit（只读外部依赖）"),
                  ("D:/global_skills", "受管根 global_skills（只读）")]


def string_constants(path):
    """ast 取字面量；语法错即上报（宁可记 UNVERIFIED，不许静默少一面）。"""
    with io.open(path, encoding="utf-8", errors="replace") as f:
        tree = ast.parse(f.read(), filename=path)
    return [n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def stem(pattern):
    """pattern 首个通配符前的字面词干；无通配符则整个 pattern。"""
    return pattern.split("*")[0] or pattern


def main():
    argv = sys.argv[1:]
    out_json = argv[argv.index("--json") + 1] if "--json" in argv else None

    with io.open(CONTRACT, encoding="utf-8") as f:
        contract = json.load(f)
    patterns = sorted(contract.get("artifacts", {}).keys())
    if not patterns:
        print("[GENCOV:UNVERIFIED] 契约 artifacts 面为空 ⇒ 无处可比，不得判过（R247）")
        return 2

    corpus = {}
    unparsed = []
    for path in sorted(glob.glob(os.path.join(SCRIPTS, "*.py"))):
        name = os.path.basename(path)
        if name == SELF:
            continue
        try:
            src = io.open(path, encoding="utf-8", errors="replace").read()
        except OSError as e:
            unparsed.append("%s(%s)" % (name, e.__class__.__name__))
            continue
        try:
            corpus[name] = (string_constants(path), src)
        except SyntaxError as e:
            unparsed.append("%s(SyntaxError:%s)" % (name, e.lineno))

    ext_index = []
    for root, label in EXTERNAL_ROOTS:
        for p in glob.glob(os.path.join(root, "**", "*.py"), recursive=True):
            if os.sep + ".git" + os.sep in p:
                continue
            ext_index.append((label, os.path.basename(p)))

    rows = []
    for pat in patterns:
        artifacts = sorted(os.path.basename(p) for p in glob.glob(os.path.join(BENCH, pat)))
        st = stem(pat)
        tokens = [t for t in re.split(r"[^a-z]+", st.lower()) if len(t) >= 5]
        loose, strict_writers, fixtures, readers = [], [], [], []
        ext_tokens = [t for t in re.split(r"[^a-z]+", st.lower()) if len(t) >= 3]
        # 必须**全部** token 命中：首跑用 any() 时 `noise_falsepositive_*` 因单词「noise」撞上
        # `A-project-handoff/scripts/noise_lint.py` 而被误记成『外部有生成器』—— 该件全库 grep
        # `falsepositive` 零命中，是真死句柄。all() 后复正（判据假通过，比假失败更坏）。
        external = ["%s/%s" % (lbl, b) for lbl, b in ext_index
                    if ext_tokens and all(t in b.lower() for t in ext_tokens)]
        for name, (lits, src) in sorted(corpus.items()):
            hit_a = any(fnmatch.fnmatch(l, pat) for l in lits)
            # 路 B 收紧：字面量须同时含词干与扩展名，否则 `"description"` 这类**字典键**会被当成文件名
            hit_b = any(st and st in l and (".json" in l or ".jsonl" in l) for l in lits)
            # 路 C 同名工具路：`rule_conflict_scan.py` 写出 `rule_conflict_scan_*.json` 时，输出文件名
            # 往往由 `--json <path>` 传入、源码里没有该字面量 ⇒ 只走 A/B 会把**真生成器**误判成死句柄。
            # r58 实测：A/B 口径给出的 3 条「死句柄」里有 2 条正是这种假阴性。
            hit_c = bool(st) and name[:-3].startswith(st.rstrip("_"))
            if not (hit_a or hit_b or hit_c):
                continue
            loose.append(name)
            if FIXTURE_RX.search(name):
                fixtures.append(name)
            elif WRITE_RX.search(src):
                strict_writers.append(name)
            else:
                readers.append(name)
        if unparsed:
            verdict = "UNVERIFIED"
        elif strict_writers:
            verdict = "COVERED"
        elif artifacts and external:
            verdict = "EXTERNAL_CANDIDATE"
        elif artifacts:
            verdict = "DEAD_HANDLE"
        else:
            verdict = "NO_ARTIFACT"
        rows.append({"pattern": pat, "stem": st, "artifact_count": len(artifacts),
                     "generator_scripts": sorted(set(strict_writers)),
                     "external_generator_candidates": sorted(set(external)),
                     "loose_refs": sorted(set(loose)),
                     "over_count_divergence": len(set(loose)) - len(set(strict_writers)),
                     "fixture_refs": sorted(set(fixtures)),
                     "read_only_refs": sorted(set(readers)),
                     "verdict": verdict})
        print("  %-32s 件=%-4d 严格生成器=%-2d 宽口径=%-2d 夹具=%-2d %-20s %s" % (
            pat, len(artifacts), len(set(strict_writers)), len(set(loose)), len(set(fixtures)), verdict,
            ", ".join(sorted(set(strict_writers))[:3]) or ", ".join(sorted(set(external))[:1]) or "（无）"))

    tally = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    sum_ok = sum(tally.values()) == len(patterns)
    print("-" * 66)
    if not sum_ok:
        print("[GENCOV:BREAKDOWN-DRIFT] 分档求和 %d != pattern 总数 %d ⇒ 枚举器漏项，本件不可引用"
              % (sum(tally.values()), len(patterns)))
        return 1
    print("pattern 总数=%d ｜ COVERED=%d ｜ EXTERNAL_CANDIDATE=%d ｜ DEAD_HANDLE=%d ｜ NO_ARTIFACT=%d ｜ UNVERIFIED=%d" % (
        len(patterns), tally.get("COVERED", 0), tally.get("EXTERNAL_CANDIDATE", 0),
        tally.get("DEAD_HANDLE", 0), tally.get("NO_ARTIFACT", 0), tally.get("UNVERIFIED", 0)))
    loose_hits = sum(len(r["loose_refs"]) for r in rows)
    strict_hits = sum(len(r["generator_scripts"]) for r in rows)
    fp_rate = (100.0 * (loose_hits - strict_hits) / loose_hits) if loose_hits else 0.0
    print("误报率实测：宽口径命中 %d 处，严格口径 %d 处 ⇒ 若按宽口径接线，%d 处（%.1f%%）会被误记为『有生成器』"
          % (loose_hits, strict_hits, loose_hits - strict_hits, fp_rate))
    dead = [r["pattern"] for r in rows if r["verdict"] == "DEAD_HANDLE"]
    if dead:
        print("死句柄清单（有件无生成器）: %s" % ", ".join(dead))
    if unparsed:
        print("⚠️ 解析失败脚本（不得当作『无生成器』）: %s" % ", ".join(unparsed))
    print("[GENCOV:%s] 接线判据：%s" % ("READY" if not dead and not unparsed else "HOLD",
                                        "零命中清单为空 ⇒ 可接线判红" if not dead and not unparsed
                                        else "非空 ⇒ 先补生成器/先修解析，禁带已知误报上线"))

    doc = {"schema": "generator-coverage-v1",
           "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "readonly": True,
           "source_contract": "05-exec/schemas/r19/baseline-contracts.json",
           "enumerator": "05-exec/r58_generator_coverage.py::main（ast 字面量三路 A 字面/B 词干+扩展/C 同名工具 + WRITE_RX + 夹具剔除）",
           "patterns": rows,
           "by_verdict": tally,
           "cross_check": {"pattern_total": len(patterns), "tally_sum": sum(tally.values()),
                           "sum_ok": sum_ok,
                           "loose_hits": loose_hits, "strict_hits": strict_hits,
                           "false_positive_pct": round(fp_rate, 1)},
           "dead_handles": dead,
           "unreadable_scripts": unparsed,
           "claims_face": "本仓 05-exec/*.py 的 ast 字符串常量面（A 字面量 + B 词干 + C 同名工具 三路）与 06-benchmark 文件名面；不含受管根、不含夹具脚本",
           "retrieval": [
               "python 05-exec/r58_generator_coverage.py --json 06-benchmark/generator_coverage_r58_2026-09-26.json",
               "python 05-exec/baseline_contract_scan.py --quiet  (其『pattern 16 个』计数须等于本件 cross_check.pattern_total)"],
           "decision_needed": ["W-46：dead_handles 清空后是否把『pattern 必须有生成器』接进 run_gates 判红"]}
    if out_json:
        with io.open(out_json, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print("写出 %s" % out_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
