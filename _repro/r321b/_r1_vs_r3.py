import importlib.util, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), 'r320a', 'entry_census', 'check_r319a.py')
sp = importlib.util.spec_from_file_location('ck', SRC); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
sp2 = importlib.util.spec_from_file_location('rs', os.path.join(HERE, '_r321b_resolve.py')); rs = importlib.util.module_from_spec(sp2); sp2.loader.exec_module(rs)
hf, ts = m.head_tree()
upn, upd = m.upstream_excludes()
slugs = []
for pr in json.load(open(m.BASELINE, encoding='utf-8'))['pairs']:
    s = pr.get('slug')
    if s and s not in slugs: slugs.append(s)
td = set(p.split('/')[0] for p in hf if '/' in p)
others = set(x.lower() for x in td if x not in slugs)
SEP = set(['-','_','.'])
def tur(stem):
    i = len(stem)
    while i > 0 and stem[i-1].isalpha() and stem[i-1].isupper(): i -= 1
    run = stem[i:]
    if len(run) < 2 or i == 0: return ''
    return run if stem[i-1] in SEP else ''
def r1(cand):
    for seg in cand.split('/'):
        if '*' in seg or '?' in seg: return True
        if seg[:1] in set(['{','<','$']): return True
    last = cand.split('/')[-1]
    stem = last.rsplit('.',1)[0] if '.' in last else last
    return tur(stem) != ''
out = []
PROBES = [('data-analysis','assets/STYLE_PRESETS.md'),('story-review','references/dispatch-NN.md'),('story-import','references/split-11.md'),('story-cover','references/split-NN.md'),('frontend-slides','STYLE_PRESETS.md'),('canvas-design','canvas-fonts/Lora-OFL.txt'),('canvas-design','canvas-fonts/Nope-OFL.txt'),('cloudbase','references/cloudbase-code-review/references/RULES_INDEX.md')]
for slug, rel in PROBES:
    own = sorted(p[len(slug)+1:] for p in hf if p.startswith(slug + '/'))
    isph, rx = rs.shape(rel)
    hits = [x for x in own if rx is not None and rx.match(x)]
    out.append({'slug': slug, 'rel': rel, 'exists_in_tree': rel in own, 'R1_exempts': bool(r1(rel)), 'R3_exempts': bool(isph and hits), 'R3_hits': len(hits)})
print(json.dumps(out, ensure_ascii=False, indent=1))