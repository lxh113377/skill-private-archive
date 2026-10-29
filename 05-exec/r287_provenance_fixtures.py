# -*- coding: utf-8 -*-
'''r287_provenance_fixtures.py —— r287 门的自证（四腿，含变异）。

为什么必须有：基线分列能让历史 54 项不再判红，但同一改动也可能把门做成恒绿 —— 新增一项不可解析
出处时它必须 FAIL 并点名，否则「基线」就是自我豁免的开关。
'''
import io, json, os, shutil, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = 'C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe'
GATE = os.path.join(ROOT, '05-exec', 'r287_provenance_resolve.py')
BASELINE = os.path.join(ROOT, '06-benchmark', 'r287_provenance_baseline.json')
ok = 0
tot = 0

def mk_root(with_baseline, extra_face):
    """独立 git 仓（门内部跑 git ls-files，所以夹具必须自带 .git）。"""
    d = tempfile.mkdtemp(prefix='r287fx_')
    os.makedirs(os.path.join(d, '05-exec'))
    os.makedirs(os.path.join(d, '06-benchmark'))
    io.open(os.path.join(d, '05-exec', 'real_gate.py'), 'w', encoding='utf-8').write('# tracked\n')
    io.open(os.path.join(d, '06-benchmark', 'a_face.json'), 'w', encoding='utf-8').write(extra_face)
    subprocess.run(['git', 'init', '-q', d], check=True, capture_output=True)
    subprocess.run(['git', '-C', d, 'add', '-A'], check=True, capture_output=True)
    subprocess.run(['git', '-C', d, '-c', 'user.email=a@b', '-c', 'user.name=t',
                    'commit', '-q', '-m', 'fx'], check=True, capture_output=True)
    if with_baseline:
        shutil.copyfile(BASELINE, os.path.join(d, '06-benchmark', 'r287_provenance_baseline.json'))
    return d

def run(d, label, want_state, want_rc):
    global ok, tot
    tot += 1
    p = subprocess.run([PY, GATE, '--root', d, '--json', os.path.join(d, 'out.json')],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    j = {} 
    op = os.path.join(d, 'out.json')
    if os.path.isfile(op):
        j = json.load(io.open(op, encoding='utf-8'))
    named = any(want_state == 'PROVRESOLVE_FAIL' and 'r999_ghost.py' in str(x.get('ref', ''))
                for x in (j.get('new_unresolvable') or [])) if want_state == 'PROVRESOLVE_FAIL' else True
    good = (want_state in ((p.stdout or '') + (p.stderr or '') or '') or j.get('state') == want_state)
    good = good and p.returncode == want_rc and named
    ok += 1 if good else 0
    print('[%s] %s rc=%d state=%s named=%s' % ('PASS' if good else 'FAIL', label,
          p.returncode, j.get('state') or ('(stdout only)' if not j else None), named))
    shutil.rmtree(d, ignore_errors=True)

# 腿 1：干净面件（引用已跟踪的 real_gate.py）⇒ OK
d = mk_root(True, json.dumps({'provenance_cmd': 'python 05-exec/real_gate.py'}))
run(d, 't1 clean reference -> OK', 'PROVRESOLVE_OK', 0)

# 腿 2：注入一个 _temp/ 下的幽灵引用 ⇒ 必须 FAIL 且点名
d = mk_root(True, json.dumps({'provenance_cmd': 'python _temp/r999_ghost.py'}))
run(d, 't2 injected _temp ghost -> FAIL', 'PROVRESOLVE_FAIL', 1)

# 腿 3：无基线 ⇒ UNVERIFIED（不得判绿）
d = mk_root(False, json.dumps({'provenance_cmd': 'python 05-exec/real_gate.py'}))
run(d, 't3 missing baseline -> UNVERIFIED', 'PROVRESOLVE:UNVERIFIED', 2)

# 腿 4：变异 —— 把 git 取数打断（root 不是仓库）⇒ UNVERIFIED，且不得当成 0 件通过
tot += 1
d = tempfile.mkdtemp(prefix='r287notgit_')
os.makedirs(os.path.join(d, '06-benchmark'))
io.open(os.path.join(d, '06-benchmark', 'x.json'), 'w', encoding='utf-8').write('{}')
p = subprocess.run([PY, GATE, '--root', d], capture_output=True, text=True,
                   encoding='utf-8', errors='replace')
g4 = p.returncode == 2 and 'UNVERIFIED' in (p.stdout or '')
ok += 1 if g4 else 0
print('[%s] t4 not-a-repo (git 取数失败) -> UNVERIFIED rc=%d' % ('PASS' if g4 else 'FAIL', p.returncode))
shutil.rmtree(d, ignore_errors=True)

print('[GATE:fixture-%s] legs=%d/%d' % ('pass' if ok == tot else 'fail', ok, tot))
raise SystemExit(0 if ok == tot else 1)
