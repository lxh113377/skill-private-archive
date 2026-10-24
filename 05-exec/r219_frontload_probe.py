# -*- coding: utf-8 -*-
'''r219_frontload_probe.py — 按生产窗口口径测触发语注入位（r219，只读取证）。

为什么要另写：r135 的 trial() 编码的是整篇 body（其输出里 body_len=6921），而生产语料是
SKILL.md 的 text[:CORPUS_CHARS=800]（一手：焚诀/eval/build_indexes.py:61 定义、:239 切片）。
整篇编码下「末尾追加」margin 不动，测的其实是引擎截断，不是生产窗口 —— 所以 r135 的结论不能
拿来指导「该把触发语放哪」。本件严格按窗口切片编码，并同测副作用（注入不能把该件原本能
召回的其它话术挤掉）。全部文案从 probe_spec219.json 读，脚本内零长中文字面量（我在本轮
已被引号互吃绊倒多次，见 §74）。只读：不写任何受管根文件，改盘一律走 rule_editor。
'''
import argparse
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GS = 'D:/global_skills'
EVAL = r'C:/Users/37533/Desktop/workspace/焚诀/eval'
SPEC = r'C:/Users/37533/AppData/Local/Temp/probe_spec219.json'
sys.path.insert(0, EVAL)
import numpy as np


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--chars', type=int, default=800)
    ap.add_argument('--slug', default='A-memory-start')
    args = ap.parse_args(argv)
    spec = json.load(io.open(SPEC, encoding='utf-8'))
    import bge_onnx_engine
    # 语料件真名（r135:53 同源）；我第一次按印象写成 skills_registry.json，不存在
    skp = os.path.join(EVAL, 'bge_fullbody_skills.json')
    ep = os.path.join(EVAL, 'bge_fullbody_embeddings.npy')
    if not (os.path.isfile(skp) and os.path.isfile(ep)):
        print('[FRONTLOAD:UNVERIFIED] 语料或嵌入面缺失')
        return 2
    sk = json.loads(io.open(skp, encoding='utf-8-sig').read())
    names = [str(s.get('name') if isinstance(s, dict) else s) for s in sk]
    idx = {n: i for i, n in enumerate(names)}
    if args.slug not in idx:
        print('[FRONTLOAD:UNVERIFIED] 目标件不在语料')
        return 2
    emb0 = np.asarray(np.load(ep, mmap_mode='r'), dtype='float32')
    enc = bge_onnx_engine.BgeOnnxEncoder()
    fp = os.path.join(GS, args.slug, 'SKILL.md')
    orig = io.open(fp, encoding='utf-8').read()
    trig = spec['trig']
    ad = spec['anchor_desc']
    an = spec['anchor_name']
    NL = chr(10)
    variants = [('V0 原样', orig)]
    if ad in orig:
        variants.append(('V1 desc行后插', orig.replace(ad, ad + NL + '  ' + trig, 1)))
    if an in orig:
        variants.append(('V2 name行后插', orig.replace(an, an + NL + trig, 1)))
    variants.append(('V3 文件末尾追加', orig.rstrip() + NL + trig))
    rows = []
    qcaches = {}
    for tag, q in ((x['tag'], x) for x in spec['queries']):
        qcaches[tag] = np.asarray(enc.encode([q['text']]), dtype='float32')[0]
    for tag, body in variants:
        cw = body[:args.chars]
        v = np.asarray(enc.encode([cw]), dtype='float32')[0]
        arr = np.array(emb0, dtype='float32', copy=True)
        arr[idx[args.slug]] = v
        for x in spec['queries']:
            qv = qcaches[x['tag']]
            s_self = float(arr[idx[args.slug]] @ qv)
            riv = x['rival']
            s_riv = float(arr[idx[riv]] @ qv) if riv in idx else None
            order = list(np.argsort(-(arr @ qv)))
            rank = order.index(idx[args.slug]) + 1
            top1 = names[order[0]]
            rows.append({'variant': tag, 'query': x['tag'], 'rival': riv,
                         'win_len': len(cw), 'self_sim': round(s_self, 4),
                         'rival_sim': (round(s_riv, 4) if s_riv is not None else None),
                         'margin': (round(s_self - s_riv, 4) if s_riv is not None else None),
                         'rank': rank, 'top1': top1,
                         'flipped': top1 == args.slug})
    doc = {'schema': 'frontload-probe-r219-v1', 'slug': args.slug,
           'corpus_chars': args.chars,
           'encoding_input': 'window slice (production口径)',
           'rows': rows}
    op = os.path.join(ROOT, '06-benchmark', 'frontload_probe_r219.json')
    io.open(op, 'w', encoding='utf-8', newline=NL).write(
        json.dumps(doc, ensure_ascii=False, indent=1))
    for r in rows:
        print('  %-16s %-22s self=%.4f riv=%s margin=%s rank=%-4d top1=%-24s %s' % (
              r['variant'], r['query'][:22], r['self_sim'],
              r['rival_sim'],
              ('%+.4f' % r['margin']) if r['margin'] is not None else '-',
              r['rank'], r['top1'][:24], 'FLIP' if r['flipped'] else ''))
    print('[FRONTLOAD] 窗口=%d 字｜变体 %d｜话术 %d' % (args.chars, len(variants), len(spec['queries'])))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())