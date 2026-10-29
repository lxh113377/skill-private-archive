# -*- coding: utf-8 -*-
"""follow-version feasibility face (R264-3 / R265).

Why: r263 concluded "15 skills are BEHIND => follow the version". r264 narrowed that to 13
same-lineage skills, but a version tag says nothing about whether the CONTENT differs: measured
r265, some local files are 6x larger than upstream (a local rewrite) while others are a strict
superset of upstream. Overwriting wholesale would therefore delete local work - exactly the
regression requirement 6 forbids.

What it does: reads the r264 semantics face (SAME_LINEAGE + BEHIND), fetches each skill upstream
SKILL.md at the repo latest release, and measures line overlap against the local file. Output =
per-skill relationship class (SUPERSET_LOCAL_NO_CONTENT_TO_ADOPT / MERGE_CANDIDATE_SMALL /
LOCAL_DERIVATIVE_REVIEW / DIFFERENT_IMPLEMENTATION) plus the counts behind it.

Promoted from _temp/ to 05-exec/ (r265): a tracked artifact must not cite a gitignored script as
its provenance command, otherwise the command is dead on a fresh clone (r260 lesson).

Read-only: reads D:/global_skills, calls gh api, writes one JSON under 06-benchmark/.
"""
import base64, io, json, os, re, subprocess, time
FACE = json.load(io.open('06-benchmark/r264_sidecar_semantics.json', encoding='utf-8'))
targets = [r for r in FACE['rows'] if r['semantics'] == 'SAME_LINEAGE' and r.get('rel') == 'BEHIND']
print('same-lineage BEHIND', len(targets))
SK = 'D:/global_skills'
OUT = '_temp/r265_follow_all'; os.makedirs(OUT, exist_ok=True)
def gh(args):
    for _ in range(3):
        p = subprocess.run(['gh'] + args, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        if p.returncode == 0:
            return p.stdout, None
        if 'HTTP 404' in (p.stderr or ''):
            return None, 'HTTP 404'
        time.sleep(1.5)
    return None, 'rc=%d:%s' % (p.returncode, (p.stderr or '')[:100])
def latest_tag(repo):
    o, e = gh(['api', 'repos/%s/releases/latest' % repo])
    if e: return None, e
    return (json.loads(o).get('tag_name') or '').strip() or None, None
rows, tags = [], {}
for r in targets:
    repo, slug = r['upstream_repo'], r['skill']
    if repo not in tags:
        tags[repo] = latest_tag(repo)
    tag, terr = tags[repo]
    lp = os.path.join(SK, slug, 'SKILL.md')
    if not tag:
        rows.append({'skill': slug, 'repo': repo, 'upstream_ref': None, 'state': 'TAG_UNAVAILABLE', 'error': terr}); continue
    up = r.get('upstream_path')
    path = (up + '/SKILL.md') if up else 'SKILL.md'
    o, e = gh(['api', 'repos/%s/contents/%s?ref=%s' % (repo, path, tag), '--jq', '.content'])
    if e:
        rows.append({'skill': slug, 'repo': repo, 'upstream_ref': tag, 'state': 'UNAVAILABLE', 'error': e}); continue
    raw = base64.b64decode(''.join(o.split()))
    d = os.path.join(OUT, slug); os.makedirs(d, exist_ok=True)
    with io.open(os.path.join(d, 'SKILL.md'), 'wb') as fh:
        fh.write(raw)
    ut = raw.decode('utf-8', 'replace')
    lt = io.open(lp, encoding='utf-8', errors='replace').read() if os.path.isfile(lp) else ''
    ll = [x.strip() for x in lt.split(chr(10)) if x.strip()]
    ul = [x.strip() for x in ut.split(chr(10)) if x.strip()]
    lset, uset = set(ll), set(ul)
    sub = len(uset & lset) / max(1, len(uset))
    up_only = len(uset - lset)
    lo_only = len(lset - uset)
    if up_only == 0:
        rel_cls = 'SUPERSET_LOCAL_NO_CONTENT_TO_ADOPT'
    elif sub >= 0.9:
        rel_cls = 'MERGE_CANDIDATE_SMALL'
    elif sub >= 0.25:
        rel_cls = 'LOCAL_DERIVATIVE_REVIEW'
    else:
        rel_cls = 'DIFFERENT_IMPLEMENTATION'
    rows.append({'skill': slug, 'repo': repo, 'upstream_ref': tag, 'state': 'OK',
                  'local_bytes': len(lt.encode('utf-8')), 'upstream_bytes': len(ut.encode('utf-8')),
                  'local_lines': len(ll), 'upstream_lines': len(ul),
                  'upstream_lines_in_local_pct': round(100 * sub, 1),
                  'upstream_only_n': up_only, 'local_only_n': lo_only, 'relationship': rel_cls})
    print('  %-30s up_only=%-4d local_only=%-4d in_local=%.1f%%  %s' % (slug, up_only, lo_only, 100 * sub, rel_cls))
doc = {'schema': 'follow-version-feasibility-v1', 'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
       'provenance_cmd': 'python _temp/r265_feasibility.py',
       'rule': 'R264-3: decide the sync semantics per skill from measured line overlap, not from the version tag',
       'face_in': '06-benchmark/r264_sidecar_semantics.json (SAME_LINEAGE + BEHIND)',
       'targets_n': len(targets), 'rows': rows}
io.open('06-benchmark/r265_follow_version_feasibility.json', 'w', encoding='utf-8', newline='').write(json.dumps(doc, ensure_ascii=False, indent=1))
import collections
print('by_relationship', dict(collections.Counter(x.get('relationship') for x in rows if x.get('state') == 'OK')))
print('[FEAS:OK] -> 06-benchmark/r265_follow_version_feasibility.json')
