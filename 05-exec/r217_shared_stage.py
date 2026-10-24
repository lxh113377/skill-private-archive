# -*- coding: utf-8 -*-
'''r217_shared_stage.py — 共享卷的条目级代提交护栏（r217 自抓，r218 修归属口径）。

一手教训：r217 我按 pathspec 跑 git add -- memory/07-next-steps.md，而那卷相对 HEAD 的新增行
全是并行会话的条目（我自己那次的插入已被撞号预检跳过）。结果他们的工作以我的提交信息入库：
内容没丢、可回滚，但违反 R269/红线5 同族规矩。根因：我的暂存检查只做到文件级（路径名像不像
别人的件），没做到条目级（这次新增的条目是不是我写的）。

口径（r218 修正）：归属按**条目标题行**判，不按行含键判。一个条目只有首行含键、其余是续行与
裁决行；按行数算会把我的续行误记成他人行（r218 实测：护栏报携带他人 37 行，逐条精算后他人
条目标题实为 0 个）—— 那样声明出来的就是假事实。

处置：命中我的条目 ⇒ STAGED，并按他人**条目数**告警（git add 是整文件粒度，共享卷上无法只提交
自己那几行 ⇒ 必须在提交信息里具名声明代带）；未命中 ⇒ SKIP 留给作者，绝不 stage。

用法: python 05-exec/r217_shared_stage.py <相对路径> --must-contain <我的条目键>[ --must-contain ...]
     python 05-exec/r217_shared_stage.py --selftest
退出码: 0 = STAGED / SKIP / NOCHANGE；2 = 用错（文件缺失、git 失败、自检不过）。
'''
import argparse
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TITLE = '- [ ]'


def git(root, *x):
    r = subprocess.run(['git', '-C', root] + list(x), capture_output=True,
                       text=True, encoding='utf-8', errors='replace', timeout=300)
    return r.returncode, ((r.stdout or '') + (r.stderr or ''))


def added_lines(root, rel, keys):
    rc, diff = git(root, '-c', 'core.quotepath=false', 'diff', 'HEAD',
                   '--unified=0', '--', rel)
    if rc != 0:
        return None, None
    add = [l[1:] for l in diff.splitlines()
           if l.startswith('+') and not l.startswith('+++')]
    return add, [l for l in add if any(k in l for k in keys)]


def decide(root, rel, keys):
    if isinstance(keys, str):
        keys = [keys]
    p = os.path.join(root, rel.replace('/', os.sep))
    if not os.path.isfile(p):
        return 2, 'ERROR 文件不存在 ' + rel
    add, mine = added_lines(root, rel, keys)
    if add is None:
        return 2, 'ERROR git diff 失败'
    if not add:
        return 0, 'NOCHANGE 相对 HEAD 无新增行'
    titles = [l for l in add if l.strip().startswith(TITLE)]
    theirs = [l for l in titles if not any(k in l for k in keys)]
    if not mine:
        msg = ('SKIP 卷里有 %d 行未提交改动（条目标题 %d 个），但不含我的键 ⇒ 留给其作者，不代提交' % (len(add), len(theirs)))
        for h in theirs[:2]:
            msg += chr(10) + '    他人条目: ' + h.strip()[:44]
        return 0, msg
    rc2, o2 = git(root, 'add', '--', rel)
    if rc2 != 0:
        return 2, 'ERROR git add 失败 rc=%d %s' % (rc2, o2.strip()[:120])
    msg = 'STAGED 新增 %d 行；条目标题共 %d 个，我的 %d 个' % (len(add), len(titles), len(titles) - len(theirs))
    if theirs:
        msg += ('；⚠ 携带他人条目 %d 个（整文件 add 连带入库，共享卷上无法只提交自己那几行）⇒ 必须在提交信息里具名声明代带，不得装作没发生' % len(theirs))
        for h in theirs[:3]:
            msg += chr(10) + '    代带: ' + h.strip()[:44]
    return 0, msg


def selftest():
    repo = os.path.join(os.environ.get('TEMP', '/tmp'), 'stageguard_selftest_repo')
    ident = ['-c', 'user.name=t', '-c', 'user.email=t@t']
    git(repo, *(ident + ['init', '-q']))
    rel = 'ledger.md'
    base = os.path.join(repo, 'ledger.md')
    io.open(base, 'w', encoding='utf-8', newline=chr(10)).write('- [ ] HEADLINE' + chr(10))
    git(repo, *(ident + ['add', '--', rel]))
    git(repo, *(ident + ['commit', '-q', '-m', 'seed']))
    io.open(base, 'a', encoding='utf-8', newline='').write(
        '- [ ] **X-other** 他人条目' + chr(10))
    c1, m1 = decide(repo, rel, ['**X-mine**'])
    # 断言按实际措辞：SKIP 报「条目标题 N 个」（SKIP 分支无需区分归属，只报数）
    ok_skip = c1 == 0 and m1.startswith('SKIP') and '条目标题 1 个' in m1
    io.open(base, 'a', encoding='utf-8', newline='').write(
        '  我的条目续行' + chr(10) + '- [ ] **X-mine** 我的条目' + chr(10));
    io.open(base, 'a', encoding='utf-8', newline='').write(chr(10))
    c2, m2 = decide(repo, rel, ['**X-mine**'])
    ok_stage = (c2 == 0 and m2.startswith('STAGED') and '携带他人条目 1 个' in m2
                  and '我的 1 个' in m2)
    git(repo, *(ident + ['add', '--', rel]))
    git(repo, *(ident + ['commit', '-q', '-m', 'second']))
    c3, m3 = decide(repo, rel, ['**X-mine**'])
    ok_clean = c3 == 0 and m3.startswith('NOCHANGE')
    print('[SELFTEST] SKIP   = %s :: %s' % (ok_skip, m1.split(chr(10))[0][:96]))
    print('[SELFTEST] STAGED = %s :: %s' % (ok_stage, m2.split(chr(10))[0][:110]))
    print('[SELFTEST] NOCHANGE = %s :: %s' % (ok_clean, m3[:70]))
    if ok_skip and ok_stage and ok_clean:
        print('[STAGEGUARD:PASS] 三向都有牙（归属按条目标题判，续行不误记）')
        return 0
    print('[STAGEGUARD:FAIL] 护栏自身没牙，不得投入使用')
    return 2


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('file', nargs='?')
    ap.add_argument('--must-contain', dest='key', action='append')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.file or not args.key:
        print('用法: r217_shared_stage.py <相对路径> --must-contain <键> | --selftest')
        return 2
    code, msg = decide(ROOT, args.file, args.key)
    print('[STAGE:%s] %s :: %s' % (msg.split(' ')[0], args.file, msg))
    return code


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())