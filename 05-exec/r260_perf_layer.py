import io,json,os,statistics,collections
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d=json.load(io.open(os.path.join(ROOT,'06-benchmark','r260_perf_face.json'),encoding='utf-8'))
rows=d['rows']
ms=[r for r in rows if isinstance(r['route_ms_med'],(int,float))]
def path(r):
    if r.get('direct_hit'): return 'L0.1_direct'
    if r.get('n_candidates')==1: return 'L0.5_tag'
    return 'L1_bge'
g=collections.defaultdict(list)
for r in ms: g[path(r)].append(r['route_ms_med'])
for k,v in sorted(g.items(),key=lambda kv:-statistics.median(kv[1])):
    print('%-14s n=%2d med=%8.3f min=%8.3f max=%8.3f' % (k,len(v),statistics.median(v),min(v),max(v)))
print('conf',collections.Counter(r.get('confidence') for r in ms).most_common())
print('needs_llm? cand_n dist',collections.Counter(r.get('n_candidates') for r in ms).most_common())
print('NO_TRIGGER slugs HIGH', [r['slug'] for r in rows if r['status']=='NO_TRIGGER' and r['tier']=='HIGH'][:40])
big=[r for r in rows if r['skillmd_bytes']>20000]
print('big_no_trig',sum(1 for r in big if r['status']=='NO_TRIGGER'),'of',len(big))
print('story_setup trig?', [r['trigger_src'] for r in rows if r['slug']=='story-setup'])
