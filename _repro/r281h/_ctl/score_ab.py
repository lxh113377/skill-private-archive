import os, re, json, glob, random, sys

# R281 mechanical rubric scorer. Input = one arm directory's ARTIFACT files only.
# Never reads the version header of the arm's SKILL.md, so scoring is blind to which
# arm is new/old. Every dimension is computed from bytes on disk (paths, regex hits,
# logged rc values) - no subjective judgment.

# ROOT resolves from this file's own location, not cwd: the durable copy lives under
# 自建skill优化/_repro (the parent tree is not a git repo), so it must rerun from any cwd.
# Override with R281_ROOT only if the corpus moves again.
ROOT = os.environ.get('R281_ROOT') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
SKILL_TREE = 'D:/global_skills/ui-ux-pro-max'
LOG_NAMES = ('_exec_log.md', '_toolcount.txt', '_triage.md', '_gen_stdout.txt')

def read(p):
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception:
        return ''

def files_in(arm):
    return sorted(p for p in glob.glob(os.path.join(arm, '**', '*'), recursive=True) if os.path.isfile(p))

def artifact_files(arm):
    return [p for p in files_in(arm) if os.path.basename(p) != 'SKILL.md']

def delivery_files(arm):
    return [p for p in artifact_files(arm) if os.path.basename(p) not in LOG_NAMES]

def text_of(paths):
    return chr(10).join(read(p) for p in paths)

# ---------- dim 1: artifact existence (design-system dir + MASTER.md) ----------
def dim1(arm):
    ds = os.path.join(arm, 'design-system')
    ev, s = [], 0
    if os.path.isdir(ds):
        s += 1; ev.append('design-system/ directory present')
    masters = [p for p in artifact_files(arm) if os.path.basename(p) == 'MASTER.md']
    if masters:
        s += 2; ev.append('MASTER.md present: ' + os.path.relpath(masters[0], arm).replace(os.sep, '/') + ' (' + str(os.path.getsize(masters[0])) + 'B)')
    else:
        alts = [p for p in delivery_files(arm) if os.path.getsize(p) > 400]
        if alts:
            s += 1; ev.append('no MASTER.md; equivalent system output file: ' + os.path.basename(alts[0]))
    pages = [p for p in artifact_files(arm) if '/pages/' in p.replace(os.sep, '/')]
    if pages:
        s += 1; ev.append('pages/ override layer present: ' + os.path.basename(pages[0]))
    inside = [p for p in artifact_files(arm) if os.sep + 'design-system' + os.sep in p]
    if len(inside) >= 2:
        s += 1; ev.append('2+ files under design-system/ (n=' + str(len(inside)) + ')')
    elif delivery_files(arm):
        s += 1; ev.append('flat delivery, ' + str(len(delivery_files(arm))) + ' file(s) outside design-system/ tree')
    return min(5, s), ev

# ---------- dim 2: category coverage (0-5, one point per category with a token) ----------
CATS = [
    ('color', ['color', 'palette', '#[0-9A-Fa-f]{6}', 'rgb' + chr(92) + chr(40)]),
    ('spacing', ['spacing', 'gap', 'padding', '[0-9]+px']),
    ('typography(font)', ['typography', 'font.?family', 'font.?stack', 'type scale', 'line.?height', 'Inter', 'Roboto', 'Geist', 'system-ui']),
    ('component states', ['hover', 'focus', 'active', 'disabled', 'loading', 'empty', 'error', 'pressed']),
    ('breakpoints', ['breakpoint', '@media', '[0-9]{3,4}px', 'mobile.first', 'sm:', 'md:', 'lg:', 'xl:']),
]
NUM = '#[0-9A-Fa-f]{3,8}|[0-9]+(px|rem|em|s|ms)|[0-9]+[.][0-9]+|[0-9]+[:][0-9]+|[0-9]{2,4}'
def dim2(arm):
    txt = text_of(delivery_files(arm))
    hit = []
    for name, alts in CATS:
        for pat in alts:
            m = re.search(pat, txt, re.I)
            if not m:
                continue
            win = txt[max(0, m.start() - 250): m.start() + 250]
            if re.search(NUM, win):
                hit.append(name); break
    return len(hit), hit

# ---------- dim 3: executability of script calls the doc mentions ----------
def doc_script_calls(docpath):
    doc = read(docpath)
    out = []
    for m in re.finditer('python[0-9]?[ ][^ ]*[.]py[^ ]*', doc):
        out.append(m.group(0).strip())
    return sorted(set(out))

def parse_exec_log(arm):
    log = read(os.path.join(arm, '_exec_log.md'))
    tried, ok = [], []
    pending = None
    for line in log.splitlines():
        cm = re.search('python[0-9]?[^ ]*[ ][^ ]*[.]py', line)
        rm = re.search('rc[ ]?[=:][ ]?(-?[0-9]+)', line, re.I)
        if cm:
            if pending is not None:
                tried.append(pending)
            pending = {'rc': None, 'line': line.strip()[:220]}
        if rm and pending is not None and pending['rc'] is None:
            pending['rc'] = int(rm.group(1))
            tried.append(pending)
            if pending['rc'] == 0:
                ok.append(pending)
            pending = None
    if pending is not None:
        tried.append(pending)
    return log, tried, ok

# dim3 is measured by the Lead, NOT parsed from the arm's own log, so both arms are
# scored on the identical ruler: for each script call that the arm's SKILL.md literally
# documents, did it exit 0 on this host. Source = _ctl/doc_calls_run.json (Lead-run).
DOCJSON = os.path.join(ROOT, '_repro', 'r281h', '_ctl', 'doc_calls_run.json')

def dim3(arm):
    tried, ok, rows = [], [], []
    try:
        d = json.loads(read(DOCJSON))
        key = os.environ.get('R281_DIM3_NAME')
        if not key:
            nrm = arm.replace(os.sep, '/')
            for cand in ('A', 'B'):
                if nrm.endswith('/' + cand):
                    key = cand
        if not key:
            key = arm
        for r in d.get(key, {}).get('rows', []):
            rc = int(r['literal_rc'])
            tried.append(rc)
            if rc == 0:
                ok.append(rc)
            rows.append({'doc_call': r['doc_call_verbatim'], 'literal_rc': rc, 'resolved_rc': int(r['resolved_rc']), 'resolved_stderr': r['resolved_stderr'][:160]})
    except Exception:
        pass
    n, k = len(tried), len(ok)
    score = 0 if n == 0 else int(round(5.0 * k / n))
    return score, n, k, rows, k
# ---------- dim 4: traceability of concrete values (3 deterministic spot checks) ----------
_corpus = None
def local_corpus():
    global _corpus
    if _corpus is None:
        blob = [read(p) for p in files_in(SKILL_TREE) if p.endswith(('.csv', '.json'))]
        _corpus = chr(10).join(blob).lower()
    return _corpus

def dim4(arm):
    body = text_of(delivery_files(arm))
    gen = read(os.path.join(arm, '_gen_stdout.txt')).lower()
    corpus = local_corpus()
    seen, vals = set(), []
    for m in re.finditer('#[0-9A-Fa-f]{6}|[0-9]{1,4}px|[0-9]{1,2}[.][0-9]{1,2}:1|[0-9]+[.][0-9]+rem|[0-9]+[.][0-9]*m?s', body):
        v = m.group(0)
        if v.lower() in seen:
            continue
        seen.add(v.lower()); vals.append(v)
    random.seed(281)
    picks = random.sample(vals, min(3, len(vals))) if vals else []
    rows = []
    for v in picks:
        lv = v.lower()
        src = None
        if lv in gen:
            src = 'generator stdout (_gen_stdout.txt)'
        elif lv in corpus:
            src = 'local skill data (data/*.csv or *.json)'
        rows.append({'value': v, 'source': src, 'traced': src is not None})
    n = len(rows); good = sum(1 for r in rows if r['traced'])
    score = 0 if n == 0 else int(round(5.0 * good / n))
    return score, rows, len(vals)

# ---------- dim 5: instruction-following traces ----------
def dim5(arm):
    log = read(os.path.join(arm, '_exec_log.md'))
    deliv = delivery_files(arm)
    body = text_of(deliv)
    checks = []
    tri = read(os.path.join(arm, '_triage.md'))
    checks.append(('step1_triage_written', len(tri.strip()) > 40 or 'triage' in log.lower()))
    checks.append(('step2_deliverable_produced', bool(deliv) and sum(os.path.getsize(p) for p in deliv) > 800))
    checks.append(('step3_bundled_assets_referenced', bool(re.search('assets/data|data/[a-z_-]+[.]csv|references/[a-z_-]+[.]md', body + log, re.I))))
    checks.append(('step4_script_touched_or_logged', '.py' in log))
    checks.append(('step5_persist_for_retrieval', os.path.isdir(os.path.join(arm, 'design-system')) or bool(re.search('MASTER|persist|cross.session|retriev', body, re.I))))
    bad = []
    for p in deliv:
        if any(ord(c) > 126 for c in read(p)):
            bad.append(os.path.basename(p))
    checks.append(('output_standard_ascii_tokens', len(bad) == 0))
    s = min(5, sum(1 for _, b in checks if b))
    return s, [{'step': n, 'met': b} for n, b in checks], bad

def score_arm(arm_name, arm_dir=None):
    arm = arm_dir or os.path.join(ROOT, '_repro', 'r281h', arm_name)
    arm = os.path.abspath(arm)
    rows, total = [], 0
    for p in artifact_files(arm):
        sz = os.path.getsize(p); total += sz
        rows.append({'path': os.path.relpath(p, ROOT).replace(os.sep, '/'), 'bytes': sz})
    d1, e1 = dim1(arm)
    d2, hit2 = dim2(arm)
    d3, n3, k3, tried, ok = dim3(arm)
    d4, tr4, nvals = dim4(arm)
    d5, c5, bad = dim5(arm)
    tc_raw = read(os.path.join(arm, '_toolcount.txt'))
    m = re.search('[0-9]+', tc_raw)
    tc = int(m.group(0)) if m else None
    return {
        'arm_dir': os.path.relpath(arm, ROOT).replace(os.sep, '/'),
        'files_produced': rows,
        'bytes': total,
        'rubric': {
            '1_artifact_existence': d1, '1_evidence': e1,
            '2_content_completeness': d2, '2_categories_hit': hit2,
            '3_executability': d3, '3_ratio_ok_over_tried': str(k3) + '/' + str(n3), '3_ruler': 'Lead-measured literal rc of each script call documented in the arm SKILL.md', '3_doc_call_rows': tried,
            '4_no_fabrication': d4, '4_spot_checks': tr4, '4_distinct_numeric_tokens': nvals,
            '5_instruction_following': d5, '5_checks': c5, '5_non_ascii_files': bad,
            '6_cost_tool_calls': tc,
        },
        'commands_tried': n3,
        'commands_ok': k3,
        'doc_script_calls': doc_script_calls(os.path.join(arm, 'SKILL.md')),
        'quality_index_Q': d1 + d2 + d3 + d4 + d5,
    }

if __name__ == '__main__':
    names = sys.argv[1:] or ['A', 'B']
    print(json.dumps(dict((n, score_arm(n)) for n in names), ensure_ascii=False, indent=1))
