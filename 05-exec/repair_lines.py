#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""repair_lines.py — 定位式行修复器（从 git 父提交取原行 → 行内正确替换 → 回填）

背景（2026-09-22 自建skill优化实测踩坑）：
  apply_patches.py 的 substr 模式曾被实现为「整行替换」（lines[ln] = new），
  而非「行内子串替换」（lines[ln] = lines[ln].replace(old, new)），
  导致 6 行**被打头的其余内容被吃掉**（含 truth_constants.json 的 `"_changed": "` 前缀）。
  dry-run 与「写后 new 首行存在」校验都没能拦住 —— 因为坏的是**被覆盖掉的旧内容**。

本器修法：对每处受损行
  ① 用 `git show <ref>:<relpath>`（**只读**，不做 checkout）取原始全文
  ② 在原文中定位含 orig_anchor 的**唯一**行 → 得 orig_line
  ③ correct = orig_line.replace(old_sub, new_sub)（replace=false 时 correct = orig_line）
  ④ 在当前工作文件中定位含 cur_anchor 的**唯一**行 → 用 correct 整行替换
  ⑤ .json 文件写后强制 json.loads 校验

用法：python repair_lines.py <repair.json> [--dry-run]
"""
import json
import subprocess
import sys

# 读写共用实现抽到 _lib（2026-09-23 r9）：原 _write 不处理行尾 ⇒ 修复 CRLF 文件会被改写成 LF，
# 且与 apply_patches 的读写语义不一致；现统一为「归一化读 + 按原行尾原子写」
from _lib import read_text as _read, write_text as _write


def _show(repo, ref, relpath):
    r = subprocess.run(["git", "-C", repo, "show", f"{ref}:{relpath}"],
                       capture_output=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "replace").strip())
    return r.stdout.decode("utf-8-sig")


def main():
    if len(sys.argv) < 2:
        print("用法: repair_lines.py <repair.json> [--dry-run]")
        return 2
    dry = "--dry-run" in sys.argv[2:]
    with open(sys.argv[1], encoding="utf-8") as f:
        specs = json.load(f)

    plan, errors = [], []
    for i, s in enumerate(specs, 1):
        try:
            orig = _show(s["repo"], s["ref"], s["relpath"])
        except Exception as e:
            errors.append(f"#{i} git show 失败: {e}")
            continue
        o_hits = [ln for ln in orig.split("\n") if s["orig_anchor"] in ln]
        if len(o_hits) != 1:
            errors.append(f"#{i} 原文锚点命中 {len(o_hits)} 行（须 1）: {s['file']}")
            continue
        orig_line = o_hits[0]
        if s.get("replace", True):
            correct = orig_line.replace(s["old_sub"], s["new_sub"])
            if correct == orig_line:
                errors.append(f"#{i} 行内替换未生效（old_sub 不在原行中）: {s['file']}")
                continue
        else:
            correct = orig_line
        text, bom, crlf = _read(s["file"])
        lines = text.split("\n")
        c_hits = [n for n, ln in enumerate(lines) if s["cur_anchor"] in ln]
        if len(c_hits) != 1:
            errors.append(f"#{i} 现文锚点命中 {len(c_hits)} 行（须 1）: {s['file']}")
            continue
        plan.append((i, s["file"], c_hits[0], correct, bom, crlf))

    if errors:
        print("[FAIL] 预检未过，**未写盘**")
        for e in errors:
            print("   " + e)
        return 1

    print(f"[OK] 预检通过：{len(plan)} 处修复")
    for i, path, ln, correct, _b, _c in plan:
        print(f"  #{i} {path}:{ln+1}")
        print(f"      → {correct[:120]}{'…' if len(correct) > 120 else ''}")
        if not dry:
            text, bom, crlf = _read(path)
            lines = text.split("\n")
            lines[ln] = correct
            _write(path, "\n".join(lines), bom, crlf)
            if path.lower().endswith(".json"):
                try:
                    with open(path, encoding="utf-8-sig") as f:
                        json.load(f)
                    print("      [JSON OK]")
                except Exception as e:
                    print(f"      [JSON FAIL] {e}")
                    return 1
    print("[dry-run] 未写盘" if dry else "[DONE] 已修复")
    return 0


if __name__ == "__main__":
    sys.exit(main())
