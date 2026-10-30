# -*- coding: utf-8 -*-
r'''check_r305a.py - long-term face assertion for the quarterly archives (r305a).

Why this file exists:
  The quarterly cadence watchdog turns green on the newest archive inside its scan face.
  The version-scan runner also emits archive-shaped documents stamped exactly the way the
  watchdog reads stamps. Nothing in either file ties the two together, so a version scan
  can keep the watchdog green while the depth audit never ran. This script pins that
  relationship as a recomputable assertion and gives it teeth with two negative controls.

How it works:
  1. load the watchdog module by path and read its own scan face and threshold from it;
  2. run its command-line once against the live repository and record that reading;
  3. negative control A: one clearly over-age archive alone must still be reported stale;
  4. negative control B: an old plus a new archive must make the pick land on the new one,
     with the quarter identifier taken from the picked path;
  5. write the version-scan document at the path its producer declares, point the watchdog
     picker at it, and report whether the version scan lands inside the face.

Exit codes: 0 every assertion held / 1 at least one assertion failed.
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
VERSION_SCAN = os.path.join(REPO, '_repro', 'r304a', 'r304_quarterly_version_scan.py')
STAMP_FMT = '%Y-%m-%dT%H:%M:%S'
STALE_QUARTER = '2020Q1'
STALE_STAMP = '2020-01-01T00:00:00'
NEW_QUARTER = '2026Q4'
NEW_STAMP = '2026-10-28T12:00:00'
SCRATCH = os.path.join(HERE, '_scratch')
os.makedirs(SCRATCH, exist_ok=True)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError('cannot load ' + str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_watchdog(mod, root, out_json):
    # drive the real entry point against a chosen root; the picker default is the only knob
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


def build_tree(root, rows, segment):
    # one archive per quarter, stamped the way the producer stamps its own
    for quarter, stamp in rows:
        d = os.path.join(root, '06-benchmark', segment, quarter)
        os.makedirs(d, exist_ok=True)
        doc = {'schema': 'r304a.quarterly_version_scan.v1', 'generated_at': stamp, 'quarter': quarter}
        with io.open(os.path.join(d, 'audit.json'), 'w', encoding='utf-8', newline=NEWLINE) as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
            fh.write(NEWLINE)


def count_face(root, patterns, strip_prefix):
    n = 0
    for pat in patterns:
        rel = pat[len(strip_prefix) + 1:]
        n += len(glob.glob(os.path.join(root, rel)))
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(prog='check_r305a.py')
    ap.add_argument('--json', dest='out', default=None)
    a = ap.parse_args(argv)

    mod = load_module(WATCHDOG, 'r260_watchdog_ck')
    m4 = load_module(VERSION_SCAN, 'r304_scan_ck')
    checks = []

    def ck(name, cond, detail=''):
        checks.append((bool(cond), name, str(detail)))
        print('%-4s %s%s' % ('PASS' if cond else 'FAIL', name, '' if cond else '  <-- ' + str(detail)))

    # ---- live face: capture the real patterns the picker uses, and the live reading ----
    seen = []
    real_glob = mod.glob.glob

    def spy(*x, **k):
        if x:
            seen.append(x[0])
        return real_glob(*x, **k)

    live_fd, live_json = tempfile.mkstemp(prefix='r305a_live_', suffix='.json', dir=SCRATCH)
    os.close(live_fd)
    mod.glob.glob = spy
    try:
        rc_live, out_live = run_watchdog(mod, mod.ROOT, live_json)
    finally:
        mod.glob.glob = real_glob
    face_abs = sorted(set(seen))
    face_rel = sorted(p[len(mod.ROOT) + 1:].replace(os.sep, '/') for p in face_abs)
    live_doc = json.load(io.open(live_json, encoding='utf-8-sig'))
    os.remove(live_json)
    max_days = live_doc.get('max_days')
    print('--- LIVE FACE (measured, not copied) ---')
    print('[R305A:LIVE] face=%s max_days=%s rc=%s newest=%s stamp=%s'
          % (','.join(face_rel), max_days, live_doc.get('rc'), live_doc.get('newest_audit'),
             live_doc.get('generated_at')))
    ck('watchdog face has two patterns and the threshold is read from it',
       len(face_rel) == 2 and isinstance(max_days, int), (face_rel, max_days))

    # concrete fixture segment derived from the primary pattern, never hand-written
    primary = next((p for p in face_rel if p.count('*') >= 2), face_rel[0])
    fix_dir = primary.split('*')[0] + '_r305a'
    segment = fix_dir.split('/')[-1]

    # ---- negative control A: one over-age archive must stay stale ----
    print('--- LEG A: one over-age archive must not pass as current (negative control) ---')
    tdA = tempfile.mkdtemp(prefix='r305a_legA_', dir=SCRATCH)
    try:
        build_tree(tdA, [(STALE_QUARTER, STALE_STAMP)], segment)
        outA_json = os.path.join(tdA, 'watchdog_reading.json')
        rcA, outA = run_watchdog(mod, tdA, outA_json)
        docA = json.load(io.open(outA_json, encoding='utf-8-sig'))
        for line in outA.rstrip().splitlines():
            print('[LEGA:VERBATIM] ' + line)
        ageA = (datetime.now() - datetime.strptime(STALE_STAMP[:19], STAMP_FMT)).total_seconds() / 86400.0
        stale_verdict = 'rc%d,age_days=%.1f,max_days=%s,verdict=%s' % (
            docA.get('rc'), ageA, docA.get('max_days'),
            'STALE_FAIL' if docA.get('rc') == 1 else 'UNEXPECTED')
        print('[LEGA:VERDICT] %s' % stale_verdict)
        ck('legA verdict is stale rc=1', rcA == 1 and docA.get('rc') == 1,
           (rcA, docA.get('rc'), docA.get('reading')))
        ck('legA prints the failing token', '[CADENCE:FAIL]' in outA, outA[-200:])
        ck('legA failing line names the depth audit as the actor',
           'r113_quarterly_audit' in outA, outA[-300:])
        ck('legA newest archive is the over-age one, not a fresh stand-in',
           docA.get('generated_at') == STALE_STAMP, docA.get('generated_at'))
    finally:
        shutil.rmtree(tdA, ignore_errors=True)

    # ---- negative control B: old plus new must make the pick land on the new one ----
    print('--- LEG B: the newer archive must win the pick (negative control) ---')
    tdB = tempfile.mkdtemp(prefix='r305a_legB_', dir=SCRATCH)
    try:
        build_tree(tdB, [(STALE_QUARTER, STALE_STAMP), (NEW_QUARTER, NEW_STAMP)], segment)
        outB_json = os.path.join(tdB, 'watchdog_reading.json')
        rcB, outB = run_watchdog(mod, tdB, outB_json)
        docB = json.load(io.open(outB_json, encoding='utf-8-sig'))
        for line in outB.rstrip().splitlines():
            print('[LEGB:VERBATIM] ' + line)
        picked = docB.get('newest_audit') or ''
        picked_quarter = os.path.basename(os.path.dirname(picked))
        quarters_n = count_face(tdB, face_abs, mod.ROOT)
        print('[LEGB:VERDICT] picked_quarter=%s stamp=%s quarters_in_face=%d'
              % (picked_quarter, docB.get('generated_at'), quarters_n))
        ck('legB verdict is fresh rc=0', rcB == 0 and docB.get('rc') == 0,
           (rcB, docB.get('rc'), docB.get('reading')))
        ck('legB picks the new quarter and the identifier is right',
           docB.get('generated_at') == NEW_STAMP and picked_quarter == NEW_QUARTER,
           (docB.get('generated_at'), picked_quarter, picked))
        ck('legB face reaches both archives', quarters_n == 2, quarters_n)
    finally:
        shutil.rmtree(tdB, ignore_errors=True)

    # ---- version-scan ownership: its own builder, its own declared path ----
    print('--- VERSION SCAN FACE (ownership assertion) ---')
    declared_rel = m4.season_relpath(NEW_QUARTER).replace(os.sep, '/')
    tdV = tempfile.mkdtemp(prefix='r305a_ver_', dir=SCRATCH)
    try:
        doc304 = m4.build_quarter_doc({}, [], {}, NEW_QUARTER, datetime(2026, 10, 28, 12, 0, 0))
        target = os.path.join(tdV, declared_rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with io.open(target, 'w', encoding='utf-8', newline=NEWLINE) as fh:
            json.dump(doc304, fh, ensure_ascii=False, indent=1)
            fh.write(NEWLINE)
        pickedV, stampV = mod.newest_audit(tdV)
        in_face = pickedV is not None
        print('[R305A:VERSION-SCAN] declared_path=%s schema=%s stamp=%s stamp_format_ok=%s'
              % (declared_rel, doc304.get('schema'), doc304.get('generated_at'),
                 doc304.get('generated_at') == datetime(2026, 10, 28, 12, 0, 0).strftime(STAMP_FMT)))
        print('[R305A:VERSION-SCAN] watchdog_picker_sees_it=%s picked=%s'
              % (str(in_face).lower(), (pickedV[len(tdV) + 1:].replace(os.sep, '/') if pickedV else None)))
        if in_face:
            print('[R305A:ALARM] the version-scan artifact is inside the watchdog face: a scan run can keep the quarterly watchdog green while the depth audit never ran.')
        ck('version-scan document is written at the path its producer declares',
           os.path.isfile(target), target)
        ck('version-scan stamp matches the watchdog stamp format',
           doc304.get('generated_at') == datetime(2026, 10, 28, 12, 0, 0).strftime(STAMP_FMT),
           doc304.get('generated_at'))
    finally:
        shutil.rmtree(tdV, ignore_errors=True)

    # ---- ownership table must not lie about the measured face ----
    own_path = os.path.join(HERE, 'ownership.json')
    own_present = os.path.isfile(own_path)
    own = json.load(io.open(own_path, encoding='utf-8-sig')) if own_present else {}
    own_rows = {r.get('producer_key'): r for r in (own.get('owners') or [])}
    scan_row = own_rows.get('version_scan')
    owner_row = own_rows.get('quarterly_depth_audit')
    ck('ownership table present and parses', own_present and len(own_rows) == 2, own_path)
    ck('scan row satisfies_watchdog equals the measured face',
       bool(scan_row) and scan_row.get('satisfies_watchdog') == in_face,
       (scan_row.get('satisfies_watchdog') if scan_row else None, in_face))
    ck('scan row is not marked responsible for the green',
       bool(scan_row) and scan_row.get('responsible_for_green') is False,
       (scan_row.get('responsible_for_green') if scan_row else None))
    ck('depth audit row is the designated owner and is in the face',
       bool(owner_row) and owner_row.get('satisfies_watchdog') is True
       and owner_row.get('responsible_for_green') is True, owner_row)
    ck('ownership threshold equals the watchdog default',
       (own.get('watchdog') or {}).get('stale_threshold_days') == max_days,
       ((own.get('watchdog') or {}).get('stale_threshold_days'), max_days))
    ck('ownership face patterns equal the measured patterns',
       sorted((own.get('watchdog') or {}).get('glob_patterns') or []) == face_rel,
       ((own.get('watchdog') or {}).get('glob_patterns'), face_rel))
    ck('ownership carries the fake-green alarm when the scan is in the face',
       (not in_face) or (own.get('fake_green_risk') or {}).get('state') == 'open',
       (in_face, (own.get('fake_green_risk') or {}).get('state')))

    fails = [n for ok, n, _ in checks if not ok]
    passed = len(checks) - len(fails)
    LONGTERM = ('[R305A:LONGTERM] watchdog_face=%s version_scan_in_face=%s quarters=%d newest=%s stale=%s stale_verdict=%s'
                % (','.join(face_rel), str(in_face).lower(), quarters_n, picked_quarter,
                   STALE_QUARTER, stale_verdict))
    result = {
        'schema': 'r305a.check.v1',
        'measured_at': datetime.now().strftime(STAMP_FMT),
        'watchdog_face': face_rel,
        'max_days': max_days,
        'live_reading': live_doc,
        'live_stdout': out_live,
        'legA_verbatim': outA,
        'legB_verbatim': outB,
        'legA_verdict': stale_verdict,
        'legB_picked_quarter': picked_quarter,
        'quarters': quarters_n,
        'version_scan_in_face': in_face,
        'version_scan_declared_path': declared_rel,
        'checks': [{'ok': ok, 'name': n, 'detail': d} for ok, n, d in checks],
        'failed': fails,
        'longterm_line': LONGTERM,
    }
    if a.out:
        with io.open(a.out, 'w', encoding='utf-8', newline=NEWLINE) as fh:
            json.dump(result, fh, ensure_ascii=False, indent=1)
            fh.write(NEWLINE)
    print('夹具合计: %d 项，通过 %d，失败 %d' % (len(checks), passed, len(fails)))
    if fails:
        print('[R305A:CHECK-FAIL] ' + ','.join(fails))
    else:
        print('[R305A:CHECK-PASS] ' + str(len(checks)) + ' checks')
    print(LONGTERM)
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
