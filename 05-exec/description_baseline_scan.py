# -*- coding: utf-8 -*-
"""description_baseline_scan.py — P1-1 description 双要素基线扫描（只读取证，对标 anthropics/skills 官方口径）。

口径（anthropics/skills 官方）：frontmatter 必填字段 = name + description；
description 是平台触发技能的第一信号，应同时含「做什么 + 何时用」双要素。

机器判定（本脚本口径，⚠️ 启发式非语义判定）：
  · 做什么 —— description 非空且 ≥15 字符
  · 何时用 —— 命中触发标记词表（中英）：触发/适用/用于/当用户/何时/使用场景/场景：/不适用/
               use when/use this/when the user/when working/triggers?/for .* tasks 等

输出：stdout 摘要 + --json <path>（机器可读全量）+ --md <path>（基线报告）。
只读：不写 D:\\global_skills 任何文件。默认 dry-run 语义（无 --apply）。
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

GS_ROOT = Path(r"D:\global_skills")
TRIGGER_RE = re.compile(
    r"触发|适用|用于|何时|使用场景|场景[：:]|不适用|当用户|需要(做|进行|生成|分析|创建|查)|"
    r"use\s+when|use\s+this|when\s+(the\s+)?user|when\s+working|triggers?\b|for\s+\S+\s+(tasks?|work)",
    re.IGNORECASE,
)
MIN_DO_LEN = 15  # 「做什么」最小长度（字符）


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
        })
    return skills, junctions


def summarize(skills, junctions):
    total = len(skills)
    errs = [s for s in skills if s.get("error")]
    no_desc = [s for s in skills if not s.get("error") and not s.get("desc")]
    has_desc = [s for s in skills if s.get("desc")]
    with_trigger = [s for s in has_desc if s["has_trigger"]]
    double = [s for s in has_desc if s["double_element"]]
    lens = sorted(s["desc_len"] for s in has_desc)
    shortest = sorted(has_desc, key=lambda s: s["desc_len"])[:10]
    no_trigger = sorted((s for s in has_desc if not s["has_trigger"]),
                        key=lambda s: s["desc_len"])
    return {
        "total": total, "errors": len(errs), "no_desc": len(no_desc),
        "has_desc": len(has_desc), "with_trigger": len(with_trigger),
        "double_element": len(double),
        "len_min": lens[0] if lens else 0, "len_max": lens[-1] if lens else 0,
        "len_median": lens[len(lens) // 2] if lens else 0,
        "junctions_excluded": junctions,
        "shortest": shortest, "no_trigger": no_trigger,
    }


def main():
    ap = argparse.ArgumentParser(description="description 双要素基线扫描（只读）")
    ap.add_argument("--json", help="全量结果 JSON 输出路径")
    ap.add_argument("--md", help="基线报告 Markdown 输出路径")
    args = ap.parse_args()

    skills, junctions = scan()
    s = summarize(skills, junctions)
    print("=== description 双要素基线（{0}，对标 anthropics 官方口径） ===".format(
        datetime.now().strftime("%Y-%m-%d %H:%M")))
    print("SKILL.md 总数: {total}  解析错误: {errors}  无/空 description: {no_desc}".format(**s))
    print("有 description: {has_desc}  含触发标记: {with_trigger}  双要素达标: {double_element}".format(**s))
    print("长度分布: min={len_min} / median={len_median} / max={len_max}".format(**s))
    print("\n最短 Top10（优先整改候选）:")
    for x in s["shortest"]:
        print("  {0:<36} {1:>4}字符  trigger={2}  {3}".format(
            x["skill"], x["desc_len"], x["has_trigger"], (x.get("desc") or "")[:50]))
    print("\n无触发标记条数: {0}（前 10 按长度升序）".format(len(s["no_trigger"])))
    for x in s["no_trigger"][:10]:
        print("  {0:<36} {1:>4}字符  {2}".format(x["skill"], x["desc_len"], x["desc"][:60]))

    if args.json:
        Path(args.json).write_text(
            json.dumps({"generated_at": datetime.now().isoformat(timespec="seconds"),
                        "summary": {k: v for k, v in s.items()
                                    if k not in ("shortest", "no_trigger")},
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
            "",
            "## 最短 Top10（优先整改候选）",
            "",
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
            "## 已知盲区",
            "",
            "- 词表启发式：无触发标记 ≠ 无「何时用」语义（可能换了措辞）；命中标记亦可能是噪声。"
            "双要素达标数是**下界**，语义级复核（LLM 抽判）为后续门禁增补项。",
            "- 「做什么」仅以长度 ≥{0} 近似，未做动词语义判定。".format(MIN_DO_LEN),
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
