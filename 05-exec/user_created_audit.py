# -*- coding: utf-8 -*-
"""阶段5-D2② 注册表 user_created 失真复核（2026-09-22）

口径（本轮裁定，附实测依据）：
  注册表口径 = `焚诀/skill/registry/unified-skills-index.json` 的 `skills` 集合；
  同一口径由焚诀 verify 的 C1/C2/C10 三方守（注册表 == BGE 索引 == skill_content）。
  顶层目录数（152）与全盘 SKILL.md 数（205）是**不同统计范围**（含非 skill 目录 / 嵌套副本），
  不得与注册表条数混用。

判为「疑似失真」的三类：
  A 注册表留存但磁盘无 SKILL.md        → 死件残留
  B user_created=true 但存在市场元数据 → 归属标错（市场件被标为自建）
  C user_created=false 但无市场元数据  → 漏标（自建件被标为社区件）

输出：05-exec/user_created_audit.json + 控制台摘要
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

from _lib import force_utf8_stdout

force_utf8_stdout()

FENJUE = Path(r"C:\Users\37533\Desktop\workspace\焚诀")
REG = FENJUE / "skill" / "registry" / "unified-skills-index.json"
SKILLS = Path(r"D:\global_skills")
OUT = Path(r"c:\Users\37533\Desktop\workspace\自建skill优化\05-exec\user_created_audit.json")
SCOPE = Path(r"c:\Users\37533\Desktop\workspace\自建skill优化\00-scope\scope_result.json")

MARKET_KEYS = ("ownerid", "publishedat", "download_count", "downloadcount", "download_url", "downloadurl")


def market_signal(d: Path):
    for name in ("_meta.json", "meta.json"):
        f = d / name
        if not f.exists():
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        keys = set()
        stack = [data]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                # 口径(2026-09-23修)：键名大小写归一，与01-scan/scan_all.py同源（原大小写敏感漏检）。
                keys |= {str(k).lower() for k in cur.keys()}
                stack.extend(cur.values())
            elif isinstance(cur, list):
                stack.extend(cur)
        hit = sorted(k for k in MARKET_KEYS if k in keys)
        if hit:
            return name, hit
    return None, []


def main():
    reg = json.loads(REG.read_text(encoding="utf-8"))
    skills = reg["skills"]
    rows = []
    for name, meta in sorted(skills.items()):
        d = SKILLS / name
        has_md = (d / "SKILL.md").is_file()
        mfile, mhit = market_signal(d) if d.is_dir() else (None, [])
        rows.append({
            "name": name,
            "user_created": bool(meta.get("user_created")),
            "source": meta.get("source"),
            "version": meta.get("version"),
            "dir_exists": d.is_dir(),
            "has_skill_md": has_md,
            "market_file": mfile,
            "market_keys": mhit,
        })

    n = len(rows)
    uc_true = [r for r in rows if r["user_created"]]
    uc_false = [r for r in rows if not r["user_created"]]
    a = [r["name"] for r in rows if not r["has_skill_md"]]
    b = [r["name"] for r in uc_true if r["market_keys"]]
    c = [r["name"] for r in uc_false if r["dir_exists"] and r["has_skill_md"] and not r["market_keys"]]
    src_mismatch = [r["name"] for r in rows
                    if r["source"] != ("user-created" if r["user_created"] else "community")]

    # 与项目阶段0 自建清单交叉（HIGH/MID）
    scope_cov = None
    if SCOPE.exists():
        sc = json.loads(SCOPE.read_text(encoding="utf-8"))
        rows0 = sc.get("rows") or []
        selfd = {r.get("skill") for r in rows0 if r.get("conf") in ("HIGH", "MID")}
        reg_names = set(skills)
        scope_cov = {
            "scope_selfbuilt": len(selfd),
            "in_registry": len(selfd & reg_names),
            "missing_from_registry": sorted(selfd - reg_names),
            "registry_user_created_not_in_scope": sorted(
                {r["name"] for r in uc_true} - selfd),
        }

    result = {
        "generated": date.today().isoformat(),
        "registry": str(REG),
        "scope_note": "注册表口径 = 本文件 skills 集合；与顶层目录数/全盘 SKILL.md 数不可混用",
        "total": n,
        "user_created_true": len(uc_true),
        "user_created_false": len(uc_false),
        "A_missing_skill_md": a,
        "B_user_created_true_with_market_signal": b,
        "C_user_created_false_without_market_signal": c,
        "source_field_mismatch": src_mismatch,
        "scope_crosscheck": scope_cov,
        "rows": rows,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("注册表条数            : %d" % n)
    print("user_created=true     : %d" % len(uc_true))
    print("user_created=false    : %d" % len(uc_false))
    print("A 磁盘无 SKILL.md     : %d  %s" % (len(a), a[:12]))
    print("B true 但有市场信号   : %d  %s" % (len(b), b[:12]))
    print("C false 且无市场信号  : %d  %s" % (len(c), c[:12]))
    print("source 字段自相矛盾   : %d  %s" % (len(src_mismatch), src_mismatch))
    if scope_cov:
        print("阶段0 自建清单(HIGH+MID): %d | 仍在注册表 %d | 已消失 %d"
              % (scope_cov["scope_selfbuilt"], scope_cov["in_registry"],
                 len(scope_cov["missing_from_registry"])))
    print("输出: %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
