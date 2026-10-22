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


def probe_wrangler():
    """wrangler（覆盖 Cloudflare D1 / R2 / Pages / Workers / Turnstile 的 CLI 面）。"""
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
    return ('READY' if logged else 'GAP_CRED'), {'version': ver, 'logged_in': logged}


def probe_sqlite():
    """SQLite：Python 内置即够用（无独立 CLI 不算缺口 —— 判据要区分「没有」与「不必有」）。"""
    rc, out = _sh([sys.executable, '-c', 'import sqlite3;print(sqlite3.sqlite_version)'])
    if rc != 0:
        return 'BROKEN', {'detail': 'py_sqlite_unusable', 'out': out[:120]}
    has_cli = bool(shutil.which('sqlite3'))
    return 'READY', {'embedded_version': (out or '').strip()[:20], 'standalone_cli': has_cli}


def probe_http_only(name, env_keys):
    """纯 HTTP API 类（Resend / Upstash / Turnstile）：无 CLI 是平台形态，不是本机缺陷。

    有 env 凭据 => READY；无 => GAP_CRED（外部凭据缺口，#29③ 不属可自动化项）。"""
    present = {k: bool(os.environ.get(k)) for k in env_keys}
    any_cred = any(present.values())
    return (('READY' if any_cred else 'GAP_CRED'),
            {'kind': 'http_api_no_cli', 'cred_env_checked': present})


PROBES = [
    ('GitHub', probe_gh),
    ('Cloudflare-D1', probe_wrangler),
    ('Cloudflare-R2', probe_wrangler),
    ('Cloudflare-Pages', probe_wrangler),
    ('Cloudflare-Workers', probe_wrangler),
    ('SQLite', probe_sqlite),
    ('Cloudflare-Turnstile', lambda: probe_http_only('turnstile', ['CF_TURNSTILE_SITE_KEY', 'CF_TURNSTILE_SECRET_KEY'])),
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
    legal = {'READY', 'GAP_CRED', 'GAP_CLI', 'BROKEN'}
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