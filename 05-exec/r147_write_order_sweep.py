# -*- coding: utf-8 -*-
# r147_write_order_sweep.py -- 证据写入顺序穷举面（第 55 门，#45 的机器判据）。
#
# 存在理由（r146 一手，r147 读码升级）：R146-4 登记时说「双写顺序崩溃下次重装补齐」——
#   r147 读码发现比登记的重：旧序（台账先写、日志最后追加）在第 1/2 步后崩溃，
#   台账 lines 会**超前**日志行数（missing<0）。而三条件宽限与 pending 通道都只覆盖
#   missing==1（滞后侧）=> 超前侧**无任何通道可救 = 永久误红**，且要人工重装才能脱窗。
#
# 三条腿（#32：判据面必须有反向案证明有牙）：
#   L1 静态：r138_install_hooks.py 源码中写入标记顺序必须是 日志 < pending < 台账（防回退）
#   L2 动态：新序穷举崩溃前缀 k=0..3 => missing<0 的前缀数必须为 0（且各前缀门全 PASS 或有宽限）
#   L3 反向：旧序穷举 => missing<0 的前缀数必须 >0（=0 说明探针无牙，本面读数不可信）
#
# ⚠ 本件运行时会临时改写 .git/hooks/*.installed* 与 06-benchmark 两份台账件，finally 还原；
#   完整门禁串行跑，并发窗口 = 门自身时长（约秒级）。模拟新行复用旧行时间戳/字段，
#   只重算链字段 —— 崩溃前缀考察的是 lines/hash 一致性，不追求时间真实。
#
# 用法: python 05-exec/r147_write_order_sweep.py [--json 06-benchmark/write_order_r147_2026-10-21.json]
# 退出码: 0 三条腿全过 / 1 任一不过 / 2 输入面不可用
import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INSTALL = os.path.join(HERE, 'r138_install_hooks.py')
GATE = os.path.join(HERE, 'r142_install_history.py')
HK = os.path.join(ROOT, '.git', 'hooks')
LOG = os.path.join(HK, 'pre-commit.installed.log')
LEDGER = os.path.join(ROOT, '06-benchmark', 'hook_install_ledger.json')
PENDING = os.path.join(ROOT, '06-benchmark', 'hook_install_pending.json')
NEW_ORDER = ['log', 'pending', 'ledger']
OLD_ORDER = ['ledger', 'pending', 'log']


def chain_row(o, prev):
    o = dict(o)
    o['prev_hash'] = prev
    payload = json.dumps({k: v for k, v in o.items() if k != 'line_hash'},
                         ensure_ascii=False, sort_keys=True)
    o['line_hash'] = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    return o


def source_order_ok():
    try:
        src = io.open(INSTALL, encoding='utf-8', errors='replace').read()
        i_log = src.find("'.installed.log', 'a'")
        i_pend = src.find('hook_install_pending.json')
        i_led = src.find('hook_install_ledger.json')
        return (0 <= i_log < i_pend < i_led), (i_log, i_pend, i_led)
    except Exception:
        return False, None


def run_gate():
    d = tempfile.mkdtemp()
    r = subprocess.run([sys.executable, GATE, '--json', os.path.join(d, 'o.json')],
                       cwd=ROOT, capture_output=True, text=True,
                       encoding='utf-8', errors='replace', timeout=300)
    j = json.load(io.open(os.path.join(d, 'o.json'), encoding='utf-8-sig'))
    row = [x for x in j['rows'] if x['hook'] == 'pre-commit'][0]
    return r.returncode, row


def apply_prefix(order, crash_after):
    objs = [json.loads(l) for l in io.open(LOG, encoding='utf-8') if l.strip()]
    led = json.load(io.open(LEDGER, encoding='utf-8-sig'))
    pend = json.load(io.open(PENDING, encoding='utf-8-sig'))
    base = {k: v for k, v in objs[-1].items()
            if k not in ('prev_hash', 'line_hash', 'seq')}
    base['seq'] = len(objs) + 1
    newrow = chain_row(base, objs[-1]['line_hash'])
    done = 0
    for step in order:
        if done >= crash_after:
            break
        if step == 'log':
            objs.append(newrow)
        elif step == 'pending':
            pend['hook']['pre-commit'] = {'line_hash': newrow['line_hash'],
                                          'lines': newrow['seq'],
                                          'invoker': newrow.get('invoker'),
                                          'reason': 'crash-prefix',
                                          'written_at': newrow['installed_at']}
        elif step == 'ledger':
            led['hook']['pre-commit'] = {'lines': newrow['seq'],
                                         'last_line_hash': newrow['line_hash'],
                                         'installed_at': newrow['installed_at'],
                                         'invoker': newrow.get('invoker'),
                                         'reason': 'crash-prefix'}
        done += 1
    io.open(LOG, 'w', encoding='utf-8', newline=chr(10)).write(
        ''.join(json.dumps(o, ensure_ascii=False) + chr(10) for o in objs))
    io.open(LEDGER, 'w', encoding='utf-8', newline=chr(10)).write(
        json.dumps(led, ensure_ascii=False, indent=1))
    io.open(PENDING, 'w', encoding='utf-8', newline=chr(10)).write(
        json.dumps(pend, ensure_ascii=False, indent=1))


def sweep(order, snap):
    """返回 [{crash, missing, rc, h7, via}]，missing<0 = 永久误红死窗形态。"""
    res = []
    for crash in range(0, len(order) + 1):
        for k, f in (('log', LOG), ('ledger', LEDGER), ('pending', PENDING)):
            shutil.copyfile(os.path.join(snap, k), f)
        apply_prefix(order, crash)
        rc, row = run_gate()
        led = json.load(io.open(LEDGER, encoding='utf-8-sig'))['hook']['pre-commit']
        lines_n = sum(1 for l in io.open(LOG, encoding='utf-8') if l.strip())
        warn = row.get('h7_warning') or ''
        via = ('pending' if 'pending' in warn
               else ('env' if 'session' in warn else ''))
        res.append({'crash': crash, 'missing': lines_n - led['lines'],
                    'rc': rc, 'h7': row.get('h7_anchor_match'), 'via': via})
    for k, f in (('log', LOG), ('ledger', LEDGER), ('pending', PENDING)):
        shutil.copyfile(os.path.join(snap, k), f)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    args = ap.parse_args()
    for f in (LOG, LEDGER, PENDING, INSTALL, GATE):
        if not os.path.isfile(f):
            print('[ORDER] UNVERIFIED 输入面缺失: %s' % f)
            return 2
    l1, idx = source_order_ok()
    snap = tempfile.mkdtemp(prefix='wo_snap_')
    for k, f in (('log', LOG), ('ledger', LEDGER), ('pending', PENDING)):
        shutil.copyfile(f, os.path.join(snap, k))
    try:
        new_res = sweep(NEW_ORDER, snap)
        old_res = sweep(OLD_ORDER, snap)
    finally:
        for k, f in (('log', LOG), ('ledger', LEDGER), ('pending', PENDING)):
            shutil.copyfile(os.path.join(snap, k), f)
    new_dead = [r for r in new_res if r['missing'] < 0]
    old_dead = [r for r in old_res if r['missing'] < 0]
    l2 = (len(new_dead) == 0)
    l3 = (len(old_dead) >= 1)
    doc = {'schema': 'write-order-sweep-r147-v1',
           'cmd': 'python 05-exec/r147_write_order_sweep.py --json <out>',
           'face': {'l1_source_order': l1, 'source_idx': idx,
                     'new_prefixes': new_res, 'old_prefixes': old_res,
                     'new_dead_n': len(new_dead), 'old_dead_n': len(old_dead),
                     'all_new_pass': all(r['rc'] == 0 for r in new_res),
                     'reading': {
                         'l1_source_order': '安装脚本源码中 日志<pending<台账 的出现顺序（防回退）',
                         'new_dead_n': '新序穷举下 missing<0（台账超前=死窗）的崩溃前缀数，必须 0',
                         'old_dead_n': '旧序穷举下 missing<0 的前缀数，必须 >0（探针有牙的反向案）',
                     }},
           'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline=chr(10)) as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    print('[ORDER] L1 源码写入序 日志<pending<台账 = %s %s' % (l1, idx))
    print('[ORDER] L2 新序死窗前缀 %d（前缀 missing: %s）门判定 %s'
          % (len(new_dead), [r['missing'] for r in new_res],
             '全PASS' if doc['face']['all_new_pass'] else '有红'))
    print('[ORDER] L3 旧序死窗前缀 %d（反向案%smust>0）=> %s（missing: %s）'
          % (len(old_dead), '', '有牙' if l3 else '无牙!',
             [r['missing'] for r in old_res]))
    if args.out:
        print('[ORDER] JSON -> %s' % args.out)
    return 0 if (l1 and l2 and l3) else 1


if __name__ == '__main__':
    raise SystemExit(main())