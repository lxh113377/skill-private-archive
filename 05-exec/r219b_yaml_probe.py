# -*- coding: utf-8 -*-
'''r219b YAML 合法注入位 + 反向副作用探针（只读，不改盘）。

V2（裸行插进 frontmatter）虽能翻正两条目标，但会让 frontmatter 结构非法（本仓有件解析它）
⇒ 本件测合法形态：新增 YAML 键 triggers_cn / 或在 description 句首前置。并测反向副作用：
注入后不得把本该由别的 skill 赢的话术（部署/图片/知识库/迁移）抢过来。expect_win=false 的行
若 top1 变成 A-memory-start，即为副作用回归（不是成绩）。
'''
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GS = 'D:/global_skills'
EVAL = r'C:/Users/37533/Desktop/workspace/焚诀/eval'
SPEC = r'C:/Users/37533/AppData/Local/Temp/probe_spec219b.json'
sys.path.insert(0, EVAL)
import numpy as np
import bge_onnx_engine

CHARS = 800


def main():
    spec = json.load(io.open(SPEC, encoding='utf-8'))
    skp = os.path.join(EVAL, 'bge_fullbody_skills.json')
    ep = os.path.join(EVAL, 'bge_fullbody_embeddings.npy')
    if not (os.path.isfile(skp) and os.path.isfile(ep)):
        print('[PROBE219B:UNVERIFIED] 面缺失')
        return 2
    sk = json.loads(io.open(skp, encoding='utf-8-sig').read())
    names = [str(s.get('name') if isinstance(s, dict) else s) for s in sk]
    idx = {n: i for i, n in enumerate(names)}
    emb0 = np.asarray(np.load(ep, mmap_mode='r'), dtype='float32')
    enc = bge_onnx_engine.BgeOnnxEncoder()
    slug = 'A-memory-start'
    orig = io.open(os.path.join(GS, slug, 'SKILL.md'), encoding='utf-8').read()
    an = spec['anchor_name']
    NL = chr(10)
    dl = 'description: '
    variants = [('V0 原样', orig)]
    variants.append(('V4 name后加合法键', orig.replace(an, an + NL + spec['line_key'], 1)))
    variants.append(('V5 同 V4 但更短', orig.replace(an, an + NL + spec['line_key2'], 1)))
    i = orig.find(dl)
    if i > 0:
        j = orig.find(NL, i)
        variants.append(('V6 description 句首前置',
                         orig[:j] + NL + spec['prepend_desc'] + orig[j:]))
    rows = []
    for tag, body in variants:
        cw = body[:CHARS]
        v = np.asarray(enc.encode([cw]), dtype='float32')[0]
        arr = np.array(emb0, dtype='float32', copy=True)
        arr[idx[slug]] = v
        for q in spec['queries']:
            qv = np.asarray(enc.encode([q['text']]), dtype='float32')[0]
            order = list(np.argsort(-(arr @ qv)))
            top1 = names[order[0]]
            rank = order.index(idx[slug]) + 1
            s_self = float(arr[idx[slug]] @ qv)
            riv = q['rival']
            s_riv = float(arr[idx[riv]] @ qv) if riv in idx else None
            win = top1 == slug
            bad = (q['expect_win'] is False and win)
            good = (q['expect_win'] and win)
            rows.append({'variant': tag, 'query': q['tag'], 'rival': riv,
                         'top1': top1, 'rank': rank,
                         'margin': (round(s_self - s_riv, 4) if s_riv is not None else None),
                         'good_flip': good, 'side_effect': bad,
                         'rival_rank': (order.index(idx[riv]) + 1) if riv in idx else None})
    doc = {'schema': 'frontload-probe-r219b-v1', 'corpus_chars': CHARS, 'rows': rows}
    io.open(os.path.join(ROOT, '06-benchmark', 'frontload_probe_r219b.json'),
            'w', encoding='utf-8', newline=NL).write(
        json.dumps(doc, ensure_ascii=False, indent=1))
    for r in rows:
        flag = 'GOOD' if r['good_flip'] else ('副作用!' if r['side_effect'] else '')
        print('  %-18s %-22s rank=%-3d top1=%-26s margin=%s %s' % (
              r['variant'], r['query'][:22], r['rank'], r['top1'][:26],
              ('%+.4f' % r['margin']) if r['margin'] is not None else '-', flag))
    se = [r for r in rows if r['side_effect']]
    gf = [r for r in rows if r['good_flip']]
    print('[PROBE219B] 翻正 %d 处；副作用 %d 处 %s' % (
          len(gf), len(se), sorted({(r['variant'], r['query']) for r in se}) or ''))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())