# -*- coding: utf-8 -*-
'''r219c_sweep.py — 注入文案长度梯度扫描：找「两条目标都翻正且注入量最小」的那一档。

为什么要扫：r219b 实测同位置文案变短后 T1 从 rank=1 退到 rank=2（top1 仍是抢答件）
⇒ 翻正依赖注入字节数，而 A-memory-start/SKILL.md 属注入 5 件（现值 66162 已超硬顶 65536
约 +626，是老大名下的 C25 债）。不知道最小够用量就写长文案，等于无谓加重那笔债。
副作用同测：S1 须仍赢（记忆加载本该它答）、S2/S4 不得被抢（部署/知识库话术各有归属件）。
只读探针：不改盘。文案从 TEMP 的 sweep219.json 读（我在本轮已被引号互吃绊倒多次）。
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
SPEC = r'C:/Users/37533/AppData/Local/Temp/sweep219.json'
sys.path.insert(0, EVAL)
import numpy as np
import bge_onnx_engine

CHARS = 800
SLUG = 'A-memory-start'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec', default=SPEC,
                    help='换话术集（留出验证用同一套机制，不造第二份实现）')
    args = ap.parse_args()
    spec = json.load(io.open(args.spec, encoding='utf-8'))
    sk = json.loads(io.open(os.path.join(EVAL, 'bge_fullbody_skills.json'),
                             encoding='utf-8-sig').read())
    names = [str(s.get('name') if isinstance(s, dict) else s) for s in sk]
    idx = {n: i for i, n in enumerate(names)}
    emb0 = np.asarray(np.load(os.path.join(EVAL, 'bge_fullbody_embeddings.npy'),
                          mmap_mode='r'), dtype='float32')
    enc = bge_onnx_engine.BgeOnnxEncoder()
    orig = io.open(os.path.join(GS, SLUG, 'SKILL.md'), encoding='utf-8').read()
    an = spec['anchor_name']
    NL = chr(10)
    qc = {}
    for q in spec['queries']:
        qc[q['tag']] = np.asarray(enc.encode([q['text']]), dtype='float32')[0]
    rows = []
    for c in spec['cands']:
        line = c['line']
        if line:
            body = orig.replace(an, an + NL + line, 1)
        else:
            body = orig
        cost = len((line + NL).encode('utf-8')) if line else 0
        v = np.asarray(enc.encode([body[:CHARS]]), dtype='float32')[0]
        arr = np.array(emb0, dtype='float32', copy=True)
        arr[idx[SLUG]] = v
        for q in spec['queries']:
            qv = qc[q['tag']]
            order = list(np.argsort(-(arr @ qv)))
            top1 = names[order[0]]
            rows.append({'cand': c['id'], 'cost_bytes': cost, 'query': q['tag'],
                         'top1': top1, 'rank': order.index(idx[SLUG]) + 1,
                         'role': q.get('role', 'target'),
                         'won': top1 == SLUG})
    doc = {'schema': 'frontload-sweep-r219c-v1', 'corpus_chars': CHARS, 'rows': rows}
    io.open(os.path.join(ROOT, '06-benchmark', 'frontload_sweep_r219c.json'),
            'w', encoding='utf-8', newline=NL).write(
        json.dumps(doc, ensure_ascii=False, indent=1))
    by = {}
    for r in rows:
        by.setdefault(r['cand'], []).append(r)
    print('  %-14s %-6s %-12s %-12s %-10s %s' % (
        '候选', '注入B', '必赢命中', '原赢退化', '抢活数', '判定'))
    for cid, rs in by.items():
        g = {x['query']: x for x in rs}
        cost = rs[0]['cost_bytes']
        need = [x for x in rs if x['role'] in ('target', 'keep')]
        hit = sum(1 for x in need if x['top1'] == SLUG)
        lost = sum(1 for x in need if x['role'] == 'keep' and x['top1'] != SLUG)
        steal = sum(1 for x in rs if x['role'] == 'steal' and x['top1'] == SLUG)
        ok = (hit == len(need) and lost == 0 and steal == 0 and len(need) > 0)
        print('  %-14s %-6d %d/%-10d %d/%-10d %d/%-8d %s' % (
              cid[:14], cost, hit, len(need), lost, len([x for x in rs if x['role'] == 'keep']),
              steal, len([x for x in rs if x['role'] == 'steal']), '合格' if ok else ''))
    # 判定按 spec 里每条话术的 role（spec 驱动，换话术集不必改代码）：
    #   target=必须我方赢 / keep=原本就该我方赢，不得退化 / steal=必须不赢（抢别人活）
    roles = {q['tag']: q.get('role', 'target') for q in spec['queries']}
    good = []
    for cid, rs in by.items():
        g = {x['query']: x for x in rs}
        ok = True
        for tag, role in roles.items():
            if tag not in g:
                ok = False
                break
            r = g[tag]
            if role in ('target', 'keep'):
                if r['top1'] != SLUG:
                    ok = False
                    break
            elif role == 'steal' and r['top1'] == SLUG:
                ok = False
                break
        if ok:
            good.append((rs[0]['cost_bytes'], cid))
    if good:
        best = min(good)[0]
        print('[SWEEP:OK] 最小合格注入 = %d B（候选 %s）' % (best, [c for b, c in good if b == best]))
        return 0
    print('[SWEEP:NONE] 梯度内无合格档 ⇒ 需扩梯度或承认治不了')
    return 1


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())