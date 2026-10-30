# -*- coding: utf-8 -*-
r'''r303a anchor builder: build the absorption baseline for the 49 lineage pairs.

Why: the priority table named the one layer that could not be answered - whether a
same-named upstream file changed since absorption. The absorption-time sha was never
recorded, so it cannot be known now; today becomes the anchor. Honest caliber: this
records an anchor, not a reconstruction of history.
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
PROJ = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir, os.pardir))
DIR_SELF = '自建skill优化'
REPRO_DIR = os.path.join(PROJ, DIR_SELF, '_repro', 'r299a')
EXEC_DIR = os.path.join(PROJ, DIR_SELF, '05-exec')
sys.path.insert(0, EXEC_DIR)
import r114_replacement_scan as R114
parse_version = R114.parse_version
SKILLS_ROOT = os.environ.get('ZIJIAN_SKILLS_ROOT', 'D:/global_skills')

ANCHOR_NOTE = ('历史吸收时该同名件的 sha 未留痕 => 已不可知; 本件以生成时刻为基准锚点, '
               '自此往后「同名件内容变没变」成为可判读数. 本锚只标志可比对的零时刻, '
               '不代表吸收当时的历史状态. local_file_sha 为本地件字节的 sha256(64 位十六进制); '
               'upstream_file_sha 为上游同名件的 git blob sha1(40 位十六进制) - 两者算法不同, '
               '不可跨域比较, 只与各自的历史值比较. upstream_commit_sha 为锚定时刻该仓默认分支的提交号.')


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


def find_git_bash():
    # The harness shell is a bundled Git Bash; a bare 'bash' can resolve to WSL,
    # which cannot see the Windows drive paths this project uses.
    try:
        p = subprocess.run(['where.exe', 'bash'], capture_output=True)
        for line in p.stdout.decode('utf-8', 'replace').splitlines():
            c = line.strip()
            if c and 'System32' not in c and os.path.isfile(c):
                return c
    except Exception:
        pass
    cands = [
        'C:/Users/37533/.dsh/profiles/desktop/node_modules/@dsh-ops/bash-win32-x64/usr/bin/bash.exe',
        'C:/Program Files/Git/bin/bash.exe',
        'C:/Program Files/Git/usr/bin/bash.exe',
    ]
    for c in cands:
        if os.path.isfile(c):
            return c
    return None


def resolve_upstream_path(row, tree):
    ph = row.get('path_hit') or {}
    if ph.get('path'):
        return ph['path']
    sh = row.get('slug_hits') or []
    if sh and sh[0].get('path'):
        return sh[0]['path']
    ent = tree.get(row['repo']) or {}
    paths = [x['path'] for x in (ent.get('skill_md_paths') or [])]
    if len(paths) == 1:
        return paths[0]
    hits = [p for p in paths if row['slug'] in p]
    if len(hits) == 1:
        return hits[0]
    return None


def make_evidence(repo, branch, path, slug):
    q = chr(39)
    local = SKILLS_ROOT.rstrip('/') + '/' + slug + '/SKILL.md'
    url = q + 'repos/' + repo + '/contents/' + path + '?ref=' + branch + q
    return ' && '.join([
        'gh api repos/' + repo + '/commits/' + branch + ' --jq .sha',
        'gh api ' + url + ' --jq .sha',
        'sha256sum ' + q + local + q + ' | cut -c1-64',
    ])


def build(workers, out_path):
    rows = json.load(open(os.path.join(REPRO_DIR, 'r299_inject_result.json'), encoding='utf-8'))['rows']
    tree = json.load(open(os.path.join(REPRO_DIR, 'tree_paths.json'), encoding='utf-8'))
    lin = [r for r in rows if r.get('kind') == 'lineage']
    lin.sort(key=lambda r: (r['repo'], r['slug']))
    print('lineage_rows', len(lin))
    print('row_keys', sorted(lin[0].keys()))
    repos = sorted(set(r['repo'] for r in lin))
    print('unique_repos', len(repos))

    br = pmap_list(lambda rp: gh(['api', 'repos/' + rp, '--jq', '.default_branch']), repos, workers)
    branches = {}
    for i, rp in enumerate(repos):
        s, v = br[i]
        branches[rp] = (v if (s == 'ok' and v) else None)
        if branches[rp] is None:
            print('WARN_branch', rp, v)
    live = [rp for rp in repos if branches[rp]]
    cr = pmap_list(lambda rp: gh(['api', 'repos/' + rp + '/commits/' + branches[rp], '--jq', '.sha']), live, workers)
    commits = {}
    for i, rp in enumerate(live):
        s, v = cr[i]
        commits[rp] = (v if s == 'ok' else None)
        if commits[rp] is None:
            print('WARN_commit', rp, v)

    tasks = []
    for r in lin:
        tasks.append((r['slug'], r['repo'], resolve_upstream_path(r, tree)))
    print('unresolved_upstream_path', [t[0] for t in tasks if not t[2]])

    def ufn(item):
        slug, repo, path = item
        b = branches.get(repo)
        if not path:
            return {'path': path, 'sha': None, 'version': None, 'err': 'no-upstream-path'}
        if not b:
            return {'path': path, 'sha': None, 'version': None, 'err': 'no-default-branch'}
        ref = 'repos/' + repo + '/contents/' + path + '?ref=' + b
        try:
            sha = gh(['api', ref, '--jq', '.sha'])
            raw = gh(['api', '-H', 'Accept: application/vnd.github.raw', ref])
        except Exception as e:
            return {'path': path, 'sha': None, 'version': None, 'err': str(e)}
        return {'path': path, 'sha': sha, 'version': parse_version(raw), 'err': None}

    def lfn(item):
        slug, repo, path = item
        fp = os.path.join(SKILLS_ROOT, slug, 'SKILL.md')
        if not os.path.isfile(fp):
            return {'sha': None, 'version': None, 'err': 'local-missing'}
        txt = open(fp, encoding='utf-8', errors='replace').read()
        return {'sha': sha256_file(fp), 'version': parse_version(txt), 'err': None}

    ur = pmap_list(ufn, tasks, workers)
    lr = pmap_list(lfn, tasks, workers)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    pairs = []
    fetch_errs = []
    for i, item in enumerate(tasks):
        slug, repo, path = item
        s, u = ur[i]
        if s != 'ok':
            u = {'path': path, 'sha': None, 'version': None, 'err': u}
        s2, l = lr[i]
        if s2 != 'ok':
            l = {'sha': None, 'version': None, 'err': l}
        if u.get('err'):
            fetch_errs.append((slug, 'upstream:' + str(u['err'])[:160]))
        if l.get('err'):
            fetch_errs.append((slug, 'local:' + str(l['err'])[:160]))
        b = branches.get(repo)
        ev = make_evidence(repo, b, path, slug) if (b and path) else None
        pairs.append({
            'slug': slug,
            'repo': repo,
            'upstream_path': path,
            'upstream_commit_sha': commits.get(repo),
            'upstream_file_sha': u['sha'],
            'upstream_version': u['version'],
            'local_file_sha': l['sha'],
            'local_version': l['version'],
            'baseline_at': now,
            'evidence_cmd': ev,
        })
    print('pair_keys', sorted(pairs[0].keys()))
    print('fetch_errors', len(fetch_errs))
    for fe in fetch_errs:
        print('  ERR', fe[0], fe[1])
    miss_u = [p['slug'] for p in pairs if not p['upstream_file_sha']]
    miss_l = [p['slug'] for p in pairs if not p['local_file_sha']]
    print('upstream_sha_missing', len(miss_u), miss_u[:10])
    print('local_sha_missing', len(miss_l), miss_l[:10])
    bad_shape = [p['slug'] for p in pairs if p['local_file_sha'] and len(p['local_file_sha']) != 64]
    print('local_sha_bad_shape', len(bad_shape), bad_shape[:5])
    by_slug = {p['slug']: p for p in pairs}
    mism = []
    for r in lin:
        ph = r.get('path_hit') or {}
        if ph.get('sha') and by_slug[r['slug']]['upstream_file_sha']:
            if not by_slug[r['slug']]['upstream_file_sha'].startswith(ph['sha']):
                mism.append((r['slug'], ph['sha'], by_slug[r['slug']]['upstream_file_sha'][:12]))
    print('tree_sha_prefix_mismatch', len(mism), mism[:5])

    probe = pairs[0]
    fp = SKILLS_ROOT.rstrip('/') + '/' + probe['slug'] + '/SKILL.md'
    q = chr(39)
    shell = 'sha256sum ' + q + fp + q + ' | cut -c1-64'
    sh = find_git_bash()
    if not sh:
        print('sha256sum_selfcheck_skipped_no_git_bash')
    else:
        try:
            sp = subprocess.run([sh, '-c', shell], capture_output=True)
            got = sp.stdout.decode('utf-8', 'replace').strip()
            print('sha256sum_selfcheck_shell', sh)
            print('sha256sum_selfcheck_probe', fp)
            print('sha256sum_selfcheck_matches_python', got == probe['local_file_sha'])
        except Exception as e:
            print('sha256sum_selfcheck_error', e)

    doc = {'schema': 'r303a.absorption_baseline.v1', 'generated_at': now, 'anchor_note': ANCHOR_NOTE, 'pairs': pairs}
    print('top_keys', sorted(doc.keys()))
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    back = json.load(open(out_path, encoding='utf-8'))
    print('reload_ok', sorted(back.keys()), 'pairs', len(back['pairs']))
    incomplete = bool(miss_u or miss_l or bad_shape)
    print('BUILD_INCOMPLETE', incomplete)
    return 1 if incomplete else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(HERE, 'absorption_baseline.json'))
    ap.add_argument('--workers', type=int, default=8)
    a = ap.parse_args()
    sys.exit(build(a.workers, a.out))


if __name__ == '__main__':
    main()