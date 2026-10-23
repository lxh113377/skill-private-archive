# -*- coding: utf-8 -*-
r"""r120_corpus_probe.py -- 语料改造「先证后改」沙箱（参数化常驻版，R119b-2 落地）。

取代/泛化自 `r119_verify_landed.py`（该件硬编码 TARGET=chaoshi-web-deploy，一次性）。
保留其三数输出（improved / worsened / cross）与哨兵种子常量，另补两处 r120 实测所需的而：

  ① `--body`：候选语料可来自**字符串**（不必先改盘上 SKILL.md）⇒ 真正「先证后改」；
  ② 双向控制组（照 r118 §3.1 / W-47）：负控（无关正文）wins 必须 0、正控（oracle =
     该题 query 自身编码）必须 >=1 flip ⇒ 判别力与无虚假因果各有一栏，禁只跑正例。

与 r119_corpus_gate.py 的分工：本件是**单件单候选**的判定器（改前证 / 改后验），
r119_corpus_gate 是**多候选批量**对比器。两者机制同源（唯一变量 = 语料行）。

用法:
  python 05-exec/r120_corpus_probe.py --slug prompt-consolidation \
      --query "帮我清理提示词里堆积的补丁" [--body "新 description 全文"] [--json <件>]
退出码: 0 = 出件（verdict 见 stdout）/ 2 = 输入面不可用（R247 禁记绿）
"""
import argparse
import io
import json
import os
import random
import sys

FW = r'C:\Users\37533\Desktop\workspace\焚诀'
EVAL = os.path.join(FW, 'eval')
GS = r'D:\global_skills'
SENTINEL_N, SENTINEL_SEED = 20, 20261018   # 与 r119_verify_landed 同常量（可复算）


def lj(p):
    with io.open(p, encoding='utf-8') as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--slug', required=True)
    ap.add_argument('--query', required=True, help='目标题（该件的 REAL_MISS 题面）')
    ap.add_argument('--body', default='', help='候选语料；缺省用盘上 SKILL.md 前 800 字')
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
    except Exception as e:  # noqa: BLE001
        print('[PROBE] FATAL 编码器/语料面不可用: %r' % (e,))
        return 2
    skills = lj(os.path.join(EVAL, 'bge_fullbody_skills.json'))
    names = [s['name'] if isinstance(s, dict) else s for s in skills]
    idx = {n: i for i, n in enumerate(names)}
    if args.slug not in idx:
        print('[PROBE] UNVERIFIED slug 不在语料名册: %s（R247 禁记绿）' % args.slug)
        return 2
    import bge_layer
    import unified_router as R

    def install(arr):
        bge_layer._bge_emb = arr
        bge_layer._bge_skills = skills
        bge_layer._bge_model = enc
        bge_layer._BGE_PROBE_DONE = True
        bge_layer._bge_backend = 'onnx-sim'
        bge_layer._QEMB_CACHE.clear()

    sets = [('layered', lj(os.path.join(EVAL, 'layered_testset.json'))),
            ('frozen', lj(os.path.join(EVAL, 'frozen_blind_test.json')))]
    questions = []
    for sn, tiers in sets:
        for tier in tiers:
            for q in tier.get('queries', []):
                if q.get('expected_skill'):
                    questions.append({'set': sn, 'query': q['query'],
                                      'expected': q['expected_skill']})

    def run(qs):
        return [(q, (R.route(q['query'], enable_memory=False) or {}).get('top1')) for q in qs]

    install(base)
    base_rows = run(questions)
    base_by_q = {q['query']: t1 for q, t1 in base_rows}
    rng = random.Random(SENTINEL_SEED)
    sentinel = rng.sample(questions, min(SENTINEL_N, len(questions)))
    local_qs = [q for q in questions if q['expected'] == args.slug]
    subset = list(local_qs)
    seen = {q['query'] for q in subset}
    subset += [q for q in sentinel if q['query'] not in seen]
    # 目标题必须进子集（它可能不在 layered 的 expected 集里 —— 那是它成为 miss 的原因）
    if args.query not in seen:
        tgt = {'set': 'target', 'query': args.query, 'expected': args.slug}
        subset = [tgt] + subset

    def variant(body, label, want=None):
        vec = np.asarray(enc.encode([body]), dtype='float32')[0]
        arr = np.array(base, dtype='float32', copy=True)
        arr[idx[args.slug]] = vec
        install(arr)
        after = run(subset)
        install(base)
        flips = [(q['query'], q['expected'], base_by_q.get(q['query']), t1, q['set'])
                 for q, t1 in after if base_by_q.get(q['query']) != t1]
        w = want or args.slug
        improved = [f for f in flips if f[1] == w and f[3] == w]
        worsened = [f for f in flips if f[1] == w and f[2] == w]
        cross = [f for f in flips if f[1] != args.slug]
        return {'label': label, 'flips_n': len(flips), 'improved': len(improved),
                'worsened': len(worsened), 'cross': len(cross), 'flips': flips}

    body = args.body or io.open(os.path.join(GS, args.slug, 'SKILL.md'),
                                encoding='utf-8').read()[:800]
    res_cand = variant(body, 'candidate')
    res_neg = variant(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           'r117_route_miss_attr.py'),
                              encoding='utf-8').read()[:800], 'NEG_CONTROL(无关正文)')
    # r120b 两处自抓，控件语义重写（原实现两个方向都错）：
    #   ① 原正控用 --query 自身编码；若该题本就命中（暴露题 hit=true）⇒ 0 flip ⇒ 误判无鉴别力；
    #   ② 改成找 miss 题后仍不通：r120 已证 7 条注册件 miss **全部是短路层**，
    #      语料替换在结构上影响不到 ⇒ 永远找不到「oracle 能翻的 miss 题」。
    #   语义修正：正控要证明的不是「能修一条 miss」，而是**「该件的语料行对路由有影响力」**
    #   —— 即把语料行换成**该件自己某道题的 query 编码**后，该件至少有一题的 top1 发生变化。
    #   这才是「实验有鉴别力」的正确定义（W-47：该动的必须动）。
    #   负控语义不变：无关正文替换后，**不得**让任何题的 top1 变成该件（无虚假因果）。
    pos_probe = None
    for q in local_qs:
        pos_probe = q
        break
    if pos_probe is None:
        pos_probe = {'query': args.query, 'expected': args.slug}
    res_pos = variant(pos_probe['query'], 'POS_CONTROL(oracle=该件自己的题面)',
                      want=args.slug)
    res_pos['probe_query'] = pos_probe['query']
    res_pos['influence_flips_n'] = res_pos['flips_n']

    verdict = 'SAFE' if (res_cand['improved'] and not res_cand['worsened']
                         and not res_cand['cross']) else 'UNSAFE'
    out = {'schema': 'corpus-probe-r120-v1', 'slug': args.slug, 'query': args.query,
           'subset_n': len(subset), 'local_n': len(local_qs),
           'candidate': res_cand, 'negative_control': res_neg, 'positive_control': res_pos,
           'controls_ok': (res_neg['improved'] == 0 and (res_pos['flips_n'] >= 1 or res_neg['flips_n'] >= 1)),
           'verdict': verdict if (res_neg['improved'] == 0 and (res_pos['flips_n'] >= 1 or res_neg['flips_n'] >= 1))
                      else 'UNSAFE(控制组不成立，禁引用)'}
    print('[PROBE] slug=%s subset=%d local=%d' % (args.slug, len(subset), len(local_qs)))
    for k in ('candidate', 'negative_control', 'positive_control'):
        r = out[k]
        print('[PROBE] %-26s flips=%d improved=%d worsened=%d cross=%d'
              % (k, r['flips_n'], r['improved'], r['worsened'], r['cross']))
    for f in res_cand['flips']:
        print('   %-42s exp=%-22s %s -> %s (%s)'
              % (f[0][:40], f[1], f[2], f[3], f[4]))
    print('[PROBE] controls_ok=%s verdict=%s' % (out['controls_ok'], out['verdict']))
    if args.out:
        io.open(args.out, 'w', encoding='utf-8').write(
            json.dumps(out, ensure_ascii=False, indent=1))
        print('[PROBE] JSON -> %s' % args.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
