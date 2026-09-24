# -*- coding: utf-8 -*-
"""r19_scan_fixtures.py — 05-exec 对标类扫描工具的自带夹具（两层验证，R238）。

根因（r18 自查）：r18 一次性交付 4 个只读工具（catalog_attention_tax / rule_conflict_scan /
cumulative_drift_scan / skill_structure_rubric_scan），**全部没有判据夹具**——违反本体系
「新判据交付契约」（A-skill-manager governance.md：新判据必须带桩）。对标对象
mycelium-hq/ai-brain-starter 的 `check-rule-conflicts.py --self-test` 自带 6 例正反样本，
本轮把这一面补上。

层 a = 纯函数边界（已知答案，不碰真机）；层 b = 真机接线 + **对照组**
（生效路径应为 0 噪声，同时必须证明真规则文件仍被抓到——防「把判据放松成永真/永假」）。

用法：
    python 05-exec/r19_scan_fixtures.py            # 全部
    python 05-exec/r19_scan_fixtures.py --layer a  # 只跑纯函数层
退出码：0=全过 / 1=有失败 / 2=环境不满足（已 SKIP，不得当通过引用）
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PY = sys.executable

import _lib  # noqa: E402  (同目录共用库，必须先于下方用例)
import claim_truth_scan as claim  # noqa: E402
import cumulative_drift_scan as drift  # noqa: E402
import description_baseline_scan as desc  # noqa: E402
import rule_conflict_scan as conflict  # noqa: E402

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-58s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def layer_a():
    root = Path(tempfile.gettempdir()) / "r19_fixture_root"
    root.mkdir(exist_ok=True)

    # --- 1. drift: 按设计累积项排除（r19 D4 缺陷①）---
    check("drift.by_design: 自动拆卷 part 文件被排除",
          drift.is_by_design("memory/07-next-steps.part5.md", root))
    check("drift.by_design: 主卷 07 不排除（承重句载体）",
          not drift.is_by_design("memory/07-next-steps.md", root))
    check("drift.by_design: 日期日志被排除",
          drift.is_by_design("memory/2026-09-22.md", root))
    check("drift.by_design: 文件名中部带日期的人工报告不排除",
          not drift.is_by_design("deliverables/焚诀_全量代码与架构优化分析_2026-09-02_R207复评增量.md", root),
          "此例是 r19 实跑输出里暴露的过度排除缺陷（日期子串误伤）")
    check("drift.by_design: 归档/回收站路径被排除",
          drift.is_by_design("archive/one-shot-scripts-2026-09/B1.py", root)
          and drift.is_by_design("x/_trash/a.md", root))
    # --- 2. drift: ruleish 必须是 markdown（缺陷②）---
    check("drift.ruleish: 代码文件含 lessons 字样不再误判为规则类",
          not drift.is_ruleish("eval/decay_lessons.py"))
    check("drift.ruleish: SKILL.md 仍判规则类",
          drift.is_ruleish("A-project-handoff/SKILL.md"))
    check("drift.ruleish: prompts 规范 md 仍判规则类",
          drift.is_ruleish("prompts/workflow_seven_step.md"))
    check("drift.ruleish: 普通笔记 md 不判规则类",
          not drift.is_ruleish("notes.md"))
    # --- 3. drift: .driftignore 语义（缺陷③ 机制面）---
    ig = root / ".driftignore"
    ig.write_text("# comment\n\nmemory/keep-me.md\n", encoding="utf-8")
    pats = drift.load_driftignore(ig)
    check("drift.ignore: 注释与空行不成为模式", pats == ["memory/keep-me.md"], str(pats))
    check("drift.ignore: 子串命中生效", drift.matches_ignore("memory/keep-me.md", pats) == "memory/keep-me.md")
    check("drift.ignore: 未命中返回 None", drift.matches_ignore("memory/other.md", pats) is None)
    # --- 4. description: 流程入描述判据（r19 D1 对标 skill-anatomy 新增）---
    hit_arrow = "视频流水线——图生视频 → TTS 配音 → 字幕 → 合成导出。当用户要求成片时使用"
    hit_step = "部署技能。第一步登录，2）推送远端，3）验证。适用于超市项目上线"
    clean = "对 CSV 做统计汇总并输出透视表。当用户上传 Excel/CSV 并要求分析时使用"
    check("desc.process: 箭头链命中", bool(desc.PROCESS_RE.search(hit_arrow)))
    check("desc.process: 编号步骤命中", bool(desc.PROCESS_RE.search(hit_step)))
    check("desc.process: 「做什么+何时用」正当描述不误伤", not desc.PROCESS_RE.search(clean))
    # --- 5. description: 官方上限边界 ---
    check("desc.cap: 上限值为 1024（anthropics/agent-skills 官方口径）", desc.DESC_MAX == 1024)
    check("desc.cap: 1024 不越界 / 1025 越界",
          (len("x" * 1024) > desc.DESC_MAX) is False and (len("x" * 1025) > desc.DESC_MAX) is True)
    check("desc.cap: 触发词表仍认「当用户」", bool(desc.TRIGGER_RE.search(clean)))
    # --- 6. 分母三口径（r19 D3 P1-C）---
    reg = _lib.registry_denominator()
    check("lib.registry: 注册表清单可读且 count==len(skills)",
          reg.get("available") and reg.get("self_consistent"), json.dumps(reg, ensure_ascii=False)[:120])
    check("lib.registry: count>0（禁止 0 冒充空集）", (reg.get("count") or 0) > 0, str(reg.get("count")))
    d_ok = _lib.denominator(reg["count"] - 1 if reg.get("available") else 166,
                            ["rag-eval"] if reg.get("available") else [])
    check("lib.denom: glob 与注册表相等时判一致", d_ok["consistent"] is True, json.dumps(d_ok, ensure_ascii=False)[:160])
    d_bad = _lib.denominator(50, [])
    check("lib.denom: 人为少算时判不一致且给出 Δ",
          d_bad["consistent"] is False and d_bad["delta"] != 0, str(d_bad.get("delta")))
    d_missing = _lib.denominator(166, [], manifest_path=str(root / "nope.json"))
    check("lib.denom: 注册表不可读 → consistent=None（不得静默判过）",
          d_missing["consistent"] is None and d_missing["registry"]["available"] is False)
    lines = _lib.denominator_lines(d_missing)
    check("lib.denom: 不可用时仍输出可见行 + 取值命令", len(lines) >= 2 and any("取值命令" in x for x in lines))
    # --- 7. conflict: 极性互斥判据边界（r18 工具首次带桩）---
    pos = conflict.phrases("必须每次改动前先跑门禁复跑", conflict.POS_RE)
    neg = conflict.phrases("禁止跳过门禁复跑环节", conflict.NEG_RE)
    check("conflict.phrases: 必须侧抽取到宾语", bool(pos), str(pos))
    check("conflict.phrases: 禁止侧抽取到宾语", bool(neg), str(neg))
    term = conflict.longest_common_cjk(pos[0], neg[0]) if pos and neg else None
    check("conflict.term: 共用词 >= %d 字则成候选" % conflict.MIN_TERM,
          term is not None and len(term) >= conflict.MIN_TERM, str(term))
    check("conflict.term: 语义无关的两句不产生共用词",
          conflict.longest_common_cjk("必须保持文件编码为 UTF8 无 BOM", "禁止在中文路径使用波浪号") is None)
    check("conflict.declared: 自述冲突词命中", bool(conflict.DECLARED_RE.search("三处计数口径不一致，待统一")))
    check("conflict.declared: 正常句子不误命中",
          not conflict.DECLARED_RE.search("门禁三条全部通过，可以收尾"))
    # --- 8. claim_truth_scan：端数/枚举/豁免判据（r19 新工具首次带桩）---
    truth = {"active": ["wb", "tr", "cx", "hm", "zc", "oc", "qw", "qd"], "n": 8}
    check("claim.enum: 五端枚举命中", bool(claim.RE_ENUM.search("| 平台探测: <HM/WB/CX/TC/ZC> |")))
    check("claim.enum: 枚举缺 3 端 → 判失真",
          claim.norm_tokens("HM/WB/CX/TC/ZC") == ["HM", "WB", "CX", "TC", "ZC"]
          and set(truth["active"]) - {claim.LABEL_TO_CODE[t] for t in ["HM", "WB", "CX", "TC", "ZC"]}
          == {"oc", "qd", "qw"})
    check("claim.enum: 八端全枚举不失真",
          not (set(truth["active"]) - {claim.LABEL_TO_CODE[t] for t in
               claim.norm_tokens("HM/WB/CX/TC/ZC/OC/QW/QD")}))
    check("claim.count: 「五端」解析为 5 且 != 真值 8",
          claim.RE_NDUAN.search("## File Resolution（五端统一）").group(1) == "五"
          and claim.CN_NUM["五"] != truth["n"])
    check("claim.retire: 声称退役的代号仍在 active 集 → 命中",
          claim.RE_RETIRE.search("OC 已退役 2026-09-21 用户确认").group(1).lower() in truth["active"])
    check("claim.exempt: 历史留痕行豁免（R241 只加注不改写）",
          claim.classify_line("【2026-09-23 注：原文保留不改，因其在当时为真】五端") is None)
    check("claim.exempt: 版本历史章节行豁免",
          claim.classify_line("V10.65.0 (2026-09-22): 权威端由四端扩为五端") is None)
    check("claim.skill: 裸「151 技能」命中且与真值不等",
          bool(claim.RE_SKILLCOUNT.search("基数 151 条 = 磁盘实测")) and
          claim.RE_SKILLCOUNT.search("151 skills").group(1) == "151")
    check("claim.skill: 三位以下数字不误伤",
          not claim.RE_SKILLCOUNT.search("8 条 AC / 9 个记忆节"))


def run_tool(script, extra):
    cmd = [PY, str(HERE / script)] + extra
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    return p


def layer_b():
    tmp = Path(tempfile.mkdtemp(prefix="r19_layer_b_"))
    j_excl = tmp / "drift_excl.json"
    j_ctrl = tmp / "drift_ctrl.json"

    p = run_tool("cumulative_drift_scan.py",
                 ["--days", "30", "--threshold", "5", "--json", str(j_excl)])
    if p.returncode not in (0, 1) or not j_excl.exists():
        check("layerb: drift 扫描可跑", False, (p.stderr or p.stdout)[-200:])
        return
    excl = json.loads(j_excl.read_text(encoding="utf-8"))
    p2 = run_tool("cumulative_drift_scan.py",
                  ["--days", "30", "--threshold", "5", "--no-exclude", "--json", str(j_ctrl)])
    ctrl = json.loads(j_ctrl.read_text(encoding="utf-8")) if j_ctrl.exists() else {}

    def ruleish_paths(doc):
        return {r["path"] for r in doc.get("flagged_ruleish", [])}

    ex, ct = ruleish_paths(excl), ruleish_paths(ctrl)
    check("layerb 生效路径: 自动拆卷件不再进复核清单",
          not any("part" in x for x in ex), str(sorted(x for x in ex if "part" in x)))
    check("layerb 对照组(真规则仍被抓): 07 主卷在列",
          "memory/07-next-steps.md" in ex, str(sorted(ex)))
    check("layerb 对照组(未放松): SKILL.md 类真技能文件在列",
          any(x.endswith("SKILL.md") for x in ex))
    check("layerb 机制而非数据: --no-exclude 时 part 件回到清单",
          any("part" in x for x in ct), str(sorted(x for x in ct if "part" in x)))
    check("layerb 排除可见留痕: excluded 非空且带原因",
          bool(excl.get("excluded")) and all(e.get("why") for e in excl["excluded"]),
          str(len(excl.get("excluded", []))))
    check("layerb 输入非空: 四根合计提交 > 0（R247）",
          excl["evidence"]["total_commits"] > 0)
    check("layerb schema 升 v2", excl.get("schema") == "cumulative-drift-scan-v2", excl.get("schema"))

    jd = tmp / "desc.json"
    p3 = run_tool("description_baseline_scan.py", ["--json", str(jd)])
    if not jd.exists():
        check("layerb: description 扫描可跑", False, (p3.stderr or p3.stdout)[-200:])
    else:
        dd = json.loads(jd.read_text(encoding="utf-8"))
        s = dd["summary"]
        check("layerb 新增键落地", "has_process" in s and "over_cap" in s, json.dumps(s)[:120])
        check("layerb 分母落地且可用",
              dd.get("denominator", {}).get("registry", {}).get("available") is True)
        check("layerb 双要素数 ≤ 总数", 0 <= s["double_element"] <= s["total"], json.dumps(s)[:120])
        check("layerb 流程入描述命中数在 0..total 且 > 0（本库实况有此类）",
              0 < s["has_process"] <= s["total"], str(s["has_process"]))

    jc = tmp / "claim.json"
    p4 = run_tool("claim_truth_scan.py", ["--json", str(jc)])
    if not jc.exists():
        check("layerb: claim 对账扫描可跑", False, (p4.stderr or p4.stdout)[-200:])
    else:
        cc = json.loads(jc.read_text(encoding="utf-8"))
        check("layerb claim 真相源可用（8 端 + 注册表计数）",
              cc["truth"]["n"] == len(cc["truth"]["active"]) > 4 and cc["registry_count"],
              json.dumps({"n": cc["truth"]["n"], "rc": cc["registry_count"]}, ensure_ascii=False))
        check("layerb claim 抓到真实失真族（本库实况：注入文本仍写五端/四端）",
              any(x["family"].startswith("endpoint") for x in cc["candidates"]),
              str(len(cc["candidates"])))
        check("layerb claim 退出码与候选数一致（有候选=1，禁静默 0）",
              (p4.returncode == 1) == bool(cc["candidates"]), "rc=%s n=%s" % (p4.returncode, len(cc["candidates"])))
        check("layerb claim 受检面非空（R247）", len(cc["targets_present"]) >= 5, str(len(cc["targets_present"])))
        check("layerb claim 无未读数错误",
              not any(x.get("family") == "unreadable" for x in cc["candidates"]))


def main():
    if _lib is not None:
        _lib.force_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", choices=["a", "b", "all"], default="all")
    args = ap.parse_args()

    if not (HERE / "cumulative_drift_scan.py").exists():
        print("SKIP: 夹具依赖的 05-exec 工具不在位（exit 2）")
        return 2
    print("=== 层 a：纯函数已知答案 ===")
    layer_a()
    if args.layer in ("b", "all"):
        print("\n=== 层 b：真机接线 + 对照组（R238）===")
        layer_b()
    fails = [r for r in RESULTS if not r[0]]
    print("\n夹具合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    if fails:
        print("[GATE:fixture-fail]")
        for ok, name, detail in fails:
            print("  FAIL %s | %s" % (name, detail))
        return 1
    print("[GATE:fixture-pass]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
