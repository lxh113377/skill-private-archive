# -*- coding: utf-8 -*-
# r163_gh_path_face.py -- gh（GitHub CLI）PATH 可达性判据面（第 64 门）。
#
# 存在理由（r163 一手实测）：本机 PATH 中 `gh` 解析到
#   C:/Users/37533/.local/bin/gh —— 该件是**指向 WSL 形态路径的 junction**
#   （fsutil Reparse Tag 0xa000001d，目标 /mnt/c/Program Files/GitHub CLI/gh.exe；
#    Windows 侧 os.path.getsize 抛 WinError 1920「系统无法访问此文件」），
#   ⚠️ 首版记作「0 字节空文件」是字段语义误读（junction 的 Length 恒 0），
#      谓词已改为判**可跑性**（见 check() 内 r163 校正注）；
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


def is_reparse(path):
    """是否重解析点（junction / symlink）。r163：junction 的 getsize 恒 0，不可当「空文件」。"""
    try:
        import stat as _stat
        st = os.lstat(path)
        return bool(getattr(st, "st_file_attributes", 0) & _stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except (OSError, AttributeError):
        return False


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
    **无扩展名的条目（含指向不可解析目标的 junction）**也当命令命中，
    裸调才报「Cannot run a document in the middle of a pipeline」。
    r163g：判据是**可跑性**（CALL=），SIZE 只作诊断 —— junction 的 Length 恒 0
    且不可解析时 Get-Item 直接抛错，拿 SIZE 当判据会双向失真（与 Python 侧同族）。
    """
    script = (
        "$c = Get-Command gh -ErrorAction SilentlyContinue; "
        "if (-not $c) { Write-Output 'NOPATH'; exit 0 }; "
        "Write-Output ('SOL=' + $c.Source); "
        "try { Write-Output ('SIZE=' + (Get-Item $c.Source).Length) } "
        "catch { Write-Output 'SIZE=NA' }; "
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
        # r163 校正（并行会话纠偏 + 我独立复算坐实）：旧谓词用 getsize<=0 判「空壳」是错的 ——
        #   C:/Users/37533/.local/bin/gh 实为 **junction**（fsutil: Reparse Tag 0xa000001d
        #   Name Surrogate，目标 /mnt/c/Program Files/GitHub CLI/gh.exe 是 WSL 形态路径，
        #   Windows 侧解析不到），而 junction 的 getsize 恒为 0 ⇒ 该谓词会把**合法 junction**
        #   误判成空壳，同时把「size>0 但跑不起来」的真坏件放过去（双向失真）。
        #   正解 = 判**可跑性**：按 PATH 解析到的那个件真跑一次 --version。
        size = -1
        try:
            size = os.path.getsize(on_path)
        except OSError:
            size = -1
        d['path_entry_size'] = size
        d['path_entry_is_reparse'] = is_reparse(on_path)
        rc_p, out_p = _run([on_path, '--version'], timeout=120)
        d['path_entry_run_rc'] = rc_p
        d['path_entry_run_out'] = (out_p or '').strip().splitlines()[:1]
        runnable = (rc_p == 0 and 'gh version' in (out_p or ''))
        d['path_entry_runnable'] = runnable
        if not runnable:
            return 'FAIL', dict(d, reason='path_entry_not_runnable',
                                fix='PATH 解析到的 gh 跑不起来（%s%s）；真实件在位 %s。'
                                    '旧形态处置：把该件从 PATH 前位移除或重命名为 .disabled'
                                    % (on_path,
                                       "，且它是 junction/重解析点，目标 Windows 侧不可解析"
                                       if d['path_entry_is_reparse'] else "",
                                       real))
    if rc2 is None:
        return 'UNVERIFIED', dict(d, reason='auth_probe_unavailable',
                                  fix='gh auth status 子进程未返回（超时或无法启动），非登录态问题')
    # r165 自抓（并发挤占致假 UNVERIFIED）：聚合跑（run_gates 68 门并发）时本门一度报
    #   `not_logged_in`，而**单跑 3 次全 rc=0 且 logged_in=True**（`gh auth status` 直跑也 rc=0、
    #   keyring 登录态完好）。真凶是并发挤占让 auth 探针拿到**非零 rc**，
    #   旧式直接判 not_logged_in ⇒ 引着人去查登录态（真凶是子进程，同 r163 那条）。
    #   修法 = 非零 rc 时**重试一次**；仍非零才判 not_logged_in，并把 attempts 具名。
    if not d['logged_in']:
        rc2b, out2b = _run([real, 'auth', 'status'], timeout=150)
        d['auth_rc_retry'] = rc2b
        d['auth_tail_retry'] = (out2b or '').strip()[-160:]
        d['logged_in'] = (rc2b == 0 and 'Logged in' in (out2b or ''))
        d['auth_attempts'] = 2
    if not d['logged_in']:
        return 'UNVERIFIED', dict(d, reason='not_logged_in',
                                  fix='两次 auth status 均未拿到登录态（rc=%s/%s）；请先单跑 gh auth status 复核，排除并发挤占后再判登录态'
                                  % (rc2, d.get('auth_rc_retry')))
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
    if ps.get('call_ok') is not True:
        return 'FAIL', dict(d, reason='ps_side_broken',
                            fix='PowerShell 侧 gh 跑不起来: %s（size=%s call=%s）'
                                % (ps.get('path'), ps.get('size'), ps.get('call_ok')))
    if os.path.normcase(str(ps.get('path'))) != os.path.normcase(str(on_path)):
        return 'FAIL', dict(d, reason='cross_interpreter_mismatch',
                            fix='Python 解析=%s 而 PowerShell 解析=%s（PATH 序遮蔽）'
                                % (on_path, ps.get('path')))

    # r167 自抓（R166-2 的真因，我上轮归因错了）：聚合跑时本门报的是 **api_unreachable**，
    #   不是 not_logged_in —— 上轮在 R166-2 里写「各分支都显示 not_logged_in」是**误判**，
    #   真凶是这最后一步 `gh api rate_limit` 在 68 门并发下偶发拿不到数（GitHub API 网络抖动，
    #   与 gh 登录态无关：纯 gh 并发压测 12/12 全成功）。
    #   修法同 auth：非零 rc 先重试一次；仍失败才 UNVERIFIED 且 attempts 具名。
    rc3, out3 = _run([real, 'api', 'rate_limit', '--jq', '.rate'], timeout=150)
    d['api_rc'] = rc3
    d['api_out'] = (out3 or '').strip()[:120]
    if rc3 != 0:
        rc3, out3 = _run([real, 'api', 'rate_limit', '--jq', '.rate'], timeout=150)
        d['api_rc_retry'] = rc3
        d['api_out_retry'] = (out3 or '').strip()[:120]
        d['api_attempts'] = 2
    if rc3 != 0:
        return 'UNVERIFIED', dict(d, reason='api_unreachable',
                                  fix='gh api rate_limit 两次均未返回（rc=%s/%s）；这是 GitHub API '
                                      '网络抖动，与 gh 登录态无关，勿去查登录态'
                                      % (d.get('api_rc'), d.get('api_rc_retry')))
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
        print('[GHPATH] %s | on_path=%s size=%s runnable=%s reparse=%s | real=%s '
              '| logged_in=%s | api=%s'
              % (PASS_TOKEN, d.get('gh_on_path'), d.get('path_entry_size'),
                 d.get('path_entry_runnable'), d.get('path_entry_is_reparse'),
                 d.get('gh_real'), d.get('logged_in'), d.get('api_rc')))
        # r163g：旧文案「PATH 件非空壳」随谓词改为可跑性同步措辞（禁留失真标签）
        print('[GHPATH:PASS] gh 可达且已登录（PATH 解析件可跑，与真实件同指一处）')
        return 0
    if state == 'FAIL':
        # r163 自抓：首版把「Python 侧解析路径」印成空壳本体（真凶在 PS 侧时归因失真）
        # ⇒ 按 reason 点名真正坏掉的那一侧。
        # r163g 自抓：谓词改名后这里仍写旧 reason 字符串 ⇒ 条件恒 False，
        #   会把「PATH 侧跑不起来」也归因到 PS 侧（同码不同因的镜像形态）。
        #   改为按 reason 显式映射，未知 reason 一律点名两侧不猜。
        r_ = d.get('reason')
        PATH_SIDE = ('path_entry_not_runnable', 'path_entry_is_empty_stub')
        if r_ in PATH_SIDE:
            bad, bsize, side = d.get('gh_on_path'), d.get('path_entry_size'), 'PATH 解析侧'
        elif r_ in ('ps_side_broken', 'cross_interpreter_mismatch'):
            bad, bsize, side = d.get('ps_resolved'), d.get('ps_size'), 'PowerShell 解析侧'
        else:
            bad, bsize, side = '(未知 reason，两侧并列)', None, '未归类'
            print('[GHPATH:FAIL] %s | PATH=%s(size=%s runnable=%s) PS=%s(size=%s)'
                  % (r_, d.get('gh_on_path'), d.get('path_entry_size'),
                     d.get('path_entry_runnable'), d.get('ps_resolved'), d.get('ps_size')))
        print('[GHPATH:FAIL] %s | 坏的一侧(%s): %s (size=%s)' % (r_, side, bad, bsize))
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
    legs.append(('s2_unrunnable_path_entry_fails', st2 == 'FAIL', 'state=%s reason=%s' % (st2, d2.get('reason'))))
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
    # 腿 4（r165 自抓，并发挤占致假 UNVERIFIED）——**单元级验证重试逻辑**，不靠 PATH 注入。
    #   一手事故：聚合跑（68 门并发）时本门报 not_logged_in，而单跑 3 次全 rc=0、
    #   gh auth status 直跑也 rc=0（keyring 登录态完好）⇒ 真凶是并发挤占致 auth 探针拿到
    #   非零 rc，旧式直接判 not_logged_in（引着人查登录态，真凶是子进程）。
    #   修法 = 非零 rc 先重试一次；本腿直接驱动那段逻辑：把 _run 换成「首次非零、二次 0」
    #   的假函数，断言重试后必须拿到登录态。
    #   （首版试过用 PATH 注入假 gh.cmd，但解析优先级不受控 ⇒ 跑到真 gh ⇒ **假验证**，已废。）
    import r163_gh_path_face as _self
    calls = {'n': 0}
    def _fake_run(argv, timeout=60):
        if argv[-2:] == ['auth', 'status'] or (len(argv) >= 2 and argv[1] == 'auth'):
            calls['n'] += 1
            if calls['n'] == 1:
                return 1, 'git: command not found (simulated contention)'
            return 0, 'github.com' + chr(10) + '  Logged in to github.com account test (keyring)'
        return 0, 'gh version 9.9.9 (test)'
    saved_run = _self._run
    _self._run = _fake_run
    try:
        st4, dd4 = _self.check()
    finally:
        _self._run = saved_run
    legs.append(('s5_auth_retry_recovers_from_flake',
                 calls['n'] >= 2 and dd4.get('logged_in') is True
                 and dd4.get('auth_attempts') == 2,
                 'auth 调用 %d 次 logged_in=%s attempts=%s（非零 rc 必须先重试再判未登录）'
                 % (calls['n'], dd4.get('logged_in'), dd4.get('auth_attempts'))))
    # 腿 5（r167 自抓，R166-2 真因的自证）：api rate_limit 非零 rc 先重试。
    #   R166-2 的真凶是这最后一步在并发下偶发失败（reason=api_unreachable），
    #   与登录态无关 —— 上轮归因成 not_logged_in 是误判，本腿锁住正确归因。
    import r163_gh_path_face as _self2
    api_calls = {'n': 0}
    def _fake_run2(argv, timeout=60):
        if len(argv) >= 2 and argv[1] == 'api':
            api_calls['n'] += 1
            if api_calls['n'] == 1:
                return 1, 'simulated api flake'
            return 0, '{"rate": {"remaining": 4926}}'
        if len(argv) >= 2 and argv[1] == 'auth':
            return 0, 'github.com' + chr(10) + '  Logged in to github.com account test (keyring)'
        return 0, 'gh version 9.9.9 (test)'
    saved2 = _self2._run
    _self2._run = _fake_run2
    try:
        st6, d6 = _self2.check()
    finally:
        _self2._run = saved2
    legs.append(('s6_api_retry_recovers_from_flake',
                 api_calls['n'] >= 2 and st6 == 'PASS' and d6.get('api_attempts') == 2,
                 'api 调用 %d 次 state=%s attempts=%s（并发抖动须重试，勿报 api_unreachable）'
                 % (api_calls['n'], st6, d6.get('api_attempts'))))
    for name, ok, note in legs:
        print('%s %-32s %s' % ('PASS' if ok else 'FAIL', name, note))
    n_ok = sum(1 for _, ok, _ in legs if ok)
    print('[GHPATH:SELFTEST] %d/%d' % (n_ok, len(legs)))
    return 0 if n_ok == len(legs) else 1


if __name__ == '__main__':
    raise SystemExit(main())