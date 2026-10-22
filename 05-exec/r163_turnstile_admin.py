# -*- coding: utf-8 -*-
# ⚠️ RETIRED（r173 退役，未删文件）—— 请改用官方 CLI：`wrangler turnstile widget <list|create|get|update|delete> [alpha]`
#
# 退役理由（r173 一手实测）：wrangler 4.151.2 已内置 Turnstile widget 管理（alpha），
#   五个子命令覆盖本件全部功能且输出更规整（含 clearance_level / bot_fight_mode / created_on）。
#   实测对账：`wrangler turnstile widget list` rc=0 列出 r163 所建 widget（sitekey
#   0x4AAAAAAFgp4grsBDhuMqpl）；`wrangler turnstile widget get <sitekey>` rc=0 同源。
#   ⇒ 按「转诊优先、不重复造」（r149 同向），本件（裸 API 封装）退役。
#
# 保留原因：R281 零物理删除；且准入门仍登记其为产读数脚本（直接删会造成登记面悬空）。
# 本件仍可运行（API 未变），但**新代码/新 skill 一律走官方 CLI**。
#
# ── 以下为退役前原文 ────────────────────────────────────────────────
# r163_turnstile_admin.py -- Cloudflare Turnstile widget 管理（纯 API，无 GUI）。
#
# 存在理由（goal 第 11 轮）：第 67 门矩阵实测 Turnstile **零引用**，且 r163 早前把它归为
#   「外部凭据缺口（无账号无 key）」。本轮实测**推翻**该结论：wrangler 已登录的 OAuth token
#   具备 `challenge-widgets.write` 权限，`POST /accounts/<id>/challenges/widgets` 直接可建。
#   ⇒ 打开「Turnstile 可搭配」的门：sitekey 可程序化创建，落点是真实存在的登录/注册表单。
#
# 用法:
#   python 05-exec/r163_turnstile_admin.py --list
#   python 05-exec/r163_turnstile_admin.py --create --name <名> --domain <域名> [--mode managed|invisible|non-interactive]
#   python 05-exec/r163_turnstile_admin.py --delete <sitekey>     # 回滚
# 退出码: 0 成功 / 1 API 拒绝 / 2 凭据或面不可用（UNVERIFIED）
import argparse
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime

CFG = os.path.expanduser(r'~\AppData\Roaming\xdg.config\.wrangler\config\default.toml')
ACCT_DEFAULT = '04b1466b2606b678a332fe6f26aa87ec'
API = 'https://api.cloudflare.com/client/v4'


def token():
    """取 wrangler 的 OAuth token（只读配置，不外传、不打印）。"""
    try:
        raw = io.open(CFG, encoding='utf-8').read()
    except OSError:
        return None, 'wrangler 配置不存在: %s' % CFG
    m = re.search(r'oauth_token\s*=\s*"([^"]+)"', raw)
    if not m:
        return None, '配置里没有 oauth_token ⇒ 未登录（先 wrangler login）'
    return m.group(1), None


def call(method, path, body=None, timeout=60):
    tok, err = token()
    if tok is None:
        return None, err
    url = API + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={'Authorization': 'Bearer ' + tok,
                                          'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8')), None
    except urllib.error.HTTPError as e:
        tail = e.read()[:400].decode('utf-8', 'replace')
        return None, 'HTTP %s: %s' % (e.code, tail)
    except (urllib.error.URLError, OSError) as e:
        return None, 'NET: %r' % (e,)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--account', default=ACCT_DEFAULT)
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--create', action='store_true')
    ap.add_argument('--delete', default='')
    ap.add_argument('--name', default='')
    ap.add_argument('--domain', default='')
    ap.add_argument('--mode', default='managed',
                    choices=('managed', 'invisible', 'non-interactive'))
    ap.add_argument('--json', dest='out', default='')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()

    doc = {'schema': 'turnstile-admin-r163-v1',
           'cmd': 'python 05-exec/r163_turnstile_admin.py <--list|--create|--delete>',
           'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}

    if args.list:
        d, err = call('GET', '/accounts/%s/challenges/widgets' % args.account)
        if d is None:
            print('[TURNSTILE] UNVERIFIED %s' % err)
            return 2
        res = d.get('result') or []
        print('[TURNSTILE] widgets: %d' % len(res))
        for w in res:
            print('  %-34s mode=%-14s domains=%s'
                  % (w.get('name'), w.get('mode'), ','.join(w.get('domains') or [])[:60]))
        doc['widgets'] = [{'name': w.get('name'), 'sitekey': w.get('sitekey'),
                           'mode': w.get('mode'), 'domains': w.get('domains')} for w in res]
        doc['state'] = 'LISTED'
        rc = 0
    elif args.create:
        if not args.name or not args.domain:
            print('[TURNSTILE] REFUSE --create 须给 --name 与 --domain')
            return 2
        body = {'name': args.name, 'domains': [args.domain],
                'mode': args.mode, 'region': 'world'}
        d, err = call('POST', '/accounts/%s/challenges/widgets' % args.account, body)
        if d is None:
            print('[TURNSTILE] FAIL %s' % err)
            return 1
        r_ = d.get('result') or {}
        print('[TURNSTILE] CREATED name=%s sitekey=%s mode=%s domains=%s'
              % (r_.get('name'), r_.get('sitekey'), r_.get('mode'), r_.get('domains')))
        print('            回滚: python 05-exec/r163_turnstile_admin.py --delete %s' % r_.get('sitekey'))
        # secret **不落 JSON**（避免把凭据写进仓）；只记长度证明拿到过
        doc.update({'state': 'CREATED', 'sitekey': r_.get('sitekey'),
                    'name': r_.get('name'), 'mode': r_.get('mode'),
                    'domains': r_.get('domains'),
                    'secret_present': bool(r_.get('secret')),
                    'secret_len': len(r_.get('secret') or ''),
                    'rollback': 'python 05-exec/r163_turnstile_admin.py --delete %s' % r_.get('sitekey')})
        rc = 0
    elif args.delete:
        d, err = call('DELETE', '/accounts/%s/challenges/widgets/%s' % (args.account, args.delete))
        if d is None:
            print('[TURNSTILE] FAIL %s' % err)
            return 1
        print('[TURNSTILE] DELETED sitekey=%s' % args.delete)
        doc.update({'state': 'DELETED', 'sitekey': args.delete})
        rc = 0
    else:
        ap.print_help()
        return 2

    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    return rc


def selftest():
    """三腿：① 凭据可解析（不打印值）② 真调 list 面（取不到=UNVERIFIED 不得判绿）
    ③ secret 不落盘的守卫：断言生成 doc 的分支不含 secret 原文（只含长度）。"""
    legs = []
    tok, err = token()
    legs.append(('f1_token_resolvable', tok is not None and len(tok) > 20,
                 'token_len=%s err=%s' % (len(tok) if tok else 0, err or '')))
    d, err2 = call('GET', '/accounts/%s/challenges/widgets' % ACCT_DEFAULT)
    legs.append(('f2_list_api_reachable', d is not None,
                 'err=%s' % (err2 or '')[:120]))
    # f3：**落盘字段**里不得出现 secret 原文（只许 len / 布尔存在性）。
    #   r163 自抓：首版断言写宽了 —— 把 `bool(x.get('secret'))` / `len(x.get('secret'))`
    #   这类**安全取用**也判成泄漏（假红）。正解是只看写进 JSON 的那个 dict：
    #   构造一次 doc 结构，扫描其键值，断言没有 secret 原值。
    src = io.open(os.path.abspath(__file__), encoding='utf-8').read()
    # 扫「会被 json.dump 的表达式」：doc.update({...}) 与 doc = {...}
    dump_blocks = re.findall(r'doc(?:.update)?\s*[=(]\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}', src, re.S)
    bad_keys = []
    for blk in dump_blocks:
        for kv in re.finditer(r"['\"]([a-z_]+)['\"]\s*:\s*([^,\n]+)", blk):
            key, val = kv.group(1), kv.group(2)
            if 'secret' in key and 'len' not in key and 'present' not in key:
                bad_keys.append((key, val.strip()[:40]))
    legs.append(('f3_secret_not_persisted', not bad_keys,
                 '落盘字段里的 secret 键=%s（应只允许 secret_len / secret_present）'
                 % (bad_keys or '[]')))
    for n, ok, d_ in legs:
        print('%s %-34s %s' % ('PASS' if ok else 'FAIL', n, d_))
    n_ok = sum(1 for _, ok, _ in legs if ok)
    print('[TURNSTILE:SELFTEST] %d/%d' % (n_ok, len(legs)))
    return 0 if n_ok == len(legs) else 1


if __name__ == '__main__':
    raise SystemExit(main())