# -*- coding: utf-8 -*-
r"""r118_layer_attr.py -- 12 条 REAL_MISS 的**失败层归因** + 「换装是否可救」上界实验。

存在理由（需求 6 缺的地基，r118 一手）
  r117 把 291 条评分面的 20 条 miss 判成 8 STALE / 12 REAL_MISS，但**没有回答「这 12 条错在哪一层」**。
  分层诊断实测（本会话）发现 12 条里至少 4 条走的是 焚诀 eval/ 的 **direct_route 短路层**、
  1 条走 **tag 短路层**，还有 1 条是 direct_route 返回 'NONE' 的**负向直连**。
  这决定了替换方案的一条硬边界：
      **换 skill 本体（SKILL.md 语料）在结构上不可能影响走了短路的题** ——
      短路发生在召回层之前，语料换了也没人读它。
  ⇒ 「REAL_MISS 12 条」不能整块当成换装靶子。

判据（可复算，零网络）
  失败层三态（互斥，和 == REAL_MISS 条数）：
    DIRECT_SHORT   direct_route(query) 返回非 None 且 != 'NONE' ⇒ 走直连短路
    DIRECT_NONE    direct_route(query) 返回 'NONE' ⇒ 负向直连（判「无需 skill」）
    TAG_SHORT      tag_hits 非空且长度 == 1 ⇒ 走 tag 精确过滤短路
    BGE_RECALL     其余（走到召回/融合层，语料面参与打分）
  「换装可救」上界（oracle 变体，进程内不落盘）：
    把该件在 bge 语料里的那一行替换成 **query 自身的编码**（理论最优语料）
    ⇒ top1 翻转 = REACHABLE（换语料理论上能救）
    ⇒ 未翻转   = UNREACHABLE_BY_CORPUS（该条在更前面的层就被拦死）
  负控：把**另一件**（非期望件）的语料行替换成 query 编码 ⇒ 期望件不得因此变好
        （若也翻转，说明本实验无鉴别力）。

边界（写进产物）
  · oracle 用 query 自身编码是**上界**，现实中拿不到；结论只用于判「可不可达」，不作收益承诺。
  · DIRECT_NONE 属负向直连：它的错在 direct_map 的 NONE 规则，不在 SKILL.md。
  · 焚诀 eval/ 只读红线：本件只**调用** direct_route/normalize_query/tag_filter/route，
    不写任何 eval 文件。

用法：python 05-exec/r118_layer_attr.py --json 06-benchmark/layer_attr_r118_2026-10-18.json
      python 05-exec/r118_layer_attr.py --source <route_miss_attr_rNN.json>   # 指定归因件
      （缺省 = 06-benchmark 下最新一份 route_miss_attr_r*.json，来源写进产物 source 字段）

r119 修正（陈旧输入面）：本件原把归因件名硬编码成 r117 那一份，而 route_miss_attr 每轮重跑
  都会产出新件 ⇒ 失败层归因永远读 2026-10-18 的旧面。r119 现跑发现 miss 已由 20 降到 16、
  REAL_MISS 由 12 降到 8（pdf / python-debugpy / brainstorming 三条已被外部会话修掉），
  若继续读旧件会把「已修复的 4 条」算进靶子，并把失败层/oracle 结论建在过期分母上
  （X-24「分母静默变小仍全绿」同族）。现改为 --source 显式 + 缺省取最新件 + 来源显形。
退出码：0 完成 / 2 输入面不可用（R247，禁按 0 缺口记绿）
"""
import argparse
import io
import json
import os
import sys

FW = r'C:\Users\37533\Desktop\workspace\焚诀'
EVAL = os.path.join(FW, 'eval')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, '06-benchmark')


def newest_miss_attr():
    """06-benchmark 下最新一份 route_miss_attr_r*.json（按文件名排序取最大）。

    r119 立：原硬编码 r117 件名 = 陈旧输入面。取不到任何件时返回 None，
    由调用方走 UNVERIFIED(rc=2)，禁静默回落到不存在的旧件。
    """
    import glob
    cands = sorted(glob.glob(os.path.join(BENCH, 'route_miss_attr_r*.json')))
    return cands[-1] if cands else None


MISS_ATTR = os.path.join(BENCH, 'route_miss_attr_r117_2026-10-18.json')   # 仅作历史默认值提示


def load_json(p, encoding='utf-8'):
    with io.open(p, encoding=encoding) as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    ap.add_argument('--source', dest='source', default=None,
                    help='归因件路径（缺省 = 06-benchmark 下最新 route_miss_attr_r*.json）')
    args = ap.parse_args()

    src_path = args.source or newest_miss_attr()
    if not src_path or not os.path.exists(src_path):
        print('[LAYERATTR] UNVERIFIED 归因件缺失（--source 或默认 glob 均取不到）: %s'
              % (src_path or 'None'))
        return 2
    src = load_json(src_path)
    rows = [r for r in src.get('rows', []) if r.get('state') == 'REAL_MISS']
    if not rows:
        print('[LAYERATTR] UNVERIFIED REAL_MISS 面为空（禁按 0 记绿）')
        return 2

    sys.path.insert(0, EVAL)
    os.environ['FENJUE_ROUTE_TRACE'] = '0'
    try:
        import numpy as np
        import bge_onnx_engine
        encoder = bge_onnx_engine.BgeOnnxEncoder()
        base = np.asarray(np.load(os.path.join(EVAL, 'bge_fullbody_embeddings.npy'),
                                  mmap_mode='r'), dtype='float32')
    except Exception as e:
        print('[LAYERATTR] FATAL 数值/语料面不可用: %s' % e)
        return 2
    skills = load_json(os.path.join(EVAL, 'bge_fullbody_skills.json'))
    names = [s['name'] if isinstance(s, dict) else s for s in skills]
    idx = {n: i for i, n in enumerate(names)}

    import bge_layer
    import unified_router as R

    def install(arr):
        bge_layer._bge_emb = arr
        bge_layer._bge_skills = skills
        bge_layer._bge_model = encoder
        bge_layer._BGE_PROBE_DONE = True
        bge_layer._bge_backend = 'onnx-sim'
        bge_layer._QEMB_CACHE.clear()

    install(base)

    out_rows = []
    for r in rows:
        q, exp = r['query'], r['expected']
        direct = R.direct_route(q)
        norm = R.normalize_query(q)
        dom = R.classify_domain(norm) if R.classify_domain is not None else None
        tag = R.tag_filter(norm, dom) if R.tag_filter is not None else None
        if direct not in (None, 'NONE'):
            layer = 'DIRECT_SHORT'
        elif direct == 'NONE':
            layer = 'DIRECT_NONE'
        elif tag and len(tag) == 1:
            layer = 'TAG_SHORT'
        else:
            layer = 'BGE_RECALL'
        out_rows.append({'query': q, 'expected': exp, 'router_top1': r.get('router_top1'),
                         'direct_route': direct, 'tag_hits_n': len(tag) if tag else 0,
                         'tag_hits': (tag or [])[:6], 'layer': layer})

    # ---- oracle 上界：把期望件的语料行换成 query 自身编码 ----
    def top1_of(q):
        return (R.route(q, enable_memory=False) or {}).get('top1')

    for row in out_rows:
        q, exp = row['query'], row['expected']
        if exp not in idx:
            row['oracle'] = 'SKIP_NOT_IN_INDEX'
            continue
        qv = np.asarray(encoder.encode([q]), dtype='float32')[0]
        arr = np.array(base, dtype='float32', copy=True)
        # 对 DIRECT_SHORT/DIRECT_NONE 层，语料替换预期无效；仍测，用来证伪「短路层可救」的假设
        arr[idx[exp]] = qv
        install(arr)
        t1 = top1_of(q)
        row['oracle_top1'] = t1
        row['oracle'] = 'REACHABLE' if t1 == exp else 'UNREACHABLE_BY_CORPUS'
        install(base)  # 复位，禁污染下一条

    # ---- 负控：把**非期望件**的行换成 query 编码，期望件不应因此变好 ----
    neg = []
    for row in out_rows[:3]:
        q, exp = row['query'], row['expected']
        other = next((n for n in names if n != exp), None)
        if other is None or exp not in idx or other not in idx:
            continue
        qv = np.asarray(encoder.encode([q]), dtype='float32')[0]
        arr = np.array(base, dtype='float32', copy=True)
        arr[idx[other]] = qv
        install(arr)
        t1_before, t1_after = row['router_top1'], top1_of(q)
        row['neg_control'] = {'other': other, 'before': t1_before, 'after': t1_after,
                              'changed_to_expected': t1_after == exp}
        neg.append(row['neg_control'])
        install(base)

    from collections import Counter
    layer_c = Counter(r['layer'] for r in out_rows)
    oracle_c = Counter(r['oracle'] for r in out_rows)
    cross = {}
    for r in out_rows:
        cross.setdefault(r['layer'], Counter())[r['oracle']] += 1

    report = {
        'schema': 'layer-attr-r118-v1',
        'cmd': 'python 05-exec/r118_layer_attr.py --json <out>',
        'source': os.path.relpath(src_path, ROOT).replace('\\', '/'),
        'conservation': {'real_miss_n': len(rows), 'rows_n': len(out_rows),
                         'layers_sum_n': sum(layer_c.values()),
                         'ok': len(rows) == len(out_rows) == sum(layer_c.values())},
        'layers': dict(layer_c),
        'oracle': dict(oracle_c),
        'layer_x_oracle': {k: dict(v) for k, v in cross.items()},
        'rows': out_rows,
        'negative_control': {'probes': neg,
                             'has_discriminating_power': all(not n['changed_to_expected'] for n in neg)},
        'reading': {
            'DIRECT_SHORT': '走 direct_route 短路 ⇒ 改 SKILL.md 语料无效，失败层在 焚诀 eval/ direct_map（只读红线）',
            'DIRECT_NONE': 'direct_route 判「无需 skill」⇒ 负向直连规则问题，同样不在 SKILL.md',
            'TAG_SHORT': 'tag 精确过滤唯一命中 ⇒ 失败层在 skill_tags 派生件（禁手改，须重建）',
            'BGE_RECALL': '走到召回层，语料（SKILL.md 前 800 字）参与打分 ⇒ 换装理论上可影响',
        },
    }
    if args.out:
        io.open(args.out, 'w', encoding='utf-8').write(json.dumps(report, ensure_ascii=False, indent=1))

    print('[LAYERATTR] conservation=%s real_miss=%d' % (report['conservation']['ok'], len(rows)))
    print('[LAYERATTR] layers=%s' % report['layers'])
    print('[LAYERATTR] oracle=%s' % report['oracle'])
    for k, v in cross.items():
        print('   %-14s %s' % (k, dict(v)))
    print('[LAYERATTR] negative_control discriminating=%s' % report['negative_control']['has_discriminating_power'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
