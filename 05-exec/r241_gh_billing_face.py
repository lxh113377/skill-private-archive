# -*- coding: utf-8 -*-
'''r241_gh_billing_face.py - GitHub 官方计费用量面（r241 新建，只读）。

存在理由（r241 一手）：配额件 r196 里我自己写下过一条缺口 ——
    「官方免费分钟数本轮未取到可靠出处（docs 页面为 JS 壳，服务端渲染取不到表格）
      ⇒ 依 r196 自立的规矩：分母无可靠出处就只报绝对值，不折算百分比。」
  那条规矩是对的，但结论「无可靠出处」是**当时的取数方式**造成的：文档页爬不到，不等于官方没有可取的数。
  本轮实测：旧用户计费端点 /users/{u}/settings/billing/actions 已迁移（HTTP 410 + documentation_url），
  新端点 **/users/{u}/settings/billing/usage** 直接返回 usageItems（product / sku / quantity / unitType /
  grossAmount / discountAmount / netAmount / repositoryName）⇒ 这才是**权威用量**：既给绝对值，
  也给「折后净额」（netAmount=0 即免费额度内、没花钱）。

顺带纠正一个假设：本仓 skill-private-archive 的 visibility=public ⇒ 其 Actions 分钟本来就免费，
  名册里那 447.92 墙钟分钟**不占额度**（墙钟 != 计费本就写在 r196 的 caveat 里）。

判据三态：取到 usageItems 且能聚合 ⇒ MEASURED(0)；端点不可达/凭据问题 ⇒ UNVERIFIED(2) 并写明 HTTP 与错误；
  usageItems 为空 ⇒ MEASURED 但记 items=0（不是取不到，是本期真没有用量）。
用法: python 05-exec/r241_gh_billing_face.py [--json <件>] [--since YYYY-MM-DD] [--until YYYY-MM-DD]
'''
import argparse
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def gh_api(path, tries=3):
    """调 gh api（沿用本机已登录凭据）。返回 (rc, 文本)。

    r241 自抓二：本机到 api.github.com 会偶发 EOF（同一命令 cmd 里成功、subprocess 里失败），
    与全仓反复记录的网络抖动同族 ⇒ 内置退避重试，别把瞬时失败读成「端点不可用」。
    """
    last = (90, 'no attempt')
    for i in range(tries):
        try:
            r = subprocess.run(['gh', 'api', path], capture_output=True, text=True,
                               encoding='utf-8', errors='replace', timeout=120)
            out = ((r.stdout or '') + (r.stderr or ''))
            if r.returncode == 0:
                return 0, out
            last = (r.returncode, out)
            if 'EOF' not in out and 'timed out' not in out.lower():
                return last
        except Exception as e:
            last = (90, 'EXC %r' % (e,))
        import time as _t
        _t.sleep(4)
    return last


def login():
    # r241 自抓：首版把 '--jq .login' 拼进路径传参 ⇒ gh 把它当路径的一部分，返回 404
    #   「Not Found」—— 端点没错，是我把 flag 塞进了 path。改为取 /user 的 JSON 自己解。
    rc, out = gh_api('/user')
    if rc != 0:
        return None, out.strip()[:160]
    try:
        d = json.loads(out)
    except ValueError:
        return None, out.strip()[:160]
    if not isinstance(d, dict) or not d.get('login'):
        return None, out.strip()[:160]
    return str(d['login']), None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out', default='')
    ap.add_argument('--since', default='')
    ap.add_argument('--until', default='')
    args = ap.parse_args(argv)
    who, why = login()
    if not who:
        print('[GHBILL:UNVERIFIED] 取不到 gh 登录名（凭据层不可用）: %s' % why)
        return 2
    q = ''
    if args.since:
        q += ('&' if q else '?') + 'since=' + args.since
    if args.until:
        q += ('&' if q else '?') + 'until=' + args.until
    rc, out = gh_api('/users/%s/settings/billing/usage%s' % (who, q))
    if rc != 0:
        print('[GHBILL:UNVERIFIED] 计费端点不可达 rc=%s: %s' % (rc, out.strip()[:200]))
        return 2
    try:
        doc = json.loads(out)
    except ValueError:
        print('[GHBILL:UNVERIFIED] 端点返回不可析: %s' % out.strip()[:200])
        return 2
    items = doc.get('usageItems') or []
    agg = {}
    for it in items:
        key = '%s / %s' % (it.get('product'), it.get('sku'))
        e = agg.setdefault(key, {'quantity': 0.0, 'unitType': it.get('unitType'),
                                 'gross': 0.0, 'discount': 0.0, 'net': 0.0, 'items': 0,
                                 'repos': []})
        e['quantity'] += float(it.get('quantity') or 0)
        e['gross'] += float(it.get('grossAmount') or 0)
        e['discount'] += float(it.get('discountAmount') or 0)
        e['net'] += float(it.get('netAmount') or 0)
        e['items'] += 1
        rn = it.get('repositoryName')
        if rn and rn not in e['repos']:
            e['repos'].append(rn)
    dates = sorted(set(str(it.get('date'))[:10] for it in items if it.get('date')))
    mins = sum(v['quantity'] for k, v in agg.items()
               if str(v.get('unitType')) == 'Minutes')
    net_all = sum(v['net'] for v in agg.values())
    gross_all = sum(v['gross'] for v in agg.values())
    res = {
        'schema': 'gh-billing-usage-v1', 'readonly': True,
        'provenance_cmd': 'python 05-exec/r241_gh_billing_face.py --json <件>',
        'account': who,
        'endpoint': '/users/%s/settings/billing/usage' % who,
        'window_items_dates': [dates[0], dates[-1]] if dates else None,
        'state': 'MEASURED',
        'items_n': len(items),
        'minutes_total': round(mins, 2),
        'gross_total': round(gross_all, 4),
        'net_total': round(net_all, 4),
        'wholly_discounted': bool(items) and abs(net_all) < 1e-9,
        'per_product': agg,
        'note': ('官方端点返回的计费用量（非墙钟分钟）。netAmount=0 表示该用量全额折扣 ⇒ 免费额度内、未花钱。'
                 '仓库可见性决定是否计费：public 仓 Actions 分钟免费。'),
    }
    if args.out:
        op = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
        io.open(op, 'w', encoding='utf-8', newline=chr(10)).write(
            json.dumps(res, ensure_ascii=False, indent=1))
    print('[GHBILL] 账 %s ｜ 计费项 %d 条 ｜ 分钟合计 %s ｜ gross %s ｜ net %s%s' % (
        who, len(items), round(mins, 2), round(gross_all, 4), round(net_all, 4),
        '（全额折扣）' if res['wholly_discounted'] else ''))
    for k in sorted(agg):
        v = agg[k]
        print('  %-40s %10s %-10s net=%s' % (k[:40], round(v['quantity'], 1),
                                              str(v['unitType']), round(v['net'], 4)))
    print('[GHBILL:PASS] 官方计费用量已取（取数入口 = %s）' % res['endpoint'])
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())