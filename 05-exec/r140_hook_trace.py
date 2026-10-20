# -*- coding: utf-8 -*-
# r140_hook_trace.py -- 漂移可归因面（第 52 门，R139-4 落地）。
#
# 存在理由（r139 一手，r140 量化）：第 51 门（r139_hook_sync.py）能发现「模板与实装件不一致」，
#   但回答不了**是怎么造成的**。r140 实测量化这个缺口：漂移时能拿到两个 sha + 两个 mtime，
#   但拿不到三件事 ——
#     ① 实装件是哪个模板版本装的？
#     ② 装完之后有没有被改？
#     ③ 是谁/哪次改的？（实装件不在 git 内，无历史可查）
#   mtime 有陷阱：实装件 mtime 晚于模板 mtime，但**无法区分**「装了旧模板」还是「装后被人改」。
#
# 解法 = 安装时留印记（.installed），漂移时做三态归因：
#   IN_SYNC      —— 实装件 sha == 模板 sha（无漂移）
#   DRIFT_AFTER_INSTALL —— 实装件 sha == 印记里的 template_sha（装的就是这个模板），
#                        但 != 当前模板 sha ⇒ **装后被人改过**（或模板被改）
#   DRIFT_OLD_TEMPLATE  —— 实装件 sha != 印记里的 template_sha ⇒ **装的是旧模板**
#   NO_STAMP     —— 无印记（r140 之前装的）⇒ 归因不可用，须重装补印记
#
# 反向验证（#32）：造「装后改实装件」「改模板不重装」「无印记」三个变体，确认三态判得对。
#
# 用法: python 05-exec/r140_hook_trace.py [--json 06-benchmark/hook_trace_r140_2026-10-21.json]
# 退出码: 0 全部 IN_SYNC / 1 有 DRIFT / 2 输入面不可用
import argparse
import hashlib
import io
import json
import os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TPL = os.path.join(HERE, 'hook_templates')
HOOKS = os.path.join(ROOT, '.git', 'hooks')
PAIRS = [('pre-commit.sh', 'pre-commit'), ('post-commit.sh', 'post-commit')]


def sha(p):
    h = hashlib.sha256()
    try:
        with io.open(p, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ''


def read_stamp(p):
    try:
        with io.open(p, encoding='utf-8-sig') as f:
            return json.load(f) or {}
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    args = ap.parse_args()
    if not os.path.isdir(TPL):
        print('[TRACE] UNVERIFIED 模板目录不存在: %s' % TPL)
        return 2
    rows = []
    for tpl, name in PAIRS:
        tp = os.path.join(TPL, tpl)
        hp = os.path.join(HOOKS, name)
        sp = hp + '.installed'
        tsha = sha(tp)
        hsha = sha(hp)
        stamp = read_stamp(sp) if os.path.isfile(sp) else {}
        ssha = stamp.get('template_sha256') or ''
        if not os.path.isfile(hp):
            cls = 'MISSING'
        elif not os.path.isfile(tp):
            cls = 'TEMPLATE_MISSING'
        elif hsha == tsha:
            cls = 'IN_SYNC'
        # r140 自抓（反向验证当场抓反）：初版把两个条件写反了 ——
        #   · installed == stamp ⇒ 实装件**就是当初装的模板** ⇒ 变的是**模板**（DRIFT_OLD_TEMPLATE）
        #   · installed != stamp ⇒ 实装件**不是**当初装的模板 ⇒ 变的是**实装件**（DRIFT_AFTER_INSTALL）
        # 三个变体（V1/V2/V3）全部判反，是 #32「先造非空面复跑」的直接收益。
        elif not ssha:
            cls = 'NO_STAMP'
        elif hsha == ssha:
            cls = 'DRIFT_OLD_TEMPLATE'
        else:
            cls = 'DRIFT_AFTER_INSTALL'
        # r141 扩展（R140-4 落地）：把印记里的 invoker / reason 也读出来，
        # 让归因从「哪次安装」细化到「谁、为什么装」。
        inv = stamp.get('invoker') or {}
        rows.append({'hook': name, 'class': cls,
                     'template_sha': tsha[:16], 'installed_sha': hsha[:16],
                     'stamp_template_sha': ssha[:16],
                     'installed_at': stamp.get('installed_at') or '',
                     'invoker': inv,
                     'invoker_desc': ('%s@%s' % (inv.get('git_user') or '?',
                                                 (inv.get('git_email') or '?').split('@')[0])
                                      if inv else '(无印记或无 invoker 字段)'),
                     'reason': stamp.get('reason') or '(未说明)',
                     'attribution': {
                         'IN_SYNC': '实装件与模板一致，无漂移',
                         'DRIFT_AFTER_INSTALL': '实装件与印记不同（装后被人改了 .git/hooks/）',
                         'DRIFT_OLD_TEMPLATE': '实装件与印记相同、但与当前模板不同（模板被改后没重装，装的是旧模板）',
                         'NO_STAMP': '无印记（r140 之前装的）—— 归因不可用，须重装补印记',
                         'MISSING': '实装件不存在',
                         'TEMPLATE_MISSING': '模板不存在',
                     }.get(cls, '')})
    drift = [r for r in rows if r['class'] not in ('IN_SYNC',)]
    # r140 自抓二：V3（删印记但模板与实装仍一致）被判 IN_SYNC —— 这是合理优先级
    # （无漂移就不需要归因），但「无印记」本身是隐患：下次漂移时无法归因。
    # 故单列一条「印记存在性」告警：不影响 drift 判定，但在读数里显形。
    no_stamp = [r['hook'] for r in rows if not r['installed_at']]
    from collections import Counter
    cnt = Counter(r['class'] for r in rows)
    doc = {'schema': 'hook-trace-r140-v1',
           'cmd': 'python 05-exec/r140_hook_trace.py --json <out>',
           'face': {'pairs_n': len(rows),
                     'by_class': dict(cnt),
                     'drift_n': len(drift),
                     'no_stamp_n': len(no_stamp),
                     'no_stamp': no_stamp,
                     'reading': {
                         'drift_n': '非 IN_SYNC 的 hook 数。任一非 IN_SYNC 即判红。',
                         'by_class': ('六态：IN_SYNC 无漂移 / DRIFT_AFTER_INSTALL 装后被人改 /',
                                      'DRIFT_OLD_TEMPLATE 装了旧模板 / NO_STAMP 无印记 / MISSING / TEMPLATE_MISSING'),
                         'attribution': '每行的归因说明 —— 这是本面相对于第 51 门（只报不一致）的核心增量：能回答「怎么造成的」',
                         'no_stamp_n': '无印记的 hook 数。不影响 drift 判定（无漂移就不需要归因），但意味着下次漂移无法归因 —— 须重装补印记',
                     }},
           'rows': rows,
           'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline=chr(10)) as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    fa = doc['face']
    print('[TRACE] %d 对 hook｜漂移 %d｜分布 %s'
          % (fa['pairs_n'], fa['drift_n'], json.dumps(fa['by_class'], ensure_ascii=False)))
    for r in rows:
        print('  %-12s %-22s %s' % (r['hook'], r['class'], r['attribution'][:52]))
        if r['installed_at']:
            print('               installed_at=%s stamp_sha=%s' % (r['installed_at'], r['stamp_template_sha']))
            # r141：归因到人与次（R140-4 落地）
            print('               invoker=%s reason=%s' % (r.get('invoker_desc'), r.get('reason')))
        else:
            print('               (无印记 —— 下次漂移将无法归因，建议重装)')
    if no_stamp:
        print('  NOTE 无印记 hook: %s（不影响本次判定，但建议重装补印记）' % ', '.join(no_stamp))
    if args.out:
        print('[TRACE] JSON -> %s' % args.out)
    return 1 if drift else 0


if __name__ == '__main__':
    raise SystemExit(main())