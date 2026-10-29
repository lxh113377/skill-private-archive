import io, json, os, subprocess, hashlib
ROOT = 'C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化'
o = json.load(io.open(os.path.join(ROOT,'06-benchmark','r282_three_arm_reconcile.json'), encoding='utf-8'))
gate = o['arm_quiescence_gate']
bad = []
for name, rec in gate.items():
    p = os.path.join(ROOT, '06-benchmark', name)
    st = os.stat(p)
    cur = hashlib.sha256(open(p,'rb').read()).hexdigest()[:12]
    ok = (cur == rec['sha256_12'])
    print('%-36s mtime=%s sha12_rec=%s sha12_now=%s unchanged=%s' % (name, rec['mtime_utc'], rec['sha256_12'], cur, ok))
    if not ok:
        bad.append(name)
print('ORIGINALS_UNCHANGED', 'YES' if not bad else 'NO ' + str(bad))
# 05-exec judges untouched (mtime older than this session start 2026-10-29T16:00Z)
for j in ['05-exec/r278_landing_effect.py', '05-exec/r268_unreferenced_siblings.py', '05-exec/r281g_score.py', '_repro/r278c/r278c_metrics.py']:
    st = os.stat(os.path.join(ROOT, j))
    import datetime as _d
    print('%-40s mtime=%s' % (j, _d.datetime.utcfromtimestamp(st.st_mtime).strftime('%Y-%m-%dT%H:%M:%SZ')))
