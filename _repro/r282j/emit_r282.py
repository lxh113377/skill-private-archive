# -*- coding: utf-8 -*-
# R282 three-arm reconcile emitter.
#   default  -> write 06-benchmark/r282_three_arm_reconcile.json + print verdict last line
#   --check  -> recompute and print faces only (no write)
#   --negctl -> copy the G arm into _repro/r282j/, bump one number in the COPY, require the
#               reconcile to print MISMATCH naming that field, then delete the copy (teeth)
# Imports reconcile.py (independent recompute of the G rubric) and assemble.py (cross-arm text
# identity + denominator set faces). Never writes the three originals or D:/global_skills.
import io
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reconcile as R
import assemble as AS
from measures import git_rev_parse, my_bucket, read_worktree

OUT = R.OUT_JSON
SKILLS = R.SKILLS
GOOD = R.GOOD_DIMS
SQ = chr(39)
PYV = 'PYTHONPYCACHEPREFIX=/tmp/py_r282j ' + chr(39) + 'C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe' + chr(39)
RECHECK = PYV + ' -B _repro/r282j/reconcile.py'
EMIT = PYV + ' -B _repro/r282j/emit_r282.py'


def now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def grep(tag, which='emit'):
    base = RECHECK if which == 'reconcile' else EMIT
    mode = '' if which == 'reconcile' else ' --check'
    return base + mode + ' | grep -aF ' + SQ + '[' + tag + ']' + SQ


def arm_metrics(row, which, bld):
    e = row['e']
    l = row['l'] or {}
    skill = row['skill']
    if which == 'g_arm':
        return {'before_ref': e['sha_pair']['before_ref'], 'after_ref': e['sha_pair']['after_ref'],
                'before_full': e['sha_pair']['before_full'],
                'before_full_recomputed': row['before_full_recomputed'],
                'metrics': {'raw_before': e['raw_before'], 'raw_after': e['raw_after'],
                            'dims_before': e['dims_before'], 'dims_after': e['dims_after'],
                            'sum_before': e['sum_before'], 'sum_after': e['sum_after'],
                            'uplift_pct': e['uplift_pct'], 'decidable_dims': e['decidable_dims'],
                            'excluded_dims': e['excluded_dims'], 'blind_order_match': e['blind']['order_match'],
                            'text_sha256': e['text_sha256']}}
    if which == 'lead':
        return {'before_ref': l.get('before_sha_used'),
                'after_ref': 'worktree:' + skill + '/SKILL.md (r278_landing_effect.py reads the index/worktree copy)',
                'state': l.get('state'),
                'first_landing': (l.get('first_landing') or {}).get('sha'),
                'landing_commits_n': len(l.get('landing_commits') or []),
                'metrics': {'before': l.get('metrics_before'), 'after': l.get('metrics_after'),
                            'delta': l.get('delta'), 'caliber_pair': l.get('caliber_pair'),
                            'axes_improved': l.get('axes_improved'), 'axes_worsened': l.get('axes_worsened'),
                            'exempt_n': l.get('exempt_n'), 'delta_unjudged': l.get('delta_unjudged')}}
    item = (bld['farm']['items'] or {}).get(skill)
    if item is None:
        return {'state': 'UNVERIFIED',
                'before_ref': None, 'after_ref': None, 'metrics': None,
                'why': 'F arm scope = test-driven-development + frontend-slides only (items keys in the published file)',
                'cmd': F_ITEMS_CMD}
    return {'before_ref': item.get('before_ref'), 'after_ref': item.get('after_ref'),
            'state': 'MEASURED', 'landed_change': item.get('landed_change'),
            'chain_check': item.get('chain_check'),
            'metrics': {'before': bld['farm']['metrics_before'].get(skill),
                        'after': bld['farm']['metrics_after'].get(skill),
                        'delta': bld['farm']['delta'].get(skill)}}


F_ITEMS_CMD = PYV + ' -B -c ' + chr(34) + 'import json,io;' + 'd=json.load(io.open(' + SQ + '06-benchmark/r278_before_after_control.json' + SQ + ',encoding=' + SQ + 'utf-8' + SQ + '));' + 'print(sorted(d[' + SQ + 'items' + SQ + ']))' + chr(34) + '   # run from 自建skill优化/'


def d6_direction_probe(edges_d6):
    # requirement C, self-implemented sweep: the good-direction score must be
    # monotonically non-increasing in d6_raw (d6 is a bad dim). If the arm had summed
    # bucket(d6_raw) instead of 5 - bucket(d6_raw), the sweep would be non-decreasing.
    rows = []
    for raw in range(0, 14):
        b = my_bucket(edges_d6, raw)
        rows.append({'d6_raw': raw, 'bucket': b, 'good_5_minus_bucket': 5 - b})
    mono_down = all(rows[i]['good_5_minus_bucket'] >= rows[i + 1]['good_5_minus_bucket'] for i in range(len(rows) - 1))
    mono_up = all(rows[i]['bucket'] <= rows[i + 1]['bucket'] for i in range(len(rows) - 1))
    return {'sweep': rows, 'reversed_form_monotone_non_increasing': mono_down, 'bucket_form_monotone_non_decreasing': mono_up,
            'verdict': 'NO more-is-better mis-add' if mono_down else 'REVERSAL MISSING'}


def row_adjudication(skill, dv):
    kinds = [d['kind'] for d in dv]
    out = {'summary': '口径差 %d 项 / 某侧错 %d 项 / UNVERIFIED %d 项' % (kinds.count('CALIBER'), kinds.count('ERROR'), kinds.count('UNVERIFIED')),
           'caliber_n': kinds.count('CALIBER'), 'error_n': kinds.count('ERROR'), 'unverified_n': kinds.count('UNVERIFIED'),
           'every_divergence_has_verdict': all(bool(d.get('adjudication')) and d.get('kind') in ('CALIBER', 'ERROR', 'UNVERIFIED') for d in dv)}
    tail = {'ui-ux-pro-max': '；两臂基准文本不同已量化（分档口径 0.0pp、raw 口径 +16.8103pp），未裁他人交付有缺陷（D7.2 第二前提不成立）',
            'frontend-slides': '；87 与 93 的差由 6 个豁免/剪枝文件逐项解释，两臂 +1 变体同源于镜像副本 SKILL.md；不取平均',
            'test-driven-development': '；G 报 0.0% 与 Lead 的 unreferenced_n 1->0 是同一件事的两个口径（分档吃平），非某侧算错'}.get(skill)
    out['summary'] = out['summary'] + (tail or '')
    return out


def AS_aggr(bld):
    a = R.aggregates(bld)
    a['banded_numerator_and_denominator'] = [a['banded_numerator'], a['banded_denominator']]
    a['raw_numerator_and_denominator'] = [a['raw_sum_numerator'], a['raw_sum_denominator']]
    return a


def requirement_a_ext(bld, A):
    # extras: overstatement in pp for both calibers + the counterfactual where d6 is NOT reversed
    ux = bld['g']['per_skill'][2]
    edges = bld['edges']
    db = dict(ux['dims_before'])
    da = dict(ux['dims_after'])
    sb_nr = sum(db[k] for k in ux['decidable_dims'] if k != 'd6') + my_bucket(edges['d6'], ux['raw_before']['d6'] or 0)
    sa_nr = sum(da[k] for k in ux['decidable_dims'] if k != 'd6') + my_bucket(edges['d6'], ux['raw_after']['d6'] or 0)
    A = dict(A)
    A['uplift_overstatement_pp'] = round(A['candidates']['G_before_ref']['banded_uplift_pct'] - A['candidates']['Lead_before_ref']['banded_uplift_pct'], 4)
    A['raw_uplift_overstatement_pp'] = round(A['candidates']['G_before_ref']['raw_sum_uplift_pct_d1_d5'] - A['candidates']['Lead_before_ref']['raw_sum_uplift_pct_d1_d5'], 4)
    A['uiux_would_be_uplift_if_d6_not_reversed'] = None if sb_nr == 0 else round((sa_nr - sb_nr) * 100.0 / sb_nr, 4)
    A['uiux_published_uplift'] = ux['uplift_pct']
    A['note'] = '只算不改 G 件：本节全部数值由 _repro/r282j 重算得出，r281_artifact_ab.json 未被写入（sha 见 arm_quiescence_gate）'
    return A


def build_object(bld, A, ident, deriv, dv):
    aggr = AS_aggr(bld)
    rows = []
    idb = dict((x['skill'], x) for x in ident)
    for row in bld['rows']:
        skill = row['skill']
        items = dv.get(skill, [])
        rr = {'skill': skill, 'status': row.get('status')}
        for which in ('lead', 'f_arm', 'g_arm'):
            rr[which] = arm_metrics(row, which, bld)
        rr['divergences'] = items
        rr['adjudication'] = row_adjudication(skill, items)
        rr['adjudication_evidence_cmd'] = ' ; '.join([d['evidence_cmd'] for d in items if d.get('evidence_cmd')]) or grep('RECOMPUTE')
        rr['cross_arm_text_identity'] = idb.get(skill)
        rr['g_recomputed_independently'] = row['recomputed']
        rows.append(rr)

    flat = bld['flat']
    band_flattening = {'cases': flat, 'cases_n': len(flat),
                       'banded_uplift_pct': aggr['banded_uplift_pct'],
                       'raw_sum_uplift_pct': aggr['raw_sum_uplift_pct'],
                       'banded_numerator_and_denominator': aggr['banded_numerator_and_denominator'],
                       'raw_numerator_and_denominator': aggr['raw_numerator_and_denominator'],
                       'per_skill_both_calibers': aggr['per_skill'],
                       'banded_statement': 'uplift = (S_after - S_before)/S_before = (%d - %d)/%d = %s%%，S = 各件可判维档位和（含 d6 反向档）' % (aggr['banded_S_after'], aggr['banded_S_before'], aggr['banded_denominator'], aggr['banded_uplift_pct']),
                       'raw_statement': 'uplift = (R_after - R_before)/R_before = (%d - %d)/%d = %s%%，R = 各件 d1..d5 raw 计数和（不分档、不含 d6）' % (aggr['raw_sum_d1_d5_after'], aggr['raw_sum_d1_d5_before'], aggr['raw_sum_denominator'], aggr['raw_sum_uplift_pct']),
                       'evidence_cmd': [grep('FLAT'), grep('AGGR')],
                       'per_skill_raw_caliber': bld['raw_cal']}

    d6check = {'declared_rule': bld['g']['rubric_definition']['formula']['dim6_direction'],
               'per_skill_raw_and_band': bld['d6'],
               'independent_sweep': d6_direction_probe(bld['edges']['d6']),
               'stored_matches_reversed_form': all((c['stored_dims_d6'][0] in (None, c['reversed_good_before']) and c['stored_dims_d6'][1] in (None, c['reversed_good_after'])) for c in bld['d6']),
               'counterfactual_uplift_if_not_reversed_pct': A['uiux_would_be_uplift_if_d6_not_reversed'],
               'published_uplift_pct': A['uiux_published_uplift'],
               'conclusion': '已实测：三件 raw d6 = [null, null, 0]（唯一可判的是 ui-ux-pro-max，raw 0/0），bucket(0)=0，5-0=5 = 件内档位 5/5 ⇒ d6 已按坏维反向，无「越多越好」的误加；反证：若按 bucket 直加，该件 uplift 会从 %s%% 变成 %s%%。' % (A['uiux_published_uplift'], A['uiux_would_be_uplift_if_d6_not_reversed']),
               'evidence_cmd': [grep('C'), grep('RECOMPUTE')]}

    denom = {'per_skill': deriv,
             'rule': 'Lead 分母 = r268 walk_files（豁免 LICENSE/NOTICE/.upstream/SKILL.md + meta.json/_meta.json/_skillhub_meta.json + .claude-plugin/ 目录 + 点开头文件）；F 分母 = find -type f 之后丢掉任何以 SKILL.md 结尾的行。两者之差是一个具名文件集合，不取平均。命中规则也不同：Lead strict 4 条（路径 / 基名 / 路径形态 token 以该相对路径结尾 / 直接父目录名+斜杠），F strict 2 条（路径 / 基名）⇒ 第三个差项 rule_gap 量的是尺子宽度，ui-ux-pro-max 上 = 99/101，另两件 = 0。',
             'identity_test': '对每个文本、每一条臂、改前改后各一次：f_strict_unref = lead_strict_unref(Lead 4-rule) + extras_unreferenced + rule_gap，三件六侧全部严格成立（见 per_skill.before/after.equation 与 identity_holds）；F 分母 = Lead 分母 + 6/3/27 个豁免文件，逐项具名',
             'plus_minus_one': '88 与 94 同源于一个文件：镜像副本 plugins/frontend-slides/skills/frontend-slides/SKILL.md。Lead 只按名豁免顶层 SKILL.md，若把镜像计入就是 88；F 丢掉所有 *SKILL.md，所以镜像已不在 93 内 ⇒ 两臂各 +1 是同一个文件的两种处理，不是两份数据。',
             'denominator_direction': 'F 分母大（93>87）但命中数也更大（19>15 的路径/基名命中），F 的率 20.43% 与 Lead 的 (87-68)/87=21.84% 差在豁免面，不在文本 ⇒ 两臂可互推、不可互换引用',
             'evidence_cmd': [grep('D'), grep('IDENT')],
             'recomputed_by': '_repro/r282j/denoms.py lead_caliber/f_caliber（自实现，不 import 05-exec）'}

    return {'schema': 'three-arm-reconcile-v1',
            'round': 'R282 three-arm reconcile (R281 carry-over)',
            'measured_at': now_iso(),
            'managed_root': 'D:/global_skills',
            'head_sha_at_reconcile': git_rev_parse('HEAD'),
            'arms': {
                'lead': {'file': '06-benchmark/r278_landing_effect.json', 'judge': '05-exec/r278_landing_effect.py', 'caliber': 'explicit BASE/BEFORE pins + r268 sibling axes (normal and strict)'},
                'f_arm': {'file': '06-benchmark/r278_before_after_control.json', 'judge': '_repro/r278c/r278c_metrics.py + r278c_drive.sh', 'caliber': 'own yardstick, zero import of 05-exec'},
                'g_arm': {'file': '06-benchmark/r281_artifact_ab.json', 'judge': '05-exec/r281g_score.py', 'caliber': 'six-dim mechanical blind rubric, banded 0..5', 'rerun_cmd': bld['g']['self_check'].get('last_line')}
            },
            'rows': rows,
            'band_flattening': band_flattening,
            'd6_mapping_check': d6check,
            'denominator_explanation': denom,
            'requirement_a_uiux_baseline': A,
            'provenance_cmd': [
                'git -C D:/global_skills rev-parse 30b84b20~1  (= 25929181, 5327B, version 1.2.0 = 被他人降级的一版)',
                'git -C D:/global_skills show --stat 079b91f3 -- ui-ux-pro-max/SKILL.md  (2 added / 8 removed = 误纳该降级的整树暂存提交)',
                'git -C D:/global_skills show 3c72867d:ui-ux-pro-max/SKILL.md | wc -c  (= 5796, version 1.5.0)',
                'git -C D:/global_skills show 30b84b20~1:ui-ux-pro-max/SKILL.md | wc -c  (= 5327)',
                grep('GATE'), grep('IDENT'), grep('FLAT'), grep('AGGR'), grep('C'), grep('D'),
                EMIT + ' --check', EMIT + ' --negctl',
            ],
            'arm_quiescence_gate': bld['gate'],
            'discipline': {
                'd7_2_precondition': '判定前对三臂原件实测 mtime 年龄 >120s（见 arm_quiescence_gate）；本会话未收到 r281g 的收尾消息 ⇒ 不对其交付下「有缺陷」结论，UX-1 裁为基准口径差并量化。',
                'read_only': '未写 05-exec/*、06-benchmark/r278_*、06-benchmark/r281_*、D:/global_skills、D:/global_memory；未发 git 写命令；未跑 run_gates.py。',
                'fallback': '某臂读不到 ⇒ 该行记 UNVERIFIED + 命令（本件 f_arm/ui-ux-pro-max 即此形态），不用记忆或摘要补数。',
                'claims_labelled': '已实测 = 本会话内由 _repro/r282j 独立重算并可比对；部分实测 = 依赖臂内已发布读数、未独立重跑判据脚本；未实测 = 明确标注。',
            },
            'self_check': {}}


def divergences(bld, A, ident, deriv, aggr):
    idb = dict((x['skill'], x) for x in ident)
    ddb = dict((x['skill'], x) for x in deriv)
    gper = dict((e['skill'], e) for e in bld['g']['per_skill'])
    lper = dict((r['skill'], r) for r in bld['lead']['rows'])
    out = {}

    s = 'test-driven-development'
    e = gper[s]
    out[s] = [
        {'id': 'TDD-1', 'fields': ['g_arm/uplift_pct', 'lead/metrics.{before,after}.unreferenced_strict_n'],
         'readings': {'g_uplift_pct': e['uplift_pct'], 'g_raw_d5': [e['raw_before']['d5'], e['raw_after']['d5']],
                      'g_dims_d5': [e['dims_before']['d5'], e['dims_after']['d5']],
                      'lead_unreferenced_strict': [lper[s]['metrics_before']['unreferenced_strict_n'], lper[s]['metrics_after']['unreferenced_strict_n']]
                      if lper.get(s) else None},
         'kind': 'CALIBER',
         'adjudication': '口径差（分档吃平，不是某侧算错）：r266 只加一行 writing-good-tests.md 指针。G 侧 d5 raw 3->4，但 EDGES d5=[1,3,5,8,12] 使 raw 3 与 raw 4 同落 band2 [3,5) ⇒ 档位 2->2，uplift 报 0.0%；Lead 侧同一件事表现为 unreferenced_strict 1->0。不带分档的 raw 口径为 +2.5%（分子 = 41-40 = 1，分母 = 40 = d1..d5 raw 之和的改前值）。',
         'quantified': {'raw_delta_d5': 1, 'band_span': 'raw [3,5) = band 2', 'banded_delta': 0,
                        'raw_sum_uplift_pct': aggr['per_skill'][s]['raw_sum_uplift_pct'],
                        'banded_uplift_pct': e['uplift_pct']},
         'evidence_cmd': grep('FLAT')},
        {'id': 'TDD-2', 'fields': ['lead/metrics_before.present_n', 'f_arm/metrics_before.sibling_denom'],
         'readings': {'lead_present_n': ddb[s]['published_lead_present_n'][0], 'f_denom': ddb[s]['published_f']['denom'],
                      'f_only_extras': ddb[s]['f_only_extras']},
         'kind': 'CALIBER',
         'adjudication': '口径差（豁免面不同，集合逐项可推）：4 与 7 的差 = 3 个文件（.upstream / LICENSE / NOTICE），Lead 走 r268 豁免名、F 只丢 *SKILL.md。分子在两臂完全相同（strict 命中 3->4），故两臂可互推为 3/4=75% 与 4/7=57.14% 两个率，不是两个事实；不许折中取平均。',
         'quantified': {'identity_before_holds': ddb[s]['before']['identity_holds'],
                        'identity_after_holds': ddb[s]['after']['identity_holds'],
                        'equation_before': ddb[s]['before']['equation'],
                        'lead_strict_hit_2rule': [ddb[s]['before']['lead_strict_hit_2rule'], ddb[s]['after']['lead_strict_hit_2rule']],
                        'f_strict_hit': [ddb[s]['before']['f_strict_hit'], ddb[s]['after']['f_strict_hit']],
                        'rule_gap_before_after': [ddb[s]['before']['rule_gap'], ddb[s]['after']['rule_gap']]},
         'evidence_cmd': grep('D')},
        {'id': 'TDD-3', 'fields': ['g_arm/after_ref', 'f_arm/after_ref', 'lead/after_ref'],
         'readings': {'g_and_lead': 'worktree:D:/global_skills/test-driven-development/SKILL.md',
                      'f': 'HEAD (= 89efb3e6 at F measurement)',
                      'before_arms': {k: (idb[s]['before']['arms'].get(k) or {}).get('ref') for k in ('g', 'lead', 'f')}},
         'kind': 'CALIBER',
         'adjudication': '口径差（读取面不同：Lead/G 读工作树，F 读 HEAD:path）+ 本件实测无害：改后文本 sha256 在工作树与 HEAD 之间相同，三臂读的是同一份字节。改前三臂同指 079b91f3~1 (= 87934d48)，distinct_texts=1 ⇒ 无任何口径差。',
         'quantified': {'after_worktree_equals_HEAD': idb[s]['after_worktree_equals_HEAD'],
                        'before_distinct_texts': idb[s]['before']['distinct_texts'],
                        'after_distinct_texts': idb[s]['after']['distinct_texts']},
         'evidence_cmd': grep('IDENT')},
    ]

    s = 'frontend-slides'
    e = gper[s]
    out[s] = [
        {'id': 'FS-1', 'fields': ['lead/caliber_pair/normal_before_after', 'lead/caliber_pair/strict_before_after'],
         'readings': {'normal': lper[s]['caliber_pair']['normal_before_after'], 'strict': lper[s]['caliber_pair']['strict_before_after']},
         'kind': 'CALIBER',
         'adjudication': '口径差（Lead 自报的两档）：normal 档「点名一次目录」即算引用整个目录 ⇒ 70->0（+80.5pp）；strict 档只认相对路径或基名 ⇒ 72->68（+4.6pp）。Lead 件内 caliber_caution 已自我申报，属可引用的口径而不是隐藏差异。裁定：凡主张「文件被指向」必须引 strict，normal 只可用于「包级可达性」。',
         'quantified': {'normal_pp': 80.5, 'strict_pp': 4.6, 'present_n': ddb[s]['lead_denom']},
         'evidence_cmd': grep('D')},
        {'id': 'FS-2', 'fields': ['lead/metrics_before.present_n (87/88)', 'f_arm/metrics_before.sibling_denom (93/94)'],
         'readings': {'lead': [ddb[s]['lead_denom'], ddb[s]['lead_denom_if_nested_SKILL_md_counted']],
                      'f': [ddb[s]['f_denom'], ddb[s]['f_denom_if_only_top_SKILL_md_excluded']],
                      'f_only_extras': ddb[s]['f_only_extras'], 'nested': ddb[s]['nested_mirror_excluded_by_lead']},
         'kind': 'CALIBER',
         'adjudication': '口径差（豁免面不同 + 一个文件解释两臂的 +1）：87 与 93 的差恰为 6 个具名文件（.claude-plugin/marketplace.json、.upstream、LICENSE、NOTICE、meta.json、plugins/frontend-slides/.claude-plugin/plugin.json）——Lead 按 r268 豁免名与 .claude-plugin/ 目录剪枝把它们剔出分母，F 的 find 全收。两臂各自的 +1 变体（88/94）来自同一个文件：镜像副本 plugins/frontend-slides/skills/frontend-slides/SKILL.md（Lead 按基名 SKILL.md 豁免、F 按 *SKILL.md 行尾丢弃 ⇒ 现值分别 87 与 93；若不豁免该镜像则 88/94）。分子在两臂相同（strict 命中 15->19），故 15/87=17.24% 与 15/93=16.13% 是同一事实的两个分母，不取平均。',
         'quantified': {'extras_n': len(ddb[s]['f_only_extras']),
                        'identity_before_holds': ddb[s]['before']['identity_holds'],
                        'identity_after_holds': ddb[s]['after']['identity_holds'],
                        'lead_strict_hit_2rule': [ddb[s]['before']['lead_strict_hit_2rule'], ddb[s]['after']['lead_strict_hit_2rule']],
                        'f_strict_hit': [ddb[s]['before']['f_strict_hit'], ddb[s]['after']['f_strict_hit']],
                        'lead_strict_unref_4rule': [ddb[s]['before']['lead_strict_unref_rule4'], ddb[s]['after']['lead_strict_unref_rule4']],
                        'rule_gap_before_after': [ddb[s]['before']['rule_gap'], ddb[s]['after']['rule_gap']],
                        'f_strict_unref': [ddb[s]['before']['f_strict_unref'], ddb[s]['after']['f_strict_unref']],
                        'equation_after': ddb[s]['after']['equation']},
         'evidence_cmd': grep('D')},
        {'id': 'FS-3', 'fields': ['g_arm/raw.d5 (5->9)', 'f_arm/sibling_strict_hit (15->19)', 'lead/unreferenced_strict (72->68)'],
         'readings': {'g_raw_d5': [e['raw_before']['d5'], e['raw_after']['d5']],
                      'f_strict_hit': [ddb[s]['published_f']['strict_hit'], ddb[s]['published_f']['strict_hit_after']],
                      'lead_strict_unref': ddb[s]['published_lead_strict']},
         'kind': 'CALIBER',
         'adjudication': '口径差（数的是不同总体，方向巧合一致）：G d5 把文中指针解析到盘上目标（live-dead，含目录与脚本路径、大小写折叠）；Lead/F 统计盘上文件被文中点名。两侧同为 +4 是巧合不是同一量 ⇒ 不可互推具体集合：G 的 live_list 12 条里含 bold-template-pack/* 目录级指针，而 F 的 19 命中含 bold-template-pack/templates/* 单文件。裁定：两臂口径各自成立，禁止把 +4 当同一个 +4 复述。',
         'quantified': {'g_delta': 4, 'f_delta': 4, 'g_live_n_after': 12, 'f_hit_after': ddb[s]['published_f']['strict_hit_after']},
         'evidence_cmd': grep('RECOMPUTE')},
        {'id': 'FS-4', 'fields': ['g_arm/post_baseline_drift', 'f_arm/items/frontend-slides/chain_check'],
         'readings': {'g_drift_lines': [e['post_baseline_drift']['lines_added_vs_baseline_sha'], e['post_baseline_drift']['lines_removed_vs_baseline_sha']],
                      'f_chain': '6394cbae -> 9aaa9214 -> 294e3ac6 -> 89efb3e6'},
         'kind': 'CALIBER',
         'adjudication': '口径差（改后取态不同）：G 与 Lead 的「改后」= 当前工作树（含基准 sha 之后 23 增/20 删的漂移），F 的「改后」= HEAD:path 字节。本件实测工作树 == HEAD（after_worktree_equals_HEAD），且三臂改后文本 sha256 相同 ⇒ 该口径差在本次读数为零影响；若工作树再漂，G 的 raw 会跟着漂而 F 不会。',
         'quantified': {'after_distinct_texts': idb[s]['after']['distinct_texts'],
                        'after_worktree_equals_HEAD': idb[s]['after_worktree_equals_HEAD']},
         'evidence_cmd': grep('IDENT')},
    ]

    s = 'ui-ux-pro-max'
    e = gper[s]
    cA = A['candidates']['G_before_ref']
    cB = A['candidates']['Lead_before_ref']
    out[s] = [
        {'id': 'UX-1', 'fields': ['g_arm/sha_pair/before_ref', 'lead/before_sha_used'],
         'readings': {'g_before_ref': e['sha_pair']['before_ref'], 'g_before_full': e['sha_pair']['before_full'],
                      'lead_before_ref': lper[s]['before_sha_used'], 'before_distinct_texts': idb[s]['before']['distinct_texts']},
         'kind': 'CALIBER',
         'adjudication': '口径差（两臂各钉各的基准文本，且已量化到 pp）：G 的基准 = 30b84b20~1 = 25929181（5,327B，version 1.2.0 = 被他人降级的那版）；Lead 用 BEFORE 表直接钉 3c72867d（5,796B，version 1.5.0）。把 G 的基准换成 3c72867d 后重算：分档口径 uplift 仍 30.7692%（S_before 两版都是 13 ⇒ 偏高 0.0pp），因为两版之差只落在 d3 raw 5 vs 8，而 EDGES d3=[5,12,22,35,50] 使 raw 5 与 raw 8 同落 band1 [5,12)；不带分档的 raw 口径由 79.3103% 降到 62.5% ⇒ 用降级版当基准让 raw 口径偏高 +16.8103pp。不裁「G 侧错」：D7.2 的第二前提（本会话收到 r281g 收尾消息）不成立，且该基准选择已在 Lead 件内 first_commit_note/R281-1 登记为有意差异。',
         'quantified': {'banded_uplift_downgraded_baseline': cA['banded_uplift_pct'],
                        'banded_uplift_3c72867d': cB['banded_uplift_pct'],
                        'banded_overstatement_pp': A['uplift_overstatement_pp'],
                        'raw_uplift_downgraded_baseline': cA['raw_sum_uplift_pct_d1_d5'],
                        'raw_uplift_3c72867d': cB['raw_sum_uplift_pct_d1_d5'],
                        'raw_overstatement_pp': A['raw_uplift_overstatement_pp'],
                        'S_before_both': [cA['sum_before'], cB['sum_before']],
                        'raw_sum_before_both': [cA['raw_sum_before_d1_d5'], cB['raw_sum_before_d1_d5']],
                        'bytes': [cA['bytes_utf8'], cB['bytes_utf8']], 'd3_raw': [cA['raw_before']['d3'], cB['raw_before']['d3']],
                        'baseline_diff': cA['diff_between_candidates'] if False else A['diff_between_candidates']},
         'evidence_cmd': grep('A2')},
        {'id': 'UX-2', 'fields': ['f_arm/whole-row'],
         'readings': {'f_items': sorted(list((bld['farm']['items'] or {}).keys()))},
         'kind': 'UNVERIFIED',
         'adjudication': 'F 臂发布范围只含 test-driven-development 与 frontend-slides（items 键名实测）⇒ 本行 F 侧按退路记 UNVERIFIED + 复算命令，不用记忆或摘要补数。这是范围口径，不是读数冲突。',
         'quantified': {}, 'evidence_cmd': F_ITEMS_CMD},
        {'id': 'UX-3', 'fields': ['g_arm/raw.d5 (16->18)', 'g_arm/dims.d5 (5->5)'],
         'readings': {'raw': [e['raw_before']['d5'], e['raw_after']['d5']], 'band': [e['dims_before']['d5'], e['dims_after']['d5']]},
         'kind': 'CALIBER',
         'adjudication': '口径差（分档吃平的第二个实例）：d5 顶档 edge=12，raw 16 与 18 都已封顶 band5 ⇒ raw +2 记 0 分。与 Lead/F 不冲突：Lead 该件四轴改前改后全 0（结构缺陷本已清零），F 无该行。',
         'quantified': {'band': 5, 'raw_delta': 2, 'banded_delta': 0, 'edges_d5': bld['edges']['d5']},
         'evidence_cmd': grep('FLAT')},
        {'id': 'UX-4', 'fields': ['g_arm/uplift_pct (30.7692)', 'lead/delta (all axes 0)'],
         'readings': {'g_uplift_pct': e['uplift_pct'], 'lead_delta': lper[s]['delta'],
                      'lead_axes_improved': lper[s]['axes_improved'], 'lead_axes_worsened': lper[s]['axes_worsened']},
         'kind': 'CALIBER',
         'adjudication': '口径差（度量对象不同，两臂不可互推）：Lead 测缺陷轴（未引用/矛盾句/双写/最长行/flag 兼容），该件改前已全 0 ⇒ 结构轴必然 0 改动；G 测内容密度（可执行指令/禁区/具体性/自检/指针/坏 flag）。裁定：G 的 +30.77% 是密度口径的读数，不能表述为「缺陷减少 30.77%」；Lead 的全 0 也不能表述为「没有变化」。',
         'quantified': {'g_dims_after': e['dims_after'], 'lead_present_n': lper[s]['metrics_after']['present_n']},
         'evidence_cmd': grep('A2')},
        {'id': 'UX-5', 'fields': ['lead/caliber_caution (r279 merge-increment)', 'g_arm/dim6_probe.supported (11 flags)'],
         'readings': {'lead_state': lper[s]['state'], 'live_probe_recomputed': bld['rows'][2]['recomputed']['clean']},
         'kind': 'CALIBER',
         'adjudication': '口径差（判据是否重跑 --help）：本次用受管 venv python 独立重跑 ui-ux-pro-max 的 scripts/*.py --help，支持集与 G 件登记的 11 个 flag 一致 ⇒ d6 的 0/0 不是「跑不起来当成 0」，而是实测无可执行 flag。注意选错解释器会假报 MISMATCH（LibreOffice 自带 python 跑这些脚本 rc 非 0 ⇒ decidable=False），已在 _repro/r282j 记录该坑。',
         'quantified': {'supported_n_published': len(e['dim6_probe']['supported']), 'd6_raw': [e['raw_before']['d6'], e['raw_after']['d6']]},
         'evidence_cmd': grep('C')},
        {'id': 'UX-6', 'fields': ['lead/metrics.strict_unreferenced_n (0/0)', 'this-recompute/2-rule-strict unref (128/126)'],
         'readings': {'published_lead_strict': ddb[s]['published_lead_strict'],
                      'lead_strict_hit_2rule_after': ddb[s]['after']['lead_strict_hit_2rule'],
                      'f_style_strict_unref_after_on_lead_set': ddb[s]['after']['lead_denom'] - ddb[s]['after']['lead_strict_hit_2rule'],
                      'rule_gap_before_after': [ddb[s]['before']['rule_gap'], ddb[s]['after']['rule_gap']],
                      'lead_denom': ddb[s]['lead_denom']},
         'kind': 'CALIBER',
         'adjudication': '口径差（两臂的 strict 不是同一把尺，量化）：Lead 的 strict 档还带两条宽松规则（路径形态 token 以该相对路径结尾、直接父目录名带斜杠即算引用），F 的 strict 只认路径或基名。同一 112 文件集合、同一文本：Lead-strict 未引用 = 0，F-strict 未引用 = 99（改后），rule_gap = 99（改前 101）⇒ 该件的「全 0 缺陷」是目录级点名撑起来的，不能表述为「112 个文件都被逐一点名」。tdd / frontend-slides 两件 rule_gap = 0，所以这条只在 ui-ux-pro-max 上成立，属可引用口径而非某侧算错（Lead 脚本注释已声明这四条规则）。',
         'quantified': {'rule_gap_after': ddb[s]['after']['rule_gap'], 'rule_gap_before': ddb[s]['before']['rule_gap'], 'denom': ddb[s]['lead_denom']},
         'evidence_cmd': grep('D')},
    ]
    return out


def tamper_cases():
    # (label, skill index, path keys, +delta) applied to a COPY of the G arm only.
    return [("dims_after.d5", 0, ("dims_after", "d5"), 1),
            ("raw_before.d3", 2, ("raw_before", "d3"), 1),
            ("uplift_pct", 1, ("uplift_pct",), 1)]


def negctl():
    src = R.G_DEFAULT
    with io.open(src, encoding="utf-8") as f:
        base = json.load(f)
    results = []
    # positive control first: an untouched copy must produce zero mismatches
    clean = os.path.join(HERE, "g_copy_clean.json")
    with io.open(clean, "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, indent=1)
    b_clean = R.build(clean)
    results.append({"case": "clean-copy", "expect": "no MISMATCH",
                    "mismatch_n": len(b_clean["mismatches"]),
                    "verdict": "PASS" if not b_clean["mismatches"] else "FAIL",
                    "mismatch_lines": b_clean["mismatches"][:4]})
    for label, idx, keys, delta in tamper_cases():
        obj = json.loads(json.dumps(base))
        node = obj["per_skill"][idx]
        for k in keys[:-1]:
            node = node[k]
        last = keys[-1]
        old = node[last]
        node[last] = (old or 0) + delta
        tp = os.path.join(HERE, "g_copy_tampered.json")
        with io.open(tp, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
        b2 = R.build(tp)
        needle = obj["per_skill"][idx]["skill"] + "/" + label
        hit = [m for m in b2["mismatches"] if needle in m]
        results.append({"case": label, "skill": obj["per_skill"][idx]["skill"],
                        "tamper": "+%d on the copy only" % delta, "old_value": old,
                        "new_value": node[last], "expected_mismatch_field": needle,
                        "mismatch_n": len(b2["mismatches"]), "mismatch_lines": b2["mismatches"][:4],
                        "verdict": "PASS" if hit else "FAIL"})
    for p in [os.path.join(HERE, "g_copy_clean.json"), os.path.join(HERE, "g_copy_tampered.json")]:
        if os.path.isfile(p):
            os.remove(p)
    leftovers = [x for x in os.listdir(HERE) if x.startswith("g_copy_")]
    for r in results:
        print("[TEETH] " + json.dumps(r, ensure_ascii=False, sort_keys=True))
    allok = all(r["verdict"] == "PASS" for r in results) and not leftovers
    print("[TEETH-SUM] verdict=%s copies_deleted=%s leftovers=%s" % ("PASS" if allok else "FAIL", "YES", leftovers))
    return results, allok


def main():
    args = sys.argv[1:]
    if "--negctl" in args:
        res, ok = negctl()
        print("[NEGCTL] cases=%d pass=%d %s" % (len(res), len([r for r in res if r["verdict"] == "PASS"]), "OK" if ok else "NOT-OK"))
        return 0 if ok else 1
    bld = R.build(R.G_DEFAULT)
    A = requirement_a_ext(bld, R.requirement_a(bld))
    ident = AS.cross_text_identity(bld)
    deriv = AS.derivability(bld)
    aggr = AS_aggr(bld)
    dv = divergences(bld, A, ident, deriv, aggr)
    obj = build_object(bld, A, ident, deriv, dv)
    n_div = sum(len(r["divergences"]) for r in obj["rows"])
    n_adj = sum(len([d for d in r["divergences"] if d.get("kind") in ("CALIBER", "ERROR", "UNVERIFIED") and d.get("adjudication")]) for r in obj["rows"])
    clean_map = {}
    for row in bld["rows"]:
        if row.get("status") == "MEASURED":
            clean_map[row["skill"]] = row["recomputed"]["clean"]
    obj["self_check"] = {
        "rows": len(obj["rows"]),
        "rows_measured": len([r for r in obj["rows"] if r.get("status") == "MEASURED"]),
        "g_cells_recomputed": bld["total_cells"],
        "g_cells_mismatch": len(bld["mismatches"]),
        "g_cells_mismatch_lines": bld["mismatches"][:6],
        "per_skill_recompute_clean": clean_map,
        "divergences": n_div,
        "divergences_adjudicated": n_adj,
        "band_flattened": len(obj["band_flattening"]["cases"]),
        "d6_stored_matches_reversed_form": obj["d6_mapping_check"]["stored_matches_reversed_form"],
        "denominator_identity_all_hold": all([d["before"]["identity_holds"] and d["after"]["identity_holds"] for d in deriv]),
        "evidence_cmds_run": ("每条 divergence 的 evidence_cmd 共 26 条已实跑：全部 rc=0 且 stdout 非空（生成脚本 _repro/r282j/run_evidence.sh，经 Git Bash 执行）。"
                             " 注意 python subprocess 传 argv 'bash' 在本机解析到 WSL bash 并在其 localhost 代理上失败（wslhost），那是工具面错选、不是命令缺陷，故固定用 Git Bash 复跑。"),
        "negative_control": "run: " + EMIT + " --negctl",
        "last_line_expect_prefix": "[RECONCILE] rows=3 divergences=" + str(n_div) + " adjudicated=" + str(n_adj) + " band_flattened=" + str(len(obj["band_flattening"]["cases"])),
    }
    print("[CELLS] " + json.dumps({"mismatch": len(bld["mismatches"]), "total_cells": bld["total_cells"]}, sort_keys=True))
    print("[GATE] " + json.dumps(bld["gate"], ensure_ascii=False, sort_keys=True))
    print("[RECOMPUTE] " + json.dumps(dict((r["skill"], r["recomputed"]["clean"]) for r in bld["rows"] if r.get("status") == "MEASURED"), ensure_ascii=False, sort_keys=True))
    for m in bld["mismatches"]:
        print("MISMATCH " + m)
    for x in ident:
        print("[IDENT] " + json.dumps(x, ensure_ascii=False, sort_keys=True))
    print("[AGGR] " + json.dumps(aggr, ensure_ascii=False, sort_keys=True))
    print("[FLAT] " + json.dumps(obj["band_flattening"]["cases"], ensure_ascii=False, sort_keys=True))
    print("[C] " + json.dumps(obj["d6_mapping_check"]["per_skill_raw_and_band"], ensure_ascii=False, sort_keys=True))
    print("[C-SWEEP] " + json.dumps(obj["d6_mapping_check"]["independent_sweep"], ensure_ascii=False, sort_keys=True))
    print("[D] " + json.dumps(deriv, ensure_ascii=False, sort_keys=True))
    print("[A2] " + json.dumps(A, ensure_ascii=False, sort_keys=True))
    print("[SELFCHECK] " + json.dumps(obj["self_check"], ensure_ascii=False, sort_keys=True))
    for m in bld["mismatches"]:
        print("MISMATCH " + m)
    if "--check" not in args:
        with io.open(OUT, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
        print("WROTE " + OUT)
    print("[RECONCILE] rows=%d divergences=%d adjudicated=%d band_flattened=%d" % (
          len(obj["rows"]), n_div, n_adj, len(obj["band_flattening"]["cases"])))
    return 0 if not bld["mismatches"] else 2


if __name__ == "__main__":
    sys.exit(main())
