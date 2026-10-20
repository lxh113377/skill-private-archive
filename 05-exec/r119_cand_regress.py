# -*- coding: utf-8 -*-
import io, os, sys, json, random
FW = r'C:\Users\37533\Desktop\workspace\焚诀'
EVAL = os.path.join(FW, 'eval')
GS = r'D:\global_skills'
sys.path.insert(0, EVAL)
os.environ['FENJUE_ROUTE_TRACE'] = '0'
import numpy as np
import bge_onnx_engine
enc = bge_onnx_engine.BgeOnnxEncoder()
base = np.asarray(np.load(os.path.join(EVAL, 'bge_fullbody_embeddings.npy'), mmap_mode='r'), dtype='float32')
def lj(p):
    with io.open(p, encoding='utf-8') as f: return json.load(f)
skills = lj(os.path.join(EVAL, 'bge_fullbody_skills.json'))
names = [s['name'] if isinstance(s, dict) else s for s in skills]
idx = {n:i for i,n in enumerate(names)}
import bge_layer, unified_router as R
def install(arr):
    bge_layer._bge_emb = arr; bge_layer._bge_skills = skills; bge_layer._bge_model = enc
    bge_layer._BGE_PROBE_DONE = True; bge_layer._bge_backend = 'onnx-sim'; bge_layer._QEMB_CACHE.clear()
TARGET='chaoshi-web-deploy'
CAND_D = ('超市web部署与部署排障唯一权威源（v3 新架构：Cloudflare Pages Functions + D1 + GitHub Pages 双前端）。'
          'cloudbase 云函数部署后订单不显示、部署后数据不显示、部署故障排查、部署后页面 404。'
          '任何 wrangler pages deploy / gh pages 推送 / d1 execute 前必须先加载本 skill 获取对应模式 checklist，禁止凭记忆裸跑。'
          '覆盖两种部署目标：①Cloudflare Pages（管理后台+API，supermarket-web.pages.dev）②GitHub Pages（微信顾客端，lxh113377.github.io）。'
          '触发词：超市部署、chaoshi deploy、超市上线、部署超市、wrangler pages deploy、gh pages 推送、D1 迁移、部署 Cloudflare。')
SENTINEL_N, SENTINEL_SEED = 20, 20261018
install(base)
sets = [('layered', lj(os.path.join(EVAL,'layered_testset.json'))), ('frozen', lj(os.path.join(EVAL,'frozen_blind_test.json')))]
questions = []
for sn, tiers in sets:
    for tier in tiers:
        for q in tier.get('queries', []):
            if q.get('expected_skill'):
                questions.append({'set': sn, 'query': q['query'], 'expected': q['expected_skill']})
def run(qs):
    return [(q, (R.route(q['query'], enable_memory=False) or {}).get('top1')) for q in qs]
base_rows = run(questions)
base_by_q = {q['query']: t1 for q, t1 in base_rows}
rng = random.Random(SENTINEL_SEED)
sentinel = rng.sample(questions, min(SENTINEL_N, len(questions)))
local_qs = [q for q in questions if q['expected'] == TARGET]
subset = list(local_qs); seen = {q['query'] for q in subset}
subset += [q for q in sentinel if q['query'] not in seen]
vec = np.asarray(enc.encode([CAND_D]), dtype='float32')[0]
arr = np.array(base, dtype='float32', copy=True); arr[idx[TARGET]] = vec
install(arr)
after = run(subset)
install(base)
flips = [(q['query'], q['expected'], base_by_q[q['query']], t1, q['set']) for q, t1 in after if base_by_q[q['query']] != t1]
improved = [f for f in flips if f[1]==TARGET and f[3]==TARGET]
worsened = [f for f in flips if f[1]==TARGET and f[2]==TARGET]
cross = [f for f in flips if f[1]!=TARGET]
print('[REGRESS-D] subset=%d local=%d sentinel=%d' % (len(subset), len(local_qs), len(subset)-len(local_qs)))
print('[REGRESS-D] flips=%d improved=%d worsened=%d cross=%d' % (len(flips), len(improved), len(worsened), len(cross)))
for f in flips: print('   %-40s exp=%-22s %s -> %s (%s)' % (f[0][:38], f[1], f[2], f[3], f[4]))
print('[REGRESS-D] verdict=%s' % ('SAFE' if (improved and not worsened and not cross) else 'UNSAFE'))