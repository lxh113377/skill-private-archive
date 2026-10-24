# -*- coding: utf-8 -*-
'''r217_shared_stage.py — 共享卷的 hunk 级代提交护栏（r217 自抓后新建）。

一手教训：r217 我按 pathspec 跑 git add -- memory/07-next-steps.md，而那卷相对 HEAD 的 10 行
新增全是并行会话的 R217-2（我自己的插入已被撞号预检跳过，那卷里我一行都没有）。结果他们的工作
以我的提交信息入库：内容没丢、可回滚，但违反 R269/红线5 同族规矩。根因：我的暂存检查只做到
文件级（路径名像不像别人的件），没做到 hunk 级（这次新增行里是不是我写的东西）。

机械化：共享台账/报告卷，只有当「我自己本轮的条目键」确实出现在该卷相对 HEAD 的新增行里才
stage；命中时若还有他人新增行，打印携带数量并强制要求在提交信息里声明（git add 是整文件粒度，
共享卷上「只提交自己那几行」不可达 ⇒ 正解是让携带变成声明出来的事实，不是假装能回避）。

用法: python 05-exec/r217_shared_stage.py <相对路径> --must-contain '<我的条目键>'
     python 05-exec/r217_shared_stage.py --selftest
退出码: 0 = STAGED / SKIP / NOCHANGE 三种正常处置；2 = 用错（文件缺失、git 失败、自检不过）。
'''
import argparse
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def git(root, *x):
    r = subprocess.run(['git', '-C', root] + list(x), capture_output=True,
                       text=True, encoding='utf-8', errors='replace', timeout=300)
    return r.returncode, ((r.stdout or '') + (r.stderr or ''))


def added_lines(root, rel, key):
    """相对 HEAD 的新增行；返回 (全部新增行, 含 key 的行)。git 失败返回 (None, None)。"""
    rc, diff = git(root, '-c', 'core.quotepath=false', 'diff', 'HEAD',
                   '--unified=0', '--', rel)
    if rc != 0:
        return None, None
    add = [l[1:] for l in diff.splitlines()
           if l.startswith('+') and not l.startswith('+++')]
    return add, [l for l in add if key in l]


def decide(root, rel, key):
    """返回 (处置码, 说明)。处置 = STAGED / SKIP / NOCHANGE / ERROR。"""
    p = os.path.join(root, rel.replace('/', os.sep))
    if not os.path.isfile(p):
        return 2, 'ERROR 文件不存在 ' + rel
    add, mine = added_lines(root, rel, key)
    if add is None:
        return 2, 'ERROR git diff 失败'
    if not add:
        return 0, 'NOCHANGE 相对 HEAD 无新增行'
    if mine:
        rc2, o2 = git(root, 'add', '--', rel)
        if rc2 != 0:
            return 2, 'ERROR git add 失败 rc=%d %s' % (rc2, o2.strip()[:120])
        other = len(add) - len(mine)
        msg = 'STAGED 新增 %d 行，含我的键 %d 行' % (len(add), len(mine))
        if other:
            msg += ('；⚠ 同时携带他人未提交新增行 %d 行（git add 是整文件粒度，共享卷上'
                    '只提交自己那几行不可达）⇒ 必须在提交信息里声明代带，不得装作没发生'
                    % other)
        return 0, msg
    heads = [l.strip()[:44] for l in add if l.strip().startswith('- [ ]')]
    msg = ('SKIP 有 %d 行未提交改动但不含我的键 %s ⇒ 留给其作者，不代提交'
           % (len(add), key))
    for h in heads[:2]:
        msg += chr(10) + '    卷里的条目头: ' + h
    return 0, msg


def selftest():
    """两向自证：在 TEMP 里造一个一次性 git 仓（隔离，绝不碰真仓），验证 SKIP 与 STAGED 都真触发。

    为什么不在真仓自测：真台账的未提交行是并行会话的在途工作，拿它做实验等于动别人的活；
    而放 gitignore 命中的目录里，未跟踪件根本不出现在 diff HEAD 面（实测 NOCHANGE，假通过）。
    """
    repo = os.path.join(os.environ.get('TEMP', '/tmp'), 'stageguard_selftest_repo')
    os.makedirs(repo, exist_ok=True)
    ident = ['-c', 'user.name=t', '-c', 'user.email=t@t'] 
    git(repo, *(ident + ['init', '-q']))
    rel = 'ledger.md'
    base = os.path.join(repo, 'ledger.md')
    io.open(base, 'w', encoding='utf-8', newline=chr(10)).write('- [ ] HEADLINE' + chr(10))
    git(repo, *(ident + ['add', '--', rel]))
    git(repo, *(ident + ['commit', '-q', '-m', 'seed']))
    # 只改工作树：先塞他人一行（未提交），验 SKIP
    io.open(base, 'a', encoding='utf-8', newline='').write('- [ ] **X-other** 他人条目' + chr(10))
    c1, m1 = decide(repo, rel, '**X-mine（自测我的）**')
    ok_skip = c1 == 0 and m1.startswith('SKIP')
    # 再补我的一行，验 STAGED 且报出携带他人行数
    io.open(base, 'a', encoding='utf-8', newline='').write('- [ ] **X-mine（自测我的）** 我的条目' + chr(10))
    c2, m2 = decide(repo, rel, '**X-mine（自测我的）**')
    ok_stage = c2 == 0 and m2.startswith('STAGED') and '携带他人' in m2
    # 第三向：卷完全干净 ⇒ NOCHANGE（不许误报）
    git(repo, *(ident + ['add', '--', rel]))
    git(repo, *(ident + ['commit', '-q', '-m', 'second']))
    c3, m3 = decide(repo, rel, '**X-mine（自测我的）**')
    ok_clean = c3 == 0 and m3.startswith('NOCHANGE')
    print('[SELFTEST] SKIP   = %s :: %s' % (ok_skip, m1.split(chr(10))[0][:96]))
    print('[SELFTEST] STAGED = %s :: %s' % (ok_stage, m2[:120]))
    print('[SELFTEST] NOCHANGE = %s :: %s' % (ok_clean, m3[:80]))
    if ok_skip and ok_stage and ok_clean:
        print('[STAGEGUARD:PASS] 三向都有牙')
        return 0
    print('[STAGEGUARD:FAIL] 护栏自身没牙，不得投入使用')
    return 2


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('file', nargs='?')
    ap.add_argument('--must-contain', dest='key')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.file or not args.key:
        print('用法: r217_shared_stage.py <相对路径> --must-contain <键> | --selftest')
        return 2
    code, msg = decide(ROOT, args.file, args.key);
    tag = msg.split(' ')[0]
    print('[STAGE:%s] %s :: %s' % (tag, args.file, msg))
    return code


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())