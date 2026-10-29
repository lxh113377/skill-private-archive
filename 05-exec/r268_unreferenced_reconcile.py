# -*- coding: utf-8 -*-
'''independent-check reconciliation for the unreferenced-siblings face (R268-1, landed r268).

Why this file exists: the R267-1 face was verified by a delegated subagent that hand-checked a 12-skill
sample. Its artifacts cite `_temp/r268_indep_negctrl.py` as the reproduce command, but that script is NOT
on disk (measured r268: `ls _temp/r268*` has no indep_* entry) - a dead command of the R261-3 class.
So this tracked script takes over that duty: it reconciles the independent check JSON against the face's
own numbers, under both calibers, and prints the agreement count.

What it compares, per sampled skill: present_n and unreferenced_n (normal caliber) and
unreferenced_strict_n (strict caliber). The r268 finding is on record: normal agrees 11/12, strict 12/12 -
the single divergence was a caliber difference (bare parent-dir mention vs path-shaped mention), which is
why both calibers are stored in the face.

Exit codes: 0 reconciled (prints AGREE/DISAGREE counts) / 2 either artifact missing.
'''
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, '06-benchmark')
FACE = os.path.join(BENCH, 'r268_unreferenced_siblings.json')
INDEP = os.path.join(BENCH, 'r268_unreferenced_independent_check.json')


def main():
    for p in (FACE, INDEP):
        if not os.path.isfile(p):
            print('[RECON:UNVERIFIED] missing artifact: %s (R247)' % p)
            return 2
    face = json.load(io.open(FACE, encoding='utf-8-sig'))
    ind = json.load(io.open(INDEP, encoding='utf-8-sig'))
    mine = {r['slug']: r for r in face['rows']}
    per = ind.get('per_skill') or ind.get('verdict_per_skill') or {}
    if isinstance(per, list):
        per = {x.get('slug'): x for x in per}
    if not per:
        print('[RECON:UNVERIFIED] independent artifact carries no per-skill block')
        return 2
    n_norm = n_str = n_all = 0
    rows = []
    for slug, v in sorted(per.items()):
        r = mine.get(slug)
        if r is None:
            rows.append((slug, None, None))
            continue
        theirs = v.get('unreferenced_n')
        ok_norm = (theirs == r.get('unreferenced_n') and v.get('my_present_n', v.get('present_n')) == r.get('present_n'))
        ok_str = (theirs == r.get('unreferenced_strict_n'))
        n_all += 1
        n_norm += 1 if ok_norm else 0
        n_str += 1 if ok_str else 0
        rows.append((slug, ok_norm, ok_str))
    for slug, a, b in rows:
        print('  %-28s normal=%s strict=%s' % (slug, 'MATCH' if a else 'DISAGREE', 'MATCH' if b else 'DISAGREE'))
    print('[RECON] sample=%d normal_agree=%d strict_agree=%d' % (n_all, n_norm, n_str))
    print('  caliber note: the face stores both readings because r268 measured a caliber-level divergence',
          'on local-mineru (mine normal=4 strict=16; the independent check landed on the strict side).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
