# -*- coding: utf-8 -*-
r"""r21e_gate_patchgen.py — 给 upgrade_footer_gate.py 生成「证据可解析性」补丁 JSON。

old 串一律从**当前真实源码**程序化取（手抄 old 是本轮四次复现的错源）；命中数 != 1 即停手。
生成物 = rule_editor 的 --patch 数组（4 处）。

分级依据 = 同日边界测量（`06-benchmark/evidence_resolvability_measure.json`，近 3 日 97 条已闭环声明）：
  · 可解析 52（53.6%）
  · 形状合规但 token 已被后续提交推走 = 18 ⇒ **只告警**（声明当时可为真；追溯拦人 = 误伤，会把下一个人逼去放宽判据）
  · 路径不存在 / backup ID 五仓与回滚目录全无 = 4 ⇒ **阻断**（不可事后合理化）
"""
import io
import json
import os
import sys

GATE = r"D:\global_skills\A-memory-start\references\upgrade_footer_gate.py"
OUT = r"C:\Users\37533\Desktop\workspace\自建skill优化\05-exec\r21e-patches\patch_gate.json"

RESOLVER = '''
# ── 证据可解析性（2026-09-24 r21e 加；分级依据 = 边界测量 97 条历史声明）──────────
# RE_EVID 只校验形状：形状合格却指不到东西的锚点照样能过（实测近 3 日 97 条里 38.1% 解析不到）。
# 三级 OK / FAKE / STALE：FAKE = 路径不存在，或 backup ID 在回滚目录与五个仓的 git 对象里都定位不到
# （不可事后合理化）⇒ 阻断；STALE = 文件在但版本 token 已被后续提交推走 ⇒ 只告警（追溯拦人即误伤）。
RESOLVE_ROOTS = (r"D:\\global_skills", r"D:\\global_memory", r"D:\\global_memory_archive",
                 r"C:\\Users\\37533\\Desktop\\workspace\\\u711a\u8bc0",
                 r"C:\\Users\\37533\\Desktop\\workspace\\\u81ea\u5efa skill\u4f18\u5316")
RESOLVE_BACKUP_DIR = r"D:\\global_memory_archive\\_trash\\rule_backup"
RE_ANCHOR = re.compile(r"^(?P<path>.+?)#(?P<kind>\u7248\u672c\u884c|backup):(?P<val>.+)$")
EV_ADVISORY = []


def _ev_target(p):
    p = p.strip().strip("`")
    if os.path.isfile(p):
        return p, True
    stripped = re.sub(r"^[A-Za-z]:[\\\\/]", "", p)
    for root in RESOLVE_ROOTS:
        cand = os.path.join(root, stripped.replace("/", os.sep))
        if os.path.isfile(cand):
            return cand, True
    known = any(p.replace("\\\\", "/").lower().startswith(r.replace("\\\\", "/").lower() + "/")
                for r in RESOLVE_ROOTS)
    return p, known


def _ev_git_has(tok):
    for root in RESOLVE_ROOTS:
        if os.path.isdir(os.path.join(root, ".git")) and subprocess.run(
                ["git", "-C", root, "cat-file", "-t", tok], capture_output=True).returncode == 0:
            return True
    return False


def resolve_evidence(val):
    m = RE_ANCHOR.match(val or "")
    if not m:
        return "SKIP", "\u65e0 kind:val \u7ed3\u6784"
    path, known = _ev_target(m.group("path"))
    if not os.path.isfile(path):
        return ("FAKE", "\u8bc1\u636e\u8def\u5f84\u4e0d\u5b58\u5728") if known else ("SKIP", "\u8def\u5f84\u5728\u672c\u4f53\u7cfb\u5916\uff0c\u4e0d\u5224")
    kind, tok = m.group("kind"), m.group("val")
    if kind == "backup":
        if os.path.isdir(RESOLVE_BACKUP_DIR) and any(tok in f for f in os.listdir(RESOLVE_BACKUP_DIR)):
            return "OK", "\u56de\u6eda\u4ef6\u5b58\u5728"
        return ("OK", "git \u5bf9\u8c61\u5b58\u5728") if _ev_git_has(tok) else ("FAKE", "backup ID \u5b9a\u4f4d\u4e0d\u5230")
    try:
        text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return "SKIP", "\u8bc1\u636e\u6587\u4ef6\u8bfb\u4e0d\u5230"
    for cand in {tok, tok.lstrip("V"), "V" + tok.lstrip("V")}:
        if cand and cand in text:
            return "OK", "token \u5728\u6587\u4ef6\u5185"
    return "STALE", "\u7248\u672c token \u5df2\u4e0d\u5728\u8be5\u6587\u4ef6\u5185\uff08\u591a\u4e3a\u540e\u7eed\u63d0\u4ea4\u63a8\u8d70\uff0c\u975e\u865a\u6784\uff09"


def check_evidence(val):
    verdict, reason = resolve_evidence(val)
    if verdict == "FAKE":
        return "\u8bc1\u636e\u951a\u70b9\u89e3\u6790\u4e0d\u5230: " + reason + " -> " + val[:120]
    if verdict == "STALE":
        EV_ADVISORY.append(val[:90] + " \uff08" + reason + "\uff09")
    return None

'''


def one(src, needle, label):
    n = src.count(needle)
    if n != 1:
        raise SystemExit("[GUARD] %s 命中 %d 次（期望 1）⇒ 停手，不生成补丁" % (label, n))
    return needle


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    src = io.open(GATE, encoding="utf-8").read()
    NL = chr(10)
    patches = []

    patches.append({"old": one(src, "import re" + NL + "import sys", "h1"),
                    "new": "import os" + NL + "import re" + NL + "import subprocess" + NL + "import sys"})

    i = src.index("FIX_HINT = (")
    j = src.index("\n\n", src.index('")', i))
    old2 = src[i:j]
    patches.append({"old": one(src, old2, "h2"), "new": RESOLVER.strip("\n") + NL + NL + NL + old2})

    k = src.index('        if state == "' + "已闭环" + '" and not RE_EVID.match(val):')
    m = src.index('        if state == "未闭环"', k)
    old3 = src[k:m].rstrip()
    patches.append({"old": one(src, old3, "h3"),
                    "new": old3 + NL + '        elif state == "已闭环":' + NL +
                           "            _e = check_evidence(val)" + NL +
                            "            if _e:" + NL + "                errs.append(_e)"})

    old4 = ('    if not args.quiet:' + NL + '        print(f"  source: {source}")')
    patches.append({"old": one(src, old4, "h4"),
                    "new": old4 + NL + "    if EV_ADVISORY and not args.quiet:" + NL +
                           '        print(f"  \u26a0\ufe0f \u8bc1\u636e\u5df2\u9648\u65e7\uff08\u4e0d\u963b\u65ad\uff09{len(EV_ADVISORY)} \u6761\uff1a{EV_ADVISORY[0]}")'})

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(patches, ensure_ascii=False, indent=1))
    for n, p in enumerate(patches, 1):
        assert chr(0) not in p["old"] + p["new"] and chr(8) not in p["old"] + p["new"]
        print("  #%d old %d 字符 / new %d 字符" % (n, len(p["old"]), len(p["new"])))
    print("[PATCHGEN] 生成 %d 处 → %s" % (len(patches), OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
