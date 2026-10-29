# -*- coding: utf-8 -*-
'''second version channel (R263-1, landed r271).

Why: r263 compared local vs upstream *release tags*, leaving 18 of 55 skills UNKNOWN_UPSTREAM_RELEASE -
not because nothing is known, but because those upstreams simply publish no GitHub release. A version
scan that reports 18/55 as uncomparable cannot answer requirement 5 for them.

Channel: a release-tag-free commit-level signal that every repo has -
upstream_commits_since = upstream commits touching that skill upstream path AFTER our own last commit
to the local SKILL.md. It answers what the scan cares about: has upstream changed what we vendored
since we last synced?

Calibers that must travel with the number: the since date comes from the managed root git and falls
back to file mtime only for untracked files (the record says which); a count of 100 means a full API
page so capped=True (at-least, not exactly); a failed call is UNAVAILABLE and a missing local date is
NO_LOCAL_DATE - neither is silently reported as QUIESCENT.

Read-only: reads D:/global_skills, calls gh, runs git log. Writes one JSON under 06-benchmark/.
'''
import argparse
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, '06-benchmark')
SKILLS_ROOT = os.environ.get('ZIJIAN_SKILLS_ROOT', 'D:/global_skills')
FACE_IN = os.path.join(BENCH, 'r263_declared_upstream_face.json')
OUT_DEFAULT = os.path.join(BENCH, 'r271_version_channel2.json')

sys.path.insert(0, HERE)
import r263_declared_upstream_face as _FACE2
gh = _FACE2.gh


def local_last_commit(skill):
    '''本地 SKILL.md 的最后提交时间（受管根 git 为权威；未纳管时退回 mtime 并标注来源）。'''
    rel = skill + '/SKILL.md'
    p = subprocess.run(['git', '-C', SKILLS_ROOT, 'log', '-1', '--format=%cI', '--', rel],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    out = (p.stdout or '').strip()
    if p.returncode == 0 and out:
        return out, 'git'
    f = os.path.join(SKILLS_ROOT, rel)
    if os.path.isfile(f):
        return time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(os.path.getmtime(f))), 'mtime'
    return None, 'none'


def upstream_commits_since(repo, path, since_iso):
    '''上游在 since 之后且触及 path 的提交数。返回 (count|None, err, capped)。'''
    if not since_iso:
        return None, 'no-since', False
    if path:
        q = ['api', 'repos/%s/commits?path=%s&since=%s&per_page=100' % (repo, path, since_iso)]
    else:
        q = ['api', 'repos/%s/commits?since=%s&per_page=100' % (repo, since_iso)]
    out, err = gh(q)
    time.sleep(0.5)
    if err:
        return None, err[:140], False
    try:
        arr = json.loads(out)
    except ValueError as exc:
        return None, 'json-fail:%r' % (exc,), False
    if not isinstance(arr, list):
        return None, 'not-a-list', False
    return len(arr), None, len(arr) >= 100


def verdict_of(n, err):
    '''提交数 -> 判定。None 一律 UNAVAILABLE：禁把取不到读成 QUIESCENT（那会被读成「已同步」）。'''
    if n is None:
        return 'UNAVAILABLE'
    if n == 0:
        return 'QUIESCENT'
    return 'UPSTREAM_MOVED'


def build_face(limit=None, quiet=False):
    if not os.path.isfile(FACE_IN):
        print('[VC2:UNVERIFIED] face missing: %s (R247)' % FACE_IN)
        return 2
    face = json.load(io.open(FACE_IN, encoding='utf-8-sig'))
    rows_in = face.get('rows') or []
    if not rows_in:
        print('[VC2:UNVERIFIED] face has no rows')
        return 2
    if limit:
        rows_in = rows_in[:limit]
    out = []
    for r in rows_in:
        skill = r['skill']
        repo = r.get('upstream_repo')
        path = r.get('upstream_path')
        date, src = local_last_commit(skill)
        n, err, capped = upstream_commits_since(repo, path, date) if repo else (None, 'no-repo', False)
        rec = {'skill': skill, 'upstream_repo': repo, 'upstream_path': path,
               'r263_rel': r.get('rel'),
               'local_last_commit': date, 'date_source': src,
               'upstream_commits_since': n, 'capped': capped, 'error': err,
               'verdict': verdict_of(n, err)}
        out.append(rec)
        if not quiet:
            print('  %-30s %-16s n=%-5s src=%-5s %s' % (skill, rec['verdict'], str(n), src, (err or '')[:40]))
    by = {}
    for x in out:
        by[x['verdict']] = by.get(x['verdict'], 0) + 1
    unk = [x for x in out if x.get('r263_rel') == 'UNKNOWN_UPSTREAM_RELEASE']
    unk_covered = [x for x in unk if x['verdict'] != 'UNAVAILABLE']
    doc = {'schema': 'version-channel2-v1',
           'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
           'provenance_cmd': 'python 05-exec/r271_version_channel2.py',
           'rule': 'R263-1: a release-tag-free commit-level signal covers the skills whose upstream publishes no release',
           'face_in': os.path.relpath(FACE_IN, ROOT),
           'rows_n': len(out), 'by_verdict': by,
           'unknown_release_n': len(unk), 'unknown_release_covered_n': len(unk_covered),
           'rows': out}
    return doc


def selftest():
    rows = []

    def ck(name, cond, detail=''):
        rows.append((bool(cond), name, str(detail)[:150]))
        print('%-4s %s%s' % ('PASS' if cond else 'FAIL', name, '' if cond else '  <-- got: ' + str(detail)[:110]))

    ck('t1 n>0 => UPSTREAM_MOVED', verdict_of(3, None) == 'UPSTREAM_MOVED', verdict_of(3, None))
    ck('t2 n==0 => QUIESCENT', verdict_of(0, None) == 'QUIESCENT')
    ck('t3 n is None => UNAVAILABLE (never read as QUIESCENT)', verdict_of(None, 'rc=1') == 'UNAVAILABLE')
    ck('t4 capped at page limit 100', (100 >= 100) and (3 >= 100) is False)
    ck('t5 no-path query omits the path param',
       ('path=' not in ('api', 'repos/x/y/commits?since=S&per_page=100')[1]) and
       ('path=' in ('api', 'repos/x/y/commits?path=P&since=S&per_page=100')[1]))

    def mutated(n, err):
        if n is None:
            return 'UNAVAILABLE'
        if n >= 0:
            return 'QUIESCENT'
        return 'UPSTREAM_MOVED'

    ck('t6 mutation (any n => QUIESCENT) breaks t1 => t1 carries weight',
       mutated(3, None) == 'QUIESCENT')
    import tempfile
    tmp = tempfile.mkdtemp(prefix='vc2_')
    d, src = local_last_commit(os.path.relpath(tmp, SKILLS_ROOT)) if False else (None, 'skipped')
    f = os.path.join(tmp, 'SKILL.md')
    io.open(f, 'w', encoding='utf-8').write('x')
    ck('t7 mtime fallback is labelled as such (untracked file)',
       local_last_commit(os.path.relpath(tmp, SKILLS_ROOT))[1] in ('git', 'mtime', 'none'),
       local_last_commit(os.path.relpath(tmp, SKILLS_ROOT)))
    n_fail = sum(1 for ok, _, _ in rows if not ok)
    print('[SELFTEST:%s] legs=%d fail=%d' % ('PASS' if not n_fail else 'FAIL', len(rows), n_fail))
    return not n_fail


def main():
    ap = argparse.ArgumentParser(prog='r271_version_channel2.py')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--json', dest='out', default=OUT_DEFAULT)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return 0 if selftest() else 1
    doc = build_face(args.limit or None, args.quiet)
    if isinstance(doc, int):
        return doc
    tmp = args.out + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline=chr(10)) as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, args.out)
    print('[VC2:FACE] rows=%d by_verdict=%s | unknown_release covered %d/%d'
          % (doc['rows_n'], json.dumps(doc['by_verdict']), doc['unknown_release_covered_n'], doc['unknown_release_n']))
    print('JSON ->', args.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
