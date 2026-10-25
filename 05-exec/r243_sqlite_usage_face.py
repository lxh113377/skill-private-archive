# -*- coding: utf-8 -*-
'''r243_sqlite_usage_face.py - SQLite 本地用量面（r243 新建，只读查询，不改库）。

存在理由（r243 一手）：名册对 SQLite 第 ④ 层写着
    '本地嵌入库，无平台额度面 ⇒ 无读数面（用量由 r203_ledger_index 本地统计）'。
  这句里的「无读数面」与 r242 的 Turnstile 同病：它把**「没有平台额度」**读成了**「没有可读的数」**。
  本机实测：_temp/gate_index.sqlite 存在、10.03 MiB、7 张表、gate_run 34468 行 —— 这些都是可以读的量，
  只是没有额度而已。⇒ 本地体量要报，且单位必须写清「体量（非额度）」。

第二件事（r243 实测发现）：r203_ledger_index.py 是**重建型**脚本（DROP TABLE + CREATE），
  但**它不在门表 GATES 里** ⇒ 索引只新到它上一次被手工运行的那一刻，而全量门每轮都在往
  06-benchmark/gate_runs.jsonl 追加。所以本面不只报体量，还报**陈旧度**：库 mtime 与最新输入件 mtime 之差。
  这样「SQLite 被搭配了但没被维护」这件事每轮都能看见，而不必靠我某轮恰好想起来。

判据：库在且能查 ⇒ MEASURED；库缺失/查询异常 ⇒ UNVERIFIED(2)（R247：取不到不等于零用量）。
用法: python 05-exec/r243_sqlite_usage_face.py [--json <件>]
'''
import argparse
import datetime
import io
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, '_temp', 'gate_index.sqlite')
INPUT_HINTS = ('gate_runs.jsonl', 'debt_runs.jsonl', 'input_pins.jsonl', '07-next-steps.md')


def _builder_in_gates():
    '''自查重建脚本是否已在门表里（不写死：写死会随我在别处的改动变成假断言）。'''
    try:
        sys.path.insert(0, HERE)
        import run_gates as R
        return any(str(g.get('script') or '').startswith('r203_ledger_index')
                   for g in getattr(R, 'GATES', []))
    except Exception:
        return None


def mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out', default='')
    args = ap.parse_args(argv)
    res = {'schema': 'sqlite-usage-v1', 'readonly': True,
           'provenance_cmd': 'python 05-exec/r243_sqlite_usage_face.py --json <件>',
           'db': os.path.relpath(DB, ROOT).replace(os.sep, '/'),
           'builder': 'r203_ledger_index.py（重建型：DROP TABLE + CREATE）',
           # r243 自抓：首版把 builder_in_gates 写死 False ⇒ 我随后把重建纳入门表，这行立刻成了假断言。
           #   改为**运行时自查门表**（与「不猜」同精神）：读 run_gates.GATES 里是否有跑 r203 的门。
           'builder_in_gates': _builder_in_gates(),
           'note': '本地嵌入库：报体量（非额度）。陈旧度 = 库 mtime vs 最新输入件 mtime；'
                   'builder 不在 GATES ⇒ 索引不会被全量门自动刷新。'}
    if not os.path.isfile(DB):
        res['state'] = 'UNVERIFIED'
        res['why'] = '库文件不存在（未建过或已被清理）⇒ 不记 0'
    else:
        try:
            c = sqlite3.connect(DB)
            c.row_factory = sqlite3.Row
            tabs = [r['name'] for r in c.execute(
                "select name from sqlite_master where type='table'").fetchall()]
            rows = {}
            for t in tabs:
                rows[t] = c.execute('select count(*) from [%s]' % t).fetchone()[0]
            c.close()
            size = os.path.getsize(DB)
            res['state'] = 'MEASURED'
            res['size_bytes'] = size
            res['size_mib'] = round(size / 1048576.0, 2)
            res['tables_n'] = len(tabs)
            res['tables_rows'] = rows
            res['rows_total'] = sum(rows.values())
            mt = mtime(DB)
            res['db_mtime'] = (datetime.datetime.fromtimestamp(mt).isoformat(timespec='seconds')
                               if mt else None)
            newest = None
            newest_name = None
            for nm in INPUT_HINTS:
                for cand in (os.path.join(ROOT, '06-benchmark', nm),
                             os.path.join(ROOT, 'memory', nm)):
                    t = mtime(cand)
                    if t and (newest is None or t > newest):
                        newest, newest_name = t, nm
            if mt and newest:
                delta_h = (newest - mt) / 3600.0
                res['newest_input'] = newest_name
                res['newest_input_mtime'] = datetime.datetime.fromtimestamp(
                    newest).isoformat(timespec='seconds')
                res['stale_hours'] = round(delta_h, 2)
                res['stale'] = bool(delta_h > 1.0)
            res['why'] = ''
        except Exception as e:
            res['state'] = 'UNVERIFIED'
            res['why'] = '查询异常：%r' % (e,)
    if args.out:
        op = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
        io.open(op, 'w', encoding='utf-8', newline=chr(10)).write(
            json.dumps(res, ensure_ascii=False, indent=1))
    print('=== SQLite 本地用量（r243）===')
    if res['state'] == 'MEASURED':
        print('  MEASURED %s ｜ %s MiB ｜ %d 表 ｜ 合计 %d 行' % (
            res['db'], res['size_mib'], res['tables_n'], res['rows_total']))
        if res.get('stale') is not None:
            print('  陈旧度：库 %s vs 最新输入 %s(%s) ⇒ 差 %s 小时 %s' % (
                res['db_mtime'], res['newest_input'], res['newest_input_mtime'],
                res['stale_hours'], '【陈旧】' if res['stale'] else '（新鲜）'))
        _big = res.get('builder_in_gates')
        print('  [SQLITE:PASS] 本地库体量已取（只读查询；builder %s）' % (
            '已在门表第 96 位 ⇒ 每轮全量自动重建' if _big else
            ('不在门表 ⇒ 需单独刷新（陈旧度即其可见症状）' if _big is False else
             '门表自查不可用 ⇒ 不臆断')))
        return 0
    print('  UNVERIFIED %s（R247：不记 0）' % res.get('why'));
    return 2


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())