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
