import difflib, hashlib, os
def L(p): return open(p, encoding='utf-8', newline='').read()
pairs = [
 ('SKILL', 'D:/global_skills/mcp-builder/SKILL.md', '_repro/r287m/_upstream_SKILL.md'),
 ('NODE', 'D:/global_skills/mcp-builder/reference/node_mcp_server.md', '_repro/r287m/_upstream_node_mcp_server.md'),
]
for name, a_p, b_p in pairs:
    A = L(a_p).splitlines(keepends=True); B = L(b_p).splitlines(keepends=True)
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    print('===', name, 'lines', len(A), len(B), 'endswith_nl', L(a_p).endswith('\n'), L(b_p).endswith('\n'))
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=='equal': continue
        print(tag,i1,i2,j1,j2,'| OLDHEAD', repr(''.join(A[i1:i2])[:70]), '| NEWHEAD', repr(''.join(B[j1:j2])[:70]))
    print('local last 3 lines:', [l[:60] for l in A[-3:]])
# license identity
for p in ['D:/global_skills/mcp-builder/LICENSE.txt','D:/global_skills/mcp-builder/LICENSE']:
    b=open(p,'rb').read(); print(p, len(b), hashlib.sha256(b).hexdigest()[:12])
print('local .upstream:', repr(open('D:/global_skills/mcp-builder/.upstream',encoding='utf-8').read()))
