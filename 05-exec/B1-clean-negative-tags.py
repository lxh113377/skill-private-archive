#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""B1 — 清理焚诀 audit/negative_constraints.json 的 ghost 条目与 ghost 引用。

背景（2026-09-22 第 10 轮实测）：
  negative_tag_audit.py 报 7 个 GHOST-ENTRY + 7 个 GHOST-REF，健康率 72.5% / RESULT: FAIL。
  7 个条目对应的 skill 全部实测 disk=False 且不在注册表（非判据假阳性，R263 已先证）。

口径：
  · GHOST-ENTRY  = 该条目自身的 skill 已不存在 → **整条删除**
  · GHOST-REF    = 其余条目的 negative / full_desc 文本里引用这些已不存在的 skill
                   （形如「那是A/B/C的活」）→ **从列表中剔除该 token**
  · 列表剔除到空 → 连同引导语「——那是…的活」一并删除（避免留下「——那是的活」残句）

安全（R271 精神）：
  · 写前模拟 json.loads + 写后复验 json.loads；任一失败即中止且不写盘
  · 不改动非 ghost 的任何文本；只做「删条目」与「列表剔除」
  · --dry-run 只预览不写盘
"""
import json
import os
import re
import sys

NEG = r"C:\Users\37533\Desktop\workspace\焚诀\audit\negative_constraints.json"
SKILLS = r"D:\global_skills"

# 实测确认的 ghost（2026-09-22：disk=False 且不在注册表）
GHOSTS = [
    "skill-install",
    "skill-creator",
    "skills-security-check",
    "install-skill-dependency",
    "deep-research-pro",
    "cloudbase-webapp-deploy-debug",
    "clawhub",
    "plugin-creator",  # 额外：仅出现在 clawhub.full_desc 中，审计的 negative-only 扫描未覆盖
]

REF_RE = re.compile(r"——那是([A-Za-z0-9_/-]+)的活")
LIST_RE = re.compile(r"那是([A-Za-z0-9_/-]+)的活")


def rewrite(text, ghosts):
    if not text:
        return text, 0
    removed = 0

    def _fix(m):
        nonlocal removed
        tokens = [t for t in m.group(1).split("/") if t]
        kept = [t for t in tokens if t not in ghosts]
        removed += len(tokens) - len(kept)
        if not kept:
            return ""  # 整段引导语删除
        return "那是" + "/".join(kept) + "的活"

    new = LIST_RE.sub(_fix, text)
    return new, removed


def main():
    dry = "--dry-run" in sys.argv[1:]
    with open(NEG, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    before_entries = len(data)

    # ① 删 ghost 条目（仅删实测确认存在的 key）
    deleted = [k for k in GHOSTS if k in data]
    for k in deleted:
        del data[k]

    # ② 剔除其余条目文本中的 ghost 引用
    total_refs = 0
    touched = []
    for name, cfg in data.items():
        if not isinstance(cfg, dict):
            continue
        n_refs = 0
        for field in ("negative", "full_desc"):
            if field in cfg and isinstance(cfg[field], str):
                cfg[field], r = rewrite(cfg[field], set(GHOSTS))
                n_refs += r
        if n_refs:
            total_refs += n_refs
            touched.append(f"{name}({n_refs})")

    # ②b 残句清理：整段引导语被删后可能留下悬空破折号（实证：chaoshi-web-deploy 出现「——。」）
    for name, cfg in data.items():
        if not isinstance(cfg, dict):
            continue
        for field in ("negative", "full_desc"):
            if isinstance(cfg.get(field), str):
                t = cfg[field]
                for bad, good in (("——。", "。"), ("——，", "，"), ("——；", "；"), ("—— ", " "),
                                  ("；。", "。"), ("。。", "。")):
                    t = t.replace(bad, good)
                cfg[field] = t

    # ③ 写前模拟：序列化后必须能解析回等价对象
    sim = json.dumps(data, ensure_ascii=False, indent=2)
    try:
        again = json.loads(sim)
        assert len(again) == len(data)
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] 写前模拟失败，未写盘: {e}")
        return 1

    print(f"[plan] 条目 {before_entries} → {len(data)}（删 {len(deleted)}: {', '.join(deleted)}）")
    print(f"[plan] 剔除 ghost 引用 {total_refs} 处，涉及 {len(touched)} 条: {', '.join(touched)}")

    # ④ 残留复核：删完后不应再有任何 ghost token 作为「那是…的活」成员
    residue = []
    for name, cfg in data.items():
        if not isinstance(cfg, dict):
            continue
        for field in ("negative", "full_desc"):
            t = cfg.get(field, "")
            for m in LIST_RE.finditer(t or ""):
                for tok in m.group(1).split("/"):
                    if tok in GHOSTS:
                        residue.append(f"{name}.{field}:{tok}")
    if residue:
        print(f"[FAIL] 仍有 ghost 引用残留: {residue}")
        return 1

    if dry:
        print("[dry-run] 未写盘")
        return 0

    with open(NEG, "w", encoding="utf-8") as f:
        f.write(sim + "\n")

    # ⑤ 写后复验
    with open(NEG, "r", encoding="utf-8") as f:
        check = json.load(f)
    if len(check) != len(data):
        print("[FAIL] 写后复验条数不一致")
        return 1
    print(f"[DONE] 已写盘 {NEG}（{len(check)} 条）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
