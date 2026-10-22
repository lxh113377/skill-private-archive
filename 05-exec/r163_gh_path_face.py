# -*- coding: utf-8 -*-
# r163_gh_path_face.py -- gh（GitHub CLI）PATH 可达性判据面（第 64 门）。
#
# 存在理由（r163 一手实测）：本机 PATH 中 `gh` 解析到
#   C:/Users/37533/.local/bin/gh —— 该件是 **0 字节空文件**（2026-08-08 遗留），
#   而真实可用件在 C:/Program Files/GitHub CLI/gh.exe（2.95.0，已登录 keyring）。
# 后果：凡经 PATH 调 `gh` 的判据/脚本都会静默失败（rc 空、零输出），
# 读数缺失被读成「无候选 / 无上游」=> 假绿（R247 同族：取不到数不得按干净记）。
#
# 判据三态：
#   PASS     PATH 件可执行且非空 且 真实件在位 且 已登录
#   FAIL     PATH 件是空壳/不可执行（给修复指引），或真实件缺失
#   UNVERIFIED(rc=2)  gh 完全不在机 / auth 状态取不到
#
# 用法: python 05-exec/r163_gh_path_face.py [--json <件>] [--selftest]
# 退出码: 0 PASS / 1 FAIL / 2 UNVERIFIED
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
PASS_TOKEN = '[GHPATH:PASS]'

# 真实件的常见安装位置（按序探测；不写死单一版本号）
GH_CANDIDATES = [
    os.path.join(os.environ.get('ProgramFiles', r'C:\Program Files'), 'GitHub CLI', 'gh.exe'),
    os.path.join(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'), 'GitHub CLI', 'gh.exe'),
    os.path.expanduser(r'~\scoop\shims\gh.exe'),
    os.path.expanduser(r'~\AppData\Local\Microsoft\WinGet\Links\gh.exe'),
]


def _run(argv, timeout=60):
    try:
        p = subprocess.run(argv, capture_output=True, text=True,
                           encoding='utf-8', errors='replace', timeout=timeout)
        return p.returncode, (p.stdout or '') + (p.stderr or '')
    except (OSError, subprocess.SubprocessError) as e:
        return None, 'EXC %r' % e


def find_real_gh():
    """返回第一个存在且非空的真实 gh 路径；找不到返回 None。"""
    for c in GH_CANDIDATES:
        try:
            if os.path.isfile(c) and os.path.getsize(c) > 0:
                return c
        except OSError:
            continue
    return None


def ps_which_gh():
    """在 PowerShell 子进程里解析 gh，并裸调一次验证真的能跑。

    为什么必须单独查：Windows 下 PATH 遮蔽对两个解释器表现不同 ——
    shutil.which 按 PATHEXT 找可执行扩展名，PowerShell 的 Get-Command 会把
    **无扩展名的 0 字节文件**也当命令命中，裸调才报
    「Cannot run a document in the middle of a pipeline」。
    """
    script = (
        "$c = Get-Command gh -ErrorAction SilentlyContinue; "
        "if (-not $c) { Write-Output 'NOPATH'; exit 0 }; "
        "Write-Output ('SOL=' + $c.Source); "
        "Write-Output ('SIZE=' + (Get-Item $c.Source).Length); "
        "try { $v = (gh --version 2>&1 | Select-Object -First 1); "
        "if ($LASTEXITCODE -eq 0 -and $v -match 'gh version') { Write-Output 'CALL=OK' } "
        "else { Write-Output ('CALL=BAD:' + $v) } } catch { Write-Output ('CALL=EXC:' + $_.Exception.Message) }"
    )
    try:
        p = subprocess.run(["powershell", "-NoProfile", "-Command", script],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=90)
    except (OSError, subprocess.SubprocessError):
        return {"path": None, "size": None, "call_ok": None}
    out = (p.stdout or "")
    if "NOPATH" in out:
        return {"path": None, "size": None, "call_ok": None}
    path = size = call_ok = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("SOL="):
            path = line[4:].strip()
        elif line.startswith("SIZE="):
            try:
                size = int(line[5:].strip())
            except ValueError:
                size = None
        elif line.startswith("CALL="):
            call_ok = line[5:].strip() == "OK"
    return {"path": path, "size": size, "call_ok": call_ok}


def check():
    """返回 (state, detail_dict)。state ∈ PASS / FAIL / UNVERIFIED。"""
    on_path = shutil.which('gh')
    real = find_real_gh()
    d = {'gh_on_path': on_path, 'gh_real': real}
    if real is None:
        # 本机没有可用 gh —— 不是「没有上游」而是「看不到上游」，禁按干净记
        return 'UNVERIFIED', dict(d, reason='no_usable_gh_binary')
    rc, out = _run([real, '--version'])
    d['version_rc'] = rc
    d['version_out'] = (out or '').strip().splitlines()[:1]
    if rc != 0:
        return 'UNVERIFIED', dict(d, reason='real_gh_not_runnable')
    # r163 自抓真因：聚合跑时并发挤占，auth 探针在默认 60s 内没返回 => _run 返回 (None, EXC)
    #   ⇒ 本门在 runner 里判 UNVERIFIED，而单跑 8 次 rc 恒 0（间歇性失效，非登录态问题）。
    #   放宽到 150s 并失败重试一次；仍取不到数才 UNVERIFIED（禁按干净记，也禁把超时写成未登录）。
    rc2, out2 = _run([real, 'auth', 'status'], timeout=150)
    if rc2 is None:
        rc2, out2 = _run([real, 'auth', 'status'], timeout=150)
    d['auth_rc'] = rc2
    # r163 自抓：原式把「探针取不到数」（rc=None，超时/进程起不来）与「确实未登录」
    #   （rc!=0）混成同一个 not_logged_in ⇒ 归因失真，会引着人去查登录态而真凶是子进程。
    d['auth_tail'] = (out2 or '').strip()[-160:]
    d['logged_in'] = (rc2 == 0 and 'Logged in' in (out2 or ''))
    if on_path:
        try:
            size = os.path.getsize(on_path)
        except OSError:
            size = -1
        d['path_entry_size'] = size
        if size <= 0:
            # 空壳：PATH 调它必静默失败 —— 这是本门要抓的形态
            return 'FAIL', dict(d, reason='path_entry_is_empty_stub',
                                fix='把 %s 加入 PATH，或删除空壳 %s' % (os.path.dirname(real), on_path))
    if rc2 is None:
        return 'UNVERIFIED', dict(d, reason='auth_probe_unavailable',
                                  fix='gh auth status 子进程未返回（超时或无法启动），非登录态问题')
    if not d['logged_in']:
        return 'UNVERIFIED', dict(d, reason='not_logged_in')
    # r163 自抓（本面首版是瞎的）：只查 Python 侧 shutil.which，而修复前
    #   Python 侧解析到真实 gh（判 PASS），PowerShell 侧解析到 0 字节空壳（裸调必失败）
    #   ⇒ 面在缺陷真实存在的那一轮打了绿。补跨解释器一致性腿：
    #   不变式不是「Python 能找到 gh」，而是「两个解释器找到同一个非空 gh」。
    ps = ps_which_gh()
    d['ps_resolved'] = ps.get('path')
    d['ps_size'] = ps.get('size')
    d['ps_bare_call_ok'] = ps.get('call_ok')
    if ps.get('path') is None:
        return 'UNVERIFIED', dict(d, reason='ps_resolution_unavailable')
    if (ps.get('size') or 0) <= 0 or not ps.get('call_ok'):
        return 'FAIL', dict(d, reason='ps_side_broken',
                            fix='PowerShell 侧 gh 解析到空壳或不可执行: %s（size=%s）'
                                % (ps.get('path'), ps.get('size')))
    if os.path.normcase(str(ps.get('path'))) != os.path.normcase(str(on_path)):
        return 'FAIL', dict(d, reason='cross_interpreter_mismatch',
                            fix='Python 解析=%s 而 PowerShell 解析=%s（PATH 序遮蔽）'
                                % (on_path, ps.get('path')))

    rc3, out3 = _run([real, 'api', 'rate_limit', '--jq', '.rate'])
    d['api_rc'] = rc3
    d['api_out'] = (out3 or '').strip()[:120]
    if rc3 != 0:
        return 'UNVERIFIED', dict(d, reason='api_unreachable')
    return 'PASS', d


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out', default='')
    ap.add_argument('--selftest', action='store_true',
                    help='自证三腿：真实态 / 空壳注入 / 无 gh 注入（不碰真 PATH）')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    state, d = check()
    doc = {'schema': 'gh-path-face-r163-v1',
           'cmd': 'python 05-exec/r163_gh_path_face.py --json <out>',
           'state': state, 'detail': d,
           'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    if state == 'PASS':
        print('[GHPATH] %s | on_path=%s size=%s | real=%s | logged_in=%s | api=%s'
              % (PASS_TOKEN, d.get('gh_on_path'), d.get('path_entry_size'),
                 d.get('gh_real'), d.get('logged_in'), d.get('api_rc')))
        print('[GHPATH:PASS] gh 可达且已登录（PATH 件非空壳）')
        return 0
    if state == 'FAIL':
        # r163 自抓：首版把「Python 侧解析路径」印成空壳本体（真凶在 PS 侧时归因失真）
        # ⇒ 按 reason 点名真正坏掉的那一侧。
        bad = (d.get('gh_on_path') if d.get('reason') == 'path_entry_is_empty_stub'
               else d.get('ps_resolved'))
        print('[GHPATH:FAIL] %s | 坏的一侧解析到: %s (size=%s)' % (
            d.get('reason'), bad,
            d.get('path_entry_size') if d.get('reason') == 'path_entry_is_empty_stub'
            else d.get('ps_size')))
        print('           真实件在位: %s' % d.get('gh_real'))
        print('           修复指引: %s' % d.get('fix'))
        return 1
    print('[GHPATH] UNVERIFIED %s' % d.get('reason'))
    return 2


def selftest():
    """三腿自证：① 真实态读数自洽 ② 空壳注入必须 FAIL ③ 无 gh 注入必须 UNVERIFIED。

    注入方式 = 临时改 PATH 环境变量（子进程继承），**不改用户环境变量**。
    """
    import tempfile
    legs = []
    # 腿 1：当前真实态（不断言具体态，只断言读数四字段齐备）
    st, d = check()
    legs.append(('s1_real_state_readable',
                 all(k in d for k in ('gh_on_path', 'gh_real', 'logged_in')),
                 'state=%s keys=%s' % (st, sorted(d.keys()))))
    # 腿 2：把 PATH 换成只含空壳目录 => 必须 FAIL（而非 UNVERIFIED / PASS）
    stub_dir = tempfile.mkdtemp(prefix='gh_stub_')
    stub = os.path.join(stub_dir, 'gh.exe')
    with io.open(stub, 'w', encoding='utf-8', newline='\n') as f:
        f.write('')  # 0 字节空壳
    old_path = os.environ.get('PATH', '')
    os.environ['PATH'] = stub_dir + os.pathsep + old_path
    try:
        st2, d2 = check()
    finally:
        os.environ['PATH'] = old_path
    legs.append(('s2_empty_stub_must_fail', st2 == 'FAIL', 'state=%s reason=%s' % (st2, d2.get('reason'))))
    # 腿 3：把 PATH 与候选面都抽掉 => 必须 UNVERIFIED（禁按干净记）
    old_cands = list(GH_CANDIDATES)
    del GH_CANDIDATES[:]
    os.environ['PATH'] = stub_dir  # 只有空壳，无真实件
    try:
        st3, d3 = check()
    finally:
        os.environ['PATH'] = old_path
        GH_CANDIDATES[:] = old_cands
    legs.append(('s3_no_real_gh_unverified', st3 == 'UNVERIFIED', 'state=%s reason=%s' % (st3, d3.get('reason'))))
    # 腿 4：跨解释器一致性 —— ps_which_gh 必须给出 path/size/call_ok 三读数，
    # 且与 Python 侧解析同值（不同值即 FAIL，本腿锁住 r163 首版假阴性）
    ps = ps_which_gh()
    py_path = shutil.which('gh')
    same = (ps.get('path') and py_path and
            os.path.normcase(str(ps.get('path'))) == os.path.normcase(str(py_path)))
    legs.append(('s4_cross_interpreter_agree',
                 bool(ps.get('path')) and ps.get('size') is not None
                 and ps.get('call_ok') is True and same,
                 'py=%s ps=%s size=%s call_ok=%s' % (py_path, ps.get('path'),
                                                     ps.get('size'), ps.get('call_ok'))))
    for name, ok, note in legs:
        print('%s %-32s %s' % ('PASS' if ok else 'FAIL', name, note))
    n_ok = sum(1 for _, ok, _ in legs if ok)
    print('[GHPATH:SELFTEST] %d/%d' % (n_ok, len(legs)))
    return 0 if n_ok == len(legs) else 1


if __name__ == '__main__':
    raise SystemExit(main())