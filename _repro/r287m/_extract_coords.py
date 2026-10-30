
import json, os
out=[]
def rec(*a): out.append(": ".join(str(x) for x in a))
d=json.load(open('06-benchmark/r264_superpowers_follow_version_diff.json',encoding='utf-8'))
rec('R264 top keys', list(d.keys()))
rec('R264 upstream_repo', d.get('upstream_repo'), 'ref', d.get('upstream_ref'))
rows=[r for r in d.get('rows',[]) if 'mcp-builder' in json.dumps(r,ensure_ascii=False)]
rec('R264 mcp rows', len(rows))
for r in rows: rec('R264 row', json.dumps(r,ensure_ascii=False))
for p in ['06-benchmark/r264_sidecar_semantics.json','06-benchmark/r265_follow_version_feasibility.json','06-benchmark/r271_version_channel2.json','06-benchmark/r263_declared_upstream_face.json']:
    if not os.path.exists(p):
        rec(p,'MISSING'); continue
    s=json.load(open(p,encoding='utf-8'))
    arr = s['rows'] if isinstance(s,dict) and isinstance(s.get('rows'),list) else (s if isinstance(s,list) else [])
    hits=[x for x in arr if isinstance(x,dict) and 'mcp-builder' in json.dumps(x,ensure_ascii=False)]
    rec(p,'rows',len(arr) if isinstance(arr,list) else 'N/A','hits',len(hits))
    for h in hits: rec(p+' row', json.dumps(h,ensure_ascii=False))
txt="\n".join(out)
open('_repro/r287m/_coord_rows.txt','w',encoding='utf-8').write(txt)
print(txt[:11000])
