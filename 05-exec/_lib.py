# -*- coding: utf-8 -*-
"""_lib.py — 05-exec 可复用工具共用库（2026-09-23 r9 由各脚本重复实现抽取）

背景：stdout UTF-8 包装曾有 5 份逐字拷贝、utf-8-sig JSON 读取 3 份、
BOM/行尾保持读写 2 份**且语义不一致**（repair_lines 旧版不处理 CRLF，
修复过 CRLF 文件会把行尾改写成 LF）——抽到此单一真相源。

  force_utf8_stdout()            stdout 强制 UTF-8（管道/重定向降级不崩）
  load_json(path)                utf-8-sig 读 JSON（BOM 兼容）
  read_text(path)                读文本 → (text_lf, bom, crlf)；CRLF 归一化 LF，
                                 由 write_text 按原行尾整体复原（防 \r\r\n 双重行尾）
  write_text(path, text, bom, crlf)  临时文件 + os.replace 原子写，保持 BOM/行尾
  backup_file(path, backup_dir)  copy2 写前备份（目录不存在则建），返回备份路径
  registry_denominator()         焚诀注册表口径（disk_manifest.json，读不到返回 error 不猜 0）
  denominator(scanned, ...)      技能统计三口径对账（纳入 / 磁盘 glob / 注册表），r19 P1-C 单一真相源
"""
import json
import os
import shutil
import sys


def force_utf8_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        import io as _io
        try:
            sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        except Exception:
            pass


def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def read_text(path):
    with open(path, "rb") as f:
        raw = f.read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    crlf = text.count("\r\n") >= text.count("\n") - text.count("\r\n")
    text = text.replace("\r\n", "\n")
    return text, bom, crlf


def write_text(path, text, bom, crlf):
    if crlf:
        text = text.replace("\n", "\r\n")
    data = text.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    tmp = os.path.join(os.path.dirname(os.path.abspath(path)), f".tmp_write.{os.getpid()}")
    try:
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def backup_file(path, backup_dir):
    os.makedirs(backup_dir, exist_ok=True)
    flat = os.path.abspath(path).replace(":", "").replace("\\", "__").replace("/", "__")
    dest = os.path.join(backup_dir, flat)
    shutil.copy2(path, dest)
    return dest


# ---------------------------------------------------------------------------
# r19 P1-C 分母统一登记（对标 sickn33/agentic-awesome-skills schemas/aas-v1 的
# 「口径契约」思路）。根因：同一件事在本体系有三处口径（r18 报告 N4）——
# 焚诀注册表 167 / 本仓扫描器 166（按设计跳过 junction）/ 历史报告 151。
# 禁再出现「单口径裸数字」：任何技能计数必须三口径并排 + 附取值命令。
# ---------------------------------------------------------------------------

REGISTRY_MANIFEST = os.path.join(
    r"C:\Users\37533\Desktop\workspace\焚诀", "skill", "registry", "disk_manifest.json")
REGISTRY_CMD = (r'python "C:\Users\37533\Desktop\workspace\焚诀\eval\verify_truth_consistency.py"'
                "  # 取 C1 行")


def registry_denominator(manifest_path=None):
    """读焚诀注册表磁盘清单口径。失败时返回 error 字段，禁止用 0 冒充「无技能」。"""
    path = manifest_path or REGISTRY_MANIFEST
    try:
        data = load_json(path)
    except (OSError, ValueError) as e:
        return {"available": False, "error": "%s: %s" % (type(e).__name__, e), "path": path}
    if not isinstance(data, dict):
        return {"available": False, "error": "manifest 非对象（%s）" % type(data).__name__, "path": path}
    count = data.get("count")
    skills = data.get("skills")
    if count is None or not isinstance(skills, list):
        return {"available": False, "error": "缺 count 或 skills 数组", "path": path}
    return {"available": True, "count": count, "skills_len": len(skills),
            "self_consistent": count == len(skills), "schema": data.get("schema"),
            "generated": data.get("generated"), "path": path}


def denominator(scanned, junctions=(), errors=(), glob_total=None, manifest_path=None):
    """三口径对账：本次纳入 / 磁盘 glob / 焚诀注册表。glob 与注册表不等 → 显式判不一致。"""
    if glob_total is None:
        glob_total = scanned + len(junctions) + len(errors)
    reg = registry_denominator(manifest_path)
    d = {"scanned": scanned, "junction_skipped": list(junctions), "parse_errors": len(errors),
         "glob_total": glob_total, "registry": reg,
         "registry_cmd": REGISTRY_CMD}
    if reg.get("available"):
        d["consistent"] = (glob_total == reg["count"])
        d["delta"] = glob_total - reg["count"]
    else:
        d["consistent"] = None
        d["delta"] = None
    return d


def denominator_lines(d):
    """把 denominator() 结果格式化成 stdout/MD 行（缺口径也必须有可见行，禁静默）。"""
    reg = d.get("registry", {})
    lines = ["口径对账: 本次纳入 %d | 磁盘 glob %d（junction 跳过 %d: %s | 解析错误 %d）" % (
        d["scanned"], d["glob_total"], len(d["junction_skipped"]),
        ",".join(d["junction_skipped"]) or "-", d["parse_errors"])]
    if reg.get("available"):
        tag = "一致" if d.get("consistent") else "不一致(Δ=%s)" % d.get("delta")
        lines.append("焚诀注册表口径: count=%s / skills=%s（%s, %s, generated=%s）→ 与磁盘 glob %s" % (
            reg["count"], reg["skills_len"], reg.get("schema"),
            "manifest 自洽" if reg.get("self_consistent") else "manifest 内部分歧",
            reg.get("generated"), tag))
    else:
        lines.append("焚诀注册表口径: 不可用（%s）→ 本表分母仅磁盘 glob，禁止引用为全库分母"
                     % reg.get("error"))
    lines.append("取值命令: %s" % d.get("registry_cmd", REGISTRY_CMD))
    return lines
