# -*- coding: utf-8 -*-
'''r291a compat-regression face (requirement 6, second half).

Why: requirement 6 says 'replaced skills must not break existing business logic / no compatibility
problems'. The existing faces measure QUALITY movement (r278_landing_effect: unreferenced rate,
half-claims, double writes) and dead links project-wide (r220_md_deadlink) and gate admission
(r129_reconcile_admission) - but nothing reads COMPATIBILITY per landing: does the trigger text
survive, can the frontmatter field set only grow, are relative pointers still reachable at that
ref, does the command surface still resolve, is version history preserved, is the mirror in sync.
This file is that reading face. It is a READER of the managed root only (red line 2).

How it works (each step is read from git, never from memory):
  1. LANDINGS pins the five landings as (commits, anchor path, before-override).
  2. base_sha = parent of the landing's first commit (git rev-parse <first>~1).
     before_sha = BEFORE_OVERRIDE when the parent is contaminated (the accidental whole-tree
     commit 079b91f3 recorded ANOTHER session's downgrade of ui-ux-pro-max, so <sha>~1 is NOT
     the pre-state this change set replaced). The chosen before arm is proved by blob equality
     with the last commit that actually touched the anchor path.
  3. after_sha = last commit of the landing.
  4. Six dims read the two texts (pure functions of the text + the git tree at that ref).
  5. Verdict per landing and top level: precedence REGRESSION > UNVERIFIED > NO_REGRESSION.
     No any()/all() washing: a cell that cannot be judged is named, never counted as pass.
'''
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True   # never litter __pycache__ into tracked dirs (AGENTS 门禁注)

SK = 'D:/global_skills'
PROJ = 'C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化'
EXEC = os.path.join(PROJ, '05-exec')
BENCH = os.path.join(PROJ, '06-benchmark')
HERE = os.path.dirname(os.path.abspath(__file__))   # works from _repro/r291a or 05-exec alike
OUT = os.path.join(HERE, 'out.json')
REPORT = os.path.join(HERE, 'report.md')
SELF_WRITE = HERE          # the ONLY allowed write surface for this round
MIRROR = 'C:/Users/37533/.agents/skills'
MIRROR_ALT = os.path.join(SK, '_my-skills')
FACE_PY = os.path.abspath(__file__).replace(os.sep, '/')   # cmd_per_cell paths come from here,

sys.path.insert(0, EXEC)
import r220_md_deadlink as D   # single source for link extraction (scan_lines, fence-aware)

# ---------------------------------------------------------------- landing table
# commits are oldest-first; anchor = the SKILL.md whose compatibility we read.
LANDINGS = [
    {'id': 'L1-r266-tdd-pointer', 'slug': 'test-driven-development',
     'commits': ['079b91f3'], 'before_override': None,
     'note': 'one pointer line to writing-good-tests.md; landing commit 079b91f3 is ALSO the '
             'accidental whole-tree commit (R269-3) - only the anchor path is read here.'},
    {'id': 'L2-r269-frontend-slides-register', 'slug': 'frontend-slides',
     'commits': ['6394cbae'], 'before_override': None,
     'note': 'r269 registration + conflict declaration line.'},
    {'id': 'L3-r272-277-frontend-slides-migration', 'slug': 'frontend-slides',
     'commits': ['9aaa9214', '294e3ac6', '89efb3e6'], 'before_override': None,
     'note': 'R310 paradigm migration (32 places) + x1 + x6 residual fixes, read as one landing.'},
    {'id': 'L4-r279-ui-ux-pro-max-merge', 'slug': 'ui-ux-pro-max',
     'commits': ['30b84b20', '3da30832'], 'before_override': '3c72867d',
     'note': 'merge-increment (not overwrite). BASE(=30b84b20~1) is 079b91f3, which recorded '
             'another session\'s downgrade (1.5.0 -> 1.2.0, three version rows dropped), so the '
             'before arm is pinned to 3c72867d - see baseline_witness.'},
    {'id': 'L5-r312-mcp-builder-relayout', 'slug': 'mcp-builder',
     'commits': ['79862372'], 'before_override': None,
     'note': 'v2 Node SDK guide merged in; new reference/node_mcp_server_v2.md.'},
]

def git(*args):
    return subprocess.run(['git', '-c', 'core.quotepath=false', '-C', SK] + list(args),
                          capture_output=True, text=True, encoding='utf-8', errors='replace')

def rev(rev_spec):
    p = git('rev-parse', rev_spec)
    s = (p.stdout or '').strip()
    return s if p.returncode == 0 and s else None

def blob_of(ref, path):
    p = git('show', ref + ':' + path)
    return p.stdout if p.returncode == 0 else None

def blob_sha(ref, path):
    p = git('rev-parse', ref + ':' + path)
    s = (p.stdout or '').strip()
    return s if p.returncode == 0 and s else None

def tree_paths(ref):
    p = git('ls-tree', '-r', '--name-only', ref)
    if p.returncode != 0:
        return None
    return set(x.strip().replace(chr(92), '/') for x in (p.stdout or '').splitlines() if x.strip())

def last_touching(ref, path):
    p = git('log', '--format=%H', '-1', ref, '--', path)
    s = (p.stdout or '').strip().splitlines()
    return s[0] if s else None

def touched_paths(ref):
    p = git('show', '--name-only', '--format=', ref)
    return [x.strip().replace(chr(92), '/') for x in (p.stdout or '').splitlines() if x.strip()]

# ---------------------------------------------------------------- text helpers
def frontmatter(text):
    if text is None:
        return None, None
    lines = text.split(chr(10))
    if not lines or lines[0].strip() != '---':
        return None, None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            return lines[1:i], chr(10).join(lines[i + 1:])
    return None, None

def fm_fields(fl):
    keys = []
    for ln in fl or []:
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_.-]*):', ln)
        if m and m.group(1) not in keys:
            keys.append(m.group(1))
    return keys

def fm_value(fl, key):
    val = []
    on = False
    for ln in fl or []:
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_.-]*):(.*)$', ln)
        if m:
            if on:
                break
            if m.group(1) == key:
                on = True
                val.append(m.group(2).strip())
        elif on and ln.startswith((' ', chr(9))):
            val.append(ln.strip())
    return ' '.join(x for x in val if x).strip()

def tokens(s):
    # retrieval-facing semantics of one text: latin words (>=4 chars) + CJK bigrams.
    # Why bigrams and not whole CJK runs: a description rewrite reorders words without
    # dropping them, and a run-level diff would flag every reorder as a loss (noise that
    # buries the real signal). Bigrams keep phrase identity across rewording.
    out = set()
    for w in re.findall(r'[A-Za-z][A-Za-z0-9_-]{3,}', s or ''):
        out.add(w.lower())
    for run in re.findall('[\\u4e00-\\u9fff]{2,}', s or ''):
        for k in range(len(run) - 1):
            out.add(run[k:k + 2])
    return out

# ---------------------------------------------------------------- dims
DIMS = ['trigger_semantics', 'frontmatter_fields', 'relative_pointers',
        'command_surface', 'version_history', 'mirror_sync']

def dim_trigger(before, after):
    '''dim 1: trigger words / description key semantics preserved.

    How it works: frontmatter trigger-bearing keys (description/name/triggers/triggers_cn/
    keywords) are read per arm. CJK is not whitespace-separated, so the load-bearing semantics
    are approximated by CJK bigrams + latin words. A token lost from the DESCRIPTION but still
    present somewhere in the whole file counts as moved (reported, not red); a token lost from
    the whole file is a real loss and turns the cell red. Verbatim equality per key is also
    recorded so identical text is provably identical reading (negative control 1).'''
    fb, _ = frontmatter(before)
    fa, _ = frontmatter(after)
    keys = [k for k in ('description', 'name', 'triggers', 'triggers_cn', 'keywords')
            if k in fm_fields(fb) or k in fm_fields(fa)]
    per_key, lost_any, moved_any = [], [], []
    for k in keys:
        vb, va = fm_value(fb, k), fm_value(fa, k)
        tb, ta = tokens(vb), tokens(va)
        lost = sorted(tb - ta)
        whole_a = tokens(after)
        truly = sorted(x for x in lost if x not in whole_a)
        moved = sorted(x for x in lost if x in whole_a)
        if truly:
            lost_any.append([k, truly[:12]])
        if moved:
            moved_any.append([k, len(moved)])
        per_key.append({'key': k, 'identical': vb == va, 'tokens_before': len(tb),
                        'tokens_after': len(ta), 'lost_from_description': len(lost),
                        'lost_from_whole_file': truly[:12], 'moved_into_body': len(moved)})
    return {'status': 'REGRESSION' if lost_any else 'PASS', 'trigger_keys': keys,
            'identical_all': all(x['identical'] for x in per_key) if per_key else None,
            'per_key': per_key, 'lost_evidence': lost_any, 'moved_into_body': moved_any,
            'caliber': 'CJK bigram + latin word token proxy over trigger-bearing frontmatter keys'}

def dim_frontmatter(before, after):
    '''dim 2: frontmatter KEY SET may only grow; both named difference sets are printed.'''
    fb, bb = frontmatter(before)
    fa, ba = frontmatter(after)
    if fb is None or fa is None:
        return {'status': 'UNVERIFIED', 'dropped': None, 'added': None,
                'reason': 'frontmatter (--- delimiters) not parseable on at least one arm',
                'parseable_before': fb is not None, 'parseable_after': fa is not None}
    kb, ka = fm_fields(fb), fm_fields(fa)
    dropped = [k for k in kb if k not in ka]
    added = [k for k in ka if k not in kb]
    return {'status': 'REGRESSION' if dropped else 'PASS', 'fields_before': kb,
            'fields_after': ka, 'dropped': dropped, 'added': added,
            'body_lines_delta': len((ba or '').split(chr(10))) - len((bb or '').split(chr(10))),
            'caliber': 'key-set only-grows; value edits are not this dim'}

def materialize(ref, slug, dst):
    '''git archive a skill dir at one ref into dst, extracted with Python tarfile.

    No shell pipe, no tar on PATH, and the managed root is only ever read through
    `git archive` (a read command) - red line 2 keeps D:/global_skills untouched.'''
    import tarfile
    os.makedirs(dst, exist_ok=True)
    p = subprocess.run(['git', '-C', SK, 'archive', '--format=tar', ref, slug],
                       capture_output=True, timeout=300)
    if p.returncode != 0:
        return False, 'git archive rc=%s %s' % (p.returncode, (p.stderr or b'').decode('utf-8', 'replace')[:200])
    try:
        tf = tarfile.open(fileobj=io.BytesIO(p.stdout), mode='r:*')
        for m in tf.getmembers():
            if not m.isfile():
                continue
            target = os.path.join(dst, m.name.replace('/', os.sep))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            f = tf.extractfile(m)
            if f is None:
                continue
            with open(target, 'wb') as w:
                w.write(f.read())
        tf.close()
    except Exception as e:
        return False, 'tar extract failed: %r' % (e,)
    return True, None



def py_interpreters():
    # AGENTS.md 门禁注：首选 managed venv（LibreOffice/系统 python 缺 pptx 等依赖，会假红）。
    # All candidates are tried in order, the first one that produces output wins, and every
    # attempt is recorded - so an UNVERIFIED cell names its real cause instead of a guessed 0.
    home = os.environ.get('USERPROFILE') or os.path.expanduser('~')
    cands = [os.path.join(home, '.workbuddy', 'binaries', 'python', 'envs', 'default',
                         'Scripts', 'python.exe'), sys.executable]
    out = []
    for c in cands:
        if c and os.path.exists(c) and c not in out:
            out.append(c)
    return out
def help_surface(workdir, slug):
    '''flag support face of a skill = union of --help output over its scripts/*.py.

    Kept on purpose comparable with r278.flag_compat, including its self-declared blind spot:
    only .py under scripts/ is probed, so shell/js entry points are NOT part of the face and
    unsupported counts can be OVERSTATED. Returns (help_text, scripts_n, ran_n, reason).'''
    sdir = os.path.join(workdir, slug, 'scripts')
    scripts = []
    for dp, dns, fns in os.walk(sdir):
        dns[:] = [d for d in dns if d != '__pycache__']
        scripts += [os.path.join(dp, x) for x in fns if x.endswith('.py')]
    if not scripts:
        return '', 0, 0, 'no scripts/*.py at this ref: no --help support face exists', None, []
    all_help, ran, failures, py_used = '', 0, [], None
    for sp in sorted(scripts):
        for pyexe in py_interpreters():
            try:
                p = subprocess.run([pyexe, '-B', sp, '--help'], capture_output=True,
                                   text=True, encoding='utf-8', errors='replace', timeout=90)
            except Exception as e:
                failures.append('%s@%s raised %r' % (os.path.basename(sp),
                                                     os.path.basename(pyexe), e))
                continue
            blob = (p.stdout or '') + (p.stderr or '')
            if p.returncode == 0 or 'usage:' in blob:
                all_help += blob
                ran += 1
                py_used = py_used or pyexe
                break
            failures.append('%s@%s rc=%s no-usage-output' % (os.path.basename(sp),
                                                             os.path.basename(pyexe), p.returncode))
    if ran == 0:
        return '', len(scripts), 0, ('no --help face produced; failures=' + '; '.join(failures[:6])), None, failures
    return all_help, len(scripts), ran, None, py_used, failures

CMD_WORDS = ['python3', 'python', 'npx', 'npm run', 'npm install', 'node', 'bash', 'sh',
             'pwsh', 'powershell', 'uv run', 'uv pip', 'pip3', 'pip', 'pytest', 'git',
             'tar', 'ffmpeg', 'curl', './scripts/', 'scripts/']
CMD_RE = re.compile('(?m)^\\s*(?:[$]\\s*)?((' + '|'.join(re.escape(w) for w in CMD_WORDS) + ')[^\\n]*)')
FLAG_RE = re.compile('(?<![A-Za-z0-9_-])(--[a-z][a-z0-9-]{1,})')

def cmd_strings(text):
    # literal command strings a reader could copy out of the body (line-initial runners)
    if text is None:
        return []
    return [m.group(1).strip() for m in CMD_RE.finditer(text)]

def read_tree_text(workdir):
    # concat every small text file under workdir = the WIDE support face (sh/js/md included)
    buf = []
    for dp, dns, fns in os.walk(workdir):
        dns[:] = [d for d in dns if d not in ('__pycache__', '.git')]
        for fn in fns:
            p = os.path.join(dp, fn)
            try:
                if os.path.getsize(p) > 4000000:
                    continue
                buf.append(io.open(p, encoding='utf-8', errors='replace').read())
            except OSError:
                continue
    return chr(10).join(buf)

def arm_command(ref, slug, tmpdir, tag, text_override=None):
    # one arm of dim 4: the text at ref plus the support faces produced from the tree at ref
    text = text_override if text_override is not None else blob_of(ref, slug + '/SKILL.md')
    wd = os.path.join(tmpdir, 'tree_' + tag)
    ok, err = materialize(ref, slug, wd)
    flags = sorted(set(FLAG_RE.findall(text or '')))
    hs = help_surface(wd, slug) if ok else ('', 0, 0, err, None, [])
    strict_help, scripts_n, ran_n, hreason, py_used, failures = hs
    wide = read_tree_text(wd) if ok else ''
    uns_strict = None if hreason else sorted(f for f in flags if f not in strict_help)
    uns_wide = None if not ok else sorted(f for f in flags if f not in wide)
    return {
        'ref': (ref or '')[:12],
        'cmds_n': len(cmd_strings(text)),
        'cmds': cmd_strings(text),
        'flags_n': len(flags),
        'flags': flags,
        'scripts_py_n': scripts_n,
        'help_ran_n': ran_n,
        'help_interpreter': (py_used or '').replace(os.sep, '/'),
        'help_attempt_failures': failures[:8],
        'unsupported_strict': uns_strict,
        'unsupported_wide': uns_wide,
        'unjudgable_reason': hreason,
    }

def dim_command(refs, slug, tmpdir, texts=None):
    # dim 4: command surface, static only. A ref whose support face cannot be produced is
    # UNVERIFIED - never 0 (0 would read as 'no incompatibility', exactly what r278's
    # flag_compat docstring forbids). strict face = union of scripts/*.py --help, i.e. the same
    # face and the same blind spot as r278.flag_compat (shell/js entries uncovered, so
    # unsupported counts may be OVERSTATED); wide face = the flag appears anywhere in the tree
    # materialized at that ref. Fewer literal command strings at after = REGRESSION (an
    # advertised way to run the skill disappeared).
    texts = texts or {}
    out = {'arms': {}}
    for tag in ('before', 'after'):
        out['arms'][tag] = arm_command(refs[tag], slug, tmpdir, tag, texts.get(tag))
    b, a = out['arms']['before'], out['arms']['after']
    out['cmd_delta'] = a['cmds_n'] - b['cmds_n']
    out['caliber_divergence_from_r278'] = (
        'r278.flag_compat counts ANY subprocess output as the support face, so a script that '
        + 'crashes on --help still yields a face there; this face requires rc==0 or argparse '
        + 'usage: output - a traceback is not a support face. Where r278 reports a number and '
        + 'this cell reports UNVERIFIED, that is the stricter rule at work, not a missing reading.')
    out['face_limitation'] = ('strict = scripts/*.py --help only (mirrors r278.flag_compat); '
                              + 'shell/js entry points excluded, so unsupported flags may be OVERSTATED')
    if a['unjudgable_reason'] or b['unjudgable_reason']:
        out['status'] = 'UNVERIFIED'
        out['reason'] = 'support face unavailable: ' + str(a['unjudgable_reason'] or b['unjudgable_reason'])
        out['needs'] = ('a runnable --help face at that ref (scripts/*.py that answers --help), or '
                        + 'a non-python entry probe for js/sh CLIs, or an owner statement that the '
                        + 'skill ships no CLI and its body advertises no flags')
    elif (a['unsupported_strict'] or []) and not (b['unsupported_strict'] or []):
        out['status'] = 'REGRESSION'
        out['reason'] = 'flags newly unsupported at after ref: ' + ', '.join(a['unsupported_strict'])
    elif a['cmds_n'] < b['cmds_n']:
        out['status'] = 'REGRESSION'
        out['reason'] = 'literal command strings shrank %d -> %d' % (b['cmds_n'], a['cmds_n'])
    elif (a['unsupported_strict'] or []):
        out['status'] = 'PASS_INHERITED'
        out['reason'] = 'unsupported flags already present at base: ' + ', '.join(a['unsupported_strict'])
    else:
        out['status'] = 'PASS'
    return out

VH_RE = re.compile('^(?:[-*]\\s*)?(?:\\*\\*)?([0-9]+\\.[0-9]+(?:\\.[0-9]+)?)(?:\\*\\*)?[ :（)]')

def vh_block(text):
    # line range of the '## Version history' block: from that heading to the next heading of
    # the same or higher level. Located by heading so prose step numbers (mcp-builder has
    # '#### 1.2 Study ...') are never counted - measured in the r291a probe: naive semver
    # matching on mcp-builder/SKILL.md returned 15 rows while the real history block holds 2.
    lines = (text or '').split(chr(10))
    start = lvl = None
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith('#') and re.search(r'(?i)version[ ][Hh]istory', s):
            start, lvl = i + 1, len(s) - len(s.lstrip('#'))
            break
    if start is None:
        return None
    body = []
    for ln in lines[start:]:
        s = ln.strip()
        if s.startswith('#'):
            this = len(s) - len(s.lstrip('#'))
            if this <= lvl:
                break
        body.append(ln)
    return body

def vh_rows(text):
    blk = vh_block(text)
    if blk is None:
        return None
    rows = []
    for ln in blk:
        m = VH_RE.match(ln.strip())
        if m:
            rows.append(m.group(1))
    return rows

def dim_version(before, after):
    # dim 5 (R241 class): a merge or landing must not eat version history. Row count may not
    # drop and no version listed before may disappear. If either arm has no history block the
    # cell is UNVERIFIED with the reason - a missing block is not an empty one, and guessing 0
    # would wash the axis.
    vb, va = vh_rows(before), vh_rows(after)
    if vb is None and va is not None:
        return {'status': 'PASS_ADDED_BLOCK', 'rows_before': None, 'rows_after': len(va),
                'versions_after': va, 'dropped_versions': [],
                'reason': 'before arm has no Version history block and the landing introduced '
                          + 'one: nothing was eaten, so the R241 axis cannot regress on null -> set'}
    if va is None and vb is not None:
        return {'status': 'REGRESSION', 'rows_before': len(vb), 'rows_after': None,
                'versions_before': vb, 'dropped_versions': vb,
                'reason': 'the landing removed the Version history block entirely'}
    if vb is None and va is None:
        miss = ', '.join([t for t, x in (('before', vb), ('after', va)) if x is None])
        return {'status': 'UNVERIFIED', 'rows_before': None, 'rows_after': None,
                'reason': 'no Version history block on arm(s): ' + miss}
    dropped = [x for x in vb if x not in va]
    if len(va) < len(vb) or dropped:
        return {'status': 'REGRESSION', 'rows_before': len(vb), 'rows_after': len(va),
                'versions_before': vb, 'versions_after': va, 'dropped_versions': dropped,
                'caliber': 'semver bullets inside the Version history heading'}
    return {'status': 'PASS', 'rows_before': len(vb), 'rows_after': len(va),
            'versions_before': vb, 'versions_after': va, 'dropped_versions': [],
            'added_versions': [x for x in va if x not in vb],
            'caliber': 'semver bullets inside the Version history heading'}

def sha_text(s):
    return hashlib.sha256((s or '').encode('utf-8')).hexdigest()[:16] if s is not None else None

def mirror_path(slug):
    return os.path.join(MIRROR, slug, 'SKILL.md')

def dim_mirror(slug, refs, after_sha, landing_shas):
    # dim 6: mirror sync, read-only probe. Two mirrors exist on this machine; measure both and
    # say which face each reading comes from:
    #   MIRROR (.agents/skills)  - per-skill copies, a real sync target.
    #   SK/_my-skills           - measured: contains only SKILL.md + registry.json + .protected
    #                             (a protection index, 3 entries), NOT a per-skill mirror => it
    #                             cannot carry this landing, so it is reported as N/A-index.
    # Verdict mapping (documented, not cosmetic):
    #   mirror bytes == after  blob -> PASS (landing propagated)
    #   mirror bytes == before blob -> REGRESSION (mirror provably still serves the pre-landing
    #                             text: project rule 5 requires the mirror gate after any
    #                             managed-root change, so a landing that has not propagated is a
    #                             compatibility issue for mirror consumers)
    #   mirror bytes == some other managed ref -> UNVERIFIED (stale at another state; needs the
    #                             sync mechanism's own log to attribute)
    #   mirror missing / unreadable -> UNVERIFIED
    out = {'_my-skills': None, 'agents_skills': None, 'status': None}
    out['_my-skills'] = {
        'path': MIRROR_ALT.replace(os.sep, '/'), 'kind': 'protection index (measured)',
        'entries': sorted(os.listdir(MIRROR_ALT)) if os.path.isdir(MIRROR_ALT) else None,
        'has_skill_dir': os.path.isdir(os.path.join(MIRROR_ALT, slug)),
        'verdict': 'N/A_NOT_A_MIRROR'}
    p = mirror_path(slug)
    m = {'path': p.replace(os.sep, '/'), 'exists': os.path.exists(p)}
    m['mirror_root_is_reparse'] = bool(os.path.islink(MIRROR) or os.path.exists(os.path.join(MIRROR, '.git')))
    txt_after = blob_of(refs['after'], slug + '/SKILL.md')
    txt_before = blob_of(refs['before'], slug + '/SKILL.md')
    if not m['exists']:
        m['verdict'] = 'UNVERIFIED'
        m['reason'] = 'no mirror copy at ' + p.replace(os.sep, '/')
        m['needs'] = 'mirror path, or a statement that this skill is not mirrored'
        out['agents_skills'] = m
        out['status'] = 'UNVERIFIED'
        out['caliber'] = 'see verdict mapping in dim_mirror header comment'
        return out
    mt = io.open(p, encoding='utf-8', errors='replace').read()
    m['bytes'] = len(mt.encode('utf-8'))
    m['sha16'] = sha_text(mt)
    m['after_sha16'] = sha_text(txt_after)
    m['before_sha16'] = sha_text(txt_before)
    if sha_text(mt) == sha_text(txt_after):
        m['verdict'] = 'PASS'
        m['observed'] = 'mirror == after arm byte-for-byte'
    elif sha_text(mt) == sha_text(txt_before):
        m['verdict'] = 'REGRESSION'
        m['observed'] = 'mirror == before arm byte-for-byte (landing not propagated)'
        m['reason'] = 'mirror still serves the pre-landing text; landing shas ' + ', '.join(landing_shas)
        m['matches_ancestor_of_before'] = [refs['before'][:12]]
        m['mirror_repo_last_touch'] = mirror_last_touch(slug)
        m['needs'] = 'none: the mirror provably still serves the before-arm blob'
    else:
        cand, stale_anc = [], []
        for s in candidate_refs(slug):
            if sha_text(blob_of(s, slug + '/SKILL.md')) == sha_text(mt):
                cand.append(s[:12])
            if is_ancestor(s, refs['before']):
                stale_anc.append(s[:12])
        m['matches_other_ref'] = cand
        m['matches_ancestor_of_before'] = stale_anc
        m['mirror_repo_last_touch'] = mirror_last_touch(slug)
        if stale_anc:
            # provably stale: the mirror content equals the managed blob of a commit that IS an
            # ancestor of the before arm, so this landing demonstrably never reached the mirror.
            m['verdict'] = 'REGRESSION'
            m['observed'] = ('mirror equals managed ref ' + stale_anc[0] + ' which ' +
                             'merge-base --is-ancestor proves is an ancestor of before')
            m['reason'] = ('mirror stale at ancestor ref(s) ' + ', '.join(stale_anc[:3]) +
                           '; last mirror sync for this path = ' + str(m['mirror_repo_last_touch']))
            m['needs'] = 'none: staleness proved; propagation needs the mirror gate to be run'
        else:
            m['verdict'] = 'UNVERIFIED'
            m['observed'] = 'mirror matches neither arm and no match is an ancestor of before'
            m['needs'] = ('mirror sync log (rule_editor _mirror_check_only / A-skill-manager, can '
                          + 'run ~45 min) - not executed here (mirrors are read-only per red line 2)')
    out['agents_skills'] = m
    mv = (out['agents_skills'] or {}).get('verdict')
    out['status'] = ('REGRESSION' if mv == 'REGRESSION' else
                     'PASS' if mv == 'PASS' else 'UNVERIFIED')
    out['needs'] = (out['agents_skills'] or {}).get('needs')
    out['caliber'] = ('PASS only when the mirror copy equals the after-arm blob byte-for-byte; '
                      + 'REGRESSION when it still equals the before-arm blob (landing not propagated); '
                      + 'any other content = UNVERIFIED needing the mirror sync log')
    return out

REF_CACHE = {}
is_ancestor_cache = {}

def is_ancestor(a, b):
    # git merge-base --is-ancestor, cached: used to prove a stale mirror is an ANCESTOR of the
    # before arm (=> the landing demonstrably never reached the mirror), not just different.
    k = (a, b)
    if k not in is_ancestor_cache:
        p = git('merge-base', '--is-ancestor', a, b)
        is_ancestor_cache[k] = (p.returncode == 0)
    return is_ancestor_cache[k]

def mirror_last_touch(slug):
    # The mirror is its OWN git repo (measured: C:/Users/37533/.agents/skills/.git exists, head
    # 'feat: Marvis 6 技能镜像同步 (R140)'). Its history for this path is the cheapest read-only
    # witness of when the mirror was last synced.
    p = subprocess.run(['git', '-C', MIRROR, 'log', '--format=%h %ad %s',
                        '--date=format:%Y-%m-%dT%H:%M', '-1', '--', slug + '/SKILL.md'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    ln = ((p.stdout or '').strip().splitlines() or [''])[0]
    return ln or None

def candidate_refs(slug):
    # commits touching the skill dir, newest first, capped - used only to name a stale mirror.
    if slug in REF_CACHE:
        return REF_CACHE[slug]
    p = git('log', '--format=%H', '-40', '--', slug)
    refs = [x.strip() for x in (p.stdout or '').splitlines() if x.strip()]
    REF_CACHE[slug] = refs
    return refs

# ---------------------------------------------------------------- pointer core (2-factor)
def pointer_norm(slug, u):
    # same skip rules as r220.dead (scheme / placeholder / anchor-only), same ../ algebra
    if re.match(r'^(https?:|mailto:|data:|//)', u):
        return None
    if u in ('URL', 'url') or re.match(r'^[A-Z]+$', u) or '<' in u or '>' in u:
        return None
    path = u.partition('#')[0]
    if not path:
        return None
    if path.startswith('/'):
        return path.lstrip('/')
    acc = []
    for pp in (slug + '/' + path).split('/'):
        if pp in ('', '.'):
            continue
        if pp == '..':
            if acc:
                acc.pop()
            continue
        acc.append(pp)
    return '/'.join(acc)

def link_set(text, slug):
    # normalized target set of the relative links one text points at
    out = set()
    for _ln, u in D.scan_lines(text or ''):
        n = pointer_norm(slug, u)
        if n:
            out.add(n)
    return out

def resolves(norm, tree):
    if tree is None:
        return None
    return bool(norm in tree or (norm + '.md') in tree or (norm + '/README.md') in tree)

def pointer_core(text, tree, base_text, base_tree, slug, face):
    # the whole dim-3 judgement as a pure function, so the negative control can inject a ghost
    # pointer WITHOUT writing anything into the managed root. Two factors classify each dead
    # link, because one factor alone lies:
    #   lives at base tree AND dead now  -> the landing BROKE a pointer that used to resolve
    #   not referenced at base AND dead  -> the landing ADDED a pointer that resolves nowhere
    #     (a reader following it hits 404; this is the injected-ghost shape)  -> both are RED
    #   referenced at base AND dead at base -> PRE-EXISTING: named, not charged to this landing
    dead = []
    base_norms = link_set(base_text, slug)
    for ln, u in D.scan_lines(text or ''):
        norm = pointer_norm(slug, u)
        if not norm:
            continue
        if resolves(norm, tree):
            continue
        live_base = resolves(norm, base_tree)
        if live_base:
            kind = 'broke'
        elif norm not in base_norms:
            kind = 'newly_added_dead'
        else:
            kind = 'preexisting'
        dead.append({'line': ln, 'target': u, 'normalized': norm, 'kind': kind,
                     'referenced_at_base': norm in base_norms,
                     'lives_at_base_tree': bool(live_base)})
    red = [x for x in dead if x['kind'] in ('broke', 'newly_added_dead')]
    if tree is None or base_tree is None:
        return {'status': 'UNVERIFIED', 'reason': 'git tree unreadable on at least one arm',
                'face': face, 'dead': dead, 'red': [x['normalized'] for x in red]}
    st = 'REGRESSION' if red else ('PASS_PREEXISTING' if dead else 'PASS')
    return {'status': st, 'face': face, 'links_total': len(D.scan_lines(text or '')),
            'dead_n': len(dead), 'red': [x['normalized'] for x in red],
            'preexisting': [x['normalized'] for x in dead if x['kind'] == 'preexisting'],
            'dead_detail': dead}

def dim_pointers(refs, slug):
    # dim 3 wiring: both arms come from git, never the worktree (80 dirty lines at read time
    # would make the reading a statement about somebody else's in-flight edits)
    t_a = blob_of(refs['after'], slug + '/SKILL.md')
    t_b = blob_of(refs['before'], slug + '/SKILL.md')
    if t_a is None or t_b is None:
        return {'status': 'UNVERIFIED',
                'reason': 'SKILL.md unreadable at an arm', 'arms': dict(refs)}
    res = pointer_core(t_a, tree_paths(refs['after']), t_b,
                        tree_paths(refs['before']), slug,
                        'git tree at ' + refs['after'][:12])
    # HEAD cross-check (second face, never a wash): a pointer dead at the landing ref but live
    # again at HEAD means that commit carried the break and something LATER restored it. The
    # cell stays red - a landing commit is what a clone can check out. This is exactly what
    # r220_md_deadlink cannot see: it scans the WORKTREE and gate_run_r220_md_deadlink.json
    # reports dead=0 there while these landing commits each contained a dead pointer.
    head = rev('HEAD')
    htree = tree_paths(head) if head else None
    res['head_crosscheck'] = {
        'head': (head or '')[:12],
        'red_still_dead_at_head': [x for x in (res.get('red') or []) if not resolves(x, htree)],
        'red_restored_by_head': [x for x in (res.get('red') or []) if resolves(x, htree)],
        'note': 'cross-check only; the cell verdict is taken at the landing ref',
    }
    return res
    # HEAD cross-check: a pointer dead at the landing ref but live again at HEAD means the
    # commit itself carried the break and something later restored it. That is reported as a
    # second face and NEVER used to downgrade the cell to PASS: the landing commit is what a
    # clone can check out, and the r220 face would have hidden it (r220 scans the worktree only,
    # which is exactly why gate_run_r220_md_deadlink.json reports dead=0 while the landing
    # commits contained a dead pointer).
    head = rev('HEAD')
    htree = tree_paths(head) if head else None
    res['head_crosscheck'] = {
        'head': (head or '')[:12],
        'red_still_dead_at_head': [x for x in (res.get('red') or []) if not resolves(x, htree)],
        'red_restored_by_head': [x for x in (res.get('red') or []) if resolves(x, htree)],
        'why_this_matters': 'r220_md_deadlink reads the worktree; a landing-only break is '
                            + 'invisible there, so this face must be read at the ref',
    }
    return res

# ---------------------------------------------------------------- landing assembly
def resolve_refs(l, anchor):
    # base / before / after are RESOLVED from git at run time, never copied from the brief.
    first_full = rev(l['commits'][0])
    after_full = rev(l['commits'][-1])
    if not first_full or not after_full:
        return {'state': 'SHA_UNREADABLE', 'wanted': l['commits']}
    base_full = rev(l['commits'][0] + '~1')
    before_full = rev(l['before_override']) if l['before_override'] else base_full
    # witness: the before arm must be the last commit that actually touched the anchor path
    lt = last_touching(before_full or '', anchor)
    same_blob = bool(lt) and bool(blob_sha(before_full, anchor)) and \
        blob_sha(before_full, anchor) == blob_sha(lt, anchor)
    # chain: no commit between before and after other than the landing's own commits
    p = git('log', '--format=%H', before_full + '..' + after_full, '--', anchor)
    chain = [x.strip() for x in (p.stdout or '').splitlines() if x.strip()]
    return {'state': 'OK', 'base': base_full, 'before': before_full, 'after': after_full,
            'base_is_before': base_full == before_full,
            'before_last_touching_anchor': lt, 'before_blob_witness': same_blob,
            'chain_commits': chain,
            'chain_is_landing': set(chain) == set(l['commits_full']),
            'on_mainline_head': {
                # repo rule: a landing commit is not delivered until merge-base proves it is an
                # ancestor of HEAD (a parallel rebase can drop it off the mainline - one-hand
                # b9e5d90e). Read here so a compatibility statement names the shipped path.
                s[:8]: is_ancestor(s, rev('HEAD')) for s in l['commits_full']
            },
            'chain_extra_commits': [x[:8] for x in chain if x not in l['commits_full']],
            'chain_extra_note': ('commits touching the anchor between before and after that are '
                                 + 'NOT part of this landing (079b91f3 = the accidental whole-tree '
                                 + 'commit) - named, not hidden' 
                                 if [x for x in chain if x not in l['commits_full']] else '')}

def run_landing(l, tmpdir):
    anchor = l['anchor'] = l['slug'] + '/SKILL.md'
    refs = resolve_refs(l, anchor)
    row = {'id': l['id'], 'slug': l['slug'], 'note': l['note'], 'refs': refs,
           'landing_commits': l['commits'], 'touched_paths': {}, 'dims': {}}
    if refs['state'] != 'OK':
        row['verdict'] = 'UNVERIFIED'
        row['dims'] = {d: {'status': 'UNVERIFIED', 'reason': 'sha unreadable'} for d in DIMS}
        return row
    for s in l['commits_full']:
        row['touched_paths'][s[:8]] = touched_paths(s)
    tb = blob_of(refs['before'], anchor)
    ta = blob_of(refs['after'], anchor)
    row['sha16'] = {'base': sha_text(blob_of(refs['base'], anchor)),
                    'before': sha_text(tb), 'after': sha_text(ta)}
    row['identical_arms'] = (tb == ta)
    row['dims']['trigger_semantics'] = dim_trigger(tb, ta)
    row['dims']['frontmatter_fields'] = dim_frontmatter(tb, ta)
    row['dims']['relative_pointers'] = dim_pointers(refs, l['slug'])
    row['dims']['command_surface'] = dim_command(refs, l['slug'], tmpdir)
    row['dims']['version_history'] = dim_version(tb, ta)
    row['dims']['mirror_sync'] = dim_mirror(l['slug'], refs, ta, l['commits_full'])
    row['verdict'] = verdict_of(row['dims'])
    return row

def verdict_of(dims):
    # EXPLICIT three-way precedence, no any()/all() washing (audit-runner-safe-aggregate):
    # a cell we could not judge is never folded into 'fine'.
    st = [dims[d]['status'] for d in DIMS]
    red = [d for d in DIMS if dims[d]['status'] == 'REGRESSION']
    unver = [d for d in DIMS if dims[d]['status'] == 'UNVERIFIED']
    if red:
        return 'REGRESSION'
    if unver:
        return 'UNVERIFIED'
    return 'NO_REGRESSION'

# ---------------------------------------------------------------- negative controls
GHOST = '_r291a_ghost_pointer_does_not_exist.md'
GHOST2 = 'sub/ghost2_r291a.md'

def nc_same_text(rows_by_id):
    # NC1: (a) same text in both arms must give the same reading (identical=true everywhere);
    # (b) swapping the arms (after := before text) MUST light up dims with named differences,
    # otherwise this face is blind to that regression class and is decoration.
    rid = 'L4-r279-ui-ux-pro-max-merge'
    row = rows_by_id[rid]
    anchor = row['slug'] + '/SKILL.md'
    tb = blob_of(row['refs']['before'], anchor)
    ta = blob_of(row['refs']['after'], anchor)
    same = {'trigger_semantics': dim_trigger(tb, tb),
            'frontmatter_fields': dim_frontmatter(tb, tb),
            'version_history': dim_version(tb, tb)}
    swap = {'trigger_semantics': dim_trigger(ta, tb),
            'frontmatter_fields': dim_frontmatter(ta, tb),
            'version_history': dim_version(ta, tb)}
    leg_a = {'trigger_identical_all': same['trigger_semantics'].get('identical_all'),
             'frontmatter_dropped': same['frontmatter_fields'].get('dropped'),
             'frontmatter_added': same['frontmatter_fields'].get('added'),
             'version_rows_equal': (same['version_history'].get('rows_before')
                                    == same['version_history'].get('rows_after')),
             'all_status': {k: v['status'] for k, v in same.items()}}
    leg_b = {'statuses': {k: v['status'] for k, v in swap.items()},
             'lost_evidence': swap['trigger_semantics'].get('lost_evidence'),
             'frontmatter_dropped': swap['frontmatter_fields'].get('dropped'),
             'version_dropped': swap['version_history'].get('dropped_versions')}
    ok_a = (leg_a['trigger_identical_all'] is True and leg_a['frontmatter_dropped'] == []
            and leg_a['frontmatter_added'] == [] and leg_a['version_rows_equal'])
    lit = [k for k, v in swap.items() if v['status'] == 'REGRESSION']
    return {'landing': rid, 'leg_same_text_same_reading': leg_a, 'leg_a_ok': ok_a,
            'leg_swapped_arms': leg_b, 'leg_b_lits': lit, 'leg_b_ok': bool(lit),
            'pass': bool(ok_a and lit)}

def nc_ghost_pointer(rows_by_id):
    # NC2: inject pointers that resolve nowhere into a TEMP COPY of the after text and run the
    # real pointer dim on it. The managed root is never written: the copy lives under
    # _repro/r291a/negctl/, is deleted after the run, and the deletion is proved by a residual
    # scan of the project tree.
    rid = 'L5-r312-mcp-builder-relayout'
    row = rows_by_id[rid]
    anchor = row['slug'] + '/SKILL.md'
    ta = blob_of(row['refs']['after'], anchor)
    tb = blob_of(row['refs']['before'], anchor)
    ghost_line = 'ghost leg [ghost](' + GHOST + ') and [g2](' + GHOST2 + ')'
    injected = ta.rstrip(chr(10)) + chr(10) + chr(10) + ghost_line + chr(10)
    keep = os.path.join(HERE, 'negctl')
    os.makedirs(keep, exist_ok=True)
    fp = os.path.join(keep, 'injected_copy.md')
    io.open(fp, 'w', encoding='utf-8', newline='').write(injected)
    res = pointer_core(injected, tree_paths(row['refs']['after']), tb,
                       tree_paths(row['refs']['before']), row['slug'], 'INJECTED temp copy')
    named = [x for x in res.get('red', []) if GHOST in x or 'ghost2' in x]
    os.remove(fp)
    try:
        os.rmdir(keep)
    except OSError:
        pass
    # residual scan is by EXACT injected filenames (a fuzzy 'ghost' substring sweep would
    # match unrelated pre-existing files and turn a clean deletion into a false alarm).
    want = set([GHOST, os.path.basename(GHOST2), 'injected_copy.md'])
    residual = []
    for dp, dns, fns in os.walk(PROJ):
        if os.sep + '.git' + os.sep in (dp + os.sep):
            continue
        for fn in fns:
            if fn in want:
                residual.append(os.path.join(dp, fn).replace(os.sep, '/'))
    return {'landing': rid, 'injected_targets': [GHOST, GHOST2], 'injected_line': ghost_line,
            'status': res['status'], 'red_named': res.get('red'), 'ghost_named': named,
            'temp_copy_path': fp.replace(os.sep, '/'),
            'temp_copy_removed': not os.path.exists(fp),
            'negctl_dir_removed': not os.path.isdir(keep),
            'residual_files_matching_ghost': residual, 'residual_n': len(residual),
            'pass': bool(res['status'] == 'REGRESSION' and len(named) == 2
                         and not os.path.exists(fp) and len(residual) == 0)}

# ---------------------------------------------------------------- cmd per cell
def cmd_for(dim, rid):
    # how to reproduce exactly one cell from a clean shell. No hand-written numbers anywhere
    # in this file: every reading in out.json/report.md comes from the command in this table.
    return ('python -B ' + FACE_PY + ' --dim ' + dim + ' --landing ' + rid)

DIM_READ = {
    'trigger_semantics': lambda r: r['dims']['trigger_semantics'],
    'frontmatter_fields': lambda r: r['dims']['frontmatter_fields'],
    'relative_pointers': lambda r: r['dims']['relative_pointers'],
    'command_surface': lambda r: r['dims']['command_surface'],
    'version_history': lambda r: r['dims']['version_history'],
    'mirror_sync': lambda r: r['dims']['mirror_sync'],
}

_ROWS_CACHE = []

def row(rid):
    # used by --dim/--landing: rebuild the face once, then pick the cell.
    if not _ROWS_CACHE:
        _ROWS_CACHE.append(build()[0])
    return [x for x in _ROWS_CACHE[0] if x['id'] == rid][0]

# ---------------------------------------------------------------- build / output
def wanted_shas():
    # every short sha this face was asked to work with (brief table + pinned overrides), so an
    # unresolvable sha is registered BY NAME instead of silently degrading a cell.
    s = []
    for l in LANDINGS:
        for x in l['commits']:
            if x not in s:
                s.append(x)
        if l['before_override'] and l['before_override'] not in s:
            s.append(l['before_override'])
    return s

WANTED_SHAS = []
def build(tmpdir=None):
    global WANTED_SHAS
    WANTED_SHAS = wanted_shas()
    own_tmp = tmpdir is None
    if own_tmp:
        tmpdir = tempfile.mkdtemp(prefix='r291a_')
    for l in LANDINGS:
        l['anchor'] = l['slug'] + '/SKILL.md'
        l['commits_full'] = [rev(x) for x in l['commits']]
    rows = [run_landing(l, tmpdir) for l in LANDINGS]
    if own_tmp:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return rows, tmpdir

def summarize(rows):
    # cell-level counts, NOT an any()/all() verdict. Top-level verdict = precedence rule over
    # the per-landing verdicts (REGRESSION > UNVERIFIED > NO_REGRESSION).
    reg_cells = unv_cells = 0
    for r in rows:
        for d in DIMS:
            st = r['dims'][d]['status'] if d in r['dims'] else 'UNVERIFIED'
            if st == 'REGRESSION':
                reg_cells += 1
            elif st == 'UNVERIFIED':
                unv_cells += 1
    v = [r['verdict'] for r in rows]
    top = ('REGRESSION' if 'REGRESSION' in v else
           'UNVERIFIED' if 'UNVERIFIED' in v else 'NO_REGRESSION')
    hist = {}
    for r in rows:
        for d in DIMS:
            k = (r['dims'].get(d) or {}).get('status', 'ABSENT')
            hist[k] = hist.get(k, 0) + 1
    return {'status_histogram': hist, 'landings': len(rows), 'cells': len(rows) * len(DIMS),
            'regression_cells': reg_cells, 'unverified_cells': unv_cells,
            'per_landing_verdicts': {r['id']: r['verdict'] for r in rows},
            'top_verdict_by_precedence': top,
            'precedence': 'REGRESSION > UNVERIFIED > NO_REGRESSION (a cell that cannot be '
                          'judged is named, never folded into pass; no any()/all() washing)'}

def render_report(rows, ncs, summary, provenance):
    L = []
    L.append('# r291a 零兼容回归读数面 · 5 笔落地 × 6 维矩阵')
    L.append('')
    L.append('> 生成：`python -B ' + FACE_PY + '`（现读，无手抄数字）。取值时刻 ' + provenance['generated_at'] + '。')
    L.append('>')
    L.append('> **本面测的是产物/接口兼容（description 触发语义、frontmatter 字段集合、相对指针可达性、')
    L.append('> 命令面、版本史行数、镜像同步），不等于业务质量。** 质量移动的读数面在 `05-exec/r278_landing_effect.py`。')
    L.append('')
    L.append('## 0. 三张 sha 表（base / before / after，全部 git 现读）')
    L.append('')
    L.append('| 落地 | slug | base（首笔之父） | before（改前文本所在） | after | before=base? | before blob 见证 | 链内提交=本笔? |')
    L.append('|---|---|---|---|---|---|---|---|')
    for r in rows:
        ref = r['refs']
        sh, sb, sa = ref.get('base'), ref.get('before'), ref.get('after')
        L.append('| %s | %s | `%s` | `%s` | `%s` | %s | %s | %s |' % (
            r['id'], r['slug'], (sh or '?')[:8], (sb or '?')[:8], (sa or '?')[:8],
            ref.get('base_is_before'), ref.get('before_blob_witness'), ref.get('chain_is_landing')))
    L.append('')
    L.append('坑（件内固化，不再靠人记）：079b91f3 是误提交他会话降级那笔，它的 <sha>~1 不等于改前状态；故 L4 的 before 显式钉在 3c72867d，并用 blob 等值见证（before_blob_witness）证明那确实是落地前最后一态。')
    L.append('')
    L.append('## 1. 矩阵（格 = 状态 + 关键读数 + 取值命令）')
    L.append('')
    L.append('| 落地 \\ 维 | trigger_semantics | frontmatter_fields | relative_pointers | command_surface | version_history | mirror_sync | 笔判定 |')
    L.append('|---|---|---|---|---|---|---|---|')
    for r in rows:
        cells = []
        for d in DIMS:
            cells.append(cell_text(r, d))
        L.append('| **%s** | %s | %s |' % (r['id'], ' | '.join(cells), r['verdict']))
    L.append('')
    L.append('每格取值命令（逐格可复跑，命令即出处）：')
    L.append('')
    for r in rows:
        L.append('- `%s`' % r['id'])
        for d in DIMS:
            L.append('  - %s → `%s`' % (d, cell_reason(r, d)))
            L.append('    - cmd: `%s`' % cmd_for(d, r['id']))
    L.append('')
    L.append('## 2. 负向对照（实测输出，非声明）')
    L.append('')
    L.append('### NC1 同文本必同读 + 交换臂必须亮')
    L.append('')
    L.append('```json')
    L.append(json.dumps(ncs['same_text'], ensure_ascii=False, indent=1))
    L.append('```')
    L.append('')
    L.append('### NC2 注入不存在的相对指针（临时副本，用完删除）')
    L.append('')
    L.append('```json')
    L.append(json.dumps(ncs['ghost'], ensure_ascii=False, indent=1))
    L.append('```')
    L.append('')
    L.append('## 3. 汇总（按格计数，不做 any()/all() 洗绿）')
    L.append('')
    L.append('```json')
    L.append(json.dumps(summary, ensure_ascii=False, indent=1))
    L.append('```')
    L.append('')
    L.append('## 3b. 红格的第二面（HEAD 复算 + 主线祖先，防止把「当时断」读成「现在断」）')
    L.append('')
    L.append('| 落地 | 指针红项 | 在 HEAD 是否已恢复 | 本笔各 commit 是否仍是 HEAD 祖先 |')
    L.append('|---|---|---|---|')
    for r in rows:
        p = r['dims'].get('relative_pointers') or {}
        hx = p.get('head_crosscheck') or {}
        ml = (r['refs'] or {}).get('on_mainline_head') or {}
        L.append('| %s | %s | restored_by_head=%s still_dead=%s | %s |' % (
            r['id'], p.get('red') or 'none', hx.get('red_restored_by_head'),
            hx.get('red_still_dead_at_head'), json.dumps(ml)))
    L.append('')
    L.append('> 判读口径：指针维的判定取**落地 commit 当时的 git tree**（那才是一个 clone 能检出的状态），'
             + 'HEAD 复算只作第二面披露；格不因 HEAD 恢复而降级。')
    L.append('')
    L.append('## 4. 判不了就写 UNVERIFIED（退路清单）')
    L.append('')
    for r in rows:
        for d in DIMS:
            if r['dims'][d]['status'] == 'UNVERIFIED':
                L.append('- `%s` / %s → 原因：%s；需要的外部条件：%s' % (
                    r['id'], d, cell_reason(r, d), r['dims'][d].get('needs', '见件内 reason 字段'))) 
    L.append('')
    return chr(10).join(L) + chr(10)

# ---------------------------------------------------------------- cell rendering
def cell_reason(r, d):
    # one-line reading of a cell, built from the cell's own fields (never typed by hand)
    c = r['dims'].get(d) or {}
    if d == 'trigger_semantics':
        pk = c.get('per_key') or []
        ident = all(x['identical'] for x in pk) if pk else None
        return '%s | identical_all=%s | lost=%s | moved_into_body=%s' % (
            c.get('status'), c.get('identical_all'),
            ';'.join(c.get('lost_evidence') or []) or 'none', c.get('moved_into_body') or 'none')
    if d == 'frontmatter_fields':
        return '%s | dropped=%s added=%s | before=%s after=%s' % (
            c.get('status'), c.get('dropped'), c.get('added'),
            c.get('fields_before'), c.get('fields_after'))
    if d == 'relative_pointers':
        return '%s | links=%s dead=%s red=%s preexisting=%s' % (
            c.get('status'), c.get('links_total'), c.get('dead_n'),
            c.get('red') or 'none', c.get('preexisting') or 'none')
    if d == 'command_surface':
        ar = c.get('arms') or {}
        b, a = ar.get('before', {}), ar.get('after', {})
        return '%s | cmds %s->%s | flags %s->%s | unsup_strict %s->%s | unsup_wide %s->%s | %s' % (
            c.get('status'), b.get('cmds_n'), a.get('cmds_n'), b.get('flags_n'), a.get('flags_n'),
            b.get('unsupported_strict'), a.get('unsupported_strict'),
            b.get('unsupported_wide'), a.get('unsupported_wide'), c.get('reason') or '')
    if d == 'version_history':
        return '%s | rows %s->%s | dropped=%s added=%s | %s' % (
            c.get('status'), c.get('rows_before'), c.get('rows_after'),
            c.get('dropped_versions'), c.get('added_versions'), c.get('reason') or '')
    if d == 'mirror_sync':
        m = (c.get('agents_skills') or {})
        return '%s | mirror=%s | %s | %s' % (
            c.get('status'), m.get('verdict'),
            'bytes=%s' % m.get('bytes') if m.get('bytes') else 'no copy',
            (m.get('reason') or m.get('observed') or '')[:220])
    return str(c.get('status'))

def cell_text(r, d):
    c = r['dims'].get(d) or {}
    st = c.get('status', 'UNVERIFIED')
    short = {
        'trigger_semantics': lambda: 'identical_all=%s / lost=%s' % (
            c.get('identical_all'), ';'.join(c.get('lost_evidence') or []) or 'none'),
        'frontmatter_fields': lambda: 'dropped=%s added=%s' % (c.get('dropped'), c.get('added')),
        'relative_pointers': lambda: 'dead=%s red=%s' % (
            c.get('dead_n'), (c.get('red') or 'none') if isinstance(c.get('red'), str) else c.get('red')),
        'command_surface': lambda: 'cmds=%s unsup_strict=%s' % (
            (c.get('arms') or {}).get('after', {}).get('cmds_n'),
            (c.get('arms') or {}).get('after', {}).get('unsupported_strict')),
        'version_history': lambda: 'rows=%s->%s dropped=%s' % (
            c.get('rows_before'), c.get('rows_after'), c.get('dropped_versions')),
        'mirror_sync': lambda: 'agents=%s myskills=%s' % (
            (c.get('agents_skills') or {}).get('verdict'),
            (c.get('_my-skills') or {}).get('verdict')),
    }
    body = ''
    if d in short:
        try:
            body = short[d]()
        except Exception as e:
            body = 'render-error %r' % (e,)
    return '**%s** %s' % (st, body)

# ---------------------------------------------------------------- main
def assert_write_surface():
    # self-guard for red line 2 / the round's write surface: this face may only ever write
    # inside its own _repro/r291a directory, and may never create or modify anything under
    # D:/global_skills or D:/global_memory. Checked before any output is written.
    for p in (OUT, REPORT):
        if os.path.commonpath([os.path.abspath(p), SELF_WRITE]) != SELF_WRITE:
            raise AssertionError('refusing to write outside the allowed surface: ' + p)
    # (commonpath raises across drives - C: workspace vs D: roots simply cannot overlap)
    for forbidden in (SK, 'D:/global_memory'):
        if os.path.abspath(SELF_WRITE).lower().startswith(os.path.abspath(forbidden).lower()):
            raise AssertionError('write surface overlaps a read-only root: ' + forbidden)

def main(argv):
    dim = rid = None
    if '--dim' in argv:
        dim = argv[argv.index('--dim') + 1]
    if '--landing' in argv:
        rid = argv[argv.index('--landing') + 1]
    assert_write_surface()
    rows, tmpdir = build()
    summary = summarize(rows)
    by_id = {r['id']: r for r in rows}
    ncs = {'same_text': nc_same_text(by_id), 'ghost': nc_ghost_pointer(by_id)}
    provenance = {
        'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'python': sys.version.split()[0],
        'managed_root': SK, 'managed_head_at_read': rev('HEAD'),
        'head_drift_note': ('the managed HEAD moves while this round runs (another session '
                            + 'commits); the before/after arms are PINNED blobs read with '
                            + 'git show <sha>:<path>, so no reading depends on HEAD. '
                            + 'head_crosscheck uses the head value printed here and only as a '
                            + 'second face, never to wash a cell.'),
        'managed_worktree_dirty_lines': len([x for x in git('status', '--porcelain').stdout
                                             .splitlines() if x.strip()]),
        'reuse_single_source': {
            'link_extraction': '05-exec/r220_md_deadlink.scan_lines (fence-aware)',
            'flag_compat_face': 'same shape as r278_landing_effect.flag_compat (scripts/*.py --help)',
            'quality_axes_stay_in': '05-exec/r278_landing_effect.py + 06-benchmark/r278_landing_effect_*.json',
            'admission_gate': '05-exec/r129_reconcile_admission.py (not re-implemented here)',
        },
        'read_only_attestation': 'only git log/show/rev-parse/ls-tree/archive (read) + filesystem reads; '
                                 + 'no git write, no file created or modified under D:/global_skills or D:/global_memory',
        'sha_accounting': {
            'requested': WANTED_SHAS,
            'resolved': {s[:8]: rev(s) for s in WANTED_SHAS},
            'unreadable': [s for s in WANTED_SHAS if not rev(s)],
            'rule': 'a sha that cannot be read is registered by name here, never substituted',
        },
        'field_names_measured_first': 'probe run printed sorted keys of r278_landing_effect.json / '
                                      'gate_run_r220_md_deadlink.json / admission_r129_2026-10-20.json before use',
    }
    doc = {
        'schema': 'compat-regression-v1',
        'provenance': provenance,
        'dims': DIMS,
        'dim_meanings': {
            'trigger_semantics': 'description/trigger key semantics preserved (CJK bigram + latin token proxy)',
            'frontmatter_fields': 'frontmatter key set only-grows; named difference sets',
            'relative_pointers': 'every relative pointer resolves at the landing ref (git tree face)',
            'command_surface': 'literal command count + flag support face (strict/wide), UNVERIFIED if unproducible',
            'version_history': 'Version history block rows may not shrink or lose a version (R241 class)',
            'mirror_sync': 'mirror copies vs before/after blobs (read-only probe)',
        },
        'scope_note': 'This face reads PRODUCT/INTERFACE compatibility only. It is NOT business '
                      + 'quality: quality movement lives in r278_landing_effect (unreferenced rate, '
                      + 'half-claims, double writes). A cell saying PASS says nothing about whether '
                      + 'the skill got better.',
        'verdict_rule': 'per landing: REGRESSION if any dim red; else UNVERIFIED if any dim cannot '
                        + 'be judged; else NO_REGRESSION. Top level = same precedence over landings. '
                        + 'No any()/all() aggregation (audit-runner-safe-aggregate).',
        'landings': rows,
        'negative_controls': ncs,
        'summary': summary,
        'cmd_per_cell': {r['id']: {d: cmd_for(d, r['id']) for d in DIMS} for r in rows},
        'cmd_all': 'python -B ' + FACE_PY,
    }
    if rid and dim:
        print(json.dumps({'landing': rid, 'dim': dim, 'cell': by_id[rid]['dims'][dim],
                          'cmd': cmd_for(dim, rid)}, ensure_ascii=False, indent=1))
        return 0
    tmp = OUT + '.tmp'
    io.open(tmp, 'w', encoding='utf-8', newline='').write(json.dumps(doc, ensure_ascii=False, indent=1))
    os.replace(tmp, OUT)
    rp = tmp + '.md'
    io.open(rp, 'w', encoding='utf-8', newline='').write(
        render_report(rows, ncs, summary, provenance))
    os.replace(rp, REPORT)
    shutil.rmtree(tmpdir, ignore_errors=True)
    reg, unv = summary['regression_cells'], summary['unverified_cells']
    print('[COMPAT:FACE] landings=%d dims=%d regression=%d unverified=%d' % (
        summary['landings'], len(DIMS), reg, unv))
    print('  out=' + OUT)
    print('  report=' + REPORT)
    print('  negative_controls: NC1.pass=%s NC2.pass=%s residual_n=%s' % (
        ncs['same_text']['pass'], ncs['ghost']['pass'], ncs['ghost']['residual_n']))
    print('  top_verdict=' + summary['top_verdict_by_precedence'] + ' per_landing=' +
          json.dumps(summary['per_landing_verdicts'], ensure_ascii=False))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
