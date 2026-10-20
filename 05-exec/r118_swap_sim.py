# -*- coding: utf-8 -*-
r"""r118_swap_sim.py -- 换装候选对生产路由的离线 A/B 沙箱（只读；零写入权威源）。

存在理由（需求 6 缺的那块地基）
  需求 6 要求「替换完成后验证任务完成质量提升幅度不低于 30%」。历轮（r113 候选面 /
  r114 评分矩阵 / r115 口径修正 / r117 miss 归因）**没有任何一件回答过**：
  「把本地该件的语料换成上游那份，生产路由会变好还是变坏」。于是所有替换只能靠人读，
  提升幅度既不可预测也不可归因（r117 报告 §12 自述「本轮把分母分清，未改路由」）。
  本件把该问题变成可复算实验。

口径（不另造尺，全部复用仓内既有实现）
  被测对象 = 焚诀 eval/unified_router.py::route()  —— 生产路由本体，不是近似函数
  语料面   = eval/bge_fullbody_embeddings.npy (182,512) —— 生产正在用的那一份
  编码器   = eval/bge_onnx_engine.BgeOnnxEncoder    —— 与 build_indexes.encode_bge 同后端
  题面     = eval/layered_testset.json + eval/frozen_blind_test.json
  计分     = eval/frozen_blind_eval.py 的 JUDGE_WEIGHT
  做法     = 进程内替换 bge_layer 模块全局 _bge_emb 的**一行**再跑同一条 route()；
            唯一变量 = 该件 SKILL.md 前 800 字符（CORPUS_CHARS 同源常量）。

受影响的题子集（显式声明，禁偷换分母）
  对每个变体 slug，只重跑：| 期望 == slug | 基线 top1 == slug | 固定哨兵 20 条 |
  基线在同一子集上重算 ⇒ 变体 delta 与基线是**同一分母**（不是拿子集比 291 全量）。
  哨兵 20 条 = 固定种子抽样的「与被换件无关的题」，用于发现跨件连带效应。

三态结论（W-47 双向证据）
  负控 = 用故意无关的正文替换同一行；若哨兵与本地题**一条都不 flip** ⇒ 本实验无鉴别力，
  整份结论作废（不是「大家都不变所以很安全」）。

用法
  python 05-exec/r118_swap_sim.py --json 06-benchmark/swap_sim_r118_2026-10-18.json
  python 05-exec/r118_swap_sim.py --only-slug pdf        # 单件调试
退出码：0 = 有鉴别力且完成 / 2 = BGE 后端或输入面不可用（R247，禁按 0 提升记绿）
"""
import argparse
import base64
import io
import json
import os
import random
import sys

FW = r'C:\Users\37533\Desktop\workspace\焚诀'
EVAL = os.path.join(FW, 'eval')
GS = r'D:\global_skills'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, '06-benchmark')
EVID = os.path.join(BENCH, 'upstream_evidence')

JUDGE_WEIGHT = {'exact': 1.0, 'usable-suboptimal': 0.75, 'wrong': 0.5, 'blindspot': 0.4}
CORPUS_CHARS = 800
SENTINEL_N = 20
SENTINEL_SEED = 20261018


def load_json(path, encoding='utf-8'):
    with io.open(path, encoding=encoding) as f:
        return json.load(f)


def load_evidence():
    """上游证据件 -> {slug: [cand, ...]}；cand 含 body(SKILL.md 前 800 字) 与来源元数据。"""
    out = {}
    if not os.path.isdir(EVID):
        return out
    for name in sorted(os.listdir(EVID)):
        if not name.endswith('.json'):
            continue
        try:
            d = load_json(os.path.join(EVID, name))
        except Exception:
            continue
        if not d.get('ok') or not d.get('content_b64'):
            continue
        try:
            raw = base64.b64decode(d['content_b64']).decode('utf-8', 'replace')
        except Exception:
            continue
        out.setdefault(d['slug'], []).append({
            'repo': d.get('repo'), 'path': d.get('path'), 'bytes': d.get('bytes'),
            'last_commit_date': d.get('last_commit_date'), 'sha256': d.get('sha256'),
            'body': raw[:CORPUS_CHARS], 'evidence': name,
        })
    return out


def load_local_body(slug):
    p = os.path.join(GS, slug, 'SKILL.md')
    if not os.path.exists(p):
        return None
    return io.open(p, encoding='utf-8').read()[:CORPUS_CHARS]


def install_index(bge_layer, skills, arr, encoder):
    bge_layer._bge_emb = arr
    bge_layer._bge_skills = skills
    bge_layer._bge_model = encoder
    bge_layer._BGE_PROBE_DONE = True
    bge_layer._bge_backend = 'onnx-sim'
    bge_layer._QEMB_CACHE.clear()


def score(rows):
    n = len(rows)
    if not n:
        return {'n': 0, 'hits': 0, 'top1_pct': None, 'weighted_pct': None}
    hits = sum(1 for r in rows if r['hit'])
    wsum = sum(r['w'] for r in rows)
    wgot = sum(r['w'] for r in rows if r['hit'])
    return {'n': n, 'hits': hits,
            'top1_pct': round(100.0 * hits / n, 2),
            'weighted_pct': round(100.0 * wgot / wsum, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    ap.add_argument('--only-slug', default='')
    ap.add_argument('--skip-baseline-full', action='store_true')
    args = ap.parse_args()

    sys.path.insert(0, EVAL)
    os.environ['FENJUE_ROUTE_TRACE'] = '0'
    try:
        import numpy as np
        import bge_onnx_engine
        encoder = bge_onnx_engine.BgeOnnxEncoder()
    except Exception as e:
        print('[SWAPSIM] FATAL 编码器/数值栈不可用: %s' % e)
        return 2
    try:
        base = np.asarray(np.load(os.path.join(EVAL, 'bge_fullbody_embeddings.npy'),
                                  mmap_mode='r'), dtype='float32')
    except Exception as e:
        print('[SWAPSIM] FATAL 语料面不可用: %s' % e)
        return 2
    skills = load_json(os.path.join(EVAL, 'bge_fullbody_skills.json'))
    names = [s['name'] if isinstance(s, dict) else s for s in skills]
    idx = {n: i for i, n in enumerate(names)}
    if len(idx) != base.shape[0]:
        print('[SWAPSIM] FATAL 语料面行数与 skill 名单不一致 %d != %d' % (base.shape[0], len(idx)))
        return 2

    evid = load_evidence()
    printable = [s for s in sorted(evid) if s in idx and load_local_body(s)]
    if args.only_slug:
        printable = [s for s in printable if s == args.only_slug]
    if not printable:
        print('[SWAPSIM] UNVERIFIED 无可替换面（证据件 0 或 slug 不在名册内）')
        return 2

    import bge_layer
    import unified_router as router

    # ---- 题面装载 ----
    sets = [('layered', load_json(os.path.join(EVAL, 'layered_testset.json'))),
            ('frozen', load_json(os.path.join(EVAL, 'frozen_blind_test.json')))]
    questions = []
    for set_name, tiers in sets:
        for tier in tiers:
            for q in tier.get('queries', []):
                if q.get('expected_skill'):
                    questions.append({'set': set_name, 'tier': tier.get('tier'),
                                      'query': q['query'], 'expected': q['expected_skill'],
                                      'judge': q.get('judge', 'exact')})
    for q in questions:
        q['w'] = JUDGE_WEIGHT.get(q['judge'], 0.5)

    def run(qs):
        rows = []
        for q in qs:
            r = router.route(q['query'], enable_memory=False)
            rows.append({**q, 'top1': r.get('top1'), 'hit': r.get('top1') == q['expected']})
        return rows

    # ---- 基线（全量面，用于与仓内权威读数对账）----
    install_index(bge_layer, skills, base, encoder)
    base_rows = run(questions)
    base_by_q = {r['query']: r for r in base_rows}
    full_base = score(base_rows)

    rng = random.Random(SENTINEL_SEED)
    sentinel = [q for q in rng.sample(questions, min(SENTINEL_N, len(questions)))]

    report = {
        'schema': 'swap-sim-r118-v1',
        'cmd': 'python 05-exec/r118_swap_sim.py --json <out>',
        'face': {
            'index_rows': len(names),
            'evidence_slugs': len(evid),
            'substitutable_slugs': len(printable),
            'questions_n': len(questions),
            'corpus_chars': CORPUS_CHARS,
            'sentinel_n': len(sentinel), 'sentinel_seed': SENTINEL_SEED,
        },
        'substitutable': sorted(printable),
        'baseline_full_face': full_base,
        'ruler': {'route': 'eval/unified_router.py::route(enable_memory=False)',
                  'judge_weights': JUDGE_WEIGHT,
                  'subset_rule': 'expected==slug OR baseline_top1==slug OR sentinel'},
    }

    def variant_run(label, slug, body, kind, repo=None, meta=None):
        arr = np.array(base, dtype='float32', copy=True)
        vec = np.asarray(encoder.encode([body]), dtype='float32')
        arr[idx[slug]] = vec[0]
        install_index(bge_layer, skills, arr, encoder)
        subset_qs = [q for q in questions
                     if q['expected'] == slug or base_by_q[q['query']]['top1'] == slug]
        seen = {q['query'] for q in subset_qs}
        subset_qs += [q for q in sentinel if q['query'] not in seen]
        rows = run(subset_qs)
        before = score([base_by_q[r['query']] for r in rows])
        after = score(rows)
        flips = [{'q': r['query'], 'expected': r['expected'],
                  'before': base_by_q[r['query']]['top1'], 'after': r['top1'],
                  'set': r['set']} for r in rows
                 if base_by_q[r['query']]['hit'] != r['hit']]
        local_q = [r for r in rows if r['expected'] == slug]
        return {
            'label': label, 'slug': slug, 'repo': repo, 'kind': kind,
            'subset_n': len(rows), 'local_n': len(local_q),
            'before': before, 'after': after,
            'delta_local_pp': round(score(local_q)['top1_pct'] - score(
                [base_by_q[r['query']] for r in local_q])['top1_pct'], 2) if local_q else None,
            'delta_subset_pp': round(after['top1_pct'] - before['top1_pct'], 2),
            'flips_n': len(flips),
            'flips_local': [f for f in flips if f['expected'] == slug][:10],
            'flips_cross': [f for f in flips if f['expected'] != slug][:10],
        }

    results = []
    if not args.skip_baseline_full:
        # 负控（应当「不变」）：用无关正文替换第一个可替换件的那一行。
        # ⚠️ r118 自抓：负控 0 flip 是**通过**（证明没有虚假因果），不是「无鉴别力」。
        #    本脚本第一版把它写成「无鉴别力」并据此试图作废整份结论 —— 那是把
        #    「不该动的没动」误读成「测不出动」。判别力另由**正控**承担（见下）。
        neg_slug = printable[0]
        neg_body = io.open(os.path.join(ROOT, '05-exec', 'r117_route_miss_attr.py'),
                           encoding='utf-8').read()[:CORPUS_CHARS]
        results.append(variant_run('NEG_CONTROL(无关正文)', neg_slug, neg_body, 'negative_control'))
        # 正控（应当「变」）：取 layer_attr 判为 REACHABLE 的第一件，把它的语料行
        # 替换成**该题 query 自身的编码**（oracle 上界）。这才是判别力证据。
        # r119：原硬编码 layer_attr_r118_2026-10-18.json —— 该件的正控件是 python-debugpy，
        # 而 r119 现跑归因显示 python-debugpy 已被外部会话修好（REAL_MISS 12→8），
        # 继续拿旧件选正控 ⇒ 正控目标已不是 miss，实测 flips=0、整份实验被判「无鉴别力」。
        # 现改为取**最新一份** layer_attr_r*.json（与 r118_layer_attr.py 的 --source 缺省同源）。
        import glob as _glob
        la_cands = sorted(_glob.glob(os.path.join(BENCH, 'layer_attr_r*.json')))
        la = la_cands[-1] if la_cands else None
        pos_slug = None
        pos_query = None
        if la and os.path.exists(la):
            try:
                lr = load_json(la)
                for rr in lr.get('rows', []):
                    if (rr.get('oracle') == 'REACHABLE' and rr['expected'] in idx
                            and rr.get('query')):
                        pos_slug = rr['expected']
                        pos_query = rr['query']
                        break
            except Exception:
                pos_slug = None
        if pos_slug and pos_query:
            results.append(variant_run('POS_CONTROL(oracle 语料)', pos_slug,
                                       pos_query, 'positive_control'))

    for slug in printable:
        for cand in evid[slug]:
            results.append(variant_run('%s<-%s' % (slug, cand['repo']), slug, cand['body'],
                                       'swap_one', repo=cand['repo'],
                                       meta={'upstream_bytes': cand['bytes'],
                                             'upstream_date': cand['last_commit_date'],
                                             'evidence': cand['evidence'],
                                             'path': cand['path']}))
            for k, v in (results[-1].get('meta') or {}).items():
                results[-1][k] = v
            results[-1].pop('meta', None)

    ok = [r for r in results if r['kind'] == 'swap_one']
    neg = [r for r in results if r['kind'] == 'negative_control']
    pos = [r for r in results if r['kind'] == 'positive_control']
    report['variants'] = results
    report['summary'] = {
        'variants_n': len(ok),
        'local_improved_n': sum(1 for r in ok if (r['delta_local_pp'] or 0) > 0),
        'local_degraded_n': sum(1 for r in ok if (r['delta_local_pp'] or 0) < 0),
        'subnet_changed_n': sum(1 for r in ok if r['flips_n'] > 0),
        'cross_flips_n': sum(len(r['flips_cross']) for r in ok),
        'negative_control': {'slug': neg[0]['slug'] if neg else None,
                             'flips_n': neg[0]['flips_n'] if neg else None,
                             'pass': bool(neg and neg[0]['flips_n'] == 0)},
        'positive_control': {'slug': pos[0]['slug'] if pos else None,
                             'flips_n': pos[0]['flips_n'] if pos else None,
                             'pass': bool(pos and pos[0]['flips_n'] > 0)},
        'discriminating_power': bool(pos and pos[0]['flips_n'] > 0),
    }
    if args.out:
        io.open(args.out, 'w', encoding='utf-8').write(
            json.dumps(report, ensure_ascii=False, indent=1))
    s = report['summary']
    print('[SWAPSIM] face: %s' % report['face'])
    print('[SWAPSIM] baseline full face: %s' % full_base)
    print('[SWAPSIM] variants=%d local_improved=%d local_degraded=%d subnet_changed=%d cross_flips=%d'
          % (s['variants_n'], s['local_improved_n'], s['local_degraded_n'],
             s['subnet_changed_n'], s['cross_flips_n']))
    print('[SWAPSIM] neg_control(slug=%s) flips=%s pass=%s | pos_control(slug=%s) flips=%s pass=%s'
          % (s['negative_control']['slug'], s['negative_control']['flips_n'], s['negative_control']['pass'],
             s['positive_control']['slug'], s['positive_control']['flips_n'], s['positive_control']['pass']))
    for r in ok[:12]:
        print('   %-46s local %+6s pp  subset %+6s pp  flips=%d'
              % (r['label'][:46], r['delta_local_pp'], r['delta_subset_pp'], r['flips_n']))
    if not s['discriminating_power']:
        print('[SWAPSIM] WARNING 正控未翻转 ⇒ 本实验无鉴别力，结论不得引用（负控 0 flip 属通过）')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
