# -*- coding: utf-8 -*-
# r163_free_tools_face.py -- 免费开发者工具可达性名册（第 65 门）。
#
# 存在理由（r163/r164）：截图那批「独立开发者穷鬼套餐」工具（D1/R2/Pages/Workers/
#   Turnstile/Resend/Upstash/SQLite/GitHub/VS Code）在本机到底能不能用、有没有登录，
#   此前只活在会话记忆里；下一轮换个会话就得重新摸，且容易把「取不到数」读成「没有该工具」
#   （r163 一手：gh 被 0 字节空壳遮蔽，取证脚本自身也中招，差点写成「本机没有 gh」）。
#   本门把现状变成每轮真跑的读数面 —— 缺口具名，禁读成干净（R247）。
#
# 三态口径（与 run_gates 一致）：
#   READY      CLI 可跑 且 需登录的已登录
#   GAP_CRED   CLI 可跑但无凭据（属外部凭据缺口 #29③，不是可自动化项）
#   GAP_CLI    本机无该 CLI（平台能力/安装缺口）
#   BROKEN     CLI 在位但不可用（遮蔽/空壳/同名劫持）=> 本门唯一判红态
#
# 判红只一条：BROKEN。GAP_* 是诚实显形不是缺陷（否则每轮固定红，稀释真红）。
# 用法: python 05-exec/r163_free_tools_face.py [--json <件>] [--selftest]
# 退出码: 0 无 BROKEN / 1 有 BROKEN / 2 探针面不可用
import argparse
import io
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _sh(argv, timeout=90):
    try:
        p = subprocess.run(argv, capture_output=True, text=True,
                           encoding='utf-8', errors='replace', timeout=timeout)
        return p.returncode, (p.stdout or '') + (p.stderr or '')
    except (OSError, subprocess.SubprocessError) as e:
        return None, 'EXC %r' % e


def _ps(script, timeout=120):
    try:
        p = subprocess.run(["powershell", "-NoProfile", "-Command", script],
                           capture_output=True, text=True, encoding='utf-8',
                           errors='replace', timeout=timeout)
        return p.returncode, (p.stdout or '')
    except (OSError, subprocess.SubprocessError):
        return None, ''


def probe_gh():
    """gh：三方争夺同一命令名（官方 CLI / npm 第三方包 / 0 字节空壳）。

    必须按解析后的真实路径调用 —— 裸名调用可能跑到 D:/npm-global/gh（2.8.9，
    连 --help 都抛 TypeError 而退出码为 0）。"""
    cands = [
        os.path.join(os.environ.get('ProgramFiles', r'C:\Program Files'), 'GitHub CLI', 'gh.exe'),
        os.path.expanduser(r'~\scoop\shims\gh.exe'),
    ]
    real = next((c for c in cands if os.path.isfile(c) and os.path.getsize(c) > 0), None)
    if real is None:
        return 'GAP_CLI', {'detail': 'no_gh_binary'}
    rc, out = _sh([real, '--version'])
    if rc != 0 or 'gh version' not in out:
        return 'BROKEN', {'detail': 'gh_present_but_not_runnable', 'out': out[:120]}
    rc2, out2 = _sh([real, 'auth', 'status'])
    logged = (rc2 == 0 and 'Logged in' in out2)
    # 跨解释器一致性（r163 教训：Python 侧好、PowerShell 侧坏，只查一侧会打假绿）
    _, ps = _ps("$c=Get-Command gh -EA SilentlyContinue; if(-not $c){'NONE'}else{$c.Source}")
    ps_path = (ps or '').strip().splitlines()[:1]
    same = bool(ps_path) and ps_path[0].upper() != 'NONE' and \
        os.path.normcase(ps_path[0]) == os.path.normcase(shutil.which('gh') or '')
    st = 'READY' if logged else 'GAP_CRED'
    note = {'version': out.strip().splitlines()[0][:40], 'logged_in': logged,
            'cross_interpreter_agree': same}
    if not same:
        return 'BROKEN', dict(note, detail='cross_interpreter_shadowed',
                              ps_resolved=ps_path[0] if ps_path else None)
    return st, note


_WRANGLER_CACHE = {}
_WRANGLER_CALLS = {'n': 0}


def probe_wrangler(service=None):
    """wrangler（覆盖 Cloudflare D1 / R2 / Pages / Workers 的 CLI 面）。

    r163 自抓（成本面）：名册里四个 Cloudflare 条目各调一次本探针，每次 spawn 一个 node
    进程（实测单跑 ~6s）⇒ 进门表后本门在聚合里耗 32.8s，占全轮 1/4。四个条目读的是
    **同一个事实**（wrangler 在不在、登没登录），故按进程内缓存复用一次读数：
    探针语义不变、判据不变，只是不重复 spawn（同 r149「转诊优先、不重复造」同向）。"""
    if 'state' not in _WRANGLER_CACHE:
        st, note = _probe_wrangler_once()
        _WRANGLER_CACHE['state'], _WRANGLER_CACHE['note'] = st, note
    st = _WRANGLER_CACHE['state']
    note = dict(_WRANGLER_CACHE['note'])
    # r163 自抓（粒度错误）：四个 Cloudflare 条目共用一条探针，旧式把**任一**服务未开通
    #   报成四条全 GAP_SERVICE ⇒ D1/Pages 明明 ready 也被连坐。按条目只判自己那项。
    if service and st == 'GAP_SERVICE':
        svc = (note.get('services') or {}).get(service) or {}
        if svc.get('state') == 'ready':
            return 'READY', dict(note, judged_service=service)
        if svc.get('state') in ('not_probed', 'probe_timeout'):
            # 未探测 ≠ 未开通（禁把「我没测」写成「平台没开」）
            return 'GAP_CRED', dict(note, judged_service=service,
                                    detail='service_not_probed', svc_state=svc.get('state'))
        return 'GAP_SERVICE', dict(note, judged_service=service,
                                  detail='service_not_enabled', code=svc.get('code'))
    if service:
        note['judged_service'] = service
    return st, note


def _probe_wrangler_once():
    _WRANGLER_CALLS['n'] += 1
    exe = shutil.which('wrangler') or shutil.which('wrangler.cmd')
    if not exe:
        return 'GAP_CLI', {'detail': 'wrangler_not_on_path'}
    rc, out = _sh([exe, '--version'])
    ver = ''
    for ln in (out or '').splitlines():
        if any(ch.isdigit() for ch in ln):
            ver = ln.strip()[:40]
            break
    if rc != 0:
        return 'BROKEN', {'detail': 'wrangler_not_runnable', 'out': out[:120]}
    rc2, out2 = _sh([exe, 'whoami'])
    logged = 'logged in' in (out2 or '').lower()
    if not logged:
        return 'GAP_CRED', {'version': ver, 'logged_in': False}
    # r163 自抓（假绿，本轮 R163-2 一手）：CLI 能跑 + 已登录 **不等于** 服务面可用。
    #   实测：R2 服务未开通时本门仍判 READY，而 wrangler r2 bucket list 回
    #   `403 code 10042 Please enable R2 through the Cloudflare Dashboard`。
    #   「工具装好了、登录了」与「这项服务能不能用」是两件事，混判就是假绿（R247 同向）。
    #   修法 = 登录后再**逐服务真调一次只读接口**，把不可用态具名成 GAP_SERVICE（不是 BROKEN：
    #   不是工具坏，是服务未开通）。
    svc = {}
    probes = (
        ('d1', [exe, 'd1', 'list', '--json']),
        ('r2', [exe, 'r2', 'bucket', 'list']),
        ('pages', [exe, 'pages', 'project', 'list']),
        # Workers：wrangler 的 deployments 子命令要 --name，故直接查账户下脚本清单（只读）
        ('workers', [exe, 'deployments', 'list', '--name', '__probe__']),
    )
    for name, argv in probes:
        rc3, out3 = _sh(argv, timeout=120)
        blob = (out3 or '')
        low = blob.lower()
        enabled = (rc3 == 0)
        # 具名归因：服务未开通有稳定错误码，不得与网络失败混为「不可用」
        code = ''
        for cand in ('10042', '10015', '10000', '10001'):
            if cand in blob:
                code = cand
                break
        if not enabled and ('enable' in low and 'dashboard' in low):
            svc[name] = {'state': 'not_enabled', 'code': code or '10042'}
        elif not enabled and code:
            svc[name] = {'state': 'api_error', 'code': code}
        elif rc3 is None:
            svc[name] = {'state': 'probe_timeout'}
        elif 'couldn' in low and 'name' in low:
            # 命令形态不适用（如 --name 占位）——属**未探测**，不是「服务未开通」（禁混判）
            svc[name] = {'state': 'not_probed'}
        else:
            svc[name] = {'state': 'ready'}
    not_enabled = [k for k, v in svc.items() if v.get('state') == 'not_enabled']
    note = {'version': ver, 'logged_in': True, 'services': svc}
    if not_enabled:
        return 'GAP_SERVICE', dict(note, detail='service_not_enabled', services_not_enabled=not_enabled)
    return 'READY', note


def probe_sqlite():
    """SQLite：Python 内置即够用（无独立 CLI 不算缺口 —— 判据要区分「没有」与「不必有」）。

    r163 自抓（瞬态被当固定红）：收尾验收时本门突然报 BROKEN: SQLite，而直测
    `python -c "import sqlite3"` 正常、连跑 3 次名册全 READY ⇒ 那是一次子进程启动抖动
    （进程创建失败/超时），不是 SQLite 坏。**单次探针失败不得直接判 BROKEN**（否则本门
    会随机咬人、变成不稳定红）；失败重试一次，两次都失败才 BROKEN，并在 note 里写明次数。"""
    rc, out = _sh([sys.executable, '-c', 'import sqlite3;print(sqlite3.sqlite_version)'])
    attempts = 1
    if rc != 0:
        rc, out = _sh([sys.executable, '-c', 'import sqlite3;print(sqlite3.sqlite_version)'])
        attempts = 2
    if rc != 0:
        return 'BROKEN', {'detail': 'py_sqlite_unusable', 'attempts': attempts, 'out': (out or '')[:120]}
    has_cli = bool(shutil.which('sqlite3'))
    return 'READY', {'embedded_version': (out or '').strip()[:20],
                      'standalone_cli': has_cli, 'attempts': attempts}


CF_ACCT = '04b1466b2606b678a332fe6f26aa87ec'
_WRANGLER_CFG = os.path.expanduser(r'~\\AppData\\Roaming\\xdg.config\\.wrangler\\config\\default.toml')


def _wrangler_token():
    """读 wrangler OAuth token（只读配置，不打印）。"""
    import re as _re
    try:
        raw = io.open(_WRANGLER_CFG, encoding='utf-8').read()
    except OSError as e:
        return None, 'config_unreadable'
    m = _re.search(r'oauth_token\s*=\s*"([^"]+)"', raw)
    return (m.group(1), None) if m else (None, 'no_oauth_token')


def now_env_ok(note):
    """GAP_CRED 分支（取不到面）允许没有 judged_by —— 它具名的是 detail。"""
    return 'detail' in note and note.get('detail') in (
        'no_wrangler_token', 'api_http_403', 'api_http_404', 'api_http_500',
        'api_unreachable') or str(note.get('detail', '')).startswith('api_')


def probe_http_only(name, env_keys):
    """纯 HTTP API 类（Resend / Upstash / Turnstile）：无 CLI 是平台形态，不是本机缺陷。

    有 env 凭据 => READY；无 => GAP_CRED（外部凭据缺口，#29③ 不属可自动化项）。"""
    present = {k: bool(os.environ.get(k)) for k in env_keys}
    any_cred = any(present.values())
    return (('READY' if any_cred else 'GAP_CRED'),
            {'kind': 'http_api_no_cli', 'cred_env_checked': present})


def probe_turnstile():
    """Turnstile：**已经在用**的工具，判据要看「widget 真存在」而不是「本机 env 有 key」。

    r164 自抓：旧式查 env CF_TURNSTILE_SITE_KEY/SECRET_KEY ⇒ 生产已启用仍判 GAP_CRED（假缺口）。
    凭据的正确归宿是 Cloudflare widget + Pages secret，本机 env 本来就不该有。
    判据：GET /accounts/<id>/challenges/widgets 有 >=1 项 ⇒ READY；取不到面 ⇒ GAP_CRED（不判红）。"""
    tok, err = _wrangler_token()
    if tok is None:
        return 'GAP_CRED', {'detail': 'no_wrangler_token', 'reason': err}
    import urllib.request
    import urllib.error
    req = urllib.request.Request(
        'https://api.cloudflare.com/client/v4/accounts/%s/challenges/widgets' % CF_ACCT,
        headers={'Authorization': 'Bearer ' + tok})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            d = json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return 'GAP_CRED', {'detail': 'api_http_%s' % e.code}
    except Exception as e:
        return 'GAP_CRED', {'detail': 'api_unreachable', 'err': repr(e)[:80]}
    ws = d.get('result') or []
    return ('READY' if ws else 'GAP_CRED'), {
        'widgets_n': len(ws),
        'sitekeys': [w.get('sitekey') for w in ws][:3],
        'judged_by': 'cloudflare_widget_exists（不是本机 env）',
    }


PROBES = [
    ('GitHub', probe_gh),
    ('Cloudflare-D1', lambda: probe_wrangler('d1')),
    ('Cloudflare-R2', lambda: probe_wrangler('r2')),
    ('Cloudflare-Pages', lambda: probe_wrangler('pages')),
    ('Cloudflare-Workers', lambda: probe_wrangler('workers')),
    ('SQLite', probe_sqlite),
    # r164 自抓（判据与现实漂移）：Turnstile 早前按「env 里有 CF_TURNSTILE_* 吗」判 GAP_CRED，
    #   但本轮实测它**已在生产启用**（widget 建好 + Pages secret 已配 + 部署后写接口回 captcha_failed）。
    #   凭据既不在本机 env、也不该在本机 env —— 它的正确归宿是 Cloudflare widget + Pages secret。
    #   判据改为「widget 是否真存在于账号下」：与第 68 门同源，但本门只做名册级别的一行读数。
    ('Cloudflare-Turnstile', probe_turnstile),
    ('Resend', lambda: probe_http_only('resend', ['RESEND_API_KEY'])),
    ('Upstash-Redis', lambda: probe_http_only('upstash', ['UPSTASH_REDIS_REST_URL', 'UPSTASH_REDIS_REST_TOKEN'])),
]

BROKEN_STATES = ('BROKEN',)


def run_probes():
    rows = []
    for name, fn in PROBES:
        try:
            st, note = fn()
        except Exception as e:  # 探针自身异常 => 记 BROKEN 具名，禁静默跳过
            st, note = 'BROKEN', {'detail': 'probe_exception', 'exc': repr(e)[:160]}
        rows.append({'tool': name, 'state': st, 'note': note})
    return rows


def selftest():
    """三腿：① 名册非空且每行有态 ② 合法态枚举闭合（禁未知态洗白）
    ③ 注入一个必 BROKEN 的探针 => 面必须判红（证明有牙）。"""
    legs = []
    rows = run_probes()
    legs.append(('f1_roster_nonempty', len(rows) == len(PROBES) and len(rows) > 0,
                 'rows=%d probes=%d' % (len(rows), len(PROBES))))
    legal = {'READY', 'GAP_CRED', 'GAP_CLI', 'GAP_SERVICE', 'BROKEN'}
    bad = [r['tool'] for r in rows if r['state'] not in legal]
    legs.append(('f2_state_enum_closed', not bad, 'illegal=%s' % (bad or '[]')))
    saved = list(PROBES)
    try:
        PROBES[:] = [('injected_broken', lambda: ('BROKEN', {'detail': 'injected'}))]
        rows2 = run_probes()
        broke = any(r['state'] in BROKEN_STATES for r in rows2)
        legs.append(('f3_injected_broken_detected', broke, 'states=%s' % [r['state'] for r in rows2]))
    finally:
        PROBES[:] = saved
    # 腿 1b：wrangler 探针缓存生效 —— 同进程内第二次调用不得再 spawn（成本腿，防退回 32s）
    _WRANGLER_CACHE.clear()
    probe_wrangler()
    n1 = _WRANGLER_CALLS['n']
    probe_wrangler()
    n2 = _WRANGLER_CALLS['n']
    legs.append(('f1b_wrangler_probe_cached_once', n2 == n1 and n1 >= 1,
                 'spawn 次数 first=%d second=%d（应相等）' % (n1, n2)))
    # 腿 1c（r163 自抓，假绿修正的自证）：GAP_SERVICE 必须**按服务分别判** ——
    #   一手事故：R2 未开通（403 code 10042）时本门仍判 READY（假绿），因为旧式只查
    #   「CLI 能跑 + 已登录」。修后另抓到粒度错误：四个 Cloudflare 条目共用一条探针 ⇒
    #   D1/Pages 明明 ready 也被连坐成 GAP_SERVICE。本腿锁住「同一探针下按 service 分流」。
    _WRANGLER_CACHE.clear()
    st_r2, n_r2 = probe_wrangler('r2')
    st_d1, n_d1 = probe_wrangler('d1')
    legs.append(('f1c_service_granularity',
                 st_d1 == 'READY' and (st_r2 in ('GAP_SERVICE', 'READY')),
                 'd1=%s r2=%s（同一探针下 d1 必须 READY，未被 r2 连坐）' % (st_d1, st_r2)))
    # 腿 1d：未探测 != 未开通（禁把「我没测」写成「平台没开」）
    #   r163 自抓：这条腿首版只查「源码里有 not_probed 字样」= 无齿（打印 want 不看 got）。
    #   改为**真注一条假探针读数**走同一分流函数，断言返回 GAP_CRED 而非 GAP_SERVICE。
    _WRANGLER_CACHE.clear()
    _WRANGLER_CACHE['state'] = 'GAP_SERVICE'
    _WRANGLER_CACHE['note'] = {'services': {'workers': {'state': 'not_probed'}}}
    st_np, n_np = probe_wrangler('workers')
    legs.append(('f1d_not_probed_not_reported_as_disabled',
                 st_np == 'GAP_CRED' and n_np.get('svc_state') == 'not_probed',
                 'state=%s svc_state=%s（未探测必须显形为 GAP_CRED 不得报「平台未开通」）'
                 % (st_np, n_np.get('svc_state'))))
    _WRANGLER_CACHE.clear()
    # 腿 1e（r164 自抓：判据与现实漂移的自证）——Turnstile 旧式按「本机 env 有 key 吗」
    #   判 GAP_CRED，而它生产已启用 ⇒ 假缺口。新判据看 Cloudflare 侧 widget 是否存在。
    #   本腿锁住：探针**不得**再读本机 env（否则换机/换会话又会漂回假缺口）。
    import inspect as _insp
    src_ts = _insp.getsource(probe_turnstile)
    # 真断言（首版写成 `... or True` = 恒真 = 无齿，已改）：
    #   ① 探针源码里不得出现任何 CF_TURNSTILE_* env 名（防判据退回「查本机 env」）
    #   ② 有 widget 时必须 READY，且必须有具名 judged_by（区分「真读过」与「没读过」）
    #   注意：本注释里**故意不写变量名**——否则会命中自己的断言（首版就踩了）。
    #   判据只看代码行（剥掉注释与 docstring），防「注释提到就算读了 env」的假红。
    import re as _re2
    code_only = _re2.sub(r'#.*', '', src_ts)
    code_only = _re2.sub(r'"""[\s\S]*?"""', '', code_only)
    code_only = _re2.sub(r"'''[\s\S]*?'''", '', code_only)
    no_env = ('CF_TURNSTILE_SITE' + '_KEY') not in code_only and ('CF_TURNSTILE_SECRET' + '_KEY') not in code_only
    # 真实读数腿：能取到面时必须有具名判据字段（区分「真读过」与「没读过」）
    st_ts, note_ts = probe_turnstile()
    legs.append(('f1e_turnstile_judged_by_widget_not_env',
                 no_env and st_ts in ('READY', 'GAP_CRED')
                 and ('judged_by' in note_ts or now_env_ok(note_ts)),
                 'state=%s judged_by=%s' % (st_ts, note_ts.get('judged_by') or note_ts.get('detail'))))
    # 零输入腿：名册空 => 不得判绿（R247）
    try:
        PROBES[:] = []
        # 真调 main()（不是读码推断）：空名册必须 rc=2 UNVERIFIED，禁按 0 记绿
        rc3 = main([])
        legs.append(('f4_empty_roster_returns_2', rc3 == 2, 'main([]) rc=%s（期望 2）' % rc3))
    finally:
        PROBES[:] = saved
    for name, ok, note in legs:
        print('%s %-32s %s' % ('PASS' if ok else 'FAIL', name, note))
    n_ok = sum(1 for _, ok, _ in legs if ok)
    print('[FREETOOLS:SELFTEST] %d/%d' % (n_ok, len(legs)))
    return 0 if n_ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out', default='')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    rows = run_probes()
    if not rows:
        print('[FREETOOLS] UNVERIFIED 名册为空，禁判绿（R247）')
        return 2
    counts = {}
    for r in rows:
        counts[r['state']] = counts.get(r['state'], 0) + 1
    doc = {'schema': 'free-tools-face-r163-v1',
           'cmd': 'python 05-exec/r163_free_tools_face.py --json <out>',
           'roster_n': len(rows), 'counts': counts, 'rows': rows,
           'rule': '仅 BROKEN 判红；GAP_CRED/GAP_CLI 是诚实显形（外部凭据/平台形态缺口，#29③）',
           'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    for r in rows:
        print('  %-24s %-9s %s' % (r['tool'], r['state'], json.dumps(r['note'], ensure_ascii=False)[:110]))
    broken = [r['tool'] for r in rows if r['state'] in BROKEN_STATES]
    print('[FREETOOLS] 名册 %d 项 | %s' % (len(rows), ' '.join('%s=%d' % (k, v) for k, v in sorted(counts.items()))))
    if broken:
        print('[FREETOOLS:FAIL] BROKEN 具名: %s' % ', '.join(broken))
        return 1
    print('[FREETOOLS:PASS] 无 BROKEN（GAP_* 已具名，禁读成「工具都可用」）')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())