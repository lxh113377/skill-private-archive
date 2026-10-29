# -*- coding: utf-8 -*-
'''r287_provenance_resolve.py —— 第 114 道门：面件的「出处命令」在 clone 后必须还能解析（只读取证 + 基线分列）。

存在理由（本会话一手，不是假想防御）：判据脚本落点决定别人能不能复算。我在 r283/r284/r286 手工搬了
四次这类件（r278c / r281g / r282j / r285k）—— 它们原先都放在 _temp/ 下，而 .gitignore 里 _temp/ 是
**任意层级**模式 ⇒ 引用它们的面件在克隆里跑不出自己的读数。R283-2、R286-1 立了三轮还是纸面条，
所以本轮把它变成门。

口径（重要，我先犯过一次粗匹配的错并写在这里以免重犯）：
  · 只看面件自己的出处类字段（provenance_cmd / produce_cmd / evidence_cmd / produce / rerun_cmd / cmd），
    不看整份 JSON —— 否则会把它**测量的对象**（例如被扫 skill 树里的 assets/xxx.py）当成出处，
    我第一次试算就因此报出 5679/13045 的假规模，真数是 21 件 / 63 处（其中 55 处指 _temp/）。
  · 裸文件名按 basename 命中即算可解析（面里常写 `r35_tracked_empty.py` 而全路径在 05-exec/ 下）。
  · 绝对路径与盘外引用不在本门判定范围（那是可移植性门 portability 的职责）。

基线分列（防恒红）：本仓历史 21 件已知不可解析项进 06-benchmark/r287_provenance_baseline.json，
门只对**新增项**判红。基线不存在 ⇒ UNVERIFIED（不得判绿，R247）。生成基线：--write-baseline。

退出码：0 PASS / 1 FAIL（新增不可解析出处）/ 2 UNVERIFIED。
用法：python 05-exec/r287_provenance_resolve.py [--json 件] [--root 仓根] [--write-baseline]
'''
import argparse
import glob
import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASELINE_REL = '06-benchmark/r287_provenance_baseline.json'
PROV_KEY = re.compile(r'(provenance_cmd|produce_cmd|evidence_cmd|reproduce_cmd|rerun_cmd|produce|cmd)$', re.I)
REF_RE = re.compile(r'([0-9A-Za-z_.\-/]*_temp/[0-9A-Za-z_.\-/]+[.](?:py|sh|mjs))'
                    r'|(?<![0-9A-Za-z_./-])([A-Za-z0-9_./-]+[.](?:py|sh|mjs))')


def tracked_index(root):
    """git ls-files -z ⇒ (全路径集合, basename 集合)。取不到必须返回 None 让调用方判 UNVERIFIED。"""
    try:
        p = subprocess.run(['git', '-C', root, 'ls-files', '-z'], capture_output=True, timeout=90)
    except Exception as e:
        return None, None, 'git 异常: %s' % e
    if p.returncode != 0:
        return None, None, 'git ls-files rc=%s' % p.returncode
    names = [x.decode('utf-8', 'replace') for x in p.stdout.split(b'\0') if x]
    if not names:
        return None, None, 'tracked 清单为空（无文件不等于通过）'
    return set(names), {os.path.basename(n) for n in names}, None


def prov_refs(obj, path, out):
    """递归收出处类字段的字符串值（带 json-path，便于人定位到具体条目）。"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and PROV_KEY.search(str(k)):
                out.append((path + '/' + str(k), v))
            prov_refs(v, path + '/' + str(k), out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            prov_refs(v, path + '[' + str(i) + ']', out)


def unresolvable(text, tracked, bases):
    """一条出处字符串里所有解析不了的脚本引用。"""
    hits = []
    for m in REF_RE.finditer(text or ''):
        r = m.group(1) or m.group(2)
        if not r:
            continue
        if '_temp/' in r:
            hits.append(r)
            continue
        if r.startswith(('D:/', 'C:/', '/', '~')):
            continue
        if r in tracked or os.path.basename(r) in bases:
            continue
        hits.append(r)
    return sorted(set(hits))


def scan(root):
    tracked, bases, err = tracked_index(root)
    if tracked is None:
        return None, err
    rows = []
    files = sorted(glob.glob(os.path.join(root, '06-benchmark', '*.json')))
    for f in files:
        try:
            d = json.load(io.open(f, encoding='utf-8', errors='replace'))
        except Exception:
            continue
        refs = []
        prov_refs(d, '', refs)
        for jp, s in refs:
            for r in unresolvable(s, tracked, bases):
                rows.append({'face': os.path.relpath(f, root).replace(os.sep, '/'),
                             'json_path': jp, 'ref': r,
                             'temp_prefixed': '_temp/' in r})
    return {'faces_total': len(files), 'rows': rows}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json')
    ap.add_argument('--root', default=ROOT)
    ap.add_argument('--write-baseline', action='store_true')
    a = ap.parse_args()
    res, err = scan(a.root)
    if res is None:
        print('[PROVRESOLVE:UNVERIFIED] 取数失败：%s ⇒ 不得判绿（R247）' % err)
        return 2
    bl_path = os.path.join(a.root, *BASELINE_REL.split('/'))
    if a.write_baseline:
        tmp = bl_path + '.tmp'
        io.open(tmp, 'w', encoding='utf-8', newline='').write(json.dumps(
            {'schema': 'provenance-baseline-v1',
             'generated_at': time.strftime('%Y-%m-%d %H:%M'),
             'why': ('known-pre-existing unresolvable provenance refs; the gate only fails on NEW ones '
                     '(otherwise the gate is permanently red and therefore useless)'),
             'count': len(res['rows']),
             'keys': sorted(set(x['face'] + '|' + x['ref'] for x in res['rows']))},
            ensure_ascii=False, indent=1))
        os.replace(tmp, bl_path)
        print('[PROVRESOLVE:BASELINE] wrote %d keys -> %s' % (len(res['rows']), BASELINE_REL))
        return 0
    if not os.path.isfile(bl_path):
        print('[PROVRESOLVE:UNVERIFIED] 基线件缺失（%s）⇒ 无法区分既有与新增，不得判绿' % BASELINE_REL)
        return 2
    keys = set((json.load(io.open(bl_path, encoding='utf-8')).get('keys') or []))
    fresh = [x for x in res['rows'] if (x['face'] + '|' + x['ref']) not in keys]
    stale = len(keys) - len({x['face'] + '|' + x['ref'] for x in res['rows'] if x['face'] + '|' + x['ref'] in keys})
    out = {'schema': 'provenance-resolve-v1',
           'generated_at': time.strftime('%Y-%m-%d %H:%M'),
           'provenance_cmd': 'python 05-exec/r287_provenance_resolve.py',
           'readonly': True,
           'faces_total': res['faces_total'],
           'unresolvable_total': len(res['rows']),
           'temp_prefixed': len([x for x in res['rows'] if x['temp_prefixed']]),
           'baseline_keys': len(keys), 'new_unresolvable': fresh, 'baseline_stale': stale,
           'scope_note': ('provenance-class fields only; basename match counts as resolvable; '
                          'absolute paths are the portability gate business'),
           'state': 'PROVRESOLVE_OK' if not fresh else 'PROVRESOLVE_FAIL'}
    if a.json:
        tmp = a.json + '.tmp'
        io.open(tmp, 'w', encoding='utf-8', newline='').write(json.dumps(out, ensure_ascii=False, indent=1))
        os.replace(tmp, a.json)
    print('  面件 %d 份｜不可解析出处 %d（_temp 前缀 %d）｜基线 %d 项｜新增 %d' % (
          out['faces_total'], out['unresolvable_total'], out['temp_prefixed'],
          out['baseline_keys'], len(fresh)))
    for x in fresh[:6]:
        print('   NEW %s %s -> %s' % (x['face'].split('/')[-1][:40], x['json_path'][:26], x['ref'][:44]))
    print('[%s]' % ('PROVRESOLVE_OK' if not fresh else 'PROVRESOLVE_FAIL'))
    return 0 if not fresh else 1


if __name__ == '__main__':
    sys.exit(main())
