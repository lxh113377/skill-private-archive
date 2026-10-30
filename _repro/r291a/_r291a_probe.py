# -*- coding: utf-8 -*-
'''r291a probe: real field names / mirror shape / pointer shapes. read-only.'''
import io, os, re, subprocess, sys, json
sys.path.insert(0, r'C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/05-exec')
import r220_md_deadlink as D
SK = 'D:/global_skills'
def gitc(*a):
    p = subprocess.run(['git', '-C', SK] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace')
    return p
print('HEAD', gitc('rev-parse', 'HEAD').stdout.strip())
print('worktree dirty lines:', len([x for x in gitc('status', '--porcelain').stdout.splitlines() if x.strip()]))
for slug in ['test-driven-development', 'frontend-slides', 'ui-ux-pro-max', 'mcp-builder']:
    rel = slug + '/SKILL.md'
    t = io.open(os.path.join(SK, rel), encoding='utf-8', errors='replace').read()
    print('=====', slug, 'bytes', len(t.encode('utf-8')))
    fm = t.split(chr(10))
    fm_end = None
    for i in range(1, len(fm)):
        if fm[i].strip() == '---':
            fm_end = i; break
    print('FRONTMATTER_LINES:', json.dumps(fm[1:fm_end], ensure_ascii=False)[:2600])
    links = D.scan_lines(t)
    esc = [u for _l, u in links if u.startswith('..') or (u.split('/')[0] not in ('',) and not os.path.exists(os.path.join(SK, slug, u.partition('#')[0])) and not os.path.exists(os.path.join(SK, u.partition('#')[0])))]
    print('LINKS_TOTAL', len(links), 'ESCAPING_OR_UNKNOWN', json.dumps(esc[:12], ensure_ascii=False))
    for pat in ['Version History', 'version history', '版本史', '版本历史', 'CHANGELOG', 'Changelog']:
        print('  pat', pat, 'hits', t.count(pat))
    print('  version: lines', json.dumps([x for x in t.split(chr(10)) if x.strip().startswith('version')][:6], ensure_ascii=False))
    vh = [x for x in t.split(chr(10)) if re.match(r'^\s*[-*]? ?v?[0-9]+\.[0-9]+', x.strip())]
    print('  vh-candidate-lines', len(vh), json.dumps(vh[:8], ensure_ascii=False)[:1200])
print('===== mirrors =====')
for m in [os.path.join(SK, '_my-skills'), 'C:/Users/37533/.agents/skills']:
    print('--', m, 'exists', os.path.isdir(m))
    if os.path.isdir(m):
        names = sorted(os.listdir(m))
        print('   count', len(names), 'sample', json.dumps(names[:15], ensure_ascii=False))
        for slug in ['test-driven-development', 'frontend-slides', 'ui-ux-pro-max', 'mcp-builder']:
            p = os.path.join(m, slug, 'SKILL.md')
            print('   ', slug, 'SKILL.md', 'exists' if os.path.exists(p) else 'ABSENT', os.path.getsize(p) if os.path.exists(p) else '-', (os.path.realpath(p)[:60] if os.path.exists(p) else ''))
print('===== git archive size check =====')
p = subprocess.run('git -C ' + SK + ' archive 79862372 mcp-builder | wc -c', shell=True, capture_output=True, text=True)
print('mcp-builder archive bytes', p.stdout.strip(), p.stderr.strip()[:200])