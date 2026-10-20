
# -*- coding: utf-8 -*-
r'''r119_cand_sandbox.py -- chaoshi-web-deploy 描述面候选的离线沙箱预验（只读）。

r119 改造 1 的前置实验：r118 已证 47 个上游换装变体对生产路由影响 0，
oracle 上界也只有 1 条（chaoshi-web-deploy）可被语料翻转。在动受管根之前，
先在沙箱里问：**「往返鉴别词」这条改法本身能不能把那一条翻过来**？
若沙箱都翻不动，就不该动 SKILL.md（避免把「改描述」当成无证据的信仰）。

做法与 r118_swap_sim 同源：进程内替换 bge_layer 的该件语料行，跑同一条 route()。
"""
'''
import io
import os
import sys

FW = r'C:\Users\37533\Desktop\workspace\焚诀'
EVAL = os.path.join(FW, 'eval')
GS = r'D:\global_skills'
HERE = os.path.dirname(os.path.abspath(__file__))

TARGET = 'chaoshi-web-deploy'
QUERY = 'cloudbase 云函数部署后订单不显示'
CHARS = 800

CANDIDATES = {
    'A_local_now': None,   # 现文（从盘上取前 800 字）
    'B_add_deploy_words': '超市web部署唯一权威源。触发词：超市部署、chaoshi deploy、部署超市、wrangler pages deploy、gh pages 推送、D1 迁移、部署 Cloudflare、Cloudflare Pages、Pages Functions、D1 数据库、云函数部署、部署后数据不显示、订单不显示、页面 404、GitHub Pages 双前端。任何 wrangler pages deploy / gh pages 推送 / d1 execute 前必须先加载本 skill 获取对应模式 checklist，禁止凭记忆裸跑。覆盖两种部署目标：①Cloudflare Pages（管理后台+API，supermarket-web.pages.dev）②GitHub Pages（微信顾客端，lxh113377.github.io）。',
    'C_short_dense': '超市web部署排障权威源。cloudbase 云函数部署后订单不显示、部署后数据不显示、wrangler pages deploy、gh pages 推送、d1 execute、Cloudflare Pages Functions + D1、GitHub Pages 双前端、部署 checklist、部署故障排查。',
    'D_only_query_echo': 'cloudbase 云函数部署后订单不显示',
}


def load_json(p):
    with io.open(p, encoding='utf-8') as f:
        return json.load(f)


def main():
    sys.path.insert(0, EVAL)
    os.environ['FENJUE_ROUTE_TRACE'] = '0'
    import numpy as np
    import bge_onnx_engine
    enc = bge_onnx_engine.BgeOnnxEncoder()
    base = np.asarray(np.load(os.path.join(EVAL, 'bge_fullbody_embeddings.npy'),
                              mmap_mode='r'), dtype='float32')
    skills = load_json(os.path.join(EVAL, 'bge_fullbody_skills.json'))
    names = [s['name'] if isinstance(s, dict) else s for s in skills]
    idx = {n: i for i, n in enumerate(names)}
    if TARGET not in idx:
        print('[SANDBOX] FATAL 目标不在语料名册')
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

    install(base)
    baseline_top1 = (R.route(QUERY, enable_memory=False) or {}).get('top1')
    local_path = os.path.join(GS, TARGET, 'SKILL.md')
    local_body = io.open(local_path, encoding='utf-8').read()[:CHARS]

    print('[SANDBOX] query=%r' % QUERY)
    print('[SANDBOX] baseline top1 = %s (expected=%s)' % (baseline_top1, TARGET))
    print()
    rows = []
    for label, body in CANDIDATES.items():
        if body is None:
            body = local_body
        vec = np.asarray(enc.encode([body]), dtype='float32')[0]
        arr = np.array(base, dtype='float32', copy=True)
        arr[idx[TARGET]] = vec
        install(arr)
        top1 = (R.route(QUERY, enable_memory=False) or {}).get('top1')
        install(base)
        ok = (top1 == TARGET)
        rows.append((label, top1, ok))
        print('  %-22s -> top1=%-28s %s' % (label, top1, 'FLIPPED' if ok else ''))
    n_flip = sum(1 for _, _, ok in rows if ok)
    print()
    print('[SANDBOX] flipped=%d / %d ｜ baseline=%s' % (n_flip, len(rows), baseline_top1))
    return 0


if __name__ == '__main__':
    import json
    raise SystemExit(main())
