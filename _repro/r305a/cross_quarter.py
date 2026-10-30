# -*- coding: utf-8 -*-
r'''cross_quarter.py - roll the version-scan archives across quarters (r305a).

Why this file exists:
  One archive answers only whether its own stamp is inside the limit. It cannot answer
  which archive the quarterly cadence watchdog would actually read, nor what the watchdog
  says about the older ones. This runner puts the whole archive set on one table and takes
  both the pick and the verdict from the watchdog module itself, imported at run time, so
  the reading cannot drift from the green light by hand-copying a rule.

How it works:
  1. mirror the watchdog scan layout in a scratch tree, one archive per quarter;
  2. ask the watchdog module which archive it would read, through its own picker;
  3. ask the watchdog module for the age verdict of every archive, through its own judge;
  4. report the quarter count, the picked quarter, the per-quarter age table and the
     verdict carried by the oldest archive;
  5. delete the scratch tree unless a keep directory is requested.

Exit codes: 0 reading produced / 2 the watchdog module could not be loaded.
'''
import argparse
import contextlib
import glob
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

NEWLINE = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
WATCHDOG = os.path.join(REPO, '05-exec', 'r260_quarterly_cadence.py')
STAMP_FMT = '%Y-%m-%dT%H:%M:%S'
SCHEMA = 'r305a.cross-quarter.v1'
SCRATCH = os.path.join(HERE, '_scratch')
os.makedirs(SCRATCH, exist_ok=True)
DEFAULT_ROWS = (('2020Q1', '2020-01-01T00:00:00'), ('2026Q4', '2026-10-28T12:00:00'))


def load_module(path, name):
    # import by file path so the watchdog itself is used, never a rewritten rule
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError('cannot load ' + str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_watchdog(mod, root, out_json):
    # drive the real command-line entry point against a chosen root and capture its printout
    saved = mod.newest_audit.__defaults__
    mod.newest_audit.__defaults__ = (root,)
    old_argv = sys.argv[:]
    sys.argv = ['r260_quarterly_cadence.py', '--json', out_json]
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = mod.main()
    finally:
        mod.newest_audit.__defaults__ = saved
        sys.argv = old_argv
    return rc, buf.getvalue()


def face_patterns(mod, root):
    # read the scan face for real: record every pattern the picker hands to glob
    seen = []
    real = mod.glob.glob

    def spy(*a, **k):
        if a:
            seen.append(a[0])
        return real(*a, **k)

    mod.glob.glob = spy
    try:
        mod.newest_audit(root)
    finally:
        mod.glob.glob = real
    return sorted(set(seen))


def build_tree(root, rows, segment):
    # one archive per quarter, stamped the way the producer stamps its own
    for quarter, stamp in rows:
        d = os.path.join(root, '06-benchmark', segment, quarter)
        os.makedirs(d, exist_ok=True)
        doc = {'schema': SCHEMA, 'generated_at': stamp, 'quarter': quarter}
        with io.open(os.path.join(d, 'audit.json'), 'w', encoding='utf-8', newline=NEWLINE) as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
            fh.write(NEWLINE)


def count_face(root, patterns, strip_prefix):
    # count the archives the face actually reaches under this root
    n = 0
    for pat in patterns:
        rel = pat[len(strip_prefix) + 1:]
        n += len(glob.glob(os.path.join(root, rel)))
    return n


def live_max_days(mod):
    # threshold read from the watchdog itself: one command-line run, value taken from its JSON
    fd, out = tempfile.mkstemp(prefix='r305a_maxd_', suffix='.json', dir=SCRATCH)
    os.close(fd)
    try:
        run_watchdog(mod, mod.ROOT, out)
        doc = json.load(io.open(out, encoding='utf-8-sig'))
        return doc.get('max_days')
    finally:
        os.remove(out)


def roll(rows=DEFAULT_ROWS, now=None, max_days=None, keep=None):
    now = now or datetime.now()
    mod = load_module(WATCHDOG, 'r260_watchdog_xq')
    td = tempfile.mkdtemp(prefix='r305a_xq_', dir=SCRATCH)
    try:
        primary = face_patterns(mod, td)[0]
        segment = primary[len(td) + 1:].split('*')[0] + '_r305a'
        segment = segment.replace(os.sep, '/').split('/')[-1]
        build_tree(td, rows, segment)
        patterns = face_patterns(mod, td)
        if max_days is None:
            max_days = live_max_days(mod)
        picked, picked_ts = mod.newest_audit(td)
        table = []
        for quarter, stamp in rows:
            d = datetime.strptime(stamp[:19], STAMP_FMT)
            rc, why = mod.judge(d, now, max_days)
            age = (now - d).total_seconds() / 86400.0
            verdict = 'FRESH' if rc == 0 else ('STALE' if rc == 1 else 'UNVERIFIED')
            table.append({'quarter': quarter, 'generated_at': stamp, 'age_days': round(age, 1),
                          'rc': rc, 'verdict': verdict, 'watchdog_reading': why})
        oldest = min(table, key=lambda e: e['generated_at'])
        newest = None
        if picked:
            newest = json.load(io.open(picked, encoding='utf-8-sig')).get('quarter')
        reading = {
            'schema': SCHEMA,
            'watchdog': {
                'path': os.path.relpath(WATCHDOG, REPO).replace(os.sep, '/'),
                'glob_patterns': [p[len(td) + 1:].replace(os.sep, '/') for p in patterns],
                'max_days': max_days,
                'newest_rule': 'max generated_at over the face; directory names are not ranked',
            },
            'now': now.strftime(STAMP_FMT),
            'quarters_n': len(table),
            'quarters_in_face': count_face(td, patterns, td),
            'quarters': table,
            'newest': newest,
            'newest_selected_path': (picked[len(td) + 1:].replace(os.sep, '/') if picked else None),
            'stale': oldest['quarter'],
            'stale_rc': oldest['rc'],
            'stale_verdict': oldest['watchdog_reading'],
        }
        if keep:
            shutil.copytree(td, keep, dirs_exist_ok=True)
            reading['kept_at'] = keep
        return reading
    finally:
        shutil.rmtree(td, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(prog='cross_quarter.py')
    ap.add_argument('--json', dest='out', default=None)
    ap.add_argument('--keep', default=None)
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args(argv)
    reading = roll(keep=a.keep)
    text = json.dumps(reading, ensure_ascii=False, indent=1)
    if a.out:
        with io.open(a.out, 'w', encoding='utf-8', newline=NEWLINE) as fh:
            fh.write(text)
    if not a.quiet:
        print(text)
    print('[R305A:CROSS-QUARTER] quarters=%d in_face=%d newest=%s stale=%s stale_rc=%s'
          % (reading['quarters_n'], reading['quarters_in_face'], reading['newest'],
             reading['stale'], reading['stale_rc']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
