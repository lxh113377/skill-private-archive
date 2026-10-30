# -*- coding: utf-8 -*-
r'''r303a reusable comparator for the absorption baseline.

Reads a baseline document, re-fetches the live sha of the local file and of the
same-named upstream file for every pair, and reports one state per pair:

  OK               both the local file and the upstream file are unchanged
  LOCAL_CHANGED    only the local file changed
  UPSTREAM_CHANGED only the upstream file changed
  BOTH_CHANGED     both changed
  UNKNOWN          anything could not be fetched - never reported as OK

Comparison is always like-for-like across time: the stored local value against the
current local value, and the stored upstream value against the current upstream value.

Usage:
  python -B compare_baseline.py --baseline absorption_baseline.json
'''
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS_ROOT = os.environ.get('ZIJIAN_SKILLS_ROOT', 'D:/global_skills')


def gh(args, attempts=3):
    last = None
    for k in range(attempts):
        try:
            p = subprocess.run(['gh'] + args, capture_output=True, timeout=120)
            if p.returncode == 0:
                return p.stdout.decode('utf-8', 'replace').strip()
            last = ((p.stderr or b'').decode('utf-8', 'replace')).strip()[:300] or ('gh rc=' + str(p.returncode))
        except Exception as e:
            last = str(e)
        time.sleep(0.6 * (k + 1))
    raise RuntimeError(str(last))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        while True:
            chunk = fh.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def pmap_list(fn, items, workers):
    out = [None] * len(items)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {}
        for i, it in enumerate(items):
            futs[ex.submit(fn, it)] = i
        for f in as_completed(futs):
            i = futs[f]
            try:
                out[i] = ('ok', f.result())
            except Exception as e:
                out[i] = ('err', str(e))
    return out


def fetch_refs(repos, workers):
    def rfn(rp):
        b = gh(['api', 'repos/' + rp, '--jq', '.default_branch'])
        c = gh(['api', 'repos/' + rp + '/commits/' + b, '--jq', '.sha'])
        return {'branch': b, 'commit': c}
    st = pmap_list(rfn, repos, workers)
    res = {}
    for i, rp in enumerate(repos):
        s, v = st[i]
        res[rp] = v if s == 'ok' else None
    return res


def evaluate(pair, refs):
    rec = {'slug': pair.get('slug'), 'repo': pair.get('repo')}
    notes = []
    cur_local = None
    fp = os.path.join(SKILLS_ROOT, str(pair.get('slug')), 'SKILL.md')
    try:
        if os.path.isfile(fp):
            cur_local = sha256_file(fp)
        else:
            notes.append('local-file-missing')
    except Exception as e:
        notes.append('local-read-error:' + str(e))
    cur_ups = None
    ref = refs.get(pair.get('repo'))
    path = pair.get('upstream_path')
    if ref is None:
        notes.append('upstream-ref-unavailable')
    elif not path:
        notes.append('upstream-path-missing')
    else:
        try:
            cur_ups = gh(['api', 'repos/' + pair['repo'] + '/contents/' + path + '?ref=' + ref['branch'], '--jq', '.sha'])
        except Exception as e:
            notes.append('upstream-fetch-error:' + str(e))
    base_l = pair.get('local_file_sha')
    base_u = pair.get('upstream_file_sha')
    rec['baseline_local_sha'] = base_l
    rec['baseline_upstream_sha'] = base_u
    rec['current_local_sha'] = cur_local
    rec['current_upstream_sha'] = cur_ups
    rec['current_upstream_commit_sha'] = (ref or {}).get('commit')
    if base_l is None or base_u is None or cur_local is None or cur_ups is None:
        rec['state'] = 'UNKNOWN'
        rec['local_changed'] = None
        rec['upstream_changed'] = None
    else:
        lc = (cur_local != base_l)
        uc = (cur_ups != base_u)
        rec['local_changed'] = lc
        rec['upstream_changed'] = uc
        if lc and uc:
            rec['state'] = 'BOTH_CHANGED'
        elif lc:
            rec['state'] = 'LOCAL_CHANGED'
        elif uc:
            rec['state'] = 'UPSTREAM_CHANGED'
        else:
            rec['state'] = 'OK'
    rec['notes'] = notes
    return rec


def summarize(records):
    s = {'pairs': len(records), 'ok': 0, 'local_changed': 0, 'upstream_changed': 0, 'both_changed': 0, 'unknown': 0}
    for r in records:
        st = r['state']
        if st == 'OK':
            s['ok'] += 1
        elif st == 'LOCAL_CHANGED':
            s['local_changed'] += 1
        elif st == 'UPSTREAM_CHANGED':
            s['upstream_changed'] += 1
        elif st == 'BOTH_CHANGED':
            s['both_changed'] += 1
        else:
            s['unknown'] += 1
    return s


def run_comparison(baseline_path, workers, only=None):
    doc = json.load(open(baseline_path, encoding='utf-8'))
    pairs = doc.get('pairs') or []
    if only:
        want = set(x for x in only if x)
        pairs = [p for p in pairs if p.get('slug') in want]
    repos = sorted(set(p.get('repo') for p in pairs if p.get('repo')))
    refs = fetch_refs(repos, workers)
    st = pmap_list(lambda p: evaluate(p, refs), pairs, workers)
    records = []
    for i in range(len(pairs)):
        s, v = st[i]
        if s == 'ok':
            records.append(v)
        else:
            records.append({'slug': pairs[i].get('slug'), 'repo': pairs[i].get('repo'), 'state': 'UNKNOWN',
                            'local_changed': None, 'upstream_changed': None, 'notes': ['pair-eval-error:' + str(v)]})
    return doc, records


def main(argv=None):
    ap = argparse.ArgumentParser(description='r303a absorption baseline comparator')
    ap.add_argument('--baseline', default=os.path.join(HERE, 'absorption_baseline.json'))
    ap.add_argument('--json-out', default=None)
    ap.add_argument('--only', default=None)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args(argv)
    if not os.path.isfile(a.baseline):
        print('FAIL baseline-not-found')
        return 2
    only = a.only.split(',') if a.only else None
    doc, records = run_comparison(a.baseline, a.workers, only)
    s = summarize(records)
    if not a.quiet:
        for r in records:
            print('%-30s %-16s local_changed=%-5s upstream_changed=%-5s notes=%s' % (r.get('slug'), r['state'], r.get('local_changed'), r.get('upstream_changed'), ','.join(r.get('notes') or [])))
    print('[R303A:COMPARE] pairs=%d ok=%d local_changed=%d upstream_changed=%d both_changed=%d unknown=%d' % (s['pairs'], s['ok'], s['local_changed'], s['upstream_changed'], s['both_changed'], s['unknown']))
    if a.json_out:
        out = {'baseline': os.path.abspath(a.baseline), 'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat(), 'pairs': records, 'summary': s}
        with open(a.json_out, 'w', encoding='utf-8') as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())