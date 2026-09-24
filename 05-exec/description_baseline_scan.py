# -*- coding: utf-8 -*-
"""description_baseline_scan.py — P1-1 description 双要素基线扫描（只读取证，对标 anthropics/skills 官方口径）。

口径（anthropics/skills 官方）：frontmatter 必填字段 = name + description；
description 是平台触发技能的第一信号，应同时含「做什么 + 何时用」双要素。

机器判定（本脚本口径，⚠️ 启发式非语义判定）：
  · 做什么 —— description 非空且 ≥15 字符
  · 何时用 —— 命中触发标记词表（中英）：触发/适用/用于/当用户/何时/使用场景/场景：/不适用/
               use when/use this/when the user/when working/triggers?/for .* tasks 等
  · 超上限 —— 长度 > 1,024 字符（anthropics / addyosmani 官方硬上限，r19 D1 实物核验补）
  · 流程入描述 —— description 里塞编号步骤/箭头链（r19 D1 对标 addyosmani/agent-skills
               docs/skill-anatomy.md：「不要在 description 里概述流程，否则 agent 会照着
               摘要做而不去读技能正文」——本体系此前无此项判据）

输出：stdout 摘要 + --json <path>（机器可读全量）+ --md <path>（基线报告）。
只读：不写 D:\\global_skills 任何文件。默认 dry-run 语义（无 --apply）。
分母口径（r19 P1-C）：三口径并排打印（纳入 / 磁盘 glob / 焚诀注册表），见 `_lib.denominator`。
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import _lib
except Exception:  # pragma: no cover - 保持脚本可独立运行
    _lib = None

GS_ROOT = Path(r"D:\global_skills")
TRIGGER_RE = re.compile(
    r"触发|适用|用于|何时|使用场景|场景[：:]|不适用|当用户|需要(做|进行|生成|分析|创建|查)|"
    r"use\s+when|use\s+this|when\s+(the\s+)?user|when\s+working|triggers?\b|for\s+\S+\s+(tasks?|work)",
    re.IGNORECASE,
)
MIN_DO_LEN = 15  # 「做什么」最小长度（字符）
DESC_MAX = 1024  # 官方硬上限（超过即告警；不阻断，判定权在人）
PROCESS_RE = re.compile(
    r"(第[一二三四五六七八九十0-9]+\s*步|[①②③④⑤⑥]|[1-9][)）、.]\s*\S|[1-9]-[a-z]:|"
    r"\s→\s.*\s→\s|步骤[:：]|流程[:：]|先.+(再|然后).+(最后|再)|pipeline|Phase\s*\d)",
)


def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None, None
    fm = m.group(1)
    lines = fm.splitlines()
    name = description = None

    def _scalar(v):
        return v.strip().strip("'\"")

    for i, ln in enumerate(lines):
        nm = re.match(r"^name:\s*(.+)$", ln)
        if nm and name is None:
            name = _scalar(nm.group(1))
            continue
        dm = re.match(r"^description:\s*(.*)$", ln)
        if dm and description is None:
            inline = dm.group(1).strip()
            # 收集后续缩进行（块标量 |/> 或「内联 + 缩进续行」混合形态，2026-09-24 r17b 实测均有）
            buf = []
            for sub in lines[i + 1:]:
                if not sub.strip() or re.match(r"^\s", sub):
                    buf.append(sub.strip())
                else:
                    break
            cont = " ".join(buf).strip()
            if inline in ("|", "|-", "|+", ">", ">-", ">+"):
                description = cont or None
            else:
                description = (_scalar(inline) + (" " + cont if cont else "")).strip() or None
    return name, description


def is_reparse_dir(p: Path) -> bool:
    """junction/符号链接判位（rag-eval@ 等并行新增项计入口径会虚增总数）。"""
    try:
        return p.stat(follow_symlinks=False).st_file_attributes & 0x400 != 0
    except (OSError, AttributeError):
        return False


def scan():
    skills = []
    junctions = []
    for md in sorted(GS_ROOT.glob("*/SKILL.md")):
        if is_reparse_dir(md.parent):
            junctions.append(md.parent.name)
            continue
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            skills.append({"skill": md.parent.name, "path": str(md), "error": str(e)})
            continue
        name, desc = parse_frontmatter(text)
        if desc is None:
            skills.append({"skill": md.parent.name, "path": str(md), "name": name,
                           "desc": None, "desc_len": 0, "has_trigger": False,
                           "double_element": False})
            continue
        has_trigger = bool(TRIGGER_RE.search(desc))
        skills.append({
            "skill": md.parent.name, "path": str(md), "name": name, "desc": desc,
            "desc_len": len(desc), "has_trigger": has_trigger,
            "double_element": has_trigger and len(desc) >= MIN_DO_LEN,
            "over_cap": len(desc) > DESC_MAX,
            "has_process": bool(PROCESS_RE.search(desc)),
        })
    return skills, junctions


def summarize(skills, junctions):
    total = len(skills)
    errs = [s for s in skills if s.get("error")]
    no_desc = [s for s in skills if not s.get("error") and not s.get("desc")]
    has_desc = [s for s in skills if s.get("desc")]
    with_trigger = [s for s in has_desc if s["has_trigger"]]
    double = [s for s in has_desc if s["double_element"]]
    over_cap = [s for s in has_desc if s["over_cap"]]
    process = [s for s in has_desc if s["has_process"]]
    lens = sorted(s["desc_len"] for s in has_desc)
    shortest = sorted(has_desc, key=lambda s: s["desc_len"])[:10]
    no_trigger = sorted((s for s in has_desc if not s["has_trigger"]),
                        key=lambda s: s["desc_len"])
    return {
        "total": total, "errors": len(errs), "no_desc": len(no_desc),
        "has_desc": len(has_desc), "with_trigger": len(with_trigger),
        "double_element": len(double),
        "over_cap": len(over_cap), "has_process": len(process),
        "len_min": lens[0] if lens else 0, "len_max": lens[-1] if lens else 0,
        "len_median": lens[len(lens) // 2] if lens else 0,
        "junctions_excluded": junctions,
        "shortest": shortest, "no_trigger": no_trigger,
        "over_cap_list": over_cap, "process_list": process,
    }


def main():
    ap = argparse.ArgumentParser(description="description 双要素基线扫描（只读）")
    ap.add_argument("--json", help="全量结果 JSON 输出路径")
    ap.add_argument("--md", help="基线报告 Markdown 输出路径")
    args = ap.parse_args()

    skills, junctions = scan()
    s = summarize(skills, junctions)
    denom = (_lib.denominator(s["total"], junctions, []) if _lib
             else {"scanned": s["total"], "glob_total": s["total"], "registry": {"available": False,
                     "error": "_lib 不可用"}, "registry_cmd": "-", "junction_skipped": junctions,
                     "parse_errors": 0})
    print("=== description 双要素基线（{0}，对标 anthropics 官方口径） ===".format(
        datetime.now().strftime("%Y-%m-%d %H:%M")))
    for ln in (_lib.denominator_lines(denom) if _lib else ["口径对账: _lib 不可用"]):
        print(ln)
    print("SKILL.md 总数: {total}  解析错误: {errors}  无/空 description: {no_desc}".format(**s))
    print("有 description: {has_desc}  含触发标记: {with_trigger}  双要素达标: {double_element}".format(**s))
    print("长度分布: min={len_min} / median={len_median} / max={len_max}  官方上限 {0} 超限: {over_cap}".format(
        DESC_MAX, **s))
    print("流程入描述（anti-pattern，对标 agent-skills skill-anatomy）: {has_process}".format(**s))
    print("\n最短 Top10（优先整改候选）:")
    for x in s["shortest"]:
        print("  {0:<36} {1:>4}字符  trigger={2}  {3}".format(
            x["skill"], x["desc_len"], x["has_trigger"], (x.get("desc") or "")[:50]))
    print("\n无触发标记条数: {0}（前 10 按长度升序）".format(len(s["no_trigger"])))
    for x in s["no_trigger"][:10]:
        print("  {0:<36} {1:>4}字符  {2}".format(x["skill"], x["desc_len"], x["desc"][:60]))
    if s["over_cap_list"]:
        print("\n超官方上限 {0} 字符（{1} 条，截短候选）:".format(DESC_MAX, len(s["over_cap_list"])))
        for x in s["over_cap_list"]:
            print("  {0:<36} {1:>4}字符".format(x["skill"], x["desc_len"]))
    if s["process_list"]:
        print("\n流程入描述命中（{0} 条，前 12 条需人工判定是否概述了正文步骤）:".format(len(s["process_list"])))
        for x in s["process_list"][:12]:
            print("  {0:<34} {1}".format(x["skill"], x["desc"][:66].replace("\n", " ")))

    if args.json:
        Path(args.json).write_text(
            json.dumps({"generated_at": datetime.now().isoformat(timespec="seconds"),
                        "denominator": denom,
                        "desc_max_official": DESC_MAX,
                        "summary": {k: v for k, v in s.items()
                                    if k not in ("shortest", "no_trigger", "over_cap_list",
                                                 "process_list")},
                        "skills": skills}, ensure_ascii=False, indent=1),
            encoding="utf-8")
        print("\nJSON -> {0}".format(args.json))
    if args.md:
        lines = [
            "# P1-1 description 双要素基线报告",
            "",
            "> 生成：{0} ｜ 扫描根：`{1}` ｜ 工具：`05-exec/description_baseline_scan.py`（只读）".format(
                datetime.now().strftime("%Y-%m-%d %H:%M"), GS_ROOT),
            "> 口径：anthropics/skills 官方 —— description = 触发第一信号，需「做什么 + 何时用」双要素；"
            "机器判定为启发式（触发标记词表 + 长度 ≥{0}），语义盲区见「已知盲区」。".format(MIN_DO_LEN),
            "",
            "## 总览",
            "",
            "| 指标 | 值 |",
            "|---|---|",
            "| SKILL.md 总数 | {total} |".format(**s),
            "| frontmatter 解析错误 | {errors} |".format(**s),
            "| 无/空 description | {no_desc} |".format(**s),
            "| 含触发标记（何时用） | {with_trigger} |".format(**s),
            "| 双要素达标 | {double_element} |".format(**s),
            "| 长度 min/median/max | {len_min} / {len_median} / {len_max} |".format(**s),
            "| 超官方上限 %d 字符 | {over_cap} |".format(**s) % DESC_MAX,
            "| 流程入描述（anti-pattern） | {has_process} |".format(**s),
            "",
            "## 口径对账（r19 P1-C 分母统一登记）",
            "",
        ]
        lines += ["- %s" % ln for ln in
                  (_lib.denominator_lines(denom) if _lib else ["_lib 不可用"])]
        lines += ["", "## 最短 Top10（优先整改候选）", "",
            "| skill | 长度 | 触发标记 | description 摘录 |",
            "|---|---|---|---|",
        ]
        for x in s["shortest"]:
            lines.append("| {0} | {1} | {2} | {3} |".format(
                x["skill"], x["desc_len"], "✓" if x["has_trigger"] else "✗",
                (x.get("desc") or "").replace("|", "\\|")[:60]))
        lines += ["", "## 无触发标记（何时用缺失，{0} 条，前 20 按长度升序）".format(len(s["no_trigger"])), ""]
        for x in s["no_trigger"][:20]:
            lines.append("- **{0}**（{1}字符）：{2}".format(
                x["skill"], x["desc_len"], (x.get("desc") or "").replace("`", "'")[:80]))
        lines += [
            "",
            "## 流程入描述命中（{0} 条，anti-pattern 候选）".format(len(s["process_list"])),
            "",
            "> 判据来源：addyosmani/agent-skills `docs/skill-anatomy.md`——「不要概述工作流；"
            "description 里出现流程步骤，agent 可能照摘要执行而不读正文」。",
            "",
        ]
        lines += ["- **{0}**：{1}".format(x["skill"], (x.get("desc") or "").replace("`", "'")[:90])
                  for x in s["process_list"][:30]] or ["- 无命中"]
        lines += [
            "",
            "## 已知盲区",
            "",
            "- 词表启发式：无触发标记 ≠ 无「何时用」语义（可能换了措辞）；命中标记亦可能是噪声。"
            "双要素达标数是**下界**，语义级复核（LLM 抽判）为后续门禁增补项。",
            "- 「做什么」仅以长度 ≥{0} 近似，未做动词语义判定。".format(MIN_DO_LEN),
            "- 「流程入描述」为形态判定（编号/箭头链/冒号后步骤），命中≠违例，"
            "亦存在漏判（用自然语言概述步骤而不带编号/箭头）；须逐条人工裁定。",
            "",
            "## 与路由命中率联动（待办）",
            "",
            "- 门禁落地（焚诀 verify 新判据）待焚诀归属会话执行（本项目红线：焚诀 eval/ 只读）；",
            "- 整改后复跑 `unified_router.py` 盲测对照，验证命中率改善（验收判据③）。",
        ]
        Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("MD   -> {0}".format(args.md))


if __name__ == "__main__":
    main()
