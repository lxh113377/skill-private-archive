# -*- coding: utf-8 -*-
"""declared-upstream face (R261-5, landed r263).

Why: requirement 2 says every local skill must be matched against its most relevant open-source
alternatives, and requirement 5 says the quarterly scan must also look for *version* movement.
The search-based candidate pool cannot answer either question for skills whose true upstream is
declared in a `.upstream` sidecar: a search by family keywords never returns the upstream repo
itself (measured r261: gstack -> garrytan/gstack and ppt-master -> hugohe3/ppt-master were both
absent from the emitted candidate face), so "is there a newer version of the thing we already
vendor" had no face at all.

What this face is NOT: it is not a replacement recommendation. The declared upstream is the same
lineage (a sync target), so mixing it into the candidate ranking would conflate replace-vs-follow.
It therefore reports a separate per-skill record: upstream repo, fetched maintenance state, local
version, upstream latest release, and a version-relationship verdict.

Read-only: it reads D:/global_skills/<skill>/.upstream and SKILL.md and calls gh api. It never
writes the managed root.

Exit codes match run_gates: 0 wrote the face / 1 no usable evidence / 2 input face unavailable.
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")
SKILLS_ROOT = os.environ.get("ZIJIAN_SKILLS_ROOT", "D:/global_skills")
GH = "gh"
CORE_SLEEP = 0.6
OUT_DEFAULT = os.path.join(BENCH, "r263_declared_upstream_face.json")

# （RE_VERSION 随本地 parse_version 一并移除：权威实现见 r114）


def gh(args, timeout=90, retries=2):
    # 瞬断重试（r263 一手）：同一面连跑两次，gh 的 EOF 会让 2-3 件的 release 取不到，
    #   于是同一件在两次运行里从 AHEAD 变 UNKNOWN_BOTH / UNKNOWN_UPSTREAM_RELEASE ⇒ 面的数字
    #   随网络抖动漂移，读者会误以为判定变了。重试使漂移只来自真实变化。
    # 只对传输层失败重试；HTTP 404 这类确定性结果立即返回，因为「上游本来就没有 release」是事实。
    last = None
    for _attempt in range(max(1, retries)):
        try:
            p = subprocess.run([GH] + args, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=timeout)
        except Exception as exc:
            last = "exc:%r" % (exc,)
            time.sleep(1.5)
            continue
        if p.returncode == 0:
            return p.stdout, None
        err = "rc=%d:%s" % (p.returncode, (p.stderr or "").strip()[:160])
        if "HTTP 404" in err or "Not Found" in err:
            return None, err
        last = err
        time.sleep(1.5)
    return None, last


# ---- 单源声明（r263）：解析与版本关系逻辑的权威实现放在 r114_replacement_scan（生产判据）。
# 为什么：本面与矩阵必须用同一套「什么是声明上游 / 什么算版本落后」，两处各写一份必然漂移
#   （R263/R280 同族：一个常量两处定义）。故此处只做别名导入。
# 我删死函数时把这段一起删了（锚点之间夹着它），真跑立刻 NameError —— 这属「删除前没列清
#   锚点之间内容」的错，本会话第二次；教训：删区间前先打印该区间全部内容并核对。
import r114_replacement_scan as _R114
parse_sidecar = _R114.parse_sidecar
parse_version = _R114.parse_version
vtuple = _R114.vtuple
rel_of = _R114.rel_of

def collect_skills():
    out = []
    if not os.path.isdir(SKILLS_ROOT):
        return out
    for name in sorted(os.listdir(SKILLS_ROOT)):
        d = os.path.join(SKILLS_ROOT, name)
        side = os.path.join(d, ".upstream")
        if os.path.isdir(d) and os.path.isfile(side):
            out.append((name, d, side))
    return out


def selftest():
    """In-process legs + one mutation leg, so the face is provably non-tautological (D-A)."""
    rows = []

    def ck(name, cond, detail=''):
        rows.append((bool(cond), name, str(detail)[:160]))
        print('%-4s %s%s' % ('PASS' if cond else 'FAIL', name,
                             '' if cond else '  <-- got: ' + str(detail)[:120]))

    Q = chr(34)
    NL = chr(10)
    ck('t1a sidecar repo-only', parse_sidecar('garrytan/gstack') == ('garrytan/gstack', None),
       parse_sidecar('garrytan/gstack'))
    ck('t1b sidecar repo+path',
       parse_sidecar('hugohe3/ppt-master' + NL + 'path: skills/ppt-master')
       == ('hugohe3/ppt-master', 'skills/ppt-master'))
    ck('t1c malformed sidecar => no repo (never guesses)',
       parse_sidecar('not a repo line' + NL + '# comment') == (None, None),
       parse_sidecar('not a repo line'))
    ck('t2a plain version', parse_version('name: x' + NL + 'version: 1.3.0') == '1.3.0')
    ck('t2b quoted version',
       parse_version('name: x' + NL + 'version: ' + Q + '6.6.0' + Q) == '6.6.0',
       parse_version('name: x' + NL + 'version: ' + Q + '6.6.0' + Q))
    ck('t2c indented nested version',
       parse_version('metadata:' + NL + '  version: ' + Q + '6.6.0' + Q) == '6.6.0')
    ck('t2d missing version => None', parse_version('name: x' + NL + 'desc: y') is None)
    ck('t3a behind', rel_of('6.6.0', '6.7.3') == 'BEHIND', rel_of('6.6.0', '6.7.3'))
    ck('t3b same', rel_of('1.3.0', '1.3.0') == 'SAME')
    ck('t3c ahead', rel_of('2.0.0', '1.9.9') == 'AHEAD')
    ck('t3d unknown upstream release stays unknown',
       rel_of('1.0.0', None) == 'UNKNOWN_UPSTREAM_RELEASE')
    ck('t3e unknown local stays unknown', rel_of(None, '1.0.0') == 'UNKNOWN_LOCAL')
    ck('t3f 1.3 vs 1.3.0 padded equal', rel_of('1.3', '1.3.0') == 'SAME', rel_of('1.3', '1.3.0'))

    def mutated(local, upstream):
        a, b = vtuple(local), vtuple(upstream)
        if a is None or b is None:
            return 'UNKNOWN'
        n = max(len(a), len(b))
        a = a + (0,) * (n - len(a))
        b = b + (0,) * (n - len(b))
        if a > b:
            return 'BEHIND'
        if a < b:
            return 'AHEAD'
        return 'SAME'

    ck('t4 mutation (operator flipped) breaks t3a => t3a carries weight',
       mutated('6.6.0', '6.7.3') == 'AHEAD')
    n_fail = sum(1 for ok, _, _ in rows if not ok)
    print('[SELFTEST:%s] legs=%d fail=%d' % ('PASS' if not n_fail else 'FAIL', len(rows), n_fail))
    return not n_fail


def build_face(limit=None, quiet=False):
    """One record per skill that declares a .upstream sidecar. Read-only on the managed root."""
    skills = collect_skills()
    if not skills:
        print('[UPSTREAM:UNVERIFIED] no .upstream sidecar found under %s (R247)' % SKILLS_ROOT)
        return 2
    if limit:
        skills = skills[:limit]
    rows, n_unavail = [], 0
    for name, d, side in skills:
        srepo, spath = parse_sidecar(io.open(side, encoding='utf-8-sig', errors='replace').read())
        sk = os.path.join(d, 'SKILL.md')
        local_v = parse_version(io.open(sk, encoding='utf-8-sig', errors='replace').read()) if os.path.isfile(sk) else None
        rec = {'skill': name, 'upstream_repo': srepo, 'upstream_path': spath,
               'local_version': local_v, 'sidecar_mtime': int(os.path.getmtime(side))}
        if not srepo:
            rec['state'] = 'SIDECAR_UNPARSABLE'
            rec['rel'] = 'UNKNOWN_BOTH'
            rows.append(rec)
            continue
        out, err = gh(['api', 'repos/' + srepo])
        time.sleep(CORE_SLEEP)
        if err:
            rec['state'] = 'UNAVAILABLE'
            rec['error'] = err[:160]
            rec['rel'] = 'UNKNOWN_BOTH'
            n_unavail += 1
            rows.append(rec)
            if not quiet:
                print('  %-28s UNAVAILABLE %s' % (name, err[:70]))
            continue
        try:
            m = json.loads(out)
        except ValueError as exc:
            rec['state'] = 'UNAVAILABLE'
            rec['error'] = 'json:%r' % (exc,)
            rec['rel'] = 'UNKNOWN_BOTH'
            n_unavail += 1
            rows.append(rec)
            continue
        rec.update({'state': 'OK',
                    'stars': m.get('stargazers_count'),
                    'pushed_at': (m.get('pushed_at') or '')[:10],
                    'archived': bool(m.get('archived')),
                    'license': ((m.get('license') or {}).get('spdx_id') or 'UNLICENSED')})
        rout, rerr = gh(['api', 'repos/' + srepo + '/releases/latest'])
        time.sleep(CORE_SLEEP)
        tag = None
        if rout:
            try:
                tag = (json.loads(rout).get('tag_name') or '').strip()
            except ValueError:
                tag = None
        else:
            rec['release_error'] = (rerr or '')[:120]
        rec['upstream_tag'] = tag
        uv = tag.lstrip('vV') if tag else None
        if uv and not re.match(r'^[0-9]+(\.[0-9]+){1,3}$', uv):
            uv = None
            rec['release_tag_not_semver'] = tag
        rec['upstream_version'] = uv
        rec['rel'] = rel_of(local_v, uv)
        rows.append(rec)
        if not quiet:
            print('  %-28s local=%-9s upstream=%-9s %-24s %s' % (
                  name, local_v or '-', uv or '-', rec['rel'],
                  'archived' if rec['archived'] else rec['license']))
    if not rows:
        print('[UPSTREAM:FAIL] 0 records => not writing an empty face (R247)')
        return 1
    by_rel = {}
    for r in rows:
        by_rel[r['rel']] = by_rel.get(r['rel'], 0) + 1
    doc = {'schema': 'declared-upstream-face-v1',
           'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
           'provenance_cmd': 'python 05-exec/r263_declared_upstream_face.py',
           'rule': 'R261-5: the search pool cannot return a skill declared upstream; this face',
           'rule2': 'reads sidecar pointers so replace-vs-follow can be answered',
           'skills_root': SKILLS_ROOT,
           'skills_with_sidecar': len(rows),
           'unavailable_n': n_unavail,
           'by_rel': by_rel,
           'rows': rows}
    return doc


def main():
    ap = argparse.ArgumentParser(prog='r263_declared_upstream_face.py')
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
    with io.open(tmp, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, args.out)
    print('[UPSTREAM:FACE] skills_with_sidecar=%d unavailable=%d by_rel=%s'
          % (doc['skills_with_sidecar'], doc['unavailable_n'], json.dumps(doc['by_rel'])))
    print('JSON ->', args.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
