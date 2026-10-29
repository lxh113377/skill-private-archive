# -*- coding: utf-8 -*-
# R282 three-arm reconcile: main judge.
# - re-derives every G cell with rubric.py (own implementation of the DECLARED rules),
#   compares cell by cell with the published G arm -> mismatch list;
# - requirement A: recompute the ui-ux uplift with the before text swapped to 3c72867d;
# - requirement B: band-flattening cases + raw-sum caliber;
# - requirement C: independent d6 direction mapping check;
# - requirement D: denominator set difference Lead(87) vs F(93) computed from disk.
# Read-only on the three originals: nothing here writes 05-exec/*, 06-benchmark/r278_*,
# 06-benchmark/r281_* or D:/global_skills.
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import difflib
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measures import GS, DIMS, lines_of, my_bucket, git_show_text, git_rev_parse, read_worktree, sha256_text
from rubric import score_text, skill_tree

ROOT = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
BENCH = os.path.join(ROOT, "06-benchmark")
TMP = os.path.join(ROOT, "_temp", "r282j")
G_DEFAULT = os.path.join(BENCH, "r281_artifact_ab.json")
LEAD_JSON = os.path.join(BENCH, "r278_landing_effect.json")
F_JSON = os.path.join(BENCH, "r278_before_after_control.json")
R268_JSON = os.path.join(BENCH, "r268_unreferenced_siblings.json")
SKILLS = ["test-driven-development", "frontend-slides", "ui-ux-pro-max"]


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True)


def mtime_gate(paths):
    out = {}
    now = datetime.now(timezone.utc)
    for p in paths:
        st = os.stat(p)
        m = datetime.fromtimestamp(st.st_mtime, timezone.utc)
        out[os.path.basename(p)] = {"mtime_utc": m.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    "age_sec": int((now - m).total_seconds()),
                                    "sha256_12": hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]}
    return out


# ---------------------------------------------------------------- denominator face
EXEMPT_NAMES = set(["LICENSE", "NOTICE", ".upstream", "SKILL.md"])
EXEMPT_PLATFORM = set(["meta.json", "_meta.json", "_skillhub_meta.json"])
EXEMPT_PLATFORM_DIRS = (".claude-plugin/",)


def lead_caliber(skill):
    """mirror of 05-exec/r268_unreferenced_siblings.walk_files (Lead denominator rule)."""
    d = os.path.join(GS, skill)
    counted = []
    exempt = []
    pruned_dirs = []
    for dirpath, dirnames, filenames in os.walk(d):
        kept = []
        for x in dirnames:
            if x.startswith(".") or x in ("__pycache__", "node_modules"):
                rel = os.path.relpath(os.path.join(dirpath, x), d).replace(os.sep, "/")
                pruned_dirs.append(rel + "/")
            else:
                kept.append(x)
        dirnames[:] = kept
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), d).replace(os.sep, "/")
            if fn in EXEMPT_NAMES or fn.lower() in ("license", "notice") or fn in EXEMPT_PLATFORM or rel.startswith(EXEMPT_PLATFORM_DIRS):
                exempt.append(rel)
                continue
            if fn.startswith("."):
                exempt.append(rel + "  (dotfile-skip)")
                continue
            if rel == "SKILL.md":
                continue
            counted.append(rel)
    return sorted(counted), sorted(exempt), sorted(pruned_dirs)


def f_caliber(skill, extra=False):
    # mirror of _repro/r278c/r278c_drive.sh step2: find <skill> -type f (no exclusions),
    # then _repro/r278c/r278c_metrics.py drops every listing line ending with SKILL.md.
    # extra=True keeps the nested mirror SKILL.md (the 93 -> 94 variant of the denominator).
    d = os.path.join(GS, skill)
    rows = []
    for dirpath, dirnames, filenames in os.walk(d):
        for fn in filenames:
            rows.append(os.path.relpath(os.path.join(dirpath, fn), d).replace(os.sep, '/'))
    rows = sorted(rows)
    if extra:
        kept = [x for x in rows if x != 'SKILL.md']
    else:
        kept = [x for x in rows if not x.endswith('SKILL.md')]
    return rows, kept

def hit_path_or_base(text, files):
    """strict-ish hit used by BOTH arms: full relative path in text OR basename in text."""
    hits = []
    for rel in files:
        base = rel.rsplit("/", 1)[-1]
        if (rel in text) or (base and (base in text)):
            hits.append(rel)
    return hits


def loose_files(text, files):
    """F loose / r268-ish: path OR basename OR direct parent dir name + slash."""
    hits = []
    for rel in files:
        base = rel.rsplit("/", 1)[-1]
        head = rel.rsplit("/", 1)[0] if "/" in rel else ""
        parent = head.rsplit("/", 1)[-1] if "/" in head else head
        if (rel in text) or (base and (base in text)) or (parent and (parent + "/" in text)):
            hits.append(rel)
    return hits


def r268_normal_files(text, files):
    """Lead normal caliber = r268.classify: path / backslash-token / basename / parent dir name
       (no slash required) / any weak ancestor dir name."""
    toks = set(m.strip() for m in re.findall("[A-Za-z0-9_][A-Za-z0-9_./-]*\\.(?:md|json|txt|py|css|js|html|sh|ya?ml)", text or ""))
    hits = []
    for rel in files:
        base = rel.rsplit("/", 1)[-1]
        dirs = rel.split("/")[:-1]
        ref = False
        if rel in text:
            ref = True
        if not ref:
            for t in toks:
                if t.replace(chr(92), "/").endswith(rel):
                    ref = True
                    break
        if not ref and base and (base in text):
            ref = True
        if not ref:
            for dd in dirs:
                if len(dd) >= 3 and dd in text:
                    ref = True
                    break
        if ref:
            hits.append(rel)
    return hits


RE_TOK = re.compile('[A-Za-z0-9_][A-Za-z0-9_./-]*\\.(?:md|json|txt|py|css|js|html|sh|ya?ml)')


def referenced_tokens(text):
    return set(m.strip() for m in RE_TOK.findall(text or ''))


def lead_strict_unreferenced(text, files):
    # faithful mirror of 05-exec/r278_landing_effect.strict_unreferenced (4 rules):
    # 1 relative path in text  2 basename in text  3 a path-shaped token ENDS WITH rel
    # 4 direct parent dir name (len>=3) + '/' in text. Kept separate from F's 2-rule
    # strict so the rule gap between arms is measurable instead of assumed away.
    out = []
    toks = referenced_tokens(text)
    for rel in files:
        base = rel.rsplit('/', 1)[-1]
        dirs = rel.split('/')[:-1]
        ref = (rel in text) or (bool(base) and (base in text))
        if not ref:
            for tok in toks:
                if tok.replace(chr(92), '/').endswith(rel):
                    ref = True
                    break
        if not ref and dirs and len(dirs[-1]) >= 3 and (dirs[-1] + '/') in text:
            ref = True
        if not ref:
            out.append(rel)
    return out


def rule_flip(text, files):
    # where the two strict RULES disagree on the same file set: Lead's 4-rule strict is more
    # lenient (extra rules: path-shaped token ending with rel, parent dir name + slash).
    lead_un = set(lead_strict_unreferenced(text, files))
    hit_f = set(hit_path_or_base(text, files))
    f_un = set(x for x in files if x not in hit_f)
    return {'only_unreferenced_under_lead_rule': sorted(lead_un - f_un),
            'only_unreferenced_under_f_rule': sorted(f_un - lead_un),
            'flipped_n': len(lead_un - f_un) + len(f_un - lead_un),
            'rule_gap': len(f_un) - len(lead_un)}
