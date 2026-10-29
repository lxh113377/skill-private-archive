import io, os, json, subprocess, hashlib, time
ROOT = os.getcwd()
PY = 'C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe'
OUT = os.path.join(ROOT, '_temp/r281smoke3')
os.makedirs(OUT, exist_ok=True)

def git_show(arg):
    p = subprocess.run(['git', '-C', 'D:/global_skills', 'show', arg], capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    return p.stdout if p.returncode == 0 else None

def sha16(x):
    return hashlib.sha256(x.encode('utf-8')).hexdigest()[:12]

# 基准必须显式给，不能用 <落地提交>~1：r266 的误整树提交 079b91f3 把当时他人在途的降级态
# （ui-ux 5796 -> 5327、删 3 条版本史、version 1.5.0 -> 1.2.0）扫进了仓库，于是 30b84b20~1
# 量到的是被污染的一版而不是我改动前的一版（r281 实测；F 在 frontend-slides 上发现同类）。
CASES = [
    ('ui-ux-pro-max', '3c72867d', '3da30832'),
    ('frontend-slides', '3681df5e', '89efb3e6'),
    ('test-driven-development', '079b91f3~1', '079b91f3'),
]
rows = {}
for skill, ref_before, ref_after in CASES:
    tb = git_show(ref_before + ':' + skill + '/SKILL.md')
    ta = git_show(ref_after + ':' + skill + '/SKILL.md')
    if tb is None or ta is None:
        rows[skill] = {'state': 'UNVERIFIED', 'before_found': tb is not None, 'after_found': ta is not None}
        print('%-24s UNVERIFIED before=%s after=%s' % (skill, tb is not None, ta is not None))
        continue
    hist_b = tb.count('**1.')
    hist_a = ta.count('**1.')
    rows[skill] = {'state': 'OK', 'ref_before': ref_before, 'ref_after': ref_after,
                   'before_sha16': sha16(tb), 'after_sha16': sha16(ta),
                   'before_bytes': len(tb.encode('utf-8')), 'after_bytes': len(ta.encode('utf-8')),
                   'version_history_entries_before': hist_b, 'version_history_entries_after': hist_a,
                   'history_lost': hist_a < hist_b}
    print('%-24s bytes %d->%d | hist %d->%d lost=%s' % (skill, rows[skill]['before_bytes'],
          rows[skill]['after_bytes'], hist_b, hist_a, rows[skill]['history_lost']))

# 只跑「各自版本文档真实写着的命令」；argv 手工硬列（自动抽取会把 argv 的 bug 记成件的失败）
SCRIPTS = 'D:/global_skills/ui-ux-pro-max/scripts/'
QUERY = 'SaaS analytics dashboard'
smoke = {}
for name, ref, argv in (('A_before', '3c72867d', [PY, SCRIPTS + 'design_system.py', QUERY]),
                        ('B_after', '3da30832', [PY, SCRIPTS + 'search.py', QUERY,
                         '--design-system', '--persist', '--output-dir', OUT])):
    txt = git_show(ref + ':ui-ux-pro-max/SKILL.md') or ''
    p = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8', errors='replace',
                       timeout=180, cwd=OUT)
    arts = []
    for dp, dns, fns in os.walk(OUT):
        for fn in fns:
            arts.append(os.path.relpath(os.path.join(dp, fn), OUT).replace(os.sep, '/'))
    smoke[name] = {'command': [os.path.basename(argv[1])] + argv[2:], 'rc': p.returncode,
                   'stdout_bytes': len((p.stdout or '').encode('utf-8')),
                   'text_bytes': len(txt.encode('utf-8')), 'persisted': sorted(set(arts))}
    print('%-9s rc=%s stdout=%dB persisted_files=%d' % (name, p.returncode,
          len((p.stdout or '').encode('utf-8')), len(set(arts))))

doc = {'schema': 'smoke-documented-commands-v1', 'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
       'provenance_cmd': 'python 05-exec/r281_smoke_ab.py',
       'baseline_rule': ('explicit before/after refs; never <first-landing>~1, because the accidental '
                         'whole-tree commit 079b91f3 recorded others in-flight downgrade for 3 files'),
       'fairness_rule': ('each arm runs only the command its own version text documents; argv is '
                         'hard-listed because auto-extraction turned argv bugs into apparent failures'),
       'limit': ('measures executability and persistence of the documented workflow; NOT task quality'),
       'version_history_audit': rows, 'smoke': smoke}
io.open('06-benchmark/r281_smoke_ab.json', 'w', encoding='utf-8', newline='').write(
    json.dumps(doc, ensure_ascii=False, indent=1))
print('[WROTE] 06-benchmark/r281_smoke_ab.json | history_lost_any =',
      any(x.get('history_lost') for x in rows.values()))
