# -*- coding: utf-8 -*-
'''r304 quarterly version scan acceptance check.

What it does: drives the quarterly runner over the live baseline and prints one
machine-readable scan line last. It also exposes two negative-control legs that are
replayed in a throwaway area, so the criteria are shown to have teeth:
  leg A - perturb one stored upstream blob id by a single hex digit; that pair must be
          reported UPSTREAM_CHANGED and must enter the candidate list;
  leg B - point one stored upstream path at a path that cannot exist under any ref;
          that pair must be UNKNOWN and must stay out of the candidate list.

Exit codes: 0 scanned (or both legs passed) / 2 baseline missing (UNVERIFIED) / 1 legs failed.
'''
import argparse
import importlib.util
import json
import os
import sys
import tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
RUNNER_NAME = 'r304_quarterly_version_scan.py'
LEG_A_SLUG = 'data-analysis'
LEG_B_SLUG = 'rag-eval'


def load_runner():
    path = os.path.join(HERE, RUNNER_NAME)
    spec = importlib.util.spec_from_file_location('r304_quarterly_runner', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def degraded_line(quarter, why):
    return ('[R304:SCAN] quarter=%s pairs=0 ok=0 upstream_changed=0 local_changed=0 both=0 unknown=0 candidates=0 unverified=%s rc=2'
            % (quarter, why))


def mutate_copy(baseline_path, dest, slug, mutator):
    # the negative controls never touch the real baseline: they work on a throwaway copy
    doc = json.load(open(baseline_path, encoding='utf-8'))
    hit = False
    for p in doc.get('pairs') or []:
        if p.get('slug') == slug:
            mutator(p)
            hit = True
    if not hit:
        raise SystemExit('negative control: target pair not present: ' + slug)
    json.dump(doc, open(dest, 'w', encoding='utf-8'), ensure_ascii=False)
    return dest


def leg_a_mutator(p):
    old = str(p.get('upstream_file_sha') or '')
    if not old:
        raise SystemExit('negative control: leg A pair carries no stored upstream blob id')
    first = '0' if old[0] != '0' else '1'
    p['upstream_file_sha'] = first + old[1:]


def leg_b_mutator(p):
    p['upstream_path'] = '__r304a_negative_control__/absent-under-any-ref.md'


def show_leg(runner, tag, baseline_path, slug, outroot, workers):
    qdoc, rc, q = runner.run_scan(baseline=baseline_path, outdir=outroot, quarter=tag, workers=workers, only=[slug], write=True, verbose=True, quiet=False)
    if qdoc is None:
        print('[R304:NC-%s] rc=%d no-document' % (tag, rc))
        return None, rc
    print(runner.format_scan_line(qdoc['summary'], q))
    return qdoc, rc


def selftest(runner, baseline, workers):
    if not os.path.isfile(baseline):
        print(degraded_line(runner.quarter_of(datetime.now()), 'baseline-missing'))
        return 2
    fails = []
    with tempfile.TemporaryDirectory() as td:
        print('[R304:NC] leg A: stored upstream blob id of pair %s perturbed by one hex digit' % LEG_A_SLUG)
        ma = mutate_copy(baseline, os.path.join(td, 'legA.json'), LEG_A_SLUG, leg_a_mutator)
        docA, rcA = show_leg(runner, 'legA', ma, LEG_A_SLUG, os.path.join(td, 'outA'), workers)
        okA = bool(docA) and docA['pairs'][0].get('state') == 'UPSTREAM_CHANGED' and len(docA.get('candidates') or []) == 1 and (docA['candidates'][0].get('slug') == LEG_A_SLUG)
        print('[R304:NC-A] verdict=%s' % ('PASS' if okA else 'FAIL'))
        if not okA:
            fails.append('legA')
        print('[R304:NC] leg B: stored upstream path of pair %s pointed at an absent path' % LEG_B_SLUG)
        mb = mutate_copy(baseline, os.path.join(td, 'legB.json'), LEG_B_SLUG, leg_b_mutator)
        docB, rcB = show_leg(runner, 'legB', mb, LEG_B_SLUG, os.path.join(td, 'outB'), workers)
        okB = bool(docB) and docB['pairs'][0].get('state') == 'UNKNOWN' and len(docB.get('candidates') or []) == 0
        print('[R304:NC-B] verdict=%s' % ('PASS' if okB else 'FAIL'))
        if not okB:
            fails.append('legB')
    if fails:
        print('[R304:NC:FAIL] %s' % fails)
        return 1
    print('[R304:NC:PASS] leg A caught drift and entered a candidate; leg B stayed UNKNOWN and out of candidates')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog='check_r304a.py')
    ap.add_argument('--baseline', default=None)
    ap.add_argument('--outdir', default=None)
    ap.add_argument('--quarter', default=None)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--only', default=None)
    ap.add_argument('--no-write', action='store_true')
    ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    runner = load_runner()
    baseline = a.baseline or runner.DEFAULT_BASELINE
    only = a.only.split(',') if a.only else None
    if a.selftest:
        return selftest(runner, baseline, a.workers)
    qdoc, rc, q = runner.run_scan(baseline=baseline, outdir=(a.outdir or HERE), quarter=a.quarter, workers=a.workers, only=only, write=not a.no_write, verbose=not a.quiet, quiet=a.quiet)
    if rc == 2 or qdoc is None:
        print(degraded_line(q, 'baseline-missing'))
        return 2
    cand = qdoc.get('candidates') or []
    drift = qdoc.get('local_drift') or []
    unk = qdoc.get('unknown_pairs') or []
    print('[R304:CANDIDATES] %s' % (','.join('%s:%s' % (c.get('slug'), c.get('state')) for c in cand) or '(none)'))
    print('[R304:LOCAL_DRIFT] %s' % (','.join(c.get('slug') for c in drift) or '(none)'))
    print('[R304:UNKNOWN] %s' % (','.join(c.get('slug') for c in unk) or '(none)'))
    print(runner.format_scan_line(qdoc['summary'], q))
    return 0


if __name__ == '__main__':
    sys.exit(main())