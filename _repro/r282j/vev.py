import io, json, subprocess, os
ROOT = 'C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化'
o = json.load(io.open(os.path.join(ROOT, '06-benchmark', 'r282_three_arm_reconcile.json'), encoding='utf-8'))
bad = []
total = 0
for r in o['rows']:
    cmds = r['adjudication_evidence_cmd'].split(' ; ')
    for c in cmds:
        total += 1
        p = subprocess.run(['bash', '-c', c], capture_output=True, timeout=900, cwd=ROOT)
        out = (p.stdout or b'').decode('utf-8', 'replace').strip()
        err = (p.stderr or b'').decode('utf-8', 'replace').strip()
        ok = p.returncode == 0 and bool(out)
        print('%-24s rc=%d chars=%6d %s :: %s%s' % (r['skill'], p.returncode, len(out), 'OK' if ok else 'NOT-OK', c[-44:], ('' if ok else ' ERR=' + err[:120])))
        if not ok:
            bad.append(c)
print('ALL_EVIDENCE_CMDS_RUNNABLE', 'NO ' + str(len(bad)) if bad else 'YES', 'total=%d' % total)
