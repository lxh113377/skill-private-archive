# -*- coding: utf-8 -*-
r'''r126_tag_closure.py -- 第 9 类失败层「Tag 闭包」常驻读数（r126 新立）。

存在理由（r126 一手）：
  r120 立了第 8 类失败层 = L0 域过滤（域失配 ⇒ 期望件结构上不在 BGE 搜索范围）。
  r126 在实测 7 条 REAL_MISS 时发现**同族但更靠前的一层**：`unified_router` 的
  `bge_recall` 里有一段「tag_hits 非空 ⇒ 只在 tag 命中的 skill 内搜索」，
  于是**tag 判错一个，期望件连 BGE 的边都碰不到** —— 比域过滤更早、影响面更窄但更致命。

  一手实例：`同步技能` → `tag_filter` 判给 `cross-platform-agent-sync`；
  而 BGE 原始相似度里 `A-skill-manager` 是**第 1 名（0.5619 vs 0.5468）**、
  经 `ensemble_rerank` 后差距拉大到 0.7371 vs 0.5945 —— 期望件在语义上明显更强，
  却因 tag 闭包**结构上不可达**。语料改造对这类条目**完全无效**（连 oracle 语料都进不了候选集）。

本件读三面（全部只读焚诀 eval，不写任何派生产物）：
  ① reachable_n   —— 期望件是否在「tag 命中 ∪ 域内」的可搜索面内
  ② raw_rank     —— 期望件在**无过滤**原始 BGE 相似度里的排名（1 = 语义上本该命中）
  ③ tag_trap     —— 被 tag 闭包挡住的条目（reachable=False 但 raw_rank 很小 ⇒ 纯 tag 误判）

用法: python 05-exec/r126_tag_closure.py --json 06-benchmark/tag_closure_r126_2026-10-20.json
退出码: 0 完成 / 2 输入面不可用（R247 禁按 0 记绿）
'''
import argparse
import io
import json
import os
import sys

FW = r'C:\Users\37533\Desktop\workspace\焚诀'
EVAL = os.path.join(FW, 'eval')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    ap.add_argument('--top', type=int, default=10, help='报告 tag_trap 时取前 N 条')
    args = ap.parse_args()

    sys.path.insert(0, EVAL)
    os.environ['FENJUE_ROUTE_TRACE'] = '0'
    try:
        import numpy as np
        import bge_onnx_engine
        import bge_layer
        import unified_router as R
    except Exception as e:  # noqa: BLE001
        print('[TAGCLOSE] FATAL 判据面不可用: %r' % (e,))
        return 2

    try:
        sk = json.loads(io.open(os.path.join(EVAL, 'bge_fullbody_skills.json'),
                                  encoding='utf-8').read())
        emb = np.asarray(np.load(os.path.join(EVAL, 'bge_fullbody_embeddings.npy'),
                                     mmap_mode='r'), dtype='float32')
        enc = bge_onnx_engine.BgeOnnxEncoder()
    except Exception as e:  # noqa: BLE001
        print('[TAGCLOSE] FATAL 语料面不可用: %r' % (e,))
        return 2

    names = [s.get('name') if isinstance(s, dict) else s for s in sk]
    idx = {n: i for i, n in enumerate(names)}
    bge_layer._bge_emb = emb
    bge_layer._bge_skills = sk
    bge_layer._bge_model = enc
    bge_layer._BGE_PROBE_DONE = True
    bge_layer._bge_backend = 'onnx-sim'
    bge_layer._QEMB_CACHE.clear()

    # 题面 = 焚诀权威评分面里带 expected_skill 的全部题
    sets = [('layered', os.path.join(EVAL, 'layered_testset.json')),
            ('frozen', os.path.join(EVAL, 'frozen_blind_test.json'))]
    questions = []
    for sn, p in sets:
        if not os.path.isfile(p):
            continue
        tiers = json.loads(io.open(p, encoding='utf-8').read())
        for tier in tiers:
            for q in tier.get('queries', []):
                if q.get('expected_skill'):
                    questions.append({'set': sn, 'query': q['query'],
                                      'expected': q['expected_skill']})
    if not questions:
        print('[TAGCLOSE] UNVERIFIED 题面为空')
        return 2

    rows = []
    for it in questions:
        exp = it['expected']
        ei = idx.get(exp)
        nq = R.normalize_query(it['query'])
        dom = R.classify_domain(nq)
        tags = R.tag_filter(nq, dom)
        # 可搜索面：tag 非空时 = tag 集合；否则 = 同域（或全量）
        if tags:
            reachable = exp in set(tags)
            gate = 'TAG'
        elif dom:
            reachable = (ei is not None and sk[ei].get('domain') == dom)
            gate = 'DOMAIN'
        else:
            reachable = (ei is not None)
            gate = 'OPEN'
        # 无过滤原始排名
        raw_rank = None
        raw_score = None
        if ei is not None:
            v = np.asarray(enc.encode([nq]), dtype='float32')[0]
            sims = emb @ v
            order = np.argsort(-sims)
            raw_rank = int(list(order).index(ei)) + 1
            raw_score = round(float(sims[ei]), 4)
        rows.append({'set': it['set'], 'query': it['query'], 'expected': exp,
                     'gate': gate, 'reachable': reachable,
                     'tag_hits': list(tags or []), 'domain': dom,
                     'raw_rank': raw_rank, 'raw_score': raw_score})

    closed = [r for r in rows if not r['reachable']]
    # tag_trap = 被 tag 闭包挡住，且原始 BGE 排名本该命中（<=5）
    traps = [r for r in closed if r['gate'] == 'TAG'
             and r['raw_rank'] is not None and r['raw_rank'] <= 5]
    doc = {'schema': 'tag-closure-r126-v1',
           'cmd': 'python 05-exec/r126_tag_closure.py --json <out>',
           'source': EVAL,
           'face': {'questions_n': len(rows),
                     'unreachable_n': len(closed),
                     'reachable_n': len(rows) - len(closed),
                     'tag_closed_n': len([r for r in closed if r['gate'] == 'TAG']),
                     'domain_closed_n': len([r for r in closed if r['gate'] == 'DOMAIN']),
                     'tag_trap_n': len(traps),
                     'reading': {
                         'tag_closed_n': '期望件不在 tag 命中集合内 ⇒ bge_recall 结构上搜不到它',
                         'tag_trap_n': '被 tag 闭包挡住、但原始 BGE 排名 <=5（纯 tag 误判，语料可救但进不了面）',
                         'domain_closed_n': '域失配（第 8 类失败层，r120 已立常驻面）',
                     }},
           'tag_trap': traps[:args.top],
           'unreachable': [r for r in closed if r['gate'] == 'TAG'][:args.top]}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    fa = doc['face']
    print('[TAGCLOSE] 题面=%d 可达=%d 不可达=%d（tag %d / domain %d） tag_trap=%d'
          % (fa['questions_n'], fa['reachable_n'], fa['unreachable_n'],
             fa['tag_closed_n'], fa['domain_closed_n'], fa['tag_trap_n']))
    for t in traps[:args.top]:
        print('  TRAP %-34s exp=%-24s raw_rank=%s' % (t['query'][:32], t['expected'], t['raw_rank']))
    if args.out:
        print('[TAGCLOSE] JSON -> %s' % args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())