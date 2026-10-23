# -*- coding: utf-8 -*-
# r162_gatemap_fixtures.py -- commit_gate_map_face 稳态歧义（R159-1）+ closing 面过宽（r137 真缺陷）的反向验证夹具。
#
# 两条被测事实（都先在本机复现过，非推理）：
#   ① 收尾跑 handoff.py volume --snapshot 后 memory/sessions/volume-snapshots.jsonl 变脏，
#      旧 CLOSING_PAT 不认它 => 空暂存分支从 SKIP 掉到 UNVERIFIED rc=2（R159-1 稳态歧义）。
#   ② 旧 CLOSING_PAT 把 06-benchmark/transmit_proposals.json（纪律面）未 add 洗成 closing
#      => 假 SKIP，击穿 r133 第④形态「禁按 0 记绿」。
#
# 判据口径（#48：每条腿都比对 want 与 got，禁只打印 want）：
#   t1 应 SKIP 面：纯 append-only 台账脏件 => rc=0 且输出含 [GATEMAP:SKIP]
#   t2 应 UNVERIFIED 面：提案台账漏 add => rc=2（禁按 SKIP 放行）
#   t3 应 UNVERIFIED 面：07 台账漏 add => rc=2
#   t4 应 UNVERIFIED 面：AGENTS.md 漏 add => rc=2
#   t5 应 UNVERIFIED 面：05-exec/run_gates.py 漏 add => rc=2
#   t6 应 UNVERIFIED 面：报告件（.md 不在白名单）=> rc=2
#   t7 空暂存 + 全干净树 => rc=0 SKIP
#   t8 纪律面优先：白名单件 + 提案台账同时脏 => rc=2（DENY 压过 ALLOW）
#   m1 变异腿：把 CLOSING_ALLOW 摘空 => t1 必须转红（证明 t1 的绿来自白名单本身）
#   m2 变异腿：把 CLOSING_DENY 摘空 => t2 必须转红（证明 DENY 有牙）
#   m3 变异腿：--dirty 指向不存在文件 => rc=2（测试缝不许静默失效）
import argparse
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TARGET = os.path.join(HERE, 'r137_commit_gate_map.py')
TARGET_RUNNER = os.path.join(HERE, 'run_gates.py')
PY = sys.executable

RESULTS = []


def record(name, want_rc, got_rc, want_token, got_out, note=''):
    ok = (want_rc == got_rc)
    if want_token is not None:
        ok = ok and (want_token in (got_out or ''))
    RESULTS.append({'name': name, 'ok': ok, 'want_rc': want_rc, 'got_rc': got_rc,
                    'want_token': want_token, 'note': note})
    return ok


def _write_tmp(prefix, lines):
    fd, path = tempfile.mkstemp(prefix=prefix, suffix='.txt')
    os.close(fd)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + ('\n' if lines else ''))
    return path


def run_with_dirty(lines, extra_argv=None, staged=None):
    """把 dirty 清单写临时文件，经 --dirty 测试缝喂给被测脚本。

    r178 修（R178-2 一手）：**同时注入 --staged**。原实现只封 --dirty 一条缝，
    暂存清单仍走真 git ⇒ 本机工作区有没有暂存件会直接改变 11 条腿的读数
    （实测：收尾件 git add 未 commit 的窗口内夹具 0/11 全 FAIL，want=2 got=0）。
    staged=None ⇒ 注入空清单（「无暂存活动」这一被测形态），而非继承真仓状态。
    """
    path = _write_tmp('r162_dirty_', lines)
    spath = _write_tmp('r162_staged_', [] if staged is None else staged)
    argv = [PY, TARGET, '--dirty', path, '--staged', spath] + list(extra_argv or [])
    try:
        p = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                           encoding='utf-8', errors='replace', timeout=180)
    finally:
        for x in (path, spath):
            if os.path.exists(x):
                os.remove(x)
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def import_target():
    import importlib.util
    spec = importlib.util.spec_from_file_location('r137_under_test', TARGET)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def t1_closing_whitelist_skips():
    dirty = ['?? 06-benchmark/gate_run_r162_probe.json',
             ' M 06-benchmark/gate_runs.jsonl',
             ' M 06-benchmark/debt_runs.jsonl',
             ' M 06-benchmark/input_pins.jsonl',
             ' M memory/sessions/volume-snapshots.jsonl']
    rc, out = run_with_dirty(dirty)
    return record('t1_append_only_ledgers_skip', 0, rc, '[GATEMAP:SKIP]', out,
                  'volume-snapshots.jsonl 必须被认成收尾台账（R159-1 实况复现面）')


def t2_proposal_ledger_not_washed():
    rc, out = run_with_dirty([' M 06-benchmark/transmit_proposals.json'])
    return record('t2_proposal_ledger_unverified', 2, rc, None, out,
                  '提案台账是纪律面：漏 add 必须 UNVERIFIED，禁洗成 SKIP')


def t3_ledger_07_not_washed():
    rc, out = run_with_dirty([' M memory/07-next-steps.md'])
    return record('t3_07_ledger_unverified', 2, rc, None, out, '07 台账漏 add')


def t4_agents_not_washed():
    rc, out = run_with_dirty([' M AGENTS.md'])
    return record('t4_agents_unverified', 2, rc, None, out, 'AGENTS.md 漏 add')


def t5_runner_not_washed():
    rc, out = run_with_dirty([' M 05-exec/run_gates.py'])
    return record('t5_runner_unverified', 2, rc, None, out, '门表漏 add')


def t6_report_md_not_whitelisted():
    rc, out = run_with_dirty(['?? 06-benchmark/全量对标报告_r162_x.md'])
    return record('t6_report_md_unverified', 2, rc, None, out, '报告 .md 不在 json 白名单')


def t7_clean_tree_skips():
    rc, out = run_with_dirty([])
    return record('t7_clean_tree_skip', 0, rc, '[GATEMAP:SKIP]', out, '干净树稳态')


def t8_deny_beats_allow():
    dirty = ['?? 06-benchmark/gate_run_r162_probe.json',
             ' M 06-benchmark/transmit_proposals.json']
    rc, out = run_with_dirty(dirty)
    return record('t8_deny_beats_allow', 2, rc, None, out,
                  '白名单件与纪律面同时脏时以纪律面优先（all() 语义天然如此，本条锁住它）')


def m1_strip_allow_breaks_t1():
    """变异：CLOSING_ALLOW 摘空 => t1 的绿必须消失（证明绿来自白名单）。"""
    src = io.open(TARGET, encoding='utf-8').read()
    tmp = os.path.join(HERE, '_r162_m1_mutant.py')

    mutated = src.replace("CLOSING_ALLOW = (", "CLOSING_ALLOW = (  # mutated: empty", 1)
    # 摘空：把第一个字符串项之后紧邻的 ')' 提前 —— 用更稳的整块替换
    mutated = src
    import re as _re
    mutated = _re.sub(r"CLOSING_ALLOW = \([^)]*\)", "CLOSING_ALLOW = ()", mutated, count=1)
    with io.open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(mutated)
    dirty_path = _write_tmp('r162_m1d_', ['?? 06-benchmark/gate_run_r162_probe.json'])
    staged_path = _write_tmp('r162_m1s_', [])
    try:
        p = subprocess.run([PY, tmp, '--dirty', dirty_path, '--staged', staged_path],
                           cwd=ROOT, capture_output=True, text=True,
                           encoding='utf-8', errors='replace', timeout=180)
    finally:
        for x in (dirty_path, staged_path, tmp):
            if os.path.exists(x):
                os.remove(x)
    return record('m1_strip_allow_breaks_t1', 2, p.returncode, None, p.stdout + p.stderr,
                  '摘白名单 => 应 SKIP 面必须转 UNVERIFIED')


def m2_strip_deny_breaks_t2():
    """变异：CLOSING_DENY 摘空 => t2 必须转绿（假 SKIP），证明 DENY 有牙。"""
    src = io.open(TARGET, encoding='utf-8').read()
    import re as _re
    mutated = _re.sub(r"CLOSING_DENY = \([^)]*\)", "CLOSING_DENY = ()", src, count=1)
    tmp = os.path.join(HERE, '_r162_m2_mutant.py')

    with io.open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(mutated)
    dirty_path = _write_tmp('r162_m2d_', [' M 06-benchmark/transmit_proposals.json'])
    staged_path = _write_tmp('r162_m2s_', [])
    try:
        p = subprocess.run([PY, tmp, '--dirty', dirty_path, '--staged', staged_path],
                           cwd=ROOT, capture_output=True, text=True,
                           encoding='utf-8', errors='replace', timeout=180)
    finally:
        for x in (dirty_path, staged_path, tmp):
            if os.path.exists(x):
                os.remove(x)
    # 摘 DENY 后提案台账落进 ALLOW => 假 SKIP rc=0 —— 变异体「变坏」即证明原判据有牙
    return record('m2_strip_deny_makes_t2_falsely_green', 0, p.returncode, '[GATEMAP:SKIP]',
                  p.stdout + p.stderr,
                  '摘 DENY => 提案台账被洗成 SKIP（变异体确实更坏）')


def m3_dirty_seam_must_exist():
    """--dirty 指向不存在文件 => rc=2。

    r178 补（R178-2）：必须同时注入**空暂存清单** —— 被测件的 dirty 形态校验只在
    「暂存为空」分支内；真仓若有暂存件则该分支根本进不去 ⇒ 本腿会「通过但没测到东西」。
    """
    staged_path = _write_tmp('r162_m3s_', [])
    try:
        p = subprocess.run([PY, TARGET, '--staged', staged_path,
                            '--dirty', os.path.join(ROOT, 'no_such_file_r162.txt')],
                           cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                           errors='replace', timeout=180)
    finally:
        if os.path.exists(staged_path):
            os.remove(staged_path)
    return record('m3_missing_dirty_seam_unverified', 2, p.returncode, None,
                  p.stdout + p.stderr, '测试缝指向不存在文件 => UNVERIFIED，禁静默走真 git')


def t9_staged_seam_not_inherited():
    """r178 新增常驻腿（R178-2 一手）：暂存面必须被接管，不得继承真仓状态。

    注入 staged=1（纪律面 07 台账）+ dirty 空 ⇒ 被测件须走「有暂存」路径，
    输出首行必须是「暂存 1 个文件」。若 --staged 缝失效（继承真仓），这个数字会跟着
    工作区变 —— 那正是本轮 0/11 全 FAIL 的形态。
    """
    rc, out = run_with_dirty([], staged=['memory/07-next-steps.md'])
    ok = rc == 0 and '暂存 1 个文件' in (out or '')
    RESULTS.append({'name': 't9_staged_seam_not_inherited', 'ok': ok,
                    'want_rc': 0, 'got_rc': rc, 'want_token': '暂存 1 个文件',
                    'note': '注入 staged=1 => 读数必须写「暂存 1 个文件」（--staged 缝生效）'})
    return ok


def m4_staged_seam_structurally_sealed():
    """r191 重定义（R191-2）：密闭性改由**结构**保证后的对应变异腿。

    旧形态（r178）：被测件无 --staged 时静默回落 staged_files() 读真仓 ⇒
    变异 = 摘掉 if args.staged and os.path.isfile(args.staged): 让读取恒假，
    此时读数应改从真仓继承（变坏）。r191 修掉那条回落（无注入 ⇒ files=None + rc=2）
    ⇒ 旧变异锚随之失效，泄漏路径已不存在。

    新变异 = 把 files = None 改成 files = []（模拟「以为空就是没暂存」的旧直觉），
    必须仍然 rc=2 且读数说「暂存清单为空」—— 即：即便把 None 降级成空清单，
    密闭腿也不放行，证明「无注入」与「有注入但为空」被区分开（r133 第④形态）。
    """
    src = io.open(TARGET, encoding="utf-8").read()
    # r192 改锚：被测件已恢复「缺省读真仓」（files = staged_files()），旧锚 files = None 不存在。
    # 新变异语义 = 把缺省路径改成读夹具注入面，从而「无注入」与「注入为空」不再可区分
    # => 必须仍 rc=2 且读数点名「暂存清单为空」（密闭性不因实现恢复而失效）。
    mutated = src.replace(
        "        files = staged_files()",
        "        files = [x.strip() for x in io.open(args.staged, encoding='utf-8').read().splitlines() if x.strip()] if args.staged else []",
        1)
    if mutated == src:
        RESULTS.append({'name': 'm4_staged_seam_structurally_sealed', 'ok': False,
                        'want_rc': None, 'got_rc': None, 'want_token': None,
                        'note': '变异锚未命中（files = None 写法已变）'})
        return False
    tmp = os.path.join(HERE, '_r162_m4_mutant.py')
    # r191 四修：dirty 注入面须含**非收尾产物**形态，否则被测件走 SKIP 分支，
    # 暂存读数分支根本不执行 => 泄漏无从复现（本轮实测：只注入空 dirty 恒 SKIP）
    staged_path = _write_tmp('r162_m4s_', ['memory/07-next-steps.md'])
    dirty_path = _write_tmp('r162_m4d_', ['05-exec/r137_commit_gate_map.py'])
    try:
        with io.open(tmp, 'w', encoding='utf-8', newline='\n') as f:
            f.write(mutated)
        # 不传 --staged：无注入是本腿的被测形态
        p = subprocess.run([PY, tmp, '--dirty', dirty_path],
                           cwd=ROOT, capture_output=True, text=True,
                           encoding='utf-8', errors='replace', timeout=180)
    finally:
        for x in (staged_path, dirty_path, tmp):
            if os.path.exists(x):
                os.remove(x)
    out = p.stdout + p.stderr
    ok = (p.returncode == 2) and ('暂存清单为空' in out)
    RESULTS.append({'name': 'm4_staged_seam_structurally_sealed', 'ok': ok,
                    'want_rc': 2, 'got_rc': p.returncode, 'want_token': '暂存清单为空',
                    'note': 'None 降级成空清单也不放行 => 无注入≠有注入但为空（r133 第④形态仍被区分）'})
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out', default='',
                    help='把逐腿读数落成 JSON 快照（对账登记用；缺省只打印）')
    args = ap.parse_args(argv)
    legs = [t1_closing_whitelist_skips, t2_proposal_ledger_not_washed,
            t3_ledger_07_not_washed, t4_agents_not_washed, t5_runner_not_washed,
            t6_report_md_not_whitelisted, t7_clean_tree_skips, t8_deny_beats_allow,
            m1_strip_allow_breaks_t1, m2_strip_deny_breaks_t2, m3_dirty_seam_must_exist,
            t9_staged_seam_not_inherited, m4_staged_seam_structurally_sealed]
    for fn in legs:
        try:
            fn()
        except Exception as e:  # 夹具自身异常一律记 FAIL，禁静默跳过
            RESULTS.append({'name': fn.__name__, 'ok': False, 'want_rc': None,
                            'got_rc': None, 'want_token': None, 'note': 'EXC %r' % e})
    n_ok = sum(1 for r in RESULTS if r['ok'])
    for r in RESULTS:
        print('%s %-42s want_rc=%s got_rc=%s %s' % (
            'PASS' if r['ok'] else 'FAIL', r['name'], r['want_rc'], r['got_rc'], r['note']))
    print('[GATEMAPFIX] %d/%d PASS' % (n_ok, len(RESULTS)))
    if args.out:
        doc = {'schema': 'gatemap-closing-fixtures-r162-v1',
               'cmd': 'python 05-exec/r162_gatemap_fixtures.py --json <out>',
               'legs': RESULTS,
               'n_pass': n_ok, 'n_total': len(RESULTS),
               'verdict': 'PASS' if n_ok == len(RESULTS) else 'FAIL',
               'target': '05-exec/r137_commit_gate_map.py'}
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print('[GATEMAPFIX] JSON -> %s' % args.out)
    return 0 if n_ok == len(RESULTS) else 1


if __name__ == '__main__':
    raise SystemExit(main())