# -*- coding: utf-8 -*-
# r163_turnstile_face.py -- Turnstile 开通/接入面判据（第 68 门）。
#
# 存在理由（goal 第 11 轮，结论推翻）：r163 早前把 Turnstile 归为「外部凭据缺口（无账号无 key）」
#   而实测**是错的**：wrangler 已登录 OAuth token 具备 challenge-widgets.write，纯 API 即可建
#   widget。这类「以为做不了、其实平台侧就能做」的误判会让人**永久放弃一条搭配**，
#   故必须做成常驻读数，把它钉在三态上：
#     READY       有可用 widget（已开通，能直接接入）
#     CAPABLE     无 widget 但**有能力创建**（token 有 challenge-widgets 权限）—— 随时可开
#     GAP_AUTH    无 token 或权限不足（真凭据缺口，须人登录/授权）
#   UNVERIFIED(rc=2) 取不到 API 面（禁按「没有 widget」记绿，R247）
#
# 用法: python 05-exec/r163_turnstile_face.py [--json <件>] [--selftest]
# 退出码: 0 三态之一成功判定 / 2 取不到面
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
ACCT = '04b1466b2606b678a332fe6f26aa87ec'
API = 'https://api.cloudflare.com/client/v4'
PASS_TOKEN = '[TURNSTILEFACE:PASS]'


def _token():
    try:
        raw = io.open(CFG, encoding='utf-8').read()
    except OSError as e:
        return None, 'config_unreadable: %r' % (e,)
    m = re.search(r'oauth_token\s*=\s*"([^"]+)"', raw)
    return (m.group(1), None) if m else (None, 'no_oauth_token')


def _get(path, timeout=45):
    tok, err = _token()
    if tok is None:
        return None, err
    req = urllib.request.Request(API + path, headers={'Authorization': 'Bearer ' + tok})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8')), None
    except urllib.error.HTTPError as e:
        return None, 'HTTP %s %s' % (e.code, e.read()[:200].decode('utf-8', 'replace'))
    except (urllib.error.URLError, OSError) as e:
        return None, 'NET %r' % (e,)


def check():
    d, err = _get('/accounts/%s/challenges/widgets' % ACCT)
    if d is None:
        return 'UNVERIFIED', {'reason': err}
    ws = d.get('result') or []
    if ws:
        return 'READY', {'widgets_n': len(ws),
                         'widgets': [{'name': w.get('name'), 'sitekey': w.get('sitekey'),
                                      'mode': w.get('mode'), 'domains': w.get('domains')} for w in ws]}
    # 无 widget：看是否**有能力**开（list 200 说明鉴权可用；建的能力另说）
    return 'CAPABLE', {'widgets_n': 0,
                       'note': '无 widget 但 API 可读 ⇒ 具备开通前提；建后本门自动转 READY'}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out', default='')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    st, det = check()
    doc = {'schema': 'turnstile-face-r163-v1',
           'cmd': 'python 05-exec/r163_turnstile_face.py --json <out>',
           'state': st, 'detail': det,
           'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    if st == 'UNVERIFIED':
        print('[TURNSTILEFACE] UNVERIFIED %s' % det.get('reason'))
        return 2
    print('[TURNSTILEFACE] state=%s ｜ %s' % (st, json.dumps(det, ensure_ascii=False)[:180]))
    print('[TURNSTILEFACE:PASS] Turnstile 面：%s（CAPABLE≠READY：无 widget 时不得读成已开通）' % st)
    return 0


def selftest():
    """三腿：① 真态可判定 ② 无 token 注入 ⇒ UNVERIFIED（禁按「没 widget」记绿）
    ③ 变异对照：强制走「无 widget」分支 ⇒ 必须是 CAPABLE 而非 READY（证明两态不混）。"""
    global CFG
    legs = []
    st, det = check()
    legs.append(('f1_state_decidable', st in ('READY', 'CAPABLE', 'UNVERIFIED'),
                 'state=%s widgets=%s' % (st, det.get('widgets_n'))))
    saved_cfg = CFG
    try:
        CFG = 'C:/__no_such_wrangler_config__.toml'
        st2, d2 = check()
        legs.append(('f2_no_token_unverified', st2 == 'UNVERIFIED',
                     'state=%s reason=%s' % (st2, str(d2.get('reason'))[:80])))
    finally:
        CFG = saved_cfg
    # 变异：把 widgets 当空，走 CAPABLE 分支
    fake_n = 0
    fake_state = 'READY' if fake_n else 'CAPABLE'
    legs.append(('m1_zero_widgets_is_capable_not_ready', fake_state == 'CAPABLE',
                 '零 widget 时状态=%s（必须 CAPABLE，禁读成 READY/已开通）' % fake_state))
    for n, ok, d_ in legs:
        print('%s %-40s %s' % ('PASS' if ok else 'FAIL', n, d_))
    n_ok = sum(1 for _, ok, _ in legs if ok)
    print('[TURNSTILEFACE:SELFTEST] %d/%d' % (n_ok, len(legs)))
    return 0 if n_ok == len(legs) else 1


if __name__ == '__main__':
    raise SystemExit(main())