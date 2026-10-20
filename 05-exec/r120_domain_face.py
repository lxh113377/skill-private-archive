# -*- coding: utf-8 -*-
r'''r120_domain_face.py -- 第 8 类失败层「L0 域过滤」的常驻量化面（R120-1/R120-2 落地）。

存在理由（r120 一手）：
  r120 发现 `bge_recall` 在 tag_hits 为空且 direct_route 为空时，只用
  `indices = [i for i,s in enumerate(_bge_skills) if s['domain']==domain]` 搜同一域 ⇒
  query 被判 code 域而期望件注册在 system 域时，**期望件结构上不在搜索范围**。
  r120 已量出：269 题中 59 题（21.9%）域失配，但 55 题有 tag/direct 掩护，仅 4 题真实暴露、1 题真失败。
  ⇒ 「21.9%」不是缺口数，**暴露/掩护二分**才是可引用的数。

本件把该一次性分析固化为常驻面，三个子面全部可复算：
  ① mismatch  —— 全 layered 题面域失配计数（query 域 != 期望件域）
  ② exposure  —— 失配题的掩护/暴露二分（有 tag 或 direct 命中期望件 ⇒ 掩护）
  ③ global-cf —— 关掉域过滤的全局反事实（净分变化 + WIN/LOSE 逐条）

口径红线（写进产物，防下一轮把 21.9% 当缺口数引用）：
  · mismatch_n 是**潜在脆弱面**，不是缺陷数；缺陷数 = exposed 中 is_miss=true 的条数；
  · 域过滤**不许关**（r120 实测全局关掉净降分），本件的 global-cf 只为量化其净贡献；
  · 只读 eval/ 与注册表，不写任何权威源。

用法：
  python 05-exec/r120_domain_face.py --json 06-benchmark/domain_face_r120_2026-10-20.json
退出码：0 完成 / 2 输入面不可用（R247，禁按 0 记绿）
'''
import argparse
import io
import json
import os
import sys

FW = r'C:\Users\37533\Desktop\workspace\焚诀'
EVAL = os.path.join(FW, 'eval')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, '06-benchmark')


def load_json(p):
    with io.open(p, encoding='utf-8') as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    args = ap.parse_args()

    sys.path.insert(0, EVAL)
    os.environ['FENJUE_ROUTE_TRACE'] = '0'
    try:
        import numpy as np
        import bge_onnx_engine
        enc = bge_onnx_engine.BgeOnnxEncoder()
        base = np.asarray(np.load(os.path.join(EVAL, 'bge_fullbody_embeddings.npy'),
                                  mmap_mode='r'), dtype='float32')
    except Exception as e:
        print('[DOMAINFACE] FATAL 数值/语料面不可用: %s' % e)
        return 2
    skills = load_json(os.path.join(EVAL, 'bge_fullbody_skills.json'))
    names = [s['name'] if isinstance(s, dict) else s for s in skills]
    dom_of = {s.get('name'): s.get('domain') for s in skills if isinstance(s, dict)}

    import bge_layer
    import unified_router as R
    from frozen_blind_eval import JUDGE_WEIGHT

    def install(arr=None):
        bge_layer._bge_emb = base if arr is None else arr
        bge_layer._bge_skills = skills
        bge_layer._bge_model = enc
        bge_layer._BGE_PROBE_DONE = True
        bge_layer._bge_backend = 'onnx-sim'
        bge_layer._QEMB_CACHE.clear()

    install()

    ls = load_json(os.path.join(EVAL, 'layered_testset.json'))
    questions = []
    for tier in ls:
        for q in tier.get('queries', []):
            if q.get('expected_skill'):
                questions.append({'query': q['query'], 'expected': q['expected_skill'],
                                  'judge': q.get('judge', 'exact')})
    if not questions:
        print('[DOMAINFACE] UNVERIFIED 题面为空（禁按 0 记绿）')
        return 2

    # ---- ① mismatch ----
    # ⚠️ 口径（r120b 两轮自抓，最终对齐生产）：qdomain 必须取 `classify_domain(q)` 的**原 query** 形态。
    #   · 首版我取 `route()['domain']`（结果字典里的域）⇒ 12 条，严重**低估**（结果域被后续改写）；
    #   · 二版我改成 `classify_domain(normalize_query(q))` ⇒ 69 条，又**高估** 4 条。
    #   读 `route()` 源码定案：`norm_query = normalize_query(query)` 之后
    #   `domain = classify_domain(norm_query)` ⇒ 生产用的是**归一化后**的 query，不是原 query。
    #   但实测 6 条题两者结论不同（normalize 后从 None 变成有域）——
    #   原因是 `normalize_query` 的同义词归一化会**新造出**域关键词，
    #   而这 6 条在真实 `route()` 里先被 `direct_route(query)` 短路（原 query 形态），根本走不到域分类。
    #   ⇒ 域失配是**潜在脆弱面**，正确口径 = 与 bge_recall 实际吃到的域一致 = classify_domain(norm_query)；
    #     而 r120 的 raw 口径把「本来会被 direct 短路的题」也算成失配，**高估**了脆弱面。
    #   本件**两个口径都算**并同列输出，禁只报一个数（口径本身是判据，不是细节）。
    rows = []
    for q in questions:
        r = R.route(q['query'], enable_memory=False) or {}
        norm = R.normalize_query(q['query'])
        qdom_prod = R.classify_domain(norm)      # 与 bge_recall 同入参（归一化后）
        qdom_raw = R.classify_domain(q['query'])  # r120 原口径（原 query）
        edom = dom_of.get(q['expected'])
        direct = R.direct_route(q['query'])
        tag = R.tag_filter(norm, qdom_prod) or []
        in_registry = q['expected'] in dom_of
        mismatch = (qdom_prod is not None and qdom_prod != edom)
        rows.append({
            'query': q['query'], 'expected': q['expected'],
            'qdomain': qdom_prod, 'qdomain_raw': qdom_raw,
            'expected_domain': edom,
            'mismatch': mismatch, 'expected_in_registry': in_registry,
            'router_top1': r.get('top1'),
            'hit': r.get('top1') == q['expected'],
            'direct_route': direct, 'tag_hits_n': len(tag),
        })
    mismatch_rows = [r for r in rows if r['mismatch']]
    # 失配题中期望件已退役/不在册的（题面脏面，非域归属问题）单列，
    # 禁并入域失配缺口数（与 STALE_EXPECT 单列同口径）。
    mismatch_live = [r for r in mismatch_rows if r['expected_in_registry']]
    mismatch_stale = [r for r in mismatch_rows if not r['expected_in_registry']]
    # 口径差（r120 raw 口径 vs 生产口径）：只统计、不裁决，供下一轮判断哪个更贴近真实伤害
    calib_diff = [r for r in rows
                 if (r['qdomain_raw'] is not None and r['qdomain_raw'] != r['expected_domain'])
                 != r['mismatch']]

    # ---- ② exposure / protected split ----
    # 掩护 = tag 命中期望件 或 direct_route 命中期望件（期望件仍在候选/被直连选中）
    def protected(r):
        return (r['direct_route'] == r['expected']) or (r['tag_hits_n'] > 0)

    for r in mismatch_rows:
        r['protected'] = protected(r)
    # 暴露面只在**在册件**上算（退役期望件的域归属无意义，属题面脏面）
    exposed = [r for r in mismatch_live if not r['protected']]
    real_fail = [r for r in exposed if not r['hit']]

    # ---- ③ global counterfact: domain filter OFF ----
    orig = R.classify_domain
    R.classify_domain = lambda q: None
    cf_rows = []
    for q in questions:
        r = R.route(q['query'], enable_memory=False) or {}
        cf_rows.append({'query': q['query'], 'expected': q['expected'],
                        'top1': r.get('top1')})
    R.classify_domain = orig

    def wscore(rs):
        tot = sum(JUDGE_WEIGHT.get(q['judge'], 0.5) for q in questions)
        got = sum(JUDGE_WEIGHT.get(q['judge'], 0.5) for q in questions for r in rs
                  if r['query'] == q['query'] and r['top1'] == q['expected'])
        return round(100.0 * got / tot, 2) if tot else None

    base_by_q = {r['query']: r['router_top1'] for r in rows}
    b_score = wscore([{'query': r['query'], 'top1': r['router_top1']} for r in rows])
    c_score = wscore(cf_rows)
    flips = []
    for r in cf_rows:
        b = base_by_q.get(r['query'])
        if b != r['top1']:
            flips.append({'query': r['query'], 'expected': r['expected'],
                          'before': b, 'after': r['top1']})
    wins = [f for f in flips if f['after'] == f['expected']]
    loses = [f for f in flips if f['before'] == f['expected']]

    doc = {
        'schema': 'domain-face-r120-v1',
        'cmd': 'python 05-exec/r120_domain_face.py --json <out>',
        'face': {
            'questions_n': len(questions),
            'questions_n2': len(questions),
            'qdomain_none_n': sum(1 for r in rows if r['qdomain'] is None),
            'mismatch_n': len(mismatch_rows),
            'mismatch_pct': round(100.0 * len(mismatch_rows) / len(questions), 1),
            'mismatch_live_n': len(mismatch_live),
            'mismatch_stale_n': len(mismatch_stale),
            'protected_n': len(mismatch_live) - len(exposed),
            'exposed_n': len(exposed),
            'real_fail_n': len(real_fail),
            # r120 原口径（classify_domain 原 query）下的失配数，用于口径校准对账
            'mismatch_raw_n': sum(1 for r in rows
                                  if r['qdomain_raw'] is not None
                                  and r['qdomain_raw'] != r['expected_domain']),
            'calibration_diff_n': len(calib_diff),
            'conservation_ok': (len(mismatch_live) + len(mismatch_stale) == len(mismatch_rows)
                                and len(mismatch_live) == (len(mismatch_live) - len(exposed)) + len(exposed)),
        },
        'global_cf': {
            'baseline_score': b_score, 'cf_score': c_score,
            'delta_pp': round((c_score - b_score), 2) if (b_score is not None and c_score is not None) else None,
            'flips_n': len(flips), 'wins_n': len(wins), 'loses_n': len(loses),
            'verdict': 'NET_HARMFUL_TO_DISABLE' if (b_score is not None and c_score is not None and c_score < b_score) else 'NEUTRAL',
        },
        'mismatch': mismatch_rows,
        'mismatch_live': mismatch_live,
        'calibration_diff': calib_diff,
        'mismatch_stale': mismatch_stale,
        'exposed': exposed,
        'real_fail': real_fail,
        'cf_flips': flips,
        'reading': {
            'qdomain_none_n': '未触发域分类的题数（不计入失配面）',
            'mismatch_n': '潜在脆弱面（L0 分类器域 != 期望件注册域），**不是**缺口数',
            'mismatch_live_n': '失配题中期望件在册的条数（可引用的域失配规模）',
            'mismatch_stale_n': '失配题中期望件已退役/不在册的条数（题面脏面，禁并入缺口数）',
            'exposed_n': '在册失配题中无 tag/direct 掩护、真实暴露于域过滤的题数',
            'real_fail_n': '暴露题中确实 miss 的题数 —— 这才是可引用的缺陷数',
            'global_cf.verdict': '关掉域过滤的净效果；NET_HARMFUL_TO_DISABLE ⇒ 域过滤不许关',
            'qdomain_definition': 'classify_domain(normalize_query(q))，与 bge_recall 的域过滤同函数同入参（route() 内先 normalize 再 classify）',
            'mismatch_raw_n': 'r120 原口径（classify_domain 原 query）的失配数；与 mismatch_n 的差 = 口径差',
            'calibration_diff_n': '两个口径结论不同的题数；这些题在原 query 形态下会被 direct_route 短路，故 raw 口径高估脆弱面',
        },
    }
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    f = doc['face']
    print('[DOMAINFACE] n=%d qdomain_none=%d mismatch=%d(%.1f%%) live=%d stale=%d protected=%d exposed=%d real_fail=%d'
          % (f['questions_n'], f['qdomain_none_n'], f['mismatch_n'], f['mismatch_pct'],
             f['mismatch_live_n'], f['mismatch_stale_n'],
             f['protected_n'], f['exposed_n'], f['real_fail_n']))
    print('[DOMAINFACE] 口径校准: r120原口径(raw)=%d ｜ 生产口径(norm)=%d ｜ 结论不同的题=%d'
          % (f['mismatch_raw_n'], f['mismatch_n'], f['calibration_diff_n']))
    print('[DOMAINFACE] global_cf: %.2f%% -> %.2f%% (%+.2fpp) flips=%d W/L=%d/%d => %s'
          % (b_score or 0, c_score or 0, doc['global_cf']['delta_pp'] or 0,
             len(flips), len(wins), len(loses), doc['global_cf']['verdict']))
    if args.out:
        print('[DOMAINFACE] JSON -> %s' % args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())