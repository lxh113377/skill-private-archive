# -*- coding: utf-8 -*-
r'''r302b builder — 需求4 证据化替换优先级表（只读输入，只写本目录新文件）。

存在理由：需求4 要「替换优先级 / 时间节点 / 验证标准 / 回滚预案」，此前优先级只有人写的主观序。
本件把三个可判面（版本态 / 上游五维 / 声明态）合成一张 49 行全序表，明写排序判据并附取值命令；
把这层回答不了的「同名 SKILL.md 内容是否变过」具名成前置缺口（盘上无吸收时基准 sha）。
写面：只写本目录新文件，不改仓内任何既有件；对共享记忆与技能根只读。
'''
import importlib.util, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(HERE))
SCAN_PATH = BASE + '/_repro/r301c/fresh_scan.json'
INJ_PATH = BASE + '/_repro/r299a/results/r299_inject_result.json'
R114_PATH = BASE + '/05-exec/r114_replacement_scan.py'
OUT_JSON = HERE + '/priority.json'
OUT_MD = HERE + '/report.md'
NL = chr(10)

STATE_RANK = {'BEHIND': 0, 'UNKNOWN': 1, 'CURRENT': 2, 'LOCAL_AHEAD': 3}
TIER_CUT = 19

CRITERIA = [
    {'id': 'C1-state-priority', 'only_fields': ['state'],
     'rule': '主分层只看 state：BEHIND > UNKNOWN > CURRENT > LOCAL_AHEAD（rank 0、1、2、3），分层先于分数。',
     'why': '同一输入两次跑必须同序；主观印象不可复算，故只留可判字段。'},
    {'id': 'C2-score-desc', 'only_fields': ['upstream_score_total'],
     'rule': '同一 state 层内按 upstream_score_total 降序。',
     'why': '取本体五维之和，禁自己算五维（复制口径即第二真相源）。'},
    {'id': 'C3-pushed-desc', 'only_fields': ['upstream_pushed_at'],
     'rule': '同层同分再按 upstream_pushed_at 降序（YYYY-MM-DD 按整数比较）。',
     'why': '同层同分时，整仓推送更近者更可能仍在变化。'},
    {'id': 'C4-slug-asc', 'only_fields': ['slug', 'repo'],
     'rule': '仍有并列按 slug 升序，末尾以 repo 升序兜底 ⇒ 全序唯一。',
     'why': '保证同一输入连跑两次排名完全一致（stable 判据）。'},
    {'id': 'C5-tier-cut', 'only_fields': ['state', 'upstream_score_total'],
     'rule': 'T1=BEHIND 且总分>=19；T2=BEHIND 且总分<19；T3=CURRENT 或 LOCAL_AHEAD；U=UNKNOWN（单列且写原因）。',
     'why': '19 为派发口径写死的阈值（非本件自选）；改阈值须重新裁定并留痕。'},
    {'id': 'C6-invalid-out', 'only_fields': ['kind'],
     'rule': '声明态 kind=invalid 的对不进 49 行表，单列 invalid_rows，走改声明或补 path 另一条路。',
     'why': '声明失效不等于有可核对的上游。'},
]

VALUE_CMDS = {
    'state_and_pushed': '逐行随行字段 rows[].state_cmd（版本态源件的取值命令，逐字保留）',
    'score5_and_total': 'python build_r302b.py --repo <repo>（本体五维缓存口径）',
    'stability_and_conservation': 'python check_r302b.py（末行固定判据行）',
}


def pnum(v):
    s = (v or '').replace('-', '')
    return int(s) if s.isdigit() else 0


def tier_of(state, total):
    if state == 'BEHIND':
        return 'T1' if total >= TIER_CUT else 'T2'
    if state == 'UNKNOWN':
        return 'U'
    return 'T3'


def rank_order(rows):
    return sorted(rows, key=lambda r: (STATE_RANK[r['state']],
                                       -int(r['upstream_score_total']),
                                       -pnum(r['upstream_pushed_at']),
                                       r['slug'], r.get('repo') or ''))


def load_r114():
    sp = importlib.util.spec_from_file_location('r302b_r114', R114_PATH)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


def schema_dump(scan, inj, cache, mod):
    print('schema.scan.top    =', sorted(scan.keys()))
    print('schema.scan.pair   =', sorted(scan['pairs'][0].keys()))
    print('schema.scan.sample =', sorted(scan['samples'][0].keys()))
    print('schema.inj.top     =', sorted(inj.keys()))
    print('schema.inj.row     =', sorted(inj['rows'][0].keys()))
    key0 = 'repo__' + mod.key_of(scan['pairs'][0]['repo'])
    print('schema.cache.entry =', sorted((cache.get(key0) or {}).keys()))


def build_rows():
    mod = load_r114()
    cache = mod.load_cache()
    scan = json.load(io.open(SCAN_PATH, encoding='utf-8'))
    rows = []
    for p in scan['pairs']:
        repo = p['repo']
        key = 'repo__' + mod.key_of(repo)
        ent = cache.get(key) or {}
        s5, tot, fc = mod.score5(ent, True, True)
        rows.append({'slug': p['slug'], 'repo': repo, 'state': p['state'],
                     'upstream_score5': {'fc': s5['fc'], 'eff': s5['eff'], 'compat': s5['compat'],
                                         'docs': s5['docs'], 'community': s5['community']},
                     'upstream_score_total': tot,
                     'upstream_pushed_at': p['upstream_pushed_at'],
                     'local_last_updated': p['local_last_updated'],
                     'local_version': p['local_version'],
                     'cache_pushed_at': ent.get('pushed_at'),
                     'cache_state': ent.get('state'),
                     'cache_tree_state': ent.get('tree_state'),
                     'cache_skill_md_n': ent.get('skill_md_n'),
                     'fc_caliber': fc,
                     'tier': tier_of(p['state'], tot),
                     'cache_key': key,
                     'score_cmd': 'python build_r302b.py --repo ' + repo,
                     'state_cmd': p['evidence_cmd']})
    order = rank_order(rows)
    for i, r in enumerate(order):
        r['rank'] = i + 1
    return rows, order


def query_repo(repo):
    mod = load_r114()
    cache = mod.load_cache()
    key = 'repo__' + mod.key_of(repo)
    ent = cache.get(key)
    s5, tot, fc = mod.score5(ent or {}, True, True)
    pack_has = False
    try:
        pk = json.load(io.open(mod.POOL_PACK, encoding='utf-8-sig'))
        pack_has = key in (pk.get('entries') or {})
    except Exception:
        pack_has = None
    print(json.dumps({'repo': repo, 'cache_key': key, 'found': ent is not None,
                      'loose_cache_file': os.path.isfile(os.path.join(mod.CACHE_DIR, key + '.json')),
                      'pack_has': pack_has, 'score5': s5, 'score_total': tot, 'fc_caliber': fc,
                      'pushed_at': (ent or {}).get('pushed_at'),
                      'license': (ent or {}).get('license')}, ensure_ascii=False, indent=1))
    return 0


def _count(vals):
    d = {}
    for v in vals:
        d[v] = d.get(v, 0) + 1
    return d


def md_table(header, data):
    out = ['| ' + ' | '.join(header) + ' |', '|' + '---|' * len(header)]
    for row in data:
        out.append('| ' + ' | '.join(str(x) for x in row) + ' |')
    return out


TH_HEAD = ['rank', 'slug', 'repo', 'state', 'total', 'fc', 'eff', 'compat', 'docs', 'community', 'pushed_at', 'local_updated']


def tier_table_rows(order, tier):
    out = []
    for r in order:
        if r['tier'] != tier:
            continue
        s5 = r['upstream_score5']
        out.append([r['rank'], r['slug'], r['repo'], r['state'], r['upstream_score_total'],
                    s5['fc'], s5['eff'], s5['compat'], s5['docs'], s5['community'],
                    r['upstream_pushed_at'], r['local_last_updated']])
    return out


def write_report(doc):
    order = sorted(doc['rows'], key=lambda r: r['rank'])
    L = []
    L.append('# r302b · 需求4 替换优先级（证据化序，49 行全序）')
    L.append('')
    L.append('本件只做一件事：把版本态、上游五维、声明态三个可判面合成一张可复算的替换序并明写判据。')
    L.append('本件不裁定值不值得换装（那是拍板人的裁定）；时间节点与验证标准只给「若要做」的建议形态。')
    L.append('')
    L.append('## 1. 排序判据（写死，可复算）')
    L.append('')
    for c in doc['criteria']:
        L.append('- **' + c['id'] + '** 规则：' + c['rule'] + ' ｜ 只看字段：' + ', '.join(c['only_fields']) + ' ｜ 理由：' + c['why'])
    L.append('')
    L.append('比较器（等价伪码；末尾以 repo 升序兜底 ⇒ 全序唯一）：')
    L.append('')
    L.append('```')
    L.append('state_rank = {BEHIND: 0, UNKNOWN: 1, CURRENT: 2, LOCAL_AHEAD: 3}')
    L.append('sort_key = (state_rank[state], -upstream_score_total, -as_int(upstream_pushed_at), slug, repo)')
    L.append('```')
    L.append('')
    L.append('口径要点：五维取本体缓存件（禁自己算五维）；19 分阈值由派发口径写死；分数相同才看推送日，推送日相同才看 slug。')
    L.append('')
    L.append('## 2. T1（BEHIND 且总分 >= 19）')
    L.append('')
    L += md_table(TH_HEAD, tier_table_rows(order, 'T1'))
    L.append('')
    L.append('## 3. T2（BEHIND 且总分 < 19）')
    L.append('')
    L += md_table(TH_HEAD, tier_table_rows(order, 'T2'))
    L.append('')
    L.append('## 4. U（state=UNKNOWN，单列）')
    L.append('')
    L.append('U 不并入 T3，也不静默丢弃；原因逐字如下（取自版本态源件的取值命令字段）。')
    L.append('')
    u_rows = [r for r in order if r['tier'] == 'U']
    L += md_table(['rank', 'slug', 'repo', 'state', 'total', 'pushed_at', 'local_updated'],
                  [[r['rank'], r['slug'], r['repo'], r['state'], r['upstream_score_total'], r['upstream_pushed_at'], r['local_last_updated']] for r in u_rows])
    L.append('')
    L.append('逐字原因：')
    L.append('')
    L.append('```')
    for r in u_rows:
        L.append('slug=' + r['slug'] + ' repo=' + r['repo'])
        L.append('reason=' + r['state_cmd'])
        L.append('cache_face=' + 'state=' + str(r['cache_state']) + ' tree=' + str(r['cache_tree_state']) + ' skill_md_n=' + str(r['cache_skill_md_n']))
    L.append('```')
    L.append('')
    L.append('## 5. T3（CURRENT 或 LOCAL_AHEAD）')
    L.append('')
    L += md_table(TH_HEAD, tier_table_rows(order, 'T3'))
    L.append('')
    L.append('## 6. 计数与守恒')
    L.append('')
    L.append('- 行数 pairs = ' + str(doc['tiers']['total']))
    L.append('- tiers：T1=' + str(doc['tiers']['T1']) + ' T2=' + str(doc['tiers']['T2']) + ' T3=' + str(doc['tiers']['T3']) + ' U=' + str(doc['tiers']['U']))
    L.append('- state 计数：' + json.dumps(doc['state_counts'], ensure_ascii=False, sort_keys=True))
    L.append('- 守恒：tier 计数之和 = ' + str(doc['conservation']['tier_sum']) + '；state 计数之和 = ' + str(doc['conservation']['state_sum']) + '；行数 = ' + str(doc['conservation']['rows_n']) + '；ok=' + str(doc['conservation']['ok']))
    L.append('- 声明失效（不进本表）：' + str(doc['invalid_rows_n']) + ' 条')
    L.append('- 抽样 sha：' + str(doc['samples_sha_n']) + ' 条')
    L.append('')
    L.append('## 7. 负向对照（两腿，实测）')
    L.append('')
    L.append('### 腿 A：防排序自相矛盾（分层优先于分数）')
    L.append('')
    L.append('```json')
    L.append(json.dumps(doc['negative_controls']['legA_tie_across_layers'], ensure_ascii=False, indent=1))
    L.append(json.dumps(doc['negative_controls']['legA_real_conflict'], ensure_ascii=False, indent=1))
    L.append(json.dumps(doc['negative_controls']['legA_unknown_above_t3'], ensure_ascii=False, indent=1))
    L.append('```')
    L.append('')
    L.append('### 腿 B：防静默丢行（守恒 + unknown 逐字）')
    L.append('')
    L.append('```json')
    L.append(json.dumps(doc['negative_controls']['legB_no_silent_drop'], ensure_ascii=False, indent=1))
    L.append('```')
    L.append('')
    L.append('## 8. 这一层回答不了什么（前置缺口，具名不掩盖）')
    L.append('')
    L.append('- 版本态比的是「本地件最后更新日」对「整个上游仓最后推送日」⇒ 它不回答「那个同名 SKILL.md 内容变了没有」。')
    L.append('- 要回答内容是否变，需要「本地吸收时该同名件的 sha」作基准；盘上没有这个基准 ⇒ 本表只能判版本面落后，不能判内容漂移。')
    L.append('- 12 对抽样里已有上游 sha：只能证明「上游那个文件当前是这个 sha」，不能证明「它变过」。')
    L.append('- 五维取自本体缓存快照：community 维含推送新鲜度，缓存生成早于最新推送的仓，分数可能偏低 ⇒ 分数是快照读数，不是实时值。')
    L.append('')
    L.append('## 9. 声明失效的对（单列，另行处理）')
    L.append('')
    L.append('这些对不满足「有可核对的上游」，故不进 49 行表；处理路径是改声明或补 path，不是换装。')
    L.append('')
    L += md_table(['slug', 'repo', 'declared_path', 'tree_skill_md_n', 'declared_matrix', 'next_route'],
                  [[r['slug'], r['repo'], r['declared_path'], r['tree_skill_md_n'], r['matrix_declared'], r['next_route']] for r in doc['invalid_rows']])
    L.append('')
    L.append('## 10. 时间节点与验证标准的建议（若要做；本件不代裁）')
    L.append('')
    L.append('前提：先补「吸收时基准 sha」，否则任何「内容变了」的结论都不可判（缺口已在第 8 节具名）。')
    L.append('')
    L.append('若要做，建议的时间节点形态（不是排期承诺）：')
    L.append('1) 先做 T1 抽样面的上游当前 sha 核对（12 对可直接对），通过后再补基准 sha；')
    L.append('2) 基准补齐后做同名件内容级比对，得到「真变化」集合；')
    L.append('3) 按比对结果分批换装，一批一验，批间留回退点；')
    L.append('4) T2 与 T3 只做巡检式核对；U 单独挂账直到能判。')
    L.append('')
    L.append('若要做，验证标准应是什么（可判、非主观）：')
    L.append('- 版本面：换装后本地标注版本 == 上游当前标注版本（限同名件）。')
    L.append('- 内容面：同名件内容哈希 == 上游当前哈希；没有基准时只能记当前哈希，不能判变化。')
    L.append('- 行为面：该件自带的判据命令仍绿。')
    L.append('- 系统面：镜像一致、噪声、进化 三门禁仍绿，注册表对账三类全 0。')
    L.append('')
    L.append('回滚预案应是什么（形态）：')
    L.append('- 换装前对受影响件做文件级快照；失败按批整体回滚。')
    L.append('- 单件级回滚覆盖不到拓扑改动时，必须用文件级快照而不是对象级。')
    L.append('')
    L.append('以上只是「若要做」的标准形态；值不值得换装由拍板人裁定。')
    L.append('')
    L.append('## 11. 抽样 sha（12）')
    L.append('')
    L += md_table(['slug', 'repo', 'path', 'sha'], [[s['slug'], s['repo'], s['path'], s['sha']] for s in doc['samples_sha']])
    L.append('')
    L.append('边界：这些 sha 是「上游同名件当前哈希」，不是「本地吸收时哈希」；没有吸收时基准就无法判定它是否变过。')
    L.append('')
    L.append('## 12. 取值命令')
    L.append('')
    L.append('```')
    L.append('python build_r302b.py                      # 重建 priority.json 与 report.md')
    L.append('python build_r302b.py --repo <repo>        # 单仓五维取值（本体缓存口径，含命中面）')
    L.append('python check_r302b.py                      # 守恒与稳定性，末行固定为 R302:PRIORITY 判据行')
    L.append('```')
    L.append('')
    L.append('逐行取值命令已写进 priority.json 的 rows[].score_cmd 与 rows[].state_cmd。')
    L.append('')
    with io.open(OUT_MD, 'w', encoding='utf-8', newline=chr(10)) as fh:
        fh.write(NL.join(L) + NL)
    print('report.md lines=%d' % len(L))


def build():
    mod = load_r114()
    cache = mod.load_cache()
    scan = json.load(io.open(SCAN_PATH, encoding='utf-8'))
    inj = json.load(io.open(INJ_PATH, encoding='utf-8'))
    schema_dump(scan, inj, cache, mod)
    rows, order = build_rows()

    state_counts = _count(r['state'] for r in rows)
    tier_counts = _count(r['tier'] for r in rows)
    t1 = tier_counts.get('T1', 0); t2 = tier_counts.get('T2', 0)
    t3 = tier_counts.get('T3', 0); uu = tier_counts.get('U', 0)

    syn = [{'slug': 'negctl-tie-behind', 'repo': 'negctl/tie-behind', 'state': 'BEHIND',
            'upstream_score_total': 15, 'upstream_pushed_at': '2026-01-01'},
           {'slug': 'negctl-tie-current', 'repo': 'negctl/tie-current', 'state': 'CURRENT',
            'upstream_score_total': 15, 'upstream_pushed_at': '2026-01-01'}]
    syn_order = rank_order(syn)
    syn_view = []
    for i, r in enumerate(syn_order):
        syn_view.append({'case': 'synthetic equal-score, differing state',
                         'state': r['state'], 'score': r['upstream_score_total'],
                         'tier': tier_of(r['state'], r['upstream_score_total']), 'rank': i + 1})
    syn_ok = syn_order[0]['state'] == 'BEHIND'

    behind_scores = sorted(set(r['upstream_score_total'] for r in rows if r['state'] == 'BEHIND'))
    current_scores = sorted(set(r['upstream_score_total'] for r in rows if r['state'] == 'CURRENT'))
    syn_note = ('数据面实测无同分对：BEHIND 总分取值 %s，CURRENT 总分取值 %s，交集为空 ⇒ '
                '同分跨层只能用合成输入对比较器做负控。' % (behind_scores, current_scores))

    t2_rows = [r for r in order if r['tier'] == 'T2']
    la_rows = [r for r in order if r['state'] == 'LOCAL_AHEAD']
    t2_low = t2_rows[0] if t2_rows else None
    la_high = max(la_rows, key=lambda r: r['upstream_score_total']) if la_rows else None
    conflict_ok = bool(t2_low and la_high and t2_low['rank'] < la_high['rank'])

    u_rows = [r for r in order if r['tier'] == 'U']
    t3_first_rank = min([r['rank'] for r in order if r['tier'] == 'T3'] or [0])
    u_ok = bool(u_rows and u_rows[0]['rank'] < t3_first_rank)

    cons_state = sum(state_counts.values()) == len(rows)
    cons_tier = (t1 + t2 + t3 + uu) == len(rows)

    unknown_view = [{'slug': r['slug'], 'repo': r['repo'], 'state': r['state'],
                     'score_total': r['upstream_score_total'], 'tier': r['tier'], 'rank': r['rank'],
                     'cache_face': 'state=' + str(r['cache_state']) + ' tree=' + str(r['cache_tree_state']) + ' skill_md_n=' + str(r['cache_skill_md_n']),
                     'reason_verbatim': r['state_cmd']} for r in order if r['state'] == 'UNKNOWN']

    inv_rows = []
    for r in inj['rows']:
        if r.get('kind') != 'invalid':
            continue
        inv_rows.append({'slug': r.get('slug'), 'repo': r.get('repo'),
                         'declared_path': r.get('declared_path'), 'kind': r.get('kind'),
                         'path_hit': r.get('path_hit'),
                         'slug_hits_n': len(r.get('slug_hits') or []),
                         'tree_skill_md_n': r.get('tree_skill_md_n'),
                         'row_verdict_before': r.get('row_verdict_before'),
                         'matrix_declared': r.get('matrix_declared'),
                         'next_route': '改声明（声明路径已失效）或补 path（声明面缺 path）'})
    inv_rows.sort(key=lambda x: (x['slug'] or '', x['repo'] or ''))

    samples_sha = []
    for s in scan['samples']:
        samples_sha.append({'slug': s['slug'], 'repo': s['repo'], 'path': s['path'],
                            'sha': s['sha'], 'sampled_state': s.get('sampled_state'),
                            'upstream_version': s.get('upstream_version')})
    samples_sha.sort(key=lambda x: (x['slug'], x['repo']))

    neg = {'legA_tie_across_layers': {
               'assert': 'score 相同（15）时 state=BEHIND 必须比 state=CURRENT 更靠前（分层优先于分数）',
               'input_verbatim': syn_view, 'pass': syn_ok, 'real_data_gap': syn_note},
           'legA_real_conflict': {
               'assert': '真实冲突：BEHIND 总分低者仍须排在 LOCAL_AHEAD 总分高者之前',
               'behind_row': ({'slug': t2_low['slug'], 'repo': t2_low['repo'], 'state': t2_low['state'],
                               'score': t2_low['upstream_score_total'], 'tier': t2_low['tier'], 'rank': t2_low['rank']} if t2_low else None),
               'local_ahead_row': ({'slug': la_high['slug'], 'repo': la_high['repo'], 'state': la_high['state'],
                                    'score': la_high['upstream_score_total'], 'tier': la_high['tier'], 'rank': la_high['rank']} if la_high else None),
               'pass': conflict_ok},
           'legA_unknown_above_t3': {
               'assert': 'U 单列且按 state 优先级排在 T3 之前',
               'unknown_rank': (u_rows[0]['rank'] if u_rows else None), 'first_t3_rank': t3_first_rank, 'pass': u_ok},
           'legB_no_silent_drop': {
               'assert': 'state 计数之和 == tiers 计数之和 == 行数（49）',
               'state_counts': state_counts, 'tier_counts': tier_counts, 'rows_n': len(rows),
               'pass': bool(cons_state and cons_tier), 'unknown_rows_verbatim': unknown_view}}

    doc = {'schema': 'r302b-priority-v1',
           'criteria': CRITERIA,
           'value_commands': VALUE_CMDS,
           'tiers': {'T1': t1, 'T2': t2, 'T3': t3, 'U': uu, 'total': len(rows)},
           'state_counts': state_counts,
           'rows': rows,
           'invalid_rows': inv_rows, 'invalid_rows_n': len(inv_rows),
           'samples_sha': samples_sha, 'samples_sha_n': len(samples_sha),
           'negative_controls': neg,
           'conservation': {'state_sum': sum(state_counts.values()),
                            'tier_sum': t1 + t2 + t3 + uu, 'rows_n': len(rows),
                            'ok': bool(cons_state and cons_tier)},
           'source_faces': {'version_face_rows': len(rows),
                            'declaration_pairs_n': inj.get('pairs_n'),
                            'declaration_kind_tally': inj.get('tally')}}

    with io.open(OUT_JSON, 'w', encoding='utf-8', newline=chr(10)) as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write(NL)
    json.load(io.open(OUT_JSON, encoding='utf-8'))
    write_report(doc)
    print('priority.json rows=%d T1=%d T2=%d T3=%d U=%d invalid=%d samples_sha=%d' % (
        len(rows), t1, t2, t3, uu, len(inv_rows), len(samples_sha)))
    print('negative controls: legA_tie=%s legA_conflict=%s legA_u=%s legB=%s' % (
        syn_ok, conflict_ok, u_ok, neg['legB_no_silent_drop']['pass']))
    return doc


def main(argv):
    if argv and argv[0] == '--repo':
        return query_repo(argv[1])
    build()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
