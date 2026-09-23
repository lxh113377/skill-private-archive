# -*- coding: utf-8 -*-
"""阶段5-D2① 直连表死目标扫描（2026-09-22）

判据（R-CURRENT 实测，双源）：
  一个直连目标「可达」= 命中注册表（焚诀 skill/registry/unified-skills-index.json，120 条）
  **或** 磁盘存在 SKILL.md（D:\\global_skills\\<name>\\SKILL.md）。
  两者皆不满足 ⇒ 死目标：任何命中该 pattern 的查询会被**短路到一个不存在的 skill**（致命纪律 #18 派生件脱节）。

输出：05-exec/direct_map_dead_targets.json + 控制台摘要
"""
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

FENJUE = Path(r"C:\Users\37533\Desktop\workspace\焚诀")
DM = FENJUE / "eval" / "direct_map.json"
REG = FENJUE / "skill" / "registry" / "unified-skills-index.json"
SKILLS = Path(r"D:\global_skills")
OUT = Path(r"c:\Users\37533\Desktop\workspace\自建skill优化\05-exec\direct_map_dead_targets.json")

NON_SKILL_TARGETS = {"NONE"}  # 哨兵值，非 skill


def main():
    entries = json.loads(DM.read_text(encoding="utf-8"))
    reg = set(json.loads(REG.read_text(encoding="utf-8"))["skills"])
    on_disk = {p.name for p in SKILLS.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()}

    targets = {}
    for pattern, name in entries:
        targets.setdefault(name, []).append(pattern)

    dead = {}
    for name, pats in sorted(targets.items()):
        if name in NON_SKILL_TARGETS:
            continue
        if name in reg or name in on_disk:
            continue
        dead[name] = pats

    total_entries = len(entries)
    dead_entries = sum(len(v) for v in dead.values())
    result = {
        "generated": "2026-09-22",
        "direct_map": str(DM),
        "entries": total_entries,
        "distinct_targets": len(targets),
        "registry_count": len(reg),
        "disk_skill_count": len(on_disk),
        "dead_targets": dead,
        "dead_entry_count": dead_entries,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("直连表条目            : %d（目标 %d 个）" % (total_entries, len(targets)))
    print("注册表 %d / 磁盘 %d" % (len(reg), len(on_disk)))
    print("死目标                : %d 个 / %d 条直连" % (len(dead), dead_entries))
    for name, pats in dead.items():
        print("  DEAD  %-28s x%d  e.g. %s" % (name, len(pats), pats[0][:48]))
    print("输出: %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
