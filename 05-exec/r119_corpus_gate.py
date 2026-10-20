# -*- coding: utf-8 -*-
r"""r119_corpus_gate.py -- 语料区分度改造的「先证后改」沙箱（常驻判据）。

针对 r118 归因出的 BGE_RECALL 层 REACHABLE miss，在**不写受管根任何文件**的前提下，
进程内替换 bge_layer 的语料行（SKILL.md 前 800 字段落），跑同一条生产 route()，
逐候选量化 WIN / LOSE / neutral，证明「赢的比输的多」且 LOSE 可控。

与 r118_swap_sim.py 的分工：
  r118_swap_sim  = 换装（上游 SKILL.md）对生产路由的影响上界
  本件           = 语料改写（本地 triggers/description）对生产路由的影响上界
两者机制同源（唯一变量 = 语料行），但**动作不同**，不可互相替代。

控制组语义（照 r118 §3.1 自抓后的两栏口径）：
  负控（无关正文）: wins 必须为 0（无虚假因果）；LOSE 允许存在且是有力证据
  正控（oracle 语料 = query 自身编码）: 必须至少 1 flip（判别力成立）

用法:
  python 05-exec/r119_corpus_gate.py --candidates _temp/r119_candidates.json --json <件>
退出码: 0 出件 / 2 编码器或语料面不可用（禁记绿，R247）
"""
import io, json, os, sys, argparse

ROOT = r"C:\Users\37533\Desktop\workspace\skill焚诀\自建skill优化"
EVAL = r"C:\Users\37533\Desktop\workspace\焚诀\eval"
CORPUS_CHARS = 800
sys.path.insert(0, EVAL)
os.environ['FENJUE_ROUTE_TRACE'] = '0'



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    ap.add_argument('--candidates', required=True,
                    help='JSON: {slug: 候选语料文本}')
    args = ap.parse_args()
    CAND = json.load(io.open(args.candidates, encoding='utf-8'))
    if not isinstance(CAND, dict) or not CAND:
        print('[CORPUSGATE] UNVERIFIED 候选件为空或形态不对（R247 不判绿）')
        return 2
    import numpy as np
    import bge_onnx_engine
    enc = bge_onnx_engine.BgeOnnxEncoder()
    base = np.asarray(np.load(os.path.join(EVAL, 'bge_fullbody_embeddings.npy'), mmap_mode='r'), dtype='float32')
    skills = json.load(io.open(os.path.join(EVAL, 'bge_fullbody_skills.json'), encoding='utf-8'))
    names = [s['name'] if isinstance(s, dict) else s for s in skills]
    idx = {n: i for i, n in enumerate(names)}
    import bge_layer, unified_router as router
    from frozen_blind_eval import JUDGE_WEIGHT

    sets = [('layered', json.load(io.open(os.path.join(EVAL, 'layered_testset.json'), encoding='utf-8'))),
            ('frozen', json.load(io.open(os.path.join(EVAL, 'frozen_blind_test.json'), encoding='utf-8')))]
    questions = []
    for sn, tiers in sets:
        for t in tiers:
            for q in t.get('queries', []):
                if q.get('expected_skill'):
                    questions.append({'set': sn, 'tier': t.get('tier'), 'query': q['query'],
                                      'expected': q['expected_skill'], 'judge': q.get('judge', 'exact')})

    def install(arr):
        bge_layer._bge_emb = arr; bge_layer._bge_skills = skills
        bge_layer._bge_model = enc; bge_layer._BGE_PROBE_DONE = True
        bge_layer._bge_backend = 'onnx-sim'; bge_layer._QEMB_CACHE.clear()

    def run(qs):
        return [{'query': q['query'], 'expected': q['expected'], 'judge': q['judge'],
                 'top1': router.route(q['query'], enable_memory=False).get('top1')} for q in qs]

    def score(rows):
        w = sum(JUDGE_WEIGHT.get(r['judge'], 0.5) for r in rows)
        hit = sum(JUDGE_WEIGHT.get(r['judge'], 0.5) for r in rows if r['top1'] == r['expected'])
        return {'n': len(rows), 'w': round(w, 2), 'top1_pct': round(hit / w * 100, 2) if w else 0.0}

    install(base)
    base_rows = run(questions)
    base_by = {r['query']: r for r in base_rows}
    base_score = score(base_rows)
    print('[FULL] baseline n=%d w=%.2f top1=%.2f%%' % (base_score['n'], base_score['w'], base_score['top1_pct']))

    results = []
    for slug, body in CAND.items():
        if slug not in idx:
            print('[FULL] SKIP %s not in corpus' % slug); continue
        arr = np.array(base, dtype='float32', copy=True)
        v = np.asarray(enc.encode([body]), dtype='float32'); arr[idx[slug]] = v[0]
        install(arr)
        rows = run(questions)
        sc = score(rows)
        wins = [{'q': r['query'], 'expected': r['expected'], 'before': base_by[r['query']]['top1'], 'after': r['top1']}
                for r in rows if not base_by[r['query']]['top1'] == base_by[r['query']]['expected']
                and r['top1'] == r['expected']]
        loses = [{'q': r['query'], 'expected': r['expected'], 'before': base_by[r['query']]['top1'], 'after': r['top1']}
                 for r in rows if base_by[r['query']]['top1'] == base_by[r['query']]['expected']
                 and r['top1'] != r['expected']]
        neutral = [{'q': r['query'], 'expected': r['expected'], 'before': base_by[r['query']]['top1'], 'after': r['top1']}
                   for r in rows if base_by[r['query']]['top1'] != base_by[r['query']]['expected']
                   and r['top1'] != r['expected'] and base_by[r['query']]['top1'] != r['top1']]
        delta = round(sc['top1_pct'] - base_score['top1_pct'], 2)
        results.append({'slug': slug, 'score': sc, 'delta_pp': delta, 'wins_n': len(wins), 'loses_n': len(loses),
                        'neutral_n': len(neutral), 'wins': wins, 'loses': loses, 'neutral': neutral,
                        'net': len(wins) - len(loses)})
        print('[FULL] %-22s delta=%+.2fpp wins=%d loses=%d neutral=%d net=%+d' % (slug, delta, len(wins), len(loses), len(neutral), len(wins) - len(loses)))
        for f in wins: print('        WIN  %s  %s -> %s (exp=%s)' % (f['q'], f['before'], f['after'], f['expected']))
        for f in loses: print('        LOSE %s  %s -> %s (exp=%s)' % (f['q'], f['before'], f['after'], f['expected']))

    install(base)
    out = {'schema': 'fullface-probe-r119-v1', 'baseline': base_score, 'results': results,
           'summary': {'wins_n': sum(r['wins_n'] for r in results), 'loses_n': sum(r['loses_n'] for r in results),
                       'net': sum(r['net'] for r in results)}}
    if args.out:
        io.open(args.out, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))
        print('[FULL] JSON -> %s' % args.out)
    print('[FULL] SUMMARY wins=%d loses=%d net=%+d' % (out['summary']['wins_n'], out['summary']['loses_n'], out['summary']['net']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
