#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""apply_patches.py — 跨文件多处补丁应用器（全有或全无 + 命中数必须为 1）

用途：一次把同一主题的改动批量落到 N 个文件（跨仓：global_memory / 焚诀 / 本项目）。
为什么不用 rule_editor.py --patch：它的 --patch 只作用于**单文件**，且 commit 固定到
GIT_ROOT=D:\\global_skills；本主题需改 GM/焚诀两仓，故用本器。

判据（与 rule_editor.py replace --patch 同款语义）：
  · 每处 old 必须**恰好命中 1 次**（按「逐行 strip 后完全相等」匹配，抗缩进差异）
  · 任一处未命中或多次命中 → **整体不写盘**（全有或全无），退出码 1
  · 写盘保持原编码（UTF-8/BOM）与原行尾（CRLF/LF）

用法：
  python apply_patches.py <patch.json> --dry-run
  python apply_patches.py <patch.json>
"""
import json
import os
import shutil
import sys
from datetime import datetime


def _read(path):
    with open(path, "rb") as f:
        raw = f.read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    crlf = text.count("\r\n") >= text.count("\n") - text.count("\r\n")
    return text, bom, crlf


def _write(path, text, bom, crlf):
    if crlf:
        text = text.replace("\n", "\r\n")
    data = text.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    with open(path, "wb") as f:
        f.write(data)


def _find(lines, old_lines):
    """返回命中起始行索引列表（逐行 strip 后相等）。"""
    n = len(old_lines)
    hits = []
    for i in range(len(lines) - n + 1):
        if all(lines[i + k].strip() == old_lines[k] for k in range(n)):
            hits.append(i)
    return hits


def _backup_all(plan):
    """写前备份：全部目标文件原字节（含 BOM/行尾）拷入脚本旁 _bak/apply_patches/<ts>/。

    任一拷贝失败即抛异常中止（fail-closed）——备份不全时绝不落盘。
    目录已被 .gitignore `_bak/` 豁免，不进仓库。
    """
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_bak", "apply_patches", ts)
    os.makedirs(backup_dir, exist_ok=True)
    backups = {}
    for path in plan:
        flat = os.path.abspath(path).replace(":", "").replace("\\", "__").replace("/", "__")
        dest = os.path.join(backup_dir, flat)
        shutil.copy2(path, dest)
        backups[path] = dest
    return backup_dir, backups


def main():
    if len(sys.argv) < 2:
        print("用法: apply_patches.py <patch.json> [--dry-run]")
        return 2
    patch_path = sys.argv[1]
    dry = "--dry-run" in sys.argv[2:]

    with open(patch_path, encoding="utf-8") as f:
        patches = json.load(f)

    # ① 全部预检（全有或全无）
    plan = {}
    errors = []
    for idx, p in enumerate(patches, 1):
        path = p["file"]
        if not os.path.exists(path):
            errors.append(f"#{idx} 文件不存在: {path}")
            continue
        text, bom, crlf = _read(path)
        lines = text.split("\n")
        # ⚠️ 必须 strip（非 rstrip）：实际行按 strip 比对，old 若保留行首缩进则永不匹配（2026-09-22 实测踩坑）
        old_lines = [ln.strip() for ln in p["old"].split("\n")]
        new_lines = p["new"].split("\n")
        if p.get("mode") == "substr":
            # 子串模式也归约为「单行替换」：old 必须整段落在**同一行**内，且全文件仅 1 行命中
            # （2026-09-22 踩坑：原实现直接改 text 变量，落盘时被 lines 覆盖 → 静默丢补丁）
            hit_lines = [i for i, ln in enumerate(lines) if p["old"] in ln]
            if len(hit_lines) != 1:
                errors.append(f"#{idx} substr 命中行数={len(hit_lines)}（须为 1）: {path}")
                continue
            plan.setdefault(path, []).append((idx, hit_lines[0], 1, new_lines, bom, crlf))
            continue
        hits = _find(lines, old_lines)
        if len(hits) != 1:
            errors.append(f"#{idx} 命中数={len(hits)}（须为 1）: {path} ← {old_lines[0][:60]}")
            continue
        plan.setdefault(path, []).append((idx, hits[0], len(old_lines), new_lines, bom, crlf))

    # ①b JSON 文件预校验：模拟应用后必须仍是合法 JSON
    # （2026-09-22 实测踩坑：补丁文本含裸 " 会写坏 JSON 字符串 → 门禁 JSONDecodeError）
    for path, items in plan.items():
        if not path.lower().endswith(".json"):
            continue
        text, _b2, _c2 = _read(path)
        sim = text.split("\n")
        for _idx, ln, n, new_lines, _bb, _cc in sorted(items, key=lambda x: -x[1]):
            # 模拟必须与 ② 的写入语义同构：substr = 行内子串替换，非 substr = 整块替换
            # （2026-09-23 实测踩坑：模拟曾一律用整块替换 → 命中行前有其它内容的合法 substr
            #   补丁被假失败拦截，而真实写入本是正确的）
            if patches[_idx - 1].get("mode") == "substr":
                sim[ln] = sim[ln].replace(patches[_idx - 1]["old"], "\n".join(new_lines))
            else:
                sim[ln:ln + n] = new_lines
        try:
            json.loads("\n".join(sim))
        except Exception as e:
            errors.append(f"JSON 预校验失败（写后会坏）: {path} → {e}")

    if errors:
        print("[FAIL] 全有或全无：以下补丁未通过预检，**未写盘**")
        for e in errors:
            print("   " + e)
        return 1

    print(f"[OK] 预检通过：{len(patches)} 处 / {len(plan)} 个文件")
    if dry:
        for path, items in plan.items():
            for idx, ln, n, new_lines, _b, _c in items:
                print(f"  #{idx} {path}:{ln+1}  old({n} 行) → new({len(new_lines)} 行)")
        print("[dry-run] 未写盘")
        return 0

    # ①c 写前备份（备份失败 = 未写盘；写后可整批还原）
    try:
        backup_dir, _backups = _backup_all(plan)
    except Exception as e:
        print(f"[FAIL] 写前备份失败，未写盘: {e}")
        return 1
    print(f"  [BACKUP] {backup_dir}")

    # ② 逐文件应用（同一文件内多处：从后往前替换，避免行号漂移）
    fails = []
    for path, items in plan.items():
        text, bom, crlf = _read(path)
        lines = text.split("\n")
        for _idx, ln, n, new_lines, _b, _c in sorted(items, key=lambda x: -x[1]):
            if patches[_idx - 1].get("mode") == "substr":
                # ⚠️ 必须是**行内子串替换**，不可整行覆盖
                # （2026-09-22 实测踩坑：误写为 lines[ln] = new → 吃掉该行打头内容，6 行受损，
                #   且 dry-run 与「new 首行存在」校验都拦不住，因为坏的是被覆盖掉的旧内容）
                lines[ln] = lines[ln].replace(patches[_idx - 1]["old"], "\n".join(new_lines))
                continue
            lines[ln:ln + n] = new_lines
        _write(path, "\n".join(lines), bom, crlf)
        # 写后自校验：每处 patch 的 new 首行必须出现（防静默丢补丁；2026-09-22 实测踩坑）
        after, _b2, _c2 = _read(path)
        for _idx, _ln, _n, new_lines, _b, _c in items:
            head = new_lines[0].strip()
            if head and head not in after:
                fails.append(f"#{_idx} 写后校验失败（new 首行未出现）: {path}")
        print(f"  [WRITE] {path}  ({len(items)} 处)")

    if fails:
        print("[FAIL] 写后自校验未通过：")
        for _f in fails:
            print("   " + _f)
        return 1

    print(f"[DONE] 已写盘 {len(plan)} 个文件 / {len(patches)} 处")
    return 0


if __name__ == "__main__":
    sys.exit(main())
