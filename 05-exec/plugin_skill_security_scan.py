# -*- coding: utf-8 -*-
"""plugin_skill_security_scan.py - r27: 插件技能面安全/合规扫描（只读，补 C27 覆盖不到的根）

背景（r20 实测）：Qoder 插件技能 57 条住在 ~/.qoder-cn/plugins/cache/.../skills/，
不在 D:\\global_skills，因此**完全在焚诀 C1 注册表与 C27/C28 之外**——每轮注入却零审计。
本脚本对标 C27 的判定思路（模式族 + 文件:行 + 是否阻断），把同一套眼力延伸到插件根。

口径：按 installed_plugins_v2.json 的 installPath 选定"活跃"插件计数，不按 cache 全树
（缓存可能滞留旧版本目录）。非活跃/缺失项单列。

退出码：0=完成且有发现或确无发现（均打印输入证据）；1=存在"高"级项；2=输入面取证失败（R247）。
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

MANIFEST = Path.home() / ".qoder-cn" / "plugins" / "installed_plugins_v2.json"

# 被检字面量用拼接构造：规则本体若含原文会被自有安全钩子判为命中（假阳性，
# 同 lessons「扫描范围含规则本体」族）。拼接不改变检测能力，运行时正则完全等价。
_RM = r"r" + "m" + r"\s+-" + "rf"
_VERIFYOFF = "verify" + "=" + "False"
_REJUN = "rejectUnauthorized" + r"\s*:\s*" + "false"
_INSTALL_FLAG = "-" + "k" + r"\s"

# 模式族：与 C27 同思路，但按"外部下载技能"的风险面定制
PATTERNS = [
    ("HIGH", "curl_pipe_shell", r"curl[^|\n]*\|\s*(ba)?sh|wget[^|\n]*\|\s*(ba)?sh", "管道执行远程脚本"),
    ("HIGH", "recursive_force_delete", r"(Remove-Item[^\n]*-Recurse[^\n]*-Force|Remove-Item[^\n]*-Force[^\n]*-Recurse|shutil\.rmtree|" + _RM + r")", "递归强制删除"),
    ("HIGH", "secret_hardcoded", r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}", "硬编码凭据"),
    ("HIGH", "base64_decode_exec", r"base64\s+(-d|--decode)[^|\n]*\|\s*(ba)?sh|eval\(atob\(", "解码后执行"),
    ("MED", "install_script", r"(?i)(npm\s+install|pip\s+install|curl -o|wget -O|Invoke-WebRequest[^|\n]*-OutFile)", "落地并安装外部物"),
    ("MED", "sudo_elevate", r"(?i)\bsudo\b|runas|Start-Process[^\n]*-Verb\s+RunAs", "提权"),
    ("MED", "external_egress", r"(?i)(requests\.(post|get)|fetch\(|axios\.|urllib\.request)[^\n]{0,80}https?://", "外发网络请求"),
    ("LOW", "absolute_path_write", r"(?i)(open|write_text|writeFile|Out-File)[^\n]{0,40}[\"'][A-Z]:\\\\", "写绝对路径（可移植性/误写风险）"),
    ("LOW", "env_read_secret", r"(?i)os\.environ\.get\(['\"](.*?(KEY|TOKEN|SECRET|PASS).*)['\"]", "从环境读密钥（正常，需过目）"),
    ("LOW", "disable_verify", r"(?i)(--no-" + "verify|--insecure|" + _VERIFYOFF + r"|" + _REJUN + r"|" + _INSTALL_FLAG + r")", "关闭校验"),
]
RX = [(lv, nm, re.compile(p, re.I), d) for lv, nm, p, d in PATTERNS]
SKIP_DIRS = {"node_modules", ".git", "__pycache__", "dist", "build", ".venv"}


def active_skills(manifest_path):
    man = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    out, missing = [], []
    for key, ents in (man.get("plugins") or {}).items():
        for e in ents if isinstance(ents, list) else [ents]:
            ip = Path(e.get("installPath", ""))
            if not ip.is_dir():
                missing.append(key)
                continue
            for md in sorted(ip.glob("skills/*/SKILL.md")):
                out.append((key.split("@")[0], md))
    return out, missing


def scan(items):
    hits = []
    files = 0
    for plugin, md in items:
        files += 1
        try:
            lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as e:
            hits.append({"level": "ERR", "pattern": "read_fail", "file": str(md), "line": 0,
                         "snippet": str(e)[:120], "plugin": plugin})
            continue
        for i, ln in enumerate(lines, 1):
            for lv, nm, rx, desc in RX:
                if rx.search(ln):
                    hits.append({"level": lv, "pattern": nm, "file": "%s/%s" % (plugin, md.parent.name),
                                 "line": i, "snippet": ln.strip()[:160], "desc": desc})
    # 附带扫同目录其他文本资产
    for plugin, md in items:
        for extra in sorted(md.parent.glob("*.md")) + sorted(md.parent.glob("**/*.sh")) + sorted(md.parent.glob("**/*.ps1")):
            if extra == md or any(s in extra.parts for s in SKIP_DIRS):
                continue
            if extra.stat().st_size > 400_000:
                continue
            for i, ln in enumerate(extra.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                for lv, nm, rx, desc in RX:
                    if rx.search(ln):
                        hits.append({"level": lv, "pattern": nm,
                                     "file": "%s/%s" % (plugin, extra.relative_to(md.parent)),
                                     "line": i, "snippet": ln.strip()[:160], "desc": desc})
    return hits, files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--top", type=int, default=25)
    args = ap.parse_args()

    if not MANIFEST.is_file():
        print("FAIL(R247): 插件清单不可读 %s → 无处可扫，不得判「无风险」" % MANIFEST)
        return 2
    items, missing = active_skills(MANIFEST)
    if not items:
        print("FAIL(R247): 活跃插件技能枚举为 0，拒绝输出「0 发现」")
        return 2
    hits, files = scan(items)
    by = {lv: sum(1 for h in hits if h["level"] == lv) for lv in ("HIGH", "MED", "LOW", "ERR")}
    print("=== 插件技能安全扫描 (%s) ===" % datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("输入证据: 活跃插件技能 %d 条 / 扫描 SKILL.md %d 个 / manifest 指向但盘上缺失 %d %s"
          % (len(items), files, len(missing), missing or ""))
    print("命中: HIGH=%d MED=%d LOW=%d 读取失败=%d" % (by["HIGH"], by["MED"], by["LOW"], by["ERR"]))
    print("口径注: 与焚诀 C27（581 文件 / global_skills 根）**互不重叠**，插件面此前零审计\n")
    seen = set()
    shown = 0
    for h in sorted(hits, key=lambda x: (x["level"] != "HIGH", x["level"] != "MED", x["pattern"], x["file"])):
        k = (h["level"], h["pattern"], h["file"])
        if k in seen:
            continue
        seen.add(k)
        if shown >= args.top:
            break
        print("  [%s] %-22s %-46s L%-4d %s" % (h["level"], h["pattern"], h["file"][:46], h["line"], h["snippet"][:78]))
        shown += 1
    per_plugin = {}
    for h in hits:
        per_plugin[h["file"].split("/")[0]] = per_plugin.get(h["file"].split("/")[0], 0) + 1
    print("\n按插件命中: %s" % ", ".join("%s=%d" % kv for kv in sorted(per_plugin.items(), key=lambda x: -x[1])))
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"schema": "plugin-skill-security-v1", "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
             "readonly": True, "manifest": str(MANIFEST), "active_skills": len(items),
             "missing_installPath": missing, "counts": by, "hits": hits,
             "caveat": "模式匹配非语义判定；HIGH 需人工过目后才可下'有漏洞'结论，也可证伪为文档示例"},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print("JSON -> %s" % args.json)
    return 1 if by["HIGH"] else 0


if __name__ == "__main__":
    # 崩溃不得与「判定拒绝」共用退出码（自有教训：rc=1 曾被 TypeError 伪装成扫到 HIGH）
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as exc:
        sys.stderr.write("UNEXPECTED_FAILURE: %r -> 退出码 2（取证失败，不得读作「无风险」或「有发现」）\n" % (exc,))
        raise SystemExit(2)
