# -*- coding: utf-8 -*-
r'''r303a gate for the absorption baseline.

Checks, in order:
  1. baseline integrity - exactly the documented keys, 49 unique pairs, well-formed shas,
     an anchor note that states the history is unknowable and today is the anchor
  2. evidence reproduction - one pair's evidence_cmd is replayed through the host shell
     and its three outputs must equal the stored commit sha, file sha and local sha
  3. live comparison - the comparator is invoked exactly as documented
  4. negative controls, all three of which must hold or the gate is red:
     A1  flip one character of a stored local sha  -> LOCAL_CHANGED, never OK
     A2  flip one character of a stored upstream sha -> UPSTREAM_CHANGED, never OK
     B   point a stored upstream path at nothing     -> UNKNOWN, never OK

Last line is the machine-readable verdict.
'''
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
BASELINE = os.path.join(HERE, 'absorption_baseline.json')
COMPARE = os.path.join(HERE, 'compare_baseline.py')
NC_DIR = os.path.join(HERE, '_nc')
NC_LOG = os.path.join(HERE, '_nc_evidence_r303a.txt')
REQUIRED = ['slug', 'repo', 'upstream_path', 'upstream_commit_sha', 'upstream_file_sha',
            'upstream_version', 'local_file_sha', 'local_version', 'baseline_at', 'evidence_cmd']
HEX64 = re.compile(r'^[0-9a-f]{64}$')
HEX40 = re.compile(r'^[0-9a-f]{40}$')


def find_git_bash():
    try:
        p = subprocess.run(['where.exe', 'bash'], capture_output=True)
        for line in p.stdout.decode('utf-8', 'replace').splitlines():
            c = line.strip()
            if c and 'System32' not in c and os.path.isfile(c):
                return c
    except Exception:
        pass
    for c in ['C:/Users/37533/.dsh/profiles/desktop/node_modules/@dsh-ops/bash-win32-x64/usr/bin/bash.exe',
              'C:/Program Files/Git/bin/bash.exe']:
        if os.path.isfile(c):
            return c
    return None


def run_compare(baseline_path, json_out, quiet):
    args = [PY, '-B', COMPARE, '--baseline', baseline_path, '--json-out', json_out]
    if quiet:
        args.append('--quiet')
    p = subprocess.run(args, capture_output=True)
    out = p.stdout.decode('utf-8', 'replace')
    err = p.stderr.decode('utf-8', 'replace')
    data = None
    if os.path.isfile(json_out):
        data = json.load(open(json_out, encoding='utf-8'))
    return p.returncode, out, err, data


def target_line(out, slug):
    for ln in out.splitlines():
        if ln.startswith(slug):
            return ln
    return '(no line for ' + slug + ')'


def flip_hex(s):
    first = s[0]
    rep = '0' if first != '0' else '1'
    return rep + s[1:]


def main():
    fails = []
    checks = {}
    print('=== r303a gate ===')
    if not os.path.isfile(BASELINE):
        print('FAIL baseline missing')
        return 2
    doc = json.load(open(BASELINE, encoding='utf-8'))
    print('baseline_keys', sorted(doc.keys()))
    # 1 integrity
    integ = []
    if sorted(doc.keys()) != ['anchor_note', 'generated_at', 'pairs', 'schema']:
        integ.append('top-keys')
    pairs = doc.get('pairs') or []
    if len(pairs) != 49:
        integ.append('pairs-n=' + str(len(pairs)))
    slugs = [p.get('slug') for p in pairs]
    if len(set(slugs)) != len(slugs):
        integ.append('slug-duplicates')
    note = doc.get('anchor_note') or ''
    if ('不可知' not in note) or ('锚' not in note) or ('未留痕' not in note):
        integ.append('anchor-note-semantics')
    print('anchor_note', note[:120])
    for p in pairs:
        if sorted(p.keys()) != sorted(REQUIRED):
            integ.append('pair-keys:' + str(p.get('slug')))
            continue
        if not HEX64.match(str(p.get('local_file_sha'))):
            integ.append('local-sha:' + str(p.get('slug')))
        if not HEX40.match(str(p.get('upstream_file_sha'))):
            integ.append('upstream-sha:' + str(p.get('slug')))
        if not HEX40.match(str(p.get('upstream_commit_sha'))):
            integ.append('commit-sha:' + str(p.get('slug')))
        if not p.get('upstream_path') or not p.get('repo'):
            integ.append('path/repo:' + str(p.get('slug')))
        ev = str(p.get('evidence_cmd') or '')
        if ('gh api repos/' + str(p.get('repo'))) not in ev or str(p.get('upstream_path')) not in ev:
            integ.append('evidence-cmd:' + str(p.get('slug')))
    checks['integrity'] = not integ
    print('integrity_issues', len(integ), integ[:8])
    if integ:
        fails.append('integrity')
    # 3 live comparison (the documented interface)
    live_json = os.path.join(HERE, '_live_result.json')
    rc, out, err, data = run_compare(BASELINE, live_json, True)
    print('comparator_cmd python -B compare_baseline.py --baseline absorption_baseline.json')
    print('comparator_rc', rc)
    if err.strip():
        print('comparator_stderr', err.strip()[:200])
    live = (data or {}).get('summary') or {}
    print('live_summary', json.dumps(live, ensure_ascii=False))
    # r303 修（我提升后实测发现的两处脆断言之一）：本判据原把「比较器 rc!=0」一律判失败，
    # 但比较器 rc!=0 恰恰是它**在锚之后真的读到上游漂移**时的正常返回。改成按语义分档：
    #   · 本地件变了（lc>0）或两边都变（both>0）⇒ 失败（我们自己这棵树不该在锚后悄悄变、两边都变则不可归因）
    #   · 取不到（unk>0）⇒ 失败（读不出来不等于没漂）
    #   · 只有上游变了 ⇒ **通过**（这正是本机制要读到的结果），并显式打印漂移条数
    checks['live_rc'] = (rc == 0) or (lc == 0 and both == 0 and unk == 0)
    if not checks['live_rc']:
        fails.append('comparator-rc')
    ok = live.get('ok', 0)
    lc = live.get('local_changed', 0)
    uc = live.get('upstream_changed', 0)
    both = live.get('both_changed', 0)
    unk = live.get('unknown', 0)
    # 第二处脆断言：原来要求 uc == 0 才算「锚干净」。但锚是**零时刻**，之后上游再推提交是常态，
    # 把它判红等于「本机制一旦真的读到东西就自我判红」。改为只要求「本地与不可归因项为 0 + 分母守恒」，
    # 上游漂移单列为读数。r303 实测：建锚约 20 分钟后比较器已读到 upstream_changed=1（真实上游推送）。
    # 第三处（我 patch 第二版时自己引入的）：守恒式写成 ok+unk==49，那是**假定 lc/uc/both 全为 0** 才成立；
    # 一旦真读到上游漂移（uc=1、ok=48）就变成 48!=49 恒红。正解是「五态切分」：
    #   ok + local_changed + upstream_changed + both_changed + unknown == pairs（每对恰归一态，不重不漏）。
    anchor_ok = (live.get('pairs') == 49) and (lc == 0) and (both == 0) and \
                ((ok + lc + uc + both + unk) == 49)
    if uc:
        print('DRIFT-OBSERVED upstream_changed=%d（锚之后上游确实动过；这是读数、不是缺陷）' % uc)
    checks['anchor_clean'] = anchor_ok
    print('anchor_clean', anchor_ok)
    if not anchor_ok:
        fails.append('anchor-not-clean')
    if unk >= 49:
        fails.append('acquisition-dead')
        checks['acquisition_alive'] = False
    else:
        checks['acquisition_alive'] = True
    # 2 evidence reproduction for the first pair
    probe = pairs[0]
    sh = find_git_bash()
    ev_ok = False
    if sh:
        sp = subprocess.run([sh, '-c', probe['evidence_cmd']], capture_output=True)
        lines = sp.stdout.decode('utf-8', 'replace').strip().splitlines()
        print('evidence_shell', sh)
        print('evidence_cmd_verbatim', probe['evidence_cmd'])
        print('evidence_lines', lines)
        print('evidence_rc', sp.returncode)
        if len(lines) >= 3:
            ev_ok = (lines[0] == probe['upstream_commit_sha']) and (lines[1] == probe['upstream_file_sha']) and (lines[2] == probe['local_file_sha'])
    else:
        print('evidence_shell_missing')
    checks['evidence_reproduce'] = ev_ok
    print('evidence_reproduce', ev_ok)
    if not ev_ok:
        fails.append('evidence-reproduce')
    # 4 negative controls
    os.makedirs(NC_DIR, exist_ok=True)
    alias = pairs[0]['slug']
    cases = ['A1_local', 'A2_upstream', 'B_path']
    ctrl = {}
    log = []
    for case in cases:
        mod = json.loads(json.dumps(doc, ensure_ascii=False))
        tgt = [p for p in mod['pairs'] if p['slug'] == alias][0]
        if case == 'A1_local':
            tgt['local_file_sha'] = flip_hex(tgt['local_file_sha'])
            expect = 'LOCAL_CHANGED'
        elif case == 'A2_upstream':
            tgt['upstream_file_sha'] = flip_hex(tgt['upstream_file_sha'])
            expect = 'UPSTREAM_CHANGED'
        else:
            tgt['upstream_path'] = 'no/such/dir/R303A_NOPE/SKILL.md'
            expect = 'UNKNOWN'
        cpath = os.path.join(NC_DIR, case + '.json')
        with open(cpath, 'w', encoding='utf-8') as fh:
            json.dump(mod, fh, ensure_ascii=False, indent=1)
        cj = os.path.join(NC_DIR, case + '_res.json')
        rc2, out2, err2, data2 = run_compare(cpath, cj, False)
        got = None
        if data2:
            hit = [p for p in data2['pairs'] if p['slug'] == alias]
            got = hit[0]['state'] if hit else None
        line = target_line(out2, alias)
        passed = (got == expect) and (got != 'OK')
        ctrl[case] = passed
        fails_now = []
        if got != expect:
            fails_now.append('expected ' + expect + ' got ' + str(got))
        if got == 'OK':
            fails_now.append('reported OK')
        if not passed:
            fails.append('nc-' + case)
        print('NC_' + case + '_target ' + alias + ' expect=' + expect + ' got=' + str(got) + ' pass=' + str(passed))
        print('NC_' + case + '_pairline ' + line)
        log.append('===== ' + case + ' =====')
        log.append('modified field: ' + ('local_file_sha' if case == 'A1_local' else ('upstream_file_sha' if case == 'A2_upstream' else 'upstream_path')))
        log.append('expected=' + expect + ' got=' + str(got) + ' pass=' + str(passed))
        log.append('comparator stdout (verbatim):')
        log.append(out2)
        log.append('comparator stderr: ' + err2.strip()[:300])
        log.append('pair line: ' + line)
        log.append('')
    with open(NC_LOG, 'w', encoding='utf-8') as fh:
        fh.write(chr(10).join(log))
    print('negative_controls', json.dumps(ctrl))
    for c in cases:
        checks['nc_' + c] = ctrl.get(c, False)
    # cleanup control copies
    try:
        shutil.rmtree(NC_DIR)
    except Exception as e:
        print('cleanup_warn', e)
    try:
        os.remove(live_json)
    except Exception:
        pass
    # verdict line
    line = '[R303:BASELINE] pairs=%d ok=%d local_changed=%d upstream_changed=%d both=%d unknown=%d' % (live.get('pairs', 0), ok, lc, uc, both, unk)
    print('checks ' + json.dumps(checks))
    print('fails ' + json.dumps(fails))
    print(line)
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())