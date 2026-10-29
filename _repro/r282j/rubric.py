# -*- coding: utf-8 -*-
# d5 (sibling pointers, net) + d6 (unsupported flags) + six-dim score assembly.
# Caliber = the one DECLARED in r281_artifact_ab.json > rubric_definition.dims:
#   d5 - only tokens with a directory shape or a known extension; canonicalised against the
#        live artifact tree; shaped-but-unresolvable = dead (subtracted); bare unresolvable
#        name = unresolved (neither added nor subtracted); raw = max(0, live - dead).
#   d6 - distinct --flag references minus the --help support set of that artifact's
#        scripts/*.py; when the interface cannot be established the value stays None.
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measures import (B, BT, DQ, SQ, GS, DIMS, SS, RE_FLAG, RE_PATHY, RE_HAS_EXT,
                      RE_TICKSPAN, RE_ATTR, BADCH, my_bucket)


def skill_tree(skill):
    rels = set()
    byname = {}
    d = os.path.join(GS, skill)
    if not os.path.isdir(d):
        return rels, byname
    for dirpath, dirnames, filenames in os.walk(d):
        dirnames[:] = [x for x in dirnames if x not in ("__pycache__", ".git", "node_modules")]
        for nm in dirnames:
            r = os.path.relpath(os.path.join(dirpath, nm), d).replace(os.sep, "/").lower()
            rels.add(r + "/")
            byname.setdefault(r.split("/")[-1], set()).add(r + "/")
        for nm in filenames:
            r = os.path.relpath(os.path.join(dirpath, nm), d).replace(os.sep, "/").lower()
            rels.add(r)
            byname.setdefault(r.split("/")[-1], set()).add(r)
    return rels, byname


def norm_token(x0, skill):
    x = x0.strip().strip(".,;:()" + DQ).split("#")[0].split(":")[0].strip().replace(B, "/")
    low = x.lower()
    for pre in ("d:/global_skills/", "./", "skills/"):
        if low.startswith(pre):
            low = low[len(pre):]
    if low.startswith(skill.lower() + "/"):
        low = low[len(skill) + 1:]
    if not low or low.startswith(("http", "~", "/")) or re.match("^[a-z]:", low):
        return None
    return low.rstrip("/") + ("/" if x0.rstrip().endswith("/") else "")


def clean_token(x0, skill):
    m = RE_ATTR.search(x0)
    base = m.group(1) if m else x0
    return norm_token(base, skill)


def m_d5(t, skill, tree=None):
    rels, byname = tree if tree else skill_tree(skill)
    spans = set(RE_TICKSPAN.findall(t)) | set(RE_PATHY.findall(t))
    live = set()
    dead = set()
    unres = set()
    for raw0 in spans:
        n = clean_token(raw0, skill)
        if not n or any(c in BADCH for c in n):
            continue
        shaped = "/" in n
        if not shaped and not RE_HAS_EXT.search(n):
            continue
        if "*" in n or "?" in n:
            par = n.split("*")[0].split("?")[0].rstrip("/")
            key = par + "/"
            if key in rels or os.path.exists(os.path.join(GS, skill, par or ".")):
                live.add(key if key != "/" else "")
            else:
                dead.add(key)
            continue
        bare = n.rstrip("/")
        found = None
        for v in (bare, bare + "/", "./" + bare, "./" + bare + "/"):
            if v in rels:
                found = v
                break
        if found is not None:
            live.add(found)
        elif shaped:
            if os.path.exists(os.path.join(GS, bare)) or os.path.exists(os.path.join(GS, bare + "/")):
                live.add(bare)
            else:
                dead.add(bare)
        else:
            m = byname.get(bare)
            if m:
                live.add(min(m))
            else:
                unres.add(bare)
    Lv = sorted(x for x in live if x)
    Dv = sorted(dead)
    Uv = sorted(unres)
    return {"raw": max(0, len(Lv) - len(Dv)), "live_n": len(Lv), "dead_n": len(Dv),
            "unresolved_n": len(Uv), "live_list": Lv, "dead_list": Dv, "unresolved_list": Uv}


def probe_flags(skill):
    """d6 support set, measured live: scripts/*.py --help (independent of the stored list)."""
    d = os.path.join(GS, skill, "scripts")
    if not os.path.isdir(d):
        return {"decidable": False, "supported": [], "why": "no scripts/ dir", "cmds_run": []}
    sup = set()
    cmds = []
    any_ok = False
    py = sys.executable
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".py") or fn == "__init__.py":
            continue
        p = os.path.join(d, fn)
        cmds.append("python -B " + p + " --help")
        try:
            r = subprocess.run([py, "-B", p, "--help"], capture_output=True, timeout=90)
        except Exception:
            continue
        txt = (r.stdout or b"").decode("utf-8", "replace") + chr(10) + (r.stderr or b"").decode("utf-8", "replace")
        if r.returncode == 0 and "usage:" in txt.lower():
            any_ok = True
            for mm in re.findall("--([A-Za-z][A-Za-z0-9_-]*)", txt):
                sup.add("--" + mm)
    why = "" if any_ok else "scripts/*.py expose no usable --help (non-argparse interface)"
    return {"decidable": any_ok, "supported": sorted(sup), "why": why, "cmds_run": cmds}


def m_d6(t, supported, decidable):
    flags = sorted({x for x in RE_FLAG.findall(t) if x != "--help"})
    if not decidable:
        return {"raw": None, "flags": flags, "bad": []}
    sup = set(supported)
    bad = [f for f in flags if f not in sup]
    return {"raw": len(bad), "flags": flags, "bad": bad}


def score_text(t, skill, edges, probe, tree=None):
    from measures import m_d1, m_d2, m_d3, m_d4
    det = {"d1": m_d1(t), "d2": m_d2(t), "d3": m_d3(t), "d4": m_d4(t),
           "d5": m_d5(t, skill, tree), "d6": m_d6(t, probe["supported"], probe["decidable"])}
    raw = {}
    good = {}
    for k in DIMS:
        raw[k] = det[k]["raw"]
    for k in ("d1", "d2", "d3", "d4", "d5"):
        good[k] = None if raw[k] is None else my_bucket(edges[k], raw[k])
    # requirement C rule, implemented independently here: d6 is a BAD dim, so the
    # good-direction band score = 5 - bucket(d6_raw). Any implementation that simply
    # added bucket(d6_raw) would count unsupported flags as an improvement.
    good["d6"] = None if raw["d6"] is None else 5 - my_bucket(edges["d6"], raw["d6"])
    return raw, good, det
