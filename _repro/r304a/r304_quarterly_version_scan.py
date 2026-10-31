# -*- coding: utf-8 -*-
r'''r304 quarterly version scan.

Why this file exists:
  The r303 absorption baseline pins, per absorbed pair, a stored local digest, a stored
  upstream blob id and the stored upstream tip commit. That baseline could only be
  compared by hand, once. This runner puts the comparison on a quarterly cadence: it
  re-reads the live values, reuses the r303 five-state caliber verbatim, archives one
  quarter document, and lists absorption candidates (pairs whose upstream side moved
  since the anchor).

How it works:
  1. load the baseline document through the same loader the r303 comparator uses;
  2. call that comparator's own run_comparison, so the five states and their boundary
     rules are not re-implemented here (one caliber, one owner);
  3. partition the records - upstream-side movement becomes an absorption candidate,
     local-side movement becomes local drift, a fetch failure becomes unknown;
  4. write the quarter archive under the output root, stamped with a naive local
     generated_at in the same textual form as the cadence watchdog uses, **but deliberately placed OUTSIDE that
     watchdog's face** (r305: the prefix must not match quarterly*) so this scan can never make it green;
  5. print one machine-readable summary line.

Exit codes: 0 scanned / 2 baseline missing (UNVERIFIED, never read as no-change).
'''
import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone

NEWLINE = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
DEFAULT_BASELINE = os.path.join(REPO_ROOT, '_repro', 'r303a', 'absorption_baseline.json')
DEFAULT_COMPARATOR = os.path.join(REPO_ROOT, '_repro', 'r303a', 'compare_baseline.py')
# r305 修（A1 实测报警）：原名 'quarterly_r304a' 会**命中**季档看门狗的 glob（06-benchmark/quarterly*/*/audit.json），
# 于是「把输出根指到仓根」时看门狗会取走本件的季档 ⇒ 假绿风险（r305a 用看门狗自带 picker 实测 watchdog_picker_sees_it=true）。
# 改成一个**不匹配 quarterly*** 的目录名：本件落 06-benchmark/version_scan/<季>/audit.json，
# 即使有人把它指到仓根，看门狗也取不到 ⇒ 它永远不能冒充 r113 的深度季档。
QUARTER_PREFIX = 'version_scan'
WATCHDOG_STAMP_FMT = '%Y-%m-%dT%H:%M:%S'
FIVE_STATES = ('OK', 'LOCAL_CHANGED', 'UPSTREAM_CHANGED', 'BOTH_CHANGED', 'UNKNOWN')
UPSTREAM_STATES = ('UPSTREAM_CHANGED', 'BOTH_CHANGED')


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError('cannot load module at ' + path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def quarter_of(dt):
    # calendar-quarter id, e.g. 2026Q4 - the shape the cadence watchdog already reads
    return '%04dQ%d' % (dt.year, (dt.month - 1) // 3 + 1)


def season_relpath(quarter):
    # stitched from segments so the path rule stays visible and portable
    return os.path.join('06-benchmark', QUARTER_PREFIX, quarter, 'audit.json')


def three_values(rec):
    # the three identifiers an absorption review asks for, current side first
    return {
        'upstream_commit_sha': rec.get('current_upstream_commit_sha'),
        'upstream_file_sha': rec.get('current_upstream_sha'),
        'local_file_sha': rec.get('current_local_sha'),
    }


def partition(records, freeze=None):
    # split the five states into the three review buckets; unknown is never a candidate
    # r318 冻结名单：declared_state=NOT_SAME_LINEAGE 的配对（gstack，r317 终裁）上游仍会被扫、
    # 状态仍如实报（UPSTREAM_CHANGED 计数不动），但**不进候选面**——候选=可吸收动作，异族靶不该再被指路。
    freeze = freeze or set()
    candidates, local_drift, unknown, frozen = [], [], [], []
    for r in records:
        st = r.get('state')
        if st in UPSTREAM_STATES and r.get('slug') in freeze:
            item = dict(r)
            item['three_values'] = three_values(r)
            item['candidate_kind'] = 'frozen_not_same_lineage'
            frozen.append(item)
        elif st in UPSTREAM_STATES:
            item = dict(r)
            item['three_values'] = three_values(r)
            item['candidate_kind'] = 'upstream_absorption'
            candidates.append(item)
        elif st == 'LOCAL_CHANGED':
            local_drift.append(dict(r))
        elif st == 'UNKNOWN':
            unknown.append(dict(r))
    return candidates, local_drift, unknown, frozen


def build_quarter_doc(doc, records, summary, quarter, now, freeze=None):
    cand, drift, unk, frozen = partition(records, freeze)
    qsummary = dict(summary)
    qsummary['candidates'] = len(cand)
    qsummary['frozen'] = len(frozen)
    qsummary['local_drift'] = len(drift)
    qsummary['unknown_pairs'] = len(unk)
    qsummary['caliber'] = 'r303a five-state comparator, imported and not re-implemented'
    qsummary['candidate_rule'] = ('candidate = upstream side moved since the anchor'
                                   ' (UPSTREAM_CHANGED or BOTH_CHANGED);'
                                   ' unknown never counts as a candidate')
    pairs = doc.get('pairs') or []
    return {
        'schema': 'r304a.quarterly_version_scan.v1',
        'generated_at': now.strftime(WATCHDOG_STAMP_FMT),
        'generated_at_utc': now.astimezone(timezone.utc).replace(microsecond=0).isoformat(),
        'quarter': quarter,
        'baseline': {
            'schema': doc.get('schema'),
            'generated_at': doc.get('generated_at'),
            'pairs': len(pairs),
        },
        'path_rule': {
            'scan_root': 'the output root this runner was pointed at',
            'relative_pattern': os.path.join('06-benchmark', QUARTER_PREFIX, '<quarter>', 'audit.json'),
            'filename': 'audit.json',
            'quarter_rule': 'calendar year + Q + quarter index of generated_at',
        },
        'watchdog_conformance': {
            'watchdog': 'r260 quarterly cadence',
            'reads': 'generated_at with a naive local timestamp',
            'stamp_format': WATCHDOG_STAMP_FMT,
            'structurally_recognizable': True,
            'recognizable_when': 'the watchdog scan root is pointed at this output root',
            'in_repo_default_run': False,
            'reason': ('this delivery is confined to the task write area, which sits outside'
                       ' the repository scan root the watchdog walks by default'),
            'reproduction': {
                'fn': 'newest_audit',
                'arg_root': 'this output root',
                'expect': 'returns this very audit document and its stamp',
            },
        },
        'caliber': {
            'states': list(FIVE_STATES),
            'fetch_failure_is_unknown': True,
            'missing_baseline_is_unverified': True,
        },
        'summary': qsummary,
        'candidates': cand,
        'frozen': frozen,
        'local_drift': drift,
        'unknown_pairs': unk,
        'pairs': records,
    }


def format_scan_line(summary, quarter):
    return ('[R304:SCAN] quarter=%s pairs=%d ok=%d upstream_changed=%d local_changed=%d both=%d unknown=%d candidates=%d'
            % (quarter, summary.get('pairs', 0), summary.get('ok', 0), summary.get('upstream_changed', 0),
               summary.get('local_changed', 0), summary.get('both_changed', 0), summary.get('unknown', 0),
               summary.get('candidates', 0)) + ' frozen=%d' % summary.get('frozen', 0))


def load_freeze(path):
    # r318：冻结名单=外部 JSON（slug 数组）；缺失返回空集（禁把「读不到名单」读成「全员可吸收」——
    # 名单缺失只影响候选面收缩，不影响任何状态读数）。
    try:
        with open(path, encoding='utf-8') as fh:
            d = json.load(fh)
        return set(d.get('slugs') or d if isinstance(d, list) else d.get('slugs') or [])
    except Exception:
        return set()


def run_scan(baseline, outdir, quarter=None, workers=8, only=None, write=True, verbose=True, quiet=False, freeze=None):
    # returns (quarter_doc or None, rc, quarter_id); rc=2 means the baseline is absent
    now = datetime.now()
    q = quarter or quarter_of(now)
    if not os.path.isfile(baseline):
        if not quiet:
            print('[R304:SCAN-UNVERIFIED] baseline missing -> rc=2 (never read as no-change)')
        return None, 2, q
    cmp = load_module(DEFAULT_COMPARATOR, 'r303a_compare_baseline')
    doc, records = cmp.run_comparison(baseline, workers, only)
    summary = cmp.summarize(records)
    # r318 一致性：freeze=None 走库级默认名单（importer 如 check_r304a 与 CLI 同口径），
    # 显式传 set() 才能关——否则判据面 candidates=1、工具面 candidates=0 两处读数打架。
    if freeze is None:
        fl = os.path.join(HERE, 'absorption_freeze_list.json')
        freeze = load_freeze(fl) if os.path.isfile(fl) else set()
    qdoc = build_quarter_doc(doc, records, summary, q, now, freeze=freeze)
    if verbose and not quiet:
        for r in records:
            print('%-30s %-16s local_changed=%-5s upstream_changed=%-5s notes=%s'
                  % (r.get('slug'), r.get('state'), r.get('local_changed'), r.get('upstream_changed'),
                     ','.join(r.get('notes') or [])))
    if write:
        target = os.path.join(outdir, season_relpath(q))
        d = os.path.dirname(os.path.abspath(target))
        if d:
            os.makedirs(d, exist_ok=True)
        with open(target, 'w', encoding='utf-8', newline=NEWLINE) as fh:
            json.dump(qdoc, fh, ensure_ascii=False, indent=1)
            fh.write(NEWLINE)
        # prove the archive parses back before it is announced
        json.load(open(target, encoding='utf-8'))
        qdoc['archive'] = target
        if not quiet:
            print('[R304:SCAN:WROTE] ' + target)
    return qdoc, 0, q


def main(argv=None):
    ap = argparse.ArgumentParser(prog='r304_quarterly_version_scan.py')
    ap.add_argument('--baseline', default=DEFAULT_BASELINE)
    ap.add_argument('--outdir', default=HERE)
    ap.add_argument('--quarter', default=None)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--only', default=None)
    ap.add_argument('--json-out', default=None)
    ap.add_argument('--freeze', default=os.path.join(HERE, 'absorption_freeze_list.json'),
                    help='r318 冻结名单 JSON（NOT_SAME_LINEAGE 等：状态照报、不进候选面）')
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args(argv)
    only = a.only.split(',') if a.only else None
    freeze = load_freeze(a.freeze) if a.freeze and os.path.isfile(a.freeze) else set()
    if not a.quiet and freeze:
        print('[R304:FREEZE] slugs=%s' % ','.join(sorted(freeze)))
    qdoc, rc, q = run_scan(a.baseline, a.outdir, a.quarter, a.workers, only, True, not a.quiet, a.quiet, freeze)
    if rc == 2 or qdoc is None:
        return 2
    if a.json_out:
        with open(a.json_out, 'w', encoding='utf-8', newline=NEWLINE) as fh:
            json.dump(qdoc, fh, ensure_ascii=False, indent=1)
            fh.write(NEWLINE)
    print(format_scan_line(qdoc['summary'], q))
    return 0


if __name__ == '__main__':
    sys.exit(main())