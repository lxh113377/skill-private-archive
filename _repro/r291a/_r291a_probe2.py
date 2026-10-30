# -*- coding: utf-8 -*-
'''r291a probe2: version-history shapes, mirror registry, python identity. read-only.'''
import io, os, re, json, subprocess, sys
SK = 'D:/global_skills'
def gitc(*a):
    return subprocess.run(['git', '-C', SK] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace')
print('PY', sys.version.split()[0], sys.executable)
PAIRS = [('test-driven-development', '079b91f3'), ('frontend-slides', '9aaa9214'), ('ui-ux-pro-max', '30b84b20'), ('mcp-builder', '79862372')]
for slug, sha in PAIRS:
    print('=====', slug, sha)
    t = gitc('show', sha + ':' + slug + '/SKILL.md').stdout or ''
    semver_rows = [x for x in t.split(chr(10)) if re.search(r'(?<![0-9.])[0-9]+\.[0-9]+(\.[0-9]+)?(?![0-9])', x)]
    print('  semver-bearing lines (whole SKILL.md):', len(semver_rows))
    print('  first 6:', json.dumps(semver_rows[:6], ensure_ascii=False)[:1500])
    heads = [x for x in t.split(chr(10)) if x.startswith('#') and re.search(r'([Vv]ersion|[Hh]istory|历史|版本)', x)]
    print('  version/history HEADINGS:', json.dumps(heads, ensure_ascii=False)[:600])
    lst = gitc('ls-tree', '-r', '--name-only', sha, '--', slug).stdout.splitlines()
    vfiles = [p for p in lst if re.search(r'(version|histor|changelog|\u7248\u672c|\u5386\u53f2)', os.path.basename(p), re.I)]
    print('  files total', len(lst), 'version-ish files', json.dumps(vfiles, ensure_ascii=False))
    for p in vfiles:
        c = gitc('show', sha + ':' + p).stdout or ''
        rows = [x for x in c.split(chr(10)) if x.strip()]
        print('    ', p, 'lines', len(rows), 'bytes', len(c.encode('utf-8'))) 
        print('      sample:', json.dumps(rows[:10], ensure_ascii=False)[:900])
print('===== mirror registry =====')
reg = os.path.join(SK, '_my-skills', 'registry.json')
d = json.load(io.open(reg, encoding='utf-8', errors='replace'))
print('registry top keys:', json.dumps(list(d.keys())[:20], ensure_ascii=False) if isinstance(d, dict) else 'LIST len ' + str(len(d)))
print(json.dumps(d, ensure_ascii=False)[:2500])
print('===== _my-skills SKILL.md head =====')
print(io.open(os.path.join(SK, '_my-skills', 'SKILL.md'), encoding='utf-8', errors='replace').read()[:1200])