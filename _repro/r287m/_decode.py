
import base64, hashlib, os
D='_repro/r287m'
rec=[]
for src,dst in [('_v2.b64','upstream_node_mcp_server_v2.md'),('_skill_up.b64','_upstream_SKILL.md'),('_node_up.b64','_upstream_node_mcp_server.md')]:
    raw=base64.b64decode(open(os.path.join(D,src),encoding='utf-8').read())
    p=os.path.join(D,dst)
    open(p,'wb').write(raw)
    h=hashlib.sha256(raw).hexdigest()
    rec.append((dst,len(raw),raw.count(b'\n')+ (0 if raw.endswith(b'\n') else 1),h[:12],h))
for a in rec: print(a)
# local equivalents
L='D:/global_skills/mcp-builder'
for n in ['SKILL.md','reference/node_mcp_server.md','reference/node_mcp_server_v2.md']:
    p=os.path.join(L,n)
    if os.path.exists(p):
        b=open(p,'rb').read(); print('LOCAL',n,len(b),hashlib.sha256(b).hexdigest()[:12])
    else:
        print('LOCAL-MISSING',n)
