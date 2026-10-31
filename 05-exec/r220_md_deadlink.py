# -*- coding: utf-8 -*-
"""围栏感知死链扫描 + 内建正反两腿自证。"""
import fnmatch, io, os, re, subprocess, sys

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

def shipping_face(root):
    """发布面 = 一次 clone 之后会存在的文件（git 跟踪 + 未跟踪但未被 ignore）。

    为什么要换面（r261 一手）：原判据 os.walk 整个工作区，_temp/ 里的 966 份草稿 md
    （照抄上游 README 的卡片、探针、夹具）全被当成品扫 ⇒ 本轮实测 336 条死链 **100%
    落在 _temp/**、发布面 0 条，整扇门被永不随克隆发布的草稿判红。恒红源与恒绿源
    同样没有信息量（06-constraints.part20 D-A）：真故障会被淹在这类固定噪声里。

    返回 (files, dirs, None) 或 (None, None, 原因)。**取不到面必须 UNVERIFIED**，
    禁退化成「扫全部」或「0 条 = 过」—— 那正是 R247 反对的零输入记绿。
    """
    try:
        # core.quotepath=false 是必须的（本仓多处 git 命令都带它）：默认配置下 git 会把非
        #   ASCII 文件名转成 "\345\205\250…" 八位引号形态，而 build() 用的是 os.walk 的真实名 ⇒
        #   过滤集里所有 CJK 路径都对不上，**存在**的中文报告链接会被误判成死链（r261 一手：
        #   我第一版就这么假红了 3 条，三条 ls-files --error-unmatch 全部 EXISTS|tracked）。
        a = subprocess.run(['git', '-c', 'core.quotepath=false', '-C', root, 'ls-files'],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        b = subprocess.run(['git', '-c', 'core.quotepath=false', '-C', root, 'ls-files',
                            '--others', '--exclude-standard'],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
    except Exception as e:
        return None, None, 'git 不可调用: %r' % (e,)
    if a.returncode != 0 or b.returncode != 0:
        return None, None, 'git rc=%s/%s' % (a.returncode, b.returncode)
    names = set()
    for src in (a.stdout, b.stdout):
        for ln in (src or '').splitlines():
            s = ln.strip().replace(chr(92), '/')
            if s:
                names.add(s)
    if not names:
        return None, None, '发布面为空（既无跟踪件也无未跟踪非 ignore 件）'
    files, dirs = build(root)
    keep_f = set(x for x in files if x in names)
    keep_d = set(dirs) | set('/'.join(x.split('/')[:-1]) for x in keep_f if '/' in x)
    return keep_f, keep_d, None


def dead(root, face=None):
    files, dirs = build(root) if face is None else face
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

def facetest():
    """发布面自身的正反两腿（r261，D-A：改判据必须当场证明它还能红）。

    怎么运作：在临时目录里建一个**一次性 scratch git 仓**（只 git init + git add 填索引，
    不 commit、不碰任何项目仓），造三种件：
      · 跟踪件 a.md 带真死链              ⇒ 必须点名（面有牙）
      · 跟踪件中文名的目标存在            ⇒ 必须不点名（quotepath 编码坑回归腿：
                                            git 默认把非 ASCII 名转八位引号，第一版就假红 3 条）
      · _temp/ 草稿件带死链              ⇒ 必须不点名（草稿永不随克隆发布，不参与判红）
    返回三条腿是否全对。
    """
    import tempfile, shutil
    d = tempfile.mkdtemp()
    try:
        for c in (["init", "-q"], ["add", "a.md", chr(26032) + chr(26118) + chr(25253) + chr(21578) + ".md"]):
            subprocess.run(["git"] + c, cwd=d, capture_output=True)
        io.open(os.path.join(d, "a.md"), "w", encoding="utf-8").write(
            chr(10).join(["# a", "", chr(27491) + chr(27573) + " [x](nope/missing.md)",
                           chr(27491) + chr(27573) + " [y](" + chr(26032) + chr(26118) + chr(25253) + chr(21578) + ".md)"]))
        io.open(os.path.join(d, chr(26032) + chr(26118) + chr(25253) + chr(21578) + ".md"), "w",
                encoding="utf-8").write("# target" + chr(10))
        # 草稿必须同时被 gitignore：发布面 = 跟踪件 + **未被 ignore** 的未跟踪件，所以只建目录
        #   不写 .gitignore 的话草稿会合法地留在发布面里、腿三判红是**用例错**而非判据错
        #   （r261 首跑实测正是如此：FACETEST 草稿不判红=False）。
        io.open(os.path.join(d, ".gitignore"), "w", encoding="utf-8").write("_temp/" + chr(10))
        subprocess.run(["git", "add", ".gitignore"], cwd=d, capture_output=True)
        os.makedirs(os.path.join(d, "_temp"), exist_ok=True)
        io.open(os.path.join(d, "_temp", "draft.md"), "w", encoding="utf-8").write(
            chr(10).join(["# draft", "", "[z](nowhere_in_draft.md)"]))
        subprocess.run(["git", "-c", "core.quotepath=false", "add", "a.md",
                        chr(26032) + chr(26118) + chr(25253) + chr(21578) + ".md"], cwd=d, capture_output=True)
        ff, fd, err = shipping_face(d)
        if ff is None:
            print("FACETEST 面取不到: %s" % err)
            return False
        res = [x for x in dead(d, (ff, fd))]
        got = set(x[2] for x in res)
        leg1 = "nope/missing.md" in got
        leg2 = (chr(26032) + chr(26118) + chr(25253) + chr(21578) + ".md") not in got
        leg3 = "nowhere_in_draft.md" not in got
        in_face = sum(1 for x in ff if x.endswith(".md"))
        print("FACETEST 跟踪死链点名=%s 中文目标不误伤=%s 草稿不判红=%s 面内md=%d" % (
              leg1, leg2, leg3, in_face))
        return leg1 and leg2 and leg3
    finally:
        shutil.rmtree(d, ignore_errors=True)


def count_md(root):
    n = 0
    for dp, _dn, fn in os.walk(root):
        if (os.sep + '.git' + os.sep) in (dp + os.sep):
            continue
        n += sum(1 for f in fn if f.endswith('.md'))
    return n

def main():
    import json, time
    args = sys.argv[1:]
    if '--selftest' in args:
        # 两件套：dead() 的围栏/占位符三腿 + 发布面的正反三腿，缺一即自证不成立
        ok = selftest('.') and facetest()
        sys.exit(0 if ok else 1)
    outp = None
    if '--json' in args:
        i = args.index('--json')
        if i + 1 >= len(args) or args[i + 1].startswith('-'):
            print('[GATE:deadlink-unverified] --json 缺输出路径'); sys.exit(2)
        outp = args[i + 1]
        args = args[:i] + args[i + 1:]
    pos = [a for a in args if not a.startswith('-')]
    if not pos:
        print('[GATE:deadlink-unverified] 无扫描根 ⇒ 无处可比不得判过（R247）'); sys.exit(2)
    root = pos[0]
    # 面 = 发布面（clone 后存在的件）。草稿面 _temp/ 不参与判红也不参与分母：
    #   打印的分母必须等于真正扫过的面，否则「md=N 死链=0」里的 N 是虚数（本仓 #32 形态）。
    face_files, face_dirs, err = shipping_face(root)
    if face_files is None:
        print('[GATE:deadlink-unverified] 发布面取不到（%s）⇒ 不得退化成扫全部或记 0 条过（R247）' % err)
        sys.exit(2)
    md = sum(1 for x in face_files if x.endswith('.md'))
    if md == 0:
        print('[GATE:deadlink-unverified] md=0 ⇒ 零输入不得记 PASS（R247）'); sys.exit(2)
    # r318 --exclude=前缀：上游字节快照证据件（_repro/**/evidence/**——其正文链接指向上游仓 sibling
    # 文件、单文件导入天然不可解）可划出判红面；**分母同步扣减**（md 计数=实扫面，防「md=N 死链=0」
    # 的 N 变虚数——本仓 #32 形态）。口子透明可审计：打印划出件数。除上游证据前缀外不得用来藏自家死链。
    excl = []
    for x in args:
        if x.startswith('--exclude='):
            excl = [q.strip().rstrip('/') for q in x.split('=', 1)[1].split(',') if q.strip()]
    if excl:
        # r329（R321-1 兑现）：把前缀匹配升级为 fnmatch，支持 `_repro/*/evidence/*` 这类通配形态。
        # 旧实现 `startswith(q)` 只能逐条硬写 rNN 目录名 ⇒ 下一轮新快照目录再红一次（r321 实测）。
        # 同时保留「必须真的划出东西」的透明打印与分母同步扣减（否则划出 0 件等于判据空转）。
        def _hit(path, pat):
            return fnmatch.fnmatch(path, pat) or path.startswith(pat)
        kept = [f for f in face_files if not any(_hit(f.replace(os.sep, '/'), q) for q in excl)]
        print('[EXCLUDE] 前缀=%s 划出 %d 件、留 %d 件（分母同步扣减）' % (excl, len(face_files) - len(kept), len(kept)))
        face_files = kept
        md = sum(1 for x in face_files if x.endswith('.md'))
    res = dead(root, (face_files, face_dirs))
    token = '[GATE:deadlink-pass]' if not res else '[GATE:deadlink-fail]'
    print('md=%d 死链=%d %s' % (md, len(res), token))
    for rel, ln, u, norm in res[:40]:
        print('  %s:%d -> %s [=%s]' % (rel, ln, u, norm))
    if outp:
        doc = {
            'schema': 'zijian-md-deadlink-v1',
            'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'root': os.path.abspath(root),
            'md_files': md,
            'face': 'shipping (git-tracked + non-ignored untracked); drafts excluded',
            'face_files_total': len(face_files),
            'dead': len(res),
            'items': [{'file': r, 'line': l, 'target': u, 'resolved': n} for r, l, u, n in res],
            'token': token,
            'status': 'PASS' if not res else 'FAIL',
            'note': '围栏感知 + 占位符跳过；三腿自证见 --selftest（反例/围栏/占位符）',
        }
        io.open(outp, 'w', encoding='utf-8', newline='').write(json.dumps(doc, ensure_ascii=False, indent=1))
        print('JSON ->', outp)
    sys.exit(0 if not res else 1)

if __name__ == '__main__':
    main()
