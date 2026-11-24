#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''t1 覆盖面自证：清单分类计数守恒 + 受管根独立现测 + 逐件证据 + 故意删一行的负控。'''
import argparse, io, json, os, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_SCOPE = REPO / '00-scope' / '自建skill清单.md'
DEFAULT_INV = Path(__file__).resolve().parent / 'data' / 'inventory.json'
DEFAULT_ROOT = Path('D:/global_skills')
CLASSES = ['HIGH', 'MID', 'LOW', 'EXCLUDE']
EXPECTED = {'HIGH': 51, 'MID': 26, 'LOW': 30, 'EXCLUDE': 43}
EXPECTED_SUM = 150

def parse_scope(path):
    lines = io.open(path, encoding='utf-8').read().splitlines()
    section = None
    headers = {}
    counts = dict((c, 0) for c in CLASSES)
    row_lines = dict((c, []) for c in CLASSES)
    for i, line in enumerate(lines, 1):
        m = re.match(r'^## (HIGH|MID|LOW|EXCLUDE)（(\d+)）', line)
        if m:
            section = m.group(1)
            headers[section] = int(m.group(2))
            continue
        if section and line.startswith('| `'):
            counts[section] += 1
            row_lines[section].append(i)
    return headers, counts, row_lines

def measure_root(root, slugs):
    slug_set = set(slugs)
    direct = []
    all_md = []
    nested_by_top = {}
    top_dirs = 0
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        top_dirs += 1
        if (entry / 'SKILL.md').is_file():
            direct.append(entry.name)
        for q in entry.rglob('SKILL.md'):
            if not q.is_file():
                continue
            all_md.append(str(q))
            rel = q.relative_to(entry)
            if len(rel.parts) > 1:
                nested_by_top[entry.name] = nested_by_top.get(entry.name, 0) + 1
    present = [s for s in slugs if (root / s / 'SKILL.md').is_file()]
    missing = [s for s in slugs if not (root / s / 'SKILL.md').is_file()]
    outside = [d for d in direct if d not in slug_set]
    return {
        'top_level_dirs': top_dirs,
        'direct_n': len(direct),
        'all_n': len(all_md),
        'nested_n': sum(nested_by_top.values()),
        'nested_by_top': nested_by_top,
        'present_n': len(present),
        'missing_n': len(missing),
        'missing': missing,
        'outside_n': len(outside),
        'outside': outside,
    }

def check(inv_path, scope_path, root, label):
    print('=== ' + label + ' ===')
    headers, counts, row_lines = parse_scope(scope_path)
    inv = json.load(io.open(inv_path, encoding='utf-8'))
    rows = inv.get('rows') or []
    by_class = dict((c, sum(1 for r in rows if r.get('class') == c)) for c in CLASSES)
    sum_class = sum(by_class.values())
    print('分母(权威清单声明) = %d' % EXPECTED_SUM)
    print('清单表头计数 = %s' % json.dumps(headers, ensure_ascii=False))
    print('清单表内行数 = %s' % json.dumps(counts, ensure_ascii=False))
    print('逐类之和 = %d %s' % (sum_class, json.dumps(by_class, ensure_ascii=False)))
    print('相等断言(分类之和 == 分母) = %s' % (sum_class == EXPECTED_SUM))
    errs = []
    if headers != EXPECTED:
        errs.append('scope_header_mismatch %s' % headers)
    if counts != EXPECTED:
        errs.append('scope_row_mismatch %s' % counts)
    if sum(counts.values()) != EXPECTED_SUM:
        errs.append('scope_sum_mismatch %d' % sum(counts.values()))
    if len(rows) != EXPECTED_SUM:
        errs.append('inventory_rows %d != %d' % (len(rows), EXPECTED_SUM))
    if by_class != EXPECTED:
        errs.append('inventory_by_class %s' % json.dumps(by_class, ensure_ascii=False))
    if sum_class != EXPECTED_SUM:
        errs.append('class_sum %d != %d' % (sum_class, EXPECTED_SUM))
    no_ev = [r.get('slug') for r in rows if not r.get('evidence_paths')]
    print('逐件证据覆盖 = %d/%d 缺证据=%s' % (len(rows) - len(no_ev), len(rows), no_ev[:5]))
    if no_ev:
        errs.append('no_evidence %s' % no_ev[:5])
    den = inv.get('denominator') or {}
    if den.get('expected') != EXPECTED_SUM:
        errs.append('denominator_expected %s' % den.get('expected'))
    if den.get('by_class') != EXPECTED:
        errs.append('denominator_by_class %s' % den.get('by_class'))
    m = measure_root(root, [r.get('slug') for r in rows])
    print('受管根现测: 顶层目录=%d 一级直属SKILL.md=%d 全深度SKILL.md=%d 嵌套=%d' % (
        m['top_level_dirs'], m['direct_n'], m['all_n'], m['nested_n']))
    print('清单内现存直属=%d 退役/缺直属=%d 清单外直属=%d 清单外样例=%s' % (
        m['present_n'], m['missing_n'], m['outside_n'], m['outside'][:5]))
    print('守恒: 现存+缺件=%d==%d ; 现存+清单外=%d==%d ; 直属+嵌套=%d==%d' % (
        m['present_n'] + m['missing_n'], len(rows),
        m['present_n'] + m['outside_n'], m['direct_n'],
        m['direct_n'] + m['nested_n'], m['all_n']))
    if m['present_n'] + m['missing_n'] != len(rows):
        errs.append('root_present_missing %d' % (m['present_n'] + m['missing_n']))
    if m['present_n'] + m['outside_n'] != m['direct_n']:
        errs.append('root_direct_split %d' % (m['present_n'] + m['outside_n']))
    if m['direct_n'] + m['nested_n'] != m['all_n']:
        errs.append('root_depth_split %d' % (m['direct_n'] + m['nested_n']))
    # 快照自洽（硬判据）：生成时记录的 measurements 必须自己满足三条守恒，
    # 否则说明 JSON 里的分母/分解被改坏，与受管根是否漂移无关。
    mm = inv.get('measurements') or {}
    s_present = mm.get('list_present_direct')
    s_missing = mm.get('list_missing_direct_count')
    s_outside = mm.get('outside_list_direct_count')
    s_direct = mm.get('skill_md_direct_top_level')
    s_nested = mm.get('nested_skill_md')
    s_all = mm.get('skill_md_all_depth')
    if not all(isinstance(v, int) for v in (s_present, s_missing, s_outside, s_direct, s_nested, s_all)):
        errs.append('snapshot_measurements_missing %s' % mm)
    else:
        if s_present + s_missing != EXPECTED_SUM:
            errs.append('snapshot_present_missing %d != %d' % (s_present + s_missing, EXPECTED_SUM))
        if s_present + s_outside != s_direct:
            errs.append('snapshot_direct_split %d != %d' % (s_present + s_outside, s_direct))
        if s_direct + s_nested != s_all:
            errs.append('snapshot_depth_split %d != %d' % (s_direct + s_nested, s_all))

    # 漂移登记（非阻断）：D:/global_skills 是并行会话共享的活跃根（R269 只登记不擅动），
    # 生成快照与本轮现测的绝对值允许不同；打印差异并指向取值命令，禁把漂移当绿也当红。
    pairs = [('skill_md_all_depth', m['all_n']), ('skill_md_direct_top_level', m['direct_n']),
             ('nested_skill_md', m['nested_n']), ('list_present_direct', m['present_n']),
             ('list_missing_direct_count', m['missing_n']), ('outside_list_direct_count', m['outside_n'])]
    drifts = []
    for key, live in pairs:
        snap = mm.get(key)
        if snap != live:
            drifts.append('%s json=%s live=%s' % (key, snap, live))
    if drifts:
        print('⚠️ [DRIFT] 受管根在生成快照后发生变化（R269 只登记不擅动；取值命令见 JSON.commands）:')
        for d in drifts:
            print('   - ' + d)
    else:
        print('受管根现测与生成快照一致（无漂移）')
    return errs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inventory', default=str(DEFAULT_INV))
    ap.add_argument('--scope', default=str(DEFAULT_SCOPE))
    ap.add_argument('--managed-root', default=str(DEFAULT_ROOT))
    ap.add_argument('--negative-control', action='store_true')
    args = ap.parse_args()
    inv_path = Path(args.inventory)
    scope_path = Path(args.scope)
    root = Path(args.managed_root)
    if not args.negative_control:
        errs = check(inv_path, scope_path, root, 'NORMAL')
        if errs:
            print('[COVERAGE:FAIL] ' + ' | '.join(errs))
            return 1
        print('[COVERAGE:PASS] 分母=150 分类之和=150 相等断言=True 逐件证据=150/150 受管根三类守恒=True')
        return 0
    tmp_dir = REPO / '_temp'
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp = tmp_dir / 't1_inventory_dropped.json'
    inv = json.load(io.open(inv_path, encoding='utf-8'))
    inv['rows'] = inv['rows'][:-1]
    with io.open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(inv, ensure_ascii=False, indent=2))
    try:
        errs = check(tmp, scope_path, root, 'NEGATIVE_CONTROL_DROP_ONE')
        if not errs:
            print('[NEGCTRL:UNEXPECTED_GREEN] 删一行后判据仍绿 = 判据无牙')
            return 1
        print('[NEGCTRL:RED] 故意删一行后覆盖判据报红（符合预期）: ' + ' | '.join(errs[:3]))
        return 0
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass

if __name__ == '__main__':
    sys.exit(main())
