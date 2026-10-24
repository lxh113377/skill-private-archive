# -*- coding: utf-8 -*-
# 双向验证 r195 估界法
import sys, os, glob, json, shutil, tempfile, datetime
sys.path.insert(0, '05-exec')
import ratchet_gate as m
from pathlib import Path

def hm(ts):
    return datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')

def od(fn):
    try:
        return (json.load(open(fn, encoding='utf-8')).get('by_class') or {}).get('OVERDUE')
    except Exception:
        return 'NA'

BENCH = Path('06-benchmark')
pick = m._newest_artifact(BENCH / 'debt_aging_r*.json')
print('A) 真机选中 =', os.path.basename(pick), '| OVERDUE =', od(pick))
arts = sorted(glob.glob('06-benchmark/debt_aging_r*.json'), key=os.path.getmtime)
print('   mtime 最新的件 =', os.path.basename(arts[-1]), hm(os.path.getmtime(arts[-1])), '| OVERDUE =', od(arts[-1]))
print('   期望二者一致，且 OVERDUE=1（真值），而非旧件的 3')

# B) CI 等价：平 mtime
tmp = tempfile.mkdtemp(prefix='r195_flat_')
names = ['debt_aging_r195_fix.json',
         'debt_aging_r_autoregen_20261024_021326.json',
         'debt_aging_r162b_2026-10-22.json']
for n in names:
    fp = os.path.join(tmp, n)
    open(fp, 'w', encoding='utf-8').write('{}')
    os.utime(fp, (1700000000.0, 1700000000.0))
p2 = m._newest_artifact(Path(tmp) / 'debt_aging_r*.json')
print('B) 平 mtime 选中 =', os.path.basename(p2),
      'OK' if 'autoregen_20261024' in p2 else 'BAD')
shutil.rmtree(tmp, ignore_errors=True)

# C) 反假绿：旧名 + checkout 刷新的 mtime
tmp2 = tempfile.mkdtemp(prefix='r195_chk_')
a1 = 'debt_aging_r100_2026-09-01.json'
a2 = 'debt_aging_r_autoregen_20261024_021326.json'
now = datetime.datetime.now().timestamp()
for nm, mt in ((a1, now), (a2, now - 60)):
    fp = os.path.join(tmp2, nm)
    open(fp, 'w').write('{}')
    os.utime(fp, (mt, mt))
p3 = m._newest_artifact(Path(tmp2) / 'debt_aging_r*.json')
print('C) 旧名新mtime 选中 =', os.path.basename(p3),
      'OK 估界生效' if 'autoregen' in p3 else 'BAD 仍被 mtime 骗')
shutil.rmtree(tmp2, ignore_errors=True)