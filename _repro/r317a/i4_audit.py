# -*- coding: utf-8 -*-
# r317 i4 假红审计：Y5（1.5.0 臂）被判 i4=0(frac .548) 但我手查约束块在 L14-18(.094)——同文件不该两个答案。
# 假设：判据的 NAMED∧LIMITWORD 同行匹配**漏配了约束行的词形**（不可改写/只允许 不在窄表里），
# 首个命中落在 L74 的 distractor（clean+不得）。⇒ 对全部历史 i4=0 格跑「窄/宽词表首命中」对照，量假红面。
# 本器只审计不动尺；宽词表=语义上限（不许|不得|不能|不可|禁止|MUST NOT|只许|仅|只允许|一律|一字不|保持原|原样|不动|禁改|以本段为准|一票否决|fail-closed）。
import hashlib, importlib.util as u, io, json, re
A = 'C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化'
s = u.spec_from_file_location('aj', A + '/_repro/r312a/anchor_judge.py')
M = u.module_from_spec(s); s.loader.exec_module(M)
BROAD = re.compile('(不许|不得|不能|不可|禁止|MUST NOT|只许|仅|只允许|一律|一字不|保持原|原样|不动|禁改|以本段为准|一票否决|fail-closed)')
NAMED = {'task2': re.compile('(价格|assets)'), 'task3': re.compile('(订单金额|金额|clean)')}
K4 = ['item4_first30', 'item5_no_fabricated', 'item6_scope', 'item8_consistent']
def first_hit(p, rxn, rxl):
    tot = len(p.encode('utf-8')); acc = 0
    for i, ln in enumerate(p.split(chr(10))):
        if rxn.search(ln) and rxl.search(ln):
            return (i + 1, round(acc / tot, 3), ln.strip()[:64])
        acc += len((ln + chr(10)).encode('utf-8'))
    return None
CELLS = [
 ('task3', 'r5|X(终版)', '_temp/r317a/out_X5/'),
 ('task3', 'r5|Y', '_temp/r317a/out_Y5/'),
 ('task2', 'r4|X', '_repro/r316a/out_R4/out_X2d__'),
 ('task2', 'r4|Y', '_repro/r316a/out_R4/out_Y2d__'),
 ('task3', 'r2|X', '_repro/r313a/out_R2/out_X3b__'),
 ('task3', 'r3|X', '_repro/r314a/out_R3/out_X3c__'),
 ('task2', 'r1|X', '_repro/r309a/out_X2/'),
]
out = {}
for task, name, base in CELLS:
    pp = (base + 'optimized_prompt.md') if base.endswith('__') or base.endswith('/') else (base + '/optimized_prompt.md')
    lp = pp.replace('optimized_prompt.md', 'process_log.md')
    b = io.open(A + '/' + pp, 'rb').read()
    p = b.decode('utf-8', 'replace')
    g = io.open(A + '/' + lp, encoding='utf-8').read()
    r = M.score_computable(p, g, named_pat=NAMED[task].pattern)
    n1 = first_hit(p, NAMED[task], M.LIMITWORD)
    n2 = first_hit(p, NAMED[task], BROAD)
    verdict = '一致'
    if r['item4_first30'] == 0 and n2 and n2[1] <= 0.30:
        verdict = '假红候选（宽表在 30% 内命中约束行 ' + str(n2[0]) + '，窄表漏配）'
    elif r['item4_first30'] == 1 and n2 and n2[1] > 0.30:
        verdict = '疑宽表过松'
    print('%-6s %-11s mech=%d/4 i4=%d(窄首=%s) 宽首=%s ⇒ %s' % (task, name, sum(r[k] for k in K4),
          r['item4_first30'], str(n1 and n1[1]), str(n2 and n2[1]), verdict))
    if n2 and r['item4_first30'] == 0:
        print('      宽表命中行:', n2[2])
    out[name] = dict(mech=[r[k] for k in K4], narrow=n1, broad=n2, sha256=hashlib.sha256(b).hexdigest()[:12], bytes=len(b))
    if name.endswith('X') and 'r5' in name:
        json.dump(r, io.open(A + '/_temp/r317a/mech_X5_final.json', 'w', encoding='utf-8', newline=''), ensure_ascii=False, indent=1)
    if name == 'r5|Y':
        json.dump(r, io.open(A + '/_temp/r317a/mech_Y5.json', 'w', encoding='utf-8', newline=''), ensure_ascii=False, indent=1)
json.dump(out, io.open(A + '/_temp/r317_i4audit.json', 'w', encoding='utf-8', newline=''), ensure_ascii=False, indent=1)
print('[AUDIT-SAVED] r317_i4audit.json')
