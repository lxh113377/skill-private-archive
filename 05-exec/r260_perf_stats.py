import io,json,os,statistics,collections,math
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d=json.load(io.open(os.path.join(ROOT,'06-benchmark','r260_perf_face.json'),encoding='utf-8'))
rows=d['rows']
ms=[r for r in rows if isinstance(r['route_ms_med'],(int,float))]
v=sorted(r['route_ms_med'] for r in ms); q=statistics.quantiles(v,n=4)
def p(x): return round(v[min(len(v)-1,int(x*len(v)))],3)
print('min',round(v[0],3),'p25',round(q[0],3),'med',round(statistics.median(v),3),'p75',round(q[2],3),'p90',p(0.9),'max',round(v[-1],3),'mean',round(statistics.mean(v),3))
print('warmup',d['meta']['warmup_ms'])
def lay(r): return 'direct' if r.get('direct_hit') else 'bge'
for k in ('direct','bge'):
    a=[r['route_ms_med'] for r in ms if lay(r)==k]
    print('LAYER',k,len(a),round(statistics.median(a),3),round(min(a),3),round(max(a),3))
print('SLOW10')
for r in sorted(ms,key=lambda r:-r['route_ms_med'])[:10]:
    print('%-34s %8.3f bytes=%-7s refs_md=%-4s refs_B=%-8s self=%-5s top1=%s' % (r['slug'],r['route_ms_med'],r['skillmd_bytes'],r['refs_md'],r['refs_bytes'],r['self_hit'],r['top1']))
print('FAST5')
for r in sorted(ms,key=lambda r:r['route_ms_med'])[:5]:
    print('%-34s %8.3f direct=%s trig=%s' % (r['slug'],r['route_ms_med'],r['direct_hit'],r['trigger']))
x=[r['skillmd_bytes'] for r in ms]; y=[r['route_ms_med'] for r in ms]; n=len(x)
def pear(a,b):
    ma=statistics.mean(a); mb=statistics.mean(b)
    sa=math.sqrt(sum((t-ma)**2 for t in a)/n); sb=math.sqrt(sum((t-mb)**2 for t in b)/n)
    return round(sum((a[i]-ma)*(b[i]-mb) for i in range(n))/n/(sa*sb),4)
print('pearson_bytes_ms',pear(x,y))
print('pearson_refsB_ms',pear([r['refs_bytes'] for r in ms],y))
def rank(t):
    o=sorted(range(len(t)),key=lambda i:t[i]); rk=[0]*len(t)
    for i,j in enumerate(o): rk[j]=i
    return rk
print('spearman_bytes_ms',pear(rank(x),rank(y)))
print('selfhit',sum(1 for r in ms if r['self_hit']),'/',len(ms))
print('MISS', [r['slug'] for r in ms if not r['self_hit']])
print('bytes_sk med',round(statistics.median([r['skillmd_bytes'] for r in rows]),1),'max',max(r['skillmd_bytes'] for r in rows),'sum',sum(r['skillmd_bytes'] for r in rows),'p90',sorted(r['skillmd_bytes'] for r in rows)[int(0.9*77)-1])
print('refs sum',sum(r['refs_bytes'] for r in rows),'md',sum(r['refs_md'] for r in rows),'files',sum(r['refs_files'] for r in rows),'zero',sum(1 for r in rows if r['refs_bytes']==0))
print('top5refs',sorted([(r['refs_bytes'],r['slug'],r['refs_md']) for r in rows],reverse=True)[:5])
print('top5sk',sorted([(r['skillmd_bytes'],r['slug']) for r in rows],reverse=True)[:5])
print('conf',collections.Counter(r.get('confidence') for r in ms).most_common())
print('cand',collections.Counter(r.get('n_candidates') for r in ms).most_common())
print('src',collections.Counter(r['trigger_src'] for r in rows).most_common())
