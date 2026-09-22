#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""B6 — 注册表字段归一化（oc-dispatch-exec-guard 的 source / install_state.mv）。

背景（2026-09-22 第 10 轮实测）：
  注册表 151 条里非法值仅 2 类：
    · `oc-dispatch-exec-guard`  source='user'（合法枚举 = user-created / community / skillhub）
    · `oc-dispatch-exec-guard`  install_state.mv=''（缺省应为 null）
  另实测 `testing` 与 `ican-frontend-design-system` 为**残缺条目**（缺 source/install_state/version），
  但补全需先裁定其 category（自建 vs 市场），**不在本次归一化范围**（已登记为待确认）。

为何不直接跑 build_registry 刷新：
  实测 build_registry.py 只对「磁盘有/注册表无」的 missing 集合做 parse+add（L263-295），
  **没有「已有条目字段刷新」路径** ⇒ 存量脏值只能一次性归一化。
  ⇒ 同时已把磁盘真相源（SKILL.md frontmatter）补上 `user_created: true` / `source: user-created`，
     使将来任何重建都能产出正确值（治本 + 治标双落）。
  ⇒ 「build_registry 缺字段刷新路径」这一缺口已登记为待确认项。

安全（R271 / R249）：
  · 不改名、不增删条目；只把 2 个字段改成合法值
  · 备份落 **受管根外**：D:\\global_memory_archive\\_trash\\registry-normalize-20260922\\
  · 写前 json 模拟 + 写后 json 复验；任一失败即中止
"""
import json
import os
import shutil
import sys

REG = r"C:\Users\37533\Desktop\workspace\焚诀\skill\registry\unified-skills-index.json"
CPM = r"C:\Users\37533\Desktop\workspace\焚诀\skill\registry\cross_platform_map.json"
BAK = r"D:\global_memory_archive\_trash\registry-normalize-20260922"

TARGET = "oc-dispatch-exec-guard"
LEGAL_SOURCE = {"user-created", "community", "skillhub"}


def load(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def main():
    dry = "--dry-run" in sys.argv[1:]
    os.makedirs(BAK, exist_ok=True)
    changed = []

    # ---------- ① unified-skills-index.json ----------
    idx = load(REG)
    sk = idx["skills"]
    e = sk.get(TARGET)
    if e is None:
        print(f"[FAIL] {TARGET} 不在注册表")
        return 1
    before = {"source": e.get("source"), "mv": (e.get("install_state") or {}).get("mv")}
    if e.get("source") not in LEGAL_SOURCE:
        e["source"] = "user-created"
    if "install_state" in e and e["install_state"].get("mv") == "":
        e["install_state"]["mv"] = None
    after = {"source": e.get("source"), "mv": (e.get("install_state") or {}).get("mv")}
    if before != after:
        changed.append((REG, before, after))

    # 全库复扫：归一化后不得再有非法 source / 空串 install_state
    bad_src = [(k, v.get("source")) for k, v in sk.items()
               if v.get("source") not in LEGAL_SOURCE and v.get("source") is not None]
    bad_mv = [(k, kk) for k, v in sk.items()
              for kk, vv in (v.get("install_state") or {}).items() if vv == ""]
    print(f"[scan] 剩余非法 source（None 除外，属残缺条目）: {bad_src}")
    print(f"[scan] 剩余空串 install_state: {bad_mv}")

    # ---------- ② cross_platform_map.json（焚诀 registry 副本） ----------
    cpm = load(CPM)
    c = (cpm.get("skills") or {}).get(TARGET)
    cpm_before = None
    if isinstance(c, dict):
        cpm_before = {"source": c.get("source"), "mv": (c.get("install_state") or {}).get("mv")}
        if c.get("source") not in LEGAL_SOURCE:
            c["source"] = "user-created"
        if isinstance(c.get("install_state"), dict) and c["install_state"].get("mv") == "":
            c["install_state"]["mv"] = None
        cpm_after = {"source": c.get("source"), "mv": (c.get("install_state") or {}).get("mv")}
        if cpm_before != cpm_after:
            changed.append((CPM, cpm_before, cpm_after))
    else:
        print(f"[info] {CPM} 无 {TARGET} 条目或结构不同，跳过")

    if not changed:
        print("[no-op] 无字段需要归一化")
        return 0
    for p, b, a in changed:
        print(f"[diff] {p}\n       before={b}\n       after ={a}")

    if dry:
        print("[dry-run] 未写盘")
        return 0

    # ---------- ③ 备份（受管根外，只迁不删精神） ----------
    for p, _b, _a in changed:
        dst = os.path.join(BAK, os.path.basename(p))
        shutil.copy2(p, dst)
        print(f"[backup] {p} -> {dst}")

    # ---------- ④ 写前模拟 ----------
    for p, _b, _a in changed:
        src = idx if p == REG else cpm
        try:
            json.loads(json.dumps(src, ensure_ascii=False))
        except Exception as ex:  # noqa: BLE001
            print(f"[FAIL] {p} 写前模拟失败: {ex}")
            return 1

    # ---------- ⑤ 写盘 + 写后复验 ----------
    for p, _b, _a in changed:
        src = idx if p == REG else cpm
        with open(p, "w", encoding="utf-8") as f:
            json.dump(src, f, ensure_ascii=False, indent=1)
        back = load(p)
        n = len(back.get("skills") or {})
        print(f"[WRITE] {p}  (复验 OK, skills={n} / cpm={len(back.get('skills') or {}) if p == CPM else '-'})")
    print("[DONE] 归一化完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
