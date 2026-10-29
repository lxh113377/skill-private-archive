# -*- coding: utf-8 -*-
'''landing-effect face (R278, requirement 6 half).

Why: two managed-root landings exist (r266 tdd pointer, r269/r272/r277 frontend-slides paradigm)
but requirement 6 asks whether quality actually improved and whether anything broke. Until now the
only figures were route-level calibers, so no one could say what a landing changed on disk.

How: for each landed skill, take the PARENT of the first landing commit (git show <sha>~1) as the
'before' text and the working tree file as 'after', then measure both with r268's OWN functions
(single source: the reference caliber must not be re-implemented here, per appendix C.1).

Metrics per text:
  unreferenced_n   on-disk sibling files the text never points at (r268 normal caliber, incl.
                   the r273 platform-metadata exemption);
  present_n        files in the denominator;
  half_claim_n     occurrences of the still-contradictory phrase pair from the r269 conflict note;
  double_write_n   occurrences of the numbered Mode-C clause (r272's prefix patch doubled it);
  max_line_bytes   longest line (the doubled line was 390B, i.e. visibly corrupted);
  vh_claims_n      viewport-relative authoring clauses left in the text (vh/dvw tokens);
  stage_claims_n   fixed-stage clauses (1920 / 1080 / fixed stage).
Requirement-6 reading is per-axis and labelled as such: it is NOT task-level quality.
'''
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, '06-benchmark')
SK = os.environ.get('ZIJIAN_SKILLS_ROOT', 'D:/global_skills')
sys.path.insert(0, HERE)
import r268_unreferenced_siblings as U

OUT_DEFAULT = os.path.join(BENCH, 'r278_landing_effect.json')

# since-day window: the landings happened on 2026-10-29 (r266 tdd, r269/72/77 frontend-slides).
WINDOW = '2026-10-29 00:00'


def git(*args):
    p = subprocess.run(['git', '-C', SK] + list(args), capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    return p


def landing_commits(rel):
    """commits touching this file inside the window, oldest first; sha + subject only."""
    p = git('log', '--format=%H%x09%ad%x09%s', '--date=format:%Y-%m-%d %H:%M',
            '--since=' + WINDOW, '--', rel)
    out = []
    for ln in (p.stdout or '').splitlines():
        parts = ln.split(chr(9))
        if len(parts) >= 3:
            out.append({'sha': parts[0], 'when': parts[1], 'subject': parts[2]})
    return list(reversed(out))


def measure(text, files):
    """apply r268's own caliber to one text version; files come from disk (only text differs)."""
    toks = U.referenced_tokens(text)
    unref = []
    for rel in files:
        base = os.path.basename(rel)
        dirs = [p for p in rel.split('/')[:-1]]
        ref, _rule = U.classify(rel, base, dirs, toks, text)
        if not ref:
            unref.append(rel)
    lines = [x.rstrip() for x in text.split(chr(10)) if x.strip()]
    vh = sum(1 for x in lines if ('vh' in x and 'NON-NEGOTIABLE' not in x) or 'dvh' in x)
    stage = sum(1 for x in lines if '1920' in x or 'fixed stage' in x.lower())
    maxb = max([len(x.encode('utf-8')) for x in lines] or [0])
    return {
        'present_n': len(files),
        'unreferenced_n': len(unref),
        'unreferenced': sorted(unref),
        'half_claim_n': text.count('指令互斥'),
        'double_write_n': text.count('After ANY modification, verify:'),
        'max_line_bytes': maxb,
        'vh_claims_n': vh,
        'stage_claims_n': stage,
    }


# 严格档（与 r268 build_face 内 strict 规则同形态：相对路径子串 / 基名子串 / 路径形态 token 结尾 / 直接父目录带斜杠）。
# 为什么不 import r268 的那段：它内联在 build_face 里不是函数（R261-3 同类：复现类逻辑不外露）。
# 风险由 assert 兜住：本函数算出的 after 严格档必须等于 r268 面已发布的 unreferenced_strict_n，不等即红。
def strict_unreferenced(text, files):
    out = []
    toks = U.referenced_tokens(text)
    for rel in files:
        base = os.path.basename(rel)
        dirs = [p for p in rel.split('/')[:-1]]
        ref = (rel in text) or (base in text)
        if not ref:
            for tok in toks:
                if tok.replace(chr(92), '/').endswith(rel):
                    ref = True
                    break
        if not ref and dirs and len(dirs[-1]) >= 3 and (dirs[-1] + '/') in text:
            ref = True
        if not ref:
            out.append(rel)
    return out


def commit_series(rel, commits, files):
    '''逐提交读数：端点对比会藏住「中途引入又修掉」的回退（本例 r272 造双写、r277 消除）。'''
    rows = []
    for c in commits:
        p = git('show', c['sha'] + ':' + rel)
        if p.returncode != 0:
            rows.append({'sha': c['sha'][:8], 'when': c['when'], 'state': 'UNREADABLE'})
            continue
        t = p.stdout or ''
        toks = U.referenced_tokens(t)
        n_norm = 0
        for rel2 in files:
            dirs2 = [x for x in rel2.split('/')[:-1]]
            ref2, _r2 = U.classify(rel2, os.path.basename(rel2), dirs2, toks, t)
            if not ref2:
                n_norm += 1
        lines = [x.rstrip() for x in t.split(chr(10)) if x.strip()]
        rows.append({'sha': c['sha'][:8], 'when': c['when'], 'state': 'OK',
                     'unreferenced_norm_n': n_norm,
                     'unreferenced_strict_n': len(strict_unreferenced(t, files)),
                     'double_write_n': t.count('After ANY modification, verify:'),
                     'max_line_bytes': max([len(x.encode('utf-8')) for x in lines] or [0])})
    return rows


def main():
    targets = ['test-driven-development/SKILL.md', 'frontend-slides/SKILL.md']
    rows = []
    for rel in targets:
        skill = rel.split('/')[0]
        commits = landing_commits(rel)
        if not commits:
            rows.append({'skill': skill, 'state': 'NO_LANDING_COMMIT_IN_WINDOW',
                         'window_since': WINDOW, 'commits_checked': []})
            print('  %-28s NO landing commit since %s' % (skill, WINDOW))
            continue
        first = commits[0]
        pb = git('show', first['sha'] + '~1:' + rel)
        pw = git('show', ':' + rel)          # index version = current committed content
        wt_path = os.path.join(SK, rel)
        if pb.returncode != 0:
            rows.append({'skill': skill, 'state': 'BEFORE_UNREADABLE', 'first': first})
            print('  %-28s before-text unreadable (%s)' % (skill, first['sha'][:8]))
            continue
        before = pb.stdout or ''
        after = io.open(wt_path, encoding='utf-8', errors='replace').read()
        files, exempt = U.walk_files(os.path.join(SK, skill))
        # 上面注释承诺了 assert，此前只写了注释没写代码（= 声明超出实现，R277-1 要防的形态）。
        # 现补真断言：本件自算的严格档必须等于 r268 面已发布的 unreferenced_strict_n，
        # 不等即抛 —— 否则两处各自实现严格档会静默漂移（R260-5/R261-3 同族）。
        try:
            pub = json.load(io.open(os.path.join(BENCH, 'r268_unreferenced_siblings.json'), encoding='utf-8'))
            prow = next((x for x in pub.get('rows') or [] if x.get('slug') == skill), None)
        except Exception:
            prow = None
        if prow is not None and prow.get('state') == 'OK':
            mine_after = len(strict_unreferenced(
                io.open(wt_path, encoding='utf-8', errors='replace').read(), files))
            assert mine_after == prow.get('unreferenced_strict_n'), (
                'strict caliber drifted from r268 face: %s mine=%s theirs=%s' % (
                    skill, mine_after, prow.get('unreferenced_strict_n')))
        mb, ma = measure(before, files), measure(after, files)
        # 双档并报：只报宽松档会把「祖先目录被提及」当成可达 ⇒ 与 r275 的口径过头同族。
        sb = strict_unreferenced(before, files)
        sa = strict_unreferenced(after, files)
        mb['unreferenced_strict_n'] = len(sb)
        ma['unreferenced_strict_n'] = len(sa)
        series = commit_series(rel, commits, files)
        axes = ['unreferenced_n', 'half_claim_n', 'double_write_n', 'max_line_bytes',
                'vh_claims_n', 'stage_claims_n']
        delta = {k: (ma[k] - mb[k]) for k in axes}
        improved = [k for k in ('unreferenced_n', 'half_claim_n', 'double_write_n',
                                'max_line_bytes', 'vh_claims_n') if ma[k] < mb[k]]
        worsened = [k for k in ('unreferenced_n', 'half_claim_n', 'double_write_n',
                                'max_line_bytes', 'vh_claims_n') if ma[k] > mb[k]]
        rows.append({'skill': skill, 'state': 'OK', 'landing_commits': commits,
                     'first_landing': first, 'before_sha_used': first['sha'] + '~1',
                     'metrics_before': mb, 'metrics_after': ma, 'delta': delta,
                     'caliber_pair': {'normal_before_after': [mb['unreferenced_n'], ma['unreferenced_n']],
                                      'strict_before_after': [mb['unreferenced_strict_n'], ma['unreferenced_strict_n']]},
                     'commit_series': series,
                     'series_flags': [s['sha'] for s in series
                                      if s.get('state') == 'OK' and s.get('double_write_n', 0) > 1],
                     'axes_improved': improved, 'axes_worsened': worsened,
                     'committed_index_matches_worktree': (pw.stdout or '') == after,
                     'exempt_n': exempt})
        print('  %-28s commits=%d norm %d->%d strict %d->%d dbl %d->%d vh %d->%d stage %d->%d' % (
              skill, len(commits), mb['unreferenced_n'], ma['unreferenced_n'],
              mb['unreferenced_strict_n'], ma['unreferenced_strict_n'],
              mb['double_write_n'], ma['double_write_n'],
              mb['vh_claims_n'], ma['vh_claims_n'],
              mb['stage_claims_n'], ma['stage_claims_n']))
    doc = {'schema': 'landing-effect-v1',
           'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
           'provenance_cmd': 'python 05-exec/r278_landing_effect.py',
           'caliber': 'unreferenced axes come from r268 single-source rules; before text = git show <first-landing>~1',
           'window_since': WINDOW,
           'axes_note': 'per-axis structural readings; NOT task-level quality (see requirement 6 wording)',
           'caliber_caution': ('normal caliber is inflatable by naming a directory once; '
               'frontend-slides normal 70->0 = +80.5pp but strict 72->68 = only +4.6pp '
               '(present_n 87), because r269 names the package dir without naming its 68 '
               'member files; quote the strict number whenever claiming files are pointed '
               'at; the R268-2 gate leg must watch both calibers or it is blind to this inflation.'),
           'series_note': ('end-to-end comparison hides mid-sequence regressions: '
               'double_write_n ran 1->2->1 across the five landing commits'),
           'first_commit_note': ('the first window commit touching frontend-slides/SKILL.md '
               'is 079b91f3, the accidental whole-tree staging commit (R269-3), so the '
               'before text is the pre-incident state - disclosed rather than hidden'),
           'rows': rows}
    tmp = OUT_DEFAULT + '.tmp'
    io.open(tmp, 'w', encoding='utf-8', newline='').write(json.dumps(doc, ensure_ascii=False, indent=1))
    os.replace(tmp, OUT_DEFAULT)
    ok = [r for r in rows if r['state'] == 'OK']
    print('[LANDING:FACE] ok=%d worsened_axes=%d -> %s' % (
          len(ok), sum(len(r['axes_worsened']) for r in ok), OUT_DEFAULT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
