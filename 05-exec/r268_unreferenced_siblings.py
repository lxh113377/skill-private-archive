# -*- coding: utf-8 -*-
'''unreferenced on-disk siblings face (R267-1, landed r268).

Why: r266 and r267 each hit the same defect class from opposite ends - a file (or a whole package)
was present on disk but its SKILL.md never pointed at it. test-driven-development carried
writing-good-tests.md (8268B) with zero references; frontend-slides carries bold-template-pack
(deck-stage.js, fixed 1920x1080) and its SKILL.md still describes the old Viewport Fitting
paradigm, so the agent cannot even see the package. In both cases the content existed and was
unreachable, which is a documentation defect that no version comparison can surface.

What it measures, per local skill:
  denominator = sibling files that actually exist on disk (recursive), excluding SKILL.md itself,
                dot-files and the exemption set (LICENSE / NOTICE / .upstream);
  numerator   = the subset that SKILL.md never points at, where 'points at' is one of three
                explicit forms (any hit counts as referenced):
                  REF_BY_PATH     the file relative path appears verbatim in SKILL.md text;
                  REF_BY_BASENAME the bare file name appears;
                  REF_BY_DIRNAME  the name of any ancestor directory appears (a package mentioned
                                  as a whole means its members are reachable, not orphaned).

Read-only: reads D:/global_skills, writes one JSON under 06-benchmark/.
Exit codes: 0 wrote face / 2 skills root unavailable.
'''
import argparse
import io
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, '06-benchmark')
SKILLS_ROOT = os.environ.get('ZIJIAN_SKILLS_ROOT', 'D:/global_skills')
OUT_DEFAULT = os.path.join(BENCH, 'r268_unreferenced_siblings.json')

EXEMPT_NAMES = {'LICENSE', 'NOTICE', '.upstream', 'SKILL.md'}
# 平台元数据类豁免（R272-1 裁定，r273 落地）：meta.json / _skillhub_meta.json / .claude-plugin/* 由平台
# 读取（作者、图标、上架描述），不是给代理读的技能内容 ⇒ 「SKILL.md 没指向它」不构成缺陷。
# 一手依据：frontend-slides 与 html-ppt 两件都有 meta.json、两件的 SKILL.md 对它的提及数都是 0（同族一致）。
EXEMPT_PLATFORM = {'meta.json', '_skillhub_meta.json'}
EXEMPT_PLATFORM_DIRS = ('.claude-plugin/',)
RE_PATH_TOKEN = re.compile(r'[A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|json|txt|py|css|js|html|sh|ya?ml)')
FILE_EXTS = ('.md', '.json', '.txt', '.py', '.css', '.js', '.html', '.sh', '.yaml', '.yml')


def referenced_tokens(text):
    '''抽出 SKILL.md 里出现的所有「带扩展名的路径样式 token」。

    为什么用这个抓法而不是只抓 markdown 链接：本树实测的引用形态不止一种 —— 有 `[x](references/y.md)`
    这种链接，也有反引号内联路径（frontend-slides 第 328 行就是），还有裸名出现。
    统一抽「任何以已知扩展名结尾的路径样式串」，三种写法都能覆盖，且不依赖 markdown 结构。'''
    return set(m.strip() for m in RE_PATH_TOKEN.findall(text or ''))


def classify(relpath, basename, dirnames, toks, text):
    '''返回 (是否被引用, 命中规则名)。规则顺序即优先级，最具体者先。

    为什么把「父目录名被提及」也算引用：整包被 SKILL.md 提到（如 bold-template-pack）时，包内文件
    是可达的，不该报成孤儿；若不做这条，度量会把正常的分卷包集体误报，读数即失去意义。'''
    if relpath in text:
        return True, 'REF_BY_PATH'
    for tok in toks:
        if tok.replace(chr(92), '/').endswith(relpath):
            return True, 'REF_BY_PATH_BACKSLASH'
    if basename in text:
        return True, 'REF_BY_BASENAME'
    if dirnames:
        parent = dirnames[-1]
        if len(parent) >= 3 and parent in text:
            return True, 'REF_BY_PARENT_DIR'
    for d in dirnames[:-1]:
        if len(d) >= 3 and d in text:
            return True, 'WEAK_ANCESTOR_DIR_ONLY'
    return False, 'UNREFERENCED'


def walk_files(skill_dir):
    '''列该 skill 目录内的在盘文件（相对路径），排除豁免件与点开头件。返回 (rows, exempt_n)。

    返回两个值而不是只返回清单：分母必须能分开报「豁免掉多少」，否则读者无法判断未引用数是
    被豁免规则压下来的还是真的少（R260-9 点名分母同族）。'''
    rows, exempt = [], 0
    for dirpath, dirnames, filenames in os.walk(skill_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in ('__pycache__', 'node_modules')]
        for fn in filenames:
            if fn in EXEMPT_NAMES or fn.lower() in ('license', 'notice'):
                exempt += 1
                continue
            # 平台元数据类：按名或其目录前缀豁免（R272-1 裁定）—— 与上面同列，便于「豁免了多少」可读。
            _rel_head = os.path.relpath(os.path.join(dirpath, fn), skill_dir).replace(os.sep, '/')
            if fn in EXEMPT_PLATFORM or _rel_head.startswith(EXEMPT_PLATFORM_DIRS):
                exempt += 1
                continue
            if fn.startswith('.'):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), skill_dir).replace(os.sep, '/')
            if rel == 'SKILL.md':
                continue
            rows.append(rel)
    return sorted(rows), exempt


def build_face(limit=None, quiet=False):
    if not os.path.isdir(SKILLS_ROOT):
        print('[UNREF:UNVERIFIED] skills root unavailable: %s (R247)' % SKILLS_ROOT)
        return 2
    slugs = sorted(d for d in os.listdir(SKILLS_ROOT) if os.path.isdir(os.path.join(SKILLS_ROOT, d)))
    if limit:
        slugs = slugs[:limit]
    rows, n_clean, n_dirty = [], 0, 0
    for slug in slugs:
        d = os.path.join(SKILLS_ROOT, slug)
        sk = os.path.join(d, 'SKILL.md')
        if not os.path.isfile(sk):
            rows.append({'slug': slug, 'state': 'NO_SKILL_MD', 'present_n': 0, 'unreferenced': [], 'exempt_n': 0})
            continue
        text = io.open(sk, encoding='utf-8', errors='replace').read()
        toks = referenced_tokens(text)
        files, exempt = walk_files(d)
        unreferenced, rules = [], {}
        for rel in files:
            base = os.path.basename(rel)
            dirs = [p for p in rel.split('/')[:-1]]
            ref, rule = classify(rel, base, dirs, toks, text)
            rules[rule] = rules.get(rule, 0) + 1
            # 常规档分子：这一行曾被我的补丁整段替换掉 ⇒ 那次跑出 normal=0 的假读数，
            #   靠「strict 16 与复核一致、normal 却是 0」这种自相矛盾读出问题。
            if not ref:
                unreferenced.append(rel)
        # 双口径（与独立复核对账后的处置）：strict = 父目录名必须以**路径形态**（parent + 斜杠）出现才算
        #   可达。常规口径认裸名提及。两者都落盘 ⇒ 分歧从「不一致」变成「已披露的两种读数」。
        strict_unref = []
        for rel2 in files:
            base2 = os.path.basename(rel2)
            dirs2 = [p for p in rel2.split('/')[:-1]]
            ref2 = (rel2 in text) or (base2 in text)
            if not ref2 and dirs2 and len(dirs2[-1]) >= 3 and (dirs2[-1] + '/') in text:
                ref2 = True
            if not ref2:
                strict_unref.append(rel2)
        rec = {'slug': slug, 'state': 'OK', 'present_n': len(files), 'exempt_n': exempt,
               'unreferenced_n': len(unreferenced), 'unreferenced': unreferenced,
               'unreferenced_strict_n': len(strict_unref), 'unreferenced_strict': strict_unref,
               'rule_hist': rules, 'skill_md_bytes': len(text.encode('utf-8'))}
        rows.append(rec)
        if unreferenced:
            n_dirty += 1
        else:
            n_clean += 1
        if not quiet and unreferenced:
            print('  %-34s present=%-3d unreferenced=%-2d %s' % (
                  slug, len(files), len(unreferenced), ', '.join(unreferenced[:4])))
    total_unref = sum(r.get('unreferenced_n') or 0 for r in rows)
    doc = {'schema': 'unreferenced-siblings-v1',
           'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
           'provenance_cmd': 'python 05-exec/r268_unreferenced_siblings.py',
           'rule': 'R267-1: a file on disk that SKILL.md never points at is unreachable content',
           'skills_root': SKILLS_ROOT,
           'skills_n': len(rows),
           'skills_with_unreferenced_n': n_dirty,
           'skills_clean_n': n_clean,
           'unreferenced_total_n': total_unref,
           'unreferenced_strict_total_n': sum(r.get('unreferenced_strict_n') or 0 for r in rows),
           'caliber_note': 'dual caliber: normal treats a bare immediate-parent dir mention as reachable; strict requires that mention to be path-shaped (parent + slash). The r268 independent check landed local-mineru on the strict side (+12 files).',
           'exemption_names': sorted(EXEMPT_NAMES),
           'rows': rows}
    return doc


def selftest():
    rows = []

    def ck(name, cond, detail=''):
        rows.append((bool(cond), name, str(detail)[:150]))
        print('%-4s %s%s' % ('PASS' if cond else 'FAIL', name, '' if cond else '  <-- got: ' + str(detail)[:110]))

    # 用临时目录造夹具：判据必须能在不依赖真实受管根的情况下证明自己有牙。
    import tempfile
    tmp = tempfile.mkdtemp(prefix='unref_st_')
    def mk(rel, body='x'):
        p = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        io.open(p, 'w', encoding='utf-8').write(body)
        return p
    mk('references/by_path.md'); mk('sub/by_basename.md'); mk('pack/inner.js'); mk('orphan.md')
    mk('LICENSE'); mk('NOTICE'); mk('.upstream')
    text_path = 'see references/by_path.md here'
    text_base = 'see by_basename.md here'
    text_dir = 'the pack is described here'
    text_none = 'nothing at all'
    files, exempt = walk_files(tmp)
    ck('t1 path form is recognised', classify('references/by_path.md', 'by_path.md', ['references'],
                                            referenced_tokens(text_path), text_path) == (True, 'REF_BY_PATH'))
    ck('t2 basename form is recognised',
       classify('sub/by_basename.md', 'by_basename.md', ['sub'], referenced_tokens(text_base), text_base)
       == (True, 'REF_BY_BASENAME'))
    ck('t3 parent-dir mention counts as reachable',
       classify('pack/inner.js', 'inner.js', ['pack'], referenced_tokens(text_dir), text_dir)
       == (True, 'REF_BY_PARENT_DIR'))
    ck('t4 no mention => UNREFERENCED (never defaulted to referenced)',
       classify('orphan.md', 'orphan.md', [], referenced_tokens(text_none), text_none)
       == (False, 'UNREFERENCED'))
    ck('t5 exemptions are out of the denominator (LICENSE/NOTICE/.upstream)', exempt == 3 and 'LICENSE' not in files, exempt)
    ck('t6 walk finds the 4 real files (any type counts)', sorted(files) == sorted(['orphan.md', 'pack/inner.js', 'references/by_path.md', 'sub/by_basename.md']), files)

    def mutated(rel, base, dirs, toks, text):
        for t in toks:
            if t == rel or t.endswith('/' + rel):
                return True, 'REF_BY_PATH'
        for t in toks:
            if os.path.basename(t) == base:
                return True, 'REF_BY_BASENAME'
        return False, 'UNREFERENCED'

    ck('t7 mutation (dirname rule removed) breaks t3 => t3 carries weight',
       mutated('pack/inner.js', 'inner.js', ['pack'], referenced_tokens(text_dir), text_dir)
       == (False, 'UNREFERENCED'))
    ck('t9 remote-ancestor mention lands in the WEAK bucket (not reachable)',
       classify('scripts/mineru_ov/client.py', 'client.py', ['scripts', 'mineru_ov'], referenced_tokens('see scripts/ for tools'), 'see scripts/ for tools')
       == (True, 'WEAK_ANCESTOR_DIR_ONLY'))
    # 真实受管根实例（有则验，无则记 SKIP，绝不当成通过）
    fs_dir = os.path.join(SKILLS_ROOT, 'frontend-slides')
    if os.path.isdir(fs_dir):
        fs_files, _e = walk_files(fs_dir)
        fs_text = io.open(os.path.join(fs_dir, 'SKILL.md'), encoding='utf-8', errors='replace').read()
        toks = referenced_tokens(fs_text)
        bang = [f for f in fs_files if 'bold-template-pack' in f]
        if not bang:
            ck('t8 full-repo: bold-template-pack files exist (else this leg is vacuous)', False, 'no files found')
        else:
            unref = [f for f in bang if not classify(f, os.path.basename(f), [p for p in f.split('/')[:-1]], toks, fs_text)[0]]
            # 这条腿在 r268 立时断言「包内件仍未被引用」（当时的真缺陷）。r269 补指针 + r272 范式迁移后该缺陷已修，
        # 故 r273 把它翻转成**回归守卫**：现在必须全部被引用；一旦有人再丢指针，这条腿立刻红（不再是恒真断言）。
        ck('t8 full-repo: frontend-slides package files are now referenced (r267 gap fixed; guard against regression)',
           len(unref) == 0 and len(bang) > 0, 'unref=%s bang=%d' % (unref[:3], len(bang)))
    else:
        print('SKIP t8 full-repo leg (frontend-slides absent)')
    n_fail = sum(1 for ok, _, _ in rows if not ok)
    print('[SELFTEST:%s] legs=%d fail=%d' % ('PASS' if not n_fail else 'FAIL', len(rows), n_fail))
    return not n_fail


def main():
    ap = argparse.ArgumentParser(prog='r268_unreferenced_siblings.py')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--json', dest='out', default=OUT_DEFAULT)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return 0 if selftest() else 1
    doc = build_face(args.limit or None, args.quiet)
    if isinstance(doc, int):
        return doc
    tmp = args.out + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline=chr(10)) as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, args.out)
    print('[UNREF:FACE] skills=%d with_unreferenced=%d clean=%d unreferenced_total=%d'
          % (doc['skills_n'], doc['skills_with_unreferenced_n'], doc['skills_clean_n'], doc['unreferenced_total_n']))
    print('JSON ->', args.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
