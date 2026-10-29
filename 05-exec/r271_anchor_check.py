# -*- coding: utf-8 -*-
"""Per-anchor grep validator (argv: <spec.json> <out.json> <expect>).

Each edit anchor must be found by GNU grep -nF with exactly ONE hit line. The
negative-control run injects a deliberately nonexistent anchor and MUST report FAIL.
grep runs per anchor as an argv element, so shell quoting cannot distort anchors.
"""
import json, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'r271_edits_spec.json')
out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'r271_anchor_hits.json')
expect = sys.argv[3] if len(sys.argv) > 3 else 'PASS'
spec = json.load(open(spec_path, encoding='utf-8'))
rows, fails = [], []
for e in spec['edits']:
    p = subprocess.run(['grep', '-nF', '-e', e['anchor'], e['file']], capture_output=True, text=True)
    hits = [int(l.split(':', 1)[0]) for l in p.stdout.strip().splitlines() if l]
    ok = len(hits) == 1
    rows.append({'id': e['id'], 'file': e['file'], 'anchor': e['anchor'], 'grep_cmd': 'grep -nF -e ' + e['anchor'] + ' ' + e['file'], 'grep_hits': hits, 'verdict': 'PASS' if ok else 'FAIL'})
    if not ok: fails.append(e['id'] + ' hits=' + str(hits))
    print(('PASS' if ok else 'FAIL') + ' line=' + str(hits) + ' ' + e['id'] + ' :: ' + e['anchor'][:58])
neg_hits = 0
if spec.get('negative_control'):
    for f in sorted(set(e['file'] for e in spec['edits'])):
        p = subprocess.run(['grep', '-nF', '-e', spec['negative_control'], f], capture_output=True, text=True)
        neg_hits += len([l for l in p.stdout.strip().splitlines() if l])
    print(('NEGCTRL-ABSENT-OK' if neg_hits == 0 else 'NEGCTRL-ABSENT-FAIL') + ' hits=' + str(neg_hits))
verdict = 'PASS' if not fails else 'FAIL'
json.dump({'schema': 'migration-plan-anchor-check-v1', 'spec': os.path.basename(spec_path), 'expect': expect, 'checked': len(rows), 'rows': rows, 'negative_control': spec.get('negative_control'), 'negative_control_absent_hits': neg_hits, 'fails': fails, 'verdict': verdict}, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('TOTAL checked=' + str(len(rows)) + ' fails=' + str(len(fails)) + ' verdict=' + verdict + ' expect=' + expect)
sys.exit(0 if (verdict == expect and (not spec.get('negative_control') or neg_hits == 0)) else 1)