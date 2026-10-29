import os, sys, json, shutil, subprocess, hashlib, time, re

# R281 roll-up: score both arms with the mechanical scorer, then run the NEGATIVE
# CONTROL: copy arm A's artifacts into a third directory and score it as if it were
# the B arm. Same bytes => same scores => uplift must be exactly 0. That proves the
# ruler does not favour a position (arm order) and that uplift comes from content.

ROOT = os.path.abspath(os.getcwd())
PY = os.environ['R281_PY']
SCORER = os.path.join(ROOT, '_temp', 'r281h', '_ctl', 'score_ab.py')
BASE = os.path.join(ROOT, '_temp', 'r281h')

def score(name, arm_dir):
    out = subprocess.run([PY, '-B', SCORER, name], capture_output=True, text=True, cwd=ROOT)
    if out.returncode != 0:
        raise RuntimeError('scorer failed for ' + name + ': ' + out.stderr[:800])
    return json.loads(out.stdout)[name]

def tree_hash(d):
    h = hashlib.sha256()
    for p in sorted(q for q in [os.path.join(r, f) for r, _, fs in os.walk(d) for f in fs]):
        h.update(os.path.relpath(p, d).encode('utf-8', 'replace'))
        h.update(open(p, 'rb').read())
    return h.hexdigest()

def q_of(res):
    return res['rubric']['1_artifact_existence'] + res['rubric']['2_content_completeness'] + res['rubric']['3_executability'] + res['rubric']['4_no_fabrication'] + res['rubric']['5_instruction_following']

arms = sys.argv[1:] or ['A', 'B']
res = {}
for a in arms:
    d = os.path.join(BASE, a)
    files = [os.path.relpath(os.path.join(r, f), ROOT).replace(os.sep, '/') for r, _, fs in os.walk(d) for f in fs]
    if not [f for f in files if not f.endswith('SKILL.md')]:
        res[a] = {'UNVERIFIED': True, 'reason': 'no artifacts produced', 'dir': d}
        continue
    res[a] = score(a, d)
    res[a]['artifact_tree_sha256'] = tree_hash(d)

# negative control: A bytes, scored under the B slot name
ctl = os.path.join(BASE, '_ctl', 'negctl')
if os.path.isdir(ctl):
    shutil.rmtree(ctl)
shutil.copytree(os.path.join(BASE, 'A'), ctl)
ctl_res = score('NEGCTL', ctl)
ctl_q = q_of(ctl_res)
a_q = q_of(res['A']) if 'UNVERIFIED' not in res['A'] else None

summary = {
    'arms_scored': {a: {'Q': q_of(res[a]) if 'UNVERIFIED' not in res[a] else None, 'rubric': res[a].get('rubric') if 'UNVERIFIED' not in res[a] else None, 'tree_sha': res[a].get('artifact_tree_sha256')} for a in arms},
    'negctl': {'dir': os.path.relpath(ctl, ROOT).replace(os.sep, '/'), 'Q': ctl_q, 'tree_sha': tree_hash(ctl), 'uplift_A_vs_negctl_pct': 0.0 if a_q == ctl_q else None, 'identical_bytes_to_A': tree_hash(ctl) == res['A'].get('artifact_tree_sha256', '') if a_q else None},
    'per_dimension_delta_B_minus_A': {},
}
for k in ['1_artifact_existence', '2_content_completeness', '3_executability', '4_no_fabrication', '5_instruction_following', '6_cost_tool_calls']:
    if 'UNVERIFIED' in res['A'] or 'UNVERIFIED' in res['B']:
        break
    va = res['A']['rubric'][k]; vb = res['B']['rubric'][k]
    summary['per_dimension_delta_B_minus_A'][k] = {'A': va, 'B': vb, 'delta': (vb - va) if isinstance(va, int) and isinstance(vb, int) else 'n/a'}

print(json.dumps(summary, ensure_ascii=False, indent=1))
