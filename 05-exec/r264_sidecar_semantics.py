# -*- coding: utf-8 -*-
'''sidecar semantics classifier (R263-3, landed r264).

Why: 55 local skills declare an .upstream sidecar, but the sidecar semantics are NOT uniform -
measured r263: obra/superpowers holds 5 skills at skills/<slug> (same lineage), anthropics/skills
holds 11 at skills/<slug> (monorepo but still same lineage per skill), Shubhamsaboo/awesome-llm-apps
is a curated collection, microsoft/playwright-mcp is a tool, gastownhall/beads is a dependency.
Reading BEHIND uniformly would tell the reader this skill has a newer version to adopt, which is
only true for the same-lineage class.

How the class is decided (most specific rule first, every row records which rule fired):
  SAME_LINEAGE  the sidecar declares a path AND that path exists in the upstream tree => the
                upstream really holds this very skill files; version comparison is meaningful.
  COLLECTION    no usable path, and the repo serves >= 3 local skills (or its name looks like a
                list/hub) => the pointer names a collection, not this skill newer version.
  TOOL          no usable path and the repo is a tool/MCP/server by name or description.
  DEPENDENCY    no usable path and the repo is a library/sdk/framework by description.
  UNKNOWN       none of the above matched: handed to a human read instead of being guessed.

Read-only: reads D:/global_skills/*/.upstream and calls gh api. Never writes the managed root.
Exit codes: 0 wrote face / 1 no usable evidence / 2 input face unavailable.
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
OUT_DEFAULT = os.path.join(BENCH, 'r264_sidecar_semantics.json')
FACE_IN = os.path.join(BENCH, 'r263_declared_upstream_face.json')
sys.path.insert(0, HERE)

# 单源借用两样东西：sidecar 解析（r114 是权威实现）+ 带瞬断重试的 gh（r263 面脚本引入的语义）。
import r114_replacement_scan as _R114
import r263_declared_upstream_face as _FACE
parse_sidecar = _R114.parse_sidecar
gh = _FACE.gh

RE_COLLECTION_NAME = re.compile(r'awesome|collection|^skills$|-skills$|hub$|list$', re.I)
RE_TOOL = re.compile(r'mcp|server|cli$|-cli|playwright|browser|inspector', re.I)
RE_DEP = re.compile(r'library|sdk|framework|engine|database|runtime|plugin|toolkit', re.I)


def classify(has_path, path_exists, shared_n, repo_name, repo_desc):
    '''返回 (类, 判据名, 证据 dict)。规则顺序即优先级：最具体的证据先行。

    为什么把 path_in_tree 放第一位：既有 48/55 行声明了 path，且实测 anthropics/skills 这类
    monorepo 里 skills/<slug> 就是**这一件的本体**（11 件共用该仓）—— 若先按仓判合集，就会把
    同源件误降级成「只是引用了一个合集」，版本落后就白读了。'''
    name, desc = repo_name or '', repo_desc or ''
    ev = {'has_path': bool(has_path), 'path_exists': None if path_exists is None else bool(path_exists),
          'shared_local_n': int(shared_n or 0), 'name': name, 'desc_hit': None}
    if has_path and path_exists:
        return 'SAME_LINEAGE', 'path_in_tree', ev
    if int(shared_n or 0) >= 3:
        return 'COLLECTION', 'serves>=3_local_skills', ev
    if RE_COLLECTION_NAME.search(name):
        return 'COLLECTION', 'name_looks_like_list', ev
    hit = RE_TOOL.search(name) or RE_TOOL.search(desc)
    if hit:
        ev['desc_hit'] = hit.group(0)
        return 'TOOL', 'tool_name_or_desc', ev
    hit = RE_DEP.search(desc)
    if hit:
        ev['desc_hit'] = hit.group(0)
        return 'DEPENDENCY', 'library_desc', ev
    return 'UNKNOWN', 'no_rule_matched', ev


def repo_meta(repo):
    '''一次调用取 name/description/topics；失败返回 (None, 原因) 供调用方显形。'''
    out, err = gh(['api', 'repos/' + repo])
    time.sleep(0.6)
    if err:
        return None, err
    try:
        d = json.loads(out)
    except ValueError as exc:
        return None, 'json:%r' % (exc,)
    return {'name': d.get('name') or repo.split('/')[-1],
            'description': d.get('description') or '',
            'topics': d.get('topics') or [],
            'stars': d.get('stargazers_count')}, None


def path_exists(repo, path):
    '''用 contents 端点验证声明路径是否真在上游树里；404 = 明确不存在（不重试），其余失败 = 不可知。

    返回 True/False/None：None 表示「取不到，不知道」，调用方据此走 UNKNOWN 而不是当成不存在。'''
    if not path:
        return None
    out, err = gh(['api', 'repos/%s/contents/%s' % (repo, path.rstrip('/'))])
    time.sleep(0.6)
    if err is None:
        return True
    if 'HTTP 404' in err or 'Not Found' in err:
        return False
    return None


def build_face(limit=None, quiet=False):
    if not os.path.isfile(FACE_IN):
        print('[SEM:UNVERIFIED] upstream face missing: %s (R247)' % FACE_IN)
        return 2
    try:
        face = json.load(io.open(FACE_IN, encoding='utf-8-sig'))
    except Exception as exc:
        print('[SEM:UNVERIFIED] face unreadable: %r' % (exc,))
        return 2
    rows_in = face.get('rows') or []
    if not rows_in:
        print('[SEM:UNVERIFIED] face has no rows')
        return 2
    if limit:
        rows_in = rows_in[:limit]
    shared = {}
    for r in rows_in:
        shared[r['upstream_repo']] = shared.get(r['upstream_repo'], 0) + 1
    meta_cache, path_cache, out = {}, {}, []
    for r in rows_in:
        repo = r['upstream_repo']
        path = r.get('upstream_path')
        if repo not in meta_cache:
            m, err = repo_meta(repo)
            meta_cache[repo] = (m, err)
        m, err = meta_cache[repo]
        pkey = (repo, path or '')
        if pkey not in path_cache:
            path_cache[pkey] = path_exists(repo, path)
        pe = path_cache[pkey]
        cls, rule, ev = classify(bool(path), pe, shared.get(repo, 1),
                                 (m or {}).get('name'), (m or {}).get('description'))
        rec = {'skill': r['skill'], 'upstream_repo': repo, 'upstream_path': path,
               'local_version': r.get('local_version'), 'upstream_version': r.get('upstream_version'),
               'rel': r.get('rel'), 'semantics': cls, 'rule': rule, 'evidence': ev,
               'meta_error': err, 'path_probe': ('unknown' if pe is None else ('exists' if pe else 'absent'))}
        out.append(rec)
        if not quiet:
            print('  %-30s %-14s %-22s %s' % (r['skill'], cls, rule, repo))
    by_cls = {}
    for r in out:
        by_cls[r['semantics']] = by_cls.get(r['semantics'], 0) + 1
    same = [r for r in out if r['semantics'] == 'SAME_LINEAGE']
    doc = {'schema': 'sidecar-semantics-v1',
           'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
           'provenance_cmd': 'python 05-exec/r264_sidecar_semantics.py',
           'rule': 'R263-3: classify .upstream sidecars so BEHIND is only read as a version gap for SAME_LINEAGE',
           'face_in': os.path.relpath(FACE_IN, ROOT),
           'rows_n': len(out),
           'by_semantics': by_cls,
           'same_lineage_behind': sorted(r['skill'] for r in same if r.get('rel') == 'BEHIND'),
           'rows': out}
    return doc


def selftest():
    rows = []

    def ck(name, cond, detail=''):
        rows.append((bool(cond), name, str(detail)[:150]))
        print('%-4s %s%s' % ('PASS' if cond else 'FAIL', name, '' if cond else '  <-- got: ' + str(detail)[:110]))

    ck('t1 path declared and present => SAME_LINEAGE',
       classify(True, True, 11, 'skills', '') [0] == 'SAME_LINEAGE')
    ck('t2 no path but serves 11 local skills => COLLECTION',
       classify(False, None, 11, 'skills', '') [0] == 'COLLECTION')
    ck('t3 name looks like a list => COLLECTION',
       classify(False, None, 1, 'awesome-llm-apps', 'curated list') [0] == 'COLLECTION')
    ck('t4 tool name => TOOL', classify(False, None, 1, 'playwright-mcp', 'browser automation MCP') [0] == 'TOOL')
    ck('t5 library description => DEPENDENCY',
       classify(False, None, 1, 'beads', 'a library for task graphs') [0] == 'DEPENDENCY')
    ck('t6 nothing matches => UNKNOWN (never guessed as same lineage)',
       classify(False, None, 1, 'weird-repo', 'no idea') [0] == 'UNKNOWN')
    ck('t7 path declared but ABSENT upstream => not SAME_LINEAGE',
       classify(True, False, 1, 'some-repo', '') [0] != 'SAME_LINEAGE')
    ck('t8 unknown path probe (None) must NOT count as present',
       classify(True, None, 1, 'some-repo', '') [0] != 'SAME_LINEAGE')

    def mutated(has_path, path_exists, shared_n, name, desc):
        if int(shared_n or 0) >= 3 or RE_COLLECTION_NAME.search(name or ''):
            return 'COLLECTION'
        return classify(has_path, path_exists, shared_n, name, desc)[0]

    ck('t9 mutation (collection rule first) breaks t1 => ordering carries weight',
       mutated(True, True, 11, 'skills', '') == 'COLLECTION')
    n_fail = sum(1 for ok, _, _ in rows if not ok)
    print('[SELFTEST:%s] legs=%d fail=%d' % ('PASS' if not n_fail else 'FAIL', len(rows), n_fail))
    return not n_fail


def main():
    ap = argparse.ArgumentParser(prog='r264_sidecar_semantics.py')
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
    print('[SEM:FACE] rows=%d by_semantics=%s same_lineage_behind=%d'
          % (doc['rows_n'], json.dumps(doc['by_semantics']), len(doc['same_lineage_behind'])))
    print('JSON ->', args.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
