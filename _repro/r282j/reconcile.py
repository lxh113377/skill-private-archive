# -*- coding: utf-8 -*-
# R282 three-arm reconcile judge.
#
# Reads the three arms read-only, re-derives every G cell with rubric.py (a fresh
# implementation of the rubric DECLARED inside the G artifact), compares cell by cell,
# then computes the four points the brief demands: A (ui-ux before-text swap),
# B (band flattening vs raw-sum caliber), C (d6 direction mapping), D (sibling
# denominator set difference).
#
# Teeth: python -B reconcile.py --json <tampered copy> must print MISMATCH lines that
# name the bumped field. Nothing here writes 05-exec/*, 06-benchmark/r278_*,
# 06-benchmark/r281_* or D:/global_skills.
import difflib
import hashlib
import io
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from measures import DIMS, GS, git_bytes, git_rev_parse, git_show_meta, lines_of, my_bucket, read_worktree, sha256_text
from rubric import probe_flags, score_text, skill_tree
from denoms import f_caliber, hit_path_or_base, lead_caliber, loose_files, r268_normal_files

ROOT = 'C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化'
BENCH = os.path.join(ROOT, '06-benchmark')
G_DEFAULT = os.path.join(BENCH, 'r281_artifact_ab.json')
LEAD_JSON = os.path.join(BENCH, 'r278_landing_effect.json')
F_JSON = os.path.join(BENCH, 'r278_before_after_control.json')
R268_JSON = os.path.join(BENCH, 'r268_unreferenced_siblings.json')
OUT_JSON = os.path.join(BENCH, 'r282_three_arm_reconcile.json')
SKILLS = ['test-driven-development', 'frontend-slides', 'ui-ux-pro-max']
GOOD_DIMS = ['d1', 'd2', 'd3', 'd4', 'd5']


def load(p):
    with io.open(p, encoding='utf-8') as f:
        return json.load(f)


def jdump(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True)


def now_utc():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def sha12(p):
    with io.open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]


def arm_gate():
    # D7.2: judge an arm only when that file has been quiescent >120 s, and record its sha.
    out = {}
    now = datetime.now(timezone.utc)
    for p in [G_DEFAULT, LEAD_JSON, F_JSON, R268_JSON]:
        st = os.stat(p)
        m = datetime.fromtimestamp(st.st_mtime, timezone.utc)
        out[os.path.basename(p)] = {
            'mtime_utc': m.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'age_sec': int((now - m).total_seconds()),
            'quiescent_over_120s': (now - m).total_seconds() > 120,
            'sha256_12': sha12(p)}
    return out


def line_ops(a, b):
    sm = difflib.SequenceMatcher(None, lines_of(a), lines_of(b))
    add = 0
    dele = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        add += j2 - j1
        dele += i2 - i1
    return {'lines_added': add, 'lines_removed': dele}


def band_span(edges, band):
    lo = edges[band - 1] if band > 0 else None
    hi = edges[band] if band < len(edges) else None
    return 'raw [%s, %s) = band %d' % ('-inf' if lo is None else lo, 'inf' if hi is None else hi, band)


def build(g_path=G_DEFAULT):
    g = load(g_path)
    lead = load(LEAD_JSON)
    farm = load(F_JSON)
    pub = load(R268_JSON)
    edges = g['rubric_definition']['EDGES']
    gper = dict((e['skill'], e) for e in g['per_skill'])
    lper = dict((r['skill'], r) for r in lead['rows'])
    gate = arm_gate()

    rows = []
    flat_cases = []
    d6_cases = []
    denom_rows = []
    raw_calibers = {}
    recompute = {}
    mismatches = []
    ctx = {}
    cells = 0

    for skill in SKILLS:
        e = gper.get(skill)
        l = lper.get(skill)
        rel = skill + '/SKILL.md'
        if e is None or e.get('status') != 'MEASURED':
            rows.append({'skill': skill, 'status': 'UNVERIFIED',
                         'g_arm': {'state': 'UNVERIFIED', 'cmd': 'python -B 05-exec/r281g_score.py check --json 06-benchmark/r281_artifact_ab.json'}})
            continue
        sp = e['sha_pair']
        bref = sp['before_ref']
        braw, tb = git_bytes(bref, rel)
        ta = read_worktree(skill)
        if tb is None or ta is None:
            rows.append({'skill': skill, 'status': 'UNVERIFIED',
                         'g_arm': {'state': 'UNVERIFIED', 'before_ref': bref,
                                   'cmd': 'git -C D:/global_skills show ' + bref + ':' + rel}})
            continue
        stored_probe = {'decidable': bool(e['dim6_probe']['decidable']),
                        'supported': list(e['dim6_probe']['supported'])}
        live_probe = probe_flags(skill)
        tree = skill_tree(skill)
        raw_b, good_b, det_b = score_text(tb, skill, edges, stored_probe, tree)
        raw_a, good_a, det_a = score_text(ta, skill, edges, stored_probe, tree)
        dec = [k for k in DIMS if good_b[k] is not None and good_a[k] is not None]
        s_b = sum(good_b[k] for k in dec)
        s_a = sum(good_a[k] for k in dec)
        up = None if s_b == 0 else round((s_a - s_b) * 100.0 / s_b, 4)
        sha_b = sha256_text(tb)
        sha_a = sha256_text(ta)

        # ---------- cell-by-cell reconcile against the published G arm
        bad = []
        cells += 2
        if e['text_sha256']['before'] != sha_b:
            bad.append('field ' + skill + '/text_sha256/before published=' + e['text_sha256']['before'][:12] + ' recomputed=' + sha_b[:12])
        if e['text_sha256']['after'] != sha_a:
            bad.append('field ' + skill + '/text_sha256/after published=' + e['text_sha256']['after'][:12] + ' recomputed=' + sha_a[:12])
        for side, stored, fresh in (('before', e['raw_before'], raw_b), ('after', e['raw_after'], raw_a)):
            for d in DIMS:
                cells += 1
                if stored.get(d) != fresh[d]:
                    bad.append('field ' + skill + '/raw_' + side + '.' + d + ' published=' + str(stored.get(d)) + ' recomputed=' + str(fresh[d]))
        for side, stored, fresh in (('before', e['dims_before'], good_b), ('after', e['dims_after'], good_a)):
            for d in DIMS:
                cells += 1
                if stored.get(d) != fresh[d]:
                    bad.append('field ' + skill + '/dims_' + side + '.' + d + ' published=' + str(stored.get(d)) + ' recomputed=' + str(fresh[d]))
        for key, stored, fresh in (('sum_before', e['sum_before'], s_b), ('sum_after', e['sum_after'], s_a), ('uplift_pct', e['uplift_pct'], up)):
            cells += 1
            if stored != fresh:
                bad.append('field ' + skill + '/' + key + ' published=' + str(stored) + ' recomputed=' + str(fresh))
        for side, stored, fresh in (('before', e.get('detail_before', {}).get('d5', {}), det_b['d5']),
                                    ('after', e.get('detail_after', {}).get('d5', {}), det_a['d5'])):
            for fld in ('live_list', 'dead_list', 'unresolved_list'):
                cells += 1
                a1 = sorted((stored or {}).get(fld) or [])
                a2 = sorted(fresh[fld])
                if a1 != a2:
                    bad.append('field ' + skill + '/detail_' + side + '.d5.' + fld + ' published_n=' + str(len(a1)) + ' recomputed_n=' + str(len(a2)) + ' delta=' + jdump([x for x in a2 if x not in set(a1)] + [x for x in a1 if x not in set(a2)])[:200])
        if bool(live_probe['decidable']) != stored_probe['decidable']:
            bad.append('field ' + skill + '/dim6_probe.decidable published=' + str(stored_probe['decidable']) + ' live=' + str(live_probe['decidable']))
        elif sorted(live_probe['supported']) != sorted(stored_probe['supported']):
            bad.append('field ' + skill + '/dim6_probe.supported published=' + jdump(stored_probe['supported']) + ' live=' + jdump(live_probe['supported']))
        mismatches.extend(bad)
        recompute[skill] = {'raw_before': raw_b, 'raw_after': raw_a, 'dims_before': good_b,
                            'dims_after': good_a, 'sum_before': s_b, 'sum_after': s_a,
                            'uplift_pct': up, 'decidable_dims': dec, 'clean': len(bad) == 0,
                            'mismatch_fields': bad, 'text_sha256': {'before': sha_b, 'after': sha_a}}
        ctx[skill] = {'tb': tb, 'ta': ta, 'tree': tree, 'edges': edges, 'probe': stored_probe,
                      'before_ref': bref, 'rel': rel}

        # ---------- requirement B: raw moved, band did not
        for d in DIMS:
            rb, ra = e['raw_before'].get(d), e['raw_after'].get(d)
            bb, ba = e['dims_before'].get(d), e['dims_after'].get(d)
            if rb is None or ra is None or bb is None or ba is None:
                continue
            if rb != ra and bb == ba:
                flat_cases.append({'skill': skill, 'dim': d,
                                   'dim_name': g['rubric_definition']['dims'][d]['name'],
                                   'raw_before': rb, 'raw_after': ra, 'raw_delta': ra - rb,
                                   'band_before_after': [bb, ba], 'edges': edges[d],
                                   'band_span': band_span(edges[d], bb),
                                   'banded_delta': 0, 'stored_uplift_pct': e['uplift_pct']})
            if rb == ra and bb != ba:
                mismatches.append('field ' + skill + '/' + d + ' band moved without raw move')

        # ---------- raw-sum (unbanded) caliber, numerator/denominator explicit
        rs_b = sum(raw_b[d] for d in GOOD_DIMS)
        rs_a = sum(raw_a[d] for d in GOOD_DIMS)
        rs6_b = rs_b + (0 if raw_b['d6'] is None else -raw_b['d6'])
        rs6_a = rs_a + (0 if raw_a['d6'] is None else -raw_a['d6'])
        entry = {'dims_used_d1_d5': GOOD_DIMS,
                 'raw_sum_before_d1_d5': rs_b, 'raw_sum_after_d1_d5': rs_a,
                 'numerator_d1_d5': rs_a - rs_b, 'denominator_d1_d5': rs_b,
                 'raw_sum_uplift_pct_d1_d5': None if rs_b == 0 else round((rs_a - rs_b) * 100.0 / rs_b, 4),
                 'banded_uplift_pct': e['uplift_pct'],
                 'banded_numerator_S_after_minus_S_before': e['sum_after'] - e['sum_before'],
                 'banded_denominator_S_before': e['sum_before'],
                 'd6_raw_before_after': [raw_b['d6'], raw_a['d6']],
                 'raw_sum_incl_signed_d6_before': rs6_b, 'raw_sum_incl_signed_d6_after': rs6_a,
                 'raw_sum_incl_signed_d6_uplift_pct': None if rs6_b == 0 else round((rs6_a - rs6_b) * 100.0 / rs6_b, 4)}
        const = [d for d in dec if e['dims_before'][d] == e['dims_after'][d]]
        if const:
            sbx = s_b - sum(e['dims_before'][d] for d in const)
            sax = s_a - sum(e['dims_after'][d] for d in const)
            entry['constant_band_dims'] = [{'dim': d, 'band': e['dims_before'][d]} for d in const]
            entry['banded_uplift_excl_constant_dims_pct'] = None if sbx <= 0 else round((sax - sbx) * 100.0 / sbx, 4)
            entry['excl_constant_denominator'] = sbx
        raw_calibers[skill] = entry

        # ---------- requirement C: d6 mapping, recomputed here
        d6_cases.append({'skill': skill, 'decidable': stored_probe['decidable'],
                         'd6_raw_before': e['raw_before'].get('d6'), 'd6_raw_after': e['raw_after'].get('d6'),
                         'stored_dims_d6': [e['dims_before'].get('d6'), e['dims_after'].get('d6')],
                         'edges_d6': edges['d6'],
                         'bucket_before': None if e['raw_before'].get('d6') is None else my_bucket(edges['d6'], e['raw_before']['d6']),
                         'bucket_after': None if e['raw_after'].get('d6') is None else my_bucket(edges['d6'], e['raw_after']['d6']),
                         'reversed_good_before': None if e['raw_before'].get('d6') is None else 5 - my_bucket(edges['d6'], e['raw_before']['d6']),
                         'reversed_good_after': None if e['raw_after'].get('d6') is None else 5 - my_bucket(edges['d6'], e['raw_after']['d6']),
                         'bad_flags_before': e.get('detail_before', {}).get('d6', {}).get('bad'),
                         'bad_flags_after': e.get('detail_after', {}).get('d6', {}).get('bad')})

        # ---------- requirement D: denominators from disk
        counted, exempt, pruned = lead_caliber(skill)
        f_all, f_kept = f_caliber(skill)
        cset = set(counted)
        fset = set(f_kept)
        tbf, taf = tb, ta
        pub_f = farm['metrics_before'].get(skill)
        pub_a_f = farm['metrics_after'].get(skill)
        pub268 = next((r for r in pub['rows'] if r.get('slug') == skill), None)
        denom_rows.append({
            'skill': skill,
            'lead_present_n_published': (l or {}).get('metrics_before', {}).get('present_n'),
            'lead_exempt_n_published': (l or {}).get('exempt_n'),
            'lead_present_n_recomputed': len(counted),
            'lead_exempt_recomputed': len(exempt),
            'lead_exempt_list': exempt,
            'lead_pruned_dirs': pruned,
            'f_denom_published': (pub_f or {}).get('sibling_denom'),
            'f_find_total_files': len(f_all),
            'f_denom_recomputed': len(f_kept),
            'f_only_extra_files': sorted(fset - cset),
            'lead_only_extra_files': sorted(cset - fset),
            'intersection_n': len(cset & fset),
            'lead_strict_unref_before_recomputed': len(counted) - len(hit_path_or_base(tbf, counted)),
            'lead_strict_unref_after_recomputed': len(counted) - len(hit_path_or_base(taf, counted)),
            'lead_strict_unref_published': [(l or {}).get('metrics_before', {}).get('unreferenced_strict_n'), (l or {}).get('metrics_after', {}).get('unreferenced_strict_n')],
            'f_strict_hit_published': [(pub_f or {}).get('sibling_strict_hit'), (pub_a_f or {}).get('sibling_strict_hit')],
            'f_strict_hit_recomputed_on_f_set': [len(hit_path_or_base(tbf, sorted(fset))), len(hit_path_or_base(taf, sorted(fset)))],
            'f_loose_hit_recomputed_on_f_set': [len(loose_files(tbf, sorted(fset))), len(loose_files(taf, sorted(fset)))],
            'lead_normal_unref_published': [(l or {}).get('metrics_before', {}).get('unreferenced_n'), (l or {}).get('metrics_after', {}).get('unreferenced_n')],
            'r268_published': None if pub268 is None else {'present_n': pub268.get('present_n'), 'exempt_n': pub268.get('exempt_n'), 'unreferenced_strict_n': pub268.get('unreferenced_strict_n')},
            'cmd': 'python -B _repro/r282j/reconcile.py --face denoms'})

        rows.append({'skill': skill, 'status': 'MEASURED', 'e': e, 'l': l,
                     'farm_before': pub_f, 'farm_after': pub_a_f,
                     'farm_item': farm['items'].get(skill),
                     'recomputed': recompute[skill], 'before_ref': bref, 'rel': rel, 'cells_cumulative': cells,
                     'before_full_recomputed': git_rev_parse(bref),
                     'lead_first_landing': (l or {}).get('first_landing')})
    total_cells = cells  # running counter: last value IS the grand total (per-row value is cumulative)
    return {'g': g, 'lead': lead, 'farm': farm, 'pub': pub, 'edges': edges, 'rows': rows, 'total_cells': total_cells,
            'flat': flat_cases, 'd6': d6_cases, 'denoms': denom_rows, 'raw_cal': raw_calibers,
            'mismatches': mismatches, 'gate': gate, 'ctx': ctx, 'gpath': g_path}


# ----------------------------------------------------------------- requirement A
UIX_CANDIDATES = [('G_before_ref', '30b84b20~1'), ('Lead_before_ref', '3c72867d')]


def requirement_a(bld):
    skill = 'ui-ux-pro-max'
    e = bld['g']['per_skill'][[x['skill'] for x in bld['g']['per_skill']].index(skill)]
    edges = bld['edges']
    probe = {'decidable': bool(e['dim6_probe']['decidable']), 'supported': list(e['dim6_probe']['supported'])}
    tree = skill_tree(skill)
    ta = read_worktree(skill)
    raw_a, good_a, det_a = score_text(ta, skill, edges, probe, tree)
    out = {}
    texts = {}
    for label, ref in UIX_CANDIDATES:
        raw, t = git_bytes(ref, skill + '/SKILL.md')
        texts[label] = t
        raw_b, good_b, det_b = score_text(t, skill, edges, probe, tree)
        dec = [k for k in DIMS if good_b[k] is not None and good_a[k] is not None]
        s_b = sum(good_b[k] for k in dec)
        s_a = sum(good_a[k] for k in dec)
        rs_b = sum(raw_b[k] for k in GOOD_DIMS)
        rs_a = sum(raw_a[k] for k in GOOD_DIMS)
        out[label] = {'ref': ref, 'full_sha': git_rev_parse(ref), 'commit': git_show_meta(ref),
                      'bytes_utf8': len(t.encode('utf-8', 'replace')),
                      'sha256_text': sha256_text(t),
                      'raw_before': raw_b, 'dims_before': good_b,
                      'sum_before': s_b, 'sum_after': s_a,
                      'banded_uplift_pct': None if s_b == 0 else round((s_a - s_b) * 100.0 / s_b, 4),
                      'banded_numerator': s_a - s_b, 'banded_denominator': s_b,
                      'raw_sum_before_d1_d5': rs_b, 'raw_sum_after_d1_d5': rs_a,
                      'raw_sum_uplift_pct_d1_d5': None if rs_b == 0 else round((rs_a - rs_b) * 100.0 / rs_b, 4),
                      'd5_live_n': det_b['d5']['live_n'], 'd5_dead_n': det_b['d5']['dead_n'],
                      'd1_flag_refs': det_b['d1']['flag_refs'], 'd1_code_lines': det_b['d1']['code_lines']}
    ver = 'MATCHES_G_ARTIFACT' if out['G_before_ref']['sha256_text'] == e['text_sha256']['before'] else 'DOES_NOT_MATCH'
    ver_l = 'MATCHES_LEAD_TEXT_SHA' if out['Lead_before_ref']['sha256_text'] == e['text_sha256']['before'] else 'NOT_THE_G_BEFORE_TEXT'
    ops = line_ops(texts['G_before_ref'], texts['Lead_before_ref'])
    delta_pp = None
    if out['G_before_ref']['banded_uplift_pct'] is not None and out['Lead_before_ref']['banded_uplift_pct'] is not None:
        delta_pp = round(out['G_before_ref']['banded_uplift_pct'] - out['Lead_before_ref']['banded_uplift_pct'], 4)
    nested = 'plugins/frontend-slides/skills/frontend-slides/SKILL.md'
    fa, fk = f_caliber(skill)
    fa2, fk2 = f_caliber(skill, extra=True)
    lead_c, lead_e, lead_p = lead_caliber(skill)
    lead_with_nested = sorted(lead_c + [nested])
    nested_test = {'nested_mirror_skill_md': nested,
                   'f_denom_excl_every_SKILL_md_line': len(fk), 'f_denom_excl_top_SKILL_md_only': len(fk2),
                   'find_total_files': len(fa),
                   'lead_denom': len(lead_c), 'lead_denom_if_nested_counted': len(lead_with_nested),
                   'nested_present_on_disk': os.path.isfile(os.path.join(GS, skill, nested)) if skill == 'frontend-slides' else None,
                   'delta_both_arms': len(fk2) - len(fk)}
    return {'skill': skill, 'g_stored_before_ref': e['sha_pair']['before_ref'],
            'nested_S_kILL_md_test': nested_test,
            'as_published2': {'dims_before_G': e['dims_before'], 'dims_after_G': e['dims_after']},
            'g_stored_before_full': e['sha_pair']['before_full'],
            'lead_before_sha_used': bld['lead']['rows'][[r['skill'] for r in bld['lead']['rows']].index(skill)]['before_sha_used'],
            'as_published': {'sum_before': e['sum_before'], 'sum_after': e['sum_after'], 'uplift_pct': e['uplift_pct']},
            'candidates': out, 'g_text_provenance_verdict': ver, 'lead_text_provenance_verdict': ver_l,
            'diff_between_candidates': ops,
            'uplift_overstatement_pp': delta_pp,
            'raw_bytes_git': {'G_before_ref': len(git_bytes('30b84b20~1', skill + '/SKILL.md')[0] or b''),
                              'Lead_before_ref': len(git_bytes('3c72867d', skill + '/SKILL.md')[0] or b'')}}


# ---------------------------------------------------------------- aggregate face
def aggregates(bld):
    g = bld['g']
    per = dict((e['skill'], e) for e in g['per_skill'])
    band_sb = 0
    band_sa = 0
    raw_b5 = 0
    raw_a5 = 0
    per_skill = {}
    for s in SKILLS:
        e = per[s]
        band_sb += e['sum_before']
        band_sa += e['sum_after']
        rb = sum(e['raw_before'][d] for d in GOOD_DIMS)
        ra = sum(e['raw_after'][d] for d in GOOD_DIMS)
        raw_b5 += rb
        raw_a5 += ra
        per_skill[s] = {'banded_sums': [e['sum_before'], e['sum_after']], 'banded_uplift_pct': e['uplift_pct'],
                        'raw_sum_d1_d5': [rb, ra],
                        'raw_sum_uplift_pct': None if rb == 0 else round((ra - rb) * 100.0 / rb, 4)}
    return {'banded_S_before': band_sb, 'banded_S_after': band_sa,
            'banded_uplift_pct': round((band_sa - band_sb) * 100.0 / band_sb, 4),
            'banded_numerator': band_sa - band_sb, 'banded_denominator': band_sb,
            'raw_sum_d1_d5_before': raw_b5, 'raw_sum_d1_d5_after': raw_a5,
            'raw_sum_uplift_pct': round((raw_a5 - raw_b5) * 100.0 / raw_b5, 4),
            'raw_sum_numerator': raw_a5 - raw_b5, 'raw_sum_denominator': raw_b5,
            'per_skill': per_skill}


def main():
    args = sys.argv[1:]
    gpath = G_DEFAULT
    if '--json' in args:
        gpath = args[args.index('--json') + 1]
    bld = build(gpath)
    aggr = aggregates(bld)
    ra = requirement_a(bld) if os.path.abspath(gpath) == os.path.abspath(G_DEFAULT) else None
    n_rows = len([r for r in bld['rows'] if r.get('status') == 'MEASURED'])
    n_flat = len(bld['flat'])
    print('[CELLS] ' + jdump({'mismatch': len(bld['mismatches']), 'total_cells': bld['total_cells']}))
    print('[GATE] ' + jdump(bld['gate']))
    clean_map = {}
    for r in bld['rows']:
        if r.get('status') == 'MEASURED':
            clean_map[r['skill']] = r['recomputed']['clean']
    print('[RECOMPUTE] ' + jdump(clean_map))
    for m in bld['mismatches']:
        print('MISMATCH ' + m)
    print('[B] band_flattened=%d raw_sum_uplift_pct=%s banded_uplift_pct=%s' % (
          n_flat, aggr['raw_sum_uplift_pct'], aggr['banded_uplift_pct']))
    if ra:
        print('[A] ' + jdump({'g': ra['candidates']['G_before_ref']['banded_uplift_pct'],
                              'fixed': ra['candidates']['Lead_before_ref']['banded_uplift_pct'],
                              'over_pp': ra['uplift_overstatement_pp'],
                              'ver': ra['g_text_provenance_verdict']}))
    print('[C] ' + jdump(bld['d6']))
    print('[D] ' + jdump(bld['denoms']))
    print('[A2] ' + jdump(ra['candidates'] if ra else None))
    print('[A3] ' + jdump(ra['nested_S_kILL_md_test'] if ra else None))
    print('[A4] ' + jdump(ra['as_published2'] if ra else None))
    print('[RAWCAL] ' + jdump(bld['raw_cal']))
    print('[AGGR] ' + jdump(aggr))
    print('[FLAT] ' + jdump(bld['flat']))
    if '--write' in args and ra:
        obj = {'bld': bld, 'aggr': aggr, 'a': ra, 'gpath': gpath}
        with io.open(os.path.join(HERE, 'assembly.json'), 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=1, default=str)
        print('WROTE ' + os.path.join(HERE, 'assembly.json'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
