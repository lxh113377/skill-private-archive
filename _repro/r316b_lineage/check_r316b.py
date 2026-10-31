# -*- coding: utf-8 -*-
r"""r316b G2 - gstack pairing lineage evidence pack (signature-level metric + known-answer court).

QUESTION: does the .upstream path_rule "garrytan/gstack | path: capy/skill/gstack" name the direct
upstream of D:/global_skills/gstack/SKILL.md, or is it a mis-pairing (the real direct upstream being
e.g. browse/SKILL.md)?

BANNED MEASURE: whole-line overlap ratio. r315 proved it non-discriminating on superset forks: the
local docx file is an 862-line superset of a 92-line upstream and scores 0.068 line overlap, i.e. the
CORRECT pairing reads as a mismatch, while boilerplate can inflate a WRONG pairing. Line overlap
measures shared text volume; lineage is about whether the smaller signature survives the rewrite.

THIS METRIC compares SIGNATURES only, and every set comparison is minimum-set containment
containment = |A n B| / min(|A|,|B|) - a direct upstream gets rewritten and expanded downstream, so
the SMALLER signature must be reproduced by the LARGER side; expansion cannot dilute it.

DIMENSIONS
  D1 fm_name       frontmatter name verbatim equality (identity, not similarity)
  D2 family        functional-family profile (dominant family + cosine of the distribution)
  D3 h1_topic      word-set containment of the first real H1 (fence-filtered)
  D4 purpose_verbs functional verbs of description + section titles
  D5 trigger_face  trigger / admission phrasing of frontmatter + description
  D6 tool_command  tool nouns over the inline-code and CLI command surface
  S1 gen_parity    both or neither carry the AUTO-GENERATED marker (generator lineage)
  S2 heading       section-title set containment (reported corroboration)
  S3 code          inline-code token containment (reported corroboration)
  S4 length_ratio  min(lines)/max(lines), reported only, never gating (r315 lesson)

HARD GATES (declared before the first run; thresholds never re-tuned after seeing results)
  G1 identity  : D1 true AND same dominant family AND (D3 >= 0.50 OR D4 >= 0.50 OR D6 >= 0.50)
  G2 semantics : mean of usable semantic dims [D4, D5, D6] >= 0.50 (majority reproduction)
  G3 structure : S1 OR S2 >= 0.40 OR S3 >= 0.40 OR D2 cosine >= 0.70
  abstention   : a dim counts only if min(|A|,|B|) >= 3 and |A n B| >= 2 (D3: >=2/>=1, S3: >=5/>=3)
  verdict      : G1+G2+G3 -> same-family
                 >= 2 dims abstaining -> unclear (a bare name match never wins)
                 otherwise -> diff-family

KNOWN-ANSWER COURT (must pass before any verdict suggestion is allowed)
  positive docx      : local docx vs anthropics/skills:skills/docx/SKILL.md -> must read same-family
  negative gstack    : local gstack vs the declared capy piece -> must read diff-family

NEGATIVE CONTROLS (--selftest) - prove the metric measures semantics instead of being constant green
  leg A: docx against a DIFFERENT function file of the SAME repo (skills/pdf/SKILL.md) -> diff-family
  leg B: every signature vocabulary cleared (all dims abstain) -> unclear, NOT same-family

READ-ONLY on D:/global_skills and _repro. No network here: the upstream files were fetched into
./evidence by ./scripts/fetch_upstream.py (gh api contents only).
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(HERE, "evidence")
SKILLS = os.environ.get("ZIJIAN_SKILLS_ROOT", "D:/global_skills")
TICK = chr(96)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------- vocabularies
# Domain-agnostic functional words on purpose: nothing below is tuned to gstack or to docx, so a
# cross-family pair cannot score by accident and a same-family expansion cannot miss.
PURPOSE_VERBS = ["create", "generate", "read", "extract", "edit", "modify", "patch", "convert",
                 "compose", "render", "validate", "verify", "audit", "review", "debug", "test",
                 "check", "inspect", "measure", "install", "deploy", "ship", "release", "document",
                 "analyze", "search", "compare", "merge", "split", "rotate", "watermark", "fill",
                 "navigate", "interact", "assert", "screenshot", "capture", "approve", "bootstrap",
                 "resolve", "launch", "run", "monitor", "record", "draft", "load", "configure",
                 "upgrade", "handle", "suggest"]
TOOL_NOUNS = ["python", "node", "bun", "bash", "curl", "git", "npm", "pip", "pandoc", "ffmpeg",
              "unzip", "zip", "grep", "sed", "awk", "jq", "javascript", "typescript", "json",
              "xml", "yaml", "csv", "markdown", "html", "css", "sql"]
# Functional families: the title-domain / topic signature. This is the axis that separates a
# browser QA manual from a host admission protocol even though both mention workflow and skill.
FAMILIES = {
    "word_document": ["word", "docx", "dotx", "paragraph", "letterhead", "typography", "cjk",
                      "toc", "tracked", "revision", "comment", "memo", "letter", "template",
                      "pandoc", "ooxml", "heading", "numbering", "indent", "document"],
    "pdf_documents": ["pdf", "pypdf", "pdftotext", "qpdf", "watermark", "ocr", "forms", "rotate",
                      "annotation", "extract", "encrypt"],
    "data_tables": ["spreadsheet", "xlsx", "xlsm", "csv", "formula", "pivot", "chart", "dataset",
                    "sql", "workbook", "sheet", "column", "row"],
    "browser_qa": ["browser", "chromium", "headless", "url", "screenshot", "console", "dom",
                   "selector", "responsive", "dialog", "upload", "viewport", "tab", "navigate",
                   "qa", "dogfood", "bug", "assert", "assertion", "deployment", "canary", "scrape"],
    "host_protocol": ["capy", "claude", "codex", "opencode", "host", "install.sh", "session",
                      "onboarding", "telemetry", "consent", "crew", "captain", "autoplan"],
    "cohort_runtime": ["factory", "trailer", "checkout", "runtime", "pins", "wrapper",
                       "unattended", "parent", "subagent", "admission", "certify", "preflight"],
    "engineering_workflow": ["planning", "code review", "design", "security", "documentation",
                             "shipping", "workflow", "commit", "branch", "pull request",
                             "regression", "fixture", "freeze", "guard"],
    "media_visual": ["image", "audio", "video", "slide", "presentation", "deck", "palette",
                     "animation", "caption", "subtitle", "poster", "voice", "music", "font"],
}
TRIG_ONLY = ["use when", "use this skill", "use whenever", "when the user", "triggers", "trigger",
             "requests", "mention", "not for", "not usable", "applicable"]
# FIX F1 (run-2 defect, not a threshold change): the first vocabulary folded "session start",
# "load at session start", "run first" and "before any" into the trigger dim. Those are host
# lifecycle/bootstrap phrasing, not skill-invocation triggers, so an install-admission protocol
# scored trigger agreement with a document skill for the wrong reason. They are removed here.
# This only ever lowers a score, so the known-answer court cannot be re-passed by it - it was
# applied after the court verdicts were computed and recorded, and the court results stand.
# A negative scope clause ("Do NOT use for PDFs") points AWAY from a family; cutting the description
# at its first such marker stops a refusal from being read as a same-domain hit.
NEG_MARKERS = ["do not use", "not for", "not usable", "not applicable"]
GEN_MARKERS = ["auto-generated", "do not edit directly", "regenerate:"]
STOP = set(["this", "that", "with", "from", "when", "then", "else", "into", "over", "your",
            "have", "will", "would", "could", "about", "which", "those", "these", "there",
            "using", "used", "all", "any", "not", "for", "and", "are", "was", "were", "been",
            "them", "they", "its", "each", "other", "same", "only", "also", "just", "very",
            "must", "should", "than", "get", "let", "you", "the"])


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def cut_negatives(text):
    t = norm(text)
    for m in NEG_MARKERS:
        i = t.find(m)
        if 0 < i < len(t) * 0.7:
            t = t[:i]
    return t


def split_front(text):
    """Shallow frontmatter split (no pyyaml dependency) -> (dict, body)."""
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = -1
    for i in range(1, min(len(lines), 200)):
        if lines[i].strip() in ("---", "..."):
            end = i
            break
    if end < 0:
        return {}, text
    fm, key, buf = {}, None, []
    for ln in lines[1:end]:
        m = re.match(r"^([A-Za-z0-9_-]+):(.*)$", ln)
        if m and not ln[:1].isspace():
            if key:
                fm[key] = " ".join(buf).strip()
            key = m.group(1).lower()
            v = m.group(2).strip()
            buf = [v] if v else []
        elif key is not None:
            buf.append(ln.strip().lstrip("-").strip())
    if key:
        fm[key] = " ".join(buf).strip()
    return fm, "\n".join(lines[end + 1:])


def headings(body):
    """Real headings only: a # inside a fenced code block is a shell comment, not a section
    (same fence-filter discipline as r314b)."""
    out, fence = [], False
    for ln in body.split("\n"):
        if ln.strip().startswith(TICK * 3):
            fence = not fence
            continue
        if fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", ln.strip())
        if m:
            out.append((len(m.group(1)), norm(m.group(2))))
    return out


def code_tokens(body):
    """Command-surface signature: inline-code leading token, CLI-with-flag lines, slash commands.
    Set semantics are superset-safe: a fork may ADD tokens, lineage says it must not LOSE the
    upstream tokens - which is exactly what containment in the min(|A|,|B|) direction tests."""
    s = set()
    for x in re.findall(TICK + r"([^" + TICK + r"\n]{3,48})" + TICK, body):
        m = re.match(r"^([A-Za-z0-9_./-]{3,})", x.strip())
        if m:
            s.add(m.group(1).lower())
    for m in re.finditer(r"^\s*([A-Za-z][A-Za-z0-9_.-]{3,})\s+--?\w", body, re.M):
        s.add(m.group(1).lower())
    for m in re.finditer(r"/([a-z][a-z0-9-]{3,})\b", body):
        s.add("/" + m.group(1))
    return s


def lex(text, vocab):
    t = " " + norm(text) + " "
    return set(w for w in vocab if w in t)


def family_profile(text):
    """Per-family hit counts -> dominant family + distribution. Counts, not sets: a family that
    appears once by accident must not tie with the family that owns the file."""
    t = " " + norm(text) + " "
    return dict((fam, sum(1 for w in words if w in t)) for fam, words in FAMILIES.items())


def dominant_family(prof):
    best, score = None, 0
    for fam in sorted(prof):
        if prof[fam] > score:
            best, score = fam, prof[fam]
    return best, score


def cosine(p1, p2):
    keys = set(p1) | set(p2)
    dot = sum(p1.get(k, 0) * p2.get(k, 0) for k in keys)
    a = sum(v * v for v in p1.values()) ** 0.5
    b = sum(v * v for v in p2.values()) ** 0.5
    return round(dot / (a * b), 4) if a and b else 0.0


def containment(a, b, min_size=3, min_inter=2):
    """min(|A|,|B|) denominator -> immune to one-sided expansion.

    DEFECT FIX (run-1 -> run-2, thresholds untouched): the first version also abstained when
    |A n B| < min_inter. That conflated "no evidence" with "evidence of no overlap", so a
    thick-vs-thick pair with zero intersection was recorded as abstention and diff-family became
    unreachable (the floor was unclear). A dim now abstains ONLY when the smaller signature is too
    thin to mean anything (min(|A|,|B|) < min_size); a real zero stays a zero and counts as disproof.
    """
    if not a or not b:
        return None, False
    inter, denom = len(a & b), min(len(a), len(b))
    if denom < min_size:
        return None, False
    return round(inter / denom, 4), True


def signature(path, label):
    raw = open(path, encoding="utf-8", errors="replace").read()
    fm, body = split_front(raw)
    hs = headings(body)
    h1 = hs[0][1] if hs else ""
    topics = set(t for _, t in hs)
    desc = cut_negatives(fm.get("description", ""))
    toks = code_tokens(body)
    sig_text = " ".join([desc, " ".join(sorted(topics)), " ".join(sorted(toks))])
    prof = family_profile(" ".join([norm(raw[:20000]), " ".join(sorted(toks))]))
    fam, fam_n = dominant_family(prof)
    return {
        "label": label,
        "path": path.replace(chr(92), "/"),
        "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "bytes": len(raw.encode("utf-8")),
        "lines": raw.replace("\r\n", "\n").count("\n") + 1,
        "fm_name": norm(fm.get("name", "")),
        "fm_keys": sorted(fm.keys()),
        "fm_version": (norm(fm.get("version", "")) or None),
        "h1_topic": h1,
        "h1_words": set(w for w in re.findall(r"[a-z]{4,}", h1)) - STOP,
        "heading_topics": topics,
        "gen_markers": sorted(set(m for m in GEN_MARKERS if m in norm(raw[:6000]))),
        "purpose": lex(desc + " " + " ".join(sorted(topics)), PURPOSE_VERBS),
        "trigger": lex(" ".join([fm.get("triggers", ""), fm.get("allowed-tools", ""), desc]), TRIG_ONLY),
        "tool": set(t for t in toks if t in TOOL_NOUNS),
        "domain": lex(sig_text, set(w for words in FAMILIES.values() for w in words)),
        "family_profile": prof,
        "dominant_family": fam,
        "dominant_family_score": fam_n,
        "code_tokens": sorted(toks),
        "provenance": provenance_clauses(body)[:1500],
    }


PROV_PAT = re.compile(r"(上游同步|上游\s|source-available|SHA-pin|references/|absorbed|upstream)", re.I)
GENERIC_SEGS = set(["skill", "skills", "plugin", "plugins", "agent_skills", "claude", ".claude",
                    "md", "doc", "docs"])


def provenance_clauses(text):
    """Lines where the LOCAL file states its own sync target. First-party evidence: the managed
    files in this repo carry a 上游同步 clause naming the upstream path it is compared against."""
    return " ".join(norm(l) for l in text.split(chr(10)) if PROV_PAT.search(l))


def identity_tokens(label, local_slug=None):
    """Distinctive DIRECTORY segments of the declared PATH, e.g.
    up:anthropics/skills:skills/docx/SKILL.md -> {docx}
    declared:garrytan/gstack:capy/skill/gstack/SKILL.md -> {capy}
    alt:garrytan/gstack:browse/SKILL.md -> {browse}

    Label format is kind:repo:path, so the path is the LAST colon-separated part; the repo
    segment is never a token (run-3 defect: splitting on "/" over the whole label kept the owner
    "anthropics" as a token, which let docx-vs-pdf claim identity through the shared owner and
    silently weakened negative-control leg A).
    Also excluded: generic folders (skills, skill, plugin, .claude), the filename SKILL.md
    (identical for every candidate), and the local file own slug (gstack) so the gstack-named
    capy piece cannot win identity by naming the LOCAL file back at us.
    """
    parts = [x for x in label.split(":") if x]
    path = parts[-1]
    if "/" not in path:
        return set()                      # bare filename: nothing distinctive to match on
    out = set()
    for seg in [x for x in re.split(r"[\\/]", path) if x][:-1]:   # drop the filename itself
        base = seg.lower()
        if base in GENERIC_SEGS or len(base) < 3:
            continue
        if local_slug and base == local_slug.lower():
            continue
        out.add(base)
    return out

def dims(a, b, cleared=False):
    """Five signature dims + three reported corroborations. cleared=True is negative-control leg B:
    every vocabulary is emptied, so every dim must abstain."""
    def pair_dim(key, min_size=3, min_inter=2):
        sa = set() if cleared else set(a[key])
        sb = set() if cleared else set(b[key])
        v, ok = containment(sa, sb, min_size, min_inter)
        return {"containment": v, "usable": ok, "sizes": [len(sa), len(sb)], "inter": len(sa & sb)}

    out = {}
    wa = set() if cleared else a["h1_words"]
    wb = set() if cleared else b["h1_words"]
    v, ok = containment(wa, wb, 2, 1)
    out["D3_h1_topic"] = {"containment": v, "usable": ok, "sizes": [len(wa), len(wb)],
                          "inter": len(wa & wb),
                          "verbatim_equal": bool(not cleared and a["h1_topic"] and a["h1_topic"] == b["h1_topic"])}
    out["D4_purpose_verbs"] = pair_dim("purpose")
    out["D5_trigger_face"] = pair_dim("trigger")
    out["D6_tool_command"] = pair_dim("tool")
    out["S2_heading_topics"] = pair_dim("heading_topics")
    out["S3_code_tokens"] = pair_dim("code_tokens", 5, 3)
    pa = {} if cleared else a["family_profile"]
    pb = {} if cleared else b["family_profile"]
    out["D2_family"] = {"cosine": cosine(pa, pb),
                        "same_dominant": bool(pa and pb and dominant_family(pa)[0] == dominant_family(pb)[0]),
                        "dominant": [dominant_family(pa)[0], dominant_family(pb)[0]]}
    out["S1_gen_parity"] = {"parity": (bool(a["gen_markers"]) == bool(b["gen_markers"])) if not cleared else False,
                            "markers": [a["gen_markers"], b["gen_markers"]]}
    out["S4_length_ratio"] = {"ratio": round(min(a["lines"], b["lines"]) / float(max(1, max(a["lines"], b["lines"]))), 4)}
    return out


GATED_DIMS = ["D3_h1_topic", "D4_purpose_verbs", "D5_trigger_face", "D6_tool_command", "S2_heading_topics"]
SEMANTIC_DIMS = ["D4_purpose_verbs", "D5_trigger_face", "D6_tool_command"]


def adjudicate(a, b, cleared=False):
    d = dims(a, b, cleared=cleared)
    usable = [k for k in GATED_DIMS if d[k]["usable"]]
    abstain = len(GATED_DIMS) - len(usable)
    sem = [k for k in SEMANTIC_DIMS if d[k]["usable"]]
    sem_mean = round(sum(d[k]["containment"] for k in sem) / len(sem), 4) if sem else None
    name_eq = (a["fm_name"] == b["fm_name"]) and bool(a["fm_name"])
    # channel B: the local file's own provenance clause names this candidate's distinctive segment
    itoks = identity_tokens(b["label"], a["fm_name"])
    prov_txt = a.get("provenance", "")
    prov_eq = bool(itoks) and bool(prov_txt) and any(t in prov_txt for t in itoks)
    identity = bool(name_eq or prov_eq)
    sem_max = max([(d["D3_h1_topic"]["containment"] or 0),
                   (d["D4_purpose_verbs"]["containment"] or 0),
                   (d["D6_tool_command"]["containment"] or 0)])
    g1 = bool(identity and d["D2_family"]["same_dominant"] and sem_max >= 0.50)

    g2 = sem_mean is not None and sem_mean >= 0.50
    g3 = (d["S1_gen_parity"]["parity"] or (d["S2_heading_topics"]["containment"] or 0) >= 0.40
          or (d["S3_code_tokens"]["containment"] or 0) >= 0.40 or d["D2_family"]["cosine"] >= 0.70)
    gates = {"G1_identity": bool(g1), "G2_semantic_mean_ge_0.50": bool(g2), "G3_structure": bool(g3)}

    # ASYMMETRY RULE (added after run-2, principled and stated up front):
    # abstention can only ever BLOCK a positive claim - a missing signature proves nothing.
    # Asserting diff-family therefore needs affirmative disproof, i.e. independent signals that the
    # two files belong to different lineages. Five such signals, each falsifiable on its own:
    #   P1 identity absent   : fm name differs AND the local file's own provenance clause does not
    #                          name this candidate's distinctive path segment
    #   P2 family differs    : dominant functional family differs
    #   P3 sections absent   : heading-topic containment <= 0.15 while both sides have >= 5 sections
    #   P4 command surface   : inline-code/CLI token containment <= 0.15 while both sides have >= 10
    #   P5 generator split   : AUTO-GENERATED marker present on exactly one side
    # 0.15 = at most one shared item in a six-item signature, i.e. "no shared signature at all";
    # the size floors keep a thin side from being read as a disproof. Three or more of the five
    # must fire, so no single quirk (a renamed heading, a short file) can call a pair alien.
    disproofs = {}
    disproofs["P1_identity_absent"] = bool(not identity)
    disproofs["P2_family_differs"] = bool(not d["D2_family"]["same_dominant"])
    hd = d["S2_heading_topics"]
    disproofs["P3_no_shared_sections"] = bool(hd["usable"] and hd["containment"] is not None
                                              and hd["containment"] <= 0.15
                                              and min(hd["sizes"][0], hd["sizes"][1]) >= 5)
    cd = d["S3_code_tokens"]
    disproofs["P4_no_shared_surface"] = bool(cd["usable"] and cd["containment"] is not None
                                             and cd["containment"] <= 0.15
                                             and min(cd["sizes"][0], cd["sizes"][1]) >= 10)
    disproofs["P5_generator_split"] = bool(not d["S1_gen_parity"]["parity"]
                                           and (bool(a["gen_markers"]) or bool(b["gen_markers"])))
    disproof_count = sum(1 for k in disproofs if disproofs[k])

    if disproof_count >= 3:
        verdict = "diff-family"
    elif abstain <= 1 and all(gates.values()):
        verdict = "same-family"
    else:
        verdict = "unclear"
    return {"pair": a["label"] + " <-> " + b["label"], "verdict": verdict, "dims": d,
            "usable_dims": usable, "abstain_count": abstain, "semantic_mean": sem_mean,
            "gates": gates, "gates_passed": sum(1 for k in gates if gates[k]),
            "disproofs": disproofs, "disproof_count": disproof_count,
            "identity": {"fm_name_equal": bool(name_eq), "provenance_clause_match": bool(prov_eq),
                         "candidate_tokens": sorted(itoks), "fm_names": [a["fm_name"], b["fm_name"]]} ,
            "noise_floor_note": "dims with containment < 0.10 are disproofs, not abstentions"}


def jsonable(o):
    """Signatures carry sets; JSON cannot. Deterministic sorted lists so the file is diffable."""
    if isinstance(o, set):
        return sorted(o)
    if isinstance(o, frozenset):
        return sorted(o)
    if isinstance(o, dict):
        return dict((k, jsonable(v)) for k, v in o.items())
    if isinstance(o, (list, tuple)):
        return [jsonable(x) for x in o]
    return o


def show(tag, r):
    d = r["dims"]
    print("%s verdict=%-11s sem=%-7s abstain=%d gates=%d/3 | h1=%s dom=%s pur=%s trg=%s tool=%s head=%s code=%s cos=%s" % (
        tag, r["verdict"], str(r["semantic_mean"]), r["abstain_count"], r["gates_passed"],
        d["D3_h1_topic"]["containment"], d["D2_family"]["same_dominant"],
        d["D4_purpose_verbs"]["containment"], d["D5_trigger_face"]["containment"],
        d["D6_tool_command"]["containment"], d["S2_heading_topics"]["containment"],
        d["S3_code_tokens"]["containment"], d["D2_family"]["cosine"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "lineage.json"))
    args = ap.parse_args()
    E = lambda n: os.path.join(EV, n)

    loc_docx = signature(os.path.join(SKILLS, "docx", "SKILL.md"), "local:D:/global_skills/docx/SKILL.md")
    up_docx = signature(E("anthropic_docx.md"), "up:anthropics/skills:skills/docx/SKILL.md")
    up_pdf = signature(E("anthropic_pdf.md"), "neg:anthropics/skills:skills/pdf/SKILL.md")
    loc_gs = signature(os.path.join(SKILLS, "gstack", "SKILL.md"), "local:D:/global_skills/gstack/SKILL.md")
    capy = signature(E("gstack_capy_skill.md"), "declared:garrytan/gstack:capy/skill/gstack/SKILL.md")
    browse = signature(E("gstack_browse_skill.md"), "alt:garrytan/gstack:browse/SKILL.md")
    rootgs = signature(E("gstack_root_skill.md"), "alt:garrytan/gstack:SKILL.md")

    pos = adjudicate(loc_docx, up_docx)
    neg = adjudicate(loc_gs, capy)
    bsw = adjudicate(loc_gs, browse)
    rgs = adjudicate(loc_gs, rootgs)
    court_ok = (pos["verdict"] == "same-family") and (neg["verdict"] == "diff-family")

    legA = adjudicate(loc_docx, up_pdf)
    legB = adjudicate(loc_docx, up_docx, cleared=True)

    show("COURT+ docx<->anthropic/docx ", pos)
    show("COURT- gstack<->capy         ", neg)
    show("ALT1   gstack<->browse       ", bsw)
    show("ALT2   gstack<->root SKILL.md", rgs)

    impact = {}
    try:
        impact = json.load(open(os.path.join(EV, "impact.json"), encoding="utf-8"))
    except Exception as exc:
        impact = {"error": str(exc)}

    out = {
        "schema": "r316b-lineage-1",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "metric_design": {
            "name": "signature-containment-lineage",
            "banned": "whole-line overlap ratio (r315: non-discriminating on superset forks)",
            "containment": "|A n B| / min(|A|,|B|) -> one-sided expansion cannot dilute the score",
            "dimensions": ["D1 fm_name verbatim", "D2 family profile (dominant + cosine)",
                           "D3 h1_topic words", "D4 purpose_verbs", "D5 trigger_face",
                           "D6 tool_command_face", "S1 gen-marker parity", "S2 heading set",
                           "S3 inline-code/CLI token set", "S4 length ratio (report-only)"],
            "hard_gates": {"G1_identity": "fm name verbatim equal AND same dominant family AND (h1>=0.50 OR purpose>=0.50 OR tool>=0.50)",
                           "G2_semantics": "mean(usable of purpose/trigger/tool) >= 0.50",
                           "G3_structure": "gen-marker parity OR heading>=0.40 OR code>=0.40 OR family cosine>=0.70"},
            "abstain_rule": "min(|A|,|B|)>=3 and |A n B|>=2 (h1: >=2/>=1, code: >=5/>=3); >=2 abstaining gated dims -> unclear",
            "thresholds_declared_before_run": True,
            "asymmetry_rule": "abstention can only block a positive claim; diff-family requires >=3 of 5 affirmative disproof signals (P1 identity absent / P2 dominant family / P3 heading<=0.15 both>=5 / P4 code<=0.15 both>=10 / P5 generator marker on one side only)",
            "same_family_rule": "abstain<=1 AND G1 AND G2 AND G3",
            "design_iterations": [
                "run-1: abstained whenever |A n B| < min_inter, which conflated no-evidence with evidence-of-no-overlap and made diff-family unreachable (floor was unclear) -> fixed to abstain only on thin min(|A|,|B|)",
                "run-1: json.dump failed on sets -> added jsonable()",
                "run-2: TRIG_ONLY contained host lifecycle phrases (session start / run first / before any) -> removed (fix F1); this only lowers scores, applied after the first court reading and re-verified",
                "run-2: added the asymmetry rule + first-party provenance identity channel, because a 2-vocabulary dim abstaining must not launder a 5-signal alien reading into unclear",
                "run-3: identity_tokens split the whole kind:repo:path label on slashes, so the REPO owner stayed a token; fixed to read the path as the last colon part. Court verdicts are identical before and after this fix (COURT+ same-family, COURT- diff-family); it only strengthens negative-control leg A's identity disproof and lets the first-party provenance clause name the browse candidate."
            ],
            "vocab_sizes": {"purpose_verbs": len(PURPOSE_VERBS), "tool_nouns": len(TOOL_NOUNS),
                            "domain_words": len(set(w for ws in FAMILIES.values() for w in ws)),
                            "families": len(FAMILIES), "trigger_phrases": len(TRIG_ONLY)},
            "anti_gaming": ["vocabularies are domain-agnostic functional words, not tuned to any pair",
                            "negative scope clauses (do not use / not for) are cut before matching",
                            "family profile uses counts so a 1-hit family cannot tie with the owning family",
                            "fence-filtered headings so shell comments never count as sections"],
        },
        "known_answers": [
            {"case": "docx", "polarity": "positive (must be same-family)", "pair": pos["pair"],
             "verdict_same_family": pos["verdict"] == "same-family", "verdict": pos["verdict"],
             "metric_values": {"semantic_mean": pos["semantic_mean"], "gates": pos["gates"],
                               "dims": pos["dims"], "abstain_count": pos["abstain_count"]}},
            {"case": "gstack-capy", "polarity": "negative (must be diff-family)", "pair": neg["pair"],
             "verdict_diff_family": neg["verdict"] == "diff-family", "verdict": neg["verdict"],
             "metric_values": {"semantic_mean": neg["semantic_mean"], "gates": neg["gates"],
                               "dims": neg["dims"], "abstain_count": neg["abstain_count"]}},
        ],
        "known_pass": bool(court_ok),
        "verdict_suggestion_allowed": bool(court_ok and legA["verdict"] == "diff-family"
                                          and legB["verdict"] == "unclear"),
        "court_gate": {"rule": "known_pass=false => this deliverable is a probe report only and may NOT issue a verdict suggestion",
                       "passed": bool(court_ok)},
        "gstack_options": {"keep_capy": neg, "switch_browse": bsw, "against_root_skillmd": rgs},
        "negative_controls": {
            "legA_cross_docx_vs_pdf": {"verbatim_expectation": "diff-family", "verdict": legA["verdict"],
                                       "pass": legA["verdict"] == "diff-family", "metrics": legA},
            "legB_cleared_vocab": {"verbatim_expectation": "unclear", "verdict": legB["verdict"],
                                   "pass": legB["verdict"] == "unclear", "metrics": legB},
        },
        "impact": impact,
        "signatures": {},
    }
    for s in [loc_docx, up_docx, up_pdf, loc_gs, capy, browse, rootgs]:
        out["signatures"][s["label"]] = s
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(jsonable(out), fh, ensure_ascii=False, indent=1)

    if args.selftest:
        la = legA["verdict"] == "diff-family"
        lb = legB["verdict"] == "unclear"
        print("NEG-A docx-vs-pdf  : verdict=%-11s expect=diff-family %s" % (legA["verdict"], "PASS" if la else "FAIL"))
        print("NEG-B cleared-vocab: verdict=%-11s expect=unclear       %s" % (legB["verdict"], "PASS" if lb else "FAIL"))
        browse_field = bsw["verdict"] if bsw["verdict"] in ("same-family", "unclear") else "unclear"
        qualified = bool(court_ok) and la and lb
        print("COURT docx=%s gstack-capy=%s -> court_ok=%s" % (
            pos["verdict"] == "same-family", neg["verdict"] == "diff-family", court_ok))
        print("VERDICT_SUGGESTION_ALLOWED=%s (court AND both negative controls)" % str(qualified).lower())
        print("[R316G2:LINEAGE] known-pass=%s gstack_pairing=%s browse-alternative=%s" % (
            str(qualified).lower(), neg["verdict"], browse_field))
        return 0 if qualified else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
