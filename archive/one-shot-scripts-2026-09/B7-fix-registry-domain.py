#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""B7 前置 — 注册表域名与残缺条目修复（M4 的根因层）。

根因链（2026-09-22 第 10 轮实测）：
  `ican-frontend-design-system` 的注册表条目 `domain = "09-dev-tools"` —— 这是**旧数字前缀域**
  （P0P1 清理计划 2026-08-16 已软删除；build_registry._infer_domain 明令「禁止再生成」）。
  它导致 skill_content 多出第 14 个域文件 `09-dev-tools.json`，从而让 degradation-test 的
  1c（期望 13 个域 JSON）/ 3b（无空域）失败；同时 domain_map.ps1 仍是 2026-08-08 的 160 条旧快照
  → 3a / 3d（domainMap 160 ≠ JSON 151）失败。=> content_snr 的 M4 判「自检金标准陈旧」。

修复：
  ① `ican-frontend-design-system`：domain → `classify_domain(...)` 实测值 `design`；
     并补齐残缺字段 install_state（DEFAULT_INSTALL_STATE）/ version（磁盘 4.0.0）
  ② `testing`：补齐缺失的 name / display_name / compatible_platforms / source / version
     （source 依 user_created=false 取 `community`，与 build_registry 缺省口径一致）
  ③ 统计全库「非法域名」（不在 13 域白名单内）与「残缺字段」条目，修完必须为 0

安全：备份到受管根外；json 写前模拟 + 写后复验；只改字段不增删条目。
"""
import json
import os
import shutil
import sys

REG = r"C:\Users\37533\Desktop\workspace\焚诀\skill\registry\unified-skills-index.json"
CPM = r"C:\Users\37533\Desktop\workspace\焚诀\skill\registry\cross_platform_map.json"
BAK = r"D:\global_memory_archive\_trash\registry-normalize-20260922"

VALID_DOMAINS = {"automation", "code", "creative", "data", "design", "doc",
                 "general_utils", "local", "media", "memory", "research", "system", "web"}
DEFAULT_INSTALL_STATE = {"wb": True, "tc": True, "codex": True, "oc": True,
                         "cc": None, "hm": None, "mv": None, "td": None}
# 旧数字前缀域（已软删除，禁止再生成）——出现即视为非法
LEGACY_PREFIX = ("00-", "01-", "02-", "03-", "04-", "05-", "07-", "08-", "09-", "10-", "99-")


def load(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def main():
    dry = "--dry-run" in sys.argv[1:]
    sys.path.insert(0, r"C:\Users\37533\Desktop\workspace\焚诀\eval")
    from domain_classifier import classify_domain  # noqa: E402

    os.makedirs(BAK, exist_ok=True)
    idx = load(REG)
    sk = idx["skills"]
    changes = []

    # ① 非法域名 → 重分类
    for name, e in sk.items():
        dom = e.get("domain", "")
        if dom not in VALID_DOMAINS:
            desc = ""
            sm = os.path.join(r"D:\global_skills", name, "SKILL.md")
            if os.path.exists(sm):
                with open(sm, encoding="utf-8", errors="ignore") as f:
                    txt = f.read()
                import re as _re
                m = _re.search(r"^description:\s*(.+)$", txt, _re.M)
                desc = (m.group(1).strip() if m else "") + txt[:400]
            new = classify_domain(f"{name} {desc}") or "general_utils"
            if new in VALID_DOMAINS:
                changes.append((REG, name, "domain", dom, new))
                e["domain"] = new

    # ② 残缺字段补齐
    for name, e in sk.items():
        if "install_state" not in e:
            changes.append((REG, name, "install_state", None, "DEFAULT"))
            e["install_state"] = dict(DEFAULT_INSTALL_STATE)
        if "version" not in e:
            sm = os.path.join(r"D:\global_skills", name, "SKILL.md")
            v = "community"
            if os.path.exists(sm):
                with open(sm, encoding="utf-8", errors="ignore") as f:
                    import re as _re
                    m = _re.search(r"^version:\s*(\S+)", f.read(), _re.M)
                    v = m.group(1) if m else "community"
            changes.append((REG, name, "version", None, v))
            e["version"] = v
        if "source" not in e:
            s = "user-created" if e.get("user_created") else "community"
            changes.append((REG, name, "source", None, s))
            e["source"] = s
        if "name" not in e:
            changes.append((REG, name, "name", None, name))
            e["name"] = name
        if "display_name" not in e:
            changes.append((REG, name, "display_name", None, name))
            e["display_name"] = name
        if "compatible_platforms" not in e:
            # 与 build_registry DEFAULT 一致（四端）
            changes.append((REG, name, "compatible_platforms", None, "['wb','tr','cx','hm']"))
            e["compatible_platforms"] = ["wb", "tr", "cx", "hm"]

    # ③ 复扫
    bad_dom = [(k, v.get("domain")) for k, v in sk.items() if v.get("domain") not in VALID_DOMAINS]
    legacy_dom = [(k, v.get("domain")) for k, v in sk.items()
                  if any(str(v.get("domain", "")).startswith(p) for p in LEGACY_PREFIX)]
    miss = [k for k, v in sk.items()
            if any(f not in v for f in ("name", "domain", "user_created", "source",
                                        "install_state", "version", "compatible_platforms"))]
    print(f"[scan] 非法域名: {bad_dom}")
    print(f"[scan] 旧数字前缀域: {legacy_dom}")
    print(f"[scan] 仍残缺条目: {miss}")
    for c in changes:
        print(f"[diff] {c[1]}.{c[2]}: {c[3]} -> {c[4]}")

    if bad_dom or legacy_dom or miss:
        print("[FAIL] 复扫未清零，未写盘")
        return 1
    if not changes:
        print("[no-op] 无需修改")
        return 0
    if dry:
        print("[dry-run] 未写盘")
        return 0

    # ④ 备份（受管根外）
    dst = os.path.join(BAK, "unified-skills-index.before-B7.json")
    shutil.copy2(REG, dst)
    print(f"[backup] {REG} -> {dst}")

    # ⑤ 同步 cpm 的域字段（cross_platform_map.json 焚诀副本）
    cpm = load(CPM)
    csk = cpm.get("skills") or {}
    for _p, name, field, _o, new in [(c[0], c[1], c[2], c[3], c[4]) for c in changes if c[2] == "domain"]:
        if name in csk and isinstance(csk[name], dict):
            if "domain" in csk[name] or True:
                csk[name]["domain"] = new
                print(f"[cpm] {name}.domain -> {new}")

    # ⑥ 写盘 + 复验
    json.loads(json.dumps(idx, ensure_ascii=False))
    json.loads(json.dumps(cpm, ensure_ascii=False))
    with open(REG, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=1)
    with open(CPM, "w", encoding="utf-8") as f:
        json.dump(cpm, f, ensure_ascii=False, indent=1)
    back = load(REG)
    print(f"[WRITE] {REG} 复验 OK, skills={len(back['skills'])}")
    print(f"[WRITE] {CPM} 复验 OK, skills={len(load(CPM).get('skills') or {})}")
    print("[DONE] 完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
