# -*- coding: utf-8 -*-
'''r242_turnstile_usage_face.py - Turnstile 官方用量面（r242 新建，只读）。

存在理由（r242 一手）：名册对 Turnstile 的第 ④ 层写的是「无读数面」，理由引的是 r228 那句
    「该读数门（r163_turnstile_face）argv 不带 --json、不做额度读数」。
  那句话描述的是**当时那个门**，不是「Turnstile 查不到用量」。r242 用官方自省实测：
    __schema.types 里存在 AccountTurnstileAdaptiveGroups 及其 Dimensions/Filter 类型，
    且 account 类型 257 个字段里有 turnstileAdaptiveGroups ⇒ **官方用量数据集存在**。
  又一次「取不到有两种：世界不给，和我取的方式不对」。

本面把「不猜」写进代码：**运行时先自省** AccountTurnstileAdaptiveGroupsFilter_InputObject
  的 inputFields，从里面挑日期区间参数名（优先 datetime_geq/datetime_leq，退回 *_geq/*_leq 家族），
  自己找出来的名字自己用、并随产物落盘 ⇒ 名字变了也当场可见，不靠我记忆里的字面量。

判据三态：取到 count 并成功聚合 ⇒ MEASURED(0)；token 取不到/端点不可达/自省拿不到日期参数名 ⇒ UNVERIFIED(2)
  并把原因与「自省到的全部 inputFields」一起落盘（供下一轮直接看，不必复现）。
用法: python 05-exec/r242_turnstile_usage_face.py [--json <件>] [--days 25]
'''
import argparse
import datetime
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

ENDPOINT = 'https://api.cloudflare.com/client/v4/graphql'


def introspect_filter_fields(gql, tok):
    q = '{ __type(name: "AccountTurnstileAdaptiveGroupsFilter_InputObject") { inputFields { name } } }'
    r = gql(q, tok, ENDPOINT)
    d = (r or {}).get('data') or {}
    t = d.get('__type')
    if not t:
        return None, (r or {}).get('errors') or 'introspection 返回空（网络/限流？）'
    return [f['name'] for f in (t.get('inputFields') or [])], None


def pick_range(names):
    '''从自省到的输入字段里挑日期区间参数（不猜字面量）。'''
    for a, b in (('datetime_geq', 'datetime_leq'), ('date_geq', 'date_leq')):
        if a in names and b in names:
            return a, b
    geqs = [n for n in names if n.endswith('_geq') and ('date' in n or 'time' in n)]
    leqs = [n for n in names if n.endswith('_leq') and ('date' in n or 'time' in n)]
    if geqs and leqs:
        return sorted(geqs)[0], sorted(leqs)[0]
    return None, None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out', default='')
    ap.add_argument('--days', type=int, default=25)
    args = ap.parse_args(argv)
    import r199_workers_face as wf
    import r200_cf_introspect_probe as P
    tok, src = wf.oauth_token()
    res = {'schema': 'turnstile-usage-v1', 'readonly': True,
           'provenance_cmd': 'python 05-exec/r242_turnstile_usage_face.py --json <件>',
           'endpoint': ENDPOINT, 'token_src': src,
           'dataset': 'account.turnstileAdaptiveGroups'}
    if not tok:
        res['state'] = 'UNVERIFIED'
        res['why'] = '本机 wrangler OAuth 凭据取不到（whoami 可核）'
    else:
        names, why = introspect_filter_fields(P.gql, tok)
        res['filter_inputs_n'] = (len(names) if names else None)
        if names is None:
            res['state'] = 'UNVERIFIED'
            res['why'] = '自省失败：%s' % (str(why)[:200],)
        else:
            a, b = pick_range(names)
            res['range_args'] = [a, b]
            if not a:
                res['state'] = 'UNVERIFIED'
                res['why'] = '自省到的 inputFields 里找不到日期区间参数 ⇒ 不猜，记未量'
                res['filter_inputs_all'] = names
            else:
                until = datetime.date.today()
                since = until - datetime.timedelta(days=args.days)
                q = ('{ viewer { accounts(filter: {accountTag: "%s"}) {'
                     ' turnstileAdaptiveGroups(limit: 10000, filter: {%s: "%sT00:00:00Z", %s: "%sT00:00:00Z"}) {'
                     ' count dimensions { date } } } } }' % (
                         wf.ACCOUNT_TAG, a, since.isoformat(), b, until.isoformat()))
                try:
                    r = P.gql(q, tok, ENDPOINT)
                    groups = ((((r or {}).get('data') or {}).get('viewer') or {}).get('accounts') or [{}])[0]
                    gs = groups.get('turnstileAdaptiveGroups') or []
                    total = sum(g.get('count') or 0 for g in gs)
                    dates = sorted(set((g.get('dimensions') or {}).get('date') for g in gs if g.get('dimensions')));
                    res['state'] = 'MEASURED'
                    res['window'] = [since.isoformat(), until.isoformat()]
                    res['count_total'] = total
                    res['groups_n'] = len(gs)
                    res['days_with_data'] = len(dates)
                    res['dates'] = dates
                    res['why'] = ''
                except Exception as e:
                    res['state'] = 'UNVERIFIED'
                    res['why'] = '查询失败：%r' % (e,)[:200]
    if args.out:
        op = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
        io.open(op, 'w', encoding='utf-8', newline=chr(10)).write(
            json.dumps(res, ensure_ascii=False, indent=1))
    print('=== Turnstile 官方用量（r242）===')
    if res['state'] == 'MEASURED':
        print('  MEASURED 校验请求合计 %s 次 ｜ 窗口 %s ｜ 有数据天 %s' % (
            res.get('count_total'), '/'.join(res.get('window') or []), res.get('days_with_data')))
        print('  [TURNSTILE:PASS] 官方数据集 account.turnstileAdaptiveGroups 已取值（参数名来自运行时自省）')
        return 0
    print('  UNVERIFIED %s（R247：取不到不等于零用量）' % res.get('why'));
    return 2


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())