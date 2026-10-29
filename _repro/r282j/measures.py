# -*- coding: utf-8 -*-
# Independent re-implementation of the six-dim mechanical rubric declared in
# 06-benchmark/r281_artifact_ab.json > rubric_definition (dims rules + EDGES).
# Written from the DECLARED rule text, not imported from 05-exec/r281g_score.py.
# Quoting discipline: no backslash or backtick literals in this file - chr(92)/chr(96).
import hashlib
import io
import os
import re
import subprocess

GS = "D:/global_skills"
DIMS = ["d1", "d2", "d3", "d4", "d5", "d6"]

B = chr(92)          # one backslash
BT = chr(96)         # one backtick
SQ = chr(39)         # one single quote
DQ = chr(34)         # one double quote
DD = B + "d"         # regex digit class
SS = B + "s"
DOT = B + "."        # regex literal dot

RE_FLAG = re.compile("--[A-Za-z][A-Za-z0-9_-]*")
RE_FENCE = re.compile("^" + SS + "*" + BT * 3 + "([A-Za-z0-9_+-]*)" + SS + "*$")
FENCE_LANGS = set(["python", "py", "bash", "sh", "shell", "zsh", "console", "powershell", "ps1"])
RE_BULLET = re.compile("^" + SS + "*(?:[-*+]|" + DD + "+[.)])" + SS + "+" + B + "S")
RE_TABLEROW = re.compile("^" + SS + "*" + B + "|.*" + B + "|" + SS + "*$")
RE_FORBID = re.compile("不|勿|禁|never|avoid|don" + SQ + "?t", re.I)
RE_SPEC = [
    re.compile(DD + "+(?:" + DOT + DD + "+)?" + SS + "*(?:px|rem|em|%|pt|ms|fps|dpi|KB|MB|GB|x" + B + "b|:1)", re.I),
    re.compile(DD + "+(?:" + DOT + DD + "+)?[:/]" + DD + "+(?:" + DOT + DD + "+)?"),
    re.compile(DD + "{3,}"),
    re.compile(DD + "+" + DOT + DD + "+"),
]
RE_CHECK = re.compile("verify|checklist|校验|确认", re.I)
EXTS = ["md", "py", "sh", "css", "json", "html", "js", "ts", "tsx", "yml", "yaml", "csv",
        "ttf", "woff", "woff2", "svg", "png", "jpg", "jpeg", "webp", "jsonl"]
RE_PATHY = re.compile("[A-Za-z0-9_.+-]+(?:" + DOT + "(?:" + "|".join(EXTS) + "))" + B + "b")
RE_HAS_EXT = re.compile(DOT + "(?:" + "|".join(EXTS) + ")$")
RE_TICKSPAN = re.compile(BT + "([^" + BT + B + "n]{1,200})" + BT)
RE_ATTR = re.compile("(?:src|href|action)" + SS + "*=" + SS + "*[" + SQ + DQ + "]?([^" + SQ + DQ + B + "s]+)", re.I)
BADCH = set("<>{}" + BT + "$" + SQ + DQ + "()|,;: " + chr(9))


def lines_of(t):
    return t.replace(chr(13) + chr(10), chr(10)).replace(chr(13), chr(10)).split(chr(10))


def sha256_text(t):
    return hashlib.sha256(t.encode("utf-8", "replace")).hexdigest()


def git_show_text(ref, rel):
    r = subprocess.run(["git", "-C", GS, "show", ref + ":" + rel], capture_output=True, timeout=180)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", "replace")


def git_bytes(ref, rel):
    r = subprocess.run(["git", "-C", GS, "show", ref + ":" + rel], capture_output=True, timeout=180)
    if r.returncode != 0:
        return None, None
    return r.stdout, r.stdout.decode("utf-8", "replace")


def git_rev_parse(ref):
    r = subprocess.run(["git", "-C", GS, "rev-parse", ref], capture_output=True, timeout=60)
    return (r.stdout or b"").decode("utf-8", "replace").strip()


def git_show_meta(ref):
    r = subprocess.run(["git", "-C", GS, "show", "--no-patch", "--format=%H%x09%ad%x09%s", "--date=format:%Y-%m-%d %H:%M", ref],
                       capture_output=True, timeout=60)
    return (r.stdout or b"").decode("utf-8", "replace").strip()


def read_worktree(skill):
    p = os.path.join(GS, skill, "SKILL.md")
    if not os.path.isfile(p):
        return None
    with io.open(p, "rb") as f:
        return f.read().decode("utf-8", "replace")


def my_bucket(edges, raw):
    """declared: score = #{e in EDGES[dim] : raw >= e}, max 5."""
    n = 0
    for e in edges:
        if raw >= e:
            n += 1
        else:
            break
    return min(5, n)


def m_d1(t):
    flags = [x for x in RE_FLAG.findall(t) if x != "--help"]
    code = 0
    inside = False
    ok = False
    for ln in lines_of(t):
        m = RE_FENCE.match(ln)
        if m and not inside:
            inside = True
            ok = (m.group(1) or "").lower() in FENCE_LANGS
            continue
        if m and inside:
            inside = False
            ok = False
            continue
        if inside and ok and ln.strip():
            code += 1
    return {"flag_refs": len(flags), "code_lines": code, "raw": len(flags) + code}


def m_d2(t):
    hits = []
    for i, ln in enumerate(lines_of(t)):
        if (RE_BULLET.match(ln) or RE_TABLEROW.match(ln)) and RE_FORBID.search(ln):
            hits.append(i + 1)
    return {"raw": len(hits)}


def m_d3(t):
    return {"raw": sum(1 for ln in lines_of(t) if any(rx.search(ln) for rx in RE_SPEC))}


def m_d4(t):
    return {"raw": sum(1 for ln in lines_of(t) if RE_CHECK.search(ln))}
