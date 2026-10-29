# -*- coding: utf-8 -*-
# R282 three-arm reconcile: assembler. Builds the three-arm table, the A/B/C/D faces, the
# cross-arm text-identity matrix and the denominator derivability check, writes
# 06-benchmark/r282_three_arm_reconcile.json and prints the verdict line.
# Read-only on the three originals; only _repro/r282j/ and the two new artifacts are touched.
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reconcile as R
from measures import git_bytes, git_rev_parse, git_show_meta, read_worktree, sha256_text
from denoms import f_caliber, hit_path_or_base, lead_caliber, loose_files

OUT_JSON = R.OUT_JSON
GOOD_DIMS = R.GOOD_DIMS
SKILLS = R.SKILLS

PYV = 'PY=' + chr(34) + '$USERPROFILE/.workbuddy/binaries/python/envs/default/Scripts/python.exe' + chr(34)
RECHECK = PYV + ' -B _repro/r282j/reconcile.py'
CMD_NEG = PYV + ' -B _repro/r282j/negctl_r282.py'
CMD_D6 = PYV + ' -B _repro/r282j/d6check.py'
CMD_A = PYV + ' -B _repro/r282j/acalc.py'
CMD_D = PYV + ' -B _repro/r282j/dcalc.py'


def first_ref(s):
    if not s:
        return None
    return str(s).split()[0]


def text_of(ref, rel):
    if ref is None:
        return None
    if ref == 'worktree':
        skill = rel.split('/')[0]
        return read_worktree(skill)
    raw, t = git_bytes(ref, rel)
    return t


def text_cells(skill, rel, refs):
    cells = {}
    for arm in ('g', 'lead', 'f'):
        ref = refs.get(arm)
        if not ref:
            cells[arm] = None
            continue
        if ref == 'worktree':
            t = read_worktree(skill)
            full = 'worktree'
        else:
            raw, t = git_bytes(ref, rel)
            full = git_rev_parse(ref)
        if t is None:
            cells[arm] = {'ref': ref, 'state': 'UNREADABLE'}
            continue
        cells[arm] = {'ref': ref, 'full_sha': full,
                      'bytes_utf8': len(t.encode('utf-8', 'replace')),
                      'sha256_16': sha256_text(t)[:16]}
    shas = set(c['sha256_16'] for c in cells.values() if c and 'sha256_16' in c)
    return {'arms': cells, 'distinct_texts': len(shas), 'all_equal': len(shas) <= 1}


def cross_text_identity(bld):
    out = []
    for row in bld['rows']:
        if row.get('status') != 'MEASURED':
            continue
        skill = row['skill']
        rel = skill + '/SKILL.md'
        e = row['e']
        l = row['l'] or {}
        item = (bld['farm']['items'] or {}).get(skill)
        rec = {'skill': skill}
        rec['before'] = text_cells(skill, rel, {
            'g': first_ref(e['sha_pair']['before_ref']),
            'lead': first_ref(l.get('before_sha_used')),
            'f': first_ref((item or {}).get('before_ref'))})
        rec['after'] = text_cells(skill, rel, {
            'g': 'worktree', 'lead': 'worktree',
            'f': first_ref((item or {}).get('after_ref'))})
        # worktree vs HEAD identity (F reads HEAD:path, Lead and G read the worktree)
        rcw, tw = git_bytes('HEAD', rel)
        wt = read_worktree(skill)
        rec['after_worktree_equals_HEAD'] = (tw is not None and wt is not None and sha256_text(tw) == sha256_text(wt))
        rec['published_g_text_sha256'] = dict((k, v[:16]) for k, v in e['text_sha256'].items())
        out.append(rec)
    return out


def derivability(bld):
    # The two denominators must be reconcilable as a set difference, not averaged.
    out = []
    for row in bld['rows']:
        if row.get('status') != 'MEASURED':
            continue
        skill = row['skill']
        rel = skill + '/SKILL.md'
        e = row['e']
        l = row['l'] or {}
        counted, exempt, pruned = lead_caliber(skill)
        f_all, f_kept = f_caliber(skill)
        cset = set(counted)
        fset = set(f_kept)
        extras = sorted(fset - cset)
        lead_only = sorted(cset - fset)
        texts = {'before': text_of(first_ref(e['sha_pair']['before_ref']), rel),
                 'after': read_worktree(skill)}
        rec = {'skill': skill,
               'lead_denom': len(counted),
               'f_denom': len(f_kept),
               'lead_exempt_n': len(exempt),
               'lead_exempt_list': exempt,
               'lead_pruned_dirs': pruned,
               'f_only_extras': extras,
               'lead_only_extras': lead_only,
               'nested_mirror_excluded_by_lead': [x for x in exempt if x.endswith('SKILL.md') and x != 'SKILL.md'],
               'nested_mirror_n': len([x for x in exempt if x.endswith('SKILL.md') and x != 'SKILL.md']),
               'skill_relative_top_self': 'SKILL.md',
               'f_denom_if_only_top_SKILL_md_excluded': len([x for x in f_all if x != 'SKILL.md']),
               'lead_denom_if_nested_SKILL_md_counted': len(counted) + len([x for x in exempt if x.endswith('SKILL.md') and x != 'SKILL.md'])}
        for side in ('before', 'after'):
            t = texts[side]
            if t is None:
                continue
            from denoms import lead_strict_unreferenced, rule_flip
            leadUnrefSet = lead_strict_unreferenced(t, counted)
            unrefL = len(leadUnrefSet)
            hitL2 = hit_path_or_base(t, counted)
            hitF = hit_path_or_base(t, sorted(fset))
            hitX = hit_path_or_base(t, extras)
            unrefF = len(fset) - len(hitF)
            exUn = len(extras) - len(hitX)
            fl = rule_flip(t, counted)
            gap = fl['rule_gap']
            rec[side] = {'lead_denom': len(counted), 'f_denom': len(f_kept),
                         'lead_strict_unref_rule4': unrefL, 'f_strict_unref': unrefF,
                         'lead_strict_hit_2rule': len(hitL2), 'f_strict_hit': len(hitF),
                         'extras_unreferenced': exUn, 'rule_gap': gap,
                         'rule_flip_files': fl['only_unreferenced_under_f_rule'],
                         'denom_gap': len(fset) - len(counted),
                         'identity_holds': unrefF == unrefL + exUn + gap,
                         'equation': 'f_unref(%d) = lead_unref_4rule(%d) + extras_unref(%d) + rule_gap(%d)' % (unrefF, unrefL, exUn, gap)}
        rec['published_lead_strict'] = [(l.get('metrics_before') or {}).get('unreferenced_strict_n'),
                                        (l.get('metrics_after') or {}).get('unreferenced_strict_n')]
        rec['published_lead_present_n'] = [(l.get('metrics_before') or {}).get('present_n'),
                                           (l.get('metrics_after') or {}).get('present_n')]
        fpub = bld['farm']
        rec['published_f'] = {'denom': (fpub['metrics_before'].get(skill) or {}).get('sibling_denom'),
                              'strict_hit': ((fpub['metrics_before'].get(skill) or {}).get('sibling_strict_hit')),
                              'strict_hit_after': ((fpub['metrics_after'].get(skill) or {}).get('sibling_strict_hit')),
                              'rate_pct': ((fpub['metrics_before'].get(skill) or {}).get('sibling_strict_rate_pct')),
                              'rate_pct_after': ((fpub['metrics_after'].get(skill) or {}).get('sibling_strict_rate_pct'))}
        out.append(rec)
    return out


PY = None  # (stale divergences face removed; the live one lives in emit_r282.py)
