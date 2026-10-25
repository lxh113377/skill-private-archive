# -*- coding: utf-8 -*-
"""围栏感知死链扫描 + 内建正反两腿自证。"""
import io, os, re, sys

LINK = re.compile(r'\[[^\]]*\]\(\s*([^)\s]+?)(?:\s+"[^"]*")?\s*\)')

def scan_lines(txt):
    """返回代码围栏【外】的 (行号, 目标)。围栏标记 = 行首 ≥3 个反引号或波浪线。"""
    out, marker = [], None
    for i, line in enumerate(txt.split(chr(10)), 1):
        st = line.strip()
        if marker is None and (st.startswith('```') or st.startswith('~~~')):
            marker = st[:3]
            continue
        if marker is not None:
            if st.startswith(marker):
                marker = None
            continue
        for mm in LINK.finditer(line):
            out.append((i, mm.group(1)))
    return out

def build(root):
    files, dirs = set(), set()
    for dp, _dn, fn in os.walk(root):
        if (os.sep + '.git' + os.sep) in (dp + os.sep):
            continue
        rel = os.path.relpath(dp, root).replace(os.sep, '/')
        if rel != '.':
            dirs.add(rel)
        for f in fn:
            files.add((rel + '/' if rel != '.' else '') + f)
    return files, dirs

def dead(root):
    files, dirs = build(root)
    res = []
    for rel in sorted(p for p in files if p.endswith('.md')):
        txt = io.open(os.path.join(root, rel.replace('/', os.sep)), encoding='utf-8', errors='replace').read()
        own = rel.rsplit('/', 1)[0] if '/' in rel else ''
        for ln, u in scan_lines(txt):
            if re.match(r'^(https?:|mailto:|data:|//|/)', u):
                continue
            # 占位符/字面量不算链接（r157 G-5a 同族：别人模板里的 [Title](URL) 曾被当死链）
            if u in ('URL', 'url') or re.match(r'^[A-Z]+$', u) or u.find('<') >= 0 or u.find('>') >= 0:
                continue
            path = u.partition('#')[0]
            if not path:
                continue
            cand = (own + '/' + path) if own else path
            acc = []
            for pp in cand.split('/'):
                if pp in ('', '.'):
                    continue
                if pp == '..':
                    if acc:
                        acc.pop()
                    continue
                acc.append(pp)
            norm = '/'.join(acc)
            if norm in files or norm in dirs or (norm + '.md') in files \
               or (norm + '/README.md') in files or norm.rstrip('/') in dirs:
                continue
            res.append((rel, ln, u, norm))
    return res

def selftest(root):
    import tempfile, shutil
    d = tempfile.mkdtemp()
    io.open(os.path.join(d, 'a.md'), 'w', encoding='utf-8').write(chr(10).join([
        '# t', '', '真死链 [x](nope/missing.md)', '', '```', '围栏内 [y](nope2.md)', '```',
    ]))
    got = dead(d)
    names = [g[2] for g in got]
    ok1 = 'nope/missing.md' in names
    ok2 = 'nope2.md' not in names
    io.open(os.path.join(d, 'b.md'), 'w', encoding='utf-8').write(chr(10).join([
        '# t2', '', '别人模板占位符 [Title](URL) 不算死链', '但 [x2](nope3.md) 必须点名',
    ]))
    n3 = [g[2] for g in dead(d)]
    ok3 = ('URL' not in n3) and ('nope3.md' in n3)
    shutil.rmtree(d, ignore_errors=True)
    print('SELFTEST 反例(围栏外须点名)=%s 正例(围栏内须不点名)=%s 占位符腿(URL不点名且同卷真链点名)=%s' % (ok1, ok2, ok3))
    return ok1 and ok2 and ok3

if '--selftest' in sys.argv:
    sys.exit(0 if selftest('.') else 1)
root = sys.argv[1]
res = dead(root)
print('md=%d 围栏外可疑相对链接=%d' % (len([1 for dp, _d, fn in os.walk(root) for f in fn if f.endswith('.md') and (os.sep + '.git' + os.sep) not in dp + os.sep]), len(res)))
for rel, ln, u, norm in res[:40]:
    print('  %s:%d -> %s [=%s]' % (rel, ln, u, norm))
